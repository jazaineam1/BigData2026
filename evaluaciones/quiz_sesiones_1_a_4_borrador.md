# Quiz 1 — Sesiones 1 a 4

> **BORRADOR DOCENTE · NO ENLAZAR EN LA PÁGINA DEL CURSO**
>
> Este archivo vive en el repositorio para conservar la planificación del quiz, pero no debe aparecer en `index.html`, tarjetas públicas, notebooks ni enlaces de navegación hasta que el docente decida aplicarlo.
>
> **Importante:** no publicar aquí la clave de respuestas. El repositorio es público y los estudiantes pueden inspeccionarlo aunque el archivo no esté enlazado.

## Alcance real

El quiz evalúa únicamente lo efectivamente trabajado en las sesiones 1 a 4.

En la sesión 4 el grupo llegó hasta **crear la base `compras_claras` en MongoDB Atlas y cargar las colecciones `noticias` y `entidades_noticias` con Python**. Por tanto, este quiz **NO** debe evaluar todavía:

- Aggregations de Atlas como práctica ya ejecutada;
- vistas de Atlas;
- `menciones_clasificadas`;
- resultados `111 / 25 / 6`;
- cruce `1.000 → 163 → 77`;
- límite `0/77`;
- Cassandra, CQL, partition key, clustering, Astra DB, SCB o `cassandra-driver`.

## Propósito

Comprobar si el estudiante puede **interpretar y tomar decisiones** con los conceptos de las primeras cuatro sesiones, no si memorizó definiciones o sintaxis.

Duración sugerida: **20–25 minutos**  
Número de preguntas: **12**  
Puntaje total: **100 puntos**

## Distribución

| Bloque | Preguntas | Peso |
|---|---:|---:|
| Sesión 1 — Fundamentos de Big Data y formatos | 3 | 20 |
| Sesión 2 — problema, proceso y arquitectura | 3 | 25 |
| Sesión 3 — modelo documental y MongoDB | 4 | 35 |
| Sesión 4 — Atlas hasta el punto realmente trabajado | 2 | 20 |

---

## Pregunta 1 — ¿Cuándo el problema justifica Big Data? — 7 puntos

Una entidad procesa cada mes un único archivo CSV de 25 MB con pandas y obtiene el informe en 40 segundos. El equipo propone migrar inmediatamente a una arquitectura distribuida “porque los datos son importantes”.

¿Cuál es la mejor decisión?

A. Migrar, porque cualquier dato institucional es Big Data.  
B. Migrar, porque CSV siempre requiere procesamiento distribuido.  
C. No necesariamente; primero debe demostrarse una necesidad asociada a volumen, velocidad, variedad u otra limitación real.  
D. No migrar, porque Big Data solo se utiliza con datos no estructurados.

**Qué busca medir:** distinguir importancia del dato de una necesidad real de arquitectura Big Data.

---

## Pregunta 2 — Estructura del dato — 7 puntos

Observa:

```json
{
  "entidad": "Ministerio X",
  "procesos": [
    {"id": "P1", "valor": 5000000},
    {"id": "P2", "valor": 8000000}
  ]
}
```

La clasificación más adecuada es:

A. dato estructurado tabular;  
B. dato semiestructurado;  
C. dato completamente no estructurado;  
D. archivo relacional normalizado.

**Qué busca medir:** reconocer estructuras anidadas y conectar el formato JSON con el modelo documental.

---

## Pregunta 3 — Formatos y significado — 6 puntos

¿Cuál afirmación es correcta?

A. Cambiar CSV por JSON convierte automáticamente un problema en Big Data.  
B. JSON permite representar naturalmente objetos y estructuras anidadas.  
C. XML es siempre más rápido que JSON.  
D. CSV soporta objetos anidados de manera nativa.

**Qué busca medir:** diferenciar formato de datos y problema Big Data.

---

## Pregunta 4 — Del problema a la decisión — 8 puntos

En el caso **Compras Claras**, la oficina tiene demasiados procesos para revisar manualmente.

¿Cuál es la formulación más útil para iniciar un proyecto analítico?

A. “Queremos usar inteligencia artificial”.  
B. “Queremos construir un dashboard”.  
C. “¿Qué procesos deberían revisarse primero y qué evidencia justifica esa prioridad?”.  
D. “Necesitamos Big Data”.

**Qué busca medir:** comenzar por una decisión profesional y no por una tecnología.

---

## Pregunta 5 — BI o Big Data — 8 puntos

Una organización tiene datos tabulares, históricos, de tamaño manejable y necesita un reporte descriptivo diario para diez analistas.

La primera arquitectura razonable sería:

A. Cassandra + Spark + Kafka necesariamente.  
B. Una solución BI puede ser suficiente mientras volumen, velocidad, variedad o complejidad no justifiquen otra arquitectura.  
C. MongoDB porque toda analítica moderna debe ser NoSQL.  
D. Hadoop porque Big Data reemplaza BI.

**Qué busca medir:** justificar una arquitectura y evitar sobredimensionarla.

---

## Pregunta 6 — Qué permite concluir una alerta — 9 puntos

Un análisis identifica procesos con duración atípica e información incompleta.

¿Cuál es la conclusión profesionalmente correcta?

A. Son contratos fraudulentos.  
B. La entidad cometió irregularidades.  
C. Son candidatos que ameritan revisión humana prioritaria; esos datos no demuestran fraude ni causalidad.  
D. El algoritmo demuestra incumplimiento.

**Qué busca medir:** separar priorización analítica de acusación o causalidad.

---

## Pregunta 7 — ¿Por qué aparece una base documental? — 8 puntos

Una noticia tiene esta estructura:

```json
{
  "titulo": "...",
  "autores": ["Ana", "Luis"],
  "entidades": [
    {"nombre": "Entidad A", "menciones": 3},
    {"nombre": "Entidad B", "menciones": 1}
  ]
}
```

¿Por qué este ejemplo ayuda a justificar un modelo documental?

A. Porque MongoDB no admite texto.  
B. Porque una noticia puede contener listas y objetos anidados que pertenecen naturalmente al mismo documento.  
C. Porque las bases relacionales no pueden almacenar cadenas.  
D. Porque MongoDB convierte cualquier consulta en Big Data.

**Qué busca medir:** entender el problema que resuelve el modelo documental.

---

## Pregunta 8 — Documento y colección — 8 puntos

Completa la analogía conceptual:

| Relacional | Documental |
|---|---|
| fila | documento |
| tabla | ? |

A. campo  
B. colección  
C. índice  
D. pipeline

**Qué busca medir:** vocabulario básico para poder razonar sobre MongoDB.

---

## Pregunta 9 — Leer una consulta MongoDB — 10 puntos

¿Qué hace el siguiente filtro?

```json
{
  "titulo": {
    "$regex": "salud",
    "$options": "i"
  }
}
```

A. Busca títulos exactamente iguales a `"salud"`.  
B. Busca títulos que contengan el patrón `"salud"` ignorando mayúsculas y minúsculas.  
C. Reemplaza `"salud"` por minúsculas.  
D. Agrupa todas las noticias relacionadas con salud.

**Qué busca medir:** leer una consulta ya escrita, no memorizarla.

---

## Pregunta 10 — Consultar no es modificar — 9 puntos

Un analista necesita primero **ver** las noticias cuyo título cumple una condición y luego, en otro momento, **cambiar** un campo de algunos documentos.

¿Cuál afirmación describe mejor la diferencia conceptual?

A. Recuperar documentos y modificarlos son la misma operación porque ambos usan filtros.  
B. Una consulta selecciona documentos; una actualización cambia el estado almacenado de los documentos seleccionados.  
C. Toda consulta MongoDB modifica los documentos recuperados.  
D. Para cambiar un documento primero hay que convertirlo a CSV.

**Qué busca medir:** distinguir lectura y escritura sin cobrar sintaxis no practicada.

> **Nota docente:** si al revisar el cierre real de S3 se confirma que agregaciones fueron practicadas en esa sesión, esta pregunta puede reemplazarse por una pregunta de `pipeline` de agregación. Si no, se conserva esta versión.

---

## Pregunta 11 — MongoDB Community vs Atlas — 10 puntos

¿Cuál describe mejor la diferencia que se trabajó al pasar a MongoDB Atlas?

A. Community y Atlas usan modelos de datos completamente distintos.  
B. Community es MongoDB ejecutado/administrado por nosotros; Atlas ofrece MongoDB como servicio administrado en la nube.  
C. Atlas solo almacena archivos CSV.  
D. Atlas sustituye Python.

**Qué busca medir:** distinguir motor/modelo de datos de la forma en que se administra el servicio.

---

## Pregunta 12 — ¿Dónde quedó realmente la sesión 4? — 10 puntos

Al finalizar la parte efectivamente realizada de la sesión 4 tenemos:

```text
Atlas
└── compras_claras
    ├── noticias
    └── entidades_noticias
```

¿Cuál afirmación es correcta?

A. Ya demostramos cuáles contratos son irregulares.  
B. Ya tenemos los datos almacenados en Atlas, pero todavía debemos consultarlos y transformarlos antes de producir una decisión analítica.  
C. Ya construimos una vista Cassandra.  
D. Ya terminamos todo el caso Compras Claras.

**Qué busca medir:** reconocer el estado real del proceso y no atribuirle resultados que todavía no se han construido.

---

## Variante de cierre integrador

Si se prefiere reducir el número de preguntas, las preguntas 11 y 12 pueden sustituirse por un caso integrador de 20 puntos:

> Compras Claras tiene información tabular de SECOP y noticias con campos anidados. El equipo necesita conservar ambas fuentes y, más adelante, priorizar revisión. Explica qué decisiones tomadas en las sesiones 1 a 4 justifican que pandas/SECOP y MongoDB Atlas coexistan, y señala una conclusión que todavía **no** puede hacerse con la evidencia disponible.

### Criterios de corrección del caso integrador

La respuesta debe contener cuatro elementos observables:

1. reconocer a SECOP como fuente tabular;
2. reconocer las noticias como una estructura documental/semiestructurada;
3. explicar Atlas como servicio administrado para MongoDB, no como un modelo distinto;
4. declarar un límite concreto: con solo haber cargado los datos todavía no se demuestra fraude, irregularidad ni una prioridad de contratos.

---

## Decisiones de aplicación pendientes

Antes de convertir este banco en el quiz definitivo, definir:

- herramienta de aplicación;
- si las preguntas se presentan en orden fijo o aleatorio;
- si se usa la pregunta 10 actual o una versión de agregaciones según el cierre real de S3;
- si se mantienen 12 preguntas o se usa el caso integrador final;
- tiempo exacto de aplicación;
- política sobre materiales abiertos;
- retroalimentación inmediata o posterior.

## Regla de publicación

- Mantener este archivo **fuera de los enlaces públicos del curso**.
- No incluirlo en la página principal ni en las tarjetas de sesiones.
- No enlazarlo desde los notebooks.
- No publicar en este archivo la clave de respuestas mientras el quiz no haya sido aplicado.
