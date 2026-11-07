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
    verify(len(cells)>=95,"Al menos 95 celdas, profundidad comparable al TC1")
    verify(all(x.get("id") for x in cells),"IDs de celdas")
    verify(all(not x.get("outputs") for x in cells if x["cell_type"]=="code"),"Notebook sin salidas preejecutadas")
    verify(sum(x["cell_type"]=="code" for x in cells)>=38,"Al menos 38 celdas ejecutables")
    verify(sum(x["cell_type"]=="markdown" for x in cells)>=57,"Al menos 57 celdas de explicación")
    for ejercicio in ("frecuencia_documental_equipo","coseno_mini","precision_cinco","rrf_dos_posiciones","luminancia_rgb","rms_manual"):
        verify(any(("def "+ejercicio+"(") in "".join(x["source"]) for x in cells),"COMPLETA debe existir: "+ejercicio)
    for fn in ("ids_desde_texto","palabras_clave_propias"):
        verify(any(("def "+fn+"(") in text for text in source),"Función nueva de OCR/ASR COMPLETA: "+fn)
    verify(len(cells)>=110,"Historia OCR/ASR tan profunda como TC1")
    # El TC1 exige un único hueco en una sola línea y mapa sin relojes.
    funciones=("frecuencia_documental_equipo","coseno_mini","precision_cinco","rrf_dos_posiciones",
               "luminancia_rgb","rms_manual","ids_desde_texto","palabras_clave_propias")
    for fn in funciones:
        candidatas=[q for q in source if q.lstrip().startswith(("# E","#@title")) and
                    "def "+fn+"(" in q and "return ____" in q]
        verify(len(candidatas)==1 and candidatas[0].count("return ____")==1,
               "Una sola línea COMPLETA por ejercicio: "+fn)
    verify("Tiempo orientativo" not in source[2] and "45–60" not in source[2],
           "Mapa de estudiante sin minutos, conforme a AGENTS")
    for etapa in ("E1","E2","E3","E4","E5","E6"):
        seccion=[q for q in source if "### Checkpoint "+etapa in q]
        verify(len(seccion)==1 and all(x in seccion[0] for x in
               ("**Cómo se lee:**","**Qué nos dice:**","**Qué NO permite concluir todavía:**","**Qué error común:**")),
               "Interpretación de cuatro rótulos en checkpoint "+etapa)
    pruebas=(ROOT/"utils/test_tc2_e2e_real.py").read_text(encoding="utf-8")
    verify("SOLUCIONES =" not in pruebas,"No publicar tabla de ocho respuestas listas para pegar")
    verify("audit_media=True" in pruebas and (ROOT/"utils/tc2_media_audit.py").exists(),
           "E2E debe verificar re-inferencia docente independiente")
    verify("puntos_parciales=" in (ROOT/"utils/tc2_core.py").read_text(encoding="utf-8"),
           "Niveles de crédito parcial observables")

    verify(any("core.ejecutar_ocr(" in x for x in source),"El notebook EJECUTA OCR de verdad")
    verify(any("core.ejecutar_asr(" in x for x in source),"El notebook EJECUTA ASR de verdad")
    verify(any("core.consultar_texto(" in x for x in source),"El notebook consulta texto enriquecido")
    for index,x in enumerate(cells):
        if x["cell_type"]=="code":
            try:ast.parse("".join(x["source"]))
            except SyntaxError as e:errors.append(f"Celda {index} sintaxis: {e}")
    full="\n".join(source)
    for term in ("PREDICCION_INICIAL","RANK_BM_LITERAL","RANK_SEM_PARAFRASIS","METRICAS_RRF","INSPECCION","AUDIOS","core.validar(","manifest_tc2.json","GitHub","no son audios"):
        verify(term.casefold() in full.casefold(),f"Enunciado/celda debe contener: {term}")
    verify(len(c.RUBRICA)==24 and sum(x[2] for x in c.RUBRICA)==100,"24 controles/100 puntos")
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
        verify(meta["suma_histograma"]==960*540 and len(meta["histograma"])==16,"Imagen real/histograma 16 bins")
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
        verify(len(manifest["controles"])==24 and manifest["puntaje"]==0,"Evaluador falla cerrado si faltan archivos")
        htmlfile=c.hacer_html(t,doc,ranks,cs,c.fusion_rrf(ranks,cs,60,5),meta,[{"n":1,"source_record_id":"ejemplo","archivo":"demo.wav","medidas":m512}],{"modelo":"BM25"})
        text=htmlfile.read_text(encoding="utf-8")
        verify("MINDS14" in text and "sin vínculo" in text and "<audio" in text,"Explorador separa procedencias")
    verify("15 de noviembre de 2026" in full and "GitHub" in full and "23:59:59" in full,"Fecha y GitHub visibles")
    # Comprobar un ETL real sin inventar asociaciones.
    with tempfile.TemporaryDirectory() as tf:
        t=Path(tf); (t/"E4").mkdir(); (t/"E5/audio").mkdir(parents=True)
        original=c.csv_image(ranks,doc,t/"E4/ranking.png")
        c.perfil_imagen(original,t/"E4/perfil_160.png",160)
        c.perfil_imagen(original,t/"E4/perfil_640.png",640)
        import soundfile as sf
        audios=[]
        for i in range(1,11):
            pcm=t/f"E5/audio/voz_{i:02d}.wav";raw=t/f"E5/audio/voz_{i:02d}_fuente.wav"
            sf.write(pcm,np.sin(np.linspace(0,2*np.pi*440,16000)),16000)
            raw.write_bytes(pcm.read_bytes())
            audios.append({"n":i,"archivo":pcm.name,"original":raw.name,"source_record_id":"prueba-"+str(i),"sha256":c.sha(pcm),"medidas":c.metricas_voz(pcm)})
        # Este bloque comprueba sólo el contrato de catálogo; NO simula una
        # ejecución real de OCR ni Whisper. Eso lo prueba E2E con modelos descargados.
        ocr={"schema":"tc2-ocr-v1","source_kind":"SECOP_ranking_generado",
             "motor":"tesseract","idioma":"spa",
             "ids_esperados":[v["id_proceso"] for v in ranks[:5]],"resultados":[]}
        for nombre in ("ranking.png","perfil_160.png","perfil_640.png"):
            p=t/"E4"/nombre
            ocr["resultados"].append({"archivo":"E4/"+nombre,"sha256_imagen":c.sha(p),
                "texto_ocr":"TOP 5 RESULTADOS SECOP CO1.REQ.12345678",
                "ids_secop_verificados":[],"cobertura_ids":0})
        c.escribir(t/"E4/ocr.json",ocr)
        asr={"schema":"tc2-asr-v1","engine":"faster-whisper","modelo":"tiny",
             "source_kind":"MINDS14_es_ES","audios":[]}
        for i,v in enumerate(audios,1):
            asr["audios"].append({"n":i,"source_record_id":v["source_record_id"],
             "sha256_audio":v["sha256"],"transcripcion_asr":"pago de cuenta",
             "transcripcion_referencia":"pago de cuenta","wer":0.0,
             "informacion":c.extraer_info_voz("pago de cuenta")})
        c.escribir(t/"E5/asr.json",asr)
        c.escribir(t/"E5/audios.json",{"audios":audios})
        items=c.construir_catalogo(t,sample)
        meta=c.guardar_catalogo(t,items)
        verify(meta["cantidad"]==13 and len(c.reabrir_catalogo(t))==13,"Catálogo real JSONL+Parquet")
        verify(len(c.consultar_catalogo(items,"audio"))==10 and len(c.consultar_catalogo(items,"image"))==3,"Consulta por tipo")
        verify(len(c.consultar_texto(items,"pago"))==10,"Consulta textual de enriquecimiento")
        verify(abs(c.wer_palabras("pago de cuenta","pago la cuenta")-1/3)<1e-6,"WER distancia por sustitución")
        verify(c.extraer_ids_secop("CO1.REQ.12345678")==["CO1.REQ.12345678"],"Regex SECOP cotejable")
        initial=c.sha(t/"E6/catalogo.jsonl")
        c.guardar_catalogo(t,c.construir_catalogo(t,sample))
        verify(initial==c.sha(t/"E6/catalogo.jsonl"),"Idempotencia de catálogo")
        fault=c.verificar_fallo(t)
        verify(fault["detected"] and fault["restored"] and fault["source_intact"],"Corrupción y restauración de derivado")
    verify("15 de noviembre de 2026" in full and "E6/catalogo.parquet" in full and "GitHub" in full,"Fecha, catálogo y GitHub visibles")
    # Validar que la página institucional realmente publique S12 y ofrezca dos recursos.
    portal=json.loads((ROOT/"lms/data/course.json").read_text(encoding="utf-8"))
    s12=next((x for x in portal["sessions"] if x["n"]==12),None)
    verify(s12 is not None and s12.get("status")=="visible" and
           s12.get("assessment",{}).get("weight_percent")==20 and
           s12.get("assessment",{}).get("due_at")=="2026-11-15T23:59:59-05:00" and
           "Taller_Control_2.ipynb" in s12.get("entry",{}).get("url",""),
           "S12 debe ser visible con peso 20%, fecha y enlace.")
    portada=(ROOT/"index.html").read_text(encoding="utf-8")
    guia=(ROOT/"assets/tutoriales/tc2-paso-a-paso.html").read_text(encoding="utf-8")
    verify("Taller_Control_2.ipynb" in portada and 'data-n="12"' in portada and
           "tc2-paso-a-paso.html" in portada and
           "lms/session-12.html" not in portada,"Portada ofrece dos recursos sin página especial S12.")
    verify(not (ROOT/"lms/session-12.html").exists(),"LMS usa el módulo universal, sin página S12 específica.")
    verify(guia.count('type="checkbox"')==41 and "GitHub" in guia and
           "15 de noviembre de 2026" in guia and guia.count("<details>")>=8 and
           "NameError" in guia and "Whisper" in guia and "Tesseract" in guia,
           "Guía completa con 41 comprobaciones, ejemplos y rescates.")
    # Separa inequívocamente material aprendido de contenido antes del TC1.
    for forbidden in ("Cassandra query-first — 15 puntos","Neo4j / contexto relacional — 15 puntos","Adquisición SECOP — 25 puntos"):
        verify(forbidden not in full,"No repetir TC1: "+forbidden)
    if errors:
        print("TC2 QA: FAIL")
        for e in errors:print(" -",e)
        return 1
    print("TC2 QA OFFLINE: OK · 200 documentos, 5 intenciones, 24 controles / 100, 111 celdas, OCR+ASR, BM25, E5, RRF y ETL.")
    print("NO VERIFICADO POR ESTA PRUEBA: descarga MINDS14, encoder real E5, Atlas real, Drive/Colab autenticado y GitHub Pages.")
    return 0
if __name__=="__main__":raise SystemExit(run())
