"""S13: cuatro operaciones SECOP necesarias para el cuaderno; sin clasificadores."""
from __future__ import annotations
import hashlib
import json
import time
from pathlib import Path
import pandas as pd
import dask.dataframe as dd

ROOT=Path(__file__).resolve().parents[2]
LAB=Path(__file__).resolve().parent
CORPUS=ROOT/"Datos/tc2_corpus_2026.json"
CSV=ROOT/"Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
COL_TEXTO="descripci_n_del_procedimiento"
COL_MODALIDAD="modalidad_de_contratacion"

def leer_corpus():
    with CORPUS.open(encoding="utf-8") as archivo:
        documentos=json.load(archivo)["documentos"]
    tabla=pd.DataFrame(documentos)
    assert len(tabla)==200 and tabla["id_proceso"].is_unique
    return tabla

def leer_etiquetados():
    """Nombre histórico de la función: se usa únicamente para contar modalidades."""
    tabla=pd.read_csv(CSV,low_memory=False)
    requeridas={"id_del_proceso",COL_TEXTO,COL_MODALIDAD}
    assert requeridas.issubset(tabla.columns), "Columnas SECOP faltantes"
    assert len(tabla)==1000, "La muestra SECOP debe contener 1000 filas"
    return tabla

def comparar_pandas_dask(tabla,npartitions=4):
    t0=time.perf_counter()
    pandas_conteos=tabla.groupby(COL_MODALIDAD).size().sort_index()
    tiempo_pandas=time.perf_counter()-t0
    t0=time.perf_counter()
    ddf=dd.from_pandas(tabla,npartitions=npartitions)
    calculado=ddf.groupby(COL_MODALIDAD).size().compute().sort_index()
    tiempo_dask=time.perf_counter()-t0
    referencia={str(k):int(v) for k,v in pandas_conteos.items()}
    resultado={str(k):int(v) for k,v in calculado.items()}
    assert referencia==resultado, "Dask y pandas produjeron diferentes conteos"
    return {"filas":len(tabla),"particiones":ddf.npartitions,
            "conteos":resultado,"segundos_pandas":round(tiempo_pandas,6),
            "segundos_dask":round(tiempo_dask,6),"coinciden":True}

def escribir_resultados(tabla):
    salida=LAB/"salidas"
    salida.mkdir(parents=True,exist_ok=True)
    columnas=["id_del_proceso",COL_TEXTO,COL_MODALIDAD]
    datos=tabla[columnas].drop_duplicates("id_del_proceso").copy()
    destino=salida/"secop_s13.parquet"
    datos.to_parquet(destino,index=False)
    leido=pd.read_parquet(destino)
    assert set(datos["id_del_proceso"])==set(leido["id_del_proceso"])
    sha=hashlib.sha256(CSV.read_bytes()).hexdigest()
    manifiesto={"fuente":str(CSV.relative_to(ROOT)),"sha256_fuente":sha,
                "filas":len(leido),"columnas":columnas,
                "salida":"secop_s13.parquet",
                "uso":"didáctico; no detección de fraude"}
    (salida/"manifest.json").write_text(json.dumps(manifiesto,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifiesto
