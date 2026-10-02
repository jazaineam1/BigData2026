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
validator=read("utils/tc1_validator.py")
validator_pinned=read("utils/tc1_validator_20261001_v8.py")
s08=read("lms/session-08.html")
sql=read("infraestructura/lms/tc1-v4-secoppipeline.sql")

try:
    nb=json.loads(nb_text)
except Exception as e:
    nb={}
    errors.append("Notebook JSON inválido: "+str(e))

all_src="\n".join(
    "".join(c.get("source",[])) if isinstance(c.get("source",[]),list) else str(c.get("source",""))
    for c in nb.get("cells",[])
)

checks=[
    ("V8 visible", "VERSIÓN OPERATIVA: V8" in all_src and "2026-10-01-tc1-native-v8" in all_src),
    ("objetivo explícito", "## Objetivo del taller" in all_src and "expediente de revisión reproducible" in all_src),
    ("una sola historia", "No son seis ejercicios independientes" in all_src and "un solo caso" in all_src.lower()),
    ("hoja de ruta", "## Hoja de ruta" in all_src and all(x in all_src for x in ["E1 · Snapshot","E2 · Atlas","E3 · Cassandra","E4 · Neo4j","E5 · Cierre"])),
    ("regla de avance", "No avances porque existe una celda siguiente" in all_src),
    ("qué está provisto/evaluado", "Qué está provisto y qué se evalúa" in all_src and "No evaluado" in all_src),
    ("rúbrica 15/30/20/25/10", 'STAGE_MAX = {"E1":15, "E2":30, "E3":20, "E4":25, "E5":10}' in validator),
    ("dos endpoints SECOP", "p6dx-8zbt" in all_src and "jbjy-vk9h" in all_src),
    ("join correcto", '"procesos.id_del_portafolio": "contratos.proceso_de_compra"' in all_src),
    ("E1 ejecutable", all(x in all_src for x in ["def descargar_secuencial","def descargar_concurrente","same_offsets","same_rows","same_hash"])),
    ("Atlas usa interfaz nativa", all(x in all_src for x in ["Atlas Data Explorer","Aggregations","pipeline_guardado"])),
    ("PyMongo solo infraestructura", "# Infraestructura provista · puente de carga a Atlas; NO se evalúa PyMongo" in all_src),
    ("Astra usa CQL Console", "Astra CQL Console" in all_src and "CQL_CREATE_STUDENT" in all_src and "ASTRA_TOP5_IDS" in all_src),
    ("Neo4j usa Aura Query", "Aura Query" in all_src and "CYPHER_QUERY_STUDENT" in all_src and "NEO4J_TOP_PROVEEDOR_NIT" in all_src),
    ("sin driver Cassandra evaluado", "from cassandra.cluster import Cluster" not in all_src and "session.execute(" not in all_src),
    ("sin driver Neo4j evaluado", "from neo4j import GraphDatabase" not in all_src and "GraphDatabase.driver(" not in all_src),
    ("sin NetworkX", "networkx" not in all_src.lower()),
    ("sin preguntas abiertas", 'input("Alternativa' not in all_src and "respuesta_concurrencia" not in all_src and all_src.count("#@param") >= 8),
    ("entrega tres archivos", "## Entrega final · exactamente tres archivos" in all_src and all(x in all_src for x in ["TC1_<PAREJA_ID>.ipynb","TC1_<PAREJA_ID>.zip","manifest_tc1.json"])),
    ("Drive restringido", "Acceso general: Restringido" in all_src and "jzaineam@ucentral.edu.co" in all_src),
    ("fecha máxima", "17 de octubre de 2026" in all_src and "11:59 p. m." in all_src),
    ("validador fijado", validator==validator_pinned and bool(validator_pinned)),
    ("validator V8", 'VERSION = "2026-10-01-tc1-native-v8"' in validator),
    ("builder canónico", "Taller_Control_1.ipynb" in builder and "CELLS" in builder),
    ("S08 explica un caso/tres modelos", "Compras Claras" in s08 and "tres modelos" in s08),
    ("S08 sin entrega LMS", "no se entrega por el LMS" in s08 and "Google Drive + correo institucional" in s08),
    ("SQL V8", "2026-10-01-tc1-native-v8" in sql and "15" in sql and "30" in sql and "25" in sql),
]
for label,ok in checks:
    if not ok:
        errors.append("Falla: "+label)

# Puntos exactos por AST
try:
    tree=ast.parse(validator)
    pts=[]
    for node in ast.walk(tree):
        if (
            isinstance(node,ast.Call)
            and isinstance(node.func,ast.Name)
            and node.func.id=="check"
            and len(node.args)>=4
            and isinstance(node.args[3],ast.Constant)
            and isinstance(node.args[3].value,int)
        ):
            pts.append(node.args[3].value)
    if sum(pts)!=100:
        errors.append(f"Validador no suma 100: {sum(pts)}; puntos={pts}")
except Exception as e:
    errors.append("No se pudo inspeccionar la ponderación: "+str(e))

# Notebook sin outputs pre-ejecutados
if any(c.get("cell_type")=="code" and c.get("outputs") for c in nb.get("cells",[])):
    errors.append("Notebook de estudiante contiene outputs preejecutados")

# No secretos obvios
if re.search(r"(mongodb\+srv://[^<\s]+:[^@\s]+@|AstraCS:[A-Za-z0-9_-]{20,}|service_role)",nb_text,re.I):
    errors.append("Posible secreto en notebook público")

# S07 intacta
s07=ROOT/"Presentaciones/s07-del-vecindario-al-texto.html"
if s07.exists():
    b=s07.read_bytes()
    blob=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if blob!="07e99d34a8896a9a6b4c5bf39cb7619a953fe0b8":
        errors.append("S07 cambió: "+blob)

if errors:
    print("TC1: FAIL")
    for e in errors:
        print(" -",e)
    sys.exit(1)

print("TC1 V8: OK")
print(" - objetivo + hoja de ruta visibles")
print(" - un caso / tres modelos")
print(" - Atlas Data Explorer / Astra CQL Console / Aura Query")
print(" - sin drivers Python como trabajo evaluado")
print(" - entrega de tres archivos")
print(" - validador 100 puntos")
