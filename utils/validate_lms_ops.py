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

ops=read("infraestructura/lms/functions/bigdata-lms-ops/index.ts")
assess=read("infraestructura/lms/functions/bigdata-lms-assess/index.ts")
page=read("lms/admin-operations.html")
client=read("lms/assets/bigdata-lms.js")
portal=read("lms/portal.html")
teacher_course=read("lms/teacher-course.html")
runbook=read("infraestructura/lms/OPS_RUNBOOK.md")
roadmap=read("infraestructura/lms/ROADMAP.md")
pages=read(".github/workflows/pages.yml")
course_text=read("lms/data/course.json")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante fase 8A")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

cleanup_start=ops.find("async function cleanupRetention")
cleanup_end=ops.find("async function overview",cleanup_start)
cleanup=ops[cleanup_start:cleanup_end] if cleanup_start>=0 and cleanup_end>cleanup_start else ""
submit_start=assess.find("async function submitFileAssignment")
submit_end=assess.find("async function fileDownloadUrl",submit_start)
submit=assess[submit_start:submit_end] if submit_start>=0 and submit_end>submit_start else ""

checks=[
    ("API operaciones separada", "bigdata-lms-ops" in client and "async function ops" in client),
    ("backend teacher/admin", "requireTeacher(ctx)" in ops and "requireAdmin(ctx)" in ops),
    ("backup académico versionado", 'format:"bigdata-lms-academic-snapshot"' in ops and "BACKUP_VERSION=1" in ops),
    ("backup con SHA256", "sha256:await sha256(dataJson)" in ops and "table_counts:counts(data)" in ops),
    ("backup excluye binarios", "includes_binary_files:false" in ops and "binary Storage objects" in ops),
    ("usuarios sin password_hash", 'inRows("lms_users","id",userIds,"id,username,display_name,role,active,email,created_at,updated_at")' in ops),
    ("backup cubre evaluación", all(x in ops for x in ["lms_submissions_v2","lms_grade_history_v2","lms_quiz_attempts_v2","lms_quiz_responses_v2"])),
    ("backup cubre competencias/colaboración", all(x in ops for x in ["lms_competencies_v2","lms_group_submissions_v2","lms_discussion_posts_v2","lms_peer_reviews_v2"])),
    ("backup cubre S08", all(x in ops for x in ["bd_lms_activity_progress","bd_lms_s08_submissions","bd_lms_session_windows"])),
    ("retención mínimo 24h", "Math.max(24,Math.min(24*90,requested))" in ops),
    ("retención solo pending/abandoned", cleanup.count('["pending","abandoned"]')>=2),
    ("cleanup admin-only", "requireAdmin(ctx)" in cleanup and 'ELIMINAR_HUERFANOS' in cleanup),
    ("claim abandoned antes de Storage", '.update({status:"abandoned"})' in cleanup and cleanup.find('.update({status:"abandoned"})') < cleanup.find("db.storage.from(bucket).remove(paths)")),
    ("cleanup no acepta attached", '"attached"' not in cleanup),
    ("submit exige pending al adjuntar", '.eq("id",file.id).eq("status","pending").select("id").maybeSingle()' in submit),
    ("submit revierte entrega si perdió el claim", 'db.from("lms_submissions_v2").delete().eq("id",sub.id)' in submit and "La carga dejó de estar disponible" in submit),
    ("hash verificado en navegador", "calc===x.manifest?.sha256" in page and "crypto.subtle.digest('SHA-256'" in page),
    ("restore destructivo ausente", "No hay botón “Restaurar”" in page and "L.ops('restore" not in page),
    ("cleanup UI admin-only", "model.viewer?.role==='admin'" in page and "ELIMINAR_HUERFANOS" in page),
    ("frontend sin service role", "SUPABASE_SERVICE_ROLE_KEY" not in page+client+portal+teacher_course),
    ("runbook separa DB y Storage", "base de datos PostgreSQL" in runbook and "objetos privados de Storage" in runbook),
    ("runbook advierte backup DB sin Storage", "backups de base de datos no incluyen los objetos" in runbook),
    ("runbook orden de restore", "Orden lógico de restauración selectiva" in runbook and "tareas, rúbricas y competencias" in runbook),
    ("portal enlaza operaciones", 'href="admin-operations.html"' in portal and "teacherOps" in portal),
    ("gestor enlaza operaciones", 'href="admin-operations.html">Operaciones</a>' in teacher_course),
    ("Pages publica operaciones", "test -f _site/lms/admin-operations.html" in pages),
    ("roadmap refleja 8A", "snapshot académico con SHA-256" in roadmap and "limpieza de archivos huérfanos" in roadmap),
]
for label,ok in checks:
    if not ok:
        errors.append("Falla: "+label)

s08=next((x for x in course.get("sessions",[]) if x.get("n")==8),{})
if s08.get("title")!="SECOP Data Pipeline · API, concurrencia y NoSQL":
    errors.append("course.json alteró el título actual de S08")
if not any(x.get("code")=="operations" and x.get("path")=="admin-operations.html" for x in course.get("teacher_tools",[])):
    errors.append("course.json no declara operaciones")

# No debe existir una selección amplia de lms_users dentro del backup.
if re.search(r'from\("lms_users"\)\.select\("\*"\)',ops):
    errors.append("El backup selecciona lms_users con *")
# Password hash puede aparecer solo como texto de exclusión/documentación, no como campo del select.
for m in re.finditer("password_hash",ops):
    window=ops[max(0,m.start()-120):m.end()+120]
    if "excludes" not in window and "No contiene" not in window:
        errors.append("password_hash aparece fuera de la lista de exclusiones")
        break

for name,html in [("admin-operations",page),("portal",portal),("teacher-course",teacher_course)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

if errors:
    print("OPERACIONES Y RESILIENCIA: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("OPERACIONES Y RESILIENCIA: OK")
print(" - snapshot académico SHA-256")
print(" - credenciales excluidas")
print(" - backup cubre evaluación, competencias y colaboración")
print(" - retención admin-only con mínimo 24 h")
print(" - pending/abandoned reclamado antes de Storage")
print(" - pending→attached protegido contra carrera")
print(" - restore destructivo fuera del navegador")
print(" - S07 intacta y S08 preservada")
print(" - JS válido")
