#!/usr/bin/env python3
"""Escaneo de secretos y datos personales sobre los archivos versionados.

El repositorio es público: una credencial o el correo de un estudiante que entra a Git
queda copiado y cacheado aunque se borre después (AGENTS.md §13). Este escaneo es la segunda
barrera; la primera es .gitignore.

Criterio: pocas reglas de alta señal, sin dependencias de terceros y con una lista de
excepciones que exige una RAZÓN por cada una. Los valores encontrados NUNCA se imprimen
completos: solo un fragmento, para que el log del CI no vuelva a filtrar el secreto.

Uso:  python utils/scan_secrets_pii.py            (archivos versionados)
      python utils/scan_secrets_pii.py --all      (también los no ignorados sin versionar)
"""
from pathlib import Path
import base64
import fnmatch
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ALL = "--all" in sys.argv

# Contenido de datos abiertos o binario: no se inspecciona su texto (sí su nombre).
SKIP_CONTENT = (".csv", ".tsv", ".parquet", ".duckdb", ".zip", ".png", ".jpg", ".jpeg", ".gif", ".webp",
                ".pdf", ".ico", ".woff", ".woff2", ".pyc", ".ipynb_checkpoints", ".gz", ".xlsx", ".docx", ".pptx")
# Un cuaderno con salidas pesa varios MB y es justo donde se cuelan las cadenas de conexión:
# un límite bajo deja ciego al escáner (ya pasó con uno de 7,8 MB).
MAX_BYTES = 30_000_000

# Archivos que jamás deben estar versionados (por nombre).
FORBIDDEN_NAMES = [
    "*respuestas*.xlsx", "Encuesta*.xlsx", "*roster*", "*.secret", "secure-connect-*.zip",
    "token.json", "databricks.env", ".env", "*/.env",
]
FORBIDDEN_ALLOW = {".env.example", "databricks.env.example", "Airflow/.env.example"}

SECRET_PATTERNS = {
    "clave privada": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"),
    "Supabase secret key": re.compile(r"\bsb_secret_[A-Za-z0-9_\-]{16,}"),
    "clave estilo OpenAI (sk-)": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_\-]{24,}"),
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "token de GitHub": re.compile(r"\b(?:ghp|gho|ghs|ghu)_[A-Za-z0-9]{30,}|\bgithub_pat_[A-Za-z0-9_]{40,}"),
    "token de Slack": re.compile(r"\bxox[baprs]-[A-Za-z0-9\-]{10,}"),
    "API key de Google": re.compile(r"\bAIza[0-9A-Za-z_\-]{35}\b"),
    "URI con contraseña": re.compile(
        r"\b(?:mongodb(?:\+srv)?|postgres(?:ql)?|mysql|redis|amqp)://[^/\s:@'\"<>]+:([^@\s'\"<>]{3,})@"),
    "JWT": re.compile(r"\beyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
}
# Valores que son marcadores de posición y no credenciales.
PLACEHOLDER = re.compile(r"^(?:<.*>|\$\{.*\}|\{\{.*\}\}|x{3,}|\*{3,}|changeme|password|contrase[nñ]a|clave|pass|"
                         r"secret|tu[_-]?\w*|your[_-]?\w*|usuario|user|example|placeholder|dummy|test|airflow|"
                         r"mongo|root|admin)$", re.I)

EMAIL = re.compile(r"\b[A-Za-z0-9._%+\-]+@([A-Za-z0-9\-]+(?:\.[A-Za-z0-9\-]+)+)\b")
# Dominios que no son personas: documentación, pruebas, remitentes técnicos.
EMAIL_DOMAIN_OK = ("example.com", "example.org", "example.net", "test.com", "ejemplo.com", "users.noreply.github.com",
                   "noreply.github.com", "anthropic.com", "localhost", "tu-correo.com", "correo.com", "domain.com")
EMAIL_LOCAL_OK = ("noreply", "no-reply", "correo", "usuario", "user", "nombre", "estudiante", "docente",
                  "email", "tu", "tucorreo", "mi", "admin", "soporte", "support", "info", "test")

# (ruta glob, tipo de hallazgo) -> razón. Cada excepción debe justificarse.
ALLOW = {
    # Llaves publicables/anónimas de Supabase están pensadas para viajar al navegador; RLS protege los datos.
    ("lms/*", "JWT"): "JWT anónimo de Supabase pensado para el navegador (RLS); revisar que role=anon",
}


def tracked_files():
    cmd = ["git", "ls-files", "-z"] + (["--others", "--exclude-standard"] if ALL else [])
    out = subprocess.run(cmd, cwd=ROOT, capture_output=True, check=True).stdout.decode("utf-8", "replace")
    files = [f for f in out.split("\0") if f]
    if ALL:
        cached = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, check=True).stdout
        files += [f for f in cached.decode("utf-8", "replace").split("\0") if f]
    return sorted(set(files))


def jwt_role(token):
    try:
        payload = token.split(".")[1]
        payload += "=" * (-len(payload) % 4)
        return json.loads(base64.urlsafe_b64decode(payload)).get("role", "?")
    except Exception:
        return "?"


def redact(s):
    s = s.strip()
    return (s[:4] + "…(" + str(len(s)) + " car.)") if len(s) > 8 else "…"


def allowed(path, kind):
    return any(fnmatch.fnmatch(path, g) and kind == k for (g, k) in ALLOW)


# Hallazgos CONOCIDOS: no bloquean el CI, pero se muestran SIEMPRE como aviso con su razón, para
# que no se olviden. Una excepción sin razón, o que deja de coincidir con algo, es un error.
KNOWN = [
    ("Cuadernos/8_NoSQL_Mongo.ipynb", "URI con contraseña",
     "URGENTE: URIs de MongoDB Atlas con contraseña de aspecto real, versionadas desde 2023-11-02. "
     "Rotar/eliminar esos usuarios en Atlas y sustituir por un marcador; después retirar esta excepción."),
    ("infraestructura/scripts/seed_mongo.py", "URI con contraseña", "credencial de práctica del docker-compose local; no expone un servicio remoto"),
    ("infraestructura/modules/04-nosql/README.md", "URI con contraseña", "credencial de práctica del docker-compose local; no expone un servicio remoto"),
    ("Cuadernos/12_MongoDB_Atlas_NoSQL_Moderno.ipynb", "URI con contraseña", "credencial de práctica del docker-compose local; no expone un servicio remoto"),
    ("utils/make_12_mongodb_atlas_nosql.py", "URI con contraseña", "generador del cuaderno anterior: misma credencial local de práctica"),
    ("Cuadernos/4_Atlas_Cassandra_Laura.ipynb", "URI con contraseña", "plantilla con variables (f-string), no una credencial"),
    ("tests/*.js", "correo (posible dato personal)", "correos ficticios de prueba (fixtures de Playwright)"),
    ("utils/build_session3_notebook.py", "correo (posible dato personal)",
     "contacto institucional del curso en el User-Agent del rastreador: identificación visible exigida por AGENTS.md §10"),
    ("Cuadernos/5_Atlas_Cassandra_Query_First.ipynb", "correo (posible dato personal)",
     "correo institucional del docente como contacto de una tarea (dato del propio docente, no de un estudiante)"),
    ("Cuadernos/Taller_Control_1.ipynb", "correo (posible dato personal)",
     "correo institucional del docente como canal oficial de entrega del TC1; dato del propio docente, no de un estudiante"),
    ("infraestructura/lms/tc1-v4-secoppipeline.sql", "correo (posible dato personal)",
     "metadato docente del TC1: canal oficial de entrega externo al LMS"),
    ("lms/session-08.html", "correo (posible dato personal)",
     "superficie S08: informa el correo institucional del docente para la entrega"),
    ("utils/validate_lms_s08.py", "correo (posible dato personal)",
     "QA verifica que S08 muestre el canal institucional correcto"),
    ("utils/tc1_contrato.py", "correo (posible dato personal)",
     "contrato del TC1: correo institucional del docente como canal oficial de entrega"),
    ("assets/tutoriales/s08-secoppipeline.html", "correo (posible dato personal)",
     "checklist del TC1: correo institucional del docente como canal oficial de entrega"),
    ("utils/test_tc1_v9.py", "URI con contraseña",
     "credencial ficticia que la prueba inyecta para comprobar que el validador bloquea la entrega"),
    ("utils/build_session4_notebook.py", "URI con contraseña", "plantilla con variables (f-string), no una credencial"),
    ("Datos/noticias_*.json", "correo (posible dato personal)", "datos periodísticos públicos: correos que aparecen en el texto de los artículos"),
    ("Cuadernos/2_multiprocessing.ipynb", "correo (posible dato personal)", "ejemplos didácticos de validación de correos"),
]
_known_used = set()


def known_reason(path, kind):
    for i, (g, k, why) in enumerate(KNOWN):
        if fnmatch.fnmatch(path, g) and kind == k:
            _known_used.add(i)
            return why
    return None


findings = []
files = tracked_files()
for rel in files:
    name = rel.rsplit("/", 1)[-1]
    if rel not in FORBIDDEN_ALLOW and any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(name, g) for g in FORBIDDEN_NAMES):
        findings.append((rel, 0, "archivo que no debe versionarse", name))
        continue
    p = ROOT / rel
    if rel.lower().endswith(SKIP_CONTENT) or not p.is_file():
        continue
    try:
        if p.stat().st_size > MAX_BYTES:
            continue
        text = p.read_bytes().decode("utf-8", "replace")
    except OSError:
        continue
    for lineno, line in enumerate(text.splitlines(), 1):
        for kind, rx in SECRET_PATTERNS.items():
            for m in rx.finditer(line):
                if kind == "URI con contraseña" and PLACEHOLDER.match(m.group(1)):
                    continue
                if kind == "JWT":
                    role = jwt_role(m.group(0))
                    kind_eff = "JWT service_role (CRÍTICO)" if role == "service_role" else "JWT"
                    if kind_eff == "JWT" and allowed(rel, "JWT") and role == "anon":
                        continue
                    findings.append((rel, lineno, kind_eff + f" role={role}", redact(m.group(0))))
                    continue
                if allowed(rel, kind):
                    continue
                findings.append((rel, lineno, kind, redact(m.group(0))))
        for m in EMAIL.finditer(line):
            domain = m.group(1).lower()
            local = m.group(0).split("@")[0].lower()
            tld = domain.rsplit(".", 1)[-1]
            if not tld.isalpha():                      # 'paquete@2.117.1' es una versión, no un correo
                continue
            if domain.endswith(EMAIL_DOMAIN_OK) or local in EMAIL_LOCAL_OK or domain.endswith(("mongodb.net",)):
                continue
            if tld in ("png", "jpg", "svg", "js", "css", "gif", "webp"):   # 'logo@2x.png'
                continue
            findings.append((rel, lineno, "correo (posible dato personal)", redact(m.group(0))))

# Separar hallazgos NUEVOS (bloquean) de CONOCIDOS (avisan con su razón).
new, known = [], []
for f in findings:
    why = known_reason(f[0], f[2])
    (known if why else new).append(f + (why,))
stale = [KNOWN[i] for i in range(len(KNOWN)) if i not in _known_used]

print(f"Escaneados {len(files)} archivos versionados.")
if known:
    print(f"\nCONOCIDOS (no bloquean, pero siguen pendientes): {len(known)}")
    reasons = {}
    for rel, ln, kind, frag, why in known:
        reasons.setdefault((why, kind), []).append(rel)
    for (why, kind), rels in sorted(reasons.items(), key=lambda kv: not kv[0][0].startswith("URGENTE")):
        flag = "::warning::" if why.startswith("URGENTE") else ""
        print(f"{flag}  [{kind}] {len(rels)} coincidencia(s) en {', '.join(sorted(set(rels)))}\n      razón: {why}")
if stale:
    print("\nExcepciones en KNOWN que ya no coinciden con nada (bórralas):")
    for g, k, why in stale:
        print(f"  {g} · {k}")
if new:
    print(f"\nHALLAZGOS NUEVOS: {len(new)}")
    by_kind = {}
    for f in new:
        by_kind.setdefault(f[2], []).append(f)
    for kind, rows in sorted(by_kind.items()):
        print(f"\n[{kind}] {len(rows)}")
        for rel, ln, _, frag, _why in rows[:15]:
            print(f"  {rel}:{ln}  {frag}")
        if len(rows) > 15:
            print(f"  … y {len(rows) - 15} más")
    sys.exit(1)
if stale:
    sys.exit(1)
print("\nSin hallazgos nuevos.")
sys.exit(0)
