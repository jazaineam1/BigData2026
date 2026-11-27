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
