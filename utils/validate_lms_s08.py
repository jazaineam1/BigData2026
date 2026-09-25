#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def need(path):
    p=ROOT/path
    if not p.exists(): errors.append(f"Falta {path}")
    return p

required=[
 "lms/index.html","lms/portal.html","lms/access.html","lms/session-08.html","lms/teacher-wall.html",
 "lms/assets/bigdata-lms.css","lms/assets/bigdata-lms.js","lms/data/course.json",
 "infraestructura/lms/bigdata-lms-s08.sql","infraestructura/lms/functions/bigdata-learning/index.ts",".github/workflows/pages.yml",
]
for x in required: need(x)

# Guardia dura: S07 debe conservar exactamente el blob publicado antes de este LMS.
s07=need("Presentaciones/s07-del-vecindario-al-texto.html")
if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    expected="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8"
    if blob!=expected: errors.append(f"S07 cambió: blob {blob}, esperado {expected}")

portal=(ROOT/"lms/portal.html").read_text("utf-8")
s08=(ROOT/"lms/session-08.html").read_text("utf-8")
wall=(ROOT/"lms/teacher-wall.html").read_text("utf-8")
client=(ROOT/"lms/assets/bigdata-lms.js").read_text("utf-8")
sql=(ROOT/"infraestructura/lms/bigdata-lms-s08.sql").read_text("utf-8")
edge=(ROOT/"infraestructura/lms/functions/bigdata-learning/index.ts").read_text("utf-8")
index=(ROOT/"index.html").read_text("utf-8")
pages=(ROOT/".github/workflows/pages.yml").read_text("utf-8")
course=json.loads((ROOT/"lms/data/course.json").read_text("utf-8"))

checks=[
 ("portal reutiliza sesión LMS","andesdb.lms.auth.v1" in client),
 ("S08 abre Taller_Control_1","Cuadernos/Taller_Control_1.ipynb" in s08),
 ("S08 acepta manifest","manifest_tc1.json" in s08 and 'type="file"' in s08),
 ("S08 no marca abrir como completar","Abrirlo <b>no</b> lo marca como completado" in s08),
 ("WALL declara desempate por inicio","demora de inicio" in wall),
 ("WALL usa modo docente BigData","requireBigData({teacher:true})" in wall and "teacher_wall" in edge),
 ("RLS habilitado",sql.count("enable row level security")>=7),
 ("inicio oficial course-scoped","bd_lms_session_windows" in sql and "teacher_open_session" in edge),
 ("inicio no nace de page_view",'["notebook_opened","activity_started","stage_opened"].includes(event)' in edge),
 ("pareja solo con hash","pair_hash:m.pair_hash" in edge and "pair_hash text" in sql and "pair_id text" not in sql),
 ("Edge Function versionada","VALIDATOR_VERSION" in edge and "submit_manifest" in edge),
 ("tablas no expuestas a anon/authenticated","revoke all" in sql and "anon,authenticated" in sql),
 ("curso declarativo",course.get("course")=="bigdata" and course.get("current_tracked_session")==8),
 ("portada enlaza LMS",'lms/portal.html' in index),
 ("portada S08 entra al LMS",'lms/session-08.html' in index),
 ("Pages publica carpeta LMS","cp -R lms _site/" in pages and "lms/**" in pages),
 ("Pages publica recursos mínimos S08","Talleres/Taller_Control_1.md" in pages and "Cuadernos/Taller_Control_1.ipynb" in pages),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

public_text="\n".join((ROOT/p).read_text("utf-8") for p in required if (ROOT/p).exists())
if re.search(r"service[_-]?role.{0,80}(eyJ|sb_secret)",public_text,re.I|re.S):
    errors.append("Posible service role expuesto en archivos públicos")

if errors:
    print("LMS S08: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)
print("LMS S08: OK")
print(" - S07 intacta por Git blob SHA")
print(" - Login LMS reutilizado")
print(" - S08 + manifest + WALL presentes")
print(" - RLS/revocación declarados")
