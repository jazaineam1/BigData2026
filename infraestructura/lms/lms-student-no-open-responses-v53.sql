-- LMS V53 · experiencia estudiante sin respuestas abiertas
-- El LMS conserva herramientas de búsqueda/consulta, pero elimina campos libres usados como respuesta/evaluación.

drop table if exists public.bd_wall_reactions;
drop table if exists public.bd_wall_posts;

update public.lms_assignments_v2
set allowed_types=array_remove(allowed_types,'text'),
    updated_at=now()
where 'text'=any(allowed_types);

alter table public.lms_questions_v2
  drop constraint if exists lms_questions_v2_question_type_check;
alter table public.lms_questions_v2
  add constraint lms_questions_v2_question_type_check
  check (question_type = any(array[
    'single_choice'::text,
    'multiple_choice'::text,
    'true_false'::text,
    'numeric'::text
  ]));

update public.lms_assignment_group_settings_v2
set peer_review_enabled=false,
    peer_rubric='[]'::jsonb,
    anonymous_peer_review=false,
    updated_at=now()
where peer_review_enabled is true
   or coalesce(jsonb_array_length(peer_rubric),0)>0
   or anonymous_peer_review is true;

update public.bd_activity_catalog
set config=coalesce(config,'{}'::jsonb)-'requires_transfer'
where code in ('bd-s09-lab3','bd-s09-lab4','bd-s09-lab8');

comment on table public.lms_questions_v2 is
  'Banco de preguntas LMS. En esta cohorte solo admite tipos objetivos: selección única/múltiple, verdadero-falso y numérico.';
