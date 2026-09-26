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
wall_redirect=read("lms/teacher-wall-09.html")
client=read("lms/assets/bigdata-lms.js")
backend=read("infraestructura/lms/functions/bigdata-session9/index.ts")
seed=read("infraestructura/lms/s09-vector-search-seed.sql")
index=read("index.html")
course_text=read("lms/data/course.json")
notebook_path=ROOT/"Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb"
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"
s08=ROOT/"lms/session-08.html"

def blob_sha(path):
    b=path.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

if s07.exists() and blob_sha(s07)!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
    errors.append("S07 cambió durante S09")
if s08.exists() and blob_sha(s08)!="b5b1e9085fe99759182d141a75f875fcbab39d3a":
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

# Parsear el array real de diapositivas.
start=deck.find("const slides=[")
end_match=re.search(r"\n\];\s*\n\s*function challengeChoice",deck[start:]) if start>=0 else None
end=(start+end_match.start()) if end_match else -1
if start<0 or end<0:
    slides=[]
    errors.append("No se pudo localizar el array de diapositivas S09")
else:
    raw=deck[start:end]
    slides=[x for x in re.split(r'\n(?=\{t:[\'"])',raw) if re.search(r'\{t:[\'"]',x)]

resource_seed_start=seed.find("insert into public.lms_run_resources_v2")
resource_seed=seed[resource_seed_start:] if resource_seed_start>=0 else ""
resource_selects=len(re.findall(r"select\s+id,9,",resource_seed,re.I))

def first_slide(term):
    # Evita falsos positivos con términos cortos como k/ANN dentro de otras palabras.
    pattern=(r"(?<![A-Za-z0-9])"+re.escape(term)+r"(?![A-Za-z0-9])") if len(term)<=3 else re.escape(term)
    for i,s in enumerate(slides,1):
        if re.search(pattern,s,re.I): return i
    return None

def def_slide(marker):
    for i,s in enumerate(slides,1):
        if marker.lower() in s.lower(): return i
    return None

# Términos cuyo primer uso debe coincidir o venir después de su definición explícita.
definition_markers={
    "corpus":"<b>Corpus</b>",
    "documento":"<b>Documento</b>",
    "consulta":"<b>Consulta</b>",
    "ranking":"<b>Ranking</b>",
    "candidato":"<b>Candidato</b>",
    "score":"<b>Score</b>",
    "juicio de relevancia":"<b>Juicio de relevancia</b>",
    "recuperación lexical":"<b>Recuperación lexical</b>",
    "analyzer":"<b>Analyzer</b>",
    "token":"<b>Token</b>",
    "índice invertido":"<b>Índice invertido</b>",
    "bm25":"<b>BM25",
    "recuperación semántica":"<b>Recuperación semántica</b>",
    "búsqueda híbrida":"<b>Búsqueda híbrida</b>",
    "motor de búsqueda":"<b>Motor de búsqueda</b>",
    "vector":"<b>Vector</b>",
    "búsqueda vectorial":"<b>Búsqueda vectorial</b>",
    "embedding":"<b>Embedding</b>",
    "espacio vectorial":"<b>Espacio vectorial</b>",
    "modelo de embeddings":"<b>Modelo de embeddings</b>",
    "tokenización del modelo":"<b>Tokenización del modelo</b>",
    "encoder":"<b>Encoder</b>",
    "pooling":"<b>Pooling</b>",
    "dimensión":"<b>Dimensión</b>",
    "e5":"<b>E5</b>",
    "prefijo de tarea":"<b>Prefijo de tarea</b>",
    "chunking":"<b>Chunking</b>",
    "chunk":"<b>Chunk</b>",
    "tamaño de chunk":"<b>Tamaño de chunk</b>",
    "solapamiento":"<b>Solapamiento · overlap</b>",
    "colección":"<b>Colección</b>",
    "documento mongodb":"<b>Documento MongoDB</b>",
    "upsert":"<b>Upsert</b>",
    "idempotencia":"<b>Idempotencia</b>",
    "updateone":"<b>UpdateOne</b>",
    "bulk_write":"<b>bulk_write</b>",
    "norma":"<b>Norma</b>",
    "normalización":"<b>Normalización</b>",
    "producto punto":"<b>Producto punto</b>",
    "similitud coseno":"<b>Similitud coseno</b>",
    "knn":"<b>kNN · k-Nearest Neighbors</b>",
    "top-k":"<b>Top-k</b>",
    "falso positivo":"<b>Falso positivo</b>",
    "falso negativo":"<b>Falso negativo</b>",
    "dominio":"<b>Dominio</b>",
    "base vectorial":"<b>Base vectorial</b>",
    "metadata":"<b>Metadata</b>",
    "filtro":"<b>Filtro</b>",
    "campo de filtro":"<b>Campo de filtro</b>",
    "prefiltro":"<b>Prefiltro</b>",
    "vecino":"<b>Vecino</b>",
    "k":"<b>k</b>",
    "índice vectorial":"<b>Índice vectorial</b>",
    "enn":"<b>ENN</b>",
    "ann":"<b>ANN</b>",
    "hnsw":"<b>HNSW</b>",
    "punto de entrada":"<b>Punto de entrada</b>",
    "capa":"<b>Capa</b>",
    "conjunto de candidatos":"<b>Conjunto de candidatos</b>",
    "recall@k":"<b>Recall@k</b>",
    "latencia":"<b>Latencia</b>",
    "numcandidates":"<b>numCandidates</b>",
    "atlas vector search":"<b>Atlas Vector Search</b>",
    "search index":"<b>Search Index</b>",
    "searchindexmodel":"<b>SearchIndexModel</b>",
    "queryable":"<b>queryable</b>",
    "pipeline de agregación":"<b>Pipeline de agregación</b>",
    "etapa":"<b>Etapa · stage</b>",
    "$vectorsearch":"<b>$vectorSearch</b>",
    "vectorsearchscore":"<b>vectorSearchScore</b>",
    "fusión de rankings":"<b>Fusión de rankings</b>",
    "normalización de score":"<b>Normalización de score</b>",
    "rrf":"<b>RRF · Reciprocal Rank Fusion</b>",
    "precision@k":"<b>Precision@k</b>",
    "evidencia reproducible":"<b>Evidencia reproducible</b>",
}
for term,marker in definition_markers.items():
    first=first_slide(term)
    defined=def_slide(marker)
    if first is None:
        errors.append(f"Falta término requerido: {term}")
    elif defined is None:
        errors.append(f"Falta definición explícita: {term}")
    elif first < defined:
        errors.append(f"Término usado antes de definirse: {term} (uso S{first}, definición S{defined})")

defs=len(re.findall(r'class=(?:\\?")card def(?:\\?")',deck))
examples=len(re.findall(r'class=(?:\\?")card ex(?:\\?")',deck))
svg_functions=len(re.findall(r"function\s+svg[A-Za-z0-9_]+\s*\(",deck))
lab_numbers=set(int(x) for x in re.findall(r"LAB\s+(\d+)\s*·",deck))
challenge_calls=re.findall(r"challengeChoice\('(bd-s09-c[1-5])'",deck)
graphic_refs=set(re.findall(r'\b(svg[A-Za-z0-9_]+)\(\)',raw))
light_without_visual=[]
for i,s in enumerate(slides,1):
    visual=bool(re.search(r'svg[A-Za-z0-9_]+\(\)|<svg|class=\\?"(?:lab|table|diagram|three|cols)|<table|<pre|<select|<input|<textarea|challengeChoice\(',s,re.I))
    if len(s)<850 and not visual:
        light_without_visual.append(i)

checks=[
    ("exactamente 35 diapositivas",len(slides)==35),
    ("profundidad de definiciones",defs>=70),
    ("ejemplos explícitos",examples>=30),
    ("gráficos/diagramas",svg_functions>=15 and len(graphic_refs)>=15),
    ("diapositivas ligeras compensadas visualmente",not light_without_visual),
    ("LAB 1–9 embebidos",set(range(1,10)).issubset(lab_numbers)),
    ("D1–D5 embebidos",set(challenge_calls)=={f"bd-s09-c{i}" for i in range(1,6)}),
    ("S09 Live embebido",'id="liveDrawer"' in deck and "S09 LIVE" in deck and "renderStudentLive" in deck),
    ("Teacher Wall embebido",'id="teacherWall"' in deck and "S09 Teacher Wall" in deck and "wall')==='docente" in deck),
    ("WALL sin ranking por velocidad","No es un ranking de velocidad" in deck and "localeCompare" in backend),
    ("primer intento + dominio server-side","first_attempt_correct" in backend and "mastery" in backend and "challenge_stats" in backend),
    ("respuestas validadas por hash","CHALLENGE_HASHES" in backend and "sha256(code+\"|\"+answer)" in backend),
    ("respuesta correcta no mapeada en frontend","CHALLENGE_HASHES" not in deck and "referencia esperada" not in deck and "function c1Check" not in deck),
    ("sin bypass complete_checkpoint","complete_checkpoint" not in backend and "complete_checkpoint" not in session),
    ("dos códigos de recurso", 'const RESOURCE_CODES=new Set(["bd-s09-presentation","bd-s09-notebook"])' in backend),
    ("sin guía en backend","bd-s09-guide" not in backend and "guide_opened" not in backend),
    ("dos recursos visibles en seed",resource_selects==2 and "'guide'" not in resource_seed and "bd-s09-guide" not in resource_seed),
    ("guía histórica solo redirige","no hay un laboratorio separado" in guide and "location.replace" in guide),
    ("LMS presenta dos recursos","repeat(2,minmax(0,1fr))" in session and "guide_opened" not in session),
    ("LMS no permite marcar dominio manual","Marcar completado" not in session and "completeCheckpoint" not in session),
    ("WALL legado redirige","s09-de-palabras-a-significado.html?wall=docente" in wall_redirect and "location.replace" in wall_redirect),
    ("tool docente apunta a wall embebido",any(x.get("code")=="wall_s09" and "?wall=docente" in x.get("path","") for x in course.get("teacher_tools",[]))),
    ("portal apunta a wall embebido","teacherWall09" in read("lms/portal.html") and "?wall=docente" in read("lms/portal.html")),
    ("portal no prioriza S08 fijo","Number(x.session_number)===8" not in read("lms/portal.html")),
    ("Elasticsearch no se confunde con lexical","Elasticsearch no es sinónimo de lexical" in deck and "Elasticsearch" in deck and "Búsqueda vectorial" in deck),
    ("ruta semántica completa",all(x in deck for x in ["Embedding","Similitud coseno","k-Nearest Neighbors","Base vectorial","HNSW","Atlas Vector Search","Reciprocal Rank Fusion"])),
    ("trade-off interactivo","tradeSvg" in deck and "Recall@k" in deck and "Latencia" in deck),
    ("pipeline E5 interactivo","function embedPipeDemo" in deck and "embedRole" in deck and "embedPipeOut" in deck),
    ("chunking interactivo","function chunkDemo" in deck and "chunkSize" in deck and "chunkOverlap" in deck),
    ("operación MongoDB explicada",all(x in deck for x in ["<b>Colección</b>","<b>Upsert</b>","<b>Idempotencia</b>","<b>bulk_write</b>"])),
    ("Atlas explicado antes del constructor",all(x in deck for x in ["<b>SearchIndexModel</b>","<b>queryable</b>","<b>Pipeline de agregación</b>","<b>vectorSearchScore</b>"])),
    ("híbrida explica fusión y escalas","<b>Fusión de rankings</b>" in deck and "<b>Normalización de score</b>" in deck and "No sumes scores crudos" in deck),
    ("RRF calculable","function rrfDemo" in deck and "RRF(d) = Σ" in deck),
    ("constructor de evidencia","alternativa_descartada" in deck and "evidencia reproducible" in deck.lower()),
    ("notebook suficientemente completo",len(nb.get("cells",[]))>=20),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

nb_text="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
for label,ok in [
    ("notebook E5","intfloat/multilingual-e5-small" in nb_text and "query: " in nb_text and "passage: " in nb_text),
    ("notebook baseline lexical","BM25Okapi" in nb_text and "buscar_lexical" in nb_text),
    ("notebook semántico local","buscar_semantico_local" in nb_text and "embeddings @ q" in nb_text),
    ("notebook Atlas","SearchIndexModel" in nb_text and "$vectorSearch" in nb_text),
    ("notebook evidencia","s09_evidencia_semantica.json" in nb_text and "falso_positivo" in nb_text and "alternativa_descartada" in nb_text),
]:
    if not ok: errors.append("Falla: "+label)

# Sintaxis Python del notebook, ignorando magics.
for i,cell in enumerate(nb.get("cells",[]),1):
    if cell.get("cell_type")!="code": continue
    src="".join(cell.get("source",[]))
    lines=[ln for ln in src.splitlines() if not ln.lstrip().startswith(("%","!"))]
    if not lines: continue
    try: compile("\n".join(lines),f"s09_cell_{i}.py","exec")
    except SyntaxError as ex: errors.append(f"Notebook: sintaxis Python celda {i}: {ex}")

# Sintaxis JavaScript de artefactos HTML.
for name,html in [("presentación",deck),("session-09",session),("wall-redirect",wall_redirect)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:700]}")

front=deck+session+wall_redirect+client
if re.search(r"(service[_-]?role|sb_secret_)[A-Za-z0-9_.-]{12,}",front,re.I):
    errors.append("Posible secreto privado expuesto en frontend")

if errors:
    print("SESION 09 PROFUNDA: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("SESION 09 PROFUNDA: OK")
print(" - 35 diapositivas")
print(f" - {defs} bloques de definición · {examples} ejemplos explícitos · {len(graphic_refs)} gráficos usados")
print(" - ninguna diapositiva ligera queda sin gráfico, tabla, código o herramienta")
print(" - LAB 1–9 + evaluación embebidos")
print(" - D1–D5 con primer intento/dominio server-side")
print(" - exactamente dos recursos visibles")
print(" - S09 Live + Teacher Wall dentro de la presentación")
print(" - términos definidos antes del primer uso")
print(" - S07 y S08 intactas")
print(" - notebook/JS válidos")
