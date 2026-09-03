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
    # improve_session5_v7.py reemplaza por completo esta celda (pasa a "Contrato
    # de éxito" con una tabla de 3 productos) en cada corrida del pipeline, así
    # que en la siguiente corrida completa este marcador ya no existe. Si ya fue
    # reemplazada, este paso queda superado y se omite en vez de fallar.
    if any("### Producto observable de hoy" in src(c) for c in cells):
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

    # 3) Sustituir el bloque de precisión por un bloque de hipótesis falsable.
    # Ya convertida en una corrida anterior (o nunca insertada porque el paso 1
    # de improve_session5_v4.py también la detecta ya presente): no hay nada
    # que sustituir, se omite en vez de fallar.
    if any("### PRECISIÓN 0/77 S05" in src(c) for c in cells):
        i = find(cells, "### PRECISIÓN 0/77 S05")
        put(cells[i], '''
### Contraste de hipótesis — usar la prensa para preguntar mejor, no para acusar

Hasta ahora sabemos que las noticias aportan **contexto sobre entidades**. Antes de convertir ese contexto en una afirmación sobre contratos concretos, formulamos una hipótesis de trabajo que pueda fallar de forma observable.

> **Hipótesis de trabajo H1:** al menos una de las 77 referencias SECOP exactas aparece literalmente en los títulos o subtítulos examinados del corpus de prensa.

Esta H1 es útil pedagógicamente porque no depende de opiniones: sabemos exactamente qué observar para sostenerla o refutarla.

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/15_contraste_flujo.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/15_contraste_flujo.png" width="500" alt="Flujo del contraste de hipotesis H1 sobre las 77 referencias SECOP"></a></div>

**Resultado del contraste:** `0/77` coincidencias exactas. En este corpus y bajo esta definición literal, **H1 queda refutada**.

Eso **no es un test estadístico inferencial**: no hay p-valor ni estimación poblacional. Es un **contraste empírico de una hipótesis de trabajo** sobre datos concretos y una regla de observación concreta.

#### ¿Qué decisión permite tomar?

El resultado no invalida la prensa; obliga a **especificar mejor qué evidencia aporta**:

```text
ANTES, demasiado fuerte:
"la prensa respalda estos procesos"

DESPUÉS, mejor especificada:
"la prensa aporta contexto sobre las entidades;
 todavía falta evidencia textual específica del proceso"
```

Aquí la prensa **gana especificidad analítica** porque ahora conocemos con precisión su unidad de evidencia:

- **unidad observada en prensa:** la entidad y su intensidad de mención;
- **unidad que Laura revisa:** el proceso contractual;
- **puente actual:** contexto de entidad, no identificación literal del proceso.

**Cómo se lee.** Ninguna de las 77 referencias exactas apareció en los títulos o subtítulos examinados.  
**Qué nos dice.** La prensa sigue siendo útil para **formular y refinar hipótesis**, priorizar contexto y decidir qué evidencia adicional buscar.  
**Qué NO permite concluir todavía.** No demuestra que ninguna noticia sea relevante para esos procesos: no examinamos aquí cuerpos completos, nombres alternativos, objeto contractual, proveedor, fechas ni similitud semántica.  
**Error frecuente.** Confundir “H1 literal fue refutada” con “la prensa no sirve”. El contraste justamente nos dice **para qué sí sirve y hasta dónde llega**.

**PARA LLEVAR.** Una buena analítica no busca confirmar la primera historia; formula una hipótesis falsable, define cómo observarla, mira la evidencia y **reformula la afirmación al nivel que los datos soportan**.
''')
    else:
        i = find(cells, "### Contraste de hipótesis")

    # 4) Inmediatamente después, dejar una hipótesis revisada que conecte S6/S7.
    if not any("Hipótesis revisada" in src(c) for c in cells):
        pos = i + 1
        cells[pos:pos] = [{
            "cell_type": "markdown",
            "metadata": {},
            "source": '''
### Hipótesis revisada — ¿qué evidencia buscaríamos después?

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

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/16_puente_s6_s7.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/16_puente_s6_s7.png" width="520" alt="Puente hacia S6 relaciones y S7 texto"></a></div>

**Pregunta de negocio.** Laura no necesita que la prensa “condene” un contrato. Necesita que le ayude a **formular mejores hipótesis de revisión y pedir la siguiente evidencia correcta**.
'''.strip(),
        }]

    # 5) El ancla hacia S6 conserva explícitamente el alcance de la prensa.
    for cell in cells:
        text = src(cell)
        if (
            '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas"' in text
            and '"alcance_prensa"' not in text
        ):
            text = text.replace(
                '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas",',
                '"criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas",\n'
                '    "alcance_prensa": "contexto a nivel de entidad; sin referencia exacta del proceso en título/subtítulo",\n'
                '    "hipotesis_h1": "refutada: ninguna referencia SECOP exacta apareció en título/subtítulo",',
                1,
            )
            put(cell, text)
            break

    # 6) Cierre: 0/77 aparece como método de contraste, no como hito equivalente a 77.
    for cell in cells:
        text = src(cell)
        if "Cierre" in text:
            text = text.replace(
                "1.000 → 163 → 77\n        ↓\n       0 / 77\n        ↓\ncontrato pandas",
                "1.000 → 163 → 77\n        ↓\ncontrastar H1: ¿aparece algún ID exacto?\n        ↓\n0/77 → refinar alcance de la prensa\n        ↓\ncontrato pandas",
            )
            text = text.replace(
                "No encontró evidencia literal a nivel de proceso en los títulos/subtítulos (`0/77`), así que la señal periodística debe seguir tratándose como **contexto de entidad**, no como acusación sobre contratos concretos.",
                "Contrastó una hipótesis literal y obtuvo `0/77` referencias exactas en títulos/subtítulos. El valor del resultado no es el cero: es que obliga a **especificar correctamente la evidencia de prensa como contexto de entidad** y a formular la siguiente hipótesis en vez de sobreafirmar.",
            )
            put(cell, text)

    # 7) Hito: exigir hipótesis, operacionalización, evidencia y reformulación.
    for cell in cells:
        text = src(cell)
        if "# Hito S05 — De la priorización al servicio" in text and "hipótesis" not in text.lower():
            text = text.replace(
                "## Mi límite concreto",
                "## Mi contraste de hipótesis\n\n- **H1 de trabajo:** al menos una de las 77 referencias SECOP exactas aparece en título/subtítulo.\n- **Cómo la operacionalicé:** busqué literalmente las 77 referencias en esos dos campos.\n- **Resultado:** 0/77 coincidencias exactas.\n- **Decisión:** H1 queda refutada en este corpus y bajo esta regla literal; la prensa se conserva como contexto de entidad.\n- **Hipótesis siguiente:** buscar relación temática mediante objeto, proveedor, fechas, cuerpo completo o relevancia textual.\n\n## Mi límite concreto",
                1,
            )
            put(cell, text)
            break

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] S5 v5: {len(cells)} celdas; 0/77 reformulado como contraste de hipótesis y especificación de evidencia.")


if __name__ == "__main__":
    main()
