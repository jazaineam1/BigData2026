-- Calendario Big Data 2026-2S · ajuste octubre
-- El jueves 1 de octubre corresponde al taller/evaluación integradora de S08.
-- S09 se desplaza al jueves siguiente, 8 de octubre.

update public.lms_run_sessions_v2
set summary='Taller evaluativo: histórico SECOP, Atlas, Cassandra, Neo4j e informe técnico.',
    starts_at='2026-10-01T23:00:00Z'::timestamptz,
    metadata=coalesce(metadata,'{}'::jsonb) || jsonb_build_object(
      'class_date','2026-10-01',
      'class_time_local','18:00',
      'class_timezone','America/Bogota',
      'class_kind','assessment_workshop'
    ),
    updated_at=now()
where course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and session_number=8;

update public.lms_run_sessions_v2
set starts_at='2026-10-08T23:00:00Z'::timestamptz,
    metadata=coalesce(metadata,'{}'::jsonb) || jsonb_build_object(
      'class_date','2026-10-08',
      'class_time_local','18:00',
      'class_timezone','America/Bogota',
      'class_kind','learning'
    ),
    updated_at=now()
where course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and session_number=9;
