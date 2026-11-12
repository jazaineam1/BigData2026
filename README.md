# S11 · Laboratorio de investigación multimedia (estudiantes)

**Universidad Central · Big Data**. Este Codespace es un kit de clase **reducido**: aquí no están Airflow, otros cursos, exámenes, respuestas docentes ni los motores extensos que hacen el trabajo por ti.

**Objetivo:** aprender a escribir Python, no ejecutar un programa ya construido. Vas a investigar **actas SECOP, cuatro fotografías reales de El Tiempo y una voz humana con licencia**. OCR extrae letras; EmbeddingGemma 2 permite recuperar fotos por significado; Whisper transcribe voz. Ninguno certifica la verdad de una afirmación.

## 1. Abrir el Codespace correcto

1. Abre [rama s11-estudiantes](https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes).
2. Comprueba que la rama seleccionada dice **s11-estudiantes**, nunca main.
3. Pulsa **Code → Codespaces → Create codespace on s11-estudiantes**. Este kit tiene un solo contenedor.
4. El explorador debe mostrar `01_laboratorio.ipynb`, `datos/raw`, `INSTALACION_UBUNTU.md`, `requirements.txt`, y poco más.
5. Haz clic en `01_laboratorio.ipynb`. Selecciona el kernel **Python 3**. Lee cada sección, escribe o modifica las líneas y ejecuta **una celda a la vez**.

**No necesitas Ubuntu local.** Codespaces es Linux en el navegador. Para comprender cómo se prepara el entorno, abre el [tutorial de instalación](./INSTALACION_UBUNTU.md): también se puede realizar en un Ubuntu propio cuando sea apropiado.

## 2. Los archivos disponibles son reales

| Carpeta | Archivos | Pregunta |
|---|---|---|
| `datos/raw/actas` | Dos primeras páginas de actas SECOP | ¿Cuál es el total, descuento y neto a pagar? |
| `datos/raw/fotos` | Cuatro imágenes de El Tiempo | ¿Qué letreros reconoce OCR? ¿Qué imagen contiene viviendas? |
| `datos/raw/` al ejecutar | WAV de voz humana PolyAI MINDS-14 es-ES, CC BY 4.0 | ¿Qué dice y qué errores tiene la transcripción? |

La grabación es bancaria y **no pertenece a las noticias**. Los documentos SECOP pueden mostrar datos personales: al compartir capturas o exportar resultados, minimízalos. Las imágenes periodísticas conservan los derechos de sus titulares; los créditos por archivo del subconjunto de 30 todavía requieren curaduría (no inventes licencias).

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

**Advertencia:** la rama s11-estudiantes contiene solo estos archivos, pero eso NO hace privados los demás archivos del repositorio público. El aislamiento real de material reservado requiere un repositorio privado independiente.

Más sobre licencias y fuentes: [FUENTES.md](./FUENTES.md).
