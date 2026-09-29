-- S10 · ETL multimodal: imágenes, audio y video
-- Publicación LMS idempotente. Dos recursos visibles: presentación + cuaderno.
-- La evidencia académica se produce en el cuaderno; no se habilitan respuestas abiertas.

insert into public.bd_lms_sessions
(course_code,session_number,title,path,position,required,metadata)
values (
  'bigdata',10,
  'ETL multimodal: de imágenes, audio y video a datos trazables',
  'session.html?s=10',10,true,
  '{
    "type":"learning",
    "topic":"multimodal-etl",
    "estimated_minutes":180,
    "graded":false,
    "canonical_module":true,
    "visible_resources":2,
    "class_date":"2026-10-15",
    "class_kind":"learning",
    "class_timezone":"America/Bogota",
    "class_time_local":"18:00",
    "outcomes":[
      "Distinguir RAW, metadata, derived asset y manifest",
      "Inspeccionar imagen, audio y video antes de transformarlos",
      "Aplicar SHA-256, canonicalización y sampling con reglas reproducibles",
      "Construir JSONL, Parquet y un manifest con provenance y quality gates"
    ]
  }'::jsonb
)
on conflict (course_code,session_number) do update set
  title=excluded.title,
  path=excluded.path,
  position=excluded.position,
  required=excluded.required,
  metadata=excluded.metadata;

insert into public.bd_lms_activities
(code,course_code,session_number,title,kind,points,position,required,metadata)
values
(
  'bd-s10-presentation','bigdata',10,
  'Recurso · Presentación + laboratorio S10',
  'resource',0,1,true,
  '{"resource_type":"presentation","formative":true,"completion_rule":"visit"}'::jsonb
),
(
  'bd-s10-notebook','bigdata',10,
  'Recurso · Cuaderno Colab S10',
  'resource',0,2,true,
  '{"resource_type":"notebook","formative":true,"completion_rule":"visit"}'::jsonb
)
on conflict (code) do update set
  course_code=excluded.course_code,
  session_number=excluded.session_number,
  title=excluded.title,
  kind=excluded.kind,
  points=excluded.points,
  position=excluded.position,
  required=excluded.required,
  metadata=excluded.metadata;

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
insert into public.lms_run_sessions_v2
(course_run_id,session_number,title,summary,status,path,starts_at,position,metadata,published_at,updated_at)
select
  id,10,
  'ETL multimodal: de imágenes, audio y video a datos trazables',
  'Pipeline reproducible sobre el caso El Tiempo: RAW, identidad, metadata, imágenes, audio, video, derivados, manifest y quality gates.',
  'visible',
  'session.html?s=10',
  '2026-10-15 23:00:00+00',
  10,
  '{
    "module_kind":"learning",
    "graded":false,
    "tracked":true,
    "class_date":"2026-10-15",
    "class_kind":"learning",
    "class_timezone":"America/Bogota",
    "class_time_local":"18:00",
    "estimated_minutes":180,
    "outcomes":[
      "Distinguir RAW, metadata, derived asset y manifest",
      "Inspeccionar imagen, audio y video antes de transformarlos",
      "Aplicar SHA-256, canonicalización y sampling con reglas reproducibles",
      "Construir JSONL, Parquet y un manifest con provenance y quality gates"
    ]
  }'::jsonb,
  now(),now()
from run
on conflict (course_run_id,session_number) do update set
  title=excluded.title,
  summary=excluded.summary,
  status=excluded.status,
  path=excluded.path,
  starts_at=excluded.starts_at,
  position=excluded.position,
  metadata=excluded.metadata,
  published_at=coalesce(public.lms_run_sessions_v2.published_at,now()),
  updated_at=now();

delete from public.lms_run_resources_v2
where course_run_id=(
  select id from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
and session_number=10;

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
insert into public.lms_run_resources_v2
(course_run_id,session_number,resource_type,title,summary,url,position,visible,metadata)
select
  id,10,'presentation',
  'Presentación S10 · ETL multimedia + laboratorio',
  'Definiciones, gráficos, inspector interactivo y laboratorios encadenados de imagen, audio y video.',
  '../Presentaciones/s10-etl-multimedia.html#s1',
  1,true,
  '{"tracked_activity":"bd-s10-presentation"}'::jsonb
from run
union all
select
  id,10,'notebook',
  'Cuaderno S10 · ETL multimedia',
  'Colab reproducible sobre El Tiempo con RAW, SHA-256, ffprobe/FFmpeg, Pillow, derivados, JSONL, Parquet y manifest.',
  'https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb',
  2,true,
  '{"tracked_activity":"bd-s10-notebook"}'::jsonb
from run;
