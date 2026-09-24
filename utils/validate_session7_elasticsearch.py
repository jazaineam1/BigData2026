from pathlib import Path
import json
import re
import nbformat

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb"
PRES = ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html"
ROUTE = ROOT / "assets" / "tutoriales" / "s07-recursos.html"
DEPLOY = ROOT / "assets" / "tutoriales" / "s07-despliegue-elasticsearch.html"
CHECK = ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html"
INDEX = ROOT / "index.html"

def main():
    errors = []

    nb = nbformat.read(NB, as_version=4)
    nbformat.validate(nb)
    text = "\n".join(c.source if isinstance(c.source, str) else "".join(c.source) for c in nb.cells)

    required_nb = [
        "s06_contexto_relacional.csv",
        "2.109 filas fuente",
        "1.994 procesos",
        "client.info()",
        "client.indices.analyze",
        "mappings=mappings",
        "elasticsearch.helpers",
        "bulk(",
        "client.count",
        "multi_match",
        "nombre_proceso^3",
        "highlight",
        "s07_resultados_busqueda.csv",
        "s07_config_busqueda.json",
        "hito_s07_relevancia.md",
        "Precision@5",
        "relevancia textual",
        "s07_reto_sala_redaccion.json",
        "987 noticias",
    ]
    for marker in required_nb:
        if marker not in text:
            errors.append("Notebook: falta " + marker)

    if re.search(r"\b\d{1,3}\s*min(?:uto)?s?\b", text, re.I):
        errors.append("Notebook: contiene tiempos minuto a minuto.")

    pres = PRES.read_text(encoding="utf-8")
    for color in ["#142153", "#0B8689", "#E5E5E3", "#ACAA00"]:
        if color not in pres:
            errors.append("Presentación: falta color institucional UCentral " + color)
    slide_count = pres.count("{c:'")
    if slide_count < 49:
        errors.append(f"Presentación: solo {slide_count} slides; se esperan al menos 49.")
    for marker in [
        "Construye un buscador con Elasticsearch",
        "1.994 procesos únicos",
        "_ANALYZE",
        "BULK",
        "CHECKPOINT 1",
        "CHECKPOINT 2",
        "PRECISION@5",
        "touchstart",
        "requestFullscreen",
        "Sala de redacción",
        "#122253",
        "#0B8689",
        "#E95D0F",
    ]:
        if marker not in pres:
            errors.append("Presentación: falta " + marker)
    if "Diagnóstico del grupo" in pres:
        errors.append("Presentación: no debe exponer el diagnóstico del grupo.")

    route = ROUTE.read_text(encoding="utf-8")
    if "No abras seis recursos" in route or "Este es el único punto de entrada" in route:
        errors.append("Ruta: contiene meta-instrucciones del proceso de diseño en lugar del producto.")
    for marker in [
        "Ruta única",
        "Entiende",
        "Experimenta",
        "Despliega",
        "Indexar",
        "Buscar",
        "Evaluar",
        "7_Elasticsearch_BM25_Compras_Claras.ipynb",
        "Precision@5",
        "Transferir",
    ]:
        if marker.lower() not in route.lower():
            errors.append("Ruta: falta " + marker)

    deploy = DEPLOY.read_text(encoding="utf-8")
    for marker in [
        "Elasticsearch Serverless",
        "Project URL",
        "API key",
        "23-sep-2026",
        "Documentos indexados: 1994",
        "Conteo Elasticsearch: 1994",
    ]:
        if marker not in deploy:
            errors.append("Despliegue: falta " + marker)

    checklist = CHECK.read_text(encoding="utf-8")
    if checklist.count('class="step"') < 21:
        errors.append("Checklist: faltan pasos.")
    for marker in ["Conexión verificada", "Tokens Elastic", "Errores bulk: 0", "Precision@5", "s07_config_busqueda.json", "s07_reto_sala_redaccion.json"]:
        if marker not in checklist:
            errors.append("Checklist: falta evidencia " + marker)

    index_text = INDEX.read_text(encoding="utf-8")
    if 'href="assets/tutoriales/s07-recursos.html"' not in index_text:
        errors.append("Index: S07 no apunta a la ruta única.")

    if errors:
        raise SystemExit("\n".join("[ERROR] " + e for e in errors))

    print(f"[OK] S07 integral validada: {len(nb.cells)} celdas, {slide_count} diapositivas, ruta, despliegue y checklist.")

if __name__ == "__main__":
    main()
