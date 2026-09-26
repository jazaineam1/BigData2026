#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

index=read("index.html")
migration=read("infraestructura/lms/lms-evidence-v4.sql")
backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
client=read("lms/assets/bigdata-lms.js")
session=read("lms/session.html")
progress=read("lms/progress.html")
wall=read("lms/wall.html")
class_wall=read("lms/class-wall.html")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
generator=read("utils/build_session9_notebook.py")
notebook=read("Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb")

labs=[
 "bd-s09-lab1","bd-s09-lab-e5","bd-s09-lab-chunk","bd-s09-lab2",
 "bd-s09-lab3","bd-s09-lab4","bd-s09-lab5","bd-s09-lab6",
 "bd-s09-lab7","bd-s09-lab8","bd-s09-lab-eval","bd-s09-lab9"
]

checks=[
 ("portada recupera fondo UC", 'assets/img/bg-masthead.jpg' in index and 'class="hero"' in index),
 ("portada sin copy rechazado", "Aprender haciendo, con evidencia." not in index and "Una ruta integrada para comprender arquitecturas" not in index),
 ("módulo máximo dos recursos", "slice(0,2)" in session and "Recursos de la sesión" in session),
 ("migración limita recursos", "row_number() over(partition by course_run_id,session_number" in migration and "x.rn>2" in migration),
 ("CHECK de eventos versionado", all(x in migration for x in ["slide_viewed","challenge_answered","lab_interaction","evidence_submitted","lab_code_issued"])),
 ("tablas de evidencia protegidas", all(x in migration for x in ["bd_activity_catalog","bd_evidence","bd_lab_codes","enable row level security","revoke all"])),
 ("muro de clase protegido", all(x in migration for x in ["bd_wall_posts","bd_wall_reactions"])),
 ("12 LAB declarados", all(x in migration for x in labs)),
 ("LAB3 seeded-numeric", "s09_topk_aero_count" in migration and "'bd-s09-lab3','seeded-numeric'" in migration),
 ("backend comprueba errores", 'failIf(eventError,"No se pudo registrar el evento")' in backend and "failIf(evidenceError" in backend),
 ("backend evidencia", 'action==="evidence"' in backend and "submitEvidence" in backend and "bd_evidence" in backend),
 ("backend código Colab", 'action==="lab_code"' in backend and 'action==="evidence_by_code"' in backend and "bd_lab_codes" in backend),
 ("evidence_by_code antes de bearer", backend.index('if(action==="evidence_by_code")') < backend.index("const ctx=await current(req)")),
 ("reset incluye evidencia", 'db.from("bd_evidence").delete()' in backend and 'db.from("bd_lab_codes").delete()' in backend),
 ("atascado LAB 5 min", 'currentDef?.kind==="lab"' in backend and "age>5" in backend),
 ("safeNext recursos internos", "/BigData2026/Presentaciones/" in client and "/BigData2026/assets/tutoriales/" in client),
 ("módulo abre LAB en slide", "function openStage(a)" in session and "resource_type:'lab'" in session),
 ("módulo genera código Colab", "labCodeCard" in session and "L.session('lab_code'" in session),
 ("Mi progreso muestra evidencia", "evidenceCard" in progress and "renderEvidence()" in progress),
 ("WALL muestra LAB y evidencia", "LAB explorados" in wall and "detailEvidence" in wall and "evidence_count" in wall),
 ("muro publicar-para-ver", "publish_first" in backend and all(x in backend for x in ['action==="wall_post"','action==="wall_list"','action==="wall_react"','action==="wall_moderate"']) and "Publica para ver" in class_wall),
 ("muro anonimiza pares", "Compañero " in backend and "Tus compañeros ven un alias" in class_wall),
 ("S09 instrumenta 12 LAB", "LAB_BY_SLIDE" in deck and all(x in deck for x in labs)),
 ("S09 envía lab_interaction", "lab_interaction" in deck and "queueLabInteraction" in deck),
 ("S09 LAB3 registra evidencia", "submitLab3Evidence" in deck and "bd-s09-lab3" in deck and "Resultado propio" in deck),
 ("Colab no recibe bearer", "Authorization" not in generator and "Authorization" not in notebook),
 ("Colab usa código efímero", "LMSBridge" in generator and "evidence_by_code" in generator and "LMSBridge" in notebook),
 ("link de notebook vuelve a módulo universal", "lms/session.html?s=9" in generator and "lms/session.html?s=9" in notebook),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

try:
    nb=json.loads(notebook)
    sources=["".join(c.get("source",[])) for c in nb.get("cells",[])]
    if not any("class LMSBridge" in s for s in sources): errors.append("Falla: notebook generado sin LMSBridge")
    if not any('lms.registrar("bd-s09-lab9"' in s for s in sources): errors.append("Falla: notebook sin envío formativo final")
except Exception as ex:
    errors.append("Notebook inválido: "+str(ex))

for name,html in [("session",session),("progress",progress),("wall",wall),("S09",deck)]:
    scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",html,re.S|re.I)
    for i,script in enumerate(scripts,1):
        with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
            fh.write(script); tmp=fh.name
        p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
        Path(tmp).unlink(missing_ok=True)
        if p.returncode:
            errors.append(f"{name} JS #{i}: {p.stderr.strip()[:900]}")

if errors:
    print("LMS EVIDENCE V4: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("LMS EVIDENCE V4: OK")
print(" - constraint de eventos versionada")
print(" - 12 LAB declarados e instrumentados")
print(" - LAB3 evidencia seeded end-to-end")
print(" - código Colab efímero sin bearer")
print(" - Mi progreso y WALL consumen evidencia")
print(" - reset y señal de atasco consistentes")
