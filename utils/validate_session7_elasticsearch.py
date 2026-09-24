from pathlib import Path
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]
PRES = ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html"
NB = ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb"
README = ROOT / "infraestructura" / "modules" / "05-elasticsearch" / "README.md"
SQL = ROOT / "infraestructura" / "modules" / "05-elasticsearch" / "s07-live-supabase.sql"

LEGACY = [
    ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html",
    ROOT / "assets" / "tutoriales" / "s07-tokenizer-lab.html",
    ROOT / "assets" / "tutoriales" / "s07-recursos.html",
    ROOT / "assets" / "tutoriales" / "s07-despliegue-elasticsearch.html",
    ROOT / "Cuadernos" / "7B_Despliegue_Elastic_Cloud.ipynb",
]


def main():
    errors = []
    pres = PRES.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    sql = SQL.read_text(encoding="utf-8")
    nb = nbformat.read(NB, as_version=4)
    nbformat.validate(nb)
    nb_text = "\n".join(c.source if isinstance(c.source, str) else "".join(c.source) for c in nb.cells)

    slide_count = pres.count('{"c":')
    if slide_count != 35:
        errors.append(f"Presentación: se esperaban 35 diapositivas; hay {slide_count}.")

    for marker in [
        "Solo usaremos dos recursos",
        "Mapping: el plano de interpretación de los campos",
        "Método HTTP",
        "POST /_analyze",
        "Dev Tools",
        "Console",
        "Tokenizer y token: pruébalos aquí mismo",
        'id=\\"tokText\\"',
        "standard",
        "whitespace",
        "keyword",
        "edge n-gram",
        "Analyzer: tokenizer más filtros",
        "BM25 es el modelo de scoring lexical",
        "No lo instalas aparte",
        "cloud.elastic.co",
        "Create project",
        "Elasticsearch endpoint / Project URL",
        "Create API key",
        "Respuesta esperada",
        "start_offset",
        "Ahora interpreta la respuesta",
        "corpus",
        "S07 Teacher Wall",
        "s07_teacher_create_round",
        "s07_teacher_reset_round",
        "?wall=docente",
        ".dark .card",
        ".dark .note",
        'target=\\"bigdata-workspace\\"',
    ]:
        if marker.lower() not in pres.lower():
            errors.append(f"Presentación: falta {marker}")

    for q in range(8):
        if f'data-question=\\"q{q}\\"' not in pres:
            errors.append(f"Presentación: falta desafío embebido q{q}.")
    if 'data-kind=\\"analyzerread\\"' not in pres:
        errors.append("Presentación: D4 debe evaluar la lectura del retorno de _analyze.")

    for forbidden in [
        "s07-laboratorio-guiado.html",
        "s07-tokenizer-lab.html",
        'target=\\"bigdata-lab\\"',
        "data-fallback=",
    ]:
        if forbidden in pres:
            errors.append(f"Presentación: referencia prohibida {forbidden}")

    for path in LEGACY:
        if path.exists():
            errors.append(f"Arquitectura: recurso S07 externo prohibido todavía existe: {path.relative_to(ROOT)}")

    if "```http" in nb_text:
        errors.append("Notebook: no debe usar fences http porque Colab vuelve clicables las rutas.")

    for marker in [
        "API y Console desde cero",
        "¿Cómo abro Console en Elastic?",
        "POST /_analyze",
        "Glosario operativo con ejemplos mínimos",
        "corpus",
        "BM25 no es un paquete",
        "tokens[]",
        "start_offset",
        "match` vs `term",
        "Precision@5",
        "Console antes de Python",
        "bulk",
        "De Elastic Cloud a Colab",
        "Elasticsearch endpoint",
        "API key",
        "Número de tokens devueltos por Elasticsearch",
    ]:
        if marker.lower() not in nb_text.lower():
            errors.append(f"Notebook: falta {marker}")

    if "BM25Okapi" in nb_text:
        errors.append("Notebook: volvió a usar BM25Okapi; BM25 debe observarse en Elasticsearch.")
    if re.search(r"pip[^\n]*rank-bm25", nb_text, flags=re.I):
        errors.append("Notebook: volvió a instalar rank-bm25.")

    for marker in [
        "s07_teacher_config",
        "s07_teacher_auth",
        "s07_teacher_create_round",
        "s07_teacher_reset_round",
        "s07_teacher_close_round",
        "s07_teacher_reopen_round",
        "pin_hash",
        "s07_live_submit",
    ]:
        if marker not in sql:
            errors.append(f"SQL canónico: falta {marker}")

    if "S07-UCENTRAL-2026" in sql or "S07-UCENTRAL-2026" in pres:
        errors.append("Seguridad: el PIN docente no debe aparecer en SQL ni presentación.")

    for marker in [
        "exactamente dos recursos",
        "Teacher Wall",
        "No crear una tercera",
        "actividades D1–D8",
    ]:
        if marker.lower() not in readme.lower():
            errors.append(f"README: falta regla {marker}")

    if len(nb.cells) > 70:
        errors.append(f"Notebook: demasiadas celdas ({len(nb.cells)}); objetivo <= 70.")
    code_cells = [c for c in nb.cells if c.cell_type == "code"]
    if len(code_cells) > 28:
        errors.append(f"Notebook: demasiadas celdas de código ({len(code_cells)}); objetivo <= 28.")

    if errors:
        raise SystemExit("\n".join("[ERROR] " + e for e in errors))

    print(
        f"[OK] S07 validada: 35 diapositivas, D1-D8 + tokenizer + Teacher Wall embebidos, "
        f"{len(nb.cells)} celdas de notebook y exactamente dos recursos visibles."
    )


if __name__ == "__main__":
    main()
