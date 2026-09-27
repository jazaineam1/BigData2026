-- LMS V5.1 · S09 deterministic labs
-- Replaces self-report completion with server-verified deterministic answers.

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"mechanism","type":"choice","label":"¿Qué señal favorece una búsqueda lexical?","options":[
      {"value":"exact_terms","label":"Coincidencia de términos presentes en consulta y documento"},
      {"value":"semantic_meaning","label":"Parecido de significado aunque cambien las palabras"},
      {"value":"random_order","label":"Orden aleatorio de documentos"}],"hint":"La búsqueda lexical depende de los términos observables del texto."},
    {"id":"limitation","type":"choice","label":"¿Cuál es su límite principal en este caso?","options":[
      {"value":"paraphrase_gap","label":"Puede perder paráfrasis que usan vocabulario distinto"},
      {"value":"no_ranking","label":"No puede ordenar resultados"},
      {"value":"no_documents","label":"No puede buscar sobre documentos"}],"hint":"Compara “aviones militares” con “aeronaves KFIR”."}
  ]'::jsonb,
  config='{"answers":{"mechanism":"7c3eb05243aa7a2c25f53124c5d16114559ac64217ec7b06ad9375cbba507129","limitation":"b7552fc6efb389078d02999b9ec5fc753f34fff4f938b2dc49079441484a1025"},"success_feedback":"Correcto: la señal lexical premia coincidencias de términos y puede perder paráfrasis."}'::jsonb,
  wall_prompt='Compara búsqueda lexical y semántica a partir del caso.',version=2,updated_at=now()
where code='bd-s09-lab1';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"model_output","type":"choice","label":"¿Qué produce un modelo de embeddings?","options":[
      {"value":"vector","label":"Un vector numérico que representa el texto"},
      {"value":"database","label":"Una base de datos ya indexada"},
      {"value":"ranking_final","label":"El ranking final validado"}],"hint":"El modelo transforma texto; no administra por sí solo el almacenamiento."},
    {"id":"storage","type":"choice","label":"¿Dónde queda la responsabilidad de almacenar e indexar esos vectores?","options":[
      {"value":"external_index","label":"En el motor/base vectorial que los almacena e indexa"},
      {"value":"embedding_model","label":"Dentro del modelo de embeddings"},
      {"value":"browser","label":"Solo en el navegador"}],"hint":"Separa generación del vector de persistencia e índice."}
  ]'::jsonb,
  config='{"answers":{"model_output":"b0d51c58c8b9c1f458fadf16c7d375630ef51da4df81915893b05c0fa4ed8bc6","storage":"1fe07b4810fb0095863ae5db80c37b543b5584403154ce95cde4da7e17fca72e"}}'::jsonb,
  wall_prompt='Distingue modelo de embeddings, vector e índice.',version=2,updated_at=now()
where code='bd-s09-lab-e5';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"overlap_effect","type":"choice","label":"Si aumentas el overlap entre chunks, ¿qué ocurre?","options":[
      {"value":"more_redundancy","label":"Aumenta la redundancia y normalmente el costo de almacenamiento/proceso"},
      {"value":"fewer_chunks","label":"Siempre disminuye el número de chunks"},
      {"value":"no_effect","label":"No cambia nada"}],"hint":"El mismo contenido puede repetirse en fragmentos vecinos."},
    {"id":"boundary_effect","type":"choice","label":"¿Qué ventaja puede aportar ese overlap?","options":[
      {"value":"less_boundary_loss","label":"Reduce la pérdida de contexto en los límites entre fragmentos"},
      {"value":"perfect_relevance","label":"Garantiza relevancia perfecta"},
      {"value":"smaller_vectors","label":"Hace más pequeños los embeddings"}],"hint":"Piensa en una frase que cruza el límite de dos chunks."}
  ]'::jsonb,
  config='{"answers":{"overlap_effect":"7104f533b2fa37637ff344afa1fd2113b7537e680afc484ef6f1ad1976b6c3ca","boundary_effect":"ae2fd73940d54b4cb8f57eb363fb22463974547a91bf2bed67805816238cfba1"}}'::jsonb,
  wall_prompt='Relaciona overlap con redundancia y contexto.',version=2,updated_at=now()
where code='bd-s09-lab-chunk';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"meaning","type":"choice","label":"¿Cómo debes interpretar la similitud coseno?","options":[
      {"value":"similarity_not_probability","label":"Como una medida de orientación/semejanza, no como probabilidad de verdad"},
      {"value":"probability","label":"Como probabilidad de que el documento sea correcto"},
      {"value":"distance_km","label":"Como distancia física"}],"hint":"Un score de similitud no es una probabilidad calibrada."},
    {"id":"higher","type":"choice","label":"Manteniendo la misma métrica, un coseno mayor suele indicar…","options":[
      {"value":"more_aligned","label":"Vectores más alineados y potencialmente más similares"},
      {"value":"less_aligned","label":"Vectores necesariamente menos similares"},
      {"value":"same_document","label":"Que son el mismo documento"}],"hint":"Observa cómo cambia el valor al acercar las direcciones."}
  ]'::jsonb,
  config='{"answers":{"meaning":"2494262e623a60cffd8b2e98150dcfdf9579a3a621498ed18c3ad564ada8048b","higher":"1d3de83a28f5730eb626c12baa7a8d24178d428f27be773438b204e9a336a551"}}'::jsonb,
  wall_prompt='Interpreta coseno sin convertirlo en probabilidad.',version=2,updated_at=now()
where code='bd-s09-lab2';

update public.bd_activity_catalog set
  evaluator='seeded-numeric',
  steps='[{"id":"result","type":"number","label":"¿Cuántos de tus primeros 5 candidatos son claramente aeronáuticos?"},{"id":"decision","type":"choice","label":"Con ese resultado, ¿qué harías con k?","options":[{"value":"mantener","label":"Mantener k=5"},{"value":"subir","label":"Subir k para revisar más vecinos"}]}]'::jsonb,
  config='{"generator":"s09_topk_aero_count","k":5,"tolerance":0}'::jsonb,
  wall_prompt='Compara tu ranking personalizado y la decisión sobre k.',version=2,updated_at=now()
where code='bd-s09-lab3';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"paraphrase","type":"choice","label":"Para recuperar una paráfrasis sin términos exactos, ¿qué señal tiene ventaja?","options":[{"value":"semantic","label":"Semántica/vectorial"},{"value":"lexical","label":"Solo lexical exacta"},{"value":"random","label":"Aleatoria"}],"hint":"El caso cambia “aviones” por “aeronaves”."},
    {"id":"identifier","type":"choice","label":"Para un código o identificador raro que debe coincidir exactamente, ¿qué señal suele ser más directa?","options":[{"value":"lexical","label":"Lexical/BM25"},{"value":"semantic","label":"Solo semántica"},{"value":"none","label":"Ninguna búsqueda"}],"hint":"Los identificadores exactos son una fortaleza de la señal lexical."}
  ]'::jsonb,
  config='{"answers":{"paraphrase":"3784070fe3e7e3de5f0ec08eadfa10acbaa0f543916b1ab2c68f371924ff7db3","identifier":"78f3f3423b346310eb58f4add60ff80181ec4c4b83fb663a6b072d6888b6b905"}}'::jsonb,
  wall_prompt='Compara cuándo conviene señal lexical y semántica.',version=2,updated_at=now()
where code='bd-s09-lab4';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"search_type","type":"choice","label":"HNSW realiza principalmente una búsqueda…","options":[{"value":"approximate_graph","label":"Aproximada navegando un grafo de vecinos"},{"value":"full_scan","label":"Exhaustiva comparando siempre todos los vectores"},{"value":"sql_join","label":"Basada en JOIN relacional"}],"hint":"HNSW evita comparar contra todos los vectores."},
    {"id":"tradeoff","type":"choice","label":"¿Cuál es su compromiso principal?","options":[{"value":"speed_for_recall","label":"Gana velocidad/costo a cambio de poder sacrificar algo de recall"},{"value":"perfect_accuracy","label":"Garantiza recall perfecto y costo cero"},{"value":"no_index","label":"No necesita índice"}],"hint":"Aproximado no significa idéntico a una búsqueda exhaustiva."}
  ]'::jsonb,
  config='{"answers":{"search_type":"ac49bcffc9e66e962831b4ecce948a80fb6618acc1bed57ce37a866a53a70a2f","tradeoff":"4f58840375e5b881716b863cb76649881a737e559e12e0a97500aa693d5f82e1"}}'::jsonb,
  wall_prompt='Explica el compromiso velocidad/recall de HNSW.',version=2,updated_at=now()
where code='bd-s09-lab5';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"increase_candidates","type":"choice","label":"Si aumentas numCandidates manteniendo lo demás, normalmente…","options":[{"value":"more_recall_more_cost","label":"Exploras más candidatos: puede mejorar recall, pero aumenta costo/latencia"},{"value":"less_cost","label":"Siempre baja el costo y la latencia"},{"value":"same","label":"No cambia la búsqueda"}],"hint":"Más candidatos implican más trabajo de exploración."},
    {"id":"limit_role","type":"choice","label":"¿Qué controla limit?","options":[{"value":"output_count","label":"Cuántos resultados finales devuelve la etapa"},{"value":"exploration_pool","label":"Cuántos candidatos explora internamente el índice"},{"value":"vector_size","label":"La dimensión del embedding"}],"hint":"No confundas exploración con cantidad final devuelta."}
  ]'::jsonb,
  config='{"answers":{"increase_candidates":"31b00f4f555618f82400abcb68f8dc582bb375ca3ed7f6d2e5c66da3422d59b3","limit_role":"fa9ffc3238261ff1ef6ab1c73d295f4d2d1bdf4f057740907afd553c90de1ab6"}}'::jsonb,
  wall_prompt='Relaciona numCandidates con recall y costo.',version=2,updated_at=now()
where code='bd-s09-lab6';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"query_vector","type":"choice","label":"¿Qué debe contener queryVector?","options":[{"value":"query_embedding","label":"El embedding de la consulta"},{"value":"raw_text","label":"El texto crudo sin vectorizar"},{"value":"document_id","label":"Solo el ID del documento"}],"hint":"$vectorSearch compara vectores."},
    {"id":"num_candidates","type":"choice","label":"¿Qué representa numCandidates?","options":[{"value":"exploration_pool","label":"El tamaño del conjunto explorado antes del corte final"},{"value":"returned_results","label":"Solo el número final que ve el usuario"},{"value":"dimensions","label":"La dimensión del vector"}],"hint":"Es un parámetro de exploración."},
    {"id":"limit","type":"choice","label":"¿Qué representa limit?","options":[{"value":"returned_results","label":"La cantidad final de vecinos devueltos"},{"value":"exploration_pool","label":"El universo completo explorado"},{"value":"index_size","label":"El tamaño del índice"}],"hint":"Es el corte final de resultados."}
  ]'::jsonb,
  config='{"answers":{"query_vector":"b6acc99cbc1a5527141cf3d59278c30ca2e3026b4395b30d5472267a602a57fa","num_candidates":"7e066c804588072bcee205ce8b84f63266b6438a417fbfd25571a6dd64ede14f","limit":"acdeab7754c36532b80d2d6a8e3cd75db7af7333a885b285195582e09b300899"}}'::jsonb,
  wall_prompt='Distingue queryVector, numCandidates y limit.',version=2,updated_at=now()
where code='bd-s09-lab7';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"fusion","type":"choice","label":"RRF combina principalmente…","options":[{"value":"rank_positions","label":"Posiciones de ranking"},{"value":"raw_scores","label":"Scores crudos sumados directamente"},{"value":"embeddings","label":"Vectores concatenados"}],"hint":"RRF usa la posición de cada documento en cada ranking."},
    {"id":"scores","type":"choice","label":"¿Por qué no conviene sumar sin más BM25 y coseno?","options":[{"value":"do_not_sum_raw","label":"Porque sus escalas no son necesariamente comparables"},{"value":"same_scale","label":"Porque siempre están en exactamente la misma escala"},{"value":"no_numbers","label":"Porque ninguno produce números"}],"hint":"Cada mecanismo puede producir scores con escalas distintas."}
  ]'::jsonb,
  config='{"answers":{"fusion":"6de7923d8f45c7b6b42af07246b92814a9a2395bdda2283d7bfeb3d622db8e77","scores":"d43b03bf4ccd6af8c263a2bf61b210dfa65a3cc396918bcfbda9038e9d7de413"}}'::jsonb,
  wall_prompt='Explica qué fusiona RRF y por qué.',version=2,updated_at=now()
where code='bd-s09-lab8';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"precision","type":"choice","label":"Si 3 de los primeros 5 resultados son relevantes, Precision@5 es…","options":[{"value":"0.60","label":"0.60"},{"value":"0.40","label":"0.40"},{"value":"1.67","label":"1.67"}],"hint":"Precision@k = relevantes en top-k / k."},
    {"id":"meaning","type":"choice","label":"¿Qué mide Precision@k?","options":[{"value":"relevant_fraction_topk","label":"La fracción de resultados relevantes dentro de los primeros k"},{"value":"all_relevant_found","label":"Todos los relevantes existentes en el corpus"},{"value":"latency","label":"La latencia de la consulta"}],"hint":"Solo mira la calidad del conjunto recuperado en las primeras k posiciones."}
  ]'::jsonb,
  config='{"answers":{"precision":"90e683111c8a35ea92f86870185d5350d940315840e636019baa36cd37bb1dc7","meaning":"bab2c07e97ba1b6ce07f78db66981c21dcca60760647820109d419b49739029a"}}'::jsonb,
  wall_prompt='Interpreta Precision@k sobre juicios de relevancia.',version=2,updated_at=now()
where code='bd-s09-lab-eval';

update public.bd_activity_catalog set
  evaluator='choice-hash',
  steps='[
    {"id":"architecture","type":"choice","label":"Si necesitas recuperar paráfrasis y también términos/identificadores exactos, ¿qué enfoque es más defendible?","options":[{"value":"hybrid","label":"Híbrido: lexical + semántico"},{"value":"lexical_only","label":"Solo lexical siempre"},{"value":"semantic_only","label":"Solo semántico siempre"}],"hint":"Las dos señales cubren fortalezas distintas."},
    {"id":"evaluation","type":"choice","label":"¿Qué necesitas para evaluar si el ranking realmente sirve?","options":[{"value":"human_relevance","label":"Juicios humanos de relevancia sobre resultados"},{"value":"score_only","label":"Solo mirar el score más alto"},{"value":"runtime_only","label":"Solo medir tiempo de ejecución"}],"hint":"El score ordena; no sustituye el juicio de relevancia."},
    {"id":"caveat","type":"choice","label":"¿Cuál es la limitación final más importante?","options":[{"value":"retrieval_not_truth","label":"Recuperar candidatos no convierte el resultado en verdad; hay que revisar relevancia/contenido"},{"value":"top1_truth","label":"El top-1 siempre es correcto"},{"value":"no_evaluation","label":"No hace falta evaluar resultados"}],"hint":"Recuperación propone candidatos, no certifica verdad."}
  ]'::jsonb,
  config='{"answers":{"architecture":"0deac0a26c0d846d7869c23130c6346c4040904a4134bb2f40a8c206a03748ed","evaluation":"b2a2e200919a310d406d167ac4ef1cddcc0001731d9234c2efb5bcd99e3b8aba","caveat":"d1a2a25dde3b7e965b5b3843b20fce7bde013ce6767c147e9c31e3f65c5c41f8"}}'::jsonb,
  wall_prompt='Cierra el caso con arquitectura, evaluación y límite.',version=2,updated_at=now()
where code='bd-s09-lab9';
