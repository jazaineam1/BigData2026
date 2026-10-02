#!/usr/bin/env python3
from pathlib import Path
import ast, hashlib, json, re, subprocess, sys, tempfile

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
validator_pinned=read("utils/tc1_validator_20261001_v7.py")
s08=read("lms/session-08.html")
edge=read("infraestructura/lms/functions/bigdata-learning/index.ts")
sql=read("infraestructura/lms/tc1-v4-secoppipeline.sql")
pages=read(".github/workflows/pages.yml")
index=read("index.html")
teacher_collab=read("lms/teacher-collaboration.html")

try:
    nb=json.loads(nb_text)
except Exception as e:
    nb={}
    errors.append("Notebook JSON inválido: "+str(e))

all_src="\n".join("".join(c.get("source",[])) for c in nb.get("cells",[]))
checks=[
    ("notebook sin versión visible", "# TC1 · SECOP Data Pipeline" in all_src and "TC1 V4" not in all_src),
    ("recap S01-S07 antes de la rúbrica", "## Antes de empezar · reconstruye el andamiaje S01–S07" in all_src and all_src.index("## Antes de empezar · reconstruye el andamiaje S01–S07") < all_src.index("## Rúbrica oficial · 100 puntos")),
    ("recap cubre las siete sesiones previas", all(("S0"+str(i)) in all_src for i in range(1,8))),
    ("recap solo usa elecciones cerradas", "#@title Autocomprobación de arranque · S01–S07" in all_src and all_src.count('#@param ["— selecciona —"') >= 7 and "input(" not in all_src[all_src.index("#@title Autocomprobación de arranque · S01–S07"):all_src.index("### Del repaso al TC1")]),
    ("recap enlaza decisiones con E1-E6", all(x in all_src for x in ["E1 · ¿puedo adquirir exactamente el mismo snapshot","E2 · ¿cómo represento ese proceso como documento","E4 · ¿qué patrón de acceso operacional","E5 · ¿qué relación contractual necesito recorrer","E6 · ¿qué decisiones tomé"])),
    ("dos endpoints SECOP", "p6dx-8zbt" in all_src and "jbjy-vk9h" in all_src),
    ("contrato API real", all(x in all_src for x in ["fecha_de_publicacion_del","id_del_portafolio","nombre_del_proveedor","proceso_de_compra"]) and "nombre_del_proveedor_adjudicado" not in all_src),
    ("join contractual correcto", '"procesos.id_del_portafolio": "contratos.proceso_de_compra"' in all_src),
    ("población adaptativa", all(x in all_src for x in ["PAGE_SIZE = 250","count_rows","N_PROCESOS = min(TARGET_PROCESOS, TOTAL_PROCESOS)","OFFSETS_PROCESOS"])),
    ("E1 ejecutable sin TODO de infraestructura", all(x in all_src for x in [
        "WHERE_PROCESOS = (","WHERE_CONTRATOS = (",
        "def descargar_secuencial","resultados.extend(rows)",
        "def descargar_concurrente","with ThreadPoolExecutor",
        "✅ Secuencial completa","✅ ThreadPoolExecutor completa"
    ]) and "return None, []" not in all_src),
    ("benchmark mismos offsets", "same_offsets" in all_src and "offsets_sequential" in all_src and "offsets_threaded" in all_src),
    ("ThreadPoolExecutor", "ThreadPoolExecutor" in all_src),
    ("micro-lab antes del reto", "demo_dos_paginas" in all_src and "no suma puntos" in all_src),
    ("retry/backoff", "RETRY_STATUS" in all_src and "base_backoff" in all_src),
    ("orden estable", "$order" in all_src and "id_del_proceso ASC" in all_src),
    ("hash canónico", "canonical_hash" in all_src and "Hash de multiconjunto" in all_src and "same_hash" in all_src),
    ("workers limitados", "MAX_WORKERS = 4" in all_src and "Use entre 2 y 6 workers" in all_src),
    ("RAW parquet", 'RAW = OUT / "raw"' in all_src and "to_parquet" in all_src),
    ("cache reanudable por páginas", all(x in all_src for x in ["RAW_PAGES","fetch_page_persisted","query_signature","_atomic_write","from_cache"])),
    ("chunks firmados", all(x in validator for x in ["_validate_page_cache","query_signature","sha256","quedaron archivos .part"])),
    ("consolidación solo tras equivalencia", all(x in all_src for x in ["No consolide RAW","same_offsets","same_rows","same_hash"])),
    ("Atlas idempotente", "bulk_write" in all_src and "UpdateOne" in all_src and "upsert=True" in all_src),
    ("decision log", "decision_log" in all_src),
    ("carga estimada 6–8h", "6–8 horas" in all_src and "Dedicación orientativa por grupo" in all_src),
    ("microdefensa estructurada", "defensa_grupal" in all_src and "06_microdefensa_grupal.json" in all_src and "E6_microdefensa_grupal" in validator and all_src.count("#@param") >= 12),
    ("sin respuesta abierta E6", "respuesta_concurrencia" not in all_src and "respuesta_calidad" not in all_src),
    ("validador actual", 'VERSION = "2026-10-01-secoppipeline-v7"' in validator),
    ("validador fijado idéntico", validator == validator_pinned and bool(validator_pinned)),
    ("E1 adquisición completa", all(x in validator for x in ["E1_contrato_y_query","E1_descarga_secuencial","E1_concurrencia_equivalente","E1_trazabilidad_calidad"])),
    ("E2 idempotencia", "E2_atlas_idempotente" in validator and "E2_indices" in validator),
    ("no speedup mínimo", "speedup >=" not in validator.lower()),
    ("backend exige versión actual", "VALIDATOR_VERSIONS" in edge and "2026-10-01-secoppipeline-v7" in edge and "security_no_secrets" in edge),
    ("gate de secretos", "secret_patterns" in validator and '"gates":gates' in validator and '".ipynb"' in validator and "ENTREGA BLOQUEADA" in validator),
    ("backend persiste versión real", "manifest_version:m.version" in edge and "validator_version:m.version" in edge),
    ("calificación grupal", "tc1GroupContext" in edge and "syncManifestGroupGradebook" in edge and "lms_group_submissions_v2" in edge and "Calificación grupal TC1" in edge),

    ("migración actividad", "E1 · API SECOP, concurrencia y trazabilidad" in sql),
    ("rúbrica 25/25/10/15/15/10", 'STAGE_MAX = {"E1": 25, "E2": 25, "E3": 10, "E4": 15, "E5": 15, "E6": 10}' in validator and sql.count('"max":25')>=2 and sql.count('"max":15')>=2 and sql.count('"max":10')>=2),
    ("S08 nueva", "SECOP Data Pipeline" in s08 and "s08-secoppipeline.html" not in s08 and "V4" not in s08),
    ("S08 informa entrega externa", "no se entrega por el LMS" in s08 and "Google Drive + correo institucional" in s08 and "jzaineam@ucentral.edu.co" in s08),
    ("S08 sin acciones redundantes", "Ruta simple" not in s08 and "Trabajar etapa" not in s08 and "Qué cuenta como completado" not in s08),
    ("S08 progreso plegable", "Ver avance por etapa" in s08 and "stageSummary" in s08),

    ("sin guía Markdown redundante", not (ROOT/"Talleres/Taller_Control_1.md").exists()),
    ("referencia no procedimental", "Pistas, no respuestas" in tutorial and "Paso a paso" not in tutorial and "hash" in tutorial.lower()),
    ("Pages referencia", "test -f _site/assets/tutoriales/s08-secoppipeline.html" in pages and "Talleres/Taller_Control_1.md" not in pages),
    ("builder canónico", "Cuadernos" in builder and "Taller_Control_1.ipynb" in builder),
    ("portada sin bloque redundante", "Aprender = comprender, practicar, comprobar y transferir." not in index and "La evidencia importa más que completar una pantalla." not in index and 'id="metodo"' not in index),
    ("carga horaria vive en notebook, no en LMS", "mínimo 6 horas por grupo" not in s08 and "6–8 horas" not in s08 and "6–8 horas por grupo" in all_src and "'estimated_minutes',360" in sql),
    ("LMS grupal en SQL", "lms_assignment_group_settings_v2" in sql and "'group_assessment',true" in sql and "Proyecto grupal" in sql),
    ("manifest único por grupo", "Este manifest ya fue registrado por otro equipo" in edge),
    ("rúbrica detallada solo en notebook", "Rúbrica oficial · 100 puntos" not in s08 and "Concurrencia equivalente" not in s08 and "Microdefensa grupal" not in s08 and "E1 · Adquisición SECOP" in all_src),
    ("evidencia auditable por Drive y correo", "Google Drive" in all_src and "jzaineam@ucentral.edu.co" in all_src and "sello de tiempo" in all_src.lower() and "Google Drive + correo" in sql),
    ("revisión docente abre evidencia", "Abrir evidencia del grupo" in teacher_collab and "Desglose automático" in teacher_collab),
    ("notebook incluye rúbrica detallada", "E1 · Adquisición SECOP" in all_src and "E6 · Decisiones y entrega" in all_src and "TOTAL" in all_src),
    ("ruta paso a paso visible", all(x in all_src for x in [
        "Qué debe hacer y qué debe entregar cada grupo",
        "Condición para pasar",
        "Checkpoint de E1",
        "Entrega final del grupo"
    ])),
    ("metodología de entrega explícita", all(x in all_src for x in ["Entrega final del grupo","manifest_tc1.json","Google Drive","correo del docente","GitHub opcional"])),
    ("GitHub opcional con tutorial", all(x in all_src for x in ["GitHub opcional","Add file → Upload files","git init","git push -u origin main","jazaineam1"])),
    ("fecha máxima explícita", "17 de octubre de 2026" in all_src and "11:59 p. m." in all_src and "2026-10-17T23:59:59-05:00" in sql and "17 de octubre de 2026" in s08),
    ("backend respeta fecha máxima", 'select("id,max_attempts,max_score,due_at")' in edge and "La fecha máxima de entrega del TC1 ya venció." in edge),
]
for label,ok in checks:
    if not ok: errors.append("Falla: "+label)

# Ponderación exacta del validador: AST, no regex, porque algunos check() son multilínea.
try:
    tree=ast.parse(validator)
    pts=[]
    for node in ast.walk(tree):
        if (
            isinstance(node,ast.Call)
            and isinstance(node.func,ast.Name)
            and node.func.id=="check"
            and len(node.args)>=3
            and isinstance(node.args[2],ast.Constant)
            and isinstance(node.args[2].value,int)
        ):
            pts.append(node.args[2].value)
    if sum(pts)!=100:
        errors.append(f"Validador no suma 100: {sum(pts)}; puntos={pts}")
except Exception as e:
    errors.append("No se pudo inspeccionar ponderación del validador: "+str(e))

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
