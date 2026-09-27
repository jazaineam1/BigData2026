from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
def read(p): return (ROOT/p).read_text(encoding="utf-8")

backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
migration=read("infraestructura/lms/lms-s09-authentic-evidence-v9.sql")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
generator=read("utils/build_session9_notebook.py")
nb=json.loads(read("Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb"))
wall=read("lms/wall.html")
sources=["".join(c.get("source",[])) for c in nb.get("cells",[])]

checks=[
 ("LAB9 authentic-review", "evaluator='authentic-review'" in migration and "requires_review" in migration),
 ("constraint permite authentic-review", "bd_activity_catalog_evaluator_check" in migration and "'authentic-review'::text" in migration),
 ("rúbrica 5x2", all(x in migration for x in ["reproducible_result","supported_decision","rejected_alternative","ranking_interpretation","concrete_limit"])),
 ("campos de revisión versionados", all(x in migration for x in ["reviewed_by","reviewed_at","rubric"])),
 ("backend valida evidencia auténtica", 'catalog.evaluator==="authentic-review"' in backend and "precision_at_5" in backend and "defensible_results" in backend and "LAB9_STRUCTURED" in backend),
 ("envío no completa", 'verdict="pending_review"' in backend and (('completed=["correct","accepted"].includes(verdict)' in backend) or ('completed=verifiedNow&&!transferMode&&!requiresTransfer' in backend))),
 ("revisión docente explícita", "teacherReviewEvidence" in backend and "teacher_review_evidence" in backend),
 ("rúbrica backend 0-2", 'v<0||v>2' in backend and 'max:10' in backend),
 ("aceptación completa progreso", 'status:accepted?"completed":"in_progress"' in backend),
 ("rechazo no verifica evidencia", 'if(accepted)' in backend and 'event_type:"evidence_verified"' in backend),
 ("notebook llama registrar", any('lms.registrar("bd-s09-lab9"' in s for s in sources)),
 ("notebook envía decisión", any('"decision": decision' in s for s in sources)),
 ("notebook envía alternativa y límite", any('"rejected_alternative": alternativa_descartada' in s and '"limit": limite' in s for s in sources)),
 ("notebook envía rankings compactos", any('"top5_lexical": _ids(top_lex)' in s and '"top5_hybrid": _ids(top_hibrido)' in s for s in sources)),
 ("generador coincide con contrato estructurado", "FINAL_LMS_CODE" in generator and "bd-s09-lab9" in generator and all(x in generator for x in ["RAZONES =","DECISIONES =","ALTERNATIVAS =","LIMITES ="]) and "qué enfoque final eliges" not in generator),
 ("presentación no suplanta LAB9", "lab9EvidencePanel" in deck and "Evidencia auténtica · LAB 9" in deck),
 ("WALL revisa con rúbrica", "RUBRIC_FIELDS" in wall and "submitEvidenceReview" in wall and "Pedir ajuste" in wall),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("S09 authentic evidence FAIL: "+", ".join(failed))
print("S09 authentic evidence: OK")
