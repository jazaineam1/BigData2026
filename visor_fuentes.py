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
                            texto_integrado_pdf, recortar_por_porcentaje,
                            recorte_logo_valle, preparar_region_ocr,
                            detalle_ocr, dibujar_cajas_ocr)

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
    st.header("Laboratorio OCR · de los píxeles a la información")
    st.write("**OCR** (reconocimiento óptico de caracteres) convierte píxeles en texto "
             "probable. **Tesseract** reconoce los caracteres y **pytesseract** lo "
             "invoca desde Python. No describe escenas ni valida cifras.")
    es_valle = item["clase"] == "imagen" and original.name == "eltiempo_023.webp"
    if es_valle:
        st.markdown("### ¿Por qué cuesta leer la Lotería del Valle?")
        st.write("El logotipo combina **letras decorativas, curvas, varios colores, "
                 "contornos y un fondo que compite con el texto**. Si pasas toda la "
                 "fotografía al OCR, algunas letras parecen formas, no palabras.")
        st.info("Experimento: compara OCR sobre la foto completa con OCR sobre "
                "la palabra VALLE aislada. La palabra visible sirve como referencia "
                "humana, no se añade artificialmente a la respuesta del motor.")

    st.subheader("1 · Selecciona la región que deseas leer")
    if item["clase"] == "pdf":
        imagen_entera = media_original.copy()
        opciones = ["Página completa", "Recorte personalizado"]
    else:
        with Image.open(original) as im:
            imagen_entera = im.convert("RGB")
        opciones = (
            ["Fotografía completa", "Logotipo completo", "Palabra VALLE",
             "Eslogan", "Recorte personalizado"] if es_valle
            else ["Fotografía completa", "Recorte personalizado"]
        )
    zona = st.selectbox("Región", opciones)
    caja = (0, 0, imagen_entera.width, imagen_entera.height)
    if zona == "Recorte personalizado":
        st.write("**EDITA AQUÍ:** ajusta los intervalos hasta que solo veas "
                 "las letras que quieres leer. Los valores son porcentajes.")
        xr = st.slider("Intervalo horizontal (%)", 0, 100, (10, 55))
        yr = st.slider("Intervalo vertical (%)", 0, 100, (15, 85))
        roi = recortar_por_porcentaje(imagen_entera, xr, yr)
        caja = (int(imagen_entera.width*xr[0]/100),
                int(imagen_entera.height*yr[0]/100),
                int(imagen_entera.width*xr[1]/100),
                int(imagen_entera.height*yr[1]/100))
    elif es_valle and zona in ("Logotipo completo", "Palabra VALLE", "Eslogan"):
        coordenadas = {
            "Logotipo completo": (145/1200, 125/675, 565/1200, 545/675),
            "Palabra VALLE": (175/1200, 240/675, 540/1200, 375/675),
            "Eslogan": (205/1200, 363/675, 482/1200, 451/675)
        }
        xy = coordenadas[zona]
        caja = (round(imagen_entera.width*xy[0]), round(imagen_entera.height*xy[1]),
                round(imagen_entera.width*xy[2]), round(imagen_entera.height*xy[3]))
        roi = recorte_logo_valle(imagen_entera, zona)
    else:
        roi = imagen_entera.copy()
    if roi.width < 10 or roi.height < 10:
        st.error("El recorte es demasiado pequeño. Amplía el intervalo.")
        st.stop()
    if es_valle:
        st.caption("Referencia leída por una persona: Lotería del VALLE · Cambia tu vida. "
                   "Un OCR real puede reconocer solo VALLE, confundir las otras "
                   "palabras o devolver texto incompleto.")

    st.subheader("2 · Cambia una variable y comprende por qué")
    st.write("**PSM** significa Page Segmentation Mode, modo de segmentación "
             "de página. Le indica a Tesseract si espera una página, "
             "un bloque, una sola línea o letras dispersas. "
             "No es un porcentaje de calidad.")
    psms = [3, 6, 7, 11]
    predeterminado = 7 if zona == "Palabra VALLE" else (3 if item["clase"] == "pdf" else 11)
    psm = st.selectbox(
        "Cómo interpretar la distribución de caracteres",
        psms, format_func=lambda n: PSM_EXPLICACION[n][0],
        index=psms.index(predeterminado),
        key=f"psm_{original.name}_{zona}"
    )
    st.info(PSM_EXPLICACION[psm][1])
    with st.expander("Explicación de los cuatro valores PSM"):
        for n in psms:
            st.markdown(f"**{PSM_EXPLICACION[n][0]}:** {PSM_EXPLICACION[n][1]}")
    escala = st.select_slider(
        "Ampliación de los píxeles (no añade información nueva)",
        options=[1, 2, 3], value=2 if zona != opciones[0] else 1,
        format_func=lambda x: f"{x} veces", key=f"escala_{original.name}_{zona}"
    )
    tratamiento = st.selectbox(
        "Preparación opcional de la imagen",
        ["Sin cambios", "Contraste y nitidez", "Blanco y negro"],
        help="Prueba y compara. Subir contraste o borrar colores puede mejorar o "
             "empeorar la lectura.", key=f"tratamiento_{original.name}_{zona}"
    )
    margen = 12 if st.checkbox(
        "Añadir margen blanco de 12 píxeles (experimento opcional)",
        value=False,
        help="Puede ayudar a regiones muy ajustadas, pero también empeorar el logotipo. "
             "Por defecto conservamos el recorte exacto."
    ) else 0
    procesada = preparar_region_ocr(
        roi, escala=escala, tratamiento=tratamiento, margen=margen)
    izq, der = st.columns(2)
    with izq:
        st.image(roi, caption=f"Original seleccionado: {roi.width}×{roi.height} píxeles",
                 use_container_width=True)
    with der:
        st.image(procesada, caption=f"Copia usada en OCR: {escala}× · {tratamiento}",
                 use_container_width=True)
    st.caption("La fuente se conserva sin modificaciones. "
               "Puedes repetir el experimento con otro recorte o PSM.")

    st.subheader("3 · Ejecuta y compara los resultados completos")
    pagina_actual = pagina if item["clase"] == "pdf" else 1
    clave = (str(original), pagina_actual, caja, psm, escala, tratamiento, margen)
    if "resultados_ocr" not in st.session_state:
        st.session_state["resultados_ocr"] = {}
    if st.button("Comparar OCR original y OCR del experimento",
                 type="primary", use_container_width=True):
        import pytesseract
        try:
            with st.spinner("Ejecutando Tesseract en ambas imágenes..."):
                t0 = time.perf_counter()
                psm_base = 3 if item["clase"] == "pdf" else 11
                lectura_base = pytesseract.image_to_string(
                    imagen_entera, lang="spa", config=f"--psm {psm_base}")
                lectura = pytesseract.image_to_string(
                    procesada, lang="spa", config=f"--psm {psm}")
                datos = pytesseract.image_to_data(
                    procesada, lang="spa", config=f"--psm {psm}",
                    output_type=pytesseract.Output.DICT)
                palabras, confianza = detalle_ocr(datos)
                duracion = time.perf_counter()-t0
            st.session_state["resultados_ocr"][clave] = dict(
                base=lectura_base, texto=lectura, palabras=palabras,
                confianza=confianza, duracion=duracion)
        except Exception as exc:
            st.error(f"El OCR no pudo procesar la región: {exc}")
    resultado = st.session_state["resultados_ocr"].get(clave)
    if resultado is None:
        st.caption("Configura el experimento y pulsa el botón. "
                   "Ningún texto se inventa antes de ejecutar el motor.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Caracteres nuevos", len(resultado["texto"]))
        c2.metric("Palabras detectadas", len(resultado["palabras"]))
        c3.metric("Tiempo", f"{resultado['duracion']:.1f} s")
        st.caption("Los conteos y la confianza interna no son una medida "
                   "de exactitud. La respuesta se valida mirando los píxeles.")

        tab_texto, tab_cajas, tab_campos, tab_python = st.tabs(
            ["A · Antes y después", "B · Dónde encontró letras",
             "C · Interpretar", "D · Reproducir en Python"])
        with tab_texto:
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**A. Fotografía o página completa**")
                st.text_area("Salida original de Tesseract",
                             resultado["base"] or "(no detectó texto)",
                             height=340)
            with col_b:
                st.markdown("**B. Tu recorte y tus parámetros**")
                st.text_area("Salida experimental completa",
                             resultado["texto"] or "(no detectó texto)",
                             height=340)
            st.write("**Compara con el original:** ¿se reconoce VALLE? "
                     "¿El resto del logotipo sigue dando problemas?")
            st.download_button("Guardar OCR experimental como TXT privado",
                               resultado["texto"].encode("utf-8"),
                               file_name=f"{original.stem}_ocr.txt", mime="text/plain")
            st.warning("Los documentos pueden contener identificaciones personales. "
                       "Revisa las salidas antes de compartirlas.")
        with tab_cajas:
            if resultado["palabras"]:
                st.image(dibujar_cajas_ocr(procesada, resultado["palabras"]),
                         caption="Cajas verdes: ubicaciones donde Tesseract detectó palabras",
                         use_container_width=True)
                st.dataframe(pd.DataFrame(resultado["palabras"]),
                             use_container_width=True, hide_index=True)
                st.caption("Confianza promedio interna: " +
                           (f"{resultado['confianza']:.1f}/100" if resultado["confianza"]
                            is not None else "no disponible") +
                           ". No equivale al porcentaje real de aciertos.")
            else:
                st.warning("No se detectaron palabras con posición. "
                           "Prueba otro recorte o modo.")
        with tab_campos:
            if es_valle:
                st.write("**Referencia humana:** Lotería del VALLE · Cambia tu vida. "
                         "Se compara con el OCR; no se copia a la salida del modelo.")
                st.write("Aprendizaje: reconocer una palabra no implica haber "
                         "comprendido toda la imagen. Los logotipos requieren "
                         "recortes y revisión humana.")
            elif item["clase"] == "pdf":
                st.write("Las siguientes son **lecturas candidatas** y sus "
                         "fragmentos de evidencia OCR, no hechos certificados.")
                st.dataframe(pd.DataFrame(candidatos_ocr(resultado["texto"])),
                             use_container_width=True, hide_index=True)
                referencia = referencia_doc_728704921(original, pagina_actual)
                if referencia:
                    st.markdown("**Comparación con la primera página original**")
                    st.table(pd.DataFrame([
                        {"Campo": k, "Lectura humana": v}
                        for k, v in referencia.items()
                    ]))
            else:
                st.info("Cuando no hay letras útiles, cambia a búsqueda "
                        "visual por embeddings para encontrar escenas.")
        with tab_python:
            st.write("Abre el único cuaderno 01_laboratorio.ipynb y "
                     "prueba estas operaciones por tu cuenta.")
            archivo = item["preview"] if item["clase"] == "pdf" else original
            ruta = str(archivo.relative_to(ROOT))
            pasos = [
                "from PIL import Image, ImageOps, ImageFilter",
                "import pytesseract",
                f"imagen = Image.open({ruta!r}).convert('RGB')",
                "# EDITA AQUÍ: coordenadas del recorte",
                f"region = imagen.crop({caja!r})",
                "# EDITA AQUÍ: escala de la imagen",
                f"region = region.resize((region.width*{escala}, region.height*{escala}), Image.Resampling.LANCZOS)"
            ]
            if tratamiento == "Contraste y nitidez":
                pasos.extend([
                    "region = ImageOps.autocontrast(ImageOps.grayscale(region))",
                    "region = region.filter(ImageFilter.UnsharpMask(radius=1, percent=130, threshold=2))"
                ])
            elif tratamiento == "Blanco y negro":
                pasos.extend([
                    "region = ImageOps.autocontrast(ImageOps.grayscale(region))",
                    "region = region.point(lambda v: 255 if v >= 150 else 0)"
                ])
            pasos.extend([
                f"region = ImageOps.expand(region, border={margen}, fill='white')",
                f"texto = pytesseract.image_to_string(region, lang='spa', config='--psm {psm}')",
                "print(texto)  # No limites la salida con [:130]"
            ])
            st.code("\n".join(pasos), language="python")
            if item["clase"] == "pdf" and pagina_actual > 1:
                st.warning("Para analizar otra página del PDF con este código "
                           "primero debes convertirla a una imagen. "
                           "El archivo PNG del ejemplo corresponde solo a la primera.")
            st.write("**Tu turno:** cambia el recorte, la escala y el PSM; "
                     "explica por qué modificaste cada línea.")

st.divider()
st.markdown("**Para aprender Python:** abre el cuaderno 01_laboratorio.ipynb y escribe "
            "tú mismo los bucles, las consultas y el catálogo. El visor solo ayuda a "
            "inspeccionar cada archivo y comprobar las predicciones.")
