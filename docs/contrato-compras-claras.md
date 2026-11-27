# Compras Claras · contrato de continuidad v1

El mismo observatorio se desarrolla desde S01 hasta S16. Las rutas originales, los motores auténticos, las evaluaciones y los datos de escala permanecen. El explorador integrado añade una **ruta portable ejecutable**, con datos reales del corpus docente de 200 procesos y el inventario de imágenes; no es un sustituto de los motores. No se utilizan etiquetas artificiales de riesgo. El grafo portable solo representa entidad–proceso porque esa fuente no contiene proveedores; Neo4j real conserva su fuente histórica propia.

Cada etapa consume el estado anterior, produce un artefacto reproducible y desbloquea la siguiente. S14A es opcional. Cambiar una decisión anterior invalida los productos posteriores; importar un archivo vuelve a calcular todos los resultados y rechaza discrepancias. La huella FNV-1a es de consistencia, no una prueba criptográfica de autenticidad. El estado no contiene claves de servicios. Los datos de respaldo son la muestra docente versionada: no se duplican archivos ni se descargan los CSV grandes. Seleccionar 40/80/120 deja registros retenidos para S15.

## Evidencia de motores reales

En la última celda del cuaderno, usar el fragmento de exportación que aparece en la ruta (formativo, no cambia ninguna rúbrica). Exporta una muestra limitada de un resultado existente, no credenciales, y el SHA-256 de su serialización. El archivo se adjunta en la etapa correspondiente. La aplicación comprueba estructura y etapa, pero el docente debe comprobar el motor, la procedencia y la ejecución; un adjunto no es certificación de ejecución remota. No se fusionan fuentes con identificadores incompatibles. S09 portable usa TF-IDF, no embeddings; S11 no inventa OCR/ASR; S13 no presenta JS como Dask; S14 no inventa MLlib.

## Hilo de productos

| Sesión | Recibe | Produce | Decisión autónoma |
|---|---|---|---|
| S01 | Corpus versionado | raw | Cantidad de procesos |
| S02 | S01 | architecture | Latencia máxima (s) |
| S03 | S02 | documents | Campo de consulta |
| S04 | S03 | queue | Tamaño de bandeja |
| S05 | S04 | partitions | Clave de agrupación |
| S06 | S05 | graph | Número de entidades |
| S07 | S06 | lexical | Consulta |
| S08 | S07 | release1 | Control de muestra |
| S09 | S08 | retrieval | Consulta |
| S10 | S09 | media | Imágenes del inventario |
| S11 | S10 | extraction | Modo de consulta |
| S12 | S11 | release2 | Muestra de auditoría |
| S13 | S12 | aggregation | Particiones lógicas |
| S14 | S13 | analytics | Entidades principales |
| S14A | S14 | capacity | Millones de filas |
| S15 | S14 | incremental | Registros adicionales |
| S16 | S15 | release3 | Resultados visibles |

## Recuperación y criterios

La ruta común es explorador + cuaderno principal; el panel de producto está integrado en el explorador. El progreso local no es nota. Las rutas de recuperación pueden reconstruirse a partir de la misma fuente con decisiones por defecto. No usar el respaldo como prueba de trabajo propio; cambiar una decisión y verificar un resultado propio antes de entregarlo. Los cuatro rótulos de interpretación se mantienen. Sin instalar motores ni paquetes en la ruta portable. Los laboratorios auténticos permanecen en sus entornos previstos.

**Publicación:** rama de revisión únicamente. El calendario y las rúbricas vigentes permanecen intactos. S15 propuesta, S14A voluntaria.
