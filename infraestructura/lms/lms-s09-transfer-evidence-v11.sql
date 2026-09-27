-- S09 · transferencia auténtica V11 sin mezclar autocomprobación y evidencia.
-- LAB3/4/8 conservan su evaluator actual; una segunda evidencia breve y revisable
-- usa el mismo activity_code con step_id='transfer' y source='presentation-transfer'.

update public.bd_activity_catalog
set config = coalesce(config,'{}'::jsonb) || jsonb_build_object(
      'requires_transfer', true,
      'transfer_fields', jsonb_build_array(
        jsonb_build_object('id','result','label','Resultado que observaste'),
        jsonb_build_object('id','decision','label','Decisión que defenderías'),
        jsonb_build_object('id','rejected_alternative','label','Alternativa descartada'),
        jsonb_build_object('id','interpretation','label','Cómo interpretas el resultado'),
        jsonb_build_object('id','limit','label','Límite concreto')
      ),
      'transfer_requires_review', true
    ),
    version = greatest(version,3) + 1,
    updated_at = now()
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

update public.bd_lms_activities
set metadata = metadata || jsonb_build_object(
      'self_check_role','formative',
      'transfer_required',true,
      'transfer_rule','resultado + decisión + alternativa descartada + interpretación + límite'
    )
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

-- Preserva el logro anterior como autocomprobación, pero deja claro que la
-- transferencia revisada es la que completa estos tres LAB.
update public.bd_lms_activity_progress p
set status='in_progress',
    completed_at=null,
    updated_at=now(),
    metadata=coalesce(p.metadata,'{}'::jsonb) || jsonb_build_object(
      'self_check_verified',
      coalesce((p.metadata->>'evidence_verdict')='correct',false) or p.status='completed',
      'transfer_required',true,
      'completion_semantics','accepted_transfer'
    )
where p.activity_code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8')
  and not exists (
    select 1 from public.bd_evidence e
    where e.user_id=p.user_id
      and e.course_run_id=p.course_run_id
      and e.activity_code=p.activity_code
      and e.step_id='transfer'
      and e.verdict='accepted'
  );

-- La competencia global de recuperación se sustenta en más de una evidencia.
update public.lms_competencies_v2 c
set min_evidence_count=2,
    description='Compara mecanismos de recuperación, justifica decisiones con resultados propios y explicita alternativas descartadas y límites en evidencias revisadas.',
    updated_at=now()
from public.lms_course_runs r
where c.course_run_id=r.id and r.code='bigdata-2026-2' and c.code='BD-E7';

insert into public.lms_activity_competencies_v2(course_run_id,activity_code,competency_code,weight)
select r.id,x.activity_code,'BD-E7',1
from public.lms_course_runs r
cross join (values
  ('bd-s09-lab3'::text),
  ('bd-s09-lab4'::text),
  ('bd-s09-lab8'::text),
  ('bd-s09-lab9'::text)
) as x(activity_code)
where r.code='bigdata-2026-2'
on conflict(course_run_id,activity_code,competency_code)
do update set weight=excluded.weight;

comment on column public.bd_evidence.step_id is
  'submission = evidencia/autocomprobación normal; transfer = evidencia breve de transferencia revisable por docente.';
