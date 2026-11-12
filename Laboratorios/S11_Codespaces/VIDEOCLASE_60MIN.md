# Videoclase de recuperación S11 — de datos multimedia a evidencia consultable

**Duración máxima:** 60 minutos (57 minutos de contenido + 3 de cierre)  
**Público:** Maestría en Analítica de Datos, Big Data 2026-2S, Universidad Central  
**Modalidad:** video grabado y laboratorio en Codespaces, con Python, Tesseract, Faster-Whisper y Ollama.  
**Objetivo:** entender, ejecutar, cuestionar y reutilizar el flujo **archivo → texto → información → catálogo → vector → resultado con fuente**, con un solo caso completo.

> **Este es un complemento, no un reemplazo de la sesión ETL original.** Lo esencial es la comprensión. Los detalles de histogramas, RMS, códecs, 42 activos, threads y Parquet avanzado permanecen en la presentación y el cuaderno original.

## Resultado de aprendizaje comprobable

Al final, un estudiante podrá (1) explicar qué hace cada motor y qué NO hace, (2) reproducir OCR y ASR reales, (3) comprobar sus errores contra la fuente original, (4) construir una consulta semántica con fuente/hash y (5) ejecutar el mismo diseño con archivos diferentes sin reescribir el motor.

## Antes de grabar: preparación técnica y ética

1. Abrir **Code → Codespaces → New with options** sobre **main** y elegir el perfil **S11 · OCR, voz y EmbeddingGemma 2** (no el de Airflow). Usar 2 CPU/8 GB, si está disponible. Evitar cargar archivos personales o ajenos sin permiso.
2. En la terminal del Codespace, ejecutar:
   ~~~bash
   cd Laboratorios/S11_Codespaces
   tesseract --list-langs
   python --version
   bash probar_todo.sh --ligero
   ~~~
   Verificar que Tesseract incluya **spa** y que la prueba ligera termine correctamente. No llamar “ASR validado” a la prueba ligera: utiliza dobles de prueba en las unitarias.
3. **Antes de iniciar la grabación**, descargar/calentar Whisper tiny mediante `python lab.py preparar && python lab.py asr` y Ollama mediante `bash iniciar_ollama.sh`. La primera descarga puede tardar: no debe ocupar minutos del video. Explicar en pantalla que los modelos ya fueron descargados, no ocultar el requisito.
4. Ejecutar `bash probar_todo.sh --completo` como comprobación separada antes de grabar. Requiere internet, CPU y descarga modelos. GitHub Actions ya ha probado OCR, Whisper real, EmbeddingGemma 2 y construcción del contenedor, pero **eso no reemplaza** la comprobación interactiva del Codespace que se vaya a filmar.
5. Preparar tres pestañas: esta guía, el archivo `lab.py` en VS Code y el explorador de `salidas/`. Para mostrar imágenes o escuchar WAV usar el visor/reproductor del editor o descargar el archivo. Tener preparada una segunda fuente autorizada y sin datos personales para el reto de reutilización.
6. No insertar como si fueran noticias propias las voces de MINDS-14: los audios bancarios de ese corpus NO pertenecen a las imágenes editoriales. **La demostración principal usa una imagen y voz sintéticas inventadas** deliberadamente para probar el flujo completo.

## Mapa de herramientas explicado en una diapositiva

| Herramienta | Traducción sencilla | Entrada → salida | Cómo se verifica |
|---|---|---|---|
| GitHub Codespaces | Computador Linux temporal en el navegador | Proyecto → entorno ejecutable | Terminal, herramientas e idiomas disponibles |
| Pillow | Abre/crea imágenes | Píxeles → imagen | Abrir el PNG |
| Tesseract + pytesseract | OCR, reconoce letras | Imagen → texto probable | Comparar con la imagen y usar CLI Tesseract |
| Faster-Whisper tiny | ASR, reconoce habla | Audio → texto y segundos | Escuchar, contrastar frase y calcular WER cuando hay referencia |
| Regex y módulo de extracción | Identifica candidatos | Texto → fechas, cifras, fragmentos | Rastrear cada candidato hasta el texto y archivo |
| JSON / JSONL / Parquet | Guarda documentos / filas / columnas | Registros → archivo consultable | Reabrir e inspeccionar |
| Ollama + EmbeddingGemma 2 (270m) | Codifica significado en números | Texto → vector de 768 componentes | API directa, dimensión y consulta con procedencia |
| Similitud coseno | Ordena fragmentos semejantes | Pregunta + vectores → ranking | Comparar ranking con los textos originales |

**Precisión:** EmbeddingGemma 2 no transcribe voz ni escribe una respuesta generativa. En esta ruta se usa la variante **270m, solo texto**. La variante **440m** permite texto e imagen y es opcional. No prometer audio directo en la distribución Ollama utilizada sin validarlo.

## Cronograma cerrado — 60 minutos

| Minutos | Capítulo | Acción que se ve | Pregunta de control |
|---|---|---|---|
| 00–04 | El caso y el objetivo | Mostrar afiche y voz simulados, dibujar el flujo | ¿Qué afirmaría con evidencia y qué no? |
| 04–09 | Herramientas, no magia | Abrir Codespaces, Tesseract, Python, `lab.py` | ¿Qué herramienta lee píxeles? |
| 09–18 | OCR | `preparar`, `ocr`, inspeccionar PNG y JSON | ¿Acertó las cifras? |
| 18–29 | ASR | `asr`, reproducir WAV, `evaluar-asr` | ¿“Terminó” significa “acertó”? |
| 29–36 | Extracción | `extraer`, abrir JSON, cotejar candidatos | ¿De qué fragmento salió esa cifra? |
| 36–41 | ETL y trazabilidad | Explicar RAW/derivados, JSONL/Parquet, hashes | ¿Qué preservamos y por qué? |
| 41–51 | Embeddings y búsqueda | `indexar`, `buscar`, API directa | ¿El coseno prueba la verdad? |
| 51–57 | Reutilizar el código | Nueva carpeta, nuevo TXT, plan/procesar/buscar | ¿Funciona con otro corpus? |
| 57–60 | Cierre y micro-reto | Repasar evidencias y proponer dos cambios | ¿Qué resultado verificarás tú mismo? |

**Producción:** incluir capítulos en el video, subtítulos, terminal con letra grande, zoom de cada salida y anotación visible “VERIFICADO / REVISAR / SIMULADO”. Nunca mostrar passwords, tokens ni credenciales.

---

## Libreto de grabación: exactamente qué decir, mostrar y comprobar

### 00:00–04:00 | La promesa del caso

**Diga:** «Hoy no vamos a pedirle a una inteligencia artificial que invente qué dice una fotografía o una grabación. Vamos a recuperar datos observables, guardar su origen y realizar preguntas que siempre podamos rastrear hasta el archivo. Nuestro caso de prueba es ficticio: una imagen dice que una entidad tuvo contratos y un audio sintético comunica una cantidad. La coincidencia entre esos archivos fue diseñada para aprender; no representa una noticia real. Al terminar, ustedes podrán cambiar ambos archivos por los de cualquier proyecto autorizado».

**Muestre:** flujo en seis cajas: **archivo → OCR/ASR → candidatos → catálogo → embeddings → búsqueda → comprobación humana**.

**Pregunta:** «¿Qué diferencia hay entre encontrar una cifra en el texto y demostrar que es verdadera?» **Responda:** «Lo primero es una extracción; lo segundo exige evidencia y contraste externo».

### 04:00–09:00 | Herramientas y ambiente

**Diga:** «Codespaces es un Linux preparado en el navegador. Python coordina; Pillow lee la imagen; Tesseract propone las letras; Faster-Whisper propone palabras y tiempos; Ollama ejecuta localmente un modelo que transforma texto en vectores. No son seis inteligencias artificiales haciendo lo mismo: cada una resuelve una etapa».

**Muestre:** terminal en `Laboratorios/S11_Codespaces`, archivo `lab.py` y el comando:
~~~bash
python lab.py --help
~~~
**Verificación:** señalar que existen acciones `preparar`, `ocr`, `asr`, `extraer`, `evaluar-asr`, `indexar`, `buscar`. **No recorrer los 336 renglones del programa**: mostrar una función pequeña a la vez.

### 09:00–18:00 | OCR: píxeles a texto

**Diga:** «Primero genero una imagen controlada. Como conozco el texto original puedo detectar errores del OCR sin confiar ciegamente en su resultado. Tesseract no lee un archivo TXT oculto: reconoce patrones de píxeles».

**Ejecute y muestre:**
~~~bash
python lab.py preparar
python lab.py ocr
cat salidas/ocr.json
~~~
Abra `salidas/afiche_simulado.png` y localice **CONTRATOS: 12** y **VALOR: 320 MILLONES**. Haga zoom en `lab.py` sobre:
~~~python
texto = pytesseract.image_to_string(im, lang="spa", config="--psm 6").strip()
~~~
**Explique:** `spa` es idioma español; `psm 6` supone un bloque de texto; `texto` es una **hipótesis**, no un hecho certificado.

**Verificación independiente, por fuera de `lab.py`:**
~~~bash
tesseract salidas/afiche_simulado.png stdout -l spa --psm 6
sha256sum salidas/afiche_simulado.png
cat salidas/origen.json
~~~
Contrastar el primer comando con `ocr.json`, y el hash con el inventario `origen.json`. Si una letra/cifra difiere, **conservar la discrepancia**: es aprendizaje.

**Pregunta:** «¿Qué haría OCR ante una fotografía sin letras?» **Respuesta:** puede devolver vacío; no es una descripción visual.

### 18:00–29:00 | ASR: ondas a palabras

**Diga:** «RMS y espectrograma describen propiedades de una señal, pero no son una transcripción. Para conocer las palabras de una voz necesitamos reconocimiento del habla. El archivo de prueba es una voz sintética generada localmente, y esa circunstancia afecta la calidad».

**Ejecute y muestre:**
~~~bash
python lab.py asr
cat salidas/asr.json
python lab.py evaluar-asr
cat salidas/evaluacion_asr.json
ffprobe -v error -show_entries format=duration,format_name -of default=noprint_wrappers=1 salidas/voz_simulada.wav
~~~
Reproduzca `salidas/voz_simulada.wav`; ubique un segmento con `inicio_s`, `fin_s` y `texto`. Resalte en `lab.py`:
~~~python
segmentos, info = modelo.transcribe(str(path), language="es", beam_size=1)
~~~
**Explique:** `tiny` es un modelo liviano; `CPU` indica procesador; `int8` reduce precisión numérica para inferencia más económica; `segmentos` registra tiempo. La transcripción fue **inferida desde el WAV**, no copiada de la frase de referencia.

**Verificación independiente:** escuchar la fuente y contrastar palabras y cifras, especialmente **doce contratos** y **trescientos veinte millones**. La evaluación WER de `lab.py` es una **métrica automatizada** contra la referencia conocida; la escucha es el contraste independiente. Un WER alto de voz sintética no describe la calidad del modelo en todo español.

**Pregunta:** «Si el programa escribe 200 y la voz dijo 320, ¿el pipeline funcionó?» **Respuesta:** técnicamente sí terminó, pero el dato requiere corrección humana.

### 29:00–36:00 | Extracción de candidatos y evidencia

**Diga:** «Transformar sonido en palabras todavía no nos da una ficha. Buscamos posibles fechas, entidades y cifras, pero ninguna coincidencia de texto verifica por sí sola la realidad del dato».

**Ejecute y muestre:**
~~~bash
python lab.py extraer
cat salidas/extraccion.json
~~~
Explique que **expresiones regulares** (`regex`) encuentran patrones: por ejemplo una fecha como `10-11-2026`. Del audio se extraen candidatos preservando el fragmento y, si existen, sus segundos.

**Verificación independiente:** elija una fecha y una cifra candidatas del JSON; localícelas visualmente en la imagen y confirme que se encuentran en el texto OCR. Para una entidad del audio, reproduzca el intervalo. Si no hay evidencia directa, no afirmar que se comprobó.

### 36:00–41:00 | ETL y procedencia sin tecnicismos innecesarios

**Diga:** «E significa extraer; T significa transformar; L significa cargar o guardar. Hay tres cosas diferentes: los bytes originales que debo preservar, la interpretación que generó un motor y un catálogo que me permite saber dónde está cada resultado».

**Muestre:** `salidas/origen.json`, `salidas/ocr.json`, `salidas/asr.json`. Enfatice **SHA-256: igualdad de bytes, NO prueba de autenticidad de la noticia**.

**Explique en una frase cada formato:** JSON = un documento estructurado; JSONL = un registro JSON por línea; Parquet = datos tabulares en columnas, con tipos. En la ruta introductoria se usa JSON; al reutilizar el proyecto se produce `catalogo.jsonl` y `catalogo.parquet`. El cuaderno S11 original profundiza en Parquet, lotes y métricas.

### 41:00–51:00 | Texto a vectores y búsqueda con EmbeddingGemma 2

**Diga:** «OCR y Whisper producen texto. EmbeddingGemma 2 no vuelve a leer el archivo original: en esta ruta convierte texto en 768 números para comparar significados. Una consulta se transforma del mismo modo. El motor ordena candidatos por cercanía de sus representaciones. No entrega un certificado de verdad ni una respuesta redactada como un chatbot».

**Ejecute y muestre (Ollama debe estar preparado):**
~~~bash
ollama list
python lab.py indexar
python lab.py buscar --consulta "¿Cuántos contratos había?"
python lab.py buscar --consulta "¿Qué valor se mencionó?"
~~~
Abra `salidas/indice.json`: mostrar **modelo**, **dimension**, **documentos**, **fuente**, **sha256** y un fragmento. No imprimir cientos de números.

**Verificación independiente del motor desde su API:**
~~~bash
curl -fsS http://127.0.0.1:11434/api/embed \
  -H 'Content-Type: application/json' \
  -d '{"model":"embeddinggemma-2:270m","input":"Un contrato de ejemplo"}' \
  | python -c 'import json,sys; print(len(json.load(sys.stdin)["embeddings"][0]))'
~~~
Debe devolver **768** para el modelo utilizado. Comparar el primer resultado de dos preguntas con los textos fuente: un coseno alto indica similitud, **no exactitud de las cifras**.

**Muestre únicamente estas tres líneas de lógica:**
~~~python
# Tesseract: píxeles → texto
texto = pytesseract.image_to_string(imagen, lang="spa")
# Whisper: audio → segmentos (se recorren para formar texto)
segmentos, info = modelo.transcribe(ruta_audio, language="es")
# Ollama: texto → vector
respuesta = requests.post(url_local, json={"model": modelo_embedding, "input": textos})
~~~
La implementación robusta está en el repositorio; el estudiante debe poder reconocer esas llamadas y sus límites.

### 51:00–57:00 | Demostrar transferibilidad sin reescribir el motor

**Diga:** «Ahora borro mentalmente el caso anterior. El motor es el mismo y los archivos son distintos. Esta es la diferencia entre copiar un ejemplo y construir una solución reutilizable».

**Ejecute:**
~~~bash
python proyecto.py iniciar --destino proyectos/otro_caso
printf 'ACTA DEMO: entrega del pedido A17 el 15-11-2026.\n' > proyectos/otro_caso/entradas/textos/acta.txt
python proyecto.py plan --config proyectos/otro_caso/config.json
python proyecto.py procesar --config proyectos/otro_caso/config.json
python proyecto.py indexar --config proyectos/otro_caso/config.json
python proyecto.py buscar --config proyectos/otro_caso/config.json --consulta "¿Qué pedido se entrega?"
python proyecto.py auditar --config proyectos/otro_caso/config.json
~~~
**Muestre:** el nuevo `config.json`, `catalogo.jsonl`, `candidatos.jsonl` y `ultima_busqueda.json`. Ningún candidato queda atribuido a otro archivo. La fuente ahora es TXT (para ahorrar tiempo), pero el mismo motor admite imágenes, PDF y audio autorizados. En un segundo intento el estudiante debe colocar un archivo propio en `entradas/imagenes/` o `entradas/audios/` y repetir; ese intento es la verdadera evidencia de transferencia.

**Verificación independiente del catálogo (fuera del motor):**
~~~bash
python -c 'import json; from pathlib import Path; p=Path("proyectos/otro_caso/salidas/catalogo.jsonl"); filas=[json.loads(s) for s in p.read_text().splitlines()]; print(len(filas),[(r["tipo"],r["path"],len(r["sha256"])) for r in filas])'
~~~
Si alcanza el tiempo, abrir la interfaz opcional:
~~~bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
~~~
Mostrar que la interfaz llama las funciones del mismo `proyecto.py`, sin iniciar un tercer proyecto. El puerto 8501 debe permanecer **privado**.

### 57:00–60:00 | Cierre y reto de dos cambios

**Diga:** «Hoy tenemos una cadena verificable. Primero observo el archivo; después leo sus píxeles o su sonido; obtengo hipótesis de texto; extraigo candidatos; guardo de dónde vino todo; hago preguntas por significado y vuelvo a la fuente cuando necesito comprobar cifras. Si cambio el archivo y el sistema sigue funcionando, he empezado a reutilizarlo. Si una búsqueda me devuelve algo convincente pero incorrecto, aprendí a no confundir ranking con verdad».

**Micro-reto asincrónico:** incorporar **dos fuentes autorizadas de modalidades diferentes** a `proyectos/mi_reto`; cambiar **un solo parámetro** (PSM, modelo de Whisper o tamaño de fragmento); capturar el antes y después; abrir manualmente una fuente; ejecutar la auditoría. Entregar una tabla corta con **ruta, herramienta, resultado, error observado y comprobación**. No alterar la rúbrica oficial del Taller 2.

## Cinco verificaciones independientes que deben quedar visibles en el video

- **Integridad:** `sha256sum archivo` contra inventario. Detecta cambio de bytes, no falsedad.
- **OCR:** la CLI `tesseract` contra `ocr.json` **y** inspección de la imagen original.
- **ASR:** audio reproducido contra el texto inferido; `evaluar-asr` solo si existe referencia válida.
- **Índice:** llamada HTTP directa a Ollama, longitud de 768 y lectura de fragmentos con fuente/hash.
- **Transferencia:** proyecto nuevo con otro TXT o un archivo autorizado, conteo del JSONL y auditoría; ejecutar `python verificar_independiente.py --proyecto proyectos/otro_caso`.

## Criterios mínimos de aceptación antes de publicar la grabación

1. La ruta funciona desde un Codespace **nuevo**, no solo desde el equipo del docente.
2. `probar_todo.sh --ligero` y `--completo` distinguen las capacidades realmente probadas.
3. El afiche PNG y el WAV se pueden **ver/escuchar**; no se muestra únicamente el JSON.
4. El video enseña al menos un error de OCR/ASR y su verificación, sin “arreglar” manualmente la salida para que coincida.
5. La consulta conserva **texto, ruta, hash** y tiempo del segmento cuando corresponde.
6. El ejercicio con `proyectos/otro_caso` funciona sin modificar funciones del motor.
7. El minuto 60 contiene el cierre. Si la descarga de modelos retrasa una ejecución, se registra el tiempo real y se realiza un corte explicado, no se oculta la dependencia.
8. Los ejemplos son sintéticos o autorizados. No se distribuyen fotografías editoriales sin permiso ni datos personales.
9. La captura final se revisa por legibilidad: terminal, subtítulos, enlaces, volumen y advertencias.

## Material asociado

- [Laboratorio introductorio](./lab.py)
- [Motor reutilizable](./proyecto.py)
- [Interfaz Streamlit](./app.py)
- [Tutorial completo](./README.md)
- [Manual de transferencia](./GUIA_REUTILIZACION.md)
- [Verificador de pruebas ligeras/completas](./probar_todo.sh)
- [Presentación ETL original](../../Presentaciones/s11-etl-audio-imagenes.html)
- [Cuaderno ETL original](../../Cuadernos/11_ETL_Audio_Imagenes.ipynb)

**Nota de publicación:** el video debe ser una explicación con ejecución real grabada; este documento es el **libreto y plan de producción**, no un archivo de video grabado.

**Documentación oficial:** [Tesseract](https://tesseract-ocr.github.io/) · [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) · [EmbeddingGemma 2](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2?hl=es-419) · [Ollama](https://ollama.com/library/embeddinggemma-2) · [Codespaces](https://docs.github.com/en/codespaces).
