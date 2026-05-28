# -*- coding: utf-8 -*-
"""
utils/patch_12_seccion14.py
===========================
Agrega la Seccion 14 al cuaderno 12_MongoDB_Atlas_NoSQL_Moderno.ipynb.

Seccion 14: Patrones de carga a escala
    - Patron 1: bulk_write con upsert (carga idempotente)
    - Patron 2: indice TEXT y busqueda con $text
    - Patron 3: carga de un DataFrame de pandas como documentos MongoDB

Uso:
    cd <repo_root>
    python utils/patch_12_seccion14.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from utils.make_notebook import md, code

NOTEBOOK_PATH = os.path.join(ROOT, "Cuadernos", "12_MongoDB_Atlas_NoSQL_Moderno.ipynb")


# =============================================================================
# Celda 1 — Encabezado de sección
# =============================================================================
c_header = md("""
---
# Sección 14 -- Patrones de carga a escala: bulk_write, indice TEXT y DataFrame a MongoDB
""")


# =============================================================================
# Celda 2 — Por qué estos tres patrones son necesarios
# =============================================================================
c_overview = md("""
## Por que estos tres patrones son necesarios

Las secciones anteriores ensenan el modelo operacional de MongoDB: CRUD, diseño documental,
aggregation pipeline e indices simples y compuestos. Eso es suficiente para consultar,
prototipar y construir aplicaciones pequenas que trabajan con documentos ya existentes.

Sin embargo, cargar decenas de miles de documentos desde una fuente externa — una API publica,
un archivo CSV o un DataFrame de pandas — exige tres herramientas adicionales que no aparecen
en el flujo CRUD basico:

| Patron | Para que sirve | Sin el |
|---|---|---|
| `bulk_write` con upsert | Cargar miles de documentos sin duplicados, de forma idempotente | `insert_one` en loop: lento (~minutos) y genera duplicados si el proceso se repite |
| Indice TEXT + `$text` | Busqueda por palabras clave en campos de texto libre | Solo se puede filtrar por igualdad exacta o regex; sin indice, MongoDB escanea toda la coleccion |
| Carga desde DataFrame | Transformar filas tabulares en documentos MongoDB con estructura anidada | Hay que construir cada dict manualmente, propenso a errores de tipo y de campos vacios |

Estos tres patrones son exactamente los que se necesitan en el **Taller Final (Sesion 13)** con datos SECOP II.
""")


# =============================================================================
# Celda 3 — Patrón 1: explicación bulk_write
# =============================================================================
c_bulk_explain = md("""
---
## Patron 1 — `bulk_write` con upsert: carga idempotente a escala

### El problema que resuelve

Supongamos que descargamos 50 000 contratos desde la API de SECOP II y los queremos guardar
en MongoDB. Hay dos enfoques ingenuos y uno correcto:

| Enfoque | Comando | Problema |
|---|---|---|
| Loop con `insert_one` | `for doc in docs: col.insert_one(doc)` | Un viaje de red por documento → muy lento. Si el proceso se interrumpe y se vuelve a correr, genera duplicados. |
| `insert_many` | `col.insert_many(docs)` | Un solo viaje de red → rapido. Pero si el proceso se corre dos veces, duplica todos los documentos. |
| **`bulk_write` con `upsert=True`** | ver codigo abajo | Rapido (pocos viajes de red) + **idempotente**. |

**Idempotente** significa que correr el mismo proceso dos veces produce el mismo estado que
correrlo una vez. Es la propiedad mas importante de cualquier pipeline de carga de datos en
produccion: garantiza que reintentar no rompe nada.

### Como funciona `UpdateOne` con upsert

`UpdateOne` es una **instruccion** que se construye en memoria y **no ejecuta nada** hasta que
se pasa a `bulk_write`:

```python
UpdateOne(
    filtro,           # Como identificar el documento si ya existe  (campo unico de negocio)
    {"$set": doc},    # Que campos escribir (actualizar si existe, crear si no)
    upsert=True       # Si el filtro no encuentra nada, crear el documento nuevo
)
```

MongoDB recibe una lista de estas instrucciones en el minimo numero de mensajes de red
(el driver las agrupa automaticamente) y las ejecuta en el servidor. Eso es `bulk_write`.

**Campo de filtro**: debe ser el identificador de negocio que no cambia entre ejecuciones.
No el `_id` generado por MongoDB, sino algo como `id_contrato`, `numero_proceso`, `referencia_contrato`.
Si el campo no es unico, upsert actualiza solo el primer documento que encuentre y deja el
resto intacto — un error silencioso muy dificil de detectar.

### Diferencia entre `$set` y reemplazo completo

```python
# Reemplazo completo (PELIGROSO en upsert): borra campos que no esten en doc
UpdateOne({"id": x}, doc, upsert=True)

# $set (CORRECTO): solo escribe los campos indicados, conserva el resto
UpdateOne({"id": x}, {"$set": doc}, upsert=True)
```

En pipelines de carga incremental, `$set` es casi siempre la opcion correcta.
""")


# =============================================================================
# Celda 4 — Patrón 1: código bulk_write
# =============================================================================
c_bulk_code = code('''
from pymongo import UpdateOne
from pprint import pprint

# Coleccion de prueba aislada para esta demostracion
col_bulk = client["bigdata_course"]["demo_bulk"]
col_bulk.delete_many({"_seed": "bulk_demo"})

# --- 1. Documentos de origen: simulan una descarga de la API ---
# En el taller real, este seria el DataFrame de pandas convertido a lista de dicts
contratos_api = [
    {"id_contrato": "CON-001", "entidad": "Min Educacion", "valor": 250_000_000, "estado": "vigente"},
    {"id_contrato": "CON-002", "entidad": "Min Salud",     "valor": 180_000_000, "estado": "vigente"},
    {"id_contrato": "CON-003", "entidad": "Min Educacion", "valor":  95_000_000, "estado": "liquidado"},
]

# --- 2. Construir lista de instrucciones UpdateOne ---
# Cada UpdateOne encapsula: filtro de identificacion, datos a escribir, modo upsert.
# La lista se construye en memoria; MongoDB no recibe nada todavia.
ops = [
    UpdateOne(
        {"id_contrato": doc["id_contrato"]},      # campo unico de negocio
        {"$set": {**doc, "_seed": "bulk_demo"}},  # $set escribe solo los campos indicados
        upsert=True                               # crear si no existe, actualizar si existe
    )
    for doc in contratos_api
]

# --- 3. Enviar todas las operaciones al servidor en un solo lote ---
# ordered=False: si un documento falla, el resto del lote continua sin detenerse
resultado = col_bulk.bulk_write(ops, ordered=False)

print("=== Primera carga ===")
print(f"  Insertados nuevos  (upserted_count): {resultado.upserted_count}")
print(f"  Encontrados        (matched_count):  {resultado.matched_count}")
print(f"  Con cambios reales (modified_count): {resultado.modified_count}")
# Esperado: upserted=3, matched=0, modified=0 (todos eran nuevos)

# --- 4. Demostrar idempotencia: segunda carga con un valor modificado ---
# CON-002 cambio de valor en la fuente; CON-001 y CON-003 siguen iguales
contratos_api[1]["valor"] = 195_000_000

ops2 = [
    UpdateOne(
        {"id_contrato": doc["id_contrato"]},
        {"$set": {**doc, "_seed": "bulk_demo"}},
        upsert=True,
    )
    for doc in contratos_api
]
resultado2 = col_bulk.bulk_write(ops2, ordered=False)

print()
print("=== Segunda carga (misma fuente, CON-002 cambio de valor) ===")
print(f"  Insertados nuevos  (upserted_count): {resultado2.upserted_count}")
print(f"  Encontrados        (matched_count):  {resultado2.matched_count}")
print(f"  Con cambios reales (modified_count): {resultado2.modified_count}")
# Esperado: upserted=0, matched=3, modified=1
# Solo CON-002 fue realmente modificado; los otros dos coincidieron pero no cambiaron

print()
total = col_bulk.count_documents({"_seed": "bulk_demo"})
print(f"Total documentos en coleccion: {total}")
# DEBE SER 3, no 6 — idempotencia garantiza que no hay duplicados

print()
print("Estado final de los documentos:")
for d in col_bulk.find({"_seed": "bulk_demo"}, {"_id": 0, "_seed": 0}):
    pprint(d)
''')


# =============================================================================
# Celda 5 — Patrón 1: mini ficha
# =============================================================================
c_bulk_ficha = md("""
### Mini ficha: `bulk_write(operaciones, ordered=False)`

| Elemento | Explicacion |
|---|---|
| **Funcion** | `bulk_write(ops)` — envia una lista de operaciones al servidor en el minimo numero de viajes de red. |
| **Parametros** | lista de objetos `UpdateOne`, `InsertOne`, `DeleteOne`, etc.; `ordered=False` para que una falla en un documento no detenga el lote entero. |
| **Retorna** | `BulkWriteResult` con contadores: `upserted_count`, `matched_count`, `modified_count`, `deleted_count`. |
| **Interpretar la salida** | `upserted_count` = documentos nuevos creados; `modified_count` = documentos existentes con cambios reales; `matched_count` >= `modified_count` porque un documento puede coincidir con el filtro pero no modificarse si el valor ya era el mismo. |

### Mini ficha: `UpdateOne(filtro, cambio, upsert=True)`

| Elemento | Explicacion |
|---|---|
| **Funcion** | construye una instruccion de actualizacion/insercion para usar dentro de `bulk_write`. |
| **Parametros** | filtro de identificacion unico del negocio; `{"$set": doc}` con los campos a escribir; `upsert=True` para crear el documento si el filtro no encuentra nada. |
| **Importante** | el campo en el filtro debe ser verdaderamente unico en el negocio; si no lo es, upsert actualiza solo el primer documento que encuentre. |
| **Por que `$set` y no reemplazo** | `$set` conserva campos existentes que no estan en `doc`; el reemplazo completo borra todo lo que no se envia en la actualizacion. |
""")


# =============================================================================
# Celda 6 — Patrón 2: explicación TEXT index
# =============================================================================
c_text_explain = md("""
---
## Patron 2 — Indice TEXT y busqueda con `$text`

### El problema que resuelve

Los filtros MQL buscan valores exactos o aplican expresiones regulares campo por campo.
Para buscar documentos donde cualquier campo de texto contenga una o varias palabras clave
— sin saber de antemano en que campo exacto aparecen — se necesita un **indice de texto**.

**Comparacion de tecnicas de busqueda textual:**

| Tecnica | Como funciona | Cuando usarla | Limitacion |
|---|---|---|---|
| `{"campo": {"$regex": "palabra"}}` | revisa cada valor con una expresion regular | busquedas simples en un campo conocido | sin indice: collection scan; lento con millones de docs |
| **Indice TEXT + `$text`** | indice invertido con tokenizacion y stopwords | busqueda por palabras clave en texto libre | un solo indice TEXT por coleccion |
| Atlas Search (`$search`) | motor de busqueda completo con relevancia y sinonimos | aplicaciones tipo buscador con UX avanzada | requiere configuracion adicional en Atlas |

### Como funciona internamente el indice TEXT

Al crear un indice TEXT sobre uno o mas campos, MongoDB ejecuta automaticamente tres pasos
por cada documento:

1. **Tokenizacion**: divide el valor del campo en palabras separadas por espacios y puntuacion.
2. **Filtrado de stopwords**: elimina palabras de alta frecuencia y baja informacion del idioma
   configurado ("de", "la", "en", "y" en espanol; "the", "a", "is" en ingles).
3. **Normalizacion**: convierte a minusculas y aplica stemming basico (variantes de raiz comun).

El resultado es un **indice invertido**: para cada token relevante, MongoDB guarda la lista de
documentos que lo contienen. La consulta `$text` consulta ese indice en tiempo casi constante,
sin escanear los textos completos.

### Parametro `default_language`

Si los textos estan en espanol, `default_language="spanish"` activa la lista de stopwords en
espanol. Sin este parametro MongoDB usa ingles por defecto, indexa palabras como "de" o "la"
innecesariamente y reduce la precision de la busqueda.

### Sintaxis de busqueda con `$text`

```python
# OR implicito: documentos que contengan "demoras" O "irregularidades"
{"$text": {"$search": "demoras irregularidades"}}

# AND forzado con +: documentos que contengan AMBAS palabras
{"$text": {"$search": "+demoras +ejecucion"}}

# Excluir: documentos con "contrato" pero SIN "transparente"
{"$text": {"$search": "contrato -transparente"}}

# Frase exacta entre comillas (escapadas en Python)
{"$text": {"$search": '\\"contrato terminado\\"'}}
```

### Restriccion importante

**Solo puede existir un indice TEXT por coleccion.** Si necesitas buscar en varios campos
de texto, agrupas todos en el mismo indice TEXT con multiples entradas. No se pueden
crear dos indices TEXT separados en la misma coleccion.
""")


# =============================================================================
# Celda 7 — Patrón 2: código TEXT index
# =============================================================================
c_text_code = code('''
from pymongo import TEXT

col_texto = client["bigdata_course"]["demo_texto"]
col_texto.delete_many({"_seed": "texto_demo"})

# --- 1. Documentos con campos de texto libre (simula contratos SECOP II) ---
# El campo "observaciones" es donde aparecen alertas narrativas sobre el contrato
contratos_texto = [
    {
        "_seed": "texto_demo",
        "id": "CON-101",
        "objeto_contrato": "Suministro de equipos de computo y accesorios para oficinas administrativas",
        "justificacion":   "Los equipos actuales tienen mas de cinco anos y presentan fallas frecuentes",
        "observaciones":   "Contrato con posibles irregularidades en el proceso de seleccion del proveedor",
    },
    {
        "_seed": "texto_demo",
        "id": "CON-102",
        "objeto_contrato": "Mantenimiento preventivo y correctivo de vehiculos oficiales",
        "justificacion":   "Garantizar la operacion continua de la flota vehicular de la entidad",
        "observaciones":   "Sin observaciones. Proceso transparente y bien documentado.",
    },
    {
        "_seed": "texto_demo",
        "id": "CON-103",
        "objeto_contrato": "Construccion de aula multiproposito en escuela rural",
        "justificacion":   "Ampliar la capacidad de atencion educativa en zona de alta vulnerabilidad",
        "observaciones":   "Demoras injustificadas en la ejecucion. Se requiere supervision adicional.",
    },
    {
        "_seed": "texto_demo",
        "id": "CON-104",
        "objeto_contrato": "Consultoria para diseno de sistema de informacion geografica",
        "justificacion":   "Modernizar la gestion territorial del municipio",
        "observaciones":   "Contrato terminado sin entregar los productos pactados al finalizar el plazo.",
    },
]

col_texto.insert_many(contratos_texto)
print(f"Documentos insertados: {col_texto.count_documents({'_seed': 'texto_demo'})}")

# --- 2. Crear indice TEXT sobre tres campos a la vez ---
# Un solo indice cubre objeto_contrato, justificacion y observaciones.
# default_language="spanish" activa stopwords en espanol para mayor precision.
# Si ya existe un indice TEXT en la coleccion hay que borrarlo primero con drop_index().
try:
    col_texto.drop_index("idx_texto_busqueda")
except Exception:
    pass  # No existe todavia, ignorar

idx_nombre = col_texto.create_index(
    [
        ("objeto_contrato", TEXT),
        ("justificacion",   TEXT),
        ("observaciones",   TEXT),
    ],
    default_language="spanish",
    name="idx_texto_busqueda",   # nombre explícito para poder referenciarlo después
)
print(f"Indice TEXT creado: {idx_nombre}")

# --- 3. Busqueda basica con $text ---
# $text busca en TODOS los campos del indice TEXT a la vez
print()
print("--- Busqueda: 'irregularidades' ---")
docs = list(col_texto.find(
    {"$text": {"$search": "irregularidades"}, "_seed": "texto_demo"},
    {"_id": 0, "_seed": 0}
))
for d in docs:
    print(f"  {d['id']} | {d['observaciones']}")

print()
print("--- Busqueda: 'demoras ejecucion' (OR: cualquiera de las dos palabras) ---")
docs2 = list(col_texto.find(
    {"$text": {"$search": "demoras ejecucion"}, "_seed": "texto_demo"},
    {"_id": 0, "id": 1, "objeto_contrato": 1}
))
for d in docs2:
    print(f"  {d['id']} | {d['objeto_contrato']}")

# --- 4. Score de relevancia mediante $meta: "textScore" ---
# textScore es mayor cuando el documento contiene mas terminos de la busqueda
# o cuando esos terminos son poco frecuentes en la coleccion (logica TF-IDF simplificada)
# Solo existe como campo virtual en la proyeccion; no se almacena en el documento
print()
print("--- Busqueda con score: 'irregularidades demoras supervision' ---")
pipeline_score = [
    {"$match": {
        "$text": {"$search": "irregularidades demoras supervision"},
        "_seed": "texto_demo",
    }},
    {"$project": {
        "_id": 0,
        "id": 1,
        "objeto_contrato": 1,
        "relevancia": {"$meta": "textScore"},   # campo virtual: mayor = mas relevante
    }},
    {"$sort": {"relevancia": -1}},   # mayor relevancia primero
]
from pprint import pprint
for d in col_texto.aggregate(pipeline_score):
    pprint(d)
''')


# =============================================================================
# Celda 8 — Patrón 2: mini ficha
# =============================================================================
c_text_ficha = md("""
### Mini ficha: indice TEXT + `$text`

| Elemento | Explicacion |
|---|---|
| **Crear el indice** | `col.create_index([(campo, TEXT), ...], default_language="spanish", name="idx_nombre")` |
| **Para que sirve** | busqueda eficiente por palabras clave sobre texto libre, con tokenizacion y eliminacion de stopwords. |
| **Parametros clave** | lista de campos con `TEXT`; `default_language` activa el idioma correcto; `name` para identificarlo y poder borrarlo si cambia la definicion. |
| **Ejecutar busqueda** | `{"$text": {"$search": "palabra1 palabra2"}}` — OR implicito; `+palabra` para AND; `-palabra` para excluir. |
| **Score de relevancia** | `{"$meta": "textScore"}` en la proyeccion; permite ordenar por relevancia con `{"$sort": {"campo_score": -1}}`. |
| **Restriccion** | una sola coleccion admite un unico indice TEXT — todos los campos de texto deben ir en el mismo indice. |
| **No sirve para** | busqueda de subcadenas dentro de palabras (eso requiere regex); frases exactas entre comillas si funcionan. |
""")


# =============================================================================
# Celda 9 — Patrón 3: explicación DataFrame → MongoDB
# =============================================================================
c_df_explain = md("""
---
## Patron 3 — Cargar un DataFrame de pandas como documentos MongoDB

### El problema que resuelve

Despues de descargar datos de una API REST o leer un CSV con pandas, el resultado es un
DataFrame: una estructura tabular con filas y columnas de tipo homogeneo. MongoDB no trabaja
con tablas planas; trabaja con documentos JSON/BSON que pueden tener campos anidados, arrays y
tipos especiales como `datetime`.

El puente entre DataFrame y MongoDB requiere resolver cuatro decisiones:

| Decision | Pregunta | Ejemplo |
|---|---|---|
| **Estructura** | Que columnas forman campos planos y cuales se agrupan como subdocumentos? | `entidad_nombre` + `entidad_nit` → subdocumento `entidad` |
| **Identificador** | Que campo actua como clave del upsert? | `id_contrato`, `numero_proceso` |
| **Tipos** | Como convertir tipos de pandas a tipos de MongoDB? | `Timestamp` → `datetime`; `NaN` → `None`; `float64` → `float` |
| **Tamano del lote** | Cuantos documentos se acumulan antes de enviar? | 500-1000 por lote |

### `iterrows()` vs `to_dict("records")`

| Metodo | Cuando usarlo | Velocidad |
|---|---|---|
| `df.to_dict("records")` | cuando la funcion de transformacion es simple (solo renombrar columnas) | rapido: crea toda la lista en memoria de una vez |
| `df.iterrows()` | cuando hay logica condicional por campo (verificar NaN, convertir tipos) | mas lento pero mas legible para transformaciones complejas |

### Por que cargar en lotes y no todo de una vez

Cargar en **lotes de 500-1000 documentos** en lugar de una lista enorme tiene dos ventajas:

1. **Control de memoria RAM**: en lugar de construir una lista de 50 000 `UpdateOne` en memoria
   (que puede ocupar cientos de MB), cada lote ocupa solo la fraccion correspondiente.
2. **Commit incremental**: si el proceso se interrumpe en el lote 40 de 100, los primeros
   39 lotes ya estan en MongoDB. Con upsert, reanudar el proceso desde el inicio es seguro:
   los lotes ya cargados se actualizaran sin duplicarse.

### Conversiones de tipo criticas

| Tipo pandas | Tipo MongoDB (BSON) | Conversion necesaria |
|---|---|---|
| `float64` con `NaN` | `None` | `float(x) if pd.notna(x) else None` |
| `Timestamp` | `datetime` (ISODate) | `ts.to_pydatetime()` |
| `object` (string con NaN) | `str` o `None` | `str(x) if pd.notna(x) else None` |
| `int64` | `int` | conversion automatica por PyMongo |
""")


# =============================================================================
# Celda 10 — Patrón 3: código DataFrame → MongoDB
# =============================================================================
c_df_code = code('''
import math
import pandas as pd
from pymongo import UpdateOne
from pprint import pprint

# --- 1. DataFrame de ejemplo: simula una descarga de la API de SECOP II ---
datos_api = {
    "id_proceso":      ["SEP-001", "SEP-002", "SEP-003", "SEP-004", "SEP-005"],
    "entidad_nombre":  ["Alcaldia de Bogota", "Min Hacienda", "SENA", "ICBF",
                        "Gobernacion de Cundinamarca"],
    "entidad_nit":     ["899999061", "899999086", "899999034", "899999034", "899999006"],
    "departamento":    ["Bogota D.C.", "Bogota D.C.", "Bogota D.C.", "Bogota D.C.", "Cundinamarca"],
    "valor_contrato":  [320_000_000.0, 85_000_000.0, 150_000_000.0, 210_000_000.0, 47_000_000.0],
    "objeto": [
        "Suministro de materiales educativos para colegios distritales",
        "Consultoria en gestion financiera publica",
        "Capacitacion en competencias digitales para jovenes",
        "Atencion psicosocial a familias en condicion de vulnerabilidad",
        "Mantenimiento de vias secundarias departamentales",
    ],
    "fecha_firma":     ["2024-03-01", "2024-05-15", "2024-07-20", "2024-02-10", "2024-09-01"],
    "estado_proceso":  ["Adjudicado", "Liquidado", "En Ejecucion", "En Ejecucion", "Adjudicado"],
}

df = pd.DataFrame(datos_api)
# pd.to_datetime convierte strings "YYYY-MM-DD" a Timestamp de pandas
# to_pydatetime() posterior los convertira a datetime de Python (compatible con BSON ISODate)
df["fecha_firma"] = pd.to_datetime(df["fecha_firma"])

print("DataFrame de origen:")
print(df.to_string(index=False))


# --- 2. Funcion de transformacion: fila -> documento MongoDB ---
# Agrupa columnas relacionadas en subdocumentos siguiendo el modelo documental.
# Convierte tipos de pandas a tipos nativos de Python para compatibilidad BSON.
def fila_a_documento(row: pd.Series) -> dict:
    # pd.notna verifica que el valor no sea NaN o NaT antes de asignarlo
    # to_pydatetime() convierte Timestamp pandas -> datetime Python -> BSON ISODate
    return {
        "id_proceso": row["id_proceso"],
        "entidad": {
            "nombre": row["entidad_nombre"],   # subdocumento: agrupa datos de la entidad
            "nit":    row["entidad_nit"],
        },
        "territorio": {
            "departamento": row["departamento"],
        },
        "valor_contrato": float(row["valor_contrato"]) if pd.notna(row["valor_contrato"]) else None,
        "objeto":         str(row["objeto"])           if pd.notna(row["objeto"])          else None,
        "fecha_firma":    row["fecha_firma"].to_pydatetime() if pd.notna(row["fecha_firma"]) else None,
        "estado_proceso": row["estado_proceso"],
    }

# Verificar la conversion de una fila antes de cargar el DataFrame completo
print()
print("Ejemplo de documento convertido (primera fila):")
pprint(fila_a_documento(df.iloc[0]))


# --- 3. Carga en lotes con bulk_write + upsert ---
col_df = client["bigdata_course"]["demo_df_carga"]
col_df.delete_many({"id_proceso": {"$exists": True}})

TAMANO_LOTE = 3   # En produccion usar 500-1000; aqui pequeno para mostrar el flujo de lotes
lotes_total  = math.ceil(len(df) / TAMANO_LOTE)
total_ins    = 0
total_mod    = 0

for n_lote in range(lotes_total):
    # Seleccionar el rango de filas del lote actual
    inicio = n_lote * TAMANO_LOTE
    fin    = min(inicio + TAMANO_LOTE, len(df))
    lote   = df.iloc[inicio:fin]

    # Construir las instrucciones UpdateOne para las filas de este lote
    ops = [
        UpdateOne(
            {"id_proceso": row["id_proceso"]},   # campo unico de negocio: clave del upsert
            {"$set": fila_a_documento(row)},
            upsert=True,
        )
        for _, row in lote.iterrows()
    ]

    # Enviar el lote a MongoDB
    res = col_df.bulk_write(ops, ordered=False)
    total_ins += res.upserted_count
    total_mod += res.modified_count

    print(f"  Lote {n_lote + 1}/{lotes_total} "
          f"| filas {inicio}-{fin - 1} "
          f"| nuevos: {res.upserted_count} "
          f"| actualizados: {res.modified_count}")

print()
print(f"Resumen: {total_ins} insertados, {total_mod} actualizados")
print(f"Documentos en coleccion: {col_df.count_documents({})}")
print()
print("Documentos almacenados (estructura anidada):")
for d in col_df.find({}, {"_id": 0}):
    pprint(d)
''')


# =============================================================================
# Celda 11 — Patrón 3: mini ficha
# =============================================================================
c_df_ficha = md("""
### Mini ficha: carga de DataFrame a MongoDB

| Elemento | Explicacion |
|---|---|
| `df.to_dict("records")` | convierte el DataFrame completo en `[{col: val, ...}, ...]` — mas rapido que `iterrows()` para DataFrames sin logica de transformacion. |
| `df.iterrows()` | devuelve `(indice, Series)` fila a fila — util cuando `fila_a_documento()` tiene condiciones por campo (verificar NaN, convertir tipos). |
| `pd.notna(valor)` | verifica que el valor no sea `NaN` o `NaT` antes de asignarlo al documento — evita guardar `float('nan')` en MongoDB. |
| `timestamp.to_pydatetime()` | convierte un `Timestamp` de pandas a `datetime` de Python, compatible con BSON `ISODate`. |
| `TAMANO_LOTE` | controla cuantos `UpdateOne` se acumulan en memoria antes de enviar; valores tipicos: 500-1000 por lote segun RAM disponible. |
| `df.iloc[inicio:fin]` | selecciona un rango de filas por posicion para procesar el DataFrame en bloques. |
| Verificar antes de cargar | llama `fila_a_documento(df.iloc[0])` y revisa el resultado antes de cargar las 50 000 filas — detecta errores de tipo a tiempo. |
""")


# =============================================================================
# Celda 12 — Cierre: conexión con el Taller Final
# =============================================================================
c_cierre = md("""
---
## Conexion con el Taller Final (Sesion 13)

El Taller Final con datos SECOP II combina los tres patrones de esta seccion con todo lo
aprendido en las secciones anteriores de este cuaderno:

| Paso del taller | Patron usado | Seccion de referencia |
|---|---|---|
| Descarga paginada de la API Socrata y construccion del DataFrame | `requests` + pandas | — |
| `fila_a_documento(row)` con campos anidados: `entidad`, `proveedor`, `territorio`, `adiciones`, `ejecucion` | Patron 3 — carga desde DataFrame | Esta seccion |
| Carga de 50K+ documentos sin duplicados con `id_contrato` como clave | Patron 1 — `bulk_write` con upsert | Esta seccion |
| Indice TEXT sobre `texto_no_estructurado.texto_busqueda` para busqueda por alertas | Patron 2 — TEXT + `$text` | Esta seccion |
| Indices compuestos sobre `territorio.departamento + valor_contrato` | `create_index` | Seccion 8 |
| Ranking de alertas, analisis por departamento, top proveedores | `aggregate` pipeline | Seccion 7 |
| Evaluar si los indices se usan en las consultas | `explain()` con `IXSCAN` vs `COLLSCAN` | Seccion 8 |

**Resumen de habilidades necesarias para la Parte 4 del taller (MongoDB Atlas):**

- Conectar a Atlas y seleccionar base de datos y coleccion. ✓ Seccion 3
- Disenar el documento con campos anidados a partir de columnas del DataFrame. ✓ Seccion 6
- Crear `fila_a_documento()` con conversion correcta de tipos. ✓ Patron 3 (esta seccion)
- Cargar en lotes con `bulk_write` + upsert idempotente. ✓ Patron 1 (esta seccion)
- Crear 4-6 indices: compuestos, TEXT, simples. ✓ Seccion 8 + Patron 2 (esta seccion)
- Ejecutar aggregation pipelines para responder preguntas analiticas. ✓ Seccion 7
""")


# =============================================================================
# Ensamblar y guardar
# =============================================================================
nuevas_celdas = [
    c_header,
    c_overview,
    c_bulk_explain,
    c_bulk_code,
    c_bulk_ficha,
    c_text_explain,
    c_text_code,
    c_text_ficha,
    c_df_explain,
    c_df_code,
    c_df_ficha,
    c_cierre,
]

with open(NOTEBOOK_PATH, encoding="utf-8") as f:
    nb = json.load(f)

# Agregar las celdas nuevas al final del notebook
for celda in nuevas_celdas:
    nb["cells"].append(celda)

with open(NOTEBOOK_PATH, "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

size_kb = os.path.getsize(NOTEBOOK_PATH) / 1024
print(f"[OK] {len(nuevas_celdas)} celdas agregadas a {NOTEBOOK_PATH}")
print(f"     Total celdas en notebook: {len(nb['cells'])}  |  {size_kb:.1f} KB")
