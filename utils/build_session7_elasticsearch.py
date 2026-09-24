# -*- coding: utf-8 -*-
"""S07 · Elasticsearch Search Lab.

Arquitectura vigente: SOLO DOS RECURSOS visibles para estudiantes.

1. Presentación interactiva:
   Presentaciones/s07-del-vecindario-al-texto.html

   Incluye:
   - explicación conceptual;
   - S07 Live;
   - D1-D8 como diapositivas;
   - laboratorio interactivo de tokenización;
   - acceso a Elastic Console explicado paso a paso;
   - Teacher Wall en el mismo HTML con ?wall=docente.

2. Cuaderno Python:
   Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb

Reglas durables:
- máximo 35 diapositivas;
- ningún término técnico se usa antes de definirlo;
- definición → ejemplo mínimo → observación/medición → error o límite;
- API, método HTTP, POST, ruta, JSON y Console se explican antes de D4;
- BM25 se enseña como scoring lexical integrado en Elasticsearch;
- no instalar rank-bm25 para enseñar BM25;
- tokenizer/token/analyzer se explican con múltiples ejemplos;
- el simulador de tokenización vive en una diapositiva, no en otra página;
- los desafíos D1-D8 viven en diapositivas, no en un laboratorio separado;
- ranking = primer intento; dominio = aprendizaje tras pistas/reintentos;
- respuestas correctas nunca se exponen en HTML;
- Teacher Wall es el mismo archivo de presentación en modo ?wall=docente;
- PIN docente solo se valida en backend; jamás se publica en el repo;
- toda caja clara sobre fondo oscuro debe forzar texto oscuro;
- Console antes de Python;
- Python automatiza la misma API;
- navegación táctil y móvil deben seguir funcionando.

No crear un tercer recurso para S07.

Para QA:

    python utils/validate_session7_elasticsearch.py
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

RESOURCES = [
    ROOT / "Presentaciones" / "s07-del-vecindario-al-texto.html",
    ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb",
]

FORBIDDEN_LEGACY = [
    ROOT / "assets" / "tutoriales" / "s07-laboratorio-guiado.html",
    ROOT / "assets" / "tutoriales" / "s07-tokenizer-lab.html",
    ROOT / "assets" / "tutoriales" / "s07-recursos.html",
]


def main():
    missing = [str(p.relative_to(ROOT)) for p in RESOURCES if not p.exists()]
    if missing:
        raise SystemExit("Faltan recursos S07: " + ", ".join(missing))

    leftover = [str(p.relative_to(ROOT)) for p in FORBIDDEN_LEGACY if p.exists()]
    if leftover:
        raise SystemExit("S07 volvió a tener recursos externos prohibidos: " + ", ".join(leftover))

    print("[OK] S07 usa exactamente dos recursos visibles:")
    for p in RESOURCES:
        print(" -", p.relative_to(ROOT))
    print("Preguntas, Tokenizer Lab y Teacher Wall están embebidos en la presentación.")
    print("Ejecuta utils/validate_session7_elasticsearch.py para QA completo.")


if __name__ == "__main__":
    main()
