-- LMS · retención de señales Realtime efímeras
-- Las señales sirven para invalidar vistas, no son evidencia académica.

create index if not exists bd_realtime_signals_created_at_idx
  on public.bd_realtime_signals(created_at);

create extension if not exists pg_cron with schema pg_catalog;
grant usage on schema cron to postgres;
grant all privileges on all tables in schema cron to postgres;

do $$
begin
  if not exists (
    select 1 from cron.job where jobname='bigdata-prune-realtime-signals'
  ) then
    perform cron.schedule(
      'bigdata-prune-realtime-signals',
      '17 * * * *',
      $cron$
        delete from public.bd_realtime_signals
        where created_at < now() - interval '24 hours';
      $cron$
    );
  end if;
end $$;

comment on table public.bd_realtime_signals is
  'Señales efímeras sin PII para invalidación LMS. Retención operativa máxima objetivo: 24 horas.';
