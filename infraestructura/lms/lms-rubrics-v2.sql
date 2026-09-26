-- Biblioteca de rúbricas reutilizables por cohorte.
-- Aplicado en Supabase como lms_rubric_templates_v2.

create table if not exists public.lms_rubric_templates_v2 (
  id uuid primary key default extensions.gen_random_uuid(),
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  title text not null check (char_length(title) between 3 and 180),
  description text not null default '',
  max_score numeric not null check (max_score > 0),
  criteria jsonb not null default '[]'::jsonb,
  active boolean not null default true,
  created_by uuid not null references public.lms_users(id) on delete restrict,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique(course_run_id,code)
);
create index if not exists lms_rubric_templates_v2_run_idx
  on public.lms_rubric_templates_v2(course_run_id,active,code);
alter table public.lms_rubric_templates_v2 enable row level security;
revoke all on public.lms_rubric_templates_v2 from anon, authenticated;
grant all on public.lms_rubric_templates_v2 to service_role;
