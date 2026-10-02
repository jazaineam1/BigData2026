#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Revalidador docente del TC1: no confía en el manifest del estudiante.

Recibe la carpeta descargada de Drive (o el ZIP) y:
1. comprueba los tres archivos oficiales y la huella SHA-256 del correo;
2. comprueba que el manifest externo es idéntico al del ZIP;
3. extrae el ZIP y recalcula TODO con el mismo núcleo que usó el estudiante
   (tc1_validador), partiendo de las páginas RAW y de las firmas de la consulta oficial;
4. busca secretos en el ZIP y en las celdas y salidas del notebook;
5. compara control por control con el manifest del estudiante y muestra el panel;
6. guarda el informe en una carpeta privada (por defecto .local-docente/tc1/revisiones).

Las capturas se confirman a mano: --capturas E2=ok,E4=ok,E5=no (sin el flag quedan pendientes).

Uso:
    python utils/tc1_teacher_validator.py --entrega <carpeta o TC1_Pxx.zip> [--sha-correo HEX]
           [--capturas E2=ok,E4=ok,E5=ok] [--salida .local-docente/tc1/revisiones]
'''
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
import tc1_contrato as C  # noqa: E402
import tc1_validador as V  # noqa: E402


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _capturas(texto):
    salida = {}
    for parte in filter(None, (texto or "").split(",")):
        etapa, _, valor = parte.partition("=")
        salida[etapa.strip().upper()] = valor.strip().lower() in ("ok", "si", "sí", "1", "true")
    return salida


def localizar(entrega):
    entrega = Path(entrega)
    if entrega.is_file() and entrega.suffix == ".zip":
        return {"zip": entrega, "manifest": None, "notebook": None, "carpeta": entrega.parent}
    zips = sorted(entrega.glob("TC1_*.zip"))
    nbs = sorted(entrega.glob("TC1_*.ipynb"))
    man = entrega / C.MANIFEST
    return {"zip": zips[0] if zips else None, "manifest": man if man.exists() else None,
            "notebook": nbs[0] if nbs else None, "carpeta": entrega, "zips": zips, "nbs": nbs}


def revisar(entrega, sha_correo=None, capturas=None):
    arch = localizar(entrega)
    avisos = []
    if not arch["zip"]:
        raise SystemExit("No encontré TC1_<PAREJA_ID>.zip en la entrega.")
    for clave, nombre in (("manifest", "manifest_tc1.json"), ("notebook", "TC1_<PAREJA_ID>.ipynb")):
        if not arch.get(clave):
            avisos.append(f"falta {nombre} fuera del ZIP")
    if len(arch.get("zips", [])) > 1 or len(arch.get("nbs", [])) > 1:
        avisos.append("hay más de un ZIP o más de un notebook en la carpeta")
    tmp = Path(tempfile.mkdtemp(prefix="tc1_revision_"))
    try:
        with zipfile.ZipFile(arch["zip"]) as zf:
            for miembro in zf.namelist():
                destino = (tmp / miembro).resolve()
                if not str(destino).startswith(str(tmp.resolve())):
                    raise SystemExit(f"El ZIP contiene una ruta insegura: {miembro}")
            zf.extractall(tmp)
        manifest_zip = tmp / C.MANIFEST
        estudiante = json.loads(manifest_zip.read_text(encoding="utf-8")) if manifest_zip.exists() else {}
        if not manifest_zip.exists():
            avisos.append("el ZIP no trae manifest_tc1.json")
        if arch.get("manifest"):
            if arch["manifest"].read_bytes() != manifest_zip.read_bytes():
                avisos.append("el manifest externo NO es idéntico al del ZIP")
            huella = _sha(arch["manifest"])
            if sha_correo and sha_correo.strip().lower() != huella:
                avisos.append(f"la huella del correo no coincide con el manifest entregado ({huella[:12]}…)")
        else:
            huella = _sha(manifest_zip) if manifest_zip.exists() else None
        nb = None
        if arch.get("notebook"):
            nb = json.loads(arch["notebook"].read_text(encoding="utf-8"))
            if C.VERSION_VISIBLE not in json.dumps(nb, ensure_ascii=False):
                avisos.append("el notebook entregado no es la versión vigente del TC1")
        docente = V.evaluar(tmp, modo="docente", capturas=capturas or {}, notebook=nb, escribir=False)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if estudiante.get("pareja_id") and estudiante.get("pareja_id") != docente["pareja_id"]:
        avisos.append("el PAREJA_ID del manifest no coincide con el de la carpeta de trabajo")
    diferencias = [k for k, c in docente["controles"].items()
                   if (estudiante.get("controles") or {}).get(k, {}).get("puntos") != c["puntos"]]
    return {"entrega": str(entrega), "huella_manifest": huella, "avisos": avisos, "estudiante": estudiante,
            "docente": docente, "diferencias": diferencias}


def panel(r):
    d, e = r["docente"], r["estudiante"]
    nombres = " / ".join(x.get("apellido") or x.get("nombre", "") for x in d.get("integrantes", []))
    lineas = [f"TC1 · {d['pareja_id']} · {nombres}", ""]
    for etapa, info in d["etapas"].items():
        marca = "✓" if info["puntos"] == info["maximo"] else "⚠"
        lineas.append(f"{etapa} · {info['nombre']:<34} {info['puntos']:>2} / {info['maximo']:<2}  {marca}")
    lineas += ["", f"TOTAL {d['puntaje']:>28} / 100",
               f"NOTA  {d['nota_exacta']:.2f} → se registra {d['nota_registrada']:.1f}", ""]
    if e:
        coincide = not r["diferencias"]
        lineas.append(f"Manifest estudiante: {e.get('puntaje')}/100 · Revalidación docente: {d['puntaje']}/100 · "
                      + ("COINCIDEN: SÍ" if coincide else "DISCREPANCIA: REVISAR " + ", ".join(r["diferencias"])))
    fallas = [(k, c) for k, c in d["controles"].items() if not c["ok"]]
    if fallas or d["pendiente_confirmacion_visual"]:
        lineas += ["", "REVISIÓN MANUAL:"]
        for k, c in fallas:
            lineas.append(f"  ⚠ {k} · {c['descripcion']} ({c['puntos']}/{c['maximo']}) · {c['evidencia'][:160]}")
        for k in d["pendiente_confirmacion_visual"]:
            etapa = C.CAPTURA_DE_ITEM[k]
            lineas.append(f"  ⚠ {k} · mira {C.CAPTURAS[etapa]} y confirma con --capturas {etapa}=ok o {etapa}=no")
    lineas += ["", "EVIDENCIAS VISUALES:"]
    for etapa, nombre in C.CAPTURAS.items():
        item = next(k for k, v in C.CAPTURA_DE_ITEM.items() if v == etapa)
        c = d["controles"][item]
        lineas.append(f"  {'✓' if 'PNG de' in c['evidencia'] else '✗'} {nombre}")
    gate = d["gates"]["sin_secretos"]
    lineas += ["", "SEGURIDAD: " + ("✓ sin secretos detectados." if gate["ok"] else "✗ " + "; ".join(gate["hallazgos"]))]
    if r["avisos"]:
        lineas += ["", "AVISOS DE LA ENTREGA:"] + [f"  ⚠ {a}" for a in r["avisos"]]
    lineas.append(f"\nHuella del manifest: {r['huella_manifest']}")
    return "\n".join(lineas)


def guardar(r, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    d = r["docente"]
    (salida / f"revision_{d['pareja_id'] or 'sin_pareja'}.json").write_text(
        json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    nuevo = not (salida / "notas_tc1.csv").exists()
    with open(salida / "notas_tc1.csv", "a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if nuevo:
            w.writerow(["revisado_utc", "pareja", *C.STAGE_MAX, "puntaje", "nota_exacta", "nota_registrada",
                        "pendiente_visual", "discrepancias", "avisos", "huella_manifest"])
        w.writerow([datetime.now(timezone.utc).isoformat(timespec="seconds"), d["pareja_id"],
                    *[d["etapas"][e]["puntos"] for e in C.STAGE_MAX], d["puntaje"], d["nota_exacta"],
                    d["nota_registrada"], " ".join(d["pendiente_confirmacion_visual"]), " ".join(r["diferencias"]),
                    " | ".join(r["avisos"]), r["huella_manifest"]])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrega", required=True)
    ap.add_argument("--sha-correo")
    ap.add_argument("--capturas", default="")
    ap.add_argument("--salida", default=str(ROOT / ".local-docente" / "tc1" / "revisiones"))
    ap.add_argument("--no-guardar", action="store_true")
    a = ap.parse_args()
    r = revisar(a.entrega, a.sha_correo, _capturas(a.capturas))
    print(panel(r))
    if not a.no_guardar:
        guardar(r, a.salida)
        print(f"Registro privado actualizado en {a.salida}")


if __name__ == "__main__":
    main()
