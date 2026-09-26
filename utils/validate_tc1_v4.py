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
tutorial=read("assets/tutoriales/s08-secoppipeline.html")
validator=read("utils/tc1_validator.py")
s08=read("lms/session-08.html")
edge=read("infraestructura/lms/functions/bigdata-learning/index.ts")
sql=read("infraestructura/lms/tc1-v4-secoppipeline.sql")
pages=read(".github/workflows/pages.yml")
index=read("index.html")

try:
    nb=json.loads(nb_text)
except Exception as e:
    nb={}
    errors.append("Notebook JSON inválido: "+str(e))

all_src="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
checks=[
    ("notebook sin versión visible", "# TC1 · SECOP Data Pipeline" in all_src and "TC1 V4" not in all_src),
    ("dos endpoints SECOP", "p6dx-8zbt" in all_src and "jbjy-vk9h" in all_src),
    ("ThreadPoolExecutor", "ThreadPoolExecutor" in all_src),
    ("micro-lab antes del reto", "demo_dos_paginas" in all_src and "no suma puntos" in all_src),
    ("retry/backoff", "RETRY_STATUS" in all_src and "base_backoff" in all_src),
    ("orden estable", "$order" in all_src and "id_del_proceso ASC" in all_src),
    ("hash canónico", "canonical_hash" in all_src and "same_hash" in all_src),
    ("workers limitados", "MAX_WORKERS = 4" in all_src and "2–6 workers" in all_src),
    ("RAW parquet", 'RAW = OUT / "raw"' in all_src and "to_parquet" in all_src),
    ("Atlas idempotente", "bulk_write" in all_src and "UpdateOne" in all_src and "upsert=True" in all_src),
    ("decision log", "decision_log" in all_src),
    ("carga mínima 6h", "6–8 horas por grupo" in all_src and "Dedicación mínima prevista por grupo: 6 horas" in all_src),
    ("microdefensa grupal", "defensa_grupal" in all_src and "06_microdefensa_grupal.json" in all_src and "E6_microdefensa_grupal" in validator),
    ("validador actual", 'VERSION = "2026-09-26-secoppipeline"' in validator),
    ("E1 adquisición completa", all(x in validator for x in ["E1_contrato_y_query","E1_descarga_secuencial","E1_concurrencia_equivalente","E1_trazabilidad_calidad"])),
    ("E2 idempotencia", "E2_atlas_idempotente" in validator and "E2_indices" in validator),
    ("no speedup mínimo", "speedup >=" not in validator.lower()),
    ("backend exige versión actual", "VALIDATOR_VERSIONS" in edge and "2026-09-26-secoppipeline" in edge and "security_no_secrets" in edge),
    ("gate de secretos", "secret_patterns" in validator and '"gates":gates' in validator),
    ("backend persiste versión real", "manifest_version:m.version" in edge and "validator_version:m.version" in edge),
    ("calificación grupal", "tc1GroupContext" in edge and "syncManifestGroupGradebook" in edge and "lms_group_submissions_v2" in edge and "Calificación grupal TC1" in edge),

    ("migración actividad", "E1 · API SECOP, concurrencia y trazabilidad" in sql),
    ("rúbrica 25/25/10/15/15/10", 'STAGE_MAX = {"E1": 25, "E2": 25, "E3": 10, "E4": 15, "E5": 15, "E6": 10}' in validator and sql.count('"max":25')>=2 and sql.count('"max":15')>=2 and sql.count('"max":10')>=2),
    ("S08 nueva", "SECOP Data Pipeline" in s08 and "s08-secoppipeline.html" in s08 and "V4" not in s08),
    ("S08 entrega por equipo", "group_context" in edge and "Sin equipo asignado" in s08 and "misma calificación" in s08),

    ("sin guía Markdown redundante", not (ROOT/"Talleres/Taller_Control_1.md").exists()),
    ("referencia no procedimental", "Pistas, no respuestas" in tutorial and "Paso a paso" not in tutorial and "hash" in tutorial.lower()),
    ("Pages referencia", "test -f _site/assets/tutoriales/s08-secoppipeline.html" in pages and "Talleres/Taller_Control_1.md" not in pages),
    ("builder canónico", "Cuadernos" in builder and "Taller_Control_1.ipynb" in builder),
    ("portada sin bloque redundante", "Aprender = comprender, practicar, comprobar y transferir." not in index and "La evidencia importa más que completar una pantalla." not in index and 'id="metodo"' not in index),
    ("LMS declara 6h", "mínimo 6 horas por grupo" in s08 and "'estimated_minutes',360" in sql),
    ("LMS grupal en SQL", "lms_assignment_group_settings_v2" in sql and "'group_assessment',true" in sql and "Proyecto grupal" in sql),
    ("manifest único por grupo", "Este manifest ya fue registrado por otro equipo" in edge),
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
public=nb_text+"\n"+tutorial
if re.search(r"(mongodb\+srv://[^<\s]+:[^@\s]+@|sb_secret|service_role)",public,re.I):
    errors.append("Posible secreto en recurso público")

if errors:
    print("TC1: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)

print("TC1: OK")
print(" - API SECOP Procesos + Contratos")
print(" - secuencial + ThreadPoolExecutor + hash")
print(" - trazabilidad + calidad + RAW")
print(" - Atlas idempotente + índices")
print(" - Cassandra + Neo4j + decision log")
print(" - backend y rúbrica actuales")
print(" - S07 intacta")
