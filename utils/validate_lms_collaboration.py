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

student=read("lms/collaboration.html")
teacher=read("lms/teacher-collaboration.html")
portal=read("lms/portal.html")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
sql=read("infraestructura/lms/lms-collaboration-v2.sql")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante colaboración")

checks=[
    ("colaboración no satura portal estudiante", 'href="collaboration.html"' not in portal),
    ("vista estudiante usa backend", "L.core('collaboration')" in student),
    ("vista estudiante solo lectura", all(x in student for x in ["Tu equipo y su estado.","Quién trabaja contigo","Entregas registradas"]) and "<textarea" not in student and "<form" not in student),
    ("sin discusión estudiante", all(x not in student for x in ["create_thread","post_discussion","Nueva conversación","Revisión por pares","submit_peer_review"])),
    ("sin entrega textual grupal estudiante", all(x not in student for x in ["group_submit","confirm_contribution",'value="text"',"contribution_text"])),
    ("backend no expone mutaciones abiertas de estudiante", all(x not in core for x in ['if(action==="group_submit")','if(action==="confirm_contribution")','if(action==="submit_peer_review")'])),
    ("discusión backend solo docente", "async function createThread(ctx:any,run:any,body:any){\n  requireTeacher(ctx);" in core and "async function postDiscussion(ctx:any,run:any,body:any){\n  requireTeacher(ctx);" in core),
    ("payload colaboración estudiante sin posts", "peer_targets" not in core[core.find("async function collaborationOverview"):core.find("async function markMentionsRead")] and "threads:" not in core[core.find("async function collaborationOverview"):core.find("async function markMentionsRead")]),
    ("vista docente exige rol", "requireBigData({teacher:true})" in teacher),
    ("gestión de equipos", "teacher_create_group" in teacher and "createGroup" in core),
    ("miembros auditables", "teacher_add_group_member" in teacher and "teacher_remove_group_member" in core),
    ("revisión abierta por pares deshabilitada", 'peer_review_enabled:false' in core and 'name="peer_review_enabled"' not in teacher),
    ("nota grupal histórica sincroniza gradebook", "teacher_grade_group_submission" in teacher and "lms_grade_history_v2" in core),
    ("moderación docente histórica", "teacher_moderate_thread" in teacher and "teacher_pin_answer" in teacher),
    ("tablas por cohorte", "course_run_id uuid not null references public.lms_course_runs" in sql),
    ("RLS colaboración", sql.count("enable row level security")>=9),
    ("sin acceso público directo", "from anon, authenticated" in sql and "to service_role" in sql),
    ("Pages estudiante", "test -f _site/lms/collaboration.html" in pages),
    ("Pages docente", "test -f _site/lms/teacher-collaboration.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("collaboration",student),("teacher-collaboration",teacher)]:
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
    print("COLABORACION: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("COLABORACION: OK")
print(" - equipos visibles en modo solo lectura")
print(" - estado de entregas grupales visible sin formulario abierto")
print(" - discusión abierta retirada para estudiantes; moderación docente histórica conservada")
print(" - revisión abierta por pares deshabilitada")
print(" - estudiante no recibe foros, posts ni menciones")
print(" - S07 intacta")
print(" - JS válido")
