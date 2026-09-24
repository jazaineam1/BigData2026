# Módulo 05 · Elasticsearch — arquitectura vigente de S07

## Objetivo

S07 enseña a construir y evaluar un buscador textual de forma reproducible. Elasticsearch se enseña primero como **motor independiente** mediante Console y después se automatiza desde Python.

Al terminar, el estudiante debe poder explicar y repetir:

1. documento, campo, índice, corpus y mapping;
2. `text`, `keyword` y full-text search;
3. tokenizer, token, analyzer, index-time y search-time;
4. `/_analyze`, índice invertido, `match`, `term`, BM25 y `_score`;
5. uso de Elastic Console para crear un índice, indexar documentos y buscar;
6. cliente Python, `bulk()` y verificación con `count()`;
7. `multi_match`, `bool`, `must`, `filter`, boost y highlight;
8. diagnóstico con API/UI;
9. Precision@5 y comparación A/B;
10. transferencia del caso contractual a noticias.

## Regla estricta: solo dos recursos visibles

S07 tiene **exactamente dos recursos para el estudiante**:

1. **Presentación interactiva:** `Presentaciones/s07-del-vecindario-al-texto.html`
2. **Cuaderno Python:** `Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb`

No existe un laboratorio separado. Las actividades D1–D8, S07 Live y el simulador de tokenización están **embebidos en la presentación**.

No crear una tercera página, tutorial o herramienta para S07. Si aparece una nueva actividad, debe agregarse como una nueva diapositiva o integrarse en una diapositiva existente.

## Secuencia de clase

```text
definición
  ↓
ejemplo mínimo
  ↓
demostración / herramienta
  ↓
desafío embebido D1–D8
  ↓
primer intento
  ↓
pista si falla
  ↓
reintento para dominio
  ↓
cuaderno Python cuando toca automatizar
```

### Regla terminológica

Ningún término técnico debe utilizarse como requisito previo antes de haber sido definido.

Una definición núcleo debe incluir, cuando aplique:

- qué es;
- para qué sirve;
- ejemplo mínimo;
- cómo observarlo o medirlo;
- error frecuente o límite.

Ejemplo: antes de pedir `POST /_analyze`, S07 define **API**, **método HTTP**, **POST**, **ruta**, **cuerpo JSON**, **Console**, **analyzer** y **token**.

## Tokenización

La presentación incluye un laboratorio interactivo embebido:

```text
texto
  ↓
tokenizer
  ↓
filtros
  ↓
tokens
```

Permite comparar al menos:

- `standard`;
- `whitespace`;
- `keyword`;
- `letter`;
- `edge n-gram`.

La simulación es pedagógica. Para verificar tokens reales se usa `POST /_analyze` en Elastic Console.

## BM25

BM25 **no se instala aparte para usarlo en Elasticsearch**. Es la similitud lexical predeterminada para campos de texto, salvo configuración diferente.

S07 ya no necesita `rank-bm25` en Python para enseñar este concepto. El estudiante observa BM25 a través del ranking y `_score` del propio Elasticsearch.

`corpus` significa el conjunto de documentos sobre el que se busca o evalúa.

## S07 Live embebido

Las ocho actividades están dentro de la presentación:

- D1 ranking vs filtro;
- D2 mapping;
- D3 analyzer;
- D4 API `/_analyze`;
- D5 bulk/count;
- D6 Query DSL;
- D7 Precision@5;
- D8 transferencia a noticias.

La respuesta correcta nunca se expone en HTML.

Se guardan dos métricas:

- **primer intento:** fija el puntaje de ranking;
- **dominio:** puede mejorar después de pistas y reintentos.

## Teacher Wall

El control docente vive **dentro del mismo archivo de presentación**, no es una tercera herramienta.

Modo docente:

```text
Presentaciones/s07-del-vecindario-al-texto.html?wall=docente
```

Funciones:

- autenticación por PIN validado en Supabase;
- crear una nueva partida con código aleatorio;
- copiar enlace estudiante;
- ver ranking en vivo;
- ver primer intento y dominio por desafío;
- reiniciar la partida actual conservando alias;
- cerrar/reabrir una partida;
- seleccionar rondas anteriores.

El PIN no debe aparecer en HTML, JavaScript, README ni SQL en texto plano. El backend conserva únicamente su hash.

## Contraste y accesibilidad

Regla visual obligatoria:

> toda caja clara debe definir texto oscuro incluso cuando está dentro de una diapositiva oscura.

El validador debe comprobar reglas para `.dark .card`, `.dark .note` y tablas.

La presentación debe conservar:

- navegación táctil;
- controles ≥ 44 px en móvil;
- scroll vertical dentro de la diapositiva;
- inputs de al menos 16 px en móvil;
- soporte para safe areas.

## Backend

Supabase mantiene:

- sesiones/partidas;
- preguntas;
- participantes;
- respuestas;
- ranking por primer intento;
- dominio;
- control docente protegido.

La migración canónica vive en:

`infraestructura/modules/05-elasticsearch/s07-live-supabase.sql`

No se guardan correos, contraseñas ni credenciales de Elasticsearch.

## QA

Ejecutar:

```bash
python utils/validate_session7_elasticsearch.py
```

Debe comprobar, como mínimo:

- exactamente 35 diapositivas;
- D1–D8 embebidos en la presentación;
- tokenizador interactivo embebido;
- Teacher Wall embebido;
- ausencia de enlaces a laboratorio/tokenizer externos;
- solo dos recursos S07;
- definición previa de API/POST/Console;
- BM25 explicado como parte de Elasticsearch;
- notebook sin `rank-bm25`;
- contraste en fondos oscuros;
- respuestas correctas no expuestas en HTML.
