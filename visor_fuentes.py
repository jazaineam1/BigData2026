"""Visor privado de documentos/fotos/audios para Codespaces S11.

Abre cada PDF, su vista PNG, las 62 fotografías y los 30 WAV autorizados.
Aprende el procesamiento escribiendo Python en 01_laboratorio.ipynb.
"""
from __future__ import annotations

import time
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps
import io
import pandas as pd
from ocr_documental import (PSM_EXPLICACION, candidatos_ocr, pdf_paginas,
                            renderizar_pagina, referencia_doc_728704921,
                            texto_integrado_pdf)

from fuentes import ROOT, AUDIO_MANIFEST, inventario, preparar_audios, sha256

st.set_page_config(page_title="S11 · Visor de fuentes", page_icon="📚", layout="wide")
st.title("📚 S11 · Documentos, imágenes y audios")
st.caption("Explora todos los originales sin salir de esta herramienta. Después escribe tú las funciones en el cuaderno.")
st.info("Cada acta tiene PDF original y primera página PNG. "
        "Las voces MINDS-14 NO corresponden a noticias de El Tiempo ni a las actas SECOP.")

items = inventario()
grupos = ["Actas SECOP (30)", "El Tiempo (30)", "Fotografías con ficha (32)", "Voces MINDS-14 (30)"]
totales = [sum(x["grupo"] == grupo for x in items) for grupo in grupos]
for col, grupo, n in zip(st.columns(4), grupos, totales):
    col.metric(grupo, n)

with st.sidebar:
    st.header("Seleccionar fuente")
    grupo = st.radio("Colección", grupos, index=0)
    buscar = st.text_input("Filtrar por número o nombre",
                           placeholder="Ej.: 728704921, eltiempo_006")
    with st.expander("Preparación de búsqueda visual (Ollama)"):
        st.caption("Ollama ejecuta EmbeddingGemma 2. Para leer caracteres de un PDF "
                   "se utiliza Tesseract, no este modelo.")
        st.code("bash iniciar_ollama.sh\nbash preparar_embeddinggemma.sh", language="bash")
    st.divider()
    st.subheader("Treinta audios reales")
    st.caption("MINDS-14 en español; CC BY 4.0. "
               "La primera descarga trae ~39 MB de Hugging Face y verifica el SHA-256.")
    if st.button("Preparar / comprobar las 30 voces", use_container_width=True):
        try:
            with st.spinner("Descargando, verificando y convirtiendo..."):
                n = preparar_audios()
            st.success(f"{n} voces listas")
            st.rerun()
        except Exception as exc:
            st.error(f"No se pudieron preparar: {exc}")
    if AUDIO_MANIFEST.is_file():
        st.success("Las treinta voces ya están preparadas")

candidatos = [x for x in items if x["grupo"] == grupo
              and buscar.casefold() in (x["nombre"] + " " + x.get("noticia", "")).casefold()]
if not candidatos:
    st.warning("Sin resultados. Si elegiste voces, primero prepara los 30 WAV en la barra lateral.")
    st.stop()

opciones = [x["nombre"] for x in candidatos]
if "doc_selected" not in st.session_state or st.session_state.doc_selected not in opciones:
    st.session_state.doc_selected = ("secop_acta_728704921" if "secop_acta_728704921" in opciones else opciones[0])


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
    st.markdown("### 1 · Comprender el PDF original")
    st.write("Un PDF puede tener varias páginas y contener texto seleccionable o páginas "
             "escaneadas. OCR se aplica sobre la imagen de una página, sin modificar el PDF.")
    try:
        paginas = pdf_paginas(str(original))
        pagina = st.selectbox("Selecciona la página que deseas analizar",
                              list(range(1, paginas + 1)),
                              format_func=lambda x: f"Página {x} de {paginas}")
        if pagina == 1:
            with Image.open(item["preview"]) as original_png:
                pagina_imagen = original_png.convert("RGB")
        else:
            pagina_imagen = Image.open(
                io.BytesIO(renderizar_pagina(str(original), pagina, 170))
            ).convert("RGB")
    except Exception as exc:
        st.error(f"No fue posible abrir esta página: {exc}")
        st.stop()
    col_pdf, col_png = st.columns(2)
    with col_pdf:
        st.markdown("**PDF completo (puedes desplazarte por sus páginas)**")
        st.pdf(original, height=620)
        st.download_button("Guardar PDF original", original.read_bytes(),
                           original.name, mime="application/pdf")
    with col_png:
        st.markdown(f"**Página {pagina}: imagen que se entregará a Tesseract**")
        st.image(pagina_imagen, caption=f"Página {pagina} de {paginas} — sin modificar",
                 use_container_width=True)
        st.caption("Si cambias de página, también cambia el OCR que se ejecutará.")
    media_original = pagina_imagen
    if original.name == "secop_acta_728704921.pdf" and pagina == 1:
        st.info("Caso de investigación: acta de inicio, contrato 006-2026. "
                "Encuentra VALOR DEL CONTRATO, DURACIÓN y FORMA DE PAGO. "
                "Comprueba las cifras en la imagen, no solo en el texto de la máquina.")
    with st.expander("¿El PDF ya tiene texto seleccionable? Compruébalo"):
        st.write("pdftotext extrae letras almacenadas en el PDF, si existen. "
                 "No es OCR ni interpreta imágenes.")
        if st.button("Revisar capa de texto del PDF", key=f"capatexto_{original.name}_{pagina}"):
            try:
                capa = texto_integrado_pdf(original, pagina)
                if capa:
                    st.text_area("Texto seleccionado desde el propio PDF", capa, height=210)
                else:
                    st.info("Esta página no tiene texto seleccionable recuperable: "
                            "utiliza el OCR sobre la imagen.")
            except Exception as exc:
                st.warning(f"No se pudo comprobar la capa de texto: {exc}")
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
    st.markdown("### 2 · ¿Qué hace OCR y qué significa PSM?")
    st.write("**OCR** (reconocimiento óptico de caracteres) intenta convertir píxeles "
             "en letras y cifras. **Tesseract** es el programa de OCR; **pytesseract** "
             "es la biblioteca Python que lo llama. OCR no interpreta por sí solo "
             "un contrato ni confirma si sus cifras son correctas.")
    st.write("**PSM** significa Page Segmentation Mode (modo de segmentación de página). "
             "Le indica a Tesseract cómo organizar columnas y bloques antes de leer.")
    psm = st.selectbox("Cómo quieres que Tesseract interprete esta imagen",
                       [3, 6, 11], format_func=lambda n: PSM_EXPLICACION[n][0],
                       index=0 if item["clase"] == "pdf" else 2)
    st.info(PSM_EXPLICACION[psm][1])
    with st.expander("¿Cuándo conviene usar cada PSM?"):
        for n in [3, 6, 11]:
            st.markdown(f"**{PSM_EXPLICACION[n][0]}:** {PSM_EXPLICACION[n][1]}")
        st.caption("Para una página completa con tabla empieza en 3. Para un recorte "
                   "con un bloque de texto prueba 6. Para letreros dispersos prueba 11. "
                   "Compara, porque ningún modo garantiza una lectura correcta.")

    transformar = st.checkbox("Crear una copia temporal en escala de grises y con contraste",
                              help="El original no cambia; una transformación también puede empeorar el OCR.")
    if item["clase"] == "pdf":
        media = media_original.copy()
        pagina_actual = pagina
    else:
        with Image.open(item["preview"]) as foto_img:
            media = foto_img.convert("RGB")
        pagina_actual = 1
    if transformar:
        media = ImageOps.autocontrast(ImageOps.grayscale(media))
        st.image(media, caption="Copia transformada, sin alterar la fuente",
                 use_container_width=True)

    st.markdown("### 3 · Reconocer la página y examinar el texto COMPLETO")
    st.write("Primero observa toda la salida de Tesseract. Después identifica campos "
             "y comprueba cada candidato en la página, sin confundirlos con verdades verificadas.")
    clave = (str(original), pagina_actual, psm, transformar)
    if "resultados_ocr" not in st.session_state:
        st.session_state["resultados_ocr"] = {}
    if st.button("Leer esta página con Tesseract OCR",
                 type="primary", use_container_width=True):
        import pytesseract
        try:
            inicial = time.perf_counter()
            with st.spinner(f"Reconociendo página {pagina_actual} con PSM {psm}..."):
                lectura = pytesseract.image_to_string(
                    media, lang="spa", config=f"--psm {psm}")
            st.session_state["resultados_ocr"][clave] = {
                "texto": lectura, "segundos": time.perf_counter() - inicial}
        except Exception as exc:
            st.error(f"Tesseract no pudo reconocer esta página: {exc}")
    resultado = st.session_state["resultados_ocr"].get(clave)
    if resultado is None:
        st.caption("Todavía no se ejecutó OCR con la configuración seleccionada.")
    else:
        lectura = resultado["texto"]
        metricas = st.columns(3)
        metricas[0].metric("Caracteres", len(lectura))
        metricas[1].metric("Líneas", len(lectura.splitlines()))
        metricas[2].metric("Tiempo", f"{resultado['segundos']:.1f} s")
        st.caption("Estas métricas indican cantidad de texto y tiempo; NO exactitud.")

        tab_texto, tab_campos, tab_codigo = st.tabs([
            "Texto OCR completo", "Campos del documento", "Python para reproducir"
        ])
        with tab_texto:
            st.write("Se muestra **toda** la transcripción OCR de la página, no solo "
                     "las líneas que contengan TOTAL o PAGAR. "
                     "El orden puede ser distinto al de las columnas del PDF.")
            if lectura.strip():
                st.text_area("Texto reconocido automáticamente", value=lectura, height=450)
                st.download_button("Guardar TXT para revisión privada",
                                   lectura.encode("utf-8"),
                                   file_name=f"{original.stem}_pagina{pagina_actual}_ocr.txt",
                                   mime="text/plain")
            else:
                st.warning("No se reconoció texto. Revisa la imagen y prueba otro PSM.")
            st.warning("El OCR puede contener identificaciones de personas. "
                       "Evita publicar esta transcripción sin revisarla.")
        with tab_campos:
            if item["clase"] == "pdf":
                st.write("El programa busca etiquetas como VALOR DEL CONTRATO, DURACIÓN "
                         "y FORMA DE PAGO. Muestra **lecturas candidatas** junto a fragmentos "
                         "del OCR; si una etiqueta no aparece, lo indica expresamente.")
                st.dataframe(pd.DataFrame(candidatos_ocr(lectura)),
                             use_container_width=True, hide_index=True)
                referencia = referencia_doc_728704921(original, pagina_actual)
                if referencia:
                    st.markdown("#### Comparación con la primera página original")
                    st.write("La siguiente ficha proviene de una **lectura visual de la fuente**. "
                             "NO es texto creado ni corregido silenciosamente por OCR.")
                    st.table(pd.DataFrame([
                        {"Campo observado": nombre, "Referencia visual": valor}
                        for nombre, valor in referencia.items()
                    ]))
                    st.write("**Pregunta de investigación:** ¿puedes encontrar los valores "
                             "$14.760.000 y $2.460.000 en la salida OCR? "
                             "¿Reconoció seis pagos? ¿Qué información aparece en la imagen "
                             "pero no en el texto automático?")
                st.caption("Una cifra aislada no es necesariamente el valor del contrato: "
                           "se necesita su etiqueta, contexto y cotejo con el PDF.")
            else:
                st.info("Para una fotografía, verifica palabras y letreros en la pestaña "
                        "del texto completo. Para escenas y objetos, usa embeddings visuales.")
        with tab_codigo:
            st.write("Abre el cuaderno único 01_laboratorio.ipynb. Estas líneas son "
                     "el núcleo del reconocimiento que vas a escribir y modificar:")
            if item["clase"] == "pdf":
                ruta_ejemplo = str(item["preview"].relative_to(ROOT))
                st.code("from PIL import Image\n"
                        "import pytesseract\n"
                        f"imagen = Image.open({ruta_ejemplo!r})\n"
                        f"texto = pytesseract.image_to_string(imagen, lang='spa', config='--psm {psm}')\n"
                        "print(texto)\n", language="python")
                st.caption("El ejemplo de arriba usa el PNG de la PRIMERA página; "
                           "para otras páginas primero hay que convertir esa página del PDF.")
            else:
                ruta_ejemplo = str(original.relative_to(ROOT))
                st.code("from PIL import Image\n"
                        "import pytesseract\n"
                        f"imagen = Image.open({ruta_ejemplo!r})\n"
                        f"texto = pytesseract.image_to_string(imagen, lang='spa', config='--psm {psm}')\n"
                        "print(texto)\n", language="python")
            st.write("Cambia el documento, prueba PSM 3, 6 y 11, identifica una diferencia "
                     "y justifica por qué ocurre. El visor ayuda a observar; "
                     "el cuaderno enseña a programar.")

st.divider()
st.markdown("**Para aprender Python:** abre el cuaderno 01_laboratorio.ipynb y escribe "
            "tú mismo los bucles, las consultas y el catálogo. El visor solo ayuda a "
            "inspeccionar cada archivo y comprobar las predicciones.")
