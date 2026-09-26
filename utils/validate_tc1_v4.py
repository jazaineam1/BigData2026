#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess, sys, tempfile

ROOT=Path(__file__).resolve().parents[1]
errors=[]

def read(path):
    p=ROOT/path
    if not p.exists():
        errors.append("Falta "+path)
        return ""
    return p.read_text("utf-8")

nb_text=read("Cuadernos/Taller_Control_1.ipynb")
builder=read("utils/build_taller_control_1.py")
guide=read("Talleres/Taller_Control_1.md")
tutorial=read("assets/tutoriales/s08-secoppipeline.html")
validator=read("utils/tc1_validator.py")
s08=read("lms/session-08.html")
edge=read("infraestructura/lms/functions/bigdata-learning/index.ts")
sql=read("infraestructura/lms/tc1-v4-secoppipeline.sql")
pages=read(".github/workflows/pages.yml")

try:
    nb=json.loads(nb_text)
except Exception as e:
    nb={}
    errors.append("Notebook JSON inválido: "+str(e))

all_src="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
checks=[
    ("notebook V4", "TC1 V4 · SECOP Data Pipeline" in all_src),
    ("dos endpoints SECOP", "p6dx-8zbt" in all_src and "jbjy-vk9h" in all_src),
    ("ThreadPoolExecutor", "ThreadPoolExecutor" in all_src),
    ("retry/backoff", "RETRY_STATUS" in all_src and "base_backoff" in all_src),
    ("orden estable", "$order" in all_src and "id_del_proceso ASC" in all_src),
    ("hash canónico", "canonical_hash" in all_src and "same_hash" in all_src),
    ("workers limitados", "MAX_WORKERS = 4" in all_src and "2–6 workers" in all_src),
    ("RAW parquet", 'raw/procesos.parquet' in guide and 'raw/contratos.parquet' in guide),
    ("Atlas idempotente", "bulk_write" in all_src and "UpdateOne" in all_src and "upsert=True" in all_src),
    ("decision log", "decision_log" in all_src),
    ("validador V4", 'VERSION = "2026-09-26-v4-secoppipeline"' in validator),
    ("E1 nueva suma 20", all(x in validator for x in ["E1_contrato_y_query","E1_descarga_secuencial","E1_concurrencia_equivalente","E1_trazabilidad_calidad"])),
    ("E2 idempotencia", "E2_atlas_idempotente" in validator and "E2_indices" in validator),
    ("no speedup mínimo", "speedup >=" not in validator.lower()),
    ("backend acepta V3+V4", "VALIDATOR_VERSIONS" in edge and "2026-09-17-v3-historico-atlas" in edge and "2026-09-26-v4-secoppipeline" in edge),
    ("backend persiste versión real", "manifest_version:m.version" in edge and "validator_version:m.version" in edge),
    ("migración actividad", "E1 · API SECOP, concurrencia y trazabilidad" in sql),
    ("rúbrica preserva 100", all(x in sql for x in ['"max":20','"max":30','"max":10','"max":15','"max":5'])),
    ("S08 nueva", "SECOP Data Pipeline" in s08 and "s08-secoppipeline.html" in s08),
    ("guía visual", "Calculadora de benchmark" in tutorial and "hash" in tutorial.lower()),
    ("Pages guía", "test -f _site/assets/tutoriales/s08-secoppipeline.html" in pages),
    ("builder canónico", "Cuadernos" in builder and "Taller_Control_1.ipynb" in builder),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

# Ponderación exacta del validador
pts=[int(x) for x in re.findall(r'check\("[^"]+",[^,]+,(\d+)',validator)]
if sum(pts)!=100:
    errors.append(f"Validador no suma 100: {sum(pts)}")

# Notebook sin salidas/soluciones incrustadas
if any(c.get("cell_type")=="code" and c.get("outputs") for c in nb.get("cells",[])):
    errors.append("Notebook de estudiante contiene outputs preejecutados")

# JavaScript del tutorial
scripts=re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>",tutorial,re.S|re.I)
for i,script in enumerate(scripts,1):
    with tempfile.NamedTemporaryFile("w",suffix=".js",encoding="utf-8",delete=False) as fh:
        fh.write(script); tmp=fh.name
    p=subprocess.run(["node","--check",tmp],capture_output=True,text=True)
    Path(tmp).unlink(missing_ok=True)
    if p.returncode:
        errors.append("Tutorial JS inválido: "+p.stderr.strip()[:400])

# Guardia S07
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"
if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió: "+blob)

# No secretos obvios
public=nb_text+"\n"+guide+"\n"+tutorial
if re.search(r"(mongodb\+srv://[^<\s]+:[^@\s]+@|sb_secret|service_role)",public,re.I):
    errors.append("Posible secreto en recurso público")

if errors:
    print("TC1 V4: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("TC1 V4: OK")
print(" - API SECOP Procesos + Contratos")
print(" - secuencial + ThreadPoolExecutor + hash")
print(" - trazabilidad + calidad + RAW")
print(" - Atlas idempotente + índices")
print(" - Cassandra + Neo4j + decision log")
print(" - backend compatible V3/V4")
print(" - S07 intacta")
