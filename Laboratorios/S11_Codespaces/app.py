"""S11 · interfaz opcional local. El motor sigue en proyecto.py y es reutilizable sin GUI.

Arranque: streamlit run app.py --server.address 0.0.0.0 --server.port 8501
La aplicación se ejecuta SOLO en el Codespace; no usa servidores de terceros para inferencia.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

import streamlit as st
import proyecto

BASE = Path(__file__).resolve().parent
RAICES = BASE / "proyectos"

st.set_page_config(page_title="Laboratorio multimedia · S11", page_icon="📚",
                   layout="wide")
st.title("Laboratorio de evidencias · S11")
st.caption("Universidad Central · OCR de imágenes/PDF · Whisper · EmbeddingGemma 2 · código editable")

st.info("Este panel guarda archivos temporalmente en TU Codespace. Usa solo datos propios "
        "o autorizados y mantén el puerto privado. No garantiza la veracidad de un OCR o ASR.")

with st.sidebar:
    st.header("Proyecto")
    nombre = st.text_input("Carpeta del proyecto (sin espacios)", value="mi_caso",
                           help="Solo letras, números, guion o guion bajo")
    valido = bool(re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,39}", nombre))
    if not valido:
        st.error("Escribe un nombre como facturas_2026")
    raiz = RAICES / nombre if valido else RAICES / "invalid"
    config_path = raiz / "config.json"
    if st.button("Crear carpeta y plantilla", disabled=not valido):
        try:
            proyecto.crear_proyecto(raiz)
            st.success("Proyecto creado. Edita config.json o usa las opciones de esta interfaz.")
        except FileExistsError:
            st.warning("El proyecto ya existe. No se sobrescribió.")
    st.divider()
    st.markdown("**Código que puedes estudiar y modificar**")
    st.code("proyecto.py\nlab.py\nconfig.json", language=None)
    st.markdown("[Tutorial paso a paso](./GUIA_REUTILIZACION.md)")
    st.caption("La interfaz es una alternativa a ejecutar los mismos comandos desde la terminal.")

if not valido:
    st.stop()
if not config_path.is_file():
    st.warning("Primero pulsa «Crear carpeta y plantilla» en la barra lateral.")
    st.stop()

try:
    cfg = proyecto.cargar_config(config_path)
except (ValueError, OSError, json.JSONDecodeError) as err:
    st.error(f"config.json inválido: {err}")
    st.stop()

tabs = st.tabs(["1 · Archivos", "2 · Configurar y procesar", "3 · Buscar", "4 · Auditar", "5 · Aprender"])

with tabs[0]:
    st.subheader("Entrada: tus propios archivos")
    st.write("Sube imágenes, PDF, audio y texto. También puedes arrastrarlos directamente "
             "a las carpetas entradas/ de VS Code.")
    tipo = st.selectbox("Modalidad", ["Imágenes", "PDF", "Audios", "Textos"])
    carpeta = {"Imágenes": "imagenes", "PDF": "documentos",
               "Audios": "audios", "Textos": "textos"}[tipo]
    extensiones = {
        "Imágenes": ["png", "jpg", "jpeg", "webp", "tif", "tiff", "bmp"],
        "PDF": ["pdf"], "Audios": ["wav", "mp3", "ogg", "flac", "m4a"],
        "Textos": ["txt", "md"]
    }[tipo]
    subidos = st.file_uploader("Archivos locales autorizados", type=extensiones,
                               accept_multiple_files=True, key="carga_"+carpeta)
    if st.button("Guardar archivos en entradas/", disabled=not bool(subidos)):
        guardados, omitidos = 0, []
        for obj in subidos or []:
            nombre_archivo = Path(obj.name.replace("\\", "/")).name
            if not nombre_archivo or Path(nombre_archivo).suffix.lower() not in proyecto.EXT:
                omitidos.append(str(obj.name)); continue
            if obj.size > proyecto.MAX_BYTES:
                omitidos.append(nombre_archivo+" (más de 80 MB)"); continue
            destino = raiz / "entradas" / carpeta / nombre_archivo
            if destino.exists():
                omitidos.append(nombre_archivo+" (ya existe)"); continue
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(obj.getvalue())
            guardados += 1
        st.success(f"Guardados: {guardados}. Ya existentes o no admitidos: {len(omitidos)}")
        if omitidos:
            st.warning("; ".join(omitidos))
    st.divider()
    if st.button("Verificar plan (no ejecuta modelos)"):
        try:
            files = proyecto.plan(raiz, cfg)
            st.dataframe([{"archivo": f.relative_to(raiz).as_posix(),
                           "bytes": f.stat().st_size} for f in files],
                         use_container_width=True)
        except Exception as ex:
            st.error(str(ex))

with tabs[1]:
    st.subheader("Modificar parámetros sin tocar la lógica")
    c1, c2, c3 = st.columns(3)
    with c1:
        psm = st.selectbox("Tesseract PSM", [3,4,6,11],
                           index=[3,4,6,11].index(int(cfg["ocr"].get("psm", 6))))
        idioma_ocr = st.text_input("Idioma Tesseract", cfg["ocr"]["idioma"])
    with c2:
        whisper = st.selectbox("Modelo Whisper (CPU)", ["tiny", "base", "small"],
                               index=["tiny","base","small"].index(cfg["asr"]["modelo"]))
        idioma_asr = st.text_input("Idioma del audio", cfg["asr"]["idioma"])
    with c3:
        tamano = st.number_input("Caracteres por fragmento", min_value=100, max_value=4000,
                                 value=int(cfg["limites"]["caracteres_por_fragmento"]))
        paginas = st.number_input("Máximo de páginas PDF", min_value=1, max_value=20,
                                  value=int(cfg["limites"]["paginas_pdf"]))
    if st.button("Guardar parámetros"):
        cfg["ocr"].update({"psm": psm, "idioma": idioma_ocr})
        cfg["asr"].update({"modelo": whisper, "idioma": idioma_asr})
        cfg["limites"].update({"caracteres_por_fragmento": int(tamano),
                               "paginas_pdf": int(paginas)})
        proyecto.escribir_json(config_path, cfg)
        st.success("Guardados en config.json. Al cambiar un parámetro, repite procesar e indexar.")
    st.caption("Revisa el archivo config.json para cambiar fuente, crédito, licencia, "
               "modelo de embeddings y tamaño del lote. Para metadatos individuales crea metadatos.json.")
    if st.button("Procesar carpeta completa (OCR / ASR / TXT)"):
        with st.spinner("Ejecutando motores locales; los modelos se descargan en el primer uso..."):
            try:
                proyecto.ejecutar(raiz, proyecto.cargar_config(config_path))
            except Exception as ex:
                st.error(str(ex))
            else:
                st.success("Procesamiento realizado. Verifica catálogo y errores.")
    ruta_catalogo = raiz / "salidas" / "catalogo.jsonl"
    if ruta_catalogo.exists():
        try:
            filas = proyecto.leer_filas(raiz)
            st.metric("Archivos procesados", len(filas))
            st.dataframe([{"archivo": x["path"], "tipo": x["tipo"],
                           "caracteres": len(x["extracted_text"]), "sha256": x["sha256"][:12]}
                          for x in filas], use_container_width=True)
            if filas:
                elegido = st.selectbox("Inspecciona evidencia", list(range(len(filas))),
                                       format_func=lambda n: filas[n]["path"])
                fila = filas[elegido]
                st.code(fila["extracted_text"][:6000] or "[sin texto reconocido]", language=None)
                if fila["tipo"] == "imagen":
                    st.image(str(raiz / fila["path"]), caption="Fuente original")
                elif fila["tipo"] == "audio":
                    st.audio(str(raiz / fila["path"]))
                    st.dataframe(fila.get("segments", []))
        except Exception as ex:
            st.error(str(ex))
    errores = raiz / "salidas" / "errores.json"
    if errores.exists():
        data = json.loads(errores.read_text(encoding="utf-8"))
        if data.get("errores"):
            st.warning("Errores parciales (revisar fuente):")
            st.json(data)

with tabs[2]:
    st.subheader("Búsqueda semántica con embeddings")
    st.caption("Primero arranca Ollama desde terminal con: bash iniciar_ollama.sh")
    consulta = st.text_input("Pregunta sobre tus propios documentos",
                             value="¿Qué documento contiene un valor económico?")
    topk = st.slider("Número de resultados", min_value=1, max_value=10, value=5)
    if st.button("Crear / regenerar índice vectorial"):
        with st.spinner("Ollama genera un vector por fragmento..."):
            try:
                proyecto.indexar(raiz, proyecto.cargar_config(config_path))
                st.success("Índice generado con fuente y SHA en cada fragmento.")
            except Exception as ex:
                st.error(str(ex))
    if st.button("Buscar en los fragmentos"):
        try:
            ranking = proyecto.buscar(raiz, proyecto.cargar_config(config_path),
                                       consulta, topk)
            for n, doc in enumerate(ranking, 1):
                with st.expander(f"{n}. {doc['path']} · coseno={doc['similitud_coseno']:.4f}", expanded=n==1):
                    st.write(doc["texto"])
                    st.caption("Fuente original: "+doc["path"]+" | SHA-256: "+doc["sha256"])
                    if "inicio_s" in doc:
                        st.caption(f"Audio: {doc['inicio_s']} s a {doc['fin_s']} s")
        except Exception as ex:
            st.error(str(ex))

with tabs[3]:
    st.subheader("Auditar: ¿se alteraron originales o catálogo?")
    if st.button("Verificar hashes"):
        try:
            if proyecto.auditar(raiz):
                st.success("Integridad verificada: no se observaron cambios en los archivos incluidos en el manifiesto.")
            else:
                st.error("Al menos un archivo difiere: consulta la terminal.")
        except Exception as ex:
            st.error(str(ex))
    st.caption("Un hash igual no certifica autoría, licencia ni verdad de una noticia.")
    for archivo in ("catalogo.jsonl", "catalogo.parquet", "manifest.json", "errores.json", "ultima_busqueda.json"):
        ruta = raiz / "salidas" / archivo
        if ruta.is_file():
            st.download_button(f"Descargar {archivo}", ruta.read_bytes(), file_name=archivo,
                               key="descarga_"+archivo)

with tabs[4]:
    st.subheader("Del código a otro proyecto")
    st.markdown("""
**Mapa del código editable**

- inventario: descubre entradas y restringe extensiones/tamaño.
- _ocr_imagen / _ocr_pdf: transforman píxeles en texto probable.
- _asr: convierte voz en texto y segmentos con tiempos.
- ejecutar: registra fuente, licencia, SHA-256 y JSONL/Parquet.
- fragmentar: crea porciones de texto que puedes cambiar.
- _embed: consulta Ollama local para obtener vectores.
- indexar / buscar: almacenan fragmentos y ordenan por coseno.
- auditar: compara huellas del catálogo y los originales.

**Ejercicio de transferencia:** cambia el nombre del proyecto y una fuente; edita
un parámetro (por ejemplo psm=6 a 11); compara texto y ranking; registra como
evidencia las rutas, los hashes y la decisión que tomaste. La respuesta no es
«copié el comando»: es «cambié una decisión y vi el efecto».
""")
    st.info("Guía completa disponible en el archivo GUIA_REUTILIZACION.md del repositorio.")
