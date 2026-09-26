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

assign=read("lms/assignments.html")
grade=read("lms/gradebook.html")
portal=read("lms/portal.html")
teacher=read("lms/teacher-course.html")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
s08edge=read("infraestructura/lms/functions/bigdata-learning/index.ts")
sql=read("infraestructura/lms/lms-gradebook-v2.sql")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante Gradebook")

checks=[
    ("portal enlaza entregas", 'href="assignments.html"' in portal),
    ("gestor enlaza gradebook", 'href="gradebook.html"' in teacher),
    ("estudiante lista tareas", "L.core('assignments')" in assign),
    ("estudiante entrega intento", "submit_assignment" in assign and "submitAssignment" in core),
    ("S08 usa evidencia automática", "bd-s08-control" in assign and "syncManifestGroupGradebook" in s08edge and "lms_group_submissions_v2" in s08edge),
    ("docente abre gradebook", "teacher_gradebook" in grade and "gradebook(ctx" in core),
    ("docente crea tarea", "teacher_save_assignment" in grade and "saveAssignment" in core),
    ("rúbrica validada", "cleanRubric" in core and "La suma de la rúbrica" in core),
    ("calificación auditada", "teacher_grade_submission" in grade and "lms_grade_history_v2" in core),
    ("excepción individual", "teacher_set_accommodation" in grade and "lms_assignment_accommodations_v2" in core),
    ("historial de nota", "teacher_grade_history" in grade and "gradeHistory" in core),
    ("modelo assignments course-run scoped", "unique(course_run_id,code)" in sql),
    ("modelo submissions con intentos", "unique(assignment_id,user_id,attempt)" in sql),
    ("evidence permitido", "('text','url','file','evidence')" in sql),
    ("RLS gradebook", sql.count("enable row level security")>=4),
    ("sin acceso directo público", "from anon, authenticated" in sql and "to service_role" in sql),
    ("Pages publica entregas", "test -f _site/lms/assignments.html" in pages),
    ("Pages publica gradebook", "test -f _site/lms/gradebook.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("assignments",assign),("gradebook",grade)]:
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

public=assign+"\n"+grade+"\n"+portal
if re.search(r"(service[_-]?role|sb_secret).{0,100}(eyJ|[A-Za-z0-9_-]{30,})",public,re.I|re.S):
    errors.append("Posible secreto expuesto en frontend")

if errors:
    print("GRADEBOOK: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("GRADEBOOK: OK")
print(" - tareas + intentos + rúbrica")
print(" - S08 sincronizada")
print(" - historial y excepciones")
print(" - S07 intacta")
print(" - JS válido")
