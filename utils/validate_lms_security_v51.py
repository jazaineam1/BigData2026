#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append(f"Falta {path}")
        return ""
    return p.read_text("utf-8")

backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
kit=read("lms/assets/lms-kit.js")
tests=read("tests/lms-v3.visual.spec.js")

dangerous={"resource_completed","challenge_answered","evidence_submitted","evidence_verified","lab_code_issued","session_completed"}
m=re.search(r"const PUBLIC_TRACK_EVENTS=new Set\(\[(.*?)\]\);",backend,re.S)
if not m:
    errors.append("Falta PUBLIC_TRACK_EVENTS")
else:
    public=set(re.findall(r'"([^"]+)"',m.group(1)))
    leaked=sorted(public & dangerous)
    if leaked: errors.append("Eventos server-only expuestos en track: "+", ".join(leaked))

checks=[
 ("track no deriva completitud", 'event==="resource_completed"' not in backend and 'event==="evidence_verified"' not in backend and 'event==="session_completed"' not in backend),
 ("answer_challenge usa endpoint dedicado", 'if(action==="answer_challenge")' in backend and '"challenge_answered"' not in (m.group(1) if m else "")),
 ("muro estudiante no expone user_id", "return isTeacher?{...publicPost,user_id:p.user_id}:publicPost" in backend),
 ("S09 define esc local", "const esc=value=>L?.esc" in deck),
 ("cola guarda propietario", "owner_id:ownerId" in kit and "entry.owner_id!==owner" in kit),
 ("cola tiene rechazados", "REJECTED_KEY='lms.bigdata.rejected.v1'" in kit and "function rejected()" in kit and "retryRejected" in kit),
 ("QA escucha pageerror", "page.on('pageerror'" in tests),
 ("QA valida vertical", "a.top < b.top-tol" in tests and "a.bottom > b.bottom+tol" in tests),
 ("QA incluye 1920x937", "desktop-1920x937" in tests),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

if errors:
    print("LMS SECURITY V5.1: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("LMS SECURITY V5.1: OK")
print(" - tracking cliente sin eventos académicos")
print(" - muro estudiante sin user_id")
print(" - cola aislada por usuario y rechazados persistentes")
print(" - QA detecta pageerror y overflow vertical")
