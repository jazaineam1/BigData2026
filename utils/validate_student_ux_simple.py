#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

portal=read("lms/portal.html")
session=read("lms/session.html")
progress=read("lms/progress.html")
s08=read("lms/session-08.html")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
backend=read("infraestructura/lms/functions/bigdata-session/index.ts")

def between(src,a,b):
    i=src.find(a); j=src.find(b,i+len(a))
    return src[i:j+len(b)] if i>=0 and j>=0 else ""

portal_header=between(portal,"<header","</header>")
session_header=between(session,"<header","</header>")
progress_header=between(progress,"<header","</header>")

checks=[
    ("Aula prioriza siguiente acción", "Qué hacer ahora" in portal and "Elige dónde continuar" in portal),
    ("Aula sin dashboard estudiante", all(x not in portal for x in ["quicknav","id=\"metrics\"","id=\"pending\"","id=\"feedback\"","id=\"calendar\""])),
    ("Aula sin lenguaje interno", all(x not in portal for x in ["Dominio</span>","Competencias<span>","Quizzes<span>","Comunidad<span>"])),
    ("Navegación Aula mínima", all(x not in portal_header for x in ['href="assignments.html"','href="competencies.html"','href="quizzes.html"','href="collaboration.html"'])),
    ("Sesión muestra siguiente acción y recursos", "Qué hacer ahora" in session and "Material de la sesión" in session and "resource-grid-v4" in session),
    ("Sesión máximo dos recursos", "slice(0,2)" in session),
    ("Sesión sin seguimiento duplicado", all(x not in session for x in ["Seguimiento integrado","Checkpoints y evidencias requeridas","Avance de la ruta","Cómo leer el progreso","Tiempo activo","Recursos visitados"])),
    ("Navegación Sesión mínima", 'href="collaboration.html"' not in session_header and 'href="account.html"' in session_header),
    ("Qué aprenderás plegable", "<details class=\"card\">" in session and "<summary><b>Qué aprenderás</b></summary>" in session),
    ("Código de laboratorio contextual", "Código de laboratorio" in session and "Úsalo solo si el cuaderno te lo solicita" in session),
    ("Mi progreso pregunta simple", "Qué terminaste y qué te falta." in progress and "Tu recorrido" in progress),
    ("Mi progreso usa tres estados", all(x in progress for x in ["Sin empezar","En curso","Lista"])),
    ("Mi progreso sin dimensiones técnicas", all(x not in progress for x in ["Visitado ","Dominado ","Calificado ","Snapshots académicos","Reglas transparentes","Señales explicables"])),
    ("Mi progreso sin JSON crudo", "<pre>" not in progress and "JSON.stringify(e.payload" not in progress),
    ("Mi progreso sin analítica estudiante", "L.core('analytics')" not in progress and "renderAnalytics" not in progress),
    ("Navegación Progreso mínima", all(x not in progress_header for x in ['href="assignments.html"','href="competencies.html"','href="collaboration.html"']) and 'href="account.html"' in progress_header),
    ("Tracking permanece fuera de la UI", "K.track('session_entered'" in session and "activity_progress" in session),
    ("S08 estudiante una sola ruta", all(x in s08 for x in ["Tu equipo","Abre el taller en Colab","Registra la evidencia del grupo","Progreso del equipo"])),
    ("S08 no duplica contenido del notebook", all(x not in s08 for x in ["Rúbrica oficial · 100 puntos","Trabajo fuera de clase","6–8 horas","Qué cuenta como completado","s08-secoppipeline.html"])),
    ("S08 no expone telemetría ni acciones repetidas", all(x not in s08 for x in ["Tiempo activo","Trabajar etapa"]) and "<details><summary>Ver avance por etapa</summary>" in s08),
    ("Muro abierto retirado del estudiante", not (ROOT/"lms/class-wall.html").exists() and "class-wall.html" not in progress and "class-wall.html" not in deck),
    ("S09 sin respuestas abiertas evaluables", all(x not in deck for x in ["data-transfer-field","data-transfer-for","presentation-transfer","Muro del LAB"])),
    ("Backend sin acciones de muro", all(x not in backend for x in ['action==="wall_post"','action==="wall_list"','action==="wall_react"','action==="wall_moderate"'])),
]

for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

for name,html in [("portal",portal),("session",session),("progress",progress),("s08",s08)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:900]}")

if errors:
    print("STUDENT UX SIMPLE: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("STUDENT UX SIMPLE: OK")
print(" - Aula: qué hacer ahora + sesiones")
print(" - Sesión: siguiente acción + máximo dos recursos")
print(" - Progreso: Sin empezar / En curso / Lista")
print(" - Analítica y telemetría permanecen en backend, no en la vista estudiante")
print(" - S08: equipo → notebook → entrega → estado, sin duplicar el cuaderno")
print(" - S09: autocomprobación cerrada; sin muro ni transferencia textual")
