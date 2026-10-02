-- TC1 V9 · nueva fecha de entrega: 18 de octubre de 2026, 11:59 p. m., hora de Bogotá.
-- Cambia solo due_at de las dos asignaciones del TC1 que creó tc1-v4-secoppipeline.sql.
-- El TC1 no se entrega ni se califica en el LMS (submit_manifest responde 409 TC1_FUERA_DEL_LMS):
-- esta fecha solo se muestra al estudiante. Aplicarla más de una vez no tiene efectos adicionales.
update public.lms_assignments_v2
set due_at='2026-10-18T23:59:59-05:00'::timestamptz,
    updated_at=now()
where code in ('bd-s08-final','bd-s08-control')
returning code, due_at;
