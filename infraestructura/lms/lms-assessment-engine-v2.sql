-- Fase 3B · archivos privados + banco de preguntas + quizzes.
-- Aplicado como migraciones lms_assessment_engine_v2 y lms_quiz_gradebook_link_v2.

create table if not exists public.lms_submission_files_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  submission_id uuid references public.lms_submissions_v2(id) on delete cascade,
  bucket text not null default 'bigdata-lms-private',
  object_path text not null unique,
  file_name text not null,
  mime_type text not null,
  size_bytes bigint not null check (size_bytes > 0 and size_bytes <= 20971520),
  status text not null default 'pending' check (status in ('pending','attached','abandoned')),
  created_at timestamptz not null default now(),
  attached_at timestamptz
);
create index if not exists lms_submission_files_v2_user_assignment_idx
  on public.lms_submission_files_v2(user_id,assignment_id,created_at desc);

create table if not exists public.lms_questions_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  version integer not null default 1 check (version >= 1),
  question_type text not null check (question_type in ('single_choice','multiple_choice','true_false','numeric','short_text')),
  prompt text not null check (char_length(prompt) between 1 and 8000),
  options jsonb not null default '[]'::jsonb,
  answer_key jsonb not null default '{}'::jsonb,
  explanation text not null default '',
  default_points numeric not null default 1 check (default_points > 0 and default_points <= 1000),
  tags text[] not null default '{}'::text[],
  active boolean not null default true,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(course_run_id,code,version)
);
create index if not exists lms_questions_v2_run_code_idx
  on public.lms_questions_v2(course_run_id,code,version desc);

create table if not exists public.lms_quizzes_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  session_number integer,
  title text not null check (char_length(title) between 3 and 180),
  instructions text not null default '',
  release_at timestamptz,
  due_at timestamptz,
  max_attempts integer not null default 1 check (max_attempts between 1 and 20),
  time_limit_minutes integer check (time_limit_minutes between 1 and 480),
  shuffle_questions boolean not null default false,
  shuffle_options boolean not null default false,
  published boolean not null default false,
  active boolean not null default true,
  assignment_id uuid references public.lms_assignments_v2(id) on delete set null,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(course_run_id,code),
  foreign key(course_run_id,session_number)
    references public.lms_run_sessions_v2(course_run_id,session_number)
    on delete set null
);
create index if not exists lms_quizzes_v2_run_release_idx
  on public.lms_quizzes_v2(course_run_id,published,release_at,due_at);
create unique index if not exists lms_quizzes_v2_assignment_uidx
  on public.lms_quizzes_v2(assignment_id) where assignment_id is not null;

create table if not exists public.lms_quiz_items_v2 (
  quiz_id uuid not null references public.lms_quizzes_v2(id) on delete cascade,
  question_id uuid not null references public.lms_questions_v2(id) on delete restrict,
  position integer not null default 0,
  points numeric not null check (points > 0 and points <= 1000),
  required boolean not null default true,
  primary key(quiz_id,question_id)
);
create index if not exists lms_quiz_items_v2_quiz_position_idx
  on public.lms_quiz_items_v2(quiz_id,position);

create table if not exists public.lms_quiz_attempts_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  quiz_id uuid not null references public.lms_quizzes_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  attempt integer not null check (attempt >= 1),
  status text not null default 'in_progress' check (status in ('in_progress','submitted','reviewed')),
  started_at timestamptz not null default now(),
  expires_at timestamptz,
  submitted_at timestamptz,
  question_order jsonb not null default '[]'::jsonb,
  option_orders jsonb not null default '{}'::jsonb,
  auto_score numeric not null default 0,
  manual_score numeric not null default 0,
  score numeric,
  max_score numeric not null default 0,
  unique(quiz_id,user_id,attempt)
);
create index if not exists lms_quiz_attempts_v2_user_idx
  on public.lms_quiz_attempts_v2(user_id,quiz_id,attempt desc);

create table if not exists public.lms_quiz_responses_v2 (
  attempt_id uuid not null references public.lms_quiz_attempts_v2(id) on delete cascade,
  question_id uuid not null references public.lms_questions_v2(id) on delete restrict,
  response jsonb not null default '{}'::jsonb,
  auto_score numeric,
  manual_score numeric,
  feedback text,
  graded_by uuid references public.lms_users(id) on delete set null,
  graded_at timestamptz,
  saved_at timestamptz not null default now(),
  primary key(attempt_id,question_id)
);
create index if not exists lms_quiz_responses_v2_attempt_idx
  on public.lms_quiz_responses_v2(attempt_id);

alter table public.lms_submission_files_v2 enable row level security;
alter table public.lms_questions_v2 enable row level security;
alter table public.lms_quizzes_v2 enable row level security;
alter table public.lms_quiz_items_v2 enable row level security;
alter table public.lms_quiz_attempts_v2 enable row level security;
alter table public.lms_quiz_responses_v2 enable row level security;

revoke all on public.lms_submission_files_v2,public.lms_questions_v2,public.lms_quizzes_v2,
 public.lms_quiz_items_v2,public.lms_quiz_attempts_v2,public.lms_quiz_responses_v2 from anon,authenticated;
grant all on public.lms_submission_files_v2,public.lms_questions_v2,public.lms_quizzes_v2,
 public.lms_quiz_items_v2,public.lms_quiz_attempts_v2,public.lms_quiz_responses_v2 to service_role;
