-- Analítica explicable e intervenciones v2.
-- Aplicado como migración Supabase: lms_analytics_interventions_v2.
create table if not exists public.lms_alert_rules_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  title text not null,
  description text not null default '',
  rule_type text not null check (rule_type in ('inactivity_days','overdue_assignments','mastery_below','unreviewed_submissions')),
  params jsonb not null default '{}'::jsonb,
  active boolean not null default true,
  position integer not null default 0,
  updated_by uuid references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now(),
  primary key(course_run_id,code)
);

create table if not exists public.lms_interventions_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  kind text not null default 'follow_up',
  note text not null,
  status text not null default 'open' check (status in ('open','resolved')),
  follow_up_at timestamptz,
  created_at timestamptz not null default now(),
  resolved_at timestamptz,
  resolved_by uuid references public.lms_users(id) on delete set null
);
create index if not exists lms_interventions_v2_run_user_idx on public.lms_interventions_v2(course_run_id,user_id,status,created_at desc);

create table if not exists public.lms_student_snapshots_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  snapshot_date date not null,
  last_activity_at timestamptz,
  pending_count integer not null default 0,
  overdue_count integer not null default 0,
  reviewed_count integer not null default 0,
  mastery_avg numeric,
  mastered_count integer not null default 0,
  active_seconds_s08 integer not null default 0,
  created_at timestamptz not null default now(),
  primary key(course_run_id,user_id,snapshot_date)
);
create index if not exists lms_student_snapshots_v2_user_date_idx on public.lms_student_snapshots_v2(user_id,snapshot_date desc);

alter table public.lms_alert_rules_v2 enable row level security;
alter table public.lms_interventions_v2 enable row level security;
alter table public.lms_student_snapshots_v2 enable row level security;
revoke all on public.lms_alert_rules_v2, public.lms_interventions_v2, public.lms_student_snapshots_v2 from anon, authenticated;
grant all on public.lms_alert_rules_v2, public.lms_interventions_v2, public.lms_student_snapshots_v2 to service_role;
