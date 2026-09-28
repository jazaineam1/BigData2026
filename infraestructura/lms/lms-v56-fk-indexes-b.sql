-- LMS V56 · índices de cobertura para claves foráneas señaladas por Performance Advisor.
-- Idempotente: no cambia datos; evita scans innecesarios en joins y deletes relacionados.
create index if not exists lms_course_runs_course_code_idx on public.lms_course_runs (course_code);
create index if not exists lms_discussion_posts_v2_parent_id_idx on public.lms_discussion_posts_v2 (parent_id);
create index if not exists lms_discussion_posts_v2_user_id_idx on public.lms_discussion_posts_v2 (user_id);
create index if not exists lms_discussion_threads_v2_assignment_id_idx on public.lms_discussion_threads_v2 (assignment_id);
create index if not exists lms_discussion_threads_v2_run_session_idx on public.lms_discussion_threads_v2 (course_run_id,session_number);
create index if not exists lms_discussion_threads_v2_created_by_idx on public.lms_discussion_threads_v2 (created_by);
create index if not exists lms_grade_history_v2_actor_user_id_idx on public.lms_grade_history_v2 (actor_user_id);
create index if not exists lms_grade_history_v2_assignment_id_idx on public.lms_grade_history_v2 (assignment_id);
create index if not exists lms_grade_history_v2_user_id_idx on public.lms_grade_history_v2 (user_id);
create index if not exists lms_group_contributions_v2_user_id_idx on public.lms_group_contributions_v2 (user_id);
create index if not exists lms_group_submissions_v2_group_id_idx on public.lms_group_submissions_v2 (group_id);
create index if not exists lms_group_submissions_v2_reviewed_by_idx on public.lms_group_submissions_v2 (reviewed_by);
create index if not exists lms_group_submissions_v2_submitted_by_idx on public.lms_group_submissions_v2 (submitted_by);
create index if not exists lms_groups_v2_created_by_idx on public.lms_groups_v2 (created_by);
create index if not exists lms_interventions_v2_created_by_idx on public.lms_interventions_v2 (created_by);
create index if not exists lms_interventions_v2_resolved_by_idx on public.lms_interventions_v2 (resolved_by);
