"""Panel de investigación didáctico. Carga SÓLO predicciones de prueba real."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent / "salidas" / "modelo_20k"
st.set_page_config(page_title="Compras Claras | ML distribuido", layout="wide")
st.title("Compras Claras · Laboratorio de presupuestos")
st.caption("SECOP II · Entrenamiento XGBoost con Dask · Revisión estadística, nunca juicio sobre legalidad")

manifest_path = BASE / "manifiesto.json"
pred_path = BASE / "procesos_revision.csv"
if not manifest_path.is_file() or not pred_path.is_file():
    st.info("Aún no hay resultados reales. En la terminal de Codespaces ejecuta:")
    st.code(
        "python Laboratorios/S13_Codespaces/modelo_distribuido_20k.py --rondas 30",
        language="bash"
    )
    st.stop()

@st.cache_data
def cargar_resultados(mtime):
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    tabla = pd.read_csv(pred_path)
    return m, tabla

manifest, datos = cargar_resultados((manifest_path.stat().st_mtime,
                                     pred_path.stat().st_mtime))
m1, m2, m3, m4 = st.columns(4)
m1.metric("Fichas reales", f'{manifest["observaciones_unicas"]:,}')
m2.metric("Entrenamiento", f'{manifest["entrenamiento"]:,}')
m3.metric("Prueba temporal", f'{manifest["prueba"]:,}')
m4.metric("Workers Dask", manifest["workers"])

st.warning(
    "Estas son discrepancias entre un modelo estadístico y los precios base publicados. "
    "NO constituyen evidencia de sobrecosto, delito, fraude ni irregularidad."
)

st.subheader("¿Ayudaron las variables y el texto?")
filas = []
for nombre, valores in manifest["metricas"].items():
    filas.append({
        "Modelo": nombre.replace("_", " "),
        "MAE log (menor mejor)": valores["mae_log"],
        "Factor mediano (menor mejor)": valores["factor_error_mediano"],
        "Dentro del factor ×2 (%)": valores["porcentaje_dentro_factor_2"],
    })
st.dataframe(pd.DataFrame(filas), hide_index=True, use_container_width=True)

st.subheader("Explorar los procesos del conjunto de prueba")
col1, col2, col3 = st.columns([2, 1, 1])
modalidades = sorted(datos["modalidad_de_contratacion"].fillna("").unique())
opcion = col1.selectbox("Modalidad", ["Todas"] + modalidades)
umbral = col2.slider("Factor mínimo de discrepancia", 1.0, 10.0, 2.0, 0.5)
solo_revisar = col3.checkbox("Solo factor ≥3", value=False)
filtrado = datos.copy()
if opcion != "Todas":
    filtrado = filtrado[filtrado["modalidad_de_contratacion"] == opcion]
filtrado = filtrado[filtrado["factor_discrepancia"] >= umbral]
if solo_revisar:
    filtrado = filtrado[filtrado["requiere_revision_estadistica"] == True]
filtrado = filtrado.sort_values("factor_discrepancia", ascending=False)
st.write(f"**{len(filtrado):,} procesos** del conjunto de prueba cumplen el filtro.")

if not filtrado.empty:
    grafica = filtrado.copy()
    grafica["log10_precio_real"] = np.log10(
        np.maximum(grafica["precio_objetivo"], 1)
    )
    grafica["log10_precio_estimado"] = np.log10(
        np.maximum(grafica["precio_estimado_cop"], 1)
    )
    st.scatter_chart(grafica, x="log10_precio_real",
                     y="log10_precio_estimado", height=340,
                     use_container_width=True)
    st.caption(
        "Cada punto es un proceso de prueba. Ejes logarítmicos base 10: "
        "estar cerca de la diagonal indica proximidad de magnitud."
    )
    columnas = [
        "id_del_proceso", "entidad", "modalidad_de_contratacion",
        "precio_objetivo", "precio_estimado_cop",
        "factor_discrepancia", "urlproceso",
    ]
    st.dataframe(
        filtrado[columnas].head(150),
        hide_index=True,
        use_container_width=True,
        column_config={
            "urlproceso": st.column_config.LinkColumn(
                "Expediente público SECOP",
                help="Abre la fuente oficial para contrastar, no una etiqueta de fraude",
            ),
            "precio_objetivo": st.column_config.NumberColumn(
                "Precio base publicado (COP)", format="%.0f"
            ),
            "precio_estimado_cop": st.column_config.NumberColumn(
                "Estimación modelo (COP)", format="%.0f"
            ),
        },
    )
    elegido = st.selectbox("Examinar una ficha",
                            filtrado["id_del_proceso"].head(150).tolist())
    ficha = filtrado[filtrado["id_del_proceso"] == elegido].iloc[0]
    st.markdown(f'**Proceso:** \`{elegido}\`')
    a, b, c = st.columns(3)
    a.metric("Precio base SECOP", f'COP ${ficha["precio_objetivo"]:,.0f}')
    b.metric("Estimación modelo", f'COP ${ficha["precio_estimado_cop"]:,.0f}')
    c.metric("Diferencia de magnitud", f'{ficha["factor_discrepancia"]:,.2f} ×')
    if isinstance(ficha["urlproceso"], str) and ficha["urlproceso"].startswith("https://"):
        st.link_button("Ver fuente original en SECOP", ficha["urlproceso"])
else:
    st.info("El filtro no devuelve casos; reduce el umbral o elige otra modalidad.")

with st.expander("Transparencia y límites"):
    st.write(
        "La predicción usa características publicadas de los procesos. "
        "No conoce calidad del bien, cantidades, contexto de mercado, decisiones "
        "legales ni ejecución real. Son fichas SECOP, no PDF. "
        "El conjunto de prueba es posterior al periodo de entrenamiento."
    )
    st.json({
        "fuentes": manifest["archivos_fuente"],
        "corte_temporal": [manifest["fecha_maxima_entrenamiento"],
                          manifest["fecha_minima_prueba"]],
        "rondas": manifest["rondas_xgboost"],
        "trabajadores": manifest["workers"],
        "nodos_fisicos": manifest["nodos_fisicos"],
    })
