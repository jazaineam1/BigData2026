#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Revalidador docente del TC1: no confía en el manifest del estudiante.

Acepta lo que realmente tendrás a mano:
- el ZIP que descarga Google Drive al bajar la carpeta de la pareja (con los tres archivos dentro),
- la carpeta ya descomprimida,
- o directamente TC1_<PAREJA_ID>.zip.

Para cada entrega:
1. comprueba los tres archivos y, si la das, la huella SHA-256 del correo;
2. comprueba que el manifest externo es idéntico al del ZIP;
3. recalcula TODO con el mismo núcleo que usó el estudiante (tc1_validador), desde las páginas
   RAW y las firmas de la consulta oficial de la pareja;
4. busca secretos en el ZIP y en las celdas y salidas del notebook;
5. compara control por control con el manifest del estudiante;
6. deja en la carpeta de revisión las tres capturas, la retroalimentación de la pareja y una
   sola fila por equipo en notas_tc1.csv (la última revisión reemplaza a la anterior).

El PAREJA_ID es libre (cada pareja escribió el que quiso) y la ventana de datos sale de los
códigos de los integrantes. Cada equipo se identifica por PAREJA_ID + apellidos, como su carpeta
de entrega, así que dos equipos con el mismo nombre no se pisan. Se avisa cuando dos equipos
comparten ventana de datos (pasa por azar, ≈ 1 en 30 por cada par de equipos) y cuando dos entregas
traen la misma descarga (mismo instante de consulta a la API: una copió el paquete de la otra).

Una entrega de la versión anterior (V7) no se puede recalcular (V7 validaba variables en
memoria): se reconoce, no se le inventa una nota y queda marcada para revisión manual.

Uso:
    python utils/tc1_teacher_validator.py --lote <carpeta con las descargas de Drive>
    python utils/tc1_teacher_validator.py --entrega <zip de Drive | carpeta | TC1_Pxx.zip>
           [--sha-correo HEX] [--capturas E2=ok,E4=ok,E5=no] [--abrir] [--salida <carpeta privada>]
'''
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import os
import re
import shutil
import sys
import tempfile
import unicodedata
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
import tc1_contrato as C  # noqa: E402

SALIDA_DEFECTO = ROOT / ".local-docente" / "tc1" / "revisiones"
ZIP_ESTUDIANTE = re.compile(r"^TC1_(?!BIGDATA_)[A-Z0-9]+\.zip$", re.I)
COLUMNAS_CSV = ["pareja", "equipo", "clave", "codigos", "ventana", "estado", "puntaje", "nota_exacta", "nota_registrada",
                *C.STAGE_MAX, "capturas", "discrepancias", "avisos", "huella_manifest", "descarga_utc", "revisado_utc"]


def requisitos():
    faltan = [m for m in ("pandas", "pyarrow") if importlib.util.find_spec(m) is None]
    if faltan:
        raise SystemExit(f"Faltan librerías para revisar: {', '.join(faltan)}.\nInstálalas con:\n"
                         f"  \"{sys.executable}\" -m pip install {' '.join(faltan)}")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _capturas(texto):
    salida = {}
    for parte in filter(None, (texto or "").split(",")):
        etapa, _, valor = parte.partition("=")
        salida[etapa.strip().upper()] = valor.strip().lower() in ("ok", "si", "sí", "1", "true")
    return salida


def _extraer_seguro(zf, destino):
    destino = Path(destino).resolve()
    for miembro in zf.namelist():
        if not str((destino / miembro).resolve()).startswith(str(destino)):
            raise SystemExit(f"El ZIP contiene una ruta insegura: {miembro}")
    zf.extractall(destino)


def _es_paquete(nombres):
    return any(n in ("identidad.json", C.MANIFEST) or n.startswith("E1/") for n in nombres)


def localizar(entrega, tmp):
    '''Devuelve {zip, manifest, notebook} a partir de un ZIP de Drive, una carpeta o el ZIP del estudiante.'''
    entrega = Path(entrega)
    if entrega.is_file() and entrega.suffix.lower() == ".zip":
        with zipfile.ZipFile(entrega) as zf:
            if _es_paquete(zf.namelist()):
                return {"zip": entrega, "manifest": None, "notebook": None, "origen": "ZIP del estudiante"}
            destino = Path(tempfile.mkdtemp(prefix="drive_", dir=tmp))
            _extraer_seguro(zf, destino)
        r = localizar(destino, tmp)
        r["origen"] = "descarga de Drive"
        return r
    if not entrega.is_dir():
        raise SystemExit(f"No encontré la entrega: {entrega}")
    zips = sorted(p for p in entrega.rglob("*.zip") if ZIP_ESTUDIANTE.match(p.name))
    if not zips:
        envolturas = sorted(p for p in entrega.rglob("*.zip"))
        if len(envolturas) == 1:
            return localizar(envolturas[0], tmp)
        raise SystemExit(f"En {entrega} no hay un TC1_<PAREJA_ID>.zip.")
    carpeta = zips[0].parent
    nbs = sorted(carpeta.glob("TC1_*.ipynb"))
    man = carpeta / C.MANIFEST
    return {"zip": zips[0], "manifest": man if man.exists() else None, "notebook": nbs[0] if nbs else None,
            "origen": "carpeta", "duplicados": len(zips) > 1 or len(nbs) > 1}


def revisar(entrega, sha_correo=None, capturas=None, salida=None):
    import tc1_validador as V
    tmp = Path(tempfile.mkdtemp(prefix="tc1_revision_"))
    try:
        arch = localizar(entrega, tmp)
        avisos = []
        for clave, nombre in (("manifest", "manifest_tc1.json"), ("notebook", "TC1_<PAREJA_ID>.ipynb")):
            if not arch.get(clave):
                avisos.append(f"falta {nombre} fuera del ZIP")
        if arch.get("duplicados"):
            avisos.append("hay más de un ZIP o más de un notebook en la carpeta: se revisó el primero")
        paquete = tmp / "paquete"
        with zipfile.ZipFile(arch["zip"]) as zf:
            _extraer_seguro(zf, paquete)
        manifest_zip = paquete / C.MANIFEST
        estudiante = json.loads(manifest_zip.read_text(encoding="utf-8")) if manifest_zip.exists() else {}
        huella = None
        if arch.get("manifest"):
            if manifest_zip.exists() and arch["manifest"].read_bytes() != manifest_zip.read_bytes():
                avisos.append("el manifest externo NO es idéntico al del ZIP")
            huella = _sha(arch["manifest"])
            if sha_correo and sha_correo.strip().lower() != huella:
                avisos.append(f"la huella del correo no coincide con el manifest entregado ({huella[:12]}…)")
        elif manifest_zip.exists():
            huella = _sha(manifest_zip)
        version = str(estudiante.get("version", ""))
        if version != C.VERSION or not (paquete / "identidad.json").exists():
            return {"entrega": str(entrega), "origen": arch["origen"], "huella_manifest": huella, "avisos": avisos,
                    "estudiante": estudiante, "docente": None, "diferencias": [], "anterior": version or "desconocida"}
        nb = json.loads(arch["notebook"].read_text(encoding="utf-8")) if arch.get("notebook") else None
        if nb is not None and C.VERSION_VISIBLE not in json.dumps(nb, ensure_ascii=False):
            avisos.append("el notebook entregado no es la versión vigente del TC1")
        docente = V.evaluar(paquete, modo="docente", capturas=capturas or {}, notebook=nb, escribir=False)
        if estudiante.get("pareja_id") != docente["pareja_id"]:
            avisos.append("el PAREJA_ID del manifest no coincide con el de la carpeta de trabajo")
        diferencias = [k for k, c in docente["controles"].items()
                       if (estudiante.get("controles") or {}).get(k, {}).get("puntos") != c["puntos"]]
        acq = json.loads((paquete / "E1" / "01_acquisition_manifest.json").read_text(encoding="utf-8"))             if (paquete / "E1" / "01_acquisition_manifest.json").exists() else {}
        r = {"entrega": str(entrega), "origen": arch["origen"], "huella_manifest": huella, "avisos": avisos,
             "estudiante": estudiante, "docente": docente, "diferencias": diferencias, "anterior": None,
             "ventana": docente.get("ventana"), "descarga_utc": acq.get("consultado_utc")}
        if salida:
            r["capturas_extraidas"] = _guardar_capturas(paquete, carpeta_equipo(r, salida))
        return r
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def _guardar_capturas(paquete, destino):
    destino.mkdir(parents=True, exist_ok=True)
    salida = []
    for etapa, nombre in C.CAPTURAS.items():
        origen = paquete / etapa / nombre
        if origen.exists():
            shutil.copyfile(origen, destino / nombre)
            salida.append(str(destino / nombre))
    return salida


def _sin_tildes(texto):
    t = unicodedata.normalize("NFKD", str(texto or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "", t).upper()


def pareja_de(r):
    return (r["docente"] or {}).get("pareja_id") or r["estudiante"].get("pareja_id") or "sin_pareja"


def _integrantes(r):
    return (r["docente"] or {}).get("integrantes") or r["estudiante"].get("integrantes") or []


def equipo(r):
    '''PAREJA_ID + apellidos, como la carpeta de entrega: dos equipos con el mismo PAREJA_ID no se pisan.'''
    return "_".join([pareja_de(r)] + [_sin_tildes(x.get("apellido")) for x in _integrantes(r) if x.get("apellido")])


def codigos(r):
    return sorted(str(x.get("codigo", "")).strip() for x in _integrantes(r) if str(x.get("codigo", "")).strip())


def clave(r):
    '''Identidad interna del equipo: huella de sus códigos normalizados, sin importar el orden de los integrantes.
    El nombre libre y los apellidos son solo el rótulo (equipo): dos equipos con el mismo rótulo no se pisan.
    Sin códigos (por ejemplo, una entrega de otra versión), la identidad es el rótulo.'''
    limpios = sorted({C.normalizar_codigo(c) for c in codigos(r)} - {""})
    if not limpios:
        return equipo(r)
    return hashlib.sha256(("EQUIPO|" + "|".join(limpios)).encode("utf-8")).hexdigest()[:12]


def _visto(x):
    '''(clave, rótulo, ventana, descarga). Acepta también las tuplas viejas (rótulo, ventana, descarga).'''
    return tuple(x) if len(x) == 4 else (x[0], x[0], x[1], x[2])


def conflictos(resultados, registradas=()):
    '''Avisa cuando dos equipos distintos comparten ventana de datos (pasa por azar) o traen la misma
    descarga (mismo instante de consulta a la API: paquete copiado). registradas: (clave, equipo, ventana,
    descarga_utc) que ya están en notas_tc1.csv, para comparar también con revisiones anteriores.
    Dos equipos son el mismo cuando tienen los mismos códigos, aunque cambie el orden de los integrantes.'''
    vistos = [_visto(x) for x in registradas] + [(clave(r), equipo(r), r.get("ventana"), r.get("descarga_utc"))
                                                 for r in resultados]
    for r in resultados:
        k, v, d = clave(r), r.get("ventana"), r.get("descarga_utc")
        copia = sorted({e for kk, e, _, dd in vistos if kk != k and d and dd == d})
        misma = sorted({e for kk, e, vv, _ in vistos if kk != k and v and vv == v})
        if copia:
            r["avisos"].append(f"misma descarga que {', '.join(copia)} (mismo instante de consulta a la API): "
                               "posible paquete copiado")
        elif misma:
            r["avisos"].append(f"comparte la ventana de datos {v} con {', '.join(misma)} (por azar): tienen las mismas "
                               "respuestas de referencia; compara sus capturas y sus decisiones de E6")
    return resultados


def estado(r):
    if r["docente"] is None:
        return f"versión anterior ({r['anterior']}): revisión manual"
    d = r["docente"]
    if r["avisos"] or r["diferencias"] or not d["gates"]["sin_secretos"]["ok"]:
        return "revisar avisos"
    if d["pendiente_confirmacion_visual"]:
        return "confirmar capturas"
    return "definitiva"


def panel(r):
    e = r["estudiante"]
    if r["docente"] is None:
        lineas = [f"TC1 · {e.get('pareja_id') or '¿pareja?'} · ENTREGA DE OTRA VERSIÓN ({r['anterior']})", "",
                  "El revalidador V9 no puede recalcular esta entrega (V7 validaba variables en memoria del cuaderno).",
                  f"Puntaje que declaró el estudiante: {e.get('puntaje', '?')}/100 · NO verificado.",
                  "NO se registra nota. Aplica tu política de transición: pedir la reentrega en V9 o revisarla a mano."]
        if r["avisos"]:
            lineas += ["", "AVISOS:"] + [f"  ⚠ {a}" for a in r["avisos"]]
        return "\n".join(lineas)
    d = r["docente"]
    nombres = " / ".join(x.get("apellido") or x.get("nombre", "") for x in d.get("integrantes", []))
    lineas = [f"TC1 · {d['pareja_id']} · {nombres} · ventana {d.get('ventana') or '?'} · estado: {estado(r).upper()}", ""]
    for etapa, info in d["etapas"].items():
        marca = "✓" if info["puntos"] == info["maximo"] else "⚠"
        lineas.append(f"{etapa} · {info['nombre']:<34} {info['puntos']:>2} / {info['maximo']:<2}  {marca}")
    lineas += ["", f"TOTAL {d['puntaje']:>28} / 100", f"NOTA  {d['nota_exacta']:.2f} → se registra {d['nota_registrada']:.1f}", ""]
    if e:
        lineas.append(f"Manifest estudiante: {e.get('puntaje')}/100 · Revalidación docente: {d['puntaje']}/100 · "
                      + ("COINCIDEN: SÍ" if not r["diferencias"] else "DISCREPANCIA: REVISAR " + ", ".join(r["diferencias"])))
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
        c = d["controles"][next(k for k, v in C.CAPTURA_DE_ITEM.items() if v == etapa)]
        lineas.append(f"  {'✓' if 'PNG de' in c['evidencia'] else '✗'} {nombre}")
    if r.get("capturas_extraidas"):
        lineas.append(f"  para mirarlas: {Path(r['capturas_extraidas'][0]).parent}")
    gate = d["gates"]["sin_secretos"]
    lineas += ["", "SEGURIDAD: " + ("✓ sin secretos detectados." if gate["ok"] else "✗ " + "; ".join(gate["hallazgos"]))]
    if r["avisos"]:
        lineas += ["", "AVISOS DE LA ENTREGA:"] + [f"  ⚠ {a}" for a in r["avisos"]]
    lineas.append(f"\nHuella del manifest: {r['huella_manifest']}")
    return "\n".join(lineas)


def retroalimentacion(r):
    '''Texto para responder a la pareja: puntos por etapa y qué revisar, sin revelar respuestas.'''
    d = r["docente"]
    filas = "\n".join(f"| {e} · {i['nombre']} | {i['puntos']} / {i['maximo']} |" for e, i in d["etapas"].items())
    descuentos = [f"- **{k} · {c['descripcion']}** ({c['puntos']}/{c['maximo']}). {C.FEEDBACK.get(k, '')}"
                  for k, c in d["controles"].items() if not c["ok"]]
    return (f"# TC1 · {d['pareja_id']} · retroalimentación\n\n**Puntaje:** {d['puntaje']}/100 · **nota:** {d['nota_registrada']:.1f}\n\n"
            f"| Etapa | Puntos |\n|---|---:|\n{filas}\n\n"
            + ("## Qué se descontó\n\n" + "\n".join(descuentos) if descuentos else "Sin descuentos.") + "\n")


def _filas_csv(salida):
    archivo = Path(salida) / "notas_tc1.csv"
    if not archivo.exists():
        return {}
    with open(archivo, newline="", encoding="utf-8") as fh:
        return {f.get("clave") or f.get("equipo") or f["pareja"]: f for f in csv.DictReader(fh)}


def registradas(salida):
    '''(clave, equipo, ventana, descarga_utc) ya guardados en notas_tc1.csv: para comparar con revisiones anteriores.'''
    return [(k, f.get("equipo") or k, f.get("ventana"), f.get("descarga_utc"))
            for k, f in _filas_csv(salida).items()] if salida else []


def carpeta_equipo(r, salida):
    '''Carpeta de revisión del equipo: su rótulo; si otro equipo (otros códigos) ya usa ese rótulo, se le agrega la clave.'''
    rotulo, k = equipo(r), clave(r)
    ocupada = any(f.get("equipo") == rotulo and (f.get("clave") or rotulo) != k for f in _filas_csv(salida).values())
    return Path(salida) / (f"{rotulo}_{k[:6]}" if ocupada else rotulo)


def guardar(r, salida):
    salida = Path(salida)
    salida.mkdir(parents=True, exist_ok=True)
    d, pareja, rotulo, k = r["docente"], pareja_de(r), equipo(r), clave(r)
    carpeta = carpeta_equipo(r, salida)
    carpeta.mkdir(parents=True, exist_ok=True)
    (carpeta / "revision.json").write_text(json.dumps(r, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    if d:
        (carpeta / f"retroalimentacion_{pareja}.md").write_text(retroalimentacion(r), encoding="utf-8")
    fila = {"pareja": pareja, "equipo": rotulo, "clave": k, "codigos": " ".join(codigos(r)), "ventana": r.get("ventana") or "",
            "descarga_utc": r.get("descarga_utc") or "", "estado": estado(r),
            "revisado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "huella_manifest": r["huella_manifest"], "avisos": " | ".join(r["avisos"]),
            "discrepancias": " ".join(r["diferencias"])}
    if d:
        fila.update({"puntaje": d["puntaje"], "nota_exacta": d["nota_exacta"], "nota_registrada": d["nota_registrada"],
                     **{k: d["etapas"][k]["puntos"] for k in C.STAGE_MAX},
                     "capturas": "pendientes: " + " ".join(d["pendiente_confirmacion_visual"]) if d["pendiente_confirmacion_visual"] else "confirmadas o ausentes"})
    filas = _filas_csv(salida)
    filas[k] = fila
    with open(salida / "notas_tc1.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNAS_CSV)
        w.writeheader()
        for clave_fila in sorted(filas, key=lambda x: (filas[x].get("equipo") or x, x)):
            w.writerow({c: filas[clave_fila].get(c, "") for c in COLUMNAS_CSV})
    return carpeta


def entregas_en(carpeta):
    '''Cada descarga de Drive (ZIP) o carpeta de pareja dentro de la carpeta del lote.'''
    carpeta = Path(carpeta)
    return sorted([p for p in carpeta.iterdir() if p.suffix.lower() == ".zip" or p.is_dir()], key=lambda p: p.name)


def main():
    ap = argparse.ArgumentParser(description="Revalidador docente del TC1")
    grupo = ap.add_mutually_exclusive_group(required=True)
    grupo.add_argument("--entrega", help="ZIP descargado de Drive, carpeta de la pareja o TC1_Pxx.zip")
    grupo.add_argument("--lote", help="carpeta con todas las descargas de Drive")
    ap.add_argument("--sha-correo")
    ap.add_argument("--capturas", default="", help="E2=ok,E4=ok,E5=no tras mirar las capturas")
    ap.add_argument("--abrir", action="store_true", help="abre las capturas con el visor del sistema")
    ap.add_argument("--salida", default=str(SALIDA_DEFECTO))
    ap.add_argument("--no-guardar", action="store_true")
    a = ap.parse_args()
    requisitos()
    salida = None if a.no_guardar else a.salida
    if a.entrega:
        r = revisar(a.entrega, a.sha_correo, _capturas(a.capturas), salida)
        conflictos([r], registradas(salida))
        print(panel(r))
        if salida:
            print(f"\nRevisión guardada en {guardar(r, salida)} · notas en {Path(salida) / 'notas_tc1.csv'}")
        if a.abrir and hasattr(os, "startfile"):
            for p in r.get("capturas_extraidas", []):
                os.startfile(p)
        return
    resultados, ajenas = [], []
    for entrega in entregas_en(a.lote):
        try:
            resultados.append(revisar(entrega, None, {}, salida))
        except SystemExit as exc:
            ajenas.append((entrega.name, str(exc)))
    conflictos(resultados, [x for x in registradas(salida) if x[0] not in {clave(r) for r in resultados}])
    print(f"{'Equipo':<30} {'Puntaje':<16} Estado")
    for r in resultados:
        if salida:
            guardar(r, salida)
        d = r["docente"]
        nota = f"{d['puntaje']}/100 → {d['nota_registrada']:.1f}" if d else "sin nota"
        print(f"{equipo(r):<30} {nota:<16} {estado(r)}")
        for aviso in r["avisos"]:
            if aviso.startswith(("misma descarga", "comparte la ventana")):
                print(f"{'':<30} ⚠ {aviso}")
    for nombre, motivo in ajenas:
        print(f"{nombre:<30} {'':<16} no es una entrega del TC1 · {motivo}")
    if salida:
        print(f"\nCapturas y retroalimentación por equipo en {salida}. Notas: {Path(salida) / 'notas_tc1.csv'}")
        print("Tras mirar las capturas de cada equipo: --entrega <su descarga> --capturas E2=ok,E4=ok,E5=ok")


if __name__ == "__main__":
    main()
