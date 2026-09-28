-- LMS V56 · índices de cobertura para claves foráneas señaladas por Performance Advisor.
-- Idempotente: no cambia datos; evita scans innecesarios en joins y deletes relacionados.
create index if not exists lms_interventions_v2_user_id_idx on public.lms_interventions_v2 (user_id);
create index if not exists lms_learning_events_v2_user_id_idx on public.lms_learning_events_v2 (user_id);
create index if not exists lms_peer_reviews_v2_assignment_id_idx on public.lms_peer_reviews_v2 (assignment_id);
create index if not exists lms_questions_v2_created_by_idx on public.lms_questions_v2 (created_by);
create index if not exists lms_quiz_items_v2_question_id_idx on public.lms_quiz_items_v2 (question_id);
create index if not exists lms_quiz_responses_v2_graded_by_idx on public.lms_quiz_responses_v2 (graded_by);
create index if not exists lms_quiz_responses_v2_question_id_idx on public.lms_quiz_responses_v2 (question_id);
create index if not exists lms_quizzes_v2_run_session_idx on public.lms_quizzes_v2 (course_run_id,session_number);
create index if not exists lms_quizzes_v2_created_by_idx on public.lms_quizzes_v2 (created_by);
create index if not exists lms_recovery_codes_user_id_idx on public.lms_recovery_codes (user_id);
create index if not exists lms_rubric_templates_v2_created_by_idx on public.lms_rubric_templates_v2 (created_by);
create index if not exists lms_submission_files_v2_assignment_id_idx on public.lms_submission_files_v2 (assignment_id);
create index if not exists lms_submission_files_v2_submission_id_idx on public.lms_submission_files_v2 (submission_id);
create index if not exists lms_submissions_reviewed_by_idx on public.lms_submissions (reviewed_by);
create index if not exists lms_submissions_user_id_idx on public.lms_submissions (user_id);
create index if not exists lms_submissions_v2_reviewed_by_idx on public.lms_submissions_v2 (reviewed_by);
