-- S07 Live · Big Data 2026-2S · Universidad Central
-- Estado canónico v3 · primer intento + mastery
--
-- Objetivo:
-- - ranking formativo por primer intento;
-- - mastery score por reintentos después de pistas;
-- - 8 actividades / 21 puntos;
-- - Broadcast para actualización inmediata + polling de respaldo en frontend.

alter table public.s07_live_questions
  add column if not exists hint text;

update public.s07_live_questions q
set hint = case q.question_id
  when 'q0' then 'Distingue una condición exacta de una necesidad que requiere ordenar candidatos por relevancia.'
  when 'q1' then 'Piensa en qué campos deben analizar palabras y cuáles deben conservar valores exactos o tipos estructurados.'
  when 'q2' then 'Empieza por la entrada original y termina en los términos que realmente quedan indexados.'
  when 'q3' then 'Separa la solicitud en método HTTP + ruta + cuerpo JSON. Para este reto no necesitas que s07-demo exista todavía.'
  when 'q4' then 'Compara el conteo remoto con el número de procesos únicos que preparaste antes de la ingesta.'
  when 'q5' then 'Separa lo que debe aportar score de lo que solo debe restringir; luego añade evidencia visible.'
  when 'q6' then 'Cuenta cuántos de los cinco primeros resultados cumplen el criterio de relevancia y divide por cinco.'
  when 'q7' then 'Separa tipos de campo, pesos de relevancia y filtro de negocio antes de validar el diseño.'
  else 'Revisa la regla del concepto antes de volver a intentarlo.'
end
where q.session_id=(select id from public.s07_live_sessions where code='ELASTIC-S07');

update public.s07_live_questions
set correct_option='POST|/_analyze|spanish',
    explanation='En S07 usamos POST /_analyze: POST es el método HTTP elegido, /_analyze es la ruta y analyzer/text viajan en el cuerpo JSON. La Analyze API también acepta GET. Cuando exista un índice, también puedes usar POST /mi_indice/_analyze.'
where question_id='q3';


alter table public.s07_live_scores
  add column if not exists first_score integer not null default 0,
  add column if not exists mastery_score integer not null default 0,
  add column if not exists mastery_answered integer not null default 0;

alter table public.s07_live_responses
  add column if not exists attempt_count integer not null default 0,
  add column if not exists first_answer text,
  add column if not exists first_correct boolean,
  add column if not exists mastered boolean not null default false,
  add column if not exists last_answer text,
  add column if not exists last_correct boolean;

create or replace function public.s07_live_submit(
  p_session uuid,
  p_participant uuid,
  p_question text,
  p_answer text
)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_correct_option text;
  v_explanation text;
  v_hint text;
  v_points integer;
  v_kind text;
  v_ok boolean;
  v_existing public.s07_live_responses%rowtype;
  v_first_attempt boolean;
  v_first_correct boolean;
  v_attempt_count integer;
  v_first_score integer;
  v_mastery_score integer;
  v_answered integer;
  v_mastery_answered integer;
  v_norm_answer text;
  v_norm_correct text;
  v_rank_delta integer;
  v_mastery_delta integer;
begin
  if not exists (
    select 1 from public.s07_live_scores
    where participant_id=p_participant and session_id=p_session
  ) then
    raise exception 'Participante no válido para esta sesión.';
  end if;

  select q.correct_option,q.explanation,q.points,q.kind,
         coalesce(q.hint,'Revisa la regla del concepto antes de volver a intentarlo.')
  into v_correct_option,v_explanation,v_points,v_kind,v_hint
  from public.s07_live_questions q
  where q.session_id=p_session and q.question_id=p_question and q.active=true;

  if v_correct_option is null then raise exception 'Pregunta no encontrada.'; end if;

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

  select * into v_existing
  from public.s07_live_responses
  where participant_id=p_participant and question_id=p_question;

  v_first_attempt := not found;

  if v_first_attempt then
    insert into public.s07_live_responses(
      session_id,participant_id,question_id,answer,correct,answered_at,
      first_answer,first_correct,attempt_count,mastered,last_answer,last_correct
    ) values (
      p_session,p_participant,p_question,trim(p_answer),v_ok,now(),
      trim(p_answer),v_ok,1,v_ok,trim(p_answer),v_ok
    );
    v_rank_delta := case when v_ok then v_points else 0 end;
    v_mastery_delta := case when v_ok then v_points else 0 end;
  else
    update public.s07_live_responses
    set answer=trim(p_answer),
        correct=v_ok,
        answered_at=now(),
        attempt_count=coalesce(attempt_count,1)+1,
        mastered=coalesce(mastered,false) or v_ok,
        last_answer=trim(p_answer),
        last_correct=v_ok
    where participant_id=p_participant and question_id=p_question;
    v_rank_delta := 0;
    v_mastery_delta := case when v_ok and not coalesce(v_existing.mastered,false) then v_points else 0 end;
  end if;

  select
    count(*)::integer,
    count(*) filter(where coalesce(r.mastered,false))::integer,
    coalesce(sum(case when coalesce(r.first_correct,false) then q.points else 0 end),0)::integer,
    coalesce(sum(case when coalesce(r.mastered,false) then q.points else 0 end),0)::integer
  into v_answered,v_mastery_answered,v_first_score,v_mastery_score
  from public.s07_live_responses r
  join public.s07_live_questions q
    on q.session_id=r.session_id and q.question_id=r.question_id
  where r.participant_id=p_participant and r.session_id=p_session;

  update public.s07_live_scores
  set score=v_first_score,
      first_score=v_first_score,
      mastery_score=v_mastery_score,
      answered=v_answered,
      mastery_answered=v_mastery_answered,
      updated_at=now()
  where participant_id=p_participant and session_id=p_session;

  select first_correct,attempt_count into v_first_correct,v_attempt_count
  from public.s07_live_responses
  where participant_id=p_participant and question_id=p_question;

  return jsonb_build_object(
    'correct',v_ok,
    'first_attempt',v_first_attempt,
    'first_correct',v_first_correct,
    'attempt_count',v_attempt_count,
    'locked_for_ranking',not v_first_attempt,
    'explanation',case when v_ok or v_attempt_count>=2 then v_explanation else v_hint end,
    'full_explanation',v_explanation,
    'points_possible',v_points,
    'points_earned_first',v_rank_delta,
    'points_earned_mastery',v_mastery_delta,
    'points_earned',v_rank_delta,
    'score',v_first_score,
    'mastery_score',v_mastery_score,
    'answered',v_answered,
    'mastery_answered',v_mastery_answered
  );
end;
$$;

drop function if exists public.s07_live_leaderboard(text);
create function public.s07_live_leaderboard(p_code text)
returns table(rank bigint,participant_id uuid,nickname text,score integer,mastery_score integer,answered integer,mastery_answered integer,updated_at timestamptz)
language sql security definer set search_path=public
as $$
  select row_number() over(order by sc.score desc,sc.mastery_score desc,sc.answered desc,sc.updated_at asc),
         sc.participant_id,sc.nickname,sc.score,sc.mastery_score,sc.answered,sc.mastery_answered,sc.updated_at
  from public.s07_live_scores sc
  join public.s07_live_sessions s on s.id=sc.session_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  order by sc.score desc,sc.mastery_score desc,sc.answered desc,sc.updated_at asc,sc.nickname;
$$;

drop function if exists public.s07_live_activity_stats(text);
create function public.s07_live_activity_stats(p_code text)
returns table(question_id text,q_position smallint,kind text,points integer,responses bigint,first_correct bigint,mastered bigint,pct_first numeric,pct_mastery numeric)
language sql security definer set search_path=public
as $$
  select q.question_id,q.position,q.kind,q.points,
         count(r.id), count(r.id) filter(where r.first_correct), count(r.id) filter(where r.mastered),
         case when count(r.id)=0 then 0 else round(100.0*count(r.id) filter(where r.first_correct)/count(r.id),1) end,
         case when count(r.id)=0 then 0 else round(100.0*count(r.id) filter(where r.mastered)/count(r.id),1) end
  from public.s07_live_sessions s
  join public.s07_live_questions q on q.session_id=s.id and q.active=true
  left join public.s07_live_responses r on r.session_id=q.session_id and r.question_id=q.question_id
  where upper(s.code)=upper(trim(p_code)) and s.active=true
  group by q.question_id,q.position,q.kind,q.points
  order by q.position;
$$;

grant execute on function public.s07_live_submit(uuid,uuid,text,text) to anon,authenticated;
grant execute on function public.s07_live_leaderboard(text) to anon,authenticated;
grant execute on function public.s07_live_activity_stats(text) to anon,authenticated;



-- ============================================================
-- Teacher Wall seguro · misma presentación, no tercera herramienta
-- ============================================================

create table if not exists public.s07_teacher_config (
  id integer primary key check (id = 1),
  pin_hash text not null,
  updated_at timestamptz not null default now()
);

alter table public.s07_teacher_config enable row level security;

-- Solo se versiona el SHA-256; el PIN en texto plano NO vive en el repositorio.
insert into public.s07_teacher_config(id,pin_hash)
values (1,'7848a2ecb7dc286be8a1abb7441f0e9cb305876e94f31b051b7349dbea07a78c')
on conflict (id) do update set pin_hash=excluded.pin_hash, updated_at=now();

revoke all on public.s07_teacher_config from anon, authenticated;

create or replace function public.s07_teacher_auth(p_pin text)
returns boolean
language sql security definer
set search_path=public,extensions
as $$
  select exists (
    select 1 from public.s07_teacher_config
    where id=1
      and pin_hash=encode(extensions.digest(coalesce(p_pin,''),'sha256'),'hex')
  );
$$;

create or replace function public.s07_teacher_create_round(p_pin text,p_label text default null)
returns jsonb
language plpgsql security definer
set search_path=public,extensions
as $$
declare
  v_source uuid;
  v_new uuid;
  v_code text;
  v_try integer:=0;
begin
  if not public.s07_teacher_auth(p_pin) then raise exception 'PIN docente inválido.'; end if;

  select id into v_source from public.s07_live_sessions where upper(code)='ELASTIC-S07' limit 1;
  if v_source is null then raise exception 'No existe la sesión plantilla ELASTIC-S07.'; end if;

  loop
    v_try:=v_try+1;
    v_code:='S07-'||upper(substr(replace(gen_random_uuid()::text,'-',''),1,6));
    exit when not exists(select 1 from public.s07_live_sessions where code=v_code);
    if v_try>20 then raise exception 'No fue posible generar código único.'; end if;
  end loop;

  insert into public.s07_live_sessions(code,title,active)
  values(v_code,coalesce(nullif(trim(p_label),''),'S07 · Elasticsearch Search Lab'),true)
  returning id into v_new;

  insert into public.s07_live_questions(session_id,question_id,position,prompt,correct_option,explanation,kind,points,active,hint)
  select v_new,question_id,position,prompt,correct_option,explanation,kind,points,active,hint
  from public.s07_live_questions
  where session_id=v_source;

  return jsonb_build_object('ok',true,'code',v_code,'session_id',v_new);
end;
$$;

create or replace function public.s07_teacher_reset_round(p_pin text,p_code text)
returns jsonb
language plpgsql security definer
set search_path=public,extensions
as $$
declare
  v_session uuid;
  v_participants integer;
  v_responses integer;
begin
  if not public.s07_teacher_auth(p_pin) then raise exception 'PIN docente inválido.'; end if;

  select id into v_session from public.s07_live_sessions
  where upper(code)=upper(trim(p_code)) limit 1;
  if v_session is null then raise exception 'Partida no encontrada.'; end if;

  select count(*)::integer into v_participants from public.s07_live_scores where session_id=v_session;
  select count(*)::integer into v_responses from public.s07_live_responses where session_id=v_session;

  delete from public.s07_live_responses where session_id=v_session;
  update public.s07_live_scores
  set score=0,first_score=0,mastery_score=0,answered=0,mastery_answered=0,updated_at=now()
  where session_id=v_session;

  return jsonb_build_object('ok',true,'code',upper(trim(p_code)),
    'participants_preserved',v_participants,'responses_deleted',v_responses);
end;
$$;

create or replace function public.s07_teacher_close_round(p_pin text,p_code text)
returns jsonb
language plpgsql security definer
set search_path=public,extensions
as $$
declare v_session uuid;
begin
  if not public.s07_teacher_auth(p_pin) then raise exception 'PIN docente inválido.'; end if;
  update public.s07_live_sessions set active=false
  where upper(code)=upper(trim(p_code)) returning id into v_session;
  if v_session is null then raise exception 'Partida no encontrada.'; end if;
  return jsonb_build_object('ok',true,'code',upper(trim(p_code)),'active',false);
end;
$$;

create or replace function public.s07_teacher_reopen_round(p_pin text,p_code text)
returns jsonb
language plpgsql security definer
set search_path=public,extensions
as $$
declare v_session uuid;
begin
  if not public.s07_teacher_auth(p_pin) then raise exception 'PIN docente inválido.'; end if;
  update public.s07_live_sessions set active=true
  where upper(code)=upper(trim(p_code)) returning id into v_session;
  if v_session is null then raise exception 'Partida no encontrada.'; end if;
  return jsonb_build_object('ok',true,'code',upper(trim(p_code)),'active',true);
end;
$$;

drop function if exists public.s07_teacher_rounds(text);
create function public.s07_teacher_rounds(p_pin text)
returns table(code text,title text,active boolean,created_at timestamptz,participants bigint,responses bigint)
language plpgsql security definer
set search_path=public,extensions
as $$
begin
  if not public.s07_teacher_auth(p_pin) then raise exception 'PIN docente inválido.'; end if;
  return query
  select s.code,s.title,s.active,s.created_at,
         count(distinct sc.participant_id)::bigint,
         count(distinct r.id)::bigint
  from public.s07_live_sessions s
  left join public.s07_live_scores sc on sc.session_id=s.id
  left join public.s07_live_responses r on r.session_id=s.id
  where s.code='ELASTIC-S07' or s.code like 'S07-%' or s.code like 'ELASTIC-S07-%'
  group by s.id,s.code,s.title,s.active,s.created_at
  order by s.created_at desc
  limit 30;
end;
$$;

grant execute on function public.s07_teacher_auth(text) to anon,authenticated;
grant execute on function public.s07_teacher_create_round(text,text) to anon,authenticated;
grant execute on function public.s07_teacher_reset_round(text,text) to anon,authenticated;
grant execute on function public.s07_teacher_close_round(text,text) to anon,authenticated;
grant execute on function public.s07_teacher_reopen_round(text,text) to anon,authenticated;
grant execute on function public.s07_teacher_rounds(text) to anon,authenticated;
