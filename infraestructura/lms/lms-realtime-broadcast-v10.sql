-- LMS Realtime V10 · Broadcast efímero
-- Las invalidaciones nuevas viajan por Realtime Broadcast.
-- La tabla bd_realtime_signals queda solo como legado temporal para rollback/auditoría de transición.

do $$
begin
  if exists (
    select 1
    from pg_publication_tables
    where pubname='supabase_realtime'
      and schemaname='public'
      and tablename='bd_realtime_signals'
  ) then
    execute 'alter publication supabase_realtime drop table public.bd_realtime_signals';
  end if;
end $$;

comment on table public.bd_realtime_signals is
  'LEGACY V10: ya no recibe invalidaciones nuevas. Realtime usa Broadcast público por sesión; el cron de 24 h elimina filas antiguas.';
