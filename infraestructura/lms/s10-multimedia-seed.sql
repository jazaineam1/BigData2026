-- S10 · imágenes reales en VS Code. Metadatos verificados contra documentación
-- vigente de Postgres/Supabase el 2026-10-28. Sin cambios de esquema ni permisos.
-- Idempotente: conserva actividades/evidencias previas. Acceso no acredita dominio.
begin;
insert into public.bd_lms_sessions(course_code,session_number,title,path,position,required,metadata)
values ('bigdata',10,'¿Cómo convertir imágenes reales en un catálogo reutilizable?','session.html?s=10',10,true,'{"type": "learning", "topic": "image-etl", "estimated_minutes": 120, "graded": false, "canonical_module": true, "visible_resources": 2, "class_date": "2026-10-15", "class_kind": "learning", "class_timezone": "America/Bogota", "class_time_local": "18:00", "completion_basis": "resource_visits", "outcomes": ["Implementar E, T y L de imágenes reales en VS Code", "Conservar RAW y procedencia por noticia", "Transformar por lotes, continuar pendientes y comparar perfiles", "Releer y verificar un catálogo JSONL/Parquet portable"]}'::jsonb)
on conflict(course_code,session_number) do update set title=excluded.title,metadata=excluded.metadata;

-- Retirar requisitos anteriores sin borrar progreso, notas ni evidencia histórica.
update public.bd_lms_activities set required=false,
 metadata=metadata || '{"archived":true,"blocks_session_completion":false,"retired_reason":"S10 se concentra en imágenes; audio/video corresponden a continuidad"}'::jsonb
where course_code='bigdata' and session_number=10 and kind in ('checkpoint','lab');

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata)
values ('bd-s10-presentation','bigdata',10,'Presentación S10 · ETL de imágenes','resource',0,1,true,'{"resource_type": "presentation", "formative": true, "completion_rule": "visit", "completion_basis": "resource_visits", "archived": false}'::jsonb)
on conflict(code) do update set title=excluded.title,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata)
values ('bd-s10-project','bigdata',10,'Proyecto S10 · VS Code','resource',0,3,false,'{"resource_type": "link", "formative": true, "completion_rule": "visit", "completion_basis": "resource_visits", "archived": true}'::jsonb)
on conflict(code) do update set title=excluded.title,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata)
values ('bd-s10-notebook','bigdata',10,'Cuaderno S10 · Python completo','resource',0,2,true,'{"resource_type": "notebook", "formative": true, "completion_rule": "visit", "completion_basis": "resource_visits", "archived": false}'::jsonb)
on conflict(code) do update set title=excluded.title,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.lms_run_sessions_v2(course_run_id,session_number,title,summary,status,path,starts_at,position,metadata,published_at,updated_at)
select id,10,'¿Cómo convertir imágenes reales en un catálogo reutilizable?','E → T → L de imágenes reales: implementación en VS Code, lotes y catálogo portable. Práctica formativa; visitas no acreditan el laboratorio.',
'visible','session.html?s=10','2026-10-15 23:00:00+00',10,'{"type": "learning", "topic": "image-etl", "estimated_minutes": 120, "graded": false, "canonical_module": true, "visible_resources": 2, "class_date": "2026-10-15", "class_kind": "learning", "class_timezone": "America/Bogota", "class_time_local": "18:00", "completion_basis": "resource_visits", "outcomes": ["Implementar E, T y L de imágenes reales en VS Code", "Conservar RAW y procedencia por noticia", "Transformar por lotes, continuar pendientes y comparar perfiles", "Releer y verificar un catálogo JSONL/Parquet portable"]}'::jsonb,now(),now()
from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata'
on conflict(course_run_id,session_number) do update set title=excluded.title,summary=excluded.summary,metadata=excluded.metadata,updated_at=now();

-- Ocultar recursos sustituidos; conservar IDs para no romper referencias históricas.
update public.lms_run_resources_v2 set visible=false,updated_at=now()
where session_number=10 and course_run_id in (select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata');

update public.lms_run_resources_v2 set resource_type='presentation',title='Presentación S10 · ETL de imágenes',summary='Conceptos y código visible E → T → L.',url='../Presentaciones/s10-etl-multimedia.html#s1',position=1,visible=true,metadata='{"tracked_activity": "bd-s10-presentation", "required": true, "completion_basis": "resource_visits"}'::jsonb,updated_at=now()
where session_number=10 and metadata->>'tracked_activity'='bd-s10-presentation' and course_run_id in
(select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata');
insert into public.lms_run_resources_v2(course_run_id,session_number,resource_type,title,summary,url,position,visible,metadata)
select r.id,10,'presentation','Presentación S10 · ETL de imágenes','Conceptos y código visible E → T → L.','../Presentaciones/s10-etl-multimedia.html#s1',1,true,'{"tracked_activity": "bd-s10-presentation", "required": true, "completion_basis": "resource_visits"}'::jsonb
from public.lms_course_runs r where r.code='bigdata-2026-2' and r.course_code='bigdata'
and not exists (select 1 from public.lms_run_resources_v2 x where x.course_run_id=r.id and x.session_number=10 and x.metadata->>'tracked_activity'='bd-s10-presentation');

update public.lms_run_resources_v2 set resource_type='notebook',title='Cuaderno S10 · Python completo',summary='ETL completa y visible; el mismo cuaderno abre en VS Code y Colab.',url='https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb',position=2,visible=true,metadata='{"tracked_activity": "bd-s10-notebook", "required": true, "completion_basis": "resource_visits"}'::jsonb,updated_at=now()
where session_number=10 and metadata->>'tracked_activity'='bd-s10-notebook' and course_run_id in
(select id from public.lms_course_runs where code='bigdata-2026-2' and course_code='bigdata');
insert into public.lms_run_resources_v2(course_run_id,session_number,resource_type,title,summary,url,position,visible,metadata)
select r.id,10,'notebook','Cuaderno S10 · Python completo','ETL completa y visible; el mismo cuaderno abre en VS Code y Colab.','https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb',2,true,'{"tracked_activity": "bd-s10-notebook", "required": true, "completion_basis": "resource_visits"}'::jsonb
from public.lms_course_runs r where r.code='bigdata-2026-2' and r.course_code='bigdata'
and not exists (select 1 from public.lms_run_resources_v2 x where x.course_run_id=r.id and x.session_number=10 and x.metadata->>'tracked_activity'='bd-s10-notebook');

commit;
