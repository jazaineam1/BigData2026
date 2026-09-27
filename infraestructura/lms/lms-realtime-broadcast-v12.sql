-- LMS Realtime V12 · migrar invalidaciones efímeras a Broadcast.
-- La tabla bd_realtime_signals queda como legado histórico; ya no recibe escrituras.

do $$
begin
  if exists (
    select 1 from pg_publication_tables
    where pubname='supabase_realtime'
      and schemaname='public'
      and tablename='bd_realtime_signals'
  ) then
    execute 'alter publication supabase_realtime drop table public.bd_realtime_signals';
  end if;
end $$;

do $$
begin
  if exists (select 1 from cron.job where jobname='bigdata-prune-realtime-signals') then
    perform cron.unschedule('bigdata-prune-realtime-signals');
  end if;
end $$;

comment on table public.bd_realtime_signals is
  'LEGACY V6/V11: invalidaciones efímeras antiguas. Desde V12 el LMS usa Supabase Realtime Broadcast y no inserta nuevas filas.';
