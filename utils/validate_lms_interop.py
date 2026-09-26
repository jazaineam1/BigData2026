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

interop=read("infraestructura/lms/functions/bigdata-lms-interop/index.ts")
page=read("lms/teacher-interoperability.html")
client=read("lms/assets/bigdata-lms.js")
portal=read("lms/portal.html")
teacher_course=read("lms/teacher-course.html")
standards=read("infraestructura/lms/STANDARDS.md")
roadmap=read("infraestructura/lms/ROADMAP.md")
pages=read(".github/workflows/pages.yml")
course_text=read("lms/data/course.json")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante fase 7")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

checks=[
    ("API interoperabilidad separada", "bigdata-lms-interop" in client and "async function interop" in client),
    ("backend solo docente", "requireTeacher(ctx);" in interop and 'if(action==="overview")' in interop),
    ("QTI namespace", 'http://www.imsglobal.org/xsd/imsqtiasi_v3p0' in interop),
    ("QTI package manifest", 'http://www.imsglobal.org/xsd/qti/qtiv3p0/imscp_v1p1' in interop and '<schemaversion>3.0.0</schemaversion>' in interop),
    ("QTI resource type", 'imsqti_item_xmlv3p0' in interop),
    ("QTI tipos soportados", all(x in interop for x in ["single_choice","multiple_choice","true_false","numeric","short_text"])),
    ("QTI tolerancia numérica", 'tolerance-mode="absolute"' in interop and 'qti-extended-text-interaction' in interop),
    ("no falsa certificación QTI", 'certified:false' in interop and "No equivale a certificación" in interop),
    ("OneRoster 1.2.1", 'format:"OneRoster 1.2.1 CSV bulk package"' in interop and '["oneroster.version","1.2"]' in interop),
    ("manifest OneRoster", '["manifest.version","1.0"]' in interop and '"academicSessions"' in interop and '"file."+n' in interop),
    ("Bulk deja metadatos delta vacíos", '[term,"","","Big Data 2026-2S"' in interop and 'catId(c),"","",c' in interop),
    ("OneRoster exige fechas", 'if(!run.starts_on||!run.ends_on)throw new Error' in interop),
    ("OneRoster no exporta hashes", "password_hash" not in interop and '.select("id,username,display_name,email,active,updated_at")' in interop),
    ("OneRoster marca compatibilidad HE", "perfil de compatibilidad" in interop.lower() and "Edu-API" in interop),
    ("ICS no inventa fechas", 'if(!s.starts_at)continue' in interop and 'if(!a.due_at)continue' in interop),
    ("Gradebook export", 'bigdata-gradebook.csv' in interop and "export_gradebook" in interop),
    ("exportaciones auditadas", interop.count("bigdata.interop.export.")>=4),
    ("integraciones externas no activas", 'status:"not_configured"' in interop and all(x in interop for x in ['code:"lti"','code:"oidc"','code:"xapi"'])),
    ("frontend docente", "requireBigData({teacher:true})" in page and "L.interop('overview')" in page),
    ("confirmación PII", "contiene nombres y correos de la cohorte" in page),
    ("ZIP local pinneado", "fflate@0.8.2" in page and "zipSync" in page),
    ("no service role frontend", "SUPABASE_SERVICE_ROLE_KEY" not in page+client+portal+teacher_course),
    ("documentación estándares", "QTI 3.0" in standards and "OneRoster 1.2.1" in standards and "Edu-API" in standards),
    ("límites externos documentados", "No configurado" in standards and "LTI 1.3" in standards and "SSO OIDC" in standards),
    ("portal enlaza interop", 'href="teacher-interoperability.html"' in portal and "teacherInterop" in portal),
    ("gestor enlaza interop", 'href="teacher-interoperability.html">Interoperabilidad</a>' in teacher_course),
    ("Pages interop", "test -f _site/lms/teacher-interoperability.html" in pages),
]
for label,ok in checks:
    if not ok:
        errors.append("Falla: "+label)

s08=next((x for x in course.get("sessions",[]) if x.get("n")==8),{})
if s08.get("title")!="SECOP Data Pipeline · API, concurrencia y NoSQL":
    errors.append("course.json revirtió el título TC1 V4 de S08")
if not any(x.get("code")=="interoperability" and x.get("path")=="teacher-interoperability.html" for x in course.get("teacher_tools",[])):
    errors.append("course.json no declara interoperabilidad docente")

# Las exportaciones con PII y claves QTI deben vivir solo en el backend.
if "answer_key" in page:
    errors.append("El frontend de interoperabilidad contiene answer_key")
if re.search(r"(service[_-]?role|sb_secret_)[A-Za-z0-9_.-]{12,}",page+client+portal+teacher_course,re.I):
    errors.append("Posible secreto privado expuesto en frontend")

# Validar sintaxis JavaScript inline.
for name,html in [("teacher-interoperability",page),("portal",portal),("teacher-course",teacher_course)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

if errors:
    print("INTEROPERABILIDAD: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("INTEROPERABILIDAD: OK")
print(" - QTI 3 export")
print(" - OneRoster 1.2.1 bulk compatibility")
print(" - iCalendar + Gradebook CSV")
print(" - PII y secretos protegidos")
print(" - integraciones externas no simuladas")
print(" - S07 intacta y TC1 V4 preservado")
print(" - JS válido")
