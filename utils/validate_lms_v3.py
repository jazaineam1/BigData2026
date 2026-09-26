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

index=read("index.html")
portal=read("lms/portal.html")
session=read("lms/session.html")
progress=read("lms/progress.html")
wall=read("lms/wall.html")
client=read("lms/assets/bigdata-lms.js")
css=read("lms/assets/bigdata-lms.css")
bridge=read("lms/assets/resource-bridge.js")
atlas_guide=read("assets/tutoriales/atlas-guia-conexion.html")
astra_guide=read("assets/tutoriales/astra-cassandra-paso-a-paso-v3.html")
neo4j_guide=read("assets/tutoriales/neo4j-aura-s06-paso-a-paso.html")
backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
sql=read("infraestructura/lms/lms-session-engine-v3.sql")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
course_text=read("lms/data/course.json")
pages=read(".github/workflows/pages.yml")

try:
    course=json.loads(course_text)
except Exception as ex:
    course={}
    errors.append(f"course.json inválido: {ex}")

def blob_sha(path):
    b=(ROOT/path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

for path,sha in [
    ("Presentaciones/s07-del-vecindario-al-texto.html","07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8"),
    ("lms/session-08.html","b5b1e9085fe99759182d141a75f875fcbab39d3a"),
]:
    if (ROOT/path).exists() and blob_sha(path)!=sha:
        errors.append(f"{path} cambió durante LMS V3")

checks=[
    ("index es gateway sin progreso local","lms/portal.html" in index and "Continuar mi curso" in index and "data-mark" not in index and "bigdata2026:index:v2" not in index),
    ("portal usa progreso backend","L.session('course_progress')" in portal and "session.html?s=" in portal and "Continuar aprendizaje" in portal),
    ("módulo universal","requireSession(sessionNumber)" in session and "session.html?s=" not in session and "Visitado" in session and "Completado" in session and "Dominado" in session and "Calificado" in session),
    ("módulo no infla tiempo","startHeartbeat" not in session),
    ("progreso universal","L.session('course_progress')" in progress and all(x in progress for x in ["Visitado","Completado","Dominado","Calificado"])),
    ("WALL universal","requireSession(sessionNumber,{teacher:true})" in wall and "teacher_student_detail" in wall and "no es un ranking de velocidad" in wall.lower()),
    ("WALL filtra ayuda","needs_attention" in wall and 'value="needs_attention"' in wall),
    ("WALL polling seguro","setInterval(load,15000)" in wall),
    ("cliente genérico","async function session(" in client and "bigdata-session" in client and "requireSession" in client),
    ("S09 usa compatibilidad genérica","return session(action,{...payload,session_number:9})" in client),
    ("backend sesión dinámica","sessionNumber" in backend and "course_progress" in backend and "teacherStudentDetail" in backend),
    ("backend sin claves hardcodeadas","CHALLENGE_HASHES" not in backend and "bd_lms_activity_keys" in backend),
    ("backend separa primer intento y dominio","first_attempt_correct" in backend and "mastery" in backend),
    ("backend no ordena por velocidad",'localeCompare' in backend and ".sort((a:any,b:any)=>(a.display_name" in backend),
    ("reset limitado por sesión","REINICIAR_S" in backend and 'eq("session_number",n)' in backend),
    ("tabla claves protegida","bd_lms_activity_keys" in sql and "enable row level security" in sql and "revoke all on table public.bd_lms_activity_keys from anon, authenticated" in sql),
    ("recursos S01-S09 declarativos","bd-s01-r1" in sql and "bd-s07-r1" in sql and "bd-s08-module" in sql and "bd-s09-c5" in sql),
    ("rutas canónicas SQL","set path = 'session.html?s=' || session_number::text" in sql and "canonical_module" in sql),
    ("S09 vuelve a módulo universal",'href="../lms/session.html?s=9"' in deck and 'href="../lms/progress.html?s=9"' in deck),
    ("S09 login vuelve a módulo universal","../lms/session.html?s=9&reason=login" in deck),
    ("SVG S09 contenidos","overflow:hidden" in re.search(r'\.svg\{[^}]*\}',deck).group(0) and "height:auto" in re.search(r'\.svg\{[^}]*\}',deck).group(0)),
    ("estándar viz-frame",".viz-frame{" in css and ":focus-visible" in css),
    ("bridge recursos internos","requireSession(n)" in bridge and "guide_opened" in bridge and all("resource-bridge.js" in x for x in [atlas_guide,astra_guide,neo4j_guide])),
    ("course policy V3+",course.get("version",0)>=11 and any(v in course.get("tracking_policy","") for v in ["LMS V3","LMS V4","LMS V5"])),
    ("course wall universal",any(x.get("code")=="wall_s09" and x.get("path")=="wall.html?s=9" for x in course.get("teacher_tools",[]))),
    ("course progress universal",any(x.get("code")=="progress_s09" and x.get("path")=="progress.html?s=9" for x in course.get("student_tools",[]))),
    ("Pages módulo universal","test -f _site/lms/session.html" in pages),
    ("Pages WALL universal","test -f _site/lms/wall.html" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,html in [("index",index),("portal",portal),("session",session),("progress",progress),("wall",wall),("S09",deck)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:700]}")

front="\n".join([index,portal,session,progress,wall,client,deck])
if re.search(r"(service[_-]?role|sb_secret_)[A-Za-z0-9_.-]{12,}",front,re.I):
    errors.append("Posible secreto privado expuesto en frontend")

if errors:
    print("LMS V3: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("LMS V3: OK")
print(" - gateway público sin progreso ficticio")
print(" - identidad única y módulo S01-S16")
print(" - tracking server-side genérico")
print(" - primer intento y dominio separados")
print(" - progreso universal en cuatro dimensiones")
print(" - WALL universal + detalle individual")
print(" - contención visual + foco")
print(" - S07/S08 protegidas")
print(" - frontend JS válido")
