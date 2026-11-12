"""S13 · Laboratorio interactivo: TF-IDF y datos SECOP reales.

Cinco módulos para aprender, CAMBIAR código, comprobar y transferir.
Ningún campo de precio es objetivo, ninguna discrepancia es alerta de fraude.
Uso: streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py --server.port 8503
"""
from __future__ import annotations

import json
import math
import re
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.svm import LinearSVC

from benchmark_unspsc_tfidf_dask import ETIQUETAS, CODIGO, texto_limpio

ROOT=Path(__file__).resolve().parents[2]
CSV=ROOT/"Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
RESULTS=Path(__file__).resolve().parent/"salidas/benchmark_unspsc"

st.set_page_config(page_title="S13 · Taller interactivo TF-IDF",layout="wide")
st.title("Laboratorio SECOP · Del texto al dato que aprende un modelo")
st.caption("Universidad Central · Big Data · S13 · TF-IDF → clasificación UNSPSC → Dask Distributed")
st.info("La fuente es un registro de proceso SECOP. Los modelos aprenden categorías declaradas, "
        "no sobrecostos, fraude ni competencia contractual.")

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
    "3 · Buscar documentos","4 · Entrenar clasificador",
    "5 · Dask y mediciones","6 · Decidir con costos",
    "7 · Evidencia reutilizable",
])

with tabs[0]:
    st.subheader("Los datos preceden al algoritmo")
    c1,c2,c3=st.columns(3)
    c1.metric("Filas de la muestra",len(data))
    c2.metric("IDs únicos",data["id_del_proceso"].nunique())
    c3.metric("UNSPSC no identificados",int((data.segmento=="NO IDENTIFICADO").sum()))
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
        value="La entidad contrata mantenimiento de computadores.\n\n"
              "La entidad contrata mantenimiento de carreteras.\n\n"
              "Un hospital compra computadores para urgencias.",
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
    st.subheader("Dask no es un algoritmo: es un planificador")
    st.markdown("**Caso 1:** vectorizar mil textos. La coordinación puede tardar "
                "más que el cálculo. **Caso 2:** entrenar 3 folds independientes "
                "de validación cruzada, sobre textos grandes. Dask puede "
                "ejecutar varios folds simultáneamente sin cambiar LinearSVC.")
    st.code("""# Una tarea = entrenar TF-IDF + LinearSVC sobre un fold.
trabajos=[client.submit(entrenar_un_fold, textos_fut, y_fut,
                        tr, val, pure=False)
         for tr,val in folds]
metricas=client.gather(trabajos)""",language="python")
    st.markdown("**Comparación justa:** local secuencial, joblib con dos procesos "
                "y Dask con dos workers reciben exactamente los mismos folds. "
                "Dask distribuye entrenamientos independientes, NO internamente "
                "un único modelo LinearSVC.")
    for name in ["benchmark_50k_test_fijo.json",
                 "cv_linearsvc_local_vs_dask.json",
                 "embgemma_vs_tfidf_1000_real.json"]:
        path=RESULTS/name
        if path.is_file():
            payload=json.loads(path.read_text(encoding="utf-8"))
            with st.expander(f"Resultados realmente medidos: {name}"):
                st.json(payload,expanded=False)
        else:
            st.caption(f"Pendiente de ejecutar: {name}")
    st.markdown("**Codespaces:** perfil S13, elegir máquina de 2 o 4 CPU según "
                "disponibilidad/cuota. El proceso Dask corre en una sola VM; "
                "para distribuir físicamente necesitas workers en otras máquinas.")


with tabs[5]:
    st.subheader("Simulador de decisión: el clúster también cuesta")
    st.markdown(
        "**Speedup (aceleración)** = tiempo local dividido por tiempo distribuido. "
        "El total distribuido suma el arranque del clúster una sola vez "
        "si lo reutilizas durante varias ejecuciones. Este simulador usa "
        "**supuestos editables**, no reemplaza un benchmark extremo a extremo."
    )
    a,b,c=st.columns(3)
    t_local=a.number_input("Local por transformación (s)",min_value=0.001,
                           value=3.9234,step=0.1,format="%.4f")
    t_dask=b.number_input("Dask por transformación (s)",min_value=0.001,
                          value=3.5522,step=0.1,format="%.4f")
    t_inicio=c.number_input("Arranque del clúster (s)",min_value=0.0,
                            value=1.35,step=0.05)
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
    st.subheader("Reto de transferencia: evidencia estructurada")
    st.markdown(
        "Escoge una arquitectura y un límite **después de ejecutar tu cuaderno**. "
        "No se acepta una respuesta académica abierta; la evidencia formal "
        "es el código y la traza del estudiante. El JSON descargado es "
        "una ayuda para guardar tu decisión, no una calificación."
    )
    opciones_motor={
        "Aún no seleccionar":None,
        "1 · Mantener TF-IDF local":1,
        "2 · Distribuir TF-IDF con Dask 2 workers":2,
        "3 · Medir pipeline completo antes de decidir":3,
    }
    opciones_limite={
        "Aún no seleccionar":None,
        "1 · El experimento excluyó arranque del clúster":1,
        "2 · La muestra no representa todo SECOP":2,
        "3 · UNSPSC puede estar mal declarado y hay desbalance":3,
        "4 · Los tiempos son de otro hardware":4,
    }
    seleccion_motor=st.selectbox("Arquitectura",list(opciones_motor))
    seleccion_limite=st.selectbox("Límite verificable",list(opciones_limite))
    st.markdown(
        "**Criterios formativos (10 puntos):** código/commit (2), "
        "tabla TF-DF-IDF (2), F1 por clase (2), tiempos comparables (2), "
        "elección y límite estructurados (2). No modifica el PDA."
    )
    if (opciones_motor[seleccion_motor] is not None
            and opciones_limite[seleccion_limite] is not None):
        ids="\n".join(data["id_del_proceso"].astype(str))
        evidencia={
            "sesion":13,
            "muestra_sha256_ids":hashlib.sha256(ids.encode("utf-8")).hexdigest(),
            "arquitectura_codigo":opciones_motor[seleccion_motor],
            "arquitectura":seleccion_motor,
            "limite_codigo":opciones_limite[seleccion_limite],
            "limite":seleccion_limite,
            "protocolo":"muestra pequeña SECOP; decisiones requieren comprobar ejecución propia",
        }
        st.json(evidencia,expanded=False)
        st.download_button(
            "Descargar mi decisión estructurada (JSON)",
            data=json.dumps(evidencia,ensure_ascii=False,indent=2),
            file_name="s13_decision_estructurada.json",
            mime="application/json",
        )
    else:
        st.info("Faltan las dos decisiones; no se inventa una respuesta ni se exporta evidencia incompleta.")
