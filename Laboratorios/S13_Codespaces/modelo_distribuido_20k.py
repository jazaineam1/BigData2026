"""Laboratorio S13 ampliado: presupuesto de referencia con >=20.000 procesos de entrenamiento.

Un UNICO modelo XGBoost se entrena con xgboost.dask sobre particiones en
DOS workers locales de GitHub Codespaces (no dos maquinas fisicas).

Fuente: tres CSV grandes SECOP II ya versionados en Cuadernos/datos/secop_chunks.
No descarga documentos ni inventa contratos. No clasifica fraude/irregularidades.

Ejecucion: python Laboratorios/S13_Codespaces/modelo_distribuido_20k.py
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
import time
from pathlib import Path

import dask.array as da
import numpy as np
import pandas as pd
import xgboost as xgb
from dask.distributed import Client, LocalCluster
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[2]
SALIDAS = Path(__file__).resolve().parent / "salidas" / "modelo_20k"
FUENTES = sorted((ROOT / "Cuadernos/datos/secop_chunks").glob("secop_chunk_*.csv"))
OBJETIVO = 26000           # Con 80 % entrenamiento: 20.800 procesos reales
ENTRENAMIENTO_MINIMO = 20000
COLUMNAS = [
    "id_del_proceso", "fecha_de_publicacion_del", "precio_base",
    "modalidad_de_contratacion", "departamento_entidad", "tipo_de_contrato",
    "codigo_principal_de_categoria", "duracion", "unidad_de_duracion",
    "ordenentidad", "nombre_del_procedimiento",
    "descripci_n_del_procedimiento", "urlproceso", "entidad",
]
NUMERICAS = ["duracion_log", "mes_publicacion", "longitud_descripcion"]
CATEGORICAS = [
    "modalidad_de_contratacion", "departamento_entidad", "tipo_de_contrato",
    "categoria_sector", "unidad_de_duracion", "ordenentidad",
]
TEXTO = "descripci_n_del_procedimiento"


def cargar_procesos(objetivo: int = OBJETIVO):
    """Muestrea todo el universo elegible; ceros registrados, nunca imputados.

    El cero del precio puede ser un valor legítimo o ausencia de valor según
    modalidad y fase; el modelo NO lo interpreta como precio cero observado.
    """
    if not FUENTES:
        raise FileNotFoundError("Faltan los CSV SECOP versionados.")
    if objetivo < 1:
        raise ValueError("Objetivo debe ser positivo")
    reservorio = []
    rng = random.Random(42)
    vistos = set()
    usados = []
    elegibles = 0
    filas_analizadas = 0
    descartes = {
        "precio_cero": 0, "precio_negativo": 0,
        "precio_no_numerico": 0, "precio_superior_1e13": 0,
        "fecha_invalida": 0, "descripcion_vacia": 0,
        "id_duplicado_o_vacio": 0,
    }
    for ruta in FUENTES:
        usados.append(ruta)
        for fragmento in pd.read_csv(
            ruta, usecols=COLUMNAS, dtype=str, keep_default_na=False,
            chunksize=5000, encoding="utf-8", encoding_errors="replace",
            on_bad_lines="error",
        ):
            filas_analizadas += len(fragmento)
            precio = pd.to_numeric(fragmento["precio_base"], errors="coerce")
            fechas = pd.to_datetime(
                fragmento["fecha_de_publicacion_del"], errors="coerce",
                format="mixed",
            )
            texto_ok = fragmento[TEXTO].str.strip().ne("")
            descartes["precio_cero"] += int(precio.eq(0).sum())
            descartes["precio_negativo"] += int(precio.lt(0).sum())
            descartes["precio_no_numerico"] += int(precio.isna().sum())
            descartes["precio_superior_1e13"] += int(precio.gt(1e13).sum())
            descartes["fecha_invalida"] += int(fechas.isna().sum())
            descartes["descripcion_vacia"] += int((~texto_ok).sum())
            valido = precio.gt(0) & precio.le(1e13) & np.isfinite(precio)
            valido &= fechas.notna() & texto_ok
            buenas = fragmento.loc[valido].copy()
            buenas["precio_objetivo"] = precio.loc[valido].astype(float)
            buenas["fecha"] = fechas.loc[valido]
            for fila in buenas.to_dict(orient="records"):
                clave = str(fila["id_del_proceso"]).strip()
                if not clave or clave in vistos:
                    descartes["id_duplicado_o_vacio"] += 1
                    continue
                vistos.add(clave)
                elegibles += 1
                if len(reservorio) < objetivo:
                    reservorio.append(fila)
                else:
                    indice = rng.randrange(elegibles)
                    if indice < objetivo:
                        reservorio[indice] = fila
    if len(reservorio) < objetivo:
        raise RuntimeError(
            f"No hay {objetivo:,} fichas validas unicas; "
            f"encontradas: {len(reservorio):,}. No inventar datos."
        )
    datos = pd.DataFrame(reservorio).sort_values(
        ["fecha", "id_del_proceso"], kind="stable"
    ).reset_index(drop=True)
    assert len(datos) == objetivo and datos["id_del_proceso"].is_unique
    return datos, {
        "archivos_fuente": [str(p.relative_to(ROOT)) for p in usados],
        "filas_analizadas": filas_analizadas,
        "universo_elegible_unico": elegibles,
        "semilla_muestreo": 42,
        "metodo_muestreo": "reservorio reproducible sobre TODO el universo elegible",
        "precios_cero_sin_imputar": descartes["precio_cero"],
        "descartes_revisar": descartes,
        "fichas_validas": len(datos),
        "limitacion": "Muestra de fichas publicadas, no precio justo de mercado.",
    }

def crear_variables(tabla: pd.DataFrame) -> pd.DataFrame:
    """Variables para REGRESIÓN EXPLORATORIA, NO estimación de precio justo."""
    df = tabla.copy()
    duracion = pd.to_numeric(df["duracion"], errors="coerce")
    df["duracion_log"] = np.log1p(duracion.clip(lower=0, upper=100000))
    df["mes_publicacion"] = pd.to_datetime(df["fecha"]).dt.month.astype(float)
    df["longitud_descripcion"] = df[TEXTO].str.len().clip(0, 3000).astype(float)
    # Códigos UNSPSC vienen como V1.80111600. Los primeros 2 dígitos
    # CORRECTOS son 80; eliminar TODOS los no dígitos daba 18 (ERROR grave).
    codigos = df["codigo_principal_de_categoria"].astype(str).str.strip()
    segmento = codigos.str.extract(
        r"^(?:V[0-9]+\.)?([0-9]{8})$", expand=False
    )
    df["categoria_sector"] = segmento.str[:2].fillna("Sin categoria")
    for columna in CATEGORICAS:
        df[columna] = df[columna].replace("", "No informado").astype(str)
    return df


def corte_temporal(datos: pd.DataFrame, proporcion=0.8):
    """Periodo antiguo para entrenar; periodo mas reciente para evaluar."""
    datos = datos.sort_values(["fecha", "id_del_proceso"], kind="stable")
    corte = int(len(datos) * proporcion)
    train = datos.iloc[:corte].copy()
    test = datos.iloc[corte:].copy()
    if train["id_del_proceso"].isin(test["id_del_proceso"]).any():
        raise ValueError("Fuga por ID entre entrenamiento y prueba.")
    if len(train) < ENTRENAMIENTO_MINIMO:
        raise ValueError(
            f"Entrenamiento real insuficiente: {len(train)} < {ENTRENAMIENTO_MINIMO}"
        )
    if train["fecha"].max() > test["fecha"].min():
        raise ValueError("La particion temporal es incorrecta.")
    return train, test


def variables_estructuradas(train, test):
    """Ajusta codificadores SOLO con train, nunca con test."""
    esquema = ColumnTransformer(
        transformers=[
            ("numericas", SimpleImputer(strategy="median"), NUMERICAS),
            ("categoricas", OneHotEncoder(
                handle_unknown="ignore", min_frequency=20,
                sparse_output=False, dtype=np.float32
            ), CATEGORICAS),
        ],
        remainder="drop",
        sparse_threshold=0,
    )
    X_train = np.asarray(esquema.fit_transform(train), dtype="float32")
    X_test = np.asarray(esquema.transform(test), dtype="float32")
    nombres = list(esquema.get_feature_names_out())
    return X_train, X_test, nombres, esquema


def ejes_textuales(train, test, componentes=16):
    """TF-IDF + SVD = ejes latentes de texto; NO embeddings neuronales."""
    texto_train = train[TEXTO].fillna("").astype(str)
    texto_test = test[TEXTO].fillna("").astype(str)
    tfidf = TfidfVectorizer(
        min_df=4, max_features=1800, ngram_range=(1, 2),
        strip_accents="unicode", sublinear_tf=True,
    )
    A = tfidf.fit_transform(texto_train)
    B = tfidf.transform(texto_test)
    if A.shape[1] < componentes + 1:
        raise ValueError("Vocabulario insuficiente para proyeccion de texto.")
    svd = TruncatedSVD(n_components=componentes, random_state=42)
    return (svd.fit_transform(A).astype("float32"),
            svd.transform(B).astype("float32"),
            [f"eje_texto_{i+1:02d}" for i in range(componentes)],
            tfidf, svd)


def crear_dask_arrays(X: np.ndarray, y: np.ndarray, tamano_particion=2500):
    """Las filas se reparten entre trabajadores para entrenar UN solo modelo."""
    X = np.ascontiguousarray(X, dtype=np.float32)
    y = np.asarray(y, dtype=np.float32)
    return (da.from_array(X, chunks=(tamano_particion, X.shape[1])),
            da.from_array(y, chunks=(tamano_particion,)))


def entrenar_xgboost_distribuido(client: Client, X_train, y_train,
                                X_test, nombres, rondas=70):
    """Entrenamiento XGBoost nativo con collective entre workers de Dask."""
    from xgboost import dask as dxgb

    dX, dy = crear_dask_arrays(X_train, y_train)
    dtrain = dxgb.DaskDMatrix(client, dX, dy, feature_names=nombres)
    t0 = time.perf_counter()
    resultado = dxgb.train(
        client,
        {
            "objective": "reg:squarederror",
            "tree_method": "hist",
            "eta": 0.08,
            "max_depth": 5,
            "subsample": 0.85,
            "colsample_bytree": 0.85,
            "nthread": 1,
            "seed": 42,
            "verbosity": 0,
        },
        dtrain, num_boost_round=rondas, evals=[(dtrain, "train")],
    )
    segundos = time.perf_counter() - t0
    booster = resultado["booster"]
    # Predicciones distribuidas a partir de chunks del conjunto de prueba.
    dtest_X, _ = crear_dask_arrays(X_test, np.zeros(len(X_test), dtype="float32"))
    # En la inferencia se conserva el MISMO esquema que en el entrenamiento.
    # Dask Array por si solo no transporta nombres de columnas de XGBoost.
    dtest = dxgb.DaskDMatrix(client, dtest_X, feature_names=nombres)
    pred_log = np.asarray(dxgb.predict(client, booster, dtest).compute())
    return booster, pred_log, segundos, int(dX.npartitions)


def evaluar(y_real_log, y_estimado_log):
    """Error logaritmico interpretable como factor multiplicativo."""
    pred = np.clip(np.asarray(y_estimado_log, dtype=float),
                   0, math.log1p(1e13))
    real = np.asarray(y_real_log, dtype=float)
    factores = np.exp(np.minimum(np.abs(pred - real), 40.0))
    return {
        "mae_log": round(float(mean_absolute_error(real, pred)), 5),
        "factor_error_mediano": round(float(np.median(factores)), 4),
        "porcentaje_dentro_factor_2": round(float(100 * np.mean(factores <= 2)), 2),
        "mae_cop": round(float(mean_absolute_error(
            np.expm1(real), np.expm1(pred))), 2),
    }


def huella(ruta: Path) -> str:
    hash_ = hashlib.sha256()
    with ruta.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(4 * 1024 * 1024), b""):
            hash_.update(bloque)
    return hash_.hexdigest()


def guardar_revision(test, pred_log, destino: Path):
    """Errores del modelo en prueba; no una lista de casos contractual anómalos."""
    pred = np.expm1(np.clip(pred_log, 0, math.log1p(1e13)))
    real = test["precio_objetivo"].to_numpy()
    discrepancia = np.maximum(real / np.maximum(pred, 1),
                              pred / np.maximum(real, 1))
    revision = test[[
        "id_del_proceso", "entidad", "modalidad_de_contratacion",
        "urlproceso", "precio_objetivo",
    ]].copy()
    revision["precio_estimado_cop"] = np.round(pred, 2)
    revision["factor_discrepancia"] = np.round(discrepancia, 2)
    revision["error_modelo_factor_alto"] = discrepancia >= 3
    revision["advertencia"] = (
        "Error de prediccion del modelo experimental; NO es alerta ni prueba de fraude o sobrecosto"
    )
    revision.to_csv(destino, index=False)
    return revision


def ejecutar(objetivo=OBJETIVO, rondas=70, workers=2):
    if workers < 2:
        raise ValueError("Se requieren al menos 2 workers para mostrar el entrenamiento distribuido.")
    SALIDAS.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    datos, procedencia = cargar_procesos(objetivo)
    datos = crear_variables(datos)
    train, test = corte_temporal(datos)
    Xtr, Xte, nombres, esquema = variables_estructuradas(train, test)
    Ttr, Tte, nombres_txt, tfidf, svd = ejes_textuales(train, test)
    Xtr_texto = np.column_stack((Xtr, Ttr)).astype("float32")
    Xte_texto = np.column_stack((Xte, Tte)).astype("float32")
    ytr = np.log1p(train["precio_objetivo"].to_numpy())
    yte = np.log1p(test["precio_objetivo"].to_numpy())

    control = DummyRegressor(strategy="median").fit(Xtr, ytr)
    metricas = {"mediana_control": evaluar(yte, control.predict(Xte))}
    print(f"Proceso de entrenamiento: {len(train):,} fichas. Prueba temporal: {len(test):,}.")
    print(f"Datos estructurados: {Xtr.shape[1]} variables; texto: {Ttr.shape[1]} ejes no neuronales.")
    with LocalCluster(n_workers=workers, threads_per_worker=1, processes=True,
                      memory_limit="1.3GiB", dashboard_address=":8787") as cluster:
        with Client(cluster) as client:
            estado = client.scheduler_info()
            activos = len(estado["workers"])
            if activos < 2:
                raise RuntimeError("No hay dos workers Dask activos.")
            print("Workers Dask:", activos, "| dashboard:", client.dashboard_link)
            modelo_num, pred_num, t_num, particiones_num = entrenar_xgboost_distribuido(
                client, Xtr, ytr, Xte, nombres, rondas=rondas,
            )
            print("Entrenamiento distribuido de variables: OK")
            modelo_txt, pred_txt, t_txt, particiones_txt = entrenar_xgboost_distribuido(
                client, Xtr_texto, ytr, Xte_texto,
                nombres + nombres_txt, rondas=rondas,
            )
            print("Entrenamiento distribuido de texto + variables: OK")

    metricas["xgboost_variables"] = evaluar(yte, pred_num)
    metricas["xgboost_variables_y_texto"] = evaluar(yte, pred_txt)
    revision = guardar_revision(test, pred_txt, SALIDAS / "procesos_revision.csv")
    modelo_num.save_model(SALIDAS / "xgboost_variables.json")
    modelo_txt.save_model(SALIDAS / "xgboost_variables_y_texto.json")
    dump({"esquema": esquema, "tfidf": tfidf, "svd": svd, "variables": nombres,
          "variables_texto": nombres_txt},
         SALIDAS / "transformadores_confiables.joblib")
    # Las observaciones se guardan sin reproducir archivos RAW ni introducir contratos falsos.
    datos[["id_del_proceso", "fecha", "precio_objetivo",
           "modalidad_de_contratacion", TEXTO]].to_parquet(
        SALIDAS / "muestra_26k.parquet", index=False,
    )
    procedencia.update({
        "observaciones_unicas": int(len(datos)),
        "entrenamiento": int(len(train)),
        "prueba": int(len(test)),
        "fecha_maxima_entrenamiento": str(train["fecha"].max()),
        "fecha_minima_prueba": str(test["fecha"].min()),
        "variables_estructuradas": len(nombres),
        "ejes_textuales": len(nombres_txt),
        "workers": workers, "nodos_fisicos": 1,
        "rondas_xgboost": rondas,
        "particiones_entrenamiento": [particiones_num, particiones_txt],
        "segundos_entrenar_variables": round(t_num, 3),
        "segundos_entrenar_variables_texto": round(t_txt, 3),
        "segundos_total": round(time.perf_counter() - t0, 3),
        "fuentes_sha256": {str(p.relative_to(ROOT)): huella(p)
                          for p in FUENTES if str(p.relative_to(ROOT)) in
                          procedencia["archivos_fuente"]},
        "metricas": metricas,
        "errores_modelo_factor_3": int(
            revision["error_modelo_factor_alto"].sum()
        ),
        "advertencia": (
            "SECOP II: fichas de procesos, NO 26000 PDF. "
            "Regresion experimental con cobertura y sesgo de datos no validados. El residual no es una alerta y no demuestra irregularidades. "
            "Dos workers en un solo Codespace, no un cluster multinodo."
        ),
    })
    (SALIDAS / "manifiesto.json").write_text(
        json.dumps(procedencia, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps({
        "procesos": len(datos), "entrenamiento": len(train), "workers": workers,
        "metricas": metricas, "errores_modelo_factor_3":
        int(revision["error_modelo_factor_alto"].sum()),
        "carpeta": str(SALIDAS.relative_to(ROOT)),
    }, ensure_ascii=False, indent=2))
    return procedencia


def main():
    parser = argparse.ArgumentParser(
        description="Entrenar XGBoost realmente distribuido sobre 26k fichas SECOP."
    )
    parser.add_argument("--registros", type=int, default=OBJETIVO)
    parser.add_argument("--rondas", type=int, default=70)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    ejecutar(objetivo=args.registros, rondas=args.rondas, workers=args.workers)


if __name__ == "__main__":
    main()
