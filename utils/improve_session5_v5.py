#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reformula el control 0/77 como contraste de una hipótesis de trabajo.

Se ejecuta después de improve_session5_v4.py. Conserva los baselines y la regla
1.000→163→77, pero quita protagonismo al cero como 'resultado final'. En su
lugar, enseña operacionalización, falsación y unidad de inferencia: la prensa
sirve como contexto a nivel de entidad y como fuente para formular/refinar
hipótesis, no como evidencia automática de irregularidad a nivel de proceso.
"""
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
    raise RuntimeError(f"No se encontró el marcador {needle!r}")


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb["cells"]

    # 1) Producto: 0/77 deja de ser un titular; pasa a ser un contraste empírico.
    i = find(cells, "### Producto observable de hoy")
    text = src(cells[i])
    text = text.replace(
        "4. el límite analítico `0 de 77` referencias de proceso citadas literalmente en prensa;",
        "4. un **contraste de hipótesis** que separa contexto de prensa a nivel de entidad de evidencia específica a nivel de proceso;",
    )
    text = text.replace(
        "9. `s05_ancla_s06.json`: el proceso que Laura abrirá en la sesión 6 para estudiar su contexto relacional.",
        "9. `s05_ancla_s06.json`: el proceso que Laura abrirá en la sesión 6, conservando también el alcance real de la evidencia de prensa.",
    )
    put(cells[i], text)

    # 2) Mapa: la etapa ahora es contrastar una hipótesis, no celebrar el 0/77.
    i = find(cells, "## Mapa de la sesión")
    text = src(cells[i])
    text = text.replace(
        "| 4. Límite | ¿qué evidencia tenemos realmente? | 0/77 |",
        "| 4. Contrastar hipótesis | ¿la prensa identifica literalmente estos procesos? | alcance de la evidencia |",
    )
    put(cells[i], text)

    # 3) Sustituir el bloque de precisión por un bloque de hipótesis más potente.
    i = find(cells, "### PRECISIÓN 0/77 S05")
    put(cells[i], '''
### CONTRASTE DE HIPÓTESIS S05 — usar la prensa para preguntar mejor, no para acusar

Hasta ahora sabemos que las noticias aportan **contexto sobre entidades**. Antes de convertir ese contexto en una afirmación sobre contratos concretos, formulamos una hipótesis de trabajo que podamos intentar refutar.

> **Hipótesis de trabajo H1:** si la evidencia periodística disponible es específica de los 77 procesos priorizados, entonces deberíamos encontrar al menos algunas de sus referencias SECOP exactas en los títulos o subtítulos examinados.

La operacionalizamos de forma observable:

```text
77 referencias SECOP exactas
        ↓
búsqueda literal en título + subtítulo
        ↓
coincidencias observadas
```

**Resultado del contraste:** `0/77` coincidencias exactas.

Eso **no es un test estadístico inferencial**: no hay p-valor ni estimación poblacional. Es un **contraste empírico de una hipótesis de trabajo** sobre este corpus y esta definición de coincidencia.

#### ¿Qué decisión permite tomar?

La evidencia **no apoya H1 bajo esta operacionalización exacta**. Por tanto, debemos refinar la afirmación:

```text
ANTES, demasiado fuerte:
"la prensa respalda estos procesos"

DESPUÉS, mejor especificada:
"la prensa aporta contexto sobre las entidades;
 todavía falta evidencia textual específica del proceso"
```

Aquí la prensa **gana especificidad analítica** porque ahora sabemos con precisión cuál es su unidad de evidencia:

- **unidad observada en prensa:** la entidad y su intensidad de mención;
- **unidad que Laura revisa:** el proceso contractual;
- **puente actual:** contexto de entidad, no identificación literal del proceso.

**Cómo se lee.** No encontramos referencias exactas de los 77 procesos en los títulos o subtítulos examinados.  
**Qué nos dice.** La prensa sigue siendo útil para **formular y refinar hipótesis**, priorizar contexto y decidir qué evidencia adicional buscar.  
**Qué NO permite concluir todavía.** No demuestra que ninguna noticia sea relevante para esos procesos: no examinamos aquí cuerpos completos, nombres alternativos, objeto contractual, proveedor, fechas ni similitud semántica.  
**Error frecuente.** Confundir “H1 no fue apoyada por esta prueba” con “la prensa no sirve”. El contraste justamente nos dice **para qué sí sirve y hasta dónde llega**.

**PARA LLEVAR.** Una buena analítica no busca confirmar la primera historia; formula una hipótesis, define cómo podría fallar, mira la evidencia y **reformula la afirmación al nivel que los datos soportan**.
''')

    # 4) Inmediatamente después, dejar una hipótesis revisada que conecte S6/S7.
    if not any("HIPÓTESIS REVISADA S05" in src(c) for c in cells):
        pos = i + 1
        cells[pos:pos] = [{
            "cell_type": "markdown",
            "metadata": {},
            "source": '''
### HIPÓTESIS REVISADA S05 — ¿qué evidencia buscaríamos después?

El `0/77` no cierra la investigación: **mejora la siguiente pregunta**.

> **H2:** aunque el ID exacto no aparezca, algunos procesos podrían estar relacionados temáticamente con noticias mediante su entidad, objeto, proveedor, lugar o periodo.

Para evaluar H2 necesitaríamos evidencia más específica, por ejemplo:

| Evidencia adicional | Qué pregunta permitiría hacer |
|---|---|
| nombre/objeto del procedimiento | ¿la noticia habla del mismo tema contractual? |
| proveedor | ¿el actor aparece en otras relaciones relevantes? |
| fechas | ¿la noticia y el proceso son temporalmente compatibles? |
| cuerpo completo del texto | ¿hay menciones que no aparecen en título/subtítulo? |
| búsqueda por relevancia | ¿qué documentos son más pertinentes aunque no compartan el ID literal? |

Esto prepara dos pasos del semestre:

```text
S6 → relaciones: entidad → proceso → proveedor
S7 → texto: relevancia, no solo coincidencia literal
```

**Pregunta de negocio.** Laura no necesita que la prensa “condene” un contrato. Necesita que le ayude a **formular mejores hipótesis de revisión y pedir la siguiente evidencia correcta**.
'''.strip(),
        }]

    # 5) El ancla hacia S6 conserva explícitamente el alcance de la prensa.
    for cell in cells:
        text = src(cell)
        if '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas"' in text:
            text = text.replace(
                '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas",',
                '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas",\n'
                '    "alcance_prensa": "contexto a nivel de entidad; sin referencia exacta del proceso en título/subtítulo",\n'
                '    "hipotesis_h1": "no apoyada por búsqueda literal de referencia exacta en título/subtítulo",',
                1,
            )
            put(cell, text)
            break

    # 6) Cierre: 0/77 aparece como método de contraste, no como hito equivalente a 77.
    for cell in cells:
        text = src(cell)
        if "CIERRE PEDAGÓGICO S05" in text:
            text = text.replace(
                "1.000 → 163 → 77\n        ↓\n       0 / 77\n        ↓\ncontrato pandas",
                "1.000 → 163 → 77\n        ↓\ncontrastar H1: ¿hay evidencia literal del proceso?\n        ↓\n0/77 → refinar alcance de la prensa\n        ↓\ncontrato pandas",
            )
            text = text.replace(
                "No encontró evidencia literal a nivel de proceso en los títulos/subtítulos (`0/77`), así que la señal periodística debe seguir tratándose como **contexto de entidad**, no como acusación sobre contratos concretos.",
                "Contrastó una hipótesis de especificidad y obtuvo `0/77` referencias exactas en títulos/subtítulos. El valor del resultado no es el cero: es que obliga a **especificar correctamente la evidencia de prensa como contexto de entidad** y a formular la siguiente hipótesis en vez de sobreafirmar.",
            )
            put(cell, text)

    # 7) Hito: exigir hipótesis, operacionalización, evidencia y reformulación.
    for cell in cells:
        text = src(cell)
        if "# Hito S05 — De la priorización al servicio" in text and "hipótesis" not in text.lower():
            text = text.replace(
                "## Mi límite concreto",
                "## Mi contraste de hipótesis\n\n- **H1 de trabajo:** la prensa identifica de forma literal algunos procesos priorizados.\n- **Cómo la operacionalicé:** busqué la referencia SECOP exacta en título/subtítulo.\n- **Resultado:** 0/77 coincidencias exactas.\n- **Decisión:** H1 no queda apoyada bajo esta prueba; la prensa se conserva como contexto de entidad.\n- **Hipótesis siguiente:** buscar relación temática mediante objeto, proveedor, fechas, cuerpo completo o relevancia textual.\n\n## Mi límite concreto",
                1,
            )
            put(cell, text)
            break

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] S5 v5: {len(cells)} celdas; 0/77 reformulado como contraste de hipótesis y especificación de evidencia.")


if __name__ == "__main__":
    main()
