#!/usr/bin/env python3
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

deck=read("Presentaciones/s09-de-palabras-a-significado.html")
assignments=read("lms/assignments.html")
quizzes=read("lms/quizzes.html")
collab=read("lms/collaboration.html")
progress=read("lms/progress.html")
portal=read("lms/portal.html")
teacher_wall=read("lms/wall.html")
teacher_quizzes=read("lms/teacher-quizzes.html")
gradebook=read("lms/gradebook.html")
teacher_collab=read("lms/teacher-collaboration.html")
kit=read("lms/assets/lms-kit.js")
session_backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
core=read("infraestructura/lms/functions/bigdata-lms-core/index.ts")
assess=read("infraestructura/lms/functions/bigdata-lms-assess/index.ts")
migration=read("infraestructura/lms/lms-student-no-open-responses-v53.sql")
generator=read("utils/build_session9_notebook.py")
notebook=read("Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb")
calendar=read("lms/data/course.json")

checks=[
    ("class-wall eliminado", not (ROOT/"lms/class-wall.html").exists()),
    ("sin enlaces class-wall", all("class-wall.html" not in x for x in [deck,progress,teacher_wall,portal])),
    ("Teacher WALL sin proyección de respuestas", "updateProjectionLink" not in teacher_wall and "projectionLink" not in teacher_wall),
    ("sin textareas evaluativos estudiante", all("<textarea" not in html for html in [assignments,quizzes,collab,progress])),
    ("S09 conserva texto solo como herramienta", "data-transfer-field" not in deck and "¿Qué tan seguro estás?" not in deck),
    ("sin wall API abierto", all(x not in kit for x in ["wallPost","wall_post"]) and all(x not in session_backend for x in ['action==="wall_post"','action==="wall_list"','action==="wall_react"','action==="wall_moderate"'])),
    ("wall competitivo embebido", "Wall de competencia" in progress and "competition_wall" in progress and "competitionWall" in progress),
    ("wall competitivo visible desde portal", "Wall de competencia" in portal and "#competitionWall" in portal),
    ("wall competitivo sin texto libre", "<textarea" not in progress and "open_responses:false" in session_backend),
    ("wall competitivo usa alias rotado", "competitionAlias" in session_backend and "sessionNumber" in session_backend and "Jugador " in session_backend),
    ("wall competitivo no premia velocidad", "speed_tiebreak:false" in session_backend),
    ("LAB9 estructurado", "LAB9_STRUCTURED" in session_backend and all(x in generator for x in ["RAZONES =","DECISIONES =","ALTERNATIVAS =","LIMITES ="])),
    ("notebook sin explicación libre", all(x not in notebook for x in ["explica qué relación semántica observaste","qué enfoque final eliges para esta necesidad y por qué","qué otra estrategia consideraste y por qué no la elegiste","qué dato o juicio falta para afirmar que el ranking es bueno"])),
    ("tareas estudiante sin texto", 'name="text"' not in assignments and 'name="type_text"' not in gradebook and '["url","file","evidence"]' in core),
    ("backend rechaza artifact text", 'type==="text"' in core and "respuestas abiertas están deshabilitadas" in core),
    ("quiz solo objetivo", 'value="short_text"' not in teacher_quizzes and '["single_choice","multiple_choice","true_false","numeric"]' in assess and 'question_type==="short_text"' not in assess),
    ("colaboración estudiante solo lectura", "<form" not in collab and all(x not in collab for x in ["post_discussion","create_thread","submit_peer_review","group_submit","confirm_contribution"])),
    ("backend no expone mutaciones abiertas colaboración", all(x not in core for x in ['if(action==="group_submit")','if(action==="confirm_contribution")','if(action==="submit_peer_review")'])),
    ("discusiones solo docentes", "async function createThread(ctx:any,run:any,body:any){\n  requireTeacher(ctx);" in core and "async function postDiscussion(ctx:any,run:any,body:any){\n  requireTeacher(ctx);" in core),
    ("peer review abierto no configurable", 'name="peer_review_enabled"' not in teacher_collab and "peer_review_enabled:false" in core),
    ("migración elimina muro", all(x in migration for x in ["drop table if exists public.bd_wall_posts","drop table if exists public.bd_wall_reactions"])),
    ("migración elimina text de tareas", "array_remove(allowed_types,'text')" in migration),
    ("migración restringe question_type", "short_text" not in migration.split("add constraint lms_questions_v2_question_type_check",1)[1].split(";",1)[0]),
    ("calendario S08 1 octubre", '"session_number": 8' in calendar and '"class_date": "2026-10-01"' in calendar and '"class_kind": "assessment_workshop"' in calendar),
    ("calendario S09 8 octubre", '"session_number": 9' in calendar and '"class_date": "2026-10-08"' in calendar),
]

for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
    if not ok: errors.append(name)

try:
    nb=json.loads(notebook)
    text="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
    if not all(x in text for x in ["defendibles_idx","razon_clave","decision_clave","alternativa_clave","limite_clave"]):
        errors.append("notebook no usa selecciones estructuradas")
except Exception as ex:
    errors.append("notebook inválido: "+str(ex))

if errors:
    print("STUDENT UX V53: FAIL")
    for x in errors: print(" -",x)
    sys.exit(1)

print("STUDENT UX V53: OK")
print(" - sin página de muro abierto ni respuestas evaluativas libres")
print(" - wall competitivo embebido con alias y métricas objetivas")
print(" - S08 permanece como taller del 1 de octubre")
