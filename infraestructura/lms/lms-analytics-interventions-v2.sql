-- Analítica longitudinal e intervenciones v2 por cohorte.
-- Aplicado en Supabase como migración lms_analytics_interventions_v2.

create table if not exists public.lms_learning_events_v2 (
  id bigint generated always as identity primary key,
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  event_type text not null check (event_type in (
    'portal_opened','assignments_opened','competencies_opened','progress_opened',
    'session_resource_opened','assignment_submitted','feedback_viewed'
  )),
  session_number integer,
  entity_type text,
  entity_id text,
  active_seconds_delta integer not null default 0 check (active_seconds_delta between 0 and 300),
  metadata jsonb not null default '{}'::jsonb,
  client_at timestamptz,
  created_at timestamptz not null default now()
);
create index if not exists lms_learning_events_v2_run_user_created_idx
  on public.lms_learning_events_v2(course_run_id,user_id,created_at desc);
create index if not exists lms_learning_events_v2_run_type_created_idx
  on public.lms_learning_events_v2(course_run_id,event_type,created_at desc);

create table if not exists public.lms_analytics_rules_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  title text not null,
  description text not null default '',
  enabled boolean not null default true,
  severity text not null default 'info' check (severity in ('info','medium','high')),
  config jsonb not null default '{}'::jsonb,
  position integer not null default 0,
  updated_by uuid references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now(),
  primary key(course_run_id,code)
);

create table if not exists public.lms_interventions_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  signal_code text,
  note text not null,
  action_text text not null default '',
  status text not null default 'open' check (status in ('open','follow_up','closed')),
  follow_up_at timestamptz,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_by uuid references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now()
);
create index if not exists lms_interventions_v2_run_user_created_idx
  on public.lms_interventions_v2(course_run_id,user_id,created_at desc);
create index if not exists lms_interventions_v2_run_status_follow_idx
  on public.lms_interventions_v2(course_run_id,status,follow_up_at);

alter table public.lms_learning_events_v2 enable row level security;
alter table public.lms_analytics_rules_v2 enable row level security;
alter table public.lms_interventions_v2 enable row level security;
revoke all on public.lms_learning_events_v2, public.lms_analytics_rules_v2, public.lms_interventions_v2 from anon, authenticated;
grant all on public.lms_learning_events_v2, public.lms_analytics_rules_v2, public.lms_interventions_v2 to service_role;
