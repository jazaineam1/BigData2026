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

student=read("lms/competencies.html")
teacher=read("lms/teacher-competencies.html")
portal=read("lms/portal.html")
grade=read("lms/gradebook.html")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
sql=read("infraestructura/lms/lms-competencies-v2.sql")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante competencias")

checks=[
    ("portal enlaza competencias", 'href="competencies.html"' in portal),
    ("gradebook enlaza matriz", 'href="teacher-competencies.html"' in grade),
    ("vista estudiante usa evidencia", "L.core('competencies')" in student and "Por qué aparece así" in student),
    ("matriz docente usa backend", "teacher_competencies" in teacher and "teacherCompetencies" in core),
    ("cálculo por rúbrica", "rubric_scores" in core and "rubric_code" in core and "mastery_pct" in core),
    ("umbral explícito", "mastery_threshold" in student and "mastery_threshold" in core),
    ("mínimo de evidencia", "min_evidence_count" in student and "min_evidence_count" in core),
    ("crear competencia", "teacher_save_competency" in teacher and "saveCompetency" in core),
    ("mapear evidencia", "teacher_map_competency" in teacher and "mapCompetency" in core),
    ("desmapear evidencia", "teacher_unmap_competency" in teacher and "unmapCompetency" in core),
    ("modelo por cohorte", "primary key(course_run_id,code)" in sql),
    ("mapeo assignment-competency", "lms_assignment_competencies_v2" in sql),
    ("RLS competencias", sql.count("enable row level security")>=2),
    ("sin acceso directo", "from anon, authenticated" in sql and "to service_role" in sql),
    ("Pages estudiante", "test -f _site/lms/competencies.html" in pages),
    ("Pages docente", "test -f _site/lms/teacher-competencies.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("competencies",student),("teacher-competencies",teacher)]:
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

if re.search(r"(service[_-]?role|sb_secret).{0,100}(eyJ|[A-Za-z0-9_-]{30,})",student+"\n"+teacher,re.I|re.S):
    errors.append("Posible secreto expuesto en frontend")

if errors:
    print("COMPETENCIAS: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("COMPETENCIAS: OK")
print(" - evidencia específica por rúbrica")
print(" - umbral + mínimo de evidencias")
print(" - matriz docente")
print(" - S07 intacta")
print(" - JS válido")
