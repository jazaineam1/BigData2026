"""S13 · Laboratorio interactivo: TF-IDF y datos SECOP reales.

Siete módulos: TF-IDF, búsquedas, Dask realmente ejecutado, costos y transferencia.
Ningún campo de precio es objetivo, ninguna discrepancia es alerta de fraude.
Uso: streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py --server.port 8503
"""
from __future__ import annotations

import json
import math
import re
import hashlib
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import LinearSVC

from benchmark_unspsc_tfidf_dask import ETIQUETAS, CODIGO, texto_limpio
from dask_cuando_si import cpus_disponibles

ROOT=Path(__file__).resolve().parents[2]
CSV=ROOT/"Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
RESULTS=Path(__file__).resolve().parent/"salidas/benchmark_unspsc"

st.set_page_config(page_title="S13 · Taller interactivo TF-IDF",layout="wide")
st.title("S13 · Dask en acción con títulos SECOP")
st.caption("Universidad Central · Big Data · S13 · Workers Dask → TF-IDF y búsqueda · clasificación opcional")
st.info("Muestra SECOP preparada para practicar particiones, concurrencia y representación de texto. "
        "No realizamos depuración administrativa ni interpretaciones jurídicas; la clasificación UNSPSC es opcional.")

@st.cache_data
def cargar():
    columnas=["id_del_proceso","nombre_del_procedimiento",
              "descripci_n_del_procedimiento","codigo_principal_de_categoria",
              "fecha_de_publicacion_del"]
    data=pd.read_csv(CSV,usecols=columnas,dtype=str,keep_default_na=False)
    data=data.drop_duplicates("id_del_proceso")
    data["texto"]=data.apply(
        lambda r:texto_limpio(r["nombre_del_procedimiento"],
                             r["descripci_n_del_procedimiento"]),axis=1)
    data["fecha"]=pd.to_datetime(
        data["fecha_de_publicacion_del"],errors="coerce")
    data["segmento"]=data["codigo_principal_de_categoria"].apply(
        lambda x: CODIGO.fullmatch(x.strip()).group(1)[:2]
        if CODIGO.fullmatch(x.strip()) else "NO IDENTIFICADO")
    return data

@st.cache_resource
def motor_busqueda(textos):
    vec=TfidfVectorizer(max_features=3000,strip_accents="unicode",
                        ngram_range=(1,2),min_df=2)
    m=vec.fit_transform(textos)
    return vec,m

def mini_ejemplo(textos):
    count=CountVectorizer(token_pattern=r"(?u)\b\w+\b")
    matriz=count.fit_transform(textos)
    tabla=pd.DataFrame(matriz.toarray(),columns=count.get_feature_names_out())
    n=len(textos)
    frecuencia_documental=(tabla>0).sum(axis=0)
    idf=np.log((1+n)/(1+frecuencia_documental))+1
    tabla_idf=pd.DataFrame({
        "término":idf.index,
        "DF (documentos que contienen el término)":frecuencia_documental.values,
        "IDF suavizado":np.round(idf.values,4),
    })
    tfidf=TfidfVectorizer(token_pattern=r"(?u)\b\w+\b",
                          use_idf=True,smooth_idf=True,norm="l2")
    w=tfidf.fit_transform(textos)
    pesos=pd.DataFrame(np.round(w.toarray(),4),columns=tfidf.get_feature_names_out())
    return tabla,tabla_idf,pesos

data=cargar()
tabs=st.tabs([
    "1 · Explorar SECOP","2 · Construir TF-IDF",
    "3 · Buscar documentos","4 · Clasificación opcional",
    "5 · Dask y mediciones","6 · Decidir con costos",
    "7 · Evidencia reutilizable",
])

with tabs[0]:
    st.subheader("Los datos preceden al algoritmo")
    c1,c2,c3=st.columns(3)
    c1.metric("Filas de la muestra",len(data))
    c2.metric("IDs únicos",data["id_del_proceso"].nunique())
    c3.metric("Lotes de la práctica Dask",8)
    st.dataframe(data["segmento"].value_counts().rename_axis("Segmento UNSPSC")
                 .reset_index(name="Procesos"),hide_index=True)
    st.markdown(
        "**Qué observamos:** las categorías declaradas son etiquetas administrativas. "
        "El segmento 80 es muy frecuente; una buena exactitud global podría engañar.")
    st.dataframe(data[["id_del_proceso","nombre_del_procedimiento",
                       "segmento","texto"]].head(40),
                 hide_index=True,use_container_width=True)
    with st.expander("Código visible que carga los datos"):
        st.code("""data=pd.read_csv(CSV,dtype=str)
data=data.drop_duplicates("id_del_proceso")
# Verifica CODIGO.fullmatch: V1.80111600 -> 80
# Nunca uses precio_base=0 como etiqueta de fraude.""",language="python")

with tabs[1]:
    st.subheader("TF-IDF paso a paso (sin una caja negra)")
    st.markdown(
        "**TF (frecuencia del término):** cuántas veces aparece una palabra en un documento. "
        "**DF (frecuencia documental):** en cuántos documentos aparece. "
        "**IDF (frecuencia documental inversa):** da menos importancia a palabras comunes.")
    st.latex(r"\mathrm{IDF}(t)=\log\left(\frac{1+N}{1+\mathrm{DF}(t)}\right)+1")
    st.markdown(
        "En scikit-learn, el peso inicial es **TF × IDF** y, por defecto, cada "
        "vector se normaliza a norma L2 igual a 1. Una palabra repetida en todos "
        "los documentos recibe menos peso que una palabra específica.")
    ejemplo=st.text_area(
        "Escribe entre 2 y 8 documentos. Sepáralos con una línea en blanco.",
        value="mantenimiento computadores\n\n"
              "infraestructura computadores\n\n"
              "hospital mantenimiento",
        height=155)
    textos=[s.strip() for s in ejemplo.split("\n\n") if s.strip()][:8]
    if len(textos)<2:
        st.warning("Se necesitan al menos dos documentos.")
    else:
        try:
            conteos,idf,pesos=mini_ejemplo(textos)
            st.write("**A · Contar términos (TF sin normalizar)**")
            st.dataframe(conteos,use_container_width=True)
            st.write("**B · Calcular DF e IDF**")
            st.dataframe(idf,use_container_width=True,hide_index=True)
            st.write("**C · Multiplicar TF × IDF y normalizar L2**")
            st.dataframe(pesos,use_container_width=True)
            st.markdown("**Cómo se lee:** una columna es una palabra; una fila, un documento. "
                        "Un peso cercano a cero significa poca importancia relativa en ese texto. "
                        "No significa que la palabra sea inútil en cualquier corpus.")
        except ValueError as exc:
            st.warning(str(exc))
    with st.expander("Fórmula y Python que puedes reescribir"):
        st.code("""conteos=CountVectorizer().fit_transform(documentos)
idf=np.log((1+N)/(1+DF))+1
TF_IDF=TF*IDF
# Después, cada fila se divide por su norma euclídea:
pesos = TF_IDF/np.sqrt((TF_IDF**2).sum(axis=1))
# TfidfVectorizer implementa y optimiza esta operación.""",language="python")

with tabs[2]:
    st.subheader("¿Qué expediente se parece a tu consulta?")
    subset=data[data["texto"].str.len().ge(20)].head(900).copy()
    consulta=st.text_input("Consulta semántica léxica",
                           value="mantenimiento de equipos de cómputo")
    if consulta.strip():
        vec,m=motor_busqueda(tuple(subset["texto"]))
        q=vec.transform([consulta])
        score=cosine_similarity(q,m).ravel()
        top=np.argsort(score)[::-1][:10]
        salida=subset.iloc[top][["id_del_proceso","nombre_del_procedimiento",
                                  "segmento","texto"]].copy()
        salida.insert(0,"similitud_coseno",np.round(score[top],4))
        st.dataframe(salida,hide_index=True,use_container_width=True)
        st.caption("TF-IDF compara vocabulario, NO entiende automáticamente "
                   "sinónimos como 'computador' y 'ordenador'. "
                   "Ahí podemos contrastar embeddings de EmbeddingGemma 2.")
    with st.expander("Código de búsqueda reproducible"):
        st.code("""vec=TfidfVectorizer(ngram_range=(1,2),min_df=2)
X=vec.fit_transform(descripciones)
q=vec.transform([consulta])
similitud=cosine_similarity(q,X).ravel()
orden=similitud.argsort()[::-1][:10]""",language="python")

with tabs[3]:
    st.subheader("Ampliación opcional · TF-IDF + LinearSVC")
    st.markdown("El propósito central de S13 es repartir trabajo con Dask. Esta clasificación de segmentos UNSPSC se activa sólo cuando quieras estudiarla; no se entrena al abrir el panel.")
    if st.toggle("Activar clasificación opcional", value=False, key="s13_clasificacion_opcional"):
        st.subheader("Un clasificador real: descripción → segmento UNSPSC")
        st.markdown("Primero se separan procesos por fecha; **después** se ajusta el "
                    "vocabulario con entrenamiento. Jamás con prueba.")
        valid=data[(data["texto"].str.len()>=20) &
                   (data["segmento"]!="NO IDENTIFICADO")].sort_values(
                       ["fecha","id_del_proceso"]).copy()
        valid["clase"]=valid["segmento"].where(
            valid["segmento"].isin(["80","85","93","81","72"]),"OTRAS")
        valid=valid[valid["fecha"].notna()]
        corte=int(len(valid)*.8)
        tr,te=valid.iloc[:corte],valid.iloc[corte:]
        if len(tr)>20 and len(te)>5:
            ngramas=st.selectbox(
                "Representación (misma división temporal para comparar)",
                options=[(1,1),(1,2)],index=1,
                format_func=lambda x: "Unigramas" if x==(1,1)
                else "Unigramas y bigramas",
                help="Modifica una sola decisión sin ver ni cambiar el test.",
            )
            v=TfidfVectorizer(max_features=3000,ngram_range=ngramas,
                              min_df=2,strip_accents="unicode")
            xt=v.fit_transform(tr["texto"])
            xte=v.transform(te["texto"])
            clf=LinearSVC(class_weight="balanced",random_state=42)
            clf.fit(xt,tr["clase"])
            pred=clf.predict(xte)
            macro=f1_score(te["clase"],pred,labels=list(ETIQUETAS),
                           average="macro",zero_division=0)
            a,b,c=st.columns(3)
            a.metric("Train",len(tr));b.metric("Test posterior",len(te))
            c.metric("F1 macro",f"{macro:.3f}")
            reporte=classification_report(
                te["clase"],pred,labels=list(ETIQUETAS),
                output_dict=True,zero_division=0)
            st.dataframe(pd.DataFrame(reporte).T,use_container_width=True)
            st.bar_chart(pd.Series({
                x:reporte[x]["f1-score"] for x in ETIQUETAS
            }).rename("F1 por segmento"),y_label="F1 por clase")
            st.caption("F1 macro promedia las categorías por igual; una clase muy "
                       "frecuente no domina la evaluación. Este panel usa sólo "
                       "una muestra pequeña y NO reemplaza el benchmark de 50.000.")
        with st.expander("Cambia el modelo y observa cómo afecta a F1"):
            st.code("""v=TfidfVectorizer(max_features=3000,ngram_range=(1,2))
    X_train=v.fit_transform(textos_train)  # aprender el vocabulario
    X_test=v.transform(textos_test)       # NO ajustar otra vez
    modelo=LinearSVC(class_weight="balanced",random_state=42)
    modelo.fit(X_train,etiquetas_train)
    pred=modelo.predict(X_test)
    f1_macro=f1_score(etiquetas_test,pred,average="macro")""",language="python")

with tabs[4]:
    st.subheader("Dask en acción: ocho lotes SECOP en workers reales")
    st.markdown(
        "**Texto real:** procesar títulos SECOP sin esperas artificiales. "
        "**Espera simulada:** repetir el trabajo y representar 0,6 s de "
        "latencia externa por lote. Son los mismos ocho lotes de entrada; "
        "un worker es un proceso en esta misma VM, no un servidor adicional."
    )
    with st.expander("Ampliación docente · entrenamiento y benchmarks históricos (no obligatorios)", expanded=False):
        st.markdown(
            "Dask también puede repartir entrenamientos independientes, "
            "como los folds de validación cruzada. Eso no significa entrenar "
            "internamente un único modelo LinearSVC de forma distribuida. "
            "Los resultados históricos se obtuvieron en otra VM."
        )
        st.code("""# Ejemplo conceptual; no se ejecuta desde el panel.
futuros=[client.submit(entrenar_un_fold, datos, train, valid, pure=False)
         for train, valid in folds]
metricas=client.gather(futuros)""",language="python")
        for nombre in ["benchmark_50k_test_fijo.json",
                       "cv_linearsvc_local_vs_dask.json",
                       "embgemma_vs_tfidf_1000_real.json"]:
            ruta=RESULTS/nombre
            if ruta.is_file():
                st.markdown(f"**Histórico:** `{nombre}`")
                st.json(json.loads(ruta.read_text(encoding="utf-8")), expanded=False)
            else:
                st.caption(f"No disponible: {nombre}")
    st.markdown(
        "**Dos pruebas sobre el mismo CSV:** la demostración de **espera simulada** "
        "permite observar concurrencia como en una API externa; la opción "
        "**texto real** cuenta términos de títulos SECOP sin tiempos de espera. "
        "La segunda puede ser más lenta con Dask: es una observación válida."
    )
    modo_demo=st.radio(
        "Procesamiento que se ejecutará",
        ["texto", "espera"], horizontal=True,
        format_func=lambda x: "Espera de API simulada" if x=="espera" else "Conteo real de palabras SECOP",
    )
    st.caption("Primero ejecuta Texto real; luego Espera simulada. Pulsa el botón una vez por modo. No hay OCR ni servicios externos.")
    st.code(
        "nproc\n"
        "lscpu | head -25\n"
        "free -h\n"
        "python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2",
        language="bash",
    )
    n_demo=st.selectbox(
        "Workers a utilizar (procesos de 1 hilo)",
        [1, 2, 4], index=1,
        help="Si creas más workers que CPU habilitadas puedes perder rendimiento.",
    )
    st.caption(
        f"CPU habilitadas estimadas (afinidad y cuota cgroups): {cpus_disponibles()}. "
        "Los workers son procesos dentro de una misma VM."
    )
    if n_demo > cpus_disponibles():
        st.warning("Sobresuscripción: se eligieron más workers que CPU disponibles; puede empeorar.")
    st.markdown("**Ruta principal:** ejecuta primero **Texto real**, después **Espera simulada**; en ambos casos Dask coordina procesos reales. La espera no hace OCR.")
    st.code("python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo texto\n"
            "python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo espera",language="bash")
    if st.button("Ejecutar la demostración ligera de Dask", key="demo_real_dask"):
        programa=Path(__file__).resolve().parent/"dask_cuando_si.py"
        try:
            result=subprocess.run(
                [sys.executable, str(programa), "--workers", str(n_demo), "--modo", modo_demo],
                cwd=ROOT, capture_output=True, text=True, timeout=120,
            )
            if result.returncode:
                st.error("Falló Dask; no se presentan tiempos inventados.")
                st.code(result.stderr[-2400:] or result.stdout[-2400:])
            else:
                prefijo="RESULTADO_S13_DASK="
                linea=next((x[len(prefijo):] for x in result.stdout.splitlines()
                            if x.startswith(prefijo)),None)
                if linea is None:
                    st.error("La ejecución terminó sin JSON verificable. Consulta la salida.")
                    st.code(result.stdout[-2400:])
                else:
                    valores=json.loads(linea)
                    if not valores["resultados_identicos"]:
                        st.error("La salida secuencial y distribuida no coincide.")
                    else:
                        st.session_state["s13_ultimo_dask"]=valores
                        almacen=st.session_state.setdefault("s13_modos_ejecutados",{})
                        almacen[modo_demo]=valores
                        st.success("Dask ejecutó tareas y produjo los mismos resultados.")
        except subprocess.TimeoutExpired:
            st.error("El programa superó 120 s; revisa CPU, procesos y RAM.")
    if "s13_ultimo_dask" in st.session_state:
        valores=st.session_state["s13_ultimo_dask"]
        st.markdown(
            f"**Última ejecución comprobada:** {valores['workers']} workers, "
            f"{valores['tareas']} tareas y {valores['filas_procesadas']} títulos. "
            "Los datos se tomaron del Codespace en esta ejecución, no de GitHub Actions."
        )
        c1,c2,c3=st.columns(3)
        c1.metric("Secuencial",f"{valores['segundos_secuencial']:.3f} s")
        c2.metric("Dask caliente",f"{valores['segundos_dask_cluster_caliente']:.3f} s")
        c3.metric("Dask + arranque",f"{valores['segundos_dask_total_incluido_arranque']:.3f} s")
        st.write(
            "Ganador del trabajo:",valores["ganador_caliente"],
            "· ganador incluyendo arranque:",valores["ganador_total"],
        )
        # Cronograma de funciones REAL: se mide dentro de cada proceso Dask de una misma VM.
        traza = valores.get("traza_tareas", [])
        if len(traza) == valores["tareas"]:
            st.markdown("#### Cronograma real de tareas por worker")
            st.caption(
                "Cada barra es un lote ejecutado por un proceso real. Eje horizontal: "
                "milisegundos relativos al primer lote. Esta traza NO incluye cola "
                "del scheduler, transferencia, lectura CSV ni arranque; los "
                "cronómetros globales de arriba sí permiten observar el arranque."
            )
            st.vega_lite_chart(
                pd.DataFrame(traza),
                {
                    "mark": {"type": "bar", "cornerRadiusEnd": 3},
                    "encoding": {
                        "x": {"field": "inicio_ms", "type": "quantitative",
                              "title": "ms desde el inicio de la primera tarea"},
                        "x2": {"field": "fin_ms"},
                        "y": {"field": "worker", "type": "nominal",
                              "title": "Worker real", "sort": "ascending"},
                        "color": {"field": "worker", "type": "nominal", "legend": None},
                        "tooltip": [
                            {"field": "lote", "type": "quantitative", "title": "Lote"},
                            {"field": "worker", "type": "nominal", "title": "Worker"},
                            {"field": "inicio_ms", "type": "quantitative", "title": "Inicio (ms)"},
                            {"field": "fin_ms", "type": "quantitative", "title": "Fin (ms)"},
                            {"field": "duracion_ms", "type": "quantitative", "title": "Duración (ms)"},
                            {"field": "registros", "type": "quantitative", "title": "Títulos"},
                        ],
                    },
                },
                use_container_width=True,
             )
            with st.expander("Ver la tabla exacta de tareas y tiempos medidos"):
                st.dataframe(pd.DataFrame(traza), hide_index=True, use_container_width=True)
        else:
            st.warning("Este JSON no contiene la traza por tarea; ejecuta el script actualizado.")
        st.json(valores,expanded=False)
        st.download_button(
            "Descargar JSON real de mi ejecución",
            data=json.dumps(valores,ensure_ascii=False,indent=2),
            file_name="s13_dask_ejecutado.json",
            mime="application/json", key="descargar_dask_real",
        )
    comparados=st.session_state.get("s13_modos_ejecutados",{})
    if comparados:
        filas=[{
            "Caso":modo,
            "Workers":dato["workers"],
            "Secuencial (s)":dato["segundos_secuencial"],
            "Dask caliente (s)":dato["segundos_dask_cluster_caliente"],
            "Dask con arranque (s)":dato["segundos_dask_total_incluido_arranque"],
            "Tareas verificadas":dato["resultados_identicos"],
            "Ganador con clúster listo":dato["ganador_caliente"],
            "Ganador con arranque":dato["ganador_total"],
        } for modo,dato in comparados.items()]
        st.markdown("**Comparación de tus ejecuciones en este Codespace:**")
        st.dataframe(pd.DataFrame(filas),hide_index=True,use_container_width=True)
        if "texto" in comparados:
            st.write("**Frecuencias reales calculadas por lote:**")
            st.write("Vocabulario por tarea:",comparados["texto"].get("terminos_distintos_por_lote",[]))
            st.write("Tareas ejecutadas por worker:",comparados["texto"].get("tareas_por_worker",{}))
        if len(comparados)<2:
            st.caption("Para comparar los dos escenarios falta ejecutar el otro modo.")
        else:
            st.success("Ambos modos ejecutados. Comparar solo fases equivalentes.")
        st.download_button(
            "Descargar comparación de ambos modos",
            data=json.dumps(comparados,ensure_ascii=False,indent=2),
            file_name="s13_dask_modos_codespace.json",
            mime="application/json",key="s13_descargar_comparacion",
        )
    st.markdown(
        "**Nota:** Dask caliente = workers ya disponibles; Dask total = incluye "
        "iniciar el scheduler y los procesos. Si gana solo caliente, hay una "
        "ventaja de concurrencia reutilizable, no necesariamente de primera ejecución."
    )



    with st.expander("Ampliación opcional · K-means: un modelo entrenado con Dask-ML", expanded=False):
        st.markdown(
            "**Caso SECOP:** texto real → TF-IDF → SVD de 20 variables "
            "→ K-means local y Dask-ML con los mismos centroides iniciales. "
            "Se comparan fases equivalentes; ARI mide acuerdo de grupos, "
            "no calidad semántica. No ejecuta DBSCAN ni 50.000 registros."
        )
        st.code(
            "python Laboratorios/S13_Codespaces/kmeans_dask_s13.py --n 250 --workers 2\n"
            "python Laboratorios/S13_Codespaces/kmeans_dask_s13.py --n 1000 --workers 2",
            language="bash",
        )
        n_kmeans=st.selectbox(
            "Muestra ligera SECOP", [250, 1000], index=0, key="s13_kmeans_n"
        )
        w_kmeans=st.selectbox(
            "Workers para K-means (un hilo por proceso)", [1, 2], index=1,
            key="s13_kmeans_workers",
        )
        if w_kmeans>cpus_disponibles():
            st.warning("Más workers que CPU efectivas: puede ser más lento.")
        if st.button("Entrenar K-means local y Dask (voluntario)",
                     key="s13_kmeans_run"):
            programa=Path(__file__).resolve().parent/"kmeans_dask_s13.py"
            try:
                res=subprocess.run(
                    [sys.executable, str(programa),
                     "--n", str(n_kmeans), "--workers", str(w_kmeans)],
                    cwd=ROOT, capture_output=True, text=True, timeout=240,
                )
                if res.returncode:
                    st.error("El laboratorio K-means no finalizó; no se inventan métricas.")
                    st.code(res.stderr[-2600:] or res.stdout[-1200:])
                else:
                    ruta=Path(__file__).resolve().parent/"salidas/kmeans_s13.json"
                    datos_kmeans=json.loads(ruta.read_text(encoding="utf-8"))
                    st.session_state["s13_kmeans_ejecucion"]=datos_kmeans
                    st.success("Modelo local y modelo Dask-ML entrenados sobre los mismos vectores.")
            except (subprocess.TimeoutExpired, OSError, ValueError) as exc:
                st.error(f"No se completó el laboratorio opcional: {exc}")
        if "s13_kmeans_ejecucion" in st.session_state:
            m=st.session_state["s13_kmeans_ejecucion"]
            tiempos=m["tiempos_segundos"]
            a,b,c=st.columns(3)
            a.metric("Local total",f"{tiempos['pipeline_local_sin_guardado']:.3f} s")
            b.metric("Dask total",f"{tiempos['pipeline_dask_sin_guardado']:.3f} s")
            c.metric("Acuerdo ARI",f"{m['ari_acuerdo_de_grupos']:.3f}")
            st.caption(
                "Tiempos totales: incluyen lectura+TF-IDF+SVD; el de Dask incluye "
                "arranque, persistencia, fit y predicción. No se incluyen escritura del JSON. "
                "Con una matriz pequeña puede ser mejor la ejecución local."
            )
            st.dataframe(pd.DataFrame([
                {"Fase":nombre,"Segundos":valor} for nombre,valor in tiempos.items()
            ]),hide_index=True,use_container_width=True)
            st.write("Tareas observadas durante entrenamiento por worker:",
                     m["tareas_entrenamiento_por_worker"])
            st.write("Workers presentes:",m["workers_reales"])
            st.bar_chart(pd.DataFrame(m["grupos_dask"])[["grupo","cantidad"]].set_index("grupo"))
            st.json(m["grupos_dask"],expanded=False)
            st.download_button(
                "Descargar JSON de K-means medido",
                data=json.dumps(m,ensure_ascii=False,indent=2),
                file_name="s13_kmeans_real.json",
                mime="application/json", key="s13_kmeans_download",
            )

with tabs[5]:
    st.subheader("Simulador de decisión: el clúster también cuesta")
    st.markdown(
        "**Speedup (aceleración)** = tiempo local dividido por tiempo distribuido. "
        "El total distribuido suma el arranque del clúster una sola vez "
        "si lo reutilizas durante varias ejecuciones. Este simulador usa "
        "**supuestos ilustrativos y editables**, no mediciones del Codespace. "
        "Cuando tengas el JSON de tu ejecución, usa sus segundos para sustituirlos."
    )
    observado=st.session_state.get("s13_modos_ejecutados",{}).get("espera")
    if observado:
        st.caption(
            f"Tu última ejecución de ESPERA: secuencial {observado['segundos_secuencial']:.3f} s; "
            f"Dask caliente {observado['segundos_dask_cluster_caliente']:.3f} s; "
            f"arranque {observado['segundos_arranque_y_espera_workers']:.3f} s. "
            "Los controles siguientes son hipótesis para repetir el trabajo, "
            "no reemplazan estos tiempos reales."
        )
    a,b,c=st.columns(3)
    t_local=a.number_input("Local por transformación (s)",min_value=0.001,
                           value=4.8,step=0.1,format="%.4f")
    t_dask=b.number_input("Dask por transformación (s)",min_value=0.001,
                          value=2.4,step=0.1,format="%.4f")
    t_inicio=c.number_input("Arranque del clúster (s)",min_value=0.0,
                            value=1.2,step=0.05)
    n_reps=st.slider("Número de transformaciones similares (hipótesis)",
                     min_value=1,max_value=30,value=1)
    total_local=t_local*n_reps
    total_dask=t_inicio+t_dask*n_reps
    c1,c2,c3=st.columns(3)
    c1.metric("Local total",f"{total_local:.3f} s")
    c2.metric("Dask total",f"{total_dask:.3f} s")
    c3.metric("Aceleración total",f"{total_local/total_dask:.2f}x")
    if t_local>t_dask:
        umbral=int(math.floor(t_inicio/(t_local-t_dask)))+1
        st.info(f"Con estos supuestos, se amortiza al repetir aproximadamente {umbral} veces.")
    else:
        st.warning("Con estos supuestos, Dask no recupera el costo inicial.")
    st.markdown(
        "**Interpretación:** compara trabajos idénticos y registra CPU, workers, "
        "RAM y caché. El overhead puede variar con tamaño, hardware y red. "
        "Dos workers dentro de Codespaces no son dos servidores."
    )
    st.code("""# Ajusta con tus medidas, no con una estimación ajena
total_local = t_local * n_reps
total_dask = t_inicio + t_dask * n_reps
speedup = total_local / total_dask
""",language="python")

with tabs[6]:
    st.subheader("Decisión estructurada · Dask y evidencia real")
    st.markdown(
        "Elige una arquitectura y un límite después de ejecutar los dos modos "
        "**texto real** y **espera simulada**. Esta pauta es una autocomprobación "
        "formativa; no es una evaluación adicional ni modifica el PDA."
    )
    opciones_motor={
        "Aún no seleccionar":None,
        "1 · Ejecutar secuencial cuando las tareas son demasiado pequeñas":1,
        "2 · Dask para lotes independientes con esperas (2 workers medidos)":2,
        "3 · Comparar 4 workers y arranque antes de decidir":3,
    }
    opciones_limite={
        "Aún no seleccionar":None,
        "1 · La aceleración caliente excluye arranque y preparación":1,
        "2 · La espera OCR/ASR fue simulada, no un servicio real":2,
        "3 · Workers de una VM comparten CPU y memoria":3,
        "4 · Los tiempos dependen de los recursos del Codespace usado":4,
    }
    seleccion_motor=st.selectbox("Arquitectura",list(opciones_motor),key="s13_decision_motor")
    seleccion_limite=st.selectbox("Límite verificable",list(opciones_limite),key="s13_decision_limite")
    st.markdown(
        "**Pauta formativa de cinco evidencias:** CPU y memoria, workers reales, "
        "igualdad secuencial/Dask, comparación de tiempos incluyendo arranque "
        "y explicación TF-IDF (DF, IDF, L2). "
        "La F1 del clasificador es exclusiva de la ampliación opcional."
    )
    medidas=st.session_state.get("s13_modos_ejecutados",{})
    if len(medidas)<2:
        st.info("Ejecuta los dos modos en la pestaña 5 para descargar la evidencia completa. No inventamos resultados.")
    elif opciones_motor[seleccion_motor] is None or opciones_limite[seleccion_limite] is None:
        st.info("Selecciona una arquitectura y un límite a partir de tus mediciones.")
    else:
        ids="\n".join(data["id_del_proceso"].astype(str))
        evidencia={
            "sesion":13,
            "muestra_sha256_ids":hashlib.sha256(ids.encode("utf-8")).hexdigest(),
            "arquitectura_codigo":opciones_motor[seleccion_motor],
            "arquitectura":seleccion_motor,
            "limite_codigo":opciones_limite[seleccion_limite],
            "limite":seleccion_limite,
            "modos_medidos":medidas,
            "protocolo":"mismos lotes SECOP, 2 modos; cronómetros diferenciados por fase",
        }
        st.json(evidencia,expanded=False)
        st.download_button(
            "Descargar decisión y mediciones propias (JSON)",
            data=json.dumps(evidencia,ensure_ascii=False,indent=2),
            file_name="s13_decision_con_mediciones.json",
            mime="application/json",key="s13_decision_evidencia",
        )
