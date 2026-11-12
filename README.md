# S11 · Una presentación + un cuaderno + un Codespace

**Universidad Central · Big Data · versión para estudiantes**

**Objetivo:** escribir Python, entender qué hace cada herramienta y pasar de ejemplos pequeños a **122 fuentes** sin ejecutar programas que resuelvan todo por ti.

## Los tres elementos de esta clase

1. **[Presentación S11](https://jazaineam1.github.io/BigData2026/Presentaciones/s11-videoclase-ocr-asr-embeddings.html#s1)**: explica cada pregunta, instalación, idea de código y comprobación; úsala mientras sigues el video.
2. **[01_laboratorio.ipynb](./01_laboratorio.ipynb)**: **único cuaderno**. FASE 1: construyes y compruebas OCR, búsqueda visual y ASR; FASE 2: amplías los bucles a lotes de 122 fuentes y generas JSONL/Parquet.
3. **Codespace S11 + visor privado**: ofrece Python, Tesseract, **Ollama integrado en el entorno**, Jupyter y un visor para abrir **cada PDF completo, PNG, foto y WAV**, sin abandonar el navegador. El visor es una ayuda de inspección y no sustituye escribir el código.

**No hay un segundo cuaderno, una segunda presentación ni Airflow en este kit.** Los archivos `INSTALACION_UBUNTU.md` y `FUENTES.md` son documentación de consulta, no pasos que debas ir ejecutando paralelamente.

## Paso 1 · Crear el Codespace correcto

1. Abre **https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes**. Comprueba que el selector de rama muestra **s11-estudiantes**, NO `main`.
2. Haz clic en **Code → Codespaces → Create codespace on s11-estudiantes**. Si se ofrece una configuración, selecciona **S11 · OCR, visión y voz (aprende Python)**.
3. Espera a que aparezca VS Code y se complete la instalación indicada por `postCreateCommand`. **El Codespace instala Ollama y las bibliotecas a partir de su configuración**; comprueba sus versiones en la terminal. No cambies de rama dentro del Codespace.
4. En el explorador abre **01_laboratorio.ipynb**. Arriba a la derecha elige **Select Kernel → Python 3** del Codespace.
5. Abre **Terminal → New Terminal** y comprueba:

~~~bash
pwd
python --version
tesseract --list-langs
command -v ollama
ollama --version
bash iniciar_ollama.sh
curl -fsS http://127.0.0.1:11434/api/tags
python -c "from PIL import Image; import pytesseract,pandas,pyarrow,requests,faster_whisper,streamlit; print('Python OK')"
~~~

**Resultado:** la ruta termina en `/workspaces/BigData2026`, aparece `spa` en Tesseract, `command -v ollama` devuelve `/usr/bin/ollama`, la API responde JSON y se imprime `Python OK`. Si no es así, consulta «Solución de problemas», al final.

**Qué aprendiste:** Codespaces es Linux remoto. `.devcontainer/Dockerfile` instala programas del sistema; `requirements.txt` instala bibliotecas Python; `.devcontainer/devcontainer.json` coordina la instalación. En Ubuntu propio se puede replicar siguiendo `INSTALACION_UBUNTU.md`.

## Paso 2 · Abrir y recorrer TODAS las fuentes en el visor

El visor se inicia automáticamente con `abrir_visor.sh`. Si no ves la vista previa:

~~~bash
bash abrir_visor.sh
curl -fsS http://127.0.0.1:8501/_stcore/health
~~~

En VS Code abre **Ports / Puertos**, elige **8501 → Open Preview / Abrir vista previa**. Confirma **Visibility: Private**. También puedes ejecutar manualmente:

~~~bash
streamlit run visor_fuentes.py --server.address 0.0.0.0 --server.port 8501
~~~

**Documento recomendado para comenzar:** elige **Actas SECOP (30)** y busca **728704921**. Abre la página 1 de su PDF, donde aparecen el contrato **006-2026**, el valor **$14.760.000**, el plazo de **6 meses** y la forma de pago en **6 cuotas de $2.460.000**. Selecciona **PSM 3** para detectar el diseño completo, ejecuta OCR y compara el texto íntegro con la referencia visual. Prueba luego PSM 6 y PSM 11; si cambian las lecturas, explica por qué.

En esta pantalla tienes cuatro selecciones de fuentes:

| Colección del visor | Qué se puede abrir | Para qué la usamos |
|---|---|---|
| El Tiempo (30) | Cada una de las 30 fotografías originales | OCR de letreros, análisis visual |
| Fotografías con ficha (32) | Cada fotografía, con crédito y URL cuando existen | Búsqueda visual y atribución |
| Actas SECOP (30) | **30 PDF completos**, junto a **30 PNG de primera página** | OCR de tablas, importes y referencias |
| Voces MINDS-14 (30) | 30 WAV humanos y referencia de transcripción | ASR, escucha, WER |

**Antes de usar los audios:** en la barra lateral pulsa **Preparar / comprobar las 30 voces**. El visor descarga un Parquet oficial (~39 MB), verifica SHA-256 y guarda WAV de fuente y derivados PCM16. Los audios no se alojan como binarios en GitHub. También puedes crearlos con las celdas del cuaderno.

**Total: 122 fuentes** = 62 fotografías + 30 actas + 30 voces. Las 30 vistas PNG de actas no son otros 30 documentos. No presupongas que una foto, un acta y un audio corresponden al mismo acontecimiento.

**Importante:** el visor **no es una página pública de GitHub Pages**; se abre desde tu Codespace privado. No publiques el puerto 8501 ni capturas completas de actas con datos personales.

## Paso 3 · Ejecutar el ÚNICO cuaderno (FASE 1: aprender)

Haz doble clic en `01_laboratorio.ipynb`. Lee el texto de una sección, **explica las líneas de su celda** y ejecuta con **Shift + Enter**. No ejecutes «Run All» sin entenderlo: hay descargas y procesos CPU que necesitan tiempo.

| Tema | Qué escribes en Python | Qué compruebas |
|---|---|---|
| Leer archivos | `Path`, `Image.open`, `display` | Foto original, formato y resolución |
| OCR de acta | `pytesseract.image_to_string(..., lang="spa")` | Valores contra página SECOP |
| OCR y PSM | `--psm 6`, `--psm 11`, `--psm 3` | Efecto sobre columnas y texto disperso |
| OCR de fotos | Bucle sobre cuatro fotos | Letreros vs escenas sin caracteres |
| Embeddings visuales | HTTP `/api/embed` + Base64 | Vector de 768 dimensiones y ranking |
| Whisper | `WhisperModel("tiny", ...)` | Audio, segmentos, referencia y WER |
| Catálogo ETL | Diccionarios, JSONL, Parquet y SHA-256 | Procedencia, integridad y lectura posterior |

**Ollama forma parte del Codespace de práctica.** En esta versión del laboratorio toda solicitud a `/api/embed` usa `input` como lista, incluso para una sola fotografía: `{"model": MODELO, "input": [{"image": imagen64}]}`. Para una pregunta: `{"model": MODELO, "input": ["viviendas en una ladera"]}`.

 Para iniciar el servidor y descargar el modelo visual 440m, ejecuta **un único comando**:

~~~bash
bash preparar_embeddinggemma.sh
~~~

La preparación comprueba el servicio, descarga `embeddinggemma-2:440m`, consulta la API local y confirma los **768 valores** del vector. Comprueba tanto una **consulta de texto** como una **fotografía real** usando `{"input": [entrada]}`; el resultado de cada elemento se recupera en `embeddings[0]`. Puedes estudiar las instrucciones de instalación del entorno en `INSTALACION_UBUNTU.md`.

Para replicar el laboratorio en Ubuntu propio, consulta `INSTALACION_UBUNTU.md`. Para analizar **imágenes** usa el modelo **440m**; el modelo 270m se limita a texto.

## Paso 4 · SIN CAMBIAR DE CUADERNO, pasar a FASE 2

Baja a la sección titulada **«FASE 2 · Las mismas funciones, ahora sobre 122 fuentes»** dentro de **01_laboratorio.ipynb**.

Escribe los bucles y comienza con muestras manejables:

| Parámetro de las celdas | Durante la explicación | Para la práctica completa |
|---|---:|---:|
| `N_ACTAS` | 5 | 30 |
| `N_FOTOS` | 8 | 62 |
| `N_VISION` | 8 | 62 |
| `N_ASR` | 3 | 30 |

Las celdas realizan inventario, OCR documental, OCR fotográfico, embeddings con caché por SHA, ranking por coseno, descarga y conversión de WAV, WER con referencia y catálogo ETL. **El procesamiento completo de 62 embeddings visuales y 30 voces puede exceder los 60 minutos**; la videoclase enseña el procedimiento con una muestra, y el alumno amplía los parámetros posteriormente.

**Resultado del catálogo:** `outputs/catalogo_122.jsonl` y `outputs/catalogo_122.parquet` con **122 filas**. La auditoría reabre ambos y comprueba de nuevo los hashes de originales. Otros resultados incluyen métricas de OCR y `outputs/vectores_440m.json`.

**La práctica no exige 122 transcripciones completas dentro del video:** separa los indicadores que se obtienen de cada fuente de las inferencias que realizas por lotes.

## Paso 5 · Evidencia de aprendizaje

Escribe una tabla o breve explicación con estas columnas:

`pregunta | archivo y fuente | motor elegido | código o parámetro que cambié | resultado | cómo lo verifiqué | límite/error`

Debes demostrar: un valor SECOP comparado con el PNG; OCR de un letrero; una consulta visual cambiada; una voz escuchada y comparada con su referencia; una fila del catálogo con SHA-256 verificado. **No basta con mostrar «ejecución exitosa».**

## Preguntas de clase

- ¿Por qué Tesseract no puede responder qué objetos aparecen en una foto sin palabras?
- ¿Qué significa PSM y por qué una tabla puede leerse peor con otro valor?
- ¿Qué función cumple Base64 en una llamada HTTP para embeddings?
- ¿Qué mide realmente la similitud coseno y qué **no** demuestra?
- ¿Cómo se calcula WER si existe referencia humana, y qué ocurre si no existe?
- ¿Por qué JSONL, Parquet y SHA-256 cumplen funciones diferentes?
- ¿Cómo cambia el tiempo de procesamiento al pasar de 5 a 30 actas o de 8 a 62 fotos?

## Solución de problemas

| Problema | Qué revisar |
|---|---|
| Aparecen Airflow o otros cursos | Estás en `main` u otro Codespace; selecciona `s11-estudiantes` |
| Falta `spa` | Comprueba `tesseract-ocr-spa` en el Dockerfile; reconstruye contenedor |
| No carga el kernel | Verifica `ipykernel` y selecciona el Python del Codespace |
| Visor no aparece | `bash abrir_visor.sh`; estado de puerto 8501 y pestaña Ports |
| PDF no se ve | Revisa soporte Streamlit PDF; también puede descargarse el original |
| No hay audios | Pulsa preparar voces; revisa red, HF y SHA-256; no inventes sustitutos |
| No se identifica el ejecutable Ollama | Comprueba Dockerfile y vuelve a crear el entorno del Codespace desde la configuración |
| Ollama no responde | `bash iniciar_ollama.sh`; revisa `/tmp/s11-ollama.log` y `127.0.0.1:11434` |
| Modelo 440m no aparece | `bash preparar_embeddinggemma.sh`, luego `ollama list` |
| Error por memoria o lentitud | Reduce `N_VISION` o `N_ASR`, conserva la caché y reintenta |
| `NameError` | Ejecuta las celdas anteriores en orden y verifica las variables |
| OCR se ejecuta pero se equivoca | Compara píxeles/PSM; no transformes un error en un supuesto acierto |

## Fuente, licencia y privacidad

- Las fotos de El Tiempo **no tienen todas créditos y permisos confirmados por archivo**. Consulta `FUENTES.md` antes de redistribuir.
- Las actas SECOP pueden contener identificaciones personales; evita publicar sus salidas OCR completas o capturas sensibles.
- Las voces reales proceden de **PolyAI MINDS-14 es-ES, CC BY 4.0**; son audios bancarios y **no corresponden a las fotos periodísticas**.
- Esta rama mínima no vuelve privados los archivos que ya existan en otras ramas públicas del repositorio.

**El libreto de narración del profesor es de uso privado y no forma parte del Codespace estudiantil.**
