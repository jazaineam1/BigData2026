# Módulo 05 · Elasticsearch — arquitectura vigente de S07

## Objetivo de aprendizaje

S07 enseña a construir y evaluar un buscador textual de forma reproducible. La clase no presenta Elasticsearch como una librería de Python: primero se usa **Elasticsearch directamente** mediante la UI y Console; después se automatizan las mismas operaciones desde Python/Colab.

El estudiante debe salir pudiendo explicar y repetir:

1. documento, campo, índice y mapping;
2. `text` vs `keyword`;
3. analyzer e índice invertido;
4. ranking BM25 y lectura de `_score`;
5. uso de Console para `PUT`, `_analyze`, indexación y `_search`;
6. `match`, `multi_match`, boost, `bool.must`, `filter` y `highlight`;
7. conexión desde Python con `Elasticsearch(...)`;
8. carga masiva con `bulk()` y verificación con `count()`;
9. evaluación A/B con juicios de relevancia y Precision@5;
10. transferencia al corpus de noticias.

## Tres recursos visibles para estudiantes

La sesión se limita deliberadamente a:

- **Presentación:** `Presentaciones/s07-del-vecindario-al-texto.html`
- **Cuaderno:** `Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb`
- **Laboratorio:** `assets/tutoriales/s07-laboratorio-guiado.html`

La presentación contiene la explicación principal.  
El laboratorio funciona como guía de ejecución y checkpoints.  
El cuaderno automatiza lo que primero se comprende en Console.

## Ruta de infraestructura de clase

La ruta principal de 2026-2S usa **Elasticsearch Serverless** y Google Colab. Docker/local no forma parte del recorrido obligatorio de S07.

```text
Elastic Cloud
   ↓
Elasticsearch project
   ↓
Console / Index Management / Discover
   ↓
Python client en Colab
   ↓
bulk + search + evaluación
```

Los materiales locales históricos pueden conservarse como referencia, pero no deben competir con esta ruta durante la clase.

## S07 Live · laboratorio de dominio, no solo Kahoot

El laboratorio incluye **ocho desafíos formativos** con ranking en tiempo real y un máximo de **21 puntos**. No son solo preguntas de selección múltiple: hay modelado de campos, ordenamiento de pipeline, completado de API, verificación de un resultado real, construcción de Query DSL, cálculo numérico y transferencia a noticias.

Arquitectura:

```text
GitHub Pages
   ↓ publishable key
Supabase RPC
   ├── join
   ├── submit
   ├── leaderboard
   └── question_stats
        ↓
s07_live_scores
        ↓
Supabase Realtime
        ↓
ranking actualizado en todos los navegadores
```

Se almacenan únicamente:

- alias elegido por el estudiante;
- respuesta a cada checkpoint;
- correcto/incorrecto;
- puntaje y cantidad respondida.

No se almacenan correos, contraseñas ni credenciales de Elasticsearch.

La migración reproducible está en:

`infraestructura/modules/05-elasticsearch/s07-live-supabase.sql`

### Seguridad

- El frontend usa una **publishable key**, no una service-role key.
- RLS está activado.
- Las respuestas no tienen lectura pública directa.
- Las escrituras pasan por RPC acotadas a S07.
- `s07_live_scores` expone solo alias y puntaje para poder renderizar el leaderboard.\n- La ruta principal de sincronización usa **Supabase Broadcast**, no `postgres_changes`; esto sigue la recomendación vigente de Supabase para notificaciones de cambios.
- Este ranking es **formativo**, no reemplaza la evidencia del notebook ni debe usarse como nota oficial por sí solo.

## QA mínimo antes de dictar

Comprobar en escritorio y teléfono:

- contraste de slides oscuras;
- botones anterior/siguiente/fullscreen;
- swipe horizontal;
- botones **Comprobar** del laboratorio;
- ingreso con alias a S07 Live;
- actualización del ranking en dos navegadores;
- distribución de respuestas por checkpoint;
- apertura/reutilización de una sola pestaña de Colab;
- Console y proyecto Elasticsearch real;
- `client.info()`, `_analyze`, `bulk`, `count` y búsquedas.

Validador:

```bash
python utils/validate_session7_elasticsearch.py
```


## Referentes técnicos usados para el diseño

La sesión toma como referencia rutas actuales de producto y formación, no solo ejemplos inventados:

- Elastic Search Labs · Search Tutorial: construcción incremental de una solución completa de búsqueda.
  https://www.elastic.co/search-labs/tutorials/search-tutorial/welcome
- Elastic · Keyword search with Python: proyecto, índice, mapping, cliente oficial, bulk y búsqueda.
  https://www.elastic.co/docs/solutions/search/get-started/keyword-search-python
- Elastic · Query DSL: diferencia entre query context, filter context y relevancia.
  https://www.elastic.co/docs/explore-analyze/query-filter/languages/querydsl/
- Elastic · Ranking Evaluation API: evaluación con necesidades de información y documentos juzgados.
  https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval
- Elastic · Search Profiler: diagnóstico del costo de ejecución de consultas.
  https://www.elastic.co/docs/explore-analyze/query-filter/tools/search-profiler
- Elastic · Search UI / e-commerce: patrones de caja de búsqueda, filtros, facets y experiencia de producto.
  https://www.elastic.co/docs/solutions/search/site-or-app/search-ui
- Supabase Realtime · Broadcast: Broadcast es la ruta recomendada para notificaciones de cambios; Postgres Changes queda como alternativa simple.
  https://supabase.com/docs/guides/realtime/subscribing-to-database-changes

Estos referentes justifican cuatro decisiones pedagógicas de S07:

1. construir en pasos pequeños y ejecutables;
2. enseñar Console antes de esconder la API detrás de Python;
3. tratar relevancia como algo que se **evalúa**, no como un score que se acepta;
4. llevar el laboratorio hasta patrones reconocibles de producto: e-commerce, empleo, noticias y bases de conocimiento.
