"""Inserta el recorrido formativo sin cambiar el orden ni código del cuaderno."""
from pathlib import Path
import html
import json
import re
ROOT = Path(__file__).resolve().parents[1]
BEGIN = "<!-- PEDAGOGIA-RUTA-v1 -->"
END = "<!-- /PEDAGOGIA-RUTA-v1 -->"

def bloque(r):
    e = lambda value: html.escape(str(value))
    return "\n".join([
        BEGIN,
        "**Ruta esencial de aprendizaje · cuatro estaciones.** Lee las estaciones antes de ejecutar; amplía únicamente cuando hayas obtenido la evidencia.",
        "<details><summary>Ver recorrido, comprobaciones y experimento formativo</summary>",
        "<ol>",
        *["<li><strong>"+e(s["title"])+":</strong> "+e(s["action"])+" <em>Evidencia:</em> "+e(s["evidence"])+"</li>" for s in r["steps"]],
        "</ol>",
        "<p><strong>Experimento complementario:</strong> copia este código en una celda nueva cuando corresponda. No se ejecuta automáticamente y no sustituye el laboratorio original.</p>",
        "<pre><code>"+e(r["code"])+"</code></pre>",
        "<p><strong>Cómo se lee:</strong> "+e(r["interpret"])+"</p>",
        "<p><strong>Modifica:</strong> "+e(r["challenge"])+"</p>",
        "<p><strong>Qué no permite concluir:</strong> "+e(r["limit"])+"</p>",
        "</details>",
        END
    ])

def integrar_ruta(cells, session):
    config = json.loads((ROOT / "assets/pedagogia/rutas.json").read_text(encoding="utf-8"))
    r = next(x for x in config["routes"] if x["id"] == session)
    for c in cells:
        if c["cell_type"] != "markdown":
            continue
        source = c["source"]
        texto = source if isinstance(source, str) else "".join(source)
        if not re.search(r"^# ", texto, flags=re.M):
            continue
        if BEGIN in texto:
            texto = texto.split("\n\n"+BEGIN, 1)[0]
        nuevo = texto.rstrip("\n") + "\n\n" + bloque(r)
        if isinstance(source, str):
            c["source"] = nuevo
        else:
            partes = nuevo.split("\n")
            c["source"] = [l+"\n" for l in partes[:-1]] + [partes[-1]]
        return cells
    raise ValueError("Sin encabezado Markdown para S"+session)
