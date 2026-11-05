# TC2 V2 — Del buscador al explorador inteligente de evidencias
Universidad Central · Maestría en Analítica de Datos · Big Data 2026-2S

**Estado: PLAN PARA REVISIÓN, NO PUBLICADO A ESTUDIANTES.**
Alcance: competencias nuevas de S07 (BM25/Elasticsearch), S09 (embeddings, recuperación semántica, búsqueda vectorial, evaluación y RRF) y S10 (imágenes y audio).
El TC1 S08 ya evaluó ingesta SECOP, concurrencia, contrato de datos, MongoDB documental, índices convencionales, agregaciones, Cassandra, Neo4j, SHA-256 de RAW y entrega técnica. TC2 NO asignará puntaje a repetir esas operaciones.
El PDA disponible corresponde a 2023-I: verificar versión vigente y equivalencia de la evaluación antes de asignar peso oficial. Fecha y canal de entrega sujetos a aprobación.

## 1. Diagnóstico de redundancia, decisión de alcance

| Habilidad ya evaluada en TC1 | Qué hace TC2 |
|---|---|
| Descarga SECOP y concurrencia | Proporcionar corpus fijo, sin evaluación de adquisición |
| Modelo documental y upsert convencional de Atlas | Tomar documentos listos, no volver a modelarlos |
| Índices B-tree, filtro, sort y aggregations convencionales | No volver a calificarlos |
| Cassandra/query-first | Excluir |
| Neo4j/Cypher | Excluir |
| RAW, SHA-256, Parquet, manifest y ZIP | Utilizar como infraestructura, no como puntos |
| Decisiones genéricas de infraestructura | Sustituir por decisiones nuevas: relevancia, semántica, imagen y señal |

### Experiencia que sí aprende el estudiante
La habilidad central es diferenciar *palabra*, *significado*, *relevancia* y *señal física*, y comprobar cómo un resultado útil cambia según decisiones observables. Cada etapa contiene seis movimientos:
1. Problema concreto del personaje.
2. Predicción por selección cerrada ANTES de ejecutar.
3. Ejemplo mínimo con números legibles.
4. Experimento con un parámetro cambiado por el estudiante.
5. Diagnóstico automático y posibilidad de corregir.
6. Interpretación: «Cómo se lee», «Qué nos dice», «Qué NO permite concluir todavía», «Qué error común».

Sin respuesta académica abierta: se permiten consultas como entrada técnica, código y números; las decisiones y los límites se registran con opciones cerradas y valores propios (AGENTS.md). La predicción debe ser guardada antes de mostrar la salida; una segunda oportunidad mejora dominio sin borrar el primer intento. Un estudiante no necesita conocer de antemano las respuestas para terminar.

## 2. Historia y producto

**Título para estudiantes:** TC2 · Compras Claras 2: cuando las palabras no coinciden y los archivos no hablan solos.

Laura conserva la bandeja contractual del TC1. Ahora una consulta sobre aeronaves no encuentra todos los procesos relevantes porque los redactores usan otras expresiones. Quiere entender por qué, mejorar el ranking y mostrar evidencia. También dispone de una nueva colección de grabaciones autorizadas y necesita extraer rasgos acústicos. La herramienta no debe confundir un espectrograma con transcripción, ni atribuir una grabación a un contrato sin relación comprobada.

**Producto verificable:** un explorador HTML generado por el propio cuaderno:
- Espacio «Expedientes SECOP»: consultas lexical, semántica e híbrida sobre exactamente el mismo corpus; Top-5, IDs, enlaces, pertinencia, filtro y métricas.
- Espacio «Imagen del hallazgo»: gráfico PNG generado a partir del ranking realmente obtenido, inspector RGB/histograma y dos versiones transformadas para comparar legibilidad y tamaño.
- Espacio «Voces autorizadas»: diez WAV de MINDS14 es-ES, escoger/reproducir, forma de onda, RMS, espectro y espectrograma de una selección; transcripción de referencia etiquetada como tal. No hay enlace causal ni editorial entre MINDS14 y SECOP.
- Ficha final: estrategia seleccionada, alternativa descartada y límite comprobable, todos referidos a valores propios; fuentes diferenciadas.
- El explorador es salida del estudiante, no un nuevo servicio que deba alojar o programar. El cuaderno es el motor, y la vista HTML es un resumen consultable offline de resultados ya calculados.

**Recursos canónicos de estudiante (máximo dos):** Cuadernos/Taller_Control_2.ipynb (toda explicación más Python y autoevaluación) y assets/tutoriales/tc2-paso-a-paso.html (checklist, solución de errores, estado local sin pretender registrar nota). Los laboratorios S07/S09/S10 se vinculan desde las celdas como apoyo, no como requisitos adicionales. No hay tres sistemas obligatorios ni edición manual de HTML.

## 3. Fuentes y reglas de evaluación justa

### Corpus textual
Se prepara una vez antes de publicar un subconjunto estable del corpus SECOP de S07/S09, inicialmente hasta 120 documentos, con campos id_proceso, nombre_proceso, descripcion, entidad y url_secop. Los estudiantes reciben el snapshot para que no se repita la adquisición de TC1.
- Usar idénticos IDs y textos en BM25, E5 y RRF.
- No premiar conteos, deduplicación ni hashes: se verifican como precondición automática.
- Congelar un banco de seis *intenciones profesionales*, cada una expresada en versión literal y paráfrasis; seis parejas de consulta, 12 redacciones. Asignar a cada equipo un par mediante identificador no personal.
- Juicios de relevancia independientes de ambos motores, validados por el docente contra los 120 documentos. Cada intención debe tener suficientes documentos relevantes y no relevantes (mínimo cinco relevantes) y una justificación factual. Si no se cumple, cambiar el banco antes de publicarlo; no inventar qrels.
- El mismo conjunto de relevancia sirve para literal/paráfrasis de una intención. Comparación por ID, no por valores absolutos de score de motores diferentes.
- La selección de 120 puede estar centrada en aeronáutica; no afirmar representatividad de SECOP ni generalizar latencia.

### Imagen
El PNG obligatorio se **genera desde el ranking propio del equipo** (por ejemplo, una visualización de los Top-5 y sus puntuaciones). Esto crea una relación auténtica entre búsqueda e imagen, sin descargar fotografías editoriales. Un segundo archivo propio autorizado es opcional. La imagen resultante permite inspeccionar píxeles, luminancia e histograma, y comparar dos perfiles con impacto en legibilidad de etiquetas.
No usar El Tiempo como fuente automática de medios ni redistribuir imágenes editoriales de derechos no verificados.

### Audio
Tomar los diez WAV reales de voz del conjunto PolyAI/MINDS14 es-ES, licencia CC BY 4.0, que ya utiliza S10; el material contiene referencia de transcripción, procedencia e intención de origen. El docente verificará hash, URL de origen, licencia y disponibilidad antes de publicar y proporcionará respaldo descargable autorizado si falla el acceso al proveedor.
Los WAV no son audios de El Tiempo ni están vinculados con contratos SECOP. Es una colección separada de consultas habladas; la relación verificada es WAV ↔ referencia textual del mismo registro, no WAV ↔ contrato. ASR/Whisper y WER no son obligatorios.

## 4. Secuencia de aprendizaje y evaluación

### Desafío 0 — La consulta que falla (no calificable)
Abrir Colab, guardar copia, seleccionar equipo, restaurar corpus y reproducir caso de Laura. Mostrar dos consultas distintas que expresan una misma intención. **Antes de buscar**, seleccionar cuál creen que encontrará más resultados útiles y por qué opción cerrada. Una predicción equivocada no resta puntos; sirve para abrir el problema.
Demostración manual: tres documentos cortos, tokens, rareza, longitud y por qué una coincidencia léxica puede no equivaler a relevancia. Resultado esperado, diagnóstico y opción «reintentar preparación». Sin descargar SECOP.

### E1 — ¿Por qué este documento aparece primero? BM25 (20 puntos, S07)
- Ejemplo resuelto: tokens, analizador, frecuencia, rareza y longitud de documento en un universo mínimo.
- Ejecutar búsqueda BM25 sobre snapshot fijo, comparando literal/paráfrasis, sin simular que Python es Elasticsearch.
- Cambiar una palabra importante de la consulta y observar el movimiento de al menos un resultado (o demostrar que no cambió).
- Comprobar orden Top-5 y desempate por ID en el motor canónico. Elasticsearch/Elastic Console puede utilizarse para contraste real si está disponible, pero no se exige abrir cuenta de pago ni se comparan scores absolutos entre implementaciones.
- Registrar predicción inicial, Top-5 antes/después, tokens que influyeron y decisión de utilidad del ranking en un campo cerrado.
- Salida para E2: consultas asignadas y rankings lexicales vinculados al mismo corpus.
- Si no hay resultados, enseñar por qué (tokens/filtros), no cambiar la respuesta de forma silenciosa.

### E2 — ¿Y si el contrato usa otras palabras? Embeddings y búsqueda vectorial (25 puntos, S09)
- Ejemplo manual de vectores cortos y coseno: dirección frente a magnitud; mostrar caso donde coincidencia literal es insuficiente.
- Transformar documentos con passage: y consultas con query: mediante multilingual-e5-small; mostrar N × 384 y comprobar que se usa el mismo modelo.
- Generar Top-5 exacto en NumPy por coseno: identificar al menos un cambio de posición respecto al BM25 sobre paráfrasis.
- Para base vectorial REAL, intentar Atlas Ephemeral, upsert de vectores e índice vectorial y consultar con $vectorSearch, guardando ping/índice/query_real. Es una habilidad nueva: no se recalifica el MongoDB documental convencional de TC1.
- Experimento una variable: filtro por entidad o presupuesto de candidatos; contrastar elegibles y Top-k. No llamar Precision@k al solapamiento entre vecinos ni presentar latencia de una corrida como benchmark.
- Contingencia justa: si Atlas devuelve error real verificable o 429, mantener ranking exacto NumPy y evidencia explícita «Atlas NO EJECUTADO», con evaluación alternativa de definición del índice/pipeline; no regalar crédito por declarar una caída sin prueba.
- Salida E3: rankings lexicales y semánticos sobre el mismo conjunto.

### E3 — ¿Cuál recupera evidencia pertinente? Comparación e híbrida (15 puntos, S07+S09)
- Antes de calcular, pedir que predigan si recuperar más documentos equivale a mejor precisión.
- Con los juicios docentes del mismo corpus, calcular TP, Precision@5 y Recall@5 para las dos consultas y ambos mecanismos. Ejemplo manual pequeño y comprobación independiente.
- Fusionar los rankings BM25 y E5 por Reciprocal Rank Fusion (RRF, constante 60) y mostrar posiciones, no comparar puntuaciones numéricas de modelos distintos.
- Decidir entre BM25, E5 y RRF con una métrica propia, nombrar alternativa descartada y límite específico («la relevancia etiquetada cubre esta muestra, no todo SECOP»; no declarar fraude/causalidad).
- Salida E4: ranking elegido convertido en insumo de una imagen de hallazgo.
- Si E1/E2 falló, se proporciona ranking de respaldo etiquetado; la etapa fallida mantiene 0/parte de sus puntos, pero E3 se puede completar sin bloqueo.

### E4 — ¿Una imagen conserva lo que necesitamos ver? (20 puntos, S10)
- Crear de forma reproducible el PNG del Top-5 del equipo, con títulos, etiquetas y escalas, sin pedir que el estudiante diseñe una interfaz.
- Inspector de un píxel elegido: RGB, luminancia calculada a mano y lectura de histograma con ejes. Verificar que la suma de bins es igual a anchura × altura.
- Probar dos perfiles (por ejemplo, 160 y 640 px en el lado mayor) y variar una transformación de contraste/umbral. Comparar legibilidad de texto, dimensiones, histograma y tamaño de salida.
- Mostrar experimento donde una reducción/umbral extremo elimina información necesaria de la gráfica. El estudiante selecciona el perfil que preserva una etiqueta técnica, no el más pequeño automáticamente.
- No dar puntos por calcular un hash o guardar RAW, ya evaluado en TC1; son guardias invisibles para no adulterar los resultados.
- Salida E6: original y perfiles de la gráfica del ranking con medidas de calidad.

### E5 — ¿Qué nos dice realmente una grabación? Audio (15 puntos, S10)
- Escuchar 2 de los 10 WAV con diferentes características, elegir la posición en la tabla.
- Ejemplo manual: muestras por segundo, forma de onda, diferencia de duración y amplitud; RMS con cuatro muestras.
- Calcular para los diez audios duración, tasa de muestreo, RMS y una característica espectral; representar forma de onda y espectrograma del audio elegido.
- Elegir dos fragmentos del mismo archivo o dos audios y variar solamente tamaño de ventana FFT; observar resolución en Hz, espectro y cambios de energía. Interpretar diferencia entre volumen/amplitud y contenido lingüístico.
- Mostrar transcripción humana del mismo WAV como **referencia preexistente**, no como salida de RMS/FFT ni como ASR ejecutado. No exigir Whisper, emoción de voz, diarización ni inferencia de intención a partir del espectro.
- Decidir qué propiedad observada permite priorizar un archivo para escucha/inspección, y qué NO permite concluir.
- Salida E6: diez fichas acústicas, audio reproducible y un espectrograma ligado al WAV correcto.

### E6 — La demostración de Laura: producto y defensa (5 puntos, integración)
- El cuaderno produce una única página HTML autosuficiente de consulta de resultados: espacio SECOP (Top-5 de los tres mecanismos + métricas + decisiones), imagen del ranking con perfiles, y diez fichas de voz con fuente y mediciones.
- Dos enlaces o pestañas visuales separan las procedencias; no hay enlace artificial entre SECOP y MINDS14. Se admite comparar funciones del sistema, no afirmar conexión de contenido.
- La defensa usa controles cerrados y números del resultado: «¿Cuál mecanismo eliges para tu consulta y cuál descartas?»; «¿Qué cambió en tu imagen?»; «¿Qué prueba el RMS y qué no?». El estudiante puede corregir y revalidar.
- La exportación técnica (notebook ejecutado, HTML, ZIP, manifest de etapa) es una operación logística que **no agrega puntos por SHA/ZIP**.

## 5. Rúbrica completa — 18 controles, 100 puntos, sin repetir TC1

| Control | Qué demuestra una habilidad nueva | Puntos |
|---|---|---:|
| E1.1 | Inspecciona y explica tokens, rareza y longitud en BM25 con valores del corpus | 6 |
| E1.2 | Ejecuta y verifica los Top-5 BM25 para consulta literal y paráfrasis | 8 |
| E1.3 | Cambia una condición léxica y explica la consecuencia observada | 6 |
| E2.1 | Construye embeddings E5 con prefijos adecuados y 384 dimensiones | 7 |
| E2.2 | Recupera por coseno Top-5 y reconoce coincidencias no literales | 8 |
| E2.3 | Demuestra $vectorSearch Atlas real o contingencia válida con contrato de índice correcto | 6 |
| E2.4 | Cambia filtro/candidatos y compara un resultado real sin confundir relevancia y solapamiento | 4 |
| E3.1 | Calcula Precision@5 y Recall@5 contra juicios independientes del corpus | 6 |
| E3.2 | Fusiona BM25 y E5 con RRF, posiciones y desempates correctos | 5 |
| E3.3 | Selecciona estrategia por métricas propias, alternativa y límite específico | 4 |
| E4.1 | Interpreta píxel RGB, luminancia y bins del histograma del PNG propio | 6 |
| E4.2 | Genera dos transformaciones de imagen y compara sus efectos medibles | 8 |
| E4.3 | Detecta pérdida de legibilidad útil y escoge perfil apropiado | 6 |
| E5.1 | Escucha/inspecciona WAV reales; distingue tasa de muestreo, duración y amplitud | 5 |
| E5.2 | Calcula RMS, FFT y espectrograma; altera ventana y observa el efecto | 6 |
| E5.3 | Compara señales y explica límites frente a transcripción/intención | 4 |
| E6.1 | Genera explorador funcional que reúne rankings, imagen y audio con origen separado | 3 |
| E6.2 | Defiende una decisión integrada anclada a salidas reales, sin atribuciones falsas | 2 |
| **Total** | **Solo competencias nuevas e integración** | **100** |

La nota se calcula por control y requiere un validador independiente desde salidas propias; no asignar puntos por pulsar Ejecutar todo, empaquetar o repetir E1 del TC1. Si el estudiante solo copia un ranking sin generar el experimento y decisión correspondiente, no alcanza el máximo.

## 6. Cómo debe sentirse el recorrido

**Pantalla inicial:** Laura plantea un problema de búsqueda concreto, el estudiante elige su predicción. Ver una respuesta inesperada crea una pregunta genuina y no una lista de definiciones.

**Por desafío:** ficha de máximo una pantalla con:
- Pregunta real que resuelve.
- Lo mínimo que necesita recordar, con ejemplo manual y contraejemplo.
- Lo que ya está preparado para no repetir TC1.
- Lo que el estudiante cambia: UNA variable, una línea o una elección.
- Botón/celda «Comprueba» con esperado, observado, evidencia y diagnóstico.
- Interpretación con los cuatro rótulos fijos.
- «Si te atascastes»: recuperación y resultado de referencia etiquetado.
- «Lo que ahora puede hacer Laura»: conexión al próximo bloque.

**Didáctica:** al menos un cambio de parámetro visible por desafío, un error intencional seguro por bloque (token sin coincidencia, filtro vacío, prefijo incorrecto, imagen demasiado pequeña, ventana FFT inapropiada), una corrección y una alternativa descartada. Las predicciones son formativas; los puntos nacen de la ejecución personal reproducible.

**Diseño editorial:** evitar glosarios largos al principio; introducir término justo cuando el caso lo exige. Aproximadamente 35–45 celdas, pero no sacrificar explicación por cumplir cifra. Un cuaderno es la clase; no un contenedor masivo de código.

## 7. Ruta del docente de 180 minutos

El tiempo vive aquí, NO en el cuaderno del estudiante.

| Minuto | Actividad | Acción observable |
|---|---|---|
| 0–15 | Historia de Laura y predicción | Dos frases, ¿mismo significado? |
| 15–55 | Desafío E1 | BM25, consulta modificada y efecto en Top-5 |
| 55–100 | Desafío E2 | E5, coseno, búsqueda real o contingencia |
| 100–110 | Pausa | — |
| 110–145 | Desafío E3 | Evaluación de pertinencia y RRF |
| 145–170 | Desafío E4 (primera parte) | Imagen del ranking, RGB y perfiles |
| 170–180 | Puente y trabajo independiente | Apertura de E5 audio y E6; dudas de procedimiento |

Fuera del encuentro: completar perfiles de imagen, diez WAV, inspector acústico y página final, con una guía autónoma estimada de 90–150 minutos que debe validarse en piloto. Ningún bloque exige esperar una aprobación del docente para avanzar.

## 8. Formato, revisión y publicación

**Formato estudiante:** notebook en Colab + checklist HTML responsive. Todo el Python en el notebook; un HTML local de resultado, no un sistema adicional que configurar. El estudiante visualiza progreso técnico propio dentro de la ejecución; ningún checkbox web se convierte en nota oficial.

**Entrega:** seguir por defecto la modalidad de TC1 —carpeta de Drive restringida y correo institucional con fecha/hora coherentes— solo una vez confirmada. Si existe envío auténtico probado en LMS y el docente autoriza reemplazar el canal, anunciar UNO solo. No inventar fecha, correo nuevo ni porcentaje del curso. Propuesta de tres archivos: TC2_EQUIPO.ipynb, TC2_EQUIPO.zip y manifest_tc2.json; el ZIP contiene explorador HTML, resultados y medios permitidos. No distribuir audios de estudiantes ni datos personales.

**Criterios de liberación que requieren pruebas reales:**
1. Congelar corpus, banco de seis intenciones, literal/paráfrasis y juicio humano para los documentos. Garantizar al menos cinco positivos por intención, sin IDs ajenos al corpus.
2. Confirmar 10 WAV reales/licenciados de S10 y permitir descarga/respaldo verificable; no reproducir medios editoriales sin derechos. Verificar reproducción de audio desde HTML/ZIP en navegador objetivo.
3. Test del ejemplo manual BM25, coseno, P@5, Recall@5, RRF e histogramas. Fijar normalización, corpus y desempate; los scores BM25 y coseno no son intercambiables.
4. Test con corpus/consulta alterados, ausencia de qrels, vector de dimensión distinta, Atlas 429, índice no disponible, imagen ilegible, archivo de audio corrupto, ventana FFT y bin de histograma erróneos.
5. Test de privacidad, origen y atribución; el manifest no contiene claimURL, secretos ni correos. La UI marca «NO EJECUTADO» donde falta servicio real.
6. Ejecutar notebook completo en CPU Colab con una cuenta de prueba, comprobar perfiles en móvil/escritorio, zoom 200 %, tema oscuro, controles por teclado y accesibilidad, y volver a calificar el ZIP en proceso aislado.
7. CI de notebook/generador, validador, HTML/Playwright, scan de secretos y no-respuesta-abierta; probar al menos dos equipos con consultas asignadas distintas.
8. Reconciliar con PDA vigente; acordar fecha, duración de entrega, canal y peso; fusionar PR y publicar solo después de cumplir los gates.

**Secuencia de implementación:**
- A: fijar corpus y juicios independientes / licencias.
- B: generador y notebook E1–E3; motor de score desde archivos.
- C: E4/E5 con imagen derivada del ranking y MINDS14 audio real.
- D: explorador generado, tutorial, validación adversarial, ejecución completa real.
- E: revisión pedagógica y publicación en LMS tras aprobación, dejando TC1 intacto.

## 9. Definición de éxito pedagógico

Al terminar, una pareja puede explicar con sus resultados:
- Por qué BM25 encontró o perdió un contrato con palabras diferentes.
- Por qué una búsqueda por significado recuperó un documento y qué significa el coseno.
- Por qué el ranking de mejor score no siempre tiene mejor Precision@5.
- Qué aporta RRF y qué NO demuestra el solapamiento ANN–ENN.
- Qué informa un histograma/píxel de la imagen del ranking, y cuándo una transformación destruyó legibilidad.
- Qué informa RMS/FFT/espectrograma de una voz real, y por qué no transcriben palabras.
- Qué medios se pueden relacionar por origen comprobable y cuáles deben quedar separados.

**Decisión central:** TC2 evalúa 95 puntos de conceptos S07–S10 y 5 de integración. Los conocimientos ya evaluados en TC1 funcionan como infraestructura gratuita, no como un segundo examen.

Fuentes del repositorio: AGENTS.md; docs/PDA_guia.md; Cuadernos/Taller_Control_1.ipynb; utils/tc1_contrato.py; Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb; Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb; Cuadernos/10_Imagenes_Audio.ipynb; Datos/s10_audio_reales/README.md; assets/s10/etl-reactivo.html.
