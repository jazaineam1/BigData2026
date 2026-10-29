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

# La compatibilidad LAB9 sigue comprobándose en el backend y migraciones.
# El cuaderno actual produce un expediente local; no usa el envío LAB9 retirado.
from s09_current_contract import validate_notebook,active_labs,ACTIVE_LABS
current_ok=validate_notebook()
checks=[
 ("Cuaderno vigente exporta expediente trazable, sin credenciales ni envío LAB9",current_ok),
 ("LAB activos coinciden con mapa vigente",active_labs(deck)==ACTIVE_LABS),
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
 ("WALL revisa con rúbrica", "RUBRIC_FIELDS" in wall and "submitEvidenceReview" in wall and "Pedir ajuste" in wall),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("S09 authentic evidence FAIL: "+", ".join(failed))
print("S09 authentic evidence: OK")
