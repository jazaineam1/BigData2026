-- V54-A · El estudiante no entrega ni publica texto libre.
-- Idempotente: se puede ejecutar más de una vez.
--
-- Qué hace:
--   1. Las tareas nuevas nacen con tipos de entrega estructurados (URL o archivo).
--   2. Las tareas existentes dejan de ofrecer 'text'. Si 'text' era su único tipo,
--      pasan a 'url' para no quedar sin forma de entrega.
-- Qué NO hace:
--   - No toca lms_submissions_v2 ni lms_group_submissions_v2: las entregas históricas
--     de tipo 'text' se conservan y siguen siendo legibles para el docente y el gradebook.
--   - No elimina tablas de discusión ni de muro: quedan como historia sin endpoint de escritura
--     para el estudiante. Su retiro es una migración posterior (V54-B).

-- ANTES de aplicar: lista las tareas activas que solo aceptaban texto. Sus instrucciones pueden
-- decir "responde aquí"; tras la migración pedirán una URL, así que reescríbelas.
--   select code, title, instructions from public.lms_assignments_v2
--   where active and allowed_types = array['text']::text[];

alter table public.lms_assignments_v2
  alter column allowed_types set default array['url','file']::text[];

update public.lms_assignments_v2
set allowed_types = case
      when cardinality(array_remove(allowed_types,'text')) = 0 then array['url']::text[]
      else array_remove(allowed_types,'text')
    end,
    updated_at = now()
where 'text' = any(allowed_types);
