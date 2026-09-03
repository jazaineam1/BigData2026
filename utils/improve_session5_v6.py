#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajusta S5 para que 0/77 sea método de contraste, no protagonista."""
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


def find_any(cells: list[dict], needles: tuple[str, ...]) -> int:
    for needle in needles:
        for i, cell in enumerate(cells):
            if needle in src(cell):
                return i
    raise RuntimeError(f"No se encontró ninguno de {needles!r}")


nb = json.loads(NB.read_text(encoding="utf-8"))
cells = nb["cells"]

# 1) La sección deja de anunciar un cero y anuncia una pregunta falsable.
i = find_any(cells, (
    "## 6. El límite que debe viajar con la bandeja",
    "## 6. Antes de afirmar: formula una hipótesis que pueda fallar",
))
put(cells[i], '''
---
## 6. Antes de afirmar: formula una hipótesis que pueda fallar

La bandeja ya existe. Ahora hacemos algo distinto de filtrar: **ponemos a prueba una afirmación sobre la prensa**.

La pregunta no es “¿la prensa sirve o no sirve?”. Esa pregunta es demasiado vaga. La hacemos observable:

> **H1: al menos una de las 77 referencias SECOP exactas aparece literalmente en los títulos o subtítulos examinados.**

¿Por qué esta formulación es mejor?

```text
afirmación vaga
"la prensa habla de estos contratos"
        ↓
hipótesis observable
"aparece al menos un ID exacto"
        ↓
regla de comprobación
buscar los 77 IDs en título + subtítulo
```

Si aparece al menos uno, H1 sobrevive a esta prueba literal. Si aparecen cero, H1 queda refutada **bajo esta operacionalización**.

**Importante:** esto no es todavía un test estadístico inferencial. Es un contraste empírico de una hipótesis de trabajo sobre este corpus.

**PARA LLEVAR.** La prensa no entra al evaluador para dictar culpabilidad. Entra para aportar contexto, permitir formular hipótesis y ayudarnos a decidir cuál debe ser la siguiente evidencia.
''')

# 2) El hito conserva explícitamente hipótesis, observación y decisión.
i = find(cells, "hito = f'''# Hito S05")
text = src(cells[i])
marker = '- Contexto desde Atlas: {primer_noticias} noticias — nivel {primer_nivel}'
if marker in text and "## Contraste de hipótesis de prensa" not in text:
    text = text.replace(
        marker,
        marker + '''

## Contraste de hipótesis de prensa
- H1: al menos una de las 77 referencias SECOP exactas aparece en título/subtítulo.
- Operacionalización: búsqueda literal de las 77 referencias exactas.
- Resultado observado: {con_referencia}/77 coincidencias exactas.
- Decisión sobre H1: {"refutada bajo esta prueba literal" if con_referencia == 0 else "no refutada por esta prueba literal"}.
- Alcance de la prensa: contexto a nivel de entidad; falta todavía evidencia textual específica del proceso.
- Hipótesis siguiente: relación temática o relacional mediante objeto, proveedor, fechas, cuerpo completo o relevancia textual.''',
        1,
    )
put(cells[i], text)

# 3) La rúbrica evalúa razonamiento de hipótesis, no memorización del cero.
i = find(cells, "## Rúbrica de calidad del hito")
text = src(cells[i])
text = text.replace(
    "| Regla + límite | 1.000→163→77 y explica 0/77 | números sin límite concreto | llama “irregulares” a los 77 | 20 |",
    "| Regla + contraste | 1.000→163→77 + H1 + operacionalización + conclusión correcta | reporta 0/77 sin explicar qué hipótesis probó | convierte prensa o bandeja en acusación | 20 |",
)
put(cells[i], text)

# 4) Cierre: la cadena principal es decisión → contraste → especificación → servicio.
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

# 5) Puente: S6 continúa H2 por relaciones y S7 por texto/relevancia.
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
print(f"[OK] S5 v6: {len(cells)} celdas; hipótesis integrada en sección, hito, rúbrica, cierre y puente S6.")
