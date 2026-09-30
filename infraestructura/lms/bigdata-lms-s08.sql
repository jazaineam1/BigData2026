-- Big Data LMS · vertical slice S08
-- Aplicado a Supabase gnpouhsvsisqoxketlfr el 2026-09-25.
-- Comparte identidad/sesión con el LMS existente, pero mantiene expediente
-- BigData course-scoped para no colisionar con las PK globales de ANDESDB.
-- S07 queda fuera de esta migración deliberadamente.

insert into public.lms_courses(code,title,description,status,position)
values ('bigdata','Big Data 2026-2S · Universidad Central',
'Maestría en Analítica de Datos. LMS especializado para seguimiento de actividades, laboratorios y evidencias del curso Big Data.',
'active',2)
on conflict(code) do update set title=excluded.title,description=excluded.description,status='active',position=excluded.position;

insert into public.lms_course_runs(course_code,code,title,timezone,active)
values ('bigdata','bigdata-2026-2','Big Data 2026-2S · Grupo 2','America/Bogota',true)
on conflict(code) do update set title=excluded.title,timezone=excluded.timezone,active=true,updated_at=now();

create table if not exists public.bd_lms_sessions(
 course_code text not null references public.lms_courses(code) on delete cascade,
 session_number smallint not null check(session_number between 1 and 16),
 title text not null,path text not null,position smallint not null,required boolean not null default true,
 metadata jsonb not null default '{}'::jsonb,created_at timestamptz not null default now(),
 primary key(course_code,session_number)
);
create table if not exists public.bd_lms_activities(
 code text primary key,course_code text not null,session_number smallint not null,title text not null,
 kind text not null default 'evidence',points numeric not null default 1 check(points>=0),position smallint not null,
 required boolean not null default true,metadata jsonb not null default '{}'::jsonb,created_at timestamptz not null default now(),
 foreign key(course_code,session_number) references public.bd_lms_sessions(course_code,session_number) on delete cascade
);
create table if not exists public.bd_lms_events(
 id bigint generated always as identity primary key,user_id uuid not null references public.lms_users(id) on delete cascade,
 course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
 event_type text not null check(event_type in ('page_opened','page_closed','heartbeat','notebook_opened','activity_started','stage_opened','manifest_submitted','ui_action')),
 session_number smallint check(session_number between 1 and 16),activity_code text references public.bd_lms_activities(code) on delete set null,
 active_seconds_delta integer not null default 0 check(active_seconds_delta between 0 and 300),
 metadata jsonb not null default '{}'::jsonb,client_at timestamptz,created_at timestamptz not null default now()
);
create index if not exists bd_lms_events_run_created_idx on public.bd_lms_events(course_run_id,created_at desc);
create index if not exists bd_lms_events_user_session_idx on public.bd_lms_events(user_id,course_run_id,session_number,created_at desc);

create table if not exists public.bd_lms_session_progress(
 user_id uuid not null references public.lms_users(id) on delete cascade,course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
 session_number smallint not null check(session_number between 1 and 16),
 status text not null default 'not_started' check(status in ('not_started','in_progress','submitted','completed')),
 started_at timestamptz,active_seconds integer not null default 0 check(active_seconds>=0),last_activity_at timestamptz,
 submitted_at timestamptz,completed_at timestamptz,score numeric not null default 0,max_score numeric not null default 0,
 updated_at timestamptz not null default now(),primary key(user_id,course_run_id,session_number)
);
create table if not exists public.bd_lms_activity_progress(
 user_id uuid not null references public.lms_users(id) on delete cascade,course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
 activity_code text not null references public.bd_lms_activities(code) on delete cascade,
 status text not null default 'not_started' check(status in ('not_started','in_progress','submitted','completed')),
 started_at timestamptz,attempts integer not null default 0 check(attempts>=0),score numeric not null default 0,max_score numeric not null default 0,
 completed_at timestamptz,updated_at timestamptz not null default now(),metadata jsonb not null default '{}'::jsonb,
 primary key(user_id,course_run_id,activity_code)
);
create table if not exists public.bd_lms_s08_submissions(
 id uuid primary key default gen_random_uuid(),user_id uuid not null references public.lms_users(id) on delete cascade,
 course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,pair_hash text not null check(pair_hash ~ '^[0-9a-f]{64}$'),
 manifest_version text not null,score integer not null check(score between 0 and 100),max_score integer not null default 100 check(max_score=100),
 note_5 numeric(3,2) not null check(note_5 between 1 and 5),sha256 text not null check(sha256 ~ '^[0-9a-f]{64}$'),
 controls jsonb not null default '{}'::jsonb,validated boolean not null default false,submitted_at timestamptz not null default now(),
 updated_at timestamptz not null default now(),unique(user_id,course_run_id)
);

create table if not exists public.bd_lms_session_windows(
 course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
 session_number smallint not null check(session_number between 1 and 16),
 opened_at timestamptz not null default now(),
 opened_by uuid not null references public.lms_users(id),
 created_at timestamptz not null default now(),
 primary key(course_run_id,session_number)
);

alter table public.bd_lms_sessions enable row level security;
alter table public.bd_lms_activities enable row level security;
alter table public.bd_lms_events enable row level security;
alter table public.bd_lms_session_progress enable row level security;
alter table public.bd_lms_activity_progress enable row level security;
alter table public.bd_lms_s08_submissions enable row level security;
alter table public.bd_lms_session_windows enable row level security;
revoke all on public.bd_lms_sessions,public.bd_lms_activities,public.bd_lms_events,public.bd_lms_session_progress,public.bd_lms_activity_progress,public.bd_lms_s08_submissions,public.bd_lms_session_windows from anon,authenticated;
grant all on public.bd_lms_sessions,public.bd_lms_activities,public.bd_lms_events,public.bd_lms_session_progress,public.bd_lms_activity_progress,public.bd_lms_s08_submissions,public.bd_lms_session_windows to service_role;
grant usage,select on sequence public.bd_lms_events_id_seq to service_role;

-- Índices detectados por el advisor para las FK usadas por el WALL.
create index if not exists bd_lms_activities_course_session_idx on public.bd_lms_activities(course_code,session_number);
create index if not exists bd_lms_activity_progress_run_idx on public.bd_lms_activity_progress(course_run_id);
create index if not exists bd_lms_activity_progress_activity_idx on public.bd_lms_activity_progress(activity_code);
create index if not exists bd_lms_events_activity_idx on public.bd_lms_events(activity_code);
create index if not exists bd_lms_s08_submissions_run_idx on public.bd_lms_s08_submissions(course_run_id);
create index if not exists bd_lms_session_progress_run_idx on public.bd_lms_session_progress(course_run_id);
create index if not exists bd_lms_session_windows_opened_by_idx on public.bd_lms_session_windows(opened_by);

insert into public.bd_lms_sessions(course_code,session_number,title,path,position,required,metadata)
values('bigdata',8,'SECOP Data Pipeline · API, concurrencia y NoSQL','lms/session-08.html',8,true,
'{"type":"evaluation","source":"Cuadernos/Taller_Control_1.ipynb","reference":"assets/tutoriales/s08-secoppipeline.html","max_score":100,"estimated_minutes":360,"work_mode":"class_and_home","group_assessment":true,"validator_version":"2026-09-30-secoppipeline-v5"}'::jsonb)
on conflict(course_code,session_number) do update set title=excluded.title,path=excluded.path,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata) values
('bd-s08-e1','bigdata',8,'E1 · API SECOP, concurrencia y trazabilidad','validator_stage',25,1,true,'{"checks":["E1_contrato_y_query","E1_descarga_secuencial","E1_concurrencia_equivalente","E1_trazabilidad_calidad"]}'),
('bd-s08-e2','bigdata',8,'E2 · Modelo documental + Atlas idempotente','validator_stage',25,2,true,'{"checks":["E2_modelo_documental","E2_atlas_idempotente","E2_indices","E2_consulta_A_count","E2_consulta_B_find","E2_evidencia_atlas"]}'),
('bd-s08-e3','bigdata',8,'E3 · Producto analítico desde Atlas','validator_stage',10,3,true,'{"checks":["E3_pipeline_bandeja","E3_artefacto_bandeja"]}'),
('bd-s08-e4','bigdata',8,'E4 · Cassandra query-first','validator_stage',15,4,true,'{"checks":["E4_datos_cassandra","E4_modelo_query_first","E4_consulta_simulada"]}'),
('bd-s08-e5','bigdata',8,'E5 · Neo4j y contexto relacional','validator_stage',15,5,true,'{"checks":["E5_historial_y_ancla","E5_metrica_relacional","E5_cypher","E5_subgrafo"]}'),
('bd-s08-e6','bigdata',8,'E6 · Decisiones, informe y paquete','validator_stage',10,6,true,'{"checks":["E6_decisiones_informe","E6_microdefensa_grupal","E6_paquete_reproducible"]}'),
('bd-s08-final','bigdata',8,'Validación final · manifest_tc1.json','manifest',100,7,true,'{"validator_versions":["2026-09-30-secoppipeline-v5"],"current":"2026-09-30-secoppipeline-v5"}')
on conflict(code) do update set title=excluded.title,kind=excluded.kind,points=excluded.points,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

-- El docente existente se matricula sin cambiar su identidad ni contraseña.
with r as(select id from public.lms_course_runs where code='bigdata-2026-2' and active limit 1),
t as(select id,role from public.lms_users where role in('teacher','admin') and active)
insert into public.lms_enrollments(user_id,course_code,role,status,enrolled_at)
select id,'bigdata',role,'active',now() from t
on conflict(user_id,course_code) do update set role=excluded.role,status='active';

with r as(select id from public.lms_course_runs where code='bigdata-2026-2' and active limit 1),
t as(select id,role from public.lms_users where role in('teacher','admin') and active)
insert into public.lms_run_enrollments(user_id,course_run_id,role,status,enrolled_at)
select t.id,r.id,t.role,'active',now() from t cross join r
on conflict(user_id,course_run_id) do update set role=excluded.role,status='active';
