from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
core=(ROOT/"infraestructura/lms/functions/bigdata-lms-core/index.ts").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-s09-competency-evidence-v10.sql").read_text(encoding="utf-8")
student=(ROOT/"lms/competencies.html").read_text(encoding="utf-8")
teacher=(ROOT/"lms/teacher-competencies.html").read_text(encoding="utf-8")
authentic=(ROOT/"infraestructura/lms/lms-s09-authentic-evidence-v9.sql").read_text(encoding="utf-8")
no_open=(ROOT/"infraestructura/lms/lms-s09-no-open-response-v15.sql").read_text(encoding="utf-8")

checks=[
 ("tabla mapeo V2", "lms_activity_competencies_v2" in migration),
 ("RLS mapeo V2", "enable row level security" in migration.lower() and "no_direct_access" in migration),
 ("competencia BD-E7", "'BD-E7'" in migration and "Recuperación de información" in migration),
 ("LAB9 mapea a BD-E7", "'bd-s09-lab9', 'BD-E7'" in migration),
 ("LAB3/4/8 no alimentan competencia por autocomprobación", "delete from public.lms_activity_competencies_v2" in no_open and all(x in no_open for x in ["bd-s09-lab3","bd-s09-lab4","bd-s09-lab8"])),
 ("BD-E7 requiere una evidencia auténtica", "min_evidence_count=1" in no_open and "BD-E7" in no_open),
 ("LAB9 sigue authentic-review", "where code='bd-s09-lab9'" in authentic and "evaluator='authentic-review'" in authentic),
 ("core carga mapeos de LAB", 'db.from("lms_activity_competencies_v2")' in core),
 ("solo evidencia aceptada", '.eq("verdict","accepted")' in core),
 ("rúbrica auténtica determina score", 'ev?.rubric?.total' in core and 'ev?.rubric?.max' in core),
 ("evidencia LAB identificada", 'source_type:"lab"' in core and 'source_title:activity?.title' in core),
 ("competencia alumno usa LAB", "computeCompetencyRows(context,subs||[],activityEvidence||[])" in core),
 ("competencia docente usa LAB", "evidenceByUser.get(u.id)||[]" in core),
 ("analítica usa LAB", "userActivityEvidence" in core and "context.activityEvidence" in core),
 ("UI estudiante renderiza fuente LAB", "function evidenceSource(e)" in student and "e.source_type==='lab'" in student),
 ("UI docente muestra mapeos LAB", "LAB auténticos mapeados" in teacher and "data.activity_mappings" in teacher),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("Competency evidence FAIL: "+", ".join(failed))
print("S09 authentic competency evidence: OK")
