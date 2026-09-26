-- Motor de evaluación v2 por cohorte.
-- Aplicado como migración Supabase: lms_gradebook_v2.
create table if not exists public.lms_assignments_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  session_number integer,
  title text not null check (char_length(title) between 3 and 180),
  instructions text not null default '',
  due_at timestamptz,
  required boolean not null default true,
  max_score numeric not null default 100 check (max_score > 0),
  rubric jsonb not null default '[]'::jsonb,
  allowed_types text[] not null default array['text','url']::text[],
  active boolean not null default true,
  max_attempts integer not null default 1 check (max_attempts between 1 and 20),
  category text not null default 'coursework',
  weight numeric not null default 1 check (weight >= 0),
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(course_run_id,code),
  foreign key (course_run_id,session_number)
    references public.lms_run_sessions_v2(course_run_id,session_number)
    on delete set null
);
create index if not exists lms_assignments_v2_run_due_idx on public.lms_assignments_v2(course_run_id,due_at);
create index if not exists lms_assignments_v2_session_idx on public.lms_assignments_v2(course_run_id,session_number);

create table if not exists public.lms_submissions_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  attempt integer not null check (attempt >= 1),
  artifact_type text not null check (artifact_type in ('text','url','file','evidence')),
  artifact jsonb not null default '{}'::jsonb,
  status text not null default 'submitted' check (status in ('draft','submitted','reviewed','returned')),
  submitted_at timestamptz not null default now(),
  score numeric,
  feedback text,
  rubric_scores jsonb not null default '{}'::jsonb,
  reviewed_by uuid references public.lms_users(id) on delete set null,
  reviewed_at timestamptz,
  unique(assignment_id,user_id,attempt)
);
create index if not exists lms_submissions_v2_assignment_user_idx on public.lms_submissions_v2(assignment_id,user_id,attempt desc);
create index if not exists lms_submissions_v2_user_idx on public.lms_submissions_v2(user_id,submitted_at desc);

create table if not exists public.lms_grade_history_v2 (
  id bigint generated always as identity primary key,
  submission_id uuid not null references public.lms_submissions_v2(id) on delete cascade,
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  actor_user_id uuid references public.lms_users(id) on delete set null,
  previous_score numeric,
  new_score numeric,
  previous_feedback text,
  new_feedback text,
  rubric_scores jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);
create index if not exists lms_grade_history_v2_submission_idx on public.lms_grade_history_v2(submission_id,created_at desc);

create table if not exists public.lms_assignment_accommodations_v2 (
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  due_at timestamptz,
  max_attempts integer check (max_attempts between 1 and 20),
  notes text not null default '',
  updated_by uuid references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now(),
  primary key(assignment_id,user_id)
);

alter table public.lms_assignments_v2 enable row level security;
alter table public.lms_submissions_v2 enable row level security;
alter table public.lms_grade_history_v2 enable row level security;
alter table public.lms_assignment_accommodations_v2 enable row level security;
revoke all on public.lms_assignments_v2, public.lms_submissions_v2, public.lms_grade_history_v2, public.lms_assignment_accommodations_v2 from anon, authenticated;
grant all on public.lms_assignments_v2, public.lms_submissions_v2, public.lms_grade_history_v2, public.lms_assignment_accommodations_v2 to service_role;
