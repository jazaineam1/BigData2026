from pathlib import Path
import json, re, nbformat
ROOT=Path(__file__).resolve().parents[1]
NB=ROOT/"Cuadernos"/"7_Elasticsearch_BM25_Compras_Claras.ipynb"
PRES=ROOT/"Presentaciones"/"s07-del-vecindario-al-texto.html"
CHECK=ROOT/"assets"/"tutoriales"/"s07-laboratorio-guiado.html"
DATA=ROOT/"Datos"/"s07_corpus_respaldo.jsonl"
def main():
    errors=[]
    nb=nbformat.read(NB,as_version=4); nbformat.validate(nb)
    text="\n".join(c.source if isinstance(c.source,str) else "".join(c.source) for c in nb.cells)
    for item in ["Rúbrica de la práctica S07","índice invertido","BM25","multi_match","s07_resultados_busqueda.csv","hito_s07_relevancia.md","relevancia textual no demuestra irregularidad"]:
        if item not in text: errors.append("Falta: "+item)
    if re.search(r"\b\d{1,3}\s*min(?:uto)?s?\b",text,re.I): errors.append("El notebook contiene tiempos.")
    for p in [PRES,CHECK,DATA]:
        if not p.exists() or p.stat().st_size<500: errors.append("Falta recurso: "+str(p))
    rows=[json.loads(x) for x in DATA.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(rows)<8: errors.append("Corpus de respaldo insuficiente.")
    if errors: raise SystemExit("\n".join("[ERROR] "+e for e in errors))
    print(f"[OK] S07 validada: {len(nb.cells)} celdas.")
if __name__=="__main__": main()
