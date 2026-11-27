# Infraestructura del curso

- `lms/`: migraciones SQL, Edge Functions y documentación de operación. **No se eliminan migraciones históricas**: son necesarias para reconstruir y auditar el LMS.
- `tutoriales/git/`: consulta complementaria para S02.

El curso vigente utiliza Colab, Codespaces especializados, Atlas, Astra, Aura, Elasticsearch y Databricks según la sesión. El stack Docker/Airflow y los benchmarks de cursos anteriores se retiraron de esta rama; se recuperan desde el commit histórico registrado en [limpieza](../docs/limpieza-repositorio.md). No iniciar contenedores ni ejecutar benchmarks para abrir el repositorio.
