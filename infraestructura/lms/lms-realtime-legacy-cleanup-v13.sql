-- LMS Realtime V13 · limpieza final de señales legacy
-- Broadcast V12 ya reemplazó por completo la tabla como transporte.

delete from public.bd_realtime_signals;

drop policy if exists bd_realtime_signals_public_read
  on public.bd_realtime_signals;

revoke select on table public.bd_realtime_signals
  from anon, authenticated;

comment on table public.bd_realtime_signals is
  'LEGACY vacío: Realtime usa Broadcast. Sin publicación, sin cron y sin acceso directo de clientes.';
