# Imágenes reales para la ETL del curso

El cuaderno obtiene automáticamente estos archivos desde el repositorio del curso. No se descarga ni se carga un ZIP. El grupo no vuelve a solicitar las imágenes al periódico.

## Procedencia y selección
- Fuente editorial: imágenes enlazadas por `Datos/noticias_contratacion_2026.json` y `Datos/entidades_en_noticias_2026.json`.
- Adquisición: `utils/s10_pipeline.py`, función `acquire_inputs`, ejecutada una vez por el docente. Identificación HTTP `BigData-UCentral-docente/1.0`; pausa mínima de 0,4 s entre peticiones. Los instantes UTC reales están en cada registro de `inputs.json`.
- Selección reproducible, variante 0: deduplicar URLs; priorizar noticias de contexto de Fuerza Aeroespacial Colombiana; ordenar después por SHA-256 de variante+URL; tomar los primeros 32 archivos decodificables, entre hasta 48 candidatos. No es una muestra aleatoria ni representativa del corpus.
- El lote es mixto. El cruce por `article_id` señala las noticias de contexto de una entidad; una mención no prueba vínculo fotografía–contrato.
- Publicación y verificación: `utils/prepare_s10_real_inputs.py`. Conserva los bytes adquiridos, sin crear imágenes artificiales ni reescribir sus créditos. El informe de adquisición registra solicitudes y fallos.

## Diccionario
| Campo | Uso |
|---|---|
| `article_id`, `occurrence_id` | Noticia y aparición dentro de ella |
| `source_url`, `final_url` | URL solicitada y URL final de adquisición |
| `credit` | Crédito consignado en el corpus; no implica autoría del curso |
| `acquired_at_utc`, `http_content_type` | Instante real de captura y tipo HTTP recibido |
| `input_path`, `input_sha256`, `expected_format` | Archivo local, integridad y formato detectado por Pillow |
| `snapshot`, `job_id`, `origin_kind` | Versión del corpus, trabajo y procedencia real |

Las fotografías conservan sus derechos y créditos de origen; no se presentan como material producido por el curso. Este snapshot contextual se utiliza para aprender extracción, transformación y carga. No permite generalizar tamaños o calidades al universo de noticias.
