-- Big Data LMS V4 · evidencia de laboratorio y tracking consistente
-- 26-sep-2026
-- Idempotente. Amplía eventos, crea catálogo/evidencias/códigos y declara los 12 LAB S09.

do $$
declare c record;
begin
  for c in
    select conname
    from pg_constraint
    where conrelid='public.bd_lms_events'::regclass
      and contype='c'
      and pg_get_constraintdef(oid) ilike '%event_type%'
  loop
    execute format('alter table public.bd_lms_events drop constraint %I',c.conname);
  end loop;
end $$;

alter table public.bd_lms_events
  add constraint bd_lms_events_event_type_check
  check (event_type = any (array[
    'page_opened','page_closed','heartbeat','notebook_opened','activity_started','stage_opened','manifest_submitted','ui_action',
    'session_entered','resource_opened','resource_completed','presentation_opened','guide_opened','lab_started','checkpoint_started',
    'slide_viewed','challenge_answered','lab_interaction','evidence_submitted','evidence_verified','lab_code_issued','session_completed'
  ]::text[]));

create table if not exists public.bd_activity_catalog(
  code text primary key references public.bd_lms_activities(code) on delete cascade,
  evaluator text not null check (evaluator in ('choice-hash','seeded-numeric','rubric','self-report','url-trace','none')),
  steps jsonb not null default '[]'::jsonb,
  config jsonb not null default '{}'::jsonb,
  competency_code text,
  seeded boolean not null default false,
  wall_prompt text,
  version integer not null default 1,
  updated_at timestamptz not null default now()
);

create table if not exists public.bd_evidence(
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.lms_users(id) on delete cascade,
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  activity_code text not null references public.bd_lms_activities(code) on delete cascade,
  step_id text not null default 'submission',
  payload jsonb not null check (pg_column_size(payload) <= 8192),
  seed text,
  source text not null check (source in ('presentation','notebook','module','lab-page')),
  verdict text not null check (verdict in ('correct','incorrect','accepted','pending_review','rejected')),
  feedback text,
  catalog_version integer not null,
  created_at timestamptz not null default now()
);
create index if not exists bd_evidence_run_activity_created_idx on public.bd_evidence(course_run_id,activity_code,created_at desc);
create index if not exists bd_evidence_user_run_created_idx on public.bd_evidence(user_id,course_run_id,created_at desc);

create table if not exists public.bd_lab_codes(
  code_hash text primary key check (code_hash ~ '^[0-9a-f]{64}$'),
  user_id uuid not null references public.lms_users(id) on delete cascade,
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  scope text[] not null default array['evidence'],
  uses integer not null default 0,
  max_uses integer not null default 200 check (max_uses between 1 and 1000),
  expires_at timestamptz not null,
  revoked_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists bd_lab_codes_user_session_idx on public.bd_lab_codes(user_id,course_run_id,session_number,created_at desc);

alter table public.bd_activity_catalog enable row level security;
alter table public.bd_evidence enable row level security;
alter table public.bd_lab_codes enable row level security;
revoke all on public.bd_activity_catalog,public.bd_evidence,public.bd_lab_codes from anon,authenticated;
grant select,insert,update,delete on public.bd_activity_catalog,public.bd_evidence,public.bd_lab_codes to service_role;

insert into public.bd_lms_activities(code,course_code,session_number,title,kind,points,position,required,metadata)
values
('bd-s09-lab1','bigdata',9,'LAB 1 · Recuperación lexical','lab',0,10,false,'{"slide":6,"formative":true,"completion_rule":"evidence","evidence":"Explora coincidencia lexical y explica cuándo la forma exacta importa."}'),
('bd-s09-lab-e5','bigdata',9,'LAB E5 · Texto a embedding','lab',0,11,false,'{"slide":12,"formative":true,"completion_rule":"evidence","evidence":"Distingue modelo de embeddings, vector y almacenamiento."}'),
('bd-s09-lab-chunk','bigdata',9,'LAB · Chunking','lab',0,12,false,'{"slide":14,"formative":true,"completion_rule":"evidence","evidence":"Relaciona tamaño, overlap y número de fragmentos con trazabilidad."}'),
('bd-s09-lab2','bigdata',9,'LAB 2 · Similitud coseno','lab',0,13,false,'{"slide":16,"formative":true,"completion_rule":"evidence","evidence":"Calcula e interpreta coseno sin tratarlo como probabilidad."}'),
('bd-s09-lab3','bigdata',9,'LAB 3 · Vecinos y Top-k','lab',0,14,true,'{"slide":17,"formative":true,"completion_rule":"evidence","evidence":"Resultado propio + decisión sobre k + alternativa descartada + límite."}'),
('bd-s09-lab4','bigdata',9,'LAB 4 · BM25 vs semántica','lab',0,15,false,'{"slide":18,"formative":true,"completion_rule":"evidence","evidence":"Compara rankings usando juicios de relevancia."}'),
('bd-s09-lab5','bigdata',9,'LAB 5 · HNSW','lab',0,16,false,'{"slide":24,"formative":true,"completion_rule":"evidence","evidence":"Explica navegación aproximada y su límite."}'),
('bd-s09-lab6','bigdata',9,'LAB 6 · numCandidates','lab',0,17,false,'{"slide":26,"formative":true,"completion_rule":"evidence","evidence":"Decide exploración vs costo/latencia."}'),
('bd-s09-lab7','bigdata',9,'LAB 7 · Constructor $vectorSearch','lab',0,18,false,'{"slide":29,"formative":true,"completion_rule":"evidence","evidence":"Construye y explica una consulta vectorial."}'),
('bd-s09-lab8','bigdata',9,'LAB 8 · RRF','lab',0,19,false,'{"slide":31,"formative":true,"completion_rule":"evidence","evidence":"Fusiona posiciones sin sumar scores incompatibles."}'),
('bd-s09-lab-eval','bigdata',9,'LAB · Precision@k','lab',0,20,false,'{"slide":32,"formative":true,"completion_rule":"evidence","evidence":"Calcula Precision@k a partir de juicios de relevancia."}'),
('bd-s09-lab9','bigdata',9,'LAB 9 · Evidencia final','lab',0,21,false,'{"slide":33,"formative":true,"completion_rule":"evidence","evidence":"Dos resultados defendibles, falso positivo, alternativa y límite."}')
on conflict(code) do update set
  title=excluded.title,kind=excluded.kind,points=excluded.points,position=excluded.position,required=excluded.required,
  metadata=public.bd_lms_activities.metadata||excluded.metadata;

insert into public.bd_activity_catalog(code,evaluator,steps,config,competency_code,seeded,wall_prompt,version,updated_at)
values
('bd-s09-lab1','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C1-mecanismos-recuperacion',false,'¿Cuándo preferirías una señal lexical y cuál sería su límite?',1,now()),
('bd-s09-lab-e5','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C2-embeddings',false,'¿Qué produce el modelo y qué responsabilidad queda fuera de él?',1,now()),
('bd-s09-lab-chunk','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C2-embeddings',false,'¿Qué compromiso encontraste entre tamaño de chunk, overlap y trazabilidad?',1,now()),
('bd-s09-lab2','self-report','[{"id":"result","type":"number"},{"id":"interpretation","type":"text","min_chars":25}]','{}','C2-embeddings',false,'Interpreta tu coseno sin convertirlo en probabilidad.',1,now()),
('bd-s09-lab3','seeded-numeric','[{"id":"result","type":"number"},{"id":"decision","type":"choice","options":["mantener","subir"]},{"id":"alternative","type":"text","min_chars":10},{"id":"limit","type":"text","min_chars":40}]','{"generator":"s09_topk_aero_count","k":5,"tolerance":0}','C3-recuperacion-vectorial',true,'Tu decisión sobre k, la alternativa descartada y el límite encontrado.',1,now()),
('bd-s09-lab4','self-report','[{"id":"decision","type":"text","min_chars":25},{"id":"limit","type":"text","min_chars":40}]','{}','C3-recuperacion-vectorial',false,'¿Qué ranking defenderías y qué falso positivo viste?',1,now()),
('bd-s09-lab5','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C4-arquitectura-vectorial',false,'¿Qué gana HNSW y qué puede sacrificar?',1,now()),
('bd-s09-lab6','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C4-arquitectura-vectorial',false,'¿Qué numCandidates elegirías y qué costo aceptas?',1,now()),
('bd-s09-lab7','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C4-arquitectura-vectorial',false,'Explica tu consulta $vectorSearch y una limitación concreta.',1,now()),
('bd-s09-lab8','self-report','[{"id":"decision","type":"text","min_chars":20},{"id":"limit","type":"text","min_chars":40}]','{}','C5-hibrida-evaluacion',false,'¿Qué aporta cada ranking a RRF y qué no resuelve la fusión?',1,now()),
('bd-s09-lab-eval','self-report','[{"id":"result","type":"number"},{"id":"limit","type":"text","min_chars":40}]','{}','C5-hibrida-evaluacion',false,'Comparte tu Precision@k y el dato que todavía te falta.',1,now()),
('bd-s09-lab9','self-report','[{"id":"decision","type":"text","min_chars":30},{"id":"alternative","type":"text","min_chars":10},{"id":"limit","type":"text","min_chars":40}]','{}','C5-hibrida-evaluacion',false,'Tu evidencia final: decisión, alternativa descartada y límite.',1,now())
on conflict(code) do update set
  evaluator=excluded.evaluator,steps=excluded.steps,config=excluded.config,competency_code=excluded.competency_code,
  seeded=excluded.seeded,wall_prompt=excluded.wall_prompt,version=excluded.version,updated_at=now();

comment on table public.bd_evidence is 'Evidencia formativa verificable de laboratorios Big Data. El payload no es progreso oficial por sí solo: el veredicto del backend determina completion.';
comment on table public.bd_lab_codes is 'Códigos efímeros para enviar evidencia desde recursos externos como Colab sin exponer el token LMS.';
