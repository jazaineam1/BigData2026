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
    insert_once(cells, "La historia necesita una transformación", "Microejemplo", [md('''
### Microejemplo — primero decide, después traduce a MongoDB

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

<div align="center">
<svg style="max-width:500px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 500 158" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de flujo"><defs><marker id="s5switch-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5switch-b{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5switch-t{font:700 14px system-ui,sans-serif;fill:#123f2b;}.s5switch-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="20" y="14" width="460" height="50" rx="10" class="s5switch-b"/><text x="250.0" y="36" text-anchor="middle" class="s5switch-t">noticias = 25</text><text x="250.0" y="54" text-anchor="middle" class="s5switch-s">¿≥20? sí → alta (deja de evaluar)</text><line x1="250.0" y1="64" x2="250.0" y2="94" stroke="#175c3c" stroke-width="2" marker-end="url(#s5switch-a)"/><rect x="20" y="94" width="460" height="50" rx="10" class="s5switch-b"/><text x="250.0" y="116" text-anchor="middle" class="s5switch-t">noticias = 8</text><text x="250.0" y="134" text-anchor="middle" class="s5switch-s">¿≥20? no → ¿≥5? sí → media</text></svg>
</div>

**OJO.** Los cortes `5` y `20` son una **regla pedagógica versionada** para resumir intensidad de menciones. No son umbrales oficiales de riesgo ni fueron estimados con un modelo estadístico.

**PARA LLEVAR.** La decisión existe antes que el operador. `$switch` solo la materializa.
''')], after=True)

    # 2) Vista: definición consultable, no copia física de los 142 documentos.
    insert_once(cells, "## 3. Tutorial visual 1", "Modelo mental", [md('''
### Modelo mental — publicar una transformación sin copiar los datos

<div align="center">
<svg style="max-width:460px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 460 260" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama: entidades_noticias pasa por un pipeline y se publica como la vista menciones_clasificadas">
  <defs>
    <marker id="s5v1-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/>
    </marker>
  </defs>
  <style>
    .s5v1-box-fill{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}
    .s5v1-view-fill{fill:#eef6f1;stroke:#175c3c;stroke-width:2;stroke-dasharray:6 4;}
    .s5v1-title{font:700 15px system-ui,sans-serif;fill:#123f2b;}
    .s5v1-sub{font:12px system-ui,sans-serif;fill:#3a4a41;}
    .s5v1-label{font:600 12px system-ui,sans-serif;fill:#175c3c;}
    .s5v1-tag{font:700 10px system-ui,sans-serif;fill:#ffffff;}
  </style>
  <rect x="60" y="18" width="340" height="64" rx="10" class="s5v1-box-fill"/>
  <text x="230" y="44" text-anchor="middle" class="s5v1-title">entidades_noticias</text>
  <text x="230" y="66" text-anchor="middle" class="s5v1-sub">colección real · 142 documentos</text>

  <line x1="230" y1="82" x2="230" y2="150" stroke="#175c3c" stroke-width="2" marker-end="url(#s5v1-arrow)"/>
  <rect x="170" y="98" width="120" height="24" rx="5" fill="#175c3c"/>
  <text x="230" y="114" text-anchor="middle" class="s5v1-tag">PIPELINE (agregación)</text>

  <rect x="60" y="164" width="340" height="78" rx="10" class="s5v1-view-fill"/>
  <text x="230" y="192" text-anchor="middle" class="s5v1-title">menciones_clasificadas</text>
  <text x="230" y="212" text-anchor="middle" class="s5v1-sub">VIEW · definición guardada, solo lectura</text>
  <text x="230" y="230" text-anchor="middle" class="s5v1-sub">se recalcula sobre entidades_noticias en cada consulta</text>
</svg>
</div>

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
    insert_once(cells, ".merge(contexto_menciones, on=\"entidad\", how=\"left\", validate=\"many_to_one\")", "Microejemplo", [md('''
### Microejemplo — muchos procesos pueden heredar el contexto de una entidad

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

<div align="center">
<svg style="max-width:460px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 460 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama: los procesos P1 y P2 se cruzan con la entidad A y heredan su contexto de 24 noticias, nivel alta">
  <defs>
    <marker id="s5v2-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/>
    </marker>
  </defs>
  <style>
    .s5v2-box{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}
    .s5v2-out{fill:#eef6f1;stroke:#175c3c;stroke-width:2;stroke-dasharray:6 4;}
    .s5v2-title{font:700 14px system-ui,sans-serif;fill:#123f2b;}
    .s5v2-sub{font:11px system-ui,sans-serif;fill:#3a4a41;}
    .s5v2-line{stroke:#175c3c;stroke-width:2;fill:none;}
  </style>
  <rect x="20" y="20" width="90" height="40" rx="8" class="s5v2-box"/>
  <text x="65" y="45" text-anchor="middle" class="s5v2-title">P1</text>

  <rect x="20" y="140" width="90" height="40" rx="8" class="s5v2-box"/>
  <text x="65" y="165" text-anchor="middle" class="s5v2-title">P2</text>

  <path d="M110,40 C150,40 150,98 168,99" class="s5v2-line"/>
  <path d="M110,160 C150,160 150,102 168,101" class="s5v2-line"/>

  <rect x="170" y="80" width="120" height="40" rx="8" class="s5v2-box"/>
  <text x="230" y="105" text-anchor="middle" class="s5v2-title">Entidad A</text>

  <line x1="290" y1="100" x2="348" y2="100" class="s5v2-line" marker-end="url(#s5v2-arrow)"/>

  <rect x="350" y="70" width="90" height="60" rx="8" class="s5v2-out"/>
  <text x="395" y="94" text-anchor="middle" class="s5v2-title">24 noticias</text>
  <text x="395" y="114" text-anchor="middle" class="s5v2-sub">nivel: alta</text>

  <text x="65" y="200" text-anchor="middle" class="s5v2-sub">P1 y P2 heredan</text>
  <text x="65" y="212" text-anchor="middle" class="s5v2-sub">el mismo contexto</text>
</svg>
</div>

Por eso usamos `validate="many_to_one"`: pandas comprueba que la tabla de contexto no tenga dos filas distintas para la misma entidad. Si esa suposición se rompe, preferimos un error explícito a duplicar procesos silenciosamente.

**PARA LLEVAR.** `noticias_entidad` y `nivel_menciones` **viajan como contexto**. No deciden por sí solos quién entra a la bandeja.
''')])

    # 4) Regla de negocio: dejar claro que es heurística de trabajo, no score de irregularidad.
    insert_once(cells, "respuestas = pd.to_numeric(paso2[\"respuestas_al_procedimiento\"]", "Fundamento de la regla", [md('''
### Fundamento de la regla — una heurística de trabajo, no un detector de fraude

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
    insert_once(cells, "pd.to_numeric(paso2[\"respuestas_al_procedimiento\"], errors=\"coerce\")", "Microejemplo", [md('''
### Microejemplo — desconocido no es lo mismo que cero

| valor original | `pd.to_numeric(..., errors="coerce")` | `.eq(0)` |
|---|---:|---|
| `"0"` | `0` | `True` |
| `"2"` | `2` | `False` |
| vacío | `NaN` | `False` |
| `"No definido"` | `NaN` | `False` |

Si hiciéramos `fillna(0)`, transformaríamos **“no conozco el dato”** en **“observé exactamente cero”**. Eso cambiaría la evidencia y podría meter filas a la bandeja por una imputación que nunca justificamos.
''')])

    # 6) Precisión metodológica del control 0/77.
    # improve_session5_v5.py reemplaza esta celda por "Contraste de hipótesis";
    # si ya existe en cualquiera de las dos formas, no la insertes de nuevo
    # (si no, cada corrida completa del pipeline añade una copia adicional).
    if not any(
        "PRECISIÓN 0/77 S05" in src(c) or "Contraste de hipótesis" in src(c)
        for c in cells
    ):
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
    insert_once(cells, "### Ejercicio", "Escena operacional", [md('''
### Escena operacional — primero la consulta de negocio

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
### Microejemplo — piensa en cajones antes de mirar la `PRIMARY KEY`

<div align="center">
<svg style="max-width:560px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 560 220" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Archivador de prioridades por cajón"><style>.s5caj-h{fill:#eef6f1;stroke:#175c3c;stroke-width:2;}.s5caj-r{fill:#fff;stroke:#175c3c;stroke-width:1;}.s5caj-t{font:700 13px system-ui,sans-serif;fill:#123f2b;}.s5caj-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="15" y="14" width="250" height="24" rx="6" class="s5caj-h"/><text x="25" y="31" class="s5caj-t">Cajón: 2026-09-03 + Bogotá</text><rect x="15" y="44" width="250" height="26" class="s5caj-r"/><text x="25" y="62" class="s5caj-s">$180 M</text><text x="255" y="62" text-anchor="end" class="s5caj-t">P8</text><rect x="15" y="70" width="250" height="26" class="s5caj-r"/><text x="25" y="88" class="s5caj-s">$120 M</text><text x="255" y="88" text-anchor="end" class="s5caj-t">P3</text><rect x="15" y="96" width="250" height="26" class="s5caj-r"/><text x="25" y="114" class="s5caj-s">$40 M</text><text x="255" y="114" text-anchor="end" class="s5caj-t">P5</text><rect x="295" y="14" width="250" height="24" rx="6" class="s5caj-h"/><text x="305" y="31" class="s5caj-t">Cajón: 2026-09-03 + Antioquia</text><rect x="295" y="44" width="250" height="26" class="s5caj-r"/><text x="305" y="62" class="s5caj-s">$250 M</text><text x="535" y="62" text-anchor="end" class="s5caj-t">P9</text><rect x="295" y="70" width="250" height="26" class="s5caj-r"/><text x="305" y="88" class="s5caj-s">$70 M</text><text x="535" y="88" text-anchor="end" class="s5caj-t">P2</text></svg>
</div>

- **Partition key `(corte, departamento)`** = la etiqueta del cajón que permite localizar el grupo.
- **Clustering `valor_base DESC, id_proceso ASC`** = cómo quedan ordenadas las filas **dentro** del cajón.

Por eso, en esta sesión `PRIMARY KEY` significa más que “un identificador único”:

<div align="center">
<svg style="max-width:420px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 460 144" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama jerárquico"><style>.s5pktree-r{fill:#eef6f1;stroke:#175c3c;stroke-width:2;}.s5pktree-c{fill:#f4faf6;stroke:#175c3c;stroke-width:1.5;}.s5pktree-t{font:700 13px system-ui,sans-serif;fill:#123f2b;}.s5pktree-s{font:11px system-ui,sans-serif;fill:#3a4a41;}.s5pktree-l{stroke:#175c3c;stroke-width:1.5;}</style><rect x="20" y="14" width="220" height="34" rx="8" class="s5pktree-r"/><text x="30" y="36" class="s5pktree-t">PRIMARY KEY</text><line x1="40" y1="48" x2="40" y2="68.0" class="s5pktree-l"/><line x1="40" y1="68.0" x2="70" y2="68.0" class="s5pktree-l"/><rect x="74" y="52.0" width="366" height="32" rx="7" class="s5pktree-c"/><text x="84" y="73.0" class="s5pktree-t">partition key</text><text x="430" y="73.0" text-anchor="end" class="s5pktree-s">dónde viven los datos</text><line x1="40" y1="48" x2="40" y2="108.0" class="s5pktree-l"/><line x1="40" y1="108.0" x2="70" y2="108.0" class="s5pktree-l"/><rect x="74" y="92.0" width="366" height="32" rx="7" class="s5pktree-c"/><text x="84" y="113.0" class="s5pktree-t">clustering columns</text><text x="430" y="113.0" text-anchor="end" class="s5pktree-s">cómo se organizan dentro de la partición</text></svg>
</div>

**Error frecuente.** Diseñar la clave mirando qué columnas parecen importantes. En Cassandra la pregunta profesional va primero.
''')])

    # 8) Astra: vocabulario mínimo antes del tutorial de interfaz.
    insert_once(cells, "## 8. Tutorial visual 2", "Modelo mental", [md('''
### Modelo mental — cuatro nombres antes de hacer clic

| Nombre | Qué significa hoy |
|---|---|
| **Astra DB** | servicio administrado donde usaremos Cassandra sin instalar un servidor en Windows |
| **Cassandra** | motor/modelo wide-column que estamos estudiando |
| **CQL** | lenguaje para definir y consultar tablas Cassandra |
| **keyspace** | contenedor lógico donde agrupamos las tablas de `compras_claras` |

<div align="center">
<svg style="max-width:460px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 460 150" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Astra database, keyspace y tabla"><style>.s5astree2-r{fill:#eef6f1;stroke:#175c3c;stroke-width:2;}.s5astree2-c{fill:#f4faf6;stroke:#175c3c;stroke-width:1.5;}.s5astree2-t{font:700 13px system-ui,sans-serif;fill:#123f2b;}.s5astree2-l{stroke:#175c3c;stroke-width:1.5;}</style><rect x="20" y="14" width="220" height="32" rx="8" class="s5astree2-r"/><text x="30" y="35" class="s5astree2-t">Astra database</text><line x1="40" y1="46" x2="40" y2="78" class="s5astree2-l"/><line x1="40" y1="78" x2="70" y2="78" class="s5astree2-l"/><rect x="74" y="62" width="300" height="32" rx="8" class="s5astree2-c"/><text x="84" y="83" class="s5astree2-t">keyspace compras_claras</text><line x1="74" y1="78" x2="74" y2="126" class="s5astree2-l"/><line x1="74" y1="126" x2="104" y2="126" class="s5astree2-l"/><rect x="108" y="110" width="330" height="32" rx="8" fill="#fff" stroke="#175c3c" stroke-width="1.5"/><text x="118" y="131" class="s5astree2-t">prioridades_por_corte_departamento</text></svg>
</div>

Elegimos **Serverless (non-vector)** porque hoy trabajamos una tabla Cassandra/CQL por claves. No estamos haciendo embeddings ni búsqueda vectorial.

**PARA LLEVAR.** No necesitas instalar Cassandra localmente ni entender estrategias de replicación para completar esta práctica; Astra administra esa infraestructura.
''')])

    # 9) Driver, SCB, token y prepared statements: reducir la fricción de nube.
    insert_once(cells, "### Ficha del driver", "Modelo de conexión", [md('''
### Modelo de conexión — no memorices objetos: asigna una función a cada uno

<div align="center">
<svg style="max-width:560px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 560 204" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Objetos de conexión Python y su función"><style>.s5scb-k{fill:#175c3c;}.s5scb-kt{font:700 12px "IBM Plex Mono",monospace;fill:#fff;}.s5scb-v{fill:#f4faf6;stroke:#175c3c;stroke-width:1;}.s5scb-vt{font:12px system-ui,sans-serif;fill:#123f2b;}</style><rect x="10" y="6" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="25" text-anchor="middle" class="s5scb-kt">SCB</text><rect x="138" y="6" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="25" class="s5scb-vt">¿cómo llega el driver de forma segura a esta base?</text><rect x="10" y="38" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="57" text-anchor="middle" class="s5scb-kt">TOKEN</text><rect x="138" y="38" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="57" class="s5scb-vt">¿con qué credencial me autentico?</text><rect x="10" y="70" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="89" text-anchor="middle" class="s5scb-kt">Cluster</text><rect x="138" y="70" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="89" class="s5scb-vt">cliente Python configurado</text><rect x="10" y="102" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="121" text-anchor="middle" class="s5scb-kt">Session</text><rect x="138" y="102" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="121" class="s5scb-vt">canal con el que ejecuto CQL</text><rect x="10" y="134" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="153" text-anchor="middle" class="s5scb-kt">prepare</text><rect x="138" y="134" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="153" class="s5scb-vt">plantilla CQL con espacios ? para valores</text><rect x="10" y="166" width="120" height="28" rx="6" class="s5scb-k"/><text x="70.0" y="185" text-anchor="middle" class="s5scb-kt">execute</text><rect x="138" y="166" width="412" height="28" rx="6" class="s5scb-v"/><text x="146" y="185" class="s5scb-vt">envía la plantilla + los valores reales</text></svg>
</div>

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
    insert_once(cells, "insertar = session.prepare", "Upsert", [md('''
### Upsert — por qué repetir la carga no crea una segunda fila con la misma clave

En Cassandra, un `INSERT` con la misma `PRIMARY KEY` tiene comportamiento de **upsert**: si la fila no existe, la crea; si ya existe, escribe/actualiza los valores de esa misma fila.

<div align="center">
<svg style="max-width:520px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 520 158" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de flujo"><defs><marker id="s5ups-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5ups-b{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5ups-t{font:700 14px system-ui,sans-serif;fill:#123f2b;}.s5ups-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="20" y="14" width="480" height="50" rx="10" class="s5ups-b"/><text x="260.0" y="36" text-anchor="middle" class="s5ups-t">1.ª ejecución: P1 no existe</text><text x="260.0" y="54" text-anchor="middle" class="s5ups-s">→ crea P1</text><line x1="260.0" y1="64" x2="260.0" y2="94" stroke="#175c3c" stroke-width="2" marker-end="url(#s5ups-a)"/><rect x="20" y="94" width="480" height="50" rx="10" class="s5ups-b"/><text x="260.0" y="116" text-anchor="middle" class="s5ups-t">2.ª ejecución: misma PK P1</text><text x="260.0" y="134" text-anchor="middle" class="s5ups-s">→ actualiza P1, no crea un duplicado</text></svg>
</div>

Esto ayuda a que la carga del laboratorio sea repetible. **No significa** que 77 escrituras síncronas sean la estrategia recomendada para cargas masivas; aquí priorizamos claridad y trazabilidad.
''')])

    # 11) Fortalecer la interpretación final de pandas ↔ CQL.
    i = find(cells, "### Interpretación del resultado CQL")
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
