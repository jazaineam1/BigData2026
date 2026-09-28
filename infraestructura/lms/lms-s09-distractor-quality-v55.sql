-- S09 V55 · distractores plausibles en las autocomprobaciones de choice-hash.
--
-- Origen del contenido: PR #91 (fix/s09-distractor-quality, migración v13),
-- portado de forma selectiva sobre main. Se numera v55 porque main ya usa v13
-- (lms-realtime-legacy-cleanup-v13), v14 (lms-s09-remove-confidence-v14), v52 y
-- V54-A; v55 es el siguiente libre y queda después de todas ellas.
--
-- QUÉ HACE
--   Reemplaza la ETIQUETA (label) de 20 opciones incorrectas de las
--   autocomprobaciones bd-s09-lab1, lab2, lab-e5, lab-chunk, lab4, lab5, lab6,
--   lab7 y lab8 por errores plausibles que el grupo comete de verdad. La
--   autocomprobación sigue siendo formativa; se mejora su poder diagnóstico.
--
-- IDEMPOTENCIA (se puede ejecutar N veces)
--   Una etiqueta se cambia SOLO si la opción de esa posición conserva el value
--   esperado Y su etiqueta actual es exactamente la antigua. En la segunda
--   ejecución ninguna condición se cumple, steps no cambia y no se toca ninguna
--   fila. La versión sube en 1 por actividad y solo si esa ejecución cambió
--   algo (no una vez por etiqueta, no en las re-ejecuciones).
--
-- QUÉ NO HACE
--   * No toca los value, config.answers (hashes), evaluator, wall_prompt, hint
--     ni el enunciado: las respuestas ya enviadas y el evaluador siguen válidos.
--   * No toca ninguna fila de bd_evidence / progreso ni datos de estudiantes.
--   * No sobrescribe una etiqueta editada a mano después de V51 (si la etiqueta
--     actual no es la antigua esperada, esa opción se deja como está).
--   * No cambia dos opciones que quedan PENDIENTES de decisión docente:
--     bd-s09-lab8 paso 0 opción 2 (value 'embeddings') y bd-s09-lab4 paso 1
--     opción 2 (value 'none'). Conservan su etiqueta de V51.
--   * No toca S07.

do $$
declare
  a record;
  m record;
  v_new jsonb;
  v_path text[];
begin
  for a in
    select c.code, c.steps
    from public.bd_activity_catalog c
    where c.code in (
      'bd-s09-lab1','bd-s09-lab2','bd-s09-lab-e5','bd-s09-lab-chunk',
      'bd-s09-lab4','bd-s09-lab5','bd-s09-lab6','bd-s09-lab7','bd-s09-lab8'
    )
    for update
  loop
    v_new := a.steps;

    for m in
      select t.step_idx, t.opt_idx, t.opt_value, t.old_label, t.new_label
      from (values
        ('bd-s09-lab1',     0, 2, 'random_order',      'Orden aleatorio de documentos',          'Coincidencia literal de la frase completa, sin ponderar términos'),
        ('bd-s09-lab1',     1, 1, 'no_ranking',        'No puede ordenar resultados',            'Solo puede ordenar si la consulta coincide con el título completo'),
        ('bd-s09-lab1',     1, 2, 'no_documents',      'No puede buscar sobre documentos',       'Requiere documentos de longitud similar para poder comparar'),
        ('bd-s09-lab2',     0, 2, 'distance_km',       'Como distancia física',                  'Como una puntuación absoluta comparable entre modelos de embeddings distintos'),
        ('bd-s09-lab2',     1, 2, 'same_document',     'Que son el mismo documento',             'Que ambos textos expresan exactamente la misma intención'),
        ('bd-s09-lab-e5',   0, 2, 'ranking_final',     'El ranking final validado',              'Un ranking de candidatos ya ordenado por relevancia'),
        ('bd-s09-lab-e5',   1, 2, 'browser',           'Solo en el navegador',                   'En la memoria del modelo mientras permanece desplegado'),
        ('bd-s09-lab-chunk',0, 2, 'no_effect',         'No cambia nada',                         'Mejora contexto sin aumentar duplicación ni costo de proceso'),
        ('bd-s09-lab-chunk',1, 1, 'perfect_relevance', 'Garantiza relevancia perfecta',          'Evita por completo los falsos positivos en los límites de fragmento'),
        ('bd-s09-lab4',     0, 2, 'random',            'Aleatoria',                              'Lexical/BM25 aumentando el peso de términos raros, aunque no haya equivalentes textuales'),
        ('bd-s09-lab5',     0, 2, 'sql_join',          'Basada en JOIN relacional',              'Aproximada sobre una muestra aleatoria del corpus'),
        ('bd-s09-lab5',     1, 1, 'perfect_accuracy',  'Garantiza recall perfecto y costo cero', 'Mantiene siempre el mismo recall que una búsqueda exacta si el grafo está bien construido'),
        ('bd-s09-lab5',     1, 2, 'no_index',          'No necesita índice',                     'Reduce costo principalmente porque evita mantener estructuras auxiliares de índice'),
        ('bd-s09-lab6',     0, 1, 'less_cost',         'Siempre baja el costo y la latencia',    'Explora más candidatos, pero la latencia suele bajar porque el ranking se estabiliza'),
        ('bd-s09-lab6',     0, 2, 'same',              'No cambia la búsqueda',                  'Solo cambia la cantidad final devuelta; el trabajo interno permanece igual'),
        ('bd-s09-lab6',     1, 2, 'vector_size',       'La dimensión del embedding',             'El máximo de candidatos que el índice puede explorar antes de ordenar'),
        ('bd-s09-lab7',     0, 2, 'document_id',       'Solo el ID del documento',               'El vector de un documento de referencia elegido manualmente'),
        ('bd-s09-lab7',     1, 2, 'dimensions',        'La dimensión del vector',                'La cantidad de vecinos que quedan después del corte final'),
        ('bd-s09-lab7',     2, 2, 'index_size',        'El tamaño del índice',                   'El número de candidatos que se exploran antes del ranking final'),
        ('bd-s09-lab8',     1, 2, 'no_numbers',        'Porque ninguno produce números',         'Porque el coseno siempre domina numéricamente al score BM25')
      ) as t(code, step_idx, opt_idx, opt_value, old_label, new_label)
      where t.code = a.code
    loop
      v_path := array[m.step_idx::text, 'options', m.opt_idx::text];
      if (v_new #>> (v_path || 'value'::text)) = m.opt_value
         and (v_new #>> (v_path || 'label'::text)) = m.old_label then
        v_new := jsonb_set(v_new, v_path || 'label'::text, to_jsonb(m.new_label));
      end if;
    end loop;

    if v_new is distinct from a.steps then
      update public.bd_activity_catalog
      set steps = v_new,
          version = version + 1,
          updated_at = now()
      where code = a.code;
    end if;
  end loop;
end
$$;
