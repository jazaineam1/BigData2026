from pathlib import Path
import json
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb"
PRES = ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html"
LAB = ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html"
ROUTE = ROOT / "assets" / "tutoriales" / "s07-recursos.html"
INDEX = ROOT / "index.html"


def main():
    errors = []

    nb = nbformat.read(NB, as_version=4)
    nbformat.validate(nb)
    nb_text = "\n".join(c.source if isinstance(c.source, str) else "".join(c.source) for c in nb.cells)
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    visible_long = []
    for i, c in enumerate(nb.cells):
        if c.cell_type != "code":
            continue
        hidden = c.metadata.get("cellView") == "form" or c.metadata.get("jupyter", {}).get("source_hidden")
        lines = (c.source if isinstance(c.source, str) else "".join(c.source)).splitlines()
        if (not hidden) and len(lines) > 45:
            visible_long.append((i, len(lines)))

    for marker in [
        "Console antes de Python",
        "Anatomía de una solicitud",
        "client.info()",
        "client.indices.analyze",
        "bulk(",
        "multi_match",
        "nombre_proceso^3",
        "Precision@5",
        "Sala de redacción",
        "987 noticias",
        "Pasaporte de habilidades",
    ]:
        if marker not in nb_text:
            errors.append("Notebook: falta " + marker)
    if len(nb.cells) > 75:
        errors.append(f"Notebook: demasiado largo ({len(nb.cells)} celdas); objetivo <=75.")
    if len(code_cells) > 30:
        errors.append(f"Notebook: demasiadas celdas de código visibles/totales ({len(code_cells)}); objetivo <=30.")
    if visible_long:
        errors.append("Notebook: celdas visibles demasiado largas: " + str(visible_long[:5]))

    pres = PRES.read_text(encoding="utf-8")
    slide_count = pres.count("{c:")
    if not (30 <= slide_count <= 35):
        errors.append(f"Presentación: se esperan 30-35 pantallas; hay {slide_count}.")
    for marker in [
        "Elasticsearch Search Lab",
        "UI, Console y Python",
        "REQUEST / RESPONSE",
        "Console ↔ Python",
        "Index Management / Discover",
        "SALA DE REDACCIÓN",
        "Gemini Notebook",
        "Laboratorio",
        "bigdata-workspace",
        ".dark .note{background:#ffffff",
        "prevBtn.addEventListener",
        "Abrir S07 Live",
    ]:
        if marker not in pres:
            errors.append("Presentación: falta " + marker)
    if "Ruta S07" in pres or "../assets/tutoriales/s07-recursos.html" in pres:
        errors.append("Presentación: todavía enlaza a la ruta antigua.")

    lab = LAB.read_text(encoding="utf-8")
    for marker in [
        "Cómo se dicta la clase",
        "Presentación",
        "Abrir / reutilizar Colab",
        "S07 Live · ranking en tiempo real",
        "s07_live_submit",
        "postgres_changes",
        "id=\"joinLive\"",
        "Exportar resumen JSON",
        "target=\"bigdata-workspace\"",
    ]:
        if marker not in lab:
            errors.append("Laboratorio: falta " + marker)
    if "Repositorio" in lab or "github.com/jazaineam1/BigData2026" in lab.replace("colab.research.google.com/github/jazaineam1/BigData2026", ""):
        errors.append("Laboratorio: no debe mostrar enlace general al repo.")

    route = ROUTE.read_text(encoding="utf-8")
    if "refresh" not in route or "s07-laboratorio-guiado.html" not in route:
        errors.append("Ruta antigua: debe redirigir al laboratorio.")

    idx = INDEX.read_text(encoding="utf-8")
    if "s07-laboratorio-guiado.html" not in idx:
        errors.append("Index: debe enlazar el laboratorio activo.")
    if 'href="assets/tutoriales/s07-recursos.html"' in idx:
        errors.append("Index: S07 todavía usa la ruta antigua en lugar del laboratorio.")
    if '>Repositorio</a>' in idx:
        errors.append("Index: no debe mostrar el botón general Repositorio en la portada.")

    if errors:
        raise SystemExit("\n".join("[ERROR] " + e for e in errors))
    print(f"[OK] S07 validada: {slide_count} pantallas, {len(nb.cells)} celdas, {len(code_cells)} celdas de código, tres recursos visibles.")


if __name__ == "__main__":
    main()
