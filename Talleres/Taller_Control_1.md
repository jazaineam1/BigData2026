# TC1 V4 — SECOP Data Pipeline

## De una API pública a un producto de datos multimodelo

**Curso:** Big Data · Maestría en Analítica de Datos  
**Modalidad:** parejas  
**Valor:** 100 puntos  
**Git/GitHub:** opcional; no suma ni resta puntos  
**Sesión LMS:** S08

---

## 1. Reto profesional

Su equipo recibe el encargo de construir un pipeline reproducible con información pública de contratación estatal.

No recibe un CSV “limpio”. Debe:

1. consultar SECOP II mediante la API pública de Datos Abiertos Colombia;
2. diseñar una consulta que reduzca transferencia innecesaria;
3. comparar una adquisición secuencial con otra concurrente;
4. demostrar que ambas producen el mismo snapshot;
5. registrar trazabilidad y calidad;
6. enriquecer procesos con contratos;
7. construir un modelo documental e idempotente en MongoDB Atlas;
8. generar un producto analítico;
9. diseñar una tabla Cassandra desde una consulta;
10. modelar contexto relacional con Neo4j;
11. justificar decisiones de ingeniería;
12. producir evidencia verificable por el LMS.

El resultado no es “un notebook que corre”: es un **producto de datos reproducible**.

---

## 2. Fuentes obligatorias

| Fuente | ID Socrata | Rol |
|---|---|---|
| SECOP II · Procesos de Contratación | `p6dx-8zbt` | universo de procesos |
| SECOP II · Contratos Electrónicos | `jbjy-vk9h` | enriquecimiento contractual |

La relación principal es:

```text
procesos.id_del_proceso
        │
        └── contratos.proceso_de_compra
```

Fuentes opcionales para extensión —no exigidas en TC1 V4—:

- Adiciones: `cb9c-h8sn`
- Ejecución: `mfmm-jqmq`
- DIVIPOLA: `gdxc-w37w`

Referencias:

- Procesos: https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt
- Contratos: https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Contratos-Electr-nicos/jbjy-vk9h
- Socrata API: https://dev.socrata.com/
- Application Tokens: https://dev.socrata.com/docs/app-tokens.html

---

## 3. Principios que se evaluarán

### 3.1 Query pushdown

No descargue 85 columnas para utilizar 10.

Construya consultas con:

- `$select`
- `$where`
- `$order`
- `$limit`
- `$offset`

La consulta debe tener un orden explícito y estable antes de paginar.

### 3.2 Concurrencia responsable

`ThreadPoolExecutor` se utiliza porque las peticiones HTTP son un problema principalmente **I/O-bound**.

Se permite entre **2 y 6 workers**.

No se califica:

> “Mi solución fue 4.2× más rápida”.

Sí se califica:

> “La adquisición secuencial y la concurrente produjeron exactamente el mismo snapshot y puedo justificar la configuración”.

### 3.3 Robustez

La API real puede responder:

- `429`
- `500`
- `502`
- `503`
- `504`
- timeout

Su cliente debe contemplar retry y backoff.

### 3.4 Reproducibilidad

Debe quedar evidencia de:

- endpoint;
- consulta;
- ventana temporal;
- timestamp UTC;
- filas;
- peticiones;
- workers;
- hashes;
- calidad;
- versión del taller.

### 3.5 Seguridad

Nunca entregue:

- App Token;
- URI de MongoDB Atlas;
- usuario;
- contraseña;
- secretos dentro de JSON/CSV/notebook.

---

# E1 — Adquisición SECOP verificable

**20 puntos**

## E1.1 Contrato de datos y consulta — 4 puntos

Complete:

```text
PAREJA_ID
INTEGRANTE_1
CODIGO_1
INTEGRANTE_2
CODIGO_2
```

El cuaderno asignará una ventana temporal de 2025 de forma determinística a partir de `PAREJA_ID`.

Construya:

- `data_contract`
- `query_plan`
- `WHERE_PROCESOS`
- `WHERE_CONTRATOS`

Antes de una descarga grande, pruebe ambos endpoints con 50 filas.

**Evidencia:** `00_dataset_contract.json`.

---

## E1.2 Descarga secuencial — 4 puntos

Implemente:

```python
descargar_secuencial(...)
```

Debe:

1. consultar por páginas;
2. usar `fetch_page()`;
3. acumular metadata HTTP;
4. detenerse al alcanzar el máximo o una página incompleta;
5. devolver DataFrame + metadata.

Objetivo orientativo:

- procesos: 6.000 filas;
- contratos: 4.000 filas.

El volumen exacto puede ser menor si la ventana asignada no contiene suficientes registros. El validador exige un volumen mínimo, no un número mágico idéntico para todos.

---

## E1.3 Descarga concurrente — 6 puntos

Implemente:

```python
descargar_concurrente(...)
```

con:

```python
ThreadPoolExecutor
```

Pruebe una configuración entre 2 y 6 workers.

Debe construir:

```python
benchmark_threads
```

con:

- filas secuenciales;
- filas concurrentes;
- tiempo secuencial;
- tiempo concurrente;
- hash secuencial;
- hash concurrente;
- `same_rows`;
- `same_hash`.

**Condición de aprendizaje:** los hashes deben coincidir.

---

## E1.4 Más información SECOP + calidad — 6 puntos

Descargue contratos para la misma ventana.

Calcule:

```text
join_coverage =
procesos que encuentran al menos un contrato
/
procesos totales
```

Construya:

- `quality_report`;
- `acquisition_manifest`.

Guarde RAW como:

```text
entrega_tc1/raw/procesos.parquet
entrega_tc1/raw/contratos.parquet
```

Y:

```text
01_acquisition_manifest.json
01_benchmark_threads.json
01_quality_report.json
```

---

# E2 — Modelo documental + Atlas

**30 puntos**

## E2.1 Modelo documental — 6 puntos

Integre procesos y contratos.

Construya:

```python
historico
documentos
```

`historico` debe tener una fila por proceso.

Cada documento debe contener al menos:

```json
{
  "id_proceso": "...",
  "entidad": {
    "nit": "...",
    "nombre": "...",
    "departamento": "...",
    "ciudad": "..."
  },
  "proceso": {
    "fecha_publicacion": "...",
    "precio_base": 0,
    "modalidad": "...",
    "estado": "...",
    "adjudicado": false
  },
  "proveedor_adjudicado": {
    "nit": "...",
    "nombre": "..."
  },
  "contratos_resumen": {
    "cantidad": 0,
    "valor_total": 0,
    "estados": []
  },
  "metadata_ingesta": {
    "dataset": "p6dx-8zbt",
    "pareja_id": "...",
    "window_start": "...",
    "window_end": "..."
  }
}
```

Guarde:

- `02_secop_integrado.parquet`
- `02_modelo_documental.json`

---

## E2.2 Atlas real e idempotencia — 8 puntos

Atlas es obligatorio.

Use:

- `MongoClient`;
- `ping`;
- índice único;
- `bulk_write`;
- `UpdateOne(..., upsert=True)`.

Base:

```text
tc1_bigdata_v4
```

Colección:

```text
secop_pipeline_<PAREJA_ID>
```

Ejecute la carga dos veces.

Construya:

```python
atlas_idempotencia = {
  "count_after_first": ...,
  "count_after_second": ...,
  "duplicates_after_second": ...
}
```

La segunda ejecución no debe crear documentos adicionales.

---

## E2.3 Índices — 5 puntos

Cree:

1. índice único por `id_proceso`;
2. al menos un índice compuesto que tenga sentido para una consulta del taller.

Guarde los nombres/propiedades en:

```python
atlas_indexes
```

No cree índices sin explicar qué consulta soportan.

---

## E2.4–E2.5 Consultas — 8 puntos

### Consulta A

Conteo de procesos que:

- tienen `precio_base > 0`;
- tienen al menos un contrato relacionado.

### Consulta B

Top 10 por:

```text
contratos_resumen.valor_total DESC
id_proceso ASC
```

El resultado debe conservar:

- `id_proceso`;
- `valor_contratos`.

---

## E2.6 Evidencia — 3 puntos

Guarde:

```text
02_atlas_evidence.json
```

No incluya secretos.

---

# E3 — Producto analítico

**10 puntos**

Construya un pipeline Atlas llamado:

```python
pipeline_bandeja
```

Debe:

- conservar procesos con precio positivo;
- exigir al menos un contrato asociado;
- calcular/exponer `valor_contratos`;
- ordenar `valor_contratos DESC`;
- desempatar `id_proceso ASC`;
- limitar a 100.

Genere:

```python
bandeja_documentos
bandeja_historica
```

Guarde:

```text
03_bandeja_historica.csv
```

La bandeja representa prioridad de revisión. **No es evidencia de fraude.**

---

# E4 — Cassandra query-first

**15 puntos**

Pregunta:

> Para un año y departamento, mostrar hasta 10 procesos priorizados, empezando por mayor valor contractual; en empate usar ID de proceso ascendente.

Construya:

```text
tc1.procesos_por_anio_departamento
```

El diseño esperado debe permitir:

```text
WHERE anio = ?
  AND departamento = ?
ORDER BY valor_contratos DESC, id_proceso ASC
LIMIT 10
```

sin `ALLOW FILTERING`.

Variables evaluadas:

- `bandeja_cassandra`
- `cql_create`
- `consulta_cassandra_simulada`
- `particion_prueba`
- `top10_cassandra`

Guarde:

```text
04_modelo_cassandra.cql
```

---

# E5 — Neo4j y contexto relacional

**20 puntos**

Pregunta:

> ¿Qué proveedores conectan a la entidad con mayor número de procesos adjudicados con otras entidades dentro de su snapshot?

Calcule el ancla desde sus propios datos.

Variables:

- `hist_adjudicado`
- `nit_ancla`
- `entidad_ancla`
- `resultado_relacional`

Cypher:

- `cypher_carga`
- `cypher_contexto`
- `cypher_compartidos`
- `cypher_ranking`

Modelo:

```text
Entidad --PUBLICA------> Proceso
Proceso --ADJUDICADO_A-> Proveedor
```

Además cree un `nx.DiGraph()` equivalente para que el validador compruebe estructura.

Guarde:

- `05_neo4j_consultas.cypher`
- `05_resultado_relacional.csv`

---

# E6 — Decisiones + informe

**5 puntos**

## Decision log

Cree:

```python
decision_log
```

con mínimo 3 decisiones.

Cada una debe incluir:

```json
{
  "decision": "...",
  "evidence": "...",
  "alternative": "...",
  "risk": "..."
}
```

No escriba frases genéricas.

Ejemplo de evidencia válida:

> Con 4 workers obtuvimos el mismo hash que secuencial y no observamos 429; 6 workers no redujo de forma material el tiempo.

Guarde:

```text
06_decision_log.json
```

## Informe

Debe contener exactamente estas secciones:

```markdown
## 1. Adquisición y contrato de datos
## 2. Concurrencia, robustez y calidad
## 3. Modelo documental e idempotencia Atlas
## 4. Producto analítico y Cassandra
## 5. Neo4j, decisiones y límites
```

Debe afirmar explícitamente que priorización y conexiones contractuales **no demuestran por sí solas fraude, favorecimiento o colusión**.

Guarde:

```text
06_informe_tecnico.md
```

---

# 4. Entrega final

El validador debe producir:

```text
manifest_tc1.json
TC1_<pareja>.zip
```

La carpeta debe contener:

```text
entrega_tc1/
├── 00_dataset_contract.json
├── 01_acquisition_manifest.json
├── 01_benchmark_threads.json
├── 01_quality_report.json
├── raw/
│   ├── procesos.parquet
│   └── contratos.parquet
├── 02_secop_integrado.parquet
├── 02_modelo_documental.json
├── 02_atlas_evidence.json
├── 03_bandeja_historica.csv
├── 04_modelo_cassandra.cql
├── 05_neo4j_consultas.cypher
├── 05_resultado_relacional.csv
├── 06_decision_log.json
├── 06_informe_tecnico.md
└── manifest_tc1.json
```

Además entregue el notebook ejecutado.

---

# 5. Qué NO se acepta

- sustituir la API por los seis CSV del taller antiguo;
- descargar una exportación completa y fingir que se utilizó paginación;
- usar más de 6 workers;
- considerar una ejecución más rápida como evidencia suficiente;
- reportar `same_hash=True` sin calcular hashes;
- borrar la colección antes de cada carga para ocultar duplicados;
- usar `insert_many()` como sustituto de idempotencia;
- usar `mongomock` para E2;
- guardar secretos;
- escribir números manualmente en los artefactos;
- usar `ALLOW FILTERING`;
- afirmar que el producto analítico o una conexión en el grafo demuestra fraude.

---

# 6. Modo contingencia

Si Datos Abiertos Colombia presenta una indisponibilidad prolongada durante una sesión evaluativa, el docente puede habilitar un snapshot de contingencia.

Ese snapshot:

- no cambia la rúbrica;
- no exime de implementar secuencial/concurrente;
- debe conservar metadata y hashes;
- se identifica explícitamente como contingencia en el manifest.

La contingencia existe para proteger la evaluación de una falla externa, no para reemplazar la ruta principal.

---

# 7. Criterio de éxito

El taller está terminado cuando el equipo puede responder, con evidencia:

1. qué descargó;
2. desde dónde;
3. con qué consulta;
4. cuándo;
5. cuánto;
6. qué errores o reintentos ocurrieron;
7. por qué eligió su nivel de concurrencia;
8. por qué secuencial y concurrente representan el mismo snapshot;
9. cómo evitó duplicados en Atlas;
10. qué pregunta responde cada modelo;
11. qué limitaciones tiene el análisis.

Ese conjunto de evidencias es lo que registra el LMS.
