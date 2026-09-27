-- LMS V5.1 · índices de rutas calientes
-- Mejora consultas de evidencia, códigos LAB y muro sin cambiar semántica ni RLS.

create index if not exists bd_evidence_activity_code_idx
  on public.bd_evidence(activity_code);

create index if not exists bd_lab_codes_course_run_id_idx
  on public.bd_lab_codes(course_run_id);

create index if not exists bd_wall_posts_activity_code_idx
  on public.bd_wall_posts(activity_code);

create index if not exists bd_wall_posts_evidence_id_idx
  on public.bd_wall_posts(evidence_id)
  where evidence_id is not null;

create index if not exists bd_wall_posts_parent_id_idx
  on public.bd_wall_posts(parent_id)
  where parent_id is not null;

create index if not exists bd_wall_reactions_user_id_idx
  on public.bd_wall_reactions(user_id);

-- Consultas frecuentes del endpoint público de solicitud.
create index if not exists lms_access_requests_email_course_created_idx
  on public.lms_access_requests(lower(email), course_code, created_at desc);
