# Plan maestro de reconstrucción pedagógica de Big Data · 150 minutos
**Universidad Central · Maestría en Analítica de Datos · Documento de diseño de la rama mejora-pedagogica-integral · 26 de noviembre de 2026**

Este documento sustituye la especificación resumida anterior. Es un plan de construcción y auditoría, no una afirmación de que las clases, sus notebooks, los resultados remotos o las evaluaciones hayan sido reconstruidos o ejecutados. Se conserva el trabajo previo. La unidad de diseño es una secuencia de enseñanza y práctica con un problema profesional, una decisión, evidencia y un producto transferible. Los 25 apartados de enseñanza por sesión son guiones de diseño para convertir en diapositivas, no 425 diapositivas ya implementadas.

## 0. Corrección vinculante del alcance: 40.000 palabras por sesión

El estándar corregido reemplaza cualquier umbral de extensión anterior. No se acepta ninguna sesión con menos de 40.000 palabras de contenido pedagógico propio. Son 640.000 palabras como mínimo para S01–S16 y 680.000 incluyendo S14A, además de 25 diapositivas docentes por sesión y 150 minutos de ruta principal. La presentación y el notebook constituyen los dos recursos estudiantiles principales; las lecturas expandidas, ejemplos interactivos y anexos formativos se integran en ellos. No se exige leer íntegramente el material durante la clase.

### Presupuesto editorial mínimo de cada sesión
| Componente | Palabras originales objetivo mínimo | Producto esperado |
|---|---:|---|
| Problema, contexto, objetivos y prerrequisitos | 2.000 | Caso, diagnóstico y vocabulario de entrada |
| Fundamentos, definiciones, mecanismos y arquitectura | 8.000 | Explicaciones completas, diagramas comentados y derivaciones |
| Ejemplos resueltos y contraejemplos | 6.000 | Datos pequeños, pasos intermedios, cálculos e interpretación |
| Experimentos, comparaciones y simuladores | 5.000 | Hipótesis, parámetros, controles, resultados y límites |
| Laboratorio E2E y explicación de código | 9.000 | Preparación, operaciones explicadas, salida, depuración y exportación |
| Interpretación y diagnóstico de errores | 3.000 | Lectura de tablas, fallos frecuentes, recuperación y decisiones |
| Ejercicios formativos, retroalimentación y transferencia | 5.000 | Variantes, soluciones formativas no evaluativas y producto autónomo |
| Profundización, glosario, síntesis y referencias comentadas | 2.000 | Material de consulta, conexiones y próximos pasos |
| **Total por sesión** | **40.000** | **Mínimo no compensable entre sesiones** |

La distribución es un presupuesto editorial de partida, no ocho capítulos idénticos para todas las tecnologías. Puede redistribuirse según tema si la suma original mantiene el mínimo y cada competencia está desarrollada. En talleres y defensa, la extensión se alcanza con preparación conceptual, casos formativos independientes, alternativas técnicas, interpretación y apoyo de ejecución; jamás mediante publicación de las respuestas de las evaluaciones vigentes. El contenido duplicado entre presentación y cuaderno se cuenta una sola vez.

### Plan de producción y medición
1. Inventariar conceptos, relaciones, datos reales disponibles, ejemplos y objetivos de cada sesión. Cada ficha de las 25 pantallas se transforma en una unidad de aprendizaje completa, no en un párrafo de resumen.
2. Redactar contenido específico desde cero cuando falte y preservar lo valioso del material previo. Elaborar ejemplos resueltos con entradas, estados intermedios y comprobaciones independientes; especificar datos y procedencia.
3. Integrar lectura expandida, interacciones, diagramas con función pedagógica y cuaderno completo. Identificar ruta principal de 150 minutos y rutas de profundización sin agregar un tercer recurso obligatorio.
4. Ejecutar y verificar cada laboratorio; distinguir datos de ejemplo, simulaciones, resultados medidos y bloqueos reales. No completar el conteo con salidas inventadas, código repetido o instrucciones genéricas.
5. Contabilizar palabras por sesión sobre fuentes pedagógicas canónicas (prosa visible y expandida, markdown explicativo del notebook y explicaciones de gráficos y ejercicios). Excluir código fuente, datos crudos, resultados automáticos sin interpretación, navegación, metadatos, títulos, referencias bibliográficas sin comentario, protocolos de QA, texto repetido y contenido duplicado. Normalizar espacios y excluir bloques idénticos; revisar también redundancias semánticas manualmente. Registrar fuentes, hash, total bruto, exclusiones y total elegible. No certificar 40.000 palabras hasta disponer del material.
6. Aplicar rúbrica y puertas de calidad, ensayo de duración y comprobación de presentación real. Solo declarar terminada una sesión cuando cumpla extensión original, profundidad, ejecución y autonomía. Mantener main intacta y reutilizar la rama actual.

### Estado de producción
Las 425 fichas existentes son especificaciones de diseño, no diapositivas implementadas ni 680.000 palabras pedagógicas. Para cada sesión el mínimo pendiente de acreditar es 40.000 palabras. La tabla de progreso siguiente registra objetivos, no conteos observados de enseñanza. La auditoría de S01 previamente reportó 5.115 palabras de desarrollo de presentación bajo otro método; no se puede restar automáticamente de la meta porque aún falta auditar y deduplicar el cuaderno y los demás recursos.

| Sesión | Meta de palabras elegibles | Diapositivas mínimas | Estado de certificación de extensión |
|---|---:|---:|---|
| S01 | 40.000 | 25 | Pendiente de acreditar |
| S02 | 40.000 | 25 | Pendiente de acreditar |
| S03 | 40.000 | 25 | Pendiente de acreditar |
| S04 | 40.000 | 25 | Pendiente de acreditar |
| S05 | 40.000 | 25 | Pendiente de acreditar |
| S06 | 40.000 | 25 | Pendiente de acreditar |
| S07 | 40.000 | 25 | Pendiente de acreditar |
| S08 | 40.000 | 25 | Pendiente de acreditar |
| S09 | 40.000 | 25 | Pendiente de acreditar |
| S10 | 40.000 | 25 | Pendiente de acreditar |
| S11 | 40.000 | 25 | Pendiente de acreditar |
| S12 | 40.000 | 25 | Pendiente de acreditar |
| S13 | 40.000 | 25 | Pendiente de acreditar |
| S14 | 40.000 | 25 | Pendiente de acreditar |
| S14A | 40.000 | 25 | Pendiente de acreditar |
| S15 | 40.000 | 25 | Pendiente de acreditar |
| S16 | 40.000 | 25 | Pendiente de acreditar |
| **Total** | **680.000** | **425** | **No certificado** |


## 1. Alcance, evidencia y diagnóstico
Se inspeccionaron el archivo previo, docs/auditoria-s01-clase-completa.md, docs/auditoria-s01-profundidad.md, docs/auditoria-aula-unificada-150-min.md, docs/auditoria-pedagogica-poslimpieza.md, docs/mapa-sesiones.md, docs/PDA_guia.md, AGENTS.md, el generador y fuente JSON de S01, el HTML del piloto, el observatorio y los notebooks S01 y S14A. La inspección del repositorio no equivale a observar una clase ni ejecutar un entorno externo. El plan anterior de 20 diapositivas y 3.000 palabras se amplía a un mínimo de 25 diapositivas sustantivas, excluidas portada decorativa, navegación y pausa; se establece, por corrección expresa del docente, un mínimo obligatorio de 40.000 palabras originales de contenido pedagógico POR CADA SESIÓN, no por curso ni por plan maestro. Este requisito incluye también S08, S12, S16 y la opcional S14A, con tratamiento compatible con sus rúbricas y sin publicar soluciones evaluativas. No se cuenta repetición de instrucciones, código, títulos o menú para ese umbral. Se generan 425 especificaciones de diapositiva para 17 recorridos (400 para las 16 sesiones obligatorias y 25 para S14A opcional). Se mantiene el límite de dos recursos obligatorios: presentación y cuaderno. El observatorio es el producto integrado, no una tercera guía que se deba recorrer antes de aprender.

La auditoría del aula unificada registró una media provisional 4,53/5 y cinco pantallas por sesión, con pruebas sobre DOM simulado. La propia auditoría reconoció que no se verificaron todos los cuadernos externos ni la proyección real. No es válido convertir esos resultados en una certificación de aprendizaje. La auditoría poslimpieza registró 3,91/5 con método diferente; no se comparan directamente los dos números. El nuevo sistema separa inventario, diseño, ejecución, experiencia de aula y aprendizaje. No asigna nuevas notas retrospectivas a sesiones no observadas. S01 tiene 20 diapositivas docentes y una pausa, 150 minutos planificados y 5.115 palabras pedagógicas reportadas por la segunda auditoría. Su notebook tiene 85 celdas, 33 de código y cero celdas de código con salidas persistidas en el JSON inspeccionado; esto no prueba que nunca se ejecutó. El reporte de S01 documenta cálculos locales y pruebas DOM simuladas, no ejecución limpia de Colab ni de API. El fuente JSON contiene 21 entradas incluyendo pausa, con tiempos que suman 150. Se preserva su contenido útil; se amplía a 25 pantallas pedagógicas, incluyendo enseñanza de cada término, ejemplos independientes, experimentación, laboratorio y relevo. S14A tiene 28 celdas, nueve de código, ninguna salida persistida en el archivo revisado y una ruta sintética de 128 variables; su objetivo de capacidad no está demostrado por la mera presencia de código.

La auditoría anterior indicó prioridades específicas S03/S06/S11/S14A/S16: explain auténtico, consultas equivalentes, OCR/ASR y visor en entorno real, entrenamiento de escala y predicciones integradas. Se mantienen como bloqueos de aceptación, no como tareas ya concluidas. Las sesiones S08 y S12 son talleres evaluativos con rúbrica vigente; el diseño de 25 pantallas apoya preparación, práctica no evaluativa y control de ejecución, pero nunca publica la solución ni crea otra evaluación. S15 es formativa, S14A opcional y S16 conserva la defensa. La guía PDA del repositorio advierte que el PDF identifica al grupo 1 y no al grupo 2; no se modifican fechas, pesos ni evaluación hasta verificar la fuente institucional pertinente. AGENTS.md establece 180 minutos y tiempos en libreto docente; el pedido explícito de este plan define un núcleo de 150, con 10 de pausa. No se reescribe AGENTS.md en este cambio documental ni se publican libretos privados. Los 30 minutos adicionales de una franja de 180 pueden ser contingencia, consultas o extensión, no contenido obligatorio encubierto; la conciliación de horas institucionales queda pendiente.

## 2. Referentes y decisiones pedagógicas
- MIT 6.5840, https://pdos.csail.mit.edu/6.5840/ y https://pdos.csail.mit.edu/6.5840/general.html : posgrado con clases, lecturas y laboratorios de programación y depuración. Se adapta su énfasis en mecanismo, coordinación y fallos, no sus prerrequisitos ni su carga semanal.
- Berkeley CS186, https://cs186berkeley.net/ y https://cs186berkeley.net/syllabus/ : clases, discusiones, ejercicios cortos y proyectos de bases de datos. Se toma la vinculación entre principios internos, consultas y proyectos, no sus evaluaciones.
- Data Engineering Zoomcamp, https://github.com/DataTalksClub/data-engineering-zoomcamp y https://datatalksclub.github.io/docs/courses/data-engineering-zoomcamp/curriculum/ : módulos con código, tareas y proyecto; se adapta continuidad entre artefactos y no se duplican plataformas externas.
- Carnegie Mellon Eberly Center, https://www.cmu.edu/teaching/assessment/basics/alignment.html : objetivos observables, actividades y evidencias alineadas; cada diapositiva debe enseñar algo que habilite una acción.
- Freeman et al., 2014, DOI 10.1073/pnas.1319030111, https://pubmed.ncbi.nlm.nih.gov/24821756/ : metaanálisis de 225 estudios universitarios STEM sobre aprendizaje activo frente a clase expositiva; orienta la actividad práctica, no establece una proporción universal de minutos para posgrado.
- Mayer, Multimedia Learning y principios de segmentación, coherencia, señalización y contigüidad, https://www.cambridge.org/core/books/multimedia-learning/7A62F072A71289E1E262980CB026A3F9/listing y https://doi.org/10.1017/9781108894333.025 : segmentar, destacar relaciones y controlar redundancia. La riqueza pedagógica se distribuye en proyección y lectura ampliada, no se vuelca todo en una pantalla.
- PRIMM (predecir, ejecutar, investigar, modificar, crear) se adapta como secuencia de apoyo progresivo, no como prueba de superioridad en este grupo. La investigación de aprendizaje activo se traslada con prudencia: esta clase es de adultos de maestría y sus resultados se deben medir con sus propias evidencias.
- Databricks Free Edition, https://docs.databricks.com/aws/en/getting-started/free-edition-limitations , versión consultada actualizada el 16 de noviembre de 2026: compute serverless limitado, cuotas, restricciones de red y ausencia de garantías de servicio. Debe comprobarse soporte de APIs ML y persistencia con prueba mínima antes de escalar, y distinguir Colab/Spark local de ejecución remota.

El patrón docente es problema, modelo mental, mecanismo, ejemplo manual, demostración, práctica guiada, modificación, control independiente, transferencia y cierre. Una actividad de selección de opciones es útil para autoevaluación cuando usa el resultado propio y distractores específicos; no es nueva calificación. En talleres, las demostraciones usan casos distintos y las estaciones respetan enunciado y rúbrica vigentes. Un laboratorio que solo ejecuta código ya escrito no acredita autonomía. La interpretación sigue los cuatro rótulos del repositorio: Cómo se lee; Qué nos dice; Qué NO permite concluir; Qué error común. Cada concepto nuevo trae definición en español y término inglés cuando aporte valor.

## 3. Tiempo de clase y presupuesto de atención
La franja núcleo se compone de 5 minutos de apertura (dos diapositivas), 20 minutos de fundamentos (cuatro), 25 minutos de ejemplos y experimentación (cinco), 20 minutos de demostración y preparación de práctica (cuatro), 10 minutos de pausa no computada como diapositiva, 45 minutos de laboratorio (seis), 15 minutos de autonomía y transferencia (tres) y 10 minutos de cierre (una). Total 150. Son 70 minutos iniciales con participación y demostraciones, 10 de pausa, 70 de trabajo y cierre. No se asignan 25 pantallas uniformes de seis minutos; la actividad define duración. En sesiones evaluativas se debe reservar el tramo de trabajo autónomo antes que repasar contenido; la secuencia se ajusta al enunciado sin cambiar sus requisitos. Para la defensa S16, el tiempo de equipos e intervención se recalcula con el número efectivo de presentaciones y la modalidad oficial: el esquema es de diseño, no impone 5 minutos por equipo.

Una exposición a 110–150 palabras por minuto podría cubrir 7.700–10.500 palabras en los 70 minutos iniciales si se hablara sin parar, pero ese escenario no es deseable. El mínimo de 40.000 palabras originales por sesión corresponde al material pedagógico completo, no a la duración oral. Leerlo íntegramente en 150 minutos exigiría aproximadamente 267 palabras por minuto incluso sin pausas ni práctica; no es un objetivo didáctico viable. La ruta de clase selecciona contenido y actividades esenciales; la lectura ampliada y el cuaderno ofrecen el desarrollo completo para consulta, práctica autónoma y profundización. La capa de proyección conserva legibilidad y no intenta colocar las 40.000 palabras simultáneamente en 25 pantallas. No todos los minutos contienen habla. Los 140 minutos netos deben incluir predicción, manipulación, lectura de resultados, ejecución, corrección y reflexión. Para el curso completo: 16×150 = 2.400 minutos (40 horas incluyendo pausas), 2.240 minutos netos (37 h 20 min), y con S14A 2.550 minutos (42 h 30 min incluyendo pausas), 2.380 minutos netos (39 h 40 min). Mínimo de contenido original de clases: 640.000 palabras para 16 sesiones, 680.000 con la opcional; ese contenido todavía debe escribirse y no es el conteo de esta especificación.

Ensayo docente: cronometrar preparación, tiempo hasta primer resultado, tiempo efectivo por actividad, celda más lenta, transición presentación-cuaderno, tiempo perdido por entorno, preguntas y cierre. Realizar ensayo de ruta base con un runtime limpio y una persona que no conozca el código. Registrar mediana y máximo cuando haya más de un ensayo, no fingir observación. Criterios propuestos: al minuto 70 deben estar preparados los conceptos y el mapa; al minuto 80 se inicia práctica; al 125 debe existir producto mínimo releíble; al 140 una decisión autónoma y un relevo; al 150 cierre. Si se excede, simplificar pasos administrativos, usar recurso congelado autorizado o desplazar ampliación, sin eliminar el objetivo esencial. El material de estudiante no lleva cronómetro obligatorio; las ventanas de este documento son planificación. Si una sesión requiere más de 150, separar extensión opcional o renegociar alcance; no repartir arbitrariamente minutos para que la suma cuadre.

## 4. Sistema visual, navegación y experiencia de uso
Mantener un único sistema de presentación: tipografía legible, colores semánticos, encabezados, tablas, diagramas SVG editables, gráficos con unidades, patrones de interacción y navegación por teclado. Proyección 16:9 sin desplazamiento vertical obligatorio, lectura ampliada y móvil con scroll natural, contraste 4.5:1 para texto normal, estados con texto además de color, alt descriptivo, foco visible, controles accesibles y retroalimentación aria-live. La portada tiene título de pregunta y dos accesos principales; cada tarjeta abre directamente presentación o cuaderno. No interponer el observatorio, el LMS o un tutorial tercero entre estudiante y clase. Las ayudas, glosario, referencias, código complementario y checklist se integran a esos dos recursos. El producto final se puede consultar desde las pantallas de relevo sin convertirlo en ruta obligatoria. Reutilizar S09 como referencia interna de interacción y calidad conceptual; S01 como piloto de estructura, no como modelo visual certificado. Una diapositiva tiene una pregunta o decisión, una visualización que explica algo y una salida o interpretación; no se agrega una imagen sin función pedagógica. En una pantalla densa se reduce cantidad de elementos simultáneos, no se corta el ejemplo. El contenido de lectura ampliada es completo, consultable y no duplica el libreto palabra por palabra.

Diseño técnico propuesto: esquema de fuente por sesión con ID estable, pregunta, objetivos, minutos de libreto, dependencia, contenido de proyección, lectura ampliada, tipo de visual, datos y modo de evidencia, ancla del notebook, interacción, resultado esperado como propiedad, limitación, evaluación formativa, y contrato de salida. Generar HTML estático desde fuente versionada; editar generador antes que salida generada. No crear un generador por diapositiva. Conservar URLs históricas y construir mapa de correspondencia antes de mover recursos. No incorporar credenciales, información personal, soluciones evaluativas o material privado. Usar activos autorizados con crédito y SHA-256 cuando proceda.

## 5. Evaluación de calidad y control de publicación
Propuesta de rúbrica de diseño de sesión, no rúbrica académica del estudiante. Escala de 0 a 5 por dimensión: 0 ausente, 1 solo declarada, 2 presente sin verificación, 3 parcial comprobada, 4 sólida con evidencia suficiente, 5 sólida con verificación independiente y prueba de transferencia. Dimensiones y ponderaciones: profundidad conceptual 20%, aprendizaje activo y autonomía 20%, práctica auténtica y reproducibilidad 20%, alineación y transferencia 15%, interpretación de resultados 10%, accesibilidad/experiencia 10%, viabilidad temporal y de recursos 5%. Calcular promedio ponderado solo con evidencia; ninguna sesión se acepta por tener media alta si una puerta crítica falla. Objetivo mínimo 4,5/5 por sesión, ninguna dimensión esencial menor a 4 y todas las puertas críticas aprobadas. Sin observación de estudiantes no se registra aprendizaje logrado; distinguir auditoría de material y evaluación de aprendizaje.

Puertas: 25 diapositivas de enseñanza con contenido propio, 40.000 palabras originales y sustantivas por sesión, verificadas individualmente y sin relleno, cronograma 150, objetivos observables, cuatro experimentos significativos o controles equivalentes no resolutivos en talleres, laboratorio principal con código visible y pasos reproducibles, interpretación después de salidas, modificación autónoma, relectura de producto, fuente y modo de evidencia, presentación real sin recorte en tamaños objetivo, prueba limpia del entorno principal y contingencia, y contrato con consumidor siguiente. Una puerta puede estar pendiente por plataforma, pero en ese caso la sesión no se certifica como completada. Para talleres y defensa se respetan restricciones de integridad y modalidad; se usan prácticas ajenas a la evaluación y controles de evidencia en lugar de resolver la entrega.

Estados de avance: E0 inventario; E1 especificación de 25 pantallas; E2 contenido y ejemplos completos; E3 generador y notebook sincronizados; E4 ejecución local controlada; E5 ejecución externa y contingencia comprobadas cuando necesarias; E6 QA real de proyección/móvil; E7 ensayo de duración; E8 aprobación docente; E9 publicación verificada y revisión de aprendizaje. Este documento alcanza E1 como especificación; no acredita E2–E9. El informe por sesión debe incluir commit, fuente, versión, entorno, fecha, caso ejecutado, salida, error, duración, captura real cuando aplique y enlace de evidencia. Una prueba de estructura no es una prueba de funcionamiento; un notebook presente no equivale a ejecución; una clase impartida no equivale a aprendizaje demostrado.

Validaciones ligeras en GitHub Actions únicamente cuando cambie el archivo pertinente: JSON, sintaxis, enlaces locales, estructura de anclas, esquemas, invariantes de cálculos pequeños y consistencia de generador. Pruebas remotas y benchmarks grandes manuales, una vez por cambio relevante, con límites y presupuesto; no introducir workflows pesados ni aumentar frecuencia. Verificar plan gratuito y disponibilidad antes de cada plataforma gestionada; preferir descarga docente autorizada y snapshot congelado frente a peticiones repetidas de estudiantes. Para S14A no se fuerza un fallo por memoria; medir capacidad mediante tamaño efectivo, presupuesto explícito y fit completado, con fallback diferenciado. Si el entorno no permite entrenamiento, reportar bloqueo sin prometer resultado. Mantener main intacta hasta completar pruebas y revisión; no crear ramas adicionales innecesarias. El plan no modifica el sitio, LMS, notebooks ni rúbricas.

## 6. Implementación por oleadas
Oleada A: S01 piloto, conservar generador y cálculos existentes, dividir cinco pantallas nuevas por valor pedagógico, vincular las 25 pantallas con las celdas reales y comprobar proyección y Colab. Aprobar con ensayo antes de clonar patrones. Oleada B: S02–S07, contratos, motores NoSQL, búsqueda lexical; ejecutar MongoDB explain, Cassandra y Neo4j reales, preflight Atlas, controles independientes y juicios de ranking. Oleada C: S08 y S09, respetar taller vigente, aprovechar mejor material interno y consolidar benchmark lexical/semántico. Oleada D: S10–S12, catálogo autónomo, OCR/ASR de activos largos, embeddings y taller sin video en S11; comprobar Codespaces y cuota de datos. Oleada E: S13–S14A, conservar datos abundantes, comparar Dask y Spark con equivalencia y entrenamientos realmente viables; S14A separado y opcional. Oleada F: S15–S16, confiabilidad y producto; respetar estado formativo y defensa vigente. Cada oleada termina con una evidencia de aceptación por sesión, no una calificación promedio que oculte bloqueos. No se fusiona este rediseño con main hasta que las puertas estén aprobadas por sesión.

## 7. Lectura de las especificaciones de diapositivas
Cada pantalla tiene contenido específico, acción, evidencia y límite, además del protocolo de diseño y QA por etapa. Las ventanas son propuestas docentes. La parte recurrente es una especificación estructurada de producción y verificación, no contenido original que pueda contabilizarse como explicación para el estudiante. Los ejemplos y resultados son contratos esperados o diseños por implementar, salvo referencias a evidencias previas identificadas. Los notebooks y motores deben verificarse antes de nombrar anclas definitivas; los números de celda no se inventan. En los talleres, ninguna pantalla contiene la resolución del entregable; aplicar la estructura de apoyo solo a casos no evaluativos o a verificación de evidencia sin solución.


# S01 · Fundamentos, adquisición y escala

**Pregunta guía:** ¿Cómo construir una fuente reproducible de procesos públicos sin confundir volumen, contratos e identidades?

**Entrada:** Corpus SECOP de 200 procesos, API de contratos como fuente distinta, diccionario y fecha de corte.

**Producto y relevo:** RAW inmutable, manifiesto de adquisición, informe de cobertura y perfil de calidad.

**Cuaderno canónico:** `sesion1_introducci_n.ipynb`. **Entorno:** Colab.

**Estado de partida:** Piloto existente: 20 pantallas docentes, pausa, 5.115 palabras según auditoría; 85 celdas, 33 de código y ninguna salida persistida en el archivo inspeccionado. Conservar experimentos comprobados y ampliar la secuencia.

**Riesgo central:** Una muestra de procesos no representa contratos, valores adjudicados ni el universo SECOP; una API variable puede cambiar entre páginas.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **RAW inmutable, manifiesto de adquisición, informe de cobertura y perfil de calidad**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Corpus SECOP de 200 procesos, API de contratos como fuente distinta, diccionario y fecha de corte** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S01.01 · La misión de Compras Claras · 0–2 min (2 min)

**Propósito y contenido específico.** Distinguir una búsqueda de procesos de una estimación de gasto; explicar el grano proceso, contrato y entidad mediante un caso uno a muchos.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir entre preguntas que admiten los campos actuales y preguntas que requieren otra tabla.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz pregunta-campo-grano; no inferir montos sin fuente contractual.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.02 · Qué sabemos y qué no · 2–5 min (3 min)

**Propósito y contenido específico.** Diagnosticar conocimientos de tabla, API, memoria y código sin presuponer manejo de clústeres.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Clasificar cuatro escenarios de datos y comparar una decisión inicial con el cierre.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico estructurado; no calificar conocimiento previo.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.03 · Volumen no es un número mágico · 5–10 min (5 min)

**Propósito y contenido específico.** Comparar almacenamiento, memoria y tiempo de procesamiento; explicar por qué una carga grande depende del presupuesto de recursos.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Estimar bytes de 200 y de un millón de filas con un ancho explícito.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estimación dimensional; distinguir tamaño de archivo y memoria.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.04 · Las cinco V · 10–15 min (5 min)

**Propósito y contenido específico.** Relacionar volumen, velocidad, variedad, veracidad y valor con decisiones de arquitectura, no con eslóganes.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Mover dos controles de tasa de llegada y capacidad; identificar crecimiento de cola.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tasa y backlog calculados; una V no diagnostica todas.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.05 · Infraestructura local y nube · 15–20 min (5 min)

**Propósito y contenido específico.** Distinguir CPU, RAM, disco, red, escalamiento vertical y horizontal con una representación de trabajadores y almacenamiento.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Comparar dos configuraciones bajo un presupuesto de memoria y latencia común.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión de infraestructura; nube no implica distribución automática.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.06 · Estructurado, JSON y multimedia · 20–25 min (5 min)

**Propósito y contenido específico.** Enseñar esquema, tipos, nulos, arrays y binarios mediante representaciones del mismo proceso.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Clasificar campos y elegir formato para lectura, intercambio y almacenamiento.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de formatos con restricciones; extensión no garantiza contenido.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.07 · Grano y fuente real · 25–30 min (5 min)

**Propósito y contenido específico.** Mostrar identificadores, entidad, objeto y descripción de una muestra real; separar fuentes de procesos y contratos.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Inspeccionar 5 filas y seleccionar claves candidatas en el visor.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Perfil de columnas y unicidad; una clave candidata no es garantía.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.08 · Veracidad y duplicados · 30–35 min (5 min)

**Propósito y contenido específico.** Mostrar diferencias entre filas, identificadores únicos, faltantes, registros inválidos y registros repetidos por diseño.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Inyectar duplicados y nulos en una copia, nunca en RAW; variar sus cantidades.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos antes y después; ausencia de campo no equivale a cero.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.09 · Filtrar y agregar · 35–40 min (5 min)

**Propósito y contenido específico.** Explicar máscara booleana, agrupamiento y agregación con cinco filas; conectar el resultado con una decisión de priorización.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Predecir y calcular frecuencias por entidad; comparar con pandas.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo y denominador; no extrapolar la muestra a toda Colombia.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.10 · Pandas y memoria · 40–45 min (5 min)

**Propósito y contenido específico.** Distinguir Series, DataFrame, dtypes y memoria profunda; enseñar cuándo una conversión multiplica memoria.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Comparar enteros, objetos y categorías en la misma muestra.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Bytes de DataFrame; no presentarlos como pico RSS.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.11 · Texto no estructurado · 45–50 min (5 min)

**Propósito y contenido específico.** Enseñar normalización, tokenización y frecuencia; explicar pérdida de contexto y diferencias entre términos y palabras.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Cambiar normalización en dos objetos contractuales y comparar tokens.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tokens y frecuencias; una coincidencia no prueba relevancia.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.12 · HTTP y API Socrata · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar petición, respuesta, estado HTTP, parámetro, JSON y límites; mostrar el esquema de una respuesta sin exponer credenciales.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Construir una consulta de lectura con límite pequeño y comprobar estado y claves.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Respuesta o fixture etiquetado; no confundir fallo de red con cero registros.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.13 · Paginación determinista · 55–60 min (5 min)

**Propósito y contenido específico.** Enseñar limit, offset y orden total estable; construir un ejemplo de páginas con IDs consecutivos.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Simular páginas de 50 y salto de 40 frente a salto de 50.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura, duplicados y ausentes; el orden no congela cambios remotos.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.14 · Fragmentos y agregaciones · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar por qué una suma y un conteo se reducen por bloques pero una media simple de medias puede fallar.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Variar tamaño de fragmento y calcular media ponderada frente al resultado global.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Igualdad de suma y conteo; no mezclar promedios sin pesos.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.15 · Capacidad y experimento controlado · 65–70 min (5 min)

**Propósito y contenido específico.** Separar prueba sintética de datos reales; definir N, ancho, repetición, tiempo y medida de memoria antes de ejecutar.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Comparar lectura completa y por bloques bajo los mismos datos.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Medidas con ambiente y unidad; menor tamaño de bloque no garantiza menor tiempo.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S01.16 · Cuaderno: entorno y entrada · 80–87 min (7 min)

**Propósito y contenido específico.** Guiar desde Colab limpio hasta cargar corpus, validar columnas y reconocer el origen de cada archivo.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar preparación sin carga manual; verificar fecha, filas y hash.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Manifiesto inicial; fixture no es una descarga nueva.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.17 · Cuaderno: inspección y calidad · 87–95 min (8 min)

**Propósito y contenido específico.** Leer salidas de shape, dtypes, isna y duplicados; explicar parámetros visibles y criterio de identidad.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Modificar una selección de entidad y ejecutar controles sobre copia.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Perfil de calidad propio; RAW no se modifica.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.18 · Cuaderno: adquirir o recuperar · 95–102 min (7 min)

**Propósito y contenido específico.** Guiar construcción de URL, parámetros, timeout y control de respuesta; separar práctica remota de contingencia offline.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar una página o abrir snapshot identificado cuando la red falla.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado, fecha y hash; no declarar éxito remoto usando snapshot.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.19 · Cuaderno: recorrer páginas · 102–110 min (8 min)

**Propósito y contenido específico.** Explicar bucle, posición inicial, condición de parada y registro de claves visitadas.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Completar un hueco en el avance de página y contrastar IDs con fixture.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura exacta en datos congelados; registrar orden y límite.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.20 · Cuaderno: procesar fragmentos · 110–117 min (7 min)

**Propósito y contenido específico.** Desarrollar acumuladores, memoria por bloque y medición temporal con tamaño controlado.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Ejecutar escala segura de 10.000 o 100.000 filas sintéticas según presupuesto.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Igualdad frente a control pandas; ningún benchmark obligatorio gigante.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.21 · Cuaderno: exportar RAW · 117–125 min (8 min)

**Propósito y contenido específico.** Enseñar estructura de directorios, JSONL o CSV, metadatos y SHA-256; verificar relectura.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Guardar archivo, manifiesto y reabrir para comprobar identidad y conteo.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Artefacto reproducible; hash de bytes no acredita veracidad.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.22 · Reto de adquisición · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar una configuración nueva de página y tamaño que obligue a modificar el algoritmo sin reescribirlo.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Elegir parámetro y entregar cobertura, conteo y hash propios.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Configuración ejecutada y salida; no responder con ensayo libre.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.23 · Interpretación profesional · 130–135 min (5 min)

**Propósito y contenido específico.** Distinguir qué puede responder el corpus, qué requiere contratos y qué sesgos introduce el recorte.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir conclusión válida y limitación a partir del resultado propio.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos decisiones contextualizadas; no acusar irregularidad.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.24 · Relevo hacia arquitectura · 135–140 min (5 min)

**Propósito y contenido específico.** Convertir el manifiesto RAW en requisitos de volumen, latencia, calidad y consumo para S02.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Importar el manifiesto en una vista de contrato de entrada.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Compatibilidad verificada; ningún dato de ejemplo pasa por evidencia personal.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S01.25 · Cierre y recuperación · 140–150 min (10 min)

**Propósito y contenido específico.** Recapitular cinco V, grano, API, paginación y fragmentación; recuperar la decisión de apertura con evidencia.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver preguntas de salida sobre los resultados propios y recuperar un fallo frecuente.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Autochequeo y artefacto de relevo; conservar resultados faltantes como pendientes.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S01

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S01.08 Veracidad y duplicados | Inyectar duplicados y nulos en una copia, nunca en RAW; variar sus cantidades. | Conteos antes y después; ausencia de campo no equivale a cero. |
| E2 · S01.10 Pandas y memoria | Comparar enteros, objetos y categorías en la misma muestra. | Bytes de DataFrame; no presentarlos como pico RSS. |
| E3 · S01.13 Paginación determinista | Simular páginas de 50 y salto de 40 frente a salto de 50. | Cobertura, duplicados y ausentes; el orden no congela cambios remotos. |
| E4 · S01.20 Cuaderno: procesar fragmentos | Ejecutar escala segura de 10.000 o 100.000 filas sintéticas según presupuesto. | Igualdad frente a control pandas; ningún benchmark obligatorio gigante. |

**Producto mínimo:** RAW inmutable, manifiesto de adquisición, informe de cobertura y perfil de calidad. Antes de publicar, ejecutar la ruta base del cuaderno `sesion1_introducci_n.ipynb` en Colab; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Una muestra de procesos no representa contratos, valores adjudicados ni el universo SECOP; una API variable puede cambiar entre páginas.

# S02 · Arquitectura, requisitos y ciclo analítico

**Pregunta guía:** ¿Cómo diseñar una arquitectura que responda preguntas de contratación y no solo acumule tecnologías?

**Entrada:** RAW, manifiesto de S01 y requisitos de Compras Claras.

**Producto y relevo:** Contrato de datos, arquitectura justificada, diagrama y decisión versionada.

**Cuaderno canónico:** `Cuadernos/2_Sesion_Arquitectura_BPM_Ciclo_Analitico.ipynb`. **Entorno:** Colab.

**Estado de partida:** Ruta de cinco bloques y cuaderno existente; reutilizar sus secciones de BPM, Git y ciclo analítico; verificar decisión autónoma antes de elegir motores.

**Riesgo central:** Arquitectura basada en nombres de herramientas, estimaciones sin unidad y diagramas sin consumidor.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Contrato de datos, arquitectura justificada, diagrama y decisión versionada**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **RAW, manifiesto de S01 y requisitos de Compras Claras** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S02.01 · El problema de Laura · 0–2 min (2 min)

**Propósito y contenido específico.** Presentar necesidades incompatibles de consulta, actualización, trazabilidad y costo; distinguir usuario de sistema.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Seleccionar el objetivo prioritario entre casos con restricciones distintas.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Caso elegido y restricción; no iniciar nombrando motores.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.02 · Relevo RAW · 2–5 min (3 min)

**Propósito y contenido específico.** Leer manifiesto de S01 y mostrar qué campos, volumen, errores y fuentes condicionan el diseño.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Comparar manifiesto propio con referencia y detectar campo ausente.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de entrada comprobado; no inventar datos faltantes.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.03 · Proceso y BPM · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar evento, actividad, decisión, responsable y salida mediante un flujo de contratación simplificado.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Ordenar eventos y distinguir decisión humana de procesamiento automático.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama con decisión y estado final; BPM no es pipeline de datos.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.04 · BI y ciclo analítico · 10–15 min (5 min)

**Propósito y contenido específico.** Diferenciar adquirir, transformar, almacenar, analizar, servir y retroalimentar; mostrar preguntas descriptivas y predictivas.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Ubicar un producto de datos en cada fase y detectar ciclo incompleto.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa de ciclo; análisis no equivale a causalidad.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.05 · Requisitos funcionales · 15–20 min (5 min)

**Propósito y contenido específico.** Explicar qué pregunta o acción debe poder ejecutar un usuario y qué constituye una respuesta correcta.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Elegir tres consultas prioritarias con columnas y filtros necesarios.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz consulta-dato; no confundir interfaz con requisito.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.06 · Requisitos no funcionales · 20–25 min (5 min)

**Propósito y contenido específico.** Introducir latencia, rendimiento, disponibilidad, costo y frescura con unidades y umbrales ilustrativos.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Modificar frecuencia de ingesta y objetivo de latencia; observar incompatibilidad.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Restricciones medibles; no prometer SLA sin infraestructura.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.07 · Arquitectura por capas · 25–30 min (5 min)

**Propósito y contenido específico.** Distinguir origen, ingesta, RAW, transformación, almacenamiento de servicio y aplicación.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Mover una transformación y examinar qué capas consumen datos crudos o depurados.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama de interfaces; capa no es necesariamente una máquina.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.08 · Batch frente a eventos · 30–35 min (5 min)

**Propósito y contenido específico.** Comparar ejecución periódica con llegada de eventos mediante 6 registros con timestamps.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar intervalo de lote y calcular demora de disponibilidad.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Latencia aproximada; llegada no equivale a tiempo de evento.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.09 · SQL y NoSQL · 35–40 min (5 min)

**Propósito y contenido específico.** Explicar relaciones, documentos, acceso por clave, grafos y motores de texto como respuestas a consultas distintas.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Asociar patrones de consulta a estructuras y justificar alternativa descartada mediante opciones.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla patrón-motor; NoSQL no significa ausencia de esquema.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.10 · Costo y capacidad · 40–45 min (5 min)

**Propósito y contenido específico.** Derivar almacenamiento mensual de tasa, retención y réplicas; separar cómputo, red y almacenamiento.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar tamaño y retención bajo una tarifa ficticia explícita.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estimación reproducible, no precio comercial vigente.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.11 · Contratos de datos · 45–50 min (5 min)

**Propósito y contenido específico.** Definir campo, tipo, nulabilidad, identidad, unidad y versión; representar cambios compatibles e incompatibles.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Probar dos registros válidos y dos inválidos contra un contrato.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Errores específicos; esquema válido no garantiza semántica.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.12 · Trazabilidad y linaje · 50–55 min (5 min)

**Propósito y contenido específico.** Mostrar relación fuente-versión-transformación-salida; explicar diferencia entre identificador y hash.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Seguir un registro a través de dos transformaciones y localizar su origen.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Linaje navegable; hash no revela autor ni fecha por sí solo.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.13 · Git como historial · 55–60 min (5 min)

**Propósito y contenido específico.** Explicar repositorio, commit, diff, rama y pull request sin confundir GitHub con Git.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Comparar dos versiones de contrato y localizar un cambio de tipo.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diff y decisión; no crear ramas innecesarias.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.14 · Comparación de diseños · 60–65 min (5 min)

**Propósito y contenido específico.** Proponer diseño de un solo motor y diseño especializado; medir qué consultas y riesgos cubren.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Variar dos restricciones y observar cambio en matriz de decisión.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Alternativas con criterios; puntuación no es verdad universal.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.15 · Seguridad y fallas · 65–70 min (5 min)

**Propósito y contenido específico.** Introducir permisos mínimos, secretos, datos públicos y recuperación; mostrar caída de una fuente.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Eliminar un componente en un simulador de flujo y localizar dependencias.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan de contingencia; no exponer credenciales.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S02.16 · Cuaderno: importar requisitos · 80–87 min (7 min)

**Propósito y contenido específico.** Leer manifiesto de S01 o fixture y convertir observaciones a requisitos explícitos.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar carga y validar campos requeridos.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Requisitos con origen; marcar fallback.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.17 · Cuaderno: contrato ejecutable · 87–95 min (8 min)

**Propósito y contenido específico.** Enseñar comprobación de tipos y claves mediante código visible, sin esconder validación principal.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Cambiar un campo y ejecutar registros de prueba.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Lista de violaciones; no modificar registros RAW.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.18 · Cuaderno: simular carga · 95–102 min (7 min)

**Propósito y contenido específico.** Convertir tasas de llegada a volumen de datos y comparar dos frecuencias de ingesta.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar escenario con tasa distinta y unidad fija.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de capacidad; no inferir costos reales.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.19 · Cuaderno: matriz de decisión · 102–110 min (8 min)

**Propósito y contenido específico.** Construir criterios ponderados y separar restricciones duras de preferencias.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Modificar una ponderación y observar sensibilidad del ranking.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz versionada; no elegir por ranking si falla restricción dura.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.20 · Cuaderno: representar arquitectura · 110–117 min (7 min)

**Propósito y contenido específico.** Construir diagrama desde componentes y conexiones; demostrar cómo se enlazan entradas y salidas.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Agregar consumidor o eliminar un enlace y validar la coherencia.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama y contrato de interfaces.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.21 · Cuaderno: versionar artefacto · 117–125 min (8 min)

**Propósito y contenido específico.** Exportar JSON de arquitectura y contrato con versión; mostrar comparación contra estado anterior.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Guardar dos versiones y validar relectura.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Hash, versión y diff; sin datos de estudiantes.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.22 · Reto de diseño · 125–130 min (5 min)

**Propósito y contenido específico.** Cambiar objetivo de consulta o restricción y exigir revisión de dos decisiones previas.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Elegir arquitectura modificada y registrar alternativa descartada.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado contextualizado; no entregar solo un dibujo.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.23 · Revisión de consistencia · 130–135 min (5 min)

**Propósito y contenido específico.** Comprobar que cada requisito llega a un consumidor y cada componente responde a una necesidad.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Identificar dos componentes redundantes o faltantes mediante controles.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz cobertura-requisito; no usar tecnología por moda.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.24 · Relevo documental · 135–140 min (5 min)

**Propósito y contenido específico.** Seleccionar parte del contrato que S03 materializará como expediente documental.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar un documento candidato y consultas prioritarias.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada de S03 con campos y restricciones.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S02.25 · Cierre de arquitectura · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar decisión inicial y comparar con diseño final bajo las restricciones originales.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver una decisión estructurada sobre batch y arquitectura usando su cálculo.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama, contrato y traza; no evaluar con definiciones aisladas.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S02

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S02.08 Batch frente a eventos | Variar intervalo de lote y calcular demora de disponibilidad. | Latencia aproximada; llegada no equivale a tiempo de evento. |
| E2 · S02.10 Costo y capacidad | Variar tamaño y retención bajo una tarifa ficticia explícita. | Estimación reproducible, no precio comercial vigente. |
| E3 · S02.13 Git como historial | Comparar dos versiones de contrato y localizar un cambio de tipo. | Diff y decisión; no crear ramas innecesarias. |
| E4 · S02.20 Cuaderno: representar arquitectura | Agregar consumidor o eliminar un enlace y validar la coherencia. | Diagrama y contrato de interfaces. |

**Producto mínimo:** Contrato de datos, arquitectura justificada, diagrama y decisión versionada. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/2_Sesion_Arquitectura_BPM_Ciclo_Analitico.ipynb` en Colab; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Arquitectura basada en nombres de herramientas, estimaciones sin unidad y diagramas sin consumidor.

# S03 · MongoDB: modelado documental y consultas

**Pregunta guía:** ¿Cómo recuperar expedientes flexibles sin perder identidad ni eficiencia de consulta?

**Entrada:** Contrato y patrones de consulta de S02; procesos SECOP congelados.

**Producto y relevo:** Colección documental, consultas reproducibles y evidencia de plan de ejecución.

**Cuaderno canónico:** `Cuadernos/3_MongoDB_Documental.ipynb`. **Entorno:** Colab y motor MongoDB verificado.

**Estado de partida:** Cuaderno de consulta profunda conservado; auditoría pide ejecución real de explain, no simulación de un índice.

**Riesgo central:** Confundir JSON y BSON, llamar índice a una estructura Python o inferir aceleración desde una colección minúscula.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Colección documental, consultas reproducibles y evidencia de plan de ejecución**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y motor MongoDB verificado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Contrato y patrones de consulta de S02; procesos SECOP congelados** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S03.01 · El expediente como unidad · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar datos de proceso y activos asociados que cambian de estructura; contrastar consulta de expediente con análisis transversal.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir la unidad documental y campos que necesitan identidad.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Modelo candidato; no replicar información sin necesidad.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.02 · Preconcepciones de bases · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar contrato y consultar diferencias entre fila, tabla, colección y documento.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Asociar ejemplos y detectar una referencia faltante.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico contextual; no presuponer sintaxis MongoDB.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.03 · JSON y BSON · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar pares clave-valor, tipos nativos, arrays, documentos anidados y representación binaria.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Comparar fechas, números y nulos de dos representaciones.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tipo observado; BSON no es texto JSON.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.04 · Grano e identidad · 10–15 min (5 min)

**Propósito y contenido específico.** Distinguir clave del negocio, identificador interno y duplicado semántico.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Diseñar id determinista para dos versiones de un proceso.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Regla de identidad; ObjectId no sustituye clave contractual.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.05 · Embebido o referencia · 15–20 min (5 min)

**Propósito y contenido específico.** Comparar lectura conjunta, cardinalidad, crecimiento del documento y actualización redundante.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Variar número de activos por expediente y elegir representación.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión por patrón de acceso; no hay diseño universal.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.06 · Esquema flexible y validación · 20–25 min (5 min)

**Propósito y contenido específico.** Introducir campos opcionales, validadores, tipos y migración; explicar por qué flexibilidad requiere contrato.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Detectar un documento con monto textual y otro sin fecha.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado de validación; ausencia no equivale a null.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.07 · CRUD desde cero · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar insertar, consultar, actualizar y eliminar con operación sobre colección de práctica aislada.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Predecir estado tras cuatro operaciones sobre dos documentos.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado antes/después; no borrar colección ajena.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.08 · Predicados y proyección · 30–35 min (5 min)

**Propósito y contenido específico.** Enseñar igualdad, rango, operadores lógicos, selección de campos y orden.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar filtro y proyección sobre una muestra y verificar resultado manual.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs esperados; filtrar no es proyectar.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.09 · Arrays y documentos anidados · 35–40 min (5 min)

**Propósito y contenido específico.** Explicar dot notation y condiciones que deben coincidir en el mismo elemento.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Comparar dos predicados sobre activos con valores cruzados.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Coincidencias; distinguir semántica de elemMatch.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.10 · Agregación por etapas · 40–45 min (5 min)

**Propósito y contenido específico.** Representar match, project, unwind, group y sort como flujo de documentos.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Calcular manualmente salida tras cada etapa y comparar motor.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cardinalidad intermedia; unwind cambia grano.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.11 · Índice y acceso · 45–50 min (5 min)

**Propósito y contenido específico.** Mostrar índice ordenado, búsqueda por clave y costo de mantenimiento; distinguir índice simple y compuesto.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Simular búsqueda de una clave y comparar inspecciones en conjunto pequeño.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Pasos didácticos; no llamarlos métricas de MongoDB.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.12 · Explain real · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar plan ganador, documentos examinados, claves examinadas y filas devueltas.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Comparar consulta idéntica antes y después de índice en colección controlada.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan real o pendiente; no asegurar menor tiempo por un solo ensayo.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.13 · Orden de índice compuesto · 55–60 min (5 min)

**Propósito y contenido específico.** Enseñar prefijo, igualdad y rango con patrones de consulta especificados.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Variar orden de campos y comparar cobertura prevista y plan cuando se ejecute.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Planes y consulta; índice no siempre elegido.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.14 · Actualización e idempotencia · 60–65 min (5 min)

**Propósito y contenido específico.** Distinguir insert, update, upsert y clave única; representar reintento después de fallo.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Ejecutar misma carga dos veces con identidad estable.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo constante; idempotencia depende de operación y clave.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.15 · Consistencia y concurrencia · 65–70 min (5 min)

**Propósito y contenido específico.** Explicar modificación simultánea, atomicidad documental y necesidad de controles entre documentos.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Predecir dos escrituras concurrentes en un ejemplo controlado.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado posible; no extrapolar garantía a múltiples documentos.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S03.16 · Cuaderno: conectar · 80–87 min (7 min)

**Propósito y contenido específico.** Mostrar URI segura, cliente, ping y selección de colección aislada.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar preflight con versión y permisos; usar fixture si conexión falla.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ping real o modo conceptual explícito.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.17 · Cuaderno: cargar documentos · 87–95 min (8 min)

**Propósito y contenido específico.** Convertir registros del contrato a documentos y crear identidad con validación.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar carga y contar claves distintas; repetir sin duplicar.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Colección o fixture, conteos y modo.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.18 · Cuaderno: consultar · 95–102 min (7 min)

**Propósito y contenido específico.** Escribir predicados, proyección y límite en código visible; asociar cada parámetro con pregunta.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Completar condición de entidad o rango y comparar IDs.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado propio; límite no representa totalidad.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.19 · Cuaderno: agregar · 102–110 min (8 min)

**Propósito y contenido específico.** Construir pipeline etapa por etapa e inspeccionar tablas intermedias.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Cambiar agrupación y contrastar conteo contra control independiente.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Agregación equivalente; explicitar tratamiento de nulos.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.20 · Cuaderno: medir índice · 110–117 min (7 min)

**Propósito y contenido específico.** Preparar datos equivalentes, ejecutar explain y registrar plan antes y después.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Crear índice autorizado y comparar examinados y devueltos.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** JSON de explain; si falta motor no usar mock como evidencia.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.21 · Cuaderno: exportar expediente · 117–125 min (8 min)

**Propósito y contenido específico.** Exportar resultado de consulta, esquema, versión e identidad sin credenciales.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y comprobar contrato del expediente.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Documentos compatibles y manifestación de procedencia.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.22 · Reto documental · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar una consulta nueva que combine un campo anidado y restricción de cardinalidad.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar predicado o índice y validar IDs en muestra controlada.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Consulta, resultados y alternativa; no texto libre.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.23 · Error clinic · 130–135 min (5 min)

**Propósito y contenido específico.** Contrastar error de autenticación, filtro vacío, tipo incorrecto y colección no seleccionada.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir diagnóstico correcto usando salida de su ejecución.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Código de error y ruta de recuperación.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.24 · Relevo Atlas · 135–140 min (5 min)

**Propósito y contenido específico.** Preparar colección y consulta reproducible para persistencia gestionada de S04.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Verificar campos y exportar configuración sin URI privada.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de expedientes; separar entorno de datos.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S03.25 · Cierre MongoDB · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar decisión de embebido frente a referencia y explicar qué indica explain.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Seleccionar modelo y límite con evidencia de su consulta.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Autochequeo y expediente; no confundir plan con tiempo real.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S03

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S03.08 Predicados y proyección | Variar filtro y proyección sobre una muestra y verificar resultado manual. | IDs esperados; filtrar no es proyectar. |
| E2 · S03.10 Agregación por etapas | Calcular manualmente salida tras cada etapa y comparar motor. | Cardinalidad intermedia; unwind cambia grano. |
| E3 · S03.13 Orden de índice compuesto | Variar orden de campos y comparar cobertura prevista y plan cuando se ejecute. | Planes y consulta; índice no siempre elegido. |
| E4 · S03.20 Cuaderno: medir índice | Crear índice autorizado y comparar examinados y devueltos. | JSON de explain; si falta motor no usar mock como evidencia. |

**Producto mínimo:** Colección documental, consultas reproducibles y evidencia de plan de ejecución. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/3_MongoDB_Documental.ipynb` en Colab y motor MongoDB verificado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir JSON y BSON, llamar índice a una estructura Python o inferir aceleración desde una colección minúscula.

# S04 · Atlas, persistencia, replicación y bandeja

**Pregunta guía:** ¿Qué cambia cuando un expediente debe persistir y ser recuperable mediante un servicio gestionado?

**Entrada:** Expediente documental y consultas de S03.

**Producto y relevo:** Bandeja consultable y diagnóstico de persistencia, conectividad y consistencia.

**Cuaderno canónico:** `Cuadernos/4_Atlas_Cassandra_Laura.ipynb`. **Entorno:** Colab y Atlas con plan verificado.

**Estado de partida:** La práctica de Atlas y la ilustración de réplica existen; faltan pruebas limpias de acceso gratuito y recuperación.

**Riesgo central:** Confundir réplica con copia de seguridad, simulación con fallo real y permiso de lectura con permiso administrativo.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Bandeja consultable y diagnóstico de persistencia, conectividad y consistencia**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y Atlas con plan verificado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Expediente documental y consultas de S03** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S04.01 · La bandeja persistente · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear dos usuarios que deben consultar la misma información después de reiniciar su entorno.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir qué datos deben persistir y cuáles son temporales.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Requisitos de persistencia; memoria no sustituye almacenamiento.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.02 · Revisión de expedientes · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar documento y consulta de S03; comprobar contrato antes de cargar un servicio.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Seleccionar versión compatible y detectar inconsistencia de identidad.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de entrada; fixture identificado.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.03 · Cliente y servidor · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar conexión, autenticación, DNS, TLS y petición a un motor remoto mediante un diagrama.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Asociar cuatro fallos a etapas de conexión.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa de errores; no imprimir URI.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.04 · Servicio gestionado · 10–15 min (5 min)

**Propósito y contenido específico.** Distinguir administración de infraestructura, motor, proyecto, clúster y base de datos.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Seleccionar tareas del proveedor y tareas del usuario.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Responsabilidades; servicio gestionado no garantiza costo cero.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.05 · Red y acceso · 15–20 min (5 min)

**Propósito y contenido específico.** Introducir allowlist, autenticación y mínimo privilegio; evitar abrir acceso universal sin necesidad.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Interpretar dos errores simulados de autenticación y red.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico y remedio seguro; no divulgar secreto.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.06 · Persistencia y reinicio · 20–25 min (5 min)

**Propósito y contenido específico.** Mostrar diferencias entre estado de cuaderno, almacenamiento local y base remota.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Predecir qué sobrevive al reinicio y comprobar una lectura.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Identidad recuperada; no confundir caché con persistencia.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.07 · Réplicas y disponibilidad · 25–30 min (5 min)

**Propósito y contenido específico.** Representar primario, secundarios, replicación y elección sin afirmar topología real del plan gratuito.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Variar demora de réplica y observar visibilidad de escritura.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Simulación etiquetada; no atribuir nodos físicos.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.08 · Consistencia de lectura · 30–35 min (5 min)

**Propósito y contenido específico.** Explicar lectura reciente frente a lectura potencialmente atrasada con una línea temporal.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Comparar dos políticas conceptuales bajo retraso de réplica.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Versiones visibles; consistencia no equivale a durabilidad.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.09 · Fragmentación frente a réplica · 35–40 min (5 min)

**Propósito y contenido específico.** Distinguir dividir datos entre particiones y copiar datos para tolerancia.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Variar claves y réplicas en una ilustración y comparar almacenamiento.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa conceptual; no afirmar sharding activo en Atlas gratuito.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.10 · Vista y consulta · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar vista lógica, filtro, proyección y persistencia de resultado derivado.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Comparar consulta base y vista en un escenario con cambio de datos.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado esperado; vista no siempre materializada.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.11 · Datos faltantes · 45–50 min (5 min)

**Propósito y contenido específico.** Distinguir campo ausente, null y cadena vacía; evaluar qué proceso entra a la bandeja.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Cambiar regla de completitud y comparar filas incluidas.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos por estado; no imputar sin justificación.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.12 · Bandeja por prioridades · 50–55 min (5 min)

**Propósito y contenido específico.** Diseñar criterios simples y trazables de revisión sin presentarlos como fraude.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Modificar umbral de faltantes y comprobar ranking o categorías.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Regla y conteo; prioridad no es acusación.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.13 · Carga repetible · 55–60 min (5 min)

**Propósito y contenido específico.** Explicar upsert, identidad y actualización de versión; mostrar por qué repetir una carga no debe duplicar.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Simular fallo entre dos lotes y reintentar uno.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Claves y versiones; no borrar originales.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.14 · Prueba de recuperación · 60–65 min (5 min)

**Propósito y contenido específico.** Separar reinicio cliente, fallo de red y pérdida de servidor; enseñar qué prueba es viable sin administrar nodos.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Desconectar conceptualmente cliente y ensayar reconexión autorizada.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Registro de reconexión; no llamar failover a un ping.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.15 · Comparación de alternativas · 65–70 min (5 min)

**Propósito y contenido específico.** Contrastar servicio remoto con motor local y archivo bajo requerimientos de continuidad.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Variar latencia y necesidad de usuarios concurrentes.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión condicionada; no prometer SLA.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S04.16 · Cuaderno: preflight Atlas · 80–87 min (7 min)

**Propósito y contenido específico.** Mostrar preparación segura, ping, versión y consulta pequeña; verificar capacidad del plan actual antes de clase.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar conexión en entorno limpio sin imprimir secreto.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado real; contingencia si cuenta no disponible.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.17 · Cuaderno: persistir muestra · 87–95 min (8 min)

**Propósito y contenido específico.** Cargar documentos con clave estable y verificar conteo y hash de datos seleccionados.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Repetir carga y leer desde cliente nuevo.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Persistencia observada; no declarar replicación medida.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.18 · Cuaderno: consultas de bandeja · 95–102 min (7 min)

**Propósito y contenido específico.** Construir filtro, proyección, orden y paginación para vista de procesos pendientes.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Cambiar criterio de completitud y observar IDs.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Bandeja propia; límites explícitos.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.19 · Cuaderno: vista o alternativa · 102–110 min (8 min)

**Propósito y contenido específico.** Crear vista si el permiso lo permite; si no, ejecutar pipeline equivalente de lectura.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Comparar salida de vista y consulta base.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Equivalencia o limitación de permiso documentada.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.20 · Cuaderno: reconectar · 110–117 min (7 min)

**Propósito y contenido específico.** Enseñar cierre de cliente y reconexión controlada; evitar operaciones destructivas de infraestructura.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Ejecutar consulta tras reconexión y comparar estado.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia de recuperación del cliente, no prueba de réplica.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.21 · Cuaderno: exportar bandeja · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar criterios, IDs, versión y procedencia para próximo diseño orientado a consulta.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y validar contrato.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Bandeja exportada; ninguna credencial persistida.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.22 · Reto de persistencia · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar un cambio de criterio y una segunda ejecución que debe recuperar el mismo expediente.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar filtro y demostrar persistencia con traza.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultados propios y modo de conexión.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.23 · Diagnóstico de fallos · 130–135 min (5 min)

**Propósito y contenido específico.** Mostrar señales de timeout, permiso y colección vacía; diferenciar fallo de consulta de fuente vacía.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir recuperación contextual basada en salida real o fixture etiquetado.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Código de error y estado final.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.24 · Relevo Cassandra · 135–140 min (5 min)

**Propósito y contenido específico.** Extraer dos consultas por entidad y estado que serán patrones de acceso en S05.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Definir clave candidata y campos necesarios, sin diseñar Cassandra todavía.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Consultas con grano y cardinalidad.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S04.25 · Cierre servicio gestionado · 140–150 min (10 min)

**Propósito y contenido específico.** Contrastar hipótesis inicial y evidencia de persistencia; recordar límites del plan.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Responder controles sobre réplica, fragmentación y conexión con su bandeja.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Artefacto y autochequeo; no declarar alta disponibilidad probada.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S04

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S04.08 Consistencia de lectura | Comparar dos políticas conceptuales bajo retraso de réplica. | Versiones visibles; consistencia no equivale a durabilidad. |
| E2 · S04.10 Vista y consulta | Comparar consulta base y vista en un escenario con cambio de datos. | Resultado esperado; vista no siempre materializada. |
| E3 · S04.13 Carga repetible | Simular fallo entre dos lotes y reintentar uno. | Claves y versiones; no borrar originales. |
| E4 · S04.20 Cuaderno: reconectar | Ejecutar consulta tras reconexión y comparar estado. | Evidencia de recuperación del cliente, no prueba de réplica. |

**Producto mínimo:** Bandeja consultable y diagnóstico de persistencia, conectividad y consistencia. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/4_Atlas_Cassandra_Laura.ipynb` en Colab y Atlas con plan verificado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir réplica con copia de seguridad, simulación con fallo real y permiso de lectura con permiso administrativo.

# S05 · Cassandra y modelado orientado a consulta

**Pregunta guía:** ¿Cómo organizar registros para servir consultas previsibles sin depender de recorridos globales?

**Entrada:** Bandeja y patrones de acceso de S04.

**Producto y relevo:** Dos tablas operacionales por consulta, perfil de distribución y evidencia CQL.

**Cuaderno canónico:** `Cuadernos/5_Atlas_Cassandra_Query_First.ipynb`. **Entorno:** Colab y Cassandra/Astra sujeto a comprobación.

**Estado de partida:** Conservar ejercicios query-first y datos de juguete; verificar dos tablas reales y distribución lógica de claves.

**Riesgo central:** Confundir partición lógica y nodo físico; asumir que una consulta permitida es eficiente o usar ALLOW FILTERING como solución general.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Dos tablas operacionales por consulta, perfil de distribución y evidencia CQL**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y Cassandra/Astra sujeto a comprobación de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Bandeja y patrones de acceso de S04** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S05.01 · Dos consultas reales · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear revisión por entidad y por período/estado; explicar por qué acceso previsible cambia el modelo.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir patrones prioritarios y sus parámetros de igualdad y rango.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos contratos de consulta; no comenzar con normalización.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.02 · Recuperar la bandeja · 2–5 min (3 min)

**Propósito y contenido específico.** Inspeccionar claves, estados y fechas provenientes de S04.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Contar entidades distintas y detectar una clave demasiado frecuente.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Perfil inicial; no representar carga física.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.03 · Modelo wide-column · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar keyspace, tabla, fila, columna y clave primaria compuesta; contrastar colección documental.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Representar un mismo proceso en dos tablas de consulta.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos representaciones; duplicación deliberada no es error automático.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.04 · Clave de partición · 10–15 min (5 min)

**Propósito y contenido específico.** Mostrar cómo una clave identifica un grupo de filas y cómo hashing distribuye particiones conceptualmente.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Variar clave entidad frente a entidad-mes y observar tamaños.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Distribución lógica; no inferir token o nodo real.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.05 · Clustering columns · 15–20 min (5 min)

**Propósito y contenido específico.** Explicar orden dentro de partición y restricciones de consultas por prefijo.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Ordenar cinco procesos de una entidad por fecha e ID.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Orden previsto; clustering no significa clúster.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.06 · Desnormalización · 20–25 min (5 min)

**Propósito y contenido específico.** Mostrar copia de información para consultas diferentes y costo de mantenerlas actualizadas.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Cambiar un estado y localizar qué tablas requieren escritura.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa de escrituras; no ocultar consistencia.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.07 · CQL desde cero · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar CREATE TABLE, INSERT y SELECT con tipos y claves de un ejemplo pequeño.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Predecir qué consulta usa clave completa o parcial válida.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Sintaxis y salida; SQL similar no implica mismas capacidades.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.08 · Consulta por igualdad · 30–35 min (5 min)

**Propósito y contenido específico.** Mostrar acceso por clave de partición y proyección de columnas.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar entidad y comparar IDs con referencia pandas.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conjunto equivalente; no escanear toda tabla.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.09 · Consulta por rango · 35–40 min (5 min)

**Propósito y contenido específico.** Introducir intervalo sobre clustering con clave de partición conocida.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Variar rango de fechas y comprobar límites inclusivos.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs y límites; no permitir rango arbitrario sin diseño.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.10 · Tamaño de particiones · 40–45 min (5 min)

**Propósito y contenido específico.** Calcular filas y bytes estimados por clave; explicar particiones grandes y calientes.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Modificar estrategia de bucket temporal y comparar máximos.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Máximo y distribución; estimación no es medida del nodo.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.11 · Concentración y skew · 45–50 min (5 min)

**Propósito y contenido específico.** Distinguir desigualdad de frecuencia y demanda de consulta con histogramas.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Inyectar una entidad frecuente en copia y comparar p50, p95 y máximo.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Histograma; frecuencia no mide tráfico real.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.12 · Replicación conceptual · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar factor de réplica, consistencia de lectura/escritura y disponibilidad bajo supuestos.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Variar RF, R y W en ejemplos de quórum y observar límites.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Relación conceptual; no asumir configuración administrada.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.13 · Escritura repetida · 55–60 min (5 min)

**Propósito y contenido específico.** Explicar upsert por clave primaria, timestamps y eliminación lógica a nivel conceptual.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Ejecutar dos escrituras a misma clave y comparar estado.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo y versión; no confundir timestamp con fecha del negocio.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.14 · Patrones malos · 60–65 min (5 min)

**Propósito y contenido específico.** Contrastar consultas sin clave, filtrado posterior y tabla diseñada para la pregunta.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Cambiar filtro y elegir rediseño de tabla en lugar de escaneo indiscriminado.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión con patrón de consulta; no usar ALLOW FILTERING por defecto.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.15 · Comparación MongoDB/Cassandra · 65–70 min (5 min)

**Propósito y contenido específico.** Comparar flexibilidad, acceso por clave, duplicación y necesidades de consulta del caso.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Elegir motor para dos preguntas distintas y registrar criterio.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz de decisiones; no ranking universal.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S05.16 · Cuaderno: preflight CQL · 80–87 min (7 min)

**Propósito y contenido específico.** Verificar acceso al motor, keyspace permitido, versión y cuota; no revelar token.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar consulta de estado o contingencia local identificada.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Acceso real o pendiente; no simular Astra.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.17 · Cuaderno: tabla entidad · 87–95 min (8 min)

**Propósito y contenido específico.** Crear o usar tabla aislada con partición y clustering documentados.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Cargar muestra y consultar entidad con rango.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** CQL, IDs y control; no borrar recursos ajenos.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.18 · Cuaderno: tabla estado-período · 95–102 min (7 min)

**Propósito y contenido específico.** Diseñar segunda tabla con clave adecuada a la otra consulta.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Cargar los mismos procesos y comparar salida con referencia.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Segunda consulta y equivalencia; duplicación esperada.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.19 · Cuaderno: medir concentración · 102–110 min (8 min)

**Propósito y contenido específico.** Calcular perfil lógico de tamaños de partición con datos congelados.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Cambiar bucket y medir máximo, número de claves y desbalance.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla lógica; no declarar latencia de Cassandra a partir de pandas.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.20 · Cuaderno: reejecución · 110–117 min (7 min)

**Propósito y contenido específico.** Probar segunda carga de la misma identidad y actualización de un campo.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Verificar que las dos tablas quedan coherentes en el escenario.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos e IDs; no afirmar transacción global.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.21 · Cuaderno: exportar acceso · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar consultas CQL, reglas de clave y resultados con fuente.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer catálogo de patrones sin credenciales.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato operativo de consulta.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.22 · Reto query-first · 125–130 min (5 min)

**Propósito y contenido específico.** Proponer consulta nueva por período y entidad y pedir elección de partición.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar definición en entorno de práctica o modelo lógico según disponibilidad.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diseño y resultado; distinguir modelo de ejecución real.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.23 · Interpretación de concentración · 130–135 min (5 min)

**Propósito y contenido específico.** Explicar por qué una entidad con muchas filas puede generar desbalance, pero requiere medir demanda.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir escenario de riesgo y dato adicional necesario.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión estructurada basada en máximo propio.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.24 · Relevo grafo · 135–140 min (5 min)

**Propósito y contenido específico.** Identificar relaciones entre entidad, proceso, proveedor cuando la fuente lo permita.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar nodos candidatos y claves sin inventar vínculos.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Identidades y relaciones verificables para S06.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S05.25 · Cierre Cassandra · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar consulta inicial y verificar si ambas tablas contestan con claves explícitas.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles sobre partición, clustering y consistencia.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos patrones, perfil y traza; no calificar definiciones solas.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S05

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S05.08 Consulta por igualdad | Variar entidad y comparar IDs con referencia pandas. | Conjunto equivalente; no escanear toda tabla. |
| E2 · S05.10 Tamaño de particiones | Modificar estrategia de bucket temporal y comparar máximos. | Máximo y distribución; estimación no es medida del nodo. |
| E3 · S05.13 Escritura repetida | Ejecutar dos escrituras a misma clave y comparar estado. | Conteo y versión; no confundir timestamp con fecha del negocio. |
| E4 · S05.20 Cuaderno: reejecución | Verificar que las dos tablas quedan coherentes en el escenario. | Conteos e IDs; no afirmar transacción global. |

**Producto mínimo:** Dos tablas operacionales por consulta, perfil de distribución y evidencia CQL. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/5_Atlas_Cassandra_Query_First.ipynb` en Colab y Cassandra/Astra sujeto a comprobación; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir partición lógica y nodo físico; asumir que una consulta permitida es eficiente o usar ALLOW FILTERING como solución general.

# S06 · Grafos y contexto relacional con Neo4j

**Pregunta guía:** ¿Cómo explorar relaciones entre procesos, entidades y otros actores sin duplicar identidades ni inferir vínculos inexistentes?

**Entrada:** Identidades y relaciones de S05 y fuentes autorizadas.

**Producto y relevo:** Grafo de contexto, consultas Cypher y validación de relaciones.

**Cuaderno canónico:** `Cuadernos/6_Neo4j_Contexto_Relacional.ipynb`. **Entorno:** Colab y Neo4j/Aura verificado.

**Estado de partida:** Conservar ruta esencial, anexos y contraste pandas; reducir redundancia y comprobar consultas reales.

**Riesgo central:** Multiplicar nodos por variantes de nombre, crear vínculos sin fuente o considerar centralidad evidencia de corrupción.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Grafo de contexto, consultas Cypher y validación de relaciones**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y Neo4j/Aura verificado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Identidades y relaciones de S05 y fuentes autorizadas** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S06.01 · Del expediente a la red · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar una pregunta que necesita recorrer relaciones en vez de abrir cada documento.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir pregunta de vecindad frente a búsqueda textual.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Pregunta y fuente de aristas; no asumir proveedores ausentes.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.02 · Identidades de entrada · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar claves de entidades y procesos y distinguir nombre visible de identificador.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Detectar dos variantes de nombre y un caso ambiguo.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Regla de identidad; homónimos no se fusionan automáticamente.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.03 · Nodos, aristas y propiedades · 5–10 min (5 min)

**Propósito y contenido específico.** Definir grafo dirigido y no dirigido, etiqueta, relación y atributos con cuatro nodos.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Construir un grafo pequeño desde una tabla de relaciones.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo de nodos y aristas; dirección tiene significado.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.04 · Modelo property graph · 10–15 min (5 min)

**Propósito y contenido específico.** Explicar propiedades en nodo o relación, cardinalidad y etiquetas.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Elegir ubicación de fecha y origen de una relación.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Modelo y grano; atributo de arista no se duplica sin criterio.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.05 · Trayectorias y vecindad · 15–20 min (5 min)

**Propósito y contenido específico.** Definir salto, vecino, camino y longitud; distinguir camino de relación directa.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Contar vecinos a uno y dos saltos en un grafo didáctico.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conjuntos de IDs; dos saltos no prueban asociación directa.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.06 · Grado y centralidad · 20–25 min (5 min)

**Propósito y contenido específico.** Explicar grado de entrada/salida y medidas de red como descripción estructural.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Agregar una arista y comparar grados de cuatro nodos.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Grados calculados; centralidad no prueba importancia causal.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.07 · Cypher desde cero · 25–30 min (5 min)

**Propósito y contenido específico.** Enseñar patrones de nodos, flechas, variables, MATCH y RETURN.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Traducir consulta verbal a patrón sobre el grafo didáctico.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Patrón e IDs esperados; variable no es etiqueta.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.08 · Filtros y proyección · 30–35 min (5 min)

**Propósito y contenido específico.** Explicar WHERE, propiedades y selección de resultados.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar filtro de fecha y comparar caminos encontrados.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado y filtros; no omitir límites de fuente.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.09 · Caminos de longitud variable · 35–40 min (5 min)

**Propósito y contenido específico.** Representar expansión por saltos y crecimiento combinatorio; introducir límites de longitud.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Variar máximo de saltos y observar número de caminos.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cantidad de caminos; no confundir caminos con nodos únicos.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.10 · Agregación y DISTINCT · 40–45 min (5 min)

**Propósito y contenido específico.** Mostrar duplicación de resultados por trayectorias alternativas y agregación por nodo.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Comparar count de caminos y count distinct de entidades.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ambos conteos; grano del resultado explícito.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.11 · MERGE e identidad · 45–50 min (5 min)

**Propósito y contenido específico.** Explicar creación frente a coincidencia y restricciones únicas; distinguir MERGE de deduplicación semántica.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Repetir carga de tres relaciones y comparar nodos y aristas.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos estables bajo claves definidas.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.12 · Importación de datos · 50–55 min (5 min)

**Propósito y contenido específico.** Construir lista de nodos y relaciones con columnas origen, destino y procedencia.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Detectar arista cuyo nodo no existe y decidir rechazo o corrección.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Reporte de integridad referencial; no fabricar nodo.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.13 · Comparación relacional · 55–60 min (5 min)

**Propósito y contenido específico.** Resolver la misma consulta con join pandas y patrón Cypher; examinar cardinalidad.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Variar una arista y contrastar ambos resultados.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Igualdad de IDs; tiempo no comparable sin condiciones.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.14 · Índices y planes · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar búsqueda inicial de nodos y expansión de vecinos; mostrar plan cuando motor disponible.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Comparar patrón con filtro inicial por identidad y sin filtro.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan observado; no inferir tiempo desde dibujo.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.15 · Sesgos de la red · 65–70 min (5 min)

**Propósito y contenido específico.** Mostrar cómo muestreo y faltantes cambian grado y componentes; distinguir ausencia de arista y evidencia negativa.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Retirar una arista en copia y observar cambio de ranking.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Sensibilidad; no tratar red parcial como universo.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S06.16 · Cuaderno: conectar al grafo · 80–87 min (7 min)

**Propósito y contenido específico.** Validar credenciales seguras, versión, conectividad y permisos de escritura aislada.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar lectura mínima en motor o ruta de referencia.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Modo y ping; no declarar Aura sin conexión.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.17 · Cuaderno: preparar nodos · 87–95 min (8 min)

**Propósito y contenido específico.** Transformar entradas en nodos únicos y aristas con procedencia y claves.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar verificación de IDs y relaciones huérfanas.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tablas de carga; rechazos explícitos.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.18 · Cuaderno: cargar idempotente · 95–102 min (7 min)

**Propósito y contenido específico.** Crear restricciones autorizadas y MERGE con propiedades correctas.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar carga dos veces y verificar conteos.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado de grafo; no eliminar toda base.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.19 · Cuaderno: consultar vecindad · 102–110 min (8 min)

**Propósito y contenido específico.** Construir MATCH por entidad y relaciones de uno o dos saltos.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Cambiar nodo inicial y comparar con control independiente.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs y aristas recuperados.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.20 · Cuaderno: medir y contrastar · 110–117 min (7 min)

**Propósito y contenido específico.** Calcular grado y resultados DISTINCT; contrastar Cypher con tabla de aristas.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Variar máximo de salto y comprobar diferencias de cardinalidad.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultados equivalentes donde corresponde.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.21 · Cuaderno: exportar contexto · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar subgrafo de consulta y manifiesto con procedencia.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y validar extremos de las aristas.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contexto de expediente para búsqueda.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.22 · Reto relacional · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar una nueva pregunta de dos saltos y pedir limitar trayectoria y filtro.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar Cypher y verificar con datos propios.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Consulta y resultado; no responder con conclusión causal.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.23 · Lectura del grafo · 130–135 min (5 min)

**Propósito y contenido específico.** Explicar visualmente leyenda, dirección, propiedades y caminos; escoger límite de interpretación.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar nodo y comparar relación directa con recorrido.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión contextualizada; evitar inferencia de fraude.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.24 · Relevo búsqueda lexical · 135–140 min (5 min)

**Propósito y contenido específico.** Extraer campos textuales de expedientes y contexto sin perder identificador.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar documentos y lista de preguntas de búsqueda.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Corpus con grano y procedencia para S07.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S06.25 · Cierre grafos · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar pregunta inicial y contrastar documento, tabla y grafo como estructuras complementarias.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles basados en un resultado de caminos propio.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Subgrafo, trazabilidad y diagnóstico.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S06

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S06.08 Filtros y proyección | Variar filtro de fecha y comparar caminos encontrados. | Resultado y filtros; no omitir límites de fuente. |
| E2 · S06.10 Agregación y DISTINCT | Comparar count de caminos y count distinct de entidades. | Ambos conteos; grano del resultado explícito. |
| E3 · S06.13 Comparación relacional | Variar una arista y contrastar ambos resultados. | Igualdad de IDs; tiempo no comparable sin condiciones. |
| E4 · S06.20 Cuaderno: medir y contrastar | Variar máximo de salto y comprobar diferencias de cardinalidad. | Resultados equivalentes donde corresponde. |

**Producto mínimo:** Grafo de contexto, consultas Cypher y validación de relaciones. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/6_Neo4j_Contexto_Relacional.ipynb` en Colab y Neo4j/Aura verificado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Multiplicar nodos por variantes de nombre, crear vínculos sin fuente o considerar centralidad evidencia de corrupción.

# S07 · Búsqueda lexical, BM25 y Elasticsearch

**Pregunta guía:** ¿Cómo recuperar documentos relevantes por palabras y demostrar por qué cambia el ranking?

**Entrada:** Documentos y campos textuales de S06; consultas juzgadas.

**Producto y relevo:** Buscador lexical, resultados top-k y evaluación de ranking.

**Cuaderno canónico:** `Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb`. **Entorno:** Colab y Elasticsearch comprobado.

**Estado de partida:** Conservar presentación BM25 y explorador; añadir juicios múltiples, comparación de analizador real y evidencias de motor.

**Riesgo central:** Confundir coincidencia con relevancia; tratar puntaje BM25 como probabilidad; ajustar consultas usando la evaluación final.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Buscador lexical, resultados top-k y evaluación de ranking**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y Elasticsearch comprobado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Documentos y campos textuales de S06; consultas juzgadas** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S07.01 · Encontrar un expediente · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear consulta donde coincidencia literal simple falla por cantidad de documentos.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir documentos candidatos y criterio de relevancia antes del ranking.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Juicio inicial; no usar resultados del motor como verdad.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.02 · Texto y campo · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar corpus de objetos y descripciones; distinguir texto analizado de identificador exacto.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Elegir campos para buscar y campos para filtrar.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapping candidato; no tokenizar IDs indiscriminadamente.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.03 · Análisis textual · 5–10 min (5 min)

**Propósito y contenido específico.** Definir token, analizador, normalización y términos; mostrar puntuación, acentos y mayúsculas.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Variar análisis de dos frases y comparar tokens.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Lista de términos; no asumir sinónimos automáticos.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.04 · Índice invertido · 10–15 min (5 min)

**Propósito y contenido específico.** Explicar diccionario de términos, postings y frecuencia por documento con tabla manual.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Construir postings de tres documentos y resolver intersección.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs candidatos; índice invertido no es vector semántico.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.05 · TF, DF e IDF · 15–20 min (5 min)

**Propósito y contenido específico.** Definir frecuencia del término, frecuencia documental y peso inverso; calcular ejemplo con cuatro documentos.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Modificar frecuencia documental y observar peso relativo.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cálculo con fórmula declarada; distinguir logaritmos y convenciones.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.06 · Longitud documental · 20–25 min (5 min)

**Propósito y contenido específico.** Explicar por qué repetir palabras o tener documentos largos puede sesgar una puntuación.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Comparar textos con igual término y distinta longitud.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Frecuencia normalizada; longitud no mide calidad.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.07 · BM25 paso a paso · 25–30 min (5 min)

**Propósito y contenido específico.** Desarrollar término de IDF, saturación TF y normalización con parámetros k1 y b.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Calcular puntaje de dos documentos con valores pequeños.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ranking manual; puntaje no es probabilidad.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.08 · Control de k1 · 30–35 min (5 min)

**Propósito y contenido específico.** Mostrar saturación de frecuencia y diferencia entre presencia y repetición.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar k1 con TF fija en documentos de igual longitud.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Curva y cambio de ranking; mantener resto fijo.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.09 · Control de b · 35–40 min (5 min)

**Propósito y contenido específico.** Mostrar influencia de longitud relativa respecto a promedio de corpus.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Variar b y longitud documental con TF constante.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Puntajes comparados; no ajustar mirando test.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.10 · Consultas multitérmino · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar suma de contribuciones, coincidencia de términos y efectos de operador AND/OR.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Predecir top-k de consulta con dos palabras.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contribución por término; AND y OR no son scoring.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.11 · Mapping de Elasticsearch · 45–50 min (5 min)

**Propósito y contenido específico.** Definir index, document, text, keyword y analyzer; mostrar campo multifield.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Elegir mapping de objeto, entidad e ID y detectar tipo incorrecto.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Configuración; índice lógico no es shard.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.12 · DSL de búsqueda · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar query match, term, bool, filter y size con ejemplos equivalentes.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Cambiar filtro de entidad y consultar ranking textual.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Hits y score; filtro no debe confundirse con coincidencia semántica.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.13 · Relevancia juzgada · 55–60 min (5 min)

**Propósito y contenido específico.** Introducir juicios por consulta, precision@k, recall@k y límites de conjunto juzgado.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Variar k y calcular métricas manualmente sobre resultados etiquetados.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métricas con denominador; no juzgar documentos por score.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.14 · Errores de búsqueda · 60–65 min (5 min)

**Propósito y contenido específico.** Contrastar consultas vacías, errores ortográficos, polisemia y términos frecuentes.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Probar pares de consultas y clasificar error de recuperación.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Casos y ranking; no prometer comprensión semántica.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.15 · Comparar manual y motor · 65–70 min (5 min)

**Propósito y contenido específico.** Distinguir cálculo didáctico de estadísticas reales del índice y del analizador.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Comparar tokens y ranking manual con analyze/explain si están disponibles.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Respuesta del motor o pendiente; diferencias explicadas.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S07.16 · Cuaderno: conectar e indexar · 80–87 min (7 min)

**Propósito y contenido específico.** Verificar servicio, versión y permisos; crear índice de práctica con mapping explícito.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Cargar documentos y comprobar conteo de IDs.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado del índice; credenciales no guardadas.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.17 · Cuaderno: analizar texto · 87–95 min (8 min)

**Propósito y contenido específico.** Invocar analizador o referencia local etiquetada; observar tokens del mismo campo.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Cambiar una consulta y verificar términos.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tokens observados; no llamar simulación servicio real.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.18 · Cuaderno: consultar y filtrar · 95–102 min (7 min)

**Propósito y contenido específico.** Construir DSL visible y recorrer hits; explicar parámetros y score.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Modificar match y filter de entidad.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ranking propio y criterios; no equiparar score entre consultas.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.19 · Cuaderno: explicar ranking · 102–110 min (8 min)

**Propósito y contenido específico.** Usar explain o evidencia disponible para identificar contribuciones y longitud.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Comparar dos hits de una misma consulta con datos controlados.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Explicación real o cálculo didáctico separado.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.20 · Cuaderno: medir relevancia · 110–117 min (7 min)

**Propósito y contenido específico.** Ejecutar conjunto de consultas juzgadas y calcular precision@k y recall@k donde procede.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Variar k y contrastar resultados sin tocar juicios.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de métricas y versión de consulta.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.21 · Cuaderno: guardar buscador · 117–125 min (8 min)

**Propósito y contenido específico.** Exportar mapping, consultas, top-k y juicios no evaluativos con procedencia.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y verificar IDs de resultados.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Producto lexical reutilizable.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.22 · Reto lexical · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar una consulta y un filtro nuevos con resultado no precargado.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar DSL y elegir causa de una recuperación inesperada.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Consulta, ranking y métrica propia.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.23 · Interpretación del ranking · 130–135 min (5 min)

**Propósito y contenido específico.** Separar relevancia humana, posición y puntaje, y señalar un caso de búsqueda insuficiente.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar documento relevante omitido según juicio previo.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Error de recuperación; no inferir calidad por score alto.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.24 · Relevo vectorial · 135–140 min (5 min)

**Propósito y contenido específico.** Guardar consultas donde palabras distintas expresan intención parecida y el baseline BM25.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar IDs y juicios para comparación controlada S09.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Benchmark lexical fijo; evitar cambiar corpus sin registrar.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S07.25 · Cierre BM25 · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar pregunta inicial y mostrar cuándo lexical funciona bien y cuándo requiere otra señal.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles de TF, IDF y filtros usando ranking propio.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Buscador y evaluación; no reemplazar lexical automáticamente.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S07

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S07.08 Control de k1 | Variar k1 con TF fija en documentos de igual longitud. | Curva y cambio de ranking; mantener resto fijo. |
| E2 · S07.10 Consultas multitérmino | Predecir top-k de consulta con dos palabras. | Contribución por término; AND y OR no son scoring. |
| E3 · S07.13 Relevancia juzgada | Variar k y calcular métricas manualmente sobre resultados etiquetados. | Métricas con denominador; no juzgar documentos por score. |
| E4 · S07.20 Cuaderno: medir relevancia | Variar k y contrastar resultados sin tocar juicios. | Tabla de métricas y versión de consulta. |

**Producto mínimo:** Buscador lexical, resultados top-k y evaluación de ranking. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb` en Colab y Elasticsearch comprobado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir coincidencia con relevancia; tratar puntaje BM25 como probabilidad; ajustar consultas usando la evaluación final.

# S08 · Taller de control 1: integración NoSQL

**Pregunta guía:** ¿Puede el estudiante adquirir, organizar y consultar evidencia con las capacidades NoSQL ya enseñadas?

**Entrada:** RAW, contratos, expedientes, consultas y relaciones de S01–S07; enunciado y rúbrica vigentes.

**Producto y relevo:** V1 de Compras Claras con las evidencias exigidas por TC1.

**Cuaderno canónico:** `Cuadernos/Taller_Control_1.ipynb`. **Entorno:** Colab y los tres motores exigidos por rúbrica.

**Estado de partida:** Conservar criterios oficiales y seis productos; realizar preflight de cuentas. La ruta de 25 pantallas no publica soluciones.

**Riesgo central:** Cambiar evaluación vigente, resolver el taller en público, sustituir motor requerido por mock o penalizar indisponibilidad externa sin decisión docente.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **V1 de Compras Claras con las evidencias exigidas por TC1**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y los tres motores exigidos por rúbrica de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **RAW, contratos, expedientes, consultas y relaciones de S01–S07; enunciado y rúbrica vigentes** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S08.01 · Qué se evalúa · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar productos y rúbrica oficial sin cambiar ponderación ni publicar resultados correctos.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Seleccionar requisito y localizar evidencia que exige el enunciado.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz requisito-evidencia; no agregar nota.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.02 · Preparación individual · 2–5 min (3 min)

**Propósito y contenido específico.** Comprobar acceso, copia de cuaderno y directorio de trabajo sin usar datos personales.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Marcar preflight de cuentas y ruta de contingencia docente.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado de acceso; no compartir claves.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.03 · Mapa de entrega · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar orden de productos, dependencias y cómo se valida un resultado.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Ordenar pasos de adquisición, persistencia y consulta según rúbrica.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist; no revelar solución.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.04 · Repaso de identidad · 10–15 min (5 min)

**Propósito y contenido específico.** Recordar distinción entre grano, clave del negocio y duplicados con caso ajeno al evaluado.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Clasificar ejemplos no evaluativos y comprobar conteos.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico sin puntaje adicional.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.05 · Repaso de adquisición · 15–20 min (5 min)

**Propósito y contenido específico.** Recordar cobertura de páginas, error de red y manifiesto con fixture diferente.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Variar tamaño de página en ejercicio de práctica.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura didáctica; no usar resultado del taller.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.06 · Repaso de modelos · 20–25 min (5 min)

**Propósito y contenido específico.** Contrastar documento, tabla por consulta y grafo mediante preguntas no evaluadas.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Asociar patrones de acceso a motores.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión de práctica; no elegir por moda.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.07 · Control de concurrencia · 25–30 min (5 min)

**Propósito y contenido específico.** Enseñar diferencia entre tareas concurrentes y paralelismo, límites de red y reintento.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Variar concurrencia en simulación pequeña sin golpear fuente pública.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tiempo y límites didácticos; no inferir velocidad real.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.08 · Control de calidad · 30–35 min (5 min)

**Propósito y contenido específico.** Repasar conteos, identificadores únicos, rechazos y procedencia.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Detectar inconsistencia en muestra distinta a la evaluada.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Reporte de práctica; no divulgar respuestas.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.09 · Control documental · 35–40 min (5 min)

**Propósito y contenido específico.** Recordar filtro, proyección, actualización y conteo de una colección de ejemplo.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Comparar consulta manual y salida en fixture no evaluativo.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Concepto y diagnóstico; no resolver producto TC1.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.10 · Control wide-column · 40–45 min (5 min)

**Propósito y contenido específico.** Repasar clave de partición y clustering con una consulta distinta al taller.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Elegir patrón correcto en caso breve.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión didáctica; no modificar rúbrica.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.11 · Control grafo · 45–50 min (5 min)

**Propósito y contenido específico.** Repasar nodos, aristas, identidad y consulta con grafo de práctica.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Contar vecinos y distinguir duplicados.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado no evaluativo.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.12 · Plan de ejecución · 50–55 min (5 min)

**Propósito y contenido específico.** Dividir trabajo en dependencias y controles de parada, con el enunciado como única autoridad.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Marcar orden propio y comprobar qué recursos están listos.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist individual; no sugerir soluciones evaluadas.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.13 · Errores de entorno · 55–60 min (5 min)

**Propósito y contenido específico.** Distinguir conexión, credencial, cuota, esquema y permiso; describir recuperación segura.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Clasificar mensajes de error de ejemplo.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico; incidencia externa se registra.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.14 · Lectura de evidencias · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar cómo presentar salida propia, archivo, commit y modo de ejecución.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Inspeccionar un manifiesto de práctica y detectar evidencia incompleta.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Criterios oficiales aplicables; no puntuar preparación.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.15 · Límite de asistencia · 65–70 min (5 min)

**Propósito y contenido específico.** Diferenciar aclaración del enunciado, ayuda técnica y resolución del trabajo.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Seleccionar qué tipo de ayuda corresponde a tres casos.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Reglas de integridad; no publicar solución.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S08.16 · Taller: entrada y adquisición · 80–87 min (7 min)

**Propósito y contenido específico.** Guiar ubicación del requisito vigente y comprobar que se puede leer la entrada sin revelar lógica de solución.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Trabajar en adquisición propia y verificar identidad según enunciado.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Artefacto personal exigido; no registrar calificación aquí.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.17 · Taller: producto documental · 87–95 min (8 min)

**Propósito y contenido específico.** Indicar estación y evidencias de la rúbrica, sin completar consultas por el estudiante.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar el producto documental autónomamente y guardar salida.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado propio; no sustituir por ejemplo didáctico.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.18 · Taller: producto operacional · 95–102 min (7 min)

**Propósito y contenido específico.** Señalar requisito de Cassandra y permisos necesarios, sin sugerir la clave evaluada.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Construir y comprobar consulta según enunciado.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia CQL propia o incidencia documentada.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.19 · Taller: producto relacional · 102–110 min (8 min)

**Propósito y contenido específico.** Señalar estación de grafos y comprobación de integridad referencial.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Construir y consultar relaciones propias de acuerdo con rúbrica.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Traza y resultado propio.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.20 · Taller: verificación cruzada · 110–117 min (7 min)

**Propósito y contenido específico.** Recordar necesidad de distinguir conteos, cardinalidad y compatibilidad entre productos.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Ejecutar controles del enunciado y registrar discrepancias.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Informe de verificación personal.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.21 · Taller: empaquetar evidencia · 117–125 min (8 min)

**Propósito y contenido específico.** Mostrar estructura de entrega, rutas y validaciones formales sin revelar datos ni soluciones de compañeros.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Guardar archivos requeridos y verificar que abren.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrega según rúbrica original; no publicar roster.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.22 · Revisión autónoma · 125–130 min (5 min)

**Propósito y contenido específico.** Usar rúbrica vigente para verificar evidencia faltante antes de entregar.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Marcar qué requisito dispone de resultado propio y cuál está pendiente.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Autoevaluación sin alterar nota.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.23 · Contingencia docente · 130–135 min (5 min)

**Propósito y contenido específico.** Separar incidente de entorno y problema conceptual; documentar estado con hora y error.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar motivo de bloqueo y anexar evidencia permitida.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Incidencia para docente; no declarar cumplimiento automático.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.24 · Relevo V1 · 135–140 min (5 min)

**Propósito y contenido específico.** Identificar artefactos aprobados para uso posterior y qué debe regenerarse.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar contrato de integración, sin copiar trabajos ajenos.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** V1 propia o estado parcial explícito.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S08.25 · Cierre TC1 · 140–150 min (10 min)

**Propósito y contenido específico.** Recordar fecha y canal únicamente desde fuente vigente del curso; no modificar evaluación.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Verificar entrega y resolver autochequeo técnico no calificable.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Trazabilidad individual; no publicar respuestas ni notas.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S08

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S08.08 Control de calidad | Detectar inconsistencia en muestra distinta a la evaluada. | Reporte de práctica; no divulgar respuestas. |
| E2 · S08.10 Control wide-column | Elegir patrón correcto en caso breve. | Decisión didáctica; no modificar rúbrica. |
| E3 · S08.13 Errores de entorno | Clasificar mensajes de error de ejemplo. | Diagnóstico; incidencia externa se registra. |
| E4 · S08.20 Taller: verificación cruzada | Ejecutar controles del enunciado y registrar discrepancias. | Informe de verificación personal. |

**Producto mínimo:** V1 de Compras Claras con las evidencias exigidas por TC1. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/Taller_Control_1.ipynb` en Colab y los tres motores exigidos por rúbrica; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Cambiar evaluación vigente, resolver el taller en público, sustituir motor requerido por mock o penalizar indisponibilidad externa sin decisión docente.

# S09 · Búsqueda semántica y bases vectoriales

**Pregunta guía:** ¿Cómo recuperar expedientes por significado y medir si mejora frente a un buscador lexical?

**Entrada:** Corpus, ranking BM25 y consultas juzgadas de S07; modelos y Atlas autorizados.

**Producto y relevo:** Recuperación semántica e híbrida con métricas y configuración reproducible.

**Cuaderno canónico:** `Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb`. **Entorno:** Colab y Atlas Vector Search.

**Estado de partida:** Referente interno: explorador, notebook desde cero y experimentos documentados; conservar y ampliar con ANN/ENN y medición reproducible.

**Riesgo central:** Confundir embedding con resumen, coseno con probabilidad, ANN con exactitud y dimensiones de modelos distintos.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Recuperación semántica e híbrida con métricas y configuración reproducible**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y Atlas Vector Search de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Corpus, ranking BM25 y consultas juzgadas de S07; modelos y Atlas autorizados** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S09.01 · La consulta que BM25 no encuentra · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar dos expresiones de intención similar sin palabras idénticas y recuperar baseline lexical.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Juzgar relevancia antes de revelar resultados vectoriales.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Juicios congelados; no declarar semántica superior siempre.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.02 · Recuperar baseline · 2–5 min (3 min)

**Propósito y contenido específico.** Revisar corpus, IDs, top-k y configuración de BM25.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Verificar que consultas y universo coincidan antes de comparar.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de benchmark; no comparar conjuntos distintos.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.03 · Vector desde cero · 5–10 min (5 min)

**Propósito y contenido específico.** Definir coordenadas, dimensión y representación numérica mediante un ejemplo de dos ejes.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Ubicar tres vectores y comparar dirección y magnitud.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Representación gráfica; dos ejes son ejemplo didáctico.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.04 · Producto punto y norma · 10–15 min (5 min)

**Propósito y contenido específico.** Desarrollar multiplicación componente a componente y norma euclidiana.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Calcular a mano producto y norma de dos vectores pequeños.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cálculo verificable; no dividir por norma cero.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.05 · Coseno y distancia · 15–20 min (5 min)

**Propósito y contenido específico.** Explicar similitud angular y diferencia con distancia euclidiana y magnitud.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Variar magnitud y ángulo para observar coseno y distancia.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Valores numéricos; coseno no es porcentaje de verdad.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.06 · Embedding de texto · 20–25 min (5 min)

**Propósito y contenido específico.** Explicar modelo que transforma secuencia en vector de dimensión fija y pérdida de información.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Comparar dos textos y verificar dimensión de salida del modelo.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Vector y metadata; no reconstruir texto exacto.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.07 · Modelo E5 y prefijos · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar representación de consulta y pasaje según convención del modelo utilizado.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Cambiar prefijo conforme a documentación y comparar resultados etiquetados.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Versión y norma; no mezclar modelos o prefijos sin registro.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.08 · Normalización y top-k · 30–35 min (5 min)

**Propósito y contenido específico.** Mostrar ranking exacto por coseno sobre una matriz pequeña; explicar empates.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar k y ordenar similitudes manual y programáticamente.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs ordenados; establecer desempate estable.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.09 · Índice vectorial · 35–40 min (5 min)

**Propósito y contenido específico.** Distinguir vector almacenado, índice y búsqueda por vecinos; explicar costo de indexación.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Comparar búsqueda lineal y esquema conceptual de vecinos.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama y operaciones; no atribuir algoritmo no documentado.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.10 · ANN frente a ENN · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar aproximación, exactitud y parámetros de candidatos cuando el servicio los admite.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar candidatos en simulación o motor verificado y comparar top-k exacto.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Recall de vecinos; aproximación no garantiza mismo ranking.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.11 · Filtros de metadata · 45–50 min (5 min)

**Propósito y contenido específico.** Mostrar restricción por entidad o estado antes o durante búsqueda según motor.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Comparar búsqueda global y restringida con mismo texto.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs y universo; no comparar recall con universo distinto.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.12 · Latencia y repetición · 50–55 min (5 min)

**Propósito y contenido específico.** Separar preparación de embeddings, indexación, consulta y red; introducir p50 y p95.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Medir consultas repetidas con configuración constante y calentamiento identificado.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Latencias y entorno; no afirmar SLA.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.13 · Fusión RRF · 55–60 min (5 min)

**Propósito y contenido específico.** Desarrollar suma de recíprocos de posiciones con constante declarada, sin combinar scores incompatibles.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Fusionar rankings de cuatro documentos y variar constante.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ranking y contribuciones; no usar scores crudos juntos.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.14 · Relevancia y recall ANN · 60–65 min (5 min)

**Propósito y contenido específico.** Distinguir recall de vecinos exactos de recall de documentos juzgados relevantes.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Calcular ambas métricas sobre listas diferentes.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos denominadores; no confundir recuperación técnica y utilidad.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.15 · Comparación lexical-semántica · 65–70 min (5 min)

**Propósito y contenido específico.** Identificar consultas exactas, sinónimos, negación y nombres propios donde cada señal ayuda.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Evaluar los tres rankings sobre consultas congeladas.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métricas por consulta; no seleccionar ganadores solo por ejemplos favorables.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S09.16 · Cuaderno: preparar e incrustar · 80–87 min (7 min)

**Propósito y contenido específico.** Validar modelo, prefijos, dimensión, versiones y presupuesto; cargar corpus por lotes.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar muestra pequeña y comprobar dimensiones y normas.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Embeddings propios o caché identificada; no fingir inferencia.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.17 · Cuaderno: ranking exacto · 87–95 min (8 min)

**Propósito y contenido específico.** Construir matriz y búsqueda por coseno con código visible.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Modificar consulta y comparar top-k con control manual.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ranking exacto y IDs; no contar similitudes nulas como relevantes.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.18 · Cuaderno: Atlas e índice · 95–102 min (7 min)

**Propósito y contenido específico.** Verificar cuota de índices, conexión y mapping vectorial de dimensión correcta.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Crear o reutilizar índice autorizado y comprobar estado disponible.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado real o pendiente; no prometer disponibilidad inmediata.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.19 · Cuaderno: consultar ANN · 102–110 min (8 min)

**Propósito y contenido específico.** Ejecutar búsqueda vectorial y, si está soportada, referencia exacta comparable.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Variar candidatos o k dentro de límite seguro.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs, recall de vecinos y modo real.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.20 · Cuaderno: evaluar y fusionar · 110–117 min (7 min)

**Propósito y contenido específico.** Calcular métricas sobre juicios, ejecutar RRF y comparar resultados con baseline.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Modificar constante en conjunto de práctica sin tocar test.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de métricas; separar selección y evaluación.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.21 · Cuaderno: exportar recuperación · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar IDs, versión del modelo, dimensión, consultas y ranking con procedencia.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y validar compatibilidad de vector y corpus.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Recuperación reproducible; no guardar secretos.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.22 · Reto semántico · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar intención nueva y filtro de entidad; pedir predicción de cuál señal ayuda.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Ejecutar lexical, vectorial e híbrida y elegir según juicio disponible.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tres resultados y decisión contextual.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.23 · Interpretación de fallos · 130–135 min (5 min)

**Propósito y contenido específico.** Mostrar texto ambiguo y vecino cercano incorrecto; explicar efecto de corpus y modelo.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar causa plausible y dato necesario para confirmar.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Límite concreto; no atribuir significado humano al vector.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.24 · Relevo multimedia · 135–140 min (5 min)

**Propósito y contenido específico.** Definir forma de enlazar OCR y transcripción por identidad, campo y modelo.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar contrato de textos e índices para S10/S11.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Esquema y consulta reutilizable.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S09.25 · Cierre semántico · 140–150 min (10 min)

**Propósito y contenido específico.** Retomar consulta de apertura y comparar evidencia sin afirmar mejora universal.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles sobre norma, ANN, filtro y fusión.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Benchmark y producto; conservar configuración.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S09

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S09.08 Normalización y top-k | Variar k y ordenar similitudes manual y programáticamente. | IDs ordenados; establecer desempate estable. |
| E2 · S09.10 ANN frente a ENN | Variar candidatos en simulación o motor verificado y comparar top-k exacto. | Recall de vecinos; aproximación no garantiza mismo ranking. |
| E3 · S09.13 Fusión RRF | Fusionar rankings de cuatro documentos y variar constante. | Ranking y contribuciones; no usar scores crudos juntos. |
| E4 · S09.20 Cuaderno: evaluar y fusionar | Modificar constante en conjunto de práctica sin tocar test. | Tabla de métricas; separar selección y evaluación. |

**Producto mínimo:** Recuperación semántica e híbrida con métricas y configuración reproducible. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb` en Colab y Atlas Vector Search; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir embedding con resumen, coseno con probabilidad, ANN con exactitud y dimensiones de modelos distintos.

# S10 · Imágenes, audio y ETL de señales

**Pregunta guía:** ¿Cómo convertir activos multimedia heterogéneos en un catálogo verificable sin perder originales?

**Entrada:** Imágenes y audios autorizados de fuentes del curso; metadatos, créditos y contratos.

**Producto y relevo:** Catálogo de activos RAW y derivados con características y métricas de transformación.

**Cuaderno canónico:** `Cuadernos/10_Imagenes_Audio.ipynb`. **Entorno:** Colab o entorno verificado del cuaderno.

**Estado de partida:** Conservar recursos ricos, fuentes y controles; medir transformaciones reales y distinguir hash de procesamiento de señales.

**Riesgo central:** Confundir códec y extensión, tamaño comprimido y memoria, canal y muestra; perder procedencia o afirmar clasificación validada sin etiquetas.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Catálogo de activos RAW y derivados con características y métricas de transformación**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab o entorno verificado del cuaderno de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Imágenes y audios autorizados de fuentes del curso; metadatos, créditos y contratos** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S10.01 · Los activos de un expediente · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear consulta donde texto descriptivo no revela contenido de foto o audio.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir qué derivados permitirían explorar sin sustituir original.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Necesidad y fuente; conservar créditos.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.02 · RAW y procedencia · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar identidad, URL, licencia o permiso, fecha y hash de archivo.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Comparar manifiestos y localizar dato de origen faltante.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Manifiesto; hash no autoriza uso.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.03 · Píxeles y canales · 5–10 min (5 min)

**Propósito y contenido específico.** Definir imagen como matriz y canal, distinguir RGB y gris; mostrar valores pequeños.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Modificar un píxel y comparar canales y representación.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz y visualización; canal no es formato de archivo.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.04 · Resolución y memoria · 10–15 min (5 min)

**Propósito y contenido específico.** Derivar ancho por alto por canales por bytes; distinguir memoria descomprimida y archivo.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Variar resolución y calcular tamaño de matriz.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Bytes estimados; compresión cambia archivo, no la fórmula.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.05 · Histogramas · 15–20 min (5 min)

**Propósito y contenido específico.** Explicar distribución de intensidad, contraste y pérdida de ubicación espacial.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Comparar dos imágenes con histograma similar y disposición distinta.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Histograma y límite; no identifica objetos.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.06 · Redimensionamiento · 20–25 min (5 min)

**Propósito y contenido específico.** Explicar muestreo, interpolación y pérdida de detalle, especialmente texto pequeño.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Variar escala y observar legibilidad y tamaño.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Imagen antes/después; resolución menor puede perjudicar OCR.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.07 · Formato y códec · 25–30 min (5 min)

**Propósito y contenido específico.** Distinguir nombre, contenedor, códec, encabezado y señal; usar caso WAV con audio MP3 si fuente verificada.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Inspeccionar metadatos y comparar extensión con detección técnica.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Formato observado; no confiar en nombre.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.08 · Audio como señal · 30–35 min (5 min)

**Propósito y contenido específico.** Definir muestra, amplitud, canal, frecuencia de muestreo y duración.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Cambiar sample rate en ejemplo y calcular cantidad de muestras.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cálculo y forma de onda; no confundir frecuencia de tono y muestreo.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.09 · RMS y amplitud · 35–40 min (5 min)

**Propósito y contenido específico.** Explicar raíz media cuadrática y nivel energético relativo con cuatro muestras.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Calcular RMS de señales con distintos signos y escalas.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** RMS calculado; no equivale a sonoridad percibida exacta.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.10 · FFT y espectro · 40–45 min (5 min)

**Propósito y contenido específico.** Mostrar descomposición de señal en componentes de frecuencia mediante dos tonos sintéticos.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar frecuencia de un tono y observar pico espectral.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Picos en Hz; resolución depende de ventana.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.11 · Espectrograma · 45–50 min (5 min)

**Propósito y contenido específico.** Explicar ventanas, tiempo, frecuencia e intensidad; mostrar señal con cambio temporal.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Variar tamaño de ventana y observar resolución tiempo-frecuencia.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Espectrograma; no identificar hablante.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.12 · Centroide y MFCC · 50–55 min (5 min)

**Propósito y contenido específico.** Introducir centroide como balance espectral y MFCC como características compactas; no exigir derivación avanzada.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Comparar dos señales con características distintas y observar variación.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Features y dimensión; no son transcripciones.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.13 · ETL de multimedia · 55–60 min (5 min)

**Propósito y contenido específico.** Distinguir extracción, transformación y carga, y representar RAW, derivados y catálogo.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Ordenar etapas y detectar qué se repite tras fallo.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Flujo y contratos; no sobrescribir RAW.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.14 · Parquet y JSONL · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar almacenamiento columnar y un JSON por línea; contrastar lectura parcial y registros anidados.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Comparar esquema y forma de lectura de muestras pequeñas.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tamaños y conteos; no declarar compresión universal.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.15 · Threads y rendimiento · 65–70 min (5 min)

**Propósito y contenido específico.** Diferenciar tareas I/O y CPU, concurrencia y paralelismo; controlar workers, datos y tiempo.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Variar workers en una muestra de descargas o transformaciones autorizadas.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tiempo y throughput medidos; no extrapolar hash a ASR.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S10.16 · Cuaderno: preparar activos · 80–87 min (7 min)

**Propósito y contenido específico.** Cargar manifiesto de imágenes y audios y comprobar archivos, fuentes y hashes.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar sobre selección segura y registrar faltantes.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo y procedencia; no usar archivos sin autorización.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.17 · Cuaderno: transformar imagen · 87–95 min (8 min)

**Propósito y contenido específico.** Leer matriz, inspeccionar canales, redimensionar y calcular histograma con código visible.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Cambiar resolución en copia y medir bytes y legibilidad.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Derivado y métricas; conservar original.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.18 · Cuaderno: transformar audio · 95–102 min (7 min)

**Propósito y contenido específico.** Detectar códec, decodificar, normalizar frecuencia de muestreo y mostrar forma de onda.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar audio corto y activo largo por segmentos cuando corresponda.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Duración y parámetros; no truncar silenciosamente.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.19 · Cuaderno: características · 102–110 min (8 min)

**Propósito y contenido específico.** Calcular RMS, espectro, centroide y MFCC sobre una muestra explicada.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Cambiar ventana y comparar métricas.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de features; distinguir unidades y dimensiones.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.20 · Cuaderno: medir transformación · 110–117 min (7 min)

**Propósito y contenido específico.** Ejecutar baseline secuencial y variante concurrente sobre mismos activos y tareas.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Comparar tiempo, errores y cantidad procesada dentro de cuota.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Throughput real de tarea medida; no atribuir a otra.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.21 · Cuaderno: catálogo y relectura · 117–125 min (8 min)

**Propósito y contenido específico.** Escribir derivados, metadata, hashes y features en JSONL o Parquet según caso.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Reabrir y verificar vínculo RAW-derivado.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Catálogo válido y créditos.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.22 · Reto de señal · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar activo nuevo o configuración de escala y pedir elegir transformación según objetivo.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar parámetro y comparar salida propia con original.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Derivado, métrica y decisión; no evaluar por estética.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.23 · Interpretación del catálogo · 130–135 min (5 min)

**Propósito y contenido específico.** Distinguir señal medible, metadatos y significado; explicar qué falta para OCR/ASR.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir qué características ayudan a detectar un problema técnico.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Límite y criterio; no afirmar contenido semántico.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.24 · Relevo OCR y ASR · 135–140 min (5 min)

**Propósito y contenido específico.** Seleccionar activos legibles y audios con parámetros, preservando identidad y duración.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar lista de trabajo y manifiesto de entrada S11.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada trazable con cobertura.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S10.25 · Cierre multimedia · 140–150 min (10 min)

**Propósito y contenido específico.** Retomar necesidad y comparar qué se obtuvo de imagen y audio sin extraer todavía significado completo.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles de píxeles, muestreo, formato y ETL con resultados propios.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Catálogo y métricas; errores quedan identificados.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S10

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S10.08 Audio como señal | Cambiar sample rate en ejemplo y calcular cantidad de muestras. | Cálculo y forma de onda; no confundir frecuencia de tono y muestreo. |
| E2 · S10.10 FFT y espectro | Variar frecuencia de un tono y observar pico espectral. | Picos en Hz; resolución depende de ventana. |
| E3 · S10.13 ETL de multimedia | Ordenar etapas y detectar qué se repite tras fallo. | Flujo y contratos; no sobrescribir RAW. |
| E4 · S10.20 Cuaderno: medir transformación | Comparar tiempo, errores y cantidad procesada dentro de cuota. | Throughput real de tarea medida; no atribuir a otra. |

**Producto mínimo:** Catálogo de activos RAW y derivados con características y métricas de transformación. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/10_Imagenes_Audio.ipynb` en Colab o entorno verificado del cuaderno; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir códec y extensión, tamaño comprimido y memoria, canal y muestra; perder procedencia o afirmar clasificación validada sin etiquetas.

# S11 · OCR, ASR, embeddings y recuperación multimedia

**Pregunta guía:** ¿Cómo convertir imágenes, documentos y audios en evidencia textual recuperable y trazable?

**Entrada:** Catálogo o bundle autónomo con imágenes, PDFs, audios, fuentes y créditos; ruta sin video.

**Producto y relevo:** Investigador multimedia con textos, segmentos, métricas de extracción y búsqueda.

**Cuaderno canónico:** `s11-estudiantes/01_laboratorio.ipynb`. **Entorno:** Codespaces especializado.

**Estado de partida:** Material canónico de rama estudiantil, 122 fuentes según guía; requiere ejecución limpia de OCR/ASR/visor, control de audios largos y embeddings.

**Riesgo central:** Audio superior al límite, contenedor engañoso, OCR sin página, ASR sin intervalo, embeddings incompatibles y dependencia de sesión previa.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Investigador multimedia con textos, segmentos, métricas de extracción y búsqueda**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Codespaces especializado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Catálogo o bundle autónomo con imágenes, PDFs, audios, fuentes y créditos; ruta sin video** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S11.01 · Investigar contenido inaccesible · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar una consulta que exige leer un PDF escaneado y escuchar un audio, no solo sus nombres.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir qué evidencia debe aparecer con página o intervalo.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Objetivo de recuperación; sin video.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.02 · Entrada autónoma · 2–5 min (3 min)

**Propósito y contenido específico.** Explicar bundle, catálogo y RAW; disponer activos suficientes sin volver a S10.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Verificar identificadores, créditos, hashes y disponibilidad en muestra.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Inventario; no depender del estado previo.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.03 · OCR desde cero · 5–10 min (5 min)

**Propósito y contenido específico.** Definir reconocimiento óptico de caracteres y separar imagen, segmentación, texto y confianza.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Comparar recorte de documento y texto esperado en caso manual.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Caracteres y región; OCR no entiende el contrato.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.04 · Preprocesamiento OCR · 10–15 min (5 min)

**Propósito y contenido específico.** Explicar escala de grises, umbral, rotación y ruido con efectos sobre legibilidad.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Variar umbral y comparar imagen y extracción.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos versiones; binarizar no siempre mejora.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.05 · PSM y estructura · 15–20 min (5 min)

**Propósito y contenido específico.** Enseñar modos de segmentación de página mediante bloque, columna y texto disperso.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Elegir PSM en imagen de formato conocido y comparar salida.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Texto y modo; no aplicar un PSM universal.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.06 · Errores OCR y CER · 20–25 min (5 min)

**Propósito y contenido específico.** Introducir distancia de edición y tasa de errores por carácter con referencia humana.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Calcular sustitución, inserción y borrado en ejemplo pequeño.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** CER con denominador; confianza del motor no sustituye referencia.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.07 · PDF y páginas · 25–30 min (5 min)

**Propósito y contenido específico.** Distinguir PDF con capa textual de PDF escaneado y extracción por página.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Inspeccionar archivo autorizado y decidir ruta OCR o texto nativo.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Página, método y origen; no mezclar páginas sin vínculo.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.08 · ASR desde cero · 30–35 min (5 min)

**Propósito y contenido específico.** Definir reconocimiento automático del habla, segmentos, timestamps y diferencia frente a traducción.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Comparar referencia y transcripción breve identificada.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Texto y segmento; no inferir identidad del hablante.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.09 · Nombre, contenedor y códec · 35–40 min (5 min)

**Propósito y contenido específico.** Usar activo largo documentado y verificar metadata real antes de decodificar.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Comparar extensión WAV y códec detectado; calcular duración.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Metadata y prueba; no asumir extensión correcta.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.10 · Segmentación de audio · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar fragmentos, ventanas, solape y offsets globales para superar límites de inferencia.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar tamaño de bloque y detectar cortes o duplicados.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura temporal; no perder últimos segundos.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.11 · WER y referencia · 45–50 min (5 min)

**Propósito y contenido específico.** Definir errores por palabra y normalización; mostrar ejemplo con inserción, borrado y sustitución.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Calcular WER sobre dos transcripciones y referencia fija.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métrica y convención; WER puede superar uno.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.12 · Modelo y costo · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar diferencia entre inferencia local y servicio, tiempo, memoria y descarga de pesos.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Comparar presupuesto de muestra corta y larga con medición disponible.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan seguro; no inventar velocidad.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.13 · Embeddings de fuentes mixtas · 55–60 min (5 min)

**Propósito y contenido específico.** Explicar texto OCR, texto ASR, metadatos y descripción de imagen como campos con procedencia; distinguir embedding de imagen nativo.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Seleccionar representación por modalidad y modelo compatible.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de vectores; texto de imagen no equivale a vector visual.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.14 · Indexación y consulta · 60–65 min (5 min)

**Propósito y contenido específico.** Conectar fragmento con documento, página, intervalo, URL y modelo para recuperar evidencia.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Filtrar por modalidad y comparar resultado global y restringido.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Hit trazable; no devolver solo un texto sin origen.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.15 · Concurrencia y fallos · 65–70 min (5 min)

**Propósito y contenido específico.** Separar descarga, OCR y ASR y mostrar reintentos por activo con errores individuales.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Variar workers en lote pequeño y comprobar cobertura y fallos.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado por activo; no ocultar errores.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S11.16 · Cuaderno: Codespace limpio · 80–87 min (7 min)

**Propósito y contenido específico.** Preparar dependencias y verificar Tesseract, decodificador y servicio de embeddings con versiones.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar preflight real sin comandos ambiguos ni regresar a S10.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado de herramientas; fallback claramente marcado.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.17 · Cuaderno: OCR de imagen/PDF · 87–95 min (8 min)

**Propósito y contenido específico.** Procesar imagen y página autorizadas; mostrar texto, región y configuración.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Cambiar PSM o preprocesamiento y medir CER donde hay referencia.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** OCR propio y página; no sustituir por cache sin aviso.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.18 · Cuaderno: ASR corto y largo · 95–102 min (7 min)

**Propósito y contenido específico.** Decodificar activo corto y segmentar uno superior a límite del motor, preservando offsets.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar ruta viable y verificar cobertura y unión de segmentos.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Intervalos y texto; fallo de larga duración queda registrado.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.19 · Cuaderno: extraer embeddings · 102–110 min (8 min)

**Propósito y contenido específico.** Usar modelo verificado y API correcta, comprobar dimensiones y compatibilidad de campos.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Generar vectores sobre OCR, ASR y texto del expediente.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Vector, modelo y origen; no mezclar dimensiones.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.20 · Cuaderno: búsqueda multimodal · 110–117 min (7 min)

**Propósito y contenido específico.** Construir consulta sobre textos derivados y metadata, y mostrar visor de evidencia.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Cambiar consulta y filtro, abrir página o intervalo correspondiente.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Top-k y fuente; no confundir OCR con descripción generada.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.21 · Cuaderno: exportar y verificar · 117–125 min (8 min)

**Propósito y contenido específico.** Persistir RAW referenciado, JSONL o Parquet, métricas, estados y vectores.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y comprobar claves, cobertura y procedencia.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Investigador multimedia portable; no publicar tokens.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.22 · Reto multimodal · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar pregunta que requiera contrastar texto de contrato, imagen y audio según fuentes disponibles.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Ejecutar recuperación y elegir evidencia que respalda respuesta.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs, páginas, intervalos y límite; no inventar contenido.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.23 · Clínica de errores · 130–135 min (5 min)

**Propósito y contenido específico.** Contrastar timeout, audio demasiado largo, error de códec, PSM y modelo inexistente.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar recuperación contextual y repetir operación mínima.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado final y fallo específico; no ocultarlo.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.24 · Relevo TC2 · 135–140 min (5 min)

**Propósito y contenido específico.** Revisar qué artefactos alimentan el taller y qué resultados deben producirse individualmente.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar contrato de activos y derivados sin divulgar solución.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada ETL trazable.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S11.25 · Cierre OCR/ASR · 140–150 min (10 min)

**Propósito y contenido específico.** Retomar consulta inicial y distinguir extracción, representación y relevancia.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver autochequeo sobre CER, WER, segmentos y trazabilidad.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia multimedia verificable; no considerar plan como ejecución.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S11

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S11.08 ASR desde cero | Comparar referencia y transcripción breve identificada. | Texto y segmento; no inferir identidad del hablante. |
| E2 · S11.10 Segmentación de audio | Variar tamaño de bloque y detectar cortes o duplicados. | Cobertura temporal; no perder últimos segundos. |
| E3 · S11.13 Embeddings de fuentes mixtas | Seleccionar representación por modalidad y modelo compatible. | Contrato de vectores; texto de imagen no equivale a vector visual. |
| E4 · S11.20 Cuaderno: búsqueda multimodal | Cambiar consulta y filtro, abrir página o intervalo correspondiente. | Top-k y fuente; no confundir OCR con descripción generada. |

**Producto mínimo:** Investigador multimedia con textos, segmentos, métricas de extracción y búsqueda. Antes de publicar, ejecutar la ruta base del cuaderno `s11-estudiantes/01_laboratorio.ipynb` en Codespaces especializado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Audio superior al límite, contenedor engañoso, OCR sin página, ASR sin intervalo, embeddings incompatibles y dependencia de sesión previa.

# S12 · Taller de control 2: ETL y recuperación

**Pregunta guía:** ¿Puede el estudiante integrar extracción, transformación y recuperación de activos de acuerdo con el taller vigente?

**Entrada:** Enunciado y rúbrica TC2, corpus y fuentes autorizadas de sesiones previas.

**Producto y relevo:** V2 con entregables originales del taller y trazabilidad individual.

**Cuaderno canónico:** `Cuadernos/Taller_Control_2.ipynb`. **Entorno:** Colab y entornos autorizados por enunciado.

**Estado de partida:** Conservar seis desafíos y 24 controles reportados; verificar recuperación y disponibilidad de audios; no publicar solución ni cambiar ponderación.

**Riesgo central:** Sobrecargar cuotas, alterar taller anunciado, usar resultados cacheados como propios o introducir S13/S14 no evaluados.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **V2 con entregables originales del taller y trazabilidad individual**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y entornos autorizados por enunciado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Enunciado y rúbrica TC2, corpus y fuentes autorizadas de sesiones previas** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S12.01 · Alcance del segundo taller · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar rúbrica y entregables originales, distinguir ETL evaluado de capacidades futuras.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Seleccionar componente y localizar evidencia exigida.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist oficial; no cambiar ponderación.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.02 · Estado y recursos · 2–5 min (3 min)

**Propósito y contenido específico.** Comprobar copia del cuaderno, fuentes, acceso y límites de ejecución sin datos personales.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Marcar disponibilidad de imágenes, audios y motores requeridos.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Preflight y contingencia; sin claves expuestas.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.03 · Mapa de dependencias · 5–10 min (5 min)

**Propósito y contenido específico.** Mostrar cómo RAW, derivados, metadata y recuperación se relacionan en la entrega.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Ordenar requisitos del enunciado sin revelar solución.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ruta de trabajo; no añadir etapas evaluables.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.04 · Repaso de RAW · 10–15 min (5 min)

**Propósito y contenido específico.** Recordar identidad, fecha, hash y diferencia entre original y derivado con caso ajeno al taller.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Inspeccionar manifiesto de ejemplo y detectar dato faltante.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ejercicio formativo; no usar respuestas del TC2.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.05 · Repaso de señales · 15–20 min (5 min)

**Propósito y contenido específico.** Revisar resolución, canales, muestreo y duración en activo de práctica.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Elegir metadatos que permiten verificar transformación.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Control conceptual sin puntaje nuevo.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.06 · Repaso de OCR · 20–25 min (5 min)

**Propósito y contenido específico.** Recordar segmentación y errores de extracción con una imagen no evaluada.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Comparar texto de dos configuraciones y seleccionar criterio.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado formativo; no entregar solución.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.07 · Repaso de ASR · 25–30 min (5 min)

**Propósito y contenido específico.** Recordar segmentación temporal, transcripción y límites de motor.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Detectar hueco temporal en segmentos de un caso pequeño.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura de ejemplo; no inventar transcripción.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.08 · Repaso de características · 30–35 min (5 min)

**Propósito y contenido específico.** Contrastar metadata, RMS, espectro y features como medidas de señal.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Elegir qué salida informa sobre formato y cuál sobre contenido.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión estructurada; no confundir feature con texto.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.09 · Repaso de embeddings · 35–40 min (5 min)

**Propósito y contenido específico.** Recuperar concepto de dimensión, modelo y coseno sin evaluar nuevas técnicas.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Detectar vectores incompatibles de ejemplo.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagnóstico no calificable.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.10 · Repaso de recuperación · 40–45 min (5 min)

**Propósito y contenido específico.** Mostrar consulta, top-k, filtro y vínculo con evidencia en un corpus de práctica.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Comparar hit trazable y hit sin procedencia.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Criterio de verificación; no publicar ranking del taller.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.11 · Control de calidad ETL · 45–50 min (5 min)

**Propósito y contenido específico.** Recordar conteos entrada, éxito, rechazo y pendiente; representar identidad en cada etapa.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Detectar discrepancia en fixture no evaluativo.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla de estados; no equiparar intento con éxito.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.12 · Plan de ejecución seguro · 50–55 min (5 min)

**Propósito y contenido específico.** Dividir práctica en lote pequeño, validación y ampliación autorizada por rúbrica.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Seleccionar orden de actividades dentro de cuota disponible.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan de trabajo; no bajar requisitos unilateralmente.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.13 · Errores de plataformas · 55–60 min (5 min)

**Propósito y contenido específico.** Distinguir timeout, archivo dañado, dependencia y límite de servicio.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Clasificar tres mensajes de error de ejemplo.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ruta de diagnóstico; incidencia real se conserva.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.14 · Evidencia individual · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar resultado propio, traza, alternativa y límite bajo rúbrica original.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Revisar evidencia no evaluativa y localizar archivo faltante.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Criterios de autenticidad; no exigir prosa libre nueva.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.15 · Límite de ayuda · 65–70 min (5 min)

**Propósito y contenido específico.** Diferenciar aclaración, soporte y resolución del ejercicio; evitar respuestas correctas visibles.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Elegir tipo de asistencia aceptable según situación.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Regla de integridad; no generar solución pública.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S12.16 · Taller: adquirir y validar · 80–87 min (7 min)

**Propósito y contenido específico.** Señalar estación del enunciado donde se prepara fuente y se verifican datos.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar adquisición propia según requisitos vigentes.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada y manifiesto personales.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.17 · Taller: imágenes y extracción · 87–95 min (8 min)

**Propósito y contenido específico.** Señalar requisito de tratamiento de imágenes y evidencia esperada sin prescribir solución.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Construir derivados y controles del enunciado.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultados propios y procedencia.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.18 · Taller: audio y extracción · 95–102 min (7 min)

**Propósito y contenido específico.** Señalar requisito de audios y cobertura; registrar fallos reales.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Procesar activos exigidos bajo estrategia propia permitida.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Segmentos, metadata o incidencia según rúbrica.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.19 · Taller: organizar derivados · 102–110 min (8 min)

**Propósito y contenido específico.** Señalar estructura de almacenamiento y verificación que exige el enunciado.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Persistir y reabrir derivados propios.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Archivos y conteos; no declarar éxito sin relectura.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.20 · Taller: recuperación · 110–117 min (7 min)

**Propósito y contenido específico.** Señalar consulta y producto exigido; no sugerir ranking evaluado.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Ejecutar recuperación y obtener evidencia de su propio corpus.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultados y traza propios.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.21 · Taller: controlar entrega · 117–125 min (8 min)

**Propósito y contenido específico.** Revisar rutas, ejecución, campos y artefactos requeridos por rúbrica.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Ejecutar verificaciones permitidas y registrar pendientes.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist y archivos personales.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.22 · Reto de autonomía · 125–130 min (5 min)

**Propósito y contenido específico.** Reservar trabajo independiente en requisito restante sin agregar tarea nueva.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Completar decisión pendiente y producir salida propia.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia según rúbrica, no ejemplo resuelto.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.23 · Revisión de coherencia · 130–135 min (5 min)

**Propósito y contenido específico.** Comparar resultados de etapas y detectar pérdida de identidad, cobertura o fuente.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Elegir discrepancia a corregir y ejecutar prueba mínima.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Registro de corrección personal.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.24 · Relevo V2 · 135–140 min (5 min)

**Propósito y contenido específico.** Identificar qué resultados autorizados servirán a procesamiento distribuido posterior.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar contrato y manifiesto sin datos privados ni notas.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** V2 o estado parcial explícito.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S12.25 · Cierre TC2 · 140–150 min (10 min)

**Propósito y contenido específico.** Verificar canal y fecha desde fuente vigente y revisar entrega bajo criterios originales.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Marcar evidencias completadas y dudas técnicas no evaluativas.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrega trazable; no certificar cumplimiento sin revisar.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S12

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S12.08 Repaso de características | Elegir qué salida informa sobre formato y cuál sobre contenido. | Decisión estructurada; no confundir feature con texto. |
| E2 · S12.10 Repaso de recuperación | Comparar hit trazable y hit sin procedencia. | Criterio de verificación; no publicar ranking del taller. |
| E3 · S12.13 Errores de plataformas | Clasificar tres mensajes de error de ejemplo. | Ruta de diagnóstico; incidencia real se conserva. |
| E4 · S12.20 Taller: recuperación | Ejecutar recuperación y obtener evidencia de su propio corpus. | Resultados y traza propios. |

**Producto mínimo:** V2 con entregables originales del taller y trazabilidad individual. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/Taller_Control_2.ipynb` en Colab y entornos autorizados por enunciado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Sobrecargar cuotas, alterar taller anunciado, usar resultados cacheados como propios o introducir S13/S14 no evaluados.

# S13 · HDFS, MapReduce y Dask

**Pregunta guía:** ¿Qué cambia al dividir un procesamiento en particiones y trabajadores, y cómo demostrar equivalencia y capacidad?

**Entrada:** Datos SECOP por lotes y resultados ETL; versiones y manifiestos.

**Producto y relevo:** Motor Dask reproducible con comparaciones de equivalencia, tiempo y entrenamiento.

**Cuaderno canónico:** `s13-laboratorio/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`. **Entorno:** Codespaces especializado.

**Estado de partida:** Conservar datos abundantes, ejercicios ocho lotes, K-means y rutas de escala; validar pruebas reales y explicar trabajadores sin hablar de hardware personal.

**Riesgo central:** Confundir worker con núcleo, partición con archivo, clúster lógico con máquinas físicas; presentar escalamiento o entrenamiento sin medición.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Motor Dask reproducible con comparaciones de equivalencia, tiempo y entrenamiento**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Codespaces especializado de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Datos SECOP por lotes y resultados ETL; versiones y manifiestos** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S13.01 · El problema de capacidad · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear análisis de lotes que excede presupuesto de memoria o tiempo de una ejecución monolítica.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir restricción dominante y definir resultado de control.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Hipótesis medible; no afirmar que pandas siempre falla.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.02 · Relevo y entorno · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar archivos, esquema y tamaño, inspeccionar CPU lógicas y memoria disponible del runtime.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Ejecutar inspección de entorno y seleccionar escala segura.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Recursos observados; no analizar dispositivos personales.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.03 · Almacenamiento distribuido HDFS · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar bloques, NameNode, DataNodes, metadata y replicación a nivel conceptual.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Distribuir bloques de un archivo en nodos ilustrativos y variar factor de réplica.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa conceptual y capacidad; no afirmar HDFS instalado.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.04 · Tolerancia a fallos · 10–15 min (5 min)

**Propósito y contenido específico.** Mostrar pérdida de copia, disponibilidad y costo de réplicas; separar cómputo y almacenamiento.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Quitar un nodo de simulación y comprobar bloques accesibles.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Disponibilidad bajo supuestos; no prueba de producción.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.05 · MapReduce desde cero · 15–20 min (5 min)

**Propósito y contenido específico.** Definir map, pares clave-valor, shuffle, agrupación y reduce con registros SECOP pequeños.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Calcular conteos por entidad a mano por particiones.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Intermedios y agregado global; no promediar medias sin pesos.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.06 · Amdahl y speedup · 20–25 min (5 min)

**Propósito y contenido específico.** Separar porción serial y paralelizable, explicar sobrecostos y fórmula ideal.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Variar fracción serial y trabajadores; contrastar límite de aceleración.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Curva teórica; no prometer tiempo medido.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.07 · Procesos, threads y workers · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar proceso, hilo, CPU lógica y worker; un worker puede tener uno o varios hilos según configuración.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Variar trabajadores e hilos manteniendo CPU disponible fija.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Configuración lógica; no crea hardware.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.08 · Particiones Dask · 30–35 min (5 min)

**Propósito y contenido específico.** Definir división lógica de colección, scheduler, tarea y worker; distinguir partición y archivo.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar particiones con número fijo de archivos.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cantidad de tareas; particiones diminutas añaden sobrecosto.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.09 · Evaluación perezosa · 35–40 min (5 min)

**Propósito y contenido específico.** Explicar grafo de tareas y diferencia entre definir transformación y compute.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Construir operación simple y predecir cuándo se materializa.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Grafo y ejecución; tiempo de construir no es tiempo de calcular.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.10 · Reducciones y equivalencia · 40–45 min (5 min)

**Propósito y contenido específico.** Mostrar agregación asociativa y casos que requieren combinación ponderada.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar particiones y comparar suma, conteo y media con pandas.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Equivalencia con tolerancia; orden de filas no necesariamente igual.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.11 · Shuffle y joins · 45–50 min (5 min)

**Propósito y contenido específico.** Explicar redistribución por clave y costo de intercambio local o remoto.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Variar distribución de claves y observar movimiento conceptual.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Distribución y resultado; no inferir tráfico real sin métricas.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.12 · Skew y carga desigual · 50–55 min (5 min)

**Propósito y contenido específico.** Mostrar partición dominante y efecto sobre fin de etapa; distinguir tamaños y complejidad de tarea.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Inyectar clave frecuente en copia y medir distribución.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Máximo y tiempo si disponible; no eliminar casos difíciles sin razón.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.13 · Benchmark justo · 55–60 min (5 min)

**Propósito y contenido específico.** Definir escala fuerte/débil, warmup, repetición, mismo algoritmo y límites de recursos.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Comparar un worker y varios con mismo dato, si entorno permite.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tiempo, configuración y exactitud; no extrapolar desde una corrida.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.14 · ML distribuido · 60–65 min (5 min)

**Propósito y contenido específico.** Explicar diferencia entre procesar datos con Dask y usar algoritmo entrenable sobre particiones; introducir Dask-ML o alternativa verificada.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Comparar flujo que materializa matriz completa con flujo incremental o distribuido.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Algoritmo y estado; no llamar distribuido a fit pandas.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.15 · K-means y clasificación · 65–70 min (5 min)

**Propósito y contenido específico.** Explicar asignación a centroides y actualización agregada; contrastar clasificador o regresor compatible con ruta real.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Calcular una iteración de K-means sobre dos particiones.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Centroides y error; no afirmar todos los estimadores distribuidos.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S13.16 · Cuaderno: verificar entorno · 80–87 min (7 min)

**Propósito y contenido específico.** Ejecutar script de verificación, identificar CPU, workers, memoria y archivos sin descargar repositorio innecesario.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Arrancar cliente Dask y observar dashboard o métricas permitidas.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Configuración efectiva y estado del scheduler.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.17 · Cuaderno: leer lotes · 87–95 min (8 min)

**Propósito y contenido específico.** Leer ocho lotes SECOP preservando esquema y procedencia; observar particiones y filas.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Modificar partición o selección de lote dentro de presupuesto.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo, dtypes y divisiones; no materializar todo por accidente.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.18 · Cuaderno: MapReduce real · 95–102 min (7 min)

**Propósito y contenido específico.** Construir agregaciones Dask y referencia pandas sobre subconjunto comparable.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Cambiar agregación y comprobar igualdad de conteo/suma.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado y tolerancias; conservar errores.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.19 · Cuaderno: medir workers · 102–110 min (8 min)

**Propósito y contenido específico.** Ejecutar configuraciones autorizadas con mismo conjunto y operaciones.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Registrar tiempo, tamaño de datos, workers e hilos; detener si excede presupuesto.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla medida; no inventar speedup.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.20 · Cuaderno: entrenar modelo · 110–117 min (7 min)

**Propósito y contenido específico.** Utilizar algoritmo realmente compatible con Dask, split reproducible y características explicadas.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Entrenar escala viable y evaluar sobre conjunto separado.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métricas, configuración y modo; no afirmar entrenamiento distribuido si hubo collect.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.21 · Cuaderno: exportar resultados · 117–125 min (8 min)

**Propósito y contenido específico.** Persistir predicciones, métricas, perfil de lotes y configuración.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y verificar IDs y equivalencia de controles.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Motor y manifiesto para Spark.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.22 · Reto distribuido · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar combinación nueva de escala, workers o particiones y exigir decisión bajo restricción.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Ejecutar prueba segura y elegir configuración según tiempo y memoria observados.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado propio y alternativa descartada.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.23 · Lectura de dashboard · 130–135 min (5 min)

**Propósito y contenido específico.** Explicar tareas, ocupación, memoria y tiempos cuando sean accesibles; distinguir inferencia y observación.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Identificar cuello de botella con una salida real o captura etiquetada.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia de entorno; no afirmar clúster físico sin prueba.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.24 · Relevo Spark · 135–140 min (5 min)

**Propósito y contenido específico.** Exportar esquema, consulta, split y métricas de referencia para repetir operaciones comparables.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Verificar IDs y tipos de salida que Spark deberá leer.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de comparación.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S13.25 · Cierre Dask · 140–150 min (10 min)

**Propósito y contenido específico.** Retomar hipótesis inicial y contrastar equivalencia, capacidad y rendimiento medido.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles de workers, partición, lazy y entrenamiento con resultados propios.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Motor Dask y límites; medición pendiente no es éxito.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S13

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S13.08 Particiones Dask | Variar particiones con número fijo de archivos. | Cantidad de tareas; particiones diminutas añaden sobrecosto. |
| E2 · S13.10 Reducciones y equivalencia | Variar particiones y comparar suma, conteo y media con pandas. | Equivalencia con tolerancia; orden de filas no necesariamente igual. |
| E3 · S13.13 Benchmark justo | Comparar un worker y varios con mismo dato, si entorno permite. | Tiempo, configuración y exactitud; no extrapolar desde una corrida. |
| E4 · S13.20 Cuaderno: entrenar modelo | Entrenar escala viable y evaluar sobre conjunto separado. | Métricas, configuración y modo; no afirmar entrenamiento distribuido si hubo collect. |

**Producto mínimo:** Motor Dask reproducible con comparaciones de equivalencia, tiempo y entrenamiento. Antes de publicar, ejecutar la ruta base del cuaderno `s13-laboratorio/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb` en Codespaces especializado; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir worker con núcleo, partición con archivo, clúster lógico con máquinas físicas; presentar escalamiento o entrenamiento sin medición.

# S14 · Spark, Databricks, Delta y MLlib

**Pregunta guía:** ¿Cómo ejecutar y entender un pipeline analítico distribuible con planes, joins, persistencia y modelos?

**Entrada:** Datos, esquema, split y operaciones comparables de S13; referencia pandas/Dask.

**Producto y relevo:** Motor Spark con resultados equivalentes, tabla Delta, planes y modelo viable.

**Cuaderno canónico:** `Cuadernos/14_PySpark_Compras_Claras.ipynb`. **Entorno:** Databricks Free Edition o Colab según ruta validada.

**Estado de partida:** Conservar ejercicio P1–P4, broadcast, MERGE, exceptAll, skew, SQL y Delta; verificar compatibilidad y resultados reales.

**Riesgo central:** Confundir Spark local con clúster físico, hint con garantía, collect con distribución o disponibilidad de MLlib en todos los modos serverless.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Motor Spark con resultados equivalentes, tabla Delta, planes y modelo viable**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Databricks Free Edition o Colab según ruta validada de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Datos, esquema, split y operaciones comparables de S13; referencia pandas/Dask** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S14.01 · Por qué Spark ahora · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear necesidad de SQL, planes, almacenamiento transaccional y cómputo de datos amplios después de Dask.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir operación que se comparará bajo igualdad de datos.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Hipótesis de capacidad; no declarar Spark más rápido siempre.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.02 · Relevo Dask · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar esquema, lotes, resultados y configuración de referencia.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Verificar IDs, columnas y split antes de comparar.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato de entrada; no cambiar universo.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.03 · Arquitectura Spark · 5–10 min (5 min)

**Propósito y contenido específico.** Definir driver, executor, tarea y scheduler; distinguir modo local y remoto.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Ubicar componentes en diagrama conceptual y entorno real observado.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Mapa de ejecución; no inferir nodos físicos.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.04 · DataFrame y Spark SQL · 10–15 min (5 min)

**Propósito y contenido específico.** Explicar esquema, filas, expresiones, tipos y diferencia frente a pandas.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Predecir salida de select, filter y groupBy en tabla pequeña.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado manual; operación no necesariamente ejecutada.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.05 · Lazy y acciones · 15–20 min (5 min)

**Propósito y contenido específico.** Distinguir transformación, acción, DAG y optimización de planes.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Comparar construir una consulta y ejecutar count o show.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Grafo y acción; tiempo de definición no es tiempo de ejecución.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.06 · Jobs, stages y tasks · 20–25 min (5 min)

**Propósito y contenido específico.** Explicar límites de etapas por shuffle, tareas por partición y coordinación.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Variar particiones en diagrama y predecir tareas.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteo conceptual; observar UI para evidencia real.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.07 · Planes lógico y físico · 25–30 min (5 min)

**Propósito y contenido específico.** Distinguir plan analizado, optimizado y físico; explicar explain y operadores visibles.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Comparar dos consultas equivalentes y localizar filtro/proyección.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Planes observados o ejemplo etiquetado.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.08 · Particiones y shuffle · 30–35 min (5 min)

**Propósito y contenido específico.** Mostrar intercambio de datos en groupBy y join; distinguir repartition y coalesce según contexto.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Variar clave y particiones y observar distribución.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Perfil y operadores; no afirmar shuffle por dibujo solamente.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.09 · Join y cardinalidad · 35–40 min (5 min)

**Propósito y contenido específico.** Usar tabla P1–P4 y dimensión de códigos; explicar left join y categoría NULL para no coincidencia.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Predecir filas, claves y duplicación si dimensión no es única.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado manual; conservar P4 cuando corresponde.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.10 · Broadcast y sort-merge · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar copia de dimensión pequeña frente a intercambio/ordenamiento; mostrar hints no vinculantes.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Comparar planes con broadcast y MERGE bajo condiciones permitidas.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Operador real, igualdad con exceptAll; no prometer aceleración.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.11 · Skew y claves calientes · 45–50 min (5 min)

**Propósito y contenido específico.** Mostrar distribución desigual y tareas rezagadas, explicar skew_rows y mitigaciones conceptuales.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Variar concentración en datos controlados y comparar máximos.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Perfil de skew; no eliminar filas para mejorar tiempo.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.12 · Delta desde cero · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar archivos Parquet más registro transaccional, versiones y snapshots.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Representar dos commits y lectura de versión en ejemplo.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Historial conceptual; motor debe confirmarlo.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.13 · Medallion y calidad · 55–60 min (5 min)

**Propósito y contenido específico.** Distinguir Bronze, Silver y Gold como capas de responsabilidades y contratos.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Asignar transformaciones y rechazos a capas del caso.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Linaje; no confundir patrón con requisito técnico universal.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.14 · MLlib y pipeline · 60–65 min (5 min)

**Propósito y contenido específico.** Introducir transformadores, estimadores, vector de características, split y evaluación.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Trazar datos de train a modelo y test sin fuga.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato ML; compatibilidad del entorno a verificar.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.15 · Databricks y límites · 65–70 min (5 min)

**Propósito y contenido específico.** Explicar workspace, notebook, compute serverless, tablas y cuotas; revisar capacidades gratuitas actuales.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Elegir ruta válida y distinguir UI real de esquema conceptual.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Preflight; no exigir pago ni configuración no disponible.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S14.16 · Cuaderno: abrir y preparar · 80–87 min (7 min)

**Propósito y contenido específico.** Verificar versión Spark, tipo de compute, catálogo, permisos y dataset antes de ejecutar.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Abrir notebook en entorno limpio y obtener esquema.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado y modo real; alternativa Colab no es Databricks.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.17 · Cuaderno: ETL y SQL · 87–95 min (8 min)

**Propósito y contenido específico.** Leer lotes, filtrar, tipar, agrupar y comparar resultados con referencia.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Modificar expresión de filtro o grupo y comprobar conteos.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla y equivalencia; sin collect de grandes datos.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.18 · Cuaderno: joins y planes · 95–102 min (7 min)

**Propósito y contenido específico.** Ejecutar tablas P1–P4, broadcast y MERGE según soporte; inspeccionar planes.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Comparar exceptAll en ambas direcciones y registrar operadores.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Igualdad y planes; hint puede ser ignorado.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.19 · Cuaderno: Delta · 102–110 min (8 min)

**Propósito y contenido específico.** Escribir tabla aislada, aplicar actualización pequeña y leer historial si entorno lo admite.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Comparar dos versiones y comprobar conservación de identidad.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Historial real o pendiente; no simular transacción como real.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.20 · Cuaderno: modelo Spark · 110–117 min (7 min)

**Propósito y contenido específico.** Usar API ML compatible comprobada o ruta Spark local explícita; separar train, validación y test.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Entrenar modelo viable con features y obtener métrica en test.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Modelo y métricas; no usar collect para entrenar.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.21 · Cuaderno: persistir y entregar · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar tabla Gold, métricas, configuración, planes y predicciones con IDs.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer artefactos y validar contrato.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Motor analítico trazable.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.22 · Reto de optimización · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar join con distribución distinta o nueva consulta, pedir elegir estrategia y validar igualdad.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Modificar hint o partición y contrastar plan y resultado.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Plan propio y decisión; no valorar velocidad sin prueba.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.23 · Interpretación de modelo · 130–135 min (5 min)

**Propósito y contenido específico.** Explicar métrica, baseline, distribución de etiquetas y límites de inferencia.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Comparar resultados y escoger una limitación contextual.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métricas y alternativa; no atribuir causalidad.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.24 · Relevo pipeline confiable · 135–140 min (5 min)

**Propósito y contenido específico.** Exportar versiones de tabla, predicciones e identidad para cambios y reintentos en S15.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Comprobar qué campos necesitan actualización y trazabilidad.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato Gold y modelo.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14.25 · Cierre Spark · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar problema inicial y comparar Dask, Spark y Delta según necesidades, no marcas.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles sobre lazy, shuffle, join, Delta y ML con evidencia propia.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Motor y límites de plataforma; no declarar escala no probada.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S14

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S14.08 Particiones y shuffle | Variar clave y particiones y observar distribución. | Perfil y operadores; no afirmar shuffle por dibujo solamente. |
| E2 · S14.10 Broadcast y sort-merge | Comparar planes con broadcast y MERGE bajo condiciones permitidas. | Operador real, igualdad con exceptAll; no prometer aceleración. |
| E3 · S14.13 Medallion y calidad | Asignar transformaciones y rechazos a capas del caso. | Linaje; no confundir patrón con requisito técnico universal. |
| E4 · S14.20 Cuaderno: modelo Spark | Entrenar modelo viable con features y obtener métrica en test. | Modelo y métricas; no usar collect para entrenar. |

**Producto mínimo:** Motor Spark con resultados equivalentes, tabla Delta, planes y modelo viable. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/14_PySpark_Compras_Claras.ipynb` en Databricks Free Edition o Colab según ruta validada; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir Spark local con clúster físico, hint con garantía, collect con distribución o disponibilidad de MLlib en todos los modos serverless.

# S14A · Laboratorio opcional E2E de escala

**Pregunta guía:** ¿Cómo demostrar entrenamiento sobre una matriz cuyo tamaño supera un presupuesto local explícito sin provocar una caída deliberada?

**Entrada:** Generación sintética distribuida con semilla, contrato de features y baseline pequeño.

**Producto y relevo:** Expediente de capacidad con escala efectiva, dos modelos compatibles, métricas y persistencia.

**Cuaderno canónico:** `Cuadernos/14A_Databricks_E2E_Escala.ipynb`. **Entorno:** Databricks Free Edition sujeto a soporte real; Spark compatible como contingencia diferenciada.

**Estado de partida:** 28 celdas, nueve de código, sin salidas persistidas en archivo inspeccionado; existe ruta Bronze/Silver/Gold y 128 variables, falta demostrar entrenamiento remoto a escala.

**Riesgo central:** MLlib o persistencia de modelo pueden no ser compatibles con modo gratuito actual; no exigir OOM, no llamar prueba de escala a una estimación.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Expediente de capacidad con escala efectiva, dos modelos compatibles, métricas y persistencia**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Databricks Free Edition sujeto a soporte real; Spark compatible como contingencia diferenciada de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Generación sintética distribuida con semilla, contrato de features y baseline pequeño** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S14A.01 · La prueba que falta · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear hipótesis de matriz superior a presupuesto explícito y entrenamiento distribuido completo.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir qué evidencia probaría capacidad sin ejecutar pandas hasta caer.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Criterio falsable; no usar tamaño de archivo como memoria.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.02 · Qué significa opcional · 2–5 min (3 min)

**Propósito y contenido específico.** Aclarar independencia de notas y condiciones de cuota; distinguir ruta segura y ampliación voluntaria.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Seleccionar escala de práctica o ampliación según entorno.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado elegido; no obligar a comprar.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.03 · Datos sintéticos honestos · 5–10 min (5 min)

**Propósito y contenido específico.** Explicar simulación, semilla, distribución y etiquetas generadas; no confundir con contratación real.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Variar semilla pequeña y observar reproducibilidad.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato sintético; métricas no generalizan al SECOP real.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.04 · Presupuesto de memoria · 10–15 min (5 min)

**Propósito y contenido específico.** Derivar límite inferior de matriz N por D por bytes; agregar advertencia de overhead y copias.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Variar N, 128 variables y dtype; comparar con presupuesto explícito.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Bytes mínimos; no presentarlos como pico de pandas.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.05 · Generación distribuida · 15–20 min (5 min)

**Propósito y contenido específico.** Explicar range, expresiones deterministas y particiones sin crear listas gigantes en driver.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Variar particiones en ejemplo seguro y verificar IDs.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Cobertura; no materializar datos completos.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.06 · Bronze, Silver, Gold · 20–25 min (5 min)

**Propósito y contenido específico.** Representar datos crudos, limpieza, rechazos y features con identidades y versiones.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Asignar transformaciones a capas y predecir conteos.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Contrato por capa; sintético no elimina necesidad de calidad.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.07 · Split reproducible · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar asignación determinista por identidad, estratificación cuando procede y separación de evaluación.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Variar semilla y medir distribución sin solapamiento.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs disjuntos y proporciones; no usar test para ajustar.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.08 · Features y vector · 30–35 min (5 min)

**Propósito y contenido específico.** Definir matriz, columna vectorial y transformadores de características.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Calcular dimensión en pequeño conjunto y comprobar columnas.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dimensión efectiva; no materializar matriz completa.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.09 · Baseline y fuga · 35–40 min (5 min)

**Propósito y contenido específico.** Distinguir baseline, variable objetivo, leakage y transformaciones ajustadas solo con train.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Detectar feature que revela etiqueta y seleccionar exclusión.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Control de fuga; no confundir métricas perfectas con éxito.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.10 · Modelo lineal · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar regresión logística o modelo compatible, función de pérdida e iteraciones conceptuales.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Variar parámetro en escala pequeña y comparar métricas.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Configuración; no asumir soporte hasta preflight.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.11 · Segundo modelo · 45–50 min (5 min)

**Propósito y contenido específico.** Contrastar modelo lineal y alternativa compatible de árboles u otro estimador explícito.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Comparar recursos y resultados en escala controlada.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Dos modelos realmente ejecutados si compatibles; no inventar.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.12 · Métricas de clasificación · 50–55 min (5 min)

**Propósito y contenido específico.** Definir matriz de confusión, precisión, recall y AUC cuando aplica.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Calcular métricas manualmente de tabla pequeña y variar umbral.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Métrica y denominador; no usar solo accuracy.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.13 · Escala escalonada · 55–60 min (5 min)

**Propósito y contenido específico.** Diseñar tamaños crecientes limitados por cuota y presupuesto, con parada antes de OOM.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Seleccionar siguiente escala según resultado y estado del entorno.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Registro de decisión; no ejecutar tamaños gigantes automáticamente.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.14 · Compatibilidad y quota · 60–65 min (5 min)

**Propósito y contenido específico.** Verificar documentación y prueba mínima de APIs ML, persistencia y compute del plan gratuito.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Clasificar soporte real de cada operación o elegir contingencia.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz de compatibilidad; no afirmar MLlib remoto sin prueba.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.15 · Criterio de evidencia · 65–70 min (5 min)

**Propósito y contenido específico.** Definir éxito como filas train realmente usadas, dimensión, modelo completado y métricas; incluir memoria solo si medida.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Evaluar expediente ficticio incompleto y detectar dato ausente.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist falsable; estimación no es éxito experimental.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S14A.16 · Cuaderno: preflight y escala · 80–87 min (7 min)

**Propósito y contenido específico.** Abrir entorno limpio, verificar versión, APIs, permisos, recursos y semilla.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar muestra mínima antes de autorizar escala.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Compatibilidad real; bloquear aumento si falla.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.17 · Cuaderno: generar Bronze · 87–95 min (8 min)

**Propósito y contenido específico.** Crear datos sintéticos distribuidos y persistir con identidad, sin collect de gran escala.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar escala inicial y comprobar conteos y duplicados.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** N efectivo y versión; no inferir capacidad desde objetivo.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.18 · Cuaderno: transformar y split · 95–102 min (7 min)

**Propósito y contenido específico.** Limpiar, separar rechazos y asignar particiones train/validación/test reproducibles.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Verificar intersecciones vacías y distribución de etiquetas.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Silver y split; sin fuga.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.19 · Cuaderno: construir Gold · 102–110 min (8 min)

**Propósito y contenido específico.** Generar 128 variables u otra dimensión declarada, verificar schema y estimación mínima.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Comparar presupuesto local y dimensión efectiva.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Gold y bytes mínimos; no provocar OOM.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.20 · Cuaderno: entrenar dos modelos · 110–117 min (7 min)

**Propósito y contenido específico.** Ejecutar solo estimadores comprobados sobre todo train en escala aprobada; registrar duración y errores.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Comparar modelo uno y dos o declarar limitación de plataforma.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia de fit real, N y métrica; no sustituir por cache.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.21 · Cuaderno: persistir expediente · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar predicciones, configuración, métricas y modelo si entorno soporta; verificar relectura.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Reutilizar predicciones o modelo según capacidad real.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Artefactos persistidos; ruta alternativa explícita.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.22 · Reto de capacidad · 125–130 min (5 min)

**Propósito y contenido específico.** Pedir nueva escala o presupuesto y decisión de detener o continuar basada en evidencia.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Cambiar configuración segura y comparar resultado efectivo.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Prueba propia; no exigir que exceda recursos reales de cada estudiante.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.23 · Lectura crítica de resultados · 130–135 min (5 min)

**Propósito y contenido específico.** Distinguir tamaño teórico, uso observado, latencia, throughput y generalización.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar afirmaciones respaldadas por expediente propio.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Límite concreto; no confundir entrenamiento con utilidad.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.24 · Relevo predicciones · 135–140 min (5 min)

**Propósito y contenido específico.** Definir contrato de métricas y predicciones para S15/S16 sin incorporar resultados sintéticos como reales.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar identificadores y marcar origen sintético.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Producto de capacidad separado del observatorio real.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S14A.25 · Cierre escala · 140–150 min (10 min)

**Propósito y contenido específico.** Evaluar hipótesis inicial únicamente si N efectivo, dimensión y fit están demostrados.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Seleccionar estado logrado, parcial o bloqueado con evidencia.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Expediente; no declarar éxito por tamaño planeado.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S14A

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S14A.08 Features y vector | Calcular dimensión en pequeño conjunto y comprobar columnas. | Dimensión efectiva; no materializar matriz completa. |
| E2 · S14A.10 Modelo lineal | Variar parámetro en escala pequeña y comparar métricas. | Configuración; no asumir soporte hasta preflight. |
| E3 · S14A.13 Escala escalonada | Seleccionar siguiente escala según resultado y estado del entorno. | Registro de decisión; no ejecutar tamaños gigantes automáticamente. |
| E4 · S14A.20 Cuaderno: entrenar dos modelos | Comparar modelo uno y dos o declarar limitación de plataforma. | Evidencia de fit real, N y métrica; no sustituir por cache. |

**Producto mínimo:** Expediente de capacidad con escala efectiva, dos modelos compatibles, métricas y persistencia. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/14A_Databricks_E2E_Escala.ipynb` en Databricks Free Edition sujeto a soporte real; Spark compatible como contingencia diferenciada; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: MLlib o persistencia de modelo pueden no ser compatibles con modo gratuito actual; no exigir OOM, no llamar prueba de escala a una estimación.

# S15 · Pipelines confiables, actualizaciones y recuperación

**Pregunta guía:** ¿Cómo mantener un producto actualizado sin duplicar datos, perder versiones ni confundir llegada con procesamiento?

**Entrada:** RAW, Silver/Gold, predicciones y manifiestos de sesiones previas.

**Producto y relevo:** Pipeline repetible con estados, rechazos, checkpoint y pruebas de recuperación.

**Cuaderno canónico:** `Cuadernos/15_Pipeline_Confiable.ipynb`. **Entorno:** Colab, Spark opcional según compatibilidad.

**Estado de partida:** Propuesta formativa no evaluable; conservar el diseño de confiabilidad y validar notebook completo y ampliación Spark antes de declarar ejecución.

**Riesgo central:** Confundir reintento con idempotencia, batch con streaming real, checkpoint con backup y exactly-once con garantía universal.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Pipeline repetible con estados, rechazos, checkpoint y pruebas de recuperación**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab, Spark opcional según compatibilidad de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **RAW, Silver/Gold, predicciones y manifiestos de sesiones previas** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S15.01 · Actualizar Compras Claras · 0–2 min (2 min)

**Propósito y contenido específico.** Plantear llegada de registros nuevos y correcciones sin duplicar expedientes ni perder historia.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Elegir qué debe cambiar y qué debe conservarse.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Requisitos de actualización; no alterar nota.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.02 · Relevo de estados · 2–5 min (3 min)

**Propósito y contenido específico.** Recuperar contrato, versiones, predicciones y claves de salida; distinguir fuentes reales y sintéticas.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Comprobar identidad, timestamp y versión antes de actualizar.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada compatible; no mezclar orígenes.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.03 · Batch, microbatch y streaming · 5–10 min (5 min)

**Propósito y contenido específico.** Definir modalidades por unidad de trabajo y disponibilidad de datos; mostrar línea temporal.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Variar intervalo y comparar demora y tamaño de lote.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Latencia conceptual; microbatch no equivale a evento individual.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.04 · Tiempo de evento y llegada · 10–15 min (5 min)

**Propósito y contenido específico.** Explicar evento, ingesta y procesamiento con registros fuera de orden.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Ordenar registros por ambos tiempos y observar diferencia.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Secuencia y tardanza; no usar llegada como fecha de negocio.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.05 · Identidad e idempotencia · 15–20 min (5 min)

**Propósito y contenido específico.** Definir que repetir operación produce mismo estado bajo claves y reglas explícitas.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Reprocesar lote de tres registros y comparar append con upsert.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos; no asumir idempotencia por reintento.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.06 · Transacción y atomicidad · 20–25 min (5 min)

**Propósito y contenido específico.** Mostrar unidad de cambio, commit, rollback y límites de operación atómica.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Interrumpir actualización conceptual entre dos pasos.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estados posibles; atomicidad depende del sistema.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.07 · Checkpoint y offset · 25–30 min (5 min)

**Propósito y contenido específico.** Explicar progreso durable y posición de lectura; distinguir estado de datos y marcador de avance.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Variar offset tras fallo y detectar hueco o repetición.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Posiciones; checkpoint no es copia de seguridad.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.08 · Reintentos y backoff · 30–35 min (5 min)

**Propósito y contenido específico.** Definir error transitorio, permanente, límite de intentos y espera creciente.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Clasificar errores y simular tres intentos limitados.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estados y tiempos conceptuales; no reintentar indefinidamente.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.09 · Rechazos y cuarentena · 35–40 min (5 min)

**Propósito y contenido específico.** Distinguir válido, inválido y pendiente; conservar motivo y origen de rechazo.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Inyectar cambio de tipo y localizar cuarentena.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conteos conservados; no borrar registros inválidos.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.10 · Cambio de esquema · 40–45 min (5 min)

**Propósito y contenido específico.** Explicar adición compatible, cambio de tipo, renombrado y migración versionada.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Probar dos cambios con contrato y decidir compatibilidad.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado de validación; no autoaceptar todo.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.11 · Duplicados tardíos · 45–50 min (5 min)

**Propósito y contenido específico.** Mostrar evento repetido después de actualización y criterio de última versión por fuente.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Variar orden de llegada de versiones y comparar estado.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Versión seleccionada; llegada más reciente no siempre válida.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.12 · Watermark conceptual · 50–55 min (5 min)

**Propósito y contenido específico.** Explicar ventana temporal, tolerancia de tardanza y descarte o manejo según política.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Variar tolerancia y observar qué eventos se admiten.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conjunto esperado; no llamar streaming real a simulación.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.13 · Delta y versiones · 55–60 min (5 min)

**Propósito y contenido específico.** Recuperar historial y lectura de snapshots; mostrar diferencia entre recuperar versión y borrar cambios.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Comparar dos estados y elegir restauración bajo permiso.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Versiones; no asumir rollback disponible en todos los motores.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.14 · Observabilidad · 60–65 min (5 min)

**Propósito y contenido específico.** Definir métricas de filas, latencia, errores, frescura, duplicados y trazas de ejecución.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Variar fallo en lote y detectar alerta por reconciliación.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Indicadores y umbral; no inferir causa solo por alerta.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.15 · Prueba de recuperación · 65–70 min (5 min)

**Propósito y contenido específico.** Definir inyección controlada de fallo, estado inicial, reinicio y condición de igualdad.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Comparar ejecución completa y ejecución interrumpida con reintento.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado esperado; no manipular servicio de producción.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S15.16 · Cuaderno: preparar estado · 80–87 min (7 min)

**Propósito y contenido específico.** Cargar entradas y versión inicial en entorno aislado; establecer identidad y manifiesto.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar preflight y verificar conteos.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado base reproducible.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.17 · Cuaderno: procesar lote · 87–95 min (8 min)

**Propósito y contenido específico.** Construir validación, transformación y upsert visible; reconciliar entradas y estados.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar lote y repetirlo.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Igualdad de estado; no contar dos veces.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.18 · Cuaderno: cambiar esquema · 95–102 min (7 min)

**Propósito y contenido específico.** Introducir registro con cambio compatible e incompatible en copia de práctica.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Ejecutar validación y cuarentena.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Aceptados/rechazados y motivo.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.19 · Cuaderno: simular fallo · 102–110 min (8 min)

**Propósito y contenido específico.** Interrumpir en punto controlado y conservar checkpoint/estado según implementación.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Reanudar y comparar con ejecución limpia.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Recuperación real del laboratorio; no afirmar garantía externa.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.20 · Cuaderno: actualización incremental · 110–117 min (7 min)

**Propósito y contenido específico.** Procesar lote tardío o corrección con política versionada y relectura.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Variar orden de eventos y comparar estado final.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Identidad y versión; no sobrescribir RAW.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.21 · Cuaderno: exportar observabilidad · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar logs, conteos, estado, versiones y evidencia de reejecución.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Releer y comprobar reconciliación y hash.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Pipeline verificable y trazable.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.22 · Reto de recuperación · 125–130 min (5 min)

**Propósito y contenido específico.** Entregar orden de eventos o error diferente y pedir configurar recuperación sin duplicar.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Ejecutar variante segura y comprobar invariantes.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado propio y estado final.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.23 · Lectura de confiabilidad · 130–135 min (5 min)

**Propósito y contenido específico.** Distinguir disponibilidad, durabilidad, consistencia y recuperación; evaluar límite de laboratorio.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar garantía probada y garantía no probada con evidencia.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión contextual; no afirmar exactly-once universal.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.24 · Relevo integración · 135–140 min (5 min)

**Propósito y contenido específico.** Exportar manifiesto de actualización y tabla de estado que S16 podrá consultar.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Comprobar compatibilidad de identificadores y versiones.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Entrada confiable del producto.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S15.25 · Cierre pipeline · 140–150 min (10 min)

**Propósito y contenido específico.** Recuperar necesidad de actualización y verificar que invariantes resisten la prueba de fallo.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Resolver controles de checkpoint, versión y reintento.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado y trazas; S15 sigue formativa.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S15

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S15.08 Reintentos y backoff | Clasificar errores y simular tres intentos limitados. | Estados y tiempos conceptuales; no reintentar indefinidamente. |
| E2 · S15.10 Cambio de esquema | Probar dos cambios con contrato y decidir compatibilidad. | Resultado de validación; no autoaceptar todo. |
| E3 · S15.13 Delta y versiones | Comparar dos estados y elegir restauración bajo permiso. | Versiones; no asumir rollback disponible en todos los motores. |
| E4 · S15.20 Cuaderno: actualización incremental | Variar orden de eventos y comparar estado final. | Identidad y versión; no sobrescribir RAW. |

**Producto mínimo:** Pipeline repetible con estados, rechazos, checkpoint y pruebas de recuperación. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/15_Pipeline_Confiable.ipynb` en Colab, Spark opcional según compatibilidad; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Confundir reintento con idempotencia, batch con streaming real, checkpoint con backup y exactly-once con garantía universal.

# S16 · Integración, evaluación y defensa del producto

**Pregunta guía:** ¿Puede el estudiante demostrar un producto de datos útil, verificable y reproducible que integra las capacidades enseñadas?

**Entrada:** Artefactos reales de S01–S15, rúbrica vigente del proyecto, contratos y evidencia de ejecución.

**Producto y relevo:** Compras Claras V3, paquete de evidencia y defensa según reglas vigentes.

**Cuaderno canónico:** `Cuadernos/Proyecto_Final_Compras_Claras.ipynb`. **Entorno:** Colab y entornos de producto aprobados.

**Estado de partida:** Conservar E0–E7, rúbrica y defensa; falta integrar predicciones reales de Spark donde corresponda y verificar autonomía y navegación.

**Riesgo central:** Introducir criterios después de anunciar el proyecto, usar datos sintéticos como reales, publicar datos personales o confundir prototipo con sistema de producción.

## Objetivos observables y alineamiento
Al terminar, el estudiante debe poder ejecutar o demostrar las capacidades especificadas en las pantallas 07 a 15, completar el producto mínimo de las pantallas 16 a 21 y transferirlo mediante las pantallas 22 a 25. En las sesiones de taller y defensa, los objetivos evaluativos siguen siendo exclusivamente los vigentes; las capacidades de repaso no agregan puntos. La evidencia fundamental de esta sesión es **Compras Claras V3, paquete de evidencia y defensa según reglas vigentes**; se verifica mediante acciones, archivos y resultados propios. El docente conserva referencias de ejemplo independientes y diferencia la disponibilidad de Colab y entornos de producto aprobados de la comprensión conceptual. No se concluye que un objetivo se logró hasta observar su evidencia. El alcance de los resultados se restringe a **Artefactos reales de S01–S15, rúbrica vigente del proyecto, contratos y evidencia de ejecución** y a sus fuentes verificadas.

## Secuencia de 25 diapositivas (150 minutos incluyendo pausa)

### S16.01 · Qué debe defenderse · 0–2 min (2 min)

**Propósito y contenido específico.** Mostrar pregunta del producto, rúbrica y alcance vigente; distinguir capacidades de herramientas obligatorias.

**Diseño de la enseñanza (Apertura y problema).** Abrir con la pregunta profesional antes de nombrar una tecnología. Mostrar el caso concreto y solicitar una decisión inicial sin revelar la respuesta. Registrar la elección como diagnóstico, no como nota. El diseño debe permitir que la misma decisión se recupere al final.

**Acción observable.** Seleccionar requisito y artefacto que lo respalda.

**Representación y composición.** Una situación, una pregunta y una visualización del dato de entrada; sin portada decorativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Matriz oficial; no cambiar condiciones.

**Criterio de construcción y QA.** Verificar que la pregunta puede resolverse con los productos de esta sesión y que no presupone conocimiento nuevo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.02 · Estado de integración · 2–5 min (3 min)

**Propósito y contenido específico.** Identificar qué módulos tienen evidencia real, simulada, pendiente o sintética.

**Diseño de la enseñanza (Diagnóstico y contrato).** Identificar qué sabe el grupo y qué insumo existe realmente. Presentar dos o tres opciones con distractores plausibles y dar retroalimentación inmediata. Si el insumo anterior no está disponible, usar una referencia congelada con procedencia explícita, no bloquear a quien llega sin ese estado.

**Acción observable.** Clasificar artefactos por procedencia y disponibilidad.

**Representación y composición.** Comparación breve y control de selección con retroalimentación visible. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Inventario verificable; no encubrir brechas.

**Criterio de construcción y QA.** Comprobar que la referencia y la entrada propia tienen el mismo contrato; registrar diferencias sin ocultarlas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.03 · Arquitectura de extremo a extremo · 5–10 min (5 min)

**Propósito y contenido específico.** Recorrer fuente, ingesta, motores, multimedia, búsqueda, analítica y servicio según producto vigente.

**Diseño de la enseñanza (Fundamento 1).** Construir vocabulario desde una representación concreta. Nombrar cada parte antes de utilizarla, explicar por qué existe y mostrar qué cambiaría si se elimina. Resolver un ejemplo corto antes de pasar a código. Dar oportunidad al estudiante de anticipar un resultado y corregir su interpretación.

**Acción observable.** Vincular módulos con entradas y salidas reales.

**Representación y composición.** Diagrama anotado o tabla de pocas filas con unidad, identidad y dirección explícitas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Diagrama de interfaces; no agregar obligación.

**Criterio de construcción y QA.** El ejemplo debe poder resolverse manualmente; los términos nuevos se definen antes de emplearse. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.04 · Identidad y contrato · 10–15 min (5 min)

**Propósito y contenido específico.** Revisar claves que unen RAW, expediente, activo y predicción; detectar cardinalidad múltiple.

**Diseño de la enseñanza (Fundamento 2).** Relacionar el nuevo concepto con el anterior y con el problema. Contrastar dos configuraciones o estados que solo cambien una variable relevante. Explicar el mecanismo, no solo las etiquetas; dejar visible la relación entre entrada y resultado. Solicitar una predicción rápida antes de mostrar la comparación.

**Acción observable.** Comprobar compatibilidad con registros propios.

**Representación y composición.** Comparación de estados con cambio resaltado y leyenda persistente. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Reporte de identidad; no forzar joins por nombre.

**Criterio de construcción y QA.** Verificar equivalencia de los elementos que se mantienen constantes y marcar cualquier supuesto del ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.05 · Linaje de evidencia · 15–20 min (5 min)

**Propósito y contenido específico.** Mostrar cómo abrir fuente desde un resultado o predicción y cómo recuperar versión.

**Diseño de la enseñanza (Fundamento 3).** Desarrollar la regla de funcionamiento con cantidades, tipos o propiedades explícitas. Enseñar cómo se lee la representación y qué observación permitiría distinguir una interpretación equivocada. Incorporar un ejemplo numérico o estructural resuelto y hacer que el estudiante modifique una entrada pequeña.

**Acción observable.** Seguir un hit del observatorio a su origen.

**Representación y composición.** Tabla o esquema del mecanismo con una operación explicada por pasos. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Traza navegable; no mostrar datos privados.

**Criterio de construcción y QA.** El resultado didáctico se calcula o deriva; no se fabrica una captura de una plataforma. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.06 · Calidad transversal · 20–25 min (5 min)

**Propósito y contenido específico.** Revisar conteos de entradas, éxitos, rechazos y pendientes por etapa.

**Diseño de la enseñanza (Fundamento 4).** Cerrar la base conceptual con una decisión de diseño. Comparar dos alternativas y señalar qué requisito hace preferible una de ellas en este caso. Presentar un contraejemplo donde la elección cambia. Comprobar comprensión con una decisión estructurada que dependa del escenario.

**Acción observable.** Detectar discrepancia de identidad o cobertura con sus artefactos.

**Representación y composición.** Matriz de alternativas con criterios y limitaciones, no una lista de marcas. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Reconciliación; no declarar cero fallos sin prueba.

**Criterio de construcción y QA.** Evitar rankings universales y confirmar que la conclusión se sostiene bajo las condiciones declaradas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.07 · Recuperación lexical y semántica · 25–30 min (5 min)

**Propósito y contenido específico.** Comparar resultados de búsqueda por palabras y significado en mismo corpus y filtros.

**Diseño de la enseñanza (Ejemplo resuelto 1).** Preparar un conjunto pequeño y mostrar los datos antes de transformarlos. Realizar la operación paso a paso, dejando los estados intermedios visibles y nombrando lo que significa cada salida. El estudiante predice el siguiente estado y contrasta su elección con el cálculo mostrado.

**Acción observable.** Ejecutar consulta de prueba y comprobar fuente.

**Representación y composición.** Entrada, transformación y salida alineadas en una sola lectura, con números legibles. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ranking y métrica cuando aplica; no inventar juicio.

**Criterio de construcción y QA.** Comprobar manualmente estados intermedios y resultado; indicar si se trata de datos reales, recorte o ejemplo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.08 · Multimedia integrada · 30–35 min (5 min)

**Propósito y contenido específico.** Revisar página OCR, segmento ASR, activos y metadata enlazados.

**Diseño de la enseñanza (Experimento 1).** Convertir la explicación en un experimento causal de juguete, no una animación decorativa. Fijar el estado inicial, anticipar la dirección del cambio, variar un parámetro y comparar un indicador pertinente. La interfaz debe permitir reiniciar y mostrar tanto el caso normal como un contraejemplo útil.

**Acción observable.** Abrir evidencia correspondiente a un resultado real.

**Representación y composición.** Control manipulable junto al resultado actualizado y a la comparación de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Página/intervalo y origen; no reconstruir contenido.

**Criterio de construcción y QA.** Probar valores mínimo, inicial y máximo, invariantes y tratamiento de entradas inválidas; no extrapolar a un motor real. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.09 · Analítica distribuida · 35–40 min (5 min)

**Propósito y contenido específico.** Examinar resultados, configuración, equivalencia y métrica de Dask/Spark cuando corresponda.

**Diseño de la enseñanza (Ejemplo resuelto 2).** Enseñar cómo una representación o cálculo responde a una consulta profesional. Comparar la salida con un control independiente cuando resulte posible. Explicar cómo se lee, qué dice, qué no permite concluir y el error común. Solicitar identificación de una fila, valor o propiedad concreta.

**Acción observable.** Seleccionar salida que prueba procesamiento y distinguir modo local/remoto.

**Representación y composición.** Tabla con encabezados, unidades y anotación de la fila o dato que se interpreta. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia auténtica; no prometer clúster.

**Criterio de construcción y QA.** Verificar el control contra la entrada y comprobar que la interpretación no excede el alcance del dato. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.10 · Predicciones y evaluación · 40–45 min (5 min)

**Propósito y contenido específico.** Revisar split, features, métricas y correspondencia entre IDs y predicciones.

**Diseño de la enseñanza (Experimento 2).** Aislar una segunda variable con relación distinta de la anterior. Formular una predicción, ejecutar dos configuraciones comparables y pedir que se identifique el cambio observado. Explicar por qué una medición conceptual y una ejecución auténtica responden preguntas diferentes. Mantener visibles las condiciones fijas.

**Acción observable.** Verificar que predicción conserva modelo y fecha.

**Representación y composición.** Gráfico o comparación de dos resultados con parámetro visible y punto de referencia. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Tabla y metadata; no demostrar causalidad.

**Criterio de construcción y QA.** Validar resultado de ambas configuraciones y especificar qué se midió, calculó o simuló. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.11 · Uso profesional · 45–50 min (5 min)

**Propósito y contenido específico.** Traducir una pregunta del usuario a consulta del observatorio y respuesta sustentada.

**Diseño de la enseñanza (Ejemplo resuelto 3).** Introducir un caso donde la aplicación mecánica de una regla conduce a un resultado incorrecto. Mostrar primero el contraejemplo, luego la corrección y finalmente la condición bajo la cual funciona. Pedir una elección entre interpretaciones apoyadas en datos, con retroalimentación para cada alternativa.

**Acción observable.** Elegir acción de priorización y dato necesario adicional.

**Representación y composición.** Dos caminos comparados con el punto exacto de divergencia resaltado. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Decisión contextual; no acusación.

**Criterio de construcción y QA.** Comprobar que el caso incorrecto es plausible y que la corrección no elimina un requisito del problema. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.12 · Confiabilidad y versiones · 50–55 min (5 min)

**Propósito y contenido específico.** Examinar qué pasa al repetir actualización o cambiar una fuente bajo capacidades implementadas.

**Diseño de la enseñanza (Demostración de mecanismo).** Pasar de la representación manual al mecanismo de una herramienta o algoritmo. Identificar entrada, parámetros relevantes, operación y salida; si la ejecución externa no está confirmada, mostrar un cálculo didáctico inequívocamente identificado. El estudiante localiza un elemento de la salida antes de interpretar.

**Acción observable.** Verificar último manifiesto o prueba de recuperación disponible.

**Representación y composición.** Código breve o interfaz conceptual al lado de una salida anotada, no captura inventada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Estado y límites; no exigir S15 si no está en rúbrica.

**Criterio de construcción y QA.** Vincular a la celda o fuente que producirá esa salida; verificar versión y disponibilidad del motor antes de enseñar. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.13 · Diseño y accesibilidad · 55–60 min (5 min)

**Propósito y contenido específico.** Revisar navegación, lectura, estados vacíos, errores y contraste en flujo del producto.

**Diseño de la enseñanza (Experimento 3).** Probar un escenario alternativo que revele el costo o límite de una decisión. Conservar datos y objetivo comparables, modificar el parámetro indicado y observar la consecuencia. Si la métrica depende de red o plataforma, registrar ese contexto. La retroalimentación debe separar observación de hipótesis.

**Acción observable.** Ejecutar prueba de acceso desde portada y abrir un resultado.

**Representación y composición.** Control de escenario, indicador y comparación; advertencia cuando la salida sea conceptual. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Ruta funcional; no confundir UI bonita con producto.

**Criterio de construcción y QA.** Revisar que no se atribuye causalidad a una comparación no controlada ni se presentan métricas fabricadas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.14 · Seguridad y publicación · 60–65 min (5 min)

**Propósito y contenido específico.** Revisar datos personales, secretos, permisos y créditos; distinguir repo y servicio desplegado.

**Diseño de la enseñanza (Interpretación y decisión).** Comparar dos respuestas y construir una decisión bajo condiciones explícitas. Señalar el dato adicional que permitiría validar una afirmación más fuerte. El estudiante elige una alternativa en función de la evidencia disponible y recibe explicación específica, no una felicitación genérica. Preparar transición al laboratorio.

**Acción observable.** Comprobar salida de higiene sin revelar información sensible.

**Representación y composición.** Matriz de decisión con evidencias y un límite visible por alternativa. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Checklist de publicación; no rotar claves ajenas.

**Criterio de construcción y QA.** Verificar que cada alternativa tenga un criterio observable; no exigir texto libre para enviar respuesta académica. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.15 · Defensa basada en evidencia · 65–70 min (5 min)

**Propósito y contenido específico.** Explicar cómo mostrar decisión, alternativa, resultado y límite según rúbrica y formato autorizado.

**Diseño de la enseñanza (Diseño del laboratorio).** Presentar la hipótesis o problema que se comprobará después del descanso. Mostrar entrada, pasos, resultado esperado como contrato, condición de parada y ruta de contingencia. Diferenciar la práctica mínima auténtica de la ampliación opcional. El estudiante debe saber exactamente qué producto tendrá al terminar.

**Acción observable.** Preparar recorrido verificable sin crear nuevas exigencias.

**Representación y composición.** Mapa de laboratorio con flechas, anclas al cuaderno y artefactos, sin tercer recurso obligatorio. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Guía de defensa; no publicar soluciones ni calificaciones.

**Criterio de construcción y QA.** Confirmar que la preparación y ejecución mínima caben en el tiempo; no esconder requisitos de cuentas o descargas. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### Pausa · 70–80 min (no computa como diapositiva)
Pausar la proyección, conservar estado del notebook y permitir recuperación de conexión antes de continuar. Si el entorno requiere preparación anticipada, ejecutarla antes de clase con datos y cuentas autorizados; no convertir el descanso en tiempo obligatorio de instalación. Reanudar con el mapa de la práctica y el estado de la entrada.

### S16.16 · Integración: importar estados · 80–87 min (7 min)

**Propósito y contenido específico.** Abrir notebook o aplicación y cargar artefactos propios por contrato, no manualmente dispersos.

**Diseño de la enseñanza (Laboratorio 1: preflight).** Abrir el segundo recurso desde la presentación, indicar la celda estable de preparación y ejecutarla en entorno limpio. Explicar brevemente las dependencias que se verifican y el estado de la fuente. Si falla, detener la ampliación, registrar el error y activar solo una contingencia previamente probada.

**Acción observable.** Ejecutar preflight y localizar dependencias faltantes.

**Representación y composición.** Checklist de pasos, estado de entorno y enlace directo a la celda o sección. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Inventario real; fixture no sustituye entrega.

**Criterio de construcción y QA.** Prueba en entorno limpio, sin credenciales visibles; la salida de referencia no se registra como ejecución personal. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.17 · Integración: conectar fuentes · 87–95 min (8 min)

**Propósito y contenido específico.** Vincular expedientes, activos, consultas y predicciones usando claves verificadas.

**Diseño de la enseñanza (Laboratorio 2: lectura guiada).** Enseñar la primera operación importante con código visible, explicando los argumentos utilizados y qué devuelve. Ejecutar un caso resuelto en la entrada acordada y detenerse ante la salida para leerla. El estudiante reproduce el procedimiento, identifica un valor o propiedad y lo contrasta con el control.

**Acción observable.** Ejecutar prueba de cardinalidad y resolver discrepancia.

**Representación y composición.** Correspondencia presentación-celda-salida con resaltado de la operación importante. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** IDs y resultados; no fabricar vínculos.

**Criterio de construcción y QA.** Reejecutar la celda y comprobar dependencia, resultado y estado; no ocultar la función que constituye el objetivo. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.18 · Integración: ejecutar consulta · 95–102 min (7 min)

**Propósito y contenido específico.** Realizar escenario de uso end-to-end según alcance de rúbrica.

**Diseño de la enseñanza (Laboratorio 3: modificación).** Reducir el apoyo a un hueco, parámetro o elección identificada, sin exigir reescribir todo el cuaderno. Pedir una predicción antes de ejecutar y comparar el resultado con el caso resuelto. La retroalimentación debe indicar qué significa un fallo y dónde recuperar el estado.

**Acción observable.** Consultar y abrir evidencia propia con fuente y versión.

**Representación y composición.** Editor de código del cuaderno y comparación de resultados propios con el contrato. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Resultado consultable y traza.

**Criterio de construcción y QA.** Probar una modificación válida y una inválida; conservar procedencia y evitar pasos manuales innecesarios. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.19 · Integración: verificar modelo · 102–110 min (8 min)

**Propósito y contenido específico.** Comprobar métrica, split y predicción cuando sea parte del proyecto; separar fuentes sintéticas.

**Diseño de la enseñanza (Laboratorio 4: control independiente).** Hacer que el estudiante compruebe su resultado mediante un método diferente o un invariante explícito. Enseñar a leer el error cuando falla la comprobación y localizar la etapa responsable. El resultado esperado es una propiedad verificable, no un valor inventado que todos deban copiar.

**Acción observable.** Releer predicciones y validar claves con producto.

**Representación y composición.** Tabla de comprobación con estado, diferencia observada y condición de éxito. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Evidencia o estado parcial documentado.

**Criterio de construcción y QA.** Ejecutar caso de igualdad y caso de fallo cuando sea viable; dejar registro del método, datos y tolerancia. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.20 · Integración: validar recuperación · 110–117 min (7 min)

**Propósito y contenido específico.** Ejecutar relectura y repetición de pasos permitidos dentro de presupuesto.

**Diseño de la enseñanza (Experimento 4: ejecución).** Ejecutar la variante auténtica central de la sesión con datos comparables y una configuración segura. Registrar parámetros, entrada, versión, resultados, errores y tiempo si es pertinente. No aumentar escala sin comprobar el caso mínimo. En el taller evaluativo, esta instrucción es un control de evidencia, nunca una solución.

**Acción observable.** Comparar conteos y contratos antes/después.

**Representación y composición.** Panel de resultados de la ejecución, indicador de modo y configuración efectiva. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Prueba reproducible; no repetir benchmarks pesados.

**Criterio de construcción y QA.** Verificar que el motor o procedimiento realmente se ejecutó; marcar pendiente o bloqueado cuando el entorno no lo permite. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.21 · Integración: empaquetar producto · 117–125 min (8 min)

**Propósito y contenido específico.** Guardar código, manifiestos, enlaces y documentación requerida por entrega vigente.

**Diseño de la enseñanza (Laboratorio 5: producto).** Convertir las salidas anteriores en un artefacto reutilizable. Explicar identidad, esquema, procedencia y cómo se lee el archivo o estado exportado. Ejecutar la relectura y comparar el resultado con el contrato. No aceptar una captura de pantalla como sustituto de un archivo o consulta requerida.

**Acción observable.** Verificar acceso de docente sin datos sensibles.

**Representación y composición.** Mapa de artefactos con rutas, versión y estado de verificación. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Paquete y traza; mantener permisos adecuados.

**Criterio de construcción y QA.** Comprobar relectura y compatibilidad; no incluir credenciales ni identificadores privados de estudiantes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.22 · Demostración o defensa · 125–130 min (5 min)

**Propósito y contenido específico.** Reservar bloque para escenario ejecutado por estudiante según formato oficial; ajustar distribución al número real de equipos.

**Diseño de la enseñanza (Transferencia autónoma).** Proponer una variación nueva que obligue a decidir y actuar con menor ayuda. La elección debe cambiar una consulta, configuración, entrada o algoritmo de forma observable. Registrar la salida propia y una alternativa descartada mediante selección contextualizada, código o archivo, sin agregar criterios evaluativos no autorizados.

**Acción observable.** Mostrar resultado propio y decisión respaldada por evidencia.

**Representación y composición.** Tarjeta de reto con condición, entrada variable y verificación, sin respuesta correcta preseleccionada. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Defensa; no sustituir por discurso generado.

**Criterio de construcción y QA.** Confirmar que la tarea puede resolverse con lo enseñado, dentro de tiempo y sin consultar una solución del docente. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.23 · Contraste y límite · 130–135 min (5 min)

**Propósito y contenido específico.** Examinar afirmaciones fuertes del producto y elegir qué dato o prueba falta.

**Diseño de la enseñanza (Interpretación de evidencia).** Usar una salida obtenida por el estudiante para distinguir observación, explicación, límite y decisión. Pedir identificación de un dato concreto y una limitación que se derive del resultado, no una definición de memoria. En caso de bloqueo, permitir revisar referencia etiquetada sin atribuirla al estudiante.

**Acción observable.** Seleccionar límite respaldado por resultado propio.

**Representación y composición.** Cuatro rótulos fijos: Cómo se lee, Qué nos dice, Qué NO permite concluir, Qué error común. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Conclusión acotada; no certificar producción.

**Criterio de construcción y QA.** La conclusión debe corresponder al resultado disponible, indicar el dato ausente y evitar afirmar causalidad no demostrada. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.24 · Relevo y cierre de producto · 135–140 min (5 min)

**Propósito y contenido específico.** Preparar snapshot final, versión y mantenimiento futuro sin modificar calificaciones.

**Diseño de la enseñanza (Relevo al producto).** Cerrar el contrato entre esta sesión y la siguiente, indicando qué artefacto, identidad, versión y limitaciones se transfieren. Verificar una lectura o importación mínima en el consumidor previsto cuando exista. Si aún no se ha implementado el consumidor, declarar esa prueba pendiente y conservar un fixture independiente.

**Acción observable.** Exportar manifiesto final y ruta de acceso autorizada.

**Representación y composición.** Puente entre entrada, capacidad aprendida, artefacto y consumidor. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** V3 con procedencia; estado de pendientes.

**Criterio de construcción y QA.** Validar contrato y compatibilidad, no dar por integrada una capacidad solo porque existe un enlace. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

### S16.25 · Cierre del curso · 140–150 min (10 min)

**Propósito y contenido específico.** Relacionar capacidades de ingeniería, búsqueda, multimedia y distribución con problema inicial; revisar rúbrica vigente y próximos pasos formativos.

**Diseño de la enseñanza (Cierre y comprobación).** Recuperar la decisión inicial, comparar con la evidencia y sintetizar el mecanismo que permitió resolver el problema. Reservar tiempo para autochequeo con retroalimentación específica y para comprobar el producto. Registrar qué objetivo quedó sin demostrar y qué actividad de recuperación se necesita; no ocultar un cierre incompleto.

**Acción observable.** Realizar autochequeo de competencias y comprobar entrega o defensa.

**Representación y composición.** Síntesis de capacidades y checklist de evidencia, con salida directa al producto o siguiente sesión. En esta pantalla la representación debe materializar la acción descrita, con la identidad del dato visible y sin depender de un enlace adicional.

**Resultado verificable y límite.** Producto, evidencia y estado; no registrar notas nuevas en este plan.

**Criterio de construcción y QA.** La prueba de salida debe depender de los objetivos y resultados de esta sesión; respetar evaluación y calendario vigentes. La implementación se acepta cuando se puede comprobar la evidencia especificada; si todavía no hay ejecución o fuente verificable, se conserva el estado pendiente en lugar de sustituirla por una salida inventada.

## Evidencias y prueba de viabilidad de S16

| Control | Entrada/variable que se manipula | Evidencia de aceptación |
|---|---|---|
| E1 · S16.08 Multimedia integrada | Abrir evidencia correspondiente a un resultado real. | Página/intervalo y origen; no reconstruir contenido. |
| E2 · S16.10 Predicciones y evaluación | Verificar que predicción conserva modelo y fecha. | Tabla y metadata; no demostrar causalidad. |
| E3 · S16.13 Diseño y accesibilidad | Ejecutar prueba de acceso desde portada y abrir un resultado. | Ruta funcional; no confundir UI bonita con producto. |
| E4 · S16.20 Integración: validar recuperación | Comparar conteos y contratos antes/después. | Prueba reproducible; no repetir benchmarks pesados. |

**Producto mínimo:** Compras Claras V3, paquete de evidencia y defensa según reglas vigentes. Antes de publicar, ejecutar la ruta base del cuaderno `Cuadernos/Proyecto_Final_Compras_Claras.ipynb` en Colab y entornos de producto aprobados; registrar exactamente el modo, los datos, la versión, el tiempo de preparación, el primer resultado, la celda más lenta, el tiempo de relectura y los fallos. El presupuesto de 45 minutos del laboratorio incluye preflight y exportación. Si la preparación no cabe, resolverla antes de la clase o activar contingencia probada sin cambiar la evaluación. Los resultados de las cuatro pruebas no se sustituyen por capturas o datos generados sin etiqueta. En una sesión evaluativa, los controles se aplican a casos formativos o a la presencia de evidencia según rúbrica, sin entregar solución ni modificar pesos.

**Verificación de continuidad:** conservar el producto con identidad, esquema, fecha, fuente y modo. El consumidor de la sesión siguiente debe leer un ejemplo válido y detectar al menos un ejemplo incompatible. En caso de ausencia de consumidor implementado, dejar prueba pendiente y no declarar integración. Para S16 el consumidor es el acceso final al producto y el archivo de evidencia.

**Revisión docente:** comprobar la pregunta inicial, la explicación de los cuatro fundamentos, los tres ejemplos, los experimentos y la decisión de transferencia. Validar presentación real y móvil, anclas del cuaderno y retroalimentación. La aceptación se registra por dimensiones de la rúbrica y puertas del apartado 5. Estado actual de esta reconstrucción: especificación propuesta; no se han implementado ni ejecutado aquí estas nuevas pantallas. Riesgo a controlar antes de aprobación: Introducir criterios después de anunciar el proyecto, usar datos sintéticos como reales, publicar datos personales o confundir prototipo con sistema de producción.

# 8. Entrega de reconstrucción y verificación global
La reconstrucción se controla por sesión, no por media. La tabla es un inventario de especificación, no una lista de sesiones terminadas.

| Sesión | Especificaciones | Minutos planificados | Palabras de especificación por capítulo | Estado de nuevas diapositivas |
|---|---:|---:|---:|---|
| S01 | 25 | 150 | 5700 | E1 · diseño; ejecución pendiente |
| S02 | 25 | 150 | 5486 | E1 · diseño; ejecución pendiente |
| S03 | 25 | 150 | 5441 | E1 · diseño; ejecución pendiente |
| S04 | 25 | 150 | 5430 | E1 · diseño; ejecución pendiente |
| S05 | 25 | 150 | 5454 | E1 · diseño; ejecución pendiente |
| S06 | 25 | 150 | 5412 | E1 · diseño; ejecución pendiente |
| S07 | 25 | 150 | 5406 | E1 · diseño; ejecución pendiente |
| S08 | 25 | 150 | 5383 | E1 · diseño; ejecución pendiente |
| S09 | 25 | 150 | 5432 | E1 · diseño; ejecución pendiente |
| S10 | 25 | 150 | 5448 | E1 · diseño; ejecución pendiente |
| S11 | 25 | 150 | 5470 | E1 · diseño; ejecución pendiente |
| S12 | 25 | 150 | 5352 | E1 · diseño; ejecución pendiente |
| S13 | 25 | 150 | 5481 | E1 · diseño; ejecución pendiente |
| S14 | 25 | 150 | 5471 | E1 · diseño; ejecución pendiente |
| S14A | 25 | 150 | 5494 | E1 · diseño; ejecución pendiente |
| S15 | 25 | 150 | 5376 | E1 · diseño; ejecución pendiente |
| S16 | 25 | 150 | 5420 | E1 · diseño; ejecución pendiente |

## Conteo y transparencia
El conteo de palabras del documento incluye las fichas temáticas y los protocolos recurrentes de diseño, control y QA. Las instrucciones recurrentes no cuentan como palabras originales de enseñanza de las futuras clases. El núcleo temático de las 425 fichas, medido únicamente sobre los cuatro campos específicos de cada ficha, contiene 13034 palabras según separación de secuencias alfanuméricas Unicode con compuestos unidos por guion. No se presenta este núcleo como un libreto de 40.000 palabras. La cifra total del documento se reporta aparte como extensión de la especificación estructurada. Las clases reconstruidas deberán acreditar, cada una, al menos 40.000 palabras originales de contenido pedagógico, calidad y ejecución, sin duplicar este texto recurrente. Las fichas de este plan no acreditan esas palabras. El requisito se verifica para cada sesión, no mediante un promedio ni una suma que compense faltantes.

Se preserva el estándar anterior de no fusionar sin validar. La modificación actual es documental y se limita a la rama de trabajo; no certifica los 425 diseños como diapositivas implementadas. El criterio de éxito final es que el estudiante pueda aprender, ejecutar, modificar, interpretar y transferir una capacidad con evidencia, en el tiempo real de clase.
