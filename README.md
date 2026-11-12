# S11 · Laboratorio de investigación multimedia (estudiantes)

**Universidad Central · Big Data**. Este Codespace es un kit de clase **reducido**: aquí no están Airflow, otros cursos, exámenes, respuestas docentes ni los motores extensos que hacen el trabajo por ti.

**Objetivo:** aprender a escribir Python, no ejecutar un programa ya construido. Vas a investigar **actas SECOP, 62 fotografías reales de dos conjuntos de El Tiempo y diez voces humanas licenciadas**. OCR extrae letras; EmbeddingGemma 2 permite recuperar fotos por significado; Whisper transcribe voz. Ninguno certifica la verdad de una afirmación.

## 1. Abrir el Codespace correcto

1. Abre [rama s11-estudiantes](https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes).
2. Comprueba que la rama seleccionada dice **s11-estudiantes**, nunca main.
3. Pulsa **Code → Codespaces → Create codespace on s11-estudiantes**. Este kit tiene un solo contenedor.
4. El explorador debe mostrar `01_laboratorio.ipynb`, `02_lotes_102_fuentes.ipynb`, `visor_fuentes.py`, `datos/raw`, `INSTALACION_UBUNTU.md`, `requirements.txt`, y poco más.
5. Abre **01_laboratorio.ipynb** para aprender OCR, búsqueda visual y Whisper con pocos ejemplos. Después abre **02_lotes_102_fuentes.ipynb** para ampliar a 102 fuentes y comparar tiempos, errores y resultados. Selecciona el kernel **Python 3** y modifica las celdas una a una.

**No necesitas Ubuntu local.** Codespaces es Linux en el navegador. Para comprender cómo se prepara el entorno, abre el [tutorial de instalación](./INSTALACION_UBUNTU.md): también se puede realizar en un Ubuntu propio cuando sea apropiado.


## Visor: abre CADA documento, fotografía y audio en una sola pantalla

La herramienta visual se llama visor_fuentes.py. Es complementaria al cuaderno: permite abrir los **30 PDF SECOP completos**, comparar cada PDF con su **primera página PNG**, recorrer las **62 fotografías originales** y escuchar **10 voces reales**.

En la terminal del Codespace:

~~~bash
streamlit run visor_fuentes.py --server.address 0.0.0.0 --server.port 8501
~~~

Abre el panel **Puertos / Ports**, localiza 8501 y selecciona **Abrir vista previa** (o abrir en el navegador). Mantén su visibilidad **Private**. Dentro del visor puedes filtrar por nombre o número de acta, usar Anterior/Siguiente, abrir el PDF y su página juntos, aplicar OCR al archivo visible y cambiar PSM. Las voces se preparan pulsando el botón **Preparar / comprobar las 10 voces**: se recupera el Parquet MINDS-14, se verifica su SHA-256 y se crea una copia PCM16 para reproducción. También se puede transcribir una voz seleccionada con Whisper.

**Importante:** el visor es para **observar fuentes y contrastar predicciones**. La actividad de aprendizaje permanece en 01_laboratorio.ipynb, donde escribirás Python y procesarás lotes completos. Esta interfaz no sustituye ese código.

### Qué material contiene el kit ampliado

- 30 fotografías El Tiempo en datos/raw/fotos.
- 32 fotografías con ficha en datos/raw/fotos_catalogadas.
- 30 PDF SECOP completos en datos/raw/actas_pdf.
- 30 vistas PNG de primera página en datos/raw/actas.
- 10 voces humanas MINDS-14 descargables y verificables desde la herramienta.

**Total para investigar: 62 fotografías + 30 actas distintas + 10 audios = 102 fuentes.** Las 30 vistas PNG son derivados de las actas y no deben contabilizarse como otros treinta documentos. Los 10 audios se obtienen al ejecutar el botón o el código de preparación, no vienen incluidos como bytes en Git.

## 2. Los archivos disponibles son reales

| Carpeta | Archivos | Pregunta |
|---|---|---|
| `datos/raw/actas` + `datos/raw/actas_pdf` | 30 actas completas PDF y sus PNG de primera página | ¿Cuál es el total, descuento y neto a pagar? |
| `datos/raw/fotos` + `datos/raw/fotos_catalogadas` | 62 fotografías de dos conjuntos de El Tiempo | ¿Qué letreros reconoce OCR? ¿Qué imagen contiene viviendas? |
| `datos/raw/audios` + `datos/derived/audios` | 10 WAV humanos PolyAI MINDS-14 es-ES, CC BY 4.0 | ¿Qué dice y qué errores tiene la transcripción? |

La grabación es bancaria y **no pertenece a las noticias**. Los documentos SECOP pueden mostrar datos personales: al compartir capturas o exportar resultados, minimízalos. Las imágenes periodísticas conservan los derechos de sus titulares; los créditos por archivo del subconjunto de 30 todavía requieren curaduría (no inventes licencias).

## Ruta de dos cuadernos

**01_laboratorio.ipynb (fundamentos, para el video):** escribes cómo abrir imágenes, OCR de un acta, vectores de cuatro fotografías y ASR de una voz.

**02_lotes_102_fuentes.ipynb (investigación por lotes):** escribes bucles sobre 30 actas, 62 fotografías, una selección de 10 voces, búsqueda vectorial y un catálogo JSONL/Parquet de 102 filas. Empieza con N_ACTAS=5, N_FOTOS=8, N_VISION=8 y N_ASR=3; después modifica esas cifras a 30, 62, 62 y 10 y explica qué cambió.

**visor_fuentes.py (vista, no solución):** muestra una fuente a la vez con anterior/siguiente, cada PDF y su PNG, imágenes periodísticas y un reproductor de audios reales. El visor no sustituye escribir y justificar el código de los dos cuadernos.

## 3. Mapa de la sesión (60 minutos)

| Tiempo | Aprendizaje que tú construyes |
|---|---|
| 00–06 | `Path` y Pillow: abrir y observar imágenes; explicar bytes/píxeles |
| 06–18 | Tesseract: OCR de un acta y comparar PSM 6, 11, 3 |
| 18–25 | OCR en letreros, contraste con fotos sin texto |
| 25–35 | Ollama + EmbeddingGemma 2 **440m**: vectores de imágenes y consulta por coseno |
| 35–44 | Audio MINDS-14 + Whisper tiny: escuchar, transcribir, cotejar WER |
| 44–54 | Bucles, diccionarios, JSONL, Parquet y SHA-256 |
| 54–60 | Tu reto: cambia fuente, parámetro y consulta; explica un error |

## 4. Qué comprobar antes de iniciar

En la terminal del Codespace:

~~~bash
python --version
tesseract --list-langs
python -c "from PIL import Image; import pytesseract,pandas,pyarrow,requests,faster_whisper; print('Python listo')"
~~~

Debe aparecer `spa`. Para preparar Ollama (solo cuando llegues al bloque de búsqueda visual) sigue `INSTALACION_UBUNTU.md` y descarga el modelo visual **embeddinggemma-2:440m**; no confundas el de texto **270m** con uno que pueda interpretar imágenes.

**Un estudiante aprende cuando:** (1) puede explicar qué hace cada línea, (2) modifica algo y predice qué pasará, (3) compara el resultado contra la fuente, y (4) transfiere el mismo procedimiento a una imagen o documento diferente. No entregues un simple pantallazo de una celda que se ejecutó.

## 5. Explorador mínimo y privacidad

Los originales se guardan en `datos/raw`. Las salidas se generan en `outputs/`, que está ignorada por Git. No subas transcripciones completas de datos personales ni WAV de terceros sin autorización.

**Advertencia:** la rama s11-estudiantes contiene solo estos materiales de clase, pero eso NO hace privados los demás archivos del repositorio público. El aislamiento real de material reservado requiere un repositorio privado independiente.

Más sobre licencias y fuentes: [FUENTES.md](./FUENTES.md).
