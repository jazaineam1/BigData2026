# Taller de Control 2 · Compras Claras 2
## Del buscador al explorador de evidencias
**Universidad Central · Maestría en Analítica de Datos · Big Data 2026-2S**

**Versión de implementación V3 · 6 de noviembre de 2026**

**Estado:** cuaderno, rúbrica, datos, guía y corrector implementados en la rama de revisión `plan/tc2-hasta-s10-20261105`, PR #145. **No se ha publicado todavía en el LMS ni fusionado a main.** La fecha de entrega ya fue definida por el docente: **sábado 14 de noviembre de 2026 a las 23:59:59, hora de Bogotá (UTC−5)**. La ponderación final sobre la nota total de la asignatura requiere confirmación del PDA vigente.

## 1. Diagnóstico y continuidad con TC1
| Propiedad | TC1 (V9) | TC2 ampliado (V3) |
|---|---|---|
| Cuaderno | 81 celdas: 50 explicativas, 31 de código | 91 celdas: 56 explicativas, 35 de código |
| Puntaje | 22 controles / 100 | 18 controles / 100 |
| Tema | Ingesta SECOP, modelado Atlas, Cassandra, Neo4j | BM25, E5/Atlas Vector Search, RRF, imágenes, audio |
| Lo que hace el estudiante | Ejecuta, elige, completa, pega y defiende | Predice, ejecuta, **completa seis funciones**, experimenta, interpreta y defiende |
| Materia prima | APIs SECOP | 200 expedientes SECOP **ya preparados**, 10 audios MINDS14 |
| Corrección | Controles independientes y manifest | Controles independientes; validador externo de ZIP |
| Entrega | Drive restringido y correo | **GitHub privado del estudiante y mismo correo docente** |
| Continuidad | Caso profesional de Laura | Laura necesita buscar por palabras y significado y describir multimedia |

**No repetir en TC2:** descarga SECOP, concurrencia, idempotencia documental, agregaciones convencionales de Atlas, Cassandra/CQL, Neo4j/Cypher, SHA/RAW y Parquet como objetivos puntuables. Se pueden usar SHA y ZIP como infraestructura de evidencia, sin recibir de nuevo puntos académicos.

La longitud extra no es relleno: cada bloque incorpora un ejemplo manual, vocabulario, contraejemplo, intervención del estudiante, salida esperada, diagnóstico y un puente hacia el siguiente bloque. Los seis huecos `COMPLETA` se califican con evidencia recalculada, no por ejecutar todo.

## 2. La experiencia completa de aprendizaje
**Problema:** Laura tiene documentos de contratación y colecciones multimedia, pero su equipo no encuentra información cuando cambia la redacción, no sabe si un ranking es pertinente y confunde propiedades de imagen/audio con el contenido semántico.

**Resultado:** un `explorador.html` offline, generado desde el notebook y sus archivos, con: Top-5 BM25, E5, RRF, IDs SECOP, métricas, gráfica de ranking procesada en dos resoluciones, catálogo de 10 WAV con medidas, decisiones y límites. Las dos procedencias siguen separadas: los audios no son contratos ni noticias.

### Introducción: la pregunta que falla
- Preparar Colab y copia de trabajo; no confundir trabajo en Drive con entrega oficial GitHub.
- Corpus proporcionado y caso asignado determinísticamente por códigos de integrantes.
- Redactar predicción inicial cerrada antes de consultar.
- Explorar tres textos pequeños que separan coincidencia de palabra y pertinencia.

### E1 · Recuperación léxica BM25 (20 puntos)
- Tokenización normalizada (sin tildes, minúsculas); ejemplos con frecuencias y documentos distintos.
- **COMPLETA** `frecuencia_documental_equipo(coleccion,termino)` con un `return` correcto; calcular DF e IDF del corpus de 200 documentos.
- Ejecutar BM25 local sobre consulta literal y paráfrasis, con Top-10 y desempate determinista. Se dice expresamente que es Python local, **no Elasticsearch remoto**.
- Cambiar UNA palabra, predecir y contrastar ranking, IDs que entran y salen; reconocer cambios nulos como resultado posible.
- Evidencias `E1/laboratorio_bm25.json`, `E1/bm25.json`.

### E2 · Representación y búsqueda semántica (25 puntos)
- Resolver ejemplo de coseno en 2D: producto punto, normas y ortogonalidad.
- **COMPLETA** `coseno_mini(a,b)` y demuestra resultados 1 y 0; no lo resuelvas por memorizar un número.
- Ejecutar `intfloat/multilingual-e5-small` real en CPU, con `passage:` y `query:`, matriz `200 × 384`, Top-10 exactos por coseno en NumPy.
- Comparar experimentalmente `query:`, `passage:` y texto sin prefijo; no deducir relevancia a partir de esa comparación geométrica.
- Recorrer pasos Atlas temporal: `ping`, índice `embedding` `numDimensions=384`, índice `queryable` y consulta **$vectorSearch**. Nunca guardar URI ni `claimUrl`. Si el proveedor falla, estado explícito y crédito parcial: la consulta local **no es** Atlas.
- Variar Top-k y aplicar filtro real por entidad; explicar cambio de universo de candidatos.
- Evidencias `E2/laboratorio_coseno.json`, `E2/experimento_prefijos.json`, `E2/embeddings.npy`, `E2/query_*.npy`, `E2/semantica.json`, `E2/experimento_filtro.json`.

### E3 · Métricas y fusión de resultados (15 puntos)
- Resolver manualmente Precision@5=TP/5 y Recall@5=TP/total de relevantes de esta intención; ejemplos con seis positivos.
- **COMPLETA** `precision_cinco(ids,relevantes)`, aplicado a los propios IDs del equipo.
- Calcular métricas para BM25 y E5 contra juicios externos curados del mismo corpus. Reconocer resultados discutibles de juicios y que no son todo SECOP.
- **COMPLETA** `rrf_dos_posiciones(posicion_bm25,posicion_e5)`, suma `1/(60+r)`, y construir RRF completo a partir de posiciones.
- Elegir motor, descartar una alternativa y limitar conclusiones con métricas reales. El híbrido no tiene obligación de ganar.
- Evidencias `E3/laboratorio_precision.json`, `E3/laboratorio_rrf.json`, `E3/evaluacion.json`.

### E4 · Imagen del propio ranking y transformaciones (20 puntos)
- La imagen `ranking.png` sale del Top-5 propio, por lo que su relación con SECOP está fundamentada sin usar fotografías editoriales protegidas.
- **COMPLETA** `luminancia_rgb(rgb)` con los coeficientes 0,2126, 0,7152 y 0,0722; compara rojo y verde.
- Inspecciona RGB, luminancia y un histograma de 16 bins; comprueba suma de píxeles.
- Genera perfiles de 160 y 640 px; compara legibilidad, dimensiones, conteo, brillo y tamaño en bytes.
- Distingue histograma de OCR: los bins no reconocen palabras ni prueban irregularidades.
- Evidencias `E4/laboratorio_luminancia.json`, `E4/ranking.png`, `E4/perfil_160.png`, `E4/perfil_640.png`, `E4/imagen.json`.

### E5 · Audio verdadero y señales acústicas (15 puntos)
- Descarga diez WAV reales MINDS14 es-ES con licencia CC BY 4.0, fuente y SHA comprobado. No atribuirlos a El Tiempo ni SECOP.
- **COMPLETA** `rms_manual(muestras)` para [1,-1,0,0] y explica por qué media simple 0 no implica RMS 0.
- Reproduce señales, inspecciona formas de onda, amplitud, duración, frecuencia de muestreo, RMS, ZCR, FFT, centroide, y espectrograma.
- Cambia únicamente la ventana FFT de 512 a 1024, con comparación de resolución temporal/frecuencial sobre el MISMO WAV.
- Distingue transcripción humana de referencia y ASR realmente ejecutado; no afirmar que RMS/FFT transcriben palabras. No exigir Whisper de pago.
- Evidencias `E5/laboratorio_rms.json`, `E5/audios.json`, `E5/audio/voz_*.wav` y originales autorizados.

### E6 · Demostración final (5 puntos)
- Crear `explorador.html` offline a partir de rankings, imagen y voces: secciones con fuentes separadas.
- Defender mediante controles cerrados una decisión de búsqueda y límites de imagen/audio.
- Correr autovalidación de 18 controles y abrir el ZIP/manifest; ninguna prueba depende exclusivamente del estado de variables del notebook.
- No confundir la fabricación del ZIP con la habilidad académica; la exportación no suma puntos nuevos.

## 3. Rúbrica oficial del cuaderno (100 puntos)
| Control | Competencia nueva comprobada | Puntos |
|---|---|---:|
| E1.1 | Tokens, DF e IDF propios | 6 |
| E1.2 | Dos rankings BM25 consistentes | 8 |
| E1.3 | Cambio léxico y ranking recalculado | 6 |
| E2.1 | Embeddings E5 con prefijos y experimento | 7 |
| E2.2 | Coseno manual + rankings por E5 | 8 |
| E2.3 | Atlas Vector Search real (o 3 puntos locales por contrato de índice, no por uso remoto) | 6 |
| E2.4 | Top-k y filtro por entidad | 4 |
| E3.1 | Precision@5 manual y métricas contra relevancia | 6 |
| E3.2 | RRF manual y fusión completa | 5 |
| E3.3 | Motor elegido, alternativa y límite anclado a datos | 4 |
| E4.1 | Luminancia manual e histograma | 6 |
| E4.2 | Dos transformaciones medibles | 8 |
| E4.3 | Elección por legibilidad y límite | 6 |
| E5.1 | Diez WAV humanos/licenciados y atribución | 5 |
| E5.2 | RMS manual y FFT real | 6 |
| E5.3 | Diferencia entre acústica y transcripción | 4 |
| E6.1 | Explorador con fuentes distinguidas | 3 |
| E6.2 | Defensa de las decisiones integradas | 2 |
| **Total** | **18 controles** | **100** |

Los ejercicios de código son requisitos de los respectivos controles; no son material decorativo. La verificación automatizada no sustituye la auditoría humana de un servicio Atlas remoto. Conversión orientativa heredada del TC1: `1 + 4 × puntos/100`, a una décima con entrega; sin entrega, 0,0. La ponderación sobre la asignatura se verifica con el PDA vigente.

## 4. Entrega definitiva: GitHub privado + correo institucional
- **Fecha:** sábado 14 de noviembre de 2026, **23:59:59, Bogotá UTC−5**. «14 de noviembre a medianoche» se interpreta como el final del 14.
- **Una entrega por equipo**, parejas o individual igual que TC1.
- **Cuenta GitHub personal:** repositorio nuevo, visibilidad **Private**, sugerido `BigData2026_TC2_<PAREJA_ID>`. No usar repositorios públicos.
- **Acceso del docente:** invitar como colaborador al usuario GitHub `jazaineam1` (cuenta propietaria del repositorio del curso; confirmar si prefiere otra cuenta). El docente debe poder acceder antes de revisar.
- **Tres archivos en la raíz:** `TC2_<PAREJA_ID>.ipynb` ejecutado, `TC2_<PAREJA_ID>.zip` con E1–E6/HTML/audios, y `manifest_tc2.json` con puntuación y huella.
- **Subida desde web:** GitHub `Add file → Upload files → Commit changes`, comprobar que los tres archivos aparezcan. No exigir terminal ni GitHub Classroom.
- **Notificación como TC1:** enviar correo institucional a el correo institucional del docente indicado en el TC1 y en la guía del TC2, con copia al compañero, enlace completo del repositorio PRIVADO, integrantes, códigos y SHA-256 del manifest. No adjuntar ZIP.
- **Cierre válido:** los tres archivos cargados, invitación enviada y correo de notificación **antes** del cierre. Tras corrección, nuevo commit y respuesta al mismo hilo con huella nueva. Cambios posteriores no sustituyen la entrega puntual.
- **Privacidad:** el notebook/ZIP pueden contener nombres y códigos del equipo y audios de terceros con atribución; nunca publicarlos. No incluir URI de MongoDB, claves, tokens ni enlaces de reclamación. El Drive de Colab es SOLO respaldo de trabajo, no canal de entrega.

## 5. Datos y límites de inferencia
**Corpus:** `Datos/tc2_corpus_2026.json` con 200 documentos únicos derivados de `Datos/bandeja_revision_2026.json`; `Datos/tc2_juicios_2026.json` con cinco intenciones, literal/paráfrasis y al menos cinco documentos positivos por intención. Juicios pedagógicos basados en objetos contractuales, que deben someterse a segunda revisión si se usan para calificación formal. No afirmar representatividad del universo SECOP.

**Audio:** diez voces MINDS14 reales, distintas, licencia CC BY 4.0 con hash del dataset fijado. Las transcripciones del dataset son **referencias humanas**, no ejecución de ASR.

**Imagen:** archivo generado desde ranking propio, no imagen editorial. El histograma no realiza OCR ni interpreta el contenido del contrato.

**Atlas:** el notebook distingue explícitamente NumPy local de índice remoto. El valor local de un ranking no puede demostrar una consulta $vectorSearch real. Una ejecución remota necesita validación docente o evidencia externa fiable.

## 6. Pruebas y criterios de publicación
| Puerta | Cómo se comprueba | Restricciones |
|---|---|---|
| Estructura académica | `utils/validate_taller_control_2.py` | 81+ celdas, 18 controles, 100 puntos, seis funciones COMPLETA |
| Cálculos | QA offline | BM25, coseno, Precision@5, Recall@5, RRF, luminancia y FFT |
| Audio verdadero | GitHub Actions `audio-real` | diez WAV reales, hash, CC BY 4.0, no síntesis |
| Prueba integral | `utils/test_tc2_e2e_real.py` | CPU limpio, seis huecos resueltos SOLO en prueba, E5 real, HTML, ZIP, nota reproducible |
| Corrector docente | `utils/calificar_tc2_zip.py` | Recalcular ZIP; rechazar traversal y ZIP desproporcionado |
| Experiencia móvil | `tests/tc2-guide.visual.spec.js` | 390, 768 y 1366 px, 31 pasos, teclado, modo oscuro, accesibilidad |
| Seguridad | `utils/scan_secrets_pii.py` | No se admiten secretos ni correos de estudiantes versionados |
| Antes de fusionar | Revisión docente + verificaciones CI | confirmar peso oficial, cuentas GitHub del docente y Atlas si aplica |
| Después de fusionar | Revisión pública de enlaces y guía | cambiar enlaces de rama temporal a `main`, actualizar LMS |

El PR permanece en revisión hasta que se completen las pruebas en su último commit. No afirmar que se ha ejecutado Atlas real ni un envío GitHub por parte de un estudiante si solo se ejecutaron las rutas locales automatizadas.

## 7. Preguntas docentes todavía abiertas
**Resueltas:** fecha y hora de entrega; GitHub privado como destino de los tres archivos; correo institucional como notificación; alcance hasta S10 y ausencia de temas evaluados en TC1.

**Pendientes de confirmar sin detener el desarrollo:** peso de TC2 en la nota final (¿25 % como PDA antiguo?) y cuál cuenta GitHub debe recibir invitaciones (`jazaineam1`, dueña del repositorio, o la cuenta personal principal `jazaineam`).

## 8. Enlaces internos
- Cuaderno: `Cuadernos/Taller_Control_2.ipynb`.
- Guía: `assets/tutoriales/tc2-paso-a-paso.html`.
- Motor: `utils/tc2_core.py`.
- Corrector de ZIP: `utils/calificar_tc2_zip.py`.
- Datos y relevancia: `Datos/tc2_corpus_2026.json`, `Datos/tc2_juicios_2026.json`.
- QA: `.github/workflows/tc2-qa.yml`.
- PR #145: `https://github.com/jazaineam1/BigData2026/pull/145`.
