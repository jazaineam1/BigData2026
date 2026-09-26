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

portal=read("lms/portal.html")
teacher=read("lms/teacher-course.html")
client=read("lms/assets/bigdata-lms.js")
edge=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
sql=read("infraestructura/lms/lms-run-backbone-v2.sql")
pages=read(".github/workflows/pages.yml")
course_text=read("lms/data/course.json")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

try:
    course=json.loads(course_text)
except Exception as e:
    course={}
    errors.append(f"course.json inválido: {e}")

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante la columna vertebral LMS")

checks=[
    ("16 sesiones declaradas", len(course.get("sessions",[]))==16 and [x.get("n") for x in course.get("sessions",[])]==list(range(1,17))),
    ("S09-S16 siguen borrador", all(x.get("status")=="draft" for x in course.get("sessions",[]) if x.get("n",0)>=9)),
    ("S07 marcada protegida", any(x.get("n")==7 and x.get("protected") for x in course.get("sessions",[]))),
    ("portal usa API core", "L.core('home')" in portal and "sessions" in portal and "announcements" in portal and "pending" in portal),
    ("cliente conecta bigdata-lms-core", "bigdata-lms-core" in client and "async function core" in client),
    ("gestor docente exige rol", "requireBigData({teacher:true})" in teacher),
    ("gestor publica/cierra sesiones", "teacher_save_session" in teacher and "teacher_save_session" in edge),
    ("gestor administra anuncios", "teacher_save_announcement" in teacher and "teacher_delete_announcement" in edge),
    ("gestor administra recursos", "teacher_save_resource" in teacher and "teacher_delete_resource" in edge),
    ("sesiones son course-run scoped", "primary key (course_run_id, session_number)" in sql),
    ("recursos son course-run scoped", "references public.lms_run_sessions_v2(course_run_id, session_number)" in sql),
    ("RLS backbone", sql.count("enable row level security")>=2),
    ("sin acceso directo anon/authenticated", sql.count("revoke all")>=2 and "anon, authenticated" in sql),
    ("Pages verifica gestor", "test -f _site/lms/teacher-course.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("portal",portal),("teacher",teacher)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",text,re.S|re.I)
    if not scripts:
        errors.append(f"{name}: sin script inline")
        continue
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode: errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

if re.search(r"(service[_-]?role|sb_secret).{0,100}(eyJ|[A-Za-z0-9_-]{30,})",portal+"\n"+teacher+"\n"+client,re.I|re.S):
    errors.append("Posible secreto expuesto en frontend")

if errors:
    print("LMS CORE: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("LMS CORE: OK")
print(" - S01-S16 declaradas")
print(" - S07 intacta")
print(" - portal + gestor docente + API core")
print(" - sesiones/recursos por cohorte")
print(" - JS válido")
