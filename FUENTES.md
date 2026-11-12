# Fuentes de S11 · inventario vigente y procedencia

**Fuente de verdad del laboratorio:** `configuracion_s11.json` selecciona los ejemplos,
`fuentes.py` construye el inventario y `01_laboratorio.ipynb` procesa el corpus.
No interpretes los PNG de primera página como documentos adicionales.

| Modalidad | Origen y ubicación | Cantidad | Precaución |
| --- | --- | ---: | --- |
| Fotografías El Tiempo | `datos/raw/fotos/` | 30 | Crédito y permisos individuales aún no contrastados |
| Fotografías con ficha | `datos/raw/fotos_catalogadas/` | 32 | Revisar ficha, URL y licencia individual |
| Actas SECOP | `datos/raw/actas_pdf/` | 30 PDF | No divulgar datos personales en OCR o capturas |
| Vistas de actas | `datos/raw/actas/` | 30 PNG | Son derivados de los PDF anteriores, NO fuentes adicionales |
| Voces humanas MINDS-14 | Fuente PolyAI; descarga verificada bajo `datos/raw/audios/` | 30 WAV de fuente | No proceden de noticias ni de los contratos SECOP |

**Total del catálogo:** 62 fotografías + 30 actas PDF + 30 audios = **122 fuentes**.
Las 30 imágenes de primera página y las conversiones PCM16 son vistas/derivados, no
nuevos documentos. Antes de preparar las voces pueden figurar 92 fuentes locales;
el inventario llega a 122 tras ejecutar `preparar_audios()`.

## Muestra reproducible de la videoclase

`configuracion_s11.json` ordena explícitamente las ocho fotografías de prueba:
`eltiempo_006.webp` (letreros y OCR), `eltiempo_009.webp` (viviendas,
consulta semántica), `eltiempo_023.webp` (logotipo Lotería del Valle y recorte),
`eltiempo_001.jpg` (contraste sin texto abundante), y `002`, `003`, `004`, `005`
como ampliación. **No** usar las primeras ocho posiciones alfabéticas.
Los lotes de 4 u 8 y el visor utilizan la misma precedencia; para 62 fuentes
se añaden todas las restantes sin repetición.

**Caso contractual:** `secop_acta_728704921.pdf`, acta de inicio del contrato
006-2026. La pregunta coherente en cuaderno, presentación y visor es:
«¿Cuál es el VALOR DEL CONTRATO, la DURACIÓN y la FORMA DE PAGO?».
La referencia visible señala $14.760.000, 6 meses y 6 cuotas de $2.460.000,
pero el estudiante **debe contrastar cada cifra con el PDF original**;
el reconocimiento OCR no la certifica. Se deben ocultar datos personales en capturas.

## Atribución y licencias

- **El Tiempo:** archivo de fotografías histórico del repositorio. Los 30 archivos
  de la primera colección no tienen licencia o crédito por archivo verificados;
  la publicación pública **no** equivale a permiso de reutilización sin restricciones.
- **Fotografías con ficha:** revisar `datos/manifiestos/fotos_catalogadas_32.json`.
  La presencia de una URL o un crédito no prueba por sí sola una licencia.
- **SECOP:** documentos de contratación; examinar fuente oficial, contexto y
  protección de datos personales antes de compartir OCR o capturas.
- **Voces:** PolyAI MINDS-14 es-ES, licencia declarada CC BY 4.0.
  Parquet fuente: https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet
  SHA-256 esperado: `989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf`.
  El script conserva WAV original, derivado y huellas; no almacenar WAV en Git.

## Límites de inferencia y trazabilidad

Una similitud coseno ordena candidatos, **no** prueba hechos, licencias ni relaciones
históricas. Las tres modalidades no corresponden al mismo evento por defecto.
Para afirmar una relación se necesitan IDs o metadatos verificables independientes.
Conserva ruta, bytes originales, SHA-256, modelo, parámetros, origen y recorte/página.
Si cambias modelo, normalización o corpus, **recalcula** los vectores correspondientes.
