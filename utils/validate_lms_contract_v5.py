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

def blob_sha(path):
    p=ROOT/path
    b=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

course_text=read("lms/data/course.json")
index=read("index.html")
session=read("lms/session.html")
progress=read("lms/progress.html")
wall=read("lms/wall.html")
class_wall=read("lms/class-wall.html")
client=read("lms/assets/bigdata-lms.js")
kit=read("lms/assets/lms-kit.js")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
migration=read("infraestructura/lms/lms-runtime-v5.sql")
evidence_sql=read("infraestructura/lms/lms-evidence-v4.sql")
legacy_session=read("lms/session-09.html")
legacy_progress=read("lms/progress-09.html")
legacy_wall=read("lms/teacher-wall-09.html")
pages=read(".github/workflows/pages.yml")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

sessions=course.get("sessions",[])
visible=[s for s in sessions if s.get("status")=="visible"]
nums=[int(s.get("n",0)) for s in sessions]
labs=set(re.findall(r"bd-s09-lab(?:-e5|-chunk|-eval|\d+)",deck))

checks=[
    ("16 sesiones declaradas",course.get("total_sessions")==16 and nums==list(range(1,17))),
    ("course.json declara contrato V5",course.get("version",0)>=12 and "LMS V5" in course.get("tracking_policy","")),
    ("módulo universal", "requireSession(sessionNumber)" in session and "session.html?s=" not in session),
    ("progreso universal", "L.session('course_progress')" in progress and "session.html?s=" in progress),
    ("WALL universal", "requireSession(sessionNumber,{teacher:true})" in wall),
    ("máximo dos recursos en módulo", "slice(0,2)" in session),
    ("regla SQL máximo dos recursos", "x.rn>2" in evidence_sql and "integrated_support" in evidence_sql),
    # Desde 2026-10-02 la portada abre el material en un clic (AGENTS.md §12):
    # el Colab directo ya no es una fuga del LMS, es la regla.
    ("portada sin marcar revisada", "Marcar revisada" not in index),
    ("portada: S08 abre Colab en un clic", "Cuadernos/Taller_Control_1.ipynb" in index and "lms/session.html?s=8" not in index),
    ("runtime único V5", "window.LMS=api" in kit and "lms.bigdata.queue.v1" in kit),
    ("cola limitada", "MAX_QUEUE=500" in kit and "compactQueue" in kit),
    ("prioriza evidencia", "entry.kind==='evidence'||entry.kind==='wall_post'" in kit),
    ("retry escalonado", "RETRY_MS=[1000,2000,4000,8000,30000]" in kit),
    ("pagehide autenticado usa keepalive", "keepalive:true" in kit and "'Authorization':'Bearer '+auth.token" in kit),
    ("safeNext allowlist", "/BigData2026/Presentaciones/" in client and "/BigData2026/assets/tutoriales/" in client),
    ("idempotencia eventos", "client_event_id" in migration and "bd_lms_events_client_event_uidx" in migration and "client_event_id:eventClientId" in backend),
    ("idempotencia evidencia", "client_evidence_id" in migration and "bd_evidence_client_evidence_uidx" in migration and "client_evidence_id:evidenceClientId" in backend),
    ("idempotencia muro", "client_post_id" in migration and "bd_wall_posts_client_post_uidx" in migration and "client_post_id:postClientId" in backend),
    ("S09 usa runtime V5", "lms-kit.js?v=20260926-v5" in deck and "K.track('lab_interaction'" in deck and "K.evidence(" in deck),
    ("módulo usa runtime V5", "lms-kit.js?v=20260926-v5" in session and "K.track(" in session),
    ("muro estudiantil sin publicación abierta", "K.wallPost(" not in class_wall),
    ("bridge de recursos usa runtime V5", "loadKit" in read("lms/assets/resource-bridge.js") and "K.track('guide_opened'" in read("lms/assets/resource-bridge.js")),
    ("12 LAB S09 declarados en presentación", len(labs)==12),
    ("legacy módulo redirige", "session.html?" in legacy_session and "p.set('s','9')" in legacy_session),
    ("legacy progreso redirige", "progress.html?" in legacy_progress and "p.set('s','9')" in legacy_progress),
    ("legacy WALL redirige", "wall.html?" in legacy_wall and "p.set('s','9')" in legacy_wall),
    ("Pages hace smoke test público", "Smoke test del sitio publicado" in pages and "bg-masthead.jpg" in pages),
]

for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

# No permitir nuevas páginas de sesión específicas: S08 es protegida y S09 solo redirect legacy.
legacy_files=sorted(p.name for p in (ROOT/"lms").glob("session-[0-9][0-9].html"))
unexpected=[x for x in legacy_files if x not in {"session-08.html","session-09.html"}]
if unexpected:
    errors.append("Páginas de sesión específicas no permitidas: "+", ".join(unexpected))

for path,sha in [
    ("Presentaciones/s07-del-vecindario-al-texto.html","07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8"),
    ("lms/session-08.html","e22893a179d2d7117f0f178c59f6f2ff4aa5b372"),
]:
    if (ROOT/path).exists() and blob_sha(path)!=sha:
        errors.append(f"Protección SHA violada: {path}")

# Sintaxis JS del runtime y de las superficies tocadas.
for name,src in [("lms-kit",kit)]:
    with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
        fh.write(src);tmp=fh.name
    p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
    Path(tmp).unlink(missing_ok=True)
    if p.returncode:
        errors.append(f"{name}: {p.stderr.strip()[:800]}")

if errors:
    print("LMS CONTRACT V5: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("LMS CONTRACT V5: OK")
print(f" - {len(visible)} sesiones visibles · {len(sessions)} declaradas")
print(" - módulo/progreso/WALL universales")
print(" - máximo dos recursos")
print(" - runtime offline con retry e idempotencia")
print(" - rutas S09 legacy son redirects")
print(" - S07/S08 protegidas")
