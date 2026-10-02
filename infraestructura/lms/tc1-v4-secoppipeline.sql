-- TC1 · Compras Claras · un caso, tres modelos
-- Migración del esquema actual del TC1.
-- Mantiene códigos de actividad e historial del LMS; actualiza títulos, pesos, checks y rúbrica.

update public.bd_lms_sessions
set title='Compras Claras · un caso, tres modelos · API, concurrencia y NoSQL',
    metadata=jsonb_build_object(
      'type','evaluation',
      'source','Cuadernos/Taller_Control_1.ipynb',
      'reference','assets/tutoriales/s08-secoppipeline.html',
      'max_score',100,
      'estimated_minutes',360,
      'work_mode','class_and_home',
      'group_assessment',true,
      'validator_version','2026-10-01-tc1-native-v8'
    )
where course_code='bigdata' and session_number=8;

update public.bd_lms_activities
set title='E1 · Snapshot SECOP reproducible',
    points=15,
    metadata='{"checks":["Contrato de datos","Secuencial = concurrente","Cache íntegro","RAW reutilizable y población relacional"]}'::jsonb
where code='bd-s08-e1';

update public.bd_lms_activities
set title='E2 · MongoDB Atlas · priorización',
    points=30,
    metadata='{"checks":["Modelo documental preparado","Pipeline real de Atlas","Resultado de priorización Atlas","Pipeline guardado"]}'::jsonb
where code='bd-s08-e2';

update public.bd_lms_activities
set title='E3 · Astra/Cassandra · consulta query-first',
    points=20,
    metadata='{"checks":["Diseño Cassandra query-first","Top 5 de CQL Console"]}'::jsonb
where code='bd-s08-e3';

update public.bd_lms_activities
set title='E4 · Neo4j Aura · contexto relacional',
    points=25,
    metadata='{"checks":["Consulta Cypher relacional","Resultado de Aura Query","Subgrafo cargable de la entidad ancla"]}'::jsonb
where code='bd-s08-e4';

update public.bd_lms_activities
set title='E5 · Integración y entrega',
    points=10,
    metadata='{"checks":["Decisiones de modelo","Seguridad de la entrega"]}'::jsonb
where code='bd-s08-e5';

update public.bd_lms_activities
set title='V8 · etapa histórica sin puntaje',
    points=0,
    metadata='{"checks":[]}'::jsonb
where code='bd-s08-e6';

update public.bd_lms_activities
set metadata='{"validator_versions":["2026-10-01-tc1-native-v8"],"current":"2026-10-01-tc1-native-v8"}'::jsonb
where code='bd-s08-final';

update public.lms_assignments_v2
set title='TC1 · Compras Claras · un caso, tres modelos',
    instructions='Construya un único expediente SECOP: prepare un snapshot reproducible en Colab y resuelva tres preguntas profesionales en MongoDB Atlas Data Explorer/Aggregations, Astra CQL Console y Neo4j Aura Query. Colab prepara y valida; los motores se usan en sus interfaces nativas. El LMS no es canal de entrega: la entrega oficial se realiza mediante Google Drive + correo institucional al docente.',
    due_at='2026-10-17T23:59:59-05:00'::timestamptz,
    rubric='[
      {"code":"E1","title":"Snapshot SECOP reproducible","max":15},
      {"code":"E2","title":"MongoDB Atlas · Data Explorer/Aggregations","max":30},
      {"code":"E3","title":"Astra/Cassandra · CQL Console","max":20},
      {"code":"E4","title":"Neo4j Aura · Aura Query/Cypher","max":25},
      {"code":"E5","title":"Integración y entrega","max":10}
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


-- TC1 se entrega y califica por equipo.
insert into public.lms_assignment_group_settings_v2(
  assignment_id,enabled,peer_review_enabled,reviews_per_student,peer_rubric,anonymous_peer_review,updated_at
)
select id,true,false,1,'[]'::jsonb,false,now()
from public.lms_assignments_v2
where code='bd-s08-control'
  and course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1)
on conflict (assignment_id) do update
set enabled=true,
    peer_review_enabled=false,
    reviews_per_student=1,
    peer_rubric='[]'::jsonb,
    anonymous_peer_review=false,
    updated_at=now();

update public.lms_assignments_v2
set instructions='Proyecto grupal. Entregables: notebook ejecutado, TC1_<pareja>.zip y manifest_tc1.json en Google Drive. Un solo integrante envía el enlace por correo institucional a jzaineam@ucentral.edu.co y copia a su compañero. GitHub es opcional y no reemplaza Drive + correo. Fecha máxima: 17 de octubre de 2026, 11:59 p. m. hora de Bogotá. El LMS no se usa para entregar.',
    due_at='2026-10-17T23:59:59-05:00'::timestamptz,
    updated_at=now()
where code='bd-s08-control'
  and course_run_id=(select id from public.lms_course_runs where code='bigdata-2026-2' limit 1);
