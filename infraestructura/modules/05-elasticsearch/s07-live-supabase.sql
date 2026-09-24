-- S07 Live · Big Data 2026-2S · Universidad Central
-- Estado canónico v2 · 24-sep-2026
--
-- Objetivo:
-- - ranking formativo en vivo;
-- - 8 actividades de tipos distintos;
-- - 21 puntos máximos;
-- - Broadcast para actualización inmediata + polling de respaldo en el frontend.
--
-- Datos guardados: alias, respuestas, correcto/incorrecto, puntaje.
-- No se almacenan correos ni credenciales de Elasticsearch.

create table if not exists public.s07_live_sessions (
  id uuid primary key default gen_random_uuid(),
  code text not null unique,
  title text not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create table if not exists public.s07_live_questions (
  session_id uuid not null references public.s07_live_sessions(id) on delete cascade,
  question_id text not null,
  position smallint not null,
  prompt text not null,
  correct_option text not null,
  explanation text not null,
  kind text not null default 'single_choice',
  points integer not null default 1 check (points between 1 and 10),
  active boolean not null default true,
  primary key (session_id, question_id)
);

create table if not exists public.s07_live_scores (
  participant_id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.s07_live_sessions(id) on delete cascade,
  client_id uuid not null,
  nickname text not null check (char_length(nickname) between 2 and 40),
  score integer not null default 0,
  answered integer not null default 0,
  updated_at timestamptz not null default now(),
  unique (session_id, client_id)
);

create table if not exists public.s07_live_responses (
  id bigint generated always as identity primary key,
  session_id uuid not null references public.s07_live_sessions(id) on delete cascade,
  participant_id uuid not null references public.s07_live_scores(participant_id) on delete cascade,
  question_id text not null,
  answer text not null,
  correct boolean not null,
  answered_at timestamptz not null default now(),
  unique (participant_id, question_id)
);

alter table public.s07_live_sessions enable row level security;
alter table public.s07_live_questions enable row level security;
alter table public.s07_live_scores enable row level security;
alter table public.s07_live_responses enable row level security;

drop policy if exists "s07_scores_active_read" on public.s07_live_scores;
create policy "s07_scores_active_read"
on public.s07_live_scores
for select
to anon, authenticated
using (
  exists (
    select 1
    from public.s07_live_sessions s
    where s.id=s07_live_scores.session_id and s.active=true
  )
);

revoke all on public.s07_live_sessions from anon, authenticated;
revoke all on public.s07_live_questions from anon, authenticated;
revoke all on public.s07_live_responses from anon, authenticated;
revoke all on public.s07_live_scores from anon, authenticated;
grant select on public.s07_live_scores to anon, authenticated;

insert into public.s07_live_sessions(code,title,active)
values ('ELASTIC-S07','S07 · Elasticsearch Search Lab',true)
on conflict (code) do update set title=excluded.title,active=true;

insert into public.s07_live_questions(
  session_id,question_id,position,prompt,correct_option,explanation,kind,points,active
)
select s.id,q.question_id,q.q_position,q.prompt,q.correct_option,q.explanation,q.kind,q.points,true
from public.s07_live_sessions s
cross join (values
  ('q0',1,'¿Qué tarea necesita ranking de relevancia?','b',
   'Buscar candidatos textuales exige ordenar documentos por relevancia; un filtro solo decide si cumplen una condición.',
   'single_choice',1),
  ('q1',2,'Clasifica titulo, categoria, premium y publicado.','text|keyword|boolean|date',
   'El tipo depende del uso: titulo se analiza; categoria se compara completa; premium es booleano; publicado es fecha.',
   'mapping_grid',4),
  ('q2',3,'Ordena el recorrido del texto hasta términos buscables.','texto>tokenizer>filtros>tokens',
   'Texto → tokenizer → filtros lingüísticos → tokens indexables.',
   'sequence',2),
  ('q3',4,'Completa la llamada de Console para inspeccionar spanish.','POST|s07-demo/_analyze|spanish',
   'La API _analyze se invoca con POST sobre el índice y recibe el analyzer en JSON.',
   'code_fill',2),
  ('q4',5,'¿Cuántos procesos únicos deben quedar después de bulk()?','1994',
   'El count remoto debe coincidir con 1.994 procesos únicos.',
   'result_number',2),
  ('q5',6,'Construye boost + descripción + filtro adjudicado + highlight.',
   'nombre_proceso^3,descripcion|tipo_registro=historico_adjudicado|highlight',
   'La recuperación textual puntúa; la condición exacta va en filter; highlight apoya inspección.',
   'query_builder',4),
  ('q6',7,'Si 3 de 5 resultados son relevantes, escribe Precision@5.','0.6',
   'Precision@5 = 3/5 = 0,60.',
   'numeric',2),
  ('q7',8,'Diseña el buscador editorial completo.',
   'text|keyword|boolean|date|titulo^4,subtitulo^2,cuerpo|premium=false',
   'El reto combina mapping, pesos de campos y filtro operacional.',
   'transfer_builder',4)
) as q(question_id,q_position,prompt,correct_option,explanation,kind,points)
where s.code='ELASTIC-S07'
on conflict (session_id,question_id) do update
set position=excluded.position,
    prompt=excluded.prompt,
    correct_option=excluded.correct_option,
    explanation=excluded.explanation,
    kind=excluded.kind,
    points=excluded.points,
    active=true;

create or replace function public.s07_live_join(
  p_code text,
  p_nickname text,
  p_client_id uuid
)
returns table(participant_id uuid,session_id uuid,nickname text,score integer,answered integer)
language plpgsql
security definer
set search_path=public
as $$
declare
  v_session uuid;
  v_name text;
begin
  v_name:=trim(coalesce(p_nickname,''));
  if char_length(v_name)<2 or char_length(v_name)>40 then
    raise exception 'Usa un nombre o alias de 2 a 40 caracteres.';
  end if;

  select s.id into v_session
  from public.s07_live_sessions s
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  limit 1;

  if v_session is null then
    raise exception 'Código de sesión inválido o sesión cerrada.';
  end if;

  insert into public.s07_live_scores(session_id,client_id,nickname)
  values(v_session,p_client_id,v_name)
  on conflict on constraint s07_live_scores_session_id_client_id_key
  do update set nickname=excluded.nickname,updated_at=now();

  return query
  select sc.participant_id,sc.session_id,sc.nickname,sc.score,sc.answered
  from public.s07_live_scores sc
  where sc.session_id=v_session and sc.client_id=p_client_id;
end;
$$;

create or replace function public.s07_live_submit(
  p_session uuid,
  p_participant uuid,
  p_question text,
  p_answer text
)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
  v_correct_option text;
  v_explanation text;
  v_points integer;
  v_kind text;
  v_ok boolean;
  v_answered integer;
  v_score integer;
  v_norm_answer text;
  v_norm_correct text;
begin
  if not exists(
    select 1 from public.s07_live_scores
    where participant_id=p_participant and session_id=p_session
  ) then
    raise exception 'Participante no válido para esta sesión.';
  end if;

  select q.correct_option,q.explanation,q.points,q.kind
  into v_correct_option,v_explanation,v_points,v_kind
  from public.s07_live_questions q
  where q.session_id=p_session and q.question_id=p_question and q.active=true;

  if v_correct_option is null then
    raise exception 'Pregunta no encontrada.';
  end if;

  v_norm_answer:=replace(regexp_replace(lower(trim(coalesce(p_answer,''))),'\s+','','g'),',','.');
  v_norm_correct:=replace(regexp_replace(lower(trim(v_correct_option)),'\s+','','g'),',','.');

  if v_kind in ('numeric','result_number') then
    begin
      v_ok:=abs(v_norm_answer::numeric-v_norm_correct::numeric)<0.0001;
    exception when others then
      v_ok:=false;
    end;
  else
    v_ok:=v_norm_answer=v_norm_correct;
  end if;

  insert into public.s07_live_responses(session_id,participant_id,question_id,answer,correct,answered_at)
  values(p_session,p_participant,p_question,trim(p_answer),v_ok,now())
  on conflict(participant_id,question_id)
  do update set answer=excluded.answer,correct=excluded.correct,answered_at=now();

  select count(*)::integer,
         coalesce(sum(case when r.correct then q.points else 0 end),0)::integer
  into v_answered,v_score
  from public.s07_live_responses r
  join public.s07_live_questions q
    on q.session_id=r.session_id and q.question_id=r.question_id
  where r.participant_id=p_participant and r.session_id=p_session;

  update public.s07_live_scores
  set score=v_score,answered=v_answered,updated_at=now()
  where participant_id=p_participant and session_id=p_session;

  return jsonb_build_object(
    'correct',v_ok,
    'explanation',v_explanation,
    'points_possible',v_points,
    'points_earned',case when v_ok then v_points else 0 end,
    'score',v_score,
    'answered',v_answered
  );
end;
$$;

drop function if exists public.s07_live_leaderboard(text);
create function public.s07_live_leaderboard(p_code text)
returns table(rank bigint,participant_id uuid,nickname text,score integer,answered integer,updated_at timestamptz)
language sql
security definer
set search_path=public
as $$
  select
    row_number() over(order by sc.score desc,sc.answered desc,sc.updated_at asc),
    sc.participant_id,
    sc.nickname,
    sc.score,
    sc.answered,
    sc.updated_at
  from public.s07_live_scores sc
  join public.s07_live_sessions s on s.id=sc.session_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  order by sc.score desc,sc.answered desc,sc.updated_at asc,sc.nickname;
$$;

drop function if exists public.s07_live_activity_stats(text);
create function public.s07_live_activity_stats(p_code text)
returns table(
  question_id text,
  q_position smallint,
  kind text,
  points integer,
  responses bigint,
  correct bigint,
  pct_correct numeric
)
language sql
security definer
set search_path=public
as $$
  select
    q.question_id,
    q.position,
    q.kind,
    q.points,
    count(r.id),
    count(r.id) filter(where r.correct),
    case when count(r.id)=0 then 0
         else round(100.0*count(r.id) filter(where r.correct)/count(r.id),1)
    end
  from public.s07_live_sessions s
  join public.s07_live_questions q on q.session_id=s.id and q.active=true
  left join public.s07_live_responses r
    on r.session_id=q.session_id and r.question_id=q.question_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  group by q.question_id,q.position,q.kind,q.points
  order by q.position;
$$;

grant execute on function public.s07_live_join(text,text,uuid) to anon,authenticated;
grant execute on function public.s07_live_submit(uuid,uuid,text,text) to anon,authenticated;
grant execute on function public.s07_live_leaderboard(text) to anon,authenticated;
grant execute on function public.s07_live_activity_stats(text) to anon,authenticated;

-- Broadcast es la ruta principal. Supabase recomienda Broadcast para notificaciones
-- de cambios en base de datos; el frontend conserva polling de 3 s como fallback móvil.
create or replace function public.s07_live_broadcast_score()
returns trigger
language plpgsql
security definer
set search_path=''
as $$
begin
  perform realtime.send(
    jsonb_build_object(
      'session_id',new.session_id,
      'participant_id',new.participant_id,
      'score',new.score,
      'answered',new.answered,
      'updated_at',new.updated_at
    ),
    'score_changed',
    's07:elastic-s07',
    false
  );
  return new;
end;
$$;

drop trigger if exists s07_live_scores_broadcast on public.s07_live_scores;
create trigger s07_live_scores_broadcast
after insert or update on public.s07_live_scores
for each row execute function public.s07_live_broadcast_score();

-- Ya no dependemos de postgres_changes para este tablero.
do $$
begin
  if exists(
    select 1 from pg_publication_tables
    where pubname='supabase_realtime'
      and schemaname='public'
      and tablename='s07_live_scores'
  ) then
    alter publication supabase_realtime drop table public.s07_live_scores;
  end if;
end $$;
