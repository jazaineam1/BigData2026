# Evaluación pedagógica S01 — diseño y recorrido de aula
 
## Hallazgos y decisiones
Se revisaron 25 preguntas: el índice correcto repetía 0,1,2, permitiendo adivinar sin aprender. Se permutaron opciones y retroalimentaciones de forma consistente, con distribución no periódica. Las preguntas son formativas, no examen oficial. Se revisó la secuencia: API básica → paginación → cobertura → mutabilidad → recuperación HTTP, para enseñar primero el modelo y luego los mecanismos de resiliencia. Se incluyó una comprobación accesible sin abrir la lectura extensa. Siete comprobaciones se marcaron como prioritarias en aula; las otras quedan para estudio autónomo. La lectura de 40.000 palabras es un recurso de consulta, no un libreto de lectura continua.
 
## Referentes
- Carnegie Mellon Eberly Center: alineación objetivos/actividad/evaluación, https://www.cmu.edu/teaching/assessment/basics/alignment.html
- Freeman et al. (2014), aprendizaje activo en STEM, DOI 10.1073/pnas.1319030111. Estudios principalmente de pregrado; orientan el diseño, no demuestran eficacia de esta clase.
- CESE, carga cognitiva y ejemplos resueltos: https://education.nsw.gov.au/about-us/education-and-research/cese/publications/practical-guides-for-educators/cognitive-load-theory-in-practice.html
- CAST DUA 3.0: https://udlguidelines.cast.org/es/
 
## Alineación de resultados de aprendizaje
| Objetivo observable | Práctica | Evidencia de dominio |
|---|---|---|
| Diagnosticar escala y restricciones | A1 y simuladores | Explicar saldo, memoria mínima y decisión con unidades |
| Distinguir formato, grano e identidad | A2/A3 | Predecir cardinalidad y detectar duplicación sin alterar fuente |
| Adquirir y reconciliar un universo | A4/A5 | Corregir offset, verificar cobertura, explicar fallo y reintento |
| Combinar estados y medir | A6 | Igualdad de agregados, interpretación de memoria lógica |
| Construir y verificar producto | A7/A8 | Paquete releído, variante paramétrica, hipótesis y defensa |
 
## Itinerario de 150 minutos (plan, no medición)
| Intervalo | Actividad | Evidencia |
|---|---|---|
| 0–5 | 01 · La misión · Diagnóstico | Docente: plantea la decisión de Laura y recoge dos respuestas sin corregir inmediatamente. Estudiante: delimita pregunta y unidad. Evidencia: una afirmación permitida y otra que requiere datos adicionales. |
| 5–9 | 02 · Escala y decisión · Modelo | Docente: fija llegada y capacidad, predice primero. Estudiante: calcula cola antes de mover el control. Evidencia: saldo y unidad. |
| 9–13 | 03 · Diagnóstico · Diagnóstico | Docente: pide justificar una V mediante una métrica, no recitar definiciones. Estudiante: discute un caso y propone primera medición. |
| 13–18 | 04 · Infraestructura · Modelo | Docente: explica RAM, disco, CPU y red; calcula el mínimo de una matriz. Estudiante: elige una estrategia bajo presupuesto. |
| 18–22 | 05 · Estructuras · Ejemplo | Docente: muestra los mismos dos registros en CSV y JSON, y pregunta qué cambia. Estudiante: identifica campos y tipos. |
| 22–26 | 05B · Identidad y grano · Ejemplo | Docente: dibuja P1–P3 y sus contratos; estudiante predice filas y únicos, luego verifica con control. |
| 26–31 | 06 · Fuente real · Exploración | Docente: abre la fuente congelada y señala ID, entidad, descripción y procedencia. Estudiante: encuentra un ID y formula límite. |
| 31–35 | 07 · Calidad · Exploración | Docente: introduce cinco copias y muestra el conteo. Estudiante: explica por qué cambian filas, no IDs. |
| 35–39 | 08 · Primera transformación · Ejemplo | Docente: diferencia selección y agrupación. Estudiante: compara dos prefijos y predice la suma de conteos. |
| 39–44 | 09 · Pandas · Práctica guiada | Docente: ejecuta A0/A3 y enseña la expresión groupby. Estudiante: cambia N_TEXTO o un prefijo y comprueba denominador. |
| 44–50 | 10 · Texto · Práctica guiada | Docente: usa dos frases pequeñas y predice frecuencia. Estudiante: prueba un término real y explica diferencia. |
| 50–60 | Pausa · Pausa | Descanso de diez minutos. No asignar lectura, tareas ni instalación. |
| 60–63 | 11 · API · Modelo | Docente: dibuja cliente → petición → respuesta → validación. Estudiante: distingue HTTP 200 de contenido correcto. |
| 63–68 | 12 · Paginación · Ejemplo resuelto | Docente: enseña 12 filas con limit=5 y offsets 0,5,10. Estudiante: predice página final y contrasta. |
| 68–73 | 12B · Control de cobertura · Práctica con ayuda decreciente | Docente: muestra 200 filas con salto 40 y deja que el estudiante calcule únicos/ausentes. Estudiante: corrige el salto y explica. |
| 73–76 | 12C · Orden y cambios · Contraejemplo | Docente: inserta P00 entre páginas. Estudiante: identifica repetido y ausente. |
| 76–84 | 12D · Recuperación HTTP · Demostración técnica | Docente: ejecuta normal y transitorio del cliente HTTP y muestra trazas. Estudiante: predice el efecto de bajar intentos a dos. |
| 84–89 | 13 · Fragmentar · Práctica guiada | Docente: muestra parciales A=2,B=1 y B=1,C=3. Estudiante: combina por clave y cambia chunk. |
| 89–93 | 14 · Experimento manual · Ejemplo resuelto | Docente: plantea dos valores diez y ocho valores cien. Estudiante: calcula media global y compara. |
| 93–97 | 14B · Estado combinable · Práctica con ayuda decreciente | Docente: proporciona estados parciales; estudiante calcula la combinación cuando hay nulos. |
| 97–106 | 15 · Capacidad real en Python · Práctica de medición | Docente: ejecuta A6 benchmark de 10.000 filas y explica bytes lógicos. Estudiante: compara dos tamaños y justifica una decisión. |
| 106–116 | 16 · Reutilizar el resultado · Producto guiado | Docente: ejecuta producir y señala los archivos. Estudiante: genera un paquete propio con universo fijo. |
| 116–122 | 16B · Auditoría del producto · Prueba negativa | Docente: modifica una copia del paquete y muestra rechazo. Estudiante: explica qué controla hash y qué controla contenido. |
| 122–138 | 17 · Construir tu propia adquisición · Autonomía | Estudiante: elige N, limit y chunk, calcula cuatro predicciones sin mostrar la solución, activa A8.1 y verifica dos paquetes. Docente: acompaña solo si hay bloqueo. |
| 138–145 | 18 · Interpretar y defender · Evaluación de transferencia | Estudiante: explica una evidencia, un error detectado y un límite. Docente: contrasta con criterios formativos. |
| 145–150 | 19 · Relevo · Cierre | Docente: aplica ticket de salida de tres preguntas y recoge el producto mínimo. Estudiante: declara fuente, grano, universo y una restricción desconocida. |
 
### Carga y prioridades
50 min fundamentos y exploración; 10 min pausa; 24 min adquisición (incluida demostración HTTP); 22 min reducción y medición; 16 min producto y prueba negativa; 16 min autonomía; 12 min defensa/cierre. Las 25 diapositivas sirven como anclas de actividad y no como 25 lecturas. Priorizar siete comprobaciones. Ante retraso, retirar ampliaciones y proteger autonomía y cierre. La ruta de clase no obliga a leer la implementación completa del servidor ni las 24 pruebas de frontera; se conservan en los dos recursos existentes.
 
### Criterios formativos, sin cambiar rúbrica oficial
Producto mínimo: universo declarado, cobertura y unicidad, conteos correctos, paquete releído; variante propia con cuatro predicciones, explicación de una prueba negativa y un límite. Docente registra sin datos personales: completó producto, completó variante sin solución, justifica límite; distinguir estudiante que necesitó ayuda. Meta de ensayo: ≥80% producto y ≥70% variante autónoma (propuesta, no observada). Registrar tiempos reales por bloque y ajustar; no aprobar por planificación.
 
## Evaluación provisional
Diseño conceptual 4; actividad/autonomía 4 por ruta con ayuda decreciente y tarea observable (no se acredita resultado de estudiante); práctica 3; alineación 4,5 por matriz y secuencia explícitas; interpretación 4; visual/accesibilidad 3; tiempo 2 por itinerario priorizado, no ensayado. Ponderación previa: 20/20/20/15/10/10/5. Nota 3,68/5 redondeada (3,675 exacta). No alcanza 4,5 y no cumple las puertas de ejecución completa, navegador real, revisión semántica de extensión, ensayo ni autonomía observada. S02 bloqueada. No despliegue oficial.

## QA de la intervención pedagógica
Se releen las fuentes guardadas y se regenera el HTML idéntico; 26 pantallas, 25 capítulos, 75 retroalimentaciones y 50 aperturas/cierres de comprobación rápida pasaron en DOM simulado. Distribución de posiciones correctas 8/8/9, sin ciclo A-B-C. Siete comprobaciones de aula y 13 celdas de código de núcleo, 11 de ampliación. Se corrige el nombre del parámetro del recorrido de pandas a N (celda s01-quality) y se incorpora un ticket de salida de tres preguntas reales, no una indicación vacía. Resultado final: 46 celdas, 24 de código, 41894 palabras en conteo léxico depurado. La revisión semántica y el ensayo en aula no se consideran aprobados. No se pudo ejecutar el ipynb exacto ni abrir HTML en navegador real por acceso directo a GitHub restringido. SHA main 9876871419dca42e6a3d50bf5f2524a94e399a5a. Nota de diseño provisional 3,68/5; no cambia el bloqueo de S02.

## Novena iteración: recorrido autónomo sin dependencias innecesarias
Se ordena físicamente el cuaderno en un núcleo continuo seguido de un apéndice. El núcleo no abre sockets, no consulta SECOP y no requiere ejecutar las pruebas avanzadas: la huella incremental está en A0 y se conserva HTTP local como demostración posterior. La medición breve A6 compara tres estrategias con alcance temporal idéntico y referencia matemática. A7 verifica esquema, procedencia y orden explícitos, además de bytes, identidades y conteos; se separa una prueba negativa esencial de seis casos avanzados. A8 crea ZIP verificable de los paquetes, con etiqueta distinta si es solo el ejemplo guiado. Se incluye mapa de estaciones y acceso directo a la ruta de aula en cada diapositiva. Se conserva el contenido previo en apéndice, sin modificar los dos recursos oficiales. Conteo léxico 42202, 52 celdas, 12 de código núcleo y 15 de ampliación. Pendiente QA de la modificación y ejecución exacta; la puerta sigue cerrada.

## Reevaluación después de la novena iteración
Prueba estática y DOM simulado sobre archivos guardados: HTML regenerado idéntico, 26 pantallas, 25 capítulos, 75 opciones formativas, 52 aperturas/cierres de ruta y 42 extremos de controles. Se confirmó que las 12 celdas núcleo preceden al apéndice (15 de código) y no requieren el servidor docente. Copia de los 200 objetos del snapshot exacta. Conteos reales por prefijo 40/80/120: 26/39/46 nombres de entidad; salud: 6 ocurrencias y 4 procesos. Se incorporaron salidas de referencia y se distingue producto válido de hipótesis acertada.
 
Prueba Python local de referencia con funciones copiadas y fixture sintético de 200 registros: suma 499.950 en tres estrategias sobre 10.000 filas, memoria lógica completa 160.132 bytes, bloques 1.000:16.132, 5.000:80.132. Tiempos de una corrida 1,80 / 7,56 / 2,10 ms respectivamente, no extrapolables. Seis paquetes alterados rechazados (bytes, ausente, orden, conteo, esquema, procedencia); siete ZIP comprobados y tres pares de transferencias equivalentes. No se afirma ejecución integral del ipynb real ni duración de una clase. Se agrega opción manual `python utils/validar_s01_revision.py --core` y se conserva `--execute` para ejecución completa; ambas pendientes en checkout accesible. Sin workflows nuevos. La descarga de raw.githubusercontent.com falló también vía visor web, por lo que no hay render real ni ejecución exacta.
 
| Dimensión | Nota | Peso |
|---|---:|---:|
| Profundidad conceptual | 4 | 20% |
| Actividad y autonomía | 4.5 | 20% |
| Práctica auténtica y reproducibilidad | 3.5 | 20% |
| Alineación y transferencia | 4.5 | 15% |
| Interpretación de resultados | 4.5 | 10% |
| Diseño visual y accesibilidad | 3 | 10% |
| Viabilidad temporal | 2.5 | 5% |
 
**Nota provisional 3.95/5; NO APROBADA.** Conteo léxico depurado 42549; 0 pares señalados por cribado, revisión semántica pendiente. Permanecen bloqueadas las puertas de ejecución exacta, navegador real, ensayo de aula y observación de autonomía. No se avanza S02. main 9876871419dca42e6a3d50bf5f2524a94e399a5a.


## Décima intervención: portada, visualización, escala y construcción
La nueva portada, incluida en los ocho minutos de apertura, tiene ilustración vectorial propia. Se conservan 25 pantallas docentes, pausa y portada adicional; se mantienen los enlaces #sN. Se añadieron diagramas de procesos y modos de proyección, exploración y lectura. No son fotografías externas. La simulación de calidad usa duplicados antes de faltantes, con valores iniciales iguales en JS/Python. La paginación admite límite 37. Se introduce JSONL, dimensionamiento interactivo, exportación de plan A8 con cuatro configuraciones aisladas, y retroalimentación «Respuesta correcta» sin certificar comprensión. El cuaderno conserva la ruta guiada e incorpora A6.2 (100.000 filas y millón manual), A8.2 (TODO de conteo y offset), A8.3 (aislamiento de límite, bloque, universo) y A8.4 (ZIP de evidencias con métricas, bitácora, validación y datos). Se mantienen los paquetes de datos originales separados y compatibles. Falta validar un puente de importación con el estado portable de otras sesiones.

### QA y límites
HTML guardado reconstruido byte a byte a partir de fuentes. DOM simulado: portada/inicio/regreso, 26 pantallas, 75 respuestas, 26 pares de apertura/cierre y 89 cambios de controles sin errores. No equivale a navegador real. En el entorno local, copia de la función de medición con pandas 2.2.3: 9 ejecuciones, 10.000/100.000/1.000.000 filas y lectura completa/bloques de 1.000/5.000; sumas respectivas 499950/4999545/49999950 en todas las rutas. Para un millón: memoria lógica 16000132/16132/80132 bytes y tiempos de una corrida 0,073/0,541/0,147 s; no RAM máxima, ni comparación universal. No se ejecutó el ipynb guardado íntegro; DNS de GitHub inaccesible desde el contenedor. El conector sí permite leer y escribir. Prueba real de navegador, revisión semántica integral, ensayo de 150 minutos y observación de autonomía siguen pendientes. Conteo léxico depurado 42785, bruto 43076; 0 coincidencias del cribado, no certificación editorial.

### Nueva ruta (150 min planificados)
| Pantalla | Minutos |
|---|---:|
| 01 · La misión | 8 |
| 02 · Escala y decisión | 5 |
| 03 · Diagnóstico | 4 |
| 04 · Infraestructura | 5 |
| 05 · Estructuras | 4 |
| 05B · Identidad y grano | 4 |
| 06 · Fuente real | 3 |
| 07 · Calidad | 3 |
| 08 · Primera transformación | 2 |
| 09 · Pandas | 4 |
| 10 · Texto | 3 |
| Pausa | 10 |
| 11 · API | 4 |
| 12 · Paginación | 5 |
| 12B · Control de cobertura | 5 |
| 12C · Orden y cambios | 3 |
| 12D · Recuperación HTTP | 6 |
| 13 · Fragmentar | 5 |
| 14 · Experimento manual | 4 |
| 14B · Estado combinable | 4 |
| 15 · Capacidad real en Python | 9 |
| 16 · Reutilizar el resultado | 11 |
| 16B · Auditoría del producto | 7 |
| 17 · Construir tu propia adquisición | 25 |
| 18 · Interpretar y defender | 4 |
| 19 · Relevo | 3 |

### Reevaluación de diseño provisional
| Dimensión | Peso | Nota |
|---|---:|---:|
| Profundidad conceptual | 20% | 4.3 |
| Actividad y autonomía | 20% | 4.3 |
| Práctica auténtica y reproducibilidad | 20% | 3.7 |
| Alineación y transferencia | 15% | 4.3 |
| Interpretación de resultados | 10% | 4.5 |
| Diseño visual y accesibilidad | 10% | 3.5 |
| Viabilidad temporal | 5% | 3 |

**4.06/5: NO APROBADA.** Frente a la auditoría independiente anterior (3,78), mejora provisional de 0.28. No se abre S02. No se modifican materiales oficiales ni se agregan ejecuciones automáticas. Pendientes adicionales: mejorar variedad de diagramas y revisar cada pantalla proyectada, ampliar ejemplos de representación y complejidad, sincronizar referencias del apéndice, incorporar libreto docente integral y probar entrega autónoma con estudiante.


## Undécima intervención: presentación visual completa, libreto y experimentos adicionales
Se amplía la portada con competencias, una ilustración SVG original y propósito. Se desarrollan 25 ilustraciones didácticas específicas más una pausa ilustrada (27 pantallas ilustradas con la portada). No son fotografías externas. Se incluye libreto por pantalla: «Di esto», «Haz esto» y ruta/celda exacta; 3218 palabras contando títulos, explicación y acciones, 2615 palabras en texto para decir. No se suma este material al umbral léxico original. Se corrige gráfica de escala con barras proporcionales y se incorpora control para ocultar ilustraciones al proyectar. En el cuaderno, A8.3 añade contraste del JSON exportado por el simulador, verificando configuraciones, identidad, orden, conteos y tamaños; A6.3 agrega representación int64/int32 y complejidad de conteo, como ampliaciones sin incrementar carga obligatoria. Se extiende el validador manual. 

**Pruebas efectivamente realizadas:** HTML exacto recompuesto, DOM simulado: portada/inicio/regreso, 26 pantallas y SVG, 26 guiones y rutas, 75 opciones, 89 variaciones, cero errores de la prueba. En Chromium se reprodujo localmente la portada a partir de su marcado y reglas CSS copiadas, detectando superposición de navegación a 1366×768; después de corregir, la portada cabe a 1366×768 y 1920×1080 y no desborda horizontalmente a 360×800. Esta es una muestra local, no render del HTML completo ni validación del visor externo. En Python pandas 2.2.3, 9 ejecuciones de referencia de medir_csv transcrita, sumas 499950/4999545/49999950 para 10k/100k/1M. En un millón tiempos de referencia 0,110895/0,519068/0,150491 s (completo/1000/5000); memoria lógica 16000132/16132/80132 bytes. Validadores de construcción y paginación transcritos: 6 aceptaciones correctas, 9 rechazos en fixture sintético. Representación 100k filas: 1600132/800132 bytes int64/int32 y misma suma 4999545. Complejidad: 500000 comparaciones/10000 visitas modeladas, paridad comprobada y tres mediciones por estrategia. No equivale a ejecución del notebook exacto. El puente de plan JSON y el ZIP requieren ejecución integral; navegador completo, revisión semántica y ensayo humano pendientes. Conteo depurado 42978 palabras (43275 bruto); cribado de 72010 pares, cero coincidencias por umbral, no acredita ausencia de redundancia semántica.

| Dimensión | Peso | Nota |
|---|---:|---:|
| Profundidad conceptual | 20% | 4.5 |
| Actividad y autonomía | 20% | 4.4 |
| Práctica auténtica y reproducibilidad | 20% | 4 |
| Alineación y transferencia | 15% | 4.5 |
| Interpretación de resultados | 10% | 4.6 |
| Diseño visual y accesibilidad | 10% | 4.1 |
| Viabilidad temporal | 5% | 3.2 |

**4.29/5: NO APROBADA.** Se mantiene S02 bloqueada. Se conserva la rama alternativa y no se modifica el sitio oficial. Pendiente: ejecución exacta con núcleo y apéndice; validación del ZIP autónomo y del puente de plan; inspección real de las 27 pantallas; revisión editorial semántica; ensayo de 150 minutos y observación de autonomía.


## Duodécima intervención: herramientas interpretables, diagnóstico y recuperación
Se rediseñan cola (tasas constantes, pico, pausa, caída y saldo inicial), memoria (tipo, presupuesto y bloque), transformaciones (filtro, proyección, agrupación), pandas (cinco instrucciones, dos fallos), API (petición y cuerpo ficticios, estados), reducción (iteraciones y tres fallos). Las otras herramientas con controles añaden mensajes situados con interpretación, acción recomendada y prueba siguiente. Se incorporan seis predicciones con resultados inicialmente ocultos, opción de observar sin responder, comprobaciones con explicación, y texto de diagnóstico para diferenciar un escenario adverso de una hipótesis incorrecta. Se amplía la tokenización, se agrega conflicto de identidad simulado y se muestran tiempos de referencia solo para configuraciones previamente medidas. El cuaderno incorpora diagnóstico de tabla, respuesta HTTP y reducción; corrige referencias A8.1 (dos paquetes de referencia) vs A8.3 (cuatro casos aislados) y A8.4 (entrega). No se añade un recurso pedagógico. Itinerario: 150 min, 25 min autónomos, 3101 palabras orales, 3702 palabras de libreto. 

QA del HTML guardado en DOM simulado: 26 pantallas, 21 herramientas con diagnóstico, 150 variaciones de control, 171 diagnósticos, 130 respuestas a hipótesis, 58 comprobaciones de ocultamiento y 6 rutas de observación sin respuesta, 75 comprobaciones formativas, 35 opciones de los cuestionarios conceptuales, 72 pruebas de conservación de cola y 17 casos dirigidos de fallo/recuperación. Cero errores en estas pruebas; HTML reconstruido exacto. No se ejecutó el cuaderno exacto ni se renderizaron todas las pantallas en navegador real. Los paneles adicionales pueden aumentar desplazamiento; falta inspección. No se añadieron fotos externas; siguen pendientes revisión editorial semántica, ensayo y autonomía observada. Conteo léxico depurado 43137, no equivale a certificación editorial. 

| Dimensión | Peso | Nota |
|---|---:|---:|
| Profundidad conceptual | 20% | 4.5 |
| Actividad y autonomía | 20% | 4.6 |
| Práctica auténtica y reproducibilidad | 20% | 4 |
| Alineación y transferencia | 15% | 4.5 |
| Interpretación de resultados | 10% | 4.7 |
| Diseño visual y accesibilidad | 10% | 4 |
| Viabilidad temporal | 5% | 3.5 |

**4.34/5 provisional, NO APROBADA.** Comparación con auditoría independiente 4,19; S02 continúa bloqueada. No fusionar ni tocar main.
