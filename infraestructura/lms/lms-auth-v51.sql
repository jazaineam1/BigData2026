-- LMS V5.1 · backfill de expiración de sesiones legacy
-- Las nuevas sesiones ya reciben expires_at desde learning-auth.
-- Este backfill elimina sesiones activas históricas sin fecha explícita.

update public.lms_auth_sessions s
set expires_at = s.created_at
  + case when u.role='student' then interval '30 days' else interval '24 hours' end
from public.lms_users u
where u.id=s.user_id
  and s.expires_at is null;

comment on column public.lms_auth_sessions.expires_at is
  'Vencimiento explícito de la sesión LMS. V5.1 backfillea sesiones legacy; estudiantes nuevos: 30 días, otros roles: 24 horas.';
