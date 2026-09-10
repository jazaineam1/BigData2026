#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida la versión alterna aprender-haciendo de S6, sin usar credenciales de Aura."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.notebook_checks import check_question_widget_renders

NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional_AprenderHaciendo.ipynb"
DATA = ROOT / "Datos" / "s06_contexto_relacional.csv"
MANIFEST = ROOT / "Datos" / "s06_contexto_relacional_manifest.json"
TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
GEN = ROOT / "utils" / "build_session6_notebook_aprender_haciendo.py"


def src(cell):
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def main():
    errors = []
    for path in (NB, DATA, MANIFEST, TUTORIAL, GEN):
        if not path.is_file():
            errors.append(f"Falta {path.relative_to(ROOT)}")
    if errors:
        raise SystemExit("\n".join(errors))

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if not manifest.get("ancla_pedagogica", {}).get("id_proceso"):
        errors.append("Falta ancla pedagógica en el manifest")
    if manifest.get("mediana_maximo_conectadas_candidatas", 0) <= 0:
        errors.append("Falta la mediana de referencia de H2-R")

    nb = json.loads(NB.read_text(encoding="utf-8"))
    if nb.get("nbformat") != 4:
        errors.append("nbformat debe ser 4")
    cells = nb.get("cells", [])
    text = "\n".join(src(c) for c in cells)
    if len(cells) < 40:
        errors.append(f"S6-ALT tiene pocas celdas: {len(cells)}")
    if any(not src(c).strip() for c in cells):
        errors.append("S6-ALT contiene celdas vacías")

    # Diferencias deliberadas de esta versión respecto a la original: sin
    # celdas de predicción libre con input(), y sin pedir un archivo de S5
    # que un estudiante que la use de forma independiente no tiene.
    if "tu_prediccion" in text:
        errors.append("S6-ALT todavía tiene celdas de predicción libre con input() (prohibidas por feedback directo)")
    if "Ruta de s05_ancla_s06.json" in text or "sube tu archivo" in text.lower():
        errors.append("S6-ALT no debe pedir un archivo de S5 que el estudiante no tiene")

    caja_ascii = set("─│└┘┌┐")
    if any(ch in text for ch in caja_ascii):
        errors.append("S6-ALT todavía tiene diagramas dibujados con caracteres ASCII; deben ser SVG reales embebidos")
    if text.count("data:image/svg+xml;base64") < 4:
        errors.append("Faltan diagramas SVG embebidos en S6-ALT (se esperan al menos 4)")
    if "{svg(" in text:
        errors.append("Quedó un llamado a svg() sin interpolar como texto literal — revisa que la celda use md(f'''...''')")

    src_generador = GEN.read_text(encoding="utf-8")
    # INTERACTIVITY se importa desde build_session6_notebook.py; se prueba ahí,
    # pero confirmamos aquí que este generador la sigue usando sin copiarla.
    if "from utils.build_session6_notebook import" not in src_generador or "INTERACTIVITY" not in src_generador:
        errors.append("S6-ALT debería reutilizar INTERACTIVITY del generador original, no duplicarla")
    else:
        original_src = (ROOT / "utils" / "build_session6_notebook.py").read_text(encoding="utf-8")
        match = re.search(r"INTERACTIVITY = r'''(.*?)'''", original_src, re.S)
        if match:
            errors.extend(check_question_widget_renders(match.group(1)))

    required = [
        "Laura ya sabe qué proceso revisar primero",
        "H2-R",
        "EJERCICIO S06-PATRON",
        'RELACION_PROCESO_PROVEEDOR = "____"',
        "EJERCICIO — identifica las tres piezas",
        "ADJUDICADO_A",
        "Contrato de resultado: primero pandas",
        "esperado_pd",
        "RECUPERACIÓN S06",
        "pandas == Neo4j",
        "verify_connectivity",
        "CREATE CONSTRAINT entidad_nit IF NOT EXISTS",
        "UNWIND $filas AS fila",
        "MERGE (e:Entidad",
        "S06-DEMO",
        "conexión más fuerte que la mediana",
        "conexión igual o menor que la mediana",
        "no evaluable con esta ancla",
        "mediana_maximo_conectadas_candidatas",
        "desenlace_h2r_neo",
        "desenlace_h2r_pd",
        "### Función usada: `UNWIND`",
        "MATCH (e:Entidad) RETURN",
        "Interpretación de tu vecindario",
        "alternativa_modelo",
        "razon_alternativa",
        "hito_s06_ficha_relacional.md",
        "s06_contexto_procesos.jsonl",
        "Completo | Parcial | Sin evidencia",
        "Elasticsearch/BM25",
        "¿Dónde se usa esto en la vida real?",
    ]
    for item in required:
        if item not in text:
            errors.append(f"Falta elemento S6-ALT: {item!r}")

    for label in ["**Cómo se lee.**", "**Qué nos dice.**", "**Qué NO permite concluir todavía.**", "**Error frecuente.**"]:
        if text.count(label) < 4:
            errors.append(f"El rótulo {label} aparece menos de cuatro veces")

    if re.search(r"\|\s*Tiempo\s*\|", text, re.I) or "Agenda de 180 minutos" in text:
        errors.append("Los tiempos docentes no deben vivir en el notebook")

    nums = []
    for c in cells:
        s = src(c)
        m = re.search(r'pregunta_codificada\("([A-Za-z0-9+/=]+)"\)', s)
        if m:
            import base64
            payload = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))
            nums.append(payload["numero"])
    if nums != sorted(set(nums)) or len(nums) != len(set(nums)):
        errors.append(f"Las autoevaluaciones tienen números duplicados o desordenados: {nums}")
    if len(nums) < 5:
        errors.append(f"S6-ALT debería tener al menos 5 autoevaluaciones, tiene {len(nums)}")

    secret_patterns = [
        r"neo4j\+s://[A-Za-z0-9.-]+\.databases\.neo4j\.io",
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        r"github_pat_[A-Za-z0-9_]{20,}",
    ]
    for pattern in secret_patterns:
        if re.search(pattern, text):
            errors.append("Posible secreto o endpoint personal publicado")

    if errors:
        print("Validación S6-ALT fallida:")
        for e in errors:
            print("[ERROR]", e)
        raise SystemExit(1)

    print(f"[OK] S6-ALT válida: {len(cells)} celdas")
    print("[OK] Sin celdas de predicción libre, sin pedir archivo de S5, sin diagramas ASCII")
    print("[OK] Widget de preguntas probado funcionalmente: no filtra JS al texto visible")
    print(f"[OK] {len(nums)} autoevaluaciones numeradas correctamente: {nums}")


if __name__ == "__main__":
    main()
