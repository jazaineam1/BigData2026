# -*- coding: utf-8 -*-
"""TC2 · motor de ejercicios, evaluador por archivos y exportación (Big Data UC).
La autoevaluación técnica NO sustituye la revisión del docente. Sin credenciales.
"""
from __future__ import annotations
import base64, collections, hashlib, html, io, json, math, re, shutil, unicodedata, wave
from pathlib import Path
import numpy as np

SCHEMA = "tc2-v1"
MODELO = "intfloat/multilingual-e5-small"
RUBRICA = [
 ("E1.1","BM25: tokens y mecanismo",6),("E1.2","BM25: rankings literal y paráfrasis",8),
 ("E1.3","BM25: modificar una palabra y comprobar",6),
 ("E2.1","E5: vectores 384 y prefijos",7),("E2.2","Similitud coseno y top 5",8),
 ("E2.3","Atlas vectorial real o contrato local",6),("E2.4","Experimento con candidatos o filtro",4),
 ("E3.1","Precision y Recall con juicios externos",6),("E3.2","RRF calculado por posiciones",5),
 ("E3.3","Elección con alternativa y límite",4),
 ("E4.1","RGB, luminancia e histograma",6),("E4.2","Dos transformaciones medibles",8),
 ("E4.3","Perfil que conserva legibilidad",6),
 ("E5.1","Diez voces humanas licenciadas",5),("E5.2","RMS y FFT en dos ventanas",6),
 ("E5.3","Interpretación acústica y límite",4),
 ("E6.1","Explorador de dos orígenes",3),("E6.2","Decisiones ancladas al resultado",2)]
assert len(RUBRICA)==18 and sum(r[2] for r in RUBRICA)==100
URL_VOCES = "https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet"
SHA_VOCES = "989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf"

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def escribir(path, data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+"\n",encoding="utf-8")
    return path

def leer(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def normalizar(s):
    return "".join(c for c in unicodedata.normalize("NFKD",str(s).lower()) if not unicodedata.combining(c))

def tokens(s):
    return re.findall(r"[a-z0-9]{2,}",normalizar(s))

def texto(doc):
    return (doc["nombre_proceso"]+" "+doc["descripcion"]).strip()

def corpus_lista(base):
    data=leer(Path(base)/"tc2_corpus_2026.json")
    docs=data["documentos"]
    ids=[d["id_proceso"] for d in docs]
    if not docs or len(ids)!=len(set(ids)):raise ValueError("Corpus duplicado o vacío")
    return docs

def intenciones(base):
    data=leer(Path(base)/"tc2_juicios_2026.json")
    return data["intenciones"]

def elegir_intencion(base,alias):
    opciones=intenciones(base)
    pos=int(hashlib.sha256(str(alias).strip().encode()).hexdigest(),16)%len(opciones)
    return opciones[pos]

def bm25(docs,consulta,k=10):
    """BM25 local sobre tokens Unicode normalizados; no es Elasticsearch."""
    q=tokens(consulta);toks=[tokens(texto(d)) for d in docs]
    cnt=[collections.Counter(t) for t in toks];n=len(cnt)
    avdl=sum(map(len,toks))/max(n,1)
    df=collections.Counter(w for t in cnt for w in t)
    scores=[]
    for d,c,t in zip(docs,cnt,toks):
        s=0.
        for w in q:
            if not c.get(w):continue
            idf=math.log(1+(n-df[w]+.5)/(df[w]+.5))
            freq=c[w];s+=idf*(freq*2.2)/(freq+1.2*(.25+.75*len(t)/max(avdl,1)))
        scores.append({"id_proceso":d["id_proceso"],"score":round(s,8)})
    return sorted(scores,key=lambda x:(-x["score"],x["id_proceso"]))[:k]

def coseno(docs,m,q,k=10):
    m=np.asarray(m,dtype=np.float32);q=np.asarray(q,dtype=np.float32)
    if m.shape!=(len(docs),384) or q.shape!=(384,):raise ValueError("E5 debe generar N×384 y query vector 384")
    if not np.isfinite(m).all() or not np.isfinite(q).all():raise ValueError("Vector no finito")
    norma=np.linalg.norm(m,axis=1)*np.linalg.norm(q)
    if np.min(norma)<=1e-9:raise ValueError("Vector nulo")
    sc=(m@q)/norma
    return sorted([{"id_proceso":d["id_proceso"],"score":round(float(s),7)} for d,s in zip(docs,sc)],key=lambda x:(-x["score"],x["id_proceso"]))[:k]

def medidas(ranking,relevantes,k=5):
    ids=[r["id_proceso"] for r in ranking[:k]]
    rel=set(relevantes);aciertos=len(set(ids)&rel)
    return {"aciertos":aciertos,"precision_at_5":round(aciertos/k,4),"recall_at_5":round(aciertos/max(len(rel),1),4),"relevantes_totales":len(rel)}

def fusion_rrf(a,b,k0=60,top=10):
    puntos=collections.defaultdict(float)
    for ranked in (a,b):
        for pos,r in enumerate(ranked,1):puntos[r["id_proceso"]]+=1/(k0+pos)
    return [{"id_proceso":i,"score":round(v,10)} for i,v in sorted(puntos.items(),key=lambda x:(-x[1],x[0]))[:top]]

def csv_image(ranking,docs,path):
    """PNG académico derivado del Top-5 verdadero; no implica fotos de contratos."""
    from PIL import Image,ImageDraw,ImageFont
    lookup={d["id_proceso"]:d for d in docs};rs=ranking[:5]
    im=Image.new("RGB",(960,520),"#f5f9ff");d=ImageDraw.Draw(im)
    d.text((36,24),"Top 5 del buscador — imagen generada en el TC2",fill="#172c50")
    maxi=max((float(x["score"]) for x in rs),default=1)
    for n,r in enumerate(rs):
        y=90+n*76;title=lookup[r["id_proceso"]]["nombre_proceso"][:67]
        d.text((40,y),str(n+1)+". "+title,fill="#14253f")
        w=int(820*float(r["score"])/max(maxi,1e-9))
        d.rectangle((40,y+24,40+max(w,0),y+41),fill="#1d608f")
        d.text((870,y+23),f'{r["score"]:.3f}',fill="#152c4f")
    d.text((35,485),"Imagen derivada de resultados SECOP; no es fotografia ni prueba de irregularidad",fill="#263d57")
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);im.save(path)
    return path

def inspeccion_imagen(path):
    from PIL import Image
    im=Image.open(path).convert("RGB");a=np.asarray(im)
    y=(.2126*a[:,:,0]+.7152*a[:,:,1]+.0722*a[:,:,2])
    hist,bins=np.histogram(y,bins=16,range=(0,256))
    pixel=a[min(im.height-1,120),min(im.width-1,50)].tolist()
    return {"ancho":im.width,"alto":im.height,"pixel_rgb":pixel,
      "pixel_luminancia":round(.2126*pixel[0]+.7152*pixel[1]+.0722*pixel[2],3),
      "histograma":hist.tolist(),"suma_histograma":int(hist.sum()),"luminancia_media":round(float(y.mean()),3)}

def perfil_imagen(original,dest,lado,contraste=1.0):
    from PIL import Image,ImageEnhance
    if not (80<=int(lado)<=960 and .5<=float(contraste)<=2.0):raise ValueError("Perfil fuera de rango")
    im=Image.open(original).convert("RGB");im.thumbnail((int(lado),int(lado)))
    im=ImageEnhance.Contrast(im).enhance(float(contraste))
    dest=Path(dest);dest.parent.mkdir(parents=True,exist_ok=True);im.save(dest)
    return {"lado":int(lado),"contraste":float(contraste),"ancho":im.width,"alto":im.height,"bytes":dest.stat().st_size,"sha256":sha(dest)}

def audio_pcm(path):
    import soundfile as sf
    x,sr=sf.read(str(path),dtype="float32",always_2d=False)
    if x.ndim==2:x=x.mean(axis=1)
    if sr<=0 or len(x)==0:raise ValueError("Audio PCM vacío")
    return x,int(sr)

def metricas_voz(path,ventana=512):
    x,sr=audio_pcm(path);n=int(ventana)
    if n not in (256,512,1024,2048):raise ValueError("Ventana fuera del laboratorio")
    rms=float(np.sqrt(np.mean(np.square(x.astype(np.float64)))))
    zcr=float(np.mean((x[:-1]*x[1:])<0)) if len(x)>1 else 0.
    segmento=np.pad(x[:n],(0,max(0,n-len(x))))[:n]
    amp=np.abs(np.fft.rfft(segmento*np.hanning(n)))
    frec=np.fft.rfftfreq(n,1/sr)
    pico=float(frec[int(np.argmax(amp[1:])+1)]) if len(amp)>1 else 0.
    centr=float(np.sum(frec*amp)/max(np.sum(amp),1e-12))
    return {"duracion_s":round(len(x)/sr,4),"sr":sr,"rms":round(rms,7),
       "zcr":round(zcr,7),"frecuencia_pico_hz":round(pico,3),
       "centroide_hz":round(centr,3),"resolucion_hz":round(sr/n,3),"ventana_fft":n}

def obtener_voces(out,source=None):
    """Carga bytes REALES del MINDS14 versión fijada; falla cerrado, sin audio sintético."""
    import pandas as pd
    import soundfile as sf
    import urllib.request
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    fuente=Path(source) if source else out/"minds14_es_ES.parquet"
    if not fuente.exists():
        tmp=fuente.with_suffix(".parquet.part")
        try:
            req=urllib.request.Request(URL_VOCES,headers={"User-Agent":"BigData-UCentral-TC2/1.0"})
            with urllib.request.urlopen(req,timeout=120) as r,open(tmp,"wb") as w:
                while True:
                    b=r.read(1024*1024)
                    if not b:break
                    w.write(b)
                    if w.tell()>100_000_000:raise ValueError("Descarga >100 MB")
            tmp.replace(fuente)
        except Exception:
            tmp.unlink(missing_ok=True);raise
    if sha(fuente)!=SHA_VOCES:raise ValueError("La fuente real no coincide con el SHA autorizado")
    df=pd.read_parquet(fuente,columns=["audio","path","transcription","intent_class"])
    vistos=set();sel=[]
    for _,r in df.sort_values("path",kind="stable").iterrows():
        c=int(r["intent_class"])
        if c not in vistos:sel.append(r);vistos.add(c)
        if len(sel)==10:break
    if len(sel)!=10:raise ValueError("No hay diez intenciones distintas en el corpus real")
    audios=[]; hashes=set()
    for i,r in enumerate(sel,1):
        raw=r["audio"].get("bytes")
        if not isinstance(raw,(bytes,bytearray)):raise ValueError("Se esperan WAV reales embebidos")
        original=out/f"voz_{i:02d}_fuente.wav";original.write_bytes(raw)
        x,sr=sf.read(io.BytesIO(raw),dtype="float32",always_2d=False)
        if x.ndim==2:x=x.mean(axis=1)
        pcm=out/f"voz_{i:02d}.wav"
        sf.write(pcm,x,sr,subtype="PCM_16",format="WAV")
        digest=sha(original)
        if digest in hashes:raise ValueError("Voz duplicada")
        hashes.add(digest)
        audios.append({"n":i,"archivo":str(pcm.name),"original":original.name,
           "fuente_url":URL_VOCES,"source_record_id":str(r["path"]),
           "source_original_sha256":digest,"sha256":sha(pcm),
           "license":"CC BY 4.0","source_kind":"MINDS14_es_ES","source_dataset_sha256":SHA_VOCES,
           "intent_class":int(r["intent_class"]),
           "transcripcion_referencia":str(r["transcription"]),
           "medidas":metricas_voz(pcm)})
    return audios

def hacer_html(carpeta,docs,bm,sem,rrf,datoimg,audios,decisiones):
    """Explorador offline: filtra resultados YA calculados; no recalcula embeddings en navegador."""
    carpeta=Path(carpeta);lookup={d["id_proceso"]:d for d in docs}
    def tabla(nombre,filas):
        tr=[]
        for x in filas[:5]:
            d=lookup[x["id_proceso"]]
            tr.append("<tr><td>"+html.escape(x["id_proceso"])+"</td><td>"+html.escape(d["nombre_proceso"][:120])+
              "</td><td>"+html.escape(str(round(x["score"],5)))+
              "</td><td><a href='"+html.escape(d["url_secop"],quote=True)+"' target='_blank' rel='noopener'>SECOP</a></td></tr>")
        return "<section><h3>"+html.escape(nombre)+"</h3><table><thead><tr><th>ID</th><th>Objeto</th><th>Score</th><th>Fuente</th></tr></thead><tbody>"+"".join(tr)+"</tbody></table></section>"
    voces="".join("<article><strong>Voz "+str(a["n"])+"</strong><p>PolyAI MINDS14 · CC BY 4.0 · "+html.escape(a["source_record_id"])+
      "</p><audio controls preload='none' src='E5/audio/"+html.escape(a["archivo"],quote=True)+"'></audio><p>RMS "+str(a["medidas"]["rms"])+
      " · duración "+str(a["medidas"]["duracion_s"])+" s · centroide "+str(a["medidas"]["centroide_hz"])+" Hz</p></article>" for a in audios)
    style="""body{font:16px/1.5 system-ui;margin:0;background:#f3f7fc;color:#182c44}main{max-width:1150px;margin:auto;padding:20px}header{background:#132f56;color:white;padding:25px}section,article{background:white;border:1px solid #d9e2ed;border-radius:12px;padding:16px;margin:14px 0;overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border-bottom:1px solid #dbe2ea;padding:8px;text-align:left}a{color:#145c9e}img{max-width:100%;height:auto}audio{width:100%;max-width:400px}p{max-width:90ch}@media(prefers-color-scheme:dark){body{background:#101b2a;color:#e8f0fa}section,article{background:#1c2e45;border-color:#405574}a{color:#a3caff}th,td{border-color:#3e5066}}"""
    page="<!doctype html><html lang='es'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>TC2 · Explorador de Laura</title><style>"+style+"</style><header><h1>Explorador de Evidencias · TC2</h1><p>SECOP: búsqueda sobre texto contractual · MINDS14: audios financieros distintos, sin vínculo documental con SECOP</p></header><main><h2>Resultados de búsqueda</h2>"+tabla("BM25 léxico",bm)+tabla("E5 semántico",sem)+tabla("RRF híbrido",rrf)+"<h2>Imagen derivada del ranking</h2><section><img alt='Visualización del Top 5 generado en el taller, no fotografía de contratos' src='E4/ranking.png'><p>El histograma y la reducción representan píxeles; no describen el contenido semántico de un documento.</p><img alt='Versión de tamaño reducido' src='E4/perfil_160.png'><img alt='Versión legible' src='E4/perfil_640.png'></section><h2>Diez voces reales autorizadas</h2>"+voces+"<section><h2>Decisiones y límites</h2><pre>"+html.escape(json.dumps(decisiones,ensure_ascii=False,indent=2))+"</pre><p>Los audios no pertenecen a las noticias ni a los contratos SECOP. Una FFT no transcribe palabras.</p></section></main></html>"
    ruta=carpeta/"explorador.html";ruta.write_text(page,encoding="utf-8")
    return ruta

def empaquetar(carpeta,manifest):
    """Archivo para Drive, evitando cachés, secretos y fuentes externas pesadas."""
    import zipfile
    carpeta=Path(carpeta)
    no_ext={".env",".pem",".key"}
    rutas=[p for p in carpeta.rglob("*") if p.is_file() and not p.name.endswith(".part") and p.suffix.lower() not in no_ext and not p.name.startswith("minds14_")]
    prohibido=re.compile(r"(mongodb\+srv://|sk-proj-|BEGIN PRIVATE KEY|claimUrl)",re.I)
    zip_path=carpeta.parent/(carpeta.name+".zip")
    with zipfile.ZipFile(zip_path,"w",compression=zipfile.ZIP_DEFLATED) as z:
        for p in rutas:
            if p.stat().st_size>50_000_000:raise ValueError("Un archivo de evidencia supera 50 MB")
            if p.suffix.lower() in {".json",".jsonl",".html",".txt"} and prohibido.search(p.read_text(encoding="utf-8",errors="ignore")):
                raise ValueError("Se detectó un posible secreto en "+str(p))
            z.write(p,p.relative_to(carpeta))
    return zip_path

def validar(carpeta,docs,intencion):
    """Recalcula controles desde archivos, no confía en el puntaje del manifest."""
    carpeta=Path(carpeta);checks={}
    def lee(r):return leer(carpeta/r)
    def ok(item,cond,detalle):
        puntos=next(p for c,_,p in RUBRICA if c==item)
        checks[item]={"maximo":puntos,"puntos":puntos if bool(cond) else 0,"ok":bool(cond),"detalle":str(detalle)[:260]}
    def near(a,b,tol=1e-4):
        try:return abs(float(a)-float(b))<=tol
        except (TypeError,ValueError):return False
    try:
        bm=lee("E1/bm25.json");q=intencion
        expected1=bm25(docs,q["literal"],10); expected2=bm25(docs,q["parafrasis"],10)
        lab1=lee("E1/laboratorio_bm25.json") if (carpeta/"E1/laboratorio_bm25.json").exists() else {}
        termino=tokens(q["literal"])[0]
        df_real=sum(1 for d in docs if termino in set(tokens(texto(d))))
        idf_real=math.log(1+(len(docs)-df_real+.5)/(df_real+.5))
        e1_lab_ok=lab1.get("termino")==termino and lab1.get("df")==df_real and lab1.get("n")==len(docs) and near(lab1.get("idf"),idf_real,1e-7)
        ok("E1.1",bm.get("tokens_literal")==tokens(q["literal"]) and bm.get("analizador")=="normalizado_simple" and e1_lab_ok,
           "Tokenización, frecuencia documental e IDF verificados; completa el ejercicio si falta.")
        ok("E1.2",bm.get("literal")==expected1 and bm.get("parafrasis")==expected2,"Dos rankings BM25 local verificables.")
        cambio=bm.get("cambio",{});original=q["literal"];nuevo=cambio.get("consulta","")
        ok("E1.3",nuevo!=original and len(tokens(nuevo))>0 and cambio.get("ranking")==bm25(docs,nuevo,10) and bool(cambio.get("prediccion")),"Consulta modificada y ranking correcto.")
    except Exception as e:
        for item in ("E1.1","E1.2","E1.3"):ok(item,False,str(e))
        bm={}
    try:
        e=lee("E2/semantica.json")
        x=np.load(carpeta/"E2/embeddings.npy",allow_pickle=False);q1=np.load(carpeta/"E2/query_literal.npy",allow_pickle=False);q2=np.load(carpeta/"E2/query_parafrasis.npy",allow_pickle=False)
        shape_ok=x.shape==(len(docs),384) and q1.shape==(384,) and q2.shape==(384,) and np.isfinite(x).all() and np.isfinite(q1).all()
        pref=lee("E2/experimento_prefijos.json") if (carpeta/"E2/experimento_prefijos.json").exists() else {}
        experimento_prefijos_ok=all(isinstance(pref.get(k),(int,float)) and -1<=pref.get(k)<=1 for k in ("query_vs_passage","query_vs_sin_prefijo"))
        ok("E2.1",shape_ok and e.get("modelo")==MODELO and e.get("prefijos")==["passage:","query:"] and experimento_prefijos_ok,
           "N×384 y comparación real de prefijos guardada.")
        want1=coseno(docs,x,q1,10);want2=coseno(docs,x,q2,10)
        lab2=lee("E2/laboratorio_coseno.json") if (carpeta/"E2/laboratorio_coseno.json").exists() else {}
        lab_cos_ok=lab2.get("formula")=="producto_punto_dividido_por_normas" and near(lab2.get("cos_ab"),1.0,1e-6) and near(lab2.get("cos_ac"),0.0,1e-6)
        ok("E2.2",e.get("literal")==want1 and e.get("parafrasis")==want2 and lab_cos_ok,
           "Top-k coseno y función completada de dos dimensiones.")
        a=e.get("atlas",{})
        remoto=bool(a.get("ping") and a.get("indice_queryable") and a.get("query_ejecutada") and len(a.get("resultados",[]))>0 and a.get("motor")=="MongoDB Atlas Vector Search")
        contrato=bool(a.get("indice_path")=="embedding" and a.get("indice_dimensiones")==384 and a.get("pipeline_limit")==5 and a.get("sistema") in ("Atlas real","Ruta local declarada"))
        ok("E2.3",contrato and remoto,"Atlas declarado real = "+str(remoto)+"; validación remota definitiva pendiente de auditoría docente.")
        if contrato and a.get("sistema")=="Ruta local declarada" and not remoto:
            checks["E2.3"]["puntos"]=3
            checks["E2.3"]["ok"]=False
            checks["E2.3"]["detalle"]="3/6 por contrato vectorial local, no por ejecución remota de Atlas."
        varia=e.get("experimento",{}); k=varia.get("k")
        fil=lee("E2/experimento_filtro.json") if (carpeta/"E2/experimento_filtro.json").exists() else {}
        id_lider=e.get("parafrasis",[{}])[0].get("id_proceso")
        entidad_real=next((d["entidad"] for d in docs if d["id_proceso"]==id_lider),None)
        indices=[i for i,d in enumerate(docs) if d["entidad"]==entidad_real] if entidad_real else []
        fil_ok=bool(indices) and fil.get("entidad")==entidad_real and fil.get("candidatos")==len(indices) and fil.get("ranking")==coseno([docs[i] for i in indices],x[indices],q2,min(5,len(indices)))
        k_ok=k in (3,8) and varia.get("ranking")==coseno(docs,x,q2,int(k)) if k in (3,8) else False
        ok("E2.4",k_ok and fil_ok,"Cambio Top-k y filtro de candidatos real, sobre E5.")
    except Exception as err:
        for item in ("E2.1","E2.2","E2.3","E2.4"):ok(item,False,str(err))
        e={}
    try:
        r=lee("E3/evaluacion.json")
        ranking_lex=bm.get("parafrasis",[])
        ranking_sem=e.get("parafrasis",[])
        fusion=fusion_rrf(ranking_lex,ranking_sem,60,10)
        a=medidas(ranking_lex,intencion["relevantes"]);b=medidas(ranking_sem,intencion["relevantes"])
        labp=lee("E3/laboratorio_precision.json") if (carpeta/"E3/laboratorio_precision.json").exists() else {}
        ids_bm=[t["id_proceso"] for t in ranking_lex[:5]]
        labp_ok=labp.get("top5")==ids_bm and labp.get("positivos_totales")==len(intencion["relevantes"]) and near(labp.get("precision_manual"),a["precision_at_5"],1e-4)
        ok("E3.1",r.get("bm25")==a and r.get("e5")==b and labp_ok,
           "Precision@5 manual y Recall@5 contrastados con juicios externos.")
        labr=lee("E3/laboratorio_rrf.json") if (carpeta/"E3/laboratorio_rrf.json").exists() else {}
        labr_ok=labr.get("pos_bm25")==1 and labr.get("pos_e5")==3 and labr.get("k")==60 and near(labr.get("score"),1/61+1/63,1e-8)
        ok("E3.2",r.get("rrf")==fusion and r.get("metricas_rrf")==medidas(fusion,intencion["relevantes"]) and labr_ok,
           "RRF manual y fusión completa correctos.")
        de=r.get("decision",{})
        ok("E3.3",de.get("elegido") in ("BM25","E5","RRF") and de.get("descartado") in ("BM25","E5","RRF") and de.get("descartado")!=de.get("elegido") and de.get("limite") in ("Solo cubre los juicios etiquetados","No demuestra irregularidades") and de.get("precision_observada")=={"BM25":a,"E5":b,"RRF":medidas(fusion,intencion["relevantes"])}[de.get("elegido", "BM25")]["precision_at_5"],"Elegir, descartar y usar métrica real.")
    except Exception as err:
        for item in ("E3.1","E3.2","E3.3"):ok(item,False,str(err))
    try:
        meta=lee("E4/imagen.json")
        orig=carpeta/"E4/ranking.png"
        m=inspeccion_imagen(orig)
        lumi=lee("E4/laboratorio_luminancia.json") if (carpeta/"E4/laboratorio_luminancia.json").exists() else {}
        lumi_ok=lumi.get("rgb_rojo")==[255,0,0] and lumi.get("rgb_verde")==[0,255,0] and near(lumi.get("luminancia_rojo"),54.213,.002) and near(lumi.get("luminancia_verde"),182.376,.002)
        ok("E4.1",meta.get("inspeccion")==m and m["suma_histograma"]==m["ancho"]*m["alto"] and lumi_ok,
           "RGB, fórmula propia de luminancia y 16 bins del histograma.")
        files=all((carpeta/f"E4/perfil_{n}.png").exists() for n in (160,640))
        both=meta.get("perfiles",{})
        a=inspeccion_imagen(carpeta/"E4/perfil_160.png");b=inspeccion_imagen(carpeta/"E4/perfil_640.png")
        ok("E4.2",files and a["ancho"]<b["ancho"] and both.get("160",{}).get("sha256")==sha(carpeta/"E4/perfil_160.png") and both.get("640",{}).get("sha256")==sha(carpeta/"E4/perfil_640.png"),"Perfiles generados con diferencia observable.")
        ok("E4.3",meta.get("preferido")=="640" and meta.get("limite")=="Reducir puede volver ilegibles las etiquetas" and b["ancho"]>=480,"Perfil útil por legibilidad.")
    except Exception as err:
        for item in ("E4.1","E4.2","E4.3"):ok(item,False,str(err))
    try:
        a=lee("E5/audios.json"); voces=a["audios"]
        bueno=len(voces)==10 and len({v.get("source_record_id") for v in voces})==10 and len({v.get("intent_class") for v in voces})==10
        for v in voces:
            p=carpeta/"E5/audio"/v["archivo"]
            original=carpeta/"E5/audio"/v["original"]
            bueno=bueno and p.exists() and original.exists() and sha(p)==v["sha256"] and sha(original)==v.get("source_original_sha256") and v.get("license")=="CC BY 4.0" and v.get("source_kind")=="MINDS14_es_ES" and v.get("source_dataset_sha256")==SHA_VOCES
        ok("E5.1",bueno,"Diez voces humanas distintas, procedencia y huellas.")
        a1=a["comparacion"];v=voces[int(a1["posicion"])-1];ruta=carpeta/"E5/audio"/v["archivo"]
        m512=metricas_voz(ruta,512);m1024=metricas_voz(ruta,1024)
        lab_rms=lee("E5/laboratorio_rms.json") if (carpeta/"E5/laboratorio_rms.json").exists() else {}
        lab_rms_ok=lab_rms.get("muestras")==[1,-1,0,0] and near(lab_rms.get("rms_manual"),math.sqrt(.5),1e-6) and lab_rms.get("media_simple")==0.0
        ok("E5.2",a1.get("ventana_512")==m512 and a1.get("ventana_1024")==m1024 and m512["resolucion_hz"]>m1024["resolucion_hz"] and lab_rms_ok,
           "RMS de cuatro muestras implementado y FFT 512/1024 medido en WAV real.")
        ok("E5.3",a1.get("limite")=="RMS y FFT no transcriben palabras" and a1.get("referencia_no_asr") is True and 1<=int(a1.get("posicion",0))<=10,"Distinción entre señal y transcripción.")
    except Exception as err:
        for item in ("E5.1","E5.2","E5.3"):ok(item,False,str(err))
    try:
        report=leer(carpeta/"E6/defensa.json")
        page=(carpeta/"explorador.html").read_text(encoding="utf-8")
        ok("E6.1","BM25 léxico" in page and "E5 semántico" in page and "Diez voces reales autorizadas" in page and "sin vínculo" in page and "<audio" in page,"Explorador HTML con orígenes separados.")
        ok("E6.2",report.get("modelo") in ("BM25","E5","RRF") and report.get("audio_no_implica")=="Transcripción ni intención" and report.get("imagen_no_implica")=="Contenido semántico del contrato","Defensa de los tres mecanismos.")
    except Exception as err:
        for item in ("E6.1","E6.2"):ok(item,False,str(err))
    total=sum(v["puntos"] for v in checks.values())
    return {"schema":SCHEMA,"puntaje":total,"nota_provisional":math.floor((1+4*total/100)*10+0.5+1e-9)/10,
            "controles":checks,"pendiente_revision_docente":"E2.3: confirmar Atlas con auditoría o aplicar contingencia documentada"}
