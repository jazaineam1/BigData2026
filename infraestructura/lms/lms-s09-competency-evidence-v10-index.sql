-- S09 competencias · índice para FK compuesto y consultas por competencia
create index if not exists lms_activity_competencies_v2_run_comp_idx
  on public.lms_activity_competencies_v2(course_run_id, competency_code);
