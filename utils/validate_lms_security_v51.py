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
auth=read("infraestructura/lms/functions/bigdata-auth/index.ts")
access=read("infraestructura/lms/functions/bigdata-access-request/index.ts")
review=read("infraestructura/lms/functions/bigdata-access-review/index.ts")
client=read("lms/assets/bigdata-lms.js")
portal=read("lms/portal.html")
wall=read("lms/wall.html")
auth_migration=read("infraestructura/lms/lms-auth-v51.sql")

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
 ("QA vigila errores JS", "page.on('pageerror'" in tests and "ReferenceError|TypeError|SyntaxError|Uncaught" in tests),
 ("sesiones estudiante tienen caducidad", "ttlHours=student?30*24:24" in auth and "deadline=s.expires_at?" in auth),
 ("sesiones legacy se backfillean", "update public.lms_auth_sessions" in auth_migration and "s.expires_at is null" in auth_migration and "interval '30 days'" in auth_migration),
 ("claim_access es single-use", 'ctx.tokenRow.used_at)return out(req,{error:"Este enlace ya fue utilizado' in auth and '.is("used_at",null).select("id").maybeSingle()' in auth),
 ("inspect_access usado no expone identidad", "if(ctx.alreadyUsed)return out(req,{ok:true,already_used:true})" in auth),
 ("login limita también por cuenta", "account_hash" in auth and "accountCount" in auth),
 ("Supabase exige correo confirmado", "email_confirmed_at" in auth),
 ("Supabase enlaza email exacto", '.eq("email",normalizedEmail)' in auth and '.ilike("email"' not in auth),
 ("solicitud pública no reabre aprobados", 'existing?.status==="pending"||existing?.status==="approved"' in access and "reopened" not in access),
 ("solicitud pública no enumera matrícula", "Si corresponde, tu solicitud será revisada" in access and "Tu matrícula ya estaba aprobada" not in access),
 ("Big Data usa endpoints propios", all(x in client for x in ["bigdata-auth","bigdata-access-request","bigdata-access-review"]) and "learning-auth" not in client and "learning-access-request" not in client and "learning-access-review" not in client),
 ("Big Data usa solo storage propio", "andesdb.lms.auth" not in client and "LEGACY_STORE" not in client),
 ("review de matrícula es exclusivo BigData", 'const COURSE_CODE = "bigdata"' in review and "BigData2026/lms/access.html" in review and 'source: "bigdata"' in review),
 ("portal evita flash de login", "Cargando tu aula…" in portal and "data-lms-auth" in portal and "setAuthState('stored')" in portal),
 ("WALL excluye heartbeat", '.neq("event_type","heartbeat")' in backend),
 ("atasco se limita a 5-30 min", "meaningfulAge>5&&meaningfulAge<=30" in backend and "present&&" in backend),
 ("WALL usa presencia backend", "r.present===true" in wall),
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
print(" - QA detecta pageerror, errores JS y overflow vertical")
print(" - autenticación BigData aislada: expiración, single-use, rate limit por cuenta y email confirmado")
print(" - solicitud/revisión de matrícula usan endpoints y URLs propias de BigData")
print(" - acceso público no enumera ni reabre matrículas aprobadas")
print(" - portal restaura sesión sin flash de login")
print(" - WALL excluye heartbeats y acota atasco 5–30 min")
