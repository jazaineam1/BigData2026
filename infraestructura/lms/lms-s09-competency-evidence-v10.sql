-- S09 · evidencia auténtica como fuente de competencias V2
-- Solo evidencia revisada/aceptada puede alimentar competencias.

create table if not exists public.lms_activity_competencies_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  activity_code text not null,
  competency_code text not null,
  weight numeric not null default 1 check (weight > 0),
  primary key (course_run_id, activity_code, competency_code),
  foreign key (course_run_id, competency_code)
    references public.lms_competencies_v2(course_run_id, code)
    on delete cascade
);

alter table public.lms_activity_competencies_v2 enable row level security;
revoke all on table public.lms_activity_competencies_v2 from anon, authenticated;

comment on table public.lms_activity_competencies_v2 is
  'Mapeo explícito entre evidencias auténticas de actividades LMS y competencias V2. La lectura/escritura ocurre solo desde Edge Functions con control de rol.';

insert into public.lms_competencies_v2 (
  course_run_id, code, domain, title, description, position,
  mastery_threshold, min_evidence_count, active, updated_at
)
select
  id,
  'BD-E7',
  'Recuperación de información',
  'Diseña y evalúa recuperación lexical, vectorial e híbrida',
  'Compara mecanismos de recuperación, justifica una decisión con resultados reproducibles y explicita una alternativa descartada y un límite.',
  70,
  80,
  1,
  true,
  now()
from public.lms_course_runs
where code='bigdata-2026-2'
on conflict (course_run_id, code) do update
set domain=excluded.domain,
    title=excluded.title,
    description=excluded.description,
    position=excluded.position,
    mastery_threshold=excluded.mastery_threshold,
    min_evidence_count=excluded.min_evidence_count,
    active=true,
    updated_at=now();

insert into public.lms_activity_competencies_v2 (
  course_run_id, activity_code, competency_code, weight
)
select id, 'bd-s09-lab9', 'BD-E7', 1
from public.lms_course_runs
where code='bigdata-2026-2'
on conflict (course_run_id, activity_code, competency_code)
do update set weight=excluded.weight;
