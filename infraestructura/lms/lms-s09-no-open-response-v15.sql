-- S09 V15 · sin respuestas abiertas en el flujo estudiante
-- LAB3/4/8 vuelven a completarse con autocomprobación estructurada.
-- La competencia BD-E7 queda sustentada por LAB9 auténtico.

update public.bd_activity_catalog
set config = coalesce(config,'{}'::jsonb)
  - 'requires_transfer'
  - 'transfer_fields'
  - 'transfer_requires_review'
  - 'transfer_rule',
  updated_at = now()
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

update public.bd_lms_activities
set metadata = coalesce(metadata,'{}'::jsonb)
  - 'transfer_required'
  - 'transfer_rule'
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

update public.bd_lms_activity_progress
set status='completed',
    completed_at=coalesce(completed_at,updated_at,now()),
    metadata=(coalesce(metadata,'{}'::jsonb)
      - 'transfer_required'
      - 'transfer_pending'
      - 'transfer_verified')
      || jsonb_build_object('completion_semantics','structured_self_check')
where activity_code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8')
  and (
    coalesce((metadata->>'self_check_verified')::boolean,false)
    or metadata->>'evidence_verdict'='correct'
  );

delete from public.lms_activity_competencies_v2
where activity_code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

update public.lms_competencies_v2 c
set min_evidence_count=1,
    updated_at=now()
from public.lms_course_runs r
where c.course_run_id=r.id
  and r.code='bigdata-2026-2'
  and c.code='BD-E7';
