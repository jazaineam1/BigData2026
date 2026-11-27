# Puerta secuencial de calidad — S01
Estado: **NO APROBADA / S02 BLOQUEADA**. Se exige ≥4,5/5, cada dimensión esencial ≥4, 40.000 palabras originales sustantivas deduplicadas por sesión, ≥25 diapositivas de enseñanza, laboratorio reproducible, evidencia visual y ensayo de 150 minutos. La calificación se justifica con evidencia; no se redondea para desbloquear. Solo se trabaja sobre S01 hasta que todas las puertas pasen. No se modifica main ni el curso publicado.
 
## Implementación actual
S01 tiene 25 pantallas de enseñanza y una pausa, agenda total 150 min, presentación específica que conserva el piloto anterior, cinco mecanismos nuevos, lectura ampliada por pantalla, enlaces por sección A0–A8, y un cuaderno alternativo autónomo con 200 registros reales del snapshot (no descarga viva). La ruta por defecto no depende de red, ICFES remoto ni API. Se conservan el cuaderno original y las demás sesiones. Paquete RAW, derivados y manifiesto persistente en runtime. La consulta viva es optativa y separada.
 
Conteo bruto de prosa de lectura en presentación: 8746; markdown de cuaderno: 1477. El total bruto 10223 no es elegible deduplicado y está por debajo de 40.000 incluso antes de excluir coincidencias. No se contabilizan datos incrustados, código ni metadatos. Estado de extensión: NO CUMPLE.
 
## Evidencia previa al guardado
Corpus comprobado: 200 filas, 200 IDs, 51 entidades distintas. Cuatro páginas de 50 con salto 40: 200 filas y 170 IDs; 30 repetidos y 30 ausentes. Agenda de 150 y 25 pantallas de enseñanza; compilación JavaScript correcta. La ejecución Python del nuevo notebook, pruebas de navegador, ensayo docente y evaluación pedagógica todavía deben documentarse con evidencia independiente.
 
## Matriz de calificación provisional
| Dimensión | Peso | Estado |
|---|---:|---|
| Profundidad | 20% | No cumple extensión, desarrollo parcial |
| Actividad y autonomía | 20% | Actividades y transferencia implementadas; autonomía de estudiante no observada |
| Práctica reproducible | 20% | Código y datos disponibles; ejecución completa por validar |
| Alineación | 15% | Anclas A0–A8 diseñadas, falta prueba integral |
| Interpretación | 10% | Lectura y límites por pantalla; verificación pendiente |
| Visual y accesibilidad | 10% | Interfaz adaptativa, proyección real pendiente |
| Tiempo | 5% | 150 planificados, no medidos |
 
No se otorga 4,5/5 sin comprobaciones; no se autoriza iniciar S02. La política de revisión secuencial se aplica a todas las sesiones, incluida S14A opcional. Los borradores anteriores se conservan como referencia, no como sesiones aceptadas.

## Segunda iteración: corrección de alineación y pruebas locales
Se corrigieron las referencias heredadas S01-A/S01-B y código de API, se incorporó selección por prefijo en A3, ejemplo ejecutable CSV/JSON/XML en A2 y caso de fuente mutable en A5. El orden del cuaderno coincide con la posición del snapshot que usa la presentación y se documenta en el manifiesto; no se exige importar estado al observatorio oficial ni avanzar a S02. Se leyó el notebook guardado y se comparó la lista de 200 objetos incorporados con el corpus fuente: identidad exacta por serialización JSON. Se verificó agrupación por bloques en 20 configuraciones sobre el corpus real (4 escalas × 5 bloques).

Prueba local reproducida de las funciones Python con fixture SINTÉTICO de 200 registros (no ejecución íntegra del notebook remoto): Python 3.13.5, pandas 2.2.3. Ocho tamaños de página, seis tamaños de bloque, tres paquetes reabiertos, detección de modificación de bytes, ocho mediciones sintéticas CSV. Para N=100.000, suma 4.999.545 en las cuatro rutas; memoria lógica del DataFrame completo 1.600.132 bytes, bloques 500/1000/5000: 8.132/16.132/80.132 bytes. Tiempo observado 0,01244 s completo; 0,10076/0,05500/0,01756 s por bloques, una sola corrida y sin medición RSS. No se trasladó el ipynb remoto al entorno por DNS y acceso externo restringido; la prueba usa una transcripción local de las funciones y no acredita ejecución integral Colab ni consulta viva.

Conteo bruto actualizado: 8749 palabras de lectura de la presentación y 1568 de Markdown del cuaderno; total 10317. El total no alcanza 40.000 ni acredita deduplicación. S01 sigue sin aprobar, S02 bloqueada.

## Tercera iteración — evaluación formativa
25 comprobaciones de comprensión nuevas, una por pantalla sustantiva. Cada comprobación plantea una decisión, tres opciones no preseleccionadas, retroalimentación diferenciada para las tres alternativas y una transferencia al experimento o cuaderno. Se registra en memoria solo el primer intento, sin datos personales, sin enviar respuestas y sin calificar a estudiantes. La lectura ampliada incluye estas comprobaciones sin saturar la proyección. Prosa bruta adicional de preguntas, opciones, explicaciones y transferencias: 2367 palabras (no certificadas como elegibles ni deduplicadas). Se conserva la puntuación conceptual de la clase como pendiente de validación con estudiantes. 

## Evaluación provisional posterior a las tres iteraciones
El dictamen corresponde al nuevo recurso específico de S01, no a una nota del estudiante ni a una recalificación de todas las sesiones anteriores. Escala: 0 ausente, 1 declarado, 2 presente sin verificación suficiente, 3 parcial comprobado, 4 evidencia sólida, 5 verificación independiente con transferencia. Se aplica estrictamente la ponderación del plan.

| Dimensión | Peso | Nota / 5 | Evidencia y brecha |
|---|---:|---:|---|
| Profundidad conceptual | 20% | 3 | 25 pantallas con explicaciones y ejemplos; solo 12.684 palabras brutas entre lectura, cuaderno y comprobaciones, sin acreditar 40.000 originales. |
| Actividad y autonomía | 20% | 3 | 25 comprobaciones, 75 alternativas probadas, cambios de parámetros y reto A8; falta observar modificación autónoma de un estudiante. |
| Práctica auténtica y reproducibilidad | 20% | 3 | 200 registros reales incorporados, referencia Python local con fixture sintético y pruebas de relectura; no se ejecutó el ipynb remoto completo con su corpus real. |
| Alineación y transferencia | 15% | 4 | 25 referencias a secciones A0–A8 verificadas, misma selección del snapshot y paquete de relevo; S02 permanece bloqueada. |
| Interpretación de resultados | 10% | 4 | Límites por pantalla, explicaciones de las 75 alternativas y controles de cobertura, memoria lógica, grano y relectura probados. |
| Diseño visual y accesibilidad | 10% | 3 | 25 pantallas y pausa en DOM simulado, navegación y controles comprobados; falta navegador real, contraste medido y proyección. |
| Viabilidad temporal | 5% | 1 | Agenda suma 150 min; no se cronometró ensayo docente ni recorrido de estudiante. |

**Resultado provisional: 3.15/5. NO APROBADA.** La puerta de 4,5/5 no se supera; el mínimo individual y las puertas de extensión, ejecución integral, navegador, autonomía y ensayo siguen pendientes. S02 NO se modifica. El conteo bruto (8.749 lectura, 1.568 Markdown, 2.367 preguntas/retroalimentación) suma 12.684; faltan al menos 27.316 palabras brutas, y el déficit elegible puede ser mayor. No se rellena con repeticiones.

QA final del contenido guardado: regeneración HTML idéntica, 26 pantallas (25 de enseñanza), 73 cambios de parámetros y 35 respuestas de cuestionario anterior, 52 alternancias de lectura, 25 referencias al cuaderno, 20 reducciones con el corpus real. Las 25 comprobaciones nuevas arrancan sin opción seleccionada y botón deshabilitado: 75 respuestas probadas, 25 correctas y 50 incorrectas con retroalimentación y transferencia correctas; el primer intento no cambia por reintento. Son pruebas automatizadas de UI con DOM simulado, no resultados de estudiantes. La rama main conservó el SHA 9876871419dca42e6a3d50bf5f2524a94e399a5a. No se ejecutó despliegue ni se modificó S02 o posterior. El validador manual utils/validar_s01_revision.py permite verificar el cuaderno completo y navegador en un checkout; no se ejecutó ese archivo sobre checkout porque no fue posible descargar el repo al contenedor. No activar workflows pesados ni publicar como final.

## Cuarta iteración — adquisición verificable frente a fallos
Se integra A4.1/A4.2 con servidor HTTP local de loopback y un cliente Python que obtiene el snapshot SECOP incorporado en páginas. El servidor emite respuestas reales HTTP y fallos docentes controlados; el cliente conserva bytes de respuestas, valida esquema, identidad, contenido y tamaño de página, reintenta el mismo offset, acumula conteos por entidad y escribe JSONL de forma incremental. El manifiesto marca la finalización tras relectura; los fallos conservan incidencia y no producen manifiesto completo. No se afirma memoria constante: el control de identidad/contenido mantiene un mapa del universo. No se afirma reanudación entre procesos ni transacción de todo el directorio. Se incorpora una matriz de ocho casos y un reto paramétrico. El simulador de navegador calcula la traza de cada escenario y enseña el efecto del máximo de intentos. Los controles de rango ahora muestran su valor.

Prueba local de referencia del mismo algoritmo Python, con **200 registros sintéticos**, servidor HTTP real 127.0.0.1 y archivos temporales: normal 200 filas/4 solicitudes, transitorio 200/6; prohibido, JSON inválido, esquema, repetido, alterado y corto: 50 filas/2 solicitudes y sin manifiesto completo. 8/8 casos comprobados. No se ha acreditado aún la ejecución integral del cuaderno guardado con los 200 registros SECOP reales. No se toca S02 ni se publica en main.

## Quinta a séptima iteración — profundización completa y control de aprendizaje
- 25 capítulos específicos de lectura ampliada, 17.455 palabras en capítulos, con mecanismos, ejemplos numéricos, errores y transferencia. No son diapositivas adicionales para proyectar en 150 minutos. 
- 44 celdas, 24 de código; guías A0–A8 explican dependencias, funciones y salidas. Se amplían colas variables, pérdidas de identidad al convertir CSV/JSON, calidad y coincidencia textual, cliente HTTP con fallos controlados, paginación de frontera, comparación repetida de lectura, verificador independiente de paquete y reto con hipótesis antes de ejecución. Se alinea tokenización ASCII normalizada de Python y JavaScript. No se cambian rúbricas oficiales.
- Conteo bruto por recurso: lectura 8854, capítulos 17455, evaluación formativa 2367, Markdown del cuaderno 13002; total 41678. Conteo léxico depurado 41470 (563 bloques; se eliminó 1 palabra de duplicado exacto, además de encabezados, enlaces y código inline). Se analizaron 65703 pares de bloques de al menos 40 palabras, con similitud de secuencias de cinco palabras, contención ≥0,55 y relación de longitud ≥0,7. Cero pares señalados. No se cuentan código, fixture, datos, salidas, metadatos ni títulos de capítulos. Este cribado no demuestra ausencia de paráfrasis o redundancias conceptuales: revisión editorial de pertinencia/originalidad aún pendiente. El umbral léxico de 40.000 sí se supera. Repetible con `node utils/audit_s01_words.js`.
- QA de archivos guardados: HTML regenerado idéntico, 200 objetos incorporados idénticos al archivo fuente, 200 IDs únicos, 25 pantallas de enseñanza + pausa, anclas A0–A8, agenda suma 150 y 44 IDs de celda únicos. DOM simulado: 26 pantallas, 25 capítulos, 75 opciones formativas, 42 extremos de deslizadores, 96 combinaciones HTTP (8 escenarios × 3 límites × 4 presupuestos), 30 reducciones sobre el snapshot real; no navegador real.
- Prueba Python de referencia local (Python 3.13.5, pandas 2.2.3), transcripción de funciones con fixture sintético de 200 registros: tres casos de cola, cuatro controles de formato/unión, 24 fronteras de paginación, ocho casos HTTP de loopback, 12 mediciones CSV, cuatro rechazos de paquetes (bytes, archivo ausente, orden alterado y conteo alterado incluso con hash interno actualizado), tres pares de transferencia. Los cuatro rechazos fueron efectivos; normal y transitorio preservaron RAW y cambiaron traza. En el benchmark de 20.000 filas, las 12 corridas obtuvieron suma 999.901; mediana de lectura+agregación+instrumentación: completo 0,00188 s (320.132 bytes lógicos), bloques 500 0,02225 s (8.132 bytes), 1.000 0,01196 s (16.132 bytes), 5.000 0,00376 s (80.132 bytes). Tres repeticiones por ruta, tiempos locales no extrapolables, sin RSS. No se ejecutó el ipynb exacto guardado con sus datos SECOP en Python por acceso de red restringido; no se atribuyen las cifras sintéticas al portal ni a una ejecución Colab. `python utils/validar_s01_revision.py --execute --browser` incluye ahora QA de tres variantes en memoria; sigue pendiente de ejecución en checkout accesible.
 
### Nueva evaluación provisional
| Dimensión | Peso | Nota / 5 | Evidencia / límite |
|---|---:|---:|---|
| Profundidad conceptual | 20% | 4 | 25 capítulos específicos, explicación de código y 41.470 palabras de prosa tras exclusiones y deduplicación exacta; cribado de 65.703 pares sin coincidencias por umbral. Aún falta revisión editorial de redundancia conceptual y pertinencia. |
| Actividad y autonomía | 20% | 3 | 25 comprobaciones, 75 opciones verificadas, retos paramétricos, hipótesis obligatoria y verificación del producto; 3 pares de transferencia de referencia probados. Falta observar autonomía de un estudiante. |
| Práctica auténtica y reproducibilidad | 20% | 3 | 200 objetos SECOP exactos comparados con snapshot; servidor HTTP local y 8 casos de referencia, 24 casos de frontera, 12 mediciones, 4 rechazos de paquetes y 3 pares de transferencia con fixture sintético. Falta ejecutar íntegro el ipynb guardado con corpus real. |
| Alineación y transferencia | 15% | 4 | 25 anclas A0–A8 y 25 capítulos comprobados; producto verificable, hipótesis y defensa articulados. Falta ensayo integral. |
| Interpretación de resultados | 10% | 4 | 75 retroalimentaciones probadas y ejemplos de transporte, cobertura, grano, tipos, memoria lógica y fallos de integridad. Comparación con referencia matemática y verificador independiente. |
| Diseño visual y accesibilidad | 10% | 3 | 26 pantallas en DOM simulado, 25 capítulos, 42 cambios de extremos de sliders y 96 escenarios HTTP en navegador simulado. Falta renderizado real y proyección. |
| Viabilidad temporal | 5% | 1 | Agenda suma 150 min. Lecturas extensas y pruebas de profundización no se asignan como lectura oral de clase. Falta ensayo cronometrado y medición de autonomía. |
 
**Nota 3.35/5. S01 NO APROBADA. S02 BLOQUEADA.** Aumenta profundidad de 3 a 4 por capítulos completos y extensión léxica verificada; las demás notas no se inflan por pruebas de referencia o por autoevaluación del autor. Falta revisión semántica editorial, ejecución íntegra del cuaderno real, navegador real, ensayo de 150 minutos y observación de autonomía. Ninguna sesión posterior se intervino. No se fusiona ni despliega. SHA de main comprobado: 9876871419dca42e6a3d50bf5f2524a94e399a5a.

## Octava iteración: evaluación pedagógica y secuencia
Ver [evaluación pedagógica S01](evaluacion-pedagogica-s01.md). Nota provisional 3.68/5; S02 permanece bloqueada. Conteo léxico actualizado 41717. La modificación de diseño aún requiere QA posterior. 
