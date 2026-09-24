from pathlib import Path
import re
import nbformat

ROOT=Path(__file__).resolve().parents[1]
NB=ROOT/"Cuadernos"/"7_Reto_Elasticsearch_Noticias.ipynb"

def main():
    nb=nbformat.read(NB,as_version=4)
    nbformat.validate(nb)
    text="\n".join(c.source if isinstance(c.source,str) else "".join(c.source) for c in nb.cells)
    required=[
        "noticias_eltiempo_2026-08.json",
        "Documentos indexados:",
        "titulo^4",
        "Precision@5",
        "126",
        "s07_reto_noticias_resultados.csv",
        "s07_reto_noticias_config.json",
        "s07_reto_noticias.md"
    ]
    missing=[x for x in required if x not in text]
    if missing:
        raise SystemExit("Faltan: "+", ".join(missing))
    if re.search(r"\b\d{1,3}\s*min(?:uto)?s?\b",text,re.I):
        raise SystemExit("El notebook público contiene tiempos.")
    print(f"[OK] Reto S07 noticias validado: {len(nb.cells)} celdas")

if __name__=="__main__":
    main()
