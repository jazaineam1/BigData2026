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

# Deuda conocida, todavía sin cerrar: se informa, no falla (ver plan V54-B).
pending = []
for rel in ["infraestructura/lms/functions/bigdata-lms-assess/index.ts",
            "infraestructura/lms/functions/bigdata-lms-interop/index.ts",
            "infraestructura/lms/lms-assessment-engine-v2.sql"]:
    n = read(rel).count("short_text")
    if n:
        pending.append(f"{rel}: {n} mención(es) de short_text")

if errors:
    print("SIN RESPUESTAS ABIERTAS: FAIL")
    for e in errors:
        print(" -", e)
    sys.exit(1)

print("SIN RESPUESTAS ABIERTAS: OK")
print(f" - {checked} superficies revisadas; {len(ALLOWLIST)} excepciones declaradas con razón")
print(" - entregas, colaboración y muro sin texto libre del estudiante")
print(" - el backend rechaza lo que la UI ya no ofrece")
for x in pending:
    print(" ! PENDIENTE V54-B:", x)
