# S09 · Búsqueda semántica y bases vectoriales — arquitectura vigente

## Objetivo

S09 enseña a comparar **mecanismos de recuperación**, no marcas de producto.

La continuidad conceptual es:

```text
S07 · evidencia textual
texto → analyzer → tokens → índice invertido → BM25

S09 · significado
texto → modelo → embedding → similitud → vecinos → Top-k

cierre S09 · complementar señales
ranking lexical + ranking semántico → fusión → ranking híbrido
```

Elasticsearch no se presenta como “motor lexical”: puede soportar recuperación lexical, vectorial e híbrida. MongoDB Atlas se usa como una implementación visible de persistencia + metadata + índice vectorial, no como definición del concepto.

## Regla estricta: dos recursos visibles

S09 tiene exactamente dos recursos visibles para estudiantes:

1. **Presentación interactiva/laboratorio:** `Presentaciones/s09-de-palabras-a-significado.html`
2. **Cuaderno reproducible:** `Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb`

No existe un tercer laboratorio. La URL histórica `assets/tutoriales/s09-laboratorio-guiado.html` solo redirige a la presentación.

## La presentación es el laboratorio

La presentación incluye:

- definiciones antes de uso;
- ejemplos mínimos;
- gráficos/SVG explicativos;
- LAB 1–9;
- herramientas de simulación;
- desafíos D1–D5;
- S09 Live para el estudiante;
- Teacher Wall con `?wall=docente`.

Secuencia:

```text
definición
  ↓
ejemplo mínimo
  ↓
gráfico o herramienta
  ↓
desafío D1–D5
  ↓
primer intento
  ↓
pista si falla
  ↓
reintento
  ↓
dominio
  ↓
cuaderno cuando toca ejecutar el pipeline completo
```

## Regla terminológica

Un término técnico nuevo no puede ser requisito previo a su definición.

Cuando aplica, la explicación debe responder:

- qué es;
- para qué sirve;
- ejemplo;
- cómo se observa o mide;
- error frecuente o límite.

La ruta incluye, entre otros:

- corpus, documento, consulta, ranking;
- candidato, señal de ranking, score y juicio de relevancia;
- recuperación lexical, analyzer, token, índice invertido y BM25;
- recuperación semántica, búsqueda híbrida, motor y mecanismo;
- vector, búsqueda vectorial, embedding y espacio vectorial;
- modelo de embeddings, tokenización del modelo, encoder y pooling;
- dimensión, E5, prefijos query/passage, chunk, tamaño de chunk y overlap;
- colección MongoDB, documento MongoDB, UpdateOne, bulk_write, upsert e idempotencia;
- Search Index, SearchIndexModel y estado queryable;
- pipeline de agregación, stage, $vectorSearch y vectorSearchScore;
- norma, normalización, producto punto y similitud coseno;
- kNN y Top-k;
- falso positivo y falso negativo;
- base vectorial, metadata, filtro e índice vectorial;
- ENN, ANN y HNSW;
- conjunto de candidatos, Recall@k, latencia y numCandidates;
- Atlas Vector Search y $vectorSearch;
- RRF;
- Precision@k;
- evidencia reproducible.

## Desafíos D1–D5

D1–D5 no guardan una respuesta correcta en HTML.

La presentación envía la opción seleccionada a `bigdata-session9`. El backend compara un SHA-256 y devuelve:

- correcto/incorrecto;
- pista en caso de error;
- primer intento;
- dominio.

Primer intento no cambia tras responder de nuevo. Dominio sí puede mejorar después de una pista y reintento.

Los desafíos son formativos; no añaden nota al TC1.

## S09 Live

El estudiante abre **S09 Live** dentro de la presentación y ve:

- desafíos intentados;
- dominio D1–D5;
- primer intento por desafío;
- tiempo activo aproximado;
- última actividad.

Si abre la presentación sin sesión LMS, las herramientas locales siguen funcionando pero no se registra progreso.

## Teacher Wall embebido

Modo docente:

```text
Presentaciones/s09-de-palabras-a-significado.html?wall=docente#s1
```

El WALL usa la misma identidad LMS y muestra:

- estudiantes activos;
- acceso a presentación y cuaderno;
- inicio y última actividad;
- primer intento D1–D5;
- dominio D1–D5;
- resumen por desafío;
- tiempo activo aproximado.

No ordena estudiantes por velocidad o puntaje.

`lms/teacher-wall-09.html` se conserva únicamente como redirección compatible.

## Gráficos y herramientas

La presentación debe conservar, como mínimo:

- mapa consulta → mecanismo → evaluación;
- pipeline lexical;
- mapa de paráfrasis;
- embedding;
- espacio vectorial;
- pipeline del modelo;
- chunking;
- normalización;
- diagrama kNN;
- arquitectura modelo/base/índice;
- metadata/filtro;
- HNSW interactivo;
- trade-off candidatos/recall/costo;
- arquitectura Atlas;
- búsqueda híbrida;
- fusión RRF.

Herramientas mínimas:

- simulador de coincidencia literal;
- inspector conceptual del pipeline E5 (rol → unidades → encoder → pooling → vector);
- simulador de chunking con tamaño y overlap;
- LAB 1 lexical;
- LAB 2 coseno;
- LAB 3 Top-k;
- LAB 4 BM25 vs semántica;
- LAB 5 HNSW;
- LAB 6 numCandidates;
- LAB 7 constructor $vectorSearch;
- LAB 8 RRF;
- LAB de Precision@k;
- LAB 9 constructor de evidencia.

## Cuaderno

El cuaderno ejecuta el pipeline reproducible:

1. corpus;
2. baseline BM25;
3. multilingual-e5-small;
4. búsqueda exacta local;
5. comparación de rankings;
6. Atlas Vector Search si está disponible;
7. evidencia final.

Si Atlas falla, la ruta local conserva el objetivo conceptual.

## QA

Ejecutar:

```bash
python utils/validate_session9.py
```

Debe impedir al menos:

- modificar S07 o S08;
- bajar de 35 diapositivas;
- usar términos antes de definirlos;
- reducir profundidad de definiciones/ejemplos;
- crear un laboratorio separado;
- volver a tres recursos visibles;
- sacar el WALL fuera de la presentación;
- exponer respuestas correctas;
- usar progreso manual para simular dominio;
- mezclar heartbeat S08/S09;
- romper notebook, JavaScript o navegación móvil.
