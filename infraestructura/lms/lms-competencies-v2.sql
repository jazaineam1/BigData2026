-- Competencias y dominio v2 por cohorte.
-- Aplicado como migración Supabase: lms_competencies_v2.
create table if not exists public.lms_competencies_v2 (
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  code text not null,
  domain text not null,
  title text not null,
  description text not null default '',
  position integer not null default 0,
  mastery_threshold numeric not null default 80 check (mastery_threshold between 0 and 100),
  min_evidence_count integer not null default 1 check (min_evidence_count between 1 and 20),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  primary key(course_run_id,code)
);
create index if not exists lms_competencies_v2_run_position_idx on public.lms_competencies_v2(course_run_id,position);

create table if not exists public.lms_assignment_competencies_v2 (
  assignment_id uuid not null references public.lms_assignments_v2(id) on delete cascade,
  course_run_id uuid not null,
  competency_code text not null,
  rubric_code text,
  weight numeric not null default 1 check (weight > 0),
  created_at timestamptz not null default now(),
  primary key(assignment_id,competency_code,rubric_code),
  foreign key(course_run_id,competency_code)
    references public.lms_competencies_v2(course_run_id,code) on delete cascade
);
create index if not exists lms_assignment_competencies_v2_comp_idx on public.lms_assignment_competencies_v2(course_run_id,competency_code);

alter table public.lms_competencies_v2 enable row level security;
alter table public.lms_assignment_competencies_v2 enable row level security;
revoke all on public.lms_competencies_v2, public.lms_assignment_competencies_v2 from anon, authenticated;
grant all on public.lms_competencies_v2, public.lms_assignment_competencies_v2 to service_role;
