# Fixtures del TC1 V9

Datos reales congelados para probar el TC1 sin consultar la API en cada ejecución.

| Archivo | Qué es | Cómo se produjo |
|---|---|---|
| `P03_procesos.json.gz` | primeros 3.000 registros de SECOP II Procesos (`p6dx-8zbt`) desde el 2025-03-01, orden estable con `:id` | `utils/tc1_data_gates.py --fixture P03`, descarga única del lado docente el 2026-10-01, con pausa entre peticiones y User-Agent identificado |
| `P03_contratos.json.gz` | primeros 4.000 contratos (`jbjy-vk9h`) desde el 2025-03-01 con `tipodocproveedor = 'NIT' AND es_grupo = 'No'` | mismo script y misma descarga |
| `P03_totales.json` | conteos totales de la ventana en la API | mismo script |
| `P03_cqlsh_salida.txt` | salida real de Cassandra 4.1 (`cqlsh -f`) para el script CQL correcto de P03 | `utils/test_tc1_v9_e2e.py` contra Cassandra en Docker |
| `P03_E5/` | evidencia real de Neo4j 5 (carga, ancla, compartidos y ranking) para P03 | `utils/test_tc1_v9_e2e.py` contra Neo4j en Docker |

Criterios de selección: los mismos del contrato del taller (`utils/tc1_contrato.py`). El resumen de las 12 ventanas, con los umbrales que cada una supera, está en `Datos/tc1_ventanas_resumen.json`.

Son datos públicos de datos.gov.co; no contienen información de estudiantes.
