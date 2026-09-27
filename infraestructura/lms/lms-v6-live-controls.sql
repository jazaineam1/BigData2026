-- LMS V6 · controles docentes + señal Realtime segura
-- La tabla de señales no contiene datos académicos ni identidades.
-- El navegador recibe solo invalidaciones y vuelve a consultar la Edge Function autenticada.

create table if not exists public.bd_session_controls (
  id bigint generated always as identity primary key,
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  control_key text not null,
  control_type text not null check (control_type in ('open_lab','close_lab','goto_slide','pin_hint')),
  payload jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  created_by uuid not null references public.lms_users(id),
  created_at timestamptz not null default now(),
  expires_at timestamptz null,
  superseded_at timestamptz null
);

create index if not exists bd_session_controls_lookup_idx
  on public.bd_session_controls(course_run_id, session_number, control_key, active, created_at desc);

create unique index if not exists bd_session_controls_one_active_key_uidx
  on public.bd_session_controls(course_run_id, session_number, control_key)
  where active;

alter table public.bd_session_controls enable row level security;
revoke all on table public.bd_session_controls from anon, authenticated;

drop policy if exists "bd_session_controls_no_direct_access" on public.bd_session_controls;
create policy "bd_session_controls_no_direct_access"
  on public.bd_session_controls
  for all
  to anon, authenticated
  using (false)
  with check (false);

create table if not exists public.bd_realtime_signals (
  id bigint generated always as identity primary key,
  course_code text not null default 'bigdata',
  session_number smallint not null check (session_number between 1 and 99),
  scope text not null check (scope in ('controls','wall','progress','teacher_wall')),
  created_at timestamptz not null default now()
);

alter table public.bd_realtime_signals enable row level security;
grant select on table public.bd_realtime_signals to anon, authenticated;

drop policy if exists "bd_realtime_signals_public_read" on public.bd_realtime_signals;
create policy "bd_realtime_signals_public_read"
  on public.bd_realtime_signals
  for select
  to anon, authenticated
  using (course_code = 'bigdata');

do $$
begin
  if not exists (
    select 1
    from pg_publication_tables
    where pubname='supabase_realtime'
      and schemaname='public'
      and tablename='bd_realtime_signals'
  ) then
    alter publication supabase_realtime add table public.bd_realtime_signals;
  end if;
end $$;

comment on table public.bd_session_controls is
  'Controles docentes server-side por sesión. No hay acceso directo desde el navegador.';
comment on table public.bd_realtime_signals is
  'Señales públicas sin PII para invalidar vistas LMS; los datos reales se recuperan por Edge Function autenticada.';
