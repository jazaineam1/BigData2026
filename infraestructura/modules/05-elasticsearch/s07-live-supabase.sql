-- S07 Live · Big Data 2026-2S · Universidad Central
-- Estado canónico v3 · primer intento + mastery
--
-- Objetivo:
-- - ranking formativo por primer intento;
-- - mastery score por reintentos después de pistas;
-- - 8 actividades / 21 puntos;
-- - Broadcast para actualización inmediata + polling de respaldo en frontend.

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
set search_path=public
as $$
declare
  v_correct_option text; v_explanation text; v_points integer; v_kind text;
  v_ok boolean; v_first boolean; v_attempts integer;
  v_first_score integer; v_mastery_score integer; v_answered integer; v_mastered_count integer;
  v_norm_answer text; v_norm_correct text;
begin
  if not exists (select 1 from public.s07_live_scores where participant_id=p_participant and session_id=p_session) then
    raise exception 'Participante no válido para esta sesión.';
  end if;

  select q.correct_option,q.explanation,q.points,q.kind
  into v_correct_option,v_explanation,v_points,v_kind
  from public.s07_live_questions q
  where q.session_id=p_session and q.question_id=p_question and q.active=true;

  if v_correct_option is null then raise exception 'Pregunta no encontrada.'; end if;

  v_norm_answer:=replace(regexp_replace(lower(trim(coalesce(p_answer,''))),'\s+','','g'),',','.');
  v_norm_correct:=replace(regexp_replace(lower(trim(v_correct_option)),'\s+','','g'),',','.');
  if v_kind in ('numeric','result_number') then
    begin v_ok:=abs(v_norm_answer::numeric-v_norm_correct::numeric)<0.0001; exception when others then v_ok:=false; end;
  else
    v_ok:=v_norm_answer=v_norm_correct;
  end if;

  select not exists (select 1 from public.s07_live_responses where participant_id=p_participant and session_id=p_session and question_id=p_question) into v_first;

  insert into public.s07_live_responses(session_id,participant_id,question_id,answer,correct,answered_at,attempt_count,first_answer,first_correct,mastered,last_answer,last_correct)
  values (p_session,p_participant,p_question,trim(p_answer),v_ok,now(),1,trim(p_answer),v_ok,v_ok,trim(p_answer),v_ok)
  on conflict (participant_id,question_id)
  do update set answer=excluded.answer, correct=excluded.correct, answered_at=now(), attempt_count=public.s07_live_responses.attempt_count+1,
                mastered=public.s07_live_responses.mastered or excluded.correct, last_answer=excluded.answer, last_correct=excluded.correct;

  select r.attempt_count into v_attempts from public.s07_live_responses r
  where r.participant_id=p_participant and r.session_id=p_session and r.question_id=p_question;

  select count(*)::integer,
         count(*) filter(where r.mastered)::integer,
         coalesce(sum(case when r.first_correct then q.points else 0 end),0)::integer,
         coalesce(sum(case when r.mastered then q.points else 0 end),0)::integer
  into v_answered,v_mastered_count,v_first_score,v_mastery_score
  from public.s07_live_responses r
  join public.s07_live_questions q on q.session_id=r.session_id and q.question_id=r.question_id
  where r.participant_id=p_participant and r.session_id=p_session;

  update public.s07_live_scores
  set score=v_first_score, first_score=v_first_score, mastery_score=v_mastery_score,
      answered=v_answered, mastery_answered=v_mastered_count, updated_at=now()
  where participant_id=p_participant and session_id=p_session;

  return jsonb_build_object(
    'correct',v_ok,
    'first_attempt',v_first,
    'locked_for_ranking',not v_first,
    'attempt_count',v_attempts,
    'explanation',case when v_first and not v_ok then 'Pista: revisa la regla del concepto antes de reintentar. La explicación completa aparece después del segundo intento.' else v_explanation end,
    'full_explanation',v_explanation,
    'points_possible',v_points,
    'points_earned_first',case when v_first and v_ok then v_points else 0 end,
    'points_earned_mastery',case when v_ok then v_points else 0 end,
    'score',v_first_score,
    'mastery_score',v_mastery_score,
    'answered',v_answered,
    'mastery_answered',v_mastered_count
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
