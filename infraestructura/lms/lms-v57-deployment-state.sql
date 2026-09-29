-- LMS V57 · canary de esquema para detectar drift entre main y producción.
create table if not exists public.bd_deployment_state (
  component text primary key,
  release text not null,
  updated_at timestamptz not null default now()
);
alter table public.bd_deployment_state enable row level security;

insert into public.bd_deployment_state(component,release,updated_at)
values ('schema','2026-09-29-v57',now())
on conflict(component) do update
set release=excluded.release,updated_at=excluded.updated_at;

comment on table public.bd_deployment_state is
  'Canary técnico de despliegue; RLS sin policies impide acceso directo del cliente.';
