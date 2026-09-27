-- Calendario Big Data 2026-2S · ajuste de sesiones S08/S09
-- Jueves 1 de octubre: Taller S08
-- Jueves 8 de octubre: S09 búsqueda semántica y bases vectoriales

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
update public.lms_run_sessions_v2 s
set title='SECOP Data Pipeline · API, concurrencia y NoSQL',
    summary='Taller evaluativo grupal: adquisición SECOP, concurrencia, Atlas, Cassandra, Neo4j y evidencia reproducible.',
    starts_at='2026-10-01 23:00:00+00',
    updated_at=now()
from run
where s.course_run_id=run.id
  and s.session_number=8;

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
update public.lms_run_sessions_v2 s
set starts_at='2026-10-08 23:00:00+00',
    updated_at=now()
from run
where s.course_run_id=run.id
  and s.session_number=9;
