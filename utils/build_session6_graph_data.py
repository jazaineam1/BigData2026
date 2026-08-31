#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye el extracto relacional de S6 desde los datos reales ya versionados.

La entrada de S6 no es un dataset nuevo desconectado del curso. Primero reconstruye
la bandeja operacional de S5 (1.000 -> 163 -> 77). Después usa los chunks SECOP
históricos para obtener contrataciones adjudicadas de esas entidades y ampliar el
contexto con otras entidades que compartan proveedor.

Salidas:
    Datos/s06_contexto_relacional.csv
    Datos/s06_contexto_relacional_manifest.json
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SMALL = ROOT / "Cuadernos" / "datos" / "secop_chunks" / "prueba_chunk_0000000.csv"
CHUNKS = sorted((ROOT / "Cuadernos" / "datos" / "secop_chunks").glob("secop_chunk_*.csv"))
MENTIONS = ROOT / "Datos" / "entidades_en_noticias_2026.json"
OUT = ROOT / "Datos" / "s06_contexto_relacional.csv"
MANIFEST = ROOT / "Datos" / "s06_contexto_relacional_manifest.json"

HIST_COLS = [
    "entidad", "nit_entidad", "departamento_entidad", "id_del_proceso",
    "referencia_del_proceso", "nombre_del_procedimiento",
    "descripci_n_del_procedimiento", "fecha_de_publicacion", "precio_base",
    "modalidad_de_contratacion", "adjudicado", "nombre_del_proveedor",
    "nit_del_proveedor_adjudicado", "departamento_proveedor",
    "valor_total_adjudicacion", "urlproceso",
]


def clean_text(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def valid_provider(df: pd.DataFrame) -> pd.Series:
    name = df["nombre_del_proveedor"].fillna("").astype(str).str.strip()
    nit = df["nit_del_proveedor_adjudicado"].fillna("").astype(str).str.strip()
    bad = {"", "No Definido", "No definido", "nan", "None"}
    return (
        df["adjudicado"].fillna("").astype(str).str.casefold().eq("si")
        & ~name.isin(bad)
        & ~nit.isin(bad)
    )


def mention_level(n: int) -> str:
    if n >= 20:
        return "alta"
    if n >= 5:
        return "media"
    return "baja"


def main() -> None:
    if not CHUNKS:
        raise SystemExit("No se encontraron secop_chunk_*.csv")

    mentions_raw = json.loads(MENTIONS.read_text(encoding="utf-8"))
    mentions = pd.DataFrame([
        {
            "entidad": clean_text(x.get("entidad")),
            "noticias_entidad": int(x.get("noticias", 0) or 0),
            "nivel_menciones": mention_level(int(x.get("noticias", 0) or 0)),
        }
        for x in mentions_raw
    ])
    if mentions["entidad"].duplicated().any():
        raise SystemExit("entidades_en_noticias contiene entidades duplicadas")

    small = pd.read_csv(SMALL, low_memory=False)
    contexto = mentions.set_index("entidad")
    entidades_prensa = set(contexto.index)
    paso1 = small[small["entidad"].isin(entidades_prensa)]
    paso2 = paso1[
        paso1["modalidad_de_contratacion"].fillna("").astype(str)
        .str.contains("directa", case=False, na=False)
    ]
    respuestas = pd.to_numeric(paso2["respuestas_al_procedimiento"], errors="coerce")
    candidatos = paso2[respuestas.eq(0)].copy()
    if len(paso1) != 163 or len(candidatos) != 77:
        raise SystemExit(f"Baseline S5 cambió: paso1={len(paso1)}, candidatos={len(candidatos)}")

    candidatos = candidatos.merge(mentions, on="entidad", how="left", validate="many_to_one")
    candidate_entities = set(candidatos["entidad"].astype(str))
    candidate_ids = set(candidatos["id_del_proceso"].astype(str))

    seed_parts: list[pd.DataFrame] = []
    for path in CHUNKS:
        df = pd.read_csv(path, usecols=HIST_COLS, low_memory=False)
        mask = valid_provider(df) & df["entidad"].astype(str).isin(candidate_entities)
        if mask.any():
            seed_parts.append(df.loc[mask].copy())
    if not seed_parts:
        raise SystemExit("Ninguna entidad candidata tiene historial adjudicado en los chunks")
    seed = pd.concat(seed_parts, ignore_index=True)
    provider_nits = set(seed["nit_del_proveedor_adjudicado"].astype(str).str.strip())

    connected_parts: list[pd.DataFrame] = []
    for path in CHUNKS:
        df = pd.read_csv(path, usecols=HIST_COLS, low_memory=False)
        mask = valid_provider(df) & df["nit_del_proveedor_adjudicado"].astype(str).str.strip().isin(provider_nits)
        if mask.any():
            connected_parts.append(df.loc[mask].copy())
    historical = pd.concat(connected_parts, ignore_index=True)
    historical = historical.drop_duplicates(["id_del_proceso", "nit_del_proveedor_adjudicado"])

    # Los 77 candidatos se conservan aunque todavía no tengan proveedor: son el ancla de Laura.
    candidate_rows = candidatos.copy()
    for col in HIST_COLS:
        if col not in candidate_rows:
            candidate_rows[col] = ""
    candidate_rows["nombre_del_proveedor"] = ""
    candidate_rows["nit_del_proveedor_adjudicado"] = ""
    candidate_rows["departamento_proveedor"] = ""
    candidate_rows["valor_total_adjudicacion"] = pd.NA
    candidate_rows["adjudicado"] = candidate_rows["adjudicado"].fillna("")

    historical = historical.merge(mentions, on="entidad", how="left")
    historical["noticias_entidad"] = historical["noticias_entidad"].astype("Int64")
    historical["nivel_menciones"] = historical["nivel_menciones"].fillna("")

    def standardize(df: pd.DataFrame, kind: str) -> pd.DataFrame:
        out = pd.DataFrame({
            "tipo_registro": kind,
            "entidad": df["entidad"].map(clean_text),
            "nit_entidad": df["nit_entidad"].map(clean_text),
            "departamento_entidad": df["departamento_entidad"].map(clean_text),
            "id_proceso": df["id_del_proceso"].map(clean_text),
            "referencia": df["referencia_del_proceso"].map(clean_text),
            "nombre_proceso": df["nombre_del_procedimiento"].map(clean_text),
            "descripcion": df["descripci_n_del_procedimiento"].map(clean_text),
            "fecha_publicacion": df["fecha_de_publicacion"].map(clean_text),
            "precio_base": pd.to_numeric(df["precio_base"], errors="coerce"),
            "modalidad": df["modalidad_de_contratacion"].map(clean_text),
            "adjudicado": df["adjudicado"].map(clean_text),
            "proveedor": df["nombre_del_proveedor"].map(clean_text),
            "nit_proveedor": df["nit_del_proveedor_adjudicado"].map(clean_text),
            "departamento_proveedor": df["departamento_proveedor"].map(clean_text),
            "valor_adjudicado": pd.to_numeric(df["valor_total_adjudicacion"], errors="coerce"),
            "url_secop": df["urlproceso"].map(clean_text),
            "noticias_entidad": pd.to_numeric(df["noticias_entidad"], errors="coerce").astype("Int64"),
            "nivel_menciones": df["nivel_menciones"].map(clean_text),
        })
        out["es_proceso_candidato_s05"] = out["id_proceso"].isin(candidate_ids)
        out["es_entidad_candidata_s05"] = out["entidad"].isin(candidate_entities)
        return out

    graph = pd.concat([
        standardize(candidate_rows, "candidato_s05"),
        standardize(historical, "historico_adjudicado"),
    ], ignore_index=True)
    graph = graph.drop_duplicates(["tipo_registro", "id_proceso", "nit_proveedor"])
    graph.to_csv(OUT, index=False, encoding="utf-8")

    hist = graph[graph["tipo_registro"].eq("historico_adjudicado")].copy()
    provider_entity_counts = hist.groupby("nit_proveedor")["nit_entidad"].nunique()
    shared_provider_nits = set(provider_entity_counts[provider_entity_counts.ge(2)].index)

    candidate_hist = hist[hist["es_entidad_candidata_s05"]].copy()
    per_entity = candidate_hist.groupby(["nit_entidad", "entidad"]).agg(
        procesos_historicos=("id_proceso", "nunique"),
        proveedores=("nit_proveedor", "nunique"),
    ).reset_index()
    shared_counts = (
        candidate_hist[candidate_hist["nit_proveedor"].isin(shared_provider_nits)]
        .groupby(["nit_entidad", "entidad"])["nit_proveedor"].nunique()
        .rename("proveedores_compartidos")
        .reset_index()
    )
    per_entity = per_entity.merge(shared_counts, on=["nit_entidad", "entidad"], how="left")
    per_entity["proveedores_compartidos"] = per_entity["proveedores_compartidos"].fillna(0).astype(int)
    per_entity = per_entity.sort_values(
        ["proveedores_compartidos", "procesos_historicos", "proveedores"],
        ascending=[False, False, False],
    )

    if per_entity.empty:
        raise SystemExit("No hay contexto histórico para ninguna entidad candidata")
    recommended = per_entity.iloc[0]
    candidate_for_recommended = candidatos[
        candidatos["nit_entidad"].astype(str).str.strip().eq(str(recommended["nit_entidad"]).strip())
    ].sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])
    if candidate_for_recommended.empty:
        candidate_for_recommended = candidatos[candidatos["entidad"].eq(recommended["entidad"])]
    anchor = candidate_for_recommended.iloc[0]

    manifest = {
        "version": "s06-v1",
        "fuente": "bandeja S05 + chunks SECOP versionados",
        "regla_s05": "1.000→163→77",
        "filas_total": int(len(graph)),
        "candidatos_s05": int(graph["tipo_registro"].eq("candidato_s05").sum()),
        "historicos_adjudicados": int(len(hist)),
        "entidades_candidatas_s05": int(len(candidate_entities)),
        "entidades_candidatas_con_historial": int(per_entity.shape[0]),
        "proveedores_historicos": int(hist["nit_proveedor"].nunique()),
        "proveedores_compartidos_entre_entidades": int(len(shared_provider_nits)),
        "ancla_pedagogica": {
            "id_proceso": clean_text(anchor["id_del_proceso"]),
            "entidad": clean_text(anchor["entidad"]),
            "nit_entidad": clean_text(anchor["nit_entidad"]),
            "departamento": clean_text(anchor["departamento_entidad"]),
            "noticias_entidad": int(anchor["noticias_entidad"]),
            "nivel_menciones": clean_text(anchor["nivel_menciones"]),
            "procesos_historicos": int(recommended["procesos_historicos"]),
            "proveedores": int(recommended["proveedores"]),
            "proveedores_compartidos": int(recommended["proveedores_compartidos"]),
        },
        "limite": "Una conexión contractual describe relaciones registradas; no demuestra irregularidad, favorecimiento ni colusión.",
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print("[OK] S6 datos:", OUT.relative_to(ROOT))
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
