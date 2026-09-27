from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
backend=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text(encoding="utf-8")
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")
wall=(ROOT/"lms/class-wall.html").read_text(encoding="utf-8")
progress=(ROOT/"lms/progress.html").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-s09-no-open-responses-v52.sql").read_text(encoding="utf-8")

checks=[
 ("V52 retira transferencia obligatoria", all(x in migration for x in ["- 'requires_transfer'","- 'transfer_fields'","- 'transfer_requires_review'"])),
 ("V52 conserva historial", "delete from public.bd_evidence" not in migration.lower() and "delete from public.bd_lms_activity_progress" not in migration.lower()),
 ("V52 reconoce self-check previo", "self_check_verified" in migration and "objective_self_check" in migration),
 ("deck conserva autocomprobación objetiva", "Autocomprobación" in deck and "box.dataset.evidenceKind='self-check'" in deck and "step.type==='choice'" in deck and "step.type==='number'" in deck),
 ("deck elimina transferencia abierta", all(x not in deck for x in ["Transferencia breve","data-transfer-field","presentation-transfer","Escribe una evidencia concreta","TRANSFER_CODES"])),
 ("deck elimina enlaces a muro estudiante", "class-wall.html" not in deck),
 ("progreso elimina enlaces a muro estudiante", "class-wall.html" not in progress),
 ("muro sin formulario abierto", all(x not in wall for x in ["Publica para ver","Tu respuesta",'<textarea id="body"',"K.wallPost("])),
 ("muro solo docente", "if(!teacher){location.replace('session.html?s='+sessionNumber)" in wall),
 ("backend mantiene compatibilidad histórica", 'source==="presentation-transfer"' in backend and "TRANSFER_REVIEW_CODES" in backend),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
if failed:
    raise SystemExit("S09 no-open-response FAIL: "+", ".join(failed))
print("S09 sin respuestas abiertas: OK")
