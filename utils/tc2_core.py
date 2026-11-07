# -*- coding: utf-8 -*-
"""TC2 · motor de ejercicios, evaluador por archivos y exportación (Big Data UC).
La autoevaluación técnica NO sustituye la revisión del docente. Sin credenciales.
"""
from __future__ import annotations
import base64, collections, hashlib, html, io, json, math, re, shutil, unicodedata, wave
from pathlib import Path
import numpy as np

SCHEMA = "tc2-v3-ocr-asr"
MODELO = "intfloat/multilingual-e5-small"
RUBRICA = [
 ("E1.1","Tokens y DF/IDF",3),("E1.2","BM25 dos rankings",4),("E1.3","Variación léxica",3),
 ("E2.1","E5 384 dimensiones",4),("E2.2","Coseno y Top-k",5),("E2.3","Atlas real o ruta local",4),("E2.4","Filtro y candidatos",2),
 ("E3.1","Precision/Recall@5",4),("E3.2","RRF manual e híbrido",4),("E3.3","Decisión y límite",2),
 ("E4.1","RGB, luminancia e histograma",5),("E4.2","Transformación de imagen",5),
 ("E4.3","Legibilidad y pérdida",4),("E4.4","OCR real, códigos y evidencia",6),
 ("E5.1","Diez audios reales",5),("E5.2","RMS, FFT y espectrograma",5),
 ("E5.3","Interpretación de audio",2),("E5.4","ASR Whisper real sobre diez voces",6),
 ("E5.5","WER, segmentos y extracción estructurada",2),
 ("E6.1","Catálogo enriquecido y procedencia",6),("E6.2","Reimportación, consultas y texto extraído",6),
 ("E6.3","Idempotencia",4),("E6.4","Corrupción y recuperación",4),("E6.5","Explorador y defensa",5)]
assert len(RUBRICA)==24 and sum(r[2] for r in RUBRICA)==100

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
    """Imagen auténtica del ranking del estudiante, letras grandes e IDs para OCR."""
    from PIL import Image,ImageDraw,ImageFont
    lookup={d["id_proceso"]:d for d in docs};rs=ranking[:5]
    im=Image.new("RGB",(960,540),"#ffffff");drawer=ImageDraw.Draw(im)
    try:
        titlefont=ImageFont.truetype("DejaVuSans-Bold.ttf",24)
        idfont=ImageFont.truetype("DejaVuSans-Bold.ttf",20)
        bodyfont=ImageFont.truetype("DejaVuSans.ttf",15)
    except OSError:
        titlefont=ImageFont.load_default();idfont=titlefont;bodyfont=titlefont
    drawer.text((28,18),"TOP 5 - RESULTADOS SECOP",font=titlefont,fill="#122238")
    drawer.text((28,58),"Imagen generada desde el ranking del equipo: transcribir y comprobar IDs",font=bodyfont,fill="#193d5c")
    maxi=max((abs(float(x["score"])) for x in rs),default=1)
    for n,r in enumerate(rs):
        y=102+n*85
        proc=lookup[r["id_proceso"]]
        drawer.text((32,y),str(n+1)+"  "+proc["id_proceso"],font=idfont,fill="#0b192b")
        drawer.text((40,y+30),proc["nombre_proceso"][:73],font=bodyfont,fill="#1b3852")
        barwidth=int(740*abs(float(r["score"]))/max(maxi,1e-8))
        drawer.rectangle((40,y+56,40+max(barwidth,0),y+65),fill="#166999")
        drawer.text((796,y+53),f'{r["score"]:.3f}',font=bodyfont,fill="#153651")
    drawer.text((25,519),"Gráfico docente: no es fotografía, OCR no demuestra veracidad contractual",font=bodyfont,fill="#384f65")
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

def normalizar_palabras(s):
    """Normalización de evaluación WER; conserva palabras de una letra."""
    return re.findall(r"[a-z0-9]+",normalizar(s),flags=re.U)

def wer_palabras(referencia,prediccion):
    """Distancia Levenshtein por palabras / longitud de referencia; puede ser >1."""
    a,b=normalizar_palabras(referencia),normalizar_palabras(prediccion)
    if not a:return None
    prev=list(range(len(b)+1))
    for i,word in enumerate(a,1):
        cur=[i]+[0]*len(b)
        for j,other in enumerate(b,1):
            cur[j]=min(prev[j]+1,cur[j-1]+1,prev[j-1]+int(word!=other))
        prev=cur
    return round(prev[-1]/len(a),6)

def extraer_ids_secop(s):
    """Sólo identificadores que aparecen en texto OCR; nunca inventar un ID."""
    t=str(s).upper()
    t=re.sub(r"\s+"," ",t)
    patron=r"CO[1I]\s*[.\- ]*\s*REQ\s*[.\- ]*\s*(\d{7,10})"
    return sorted({"CO1.REQ."+m for m in re.findall(patron,t)})

def extraer_cifras(s):
    return sorted(set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)*(?!\w)",str(s))))[:25]

def extraer_info_voz(texto):
    """Heurística reproducible; etiquetas inferidas, no entidades verificadas."""
    t=normalizar(texto)
    catalogo={"cuenta":["cuenta","saldo","transferencia"],
      "tarjeta":["tarjeta","credito","debito"],
      "credito":["prestamo","credito","hipoteca"],
      "pagos":["pago","pagar","factura"],
      "seguridad":["contrasena","bloquear","fraude"]}
    temas=sorted(k for k,palabras in catalogo.items() if any(re.search(r"\b"+re.escape(v)+r"\b",t) for v in palabras))
    return {"temas_heuristicos":temas or ["sin_clasificar"],
       "numeros_mencionados":extraer_cifras(texto),
       "metodo":"reglas_lexicas_deterministas","requiere_revision_humana":True}

def ejecutar_ocr(carpeta,ranking):
    """Tesseract de verdad sobre 3 PNG; guarda texto y procedencia por archivo."""
    from PIL import Image
    import pytesseract
    from pytesseract import Output
    idiomas=pytesseract.get_languages(config="")
    if "spa" not in idiomas:
        raise RuntimeError("Instala el paquete del sistema tesseract-ocr-spa antes de ejecutar E4 OCR")
    carpeta=Path(carpeta);esperados=[x["id_proceso"] for x in ranking[:5]]
    results=[]
    for nombre in ("ranking.png","perfil_160.png","perfil_640.png"):
        p=carpeta/"E4"/nombre
        with Image.open(p) as image:
            rgb=image.convert("RGB")
            data=pytesseract.image_to_data(rgb,lang="spa",config="--psm 6",
                      output_type=Output.DICT)
        tokens_validos=[]
        conf=[]
        for token,c in zip(data["text"],data["conf"]):
            try: score=float(c)
            except (ValueError,TypeError):score=-1
            if str(token).strip() and score>=0:
                tokens_validos.append(str(token).strip())
                conf.append(score)
        texto_ocr=" ".join(tokens_validos)
        ids_detectados=extraer_ids_secop(texto_ocr)
        resultados_esperados=[ident for ident in esperados if ident in ids_detectados]
        results.append({"archivo":"E4/"+nombre,"sha256_imagen":sha(p),
           "motor":"tesseract","idioma":"spa","psm":6,
           "texto_ocr":texto_ocr,"ids_ocr":ids_detectados,"ids_secop_verificados":resultados_esperados,
           "cifras":extraer_cifras(texto_ocr),
           "confianza_media":round(sum(conf)/len(conf),3) if conf else None,
           "cobertura_ids":round(len(resultados_esperados)/max(len(esperados),1),4),
           "tokens_ocr":len(tokens_validos)})
    out={"schema":"tc2-ocr-v1","source_kind":"SECOP_ranking_generado",
         "motor":"tesseract","idioma":"spa","ids_esperados":esperados,
         "resultados":results,
         "nota":"Los IDs se comparan con ranking real; texto OCR es hipótesis, no hechos verificados."}
    escribir(carpeta/"E4/ocr.json",out)
    return out

def ejecutar_asr(carpeta,voces,modelo="tiny"):
    """Whisper real local sobre diez WAV MINDS14; no reutiliza referencia como predicción."""
    from faster_whisper import WhisperModel
    if modelo!="tiny":raise ValueError("El TC2 se prueba con Whisper tiny multilingüe CPU")
    carpeta=Path(carpeta)
    engine=WhisperModel(modelo,device="cpu",compute_type="int8",cpu_threads=2,num_workers=1)
    salida=[]
    if len(voces)!=10:raise ValueError("Faltan voces de origen")
    for audio in voces:
        p=carpeta/"E5/audio"/audio["archivo"]
        if sha(p)!=audio["sha256"]:raise ValueError("WAV alterado: "+str(p))
        chunks,info=engine.transcribe(str(p),language="es",beam_size=1,
                    vad_filter=False,condition_on_previous_text=False)
        segmentos=[{"inicio_s":round(float(c.start),3),
                    "fin_s":round(float(c.end),3),
                    "texto":str(c.text).strip()} for c in chunks]
        prediccion=" ".join(c["texto"] for c in segmentos).strip()
        referencia=str(audio["transcripcion_referencia"])
        salida.append({"n":int(audio["n"]),"archivo":audio["archivo"],
            "source_kind":"MINDS14_es_ES","source_record_id":audio["source_record_id"],
            "sha256_audio":audio["sha256"],"engine":"faster-whisper",
            "modelo":modelo,"language":"es","compute_type":"int8",
            "transcripcion_asr":prediccion,
            "transcripcion_referencia":referencia,
            "segmentos":segmentos,
            "wer":wer_palabras(referencia,prediccion),
            "informacion":extraer_info_voz(prediccion)})
    resultado={"schema":"tc2-asr-v1","engine":"faster-whisper","modelo":modelo,
      "source_kind":"MINDS14_es_ES","licencia":"CC BY 4.0",
      "audios":salida,"limitacion":"Predicciones Whisper; no son transcripciones humanas ni noticias de El Tiempo."}
    escribir(carpeta/"E5/asr.json",resultado)
    return resultado

def construir_catalogo(carpeta,intencion):
    """Linaje multimodal + textos OCR/ASR de archivos reales."""
    carpeta=Path(carpeta)
    audios=leer(carpeta/"E5/audios.json")["audios"]
    ocr=leer(carpeta/"E4/ocr.json")
    asr=leer(carpeta/"E5/asr.json")
    por_imagen={Path(row["archivo"]).name:row for row in ocr["resultados"]}
    por_audio={int(row["n"]):row for row in asr["audios"]}
    if len(por_imagen)!=3 or len(por_audio)!=10:raise ValueError("Faltan OCR o ASR de activos")
    filas=[]
    for nombre in ("ranking.png","perfil_160.png","perfil_640.png"):
        ruta="E4/"+nombre;p=carpeta/ruta
        from PIL import Image
        with Image.open(p) as im: width,height=im.size
        lectura=por_imagen[nombre]
        if sha(p)!=lectura["sha256_imagen"]:raise ValueError("OCR no corresponde a la imagen")
        filas.append({"asset_id":"imagen_"+nombre.replace(".","_"),
          "source_kind":"SECOP_ranking_generado","source_record_id":intencion["id"],
          "media_type":"image/png","license":"Imagen generada en taller a partir de resultados SECOP",
          "raw_path":"E4/ranking.png","derived_path":ruta,
          "sha256":sha(p),"width":int(width),"height":int(height),
          "duration_s":None,"rms":None,
          "extracted_text":lectura["texto_ocr"],"text_origin":"ocr_tesseract_spa",
          "reference_text":"","wer":None,
          "extracted_info_json":json.dumps({"ids_secop":lectura["ids_secop_verificados"],
             "cobertura_ids":lectura["cobertura_ids"]},ensure_ascii=False,sort_keys=True)})
    if len(audios)!=10:raise ValueError("Se exigen 10 audios reales")
    for a in audios:
        ruta="E5/audio/"+a["archivo"];p=carpeta/ruta
        if sha(p)!=a["sha256"]:raise ValueError("Audio alterado: "+ruta)
        rec=por_audio[int(a["n"])]
        if rec["sha256_audio"]!=a["sha256"]:raise ValueError("ASR no corresponde al WAV")
        filas.append({"asset_id":"audio_"+str(a["n"]).zfill(2),
          "source_kind":"MINDS14_es_ES","source_record_id":a["source_record_id"],
          "media_type":"audio/wav","license":"CC BY 4.0",
          "raw_path":"E5/audio/"+a["original"],"derived_path":ruta,
          "sha256":sha(p),"width":None,"height":None,
          "duration_s":float(a["medidas"]["duracion_s"]),"rms":float(a["medidas"]["rms"]),
          "extracted_text":rec["transcripcion_asr"],"text_origin":"asr_whisper_tiny",
          "reference_text":rec["transcripcion_referencia"],"wer":rec["wer"],
          "extracted_info_json":json.dumps(rec["informacion"],ensure_ascii=False,sort_keys=True)})
    if len(filas)!=13 or len({f["asset_id"] for f in filas})!=13:raise ValueError("Catálogo duplicado")
    return filas

def guardar_catalogo(carpeta,filas):
    import pandas as pd
    carpeta=Path(carpeta);out=carpeta/"E6";out.mkdir(parents=True,exist_ok=True)
    contenido="\n".join(json.dumps(f,sort_keys=True,ensure_ascii=False,allow_nan=False) for f in filas)+"\n"
    (out/"catalogo.jsonl").write_text(contenido,encoding="utf-8")
    pd.DataFrame(filas).to_parquet(out/"catalogo.parquet",index=False)
    return {"cantidad":len(filas),"imagenes":sum(f["media_type"]=="image/png" for f in filas),
       "audios":sum(f["media_type"]=="audio/wav" for f in filas),
       "jsonl_sha256":sha(out/"catalogo.jsonl"),"parquet_sha256":sha(out/"catalogo.parquet")}

def reabrir_catalogo(carpeta):
    import pandas as pd
    carpeta=Path(carpeta);out=carpeta/"E6"
    lineas=[json.loads(v) for v in (out/"catalogo.jsonl").read_text(encoding="utf-8").splitlines() if v.strip()]
    tabla=pd.read_parquet(out/"catalogo.parquet")
    rec=[]
    for row in tabla.to_dict("records"):
        clean={k:(None if v is None or (isinstance(v,float) and math.isnan(v)) else v) for k,v in row.items()}
        rec.append(clean)
    if rec!=lineas:raise ValueError("JSONL y Parquet no coinciden tras releerlos")
    return lineas

def consultar_catalogo(filas,clase):
    if clase not in ("image","audio"):raise ValueError("Clase no admitida")
    return sorted(f["asset_id"] for f in filas if f["media_type"].startswith(clase+"/"))

def consultar_texto(filas,consulta):
    """Busca texto derivado real; nunca junta fuentes distintas por coincidencia de palabra."""
    q=normalizar(consulta).strip()
    if len(q)<2:raise ValueError("Consulta textual debe tener al menos dos caracteres")
    return [{"asset_id":f["asset_id"],"source_kind":f["source_kind"],
             "source_record_id":f["source_record_id"],"text_origin":f["text_origin"],
             "fragmento":f["extracted_text"][:220]}
            for f in filas if q in normalizar(f.get("extracted_text",""))]

def verificar_fallo(carpeta):
    """Corrompe copia aislada: nunca el archivo de la actividad."""
    import tempfile
    carpeta=Path(carpeta);original=carpeta/"E4/perfil_160.png"
    huella=sha(original)
    with tempfile.TemporaryDirectory(prefix="tc2-corrupt-") as tmp:
        p=Path(tmp)/"copia.png"
        shutil.copy2(original,p)
        b=bytearray(p.read_bytes())
        if len(b)<90:raise ValueError("PNG demasiado corto")
        b[-40] ^= 1
        p.write_bytes(b)
        corrupto=sha(p)
        shutil.copy2(original,p)
        restaurado=sha(p)==huella
    return {"path":"E4/perfil_160.png","original_sha":huella,
      "corrupted_sha":corrupto,"detected":corrupto!=huella,
      "restored":restaurado,"source_intact":sha(original)==huella}

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
    if (carpeta/"E6/catalogo_meta.json").exists():
        meta=leer(carpeta/"E6/catalogo_meta.json")
        resumen="<section><h2>Catálogo ETL verificado</h2><p>"+str(meta["cantidad"])+" activos, "+str(meta["imagenes"])+" imágenes y "+str(meta["audios"])+" audios. Exportaciones JSONL y Parquet disponibles en E6.</p></section>"
        page=page.replace("</main></html>",resumen+"</main></html>")
    # Exporta una ficha verificable con textos producidos por modelos reales, no etiquetas de referencia.
    if (carpeta/"E4/ocr.json").exists() and (carpeta/"E5/asr.json").exists():
        ocr=leer(carpeta/"E4/ocr.json")["resultados"]
        asr=leer(carpeta/"E5/asr.json")["audios"]
        tabla_ocr="".join("<tr><td>"+html.escape(Path(o["archivo"]).name)+"</td><td>"+html.escape(o["texto_ocr"][:500])+
               "</td><td>"+html.escape(str(o["ids_secop_verificados"]))+"</td></tr>" for o in ocr)
        tabla_asr="".join("<tr><td>"+str(a["n"])+"</td><td>"+html.escape(a["transcripcion_asr"][:500])+
               "</td><td>"+html.escape(str(a["wer"]))+"</td><td>"+html.escape(str(a["informacion"]["temas_heuristicos"]))+"</td></tr>"
               for a in asr)
        pagina_ocr="<section><h2>OCR Tesseract · texto extraído de imágenes</h2><table><thead><tr><th>Imagen</th><th>Texto predicho</th><th>IDs cotejados</th></tr></thead><tbody>"+tabla_ocr+"</tbody></table><p>Un ID reconocido no verifica la veracidad del expediente. El perfil 160 px puede perder texto.</p></section>"
        pagina_asr="<section><h2>ASR Whisper tiny · 10 audios transcritos realmente</h2><table><thead><tr><th>Voz</th><th>Predicción ASR</th><th>WER</th><th>Temas heurísticos</th></tr></thead><tbody>"+tabla_asr+"</tbody></table><p>WER compara predicciones con referencias humanas de MINDS14; los temas son reglas léxicas, no veredictos.</p></section>"
        page=page.replace("</main></html>",pagina_ocr+pagina_asr+"</main></html>")
    ruta=carpeta/"explorador.html";ruta.write_text(page,encoding="utf-8")
    return ruta

def empaquetar(carpeta,manifest):
    """ZIP de evidencias para GitHub privado, sin secretos ni parquet original de 39MB."""
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
            checks["E2.3"]["puntos"]=2
            checks["E2.3"]["ok"]=False
            checks["E2.3"]["detalle"]="2/4 por contrato vectorial local, no por Atlas remoto."
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
        ocr=lee("E4/ocr.json")
        image_files=("ranking.png","perfil_160.png","perfil_640.png")
        check_ocr=ocr.get("schema")=="tc2-ocr-v1" and ocr.get("motor")=="tesseract" and ocr.get("idioma")=="spa"
        if check_ocr:
            registros={Path(r["archivo"]).name:r for r in ocr["resultados"]}
            check_ocr=(len(registros)==3 and
                ocr.get("ids_esperados")==[x["id_proceso"] for x in fusion_rrf(
                    lee("E1/bm25.json")["parafrasis"],lee("E2/semantica.json")["parafrasis"],60,10)[:5]]
                and all(registros[n]["sha256_imagen"]==sha(carpeta/"E4"/n) and
                    registros[n].get("motor")=="tesseract" and registros[n].get("idioma")=="spa" and
                    isinstance(registros[n].get("texto_ocr"),str) and
                    isinstance(registros[n].get("tokens_ocr"),int) and registros[n]["tokens_ocr"]>=0 and
                    registros[n].get("ids_ocr")==extraer_ids_secop(registros[n]["texto_ocr"]) and
                    abs(float(registros[n]["cobertura_ids"])-len(registros[n]["ids_secop_verificados"])/5)<1e-6
                    for n in image_files) and
                registros["ranking.png"]["tokens_ocr"]>0 and
                registros["perfil_640.png"]["tokens_ocr"]>0)
        manual_ocr=lee("E4/ocr_manual.json")
        manual_ok=(manual_ocr.get("ejemplo")=="Expediente CO1.REQ.12345678 en la imagen" and
                   manual_ocr.get("ids_detectados")==["CO1.REQ.12345678"])
        ok("E4.4",check_ocr and manual_ok,"OCR español ejecutado y extractor manual de IDs verificado.")
    except Exception as err:
        for item in ("E4.1","E4.2","E4.3","E4.4"):ok(item,False,str(err))
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
        pred=lee("E5/asr.json")
        trans=pred.get("audios",[])
        pred_ok=(pred.get("schema")=="tc2-asr-v1" and pred.get("engine")=="faster-whisper" and
                 pred.get("modelo")=="tiny" and len(trans)==10 and
                 len({item.get("source_record_id") for item in trans})==10)
        if pred_ok:
            pred_ok=all(v["source_record_id"]==r.get("source_record_id") and
                 v["sha256"]==r.get("sha256_audio") and
                 r.get("engine")=="faster-whisper" and r.get("modelo")=="tiny" and
                 r.get("language")=="es" and isinstance(r.get("transcripcion_asr"),str) and
                 isinstance(r.get("segmentos"),list) and
                 r.get("transcripcion_referencia")==v.get("transcripcion_referencia")
                 for v,r in zip(voces,trans))
        ok("E5.4",pred_ok and sum(bool(x["transcripcion_asr"].strip()) for x in trans)>=8 if pred_ok else False,
           "ASR real Whisper tiny ejecutado en los 10 WAV; >=8 hipótesis no vacías.")
        info_ok=pred_ok and all(r.get("wer")==wer_palabras(r["transcripcion_referencia"],r["transcripcion_asr"]) and
              r.get("informacion")==extraer_info_voz(r["transcripcion_asr"]) for r in trans)
        manual_asr=lee("E5/asr_manual.json")
        pos=manual_asr.get("voz")
        manual_ok=(manual_asr.get("ejemplo")=="Pago, pago y saldo" and
                   set(manual_asr.get("terminos_ejemplo",[]))=={"pago","saldo"} and
                   isinstance(pos,int) and 1<=pos<=10 and
                   manual_asr.get("terminos_prediccion")==sorted(set(tokens(trans[pos-1]["transcripcion_asr"]))))
        ok("E5.5",info_ok and manual_ok,"WER recalculado, extracción estructurada y función manual comprobadas.")
    except Exception as err:
        for item in ("E5.1","E5.2","E5.3","E5.4","E5.5"):ok(item,False,str(err))
    try:
        filas=construir_catalogo(carpeta,intencion)
        meta=lee("E6/catalogo_meta.json")
        ok("E6.1",len(filas)==13 and meta.get("cantidad")==13 and meta.get("imagenes")==3 and meta.get("audios")==10 and
           meta.get("jsonl_sha256")==sha(carpeta/"E6/catalogo.jsonl") and
           all(f["sha256"]==sha(carpeta/f["derived_path"]) for f in filas) and
           sum(f["text_origin"]=="ocr_tesseract_spa" for f in filas)==3 and
           sum(f["text_origin"]=="asr_whisper_tiny" for f in filas)==10,"Catálogo con 3 imágenes, 10 audios, fuente y huellas.")
        reabierto=reabrir_catalogo(carpeta)
        consult=lee("E6/consultas.json")
        ok("E6.2",reabierto==filas and consult.get("imagenes")==consultar_catalogo(reabierto,"image") and
           consult.get("audios")==consultar_catalogo(reabierto,"audio") and
           consult.get("coincidencias_texto")==consultar_texto(reabierto,consult.get("consulta_textual","")),
           "JSONL y Parquet, consultas por modalidad y texto extraído recomputables.")
        idem=lee("E6/idempotencia.json")
        ok("E6.3",idem.get("primera")==idem.get("segunda")==sha(carpeta/"E6/catalogo.jsonl") and
           idem.get("filas_primera")==idem.get("filas_segunda")==13 and
           len(set(f["asset_id"] for f in reabierto))==13,"Reejecutar no duplica ni modifica catálogo.")
        rec=lee("E6/recuperacion.json");expected=verificar_fallo(carpeta)
        ok("E6.4",rec==expected and rec.get("detected") and rec.get("restored") and rec.get("source_intact"),
           "Copia corrupta detectada y restaurada; original intacto.")
        report=lee("E6/defensa.json")
        page=(carpeta/"explorador.html").read_text(encoding="utf-8")
        ok("E6.5","BM25 léxico" in page and "E5 semántico" in page and
           "Diez voces reales autorizadas" in page and "sin vínculo" in page and
           "Catálogo ETL verificado" in page and "OCR Tesseract" in page and
           "ASR Whisper" in page and "<audio" in page and
           report.get("modelo") in ("BM25","E5","RRF") and
           report.get("audio_no_implica")=="Transcripción ni intención" and
           report.get("imagen_no_implica")=="Contenido semántico del contrato",
           "Producto con procedencias y defensa.")
    except Exception as err:
        for item in ("E6.1","E6.2","E6.3","E6.4","E6.5"):ok(item,False,str(err))
    total=sum(v["puntos"] for v in checks.values())
    return {"schema":SCHEMA,"puntaje":total,"nota_provisional":math.floor((1+4*total/100)*10+0.5+1e-9)/10,
            "controles":checks,"pendiente_revision_docente":"E2.3: confirmar Atlas con auditoría o aplicar contingencia documentada"}
