-- LMS V56 · índices de cobertura para claves foráneas señaladas por Performance Advisor.
-- Idempotente: no cambia datos; evita scans innecesarios en joins y deletes relacionados.
create index if not exists bd_evidence_reviewed_by_idx on public.bd_evidence (reviewed_by);
create index if not exists bd_session_controls_created_by_idx on public.bd_session_controls (created_by);
create index if not exists lms_activity_competencies_competency_code_idx on public.lms_activity_competencies (competency_code);
create index if not exists lms_alert_rules_v2_updated_by_idx on public.lms_alert_rules_v2 (updated_by);
create index if not exists lms_analytics_rules_v2_updated_by_idx on public.lms_analytics_rules_v2 (updated_by);
create index if not exists lms_announcement_reads_user_id_idx on public.lms_announcement_reads (user_id);
create index if not exists lms_announcements_created_by_idx on public.lms_announcements (created_by);
create index if not exists lms_assignment_accommodations_v2_updated_by_idx on public.lms_assignment_accommodations_v2 (updated_by);
create index if not exists lms_assignment_accommodations_v2_user_id_idx on public.lms_assignment_accommodations_v2 (user_id);
create index if not exists lms_assignment_group_settings_v2_updated_by_idx on public.lms_assignment_group_settings_v2 (updated_by);
create index if not exists lms_assignments_created_by_idx on public.lms_assignments (created_by);
create index if not exists lms_assignments_session_number_idx on public.lms_assignments (session_number);
create index if not exists lms_assignments_v2_created_by_idx on public.lms_assignments_v2 (created_by);
create index if not exists lms_bookmarks_activity_code_idx on public.lms_bookmarks (activity_code);
create index if not exists lms_bookmarks_session_number_idx on public.lms_bookmarks (session_number);
create index if not exists lms_certificates_issued_by_idx on public.lms_certificates (issued_by);
