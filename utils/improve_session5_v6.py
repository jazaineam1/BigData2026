#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajusta el cierre de S5 para que 0/77 sea método, no protagonista."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell: dict, text: str) -> None:
    cell["source"] = text.strip()


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in src(cell):
            return i
    raise RuntimeError(f"No se encontró {needle!r}")


nb = json.loads(NB.read_text(encoding="utf-8"))
cells = nb["cells"]

# Cierre: la cadena principal es decisión → contraste → especificación → servicio.
i = find(cells, "CIERRE PEDAGÓGICO S05")
put(cells[i], '''
# CIERRE PEDAGÓGICO S05 — la pregunta de S4 por fin tiene una respuesta operacional

S4 terminó con **datos persistidos y compartidos**. S5 convirtió ese estado en una cadena defendible:

```text
142 entidades en Atlas
        ↓
6 alta / 25 media / 111 baja
        ↓
1.000 procesos SECOP
        ↓
163 con contexto de prensa disponible
        ↓
77 candidatos bajo una heurística explícita
        ↓
CONTRASTE DE H1
¿aparece al menos una referencia SECOP exacta en título/subtítulo?
        ↓
0/77 → H1 literal refutada
        ↓
la prensa queda mejor especificada:
contexto de entidad, no evidencia directa del proceso
        ↓
top esperado con pandas
        ↓
misma respuesta servida por Cassandra
        ↓
un proceso elegido como ancla para S6
```

El valor pedagógico del `0/77` **no es terminar en cero**. Es mostrar una disciplina analítica:

```text
formular hipótesis
→ definir qué observación la puede refutar
→ mirar la evidencia
→ reducir o reformular la afirmación
→ pedir la siguiente evidencia correcta
```

**PARA LLEVAR.** Laura ya puede explicar por qué un proceso llegó a su bandeja, qué papel cumplió la prensa y qué NO puede afirmar todavía. La prensa sirve para **dar contexto, formular hipótesis y orientar la siguiente búsqueda de evidencia**; no convierte una mención de entidad en acusación sobre un contrato.

Lo más importante de Cassandra hoy tampoco fue la sintaxis CQL: fue comprobar que **el diseño de almacenamiento nació de una pregunta concreta** y que el nuevo servicio devolvió la misma respuesta que la lógica analítica que lo alimentó.
''')

# Puente: S6 continúa H2 por relaciones y S7 por texto/relevancia.
i = find(cells, "## Lo que sigue")
put(cells[i], '''
## Lo que sigue — una hipótesis refutada produce una pregunta mejor

S5 no terminó diciendo “la prensa no sirve”. Terminó diciendo algo mucho más preciso:

> **La prensa aporta contexto de entidad; la prueba literal no encontró IDs de proceso en título/subtítulo.**

Por eso la siguiente hipótesis ya no es “¿aparece el ID exacto?”, sino:

> **H2: ¿existe evidencia específica alrededor de este proceso mediante actores, relaciones o contenido temático?**

La próxima sesión empieza cuando Laura abre **el proceso que acabas de elegir** y pregunta:

> **“Ya sé por qué este proceso llegó a mi bandeja y cuál es el alcance real de la prensa. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de su entidad y sus procesos históricos necesito ver?”**

El candidato de S5 será el **ancla**. Los procesos históricos adjudicados aportarán hechos que el candidato todavía no tiene: proveedores, otras contrataciones y conexiones con otras entidades.

```text
S5  contexto de prensa + bandeja + H1 literal refutada
 ↓
S6  especificidad relacional: entidad → proceso → proveedor
 ↓
S7  especificidad textual: relevancia, no solo coincidencia literal
```

Ahí aparece Neo4j. No para declarar irregularidades, sino para **probar una nueva hipótesis con evidencia relacional**.
''')

NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
json.loads(NB.read_text(encoding="utf-8"))
print(f"[OK] S5 v6: {len(cells)} celdas; cierre y puente S6 alineados con contraste de hipótesis.")
