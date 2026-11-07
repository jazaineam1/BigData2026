# Taller de Control 2 · Compras Claras: evidencia que se lee, se escucha y se consulta

**Universidad Central · Maestría en Analítica de Datos · 2026-2S**  
**Edición V5 · 6 de noviembre de 2026 · Rama de desarrollo OCR/ASR**

## Estado y referencia académica

El TC2 del PDA de referencia 2026-2 evalúa **implementación de procesos ETL** y corresponde al **20 %** de la asignatura. El PDF conocido pertenece al grupo 1, por lo que cualquier ajuste administrativo específico del grupo 2 requiere comprobación docente. Para este grupo el profesor estableció un corte de contenidos **hasta la sesión 10**; se integran BM25/S07, búsqueda semántica/E5/Atlas/S09 e imagen y audio/S10. La sesión 10 ofrece fundamentos de ASR y WER y una extensión opcional de Whisper; **este TC2 convierte OCR y ASR en laboratorios guiados y puntuables**, tal como solicitó el docente. No exige video, Spark, Dask ni contenidos posteriores.

**Fecha límite fijada:** sábado **14 de noviembre de 2026, 23:59:59, hora de Bogotá UTC−5**. Entrega mediante repositorio **preexistente y privado** del equipo, rama y PR propio, más correo institucional; no crear un nuevo repo.

**Estado de publicación:** esta versión V5 requiere ejecución de GitHub Actions y revisión antes de fusionar a main. No afirmar que está disponible en Pages hasta observar un despliegue exitoso del commit fusionado.

## Historia de Laura · cuatro actos y un producto

**Acto I · Encontrar.** Laura dispone de 200 expedientes SECOP preparados (TC1 ya evaluó su adquisición). Recupera por palabras con BM25 y por significado con E5, compara literal/paráfrasis y ranking RRF, contrasta Precision@5/Recall@5 contra cinco intenciones con juicios externos.

**Acto II · Leer.** Un gráfico PNG generado desde el Top-5 RRF propio contiene los identificadores visibles de cinco expedientes. El estudiante inspecciona RGB, luminancia, histograma y dos transformaciones (160/640 px); luego **Tesseract OCR español** extrae de verdad texto de los tres PNG. Implementa su función de regex para identificar códigos CO1.REQ.*, coteja contra IDs de origen y reporta cobertura y pérdidas de legibilidad. No se permite copiar el ranking como resultado de OCR.

**Acto III · Escuchar.** Diez grabaciones MINDS14 es-ES CC BY 4.0, registradas con source_record_id, licencia y SHA. Decodifica, calcula RMS/FFT, forma de onda y espectrograma; ejecuta **Whisper tiny mediante faster-whisper en CPU INT8** sobre las diez voces. Conserva para cada audio una hipótesis real, segmentos temporales, la referencia humana distinta del dataset, **WER** por palabras y temas/cifras por reglas transparentes. Implementa su función de extracción manual; no se atribuyen los audios a SECOP ni a noticias de El Tiempo.

**Acto IV · Verificar.** Con **13 activos** (3 imágenes + 10 WAV) el estudiante construye un catálogo enriquecido con asset_id, source_kind, source_record_id, original, derivado, licencia, sha256, extracted_text, text_origin, reference_text, wer y extracted_info_json. Escribe JSONL y Parquet, reabre ambos, consulta por tipo y por término extraído, verifica idempotencia, corrompe/restaura una **copia** del PNG y genera un explorador offline con rankings, OCR, ASR, WER y límites explícitos.

## Rúbrica definitiva propuesta (24 controles · 100 puntos)

| Control | Evidencia evaluada | Puntos |
|---|---|---:|
| E1.1 | Tokens, frecuencia documental, DF/IDF | 3 |
| E1.2 | Dos rankings BM25 | 4 |
| E1.3 | Cambio de palabra y predicción | 3 |
| E2.1 | Embeddings E5 reales, prefijos, 384 dimensiones | 4 |
| E2.2 | Coseno manual y Top-10 E5 | 5 |
| E2.3 | Atlas remoto verificado o crédito parcial local declarado | 4 |
| E2.4 | Top-k y filtro por entidad | 2 |
| E3.1 | Precision@5 y Recall@5 reales, más función manual | 4 |
| E3.2 | RRF por rangos, función manual | 4 |
| E3.3 | Motor elegido, alternativa y límite | 2 |
| E4.1 | RGB, luminancia e histograma | 5 |
| E4.2 | Dos perfiles reales de imagen | 5 |
| E4.3 | Legibilidad y pérdida por reducción | 4 |
| E4.4 | Tesseract español en tres imágenes, función de códigos y evidencia | 6 |
| E5.1 | Diez WAV humanos, fuente y licencia | 5 |
| E5.2 | RMS manual, FFT y espectrograma | 5 |
| E5.3 | Diferencia de acústica y lenguaje | 2 |
| E5.4 | Whisper tiny real sobre diez audios, segmentos | 6 |
| E5.5 | WER y temas/cifras, función propia | 2 |
| E6.1 | Catálogo de 13 activos enriquecidos | 6 |
| E6.2 | Exportación/relectura y consultas por tipo/texto | 6 |
| E6.3 | Idempotencia, 13 registros y SHA estable | 4 |
| E6.4 | Corrupción y restauración verificable | 4 |
| E6.5 | Explorador offline y defensa de decisiones | 5 |
| **Total** | **35 búsqueda + 65 ETL multimedia/integración** | **100** |

Los controles E4.4 y E5.4 exigen **inferencia ejecutada verdaderamente**. La reproducción de una referencia humana no cuenta como ejecución de ASR. Un WER alto, OCR sin todos los códigos o un reconocimiento imperfecto **no deben esconderse**: se califica el proceso, las evidencias y sus interpretaciones. El corrector recalcúla la documentación y puede requerir revisión manual del docente; la prueba E2E instala Tesseract y Whisper para verificar la ruta real.

## Ruta visible, ocho funciones COMPLETA y herramientas

- **Notebook:** \`Cuadernos/Taller_Control_2.ipynb\`, dos recursos del estudiante junto a la guía.
- **Guía:** \`assets/tutoriales/tc2-paso-a-paso.html\`, 41 verificaciones, teclado y móvil.
- **Motor:** \`utils/tc2_core.py\`, mismo código embebido en el notebook.
- **Corrector de ZIP:** \`utils/calificar_tc2_zip.py\` y manifest de controles.
- **Datos:** \`Datos/tc2_corpus_2026.json\`, \`Datos/tc2_juicios_2026.json\`, MINDS14 es-ES con SHA fijado.
- **Ocho funciones del estudiante:** frecuencia_documental_equipo, coseno_mini, precision_cinco, rrf_dos_posiciones, luminancia_rgb, rms_manual, **ids_desde_texto**, **palabras_clave_propias**.
- **Modelos sin servicio de pago:** \`pytesseract\` + \`tesseract-ocr-spa\`, \`faster-whisper\` + Whisper \`tiny\` CPU/INT8. La instalación y descarga de pesos necesitan red y tiempo.
- **Salida:** \`E4/ocr.json\`, \`E4/ocr_manual.json\`, \`E5/asr.json\`, \`E5/asr_manual.json\`, \`E6/catalogo.jsonl\`, \`E6/catalogo.parquet\`, \`E6/consultas.json\`, \`explorador.html\`, \`manifest_tc2.json\`.

## Entrega GitHub (mismo repositorio creado en el curso)

1. Trabajar en el **repositorio ya creado por cada pareja**, convertirlo a **privado** si estaba público, porque el cuaderno/ZIP contienen códigos y nombres; mantener acceso de lectura del docente.
2. Crear rama \`taller/tc2-etl\` y carpeta \`talleres/TC2/\`; subir \`TC2_<PAREJA>.ipynb\` ejecutado, \`TC2_<PAREJA>.zip\`, \`manifest_tc2.json\` a esa carpeta. No subir contraseñas, tokens, claimUrl o URI Atlas.
3. Abrir PR en el propio repo del equipo (no en el docente). Notificar por correo institucional a los mismos destinatarios de TC1 con enlace al repo y al commit, integrantes y SHA del manifiesto.
4. Commit y correo deben estar enviados antes de las **23:59:59 del sábado 14-11-2026**, hora Bogotá. Drive es respaldo de trabajo, no destino final.

## Control técnico antes de publicar

- [ ] Contrato académico, estructura de 24 controles y motor embebido exacto.
- [ ] Pruebas unitarias/QA offline: BM25, coseno, WER, extracción y catálogo JSONL/Parquet. Los resultados simulados usados en QA offline **no** equivalen a modelos ejecutados.
- [ ] E2E real Colab-equivalente en CPU: E5, OCR Tesseract español sobre 3 PNG y Whisper tiny sobre 10 WAV, ZIP y recalificación externa equivalente (98/100 si la ruta Atlas se declara local).
- [ ] Licencias/hashes de voces reales, Playwright móvil/desktop, accesibilidad y escáner de seguridad.
- [ ] Compatibilidad con LMS V5: módulo universal; no introducir \`lms/session-12.html\`.
- [ ] Fusionar PR y verificar workflow de GitHub Pages + enlaces Colab/guía.

## Advertencias de interpretación

**Fuente ≠ predicción ≠ referencia ≠ verdad comprobada.** Un PNG producido desde el ranking no representa una foto de un contrato. Tesseract lee símbolos estimados; el cotejo contra el ranking no es un sello de veracidad legal. Whisper procesa grabaciones auténticas pero puede alucinar palabras; WER compara frente a una sola referencia humana del mismo registro, no mide generalización. Las reglas de temas y cifras pueden fallar si la transcripción falla. No se extraen ni descargan automáticamente audios editoriales de El Tiempo, y **no se inventa relación entre MINDS14 y SECOP**.

El proceso ETL se evalúa como sistema integrado de **extraer → transformar/enriquecer → cargar → reabrir/consultar → verificar**, no como mera ejecución de herramientas aisladas.
