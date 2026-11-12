"""Visor privado de documentos/fotos/audios para Codespaces S11.

Abre cada PDF, su vista PNG, las 62 fotografías y los 10 WAV autorizados.
Aprende el procesamiento escribiendo Python en 01_laboratorio.ipynb.
"""
from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

from fuentes import ROOT, AUDIO_MANIFEST, inventario, preparar_audios, sha256

st.set_page_config(page_title="S11 · Visor de fuentes", page_icon="📚", layout="wide")
st.title("📚 S11 · Documentos, imágenes y audios")
st.caption("Explora todos los originales sin salir de esta herramienta. Después escribe tú las funciones en el cuaderno.")
st.info("Cada acta tiene PDF original y primera página PNG. "
        "Las voces MINDS-14 NO corresponden a noticias de El Tiempo ni a las actas SECOP.")

items = inventario()
grupos = ["Actas SECOP (30)", "El Tiempo (30)", "Fotografías con ficha (32)", "Voces MINDS-14 (10)"]
totales = [sum(x["grupo"] == grupo for x in items) for grupo in grupos]
for col, grupo, n in zip(st.columns(4), grupos, totales):
    col.metric(grupo, n)

with st.sidebar:
    st.header("Seleccionar fuente")
    grupo = st.radio("Colección", grupos)
    buscar = st.text_input("Buscar por número, nombre o artículo", placeholder="Ej. 728490281, 006")
    st.divider()
    st.subheader("Diez audios reales")
    st.caption("MINDS-14 en español; CC BY 4.0. "
               "La primera descarga trae ~39 MB de Hugging Face y verifica el SHA-256.")
    if st.button("Preparar / comprobar las 10 voces", use_container_width=True):
        try:
            with st.spinner("Descargando, verificando y convirtiendo..."):
                n = preparar_audios()
            st.success(f"{n} voces listas")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudieron preparar: {exc}")
    if AUDIO_MANIFEST.is_file():
        st.success("Las diez voces ya están preparadas")

candidatos = [x for x in items if x["grupo"] == grupo
              and buscar.casefold() in (x["nombre"] + " " + x.get("noticia", "")).casefold()]
if not candidatos:
    st.warning("Sin resultados. Si elegiste voces, primero prepara los 10 WAV en la barra lateral.")
    st.stop()

opciones = [x["nombre"] for x in candidatos]
if "doc_selected" not in st.session_state or st.session_state.doc_selected not in opciones:
    st.session_state.doc_selected = opciones[0]


def navegar(salto):
    seleccionado = st.session_state.doc_selected
    if seleccionado in opciones:
        st.session_state.doc_selected = opciones[(opciones.index(seleccionado) + salto) % len(opciones)]
    else:
        st.session_state.doc_selected = opciones[0]


elegido = st.selectbox("Abrir uno de los archivos", opciones, key="doc_selected")
left, right, status = st.columns([1, 1, 3])
with left:
    st.button("← Anterior", on_click=navegar, args=(-1,), use_container_width=True)
with right:
    st.button("Siguiente →", on_click=navegar, args=(1,), use_container_width=True)
with status:
    st.caption(f"Elemento {opciones.index(elegido)+1} de {len(opciones)} en esta selección")

item = next(x for x in candidatos if x["nombre"] == elegido)
original = item["original"]
st.subheader(elegido)
st.caption(f"{item['clase'].upper()} · {item['credito']}")
st.code(str(original.relative_to(ROOT)), language="text")

with st.expander("Origen, tamaño e integridad SHA-256"):
    st.write("Archivo:", original.name)
    st.write("Tamaño:", f"{original.stat().st_size:,}", "bytes")
    st.code(sha256(original), language="text")
    if item.get("noticia"):
        st.write("ID del artículo o registro:", item["noticia"])
    if item.get("url"):
        st.link_button("Abrir referencia registrada", item["url"])
    else:
        st.caption("No hay URL individual contrastada; no se inventa.")
    if item["clase"] == "pdf":
        st.warning("El original puede contener nombres, identificaciones y cuentas. "
                   "No publiques capturas completas ni texto OCR con datos personales.")

if item["clase"] == "pdf":
    st.markdown("#### PDF original completo junto a su primera página")
    col_pdf, col_png = st.columns(2)
    with col_pdf:
        st.pdf(original, height=650)
        st.download_button("Guardar PDF original", original.read_bytes(),
                           original.name, mime="application/pdf")
    with col_png:
        st.image(item["preview"], caption="Primera página del documento", use_container_width=True)
        st.download_button("Guardar PNG de primera página", item["preview"].read_bytes(),
                           item["preview"].name, mime="image/png")
elif item["clase"] == "imagen":
    st.image(original, caption=elegido, use_container_width=True)
    with Image.open(original) as img:
        st.caption(f"Dimensiones: {img.width} × {img.height}; formato: {img.format}")
    mime = "image/jpeg" if original.suffix.lower() in (".jpg", ".jpeg") else "image/webp"
    st.download_button("Guardar imagen original", original.read_bytes(), original.name, mime=mime)
else:
    st.audio(original, format="audio/wav")
    st.caption("Voz humana de PolyAI MINDS-14 · es-ES · CC BY 4.0")
    with st.expander("Mostrar la transcripción humana de referencia"):
        st.text(item["referencia"])
    st.download_button("Guardar WAV PCM16", original.read_bytes(), original.name, mime="audio/wav")
    if st.button("Transcribir esta voz con Whisper tiny"):
        from faster_whisper import WhisperModel

        @st.cache_resource(show_spinner="Cargando Whisper tiny...")
        def whisper():
            return WhisperModel("tiny", device="cpu", compute_type="int8", cpu_threads=2)

        start = time.perf_counter()
        try:
            with st.spinner("Reconociendo palabras..."):
                segments, info = whisper().transcribe(str(original), language="es", beam_size=2)
                lines = [f"{s.start:.1f}–{s.end:.1f} segundos: {s.text.strip()}" for s in segments]
            st.text_area("Transcripción del modelo (contrasta con la voz)", "\n".join(lines), height=200)
            st.caption(f"Inferencia: {time.perf_counter()-start:.1f} s. "
                       "No equivale a una transcripción certificada.")
        except Exception as exc:
            st.error(f"Error de Whisper: {exc}")

if item["clase"] in ("imagen", "pdf"):
    st.divider()
    st.subheader("Experimentar con OCR en ESTE archivo")
    st.caption("Abre la imagen antes de preguntar si tiene texto. "
               "Tesseract reconoce caracteres; no explica lo que ocurre en una escena.")
    psm = st.selectbox("PSM: segmentación de página", [6, 11, 3], index=1)
    transformar = st.checkbox("Ver imagen en grises y con contraste", value=False)
    with Image.open(item["preview"]) as img:
        media = img.convert("RGB")
    if transformar:
        media = ImageOps.autocontrast(ImageOps.grayscale(media))
        st.image(media, caption="Transformación temporal; se conserva el original",
                 use_container_width=True)
    if st.button("Aplicar Tesseract OCR a este archivo"):
        import pytesseract
        try:
            start = time.perf_counter()
            with st.spinner("Reconociendo los caracteres..."):
                leido = pytesseract.image_to_string(media, lang="spa", config=f"--psm {psm}")
            st.caption(f"{len(leido)} caracteres; {time.perf_counter()-start:.2f} s")
            if item["clase"] == "pdf":
                lineas = [s for s in leido.splitlines()
                          if any(q in s.upper() for q in ("TOTAL", "DESCUENTO", "PAGAR", "VALOR"))]
                st.text_area("Solo líneas relacionadas con valores; confirmar en la página",
                             "\n".join(lineas) or "Sin coincidencias", height=170)
                if st.checkbox("Mostrar texto OCR completo (puede contener datos personales)"):
                    st.text_area("OCR completo — NO publicar", leido, height=230)
            else:
                st.text_area("Texto OCR — ¿es correcto?", leido, height=220)
        except Exception as exc:
            st.error(f"No se pudo ejecutar OCR: {exc}")

st.divider()
st.markdown("**Para aprender Python:** abre el cuaderno 01_laboratorio.ipynb y escribe "
            "tú mismo los bucles, las consultas y el catálogo. El visor solo ayuda a "
            "inspeccionar cada archivo y comprobar las predicciones.")
