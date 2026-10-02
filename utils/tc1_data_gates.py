#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Control de datos del TC1: comprueba, ventana por ventana, que el taller es posible.

Descarga una sola vez, del lado docente, con pausa entre peticiones y User-Agent
identificado, lo mismo que descargará cada pareja (misma consulta, mismo código de
tc1_secop). Para cada ventana verifica los umbrales del contrato:

- E1: procesos cruzados con contratos >= MIN_MATCHED_PROCESSES
- E4: la partición de prueba tiene >= MIN_PARTICION_E4 filas
- E5: la ancla tiene >= MIN_COMPARTIDOS_ANCLA proveedores compartidos y conecta con
      >= MIN_OTRAS_ENTIDADES entidades

Uso:
    python utils/tc1_data_gates.py --cache <carpeta> [--parejas P01 P02 ...]
                                   [--resumen Datos/tc1_ventanas_resumen.json]
                                   [--fixture P03 --fixture-dir tests/fixtures/tc1]
'''
from __future__ import annotations

import argparse
import gzip
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pandas as pd  # noqa: E402

import tc1_contrato as C  # noqa: E402
import tc1_secop as S  # noqa: E402

S.HEADERS["User-Agent"] = "BigData2026-docente-QA (controles de datos TC1; descarga unica)"


def descargar(pareja, dataset, cache, pausa):
    q = S.plan_consulta(pareja)[dataset]
    total = S.count_rows(q["endpoint"], q["where"])
    n = min(C.TARGET_PROCESOS if dataset == "procesos" else C.TARGET_CONTRATOS, total)
    carpeta = Path(cache) / pareja / dataset
    bajar = S.descargador(pareja, dataset, n, carpeta)
    paginas = {}
    for offset in S.offsets_para(n):
        filas, meta = bajar(offset)
        paginas[offset] = (filas, meta)
        if not meta.get("from_cache"):
            time.sleep(pausa)
    df, _ = S.unir_paginas(paginas, n, q["select"])
    ok, msg = S.validar_cache(carpeta, S.offsets_para(n))
    if not ok:
        raise RuntimeError(f"{pareja}/{dataset}: caché inválido ({msg})")
    return df, total


def evaluar_ventana(pareja, procesos, contratos, totales):
    cruce = S.cruce(procesos, contratos)
    docs = S.construir_documentos(procesos, contratos, C.GRANO_CORRECTO, pareja)
    bandeja = S.ref_bandeja(docs)
    datos = S.datos_cassandra(bandeja)
    anio, dep = S.particion_prueba(datos)
    ref4 = S.ref_cassandra(datos, (anio, dep))
    rel = S.relaciones_grafo(contratos)
    ancla = S.entidad_ancla(rel)
    rank = S.ranking_ancla(rel, ancla["nit_ancla"])
    otras = int(rel[rel["nit_proveedor"].isin(set(rank["nit_proveedor"])) & rel["nit_entidad"].ne(ancla["nit_ancla"])]["nit_entidad"].nunique())
    fp, fc = S.rango_fechas(procesos["fecha_de_publicacion_del"]), S.rango_fechas(contratos["fecha_de_firma"])
    r = {
        "inicio": C.VENTANAS[pareja][0][:10], "fin": C.VENTANAS[pareja][1][:10],
        "procesos": {"total_api": totales["procesos"], "descargados": int(len(procesos)), "unicos": cruce["procesos_unicos"],
                     "fechas": fp},
        "contratos": {"total_api": totales["contratos"], "descargados": int(len(contratos)), "fechas": fc},
        "matched_processes": cruce["matched_processes"], "join_coverage": round(cruce["join_coverage"], 4),
        "consulta_a": S.ref_consulta_a(docs), "bandeja_filas": len(bandeja),
        "particion_e4": {"anio": anio, "departamento": dep, "filas": ref4["count"]},
        "ancla_e5": {"nit": ancla["nit_ancla"], "entidad": ancla["nombre"], "nombres_bajo_nit": ancla["nombres_bajo_nit"],
                     "proveedores_compartidos": ancla["proveedores_compartidos"], "otras_entidades": otras,
                     "puente_max_entidades": int(rank["entidades_conectadas"].max()) if len(rank) else 0},
    }
    r["pasa"] = (r["matched_processes"] >= C.MIN_MATCHED_PROCESSES and ref4["count"] >= C.MIN_PARTICION_E4
                 and ancla["proveedores_compartidos"] >= C.MIN_COMPARTIDOS_ANCLA and otras >= C.MIN_OTRAS_ENTIDADES)
    return r


def guardar_fixture(pareja, procesos, contratos, totales, destino):
    destino = Path(destino)
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, df in (("procesos", procesos), ("contratos", contratos)):
        filas = [{k: v for k, v in fila.items() if not (isinstance(v, float) and pd.isna(v)) and v is not None}
                 for fila in df.to_dict("records")]
        with gzip.open(destino / f"{pareja}_{nombre}.json.gz", "wt", encoding="utf-8") as fh:
            json.dump(filas, fh, ensure_ascii=False)
    (destino / f"{pareja}_totales.json").write_text(json.dumps(totales, indent=2), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cache", required=True)
    ap.add_argument("--parejas", nargs="*", default=C.PAREJAS)
    ap.add_argument("--resumen")
    ap.add_argument("--pausa", type=float, default=0.8)
    ap.add_argument("--fixture", nargs="*", default=[])
    ap.add_argument("--fixture-dir", default="tests/fixtures/tc1")
    a = ap.parse_args()
    resumen = {"generado_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "script": "utils/tc1_data_gates.py", "version": C.VERSION,
               "fuente": "datos.gov.co · SECOP II Procesos (p6dx-8zbt) y Contratos (jbjy-vk9h)",
               "criterios": {"procesos": "primeros 3000 registros desde el inicio de la ventana, orden estable con :id",
                             "contratos": f"primeros 4000 desde el inicio de la ventana con {C.FILTRO_CONTRATOS}",
                             "ancla_e5": "entidad con más proveedores compartidos (desempate: más contratos, NIT)"},
               "umbrales": {"matched_processes": C.MIN_MATCHED_PROCESSES, "particion_e4": C.MIN_PARTICION_E4,
                            "compartidos_ancla": C.MIN_COMPARTIDOS_ANCLA, "otras_entidades": C.MIN_OTRAS_ENTIDADES},
               "ventanas": {}}
    fallan = []
    for pareja in a.parejas:
        procesos, tp = descargar(pareja, "procesos", a.cache, a.pausa)
        contratos, tc = descargar(pareja, "contratos", a.cache, a.pausa)
        totales = {"procesos": tp, "contratos": tc}
        r = evaluar_ventana(pareja, procesos, contratos, totales)
        resumen["ventanas"][pareja] = r
        e5 = r["ancla_e5"]
        print(f"{pareja} {r['inicio']} | días P/C {r['procesos']['fechas'][2]}/{r['contratos']['fechas'][2]} | "
              f"cruzados {r['matched_processes']:>4} | consA {r['consulta_a']:>4} | E4 {r['particion_e4']['filas']:>3} | "
              f"E5 compartidos {e5['proveedores_compartidos']:>3} otras {e5['otras_entidades']:>3} puente {e5['puente_max_entidades']:>2} | "
              f"{'PASA' if r['pasa'] else 'FALLA'} · {e5['entidad'][:40]}", flush=True)
        if not r["pasa"]:
            fallan.append(pareja)
        if pareja in a.fixture:
            guardar_fixture(pareja, procesos, contratos, totales, a.fixture_dir)
            print(f"   fixture guardado en {a.fixture_dir}")
    if a.resumen:
        Path(a.resumen).write_text(json.dumps(resumen, ensure_ascii=False, indent=2), encoding="utf-8")
        print("resumen:", a.resumen)
    print("CONTROL DE DATOS:", "OK" if not fallan else f"FALLA en {fallan}")
    sys.exit(1 if fallan else 0)


if __name__ == "__main__":
    main()
