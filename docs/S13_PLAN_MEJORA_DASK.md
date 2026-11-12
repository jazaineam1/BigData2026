# S13 · Plan de mejora pedagógica: Dask que se entiende y se ejecuta

**Objetivo:** sustituir una narrativa dominada por auditorías y benchmarks históricos por una secuencia de procesamiento paralelo observable. El docente valida fuente, modelos y resultados de gran escala fuera de la actividad estudiantil. La clase no menciona equipos personales.

## Diagnóstico y acciones

| Problema detectado | Corrección concreta | Comprobación |
|---|---|---|
| Referencias a hardware personal | Retirar esas referencias de diapositivas, cuaderno y guía de estudiante | Validador impide volver a introducir “HP” en la presentación |
| La clase explica más resultados negativos que usos de Dask | Mostrar OCR/audio por archivo, lotes independientes y Parquet; incorporar ejecución con workers reales | Script pequeño produce direcciones y timings de Dask |
| Confusión entre núcleo, vCPU, hilo, nodo y worker | Mostrar configuraciones 1×4, 2×2, 4×1 y 8×1 y sus límites | Selector interactivo de workers y comandos `nproc`, `lscpu`, `free -h` |
| La tabla TF-IDF no indica el propósito ni explica pesos | Introducir por qué representamos texto, caso de tres documentos y tabla HTML con TF/DF/IDF/L2 separados | Alumno puede cambiar texto y ver cada columna y norma |
| Los segundos de entrenamiento y transformación se mezclan | Explicar cada cronómetro, operación y VM; dejar resultados de 50k solo como referencia histórica | Se identifica el ganador de **cada fase**, sin afirmar ganador global |
| Train 10k / test 10k parece arbitrario | Explicar que el test de 10.000 es fijo y posterior en el estudio de tamaños; no utilizarlo en la primera práctica | Laboratorio central trabaja con ocho tareas pequeñas |
| “Caché de embeddings” no se entiende | Diferenciar primera generación, conservación de vectores del corpus y vectorización de cada consulta nueva | Explicación con tres pasos y ejemplo de consultas repetidas |
| GitHub Actions consumió recursos innecesarios | Prohibir lanzamiento automático de 50k, 26k y Ollama en flujo docente; mantener solo pruebas ligeras | Verificar configuración manual de experimentos pesados |

## Laboratorio central de 180 minutos (recomendación)

| Tramo | Minutos | Acción verificable |
|---|---:|---|
| Problema de distribución y casos reales | 20 | Elegir partición: archivos, lotes, consultas |
| Arquitectura: CPU, worker, hilo y scheduler | 25 | Ejecutar `nproc`, `lscpu`, `free -h`, grafo de workers |
| MapReduce y TF-IDF | 35 | Obtener promedio ponderado y una fila correcta de TF/DF/IDF/L2 |
| **Dask real** | 50 | Script de ocho tareas secuencial/Dask 2 workers; observar igualdad y tiempos |
| Escalado opcional a 4 workers | 20 | Ejecutar solo si hay CPU disponibles; comparar caliente vs total |
| Consolidación y puente a PySpark | 30 | Leer JSON, razonar por qué ganó/perdió y reutilizar función por archivo |

Los simuladores del navegador explican el mecanismo; **la medición real se hace en Codespaces**.

## Casos donde Dask sí tiene sentido

1. **Solicitudes independientes** (OCR/ASR o APIs): workers pueden superponer esperas. La práctica sustituye la API por una **espera simulada declarada**, evitando costos y credenciales; Dask y sus procesos sí son reales.
2. **Cálculos intensivos independientes por archivo:** al existir CPU libres, las funciones suficientemente costosas pueden repartirse entre procesos. El modo CPU opcional es sintético y no garantiza aceleración.
3. **ETL sobre particiones Parquet que superan una sola RAM:** Dask DataFrame permite particionar lectura y agregaciones, y puede escalar a varios nodos cuando existen; no se demuestra por ejecutar ocho trabajos en una VM.

## Criterios para considerar completa la mejora

- La presentación conserva 32 diapositivas y no incluye el equipo personal del docente.
- El cuaderno ejecuta el caso pequeño y muestra **tiempos reales de la VM**, no estimados.
- El resultado secuencial coincide exactamente con el distribuido por lote.
- El JSON separa tiempo de arranque, tiempo caliente y tiempo total; no se falsifican ganadores.
- Las tablas grandes de GitHub Actions están explicadas como **histórico interno**; no vuelven a correr.
- El widget Streamlit ofrece el programa y permite ejecutar voluntariamente la demostración pequeña.
- Las pruebas automáticas revisan solamente sintaxis, navegación y cálculos pequeños. El ensayo de Codespaces con un clúster real se valida de forma explícita en el aula, sin Actions pesados.

## Documentación técnica

- [Dask: buenas prácticas](https://docs.dask.org/en/stable/best-practices.html)
- [Dask Distributed: eficiencia y tamaños de tarea](https://distributed.dask.org/en/stable/efficiency.html)
- [Dask: cargas independientes](https://examples.dask.org/applications/embarrassingly-parallel.html)
- [GitHub Actions: especificaciones estándar](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)
