-- S09 · evidencia auténtica y revisión docente

alter table public.bd_activity_catalog
  drop constraint if exists bd_activity_catalog_evaluator_check;
alter table public.bd_activity_catalog
  add constraint bd_activity_catalog_evaluator_check
  check (evaluator = any (array[
    'choice-hash'::text,
    'seeded-numeric'::text,
    'rubric'::text,
    'self-report'::text,
    'url-trace'::text,
    'authentic-review'::text,
    'none'::text
  ]));

alter table public.bd_evidence
  add column if not exists reviewed_by uuid null references public.lms_users(id),
  add column if not exists reviewed_at timestamptz null,
  add column if not exists rubric jsonb null;

alter table public.bd_evidence
  drop constraint if exists bd_evidence_rubric_size_check;
alter table public.bd_evidence
  add constraint bd_evidence_rubric_size_check
  check (rubric is null or pg_column_size(rubric) <= 4096);

update public.bd_activity_catalog
set evaluator='authentic-review',
    steps='[
      {"id":"query","type":"text","label":"Consulta propia","min_chars":12},
      {"id":"decision","type":"text","label":"Decisión defendida","min_chars":12},
      {"id":"rejected_alternative","type":"text","label":"Alternativa descartada","min_chars":12},
      {"id":"limit","type":"text","label":"Límite concreto","min_chars":12}
    ]'::jsonb,
    config='{
      "source":"colab",
      "requires_review":true,
      "required_fields":["query","precision_at_5","defensible_results","false_positive","reason","decision","rejected_alternative","limit","trace"],
      "rubric":[
        {"id":"reproducible_result","label":"Resultado reproducible","max":2},
        {"id":"supported_decision","label":"Decisión sustentada","max":2},
        {"id":"rejected_alternative","label":"Alternativa descartada","max":2},
        {"id":"ranking_interpretation","label":"Interpretación del ranking","max":2},
        {"id":"concrete_limit","label":"Límite concreto","max":2}
      ]
    }'::jsonb,
    wall_prompt='Comparte la decisión, la alternativa descartada y el límite de tu evidencia final.',
    version=3,
    updated_at=now()
where code='bd-s09-lab9';

comment on column public.bd_evidence.rubric is
  'Revisión docente estructurada de evidencia auténtica. No contiene telemetría.';
