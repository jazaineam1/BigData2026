-- S09 V56 · catálogo de LAB9 completamente estructurado.
-- La consulta es entrada de herramienta; las respuestas académicas son elecciones cerradas.

update public.bd_activity_catalog
set steps='[
  {"id":"query","type":"tool_text","label":"Consulta ejecutada en el buscador","min_chars":12},
  {"id":"defensible_result_1","type":"rank_position","label":"Primer resultado defendible del Top-5","min":1,"max":5},
  {"id":"defensible_result_2","type":"rank_position","label":"Segundo resultado defendible del Top-5","min":1,"max":5},
  {"id":"false_positive","type":"rank_position","label":"Falso positivo del Top-5","min":1,"max":5},
  {"id":"reason","type":"choice","label":"Lectura del ranking","options":[
    {"value":"El embedding recuperó documentos con sinónimos o términos relacionados que la búsqueda lexical no encontró.","label":"El embedding recuperó documentos con sinónimos o términos relacionados que la búsqueda lexical no encontró."},
    {"value":"El embedding trajo documentos del mismo tema general aunque no compartan el objeto contractual concreto.","label":"El embedding trajo documentos del mismo tema general aunque no compartan el objeto contractual concreto."},
    {"value":"Lexical y semántico coinciden casi por completo: el embedding no aportó documentos nuevos.","label":"Lexical y semántico coinciden casi por completo: el embedding no aportó documentos nuevos."},
    {"value":"El ranking semántico mezcla documentos relevantes con otros que solo comparten vocabulario frecuente.","label":"El ranking semántico mezcla documentos relevantes con otros que solo comparten vocabulario frecuente."}
  ]},
  {"id":"decision","type":"choice","label":"Enfoque elegido","options":[
    {"value":"Búsqueda híbrida: lexical y semántica fusionadas con RRF.","label":"Búsqueda híbrida: lexical y semántica fusionadas con RRF."},
    {"value":"Solo búsqueda semántica (embeddings).","label":"Solo búsqueda semántica (embeddings)."},
    {"value":"Solo búsqueda lexical (BM25).","label":"Solo búsqueda lexical (BM25)."},
    {"value":"Búsqueda semántica y revisión manual de los primeros resultados.","label":"Búsqueda semántica y revisión manual de los primeros resultados."}
  ]},
  {"id":"rejected_alternative","type":"choice","label":"Alternativa descartada","options":[
    {"value":"Búsqueda híbrida: lexical y semántica fusionadas con RRF.","label":"Búsqueda híbrida: lexical y semántica fusionadas con RRF."},
    {"value":"Solo búsqueda semántica (embeddings).","label":"Solo búsqueda semántica (embeddings)."},
    {"value":"Solo búsqueda lexical (BM25).","label":"Solo búsqueda lexical (BM25)."},
    {"value":"Búsqueda semántica y revisión manual de los primeros resultados.","label":"Búsqueda semántica y revisión manual de los primeros resultados."}
  ]},
  {"id":"limit","type":"choice","label":"Límite de la evidencia","options":[
    {"value":"Precision@5 mide una sola consulta y solo 5 resultados: faltan más consultas y medir recall.","label":"Precision@5 mide una sola consulta y solo 5 resultados: faltan más consultas y medir recall."},
    {"value":"Faltan juicios de relevancia de una persona experta que no haya visto el ranking antes de juzgarlo.","label":"Faltan juicios de relevancia de una persona experta que no haya visto el ranking antes de juzgarlo."},
    {"value":"El modelo de embeddings no se validó con el vocabulario contractual colombiano.","label":"El modelo de embeddings no se validó con el vocabulario contractual colombiano."},
    {"value":"Falta un ranking de referencia construido antes de ver los resultados de cada método.","label":"Falta un ranking de referencia construido antes de ver los resultados de cada método."}
  ]}
]'::jsonb,
config=coalesce(config,'{}'::jsonb)||'{"closed_academic_choices":true,"query_is_tool_input":true}'::jsonb,
wall_prompt='Evidencia final estructurada: resultados elegidos del Top-5, decisión, alternativa y límite.',
version=case when coalesce(config->>'closed_academic_choices','false')<>'true' then version+1 else version end,
updated_at=now()
where code='bd-s09-lab9'
  and coalesce(config->>'closed_academic_choices','false')<>'true';
