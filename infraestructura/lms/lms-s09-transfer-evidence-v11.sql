-- S09 · evidencia de transferencia en LAB 3, 4 y 8
-- Las autocomprobaciones D1–D5 siguen siendo formativas; estos LAB producen
-- evidencia corta revisable por docente. LAB9 continúa como evidencia final fuerte.

update public.bd_activity_catalog
set evaluator='authentic-review',
    steps='[
      {"id":"result","type":"number","label":"Resultado propio · candidatos aeronáuticos en tu Top-5"},
      {"id":"decision","type":"choice","label":"Decisión sobre k","options":[
        {"value":"mantener","label":"Mantener k=5"},
        {"value":"subir","label":"Subir k para revisar más vecinos"}
      ]},
      {"id":"rejected_alternative","type":"text","label":"Alternativa descartada y por qué","min_chars":12},
      {"id":"limit","type":"text","label":"Límite concreto de esta conclusión","min_chars":12}
    ]'::jsonb,
    config='{
      "source":"presentation",
      "generator":"s09_topk_aero_count",
      "k":5,
      "requires_review":true,
      "required_fields":["result","decision","rejected_alternative","limit"],
      "rubric":[
        {"id":"reproducible_result","label":"Resultado reproducible","max":2},
        {"id":"supported_decision","label":"Decisión sustentada","max":2},
        {"id":"rejected_alternative","label":"Alternativa descartada","max":2},
        {"id":"concrete_limit","label":"Límite concreto","max":2}
      ]
    }'::jsonb,
    wall_prompt='Comparte tu conteo Top-5, la decisión sobre k, la alternativa descartada y un límite.',
    version=4,
    updated_at=now()
where code='bd-s09-lab3';

update public.bd_activity_catalog
set evaluator='authentic-review',
    steps='[
      {"id":"query_case","type":"choice","label":"Caso comparado","readonly":true,"options":[
        {"value":"aviones","label":"reparación de aviones militares"},
        {"value":"oracle","label":"licencia Oracle"},
        {"value":"educacion","label":"plataforma educativa virtual"}
      ]},
      {"id":"observed_result","type":"text","label":"Diferencia concreta que observaste entre los rankings","min_chars":12},
      {"id":"decision","type":"choice","label":"Mecanismo que defenderías para este caso","options":[
        {"value":"lexical","label":"Lexical / BM25"},
        {"value":"semantic","label":"Semántico / vectorial"},
        {"value":"hybrid","label":"Híbrido"}
      ]},
      {"id":"rejected_alternative","type":"text","label":"Alternativa descartada y por qué","min_chars":12},
      {"id":"limit","type":"text","label":"Límite concreto de la comparación","min_chars":12}
    ]'::jsonb,
    config='{
      "source":"presentation",
      "requires_review":true,
      "required_fields":["query_case","observed_result","decision","rejected_alternative","limit"],
      "rubric":[
        {"id":"observed_result","label":"Resultado observado","max":2},
        {"id":"supported_decision","label":"Decisión sustentada","max":2},
        {"id":"rejected_alternative","label":"Alternativa descartada","max":2},
        {"id":"concrete_limit","label":"Límite concreto","max":2}
      ]
    }'::jsonb,
    wall_prompt='Comparte qué cambió entre rankings, qué mecanismo defenderías, cuál descartaste y qué límite encontraste.',
    version=4,
    updated_at=now()
where code='bd-s09-lab4';

update public.bd_activity_catalog
set evaluator='authentic-review',
    steps='[
      {"id":"document","type":"choice","label":"Documento inspeccionado","readonly":true,"options":[
        {"value":"D8","label":"D8"},{"value":"D3","label":"D3"},{"value":"D5","label":"D5"},{"value":"D1","label":"D1"}
      ]},
      {"id":"rank_constant","type":"number","label":"rank_constant usado","readonly":true},
      {"id":"rrf_score","type":"number","label":"RRF calculado","readonly":true,"step":"0.00001"},
      {"id":"decision","type":"text","label":"Decisión que tomarías con la fusión","min_chars":12},
      {"id":"rejected_alternative","type":"text","label":"Alternativa descartada y por qué","min_chars":12},
      {"id":"limit","type":"text","label":"Límite concreto de RRF en este caso","min_chars":12}
    ]'::jsonb,
    config='{
      "source":"presentation",
      "generator":"s09_rrf_demo",
      "requires_review":true,
      "required_fields":["document","rank_constant","rrf_score","decision","rejected_alternative","limit"],
      "rubric":[
        {"id":"reproducible_result","label":"Resultado reproducible","max":2},
        {"id":"supported_decision","label":"Decisión sustentada","max":2},
        {"id":"rejected_alternative","label":"Alternativa descartada","max":2},
        {"id":"ranking_interpretation","label":"Interpretación de la fusión","max":2},
        {"id":"concrete_limit","label":"Límite concreto","max":2}
      ]
    }'::jsonb,
    wall_prompt='Comparte el resultado RRF, la decisión, la alternativa descartada y un límite de la fusión.',
    version=4,
    updated_at=now()
where code='bd-s09-lab8';

comment on column public.bd_activity_catalog.evaluator is
  'choice-hash = autocomprobación; authentic-review = evidencia de transferencia revisable; otras estrategias conservan su contrato específico.';
