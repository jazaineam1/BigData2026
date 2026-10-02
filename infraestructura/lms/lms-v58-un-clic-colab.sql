-- LMS V58 · un clic de la sesión al material
-- El taller S08 se abría en tres saltos: session.html?s=8 -> session-08.html -> Colab.
-- session.html ya salta la página intermedia usando el cuaderno Colab de la sesión;
-- esto deja el destino declarado en los datos para no depender de esa deducción.
-- Idempotente: se puede ejecutar más de una vez.

update public.lms_run_resources_v2
set metadata = coalesce(metadata,'{}'::jsonb)
  || '{"direct_url":"https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/Taller_Control_1.ipynb"}'::jsonb
where course_run_id = (select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and session_number = 8
  and metadata->>'tracked_activity' = 'bd-s08-module';

-- Comprobación: debe devolver una fila con direct_url apuntando a Colab.
select session_number, title, url, metadata->>'direct_url' as direct_url
from public.lms_run_resources_v2
where course_run_id = (select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and session_number = 8
order by position;
