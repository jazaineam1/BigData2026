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
migration=read("infraestructura/lms/lms-evidence-v4.sql")
deterministic=read("infraestructura/lms/lms-s09-deterministic-v51.sql")
authentic=read("infraestructura/lms/lms-s09-authentic-evidence-v9.sql")
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

# Verifica que cada answer hash privado corresponda a exactamente una opción publicada.
det_blocks=re.findall(r"update public\.bd_activity_catalog set(.*?)where code='([^']+)';",deterministic,re.S|re.I)
det_by_code={}
for block,code in det_blocks:
    ev=re.search(r"evaluator='([^']+)'",block)
    st=re.search(r"steps='(.*?)'::jsonb",block,re.S)
    cfg=re.search(r"config='(.*?)'::jsonb",block,re.S)
    if not (ev and st and cfg):
        errors.append(f"Falla: contrato determinístico incompleto para {code}")
        continue
    try:
        steps=json.loads(st.group(1))
        config=json.loads(cfg.group(1))
    except Exception as ex:
        errors.append(f"Falla: JSON determinístico inválido en {code}: {ex}")
        continue
    det_by_code[code]={"evaluator":ev.group(1),"steps":steps,"config":config}

if set(det_by_code)!=set(labs):
    errors.append("Falla: la migración determinística no cubre exactamente los 12 LAB S09")

for code,x in det_by_code.items():
    if x["evaluator"]=="self-report":
        errors.append(f"Falla: {code} todavía usa self-report")
    if x["evaluator"]=="choice-hash":
        answers=x["config"].get("answers",{})
        for step in x["steps"]:
            if step.get("type")!="choice":
                errors.append(f"Falla: {code}/{step.get('id')} no es choice en un evaluador choice-hash")
                continue
            sid=str(step.get("id",""))
            target=str(answers.get(sid,""))
            vals=[str(o.get("value","")) if isinstance(o,dict) else str(o) for o in step.get("options",[])]
            matches=[v for v in vals if hashlib.sha256(v.encode()).hexdigest()==target]
            if len(matches)!=1:
                errors.append(f"Falla: hash de respuesta inválido/ambiguo en {code}/{sid}")
    elif code=="bd-s09-lab3":
        if x["evaluator"]!="seeded-numeric" or x["config"].get("generator")!="s09_topk_aero_count":
            errors.append("Falla: LAB3 perdió su evaluador seeded-numeric")
    else:
        errors.append(f"Falla: evaluador inesperado en {code}: {x['evaluator']}")

checks=[
 ("portada recupera fondo UC", 'assets/img/bg-masthead.jpg' in index and 'class="hero"' in index),
 ("portada sin copy rechazado", "Aprender haciendo, con evidencia." not in index and "Una ruta integrada para comprender arquitecturas" not in index),
 ("módulo máximo dos recursos", "slice(0,2)" in session and "Material de la sesión" in session),
 ("migración limita recursos", "row_number() over(partition by course_run_id,session_number" in migration and "x.rn>2" in migration),
 ("CHECK de eventos versionado", all(x in migration for x in ["slide_viewed","challenge_answered","lab_interaction","evidence_submitted","lab_code_issued"])),
 ("tablas de evidencia protegidas", all(x in migration for x in ["bd_activity_catalog","bd_evidence","bd_lab_codes","enable row level security","revoke all"])),
 ("muro de clase protegido", all(x in migration for x in ["bd_wall_posts","bd_wall_reactions"])),
 ("12 LAB declarados", all(x in migration for x in labs)),
 ("LAB3 seeded-numeric", "s09_topk_aero_count" in deterministic and "evaluator='seeded-numeric'" in deterministic and "code='bd-s09-lab3'" in deterministic),
 ("LAB S09 con autocomprobación + evidencia auténtica", deterministic.count("evaluator='choice-hash'")>=11 and "version=2" in deterministic and "authentic-review" in authentic and "bd-s09-lab9" in authentic),
 ("backend choice-hash", 'catalog.evaluator==="choice-hash"' in backend and "await sha256(v)" in backend),
 ("backend bloquea self-report S09", 'n===9&&catalog.evaluator==="self-report"' in backend),
 ("LAB3 sin texto libre", "lab3Alternative" not in deck and "lab3Limit" not in deck and "Comprueba tu aprendizaje · LAB 3" in deck),
 ("paneles determinísticos", (("La corrección es automática e inmediata." in deck) or ("Autocomprobación" in deck and "no es nota ni evidencia de competencia" in deck)) and "stepOptionValue" in deck),
 ("backend comprueba errores", 'failIf(eventError,"No se pudo registrar el evento")' in backend and "failIf(evidenceError" in backend),
 ("backend evidencia", 'action==="evidence"' in backend and "submitEvidence" in backend and "bd_evidence" in backend),
 ("backend código Colab", 'action==="lab_code"' in backend and 'action==="evidence_by_code"' in backend and "bd_lab_codes" in backend),
 ("evidence_by_code antes de bearer", backend.index('if(action==="evidence_by_code")') < backend.index("const ctx=await current(req)")),
 ("reset incluye evidencia", 'db.from("bd_evidence").delete()' in backend and 'db.from("bd_lab_codes").delete()' in backend),
 ("atascado LAB 5–30 min con presencia", 'currentDef?.kind==="lab"' in backend and "meaningfulAge>5&&meaningfulAge<=30" in backend and "present&&" in backend),
 ("safeNext recursos internos", "/BigData2026/Presentaciones/" in client and "/BigData2026/assets/tutoriales/" in client),
 ("módulo abre LAB en slide", "function openStage(a)" in session and "resource_type:'lab'" in session),
 ("módulo genera código Colab", "labCodeCard" in session and "L.session('lab_code'" in session),
 ("Mi progreso muestra evidencia", "evidenceCard" in progress and "renderEvidence()" in progress),
 ("WALL muestra LAB y evidencia", "LAB explorados" in wall and "detailEvidence" in wall and "evidence_count" in wall),
 ("muro publicar-para-ver", "publish_first" in backend and all(x in backend for x in ['action==="wall_post"','action==="wall_list"','action==="wall_react"','action==="wall_moderate"']) and "Publica para ver" in class_wall),
 ("muro anonimiza pares", "Compañero " in backend and "Tus compañeros ven un alias" in class_wall),
 ("S09 instrumenta 12 LAB", "LAB_BY_SLIDE" in deck and all(x in deck for x in labs)),
 ("S09 envía lab_interaction", "lab_interaction" in deck and "queueLabInteraction" in deck),
 ("S09 LAB3 registra evidencia", "submitLab3Evidence" in deck and "bd-s09-lab3" in deck and "¿Cuántos son claramente aeronáuticos?" in deck),
 ("S09 LAB9 evidencia auténtica", "lab9EvidencePanel" in deck and "authentic-review" in deck and "Evidencia auténtica · LAB 9" in deck),
 ("backend revisión LAB9", 'catalog.evaluator==="authentic-review"' in backend and "teacher_review_evidence" in backend and "pending_review" in backend),
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
    if not any('lms.registrar("bd-s09-lab9"' in s for s in sources): errors.append("Falla: notebook no sincroniza la evidencia auténtica LAB9")
    if not any("pending_review" in s and "Evidencia enviada" in s for s in sources): errors.append("Falla: notebook sin cierre de evidencia pendiente de revisión")
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
print(" - autocomprobación determinística separada de evidencia auténtica LAB9")
print(" - LAB3 seeded sin campos abiertos")
print(" - hashes de respuesta validados contra opciones publicadas")
print(" - código Colab efímero sin bearer")
print(" - Mi progreso y WALL consumen evidencia")
print(" - reset y señal de atasco consistentes")
