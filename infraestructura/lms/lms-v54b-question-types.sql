-- V54-B · Tipos de pregunta definitivos: single_choice, multiple_choice, true_false, numeric.
-- Idempotente: se puede ejecutar más de una vez.
-- Criterio (AGENTS.md §4): el estudiante no escribe respuestas abiertas. 'short_text' queda prohibido.
--
-- Qué hace:
--   Sustituye el CHECK de lms_questions_v2.question_type (el de lms-assessment-engine-v2.sql, que aceptaba
--   'short_text') por uno con los 4 tipos, declarado NOT VALID. Un CHECK NOT VALID:
--     - SÍ se aplica a todo INSERT y a todo UPDATE posterior: no se puede crear una pregunta 'short_text'.
--     - NO revisa las filas que ya existían: la historia se conserva y sigue siendo legible (SELECT).
--   El nombre del CHECK viejo no se supone: se busca en pg_constraint (el que genera Postgres para un CHECK en
--   línea es lms_questions_v2_question_type_check, pero la BD real pudo crearse con otro nombre).
--
-- Qué NO hace:
--   - No borra ni modifica preguntas, quizzes, intentos ni respuestas de tipo 'short_text' ya guardados:
--     el docente, el gradebook y los reportes los siguen leyendo.
--   - No valida la tabla: NO ejecutes VALIDATE CONSTRAINT mientras existan filas históricas 'short_text'; fallaría.
--   - No toca lms_quiz_responses_v2 (su respuesta es jsonb, sin CHECK de tipo) ni lms_quiz_items_v2.
--
-- Consecuencia que hay que conocer (riesgo):
--   Cualquier UPDATE sobre una fila histórica 'short_text' de lms_questions_v2 FALLA por este CHECK, aunque no
--   cambie question_type (p. ej. poner active=false o tocar updated_at). Postgres comprueba el CHECK de la fila
--   nueva completa. La Edge Function bigdata-lms-assess ya no lo intenta: no versiona preguntas de ese tipo.
--   Si algún día hay que modificar una de esas filas, opciones:
--     a) Dejarla intacta (recomendado): la pregunta histórica no estorba; los quizzes nuevos no pueden incluirla.
--     b) Ventana de mantenimiento, en una sola transacción:
--          alter table public.lms_questions_v2 drop constraint lms_questions_v2_question_type_v54b_check;
--          update public.lms_questions_v2 set active = false where question_type = 'short_text' and active;
--          alter table public.lms_questions_v2 add constraint lms_questions_v2_question_type_v54b_check
--            check (question_type in ('single_choice','multiple_choice','true_false','numeric')) not valid;
--        (queda NOT VALID a propósito; las filas 'short_text' siguen existiendo.)
--     c) Solo cuando la historia se haya exportado y archivado fuera de la tabla, borrar esas filas
--        (lms_quiz_items_v2 y lms_quiz_responses_v2 las referencian con ON DELETE RESTRICT: primero habría que
--        decidir qué pasa con esos intentos) y entonces sí VALIDATE CONSTRAINT.

-- ANTES de aplicar (informativo): cuánta historia de este tipo existe.
--   select active, count(*) from public.lms_questions_v2 where question_type = 'short_text' group by active;
--   select count(*) from public.lms_quiz_responses_v2 r
--     join public.lms_questions_v2 q on q.id = r.question_id where q.question_type = 'short_text';

do $$
declare
  old_check record;
begin
  for old_check in
    select conname
    from pg_constraint
    where conrelid = 'public.lms_questions_v2'::regclass
      and contype = 'c'
      and pg_get_constraintdef(oid) ilike '%question_type%'
      and conname <> 'lms_questions_v2_question_type_v54b_check'
  loop
    execute format('alter table public.lms_questions_v2 drop constraint %I', old_check.conname);
  end loop;

  if not exists (
    select 1
    from pg_constraint
    where conrelid = 'public.lms_questions_v2'::regclass
      and conname = 'lms_questions_v2_question_type_v54b_check'
  ) then
    alter table public.lms_questions_v2
      add constraint lms_questions_v2_question_type_v54b_check
      check (question_type in ('single_choice','multiple_choice','true_false','numeric')) not valid;
  end if;
end
$$;

-- DESPUÉS de aplicar (informativo): debe listar exactamente un CHECK sobre question_type, con convalidated = false.
--   select conname, convalidated, pg_get_constraintdef(oid)
--   from pg_constraint
--   where conrelid = 'public.lms_questions_v2'::regclass and contype = 'c' and pg_get_constraintdef(oid) ilike '%question_type%';
-- Prueba de que rechaza lo nuevo (dentro de una transacción que luego se revierte):
--   begin; insert into public.lms_questions_v2 (course_run_id, code, question_type, prompt, created_by)
--     values ('<run_id>', 'prueba-v54b', 'short_text', 'x', '<user_id>'); rollback;   -- debe fallar por el CHECK
