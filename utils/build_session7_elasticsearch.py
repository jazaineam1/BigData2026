# -*- coding: utf-8 -*-
"""S07 · Elasticsearch Search Lab.

La sesión ya no se regenera desde este archivo porque el rediseño quedó
organizado como tres recursos docentes versionados directamente:

1. Presentación principal:
   Presentaciones/s07-del-vecindario-al-texto.html

2. Cuaderno ejecutable:
   Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb

3. Laboratorio activo / guía de clase:
   assets/tutoriales/s07-laboratorio-guiado.html

Principios vigentes del rediseño:
- máximo 35 pantallas en la presentación;
- explicación conceptual completa en la presentación;
- toda definición núcleo debe incluir: qué es, ejemplo mínimo, cómo observarla/medirla y error o límite;
- tokenización explicada explícitamente: token, conteo, posición, offsets y tamaño dependiente del tokenizer;
- presentación, laboratorio y Colab usan pestañas reutilizables distintas para no destruir el contexto de clase;
- Console antes de Python;
- Python como automatización de la API;
- cuaderno con explicación de código, evidencia, salidas esperadas y errores;
- laboratorio como tablero de clase, no como cuarta fuente de contenido;
- deep links D1-D8 desde la presentación al desafío exacto;
- ranking por primer intento para evitar autocorrección inflada;
- dominio por reintentos para conservar aprendizaje con feedback, separado del ranking por primer intento;
- no exponer respuestas correctas en data-fallback del HTML;
- ejemplos de industria: e-commerce, empleo, noticias y bases de conocimiento;
- match vs term, index-time/search-time, BM25 trabajado, troubleshooting y P@5;
- Supabase Broadcast como sincronización principal con polling móvil de respaldo;
- bloques Console marcados como NO SE EJECUTA EN COLAB para evitar rutas clicables.

Este script se conserva para documentar la arquitectura y evitar que una
regeneración antigua sobrescriba el notebook vigente. Para QA usa:

    python utils/validate_session7_elasticsearch.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESOURCES = [
    ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html",
    ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb",
    ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html",
]


def main():
    missing = [str(p.relative_to(ROOT)) for p in RESOURCES if not p.exists()]
    if missing:
        raise SystemExit("Faltan recursos S07: " + ", ".join(missing))
    print("[OK] S07 usa tres recursos versionados directamente:")
    for p in RESOURCES:
        print(" -", p.relative_to(ROOT))
    print("Ejecuta utils/validate_session7_elasticsearch.py para validar la sesión.")


if __name__ == "__main__":
    main()
