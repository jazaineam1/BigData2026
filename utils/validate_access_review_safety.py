from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
backend=(ROOT/"infraestructura/lms/functions/bigdata-access-review/index.ts").read_text(encoding="utf-8")
ui=(ROOT/"lms/admin-users.html").read_text(encoding="utf-8")

checks=[
    ("inspect de cuenta existente", 'action === "inspect"' in backend and '"inspect"].includes(action)' in backend),
    ("aprobación exige confirmación", 'confirm_existing_account !== true' in backend),
    ("cuenta existente no sobrescribe identidad", '.update({ email: r.email, username: r.email, display_name: r.full_name, active: true' not in backend),
    ("cuenta existente no resetea contraseña", 'if (existingAccount) {' in backend and 'Cuenta existente matriculada sin cambiar nombre' in backend),
    ("rol existente se conserva", 'enrollmentRole = existingAccount ? String(lms.role || "student") : "student"' in backend),
    ("cuenta inactiva no se reactiva", 'existing_account_inactive' in backend),
    ("auditoría diferenciada", 'access.approve_existing' in backend),
    ("UI inspecciona antes de aprobar", "action:'inspect'" in ui),
    ("UI confirma cuenta existente", 'confirm_existing_account:true' in ui),
    ("UI advierte no cambio de credenciales", 'NO se cambiarán nombre, usuario, contraseña ni sesiones' in ui),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
if failed:
    raise SystemExit("Seguridad de aprobación falló: "+", ".join(failed))
print("Aprobación segura de cuentas existentes: OK")
