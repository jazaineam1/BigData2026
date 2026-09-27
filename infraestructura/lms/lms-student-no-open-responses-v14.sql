-- LMS V14 · estudiantes sin respuestas abiertas
-- Regla de producto: el estudiante responde solo con selección, verdadero/falso,
-- numérico, URL/archivo o evidencia estructurada generada por el recurso.

-- El antiguo muro de respuestas abiertas queda vacío e inaccesible.
delete from public.bd_wall_reactions;
delete from public.bd_wall_posts;

revoke all on table public.bd_wall_posts from anon, authenticated;
revoke all on table public.bd_wall_reactions from anon, authenticated;

comment on table public.bd_wall_posts is
  'LEGACY V14: muro abierto de estudiantes deshabilitado. No se usa en el runtime.';
comment on table public.bd_wall_reactions is
  'LEGACY V14: reacciones del muro abierto deshabilitadas. No se usa en el runtime.';

-- Ninguna tarea existente debe conservar el tipo texto como entrega de estudiante.
update public.lms_assignments_v2
set allowed_types=array_remove(allowed_types,'text'),
    updated_at=now()
where 'text'=any(allowed_types);

-- El banco ya no permite crear preguntas de respuesta abierta.
-- No existen filas short_text en la cohorte al aplicar esta migración.
alter table public.lms_questions_v2
  drop constraint if exists lms_questions_v2_question_type_check;

alter table public.lms_questions_v2
  add constraint lms_questions_v2_question_type_check
  check (question_type = any(array['single_choice'::text,'multiple_choice'::text,'true_false'::text,'numeric'::text]));

-- La revisión por pares abierta queda desactivada; las rúbricas numéricas históricas se conservan.
update public.lms_assignment_group_settings_v2
set peer_review_enabled=false,
    updated_at=now()
where peer_review_enabled=true;
