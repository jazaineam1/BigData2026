-- S07 Live · Big Data 2026-2S · Universidad Central
-- Backend formativo para ranking y checkpoints en tiempo real.
-- Aplicado en Supabase el 24-sep-2026.
--
-- Diseño:
-- - GitHub Pages aloja la interfaz.
-- - Supabase almacena únicamente alias, respuestas y puntaje.
-- - No se almacenan correos ni credenciales de Elasticsearch.
-- - La clave publicada en el frontend es publishable/anon.
-- - Las tablas sensibles tienen RLS; los writes pasan por RPC SECURITY DEFINER.
-- - s07_live_scores es la única tabla de lectura pública y participa en Realtime.

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
on public.s07_live_scores for select to anon, authenticated
using (
  exists (
    select 1 from public.s07_live_sessions s
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

insert into public.s07_live_questions(session_id,question_id,position,prompt,correct_option,explanation,active)
select s.id,q.question_id,q.position,q.prompt,q.correct_option,q.explanation,true
from public.s07_live_sessions s
cross join (values
  ('q0',1,'¿Qué tarea necesita ranking de relevancia?','b','Buscar candidatos textuales requiere ordenar documentos por relevancia.'),
  ('q1',2,'¿Cuál mapping es más razonable?','c','El tipo depende del uso: text para búsqueda, keyword para igualdad y boolean para verdadero/falso.'),
  ('q2',3,'¿Qué componente produce los tokens?','a','El analyzer transforma el texto en tokens.'),
  ('q3',4,'¿Dónde viene el documento original en un hit?','b','El documento recuperado vive en _source.'),
  ('q4',5,'¿Qué prueba mínima confirma conexión desde Python?','c','client.info() valida conectividad y autorización.'),
  ('q5',6,'Si 3 de 5 resultados son relevantes, ¿cuál es Precision@5?','a','3/5 = 0,60.')
) as q(question_id,position,prompt,correct_option,explanation)
where s.code='ELASTIC-S07'
on conflict (session_id,question_id) do update
set position=excluded.position,prompt=excluded.prompt,correct_option=excluded.correct_option,
    explanation=excluded.explanation,active=true;

create or replace function public.s07_live_join(
  p_code text,p_nickname text,p_client_id uuid
)
returns table(participant_id uuid,session_id uuid,nickname text,score integer,answered integer)
language plpgsql security definer set search_path=public
as $$
declare v_session uuid; v_name text;
begin
  v_name:=trim(coalesce(p_nickname,''));
  if char_length(v_name)<2 or char_length(v_name)>40 then
    raise exception 'Usa un nombre o alias de 2 a 40 caracteres.';
  end if;

  select s.id into v_session
  from public.s07_live_sessions s
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  limit 1;

  if v_session is null then raise exception 'Código de sesión inválido o sesión cerrada.'; end if;

  insert into public.s07_live_scores(session_id,client_id,nickname)
  values(v_session,p_client_id,v_name)
  on conflict on constraint s07_live_scores_session_id_client_id_key
  do update set nickname=excluded.nickname,updated_at=now();

  return query
  select sc.participant_id,sc.session_id,sc.nickname,sc.score,sc.answered
  from public.s07_live_scores sc
  where sc.session_id=v_session and sc.client_id=p_client_id;
end $$;

create or replace function public.s07_live_submit(
  p_session uuid,p_participant uuid,p_question text,p_answer text
)
returns jsonb
language plpgsql security definer set search_path=public
as $$
declare
  v_correct_option text; v_explanation text; v_ok boolean;
  v_answered integer; v_score integer;
begin
  if not exists(
    select 1 from public.s07_live_scores
    where participant_id=p_participant and session_id=p_session
  ) then raise exception 'Participante no válido para esta sesión.'; end if;

  select q.correct_option,q.explanation into v_correct_option,v_explanation
  from public.s07_live_questions q
  where q.session_id=p_session and q.question_id=p_question and q.active=true;

  if v_correct_option is null then raise exception 'Pregunta no encontrada.'; end if;
  v_ok:=lower(trim(p_answer))=lower(trim(v_correct_option));

  insert into public.s07_live_responses(session_id,participant_id,question_id,answer,correct,answered_at)
  values(p_session,p_participant,p_question,trim(p_answer),v_ok,now())
  on conflict(participant_id,question_id)
  do update set answer=excluded.answer,correct=excluded.correct,answered_at=now();

  select count(*)::integer,count(*) filter(where correct)::integer
  into v_answered,v_score
  from public.s07_live_responses
  where participant_id=p_participant and session_id=p_session;

  update public.s07_live_scores
  set score=v_score,answered=v_answered,updated_at=now()
  where participant_id=p_participant and session_id=p_session;

  return jsonb_build_object(
    'correct',v_ok,'explanation',v_explanation,'score',v_score,'answered',v_answered
  );
end $$;

create or replace function public.s07_live_leaderboard(p_code text)
returns table(rank bigint,nickname text,score integer,answered integer,updated_at timestamptz)
language sql security definer set search_path=public
as $$
  select row_number() over(order by sc.score desc,sc.answered desc,sc.updated_at asc),
         sc.nickname,sc.score,sc.answered,sc.updated_at
  from public.s07_live_scores sc
  join public.s07_live_sessions s on s.id=sc.session_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  order by sc.score desc,sc.answered desc,sc.updated_at asc,sc.nickname;
$$;

create or replace function public.s07_live_question_stats(p_code text,p_question text)
returns table(option text,responses bigint)
language sql security definer set search_path=public
as $$
  select r.answer,count(*)
  from public.s07_live_responses r
  join public.s07_live_sessions s on s.id=r.session_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true and r.question_id=p_question
  group by r.answer order by r.answer;
$$;

grant execute on function public.s07_live_join(text,text,uuid) to anon,authenticated;
grant execute on function public.s07_live_submit(uuid,uuid,text,text) to anon,authenticated;
grant execute on function public.s07_live_leaderboard(text) to anon,authenticated;
grant execute on function public.s07_live_question_stats(text,text) to anon,authenticated;

do $$
begin
  if not exists(
    select 1 from pg_publication_tables
    where pubname='supabase_realtime' and schemaname='public' and tablename='s07_live_scores'
  ) then
    alter publication supabase_realtime add table public.s07_live_scores;
  end if;
end $$;
