-- Big Data LMS V5 · idempotencia para runtime offline
-- 26-sep-2026
-- Permite reintentos seguros desde navegador/Colab sin duplicar progreso ni tiempo activo.

alter table public.bd_lms_events
  add column if not exists client_event_id text;

alter table public.bd_evidence
  add column if not exists client_evidence_id text;

alter table public.bd_wall_posts
  add column if not exists client_post_id text;

alter table public.bd_lms_events
  drop constraint if exists bd_lms_events_client_event_id_format;
alter table public.bd_lms_events
  add constraint bd_lms_events_client_event_id_format
  check (client_event_id is null or client_event_id ~ '^[A-Za-z0-9._:-]{8,120}$');

alter table public.bd_evidence
  drop constraint if exists bd_evidence_client_evidence_id_format;
alter table public.bd_evidence
  add constraint bd_evidence_client_evidence_id_format
  check (client_evidence_id is null or client_evidence_id ~ '^[A-Za-z0-9._:-]{8,120}$');

alter table public.bd_wall_posts
  drop constraint if exists bd_wall_posts_client_post_id_format;
alter table public.bd_wall_posts
  add constraint bd_wall_posts_client_post_id_format
  check (client_post_id is null or client_post_id ~ '^[A-Za-z0-9._:-]{8,120}$');

create unique index if not exists bd_lms_events_client_event_uidx
  on public.bd_lms_events(user_id,course_run_id,client_event_id)
  where client_event_id is not null;

create unique index if not exists bd_evidence_client_evidence_uidx
  on public.bd_evidence(user_id,course_run_id,client_evidence_id)
  where client_evidence_id is not null;

create unique index if not exists bd_wall_posts_client_post_uidx
  on public.bd_wall_posts(user_id,course_run_id,client_post_id)
  where client_post_id is not null;

comment on column public.bd_lms_events.client_event_id is
  'Idempotency key generada por el cliente. Reintentos con la misma clave no deben incrementar tiempo ni progreso.';
comment on column public.bd_evidence.client_evidence_id is
  'Idempotency key de una entrega de evidencia; permite reintentos offline seguros.';
comment on column public.bd_wall_posts.client_post_id is
  'Idempotency key de una publicación del muro; evita duplicados por reconexión.';
