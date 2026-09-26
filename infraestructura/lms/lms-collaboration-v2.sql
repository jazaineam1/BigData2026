-- Colaboración v2 por cohorte.
-- Aplicado como migración Supabase: lms_collaboration_v2.

create table if not exists public.lms_groups_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  name text not null check (char_length(name) between 2 and 120),
  description text not null default '',
  active boolean not null default true,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  unique(course_run_id,name)
);

create table if not exists public.lms_group_members_v2 (
  group_id uuid not null references public.lms_groups_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  role text not null default 'member' check (role in ('member','lead')),
  joined_at timestamptz not null default now(),
  primary key(group_id,user_id)
);
create index if not exists lms_group_members_v2_user_idx on public.lms_group_members_v2(user_id,group_id);

create table if not exists public.lms_assignment_group_settings_v2 (
  assignment_id uuid primary key references public.lms_assignments_v2(id) on delete cascade,
  enabled boolean not null default true,
  peer_review_enabled boolean not null default false,
  reviews_per_student integer not null default 1 check (reviews_per_student between 1 and 5),
  peer_rubric jsonb not null default '[]'::jsonb,
  anonymous_peer_review boolean not null default false,
  updated_by uuid references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now()
);

create table if not exists public.lms_group_submissions_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  group_id uuid not null references public.lms_groups_v2(id) on delete cascade,
  attempt integer not null check (attempt >= 1),
  artifact_type text not null check (artifact_type in ('text','url','evidence')),
  artifact jsonb not null default '{}'::jsonb,
  status text not null default 'submitted' check (status in ('draft','submitted','reviewed','returned')),
  submitted_by uuid not null references public.lms_users(id) on delete restrict,
  submitted_at timestamptz not null default now(),
  score numeric,
  feedback text,
  rubric_scores jsonb not null default '{}'::jsonb,
  reviewed_by uuid references public.lms_users(id) on delete set null,
  reviewed_at timestamptz,
  unique(assignment_id,group_id,attempt)
);
create index if not exists lms_group_submissions_v2_assignment_idx on public.lms_group_submissions_v2(assignment_id,group_id,attempt desc);

create table if not exists public.lms_group_contributions_v2 (
  group_submission_id uuid not null references public.lms_group_submissions_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  contribution_text text not null default '',
  confirmed_at timestamptz not null default now(),
  primary key(group_submission_id,user_id)
);

create table if not exists public.lms_discussion_threads_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number integer,
  assignment_id uuid references public.lms_assignments_v2(id) on delete cascade,
  title text not null check (char_length(title) between 3 and 180),
  pinned boolean not null default false,
  locked boolean not null default false,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  foreign key(course_run_id,session_number)
    references public.lms_run_sessions_v2(course_run_id,session_number)
    on delete set null
);
create index if not exists lms_discussion_threads_v2_run_idx on public.lms_discussion_threads_v2(course_run_id,pinned desc,created_at desc);

create table if not exists public.lms_discussion_posts_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  thread_id uuid not null references public.lms_discussion_threads_v2(id) on delete cascade,
  user_id uuid not null references public.lms_users(id) on delete cascade,
  parent_id uuid references public.lms_discussion_posts_v2(id) on delete cascade,
  body text not null check (char_length(body) between 1 and 8000),
  pinned_answer boolean not null default false,
  hidden boolean not null default false,
  created_at timestamptz not null default now(),
  edited_at timestamptz
);
create index if not exists lms_discussion_posts_v2_thread_idx on public.lms_discussion_posts_v2(thread_id,created_at);


create table if not exists public.lms_discussion_mentions_v2 (
  post_id uuid not null references public.lms_discussion_posts_v2(id) on delete cascade,
  mentioned_user_id uuid not null references public.lms_users(id) on delete cascade,
  created_at timestamptz not null default now(),
  read_at timestamptz,
  primary key(post_id,mentioned_user_id)
);
create index if not exists lms_discussion_mentions_v2_user_idx
  on public.lms_discussion_mentions_v2(mentioned_user_id,read_at,created_at desc);

create table if not exists public.lms_peer_reviews_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  reviewee_submission_id uuid not null references public.lms_group_submissions_v2(id) on delete cascade,
  reviewer_user_id uuid not null references public.lms_users(id) on delete cascade,
  rubric_scores jsonb not null default '{}'::jsonb,
  feedback text not null default '',
  status text not null default 'submitted' check (status in ('draft','submitted')),
  submitted_at timestamptz not null default now(),
  unique(reviewee_submission_id,reviewer_user_id)
);
create index if not exists lms_peer_reviews_v2_reviewer_idx on public.lms_peer_reviews_v2(reviewer_user_id,assignment_id);

alter table public.lms_groups_v2 enable row level security;
alter table public.lms_group_members_v2 enable row level security;
alter table public.lms_assignment_group_settings_v2 enable row level security;
alter table public.lms_group_submissions_v2 enable row level security;
alter table public.lms_group_contributions_v2 enable row level security;
alter table public.lms_discussion_threads_v2 enable row level security;
alter table public.lms_discussion_posts_v2 enable row level security;
alter table public.lms_peer_reviews_v2 enable row level security;
alter table public.lms_discussion_mentions_v2 enable row level security;

revoke all on public.lms_groups_v2, public.lms_group_members_v2, public.lms_assignment_group_settings_v2,
  public.lms_group_submissions_v2, public.lms_group_contributions_v2,
  public.lms_discussion_threads_v2, public.lms_discussion_posts_v2, public.lms_discussion_mentions_v2, public.lms_peer_reviews_v2
  from anon, authenticated;

grant all on public.lms_groups_v2, public.lms_group_members_v2, public.lms_assignment_group_settings_v2,
  public.lms_group_submissions_v2, public.lms_group_contributions_v2,
  public.lms_discussion_threads_v2, public.lms_discussion_posts_v2, public.lms_discussion_mentions_v2, public.lms_peer_reviews_v2
  to service_role;
