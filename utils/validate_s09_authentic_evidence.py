from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text(encoding="utf-8")

backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
migration=read("infraestructura/lms/lms-s09-authentic-evidence-v9.sql")
closed_v56=read("infraestructura/lms/lms-s09-authentic-closed-v56.sql")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
generator=read("utils/build_session9_notebook.py")
nb=json.loads(read("Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb"))
wall=read("lms/wall.html")
sources=["".join(c.get("source",[])) for c in nb.get("cells",[])]

# Regla de laboratorios: se decide ELIGIENDO en listas cerradas, no redactando (AGENTS.md §4).
import ast, re
CATALOGS=("RAZONES","ENFOQUES","LIMITES")
def closed_choice_cell():
    cell=next((s for s in sources if "resultado_defendible_1" in s and "RAZONES" in s),None)
    if cell is None: return None
    catalogs={}
    for node in ast.parse(cell).body:
        if isinstance(node,ast.Assign) and isinstance(node.targets[0],ast.Name) and node.targets[0].id in CATALOGS:
            catalogs[node.targets[0].id]=ast.literal_eval(node.value)
    menus={}
    for line in cell.splitlines():
        m=re.match(r"^(\w+) = .*#@param (\[.*\])\s*$",line)
        if m and m.group(1) in ("razon","decision","alternativa_descartada","limite"):
            menus[m.group(1)]=[x for x in json.loads(m.group(2)) if x!="Elige una opción"]
    return cell,catalogs,menus

_cc=closed_choice_cell()
def menu_matches_catalog():
    if not _cc: return False
    _,cat,menu=_cc
    return (len(cat)==3 and menu.get("razon")==cat["RAZONES"] and menu.get("decision")==cat["ENFOQUES"]
            and menu.get("alternativa_descartada")==cat["ENFOQUES"] and menu.get("limite")==cat["LIMITES"])

checks=[
 ("LAB9 sin texto libre: listas cerradas con RAZONES, ENFOQUES y LIMITES", bool(_cc) and len(_cc[1])==3 and all(len(v)>=3 for v in _cc[1].values())),
 ("LAB9: el menú desplegable es idéntico al catálogo que valida la celda", menu_matches_catalog()),
 ("LAB9: la celda rechaza texto libre y exige opciones distintas", bool(_cc) and "no se admite texto libre" in _cc[0] and "assert decision != alternativa_descartada" in _cc[0]),
 ("LAB9: ningún campo de respuesta queda como texto de instrucciones para escribir", bool(_cc) and not re.search(r'^(razon|decision|alternativa_descartada|limite|resultado_defendible_\d|falso_positivo)\s*=\s*"(?!Elige)[^"]*(explica|qué |por qué|ID o nombre)',_cc[0],re.M|re.I)),
 ("LAB9: los resultados se eligen por posición en el Top-5 propio", bool(_cc) and "posicion_defendible_1" in _cc[0] and "top5_evidencia" in _cc[0]),
 ("LAB9 authentic-review", "evaluator='authentic-review'" in migration and "requires_review" in migration),
 ("LAB9 catálogo V56 distingue herramienta y respuestas estructuradas", '"type":"tool_text"' in closed_v56 and '"type":"rank_position"' in closed_v56 and closed_v56.count('"type":"choice"')>=4),
 ("LAB9 backend usa catálogos cerrados", all(x in backend for x in ["S09_AUTHENTIC_REASONS","S09_AUTHENTIC_APPROACHES","S09_AUTHENTIC_LIMITS","closedAcademicChoice"])),
 ("LAB9 backend exige evidencia del Top-5 propio", "selected.some((x:string)=>!topHybrid.includes(x))" in backend and "new Set(selected).size!==3" in backend),
 ("constraint permite authentic-review", "bd_activity_catalog_evaluator_check" in migration and "'authentic-review'::text" in migration),
 ("rúbrica 5x2", all(x in migration for x in ["reproducible_result","supported_decision","rejected_alternative","ranking_interpretation","concrete_limit"])),
 ("campos de revisión versionados", all(x in migration for x in ["reviewed_by","reviewed_at","rubric"])),
 ("backend valida evidencia auténtica", 'catalog.evaluator==="authentic-review"' in backend and "precision_at_5" in backend and "defensible_results" in backend),
 ("envío no completa", 'verdict="pending_review"' in backend and (('completed=["correct","accepted"].includes(verdict)' in backend) or ('completed=verifiedNow&&!transferMode&&!requiresTransfer' in backend))),
 ("revisión docente explícita", "teacherReviewEvidence" in backend and "teacher_review_evidence" in backend),
 ("rúbrica backend 0-2", 'v<0||v>2' in backend and 'max:10' in backend),
 ("aceptación completa progreso", 'status:accepted?"completed":"in_progress"' in backend),
 ("rechazo no verifica evidencia", 'if(accepted)' in backend and 'event_type:"evidence_verified"' in backend),
 ("notebook llama registrar", any('lms.registrar("bd-s09-lab9"' in s for s in sources)),
 ("notebook envía decisión", any('"decision": decision' in s for s in sources)),
 ("notebook envía alternativa y límite", any('"rejected_alternative": alternativa_descartada' in s and '"limit": limite' in s for s in sources)),
 ("notebook envía rankings compactos", any('"top5_lexical": _ids(top_lex)' in s and '"top5_hybrid": _ids(top_hibrido)' in s for s in sources)),
 ("generador coincide con contrato", "FINAL_LMS_CODE" in generator and "bd-s09-lab9" in generator and "ENFOQUES" in generator),
 ("presentación no suplanta LAB9", "lab9EvidencePanel" in deck and "Evidencia auténtica · LAB 9" in deck),
 ("presentación LAB9 sin campos abiertos", all(f'<select id="{x}"' in deck for x in ["evQ","evGood","evBad","evAlt","evLim"]) and not any(f'<input id="{x}"' in deck for x in ["evQ","evGood","evBad","evAlt","evLim"])),
 ("WALL revisa con rúbrica", "RUBRIC_FIELDS" in wall and "submitEvidenceReview" in wall and "Pedir ajuste" in wall),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("S09 authentic evidence FAIL: "+", ".join(failed))
print("S09 authentic evidence: OK")
