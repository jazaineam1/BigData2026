# Segunda auditoría pedagógica · después de reorganizar el repositorio

## Alcance y método
Revisión de diseño de las 17 rutas (16 sesiones numeradas y S14A), encabezados de cuadernos canónicos y recursos de apoyo, conservación de datos y navegación. Comparación cualitativa con alineamiento constructivo, aprendizaje activo, PRIMM, carga cognitiva y competencias de ingeniería de datos. No se midió aprendizaje de estudiantes. No se certifica ejecución de plataformas remotas.

Escala ordinal de diseño (1 ausente, 2 inicial, 3 suficiente con limitaciones, 4 sólido, 5 referente interno): **C** claridad del recorrido, **P** práctica auténtica prevista en el material, **A** autonomía progresiva, **E** evidencia verificable. P no afirma que el servicio haya sido ejecutado en esta auditoría. Los criterios son una selección propia de revisión, no una acreditación. Media orientativa 3.91/5; no comparable numéricamente con la auditoría anterior (criterios distintos).

| Sesión | Tema | C | P | A | E | Mejora observada | Siguiente comprobación |
|---|---|---:|---:|---:|---:|---|---|
| 01 | Fundamentos | 4 | 4 | 3 | 4 | Conserva API y lectura por fragmentos; explorador de memoria acorta el comienzo. | Medir una escala real y distinguir memoria de DataFrame frente a RSS. |
| 02 | Arquitectura | 4 | 4 | 4 | 4 | Requisitos de latencia, costo y proceso conectados a una decisión; Git como soporte. | Comprobar que el estudiante elige arquitectura antes de seleccionar herramientas. |
| 03 | MongoDB | 4 | 4 | 3 | 4 | Ruta 0–3 y 6–7 reduce navegación; conserva 130 celdas de consulta profunda. | Mayor prioridad: experimento MongoDB explain real, no solo índice en memoria. |
| 04 | Atlas | 4 | 4 | 3 | 4 | Replicación ilustrativa y práctica cloud claramente diferenciadas. | Validar acceso gratuito y la recuperación tras fallas de conexión; no simular servicio real. |
| 05 | Cassandra | 4 | 4 | 4 | 4 | Clave de partición vinculada con consulta; comparación sobre datos de juguete. | Verificar dos tablas reales y su distribución de claves, sin inferir nodos físicos. |
| 06 | Neo4j | 4 | 4 | 3 | 4 | Ruta esencial separa apéndices A1–A10; buena contrastación con pandas. | Reducir redundancia de tutoriales históricos; contrastar consultas equivalentes. |
| 07 | BM25 | 5 | 4 | 4 | 4 | Explorador BM25 ajustable y laboratorio Elasticsearch con ranking. | Evaluar varias consultas juzgadas y registrar diferencias con el analizador real. |
| 08 | TC1 | 4 | 4 | 3 | 4 | Cuatro estaciones organizan seis productos; conserva evaluación original. | Preflight real de las tres cuentas y contingencia autorizada, sin cambiar rúbrica. |
| 09 | Vectores | 5 | 4 | 4 | 4 | Recorrido compacto, Atlas real, coseno y recall respecto a ranking exacto. | Probar recall exacto/aproximado y latencia real en la misma configuración. |
| 10 | Multimedia | 5 | 4 | 4 | 4 | Controles de tamaño y concurrencia conectan señales con escala; conserva originales. | Medir transformación real de imágenes y audios, no extrapolar benchmark de hash. |
| 11 | OCR/ASR | 4 | 4 | 3 | 4 | Ruta pequeña y ampliación explícita; 122 fuentes sin obligación de ejecutar todo. | Validar Codespace y visor reales; simplificar pasos dentro de rama estudiantil. |
| 12 | TC2 | 4 | 4 | 3 | 5 | Seis desafíos y 24 controles; diferencia ejecución real de referencias. | Mantener criterios oficiales; probar recuperación y carga de diez audios. |
| 13 | Dask | 4 | 4 | 4 | 4 | Workers, resultados equivalentes, K-means y Amdahl; archivos grandes preservados. | Ejecutar escalamiento fuerte y débil con datos/algoritmo equivalentes. |
| 14 | Spark | 4 | 4 | 3 | 4 | Ruta SQL/joins/Delta/MLlib; experimento de planes y equivalencia. | Confirmar perfiles Spark y planes en Databricks; no afirmar aceleración por hints. |
| 14A | Escala | 4 | 4 | 3 | 4 | Memoria mínima, control local y MLlib; tamaños grandes voluntarios. | Demostrar entrenamiento remoto exitoso que exceda el presupuesto local, sin forzar OOM. |
| 15 | Confiabilidad | 4 | 4 | 4 | 4 | Pipeline nuevo con transacciones, rechazo, checkpoint y ampliación Spark opcional. | Validar notebook completo y Structured Streaming; S15 sigue no evaluable. |
| 16 | Proyecto | 4 | 4 | 3 | 4 | Flujo E0–E7 preservado; integración, split y producto consultable. | Para próxima cohorte, aumentar construcción autónoma e integrar predicciones Spark en producto. |

## Qué mejora frente al estado anterior
- Alineamiento: una pregunta, cuatro estaciones, evidencia y reto por sesión; dos accesos principales. Los recursos complementarios no son recorridos obligatorios.
- Carga cognitiva: se retira infraestructura antigua; se mantiene el material rico mediante apoyo y ampliaciones. S03 y S06 siguen siendo extensos; el cambio es de recorrido, no una reescritura completa.
- Aprendizaje activo: 17 simuladores, preguntas con retroalimentación y código modificable. En S03, S04 y S05 los simuladores no sustituyen la práctica con el motor.
- Transferencia: el proyecto y talleres conservan evaluación vigente. Las microintervenciones del proyecto no bastan para acreditar autonomía avanzada sin una defensa.
- Big Data: capacidad, particiones, replicación, índices, relevancia, latencia y recuperación de fallos aparecen transversalmente. S14A aún requiere una ejecución de escala exitosa; S15 cubre conceptos de confiabilidad, con ampliación Spark voluntaria.
- Reproducibilidad: el árbol conserva 191 archivos de fuentes y muestras con SHA idéntico. Solo se retiró el marcador de un byte Datos/a. Las ramas de estudiantes se mantienen intactas.

## QA registrada
- 17 páginas principales: 113 referencias locales literales verificadas, 0 rotas; 313 valores externos, dinámicos o ignorados no constituyen comprobación de conectividad externa.
- 17 tarjetas con dos acciones principales y 17 rutas con cuatro estaciones.
- 51 casos de cálculo/gráficos (mínimo, máximo e inicial); 17 rutas probadas con DOM simulado, incluyendo respuesta, cambios de controles, progreso local y selección de enlace de preview/producción.
- Inventario de 149 archivos retirados: ninguno permanece en el árbol.
- La rama de revisión no se publicó ni fusionó. El intento de acceso Git desde el contenedor falló por DNS; no se ejecutaron QA de navegador real, CI integral, Colab, Codespaces, Atlas, Astra, Aura ni Databricks. No declarar esas pruebas completadas.

## Referentes
- Biggs y Tang, Teaching for Quality Learning at University: alineamiento constructivo.
- Freeman et al. (2014), Active learning increases student performance in science, engineering, and mathematics, DOI 10.1073/pnas.1319030111.
- PRIMM: Predict, Run, Investigate, Modify, Make, adaptado a posgrado.
- ACM Data Science Curriculum Framework: https://dstf.acm.org/
- Stanford CS246: https://web.stanford.edu/class/cs246/ ; MIT 6.5840: https://pdos.csail.mit.edu/6.5840/ ; Berkeley CS186: https://cs186berkeley.net/.

## Prioridad antes de integrar
1. Ejecutar validación ligera y QA visual real del sitio; comprobar generadores sincronizados.
2. Validar Colab y ramas S11/S13 con cuota disponible; S03 explain y S14/S14A experimentos reales de capacidad y ejecución.
3. Confirmar el PDA del grupo 2 (el PDF actual identifica grupo 1), sin alterar el calendario ni las rúbricas ya anunciadas.
4. Rotar credenciales históricas expuestas; no se ha reescrito el historial.
5. Para siguiente cohorte: reducir longitud de ruta esencial S03/S06, fortalecer autonomía y transferencia en S16, consolidar las rutas de compatibilidad cuando los enlaces históricos y el LMS se hayan migrado.
