-- S09 · búsqueda semántica y bases vectoriales
-- Datos de configuración LMS. No altera S07 ni S08.

insert into public.bd_lms_sessions
(course_code,session_number,title,path,position,required,metadata)
values (
  'bigdata',9,
  'Cuando las palabras no coinciden · búsqueda semántica y bases vectoriales',
  'lms/session-09.html',9,true,
  '{"type":"formative","topic":"semantic-search-vector-databases","estimated_minutes":180,"graded":false,"wall":true,"pda_product":"Ejercicio en Colab de búsquedas semánticas"}'::jsonb
)
on conflict (course_code,session_number) do update set
  title=excluded.title,path=excluded.path,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.bd_lms_activities
(code,course_code,session_number,title,kind,points,position,required,metadata)
values
('bd-s09-presentation','bigdata',9,'Recurso · Presentación S09','resource',0,1,true,'{"resource_type":"presentation","formative":true}'::jsonb),
('bd-s09-notebook','bigdata',9,'Recurso · Cuaderno Colab S09','resource',0,2,true,'{"resource_type":"notebook","formative":true}'::jsonb),
('bd-s09-guide','bigdata',9,'Recurso · Guía de apoyo S09','resource',0,3,false,'{"resource_type":"guide","formative":true}'::jsonb),
('bd-s09-c1','bigdata',9,'C1 · Diferenciar lexical, semántica e híbrida','checkpoint',1,4,true,'{"formative":true,"evidence":"Explica qué recupera BM25 y qué recupera un embedding"}'::jsonb),
('bd-s09-c2','bigdata',9,'C2 · Embeddings y similitud coseno','checkpoint',1,5,true,'{"formative":true,"evidence":"Interpreta vector, dimensión y coseno sin llamarlo probabilidad"}'::jsonb),
('bd-s09-c3','bigdata',9,'C3 · Comparar Top-5 lexical vs semántico','checkpoint',1,6,true,'{"formative":true,"evidence":"Compara rankings sobre la misma consulta"}'::jsonb),
('bd-s09-c4','bigdata',9,'C4 · Persistir e indexar vectores','checkpoint',1,7,true,'{"formative":true,"evidence":"Distingue modelo de embeddings, base vectorial e índice ANN/ENN"}'::jsonb),
('bd-s09-c5','bigdata',9,'C5 · Defender resultados y límites','checkpoint',1,8,true,'{"formative":true,"evidence":"Dos resultados defendibles, un falso positivo, alternativa y límite"}'::jsonb)
on conflict (code) do update set
  course_code=excluded.course_code,session_number=excluded.session_number,title=excluded.title,
  kind=excluded.kind,points=excluded.points,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

with run as (
  select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata' limit 1
)
insert into public.lms_run_sessions_v2
(course_run_id,session_number,title,summary,status,path,starts_at,position,metadata,published_at,updated_at)
select id,9,
  'Cuando las palabras no coinciden: búsqueda semántica y bases vectoriales',
  'Presentación-laboratorio con definiciones, herramientas interactivas, comparación BM25 vs semantic search, índices vectoriales y MongoDB Atlas Vector Search.',
  'visible','session-09.html','2026-10-01 23:00:00+00',9,
  '{"pda":"Introducción a bases de datos vectoriales","product":"Ejercicio en Colab de búsquedas semánticas","graded":false,"tracked":true}'::jsonb,
  now(),now()
from run
on conflict (course_run_id,session_number) do update set
  title=excluded.title,summary=excluded.summary,status=excluded.status,path=excluded.path,
  starts_at=excluded.starts_at,position=excluded.position,metadata=excluded.metadata,
  published_at=coalesce(public.lms_run_sessions_v2.published_at,now()),updated_at=now();

delete from public.lms_run_resources_v2
where course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata' limit 1)
  and session_number=9;

with run as (
  select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata' limit 1
)
insert into public.lms_run_resources_v2
(course_run_id,session_number,resource_type,title,summary,url,position,visible,metadata)
select id,9,'presentation','Presentación S09 · laboratorio integrado',
  'Recurso principal: definiciones, ejemplos, herramientas interactivas y laboratorio al estilo S07.',
  '../Presentaciones/s09-de-palabras-a-significado.html#s1',1,true,
  '{"tracked_activity":"bd-s09-presentation"}'::jsonb from run
union all
select id,9,'notebook','Cuaderno S09 · búsqueda semántica',
  'Colab para ejecutar BM25 local, embeddings E5, búsqueda exacta, Atlas Vector Search y evidencia reproducible.',
  'https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb',2,true,
  '{"tracked_activity":"bd-s09-notebook"}'::jsonb from run
union all
select id,9,'guide','Guía de apoyo S09',
  'Respaldo de conceptos y checklist; no sustituye el laboratorio principal de la presentación.',
  '../assets/tutoriales/s09-laboratorio-guiado.html',3,true,
  '{"tracked_activity":"bd-s09-guide"}'::jsonb from run;
