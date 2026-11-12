# Recuperación de S11 · OCR, transcripción y EmbeddingGemma 2

**Para la videoclase de máximo 60 minutos:** empieza con el [libreto operativo y verificaciones independientes](./VIDEOCLASE_60MIN.md) y la [presentación breve de 13 pantallas](../../Presentaciones/s11-videoclase-ocr-asr-embeddings.html). Para el alumnado, la ruta corta es [Guía del estudiante: ejecutar y verificar](./GUIA_ESTUDIANTE.md). La ruta usa primero `lab.py` y, solo al final, `proyecto.py`; este README queda como referencia completa.


**Big Data 2026-2S — Universidad Central**  
**Caso transversal:** Laura / Compras Claras  
**Modalidad:** GitHub Codespaces, Python y Ollama local; sin GPU ni servicios comerciales obligatorios.

La clase anterior quedó sin cubrir OCR ni transcripción. Aquí se enseñan ambos **desde cero, con código ejecutable**, y se conectan con búsqueda semántica (S09). Esta **práctica formativa** complementa, pero **no sustituye**, el ETL ni el Taller 2 existentes.

## Material que ya tenemos y vamos a reutilizar

- [Presentación actual de S11](../../Presentaciones/s11-etl-audio-imagenes.html)
- [Cuaderno original S11 para Colab](../../Cuadernos/11_ETL_Audio_Imagenes.ipynb)
- [Motor ETL que verifica fuentes, RAW y derivados](../../utils/s11_etl_core.py)
- [Lector OCR y evaluación ASR del Taller 2](../../utils/tc2_core.py)
- [Verificador externo de calidad e integridad](./verificar_independiente.py)
- [Extracción de información en audios](../../utils/s11_audio_noticia.py)
- [Licencia, identidad y trazabilidad de las voces](../../Datos/s10_audio_reales/README.md)

El repositorio tiene inventario de **32 fotografías editoriales de 24 artículos** y un corpus de **diez voces humanas de MINDS-14 en español**. **No son audios de las noticias**. El código conserva la separación entre article_id (foto) y source_record_id (voz). No hay video en S11 por la adaptación docente ya documentada en el repositorio.

### Producto final

Un conjunto de archivos original y derivado con SHA-256, texto OCR, texto ASR segmentado, embeddings de 768 dimensiones y resultados de búsqueda con fuentes. En la clase S11 existente se añade la construcción formal del catálogo JSONL/Parquet, manifiesto y auditoría de integridad.

### Mapa de etapas

| Etapa | Problema | Evidencia |
|---|---|---|
| Recibir | ¿De dónde salió el dato? | Origen y SHA-256 |
| Leer imagen | ¿Qué letras se ven? | OCR e imagen original |
| Escuchar | ¿Qué se pronunció? | Transcripción y segundos |
| Indexar | ¿Cómo buscar por significado? | Vectores y metadatos |
| Auditar | ¿Qué no puedo afirmar? | Contraste con el original y límites |

## Interfaz de usuario disponible en Codespaces

El mismo motor `proyecto.py` puede ejecutarse con una **interfaz web local** opcional: [app.py](./app.py), construida con Streamlit. Permite cargar imágenes, audio, PDF o TXT; definir algunos parámetros; procesar OCR/ASR; indexar y buscar con Ollama; inspeccionar los originales y descargar el catálogo. No sustituye el código: cada acción llama las funciones de `proyecto.py`.

En la terminal de Codespaces, desde `Laboratorios/S11_Codespaces`:

~~~bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
~~~

Abre el enlace del **puerto 8501** que muestra Codespaces. **Mantén su visibilidad privada**, pues los datos permanecen dentro del Codespace y no deben exponerse públicamente. El panel no envía archivos a una API externa; Ollama se consulta en `localhost`. Para abrirlo basta un navegador, pero iniciar la máquina y ejecutar modelos consume cuota de Codespaces.

**La interfaz es opcional.** El tutorial también enseña a ejecutar los comandos directamente, y los estudiantes deben revisar/modificar las funciones en `proyecto.py`, no depender de botones.

## Cómo convertir el ejemplo en un proyecto independiente

El laboratorio `lab.py` es la ruta **introductoria**: primero una imagen y un audio, para entender qué hace cada herramienta. La ruta **transferible** ya está implementada en [proyecto.py](./proyecto.py): lee **carpetas completas** de imágenes, PDF, audios y textos aportados por cada estudiante; acepta parámetros desde `config.json`; guarda JSONL, Parquet, candidatos estructurados en `candidatos.jsonl`, índices y errores; verifica integridad; permite recuperar por significado.

**[Manual completo para comprender y modificar cada función](./GUIA_REUTILIZACION.md)**. Incluye parámetros, ejemplos de código sustituible, uso de otros formatos, proyecto propio, pruebas y un mini-reto con evidencias reales. No es necesario seguir trabajando con las noticias de Compras Claras.

### Ruta corta: ejecución de otro proyecto

~~~bash
cd Laboratorios/S11_Codespaces
python proyecto.py iniciar --destino proyectos/ejemplo_nuevo
printf 'El contrato 18 tiene valor 320000 COP\n' > proyectos/ejemplo_nuevo/entradas/textos/prueba.txt
python proyecto.py plan --config proyectos/ejemplo_nuevo/config.json
python proyecto.py procesar --config proyectos/ejemplo_nuevo/config.json
bash iniciar_ollama.sh
python proyecto.py indexar --config proyectos/ejemplo_nuevo/config.json
python proyecto.py buscar --config proyectos/ejemplo_nuevo/config.json --consulta "¿Qué contrato tiene un valor?"
python proyecto.py auditar --config proyectos/ejemplo_nuevo/config.json
~~~

La ruta procesa solo el TXT de demostración; para activar OCR y ASR coloca archivos **propios o autorizados** en entradas/imagenes, entradas/documentos o entradas/audios. El proyecto generado no requiere modificar rutas del código ni repetir el caso editorial. **Los datos dentro de proyectos/ están excluidos de Git** para evitar publicar por error archivos de los estudiantes.

### Cómo comprobar que se entendió

1. Reconocer qué función transforma píxeles en texto, cuál transforma voz en palabras y cuál convierte texto en vectores.
2. Cambiar un parámetro y observar el antes/después de una misma fuente.
3. Cambiar de corpus sin tocar el código de las fuentes editoriales.
4. Reconocer un error, verificar la procedencia y auditar que los bytes originales no cambiaron.

### Verificar que la instalación y los modelos funcionan

Al abrir Codespaces, desde Laboratorios/S11_Codespaces ejecuta `bash probar_todo.sh --ligero` para comprobar sintaxis, OCR real, Parquet e integridad con datos simulados. Si tienes recursos disponibles, `bash probar_todo.sh --completo` realiza también transcripción e inferencia real en Ollama. **El modo completo no se ha validado desde esta conversación en una máquina Codespaces real** y debe pasar antes de publicar la actividad a todo el grupo.

### Comprobación independiente y ficha de extracción

Después de OCR, ASR e indexación del ejemplo, ejecuta:

~~~bash
python verificar_independiente.py --caso lab --modelo
~~~

El motor genérico genera también `salidas/candidatos.jsonl` con fechas, cifras y referencias detectadas, con ruta, fuente y hash. Para auditar sin ejecutar las funciones del motor:

~~~bash
python verificar_independiente.py --proyecto proyectos/mi_reto
~~~

Estas comprobaciones no reemplazan el contraste humano de imagen/audio.

## Paso 1. Crear Codespace de S11

1. Abre [el repositorio](https://github.com/jazaineam1/BigData2026).
2. Escoge la rama que contiene este laboratorio. La versión integrada de este laboratorio está en **main**; si revisas una mejora abierta en un pull request, selecciona su rama.
3. Pulsa **Code → Codespaces → … → New with options**.
4. En **Dev container configuration**, selecciona **S11 · OCR, voz y EmbeddingGemma 2**. Su archivo está en la carpeta .devcontainer/s11-multimedia. **No es el perfil Airflow Lab** que también existe.
5. Usa 2 CPU y 8 GB si tu cuenta lo permite. La memoria y el tiempo de máquina dependen de tu cuota de GitHub.
6. Ya dentro de VS Code, abre **Terminal → New Terminal**.

Ejecuta:

    cd Laboratorios/S11_Codespaces
    python --version
    tesseract --list-langs
    python lab.py --help

**Debe verse:** Python 3.11, idioma spa y comandos preparar, fuentes-repo, ocr, asr, extraer, indexar, buscar e imagen.

**Si no:** espera a que termine la instalación del contenedor. Si escogiste Airflow, crea un Codespace nuevo con el perfil S11 o reconstruye el contenedor con la configuración correcta. Puedes instalar las dependencias desde esta carpeta con:

    python -m pip install -r requirements.txt

## Paso 2. Fabricar dos fuentes sin dependencia externa

Primero crearemos **datos simulados**, no noticias ni audio periodístico real. Esto permite aprender la tubería incluso si falta internet:

    python lab.py preparar
    cat salidas/origen.json

**Qué hace:** Pillow dibuja un afiche con texto y cifras ficticias. Espeak-ng sintetiza una voz española en WAV. Se guarda una ficha con generador y huella SHA-256 de ambos archivos.

**Cómo se lee:** una huella SHA-256 tiene 64 caracteres hexadecimales y representa los bytes.  
**Qué nos dice:** permite detectar cambios posteriores.  
**Qué NO permite concluir:** que la noticia exista, que sus datos sean auténticos o que foto y audio estén asociados.  
**Error común:** tratar SHA-256 como certificación de veracidad.

## Paso 3. OCR verdadero, leyendo píxeles

Ejecuta:

    python lab.py ocr
    cat salidas/ocr.json

**OCR** = reconocimiento óptico de caracteres. El programa abre la imagen y llama a Tesseract. No lee un texto preestablecido.

La llamada utilizada es:

    pytesseract.image_to_string(imagen, lang="spa", config="--psm 6")

- **lang spa:** reconoce letras y signos usando español.
- **psm 6:** presupone un bloque de texto relativamente uniforme; otra distribución puede exigir un modo distinto.
- **texto_extraido:** hipótesis del OCR.
- **fuente y sha256:** vinculan la hipótesis con los píxeles realmente procesados.

**Ejemplo manual:** si la imagen dice CONTRATOS: 12 pero el OCR devuelve CONTRAT0S: 12, reconoció la cifra pero confundió una letra. Para verificar hay que mirar el original.

**Con imagen autorizada propia:** desde el explorador de VS Code arrastra un PNG o JPG a la carpeta salidas y ejecuta:

    python lab.py ocr --archivo salidas/mi_imagen.png

**Cómo se lee:** compara texto_extraido contra la fotografía.  
**Qué nos dice:** qué caracteres son candidatos a indexación.  
**Qué NO permite concluir:** que el OCR entienda la escena o que las cantidades sean verdaderas.  
**Error común:** esperar una descripción visual a partir de una foto sin letras.

## Paso 4. ASR verdadero: reconocer voz

Ejecuta:

    python lab.py asr
    cat salidas/asr.json

**ASR** = reconocimiento automático del habla. Faster-Whisper abre la señal WAV y ejecuta el modelo multilingüe **Whisper tiny** con CPU e INT8. La primera ejecución descarga los pesos. **No toma como respuesta el texto con el que se generó la voz**: infiere el habla desde el audio.

En el JSON revisa:

- **transcripcion:** concatenación del texto inferido.
- **segmentos:** inicio_s y fin_s para ubicar dónde se dijo algo.
- **sha256:** huella del archivo realmente escuchado.
- **modelo:** versión y configuración del reconocedor.

**WER** (tasa de error de palabras): (sustituciones + eliminaciones + inserciones) / palabras de la transcripción humana de referencia. Si hay cuatro palabras y dos errores, WER = 0,50. El script **no inventa WER** si no se ha proporcionado una referencia humana.

**Con voz real propia o autorizada:**

    python lab.py asr --archivo salidas/mi_audio.wav

Para un archivo largo, inspecciona primero **contenedor y códec**. El caso anterior 3530042.wav del curso enseñó precisamente que la extensión .wav no garantiza que los bytes estén codificados como PCM. En una demostración con CPU conviene producir una copia de 20 segundos:

    ffprobe -v error -show_entries format=duration,format_name -of default=noprint_wrappers=1 salidas/mi_audio.wav
    ffmpeg -y -i salidas/mi_audio.wav -t 20 -ar 16000 -ac 1 salidas/muestra_20s.wav
    python lab.py asr --archivo salidas/muestra_20s.wav

El recorte **no representa un límite de 60 segundos de Whisper**.

**Cómo se lee:** escucha y compara cada segmento.  
**Qué nos dice:** existen palabras probables que podemos buscar y estructurar.  
**Qué NO permite concluir:** que todos los nombres, números y citas estén bien reconocidos.  
**Error común:** confundir RMS y espectro con lenguaje hablado.

### Medir la calidad: el sistema puede funcionar y aun así equivocarse

Cuando hayas transcrito la voz simulada con `python lab.py asr`, ejecuta:

~~~bash
python lab.py evaluar-asr
cat salidas/evaluacion_asr.json
~~~

El programa compara la **transcripción producida por Whisper** con la **frase original conocida** que se usó para sintetizar esta voz. Calcula una tasa WER real mediante distancia de edición a nivel de palabras, no la inventa. Al comparar ignoramos mayúsculas y puntuación; aun así, el acento artificial puede inducir errores grandes. La ejecución real de GitHub Actions produjo sustituciones en palabras y cifras con Whisper tiny, lo que demuestra por qué `ASR terminó` no significa `ASR acertó`.

**Cómo se lee:** `wer` es proporción de errores de palabras respecto de las palabras de referencia; puede exceder 1 si hay muchas inserciones.
**Qué nos dice:** exactitud de esta grabación sintética concreta frente a su referencia.
**Qué NO permite concluir:** la calidad de Whisper para todos los audios en español; faltan muestras diversas y referencias humanas verificadas.
**Error común:** calcular WER sobre un audio real sin referencia o usar la similitud semántica para validar una cifra que Whisper reconoció mal.

## Paso 5. Conectar con los activos REALES del repositorio

Usamos el **mismo motor de S11** que verifica las 32 imágenes del snapshot docente y la colección MINDS-14 español. No utilizamos scraping de noticias, ni juntamos un audio bancario a una imagen editorial.

Para traer **dos fotografías y dos voces**:

    python lab.py fuentes-repo --imagenes 2 --audios 2
    cat salidas/fuentes_repo.json

El comando imprime dos rutas exactas: una imagen y una voz. Copia esas rutas y ejecuta:

    python lab.py ocr --archivo RUTA_QUE_SE_IMPRIMIO_DE_LA_IMAGEN
    python lab.py asr --archivo RUTA_QUE_SE_IMPRIMIO_DE_LA_VOZ

**Observación clave:** un OCR de una fotografía periodística puede devolver una cadena vacía porque no hay letras visibles, aunque la imagen aporte significado. Una transcripción de MINDS-14 puede mencionar atención bancaria; **no corresponde a la noticia**.

**Para la colección documentada completa:**

    python lab.py fuentes-repo --imagenes 32 --audios 10

Este comando verifica y prepara las fuentes; **no ejecuta automáticamente 42 OCR/ASR**. La normalización de los 42 activos, el catálogo JSONL/Parquet, manifiesto, benchmarks y ZIP se mantienen en el **cuaderno original S11**. Si quieres comparar Whisper contra la **transcripción humana** de diez voces, el repositorio ya contiene la función ejecutar_asr y la evaluación WER del motor TC2.

**Licencia:** MINDS-14 es CC BY 4.0 con atribución a PolyAI. Las fotografías tienen derechos editoriales: conservar referencia y crédito no autoriza redistribuirlas. No subas medios editoriales al repositorio público.

## Paso 5B. Extraer información estructurada con el módulo original S11

Después de obtener un OCR y una transcripción (de la simulación o de los archivos autorizados), ejecuta:

    python lab.py extraer
    cat salidas/extraccion.json

El programa reutiliza [s11_audio_noticia.py](../../utils/s11_audio_noticia.py) para detectar **posibles entidades, cantidades y temas** dentro del texto ASR, conservar fragmentos de evidencia y auditar que los fragmentos correspondan al texto de origen. Del OCR extrae **cifras y fechas candidatas** usando expresiones regulares. Para la voz, cuando hay información temporal, la ficha retiene el intervalo de audio.

**No son hechos certificados:** una regla puede encontrar un número equivocado si el OCR o Whisper falló. La palabra «candidato» es parte del resultado, no una excusa para omitir la verificación manual. Este paso conecta la extracción de información con el catálogo ETL que ya existe.

## Paso 6. Instalar y usar EmbeddingGemma 2

**No es Gemma 2 generativo.** EmbeddingGemma 2 es un modelo de **representaciones vectoriales**. La familia tiene codificadores modulares: **270m** de solo texto, **440m** texto/imagen, **570m** texto/audio y **740m** multimodal completo a nivel de arquitectura. Para la práctica en Codespaces empezamos con **embeddinggemma-2:270m** bajo Ollama.

Los vectores nativos tienen **768 dimensiones**. El número 270m designa parámetros, no dimensiones.

### 6A. Iniciar Ollama (sin otra API de pago)

    bash iniciar_ollama.sh
    ollama list

Si Ollama no inicia, abre el log:

    cat /tmp/s11-ollama.log

Prueba la API que usa el programa:

    curl -fsS http://127.0.0.1:11434/api/embed -H 'Content-Type: application/json' -d '{"model":"embeddinggemma-2:270m","input":"La entidad mencionó doce contratos"}' | python -c 'import json,sys; v=json.load(sys.stdin)["embeddings"][0]; print("Dimensiones:",len(v),"Muestra:",v[:5])'

**Salida esperada:** Dimensiones: 768. La primera descarga y la velocidad en CPU dependerán del Codespace.

### 6B. Comprender las instrucciones para cada vector

EmbeddingGemma 2 recomienda distintos formatos para **documento** y **consulta**:

    Documento: title: Evidencia de imagen | text: CONTRATOS: 12
    Consulta:  task: search result | query: ¿cuántos contratos registra el afiche?

El documento es lo que queremos recuperar y la consulta es nuestra pregunta; esto es una tarea **asimétrica**. Una similitud de coseno alta solo representa proximidad de vectores; **no es un porcentaje de certeza factual**.

### 6C. Construir índice y preguntar

    python lab.py indexar
    python lab.py buscar --consulta "¿Cuál era el valor informado?"
    python lab.py buscar --consulta "¿Qué dijo la voz sobre contratos?"

El índice JSON contiene **cada línea OCR y cada segmento ASR**, junto con **texto + fuente + hash + modelo + vector**. Los segmentos conservan su marca temporal para volver al audio. Las búsquedas calculan similitud coseno y muestran resultados ordenados y fragmentos para verificar.

**Cómo se lee:** compara el primer y segundo resultado para cada pregunta.  
**Qué nos dice:** prioriza documentos semánticamente cercanos.  
**Qué NO permite concluir:** que la fuente sea confiable; una similitud alta no valida una cifra.  
**Error común:** indexar con un modelo y consultar con otro o interpretar el coseno como probabilidad.

### 6D. Extensión opcional: imagen sin OCR previo

EmbeddingGemma 2 puede trabajar con imágenes, siempre que usemos un codificador visual. Para probarlo:

    ollama pull embeddinggemma-2:440m
    python lab.py imagen --consulta "Afiche con cifras de contratos y presupuesto"

Este comando envía los bytes PNG como imagen y la pregunta como texto al mismo espacio vectorial. El embedding visual puede captar temas generales sin extraer exactamente cada dígito. Para cifras y nombres vuelve al OCR y al original.

La capacidad de **embedding de audio directo** existe en la arquitectura de Google, pero **no se presupone que esté habilitada en todas las distribuciones de Ollama**. No depende de ella ninguna actividad obligatoria de esta clase.

## Paso 7. Interpretación, reto y cierre

El estudiante debe producir evidencia obtenida en su ejecución, no responder con prosa libre:

1. Cambia una cifra del código que genera el afiche, vuelve a ejecutar preparar y compara su hash.
2. Ejecuta OCR de nuevo y selecciona un estado estructurado: **coincide / se confundió un carácter / salió vacío**.
3. Ejecuta Whisper sobre una voz real permitida e inspecciona un segmento con sus segundos.
4. Realiza dos búsquedas diferentes y observa si cambia el primer resultado.
5. Comprueba que **fuente y hash** viajan con el texto hasta el ranking, y que no se afirma correspondencia de fuentes distintas.

**Producto de la recuperación:** origen.json, ocr.json, asr.json, extraccion.json, indice.json y las trazas de búsqueda. **Producto de la S11 original:** catálogo de 42 transformaciones en JSONL/Parquet, manifiesto verificable, relectura, pruebas de corrupción y ZIP.

## Problemas típicos

| Mensaje o síntoma | Comprobación | Solución |
|---|---|---|
| No existe pytesseract | Instalación Python incompleta | Repite instalación desde requirements.txt |
| Tesseract no lista spa | Perfil de contenedor incorrecto | Usar perfil S11 y reconstruir |
| Whisper tarda | Archivo largo, solo CPU | Probar copia de 20 s |
| OCR vacío | La imagen no contiene letras legibles | Abrir la imagen y comparar |
| Hugging Face no responde | Red o fuente temporalmente indisponible | Continuar simulación; reintentar más tarde sin saltar hashes |
| Connection refused en Ollama | Servicio no iniciado | Ejecutar iniciar_ollama.sh |
| Model not found | No se descargó el modelo | Ejecutar ollama pull embeddinggemma-2:270m |
| El coseno cambia | Se cambió modelo, texto o fuente | Reconstruir indice.json y comparar bajo el mismo modelo |

## Fuentes oficiales

- [Google: EmbeddingGemma 2 y sus codificadores](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2?hl=es-419)
- [Ollama: modelos EmbeddingGemma 2](https://ollama.com/library/embeddinggemma-2)
- [API de embeddings de Ollama](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [GitHub: varios perfiles de dev container](https://docs.github.com/es/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)

**Recordatorio de seguridad:** sin claves privadas ni datos personales, sin redistribución editorial; los resultados OCR, ASR y embeddings son hipótesis técnicas y exigen verificación de las fuentes.
