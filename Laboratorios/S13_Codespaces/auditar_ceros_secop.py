"""Auditoría SECOP II sin presuposiciones sobre los ceros ni los estados.

Este programa lee TODOS los CSV secop_chunk_*.csv en lotes y distingue:
- cero literal, vacío, inválido, positivo y negativo;
- cero en conteo_de_respuestas_a_ofertas ≠ ausencia comprobada de ofertas;
- estado/fase/fecha/modalidad de cada observación;
- sesgo de los PRIMEROS 26000 elegidos por el modelo anterior.
La auditoría NO etiqueta fraude, sobrecostos ni información faltante a partir de 0.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
DIR=ROOT/"Cuadernos/datos/secop_chunks"
OUTPUT=Path(__file__).resolve().parent/"salidas"/"auditoria_ceros_secop.json"
FILES=sorted(DIR.glob("secop_chunk_*.csv"))
COLS=[
  "id_del_proceso","precio_base","conteo_de_respuestas_a_ofertas",
  "respuestas_al_procedimiento","proveedores_unicos_con","estado_del_procedimiento",
  "fase","modalidad_de_contratacion","adjudicado","valor_total_adjudicacion",
  "fecha_de_publicacion_del","descripci_n_del_procedimiento",
  "tipo_de_contrato","unidad_de_duracion",
]

def summary_counter(c, top=18):
    return {str(k):int(v) for k,v in c.most_common(top)}

def execute(sample_max=26000):
    if not FILES:
        raise FileNotFoundError("No están los secop_chunk_*.csv originales.")
    n=0
    byfile=Counter(); zero_status=Counter(); zero_phase=Counter()
    zero_modality=Counter(); nonzero_modality=Counter()
    offer_zero_status=Counter(); offer_zero_phase=Counter()
    zero_bid_selected=0; zero_bid_adjudicado=0
    price_zero_awarded=0; price_zero_with_award_money=0
    prices=Counter(); offers=Counter(); responded=Counter()
    years_all=Counter(); years_early=Counter()
    mode_all=Counter(); mode_early=Counter()
    selected=0; duplicate_selected=0; seen_selected=set()
    all_ids=set(); dupe_all=0; blank_ids=0
    selected_year_all=Counter(); selected_year_early=Counter()
    dates_parse_fail=0
    price_sample_by_class=defaultdict(list)
    descriptions_money_hint=Counter()
    for file in FILES:
        for frame in pd.read_csv(
            file,usecols=COLS,dtype=str,keep_default_na=False,
            chunksize=5000,encoding="utf-8",encoding_errors="replace",
        ):
            n+=len(frame)
            byfile[file.name]+=len(frame)
            price_raw=frame["precio_base"].str.strip()
            price_num=pd.to_numeric(price_raw,errors="coerce")
            bids_raw=frame["conteo_de_respuestas_a_ofertas"].str.strip()
            bids_num=pd.to_numeric(bids_raw,errors="coerce")
            responses_num=pd.to_numeric(frame["respuestas_al_procedimiento"],errors="coerce")
            prices.update({
                "literal_0":int(price_raw.eq("0").sum()),
                "vacio":int(price_raw.eq("").sum()),
                "negativo":int(price_num.lt(0).sum()),
                "positivo":int(price_num.gt(0).sum()),
                "numerico_cero":int(price_num.eq(0).sum()),
                "no_numerico":int(price_num.isna().sum()-price_raw.eq("").sum()),
                "superior_1e13":int(price_num.gt(1e13).sum()),
            })
            offers.update({
                "numerico_cero":int(bids_num.eq(0).sum()),
                "vacio":int(bids_raw.eq("").sum()),
                "positivo":int(bids_num.gt(0).sum()),
                "no_numerico":int(bids_num.isna().sum()-bids_raw.eq("").sum()),
            })
            responded.update({
                "respuesta_procedimiento_positiva":int(responses_num.gt(0).sum()),
                "cero_respuestas_a_ofertas_con_respuestas_procedimiento_positivas":
                  int((bids_num.eq(0)&responses_num.gt(0)).sum()),
            })
            mask_p0=price_num.eq(0)
            mask_b0=bids_num.eq(0)
            mask_award=frame["adjudicado"].str.strip().str.lower().isin(["si","sí"])
            award_num=pd.to_numeric(frame["valor_total_adjudicacion"],errors="coerce")
            price_zero_awarded+=int((mask_p0 & mask_award).sum())
            price_zero_with_award_money+=int((mask_p0 & award_num.gt(0)).sum())
            zero_bid_selected+=int((mask_b0 & frame["estado_del_procedimiento"].eq("Seleccionado")).sum())
            zero_bid_adjudicado+=int((mask_b0 & mask_award).sum())
            zero_status.update(frame.loc[mask_p0,"estado_del_procedimiento"].tolist())
            zero_phase.update(frame.loc[mask_p0,"fase"].tolist())
            zero_modality.update(frame.loc[mask_p0,"modalidad_de_contratacion"].tolist())
            nonzero_modality.update(frame.loc[price_num.gt(0),"modalidad_de_contratacion"].tolist())
            offer_zero_status.update(frame.loc[mask_b0,"estado_del_procedimiento"].tolist())
            offer_zero_phase.update(frame.loc[mask_b0,"fase"].tolist())
            years=frame["fecha_de_publicacion_del"].str[:4]
            years_all.update(years.tolist())
            mode_all.update(frame["modalidad_de_contratacion"].tolist())
            for idv in frame["id_del_proceso"].astype(str):
                k=idv.strip()
                if not k: blank_ids+=1
                elif k in all_ids: dupe_all+=1
                else: all_ids.add(k)
            desc=frame["descripci_n_del_procedimiento"].str.strip()
            # Esto sólo indica "texto con cifra" y posible fuga, no prueba que revele precio base.
            has_millions=desc.str.contains(
                r"(?i)(\b\$\s*\d{5,}|\b\d[\d.,]{5,}\b|millones\s+de\s+pesos|valor\s+estimado|presupuesto)",
                regex=True,na=False,
            )
            descriptions_money_hint.update({
                "descripcion_con_pista_monetaria":int(has_millions.sum()),
                "descripcion_con_pista_y_precio_valido":int((has_millions & price_num.gt(0)).sum()),
            })
            for year,mod,pr,desc0,id0,date0 in zip(
                years,frame["modalidad_de_contratacion"],price_num,
                desc,frame["id_del_proceso"],frame["fecha_de_publicacion_del"],
            ):
                if selected>=sample_max: continue
                # reproducir exactamente el procedimiento anterior para exponer sesgo de selección
                date=pd.to_datetime(date0,errors="coerce",format="mixed")
                eligible=(pd.notna(pr) and np.isfinite(pr) and pr>0 and pr<=1e13
                          and pd.notna(date) and bool(desc0))
                if eligible and id0.strip() and id0 not in seen_selected:
                    seen_selected.add(id0);selected+=1
                    years_early.update([year]);mode_early.update([mod])
                elif eligible and id0 in seen_selected:
                    duplicate_selected+=1
    def rates(numerator,denom):
        return round(100*numerator/denom,3) if denom else None
    result={
        "veredicto":"EXPLORATORIO: NO INTERPRETAR 0 COMO CERO OFERTAS CONFIRMADAS, NI RESIDUALES COMO ANOMALIAS REALES",
        "fuentes":[p.name for p in FILES],
        "filas_totales":n,
        "filas_por_archivo":dict(byfile),
        "ids_unicos_no_vacios":len(all_ids),
        "ids_duplicados":dupe_all,
        "ids_vacios":blank_ids,
        "precio_base":{
            **dict(prices),
            "porcentaje_cero":rates(prices["numerico_cero"],n),
            "cero_con_adjudicado_si":price_zero_awarded,
            "cero_con_valor_adjudicado_positivo":price_zero_with_award_money,
            "estados_cero":summary_counter(zero_status),
            "fases_cero":summary_counter(zero_phase),
            "modalidades_cero":summary_counter(zero_modality),
            "modalidades_positivas":summary_counter(nonzero_modality),
        },
        "conteo_respuestas_a_ofertas":{
            **dict(offers),
            "porcentaje_cero":rates(offers["numerico_cero"],n),
            "cero_y_estado_seleccionado":zero_bid_selected,
            "cero_y_adjudicado_si":zero_bid_adjudicado,
            "estados_cero":summary_counter(offer_zero_status),
            "fases_cero":summary_counter(offer_zero_phase),
            "advertencia":"No equivale a numero confirmado de oferentes: fases y semantica distintas",
        },
        "respuestas_al_procedimiento":dict(responded),
        "descripcion_pista_precio":dict(descriptions_money_hint),
        "distribucion_poblacion":{
            "anios":summary_counter(years_all,20),
            "modalidades":summary_counter(mode_all,20),
        },
        "seleccion_vieja":{
            "n_elegidos":selected,
            "duplicados_en_proceso":duplicate_selected,
            "anios":summary_counter(years_early,20),
            "modalidades":summary_counter(mode_early,20),
            "advertencia":"Se tomaron los PRIMEROS registros validos de archivos ordenados por nombre; no es muestreo representativo ni por fecha",
        },
        "advertencias":[
            "Los ceros deben explicarse con reglas de cada modalidad y fase; no imputarlos",
            "El precio_base es valor publicado/estimado, no precio justo ni costo de mercado",
            "No interpretar residuos como fraude, sobrecostos ni irregularidades",
            "Si el texto revela cifras del presupuesto, la comparacion con TF-IDF puede tener fuga",
            "La muestra antigua de 26k excluye valores cero y no identifica porque",
        ],
    }
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    OUTPUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print("AUDITORÍA COMPLETA SECOP (sin imputar ceros)")
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--muestra",type=int,default=26000)
    args=p.parse_args()
    execute(args.muestra)
