# Auditoría de viabilidad y aprendizaje — proyecto final Big Data 2026
**22-nov-2026 · solo revisión docente · NO publicar todavía**

**Decisión:** viable con cambios y piloto. El objetivo es **construir un observatorio consultable**, no un conjunto de notebooks ejecutados sin relación. Caso único SECOP II; etiquetas y modelo idénticos para todos. Alcance curricular hasta S14.

## 1. Revisión real de contenidos

| En el proyecto | Ya impartido | Material exacto | ¿Nuevo? y mitigación |
|---|---|---|---|
| API, paginación, descarga concurrente y hash | TC1, S01 | Cuadernos/Taller_Control_1.ipynb; utils/tc1_secop.py | no; solo 2 páginas × 20 filas, repaso |
| ETL, calidad, metadatos, persistencia | S10-S12 | Cuadernos/Taller_Control_2.ipynb; S11 | no; usar fuente SECOP preparada |
| Dask, particiones, workers y \`compute()\` | S13 | Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb; Laboratorios/S13_Codespaces | no; comparar conteos reales con pandas |
| TF-IDF y regresión logística de dos modalidades | S13 | Laboratorios/S13_Codespaces/analisis.py | no; misma fuente y split |
| Tres fits scikit-learn repartidos por Dask | S13 | \`experimentos_distribuidos\` | no; **distribuir experimentos no distribuye un mismo fit** |
| Spark SQL / Delta / Databricks Free | S14 | Cuadernos/14_PySpark_Compras_Claras.ipynb | no; CSV manual, capas del caso |
| Entrenar un único modelo Spark MLlib | NO en recorrido principal de S14 | extensión resuelta en E6 | **sí**; se entrega código completo, diagrama, guía y resultado esperado; evaluar lectura e integración, no memorización de API |
| Construir interfaz consultable | S13 ya mostró Streamlit y exploración visual, pero la app final no | generador offline nuevo | **sí, integración guiada**; HTML completo suministrado, reto es producirlo con datos/modelos propios |
| NoSQL y búsqueda semántica S03-S09; OCR/ASR S10-S12 | sí | Explorer consultable | no repetir despliegues/cómputos de esos motores como requisito final |

### Hallazgo pedagógico crítico

El borrador original terminaba con JSON y un manifiesto, pero **no exigía construir una aplicación útil**. La versión corregida genera **observatorio.html**, abrible por doble clic incluso sin conexión: busca por texto, filtra modalidades y train/test, muestra predicciones **solo de test**, consulta ficha e incluye exportación CSV y métricas del entrenamiento real.

El Explorer docente de S01–S14 es **guía de estudio**, no sustituye al producto propio del equipo.

## 2. Auditoría etapa por etapa

| Etapa | Viabilidad con recursos gratuitos | Aprende al hacer | Prueba observable | Riesgo y rescate |
|---|---|---|---|---|
| E0 entorno | Alta con recurso previo | interpretar cuota, dependencias, ruta de dato | CSV S13 de 1.000 filas y SHA256 | cuota Codespaces agotada → Colab CPU descargando **3 archivos** |
| E1 API paralela | Media: servicio público variable | paginación, I/O, latencia, concurrencia, equivalencia | 2 páginas, hash, segundos, o error real | 429/red → registrar error y seguir desde snapshot |
| E2 ETL | Alta | grano de proceso, clases reales, deduplicación, fuga de datos | 2 clases, IDs únicos, split estratificado semilla 42 | falta columna/clase → error explícito, NO datos fabricados |
| E3 Dask DataFrame | Alta | tareas, particiones, \`compute()\`, verificación | 2 workers y conteos Dask=pandas | overhead > pandas → enseñar por qué |
| E4 Dask modelos | Alta si corre scikit-learn | entrenamiento/prueba, CV y distribución de **experimentos** | 3 hiperparámetros, F1 CV, baseline, F1 test | datos pequeños / cuotas → CPU con 2 workers, sin pruebas de 50k |
| E5 Databricks | Media, cuenta no garantizada | CSV → Delta Bronze/Silver/Gold → SQL | tablas auténticas y conteos | bloqueo cuota/egress; ruta PySpark local solo tras pilotarla |
| E6 Spark MLlib | Media, contenido nuevo guiado | entender un fit calculado sobre particiones | train/test idénticos, matriz y F1 real | serverless/ML cache/quota; plan local validado antes de exigir |
| E7 observatorio | **Alta, sin servidor** | datos y modelo alimentan filtros y visualización; limitaciones | HTML con consulta, predicción, CSV descargable, hash | si servidor GitHub acaba, la app offline sigue funcionando |
| Defensa/PR | Alta | justificar por qué un resultado es correcto y qué no demuestra | ID de acierto/error de su test, PR de su repo privado | no clonar/sin Codespace nuevo; git web o subida por UI si hace falta |

**No afirmar velocidad de Dask mayor que pandas, que 1.000 filas prueban escala Big Data, que las etiquetas son fraude, ni igualdad exacta del F1 entre Spark MLlib y scikit-learn.** El experimento es sobre un solo caso común, con arquitecturas aprendidas y datos reales pequeños por viabilidad.

## 3. Presupuesto Github para el estudiante (fuente oficial, nov 2026)

GitHub Free **personal**: **120 horas-núcleo/mes** y **15 GB-mes** de almacenamiento para Codespaces. Son **60 horas de uso de máquina de 2 núcleos** si no se ha usado nada más, no 120 horas del navegador. Un codespace de 4 núcleos consume doble de horas-núcleo por unidad de tiempo. Quien ya cursó S11–S13 puede tener cuota insuficiente; **no se puede conocer el saldo de sus cuentas desde el repositorio del docente**.

Medidas obligatorias:
- Reusar **el Codespace S13** sin crear otro; máquina **2 núcleos** suficiente para el ejercicio con dos workers; un worker no es un equipo físico.
- Revisar cuota personal **Settings → Billing → Usage** y almacenamiento en **https://github.com/codespaces**; no solicitar capturas públicas de factura.
- Acortar autoapagado por inactividad y detener manualmente; la referencia predeterminada GitHub es 30 minutos.
- Evitar que el proyecto descargue modelos de IA, clones redundantes y entornos preconstruidos; no encender servicios que permanezcan vivos al terminar.
- Guardar \`secop_final.csv\`, JSON, HTML y cuaderno en almacenamiento persistente **antes de borrar** Codespaces sin uso; el almacenamiento de Codespaces detenido sigue computando como GB-mes.
- **No ejecutar Actions con modelos, notebooks completos, 50.000 registros, OCR, ASR o benchmarks**; solo validar estructura de archivos.
- La API SECOP se solicita con **dos páginas × dos métodos = cuatro solicitudes nominales por equipo**, orden estable y reintento acotado. Coordinar para no saturar un servicio externo durante clase.

El repositorio principal público figura con \`size ≈ 383837 KiB\` (~375 MiB) en GitHub API; es un **dato informativo del repositorio, NO una medición del disco ocupado por un Codespace**. En Colab E0 baja la muestra (~1 MB), el corpus 200 expedientes (~0,1 MB) y un módulo Python (~11 KB), y E7 baja el generador auxiliar (~11 KB). Evita clonar todo.

Fuentes: https://docs.github.com/en/billing/concepts/product-billing/github-codespaces ; https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-included-usage .

## 4. Databricks Free y Colab: viabilidad condicionada

**Databricks Free Edition:** recursos únicamente serverless, salida a Internet restringida y cuotas que pueden suspender la ejecución (por el día o más). No usar Spark UI clásico: serverless ofrece Query Profile. La caché Spark ML tiene límites documentados. La edición gratuita no garantiza disponibilidad para toda una cohorte en el mismo momento. Usar **carga manual CSV** de ~1 MB, sin solicitudes HTTP desde el notebook de Databricks. **Un único fit** de Spark MLlib, sin búsqueda exhaustiva de hiperparámetros ni Jobs automáticos.

- Fuentes: https://docs.databricks.com/aws/en/getting-started/free-edition-limitations y https://docs.databricks.com/aws/en/compute/serverless/limitations .
- **Bloqueo docente:** hasta probar un flujo real con cuenta de estudiante y sin servicios pagos, no calificar obligatoriamente una ejecución Databricks. Contingencia sería PySpark local/Colab con mismas operaciones, **solo después de validarla**.
- El ejercicio Spark MLlib excede levemente lo ejecutado en S14; es extensión enseñada paso a paso y con código provisto, no prueba de una API no vista.

**Google Colab CPU:** gratuito pero con límites de tiempo y disponibilidad dinámicos. No requiere GPU. E0 usa una descarga mínima cuando no encuentra el repositorio y E7 descarga únicamente el generador. Advertir que el espacio de ejecución es temporal y hay que exportar resultados por etapa. Fuente: https://research.google.com/colaboratory/faq.html .

## 5. Cómo enseñar para que no sea solo «Run All»

El alumno debe poder completar cada etapa con cuatro comprobaciones visibles: **HAZ ESTO / DEBE VERSE / SI FALLA / EVIDENCIA**. Cada salida se interpreta siempre con **Cómo se lee / Qué nos dice / Qué NO permite concluir / Qué error común**.

Aprendizaje con una sola tarea profesional:
1. **Reproduce:** observa ejemplo docente resuelto con los mismos datos y variables.
2. **Interviene:** ejecuta y verifica una acción técnica concreta (paginación; selección train/test; groupby Dask; CV; SQL; búsqueda).
3. **Predice el resultado esperado:** consulta comprobación antes de ejecutar; identifica límites, sin inventar métricas ni rellenar texto libre evaluable.
4. **Contrasta:** compara propia salida con comprobación de igualdad o rango.
5. **Usa:** abre el producto generado y realiza una consulta, observando un registro correcto y uno mal clasificado.
6. **Defiende:** señala línea o evidencia que respalda su afirmación; explica un límite concreto sin atribuir irregularidades.

No exigir que el estudiante construya una aplicación desde cero, que aprenda una pila de front-end o que repita el OCR/ASR del TC2: debe **comprender y modificar partes pequeñas de código visible, verificar y transferir**. El producto final es rico porque reutiliza correctamente etapas, no por cantidad de frameworks.

### Rúbrica de 100 puntos

| Área | Puntos |
|---|---:|
| Descarga controlada | 8 |
| Preparación de datos/ETL y split | 12 |
| Dask/particiones y workers | 12 |
| Experimentos de entrenamiento Dask | 13 |
| Databricks SQL/Delta | 15 |
| Spark MLlib guiado | 15 |
| **Observatorio funcional offline** | **20** |
| Manifiesto, PR, defensa | 5 |
| **Total** | **100** |

**Equidad:** cuotas consumidas durante cursos previos no se califican como incompetencia. Las salidas remotas que no se ejecutaron se señalan como pendientes y tienen rescate definido; el mismo conjunto de datos y el mismo problema siguen siendo obligatorios.

## 6. Aprobación antes de publicarlo: puertas de calidad

| Puerta | ¿Comprobado? | Condición antes de habilitar taller |
|---|---|---|
| Integridad de archivos, estructura del cuaderno, rubrica, fichas | verificación estática | validador ligero pasa sin ejecutar código pesado |
| Datos S13 realmente 1.000, 2 clases con tamaño útil | pendiente ejecución limpia | conteo y etiquetas reales impresas, hashes |
| Colab CPU con solo 3 descargas funciona | pendiente piloto | E0–E4 produce el mismo CSV/test y el HTML |
| API SECOP en vivo | pendiente comprobación | 4 consultas nominales, hash o error reproducible |
| Codespaces existente 2-core | pendiente piloto | Dask 2 workers, sin consumo excesivo |
| Databricks Free en cuenta no paga | pendiente piloto | E5/E6 con SQL, Delta, MLlib |
| Observatorio estático en navegador móvil | pendiente QA visual | 3 consultas, exportación CSV y accesibilidad |
| Rúbrica y porcentaje aplicables a **grupo 2** | pendiente confirmación | calendario y evaluación aprobados |
| Índice y LMS permanecen sin enlace | sí, comprobado al revisar | no añadir hasta autorización docente |

**Conclusión:** el esquema es pedagógicamente razonable **solo si** pasa esas puertas. Si no se consigue un piloto de Databricks Free, reducir su peso o convertirlo a la ruta local previamente probada; no descalificar al estudiante por la plataforma.

## 7. Bloqueo de publicación

**No editar \`index.html\`, \`lms/data/course.json\` ni la navegación del LMS; no anunciar fecha/nota/peso a estudiantes.** Mantener el material en revisión hasta aprobación.

**Matiz imprescindible:** el repositorio es **público** y los archivos HTML ya fusionados en main tienen URL directa aunque no estén enlazados en la portada. Un \`robots: noindex\` disuade indexación, **no crea privacidad**; si se quiere inaccesibilidad real, mover la revisión a un repositorio privado autorizado, sin publicarla por GitHub Pages.

Aplicar **una rama de trabajo → una fusión PR → eliminación de rama**, sin acumular ramas temporales. No borrar ramas históricas ajenas a esta auditoría sin comprobar qué trabajo contienen.


## Actualización de verificación técnica del OFFSET y de los datos (22-nov-2026)

- Archivo real [snapshot S13](../Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv): CSV leído desde GitHub, 1.000 filas, 59 columnas, 1.000 IDs únicos, sin filas truncadas.
- Filtrado de modalidades S13: **830 registros (440 directa y 390 régimen especial)**, sin texto vacío.
- Revisión técnica previa a entrenamiento: 19 valores de descripción marcadora **«No Definido»**; un par de registros con descripción idéntica adicional. El cuaderno E2 retira esas 20 filas **antes del split**: **810 procesos con 810 descripciones distintas**, 435 directa y 375 régimen especial. Esta corrección la proporciona el docente; no es una auditoría adicional para el alumno.
- División estratificada prevista 80/20 con semilla 42: 648 entrenamiento y 162 prueba, pendiente de validar ejecutando el código completo en el entorno real.
- Se probó localmente la lógica OFFSET con **7 tests unitarios**, todos satisfactorios: páginas 0/20, última parcial, incompleta, HTTP 429/reintento, cambio entre lecturas, offsets inválidos y fallo persistente. Las respuestas de esos tests son **simuladas**, no la red real.
- El endpoint base `https://www.datos.gov.co/resource/p6dx-8zbt.json` devuelve JSON por una consulta web pública, pero el acceso a **solicitudes parametrizadas con OFFSET y LIMIT desde este entorno quedó bloqueado**. Es incorrecto declararlas verificadas contra SECOP en vivo.
- No se ha ejecutado Spark MLlib en Databricks Free ni Dask en Codespaces para esta revisión. La aprobación final depende de un piloto con acceso real; no hacer correr benchmarks pesados en GitHub Actions.

**Condición de publicación:** ninguna; el taller continúa como borrador no publicado en Pages/índice/LMS.
