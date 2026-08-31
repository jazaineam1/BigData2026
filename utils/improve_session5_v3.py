#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alinea S5 con el hilo S3→S4→S5→S6 del caso Compras Claras.

Se ejecuta después de improve_session5_v2.py. No cambia la regla 1.000→163→77;
explicita que los 200 de S3 fueron un prototipo exploratorio y convierte la
salida de S5 en una entrada concreta e individual para S6: s05_ancla_s06.json.
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


def find_any(cells: list[dict], needles: tuple[str, ...]) -> int:
    for needle in needles:
        for i, cell in enumerate(cells):
            if needle in src(cell):
                return i
    raise RuntimeError(f"No se encontró ninguno de los marcadores: {needles!r}")


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
            "8. un hito descargable con tu decisión y su límite;\n9. `s05_ancla_s06.json`: el proceso que tú eliges para que Laura abra en S6 y estudie su contexto relacional.",
        )
        put(cells[i], text)

    insert_once(cells, "# Hito S05 — De la priorización al servicio", "PUENTE S05-S06", [
        md('''
---
## PUENTE S05-S06 — elige la fila que Laura abrirá después

Hasta aquí S5 respondió **qué mirar primero**. La próxima sesión no vuelve a construir esa decisión: toma **uno de tus procesos priorizados** y pregunta **qué relaciones existen alrededor de él**.

Si ejecutaste el contrato individual, verás tu top de pandas y escogerás cuál proceso llevar. Esa pequeña decisión hace que S6 empiece desde tu propia ejecución y no desde una fila impuesta por el cuaderno.

**Qué debe verse si salió bien:** un JSON con el ID, entidad, NIT, departamento, valor, contexto de prensa y criterio de priorización.  
**Error probable:** elegir un número fuera de la lista. Significa que la selección no corresponde a tu top disponible.  
**Recuperación:** vuelve a ejecutar la celda y elige uno de los números mostrados; si no existe el top individual, la celda usa el primer candidato como respaldo explícito.
'''),
        code('''
import json

if "top5_esperado_pd" in globals() and len(top5_esperado_pd):
    opciones_ancla = top5_esperado_pd.reset_index(drop=True)
    print("Elige el proceso que quieres llevar a S6:")
    for i, fila in opciones_ancla.iterrows():
        print(
            f"{i+1:>2}. {fila['id_del_proceso']} | {fila['entidad']} | "
            f"$ {float(fila['precio_base']):,.0f}"
        )
    seleccion_ancla = int(input("Número de proceso para S6: ").strip())
    if not 1 <= seleccion_ancla <= len(opciones_ancla):
        raise ValueError("El número debe corresponder a uno de los procesos mostrados.")
    fila_ancla = opciones_ancla.iloc[seleccion_ancla - 1]
    origen_eleccion_s06 = "selección propia dentro del top pandas S05"
else:
    fila_ancla = candidatos.iloc[0]
    seleccion_ancla = 1
    origen_eleccion_s06 = "respaldo: primer candidato de la bandeja S05"
    print("No existe top individual en memoria; se usa el primer candidato como respaldo.")

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
    "criterio_priorizacion": "entidad en prensa; contratación directa; 0 respuestas",
    "origen": "bandeja operacional S05: 1.000→163→77",
    "origen_eleccion": origen_eleccion_s06,
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
        md('''
### Interpretación del ancla elegida

**Cómo se lee.** El JSON conserva una fila que ya pasó la regla `1.000→163→77` y registra si fue una elección propia o un respaldo.

**Qué nos dice.** S6 puede comenzar desde un proceso concreto sin rehacer la priorización.

**Qué NO permite concluir todavía.** Elegir una fila para profundizar no significa que sea irregular ni la “más riesgosa”. Faltan relaciones contractuales históricas y evidencia específica del proceso.

**Error frecuente.** Tratar la posición en la bandeja como una probabilidad de fraude.
'''),
    ], after=False)

    i = find_any(cells, ("## Lo que sigue", "# Cierre"))
    put(cells[i], '''
## Lo que sigue

S5 terminó con una fila que Laura puede justificar y consultar repetidamente. Pero una fila sigue siendo una fila.

La próxima sesión empieza cuando Laura abre **el proceso que acabas de elegir** y pregunta:

> **“Ya sé por qué este proceso llegó a mi bandeja. Antes de asignarlo a un auditor, ¿qué relaciones alrededor de su entidad y sus procesos históricos necesito ver?”**

El candidato de S5 será el **ancla**. Los procesos históricos adjudicados aportarán el contexto que ese candidato todavía no tiene: proveedores, otras contrataciones y conexiones con otras entidades.

```text
S3  evidencia documental
 ↓
S4  persistencia compartida
 ↓
S5  qué revisar primero + ancla elegida
 ↓
S6  qué hay alrededor de lo que voy a revisar
```

Ahí aparece Neo4j. No para declarar irregularidades, sino para hacer de las **relaciones** una parte explícita de la revisión.
''')

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"[OK] S5 v3: {len(cells)} celdas; continuidad y puente individual S6 aplicados.")


if __name__ == "__main__":
    main()
