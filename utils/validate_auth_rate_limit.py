from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
auth=(ROOT/"infraestructura/lms/functions/bigdata-auth/index.ts").read_text(encoding="utf-8")
ops=(ROOT/"infraestructura/lms/functions/bigdata-lms-ops/index.ts").read_text(encoding="utf-8")
checks=[
 ("límite fuerte solo IP+cuenta", 'if((count||0)>=8)' in auth and '(accountCount||0)>=12' not in auth),
 ("retardo progresivo global", 'globalFailures>=6' in auth and 'Math.min(2000,250*(globalFailures-5))' in auth),
 ("respuesta 429 no revela cuenta", 'Demasiados intentos desde este origen' in auth),
 ("credencial inválida sigue genérica", 'Usuario o contraseña incorrectos' in auth),
 ("operaciones documentan política real", '8 fallos por combinación IP+cuenta' in ops and 'retardo progresivo sin bloqueo global' in ops),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("Auth rate limit FAIL: "+", ".join(failed))
print("Auth progressive rate limit: OK")
