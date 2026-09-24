# Módulo 05 · Elasticsearch — arquitectura vigente de S07

## Objetivo de aprendizaje

S07 enseña a construir y evaluar un buscador textual de forma reproducible. La clase no presenta Elasticsearch como una librería de Python: primero se usa **Elasticsearch directamente** mediante UI/Console; después se automatizan las mismas operaciones desde Python/Colab.

El estudiante debe salir pudiendo explicar y repetir:

1. documento, campo, índice y mapping;
2. `text`, `keyword` y multi-fields;
3. analyzer en index-time y search-time;
4. índice invertido, BM25 y lectura de `_score`;
5. `match` vs `term`;
6. uso de Console para `PUT`, `_analyze`, indexación y `_search`;
7. `multi_match`, boost, `bool.must`, `filter` y `highlight`;
8. conexión desde Python con `Elasticsearch(...)`;
9. carga masiva con `bulk()` y verificación con `count()`;
10. diagnóstico de errores comunes;
11. evaluación A/B con criterios de relevancia y Precision@5;
12. transferencia al corpus de noticias.

## Tres recursos visibles

- **Presentación:** `Presentaciones/s07-del-vecindario-al-texto.html`
- **Cuaderno:** `Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb`
- **Laboratorio:** `assets/tutoriales/s07-laboratorio-guiado.html`

La presentación enseña. El cuaderno automatiza. El laboratorio registra desempeño, progreso y mastery.

## Ruta de clase

```text
Explicación con ejemplo resuelto
        ↓
Console / Colab
        ↓
Desafío D1–D8
        ↓
Primer intento puntúa ranking
        ↓
Pista
        ↓
Reintento puntúa mastery, no ranking
```

Los deep links de la presentación apuntan al desafío exacto:

- `#d1` ranking vs filtro;
- `#d2` mapping;
- `#d3` analyzer;
- `#d4` API `_analyze`;
- `#d5` bulk/count;
- `#d6` Query DSL;
- `#d7` Precision@5;
- `#d8` transferencia a noticias.

## S07 Live · primer intento y mastery

El ranking ya no se autocorrige. Cada actividad conserva dos métricas:

- **ranking / first score:** puntos obtenidos en el primer intento;
- **mastery score:** puntos dominados después de pistas y reintentos.

Esto permite ver:

```text
D2 Mapping
Primer intento correcto: 6/10
Mastery después de pista: 9/10
```

Así el laboratorio conserva valor formativo sin maquillar la medición inicial.

## Backend

Arquitectura:

```text
GitHub Pages
   ↓ publishable key
Supabase RPC
   ├── s07_live_join
   ├── s07_live_submit
   ├── s07_live_leaderboard
   └── s07_live_activity_stats
        ↓
s07_live_scores / s07_live_responses
        ↓
realtime.send() / Broadcast
        ↓
ranking actualizado
        ↓
polling de 3 s como respaldo móvil
```

Datos guardados:

- alias;
- respuesta;
- first answer / first correct;
- mastered;
- attempt count;
- ranking score;
- mastery score.

No se guardan correos, contraseñas ni credenciales de Elasticsearch.

Migración canónica:

`infraestructura/modules/05-elasticsearch/s07-live-supabase.sql`

## Reglas pedagógicas vigentes

1. No revelar solución completa después del primer error.
2. La primera respuesta fija ranking.
3. Los reintentos sirven para mastery.
4. Cada reto debe ser isomorfo al ejemplo, no idéntico.
5. Los bloques de Console en el notebook deben decir **NO SE EJECUTA EN COLAB**.
6. No usar fences `http` que Colab convierta en enlaces clicables.
7. La sesión mantiene máximo 35 pantallas.
8. No crear más de tres recursos visibles.

## Referentes técnicos usados

- Elastic Search Labs · Search Tutorial: construcción incremental de una solución completa de búsqueda.
- Elastic · Keyword search with Python: proyecto, índice, mapping, cliente oficial, bulk y búsqueda.
- Elastic · Query DSL: query context vs filter context.
- Elastic · Match query y Term query: full-text vs exact matching.
- Elastic · Ranking Evaluation API: evaluación con necesidades de información y documentos juzgados.
- Elastic · Search Profiler: diagnóstico de costo de ejecución.
- Elastic · Search UI / e-commerce: patrones de caja de búsqueda, filtros, facets y experiencia de producto.
- Supabase Realtime · Broadcast: Broadcast para notificaciones de cambios; polling como respaldo móvil.

## QA mínimo antes de dictar

- Abrir presentación en portátil y teléfono.
- Probar botones D1–D8 desde la presentación.
- Entrar a S07 Live en dos navegadores.
- Responder mal y luego bien: ranking no debe subir; mastery sí.
- Ver actualización sin recargar.
- Confirmar que el cuaderno no tiene rutas de Console clicables.
- Ejecutar `client.info()`, `_analyze`, `bulk`, `count` y al menos una búsqueda real.
- Verificar que `Precision@5` acepte `0.6`, `0.60`, `0,6` y `0,60`.


## Estándar de explicación de conceptos

S07 no acepta definiciones de una sola línea para los conceptos núcleo. Cada concepto importante debe responder, cuando aplique, estas preguntas:

1. **Qué es:** definición precisa y breve.
2. **Para qué sirve:** problema que resuelve.
3. **Ejemplo mínimo:** caso de 1–3 líneas que pueda razonarse sin ejecutar nada.
4. **Cómo se observa o mide:** campo de respuesta, conteo, propiedad o API que permite comprobarlo.
5. **Error frecuente o límite:** interpretación que no debe hacerse.
6. **Ejemplo aplicado:** contratación, noticias, e-commerce, empleo o knowledge base.

Ejemplo obligatorio para tokenización:

```text
"Quick brown fox"
→ [quick] [brown] [fox]
→ 3 tokens
```

Un token no tiene longitud fija. `_analyze` devuelve `token`, `position`, `start_offset` y `end_offset`. El tokenizer `standard` tiene `max_token_length=255` por defecto; un tokenizer `keyword` puede tratar una cadena completa como un único token.

## Regla de navegación: tres recursos, tres pestañas reutilizables

Para conservar el contexto durante la clase:

- **Presentación** → `target="bigdata-presentation"`
- **Laboratorio** → `target="bigdata-lab"`
- **Colab** → `target="bigdata-workspace"`

No se usa `_blank` indiscriminadamente: cada recurso reutiliza su propia pestaña y no genera decenas de tabs.
