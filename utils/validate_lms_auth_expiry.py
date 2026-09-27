from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FUNCS=ROOT/"infraestructura/lms/functions"

targets=[
    "bigdata-auth","bigdata-access-review","bigdata-learning","bigdata-lms-core",
    "bigdata-lms-assess","bigdata-lms-interop","bigdata-lms-ops","bigdata-session9","bigdata-session"
]

errors=[]
for slug in targets:
    path=FUNCS/slug/"index.ts"
    if not path.exists():
        errors.append(f"Falta {path.relative_to(ROOT)}")
        continue
    text=path.read_text(encoding="utf-8")
    if "if(!s.persistent&&" in text or "if (!s.persistent &&" in text:
        errors.append(f"{slug}: todavía permite omitir expiración cuando persistent=true")
    if slug not in ("bigdata-auth","bigdata-access-review"):
        if 'created_at' not in text:
            errors.append(f"{slug}: no recupera created_at para sesiones legadas")
        if "deadline=" not in text:
            errors.append(f"{slug}: no calcula deadline uniforme")
        if "deadline<=Date.now()" not in text and "deadline <= Date.now()" not in text:
            errors.append(f"{slug}: no rechaza deadline vencido")

auth=(FUNCS/"bigdata-auth/index.ts").read_text(encoding="utf-8")
review=(FUNCS/"bigdata-access-review/index.ts").read_text(encoding="utf-8")
for slug,text in [("bigdata-auth",auth),("bigdata-access-review",review)]:
    if "deadline" not in text or "persistent?30:1" not in text:
        errors.append(f"{slug}: contrato de expiración no coincide con 30d/1d fallback")
    if "deadline<=Date.now()" not in text and "deadline <= Date.now()" not in text:
        errors.append(f"{slug}: no rechaza deadline vencido")

if errors:
    print("LMS auth expiry: FAIL")
    for e in errors: print(" -",e)
    raise SystemExit(1)
print("LMS auth expiry: OK")
