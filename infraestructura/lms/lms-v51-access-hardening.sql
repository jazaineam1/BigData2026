-- LMS V5.1 · hardening de tablas de acceso
-- Las Edge Functions operan con service_role; clientes anon/authenticated no requieren acceso SQL directo.

revoke all on table public.lms_access_requests from anon, authenticated;
revoke all on table public.lms_access_tokens from anon, authenticated;
