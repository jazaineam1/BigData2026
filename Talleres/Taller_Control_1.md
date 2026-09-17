# Taller domiciliario de control 1 — S1 a S6

## Construir un histórico SECOP y convertirlo en una solución NoSQL

**Curso:** Big Data — Maestría en Analítica de Datos  
**Modalidad:** parejas  
**Valor:** 100 puntos  
**Git/GitHub:** opcional; no suma ni resta puntos  
**Regla:** no hay preguntas de selección múltiple.

---

# 1. ¿Qué van a hacer?

En las clases ya practicaron con una muestra de 1.000 procesos y aprendieron a:

- cargar archivos con Python;
- trabajar con documentos;
- conectarse a MongoDB Atlas;
- usar `insert_many()`;
- consultar con `count_documents()` y `find()`;
- usar filtros, proyecciones, orden y límites;
- construir pipelines de agregación;
- pensar Cassandra desde la consulta;
- modelar relaciones Entidad → Proceso → Proveedor en Neo4j.

Este taller **no repite esos ejercicios**.

Ahora recibirán **seis archivos SECOP distintos, cada uno de 1.000 filas**, y deberán construir una solución nueva:

```text
6 CSV
  ↓
histórico de 6.000 registros
  ↓
JSON documental
  ↓
MongoDB Atlas real
  ↓
consultas nuevas
  ↓
bandeja histórica
  ↓
Cassandra query-first
  ↓
Neo4j / contexto relacional
  ↓
informe técnico
```

La pregunta central es:

> ¿Pueden tomar varias fuentes crudas, convertirlas en una colección documental útil, cargarlas correctamente en Atlas y reutilizar los mismos datos para responder preguntas operacionales y relacionales diferentes?

---

# 2. ¿Qué deben entregar?

El notebook debe generar la carpeta `entrega_tc1/` con estos archivos:

| Archivo | Qué demuestra |
|---|---|
| `01_secop_historico_6000.json` | que integraron y transformaron los seis CSV |
| `01_control_ingesta.json` | que verificaron la carga y la calidad básica |
| `02_atlas_consultas.json` | que cargaron Atlas y resolvieron tres consultas |
| `03_bandeja_historica.csv` | que construyeron una salida nueva desde Atlas |
| `04_modelo_cassandra.cql` | que diseñaron una tabla desde otra consulta |
| `05_neo4j_consultas.cypher` | que saben expresar carga y recorridos en Cypher |
| `05_resultado_relacional.csv` | que calcularon proveedores compartidos |
| `06_informe_tecnico.md` | que pueden explicar lo construido y sus límites |
| `manifest_tc1.json` | resultado del validador |
| `TC1_<pareja>.zip` | paquete final |

Además deben entregar el `.ipynb` ejecutado y con las salidas visibles.

---

# ETAPA 1 — Construyan un histórico nuevo de SECOP

**20 puntos**

## Objetivo

Demostrar que pueden recibir varios archivos con el mismo esquema, integrarlos por código, limpiar sus tipos y convertirlos en documentos JSON listos para MongoDB.

## Paso 1.1 — Cargar los seis archivos

Los archivos asignados son:

```text
prueba_chunk_0000000.csv
prueba_chunk_0001000.csv
prueba_chunk_0002000.csv
prueba_chunk_0003000.csv
prueba_chunk_0004000.csv
prueba_chunk_0005000.csv
```

Las URL ya están disponibles en el diccionario `URLS_SECOP` del notebook.

Deben programar un ciclo que, para cada elemento de `URLS_SECOP`:

1. lea el archivo con `pd.read_csv(..., low_memory=False)`;
2. agregue una columna `archivo_origen` con el nombre del archivo;
3. imprima el nombre, número de filas y número de columnas;
4. agregue el DataFrame a una lista llamada `fragmentos`.

Después concatenen los seis DataFrames en:

```python
secop_historico
```

No concatenen los archivos manualmente ni en Excel.

### Evidencia que debe quedar visible

Calculen por código e impriman:

- número de archivos cargados;
- número total de filas;
- número de procesos únicos en `id_del_proceso`;
- número de departamentos distintos.

No escriban esos resultados manualmente.

---

## Paso 1.2 — Crear un esquema más pequeño y útil

El dataset original tiene muchas columnas. Para este taller deben construir un DataFrame llamado `historico` con **exactamente estos 16 campos y en este orden**:

| Campo de `historico` | Campo original |
|---|---|
| `id_proceso` | `id_del_proceso` |
| `entidad` | `entidad` |
| `nit_entidad` | `nit_entidad` |
| `departamento` | `departamento_entidad` |
| `ciudad` | `ciudad_entidad` |
| `fecha_publicacion` | `fecha_de_publicacion` |
| `anio` | se deriva de `fecha_publicacion` |
| `precio_base` | `precio_base` |
| `modalidad` | `modalidad_de_contratacion` |
| `respuestas` | `respuestas_al_procedimiento` |
| `estado` | `estado_del_procedimiento` |
| `adjudicado` | `adjudicado` |
| `proveedor` | `nombre_del_proveedor` |
| `nit_proveedor` | `nit_del_proveedor_adjudicado` |
| `url` | `urlproceso` |
| `archivo_origen` | creado en el paso anterior |

### Conversión de tipos obligatoria

Deben aplicar:

```python
pd.to_datetime(..., errors="coerce")
pd.to_numeric(..., errors="coerce")
```

según corresponda.

`adjudicado` debe terminar como booleano `True/False`, no como texto `"Si"/"No"`.

`anio` debe derivarse de `fecha_publicacion`, no copiarse manualmente.

Al terminar muestren:

```python
historico.head()
historico.dtypes
```

---

## Paso 1.3 — Convertir el histórico a documentos JSON

MongoDB trabaja naturalmente con documentos. Ahora transformen `historico` en una lista de diccionarios llamada:

```python
documentos
```

Una forma válida es:

```python
documentos = json.loads(
    historico.to_json(
        orient="records",
        force_ascii=False,
        date_format="iso"
    )
)
```

Esto además convierte los faltantes en `null` de JSON en lugar de dejar el texto `"nan"`.

## ¿Cómo debe verse el JSON?

El archivo debe ser **un arreglo de documentos**:

```json
[
  {
    "id_proceso": "CO1.REQ....",
    "entidad": "...",
    "nit_entidad": "...",
    "departamento": "...",
    "ciudad": "...",
    "fecha_publicacion": "2025-07-23T00:00:00.000",
    "anio": 2025,
    "precio_base": 250000000.0,
    "modalidad": "...",
    "respuestas": 0,
    "estado": "...",
    "adjudicado": true,
    "proveedor": "...",
    "nit_proveedor": "...",
    "url": "https://...",
    "archivo_origen": "prueba_chunk_0000000.csv"
  }
]
```

Los valores anteriores son únicamente un ejemplo de estructura. **No son resultados del taller.**

Guarden:

```text
entrega_tc1/01_secop_historico_6000.json
```

---

## Paso 1.4 — Crear controles de ingesta

Construyan este diccionario usando resultados calculados:

```python
control_ingesta = {
    "archivos_cargados": ...,
    "filas_integradas": ...,
    "procesos_unicos": ...,
    "departamentos": ...,
    "anio_min": ...,
    "anio_max": ...,
    "documentos_json": ...
}
```

Guárdenlo como:

```text
entrega_tc1/01_control_ingesta.json
```

### Al terminar la etapa 1 deben tener

- `fragmentos`
- `secop_historico`
- `historico`
- `documentos`
- `control_ingesta`
- dos archivos JSON en `entrega_tc1/`

---

# ETAPA 2 — Carguen el histórico en MongoDB Atlas

**30 puntos**

## Objetivo

Demostrar que pueden pasar de un archivo construido por ustedes a una **colección real en MongoDB Atlas** y consultarla.

En esta etapa Atlas **sí es obligatorio**. No se acepta `mongomock` como sustituto.

---

## Paso 2.1 — Conectarse a Atlas

Usen la técnica practicada en clase:

```python
from getpass import getpass
from urllib.parse import quote_plus
from pymongo import MongoClient
```

Obtengan de Atlas su plantilla de conexión SRV, por ejemplo:

```text
mongodb+srv://<db_username>:<db_password>@cluster....
```

Pidan:

- la plantilla SRV con `input()`;
- el usuario con `input()`;
- la contraseña con `getpass()`.

Reemplacen `<db_username>` y `<db_password>` usando el usuario y la contraseña codificada con `quote_plus()`.

**Nunca escriban la contraseña directamente en una celda.**

Creen `client` y comprueben la conexión con:

```python
client.admin.command("ping")
```

Deben dejar:

```python
atlas_ping = True
atlas_server_version = ...
```

La versión se puede obtener desde `client.server_info()`.

---

## Paso 2.2 — Crear la colección de la pareja

Usen exactamente:

```text
base de datos: tc1_bigdata
colección: secop_historico_<PAREJA_ID>
```

En Python:

```python
db = client["tc1_bigdata"]
NOMBRE_COLECCION = f"secop_historico_{PAREJA_ID}"
coleccion = db[NOMBRE_COLECCION]
```

Antes de insertar, vacíen **solo su colección** para que el notebook pueda ejecutarse de nuevo sin duplicar documentos:

```python
coleccion.delete_many({})
```

Carguen una copia de sus documentos:

```python
coleccion.insert_many([dict(d) for d in documentos])
```

Después verifiquen la carga:

```python
documentos_atlas = coleccion.count_documents({})
```

Impriman:

- base de datos;
- nombre de colección;
- número de documentos cargados.

---

## Paso 2.3 — Consulta A: contar procesos recientes de contratación directa

Construyan `filtro_a` para contar documentos que cumplan **todas** estas condiciones:

- `anio >= 2024`;
- `modalidad` contiene la palabra `directa` sin distinguir mayúsculas/minúsculas;
- `respuestas == 0`;
- `precio_base > 0`.

Para expresar el texto en MongoDB utilicen `$regex` y `$options`:

```python
"modalidad": {
    "$regex": "directa",
    "$options": "i"
}
```

No se entrega el filtro completo ni el resultado numérico.

Ejecuten:

```python
resultado_a = coleccion.count_documents(filtro_a)
```

---

## Paso 2.4 — Consulta B: buscar los procesos de mayor valor

Construyan `filtro_b` para:

- `anio == 2025`;
- `departamento == "Antioquia"`;
- `precio_base > 0`.

Construyan `proyeccion_b` para mostrar únicamente:

- `id_proceso`;
- `entidad`;
- `precio_base`;
- `modalidad`;

Debe ocultarse `_id`.

Ejecuten un `find()` que además:

1. ordene `precio_base DESC`;
2. en empate ordene `id_proceso ASC`;
3. devuelva máximo 10 documentos.

Conviertan el cursor a lista y guárdenlo en:

```python
resultado_b
```

---

## Paso 2.5 — Consulta C: agregación por departamento

Construyan `pipeline_c` con **exactamente cuatro etapas**.

### `$match`

```text
anio >= 2024
precio_base > 0
```

### `$group`

Agrupen por `departamento` y calculen:

```text
procesos       = cantidad de documentos
valor_total    = suma de precio_base
valor_promedio = promedio de precio_base
```

### `$sort`

```text
procesos DESC
_id ASC
```

### `$limit`

```text
8
```

Ejecuten:

```python
resultado_c = list(coleccion.aggregate(pipeline_c))
```

---

## Paso 2.6 — Guardar evidencia de las consultas

Construyan:

```python
atlas_resultados = {
    "carga": {
        "base_datos": "tc1_bigdata",
        "coleccion": NOMBRE_COLECCION,
        "documentos": documentos_atlas,
        "server_version": atlas_server_version
    },
    "consulta_a": {
        "filtro": filtro_a,
        "resultado": resultado_a
    },
    "consulta_b": {
        "filtro": filtro_b,
        "proyeccion": proyeccion_b,
        "resultado": resultado_b
    },
    "consulta_c": {
        "pipeline": pipeline_c,
        "resultado": resultado_c
    }
}
```

Guárdenlo como:

```text
entrega_tc1/02_atlas_consultas.json
```

No guarden URI, usuario ni contraseña.

---

# ETAPA 3 — Construyan una bandeja histórica desde Atlas

**10 puntos**

## Objetivo

Usar Atlas para producir una salida diferente de las trabajadas en clase.

La nueva pregunta es:

> ¿Cuáles son los procesos recientes, adjudicados, de mayor exposición económica y con baja participación dentro del histórico construido por la pareja?

Construyan un pipeline llamado `pipeline_bandeja`.

## `$match`

Conserven documentos con:

```text
anio >= 2024
adjudicado == true
precio_base >= 50000000
respuestas <= 1
```

## `$project`

Conserven:

```text
id_proceso
entidad
nit_entidad
departamento
fecha_publicacion
anio
precio_base
respuestas
proveedor
nit_proveedor
url
```

Oculten `_id`.

## `$sort`

```text
precio_base DESC
fecha_publicacion DESC
id_proceso ASC
```

## `$limit`

```text
100
```

Ejecuten el pipeline directamente en Atlas:

```python
bandeja_documentos = list(coleccion.aggregate(pipeline_bandeja))
bandeja_historica = pd.DataFrame(bandeja_documentos)
```

Guarden:

```text
entrega_tc1/03_bandeja_historica.csv
```

La bandeja representa **prioridad de revisión**, no evidencia de fraude o irregularidad.

---

# ETAPA 4 — Diseñen Cassandra desde una consulta nueva

**15 puntos**

## Pregunta operacional

> Para un `anio` y un `departamento`, mostrar hasta 10 procesos de la bandeja empezando por los más recientes. Si dos procesos tienen la misma fecha, mostrar primero el de mayor `precio_base`; si persiste el empate, ordenar por `id_proceso` ascendente.

Esta consulta **no es la de la sesión 5**.

## Paso 4.1 — Preparar los datos

Creen `bandeja_cassandra` desde `bandeja_historica` con:

```text
anio
departamento
fecha_publicacion
precio_base
id_proceso
entidad
respuestas
proveedor
url
```

Conviertan `fecha_publicacion` a `datetime`.

## Paso 4.2 — Diseñar la tabla

La tabla debe llamarse:

```text
tc1.procesos_por_anio_departamento
```

Creen el texto CQL en:

```python
cql_create
```

La clave primaria debe estar diseñada para responder la consulta con igualdad sobre `anio + departamento`, sin `ALLOW FILTERING`.

Las columnas de clustering deben permitir obtener directamente el orden solicitado:

```text
fecha_publicacion DESC
precio_base DESC
id_proceso ASC
```

No se entrega el `PRIMARY KEY`: deben deducirlo a partir de la pregunta.

Guarden:

```text
entrega_tc1/04_modelo_cassandra.cql
```

## Paso 4.3 — Probar el patrón de acceso

Implementen:

```python
def consulta_cassandra_simulada(df, anio, departamento, n=10):
    ...
```

Debe:

1. filtrar por `anio` y `departamento`;
2. ordenar fecha DESC, precio DESC e ID ASC;
3. retornar `n` filas.

Para la prueba determinen por código la partición `(anio, departamento)` con mayor cantidad de filas.

Si dos particiones tienen la misma cantidad de filas, desempaten por:

1. `anio ASC`;
2. `departamento ASC`.

Guárdenla como:

```python
particion_prueba = (anio, departamento)
```

Ejecuten la función con `n=10` y guarden:

```python
top10_cassandra
```

---

# ETAPA 5 — Construyan contexto relacional con el histórico propio

**20 puntos**

## Pregunta

> ¿Qué proveedores conectan a la entidad con mayor número de procesos adjudicados con otras entidades dentro de los 6.000 registros?

No utilicen el NIT ancla usado en clase. El ancla de este taller debe salir de sus datos.

## Paso 5.1 — Construir el historial adjudicado

Desde `historico`, creen `hist_adjudicado` conservando registros donde:

- `adjudicado == True`;
- `nit_entidad` no sea nulo ni vacío;
- `nit_proveedor` no sea nulo ni vacío;
- `nit_proveedor` no sea `"No Definido"`.

Conserven el orden original de las filas.

## Paso 5.2 — Encontrar el ancla

Agrupen `hist_adjudicado` por `nit_entidad` y calculen el número de `id_proceso` distintos.

Ordenen:

1. procesos DESC;
2. `nit_entidad` ASC.

La primera entidad define:

```python
nit_ancla
entidad_ancla
```

Ambos valores deben calcularse por código.

## Paso 5.3 — Medir proveedores compartidos

Para cada proveedor utilizado por el ancla calculen:

```text
procesos_con_ancla  = procesos distintos del proveedor con el ancla
entidades_conectadas = entidades distintas relacionadas con ese proveedor en todo hist_adjudicado
```

Construyan:

```python
prov_ancla
prov_global
resultado_relacional
```

Ordenen `resultado_relacional` por:

```text
entidades_conectadas DESC
procesos_con_ancla DESC
nit_proveedor ASC
```

Guarden:

```text
entrega_tc1/05_resultado_relacional.csv
```

---

## Paso 5.4 — Escribir las consultas Cypher

Creen cuatro variables de texto.

### `cypher_carga`

Debe usar:

```text
UNWIND $rows
MERGE (:Entidad ...)
MERGE (:Proceso ...)
MERGE (:Proveedor ...)
PUBLICA
ADJUDICADO_A
```

### `cypher_contexto`

Debe partir de una `Entidad` filtrada por `$nit_ancla` y recorrer:

```text
Entidad → Proceso → Proveedor
```

### `cypher_compartidos`

Debe encontrar `otra:Entidad` diferente del ancla que llegue al mismo proveedor.

### `cypher_ranking`

Debe utilizar `count(DISTINCT ...)` para ordenar proveedores por cantidad de entidades conectadas.

Guarden las cuatro consultas en:

```text
entrega_tc1/05_neo4j_consultas.cypher
```

---

## Paso 5.5 — Verificar el subgrafo en Python

Construyan un `nx.DiGraph()` para el ancla.

IDs:

```text
E:<nit_entidad>
P:<id_proceso>
V:<nit_proveedor>
```

Aristas:

```text
Entidad  --PUBLICA------> Proceso
Proceso  --ADJUDICADO_A-> Proveedor
```

Guarden:

```python
nodos_grafo = G.number_of_nodes()
aristas_grafo = G.number_of_edges()
```

El dibujo es opcional. Lo evaluado es la estructura.

---

# ETAPA 6 — Expliquen la solución

**5 puntos**

Creen `informe_tecnico` y guárdenlo como:

```text
entrega_tc1/06_informe_tecnico.md
```

Debe contener exactamente:

```markdown
## 1. Cómo construimos el histórico
## 2. Qué comprobamos en MongoDB Atlas
## 3. Cómo funciona la bandeja histórica
## 4. Por qué el modelo Cassandra responde la consulta
## 5. Qué relaciones aporta Neo4j y qué no podemos concluir
```

El informe debe insertar mediante variables, no números copiados:

- cantidad de archivos integrados;
- cantidad de documentos cargados en Atlas;
- resultado de la consulta A;
- tamaño de `bandeja_historica`;
- `nit_ancla`;
- máximo de `entidades_conectadas`.

Debe afirmar explícitamente que una regla de priorización y una conexión contractual **no demuestran por sí solas fraude, favorecimiento ni colusión**.

---

# Rúbrica

| Etapa | Evidencia | Puntos |
|---|---|---:|
| 1 | integración de 6 archivos, esquema, JSON y controles | 20 |
| 2 | conexión Atlas, carga real, count, find y aggregation | 30 |
| 3 | pipeline nuevo y bandeja histórica | 10 |
| 4 | modelo Cassandra y prueba del patrón | 15 |
| 5 | ancla nueva, métrica relacional, Cypher y subgrafo | 20 |
| 6 | informe y paquete final | 5 |
| **Total** |  | **100** |

---

# Qué NO se acepta

- unir los seis CSV manualmente;
- escribir los resultados esperados a mano;
- usar `mongomock` en lugar de Atlas para la etapa 2;
- dejar usuario o contraseña de Atlas dentro del notebook;
- entregar capturas como reemplazo del código;
- copiar la regla `1.000 → 163 → 77` de las clases;
- usar el NIT ancla de la sesión de Neo4j;
- copiar el modelo Cassandra de la sesión 5 sin adaptarlo a la nueva consulta;
- afirmar que una señal de priorización o una conexión contractual prueba fraude.

---

# Antes de entregar

Ejecuten el notebook de arriba abajo y comprueben que:

- los seis archivos se cargan;
- se genera el JSON histórico;
- Atlas responde `ping`;
- la colección tiene todos los documentos;
- las tres consultas se ejecutan;
- la bandeja sale de Atlas;
- Cassandra responde la consulta nueva;
- el ancla de Neo4j se calcula desde el histórico;
- el validador termina;
- descargaron `TC1_<pareja>.zip` y el `.ipynb` ejecutado.

**Git/GitHub sigue siendo opcional.**