from pathlib import Path
import nbformat

ROOT = Path(__file__).resolve().parents[1]
PRES = ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html"
LAB = ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html"
NB = ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb"
README = ROOT / "infraestructura" / "modules" / "05-elasticsearch" / "README.md"
SQL = ROOT / "infraestructura" / "modules" / "05-elasticsearch" / "s07-live-supabase.sql"


def main():
    errors = []
    pres = PRES.read_text(encoding="utf-8")
    lab = LAB.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    sql = SQL.read_text(encoding="utf-8")
    nb = nbformat.read(NB, as_version=4)
    nbformat.validate(nb)
    nb_text = "\n".join(c.source if isinstance(c.source, str) else "".join(c.source) for c in nb.cells)

    slide_count = pres.count("{c:")
    if slide_count != 35:
        errors.append(f"Presentación: se esperaban 35 pantallas; hay {slide_count}.")

    for marker in [
        "MATCH VS TERM",
        "INDEX-TIME VS SEARCH-TIME",
        "BM25 TRABAJADO",
        "CUANDO FALLA",
        "FLUJO A/B",
        "#d1", "#d2", "#d3", "#d4", "#d5", "#d6", "#d7", "#d8",
        "Qué es exactamente un token",
        "start_offset",
        "end_offset",
        "max_token_length",
        'target="bigdata-lab"',
    ]:
        if marker not in pres:
            errors.append(f"Presentación: falta {marker}")

    if "S07 LIVE 1" in pres or "S07 LIVE 2" in pres:
        errors.append("Presentación: no debe tener slides Live separadas; los retos deben integrarse al flujo.")

    for marker in [
        "primer intento",
        "Dominio",
        'target="bigdata-presentation"',
        "mastery",
        "locked_for_ranking",
        "first_attempt",
        "mastery_score",
        "data-question=\"q7\"",
        "id=\"d8\"",
        "mobile-livebar",
        ".on('broadcast'",
        "setInterval",
    ]:
        if marker not in lab:
            errors.append(f"Laboratorio: falta {marker}")

    if lab.count('class="activity"') < 8:
        errors.append("Laboratorio: se esperaban al menos 8 actividades.")
    if "data-fallback" in lab:
        errors.append("Laboratorio: no debe exponer respuestas correctas en data-fallback.")

    for marker in [
        "primer intento",
        "mastery score",
        "s07_live_submit",
        "first_correct",
        "mastered",
        "s07_live_leaderboard",
        "s07_live_activity_stats",
    ]:
        if marker.lower() not in (readme + sql).lower():
            errors.append(f"Documentación/SQL: falta {marker}")

    if "```http" in nb_text:
        errors.append("Notebook: no debe usar fences ```http porque Colab vuelve clicables las rutas.")

    for marker in [
        "ELASTIC CONSOLE · NO SE EJECUTA EN COLAB",
        "Glosario operativo con ejemplos mínimos",
        "¿Cuánto mide un token?",
        "tokens[]",
        "start_offset",
        "match` vs `term",
        "Qué queremos hacer",
        "Evidencia esperada",
        "Precision@5",
        "_rank_eval",
        "s07_config_busqueda.json",
        "Console antes de Python",
        "bulk",
    ]:
        if marker not in nb_text:
            errors.append(f"Notebook: falta {marker}")

    if len(nb.cells) > 70:
        errors.append(f"Notebook: demasiadas celdas ({len(nb.cells)}); objetivo <= 70.")
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    if len(code_cells) > 28:
        errors.append(f"Notebook: demasiadas celdas de código ({len(code_cells)}); objetivo <= 28.")

    if errors:
        raise SystemExit("\n".join("[ERROR] " + e for e in errors))
    print(f"[OK] S07 validada: {slide_count} pantallas, {len(nb.cells)} celdas, {len(code_cells)} celdas de código, definición+ejemplo+medición y Live primer intento + dominio.")


if __name__ == "__main__":
    main()
