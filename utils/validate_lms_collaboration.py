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
    ("portal enlaza colaboración", 'href="collaboration.html"' in portal),
    ("vista estudiante usa backend", "L.core('collaboration')" in student),
    ("vista docente exige rol", "requireBigData({teacher:true})" in teacher),
    ("gestión de equipos", "teacher_create_group" in teacher and "createGroup" in core),
    ("miembros auditables", "teacher_add_group_member" in teacher and "teacher_remove_group_member" in core),
    ("configuración grupal", "teacher_save_group_setting" in teacher and "saveGroupSetting" in core),
    ("entrega grupal", "group_submit" in student and "groupSubmit" in core),
    ("contribución individual", "confirm_contribution" in student and "lms_group_contributions_v2" in core),
    ("nota grupal sincroniza gradebook", "teacher_grade_group_submission" in teacher and "lms_grade_history_v2" in core),
    ("discusión", "create_thread" in student and "post_discussion" in student and "postDiscussion" in core),
    ("moderación docente", "teacher_moderate_thread" in teacher and "teacher_pin_answer" in teacher),
    ("revisión pares", "submit_peer_review" in student and "submitPeerReview" in core),
    ("no revisión propio equipo", "No puedes revisar la entrega de tu propio equipo" in core),
    ("peer review no expone autor", "peerTargets.push({" in core and "submitted_by:x.submitted_by" not in core and "group_id:x.group_id" not in core),
    ("foros aislados por cohorte", "const threadIds=new Set((threads||[]).map((t:any)=>t.id))" in core and "const postRows=(posts||[]).filter((p:any)=>threadIds.has(p.thread_id))" in core),
    ("menciones por respuesta", "lms_discussion_mentions_v2" in sql and "mentioned_user_id:parent.user_id" in core and "parent_id:f.parent_id.value" in student),
    ("conversación inicia con mensaje", "initialBody=clampText(body.body,8000,true)" in core and 'name="body"' in student),
    ("FAQ con respuesta destacada", "teacher_pin_answer" in teacher and "pinned_answer" in student),
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
print(" - equipos + contribución individual")
print(" - entregas grupales sincronizadas")
print(" - discusión + moderación")
print(" - revisión por pares + anonimato")
print(" - foros aislados + menciones")
print(" - S07 intacta")
print(" - JS válido")
