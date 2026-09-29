#!/usr/bin/env python3
"""Valida estructura, sincronía y contratos pedagógicos de S10."""
from __future__ import annotations
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DECK=ROOT/"Presentaciones/s10-etl-multimedia.html"
GEN=ROOT/"utils/build_session10_multimedia.py"
NB=ROOT/"Cuadernos/10_ETL_Multimedia.ipynb"
SEED=ROOT/"infraestructura/lms/s10-multimedia-seed.sql"
BACKEND=ROOT/"infraestructura/lms/functions/bigdata-session/index.ts"
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

deck=DECK.read_text("utf-8")
seed=SEED.read_text("utf-8")
backend=BACKEND.read_text("utf-8")
nb=json.loads(NB.read_text("utf-8"))
text="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))

slides=re.findall(r'<section class="slide[^"]*" id="s(\d+)" data-slide="(\d+)">',deck)
need(len(slides)==34,f"presentación: se esperaban 34 diapositivas y hay {len(slides)}")
need([int(a) for a,b in slides]==list(range(1,35)),"presentación: numeración s1..s34 no es continua")
need(all(a==b for a,b in slides),"presentación: id y data-slide difieren")
for n in range(1,35):
    m=re.search(rf'<section class="slide[^"]*" id="s{n}" data-slide="{n}">(.*?)</section>',deck,re.S)
    need(bool(m),f"S{n}: no encontrada")
    if not m: continue
    s=m.group(1)
    need("<h1>" in s,f"S{n}: falta h1")
    need('class="' in s and ("visual" in s or "<svg" in s or "<pre" in s or "<table" in s),f"S{n}: falta ancla visual")
    need(len(re.sub(r"<[^>]+>"," ",s).split())>=18,f"S{n}: contenido demasiado ligero")

for term,slide in [("Asset / activo",5),("Hash",12),("MIME",15),("Container",15),("Codec",15),("Stream",15),("Canonicalizar",20),("Sampling temporal",26),("Manifest",30)]:
    section=re.search(rf'id="s{slide}".*?</section>',deck,re.S)
    need(section and term.lower() in section.group(0).lower(),f"S{slide}: falta definición explícita de {term}")

need("126 noticias" in deck and "8 con video" in deck,"presentación: faltan conteos reales del dataset de El Tiempo")
need("fixture_derivado" in deck,"presentación: debe declarar explícitamente el fallback fixture_derivado")
need("INDICE_ARTICULO = 7 #@param" in text,"notebook: falta índice numérico cerrado")
need("noticias_eltiempo_2026-08.json" in text,"notebook: no usa dataset real de El Tiempo")
need("fixture_derivado" in text and "eltiempo_real" in text,"notebook: no distingue binario real de fixture")
need("ffprobe_json" in text and "run_ffmpeg" in text,"notebook: faltan helpers multimedia")
need("assets.jsonl" in text and "assets.parquet" in text and "manifest_s10.json" in text,"notebook: faltan tres outputs")
need("QUALITY GATES: OK" in text,"notebook: faltan quality gates")
need("Cómo se lee." in text and "Qué nos dice." in text and "Qué NO permite concluir" in text and "Error común." in text,"notebook: faltan cuatro rótulos de interpretación")
need("#@param" in text and "Elige..." in text,"notebook: falta autoevaluación cerrada")

for i,c in enumerate(nb.get("cells",[]),1):
    if c.get("cell_type")!="code": continue
    src="".join(c.get("source",[]))
    try: compile(src,f"s10_cell_{i}.py","exec")
    except SyntaxError as ex: errors.append(f"notebook: sintaxis Python celda {i}: {ex}")

with tempfile.TemporaryDirectory() as td:
    tmp=Path(td)/"regen.ipynb"
    p=subprocess.run([sys.executable,str(GEN),"--output",str(tmp)],cwd=ROOT,capture_output=True,text=True)
    need(p.returncode==0,"generador: falla al regenerar notebook: "+p.stderr[-500:])
    if p.returncode==0:
        regen=json.loads(tmp.read_text("utf-8"))
        need(regen==nb,"generador y notebook no están sincronizados")

need(all(code in deck for code in [f"bd-s10-c{i}" for i in range(1,9)]),"presentación: faltan checkpoints D1-D8")
need(all(code in deck for code in ["bd-s10-lab-image","bd-s10-lab-audio","bd-s10-lab-video"]),"presentación: faltan LAB imagen/audio/video")
for marker in ["S10 LIVE","articleIndex","hashText","pipelineBuilder","mediaFile","audioRate","videoMaxFrames","manifestPreview"]:
    need(marker in deck,f"presentación: falta herramienta {marker}")
need("answer_challenge" in deck and "data-submit-challenge" in deck,"presentación: desafíos no están conectados al LMS")
need("LOCAL_ANSWERS" not in deck,"presentación: no debe exponer clave local de D1-D8")
for leaked in ["4_assets","bytes_identicos","sha256_sampling","ac1_ar16000","mp4_container__h264_aac_codecs"]:
    need(leaked not in deck,f"presentación: value semántico expone respuesta: {leaked}")
need("sessionControlBanner" in deck and "renderTeacherControls" in deck,"presentación: controles docentes no están integrados")
need('id="videoMaxFrames" type="range" min="4" max="20" value="10"' in deck,"presentación: MAX_FRAMES debe iniciar en 10")
need("K.evidence" in deck and "data-submit-lab" in deck,"presentación: LAB no registran evidencia")
need('data-session="10"' in deck and "lms-kit.js" in deck,"presentación: falta LMS Kit S10")
need(seed.count('"blocks_session_completion":true')==3,"seed: los tres LAB S10 deben bloquear completion")
for code in ["bd-s10-lab-image","bd-s10-lab-audio","bd-s10-lab-video"]:
    row=re.search(rf"\('{code}'.*?\)::jsonb\)",seed)
    need(bool(row and ",'lab',0," in row.group(0) and ",true," in row.group(0)),f"seed: {code} debe ser required")
need('const blockingLabs=activities.filter(a=>a.kind==="lab"&&a.required&&a.metadata?.blocks_session_completion===true);' in backend,"backend: falta política opt-in de LAB bloqueantes")
need('metadata?.evidence_verified===true' in backend,"backend: completion debe exigir evidencia verificada")
need('lab_completed:labsVerified,lab_total:blockingLabs.length' in backend,"backend: resumen no expone progreso LAB bloqueante")
need('body.client_evidence_id,def.activities' in backend,"backend: evidencia de presentación no recalcula con definición de sesión")
need("D1–D8 y evidencia correcta en LAB 1–3" in deck,"presentación: falta regla de cierre explícita")

if errors:
    print("SESION 10: FAIL")
    for e in errors: print(" -",e)
    raise SystemExit(1)
print("SESION 10: OK")
print(" - 34 diapositivas con ancla visual y densidad mínima")
print(" - El Tiempo real + fallback de procedencia explícita")
print(" - D1-D8 + S10 Live + 7 herramientas/simuladores")
print(" - LAB imagen, audio y video con evidencia estructurada")
print(" - cierre S10 exige D1-D8 + LAB 1-3 verificados")
print(" - imagen, audio y video encadenados en un solo ETL")
print(" - JSONL + Parquet + manifest + quality gates")
print(" - generador y notebook sincronizados")
