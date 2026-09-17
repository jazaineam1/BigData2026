# Taller domiciliario de control 1 — S1 a S6

## De datos crudos a una decisión explicable: SECOP + prensa + Cassandra + Neo4j

**Curso:** Big Data — Maestría en Analítica de Datos  
**Modalidad:** individual, para desarrollar en casa  
**Tiempo de referencia:** 6–8 horas de trabajo efectivo  
**Valor:** 100 puntos  
**Git/GitHub:** opcional; no suma ni resta puntos  
**Regla:** no hay preguntas de selección múltiple. Todo lo evaluado se demuestra construyendo artefactos reproducibles.

---

## 1. El reto

Trabajas como analista de datos en **Compras Claras**. El equipo recibe registros de contratación pública de SECOP, evidencia documental de prensa y un historial relacional de entidades, procesos y proveedores.

Tu jefe no te pide “usar MongoDB”, “usar Cassandra” ni “hacer un grafo”. Te plantea una necesidad profesional:

> Construir una ruta reproducible para reducir un universo de procesos, servir una bandeja operacional y agregar contexto relacional antes de que una persona decida qué revisar primero.

El taller sigue un solo hilo:

`datos crudos → perfilado → regla explicable → consulta documental → bandeja → consulta operacional → contexto relacional → informe`

El objetivo no es memorizar sintaxis. Debes demostrar que sabes **elegir y utilizar una estructura de datos según la pregunta que necesitas responder**.

---

## 2. Qué debes entregar

Tu notebook debe generar una carpeta `entrega_tc1/` con estos archivos:

| Archivo | Evidencia |
|---|---|
| `01_perfil_fuentes.json` | perfil reproducible de las fuentes |
| `02_bandeja_candidatos.csv` | regla de priorización aplicada |
| `03_mongo_resultados.json` | consultas documentales y agregación |
| `04_modelo_cassandra.cql` | modelo query-first y consulta operacional |
| `05_consultas_neo4j.cypher` | tres consultas relacionales en Cypher |
| `06_contexto_relacional.csv` | resultado relacional H2-R |
| `07_informe_tecnico.md` | síntesis técnica y límites |
| `manifest_tc1.json` | resultado de validación |
| `TC1_<codigo>.zip` | paquete final |

También debes entregar el `.ipynb` ejecutado y con sus salidas visibles.

Los datos están anclados a una versión fija del repositorio para que el taller sea reproducible. **No escribas manualmente resultados numéricos que pueden calcularse por código.**

---

# ETAPA 1 — Ingesta, perfil de fuentes y arquitectura

**Valor: 15 puntos**

## Qué debes aprender

Antes de decidir dónde almacenar o consultar datos debes entender qué información recibiste, cuál es su unidad de observación, qué claves permiten conectarla y qué problemas de calidad aparecen.

## Paso 1.1 — Carga las fuentes

Crea exactamente estas variables:

- `secop`: DataFrame de la muestra SECOP;
- `noticias`: lista de documentos JSON;
- `menciones`: lista de entidades resumidas desde prensa;
- `relacional`: DataFrame del historial relacional;
- `manifest_s06`: diccionario de controles del conjunto relacional.

Para `relacional`, carga `nit_entidad`, `nit_proveedor` e `id_proceso` como texto.

### Debes mostrar

Para cada fuente imprime:

1. tipo del objeto;
2. cantidad de filas o documentos;
3. columnas o claves principales;
4. un registro de ejemplo.

No avances si una fuente no carga.

## Paso 1.2 — Construye un perfil mínimo

Crea `perfil_fuentes` con cuatro bloques.

### SECOP

Calcula por código:

- número de filas;
- número de columnas;
- procesos únicos por `id_del_proceso`;
- entidades únicas;
- nulos en `precio_base`.

### Noticias

Calcula:

- número de documentos;
- noticias con `n_palabras > 800`;
- número de secciones distintas.

### Menciones

Calcula:

- número de entidades;
- número de entidades únicas;
- distribución de `nivel_menciones` con `value_counts()`.

### Relacional

Calcula:

- número de filas;
- registros `tipo_registro == "historico_adjudicado"`;
- entidades distintas por NIT;
- proveedores distintos por NIT.

Guarda el diccionario como `01_perfil_fuentes.json`.

## Paso 1.3 — Dibuja la arquitectura antes de implementarla

Crea `arquitectura_inicial` usando Mermaid. Debe representar como mínimo:

- `SECOP → pandas → bandeja`;
- `noticias → MongoDB → contexto de prensa → bandeja`;
- `bandeja → Cassandra → consulta operacional`;
- `bandeja + historial → Neo4j → revisión humana`.

El diagrama no se califica por diseño gráfico. Se valida que la arquitectura sea coherente con el problema.

### Entregable de la etapa

- `01_perfil_fuentes.json`
- `arquitectura_inicial` visible en el notebook

---

# ETAPA 2 — Construir una regla de priorización reproducible

**Valor: 20 puntos**

## Problema

La organización no puede revisar todos los procesos al mismo tiempo. Vas a construir una regla transparente para reducir el universo.

La regla es:

1. conservar procesos cuya entidad aparezca en el contexto de prensa;
2. conservar modalidades que contengan la palabra `directa`;
3. conservar procesos con `0` respuestas al procedimiento;
4. anexar el número y nivel de menciones de la entidad;
5. tratar el resultado como **candidatos de revisión**, no como procesos irregulares.

## Paso 2.1 — Prepara el contexto de menciones

Convierte `menciones` en `contexto_menciones` con únicamente:

- `entidad`;
- `noticias_entidad` — renombra el campo original `noticias`;
- `nivel_menciones`.

Verifica por código que `entidad` sea única. Si no lo fuera, el `merge` posterior podría multiplicar filas.

## Paso 2.2 — Reduce el universo paso a paso

Debes crear cuatro objetos separados.

### `paso1`

Procesos cuya `entidad` aparece en `contexto_menciones`.

### `paso2`

Desde `paso1`, conserva modalidades cuyo texto contenga `directa`, ignorando mayúsculas y minúsculas.

### `paso3`

Convierte `respuestas_al_procedimiento` a numérico y conserva exactamente las filas cuyo valor sea `0`.

### `candidatos`

Une `paso3` con `contexto_menciones` usando `merge(..., validate="many_to_one")`.

Crea además:

```python
trazabilidad_regla = {
    "entrada": len(secop),
    "entidad_en_prensa": len(paso1),
    "contratacion_directa": len(paso2),
    "cero_respuestas": len(paso3),
    "salida": len(candidatos)
}
```

Imprime ese diccionario. El evaluador debe poder reconstruir cómo se redujo el universo.

## Paso 2.3 — Construye la bandeja

Crea `bandeja` con estas columnas cuando estén disponibles:

- `id_del_proceso`;
- `entidad`;
- `nit_entidad`;
- `departamento_entidad`;
- `precio_base`;
- `modalidad_de_contratacion`;
- `respuestas_al_procedimiento`;
- `noticias_entidad`;
- `nivel_menciones`;
- `urlproceso`.

Convierte `precio_base` a numérico y ordena por:

1. `precio_base` descendente;
2. `id_del_proceso` ascendente.

Guarda `02_bandeja_candidatos.csv`.

### Entregable de la etapa

- `02_bandeja_candidatos.csv`
- `trazabilidad_regla` visible

---

# ETAPA 3 — Consultar evidencia documental con MongoDB

**Valor: 20 puntos**

Para que la nota no dependa de una cuenta externa usa `mongomock`. Replica las mismas consultas en Atlas si quieres practicar infraestructura real, pero no es requisito.

## Paso 3.1 — Crea una colección documental

Crea `coleccion` e inserta todos los documentos de `noticias`.

Muestra:

- `count_documents({})`;
- un `find_one()`;
- las claves del documento.

## Paso 3.2 — Filtro, proyección y orden

Construye una consulta que:

- filtre `n_palabras > 800`;
- proyecte únicamente `titulo`, `seccion`, `n_palabras`;
- oculte `_id`;
- ordene `n_palabras DESC` y `titulo ASC`.

Guarda la lista completa en `resultado_largas`.

## Paso 3.3 — Consulta focalizada en Bogotá

Construye `top_bogota` con:

- `seccion == "bogota"`;
- `n_palabras > 500`;
- proyección `titulo`, `fecha`, `n_palabras`;
- `_id` oculto;
- orden `n_palabras DESC`, `titulo ASC`;
- máximo 10 documentos.

## Paso 3.4 — Aggregation pipeline

Crea `pipeline_secciones` con cuatro etapas:

1. `$match`: `n_palabras > 0`;
2. `$group` por `seccion`, calculando `noticias` y `promedio_palabras`;
3. `$sort`: `noticias DESC`, `_id ASC`;
4. `$limit`: 10.

Ejecuta el pipeline en `resumen_secciones`.

## Paso 3.5 — Persiste el bloque

Guarda `03_mongo_resultados.json` con:

- documentos totales;
- número de noticias largas;
- `top_bogota`;
- `resumen_secciones`.

### Entregable de la etapa

- `03_mongo_resultados.json`

---

# ETAPA 4 — Diseñar Cassandra desde la consulta

**Valor: 15 puntos**

## Pregunta operacional

Laura repetirá muchas veces esta operación:

> Dado un `corte` y un `departamento`, devolver los 5 candidatos con mayor `valor_base`. En caso de empate, ordenar por `id_proceso` ascendente.

## Paso 4.1 — Prepara la estructura operacional

Crea `bandeja_operacional` desde `bandeja` y agrega:

- `corte = date(2026, 9, 3)`;
- `departamento` desde `departamento_entidad`;
- `valor_base` desde `precio_base`;
- `id_proceso` desde `id_del_proceso`;
- `estado_revision = "pendiente"`;
- `criterio = "entidad en prensa; contratación directa; 0 respuestas"`.

Conserva además `entidad`, `noticias_entidad`, `nivel_menciones` y `urlproceso`.

## Paso 4.2 — Diseña el DDL CQL

Escribe `cql_create` para:

`compras_claras.prioridades_por_corte_departamento`

El diseño debe permitir la consulta sin `ALLOW FILTERING`.

La clave debe corresponder a:

```text
PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
```

y el orden de clustering debe ser:

```text
CLUSTERING ORDER BY (valor_base DESC, id_proceso ASC)
```

Guarda `04_modelo_cassandra.cql`.

## Paso 4.3 — Demuestra el patrón sin depender de Astra

Implementa:

```python
def consulta_operacional(df, corte, departamento, n=5):
    ...
```

La función debe filtrar por la partición y reproducir el orden del modelo Cassandra.

Por código:

1. identifica el departamento con más filas en `bandeja_operacional`;
2. guárdalo como `departamento_prueba`;
3. ejecuta la función con `n=5`;
4. guarda la salida como `top5_operacional`.

### Entregable de la etapa

- `04_modelo_cassandra.cql`
- `top5_operacional` visible

---

# ETAPA 5 — Agregar contexto relacional con Neo4j

**Valor: 20 puntos**

La bandeja responde qué procesos revisar primero. Ahora necesitas conocer relaciones alrededor de una entidad:

`Entidad → Proceso → Proveedor → otros Procesos → otras Entidades`

## Paso 5.1 — Recupera el ancla desde el manifest

No escribas el NIT manualmente.

Crea:

```python
ancla = manifest_s06["ancla_pedagogica"]
nit_ancla = ...
```

Luego crea:

- `hist`: registros `historico_adjudicado` con NIT de proveedor no vacío;
- `hist_ancla`: filas del historial para `nit_ancla`.

Imprime entidad, procesos históricos distintos y proveedores distintos.

## Paso 5.2 — Calcula H2-R

Para cada proveedor usado por la entidad ancla calcula:

- `procesos_con_entidad`: número de `id_proceso` distintos con el ancla;
- `entidades_conectadas`: número de `nit_entidad` distintos para ese proveedor en todo el historial.

Construye:

- `prov_ancla`;
- `prov_global`;
- `resultado_h2r`.

Ordena `resultado_h2r` por:

1. `entidades_conectadas DESC`;
2. `procesos_con_entidad DESC`;
3. `nit_proveedor ASC`.

Crea:

- `maximo_h2r`;
- `mediana_referencia` desde `manifest_s06["mediana_maximo_conectadas_por_nit"]`.

Guarda `06_contexto_relacional.csv`.

## Paso 5.3 — Construye tres consultas Cypher

### Consulta 1 — Contexto

`cypher_contexto` debe recorrer:

```text
(:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(:Proveedor)
```

filtrando por `$nit_ancla`.

### Consulta 2 — Proveedor compartido

`cypher_compartido` debe salir del ancla, llegar a un proveedor y encontrar `otra:Entidad` distinta del ancla que comparta ese proveedor.

### Consulta 3 — Ranking relacional

`cypher_ranking` debe contar entidades **DISTINCT** por proveedor y ordenar ese conteo de mayor a menor.

Une las tres consultas y guarda `05_consultas_neo4j.cypher`.

## Paso 5.4 — Construye un subgrafo reproducible

Usa `networkx.DiGraph` y crea solo el subgrafo del ancla.

Usa identificadores con prefijo:

- entidad: `E:<nit_entidad>`;
- proceso: `P:<id_proceso>`;
- proveedor: `V:<nit_proveedor>`.

Relaciones:

- Entidad → Proceso, `relacion="PUBLICA"`;
- Proceso → Proveedor, `relacion="ADJUDICADO_A"`.

Deja:

- `nodos_grafo = G.number_of_nodes()`;
- `aristas_grafo = G.number_of_edges()`.

Puedes dibujarlo, pero recuerda: **la posición visual no es una medida de importancia**.

### Entregables de la etapa

- `05_consultas_neo4j.cypher`
- `06_contexto_relacional.csv`
- `G`, `nodos_grafo`, `aristas_grafo` visibles

---

# ETAPA 6 — Integración, informe y paquete final

**Valor: 10 puntos**

## Paso 6.1 — Arquitectura final

Crea `arquitectura_final` en Mermaid con:

- SECOP;
- noticias;
- MongoDB;
- pandas;
- bandeja;
- Cassandra;
- Neo4j;
- revisión humana.

Debe quedar claro que MongoDB y SECOP confluyen en la bandeja, y que después la bandeja alimenta una rama operacional y otra relacional.

## Paso 6.2 — Informe técnico

Crea `informe_tecnico` y guarda `07_informe_tecnico.md` con exactamente estas secciones:

1. `## 1. Problema y decisión`
2. `## 2. Fuentes y calidad`
3. `## 3. Regla de priorización`
4. `## 4. Por qué MongoDB`
5. `## 5. Por qué Cassandra`
6. `## 6. Por qué Neo4j`
7. `## 7. Límites de la evidencia`

Incluye desde tus variables, mediante f-string:

- tamaño inicial SECOP;
- tamaño final de la bandeja;
- máximo H2-R;
- mediana H2-R.

Debes declarar explícitamente:

- la evidencia de prensa utilizada es por entidad, no demuestra que una noticia se refiera al contrato específico;
- una conexión contractual describe relaciones registradas y **no demuestra irregularidad, favorecimiento ni colusión**;
- Cassandra se diseñó para el patrón `corte + departamento → top 5`.

## Paso 6.3 — Ejecuta el validador

El notebook incluye una celda final que descarga el validador versionado del curso y revisa los objetos que creaste.

El validador debe generar:

- `manifest_tc1.json`;
- puntaje sobre 100;
- nota sobre 5.0;
- huella SHA-256;
- `TC1_<codigo>.zip`.

---

# Rúbrica determinística

| Control | Evidencia | Puntos |
|---|---|---:|
| E1 carga | 4 fuentes correctas | 5 |
| E1 perfil | perfil y controles internos | 6 |
| E1 arquitectura | componentes y flujo | 4 |
| E2 contexto | tabla de menciones correcta | 5 |
| E2 regla | reducción reproducible | 9 |
| E2 bandeja | CSV final consistente | 6 |
| E3 colección | documentos cargados | 3 |
| E3 filtro | find/proyección/orden | 4 |
| E3 Bogotá | consulta focalizada | 4 |
| E3 pipeline | aggregation correcta | 6 |
| E3 artefacto | JSON persistido | 3 |
| E4 operacional | estructura de 77 filas | 4 |
| E4 query-first | PK + clustering correctos | 7 |
| E4 top 5 | consulta reproducida | 4 |
| E5 historial | ancla e historial correctos | 4 |
| E5 H2-R | métrica reproducida | 7 |
| E5 Cypher | tres patrones relacionales | 6 |
| E5 grafo | nodos y aristas correctos | 3 |
| E6 arquitectura | arquitectura final | 4 |
| E6 informe | hechos y límites | 4 |
| E6 artefactos | paquete completo | 2 |
| **Total** |  | **100** |

---

# Qué NO debes entregar

- capturas como sustituto del código;
- números copiados de una sesión;
- una explicación sin ejecución;
- consultas de MongoDB, CQL o Cypher que no correspondan a la pregunta del caso;
- afirmaciones de fraude o irregularidad basadas únicamente en la regla de priorización o en conexiones del grafo.

# Extensión opcional

Si quieres practicar infraestructura real puedes repetir:

1. MongoDB en Atlas;
2. CQL en Astra DB;
3. Cypher en AuraDB;
4. versionamiento en GitHub.

Estas extensiones no cambian la nota base. La nota evalúa **modelado, reproducibilidad, consulta e interpretación responsable**.