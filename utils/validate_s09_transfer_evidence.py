from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
backend=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text(encoding="utf-8")
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")
wall=(ROOT/"lms/wall.html").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-s09-no-open-response-v15.sql").read_text(encoding="utf-8")

checks=[
 ("LAB3/4/8 conservan autocomprobación", all(x in deck for x in ["bd-s09-lab3","bd-s09-lab4","bd-s09-lab8"]) and "Autocomprobación" in deck),
 ("config de transferencia se retira", all(x in migration for x in ["'requires_transfer'","'transfer_fields'","'transfer_requires_review'","'transfer_rule'"])),
 ("progreso self-check se conserva", "self_check_verified" in migration and "structured_self_check" in migration),
 ("mapeos LAB3/4/8 se retiran de competencia", "delete from public.lms_activity_competencies_v2" in migration and all(x in migration for x in ["bd-s09-lab3","bd-s09-lab4","bd-s09-lab8"])),
 ("BD-E7 queda con evidencia auténtica mínima", "min_evidence_count=1" in migration and "BD-E7" in migration),
 ("backend sin transferencia textual", all(x not in backend for x in ["presentation-transfer","TRANSFER_REVIEW_CODES","transferMode","transfer_pending"])),
 ("deck sin transferencia textual", all(x not in deck for x in ["data-transfer-field","data-transfer-for","presentation-transfer","Transferencia breve"])),
 ("deck sin muro estudiante", "class-wall.html" not in deck and "Muro del LAB" not in deck),
 ("panel docente conserva evidencia revisable", "Rúbrica de evidencia · 10 puntos" in wall and "teacher_review_evidence" in backend),
 ("LAB9 sigue como única evidencia auténtica S09", 'catalog.evaluator==="authentic-review"' in backend and "bd-s09-lab9" in deck),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("S09 no-open-response FAIL: "+", ".join(failed))
print("S09 no-open-response: OK")
