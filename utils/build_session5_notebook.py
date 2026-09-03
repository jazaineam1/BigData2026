#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye/actualiza de forma idempotente la sesión 5.

La sesión 5 nació antes de tener generador propio. Este constructor convierte el
notebook publicado en una fuente reproducible de cambios: aplica únicamente
transformaciones identificadas por marcadores, conserva el contenido validado y
reescribe JSON con json.dump para impedir errores de escaping.

Uso:
    python utils/build_session5_notebook.py
    python utils/validate_session5_notebook.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"


def source(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def code(text: str, *, hidden: bool = False, title: str | None = None) -> dict:
    metadata = {}
    body = text.strip()
    if hidden:
        metadata = {
            "tags": ["hide-input"],
            "jupyter": {"source_hidden": True},
            "cellView": "form",
            "colab": {"formView": "both"},
        }
        if title and not body.startswith("#@title"):
            body = f'#@title {title} {{ display-mode: "form" }}\n' + body
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": metadata,
        "outputs": [],
        "source": body,
    }


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in source(cell):
            return i
    raise RuntimeError(f"No se encontró el marcador: {needle!r}")


def insert_once(cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool = True) -> None:
    if any(marker in source(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def main() -> None:
    data = json.loads(NB.read_text(encoding="utf-8"))
    cells = data["cells"]

    # 1) Tutorial Atlas exclusivo de S5: no repetir carga, edición ni el Colab de S4.
    for cell in cells:
        s = source(cell)
        if "atlas-laboratorio-consultas.html" in s:
            cell["source"] = s.replace(
                "atlas-laboratorio-consultas.html",
                "atlas-s05-pipelines-vistas.html",
            )

    i = find(cells, "## 3. Tutorial visual 1")
    cells[i]["source"] = """
---
## 3. Tutorial visual 1 — Atlas: solo lo que falta

**HAZ ESTO AHORA.** Abre el tutorial embebido y trabaja en tu pestaña de Atlas.

No repite registro, clúster, carga ni edición de documentos. Empieza desde el estado real de la clase:
`compras_claras` ya contiene `noticias` y `entidades_noticias`.

Lo que debe quedar al regresar al **mismo** cuaderno S5:

- `resumen-secciones-v1` ejecutado y guardado;
- `clasificar-menciones-v1` ejecutado y guardado;
- vista **`menciones_clasificadas`** creada;
- control `6 alta + 25 media + 111 baja = 142`.

**MÁS ADELANTE.** `clasificar-noticias-v1` queda como ampliación. No es requisito de la bandeja de Laura.
""".strip()

    # 2) Microdecisión antes de ver la PK correcta.
    insert_once(
        cells,
        "### La llave se lee en dos partes",
        "Ejercicio",
        [
            md("""
### Ejercicio — Elige antes de mirar la respuesta

La consulta profesional es:

> **Para un corte y un departamento, devolver primero los procesos de mayor valor.**

¿Cuál diseño permite localizar directamente el grupo que Laura conoce al consultar?

- **A.** `PRIMARY KEY (id_proceso)`
- **B.** `PRIMARY KEY ((corte, departamento), valor_base, id_proceso)`
- **C.** `PRIMARY KEY ((entidad), id_proceso)`

No es una pregunta calificable. La decisión importa más que acertar de memoria: elige una opción y explica en una frase por qué descartas otra.
"""),
            code("""
eleccion_pk = input("Tu elección (A, B o C): ").strip().upper()
razon_descartada = input("Descarta una alternativa en una frase: ").strip()

if eleccion_pk == "B":
    print("Bien: la consulta conoce corte + departamento y puede localizar esa partición.")
elif eleccion_pk in {"A", "C"}:
    print("Revisa el patrón de acceso: Laura conoce corte + departamento, no un id ni necesariamente una entidad.")
else:
    print("Escribe A, B o C. Luego vuelve a leer la pregunta profesional.")

print("Alternativa descartada:", razon_descartada or "PENDIENTE")
"""),
        ],
        after=False,
    )

    # 3) Hoja mínima de sintaxis CQL antes del tutorial de interfaz.
    insert_once(
        cells,
        "## 8. Tutorial visual 2",
        "Chuleta CQL",
        [md("""
### Chuleta CQL — cinco comandos, una sola historia

| Comando | Para qué sirve hoy | Qué debes observar | Error frecuente |
|---|---|---|---|
| `USE compras_claras;` | trabajar en el keyspace creado en Astra | la consola cambia de contexto | intentar `CREATE KEYSPACE` en Astra |
| `CREATE TABLE` | definir la tabla para la consulta objetivo | la `PRIMARY KEY` nace del patrón de acceso | diseñar por columnas “importantes” |
| `INSERT INTO` | escribir una fila | columnas y valores corresponden | pensar que es una carga analítica masiva |
| `SELECT ... WHERE` | leer una partición | `WHERE` conoce `corte + departamento` | filtrar cualquier columna porque existe |
| `UPDATE` / `DELETE` | cambiar o borrar una fila identificada | se usa la clave necesaria para identificarla | olvidar parte de la clave |

**PARA LLEVAR.** CQL se parece visualmente a SQL; Cassandra no hereda por eso el mismo modelo de consultas ad hoc.
""")],
        after=False,
    )

    # 4) Recuperación autónoma: el receso no debe obligar a rehacer Atlas.
    insert_once(
        cells,
        "## 8. Tutorial visual 2",
        "Recuperación",
        [
            md("""
### Recuperación — si Colab reinició durante el receso

La siguiente celda es segura de ejecutar siempre. Si `candidatos` sigue en memoria, no hace nada.
Si el runtime se perdió, reconstruye la bandeja desde los archivos versionados y vuelve a comprobar
`142`, `111/25/6`, `1.000 → 163 → 77` y `0/77`.

**OJO.** Este respaldo recupera el trabajo analítico; no reemplaza la evidencia de haber creado la vista real en Atlas.
"""),
            code("""
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
    vista_real = False

    secop = pd.read_csv(
        f"{RAW}/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv",
        low_memory=False,
    )
    entidades_en_prensa = {m["entidad"] for m in menciones}
    paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]
    paso2 = paso1[
        paso1["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)
    ]
    respuestas = pd.to_numeric(paso2["respuestas_al_procedimiento"], errors="coerce")
    candidatos = paso2[respuestas.eq(0)].sort_values(
        ["precio_base", "id_del_proceso"], ascending=[False, True]
    ).reset_index(drop=True)

    with urllib.request.urlopen(f"{RAW}/Datos/noticias_contratacion_2026.json") as r:
        noticias = json.loads(r.read().decode("utf-8"))
    texto_prensa = " ".join(
        f'{n.get("titulo") or ""} {n.get("subtitulo") or ""}' for n in noticias
    ).casefold()
    referencias = candidatos["referencia_del_proceso"].fillna("").astype(str).str.strip()
    con_referencia = sum(bool(x) and len(x) >= 6 and x.casefold() in texto_prensa for x in referencias)

    assert len(menciones) == 142
    assert dict(niveles) == {"baja": 111, "media": 25, "alta": 6}
    assert len(secop) == 1000
    assert len(paso1) == 163
    assert len(candidatos) == 77
    assert con_referencia == 0
    print("Runtime recuperado: 142 entidades · 1.000 → 163 → 77 · 0/77.")
else:
    print("La bandeja sigue en memoria:", len(candidatos), "candidatos. No fue necesario reconstruirla.")
""", hidden=True, title="Recuperar la bandeja si Colab reinició"),
        ],
        after=False,
    )

    # 5) Robustecer la comparación de referencias contra mayúsculas/minúsculas.
    for cell in cells:
        s = source(cell)
        if "def citado_literalmente" in s and ".casefold()" not in s:
            s = s.replace(
                'texto_prensa = " ".join(\n    f\'{n.get("titulo") or ""} {n.get("subtitulo") or ""}\'\n    for n in noticias\n)',
                'texto_prensa = " ".join(\n    f\'{n.get("titulo") or ""} {n.get("subtitulo") or ""}\'\n    for n in noticias\n).casefold()',
            )
            s = s.replace(
                'return bool(referencia) and len(referencia) >= 6 and referencia in texto_prensa',
                'return bool(referencia) and len(referencia) >= 6 and referencia.casefold() in texto_prensa',
            )
            cell["source"] = s

    # 6) Diagnóstico de conexión justo antes del SCB/token.
    insert_once(
        cells,
        "Sube el Secure Connect Bundle",
        "Diagnóstico",
        [md("""
### Diagnóstico — si algo falla, identifica primero el síntoma

| Ves | Qué suele significar | Qué haces |
|---|---|---|
| base no está `Active` | aún está provisionando | espera/recarga; no crees otra |
| no aparece `token@cqlsh>` | CQL Console aún no conectó | espera o vuelve a abrir la consola |
| `Unauthorized` | token o permisos | genera/verifica el application token |
| SCB no conecta | bundle de otra base/región o ZIP alterado | descarga de nuevo desde **esta** base |
| consulta por `entidad` falla | **no es instalación** | revisa la clave de partición |

Antes del código recuerda cuatro objetos: **SCB = conexión**, **token = autenticación**, `"token"` = usuario literal del driver, **Cluster/Session = cliente Python**.
""")],
        after=False,
    )

    # 7) Resultado propio: adaptar la consulta a otro departamento.
    insert_once(
        cells,
        'print("Top 5 —", bogota)',
        "Evidencia individual",
        [
            md("""
### Evidencia individual — ahora cambia una decisión

No repitas Bogotá. Mira los departamentos que realmente aparecen en **tu** bandeja, elige uno y ejecuta la misma consulta.
El resultado se guardará para tu hito.
"""),
            code("""
departamentos_disponibles = sorted(candidatos["departamento_entidad"].dropna().astype(str).unique())
print("Departamentos disponibles en tu bandeja:")
for d in departamentos_disponibles:
    if d != bogota:
        print(" -", d)

departamento_elegido = input("Escribe un departamento distinto de Bogotá exactamente como aparece arriba: ").strip()
if not departamento_elegido or departamento_elegido == bogota:
    raise ValueError("Elige un departamento distinto de Bogotá de la lista mostrada.")
if departamento_elegido not in departamentos_disponibles:
    raise ValueError("Ese texto no coincide con un departamento de tu bandeja. Cópialo exactamente.")

top5_propio = list(session.execute(consulta, (CORTE_CLASE, departamento_elegido)))
print("Top 5 propio —", departamento_elegido, "· filas:", len(top5_propio))
for f in top5_propio:
    print(f.id_proceso, "|", f.entidad, "| $", f"{f.valor_base:,}", "|", f.estado_revision)

if not top5_propio:
    print("Cero filas también es un resultado: registra qué consulta hiciste y qué aprendiste.")
"""),
        ],
        after=True,
    )

    # 8) El hito incorpora evidencia individual.
    i = find(cells, "# Hito S05 — De la priorización al servicio")
    s = source(cells[i])
    if "departamento_hito" not in s:
        s = s.replace(
            'primer_id = str(candidatos.iloc[0]["id_del_proceso"])',
            'departamento_hito = globals().get("departamento_elegido", "No ejecutado")\n'
            'top5_hito = globals().get("top5_propio", [])\n'
            'primer_id = str(candidatos.iloc[0]["id_del_proceso"])',
        )
        s = s.replace(
            "## Decisión\nMongoDB conserva",
            "## Evidencia individual de ejecución\n"
            "- Departamento consultado: {departamento_hito}\n"
            "- Filas devueltas en su top 5: {len(top5_hito)}\n\n"
            "## Decisión\nMongoDB conserva",
        )
        cells[i]["source"] = s

    # 9) Hoja de trucos al final para evitar scrolls.
    insert_once(
        cells,
        "## 12. Hito de la sesión",
        "Hoja de trucos",
        [md("""
### Hoja de trucos — para consultar sin volver veinte celdas

| Necesidad | Recuerda |
|---|---|
| filtrar documentos en Atlas | `Documents` + filtro |
| encadenar transformaciones | `Aggregations` + pipeline |
| conservar la receta | `Save → Save as` |
| publicar resultado consultable | `Save → Create view` |
| localizar datos en Cassandra | primero la **partition key** |
| ordenar dentro de la partición | **clustering columns** |
| consulta de Laura | `WHERE corte = ? AND departamento = ? LIMIT 5` |
| nueva consulta por entidad | probablemente **otra tabla**, no `ALLOW FILTERING` como parche |

**PARA LLEVAR.** MongoDB favorece exploración documental flexible. Cassandra favorece patrones de acceso conocidos y repetitivos.
""")],
        after=False,
    )

    # 10) Cierre explícito de conexiones, sin convertirlo en objetivo central.
    insert_once(
        cells,
        'files.download("s05_priorizacion.csv")',
        "CERRAR CONEXIONES S05",
        [code("""
# Buena práctica: cerrar clientes al terminar la sesión.
try:
    cluster.shutdown()
    print("Conexión Cassandra cerrada.")
except Exception:
    pass

try:
    if "client" in globals():
        client.close()
        print("Conexión MongoDB cerrada.")
except Exception:
    pass
""", hidden=True, title="Cerrar conexiones" )],
        after=True,
    )

    # Reescritura segura del notebook: esta es la protección contra Bad escaped character.
    NB.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))
    print(f"[OK] Sesión 5 construida: {len(cells)} celdas. JSON válido.")


if __name__ == "__main__":
    main()
