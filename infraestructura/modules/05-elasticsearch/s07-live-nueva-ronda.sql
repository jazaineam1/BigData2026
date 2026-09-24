-- S07 Live · control docente de nueva ronda sin borrar históricos
-- Crea una sesión nueva copiando las preguntas activas desde ELASTIC-S07.
-- Uso sugerido desde el laboratorio: código ELASTIC-S07-HOY o ELASTIC-S07-YYYYMMDD.

create or replace function public.s07_live_teacher_clone_round(
  p_source_code text,
  p_new_code text,
  p_pin text
)
returns jsonb
language plpgsql
security definer
set search_path=public
as $$
declare
  v_source uuid;
  v_new uuid;
  v_code text;
begin
  if coalesce(trim(p_pin),'') <> 'S07-UCENTRAL-2026' then
    raise exception 'PIN docente inválido.';
  end if;

  v_code := upper(trim(p_new_code));
  if v_code !~ '^ELASTIC-S07-[A-Z0-9-]{2,32}$' then
    raise exception 'Código nuevo inválido. Usa formato ELASTIC-S07-...';
  end if;

  select id into v_source
  from public.s07_live_sessions
  where upper(code)=upper(trim(p_source_code)) and active=true
  limit 1;

  if v_source is null then
    raise exception 'Sesión fuente no encontrada.';
  end if;

  insert into public.s07_live_sessions(code,title,active)
  values (v_code,'S07 · Elasticsearch Search Lab · nueva ronda',true)
  on conflict (code) do update set active=true,title=excluded.title
  returning id into v_new;

  insert into public.s07_live_questions(session_id,question_id,position,prompt,correct_option,explanation,kind,points,active,hint)
  select v_new,question_id,position,prompt,correct_option,explanation,kind,points,active,hint
  from public.s07_live_questions
  where session_id=v_source
  on conflict (session_id,question_id) do update
  set position=excluded.position,
      prompt=excluded.prompt,
      correct_option=excluded.correct_option,
      explanation=excluded.explanation,
      kind=excluded.kind,
      points=excluded.points,
      active=excluded.active,
      hint=excluded.hint;

  return jsonb_build_object('ok',true,'code',v_code,'session_id',v_new);
end;
$$;

grant execute on function public.s07_live_teacher_clone_round(text,text,text) to anon, authenticated;
