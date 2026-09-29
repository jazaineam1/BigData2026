#!/usr/bin/env python3
"""Valida estructura, sincronía y contratos pedagógicos de S10."""
from __future__ import annotations
import json, re, subprocess, sys, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DECK=ROOT/"Presentaciones/s10-etl-multimedia.html"
GEN=ROOT/"utils/build_session10_multimedia.py"
NB=ROOT/"Cuadernos/10_ETL_Multimedia.ipynb"
errors=[]

def need(cond,msg):
    if not cond: errors.append(msg)

deck=DECK.read_text("utf-8")
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

for term,slide in [("Asset / activo",6),("Hash",9),("MIME type",10),("Container",11),("Codec",11),("Stream",11),("Canonicalización",21),("Sampling temporal",26),("Manifest",32)]:
    section=re.search(rf'id="s{slide}".*?</section>',deck,re.S)
    need(section and term.lower() in section.group(0).lower(),f"S{slide}: falta definición explícita de {term}")

need('<span>Noticias</span><i style="--w:100%">126</i>' in deck and '<span>con video</span><i style="--w:6.35%">8</i>' in deck,"presentación: faltan conteos reales del dataset de El Tiempo")
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

if errors:
    print("SESION 10: FAIL")
    for e in errors: print(" -",e)
    raise SystemExit(1)
print("SESION 10: OK")
need(all(code in deck for code in [f"bd-s10-c{i}" for i in range(1,9)]),"presentación: faltan checkpoints D1-D8")
need(all(code in deck for code in ["bd-s10-lab-image","bd-s10-lab-audio","bd-s10-lab-video"]),"presentación: faltan LAB imagen/audio/video")
for marker in ["S10 LIVE","articleIndex","hashText","pipelineBuilder","mediaFile","audioRate","videoMaxFrames","manifestPreview"]:
    need(marker in deck,f"presentación: falta herramienta {marker}")
need("answer_challenge" in deck and "data-submit-challenge" in deck,"presentación: desafíos no están conectados al LMS")
need("K.evidence" in deck and "data-submit-lab" in deck,"presentación: LAB no registran evidencia")
need('data-session="10"' in deck and "lms-kit.js" in deck,"presentación: falta LMS Kit S10")
print(" - 34 diapositivas con ancla visual y densidad mínima")
print(" - El Tiempo real + fallback de procedencia explícita")
print(" - D1-D8 + S10 Live + 7 herramientas/simuladores")
print(" - LAB imagen, audio y video con evidencia estructurada")
print(" - imagen, audio y video encadenados en un solo ETL")
print(" - JSONL + Parquet + manifest + quality gates")
print(" - generador y notebook sincronizados")
