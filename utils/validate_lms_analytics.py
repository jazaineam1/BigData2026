#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

progress=read("lms/progress.html")
teacher=read("lms/teacher-analytics.html")
portal=read("lms/portal.html")
assign=read("lms/assignments.html")
comp=read("lms/competencies.html")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
sql=read("infraestructura/lms/lms-analytics-interventions-v2.sql")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante analítica")

checks=[
    ("portal enlaza progreso", 'href="progress.html"' in portal),
    ("portal enlaza analítica docente", 'href="teacher-analytics.html"' in portal),
    ("progreso compara consigo mismo", "Compárate contigo" in progress and "events_previous_7_days" in progress),
    ("progreso no usa tiempo como nota", "No usa velocidad ni tiempo conectado como nota" in progress),
    ("analítica evita etiqueta opaca", "Señales para mirar, no etiquetas para decidir" in teacher),
    ("señales muestran razón", "reason" in teacher and "signals" in teacher),
    ("reglas configurables", "teacher_save_analytics_rule" in teacher and "saveAnalyticsRule" in core),
    ("intervenciones privadas", "teacher_save_intervention" in teacher and "lms_interventions_v2" in core),
    ("telemetría académica genérica", "track_learning_event" in core and "lms_learning_events_v2" in core),
    ("entrega registra evento backend", 'event_type:"assignment_submitted"' in core),
    ("portal registra actividad", "portal_opened" in portal),
    ("entregas registran actividad", "assignments_opened" in assign),
    ("competencias registran actividad", "competencies_opened" in comp),
    ("RLS analítica", sql.count("enable row level security")>=3),
    ("sin acceso directo público", "from anon, authenticated" in sql and "to service_role" in sql),
    ("intervenciones course-scoped", "course_run_id uuid not null" in sql and "eq(\"course_run_id\",run.id)" in core),
    ("Pages publica progreso", "test -f _site/lms/progress.html" in pages),
    ("Pages publica analítica", "test -f _site/lms/teacher-analytics.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("progress",progress),("teacher-analytics",teacher)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",text,re.S|re.I)
    if not scripts:
        errors.append(f"{name}: sin script inline")
        continue
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

if re.search(r"(service[_-]?role|sb_secret).{0,100}(eyJ|[A-Za-z0-9_-]{30,})",progress+"\n"+teacher+"\n"+portal,re.I|re.S):
    errors.append("Posible secreto expuesto en frontend")

if errors:
    print("ANALITICA LMS: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("ANALITICA LMS: OK")
print(" - señales explicables y configurables")
print(" - comparación personal")
print(" - intervenciones privadas y auditables")
print(" - S07 intacta")
print(" - JS válido")
