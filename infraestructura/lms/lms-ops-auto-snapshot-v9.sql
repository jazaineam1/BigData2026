-- LMS operaciones · snapshot académico automático diario
-- Capa de portabilidad separada de las tablas de negocio. NO sustituye backups de plataforma.

create extension if not exists pg_net with schema extensions;

insert into storage.buckets (id,name,public,file_size_limit,allowed_mime_types)
values (
  'bigdata-lms-snapshots',
  'bigdata-lms-snapshots',
  false,
  52428800,
  array['application/json']::text[]
)
on conflict (id) do update
set public=false,
    file_size_limit=excluded.file_size_limit,
    allowed_mime_types=excluded.allowed_mime_types;

do $$
begin
  if not exists (select 1 from vault.secrets where name='bigdata_project_url') then
    perform vault.create_secret(
      'https://gnpouhsvsisqoxketlfr.supabase.co',
      'bigdata_project_url',
      'URL interna para cron de snapshot LMS'
    );
  end if;
  if not exists (select 1 from vault.secrets where name='bigdata_publishable_key') then
    perform vault.create_secret(
      'sb_publishable_9l_od2Dg78hu1mPrmxAabA_erL2Tlge',
      'bigdata_publishable_key',
      'Publishable key para invocar Edge desde pg_cron'
    );
  end if;
  if not exists (select 1 from vault.secrets where name='bigdata_snapshot_cron_secret') then
    perform vault.create_secret(
      encode(extensions.gen_random_bytes(32),'hex'),
      'bigdata_snapshot_cron_secret',
      'Secreto interno de scheduler para snapshot académico'
    );
  end if;
end $$;

create or replace function public.bigdata_validate_snapshot_cron_secret(p_secret text)
returns boolean
language sql
security definer
set search_path=''
as $$
  select coalesce(
    extensions.digest(coalesce(p_secret,''),'sha256') =
    extensions.digest((
      select decrypted_secret
      from vault.decrypted_secrets
      where name='bigdata_snapshot_cron_secret'
      limit 1
    ),'sha256'),
    false
  );
$$;

revoke all on function public.bigdata_validate_snapshot_cron_secret(text) from public, anon, authenticated;
grant execute on function public.bigdata_validate_snapshot_cron_secret(text) to service_role;

do $$
begin
  if not exists (
    select 1 from cron.job where jobname='bigdata-daily-academic-snapshot'
  ) then
    perform cron.schedule(
      'bigdata-daily-academic-snapshot',
      '20 8 * * *',
      $cron$
        select net.http_post(
          url := (
            select decrypted_secret from vault.decrypted_secrets
            where name='bigdata_project_url' limit 1
          ) || '/functions/v1/bigdata-lms-ops',
          headers := jsonb_build_object(
            'Content-Type','application/json',
            'Authorization','Bearer ' || (
              select decrypted_secret from vault.decrypted_secrets
              where name='bigdata_publishable_key' limit 1
            ),
            'x-lms-snapshot-secret',(
              select decrypted_secret from vault.decrypted_secrets
              where name='bigdata_snapshot_cron_secret' limit 1
            )
          ),
          body := jsonb_build_object('action','scheduled_snapshot'),
          timeout_milliseconds := 120000
        );
      $cron$
    );
  end if;
end $$;

comment on function public.bigdata_validate_snapshot_cron_secret(text) is
  'Valida el secreto del cron de snapshot sin exponer su valor. Solo service_role puede ejecutarla.';
