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

admin=read("lms/admin-users.html")
portal=read("lms/portal.html")
wall=read("lms/teacher-wall.html")
css=read("lms/assets/bigdata-lms.css")
edge=read("infraestructura/lms/functions/bigdata-learning/index.ts")
pages=read(".github/workflows/pages.yml")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante el administrador docente")

checks=[
    ("portal enlaza administrador", 'href="admin-users.html"' in portal and "adminUsers" in portal),
    ("WALL enlaza administrador", 'href="admin-users.html"' in wall),
    ("administrador exige docente", "requireBigData({teacher:true})" in admin),
    ("listado docente", "teacher_admin_overview" in admin and "teacherAdminOverview" in edge),
    ("ficha individual", "teacher_user_detail" in admin and "teacherUserDetail" in edge),
    ("matrícula existente", "teacher_add_existing" in admin and "teacherAddExisting" in edge),
    ("suspensión course-scoped", "teacher_set_enrollment" in admin and 'eq("course_code",COURSE)' in edge),
    ("identidad global no se desactiva", 'lms_users").update({active' not in edge),
    ("contraseña temporal auditada", "teacher_reset_password" in admin and "bigdata.identity.password_reset" in edge),
    ("revocación de sesiones auditada", "teacher_revoke_sessions" in admin and "bigdata.identity.sessions_revoked" in edge),
    ("auditoría course-scoped", "auditAdmin" in edge and "lms_audit_log" in edge and "course_code:COURSE" in edge),
    ("exportación CSV", "exportCsv" in admin and "BigData-2026-2-cohorte.csv" in admin),
    ("estado efectivo considera cuenta global", "global_inactive" in admin and "u.global_active" in admin),
    ("reset global exige advertencia", "contraseña GLOBAL de la identidad LMS" in admin),
    ("auditoría muestra actor", "actor_name" in admin and "actor_name" in edge),
    ("Pages verifica administrador", "test -f _site/lms/admin-users.html" in pages),
    ("búsqueda y filtros", 'id="search"' in admin and 'id="filter"' in admin),
    ("Pages publica LMS", "cp -R lms _site/" in pages),
    ("estilos responsive admin", ".detailgrid" in css and "dialog{" in css and "@media(max-width:560px)" in css),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,text in [("admin",admin),("portal",portal),("wall",wall),("edge",edge)]:
    if re.search(r"(service[_-]?role|sb_secret).{0,100}(eyJ|[A-Za-z0-9_-]{30,})",text,re.I|re.S):
        errors.append(f"Posible secreto expuesto en {name}")

# Valida sintaxis de los scripts inline del administrador con Node.
scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",admin,re.S|re.I)
if not scripts:
    errors.append("Administrador sin script inline")
else:
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script)
            tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"JavaScript admin #{i}: {p.stderr.strip()[:500]}")

if errors:
    print("ADMIN DOCENTE: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("ADMIN DOCENTE: OK")
print(" - S07 intacta")
print(" - permisos course-scoped")
print(" - gestión de cohorte, solicitudes y ficha individual")
print(" - acciones sensibles auditadas")
print(" - JavaScript válido")
