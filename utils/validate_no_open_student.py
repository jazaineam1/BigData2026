#!/usr/bin/env python3
"""Guardia global: el estudiante no escribe respuestas académicas abiertas.

Criterio (AGENTS.md §4): decisiones, alternativas y límites se capturan con opciones
estructuradas, números, código ejecutado, archivos, URLs o evidencia verificable.

Distingue dos cosas que se parecen y no son lo mismo:
- un <textarea> que ENVÍA una respuesta académica  -> prohibido en superficies de estudiante;
- un <textarea> que es una HERRAMIENTA (probar un tokenizer, una consulta) o un formulario
  del DOCENTE                                       -> permitido, pero solo si está en ALLOWLIST.

Agregar un textarea nuevo obliga a declararlo aquí con su razón, no a esquivar la guardia.
"""
from pathlib import Path
import os
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

def read(path):
    p = ROOT / path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

# (archivo, identificador del textarea) -> por qué es legítimo
ALLOWLIST = {
    ("lms/gradebook.html", "feedback"): "docente: retroalimentación al calificar",
    ("lms/gradebook.html", "notes"): "docente: nota privada de una excepción",
    ("lms/gradebook.html", "instructions"): "docente: instrucciones de la tarea que crea",
    ("lms/wall.html", "data-review-feedback"): "docente: revisión de evidencia",
    ("Presentaciones/s09-de-palabras-a-significado.html", "caseQ"): "herramienta: consulta de ejemplo precargada",
    ("Presentaciones/s09-de-palabras-a-significado.html", "embedText"): "herramienta: texto para el demo de embeddings",
    ("Presentaciones/s09-de-palabras-a-significado.html", "chunkText"): "herramienta: texto para el demo de chunking",
    ("Presentaciones/s07-del-vecindario-al-texto.html", "tokText"): "herramienta: texto para el demo de tokenizer",
}

# Campos <input> de texto en superficies de estudiante de lms/ (las presentaciones se cubren con la
# regla de telemetría de más abajo: sus campos son herramientas y no envían su contenido).
INPUT_ALLOWLIST = {
    ("lms/access.html", "email"): "acceso: correo de la cuenta",
    ("lms/access.html", "full_name"): "acceso: nombre de la cuenta, no una respuesta académica",
    ("lms/access.html", "website"): "acceso: campo trampa anti-bots, permanece vacío",
    ("lms/portal.html", "username"): "acceso: usuario para iniciar sesión",
    ("lms/gradebook.html", "code"): "docente: código de la tarea",
    ("lms/gradebook.html", "title"): "docente: título de la tarea",
    ("lms/gradebook.html", "category"): "docente: categoría de la tarea",
    ("lms/gradebook.html", "templateCode"): "docente: plantilla de tarea",
    ("lms/gradebook.html", "templateTitle"): "docente: plantilla de tarea",
    ("lms/gradebook.html", "templateDescription"): "docente: plantilla de tarea",
    ("lms/gradebook.html", "?"): "docente: filas de rúbrica",
    ("lms/wall.html", "search"): "docente: filtro del muro",
    ("lms/wall.html", "controlHint"): "docente: pista que publica el docente",
    ("lms/wall.html", "resetInput"): "docente: frase de confirmación para reiniciar",
}

def text_inputs(html):
    out = []
    for attrs in re.findall(r"<input\b([^>]*)>", html, re.I):
        attrs = attrs.replace("\\", "")
        t = re.search(r'\btype="([^"]+)"', attrs)
        if (t.group(1).lower() if t else "text") in ("text", "search", "email"):
            m = re.search(r'\bname="([^"]+)"', attrs) or re.search(r'\bid="([^"]+)"', attrs)
            out.append(m.group(1) if m else "?")
    return out

def surfaces():
    for p in sorted((ROOT / "lms").glob("*.html")):
        if p.name.startswith(("teacher-", "admin-")) or p.name == "index.html":
            continue
        yield p
    yield from sorted((ROOT / "Presentaciones").glob("*.html"))
    yield from sorted((ROOT / "assets/tutoriales").glob("*.html"))

def textarea_ids(html):
    """Identificador de cada <textarea>, tolerando comillas escapadas dentro de strings JS."""
    out = []
    for attrs in re.findall(r"<textarea\b([^>]*)>", html, re.I):
        attrs = attrs.replace("\\", "")
        m = (re.search(r'\bname="([^"]+)"', attrs) or re.search(r'\bid="([^"]+)"', attrs)
             or re.search(r'\b(data-[\w-]+)=', attrs))
        out.append(m.group(1) if m else "(sin identificador)")
    return out

checked = 0
for p in surfaces():
    rel = p.relative_to(ROOT).as_posix()
    html = p.read_text("utf-8")
    checked += 1
    for ident in textarea_ids(html):
        if (rel, ident) not in ALLOWLIST:
            errors.append(f"{rel}: <textarea> '{ident}' no está en la lista de excepciones (¿respuesta abierta del estudiante?)")
    if "contenteditable" in html.lower() and not rel.startswith("Presentaciones/"):
        errors.append(f"{rel}: contenteditable fuera de una herramienta de presentación")
    if rel.startswith("lms/"):
        for ident in text_inputs(html):
            if (rel, ident) not in INPUT_ALLOWLIST:
                errors.append(f"{rel}: <input> de texto '{ident}' no está en la lista de excepciones (¿respuesta abierta del estudiante?)")
        for token in ("createElement('textarea')", 'createElement("textarea")', "contentEditable", 'role="textbox"', " prompt("):
            if token in html:
                errors.append(f"{rel}: campo de texto creado por script o prompt ({token.strip()})")

# Las páginas de estudiante que antes enviaban texto no pueden volver a hacerlo.
FORBIDDEN_PAYLOADS = [
    "contribution_text", "create_thread", "post_discussion", "artifact_type:'text'",
    'name="text"', 'value="text"', "feedback:f.feedback", "text:f.text",
]
for rel in ["lms/assignments.html", "lms/collaboration.html"]:
    src = read(rel)
    for token in FORBIDDEN_PAYLOADS:
        if token in src:
            errors.append(f"{rel}: conserva '{token}' (payload de texto libre)")

# El backend debe rechazar lo que la UI ya no ofrece: no basta con esconder el formulario.
core = read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
session = read("infraestructura/lms/functions/bigdata-session/index.ts")
backend_checks = [
    ("entrega individual rechaza texto", "Las entregas de texto libre ya no están habilitadas" in core),
    ("tipos de entrega del estudiante sin 'text'", 'STUDENT_ARTIFACT_TYPES=["url","file","evidence"]' in core),
    ("entrega grupal solo URL", 'if(type!=="url")throw new Error("La entrega grupal admite solo URL de evidencia")' in core),
    ("contribución solo por lista cerrada", "function contributionRole(" in core and not re.search(r"body\.contribution_text", core)),
    ("crear conversación solo docente", re.search(r"async function createThread\([^)]*\)\{\s*requireTeacher\(ctx\)", core) is not None),
    ("responder conversación solo docente", re.search(r"async function postDiscussion\([^)]*\)\{\s*requireTeacher\(ctx\)", core) is not None),
    ("peer review sin comentario libre", not re.search(r"body\.feedback", core.split("async function submitPeerReview")[-1].split("\nasync function")[0])),
    ("muro: publicar texto rechazado al estudiante (primera sentencia)", re.search(r"async function wallPost\([^)]*\)\{\s*if\(!\[\"teacher\",\"admin\"\]\.includes\(ctx\.user\.role\)\)throw new Error\(\"El muro abierto fue retirado", session) is not None),
]
for label, ok in backend_checks:
    if not ok:
        errors.append("Backend: " + label)

# La telemetría de los LAB no puede llevar el contenido de campos de texto al backend: solo su longitud.
s09 = read("Presentaciones/s09-de-palabras-a-significado.html")
if "el.tagName==='INPUT'&&!['checkbox','radio','range','number'].includes(el.type)" not in s09:
    errors.append("S09: labControlValue envía el contenido de campos <input> de texto al backend (debe enviar solo len:N)")

# V54-B · Tipos de pregunta: solo respuestas cerradas u objetivas, en todas las capas.
# El tipo abierto retirado solo puede aparecer donde LEE historia (declarado una vez como constante) o donde se
# prohíbe (la migración, la guardia, el validador de interop). Cualquier otro archivo que lo nombre es una
# reintroducción: la CI falla y quien la haga debe declarar aquí su razón, no esquivar la guardia.
QUESTION_TYPES = ["single_choice", "multiple_choice", "true_false", "numeric"]
RETIRED_TYPE = "short_text"
RETIRED_ALLOWLIST = {
    "infraestructura/lms/functions/bigdata-lms-assess/index.ts": "declara LEGACY_OPEN_TYPE una vez; solo lee y califica historia",
    "infraestructura/lms/functions/bigdata-lms-interop/index.ts": "declara LEGACY_OPEN_TYPE una vez; solo para omitir y avisar al exportar",
    "infraestructura/lms/lms-assessment-engine-v2.sql": "migración histórica ya aplicada; la sustituye lms-v54b-question-types.sql",
    "infraestructura/lms/lms-v54b-question-types.sql": "la migración que lo prohíbe",
    "utils/validate_no_open_student.py": "esta guardia",
    "utils/validate_lms_interop.py": "comprueba que la exportación QTI no lo emite",
}
SCAN_SUFFIXES = {".ts", ".js", ".mjs", ".html", ".sql", ".py", ".json", ".yml", ".yaml"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".local-docente"}
for dirpath, dirnames, filenames in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
    for name in filenames:
        p = Path(dirpath) / name
        if p.suffix.lower() not in SCAN_SUFFIXES:
            continue
        rel = p.relative_to(ROOT).as_posix()
        if rel in RETIRED_ALLOWLIST:
            continue
        if RETIRED_TYPE in p.read_text("utf-8", errors="replace"):
            errors.append(f"{rel}: menciona el tipo de pregunta retirado '{RETIRED_TYPE}' (respuesta abierta)")

def types_in(list_src):
    return re.findall(r"""["']([a-z_]+)["']""", list_src)

def strip_sql_comments(sql):
    return "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--"))

assess = read("infraestructura/lms/functions/bigdata-lms-assess/index.ts")
interop = read("infraestructura/lms/functions/bigdata-lms-interop/index.ts")
m = re.search(r"const ACTIVE_QUESTION_TYPES=\[([^\]]*)\]", assess)
clean_response = assess.split("function cleanResponse")[-1].split("async function saveResponse")[0]
question_checks = [
    ("API: tipos activos de pregunta = los 4 objetivos", bool(m) and types_in(m.group(1)) == QUESTION_TYPES),
    ("API: el tipo retirado se declara una sola vez (LEGACY_OPEN_TYPE)",
     assess.count(f'"{RETIRED_TYPE}"') == 1 and f'const LEGACY_OPEN_TYPE="{RETIRED_TYPE}";' in assess),
    ("API: crear pregunta valida contra ACTIVE_QUESTION_TYPES", "if(!ACTIVE_QUESTION_TYPES.includes(type))throw" in assess),
    ("API: agregar pregunta a un quiz rechaza el tipo retirado",
     "!ACTIVE_QUESTION_TYPES.includes(q.question_type)" in assess.split("async function setQuizItems")[-1].split("function publicQuestion")[0]),
    ("API: no se versiona una pregunta del tipo retirado", "prior.question_type===LEGACY_OPEN_TYPE)throw" in assess),
    ("API: responder el tipo retirado se rechaza y no guarda texto",
     "question_type===LEGACY_OPEN_TYPE)throw new Error" in clean_response and "text:" not in clean_response),
    ("QTI: exportación con los mismos 4 tipos y sin ítem de texto",
     'const QTI_EXPORT_TYPES=["single_choice","multiple_choice","true_false","numeric"];' in interop
     and "<qti-extended-text-interaction" not in interop and interop.count(f'"{RETIRED_TYPE}"') == 1),
]
migration = read("infraestructura/lms/lms-v54b-question-types.sql")
mig_code = strip_sql_comments(migration).lower()
mm = re.search(r"check\s*\(\s*question_type\s+in\s*\(([^)]*)\)\s*\)\s*not\s+valid", mig_code)
question_checks += [
    ("BD: la migración V54-B fija el CHECK con los 4 tipos y NOT VALID", bool(mm) and types_in(mm.group(1)) == QUESTION_TYPES),
    ("BD: la migración no nombra el tipo retirado en código ejecutable", RETIRED_TYPE not in mig_code),
    ("BD: la migración descubre el CHECK viejo y es idempotente", "pg_constraint" in mig_code and "if not exists" in mig_code),
    ("BD: la migración inicial remite a V54-B", "lms-v54b-question-types.sql" in read("infraestructura/lms/lms-assessment-engine-v2.sql")),
]
teacher_q = read("lms/teacher-quizzes.html")
sel = re.search(r'<select[^>]*name="question_type"[^>]*>(.*?)</select>', teacher_q, re.S)
question_checks += [
    ("UI docente: el selector de tipo ofrece solo los 4 tipos",
     bool(sel) and re.findall(r'<option value="([^"]+)"', sel.group(1)) == QUESTION_TYPES),
    ("UI estudiante: no envía texto libre en quizzes", "{text:" not in read("lms/quizzes.html")),
    ("Docs: STANDARDS.md declara el tipo retirado y no lo lista como mapeo vigente",
     "Tipo retirado" in read("infraestructura/lms/STANDARDS.md")
     and f"- `{RETIRED_TYPE}` →" not in read("infraestructura/lms/STANDARDS.md")),
]
for label, ok in question_checks:
    if not ok:
        errors.append("Tipos de pregunta: " + label)

# Laboratorios en cuadernos: el estudiante decide ELIGIENDO, no redactando (AGENTS.md §4). Una celda que deja
# una variable de respuesta vacía o con instrucciones para redactar ("explica…", "qué…") captura texto libre.
# Un menú de Colab (`#@param [...]`) es una lista cerrada y no cuenta. Los `input()` no se miran: en su mayoría
# piden configuración (URI, claves), no respuestas académicas.
import json

ANSWER_VAR = re.compile(
    r"""^\s*(raz[oó]n|decisi[oó]n|alternativa\w*|l[ií]mite|justificaci[oó]n|explicaci[oó]n|conclusi[oó]n|reflexi[oó]n|"""
    r"""interpretaci[oó]n|comentario|respuesta\w*|hip[oó]tesis)\s*=\s*(["'])(.*?)\2\s*(?:#(?!@param).*)?$""", re.I)
INSTRUCTION = re.compile(r"^(explica\b|escribe\b|describe\b|indica\b|justifica\b|redacta\b|qu[eé]\b|por qu[eé]\b|c[oó]mo\b|"
                         r"cu[aá]l\b|ID o nombre\b)", re.I)

def asks_to_write(value):
    """Vacía, o con instrucciones para que el estudiante redacte. Un texto ya escrito por el autor no cuenta."""
    v = value.strip()
    return v == "" or bool(INSTRUCTION.match(v))

# Cuadernos anteriores a la regla que aún capturan texto libre: se migran, y esta lista solo puede encogerse.
LEGACY_NOTEBOOKS = {
    "Cuadernos/Quiz_Neo4j_Fundamentos.ipynb":
        "quiz de práctica anterior a la regla: deja razon, alternativa_descartada y explicacion vacías para escribirlas; migrar a opciones cerradas",
}

def notebook_open_answers(path):
    try:
        nb = json.loads(path.read_text("utf-8-sig"))
    except (OSError, ValueError):
        return [("(ilegible)", 0)]
    found = []
    for i, cell in enumerate(nb.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        for line in "".join(cell.get("source", [])).splitlines():
            if "#@param" in line:
                continue
            m = ANSWER_VAR.match(line)
            if m and asks_to_write(m.group(3)):
                found.append((m.group(1), i))
    return found

nb_checked, legacy_seen = 0, set()
for nbp in sorted((ROOT / "Cuadernos").glob("*.ipynb")):
    rel = nbp.relative_to(ROOT).as_posix()
    nb_checked += 1
    hits = notebook_open_answers(nbp)
    if hits and rel in LEGACY_NOTEBOOKS:
        legacy_seen.add(rel)
    elif hits:
        vars_ = ", ".join(sorted({f"{v} (celda {c})" for v, c in hits})[:4])
        errors.append(f"{rel}: pide texto libre en una celda ({vars_}); usa una lista cerrada (`#@param [...]`) y rechaza lo demás")
for rel in LEGACY_NOTEBOOKS:
    if rel not in legacy_seen:
        errors.append(f"LEGACY_NOTEBOOKS obsoleto: {rel} ya no captura texto libre; bórralo de la lista")

if errors:
    print("SIN RESPUESTAS ABIERTAS: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("SIN RESPUESTAS ABIERTAS: OK")
print(f" - {checked} superficies revisadas; {len(ALLOWLIST)} excepciones declaradas con razón")
print(" - entregas, colaboración y muro sin texto libre del estudiante")
print(" - el backend rechaza lo que la UI ya no ofrece")
print(f" - laboratorios en cuadernos: {nb_checked} revisados, ninguno nuevo pide texto libre; pendientes de migrar: {', '.join(sorted(legacy_seen)) or 'ninguno'}")
print(f" - tipos de pregunta: solo {', '.join(QUESTION_TYPES)} (UI, API, BD, QTI y docs); el tipo abierto retirado solo se lee como historia")
