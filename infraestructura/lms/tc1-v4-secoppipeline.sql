-- TC1 · SECOP Data Pipeline
-- Migración compatible con entregas V3 existentes.
-- Mantiene códigos de actividad y ponderaciones; actualiza títulos, checks y rúbrica.

update public.bd_lms_sessions
set title='SECOP Data Pipeline · API, concurrencia y NoSQL',
    metadata=jsonb_build_object(
      'type','evaluation',
      'source','Cuadernos/Taller_Control_1.ipynb',
      'guide','assets/tutoriales/s08-secoppipeline.html',
      'max_score',100,
      'validator_version','2026-09-26-secoppipeline'
    )
where course_code='bigdata' and session_number=8;

update public.bd_lms_activities
set title='E1 · API SECOP, concurrencia y trazabilidad',
    points=25,
    metadata='{"checks":["E1_contrato_y_query","E1_descarga_secuencial","E1_concurrencia_equivalente","E1_trazabilidad_calidad"]}'::jsonb
where code='bd-s08-e1';

update public.bd_lms_activities
set title='E2 · Modelo documental + Atlas idempotente',
    points=25,
    metadata='{"checks":["E2_modelo_documental","E2_atlas_idempotente","E2_indices","E2_consulta_A_count","E2_consulta_B_find","E2_evidencia_atlas"]}'::jsonb
where code='bd-s08-e2';

update public.bd_lms_activities
set title='E3 · Producto analítico desde Atlas',
    metadata='{"checks":["E3_pipeline_bandeja","E3_artefacto_bandeja"]}'::jsonb
where code='bd-s08-e3';

update public.bd_lms_activities
set title='E4 · Cassandra query-first',
    metadata='{"checks":["E4_datos_cassandra","E4_modelo_query_first","E4_consulta_simulada"]}'::jsonb
where code='bd-s08-e4';

update public.bd_lms_activities
set title='E5 · Neo4j y contexto relacional',
    points=15,
    metadata='{"checks":["E5_historial_y_ancla","E5_metrica_relacional","E5_cypher","E5_subgrafo"]}'::jsonb
where code='bd-s08-e5';

update public.bd_lms_activities
set title='E6 · Decisiones, informe y paquete',
    points=10,
    metadata='{"checks":["E6_decisiones_informe","E6_paquete_reproducible"]}'::jsonb
where code='bd-s08-e6';

update public.bd_lms_activities
set metadata='{"validator_versions":["2026-09-26-secoppipeline"],"current":"2026-09-26-secoppipeline"}'::jsonb
where code='bd-s08-final';

update public.lms_assignments_v2
set title='TC1 · SECOP Data Pipeline',
    instructions='Construya una adquisición reproducible de SECOP II, compare secuencial vs ThreadPoolExecutor, documente calidad/trazabilidad, cargue Atlas de forma idempotente y produzca evidencia Cassandra/Neo4j. La entrega se registra al validar manifest_tc1.json.',
    rubric='[
      {"code":"E1","title":"API SECOP + concurrencia + trazabilidad","max":25},
      {"code":"E2","title":"Modelo documental + Atlas idempotente","max":25},
      {"code":"E3","title":"Producto analítico","max":10},
      {"code":"E4","title":"Cassandra query-first","max":15},
      {"code":"E5","title":"Neo4j y contexto relacional","max":15},
      {"code":"E6","title":"Decisiones + informe reproducible","max":10}
    ]'::jsonb,
    updated_at=now()
where code='bd-s08-control'
  and course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1);


-- Alinear competencias existentes sin cambiar sus códigos ni historial.
update public.lms_competencies_v2
set domain='Adquisición e integración',
    title='Construye una adquisición SECOP reproducible y concurrente',
    description='Diseña consultas SoQL, pagina una API real, compara adquisición secuencial y concurrente por equivalencia de datos y conserva trazabilidad/calidad.',
    updated_at=now()
where course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and code='BD-E1';

update public.lms_competencies_v2
set domain='Documental',
    title='Opera un modelo documental idempotente en MongoDB Atlas',
    description='Transforma un snapshot trazable en documentos anidados, usa upsert e índices y demuestra que la reejecución no crea duplicados.',
    updated_at=now()
where course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
  and code='BD-E2';
