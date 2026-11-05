# -*- coding: utf-8 -*-
"""S11 ETL Live: ejecución REAL por fuentes, threads, progreso y benchmarking.

Se utiliza el mismo motor verificado s11_etl_core, no se simulan tiempos.
La salida con N threads se valida contra 1 worker usando bytes derivados.
NO se llama Big Data distribuido: los threads comparten un proceso y su RAM.
"""
from __future__ import annotations

from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
import threading
from time import perf_counter
import zipfile

import pandas as pd


SCHEMA = "s11-live-threads/v1"
WORKERS = (1, 2, 4, 8)
BATCHES = (8, 16, 32, 64, 128)
STATES = ("started", "queued", "processed", "retry", "failed",
          "partition_saved", "verified", "cancelled", "finished")


def _core(core=None):
    if core is not None:
        return core
    try:
        from utils import s11_etl_core
    except ImportError:
        import s11_etl_core
    return s11_etl_core


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def _atomic_json(path: Path, obj: dict) -> None:
    """Manifiesto escrito al final; no se confunde un resultado parcial con completo."""
    path.parent.mkdir(parents=True, exist_ok=True)
    # Solo el hilo coordinador llama a esta función.
    tmp = path.with_suffix(".partial")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True),
                   encoding="utf-8")
    tmp.replace(path)


def _job(core, root: Path, index: int, kind: str, source: dict, attempt: int,
         inject_once_at: int | None, inject_always_at: int | None):
    if index == inject_always_at or (index == inject_once_at and attempt == 1):
        raise RuntimeError("Fallo didáctico inyectado sin alterar RAW")
    t0 = perf_counter()
    if kind == "image":
        a = core.transformar_imagenes(root, [source], lado=160, perfil="grises", verbose=False)
        b = core.transformar_imagenes(root, [source], lado=160, perfil="bordes", verbose=False)
        derived = a + b
    else:
        derived = core.transformar_audios(root, [source], ganancia=1.0,
                                        tasa_final=16000, verbose=False)
    for item in derived:
        if (core.sha256(root / item["original_path"]) != item["original_sha256"]
                or core.sha256(root / item["derived_path"]) != item["derived_sha256"]):
            raise ValueError("Huella no coincide tras transformación")
    return {"index": index, "kind": kind, "source_id": str(source["source_id"]),
            "rows": [core_row(core, r) for r in derived],
            "seconds": perf_counter() - t0}


def core_row(core, row: dict) -> dict:
    """Mismo contrato de S11; referencias cruzadas indebidas están prohibidas."""
    metric = "mean_luminance" if row["modality"] == "image" else "rms"
    result = {k: v for k, v in row.items() if k != "metrics"}
    result.update({
        "schema_version": core.ESQUEMA,
        "asset_id": row["original_sha256"], "metric_name": metric,
        "metric_value": row["metrics"][metric],
        "metrics_json": json.dumps(row["metrics"], sort_keys=True, ensure_ascii=False),
        "status": "ok",
    })
    if (result["modality"] == "audio" and result.get("article_id") is not None
            or result["modality"] == "image" and result.get("source_record_id") is not None):
        raise ValueError("Se intentó crear relación sin procedencia acreditada")
    return result


def _fingerprint(rows: list[dict]) -> str:
    """Identidad lógica independiente del orden de finalización de threads."""
    data = sorted((str(r["asset_id"]), str(r["profile"]),
                   str(r["derived_sha256"])) for r in rows)
    return hashlib.sha256(json.dumps(data, separators=(",", ":")).encode()).hexdigest()


def run_live(root, images, audios, *, workers=1, batch_size=32,
             label="ensayo", on_event=None, cancel_event=None,
             inject_once_at=None, inject_always_at=None, max_retries=1,
             core=None):
    """Ejecuta tareas limitando la cola a 2×workers; publica EVENTOS REALES.

    on_event recibe snapshots inmutables con etapa, tarea, duración y contadores.
    El coordinador es el ÚNICO que escribe Parquet, manifiestos y eventos.
    Cancelación: las tareas en ejecución terminan; no se declara éxito parcial.
    """
    core = _core(core)
    root = Path(root)
    if workers not in WORKERS or batch_size not in BATCHES:
        raise ValueError("Trabajadores o lote no admitidos")
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", label):
        raise ValueError("Nombre de ejecución no válido")
    if max_retries not in (0, 1, 2):
        raise ValueError("Reintentos fuera del rango pedagógico")
    if not images or not audios:
        raise ValueError("Se requieren imágenes y audios")
    tasks = [(i, "image", x) for i, x in enumerate(images)]
    tasks += [(len(images) + i, "audio", x) for i, x in enumerate(audios)]
    sha_values = [x["original_sha256"] for _, _, x in tasks]
    if len(set(sha_values)) != len(sha_values):
        raise ValueError("Los archivos RAW deben ser distintos por SHA-256")
    for _, kind, x in tasks:
        if kind == "audio" and x.get("article_id") is not None:
            raise ValueError("Audio asociado indebidamente a noticia")
        if kind == "image" and x.get("source_record_id") is not None:
            raise ValueError("Imagen asociada indebidamente a corpus de voces")
        raw = (root / x["original_path"]).resolve()
        if not raw.is_relative_to(root.resolve()) or not raw.is_file():
            raise ValueError("Ruta RAW fuera de carpeta autorizada")
        if core.sha256(raw) != x["original_sha256"]:
            raise ValueError("RAW alterado antes de ejecutar")
    run_name = f"{label}_n{workers}_b{batch_size}"
    output = root / "outputs" / "etl_live" / run_name
    output.mkdir(parents=True, exist_ok=True)
    signal = cancel_event if cancel_event is not None else threading.Event()
    if not hasattr(signal, "is_set"):
        raise ValueError("cancel_event debe ser threading.Event")
    total, total_derivatives = len(tasks), 2 * len(images) + len(audios)
    counts = dict(completed=0, derivatives=0, errors=0, retries=0)
    partitions, errors, global_rows = [], [], []
    start = perf_counter()

    with (output / "events.jsonl").open("w", encoding="utf-8") as event_log:
        def emit(state, *, index=None, modality=None, source_id=None, elapsed=None,
                 inflight=0, message="", partition=None):
            now = perf_counter() - start
            event = {
                "schema": SCHEMA, "state": state, "step": (
                    "E" if state == "started" else
                    "T" if state in ("queued", "processed", "retry", "failed") else
                    "L" if state == "partition_saved" else "QA"
                ),
                "seconds": round(now, 5), "workers": workers,
                "batch_size": batch_size, "total_sources": total,
                "expected_derivatives": total_derivatives,
                "completed_sources": counts["completed"],
                "completed_derivatives": counts["derivatives"],
                "failed_sources": counts["errors"], "retries": counts["retries"],
                "inflight": inflight,
                "sources_per_second": round(counts["completed"] / max(now, 0.000001), 2),
                "derivatives_per_second": round(counts["derivatives"] / max(now, 0.000001), 2),
                "source_index": index, "source_id": source_id,
                "modality": modality,
                "task_seconds": round(elapsed, 5) if elapsed is not None else None,
                "partition": partition, "message": message,
            }
            event_log.write(json.dumps(event, ensure_ascii=False) + "\n")
            event_log.flush()
            if on_event:
                try:
                    on_event(dict(event))
                except Exception:
                    # Un fallo de la capa de presentación nunca altera el resultado ETL.
                    pass
            return event

        emit("started", message="RAW previamente verificados. Iniciando ETL local.")
        failed = False
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="s11-etl") as executor:
            for offset in range(0, total, batch_size):
                if signal.is_set() or failed:
                    break
                group = tasks[offset:offset + batch_size]
                remaining = iter(group)
                pending = {}
                done = {}
                attempts = {}
                t_batch = perf_counter()
                # Capacidad máxima de cola: 2×workers, no 1000 futures.
                def submit_one(index, kind, source, attempt):
                    future = executor.submit(_job, core, root, index, kind, source,
                                             attempt, inject_once_at, inject_always_at)
                    pending[future] = (index, kind, source)
                    attempts[index] = attempt
                    emit("queued", index=index, modality=kind,
                         source_id=str(source["source_id"]), inflight=len(pending))
                def fill():
                    while len(pending) < 2 * workers and not signal.is_set():
                        job = next(remaining, None)
                        if job is None:
                            return
                        submit_one(*job, 1)
                fill()
                while pending:
                    finished, _ = wait(set(pending), return_when=FIRST_COMPLETED)
                    for future in finished:
                        index, kind, source = pending.pop(future)
                        attempt = attempts[index]
                        try:
                            item = future.result()
                            done[index] = item
                            counts["completed"] += 1
                            counts["derivatives"] += len(item["rows"])
                            emit("processed", index=index, modality=kind,
                                 source_id=str(source["source_id"]),
                                 elapsed=item["seconds"], inflight=len(pending))
                        except Exception as e:
                            if attempt <= max_retries and not signal.is_set():
                                counts["retries"] += 1
                                emit("retry", index=index, modality=kind,
                                     source_id=str(source["source_id"]),
                                     message=f"Reintento {attempt}: {type(e).__name__}",
                                     inflight=len(pending))
                                submit_one(index, kind, source, attempt + 1)
                            else:
                                failed = True
                                counts["errors"] += 1
                                errors.append({"index": index, "source_id": str(source["source_id"]),
                                               "kind": kind, "error": str(e)[:250]})
                                emit("failed", index=index, modality=kind,
                                     source_id=str(source["source_id"]),
                                     message=type(e).__name__ + ": " + str(e)[:140],
                                     inflight=len(pending))
                    if not failed:
                        fill()
                # No se escribe partición "completa" si hubo cancelación o fallo.
                if signal.is_set() or failed:
                    break
                rows = [row for k in sorted(done) for row in done[k]["rows"]]
                if len(done) != len(group):
                    failed = True
                    errors.append({"error": "Tareas no terminadas en lote"})
                    break
                part_file = output / f"part_{len(partitions):04d}.parquet"
                pd.DataFrame(rows).to_parquet(part_file, index=False)
                if len(pd.read_parquet(part_file)) != len(rows):
                    raise ValueError("Parquet no conserva las filas")
                part = {
                    "file": part_file.name, "sha256": _sha(part_file), "sources": len(group),
                    "rows": len(rows), "seconds": round(perf_counter() - t_batch, 6),
                    "bytes": part_file.stat().st_size,
                }
                partitions.append(part)
                global_rows.extend(rows)
                emit("partition_saved", partition=part_file.name,
                     message=f"{len(rows)} derivados; {part['seconds']} s")
        success = (not signal.is_set() and not failed and
                   counts["completed"] == total and
                   counts["derivatives"] == total_derivatives)
        status = "complete" if success else ("cancelled" if signal.is_set() else "failed")
        elapsed = perf_counter() - start
        manifest = {
            "schema": SCHEMA, "status": status, "label": label,
            "processing": "ThreadPoolExecutor local, NO procesamiento distribuido",
            "workers": workers, "batch_size": batch_size,
            "sources": total, "images": len(images), "audios": len(audios),
            "expected_derivatives": total_derivatives,
            "completed_sources": counts["completed"],
            "completed_derivatives": counts["derivatives"],
            "retries": counts["retries"], "errors": errors, "partitions": partitions,
            "originals": {x["original_path"]: x["original_sha256"] for _, _, x in tasks},
            "fingerprint": _fingerprint(global_rows) if success else None,
            "elapsed_seconds": round(elapsed, 6),
            "derivatives_per_second": round(counts["derivatives"] / max(elapsed, 0.000001), 4),
        }
        _atomic_json(output / "manifest.json", manifest)
        if success:
            verified = verify_run(root, output / "manifest.json", core=core)
            if not verified["ok"]:
                raise ValueError("Verificación fallida: " + repr(verified["errors"][:3]))
            emit("verified", message=f"{verified['rows']} derivados y SHA-256 validados")
        emit("finished" if success else "cancelled" if signal.is_set() else "failed",
             message=f"Estado {status}: {counts['completed']}/{total} fuentes")
    return {
        "status": status, "manifest_path": output / "manifest.json",
        "events_path": output / "events.jsonl", "manifest": manifest,
        "verified": verified if success else {"ok": False, "errors": errors or [status]},
    }


def verify_run(root, path, *, core=None):
    core = _core(core)
    root, path = Path(root), Path(path)
    info = json.loads(path.read_text(encoding="utf-8"))
    errors = []
    if info.get("schema") != SCHEMA or info.get("status") != "complete":
        errors.append("run_incomplete")
    rows, seen = [], set()
    for name, sha in info.get("originals", {}).items():
        original = (root / name).resolve()
        if not original.is_relative_to(root.resolve()) or not original.is_file() or core.sha256(original) != sha:
            errors.append("original:" + name)
    for p in info.get("partitions", []):
        part = (path.parent / p["file"]).resolve()
        if (not part.is_relative_to(path.parent.resolve()) or not part.is_file()
                or _sha(part) != p["sha256"]):
            errors.append("part:" + str(p["file"]))
            continue
        df = pd.read_parquet(part)
        if len(df) != p["rows"]:
            errors.append("part_count:" + p["file"])
        for row in df.to_dict("records"):
            rows.append(row)
            key = (str(row["asset_id"]), str(row["profile"]))
            if key in seen:
                errors.append("duplicated_derived:" + str(key))
            seen.add(key)
            for col, hashcol in (("original_path", "original_sha256"),
                                 ("derived_path", "derived_sha256")):
                item = (root / str(row[col])).resolve()
                if not item.is_relative_to(root.resolve()) or not item.is_file() or core.sha256(item) != row[hashcol]:
                    errors.append("asset:" + str(row[col]))
            if row["modality"] == "audio" and pd.notna(row.get("article_id")):
                errors.append("false_editorial_relation")
            if row["modality"] == "image" and pd.notna(row.get("source_record_id")):
                errors.append("false_audio_relation")
    if len(rows) != info.get("expected_derivatives"):
        errors.append("total_derivatives")
    if info.get("fingerprint") != _fingerprint(rows):
        errors.append("fingerprint")
    return {"ok": not errors, "errors": errors, "rows": len(rows),
            "parts": len(info.get("partitions", [])),
            "sources": info.get("sources", 0)}


def run_benchmark(root, images, audios, *, batch_size=32,
                  workers=(1, 2, 4), repeats=3, core=None, on_event=None,
                  cancel_event=None):
    """Repeticiones independientes y orden rotado para mitigar sesgos de caché.

    La métrica compara SOLO transformación+Parquet con RAW ya descargado.
    No compara descarga. Los resultados NO implican speedup garantizado.
    """
    import pandas as pd
    core = _core(core)
    if not workers or any(x not in WORKERS for x in workers) or len(set(workers)) != len(workers):
        raise ValueError("Workers no válidos o duplicados")
    if repeats not in (1, 2, 3, 4, 5):
        raise ValueError("Repeticiones entre 1 y 5")
    root = Path(root)
    out = root / "outputs" / "etl_live" / "benchmark"
    out.mkdir(parents=True, exist_ok=True)
    records, hashes = [], []
    for rep in range(repeats):
        order = list(workers[rep % len(workers):]) + list(workers[:rep % len(workers)])
        for n in order:
            if cancel_event is not None and cancel_event.is_set():
                raise RuntimeError("Benchmark cancelado; no se generan comparaciones incompletas")
            tag = f"benchmark_r{rep + 1:02d}"
            result = run_live(root, images, audios, workers=n, batch_size=batch_size,
                              label=tag, on_event=on_event,
                              cancel_event=cancel_event, core=core)
            if result["status"] != "complete" or not result["verified"]["ok"]:
                raise ValueError("No se compara un run incompleto: " + str(result["status"]))
            m = result["manifest"]
            hashes.append(m["fingerprint"])
            records.append({
                "rep": rep + 1, "workers": n, "batch_size": batch_size,
                "elapsed_seconds": m["elapsed_seconds"],
                "derivatives_per_second": m["derivatives_per_second"],
                "sources": m["sources"], "derivatives": m["expected_derivatives"],
                "fingerprint": m["fingerprint"],
            })
    if len(set(hashes)) != 1:
        raise ValueError("El benchmark produjo resultados diferentes con threads")
    table = pd.DataFrame(records)
    table.to_csv(out / "mediciones.csv", index=False)
    summary = (table.groupby("workers").agg(
        seconds_median=("elapsed_seconds", "median"),
        rate_median=("derivatives_per_second", "median"),
        runs=("rep", "count")).reset_index())
    if 1 not in set(summary["workers"]):
        raise ValueError("Sin línea base de 1 worker no se calcula speedup")
    base = float(summary.loc[summary.workers == 1, "seconds_median"].iloc[0])
    summary["speedup"] = (base / summary["seconds_median"]).round(4)
    summary["efficiency"] = (summary["speedup"] / summary["workers"]).round(4)
    summary.to_csv(out / "comparacion.csv", index=False)
    _atomic_json(out / "benchmark_manifest.json", {
        "schema": SCHEMA, "status": "complete", "repeats": repeats,
        "workers": list(workers), "same_fingerprint": hashes[0],
        "batch_size": batch_size, "base_seconds_median": base,
        "limitations": [
            "solo 1 proceso; no es clúster ni prueba de Dask/Spark",
            "la caché, E/S y bibliotecas nativas influyen en cada ejecución",
            "la métrica omite descarga inicial y carga de corpus",
        ],
    })
    return {"measurements": table, "summary": summary,
            "manifest": out / "benchmark_manifest.json", "folder": out}


def export_benchmark(result, destination=None):
    """ZIP de evidencia: CSV, manifiesto y eventos, NUNCA medios editoriales."""
    folder = Path(result["folder"])
    destination = Path(destination) if destination else folder / "informe_concurrencia_s11.zip"
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for name in ("benchmark_manifest.json", "mediciones.csv", "comparacion.csv"):
            z.write(folder / name, name)
        z.writestr("LEEME.txt",
            "Tiempos realmente medidos, sin garantía de aceleración.\n"
            "No incluye originales/derivados editoriales ni voces; reejecutar "
            "S11 con fuentes autorizadas para recomputar los hashes.\n")
    with zipfile.ZipFile(destination) as z:
        if z.testzip() is not None:
            raise ValueError("ZIP corrupto")
    return destination
