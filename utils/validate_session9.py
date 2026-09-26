#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

deck=read("Presentaciones/s09-de-palabras-a-significado.html")
guide=read("assets/tutoriales/s09-laboratorio-guiado.html")
session=read("lms/session-09.html")
wall=read("lms/teacher-wall-09.html")
client=read("lms/assets/bigdata-lms.js")
backend=read("infraestructura/lms/functions/bigdata-session9/index.ts")
seed=read("infraestructura/lms/s09-vector-search-seed.sql")
index=read("index.html")
course_text=read("lms/data/course.json")
pages=read(".github/workflows/pages.yml")
notebook_path=ROOT/"Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb"
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"
s08=ROOT/"lms/session-08.html"

def git_blob_sha(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

if s07.exists() and git_blob_sha(s07)!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
    errors.append("S07 cambió durante S09")
if s08.exists() and git_blob_sha(s08)!="b5b1e9085fe99759182d141a75f875fcbab39d3a":
    errors.append("S08 cambió durante S09")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

try:
    nb=json.loads(notebook_path.read_text("utf-8"))
except Exception as ex:
    nb={"cells":[]}
    errors.append(f"Notebook S09 inválido: {ex}")

nb_text="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
code_cells=["".join(c.get("source",[])) for c in nb.get("cells",[]) if c.get("cell_type")=="code"]

required_terms=[
    "Corpus","Documento","Consulta","Ranking","Recuperación de información",
    "Recuperación lexical","Recuperación semántica","Búsqueda híbrida","Analyzer","Token",
    "Índice invertido","BM25","Embedding","Vector","Dimensión","Modelo",
    "Similitud","Similitud coseno","Top-k","Falso positivo","Base vectorial",
    "Metadata","Filtro","Índice vectorial","ANN","ENN","HNSW","Atlas Vector Search","$vectorSearch","Juicio de relevancia"
]
missing_terms=[t for t in required_terms if t not in deck]
lab_markers=["LAB 1 · tokenizador didáctico","LAB 2 · calculadora de coseno","LAB 3 · comparador lexical vs semántico","LAB 4 · decisión corta","LAB 5 · ruta Atlas","LAB 6 · Top-k","LAB 7 · constructor de evidencia"]

checks=[
    ("presentación suficiente", deck.count('<section class="slide')>=38),
    ("formato tipo S07", "class=\"stage\"" in deck and "class=\"nav\"" in deck and "S09 Lab" in deck and "cqw" in deck),
    ("laboratorio embebido", all(x in deck for x in lab_markers) and "S09 Lab integrado" in deck),
    ("definiciones completas", not missing_terms and deck.count("Definición")>=24 and deck.count("Ejemplo")>=18),
    ("distinción Elasticsearch explícita", "Elasticsearch ≠ búsqueda lexical" in deck),
    ("tres mecanismos", all(x in deck.lower() for x in ["lexical","semántica","híbrida"])),
    ("S07 lexical correctamente descrita", '<div class="node">tokens</div>' in deck and '<div class="node">índice invertido</div>' in deck and '<div class="node">BM25</div>' in deck),
    ("S09 semántica correctamente descrita", "Recuperación semántica" in deck and '<div class="node">embedding</div>' in deck and '<div class="node">similitud</div>' in deck and '<div class="node">Top-k</div>' in deck),
    ("hybrid no reemplaza conceptos", "Hybrid search: no siempre hay que elegir" in deck),
    ("score no probabilidad", "0.91 no significa" in deck and "probabilidad" in deck),
    ("base vectorial separa responsabilidades", "el modelo genera vectores" in deck.lower()),
    ("ANN/ENN", "Exacto vs aproximado" in deck and "ANN" in deck and "ENN" in deck),
    ("Atlas es implementación no definición", "Atlas es una implementación. No es la definición de base vectorial." in deck),
    ("guía apoyo no ruta paralela", "El laboratorio principal está en la presentación" in guide and "no ruta paralela" in guide),
    ("guía conserva regla de herramienta/mecanismo", "Elasticsearch puede hacer lexical, vectorial e híbrida" in guide),
    ("LMS aclara laboratorio en presentación", "laboratorio integrado dentro de la presentación" in session and "Diapositivas + laboratorio" in session),
    ("notebook tamaño pedagógico", len(nb.get("cells",[]))>=20),
    ("notebook modelo E5", "intfloat/multilingual-e5-small" in nb_text and "query: " in nb_text and "passage: " in nb_text),
    ("notebook BM25", "BM25Okapi" in nb_text and "buscar_lexical" in nb_text),
    ("notebook búsqueda local", "buscar_semantico_local" in nb_text and "embeddings @ q" in nb_text),
    ("notebook Atlas", "SearchIndexModel" in nb_text and "$vectorSearch" in nb_text),
    ("notebook URI oculta", "getpass(" in nb_text and "print(MONGODB_URI)" not in nb_text),
    ("notebook evidencia", "s09_evidencia_semantica.json" in nb_text and "falso_positivo" in nb_text and "alternativa_descartada" in nb_text),
    ("ruta local contingencia", "continúa con la ruta local" in nb_text.lower()),
    ("LMS recursos", "data-resource" in session and "resource_type==='presentation'" in session and "resource_type==='notebook'" in session and "guide:'guide_opened'" in session),
    ("tracking S09 dedicado", "L.s09('track'" in session and "L.startHeartbeat(null,L.s09)" in session),
    ("S09 no usa track S08", "L.bigdata('track'" not in session),
    ("checkpoints formativos", "No agregan puntaje al TC1" in session and "complete_checkpoint" in session),
    ("WALL no ranking", "No es un ranking" in wall and "No ordenar por velocidad" in wall),
    ("WALL inicio oficial", "teacher_open_session" in wall),
    ("WALL 5 checkpoints", "completed_checkpoints+'/5" in wall),
    ("cliente separado", "async function s09" in client and "async function requireS09" in client),
    ("heartbeat parametrizable", "function startHeartbeat(activity=null,tracker=bigdata)" in client),
    ("backend sesión 9", "const SESSION=9;" in backend),
    ("backend códigos aislados", "bd-s09-presentation" in backend and "bd-s09-c5" in backend),
    ("backend no califica TC1", "submit_manifest" not in backend and "note_5" not in backend),
    ("backend checkpoint self-report", "s09-self-checkpoint" in backend and "formative:true" in backend),
    ("page_opened no inicia progreso", '["presentation_opened","notebook_opened","guide_opened","checkpoint_started"].includes(event)' in backend),
    ("seed S09", "'bigdata',9" in seed and "'bd-s09-c5'" in seed),
    ("seed tres recursos", seed.count("select id,9,")>=3 and "Presentación S09" in seed and "Cuaderno S09" in seed),
    ("index S09 actual", 'data-mark="9"' in index and "Cuando las palabras no coinciden" in index),
    ("course S09 tracked", any(x.get("n")==9 and x.get("status")=="visible" and x.get("tracked") for x in course.get("sessions",[]))),
    ("course wall S09", any(x.get("code")=="wall_s09" and x.get("path")=="teacher-wall-09.html" for x in course.get("teacher_tools",[]))),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)
if missing_terms:
    errors.append("Faltan definiciones/términos en presentación: "+", ".join(missing_terms))

for i,src in enumerate(code_cells,1):
    lines=[ln for ln in src.splitlines() if not ln.lstrip().startswith(("%","!"))]
    if not lines: continue
    try:
        compile("\n".join(lines),f"cell_{i}.py","exec")
    except SyntaxError as ex:
        errors.append(f"Notebook: sintaxis Python en celda {i}: {ex}")

for name,html in [("deck",deck),("session",session),("wall",wall)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

front=deck+guide+session+wall+client
if re.search(r"(service[_-]?role|sb_secret_)[A-Za-z0-9_.-]{12,}",front,re.I):
    errors.append("Posible secreto privado expuesto en frontend")

if errors:
    print("SESION 09: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("SESION 09: OK")
print(" - S07 y S08 intactas")
print(" - presentación estilo S07 con laboratorio embebido")
print(" - términos nuevos definidos con ejemplos")
print(" - notebook E5 + BM25 + Atlas + fallback local")
print(" - LMS con presentación/cuaderno/guía")
print(" - tracking y WALL S09 aislados")
print(" - checkpoints formativos, no nota")
print(" - JS/Python válidos")
