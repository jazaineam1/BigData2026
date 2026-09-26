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

assess=read("infraestructura/lms/functions/bigdata-lms-assess/index.ts")
schema=read("infraestructura/lms/lms-assessment-engine-v2.sql")
rubrics=read("infraestructura/lms/lms-rubrics-v2.sql")
student=read("lms/quizzes.html")
teacher=read("lms/teacher-quizzes.html")
assignments=read("lms/assignments.html")
gradebook=read("lms/gradebook.html")
portal=read("lms/portal.html")
client=read("lms/assets/bigdata-lms.js")
pages=read(".github/workflows/pages.yml")
course_text=read("lms/data/course.json")
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"

if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió durante fase 3B")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

checks=[
    ("API evaluación separada", "bigdata-lms-assess" in client and "async function assess" in client),
    ("banco versionado", "lms_questions_v2" in schema and "version integer not null" in schema and "question.version.create" in assess),
    ("tipos de pregunta", all(x in schema for x in ["single_choice","multiple_choice","true_false","numeric","short_text"])),
    ("quiz intenta y guarda respuestas", "lms_quiz_attempts_v2" in schema and "lms_quiz_responses_v2" in schema),
    ("aleatorización", "shuffle_questions" in schema and "shuffle_options" in schema and "shuffled(" in assess),
    ("quiz vacío no se publica", 'Agrega al menos una pregunta antes de publicar' in assess),
    ("answer_key no sale al estudiante", "function publicQuestion" in assess and "answer_key:q.answer_key" not in assess and "answer_key:q." not in assess),
    ("autocalificación objetiva", "function autoScore" in assess and "equalSets" in assess),
    ("texto abierto requiere docente", "teacher_grade_response" in assess and "Revisión manual" in teacher),
    ("quiz sincroniza gradebook", 'source:"quiz"' in assess and "assignment_id:quiz.assignment_id" in assess),
    ("archivos privados", 'const BUCKET="bigdata-lms-private"' in assess and "public:false" in assess),
    ("límite archivos 20MB", "const MAX_FILE=20*1024*1024" in assess),
    ("URL firmada de subida", "createSignedUploadUrl" in assess and "uploadToSignedUrl" in assignments),
    ("URL temporal de descarga", "createSignedUrl(path,300" in assess),
    ("no servicio secreto en frontend", "SUPABASE_SERVICE_ROLE_KEY" not in assignments+student+teacher+gradebook+client),
    ("publishable key no es secreto", "sb_publishable_" in assignments),
    ("metadatos de archivo trazables", "lms_submission_files_v2" in schema and "submission_id" in schema),
    ("rúbricas reutilizables", "lms_rubric_templates_v2" in rubrics and "teacher_save_rubric" in assess and "Plantilla reutilizable" in gradebook),
    ("RLS evaluación", schema.count("enable row level security")>=6 and "from anon,authenticated" in schema and "to service_role" in schema),
    ("RLS rúbricas", "enable row level security" in rubrics and "from anon, authenticated" in rubrics and "to service_role" in rubrics),
    ("portal enlaza quizzes", 'href="quizzes.html"' in portal),
    ("vista estudiante", "L.assess('quizzes')" in student and "start_quiz" in student and "save_response" in student),
    ("vista docente protegida", "requireBigData({teacher:true})" in teacher and "teacher_save_question" in teacher),
    ("Pages estudiante", "test -f _site/lms/quizzes.html" in pages),
    ("Pages docente", "test -f _site/lms/teacher-quizzes.html" in pages),
]
for label,ok in checks:
    if not ok:
        errors.append("Falla: "+label)

s08=next((x for x in course.get("sessions",[]) if x.get("n")==8),{})
if s08.get("title")!="SECOP Data Pipeline · API, concurrencia y NoSQL":
    errors.append("course.json revirtió el título TC1 V4 de S08")
if not any(x.get("code")=="quizzes" and x.get("path")=="quizzes.html" for x in course.get("student_tools",[])):
    errors.append("course.json no declara quizzes estudiante")
if not any(x.get("code")=="quizzes" and x.get("path")=="teacher-quizzes.html" for x in course.get("teacher_tools",[])):
    errors.append("course.json no declara quizzes docente")

for name,html in [("quizzes",student),("teacher-quizzes",teacher),("assignments",assignments),("gradebook",gradebook),("portal",portal)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:500]}")

front=assignments+"\n"+student+"\n"+teacher+"\n"+gradebook+"\n"+client
if re.search(r"(service[_-]?role|sb_secret_)[A-Za-z0-9_.-]{12,}",front,re.I):
    errors.append("Posible secreto privado expuesto en frontend")

if errors:
    print("EVALUACION AVANZADA: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("EVALUACION AVANZADA: OK")
print(" - archivo privado firmado")
print(" - banco versionado + quizzes")
print(" - autocalificación + revisión manual")
print(" - rúbricas reutilizables")
print(" - Gradebook sincronizado")
print(" - S07 intacta y TC1 V4 preservado")
print(" - JS válido")
