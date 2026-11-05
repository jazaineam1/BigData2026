#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QA TC2: comprobaciones deterministas offline, rúbrica, notebook y regresiones.
No atribuye a CI conexiones externas, inferencia real E5 ni Colab autenticado.
"""
from __future__ import annotations
import ast,json,re,sys,tempfile,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import tc2_core as c
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
errors=[]
def verify(expr,label):
    if not expr:errors.append(label)
def run():
    nb=json.loads((ROOT/"Cuadernos/Taller_Control_2.ipynb").read_text(encoding="utf-8"))
    cells=nb["cells"];source=["".join(x["source"]) for x in cells]
    verify(nb.get("nbformat")==4 and nb.get("nbformat_minor",0)>=5,"nbformat 4.5")
    verify(len(cells)>=35,"Mínimo 35 celdas de aprendizaje")
    verify(all(x.get("id") for x in cells),"IDs de celdas")
    verify(all(not x.get("outputs") for x in cells if x["cell_type"]=="code"),"Notebook sin salidas preejecutadas")
    verify(sum(x["cell_type"]=="code" for x in cells)>=16,"Celdas ejecutables")
    for index,x in enumerate(cells):
        if x["cell_type"]=="code":
            try:ast.parse("".join(x["source"]))
            except SyntaxError as e:errors.append(f"Celda {index} sintaxis: {e}")
    full="\n".join(source)
    for term in ("PREDICCION_INICIAL","RANK_BM_LITERAL","RANK_SEM_PARAFRASIS","METRICAS_RRF","INSPECCION","AUDIOS","core.validar(","manifest_tc2.json","jzaineam@ucentral.edu.co","No son audios de noticias"):
        verify(term.casefold() in full.casefold(),f"Enunciado/celda debe contener: {term}")
    verify(len(c.RUBRICA)==18 and sum(x[2] for x in c.RUBRICA)==100,"18 controles/100 puntos")
    found=[s for s in source if "CORE_SOURCE = " in s]
    verify(len(found)==1,"Motor embebido una sola vez")
    if found:
        tree=ast.parse(found[0]);assign=next((x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=="CORE_SOURCE" for t in x.targets)),None)
        verify(assign is not None,"Motor embebido legible")
        if assign:
            embedded=ast.literal_eval(assign.value)
            verify(embedded==(ROOT/"utils/tc2_core.py").read_text(encoding="utf-8"),"Motor del notebook es idéntico a utils/tc2_core.py")
    doc=c.corpus_lista(ROOT/"Datos")
    q=c.intenciones(ROOT/"Datos")
    verify(len(doc)==200 and len({d["id_proceso"] for d in doc})==200,"200 procesos de SECOP sin duplicados")
    verify(len(q)==5 and all(len(z["relevantes"])>=5 for z in q),"Cinco intenciones con al menos cinco relevantes")
    ids={d["id_proceso"] for d in doc}
    verify(all(set(z["relevantes"])<=ids for z in q),"Todos los juicios con ID existente")
    verify(all(z["literal"]!=z["parafrasis"] for z in q),"Paráfrasis distintas")
    sample=q[0]
    ranks=c.bm25(doc,sample["literal"],10)
    ranks2=c.bm25(doc,sample["literal"],10)
    verify(ranks==ranks2 and len(ranks)==10,"BM25 determinista")
    verify(ranks==sorted(ranks,key=lambda x:(-x["score"],x["id_proceso"])),"BM25 orden y desempate")
    verify(len(c.tokens("CAMIÓN Aeronaves"))==2,"Unicode y acentos en tokenizer")
    verify(c.medidas([{"id_proceso":str(i)} for i in range(1,6)],["1","2","3","6","7","8"])["precision_at_5"]==0.6,"Precision@5 manual")
    verify(c.medidas([{"id_proceso":str(i)} for i in range(1,6)],["1","2","3","6","7","8"])["recall_at_5"]==0.5,"Recall@5 manual")
    rrf=c.fusion_rrf([{"id_proceso":"A","score":2},{"id_proceso":"B","score":1}],
                    [{"id_proceso":"B","score":8},{"id_proceso":"C","score":7}],60,3)
    verify(rrf[0]["id_proceso"]=="B" and len(rrf)==3,"RRF posiciones, no scores")
    rng=np.random.default_rng(2026);a=rng.normal(size=(len(doc),384)).astype(np.float32);v=rng.normal(size=(384,)).astype(np.float32)
    cs=c.coseno(doc,a,v,5)
    verify(len(cs)==5 and cs==c.coseno(doc,a,v,5),"Coseno reproducible N×384")
    try:c.coseno(doc,a[:4],v,5);errors.append("Dimensión incorrecta de coseno debe fallar")
    except ValueError:pass
    with tempfile.TemporaryDirectory() as td:
        t=Path(td);i=t/"E4/ranking.png"
        c.csv_image(ranks,doc,i);meta=c.inspeccion_imagen(i)
        verify(meta["suma_histograma"]==960*520 and len(meta["histograma"])==16,"Imagen real/histograma 16 bins")
        p=c.perfil_imagen(i,t/"160.png",160,.85)
        verify(p["ancho"]<=160 and c.sha(t/"160.png")==p["sha256"],"Pillow: perfil y SHA")
        small=c.inspeccion_imagen(t/"160.png")
        verify(small["suma_histograma"]==small["ancho"]*small["alto"],"Inspector sin píxel fuera de límites en perfil reducido")
        import soundfile as sf
        x=np.sin(np.linspace(0,2*np.pi*440,16000,endpoint=False)).astype(np.float32)
        w=t/"demo.wav";sf.write(w,x,16000,subtype="PCM_16")
        m512=c.metricas_voz(w,512);m1024=c.metricas_voz(w,1024)
        verify(0.69<m512["rms"]<0.72 and m512["resolucion_hz"]==31.25 and m1024["resolucion_hz"]==15.625,"RMS y resolución FFT")
        manifest=c.validar(t,doc,sample)
        verify(len(manifest["controles"])==18 and manifest["puntaje"]==0,"Evaluador falla cerrado si faltan archivos")
        htmlfile=c.hacer_html(t,doc,ranks,cs,c.fusion_rrf(ranks,cs,60,5),meta,[{"n":1,"source_record_id":"ejemplo","archivo":"demo.wav","medidas":m512}],{"modelo":"BM25"})
        text=htmlfile.read_text(encoding="utf-8")
        verify("MINDS14" in text and "sin vínculo" in text and "<audio" in text,"Explorador separa procedencias")
    # Separa inequívocamente material aprendido de contenido antes del TC1.
    for forbidden in ("Cassandra query-first — 15 puntos","Neo4j / contexto relacional — 15 puntos","Adquisición SECOP — 25 puntos"):
        verify(forbidden not in full,"No repetir TC1: "+forbidden)
    if errors:
        print("TC2 QA: FAIL")
        for e in errors:print(" -",e)
        return 1
    print("TC2 QA OFFLINE: OK · 200 documentos, 5 intenciones, 18 controles / 100, 36 celdas, BM25, RRF, coseno, PNG, FFT, exportación.")
    print("NO VERIFICADO POR ESTA PRUEBA: descarga MINDS14, encoder real E5, Atlas real, Drive/Colab autenticado y GitHub Pages.")
    return 0
if __name__=="__main__":raise SystemExit(run())
