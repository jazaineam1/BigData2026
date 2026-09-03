#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Alinea S5 con el hilo real S3→S4→S5→S6 del caso Compras Claras.

Se ejecuta después de improve_session5_v2.py. No cambia la regla 1.000→163→77.
Hace explícita la deuda que dejó la S4 real, fortalece la recuperación post-receso,
convierte la salida de S5 en una entrada individual para S6 y limpia artefactos
duplicados que puedan aparecer por regeneraciones históricas del notebook.
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
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": text.strip(),
    }


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


def bridge_cells() -> list[dict]:
    return [
        md('''
---
## Puente hacia la sesión 6 — elige la fila que Laura abrirá después

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
    ]


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb["cells"]

    for cell in cells:
        text = src(cell)
        if text.startswith("# Sesión 5 —"):
            text = text.replace(
                "# Sesión 5 — De una vista de Atlas a una consulta operacional con Cassandra",
                "# Sesión 5 — De datos persistidos en Atlas a una consulta operacional con Cassandra",
                1,
            )
            text = text.replace(
                "**Pregunta profesional:** **¿cómo convierte Laura una priorización analítica en una consulta que pueda repetir sin reconstruir todo cada vez?**",
                "**Pregunta profesional:** **¿cómo convierte Laura la evidencia que ya dejó persistida en Atlas en una bandeja priorizada y luego en una consulta que pueda repetir sin reconstruir todo cada vez?**",
                1,
            )
            put(cell, text)
            break

    insert_once(cells, "## Mapa de la sesión", "Deuda abierta", [md('''
### Deuda abierta — la clase terminó con datos, no con una decisión

**El problema.** Laura necesita decidir, de forma repetible y explicable, qué contrato de Compras Claras revisar primero. Sesiones anteriores dejaron los datos guardados y compartidos en MongoDB Atlas, pero **la clase terminó con datos, no con una decisión**: sabíamos dónde vivía la evidencia, no cómo convertirla en una prioridad defendible.

### Continuidad — de la exploración a la bandeja operacional

**Qué hemos hecho (resumen; no necesitas recordar los detalles exactos de clases anteriores).** Ya probamos una primera bandeja como **prototipo exploratorio**: sirvió para ver que las señales de prensa podían ayudar a reducir el universo de contratos, pero todavía no era una regla reproducible.

**Qué haremos hoy.** Convertimos esa exploración en una **bandeja operacional** en tres pasos: (1) publicamos en Atlas una vista que clasifica cada entidad según su presencia en prensa, (2) usamos esa vista para construir, con una regla explícita, la bandeja de candidatos, y (3) diseñamos en Cassandra una tabla que sirve esa misma consulta una y otra vez, rápido.

**Enfoque.** Cada paso deja una evidencia verificable —una vista, una regla reproducible, una tabla que responde lo mismo que ya validaste en pandas—, no una sintaxis para memorizar.

**Para qué.** Para que puedas defender, con evidencia, por qué un proceso llegó a la bandeja y por qué Cassandra responde correctamente esa pregunta repetitiva.

**Qué se espera al final.** Que expliques la vista, justifiques la bandeja de candidatos y razones por qué la tabla Cassandra responde el top 5 — sin depender de la memoria de sesiones pasadas.
''')], after=False)

    i = find(cells, "### Producto observable de hoy")
    text = src(cells[i])
    if "s05_ancla_s06.json" not in text:
        text = text.replace(
            "8. un hito descargable con tu decisión y su límite.",
            "8. un hito descargable con tu decisión y su límite;\n9. `s05_ancla_s06.json`: el proceso que tú eliges para que Laura abra en S6 y estudie su contexto relacional.",
        )
        put(cells[i], text)

    i = find(cells, "# Recuperación")
    put(cells[i], '''
# Recuperación
if "candidatos" not in globals():
    import json, urllib.request
    import pandas as pd
    from collections import Counter

    RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"

    with urllib.request.urlopen(f"{RAW}/Datos/entidades_en_noticias_2026.json") as r:
        menciones = json.loads(r.read().decode("utf-8"))

    for e in menciones:
        n = e.get("noticias", 0)
        e["nivel_menciones"] = "alta" if n >= 20 else "media" if n >= 5 else "baja"

    niveles = Counter(m["nivel_menciones"] for m in menciones)
    contexto_menciones = (
        pd.DataFrame(menciones)[["entidad", "noticias", "nivel_menciones"]]
        .rename(columns={"noticias": "noticias_entidad"})
    )
    assert contexto_menciones["entidad"].is_unique
    vista_real = False

    secop = pd.read_csv(
        f"{RAW}/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv",
        low_memory=False,
    )
    entidades_en_prensa = set(contexto_menciones["entidad"])
    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]
    paso2 = paso1[
        paso1["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)
    ]
    respuestas = pd.to_numeric(paso2["respuestas_al_procedimiento"], errors="coerce")
    paso3 = paso2[respuestas.eq(0)]
    candidatos = (
        paso3
        .merge(contexto_menciones, on="entidad", how="left", validate="many_to_one")
        .sort_values(["precio_base", "id_del_proceso"], ascending=[False, True])
        .reset_index(drop=True)
    )

    with urllib.request.urlopen(f"{RAW}/Datos/noticias_contratacion_2026.json") as r:
        noticias = json.loads(r.read().decode("utf-8"))
    texto_prensa = " ".join(
        f'{n.get("titulo") or ""} {n.get("subtitulo") or ""}' for n in noticias
    ).casefold()
    referencias = candidatos["referencia_del_proceso"].fillna("").astype(str).str.strip()
    con_referencia = sum(
        bool(x) and len(x) >= 6 and x.casefold() in texto_prensa
        for x in referencias
    )

    assert len(menciones) == 142
    assert dict(niveles) == {"baja": 111, "media": 25, "alta": 6}
    assert len(secop) == 1000
    assert len(paso1) == 163
    assert len(candidatos) == 77
    assert candidatos["noticias_entidad"].notna().all()
    assert candidatos["nivel_menciones"].notna().all()
    assert con_referencia == 0
    print("Runtime recuperado: 142 entidades · 1.000 → 163 → 77 · 0/77 · contexto Atlas restaurado.")
else:
    print("La bandeja sigue en memoria:", len(candidatos), "candidatos. No fue necesario reconstruirla.")
''')

    new_bridge = bridge_cells()
    try:
        b = find(cells, "Puente hacia la sesión 6")
        end = b + 1
        while end < len(cells) and (
            "s05_ancla_s06.json" in src(cells[end])
            or "Interpretación del ancla elegida" in src(cells[end])
        ):
            end += 1
        cells[b:end] = new_bridge
    except RuntimeError:
        h = find(cells, "# Hito S05 — De la priorización al servicio")
        cells[h:h] = new_bridge

    indices_cierre = [
        i for i, cell in enumerate(cells)
        if "#@title Cerrar conexiones" in src(cell)
        or "# Buena práctica: cerrar clientes al terminar la sesión." in src(cell)
    ]
    if indices_cierre:
        keep = indices_cierre[0]
        cierre_src = src(cells[keep])
        if "CERRAR CONEXIONES S05" not in cierre_src:
            cierre_src = cierre_src.replace(
                "# Buena práctica: cerrar clientes al terminar la sesión.",
                "# CERRAR CONEXIONES S05\n# Buena práctica: cerrar clientes al terminar la sesión.",
                1,
            )
            put(cells[keep], cierre_src)
        for idx in reversed(indices_cierre[1:]):
            del cells[idx]

    if not any("Cierre" in src(c) for c in cells):
        cierre_anchor = find_any(cells, ("## Lo que sigue", "# Cierre"))
        cells[cierre_anchor:cierre_anchor] = [md('''
# Cierre — la pregunta de S4 por fin tiene una respuesta operacional

S4 terminó con **datos persistidos y compartidos**. S5 convirtió ese estado en una cadena defendible:

```text
142 entidades en Atlas
→ 6 alta / 25 media / 111 baja
→ 1.000 procesos SECOP
→ 163 con entidad presente en prensa
→ 77 candidatos con contratación directa y 0 respuestas
→ 0/77 referencias de proceso citadas literalmente en títulos/subtítulos
→ top esperado con pandas
→ misma respuesta servida por Cassandra
→ un proceso elegido como ancla para S6
```

**PARA LLEVAR.** Laura ya puede explicar por qué un proceso llegó a su bandeja y consultar repetidamente esa priorización. La bandeja **prioriza revisión**; no declara fraude, irregularidad ni causalidad.

Lo más importante de Cassandra hoy no fue la sintaxis CQL: fue comprobar que **el diseño de almacenamiento nació de una pregunta concreta** y que el nuevo servicio devolvió la misma respuesta que la lógica analítica que lo alimentó.
''')]

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

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] S5 v3: {len(cells)} celdas; hilo S4→S5→S6, recuperación y cierre saneados.")


if __name__ == "__main__":
    main()
