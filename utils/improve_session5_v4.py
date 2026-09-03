#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuerza S5 con microejemplos antes de cada concepto nuevo.

Se ejecuta después de improve_session5_v3.py. No cambia los baselines del caso
(142, 111/25/6, 1.000→163→77, 0/77) ni la PRIMARY KEY validada. Agrega los
puentes cognitivos que necesita el grupo: ejemplo manual → intuición → sintaxis
→ caso real → interpretación/límite.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in src(cell):
            return i
    raise RuntimeError(f"No se encontró el marcador {needle!r}")


def insert_once(cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool = False) -> None:
    if any(marker in src(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb["cells"]

    # 1) $switch: primero una regla de tres filas y su equivalente Python.
    insert_once(cells, "La historia necesita una transformación", "MICROEJEMPLO SWITCH S05", [md('''
### MICROEJEMPLO SWITCH S05 — primero decide, después traduce a MongoDB

Antes de mirar `$switch`, resuelve tres casos sin sintaxis nueva:

| entidad | noticias | nivel |
|---|---:|---|
| Entidad A | 3 | baja |
| Entidad B | 8 | media |
| Entidad C | 24 | alta |

En Python, la misma regla se leería así:

```python
if noticias >= 20:
    nivel = "alta"
elif noticias >= 5:
    nivel = "media"
else:
    nivel = "baja"
```

MongoDB no introduce una lógica diferente: `$switch` expresa esa misma decisión dentro del pipeline. Evalúa las ramas **en orden** y usa la primera condición verdadera.

```text
noticias = 25 → ¿>=20? sí → alta → deja de probar
noticias =  8 → ¿>=20? no → ¿>=5? sí → media
```

**OJO.** Los cortes `5` y `20` son una **regla pedagógica versionada** para resumir intensidad de menciones. No son umbrales oficiales de riesgo ni fueron estimados con un modelo estadístico.

**PARA LLEVAR.** La decisión existe antes que el operador. `$switch` solo la materializa.
''')], after=True)

    # 2) Vista: definición consultable, no copia física de los 142 documentos.
    insert_once(cells, "## 3. Tutorial visual 1", "MODELO MENTAL VISTA S05", [md('''
### MODELO MENTAL VISTA S05 — publicar una transformación sin copiar los datos

```text
entidades_noticias
      │
      │ pipeline
      ▼
menciones_clasificadas
      (VIEW)
```

Piensa en una vista como una **pregunta guardada y consultable**, parecida mentalmente a una `VIEW` de SQL:

| La vista... | ¿Sí o no? |
|---|---|
| crea otros 142 documentos independientes | **No** |
| guarda la definición del pipeline | **Sí** |
| calcula su resultado cuando la consultas | **Sí** |
| se consulta como un objeto propio | **Sí** |
| se edita como una colección normal | **No: es de solo lectura** |

**Ejemplo pequeño.** Si `entidades_noticias` cambia y una entidad pasa de 4 a 5 noticias, la lógica de la vista vuelve a evaluar el pipeline cuando se consulta; no tenemos que mantener manualmente una segunda copia.

**Error frecuente.** Confundir **guardar el pipeline** con **crear la vista**. El primero conserva la receta en el editor; el segundo publica esa receta como objeto consultable.
''')])

    # 3) merge many-to-one: mostrar qué cruza realmente el notebook.
    insert_once(cells, ".merge(contexto_menciones, on=\"entidad\", how=\"left\", validate=\"many_to_one\")", "MICROEJEMPLO MERGE S05", [md('''
### MICROEJEMPLO MERGE S05 — muchos procesos pueden heredar el contexto de una entidad

Antes del cruce real, mira este caso diminuto.

**Contexto de prensa**

| entidad | noticias | nivel |
|---|---:|---|
| A | 24 | alta |
| B | 6 | media |

**Procesos SECOP**

| proceso | entidad | valor |
|---|---|---:|
| P1 | A | 100 |
| P2 | A | 50 |
| P3 | C | 80 |

Al unir por `entidad`, P1 y P2 reciben el mismo contexto de A. Eso es un patrón **many-to-one**: muchos procesos pueden apuntar a una sola fila de contexto por entidad.

```text
P1 ─┐
    ├─ Entidad A → 24 noticias → alta
P2 ─┘
```

Por eso usamos `validate="many_to_one"`: pandas comprueba que la tabla de contexto no tenga dos filas distintas para la misma entidad. Si esa suposición se rompe, preferimos un error explícito a duplicar procesos silenciosamente.

**PARA LLEVAR.** `noticias_entidad` y `nivel_menciones` **viajan como contexto**. No deciden por sí solos quién entra a la bandeja.
''')])

    # 4) Regla de negocio: dejar claro que es heurística de trabajo, no score de irregularidad.
    insert_once(cells, "respuestas = pd.to_numeric(paso2[\"respuestas_al_procedimiento\"]", "FUNDAMENTO REGLA S05", [md('''
### FUNDAMENTO REGLA S05 — una heurística de trabajo, no un detector de fraude

La bandeja usa una regla explícita porque Laura necesita una cola de revisión defendible. Cada condición cumple un papel **operacional**:

| Condición | Para qué la usamos aquí | Lo que **NO** significa |
|---|---|---|
| entidad aparece en prensa | agrega contexto externo para decidir dónde mirar | que la entidad cometió una irregularidad |
| modalidad contiene `directa` | acota el ejercicio a una modalidad concreta | que contratación directa = corrupción |
| respuestas = `0` | describe una característica observada del proceso | que cero respuestas = anomalía |
| `precio_base DESC` | ordena por exposición económica potencial | que mayor valor = mayor probabilidad de irregularidad |

**Ejemplo.** Si dos procesos cumplen la misma regla y uno vale $1.000 millones y otro $20 millones, ordenar el primero antes solo expresa una decisión de **impacto potencial**. No hemos estimado la probabilidad de que exista un problema.

```text
probabilidad de irregularidad  ≠  impacto económico potencial
```

**OJO.** En contratación directa puede existir un proceso sin competencia de múltiples ofertas. Por eso `directa + 0 respuestas` se trata aquí como una **heurística pedagógica versionada**, no como dos “señales de corrupción”.

**PARA LLEVAR.** La regla organiza revisión humana. No produce un veredicto.
''')])

    # 5) Faltante vs cero: tabla mínima para que la conversión sea visible.
    insert_once(cells, "pd.to_numeric(paso2[\"respuestas_al_procedimiento\"], errors=\"coerce\")", "MICROEJEMPLO NAN S05", [md('''
### MICROEJEMPLO NAN S05 — desconocido no es lo mismo que cero

| valor original | `pd.to_numeric(..., errors="coerce")` | `.eq(0)` |
|---|---:|---|
| `"0"` | `0` | `True` |
| `"2"` | `2` | `False` |
| vacío | `NaN` | `False` |
| `"No definido"` | `NaN` | `False` |

Si hiciéramos `fillna(0)`, transformaríamos **“no conozco el dato”** en **“observé exactamente cero”**. Eso cambiaría la evidencia y podría meter filas a la bandeja por una imputación que nunca justificamos.
''')])

    # 6) Precisión metodológica del control 0/77.
    insert_once(cells, "Referencias de proceso citadas literalmente", "PRECISIÓN 0/77 S05", [md('''
### PRECISIÓN 0/77 S05 — qué examinó exactamente este control

El resultado `0/77` debe leerse con precisión:

> **No encontramos ninguna referencia exacta de esos 77 procesos dentro de los títulos o subtítulos examinados.**

Este control **no** buscó el cuerpo completo de todos los artículos, nombres alternativos del proceso, referencias indirectas ni similitud semántica. Por tanto, `0/77` **no significa** “ninguna noticia habla de esos contratos”.

**Cómo se lee.** Cero referencias exactas encontradas en el campo textual que sí examinamos.  
**Qué nos dice.** La evidencia usada para construir la bandeja sigue siendo, bajo esta prueba, contextual a nivel de entidad.  
**Qué NO permite concluir todavía.** No sabemos si el cuerpo completo de una noticia menciona indirectamente un proceso ni si existe otra evidencia externa específica.  
**Error frecuente.** Convertir “no encontré una referencia exacta aquí” en “demostré que no existe ninguna mención”.
''')], after=True)

    # 7) Cassandra nace de una escena operacional, no de las 77 filas actuales.
    insert_once(cells, "### EJERCICIO S05-PK", "ESCENA OPERACIONAL CASSANDRA S05", [md('''
### ESCENA OPERACIONAL CASSANDRA S05 — primero la consulta de negocio

Con **77 filas**, pandas ya responde. Cassandra aparece para practicar el diseño de un servicio cuando esta lectura se vuelve estable y repetitiva.

Imagina que Compras Claras ya tiene una interfaz para varios revisores:

```text
GET /prioridades?corte=2026-09-03&departamento=Bogota&limit=5
```

La pregunta detrás de esa llamada es:

> **Para este corte y este departamento, dame primero los procesos de mayor valor.**

Ahora cada término tiene sentido de negocio:

| Dato | Qué representa |
|---|---|
| `corte` | la versión/fecha de la bandeja |
| `departamento` | la cola territorial que atiende un revisor |
| `valor_base DESC` | el orden de exposición económica dentro de esa cola |
| `LIMIT 5` | qué abre primero el revisor |

**PARA LLEVAR.** No usamos Cassandra porque 77 filas “sean Big Data”. La usamos para aprender **query-first design**: una tabla nace de una consulta que sabemos que el servicio debe atender repetidamente.
'''), md('''
### MICROEJEMPLO PARTICIONES S05 — piensa en cajones antes de mirar la `PRIMARY KEY`

```text
ARCHIVADOR DE PRIORIDADES

Cajón: 2026-09-03 + Bogotá
├── $180 M → P8
├── $120 M → P3
└──  $40 M → P5

Cajón: 2026-09-03 + Antioquia
├── $250 M → P9
└──  $70 M → P2
```

- **Partition key `(corte, departamento)`** = la etiqueta del cajón que permite localizar el grupo.
- **Clustering `valor_base DESC, id_proceso ASC`** = cómo quedan ordenadas las filas **dentro** del cajón.

Por eso, en esta sesión `PRIMARY KEY` significa más que “un identificador único”:

```text
PRIMARY KEY
├── partition key      → dónde viven los datos
└── clustering columns → cómo se organizan dentro de la partición
```

**Error frecuente.** Diseñar la clave mirando qué columnas parecen importantes. En Cassandra la pregunta profesional va primero.
''')])

    # 8) Astra: vocabulario mínimo antes del tutorial de interfaz.
    insert_once(cells, "## 8. Tutorial visual 2", "MODELO MENTAL ASTRA S05", [md('''
### MODELO MENTAL ASTRA S05 — cuatro nombres antes de hacer clic

| Nombre | Qué significa hoy |
|---|---|
| **Astra DB** | servicio administrado donde usaremos Cassandra sin instalar un servidor en Windows |
| **Cassandra** | motor/modelo wide-column que estamos estudiando |
| **CQL** | lenguaje para definir y consultar tablas Cassandra |
| **keyspace** | contenedor lógico donde agrupamos las tablas de `compras_claras` |

```text
Astra database
└── keyspace compras_claras
    └── prioridades_por_corte_departamento
```

Elegimos **Serverless (non-vector)** porque hoy trabajamos una tabla Cassandra/CQL por claves. No estamos haciendo embeddings ni búsqueda vectorial.

**PARA LLEVAR.** No necesitas instalar Cassandra localmente ni entender estrategias de replicación para completar esta práctica; Astra administra esa infraestructura.
''')])

    # 9) Driver, SCB, token y prepared statements: reducir la fricción de nube.
    insert_once(cells, "### MINI FICHA DRIVER S05", "MODELO CONEXIÓN PYTHON S05", [md('''
### MODELO CONEXIÓN PYTHON S05 — no memorices objetos: asigna una función a cada uno

```text
SCB      → ¿cómo llega el driver de forma segura a ESTA base?
TOKEN    → ¿con qué credencial me autentico?
Cluster  → cliente Python configurado
Session  → canal con el que ejecuto CQL
prepare  → plantilla CQL con espacios `?` para valores
execute  → envía la plantilla + los valores reales
```

**Ejemplo de `prepare()`:**

```python
consulta = session.prepare("""
SELECT * FROM prioridades_por_corte_departamento
WHERE corte = ? AND departamento = ?
LIMIT 5
""")

session.execute(consulta, (CORTE_CLASE, departamento_elegido))
```

Se lee así:

```text
corte = ?         ← 2026-09-03
departamento = ?  ← Bogotá
```

Los `?` no son valores desconocidos del dataset: son **lugares reservados** que se completan al ejecutar.

**Error frecuente.** Pensar que `Cluster(...)` crea otro clúster en la nube. Aquí solo crea el objeto cliente del driver Python.
''')])

    # 10) INSERT en Cassandra: explicar upsert e idempotencia del laboratorio.
    insert_once(cells, "insertar = session.prepare", "UPSERT S05", [md('''
### UPSERT S05 — por qué repetir la carga no crea una segunda fila con la misma clave

En Cassandra, un `INSERT` con la misma `PRIMARY KEY` tiene comportamiento de **upsert**: si la fila no existe, la crea; si ya existe, escribe/actualiza los valores de esa misma fila.

```text
1.ª ejecución: P1 no existe  → crea P1
2.ª ejecución: misma PK P1   → actualiza P1, no crea un duplicado P1
```

Esto ayuda a que la carga del laboratorio sea repetible. **No significa** que 77 escrituras síncronas sean la estrategia recomendada para cargas masivas; aquí priorizamos claridad y trazabilidad.
''')])

    # 11) Fortalecer la interpretación final de pandas ↔ CQL.
    i = find(cells, "### INTERPRETACIÓN CQL S05")
    text = src(cells[i])
    if "Cambiar de motor no debería cambiar" not in text:
        text += "\n\n**PARA LLEVAR.** Cambiar de motor no debería cambiar la decisión de negocio. pandas fija el contrato; Cassandra debe servir la misma respuesta para esta consulta."
        cells[i]["source"] = text

    # 12) Los tutoriales mejorados viven en v3; mantener v2 como historial estable.
    for cell in cells:
        text = src(cell)
        text = text.replace("atlas-s05-pipelines-vistas-v2.html", "atlas-s05-pipelines-vistas-v3.html")
        text = text.replace("astra-cassandra-paso-a-paso-v2.html", "astra-cassandra-paso-a-paso-v3.html")
        cell["source"] = text

    nb["cells"] = cells
    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] S5 v4: {len(cells)} celdas; conceptos nuevos precedidos por microejemplos y fundamento de negocio.")


if __name__ == "__main__":
    main()
