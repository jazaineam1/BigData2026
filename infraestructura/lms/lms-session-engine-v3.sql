-- Big Data LMS V3 · motor genérico de sesiones
-- Idempotente: crea claves server-side, declara S01–S07 en la capa de actividades
-- y asocia cada recurso visible con una actividad rastreable.

create table if not exists public.bd_lms_activity_keys (
  activity_code text primary key references public.bd_lms_activities(code) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  answer_hash text not null check (length(answer_hash)=64),
  hint text not null default '',
  updated_at timestamptz not null default now()
);

alter table public.bd_lms_activity_keys enable row level security;
revoke all on table public.bd_lms_activity_keys from anon, authenticated;
grant select, insert, update, delete on table public.bd_lms_activity_keys to service_role;

comment on table public.bd_lms_activity_keys is
'Claves server-side para checkpoints formativos del LMS Big Data; no exponer al navegador.';

insert into public.bd_lms_sessions(course_code,session_number,title,path,position,required,metadata)
select 'bigdata',s.session_number,s.title,
       coalesce(s.path,'session.html?s='||s.session_number::text),
       s.position,true,
       s.metadata || jsonb_build_object('source','lms_run_sessions_v2')
from public.lms_run_sessions_v2 s
where s.course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and s.session_number between 1 and 7
on conflict(course_code,session_number) do update
set title=excluded.title,path=excluded.path,position=excluded.position,required=excluded.required,
    metadata=public.bd_lms_sessions.metadata || excluded.metadata;

insert into public.bd_lms_activity_keys(activity_code,session_number,answer_hash,hint)
values
('bd-s09-c1',9,'527bbe6e343018a39e6e78ba0fc39e8c8d67d88e9dbe2ab7d52f6215501e9892','Piensa si la necesidad exige coincidencia exacta o puede tolerar paráfrasis.'),
('bd-s09-c2',9,'6e65ee7bd666203cba62114ae0e43eb002dfe01315969773ced9608543eab77f','El coseno describe cercanía geométrica; no es una probabilidad calibrada.'),
('bd-s09-c3',9,'701c258052172c1ffcdede204b508111671a980c9101b561ea8d88b021a255ba','Dos rankings se comparan contra juicios de relevancia, no por quién produce el número mayor.'),
('bd-s09-c4',9,'b31e961d21cdf1676df29fa87555cc14edbddfc3b2dcc2a8889dcec440e97956','Separa quién transforma texto en vector de quién lo almacena e indexa.'),
('bd-s09-c5',9,'e92de32e71f3f3ed64f76dca618fdaefc1bc78e9a349cd7c7731a9d224ef9929','RRF trabaja con posiciones de ranking para no asumir que BM25 y coseno comparten escala.')
on conflict(activity_code) do update set
  session_number=excluded.session_number,
  answer_hash=excluded.answer_hash,
  hint=excluded.hint,
  updated_at=now();

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata)
values
('bd-s01-r1','bigdata',1,'Cuaderno S01','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s02-r1','bigdata',2,'Cuaderno S02','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s03-r1','bigdata',3,'Cuaderno S03','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s04-r1','bigdata',4,'Cuaderno S04','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s04-r2','bigdata',4,'Guía Atlas','resource',0,2,false,'{"resource_type":"guide","completion_rule":"visit","formative":true}'::jsonb),
('bd-s05-r1','bigdata',5,'Cuaderno S05','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s05-r2','bigdata',5,'Guía Astra','resource',0,2,false,'{"resource_type":"guide","completion_rule":"visit","formative":true}'::jsonb),
('bd-s06-r1','bigdata',6,'Cuaderno S06','resource',0,1,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s06-r2','bigdata',6,'Guía Aura','resource',0,2,false,'{"resource_type":"guide","completion_rule":"visit","formative":true}'::jsonb),
('bd-s07-r1','bigdata',7,'Presentación S07','resource',0,1,true,'{"resource_type":"presentation","completion_rule":"visit","formative":true,"protected":true}'::jsonb),
('bd-s07-r2','bigdata',7,'Cuaderno S07','resource',0,2,true,'{"resource_type":"notebook","completion_rule":"visit","formative":true}'::jsonb),
('bd-s08-module','bigdata',8,'Taller de control S08','resource',0,0,true,'{"resource_type":"lab","completion_rule":"visit","formative":false}'::jsonb),
('bd-s08-notebook','bigdata',8,'Cuaderno S08','resource',0,8,false,'{"resource_type":"notebook","completion_rule":"visit","formative":false}'::jsonb),
('bd-s08-guide','bigdata',8,'Guía de entrega S08','resource',0,9,false,'{"resource_type":"guide","completion_rule":"visit","formative":false}'::jsonb)
on conflict(code) do update set
 title=excluded.title,kind=excluded.kind,points=excluded.points,position=excluded.position,
 required=excluded.required,metadata=public.bd_lms_activities.metadata || excluded.metadata;

update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"visit","resource_type":"presentation","formative":true}'::jsonb where code='bd-s09-presentation';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"visit","resource_type":"notebook","formative":true}'::jsonb where code='bd-s09-notebook';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"mastery","slide":9}'::jsonb where code='bd-s09-c1';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"mastery","slide":16}'::jsonb where code='bd-s09-c2';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"mastery","slide":18}'::jsonb where code='bd-s09-c3';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"mastery","slide":21}'::jsonb where code='bd-s09-c4';
update public.bd_lms_activities set metadata=metadata || '{"completion_rule":"mastery","slide":31}'::jsonb where code='bd-s09-c5';

update public.lms_run_resources_v2
set metadata=metadata || jsonb_build_object('tracked_activity',
case
 when session_number=1 and position=1 then 'bd-s01-r1'
 when session_number=2 and position=1 then 'bd-s02-r1'
 when session_number=3 and position=1 then 'bd-s03-r1'
 when session_number=4 and position=1 then 'bd-s04-r1'
 when session_number=4 and position=2 then 'bd-s04-r2'
 when session_number=5 and position=1 then 'bd-s05-r1'
 when session_number=5 and position=2 then 'bd-s05-r2'
 when session_number=6 and position=1 then 'bd-s06-r1'
 when session_number=6 and position=2 then 'bd-s06-r2'
 when session_number=7 and position=1 then 'bd-s07-r1'
 when session_number=7 and position=2 then 'bd-s07-r2'
 when session_number=8 and position=1 then 'bd-s08-module'
 when session_number=8 and position=2 then 'bd-s08-notebook'
 when session_number=8 and position=3 then 'bd-s08-guide'
 else metadata->>'tracked_activity'
end)
where session_number between 1 and 8;

update public.lms_run_sessions_v2
set metadata=metadata || case session_number
 when 1 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Distinguir las 5 V de Big Data","Leer fuentes estructuradas y semiestructuradas","Reconocer una API como fuente reproducible"]}'::jsonb
 when 2 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Traducir un problema de negocio a una decisión analítica","Relacionar proceso, caso de uso y arquitectura","Usar Git como trazabilidad del trabajo"]}'::jsonb
 when 3 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Modelar documentos cuando una fila no basta","Consultar con MQL","Construir agregaciones reproducibles"]}'::jsonb
 when 4 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Diferenciar modelo documental y wide-column","Diseñar desde la consulta","Conectar Atlas y Cassandra con una pregunta"]}'::jsonb
 when 5 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Transformar evidencia en una vista operacional","Diseñar patrones de acceso","Construir una tabla wide-column defendible"]}'::jsonb
 when 6 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Modelar relaciones como grafo","Ejecutar Cypher en Aura","Contrastar resultados de grafo con referencia tabular"]}'::jsonb
 when 7 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Explicar análisis de texto e índice invertido","Construir una búsqueda BM25","Evaluar un ranking con juicios de relevancia"]}'::jsonb
 when 8 then '{"module_kind":"assessment","estimated_minutes":360,"outcomes":["Construir un pipeline SECOP reproducible","Integrar evidencia multimodelo","Entregar un paquete técnico verificable"]}'::jsonb
 when 9 then '{"module_kind":"learning","estimated_minutes":180,"outcomes":["Diferenciar búsqueda lexical, semántica e híbrida","Interpretar embeddings y similitud coseno","Diseñar búsqueda vectorial y evaluar Top-k"]}'::jsonb
 else '{}'::jsonb end
where session_number between 1 and 9;
