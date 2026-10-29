# S10 · ETL de imágenes reales en VS Code

Universidad Central · Maestría en Analítica de Datos · Big Data.

**¿Cómo prepara Laura las imágenes de las noticias de contratación para un catálogo reutilizable?** Aquí implementas extracción, transformación y carga sobre archivos reales. El mismo contexto documental de S3–S7 y la selección de S09 acompañan la entrada. Una imagen de una noticia no demuestra hechos sobre un contrato particular.

El docente entrega `S10_entradas_reales.zip`: proyecto, corpus, contexto y 32 imágenes reales adquiridas una sola vez. No contiene imágenes sintéticas. Descomprímelo en una carpeta `S10_entradas_reales` y abre **esa carpeta** en VS Code. Conserva el ZIP original junto a ella. Si trabajas desde el repositorio, abre `laboratorios/s10_etl_imagenes` y utiliza la ruta donde recibiste el ZIP.

[Presentación](https://jazaineam1.github.io/BigData2026/Presentaciones/s10-etl-multimedia.html#s1) · [Checklist](https://jazaineam1.github.io/BigData2026/assets/tutoriales/s10-laboratorio-guiado.html) · [Cuaderno de apoyo](https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb).

## Preparar antes del encuentro

Python 3.12 recomendado. En VS Code, `Python: Select Interpreter` selecciona el entorno creado. Ejecuta en la terminal integrada:

```sh
python -m venv .venv
```

Activa el entorno: PowerShell `./.venv/Scripts/Activate.ps1`; Linux/macOS `source .venv/bin/activate`. Si la política del equipo no permite activar scripts, selecciona el intérprete de `.venv` en VS Code y ejecuta con él. Instala las dependencias:

```sh
python -m pip install -r requirements.txt
```

No hace falta Atlas, FFmpeg, tarjetas ni claves. Las tres etapas de S10 son de **imágenes**. Audio/video se trabajan en S11. El lote se distribuye por la vía docente; la práctica no descarga masivamente del periódico. La adquisición reproducible está en `utils/prepare_s10_real_inputs.py` del repositorio y se ejecuta del lado docente.

## Mapa sin relojes

| Etapa | Pregunta | Producto |
|---|---|---|
| E · Extraer | ¿Qué llegó y de qué noticia? | RAW, contexto y hashes |
| T · Transformar | ¿Qué perfil necesitamos? | Thumbnail y parámetros |
| L · Cargar | ¿Qué puede consultar otro proceso? | JSONL, Parquet y manifiesto |
| Verificar | ¿Qué hice y qué falta? | Archivos reabiertos y reporte |

## 1. E · Extraer el snapshot real

Desde la carpeta del proyecto descomprimido, con el ZIP en la carpeta superior:

```sh
python main.py extraer --entrada ../S10_entradas_reales.zip --trabajo work/s10 --cantidad 32
```

Si guardaste el ZIP en otra ruta, cambia solo `--entrada` y usa comillas si tiene espacios. Debes ver `E · extracción`, `imagenes_reales_del_lote` y `origen: eltiempo_real`. Abre un archivo en `work/s10/raw/` y localiza su noticia en `config/jobs.json`.

**Cómo se lee:** 987 noticias y 5.152 referencias describen el catálogo; 32 es el lote binario disponible.

**Qué nos dice:** qué archivos reales y qué contexto procesará tu ejecución.

**Qué NO permite concluir todavía:** no se adquirieron todas las 4.071 URLs distintas; tampoco conocemos su disponibilidad futura.

**Qué error común:** confundir referencias con fotografías únicas o una mención de entidad con evidencia de un contrato.

Si falla el ZIP, recupera la entrada docente. Si falla un hash o un decoder, se informa el fallo: no se genera un sustituto.

## 2. Implementa primero una imagen

Abre **`paso_a_paso.py`**. Identifica las líneas E, T y L: lectura de bytes/contexto, `thumbnail()`/`save()`, y escritura/relectura de la tabla.

```sh
python paso_a_paso.py --trabajo work/s10 --posicion 1 --lado 640
```

Abre el original y `work/s10/ejemplo/fila_1_640.jpg` en VS Code. Repite cambiando **solo** `--lado 640` por `--lado 320`. No cambies de entrada al comparar.

| Función | Para qué / parámetros | Devuelve / lectura | Error frecuente |
|---|---|---|---|
| `Image.open(path)` y `load()` | Leer/decodificar archivo | Imagen y propiedades reales | Confiar en extensión |
| `ImageOps.exif_transpose()` | Respetar orientación si existe | Imagen orientada | Confundir orientación con resolución |
| `thumbnail((lado,lado))` | Acotar dimensiones manteniendo proporción | Modifica imagen en memoria | Sobrescribir RAW al guardar |
| `save(..., "JPEG", quality=88)` | Escribir derivado explícito | Archivo nuevo | Prometer menos bytes en toda conversión |
| `to_parquet()` / `read_parquet()` | Escribir/releer metadata | Archivo / tabla | Existencia del archivo ≠ contenido correcto |

El lote adquirido dio WEBP al decodificar. El derivado será JPEG: observa qué cambió en vez de asumirlo por el nombre.

## 3. T · Aplicar la misma operación por micro-lotes

```sh
python main.py transformar --trabajo work/s10 --perfil catalogo640 --lote 16 --hasta 16
python main.py transformar --trabajo work/s10 --perfil catalogo640 --lote 16
```

La primera ejecución deja 16 DONE y 16 PENDING. La segunda verifica lo terminado y completa lo pendiente. La operación unitaria está en `make_thumbnail()`; el ejecutor registra estados por trabajo y mantiene acotadas las imágenes activas.

Compara una alternativa sobre **el mismo lote**:

```sh
python main.py transformar --trabajo work/s10 --perfil vista320 --lote 16
```

**Cómo se lee:** `processed_now` es trabajo nuevo; `skipped_verified` es trabajo previo revalidado. DONE/FAILED/PENDING describen el estado acumulado.

**Qué nos dice:** qué cambió al elegir perfil y qué falta por terminar.

**Qué NO permite concluir todavía:** los tiempos locales no demuestran rendimiento de un cluster ni calidad visual general.

**Qué error común:** contar lo omitido como trabajo nuevo o igualar tamaño de lote con cantidad de imágenes abiertas a la vez.

Si hay FAILED, lee el mensaje en `state/checkpoint.json` y recupera el original. No marques un trabajo completo por editar el checkpoint. Para otra selección de entrada utiliza otra carpeta `--trabajo`.

## 4. L · Cargar, releer y consultar

```sh
python main.py cargar --trabajo work/s10 --zip paquete_s10.zip
python main.py verificar --trabajo work/s10
```

Debes obtener `ok: true`. La carga rechaza perfiles con pendientes y vuelve a comprobar hashes, decodificación, dimensiones, relaciones y consistencia JSONL/Parquet. Abre `work/s10/outputs/assets.jsonl`, `manifest_s10.json` y `checks/quality_report.json`.

Consulta desde la terminal Python o el cuaderno:

```python
import pandas as pd
catalogo = pd.read_parquet("work/s10/outputs/assets.parquet")
print(catalogo.groupby("profile")[["raw_bytes", "derived_bytes"]].sum())
print(catalogo[["article_id", "profile", "derived_width", "derived_height"]].head())
```

**Cómo se lee:** una fila representa un trabajo/perfil con un derivado y vínculo editorial.

**Qué nos dice:** qué salidas puede consumir otro proceso y cómo volver a la noticia.

**Qué NO permite concluir todavía:** integridad técnica no autentica la fuente ni prueba pertinencia de la imagen para un contrato.

**Qué error común:** declarar carga completa por terminar un comando, sin releer el catálogo.

## 5. Comprobar portabilidad y reejecución

```sh
python main.py verificar --zip paquete_s10.zip --destino restaurado_s10
python main.py transformar --trabajo work/s10 --perfil catalogo640
```

Usa una carpeta destino vacía. La primera orden comprueba el paquete en otra ruta; la segunda debe procesar cero archivos nuevos y omitir 32 tras verificarlos. Si transformas o cambias métricas después de cargar, vuelve a ejecutar `cargar` para que el manifiesto del paquete refleje la nueva ejecución.

## 6. Conservar una decisión propia

Selecciones formativas, sin texto libre. Los códigos 0 dejan la selección pendiente. Perfiles: 1=vista320, 2=catalogo640, 3=detalle1024. Elige solo perfiles que ejecutaste; la posición corresponde a tu tabla de salida.

Límites: 1=faltan juicios de calidad visual; 2=falta medir otra distribución de tamaños; 3=falta medir I/O y concurrencia; 4=el contexto de entidad no demuestra vínculo con un contrato.

```sh
python main.py decidir --trabajo work/s10 --posicion 0 --elegido 0 --descartado 0 --limite 0
python main.py cargar --trabajo work/s10 --zip paquete_s10.zip
```

Reemplaza los ceros por tu selección. No se añade una nota ni se acredita oficialmente el laboratorio con un formulario. Conserva el ZIP y tu código ejecutado por la vía docente.

## Crecimiento y siguiente sesión

```sh
python main.py escenario --trabajo work/s10 --activos 1000000
```

Es una **proyección condicionada** a medias del lote y una medición secuencial, no una ejecución de un millón de activos. Compara bytes comprimidos con píxeles decodificados, y nombra el recurso que falta medir.

S11 amplía el mismo contrato a audio/video reales; S12 integra ETL. Los motores distribuidos se estudian después. La idea para llevar: **E obtiene una entrada identificada; T la adapta sin borrar el original; L deja una salida que otro proceso puede abrir y consultar**.
