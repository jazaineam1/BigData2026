from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
backend=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text(encoding="utf-8")
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")
wall=(ROOT/"lms/wall.html").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-s09-transfer-evidence-v11.sql").read_text(encoding="utf-8")
competency=(ROOT/"infraestructura/lms/lms-s09-competency-evidence-v10.sql").read_text(encoding="utf-8")

checks=[
 ("LAB3/4/8 conservan autocomprobación", "set evaluator=" not in migration.lower() and all(x in migration for x in ["bd-s09-lab3","bd-s09-lab4","bd-s09-lab8"])),
 ("config exige transferencia", "'requires_transfer', true" in migration and "transfer_requires_review" in migration),
 ("progreso previo se conserva como self-check", "self_check_verified" in migration and "completion_semantics" in migration and "accepted_transfer" in migration),
 ("sesión se reconcilia", "update public.bd_lms_session_progress" in migration and "p.activity_code='bd-s09-lab3'" in migration and "completed_at=null" in migration),
 ("transferencia no borra historial", "delete from public.bd_lms_activity_progress" not in migration.lower()),
 ("backend separa transfer", 'source==="presentation-transfer"' in backend and "TRANSFER_REVIEW_CODES" in backend),
 ("transfer usa step_id propio", 'step_id:transferMode?"transfer":"submission"' in backend),
 ("transfer requiere self-check", "Completa primero la autocomprobación del LAB" in backend),
 ("self-check no completa LAB con transferencia", "requiresTransfer" in backend and "completed=verifiedNow&&!transferMode&&!requiresTransfer" in backend),
 ("transfer queda pendiente de revisión", 'verdict="pending_review"' in backend and "Transferencia recibida" in backend),
 ("revisión docente acepta transfer", 'evidence.step_id==="transfer"' in backend and "transferEvidence" in backend),
 ("deck mantiene autocomprobación", "Autocomprobación" in deck and "box.dataset.evidenceKind='self-check'" in deck),
 ("deck transferencia plegable", "Transferencia breve" in deck and "data-transfer-for" in deck and "document.createElement('details')" in deck),
 ("deck usa cola offline existente", "K.evidence(code,payload,{source:'presentation-transfer'})" in deck),
 ("deck cinco dimensiones", all(x in deck for x in ["Resultado que observaste","Decisión que defenderías","Alternativa descartada y por qué","Cómo interpretas el resultado","Límite concreto de tu conclusión"])),
 ("WALL rúbrica genérica", "Rúbrica de evidencia · 10 puntos" in wall and "Interpretación del resultado / ranking" in wall),
 ("competencia usa múltiples evidencias", "min_evidence_count=2" in migration),
 ("mapeos LAB3/4/8/9", all(x in migration for x in ["'bd-s09-lab3'","'bd-s09-lab4'","'bd-s09-lab8'","'bd-s09-lab9'"])),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("S09 transfer evidence FAIL: "+", ".join(failed))
print("S09 transfer evidence: OK")
