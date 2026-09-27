-- S09 V16 · evidencia LAB9 completamente estructurada, sin texto libre

update public.bd_activity_catalog
set config = coalesce(config,'{}'::jsonb) || jsonb_build_object(
  'schema_version', 3,
  'response_mode', 'structured',
  'query_choices', jsonb_build_object(
    'aircraft_repair','reparación de aviones militares',
    'aircraft_maintenance','mantenimiento de aeronaves militares',
    'air_force_maintenance','mantenimiento de aeronaves de la fuerza aérea'
  ),
  'strategy_choices', jsonb_build_array('lexical','semantic','hybrid'),
  'limit_choices', jsonb_build_array('sample_five','manual_labels','model_dependence','latency_not_measured')
),
version = greatest(version,3),
updated_at = now()
where code='bd-s09-lab9';

update public.bd_lms_activities
set metadata = coalesce(metadata,'{}'::jsonb) || jsonb_build_object(
  'response_mode','structured',
  'open_response',false
)
where code='bd-s09-lab9';
