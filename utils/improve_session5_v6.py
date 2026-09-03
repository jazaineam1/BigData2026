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

<div align="center">
<svg style="max-width:520px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 520 238" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de flujo"><defs><marker id="s5hip-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5hip-b{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5hip-t{font:700 14px system-ui,sans-serif;fill:#123f2b;}.s5hip-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="20" y="14" width="480" height="50" rx="10" class="s5hip-b"/><text x="260.0" y="36" text-anchor="middle" class="s5hip-t">Afirmación vaga</text><text x="260.0" y="54" text-anchor="middle" class="s5hip-s">“la prensa habla de estos contratos”</text><line x1="260.0" y1="64" x2="260.0" y2="94" stroke="#175c3c" stroke-width="2" marker-end="url(#s5hip-a)"/><rect x="20" y="94" width="480" height="50" rx="10" class="s5hip-b"/><text x="260.0" y="116" text-anchor="middle" class="s5hip-t">Hipótesis observable</text><text x="260.0" y="134" text-anchor="middle" class="s5hip-s">“aparece al menos un ID exacto”</text><line x1="260.0" y1="144" x2="260.0" y2="174" stroke="#175c3c" stroke-width="2" marker-end="url(#s5hip-a)"/><rect x="20" y="174" width="480" height="50" rx="10" class="s5hip-b"/><text x="260.0" y="196" text-anchor="middle" class="s5hip-t">Regla de comprobación</text><text x="260.0" y="214" text-anchor="middle" class="s5hip-s">buscar los 77 IDs en título + subtítulo</text></svg>
</div>

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
i = find(cells, "Cierre")
put(cells[i], '''
# Cierre — la pregunta de S4 por fin tiene una respuesta operacional

S4 terminó con **datos persistidos y compartidos**. S5 convirtió ese estado en una cadena defendible:

<div align="center">
<svg style="max-width:660px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 660 658" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Arquitectura de la sesión: de la vista en Atlas al ancla para S6"><defs><marker id="s5cierre-arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5cierre-box{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5cierre-h{font:700 15px system-ui,sans-serif;fill:#123f2b;}.s5cierre-s{font:12.5px system-ui,sans-serif;fill:#3a4a41;}.s5cierre-n{font:700 12px system-ui,sans-serif;fill:#ffffff;}</style><circle cx="38" cy="42.0" r="14" fill="#175c3c"/><text x="38" y="47.0" text-anchor="middle" class="s5cierre-n">1</text><rect x="62" y="14" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="38" class="s5cierre-h">Atlas — vista</text><text x="78" y="56" class="s5cierre-s">142 entidades clasificadas · 6 alta / 25 media / 111 baja</text><line x1="38" y1="70" x2="38" y2="96" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="124.0" r="14" fill="#175c3c"/><text x="38" y="129.0" text-anchor="middle" class="s5cierre-n">2</text><rect x="62" y="96" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="120" class="s5cierre-h">SECOP</text><text x="78" y="138" class="s5cierre-s">1.000 procesos de contratación</text><line x1="38" y1="152" x2="38" y2="178" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="206.0" r="14" fill="#175c3c"/><text x="38" y="211.0" text-anchor="middle" class="s5cierre-n">3</text><rect x="62" y="178" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="202" class="s5cierre-h">Filtro: entidad en prensa</text><text x="78" y="220" class="s5cierre-s">163 procesos</text><line x1="38" y1="234" x2="38" y2="260" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="288.0" r="14" fill="#175c3c"/><text x="38" y="293.0" text-anchor="middle" class="s5cierre-n">4</text><rect x="62" y="260" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="284" class="s5cierre-h">Filtro: directa + 0 respuestas</text><text x="78" y="302" class="s5cierre-s">77 candidatos (la bandeja)</text><line x1="38" y1="316" x2="38" y2="342" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="370.0" r="14" fill="#175c3c"/><text x="38" y="375.0" text-anchor="middle" class="s5cierre-n">5</text><rect x="62" y="342" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="366" class="s5cierre-h">Contraste H1</text><text x="78" y="384" class="s5cierre-s">¿ID exacto en título/subtítulo? → 0/77 → H1 refutada</text><line x1="38" y1="398" x2="38" y2="424" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="452.0" r="14" fill="#175c3c"/><text x="38" y="457.0" text-anchor="middle" class="s5cierre-n">6</text><rect x="62" y="424" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="448" class="s5cierre-h">pandas</text><text x="78" y="466" class="s5cierre-s">calcula el top 5 esperado por corte + departamento</text><line x1="38" y1="480" x2="38" y2="506" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="534.0" r="14" fill="#175c3c"/><text x="38" y="539.0" text-anchor="middle" class="s5cierre-n">7</text><rect x="62" y="506" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="530" class="s5cierre-h">Cassandra</text><text x="78" y="548" class="s5cierre-s">sirve el mismo top 5 desde la tabla operativa</text><line x1="38" y1="562" x2="38" y2="588" stroke="#175c3c" stroke-width="2" marker-end="url(#s5cierre-arrow)"/><circle cx="38" cy="616.0" r="14" fill="#175c3c"/><text x="38" y="621.0" text-anchor="middle" class="s5cierre-n">8</text><rect x="62" y="588" width="578" height="56" rx="10" class="s5cierre-box"/><text x="78" y="612" class="s5cierre-h">Ancla S6</text><text x="78" y="630" class="s5cierre-s">1 proceso elegido para explorar relaciones</text></svg>
</div>

**Cómo leer el diagrama.** El contraste de H1 resultó en `0/77 → H1 literal refutada`: la prensa queda mejor especificada como contexto de entidad, no como evidencia directa del proceso.

El valor pedagógico del `0/77` **no es terminar en cero**. Es mostrar una disciplina analítica:

<div align="center">
<svg style="max-width:520px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 520 310" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de flujo"><defs><marker id="s5disc-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5disc-b{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5disc-t{font:700 14px system-ui,sans-serif;fill:#123f2b;}.s5disc-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="20" y="14" width="480" height="42" rx="10" class="s5disc-b"/><text x="260.0" y="40.0" text-anchor="middle" class="s5disc-t">1 · Formular hipótesis</text><line x1="260.0" y1="56" x2="260.0" y2="74" stroke="#175c3c" stroke-width="2" marker-end="url(#s5disc-a)"/><rect x="20" y="74" width="480" height="42" rx="10" class="s5disc-b"/><text x="260.0" y="100.0" text-anchor="middle" class="s5disc-t">2 · Definir qué observación la puede refutar</text><line x1="260.0" y1="116" x2="260.0" y2="134" stroke="#175c3c" stroke-width="2" marker-end="url(#s5disc-a)"/><rect x="20" y="134" width="480" height="42" rx="10" class="s5disc-b"/><text x="260.0" y="160.0" text-anchor="middle" class="s5disc-t">3 · Mirar la evidencia</text><line x1="260.0" y1="176" x2="260.0" y2="194" stroke="#175c3c" stroke-width="2" marker-end="url(#s5disc-a)"/><rect x="20" y="194" width="480" height="42" rx="10" class="s5disc-b"/><text x="260.0" y="220.0" text-anchor="middle" class="s5disc-t">4 · Reducir o reformular la afirmación</text><line x1="260.0" y1="236" x2="260.0" y2="254" stroke="#175c3c" stroke-width="2" marker-end="url(#s5disc-a)"/><rect x="20" y="254" width="480" height="42" rx="10" class="s5disc-b"/><text x="260.0" y="280.0" text-anchor="middle" class="s5disc-t">5 · Pedir la siguiente evidencia correcta</text></svg>
</div>

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

<div align="center">
<svg style="max-width:540px;width:100%;height:auto;display:block;margin:0 auto;" viewBox="0 0 540 238" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Diagrama de flujo"><defs><marker id="s5puente-a" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#175c3c"/></marker></defs><style>.s5puente-b{fill:#f4faf6;stroke:#175c3c;stroke-width:2;}.s5puente-t{font:700 14px system-ui,sans-serif;fill:#123f2b;}.s5puente-s{font:12px system-ui,sans-serif;fill:#3a4a41;}</style><rect x="20" y="14" width="500" height="50" rx="10" class="s5puente-b"/><text x="270.0" y="36" text-anchor="middle" class="s5puente-t">S5</text><text x="270.0" y="54" text-anchor="middle" class="s5puente-s">contexto de prensa + bandeja + H1 literal refutada</text><line x1="270.0" y1="64" x2="270.0" y2="94" stroke="#175c3c" stroke-width="2" marker-end="url(#s5puente-a)"/><rect x="20" y="94" width="500" height="50" rx="10" class="s5puente-b"/><text x="270.0" y="116" text-anchor="middle" class="s5puente-t">S6</text><text x="270.0" y="134" text-anchor="middle" class="s5puente-s">especificidad relacional: entidad → proceso → proveedor</text><line x1="270.0" y1="144" x2="270.0" y2="174" stroke="#175c3c" stroke-width="2" marker-end="url(#s5puente-a)"/><rect x="20" y="174" width="500" height="50" rx="10" class="s5puente-b"/><text x="270.0" y="196" text-anchor="middle" class="s5puente-t">S7</text><text x="270.0" y="214" text-anchor="middle" class="s5puente-s">especificidad textual: relevancia, no solo coincidencia literal</text></svg>
</div>

**En síntesis:** S6 — especificidad relacional: entidad → proceso → proveedor. S7 — especificidad textual: relevancia, no solo coincidencia literal.

Ahí aparece Neo4j. No para declarar irregularidades, sino para **probar una nueva hipótesis con evidencia relacional**.
''')

NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
json.loads(NB.read_text(encoding="utf-8"))
print(f"[OK] S5 v6: {len(cells)} celdas; hipótesis integrada en sección, hito, rúbrica, cierre y puente S6.")
