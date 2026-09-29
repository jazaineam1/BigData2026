-- S10 · ETL multimodal: imágenes, audio y video
-- Publicación LMS idempotente. Dos recursos visibles: presentación + cuaderno.
-- La evidencia académica se produce en el cuaderno; no se habilitan respuestas abiertas.

insert into public.bd_lms_sessions
(course_code,session_number,title,path,position,required,metadata)
values (
  'bigdata',10,
  'ETL multimodal: de imágenes, audio y video a datos trazables',
  'session.html?s=10',10,true,
  '{
    "type":"learning",
    "topic":"multimodal-etl",
    "estimated_minutes":180,
    "graded":false,
    "canonical_module":true,
    "visible_resources":2,
    "class_date":"2026-10-15",
    "class_kind":"learning",
    "class_timezone":"America/Bogota",
    "class_time_local":"18:00",
    "outcomes":[
      "Distinguir noticia, asset, RAW, metadata, derived asset y manifest",
      "Inspeccionar imagen, audio y video antes de transformarlos",
      "Aplicar SHA-256, canonicalización y sampling con reglas reproducibles",
      "Construir y depurar un manifest mediante quality gates",
      "Demostrar dominio en ocho desafíos y tres LAB verificables"
    ]
  }'::jsonb
)
on conflict (course_code,session_number) do update set
  title=excluded.title,
  path=excluded.path,
  position=excluded.position,
  required=excluded.required,
  metadata=excluded.metadata;

insert into public.bd_lms_activities
(code,course_code,session_number,title,kind,points,position,required,metadata)
values
('bd-s10-presentation','bigdata',10,'Recurso · Presentación-laboratorio S10','resource',0,1,true,'{"resource_type":"presentation","formative":true,"completion_rule":"visit"}'::jsonb),
('bd-s10-notebook','bigdata',10,'Recurso · Cuaderno Colab S10','resource',0,2,true,'{"resource_type":"notebook","formative":true,"completion_rule":"visit"}'::jsonb),
('bd-s10-c1','bigdata',10,'D1 · Grano noticia → asset','checkpoint',1,3,true,'{"slide":3,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c2','bigdata',10,'D2 · RAW, metadata y derived','checkpoint',1,4,true,'{"slide":8,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c3','bigdata',10,'D3 · Orden del pipeline','checkpoint',1,5,true,'{"slide":11,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c4','bigdata',10,'D4 · Qué demuestra el hash','checkpoint',1,6,true,'{"slide":14,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c5','bigdata',10,'D5 · Container, codec y stream','checkpoint',1,7,true,'{"slide":18,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c6','bigdata',10,'D6 · Canonicalización de audio','checkpoint',1,8,true,'{"slide":22,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c7','bigdata',10,'D7 · Sampling temporal','checkpoint',1,9,true,'{"slide":28,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-c8','bigdata',10,'D8 · Quality gates','checkpoint',1,10,true,'{"slide":33,"formative":true,"completion_rule":"mastery"}'::jsonb),
('bd-s10-lab-image','bigdata',10,'LAB 1 · Imagen real El Tiempo','lab',0,11,false,'{"slide":19,"formative":true,"completion_rule":"evidence"}'::jsonb),
('bd-s10-lab-audio','bigdata',10,'LAB 2 · Audio canónico','lab',0,12,false,'{"slide":23,"formative":true,"completion_rule":"evidence"}'::jsonb),
('bd-s10-lab-video','bigdata',10,'LAB 3 · Video y sampling','lab',0,13,false,'{"slide":29,"formative":true,"completion_rule":"evidence"}'::jsonb)
on conflict (code) do update set
  course_code=excluded.course_code,session_number=excluded.session_number,title=excluded.title,kind=excluded.kind,
  points=excluded.points,position=excluded.position,required=excluded.required,metadata=excluded.metadata;

insert into public.bd_lms_activity_keys(activity_code,session_number,answer_hash,hint)
values
('bd-s10-c1',10,'6edb2e96de687a310049a542bdd5ffcafa7e4fd66db058acde09d6a8b8390e6d','Cuenta archivos procesables, no modalidades ni noticias.'),
('bd-s10-c2',10,'ebb031520306d7f719f398ee120dcf2e5132194b1add303c99f4b88c1ede9001','El RAW entra; metadata describe; derived nace del RAW.'),
('bd-s10-c3',10,'1830ab2e9b890df57e2823c4665aef9ec4ec1796f2d501d7c96942f9f7ddcea9','Identifica e inspecciona antes de transformar.'),
('bd-s10-c4',10,'af484f06684f480191ebb363e64c1dde0c382d70d19448c2524f7237cf9dff49','SHA-256 responde identidad exacta de bytes, no significado.'),
('bd-s10-c5',10,'1d9d3114434666b836fe2d13dde5436ef3fb8d8cd8c1e0f54e0d637d2c649c9c','MP4 organiza streams; H.264 y AAC codifican señales.'),
('bd-s10-c6',10,'0e001199cea558cc9b85276eebbd8f4e7d8d2103d6576d02ca18be25c88796dd','-ac controla canales y -ar sample rate.'),
('bd-s10-c7',10,'82c1f8f954a321d3a77877bc78a5a56640ee60ffff78b2179516a7d5c2699579','Divide duración entre el máximo de frames.'),
('bd-s10-c8',10,'bb4847f195eccb64e9d5bd6ccfdc8561246da3688d036be4af588b64b76ecf16','Falta identidad y el conteo de frames viola el límite.')
on conflict(activity_code) do update set session_number=excluded.session_number,answer_hash=excluded.answer_hash,hint=excluded.hint,updated_at=now();

insert into public.bd_activity_catalog(code,evaluator,steps,config,competency_code,seeded,wall_prompt,version,updated_at)
values
('bd-s10-lab-image','choice-hash',
 '[{"id":"origin_declared","type":"choice","options":[{"value":"si","label":"Sí"},{"value":"no","label":"No"}],"hint":"El valor puede ser real o fallback; lo obligatorio es declararlo."},{"id":"sha_len","type":"choice","options":[{"value":"64","label":"64"},{"value":"32","label":"32"}],"hint":"SHA-256 en hexadecimal tiene 64 caracteres."},{"id":"raw_preserved","type":"choice","options":[{"value":"si","label":"Sí"},{"value":"no","label":"No"}],"hint":"El thumbnail no debe sobrescribir RAW."}]'::jsonb,
 '{"answers":{"origin_declared":"97a62ad21d79c01cceb7767952acec4fec86bfe909b06e5f3f6963365cf91ab8","sha_len":"a68b412c4282555f15546cf6e1fc42893b7e07f271557ceb021821098dd66c1b","raw_preserved":"97a62ad21d79c01cceb7767952acec4fec86bfe909b06e5f3f6963365cf91ab8"},"success_feedback":"Correcto: identidad y preservación RAW verificadas."}'::jsonb,
 'S10-ETL-IMAGE',false,'Imagen: origen, hash y preservación RAW.',1,now()),
('bd-s10-lab-audio','choice-hash',
 '[{"id":"sample_rate","type":"choice","options":[{"value":"16000","label":"16000"},{"value":"44100","label":"44100"}],"hint":"Revisa el ffprobe del derived."},{"id":"channels","type":"choice","options":[{"value":"1","label":"1"},{"value":"2","label":"2"}],"hint":"El objetivo es mono."},{"id":"hash_relation","type":"choice","options":[{"value":"distinto","label":"Distinto"},{"value":"igual","label":"Igual"}],"hint":"Una transformación intencional cambia bytes."}]'::jsonb,
 '{"answers":{"sample_rate":"2570901c76653e578fecf066b5fc3fa1619f1a051e928e39797bab1b1342bf40","channels":"6b86b273ff34fce19d6b804eff5a3f5747ada4eaa22f1d49c01e52ddb7875b4b","hash_relation":"b72802bda9ff01bc0a8f16b03d058fa5aa1c687b9c375b5c85c0e0b204f46e19"},"success_feedback":"Correcto: audio canónico 16 kHz mono y derived distinto del RAW."}'::jsonb,
 'S10-ETL-AUDIO',false,'Audio: interfaz canónica y verificación posterior.',1,now()),
('bd-s10-lab-video','choice-hash',
 '[{"id":"streams","type":"choice","options":[{"value":"video_audio","label":"video + audio"},{"value":"solo_video","label":"solo video"}],"hint":"ffprobe debe mostrar ambos streams en el fixture."},{"id":"within_limit","type":"choice","options":[{"value":"si","label":"Sí"},{"value":"no","label":"No"}],"hint":"Comprueba n_frames <= MAX_FRAMES."},{"id":"frame_count","type":"choice","options":[{"value":"8_o_menos","label":"8 o menos"},{"value":"mas_de_8","label":"más de 8"}],"hint":"Con MAX_FRAMES=8 el resultado debe respetar el límite."}]'::jsonb,
 '{"answers":{"streams":"2f10a30d42279b4ca50dfedb1e05ccb40c95e9a061ce022c93f16d15e68f8367","within_limit":"97a62ad21d79c01cceb7767952acec4fec86bfe909b06e5f3f6963365cf91ab8","frame_count":"18671ee17034f14e795cc314c1dcd02297904e28477c8da035410b2a12426f13"},"success_feedback":"Correcto: streams y sampling cumplen el contrato."}'::jsonb,
 'S10-ETL-VIDEO',false,'Video: streams y límite de sampling.',1,now())
on conflict(code) do update set evaluator=excluded.evaluator,steps=excluded.steps,config=excluded.config,
 competency_code=excluded.competency_code,seeded=excluded.seeded,wall_prompt=excluded.wall_prompt,
 version=excluded.version,updated_at=now();

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
insert into public.lms_run_sessions_v2
(course_run_id,session_number,title,summary,status,path,starts_at,position,metadata,published_at,updated_at)
select
  id,10,
  'ETL multimodal: de imágenes, audio y video a datos trazables',
  'Presentación-laboratorio multimodal al estilo S07: caso real El Tiempo, S10 Live, ocho desafíos, simuladores, tres LAB verificables, manifest y quality gates.',
  'visible',
  'session.html?s=10',
  '2026-10-15 23:00:00+00',
  10,
  '{
    "module_kind":"learning",
    "graded":false,
    "tracked":true,
    "class_date":"2026-10-15",
    "class_kind":"learning",
    "class_timezone":"America/Bogota",
    "class_time_local":"18:00",
    "estimated_minutes":180,
    "outcomes":[
      "Distinguir noticia, asset, RAW, metadata, derived asset y manifest",
      "Inspeccionar imagen, audio y video antes de transformarlos",
      "Aplicar SHA-256, canonicalización y sampling con reglas reproducibles",
      "Construir y depurar un manifest mediante quality gates",
      "Demostrar dominio en ocho desafíos y tres LAB verificables"
    ]
  }'::jsonb,
  now(),now()
from run
on conflict (course_run_id,session_number) do update set
  title=excluded.title,
  summary=excluded.summary,
  status=excluded.status,
  path=excluded.path,
  starts_at=excluded.starts_at,
  position=excluded.position,
  metadata=excluded.metadata,
  published_at=coalesce(public.lms_run_sessions_v2.published_at,now()),
  updated_at=now();

delete from public.lms_run_resources_v2
where course_run_id=(
  select id from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
and session_number=10;

with run as (
  select id
  from public.lms_course_runs
  where code='bigdata-2026-2' and course_code='bigdata'
  limit 1
)
insert into public.lms_run_resources_v2
(course_run_id,session_number,resource_type,title,summary,url,position,visible,metadata)
select
  id,10,'presentation',
  'Presentación S10 · ETL multimedia + laboratorio',
  'Recurso principal: definiciones, S10 Live, ocho desafíos, siete herramientas de simulación y tres LAB encadenados con el cuaderno.',
  '../Presentaciones/s10-etl-multimedia.html#s1',
  1,true,
  '{"tracked_activity":"bd-s10-presentation"}'::jsonb
from run
union all
select
  id,10,'notebook',
  'Cuaderno S10 · ETL multimedia',
  'Colab reproducible sobre El Tiempo con RAW, SHA-256, ffprobe/FFmpeg, Pillow, derivados, JSONL, Parquet y manifest.',
  'https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/10_ETL_Multimedia.ipynb',
  2,true,
  '{"tracked_activity":"bd-s10-notebook"}'::jsonb
from run;
