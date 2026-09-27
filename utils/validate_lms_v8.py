from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

auth=read("infraestructura/lms/functions/bigdata-auth/index.ts")
ops=read("infraestructura/lms/functions/bigdata-lms-ops/index.ts")
client=read("lms/assets/bigdata-lms.js")
css=read("lms/assets/bigdata-lms.css")
account=read("lms/account.html")
ops_ui=read("lms/admin-operations.html")
runbook=read("infraestructura/lms/OPERATIONS_V8.md")
tests=read("tests/lms-v8-ops-a11y.spec.js")

checks=[
    ("TTL estudiante 30 días", 'student:{ttl_hours:30*24,persistent:true' in auth),
    ("TTL docente 12 h", 'teacher:{ttl_hours:12,persistent:false' in auth),
    ("TTL admin 4 h", 'admin:{ttl_hours:4,persistent:false' in auth),
    ("issueSession usa policy", "policy=sessionPolicy(user.role)" in auth and "ttlHours=policy.ttl_hours" in auth),
    ("me expone policy", "session_policy:" in auth and "policy.label" in auth),
    ("cliente respeta no persistencia", "if(x.persistent===false)localStorage.removeItem(STORE)" in client),
    ("login conserva persistent", "persistent:x.persistent!==false" in client),
    ("skip link automático", "ensureA11yShell" in client and "Saltar al contenido principal" in client),
    ("mensajes accesibles", "aria-live" in client and "type==='err'?'alert':'status'" in client),
    ("foco y forced colors", ".skip-link" in css and "@media(forced-colors:active)" in css and ":focus-visible" in css),
    ("observabilidad server-side", "async function healthSnapshot" in ops and "lms_login_attempts" in ops and "bd_realtime_signals" in ops and 'transport:"broadcast"' in ops),
    ("conteos server-side", 'select("id",{count:"exact",head:true})' in ops and "const activeSessions=Number(explicitSessionsQ.count||0)" in ops),
    ("observabilidad sin hashes login", '.from("lms_login_attempts").select("id",{count:"exact",head:true})' in ops and 'select("id,key_hash' not in ops and '"key_hash"' not in ops),
    ("RPO RTO", "const RPO_HOURS=24" in ops and "const RTO_HOURS=4" in ops and 'platform_backup_status:"not_observed_by_lms"' in ops),
    ("capacidades por rol", "roleCapabilities" in ops and '"retention.cleanup"' in ops),
    ("panel de salud", 'id="health"' in ops_ui and "Snapshot académico" in ops_ui and "No equivale al backup administrado" in ops_ui and "Capacidades efectivas" in ops_ui),
    ("cuenta muestra policy", 'id="sessionPolicy"' in account and "Política de esta cuenta" in account),
    ("revocación individual", "revoke_session" in account and "Cerrar esta sesión" in account),
    ("runbook documentado", "RPO objetivo de plataforma: 24 horas" in runbook and "RTO objetivo: 4 horas" in runbook and "no sustituye el backup de plataforma" in runbook),
    ("regresiones V8", "WCAG" in tests and "no persistente" in tests and "observabilidad" in tests),
]

failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
if failed:
    raise SystemExit("Validación LMS V8 falló: "+", ".join(failed))
print("LMS V8 ops/a11y: OK")
