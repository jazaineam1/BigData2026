-- LMS V5.1 · limpieza operativa posterior al hardening
-- 27-sep-2026
-- 1) marca como revocadas sesiones cuyo vencimiento ya pasó;
-- 2) elimina un índice duplicado exacto;
-- 3) impide invocar directamente por REST una función SECURITY DEFINER sin consumidores.

update public.lms_auth_sessions
set revoked_at = coalesce(revoked_at, expires_at, now())
where revoked_at is null
  and expires_at is not null
  and expires_at <= now();

drop index if exists public.lms_access_requests_email_course_created_idx;

revoke execute on function public.lms_recover_with_code(text,text,text) from public, anon, authenticated;

comment on function public.lms_recover_with_code(text,text,text) is
  'Función interna legacy de recuperación. V5.1 revoca EXECUTE a public/anon/authenticated; no se expone por REST.';
