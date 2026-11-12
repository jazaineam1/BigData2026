# Manual de transferencia · adapta el laboratorio S11 a un proyecto propio

**Universidad Central · Big Data · recuperación de sesión 11**  
**Ruta de aprendizaje:** entender → ejecutar → intervenir → comprobar → reutilizar.  
**Programa editable:** [proyecto.py](./proyecto.py) · [laboratorio introductorio](./lab.py) · [manual de recuperación S11](./README.md).

> **Qué lograrás:** recibir una carpeta con archivos autorizados de otro tema, extraer texto de documentos e imágenes con Tesseract, transcribir audios con Whisper, indexar esos textos usando EmbeddingGemma 2 en Ollama, buscar evidencias y comprobar si se alteraron los originales. **No necesitas copiar los nombres de archivos, las rutas ni los datos de Compras Claras.**

Esta guía no supone que OCR y ASR hayan sido dictados en la clase anterior. Su práctica no cambia el Taller 2, ni autoriza extraer o compartir material de terceros sin permiso.

## 1. Entiende la estructura antes de ejecutar

No escribimos un programa que «solo funciona con una noticia». Separaremos **fuentes**, **reglas** y **resultados**.

| Elemento | Qué contiene | Puedes modificarlo |
|---|---|---|
| entradas/ | Imágenes PNG/JPG/TIFF, PDF, audios WAV/MP3, TXT o Markdown tuyos/licenciados | **Sí: cambia archivos** |
| config.json | Idioma, modelo, páginas PDF, límites, nombre de fuente y licencia | **Sí: cambia valores** |
| proyecto.py | Reglas que leen formatos, ejecutan modelos, trocean documentos, indexan y auditan | **Sí: adapta funciones** |
| salidas/catalogo.jsonl | Un registro JSON por cada archivo exitoso, con texto y SHA-256 | **Resultado: no editar manualmente** |
| salidas/catalogo.parquet | La misma información tabular, sin la lista de segmentos de audio | **Resultado: no editar manualmente** |
| salidas/indice.json | Fragmentos + vectores; cada resultado conserva su fuente | **Resultado: regenerar si cambias modelo/datos** |
| salidas/manifest.json | Huellas del catálogo y los originales | **Resultado: auditar** |
| salidas/errores.json | Archivos que no fue posible procesar y por qué | **Diagnóstico** |

**Mini-ejemplo de transferencia:** el caso inicial pregunta por «contratos». En otro proyecto puedes subir una factura escaneada, un audio de una reunión de prueba y un TXT de instrucciones. **El mismo programa** puede buscar «valor», «fecha» y «acuerdo» en los textos de estas tres fuentes. La salida no inventa que los tres archivos se relacionen: eso debe constar en los metadatos del proyecto.

## 2. Crear un proyecto nuevo desde el Codespace

Primero entra en el perfil **S11 · OCR, voz y EmbeddingGemma 2** de Codespaces (no el perfil Airflow). Abre una terminal y ejecuta desde la raíz del laboratorio:

    cd Laboratorios/S11_Codespaces
    python proyecto.py iniciar --destino proyectos/facturas_demo

**Salida esperada:** crea config.json, las carpetas entradas/{imagenes,audios,documentos,textos} y salidas. No sobrescribe un proyecto anterior. Abre config.json en el editor de VS Code y localiza las secciones ocr, asr y embeddings.

Para hacer la primera prueba sin aportar un PDF, coloca este TXT:

    printf "FACTURA SIMULADA 18\nVALOR: 320000 COP\nESTADO: pendiente de revisión\n" > proyectos/facturas_demo/entradas/textos/ejemplo.txt
    python proyecto.py plan --config proyectos/facturas_demo/config.json

**Salida esperada:** una línea de tipo texto, su ruta y su tamaño, sin que arranque Whisper ni Ollama.

**Cómo se lee:** el plan enumera archivos aceptados y su tamaño.  
**Qué nos dice:** qué va a entrar al proceso.  
**Qué NO permite concluir:** si OCR o ASR pueden reconocer el contenido.  
**Error común:** comenzar descargando modelos sin comprobar qué fuentes se leerán.

## 2B. Un proyecto puede tener fuentes distintas

El archivo `config.json` define un origen y una licencia **predeterminados**, pero un proyecto real puede mezclar archivos con créditos diferentes. Para esos casos, al ejecutar `iniciar` se crea una plantilla `metadatos.example.json`.

Copia la plantilla a `metadatos.json`, cambia las rutas y documenta cada fuente. Por ejemplo:

~~~json
{
  "entradas/imagenes/afiche.png": {
    "nombre": "equipo_de_comunicaciones",
    "credito": "Autora del afiche",
    "licencia": "uso_autorizado_para_curso"
  },
  "entradas/audios/reunion.wav": {
    "nombre": "simulacion_grabada",
    "credito": "participantes_con_consentimiento",
    "licencia": "solo_uso_local"
  }
}
~~~

Estas etiquetas son **ejemplos ficticios**: no demuestran por sí mismas autorización ni permiten redistribución. Cada registro del catálogo conservará sus campos **source_name, credit y license**. Un archivo sin entrada específica usa los valores de `config.json`; **no** infieras que dos archivos se relacionan porque se guardaron en la misma carpeta.

## 3. ¿Qué código se ejecuta y qué significa?

### Función 1: recepción de datos

**Código de proyecto.py:**

~~~python
def inventario(raiz, cfg):
    entradas = raiz / "entradas"
    # Busca archivos reconocidos y evita enlaces simbólicos.
    ...
    return files
~~~

- **raiz**: carpeta del proyecto.
- **cfg**: diccionario cargado desde config.json.
- **rglob**: recorre carpetas y subcarpetas.
- **Path**: representa rutas sin concatenar manualmente barras.
- **return**: lista de archivos que se procesarán.
- **Límite:** no procesa archivos mayores de 80 MB ni más archivos que el máximo configurado.

**Intervención 1:** cambia **solo** el nombre de la carpeta del proyecto en el comando iniciar; comprueba con plan que no depende del nombre «Compras Claras».

### Función 2: OCR

**Código usado:**

~~~python
def _ocr_imagen(p, cfg):
    import pytesseract
    from PIL import Image, ImageOps
    with Image.open(p) as im:
        img = ImageOps.exif_transpose(im).convert("RGB")
        return pytesseract.image_to_string(
            img,
            lang=cfg["ocr"]["idioma"],
            config=f'--psm {int(cfg["ocr"]["psm"])}'
        ).strip()
~~~

La imagen **no se sobrescribe**. Pillow abre los píxeles y ajusta orientación. Tesseract devuelve **texto probable**. El modo psm=6 presupone un bloque uniforme; un documento disperso puede mejorar con psm=3 o 11. El idioma «spa» corresponde al paquete Tesseract en español.

**Intervención 2:** abre config.json, sustituye psm=6 por psm=11, repite el OCR en una copia de imagen autorizada y compara los dos textos. **No cambies los dos parámetros al mismo tiempo**: si varían dos cosas no sabrás cuál causó la diferencia.

### Función 3: transcripción

**Código usado:**

~~~python
def _asr(p, cfg, modelo):
    segmentos, info = modelo.transcribe(
        str(p),
        language=cfg["asr"]["idioma"],
        beam_size=int(cfg["asr"]["beam_size"]),
        vad_filter=False,
        condition_on_previous_text=False
    )
    # Convierte los segmentos a segundos y texto.
    ...
~~~

Whisper convierte señal en fragmentos de voz con inicio y fin en segundos. **No** se usa una transcripción conocida como predicción. En config.json puedes cambiar el modelo de «tiny» a «base» o «small», dentro de los límites previstos. En CPU normalmente el costo de cómputo sube con el tamaño.

**Intervención 3:** usa dos configuraciones distintas sobre **el mismo audio autorizado**. Guarda sus salidas por separado, compara un segmento y observa si hay nombres o cifras diferentes. **Sin texto de referencia humana no hay WER real.**

### Función 4: documentos PDF

La función _ocr_pdf transforma temporalmente las primeras páginas PDF en PNG con **pdftoppm** y después reutiliza _ocr_imagen. Cambia limites.paginas_pdf en config.json para trabajar 1, 3 o más páginas hasta el máximo permitido.

**Error frecuente:** pensar que todo PDF es una imagen. Si el PDF ya tiene una capa de texto seleccionable, una extensión para otro proyecto puede **extraer primero texto digital** y reservar OCR para páginas escaneadas. Esta versión del laboratorio aplica OCR a las páginas rasterizadas.

### Función 5: embeddings

**Código usado:**

~~~python
def _embed(entradas, cfg):
    import requests
    r = requests.post(
        cfg["embeddings"]["ollama_url"],
        json={"model": cfg["embeddings"]["modelo"], "input": entradas},
        timeout=300
    )
    r.raise_for_status()
    return r.json()["embeddings"]
~~~

- **requests.post**: envía datos al servicio **local** Ollama.
- **modelo**: identifica el encoder, por ejemplo embeddinggemma-2:270m.
- **input**: fragmentos de texto, preparados como documentos o consultas.
- **embeddings**: vectores para comparar significados.
- **Error frecuente:** tratar un vector como un resumen explicativo; no es texto generado.

El motor solo permite **localhost o 127.0.0.1** como dirección de la API para evitar enviar por accidente documentos propios a otro servicio.

### Función 6: fragmentación e indexación

**Código usado:**

~~~python
fragmentos = [
    frag for fila in filas
    for frag in fragmentar(fila, max_chars)
]
entrada = [
    f"title: {d['titulo']} | text: {d['texto']}"
    for d in fragmentos
]
~~~

**Fragmentar** es dividir el texto en unidades que se puedan recuperar. En audio preserva inicio_s/fin_s. En OCR divide el texto por longitud, conservando siempre archivo y SHA. El fragmentador introductorio divide por caracteres y **puede cortar una palabra en medio**: es un lugar legítimo para mejorar el código en futuros proyectos.

**Intervención 4:** cambia caracteres_por_fragmento de 700 a 250 en config.json, reconstruye el índice y registra cuántos fragmentos se produjeron. La decisión sobre tamaño afecta al número de vectores y a lo que puede recuperar una consulta.

### Función 7: búsqueda e integridad

**Similitud coseno:**

\[
\cos(a,b)=\frac{a\cdot b}{\lVert a\rVert \lVert b\rVert}
\]

Ejemplo manual: a=(1,0), b=(1,0) tienen coseno 1; a=(1,0), c=(0,1) tienen coseno 0. **No significan 100 % o 0 % de verdad**.

**Auditar** recalcula el hash de cada entrada y del catálogo. Si alguien altera un original **después de procesarlo**, se informa la diferencia en lugar de afirmar que es el mismo archivo.

## 4. Ejecuta el proyecto con fuentes propias

Elige archivos que puedas procesar legalmente. Para probar todas las modalidades, coloca una imagen con texto, un PDF escaneado, un audio y el TXT anterior en sus carpetas correspondientes. No son obligatorios los cuatro: la herramienta procesa los que encuentre.

Primero inspecciona:

    python proyecto.py plan --config proyectos/facturas_demo/config.json

Después ejecuta OCR/ASR y crea catálogo:

    python proyecto.py procesar --config proyectos/facturas_demo/config.json

**Salida esperada:** salidas/catalogo.jsonl, candidatos.jsonl, catalogo.parquet, errores.json y manifest.json. Si una fuente está dañada, el programa sigue con las demás, registra el problema y termina con error para indicar que el lote quedó **parcial**.

**Extracción reutilizable:** `extraer_candidatos` detecta fechas, cifras y referencias en el texto, conservando archivo, fuente, SHA-256 y, en los audios, segundos cuando corresponden. Los candidatos son hipótesis, no hechos certificados.

**Interpretación obligatoria:**
- **Cómo se lee:** una línea JSONL por archivo exitoso; el campo extracted_text conserva texto; segments conserva tiempos si es audio.
- **Qué nos dice:** qué archivos fueron procesados y cómo localizarlos.
- **Qué NO permite concluir:** que las cifras extraídas sean ciertas, que los medios pertenezcan al mismo expediente, ni que un OCR vacío signifique «no hay información».
- **Error común:** considerar 10 archivos recibidos igual a 10 transcripciones correctas.

Para ver qué campos genera el catálogo:

    python -c 'import json; from pathlib import Path; p=Path("proyectos/facturas_demo/salidas/catalogo.jsonl"); print(json.loads(p.read_text().splitlines()[0]).keys())'

## 5. Genera un índice semántico y realiza búsquedas

Desde el directorio S11, instala y descarga el modelo **una vez**:

    bash iniciar_ollama.sh

Después:

    python proyecto.py indexar --config proyectos/facturas_demo/config.json
    python proyecto.py buscar --config proyectos/facturas_demo/config.json --consulta "¿Cuál es el valor de la factura?" --topk 3
    python proyecto.py auditar --config proyectos/facturas_demo/config.json

El resultado de buscar muestra **texto, fuente, hash, tipo de archivo y coseno**. Una búsqueda también deja salidas/ultima_busqueda.json.

**Lo que enseña este paso:** antes buscábamos la cadena «320000»; ahora podemos probar una consulta como «¿cuánto dinero se indicó?». El encoder aproxima significados, pero la precisión debe evaluarse contra consultas con relevancia conocida: no basta con ver si el primer resultado parece razonable.

**Distingue estas tres funciones:**
- Tesseract: píxeles → texto.
- Whisper: voz → texto.
- EmbeddingGemma 2: texto → vector. **No genera la respuesta redactada**; recupera candidatos.

**Nota de versiones:** en Ollama, 270m admite texto; 440m admite texto e imagen. No confundas compatibilidad del modelo base con las modalidades que acepta cada variante de Ollama. Para transcribir audio, nuestra ruta obligatoria sigue siendo Whisper.

## 6. Cambia parámetros sin tocar el código

Abre proyectos/facturas_demo/config.json y modifica **un parámetro por experimento**.

| Campo | Valor inicial | Para qué lo cambiarías |
|---|---|---|
| proyecto | facturas_demo | Distinguir el caso de uso |
| fuente.nombre | archivos_aportados_por_usuario | Documentar origen real |
| fuente.credito / fuente.licencia | Pendientes de verificar | Atribuir y definir uso autorizado |
| ocr.idioma | spa | Reconocer textos de otro idioma si Tesseract lo tiene instalado |
| ocr.psm | 6 | Ajustar distribución del texto |
| asr.modelo | tiny | Comparar calidad y velocidad con base/small |
| asr.idioma | es | Ajustar idioma del audio |
| embeddings.modelo | embeddinggemma-2:270m | Probar otro encoder **reindexando desde cero** |
| limites.paginas_pdf | 3 | Analizar más páginas |
| limites.caracteres_por_fragmento | 700 | Cambiar granularidad de búsqueda |
| embeddings.lote | 8 | Balancear memoria y llamadas al encoder |

**Importante:** cambiar el modelo de embeddings obliga a regenerar indice.json. El programa rechaza consultas cuando detecta un índice creado con un modelo distinto o con catálogo cambiado.

## 7. Cambia el código: dos ejemplos de transferencia

### Ejemplo A: otro tipo de documento (CSV)

**Objetivo:** aplicar el mismo sistema a un CSV de inventario propio con una fila por producto. En la primera versión del motor los CSV son ignorados para evitar leerlos incorrectamente como texto plano.

**Intervención guiada en una copia o rama del proyecto:**

1. Busca TEXT_EXT al inicio de proyecto.py.
2. Añade ".csv" al conjunto de extensiones **solo cuando hayas definido su lectura**.
3. En ejecutar, cuando tipo == "texto", detecta .csv con la librería csv de Python y convierte cada fila a texto con nombres de columnas.
4. Añade una prueba con CSV de dos filas, ejecuta plan y procesar, y confirma que el catálogo conserva fuente y SHA.

**Fragmento reutilizable:**

~~~python
import csv

def csv_a_texto(ruta):
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        registros = csv.DictReader(f)
        return "\n".join(
            " | ".join(f"{campo}: {valor}" for campo, valor in fila.items())
            for fila in registros
        )
~~~

**No hagas un reemplazo ciego** de toda la función ejecutar: integra esa rama conservando la lógica que calcula hashes, licencia y errores.

### Ejemplo B: mejorar los fragmentos

En fragmentar, el corte actual se hace cada max_chars caracteres. Puedes sustituirlo por una versión que agrupe oraciones y respete un máximo. Compara en dos ejecuciones el número de fragmentos y el ranking. **No prometas que más fragmentos garantizan mejores resultados**: mide Precision@k sobre consultas con relevancia etiquetada.

## 8. Tres proyectos de aplicación, sin dependencia de El Tiempo

| Proyecto de transferencia | Archivos que aporta el estudiante | Consulta de comprobación |
|---|---|---|
| **Facturas y compras** | Un PDF propio o sintético + TXT de reglas | «¿Qué factura menciona el valor más alto?» |
| **Actas de reunión** | Audio grabado con autorización + acta TXT | «¿En qué intervalo se mencionó la entrega?» |
| **Soporte y servicio** | Capturas de pantalla con texto + grabación de prueba | «¿Qué evidencia menciona un error de acceso?» |

**No** utilices cuentas personales, informes médicos ni conversaciones reales de terceros en el repositorio público. Un Codespace **puede implicar consumo de recursos y retención de archivos**: confirma permisos institucionales antes de subir datos confidenciales.

## 9. Mini-reto con decisiones que dependen de la ejecución

**Punto de partida:** crea un proyecto con nombre diferente a facturas_demo. Elabora o incorpora **dos archivos propios de modalidades distintas**. Ejecuta el pipeline.

Evidencias verificables del reto: ruta del proyecto, número de fuentes aceptadas en plan, número de registros en el catálogo, presencia de segmentos si hay audio, hash de una fuente, número de fragmentos del índice y dos rankings de consultas diferentes.

**Elige exactamente una alternativa por decisión:**

| Decisión | Opciones |
|---|---|
| ¿Qué cambiaste para adaptar el proyecto? | Fuente / OCR / ASR / modelo de embeddings / fragmentador |
| ¿Qué error o límite observaste? | OCR vacío / palabra ASR equivocada / ranking poco pertinente / archivo dañado / ninguno |
| ¿Cómo verificaste un resultado? | Imagen original / escucha del segmento / comparación con texto fuente / comparación de SHA |
| ¿Qué significa el primer ranking? | Relevancia aproximada / verdad certificada / transcripción perfecta |

Los resultados se comprueban **con archivos y salidas propias**, no con preguntas de definiciones ni respuestas de prosa libre.

## 10. Cómo evaluar si aprendieron a transferir

| Criterio formativo | Evidencia observable |
|---|---|
| Reutilizar | Ejecuta la plantilla con una ruta y archivos distintos |
| Comprender | Explica a partir de su ejecución la función de OCR, ASR y embeddings |
| Modificar | Cambia **un parámetro** y compara el antes/después |
| Depurar | Reconoce un error y localiza el archivo en errores.json |
| Trazabilidad | Comprueba hash, fuente, licencia y archivo asociado a un resultado |
| Evaluar límites | Selecciona una limitación concreta respaldada por su ejecución |

No se asigna automáticamente nota ni se altera la rúbrica oficial del Taller 2.

## 11. Calidad, costos y límites que debe conocer quien reutilice

- **CPU:** Whisper y los embeddings pueden ser lentos; el costo de Codespaces varía con los recursos contratados y el tiempo encendido. Detén el Codespace al terminar.
- **Lote:** el procesamiento de varias fuentes funciona, pero no es todavía un servicio distribuido ni un sistema de colas; la concurrencia se enseña separadamente en el cuaderno S11 original.
- **Calidad de OCR:** Tesseract puede confundir números y letras; compara con originales y, si existen, etiquetas humanas.
- **Calidad ASR:** nombres propios, cantidades y ruido aumentan errores. WER requiere texto de referencia.
- **PDF:** esta versión convierte las primeras páginas a imágenes para hacer OCR; no extrae directamente capas de texto.
- **Embeddings:** la similitud no valida contenidos. Cambiar modelo, prefijo o fragmentador exige comparar rankings y, cuando corresponda, reconstruir el índice.
- **Escalado:** indice.json es un ejemplo legible para pocas fuentes. Para muchos documentos, evalúa un almacén vectorial y procesamiento incremental.
- **Derechos:** conservamos archivos aportados localmente; no descargamos masivamente material editorial sin autorización.
- **Pruebas:** las unitarias simulan Whisper y Ollama donde no corresponde descargar modelos, y ejecutan OCR real de imagen/PDF. Una prueba integral sobre Codespaces con modelos descargados requiere comprobación por separado.

## 12. Comprobación guiada antes de entregar

La herramienta incluye el [comprobador probar_todo.sh](./probar_todo.sh), que distingue claramente lo ensayado de lo que requiere descargar modelos.

~~~bash
# Sin descargar Whisper ni Ollama: prueba Tesseract, PDF, TXT, hashes, Parquet e índice simulado.
bash probar_todo.sh --ligero

# Prueba de extremo a extremo en tu Codespace: ejecuta Whisper real y Ollama.
bash probar_todo.sh --completo
~~~

El segundo modo **descarga modelos a tu Codespace y consume recursos de cómputo**. No se ejecuta automáticamente para evitar costos inesperados. El mensaje final confirma los pasos ejecutados: si hay error, revisa la primera etapa que falló antes de continuar. No se simulan resultados de Whisper u Ollama en el modo completo.

## Auditoría adicional sin ejecutar el motor

~~~bash
python verificar_independiente.py --caso lab --modelo
python verificar_independiente.py --proyecto proyectos/facturas_demo
~~~

El verificador lee originales, hashes, catálogo, candidatos e índice, invoca la CLI Tesseract y puede consultar Ollama por HTTP. El reconocimiento correcto de letras y palabras exige contrastar las fuentes visual y auditiva.

## 13. Pruebas y recuperación

Ejecuta:

    python -m unittest -v test_lab test_proyecto

Las pruebas muestran qué debería funcionar sin datos privados: crear un proyecto, plan, procesamiento, OCR, índice con vectores simulados y detección de alteración.

Si el proceso falla:
1. Abre salidas/errores.json y encuentra la ruta que falló.
2. Comprueba formato y permiso del archivo, idiomas instalados y estado del modelo.
3. Vuelve a ejecutar procesar y después **indexar**: nunca uses un índice generado con un catálogo diferente.
4. Ejecuta auditar y confirma las fuentes.

**Cierre:** el curso entrega **dos niveles**. lab.py enseña cada concepto aisladamente con el mismo caso. proyecto.py enseña transferencia: orígenes y parámetros nuevos, procesamiento por lotes, almacenamiento y recuperación. Las dos herramientas comparten el mismo entorno, no son dos clases desconectadas.

**Referencias:** [EmbeddingGemma 2, documentación Google](https://ai.google.dev/gemma/docs/embeddinggemma/model_card_2?hl=es-419) · [Versiones Ollama](https://ollama.com/library/embeddinggemma-2) · [Tesseract](https://tesseract-ocr.github.io/) · [Faster-Whisper](https://github.com/SYSTRAN/faster-whisper) · [GitHub Codespaces](https://docs.github.com/en/codespaces)
