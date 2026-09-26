-- Modelo genérico de sesiones/recursos por cohorte.
-- Aplicado en Supabase como migración lms_run_sessions_v2_backbone.
-- El diseño usa PK compuesta (course_run_id, session_number) para evitar colisiones entre cursos.

create table if not exists public.lms_run_sessions_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number integer not null check (session_number between 1 and 99),
  title text not null,
  summary text not null default '',
  status text not null default 'draft' check (status in ('draft','visible','closed')),
  path text,
  starts_at timestamptz,
  position integer not null default 0,
  metadata jsonb not null default '{}'::jsonb,
  published_at timestamptz,
  updated_at timestamptz not null default now(),
  primary key (course_run_id, session_number)
);

create index if not exists lms_run_sessions_v2_run_position_idx
  on public.lms_run_sessions_v2(course_run_id, position);

create table if not exists public.lms_run_resources_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null,
  session_number integer not null,
  resource_type text not null check (resource_type in ('presentation','notebook','guide','reading','lab','link','evidence')),
  title text not null,
  summary text not null default '',
  url text not null,
  position integer not null default 0,
  visible boolean not null default true,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  foreign key (course_run_id, session_number)
    references public.lms_run_sessions_v2(course_run_id, session_number)
    on delete cascade
);

create index if not exists lms_run_resources_v2_run_session_idx
  on public.lms_run_resources_v2(course_run_id, session_number, position);

alter table public.lms_run_sessions_v2 enable row level security;
alter table public.lms_run_resources_v2 enable row level security;
revoke all on public.lms_run_sessions_v2 from anon, authenticated;
revoke all on public.lms_run_resources_v2 from anon, authenticated;
grant all on public.lms_run_sessions_v2 to service_role;
grant all on public.lms_run_resources_v2 to service_role;
