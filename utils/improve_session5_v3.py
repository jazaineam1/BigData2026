#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alinea S5 con el hilo S3→S4→S5→S6 del caso Compras Claras.

Se ejecuta después de improve_session5_v2.py. No cambia la regla 1.000→163→77;
explicita que los 200 de S3 fueron un prototipo exploratorio y convierte la
salida de S5 en una entrada concreta para S6: s05_ancla_s06.json.
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


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def code(text: str) -> dict:
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": text.strip()}


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in src(cell):
            return i
    raise RuntimeError(f"No se encontró el marcador {needle!r}")


def insert_once(cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool) -> None:
    if any(marker in src(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb["cells"]

    insert_once(cells, "## Mapa de la sesión", "CONTINUIDAD S03-S05", [md('''
### CONTINUIDAD S03-S05 — del prototipo a la bandeja operacional

En S3 apareció una primera bandeja de **200 procesos**. Ese resultado fue un **prototipo exploratorio**: servía para demostrar que las señales podían reducir el universo, pero todavía mezclaba decisiones que no habíamos convertido en una regla operacional estable.

Hoy no estamos “corrigiendo 200 por 77” ni comparando el mismo indicador. En S5 fijamos una regla distinta, explícita y reproducible sobre la muestra de 1.000 procesos:

```text
entidad presente en prensa
+ modalidad contiene "directa"
+ respuestas al procedimiento = 0
────────────────────────────────
77 candidatos
```

**PARA LLEVAR.** El número importante no es 77 por sí solo. Lo importante es que Laura puede explicar exactamente **cómo entró cada proceso** y qué evidencia todavía falta.
''')], after=False)

    i = find(cells, "### Producto observable de hoy")
    text = src(cells[i])
    if "s05_ancla_s06.json" not in text:
        text = text.replace(
            "8. un hito descargable con tu decisión y su límite.",
            "8. un hito descargable con tu decisión y su límite;\n9. `s05_ancla_s06.json`: el proceso que Laura abrirá en la sesión 6 para estudiar su contexto relacional.",
        )
        put(cells[i], text)

    insert_once(cells, "# Hito S05 — De la priorización al servicio", "PUENTE S05-S06", [
        md('''
---
## PUENTE S05-S06 — guarda la fila que Laura abrirá después

Hasta aquí S5 respondió **qué mirar primero**. La próxima sesión ya no vuelve a construir esa decisión: toma uno de tus procesos priorizados y pregunta **qué relaciones existen alrededor de él**.

El archivo `s05_ancla_s06.json` conserva el proceso elegido, su entidad y el contexto heredado de las noticias. Si lo conservas, S6 comienza exactamente desde tu propia ejecución. Si lo pierdes, S6 podrá reconstruir la misma bandeja sin bloquearte.
'''),
        code('''
import json

if "top5_esperado_pd" in globals() and len(top5_esperado_pd):
    fila_ancla = top5_esperado_pd.iloc[0]
else:
    fila_ancla = candidatos.iloc[0]

ancla_s06 = {
    "id_proceso": str(fila_ancla["id_del_proceso"]),
    "referencia": str(fila_ancla.get("referencia_del_proceso", "")),
    "entidad": str(fila_ancla["entidad"]),
    "nit_entidad": str(fila_ancla.get("nit_entidad", "")),
    "departamento": str(fila_ancla.get("departamento_entidad", "")),
    "valor_base": int(float(fila_ancla["precio_base"])),
    "modalidad": str(fila_ancla.get("modalidad_de_contratacion", "")),
    "noticias_entidad": int(fila_ancla["noticias_entidad"]),
    "nivel_menciones": str(fila_ancla["nivel_menciones"]),
    "url_secop": str(fila_ancla.get("urlproceso", "")),
    "origen": "bandeja operacional S05: 1.000→163→77",
}

with open("s05_ancla_s06.json", "w", encoding="utf-8") as f:
    json.dump(ancla_s06, f, ensure_ascii=False, indent=2)

print("Ancla S6 lista:")
print(json.dumps(ancla_s06, ensure_ascii=False, indent=2))

try:
    from google.colab import files
    files.download("s05_ancla_s06.json")
except Exception:
    print("Archivo guardado como s05_ancla_s06.json")
'''),
    ], after=False)

    i = find(cells, "## Lo que sigue")
    put(cells[i], '''
## Lo que sigue

S5 terminó con una fila que Laura puede justificar y consultar repetidamente. Pero una fila sigue siendo una fila.

La próxima sesión empieza cuando Laura abre **ese proceso** y pregunta:

> **“Ya sé por qué este proceso llegó primero a mi bandeja. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de su entidad y sus procesos históricos necesito ver?”**

El candidato de S5 será el **ancla**. Los procesos históricos adjudicados aportarán el contexto que ese candidato todavía no tiene: proveedores, otras contrataciones y conexiones con otras entidades.

```text
S3  evidencia documental
 ↓
S4  persistencia compartida
 ↓
S5  qué revisar primero
 ↓
S6  qué hay alrededor de lo que voy a revisar
```

Ahí aparece Neo4j. No para declarar irregularidades, sino para hacer de las **relaciones** una parte explícita de la revisión.
''')

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] S5 v3: {len(cells)} celdas; continuidad y puente S6 aplicados.")


if __name__ == "__main__":
    main()
