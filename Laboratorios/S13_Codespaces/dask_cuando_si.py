#!/usr/bin/env python3
"""S13 · Dask en acción. Demo pequeña: mismas tareas secuenciales y con workers reales.

Modo espera: latencia externa SIMULADA (análoga a OCR/ASR por archivo), no hace OCR.
Modo cpu: carga CPU reproducible de PBKDF2; es sintética, no representa un modelo IA.
Nunca procesa 50.000 documentos y no debe ejecutarse automáticamente en Actions.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FUENTE = ROOT / "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
SALIDA = Path(__file__).resolve().parent / "salidas" / "dask_demostracion_s13.json"


def cpus_disponibles() -> int:
    """Respeta afinidad Linux/contendor cuando existe; son CPU lógicas, NO núcleos físicos."""
    return len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else (os.cpu_count() or 1)


def crear_trabajos(cantidad: int, espera: float, modo: str, iteraciones: int) -> list[dict]:
    """Usa títulos SECOP versionados; el número de tareas no cambia el tamaño de entrada."""
    with FUENTE.open(encoding="utf-8-sig", newline="") as f:
        fila = csv.DictReader(f)
        textos = [
            (x.get("nombre_del_procedimiento") or "").strip()
            for x in fila
        ][:1000]
    if not textos:
        raise RuntimeError(f"CSV vacío: {FUENTE}")
    return [
        {"id": i, "textos": textos[i::cantidad], "modo": modo,
         "espera": espera, "iteraciones": iteraciones}
        for i in range(cantidad)
    ]


def procesar_lote(tarea: dict) -> dict:
    """Trabajo independiente. La espera imita I/O remoto; no es OCR real."""
    textos = tarea["textos"]
    palabras = sum(len(x.split()) for x in textos)
    contenido = "\n".join(textos).encode("utf-8")
    huella = hashlib.sha256(contenido).hexdigest()
    if tarea["modo"] == "espera":
        time.sleep(tarea["espera"])
    else:
        huella = hashlib.pbkdf2_hmac("sha256", contenido, b"s13", tarea["iteraciones"]).hex()
    try:
        from distributed import get_worker
        trabajador = get_worker().address
    except (ValueError, ImportError):
        trabajador = "secuencial"
    return {"id": tarea["id"], "registros": len(textos), "palabras": palabras,
            "sha256": huella, "worker": trabajador}


def ejecutar(trabajos: list[dict], workers: int, tablero: bool = False) -> dict:
    from distributed import Client, LocalCluster
    inicio_local = time.perf_counter()
    secuencial = [procesar_lote(t) for t in trabajos]
    t_local = time.perf_counter() - inicio_local

    inicio_cluster = time.perf_counter()
    with LocalCluster(
        n_workers=workers, threads_per_worker=1, processes=True,
        dashboard_address=":8787" if tablero else None,
    ) as cluster:
        with Client(cluster) as client:
            client.wait_for_workers(workers)
            t_inicio = time.perf_counter() - inicio_cluster
            info = client.scheduler_info()["workers"]
            inicio_trabajo = time.perf_counter()
            paralelos = client.gather(client.map(procesar_lote, trabajos, pure=False))
            t_dask_caliente = time.perf_counter() - inicio_trabajo
            t_total = time.perf_counter() - inicio_cluster

    def firma(rows: list[dict]) -> list[tuple]:
        return [(r["id"], r["registros"], r["palabras"], r["sha256"])
                for r in sorted(rows, key=lambda x: x["id"])]

    if firma(secuencial) != firma(paralelos):
        raise AssertionError("Los motores produjeron resultados distintos.")
    return {
        "caso": trabajos[0]["modo"],
        "descripcion": (
            "espera de servicio EXTERNO SIMULADA, no OCR/ASR real"
            if trabajos[0]["modo"] == "espera" else "cálculo CPU sintético PBKDF2"
        ),
        "tareas": len(trabajos),
        "workers": workers,
        "threads_por_worker": 1,
        "cpus_logicas_disponibles": cpus_disponibles(),
        "filas_procesadas": sum(x["registros"] for x in paralelos),
        "palabras_procesadas": sum(x["palabras"] for x in paralelos),
        "workers_reales": [{"direccion": addr,
                            "hilos": data["nthreads"],
                            "limite_memoria_bytes": data["memory_limit"]}
                           for addr, data in info.items()],
        "segundos_secuencial": round(t_local, 4),
        "segundos_arranque_y_espera_workers": round(t_inicio, 4),
        "segundos_dask_cluster_caliente": round(t_dask_caliente, 4),
        "segundos_dask_total_incluido_arranque": round(t_total, 4),
        "aceleracion_cluster_caliente": round(t_local / t_dask_caliente, 3),
        "aceleracion_extremo_a_extremo": round(t_local / t_total, 3),
        "resultados_identicos": True,
        "ganador_caliente": "Dask" if t_dask_caliente < t_local else "secuencial",
        "ganador_total": "Dask" if t_total < t_local else "secuencial",
        "trazabilidad": "Medido en esta máquina al ejecutarse, nunca extrapolar a otra",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=2,
                        help="Procesos Dask; 1, 2 o 4, cada uno con un hilo.")
    parser.add_argument("--tareas", type=int, default=8,
                        help="Número de lotes independientes del CSV pequeño.")
    parser.add_argument("--espera", type=float, default=0.60,
                        help="Segundos de espera externa simulada por lote.")
    parser.add_argument("--modo", choices=["espera", "cpu"], default="espera")
    parser.add_argument("--iteraciones", type=int, default=300000,
                        help="Carga sintética si --modo cpu; no es modelo de IA.")
    parser.add_argument("--tablero", action="store_true",
                        help="Abre puerto 8787 si está disponible (mantener PRIVATE).")
    args = parser.parse_args()

    if args.workers not in (1, 2, 4):
        parser.error("Para la clase, los workers se limitan a 1, 2 o 4.")
    if not 2 <= args.tareas <= 16:
        parser.error("Usa entre 2 y 16 tareas para mantener la prueba ligera.")
    if not 0 <= args.espera <= 1.0 or not 1000 <= args.iteraciones <= 1000000:
        parser.error("Parámetros fuera de los límites de seguridad de la clase.")

    disponibles = cpus_disponibles()
    print(f"CPU lógicas habilitadas: {disponibles}; workers: {args.workers} × 1 hilo")
    if args.workers > disponibles:
        print("ADVERTENCIA: hay más workers que CPU lógicas; puede empeorar el tiempo.")

    datos = crear_trabajos(args.tareas, args.espera, args.modo, args.iteraciones)
    resultado = ejecutar(datos, args.workers, args.tablero)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    SALIDA.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nRESULTADO_S13_DASK="+json.dumps(resultado, ensure_ascii=False))
    print(f"JSON: {SALIDA}")
    print(f"Ganador de la TAREA (clúster ya abierto): {resultado['ganador_caliente']}")
    print(f"Ganador INCLUYENDO arranque: {resultado['ganador_total']}")
    print("Si pierdes con Dask, identifica sobrecarga y cambia tareas/workers; no manipules tiempos.")


if __name__ == "__main__":
    main()
