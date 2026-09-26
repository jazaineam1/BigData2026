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

student=read("lms/progress.html")
teacher=read("lms/teacher-analytics.html")
portal=read("lms/portal.html")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
sql=read("infraestructura/lms/lms-analytics-v2.sql")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante analítica")

checks=[
    ("portal enlaza progreso", 'href="progress.html"' in portal),
    ("vista estudiante usa analytics", "L.core('analytics')" in student and "Reglas transparentes" in student),
    ("vista docente exige rol", "requireBigData({teacher:true})" in teacher),
    ("backend analytics estudiante", "analyticsForUser" in core and 'action==="analytics"' in core),
    ("backend analytics docente", "teacherAnalytics" in core and 'action==="teacher_analytics"' in core),
    ("reglas explicables", "evaluateAlerts" in core and "rule_type" in core and "evidence" in core),
    ("separa señal docente", 'kind:"teacher"' in core and 'kind:"student"' in core),
    ("intervenciones trazables", "teacher_create_intervention" in teacher and "lms_interventions_v2" in core),
    ("resolución de intervención", "teacher_resolve_intervention" in teacher and "resolveIntervention" in core),
    ("snapshots diarios", "lms_student_snapshots_v2" in core and "snapshot_date" in sql),
    ("fricción S08", "bd_lms_activity_progress" in core and "friction" in teacher),
    ("RLS analytics", sql.count("enable row level security")>=3),
    ("sin acceso directo", "from anon, authenticated" in sql and "to service_role" in sql),
    ("Pages progreso", "test -f _site/lms/progress.html" in pages),
    ("Pages analítica docente", "test -f _site/lms/teacher-analytics.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("progress",student),("teacher-analytics",teacher)]:
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
    print("ANALITICA: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("ANALITICA: OK")
print(" - reglas explicables")
print(" - señales estudiante/docente separadas")
print(" - intervenciones + snapshots")
print(" - S07 intacta")
print(" - JS válido")
