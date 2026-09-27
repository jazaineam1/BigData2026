-- S09 V14 · retirar telemetría de confianza
-- La autocomprobación queda en una sola decisión: elegir opción y responder.

update public.bd_lms_activity_progress
set metadata = coalesce(metadata,'{}'::jsonb) - 'last_confidence' - 'first_confidence',
    updated_at = now()
where activity_code like 'bd-s09-c%'
  and (
    coalesce(metadata,'{}'::jsonb) ? 'last_confidence'
    or coalesce(metadata,'{}'::jsonb) ? 'first_confidence'
  );

update public.bd_lms_events
set metadata = coalesce(metadata,'{}'::jsonb) - 'confidence'
where event_type='challenge_answered'
  and activity_code like 'bd-s09-c%'
  and coalesce(metadata,'{}'::jsonb) ? 'confidence';
