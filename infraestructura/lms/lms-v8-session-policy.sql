-- LMS V8 · documentación de política de sesión por rol
-- No modifica sesiones activas: la política se aplica al emitir nuevas sesiones desde bigdata-auth.

comment on column public.lms_auth_sessions.expires_at is
  'Vencimiento explícito LMS. Nuevas sesiones V8: student 30 días; teacher 12 horas; admin 4 horas. Sesiones legacy conservan fallback de compatibilidad cuando expires_at es null.';

comment on column public.lms_auth_sessions.persistent is
  'Persistencia lógica de sesión. V8: student=true; teacher/admin=false. El cliente evita localStorage cuando persistent=false.';
