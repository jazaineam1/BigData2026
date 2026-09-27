-- S09 V13 · distractores plausibles sin cambiar los values ni los hashes.
-- La autocomprobación sigue siendo formativa; se mejora su poder diagnóstico.

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(
                jsonb_set(steps,'{0,options,2,label}',to_jsonb('Coincidencia literal de la frase completa, sin ponderar términos'::text)),
                '{1,options,1,label}',to_jsonb('Solo puede ordenar si la consulta coincide con el título completo'::text)
              ),
              '{1,options,2,label}',to_jsonb('Requiere documentos de longitud similar para poder comparar'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab1';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(steps,'{0,options,2,label}',to_jsonb('Como una puntuación absoluta comparable entre modelos de embeddings distintos'::text)),
              '{1,options,2,label}',to_jsonb('Que ambos textos expresan exactamente la misma intención'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab2';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(steps,'{1,options,2,label}',to_jsonb('En la memoria del modelo mientras permanece desplegado'::text)),
              '{0,options,2,label}',to_jsonb('Un ranking de candidatos ya ordenado por relevancia'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab-e5';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(steps,'{0,options,2,label}',to_jsonb('Mejora contexto sin aumentar duplicación ni costo de proceso'::text)),
              '{1,options,1,label}',to_jsonb('Evita por completo los falsos positivos en los límites de fragmento'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab-chunk';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(steps,'{0,options,2,label}',to_jsonb('Lexical/BM25 aumentando el peso de términos raros, aunque no haya equivalentes textuales'::text)),
              '{1,options,2,label}',to_jsonb('RRF sin incorporar una señal lexical exacta'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab4';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(
                jsonb_set(steps,'{0,options,2,label}',to_jsonb('Aproximada sobre una muestra aleatoria del corpus'::text)),
                '{1,options,1,label}',to_jsonb('Mantiene siempre el mismo recall que una búsqueda exacta si el grafo está bien construido'::text)
              ),
              '{1,options,2,label}',to_jsonb('Reduce costo principalmente porque evita mantener estructuras auxiliares de índice'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab5';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(
                jsonb_set(steps,'{0,options,1,label}',to_jsonb('Explora más candidatos, pero la latencia suele bajar porque el ranking se estabiliza'::text)),
                '{0,options,2,label}',to_jsonb('Solo cambia la cantidad final devuelta; el trabajo interno permanece igual'::text)
              ),
              '{1,options,2,label}',to_jsonb('El máximo de candidatos que el índice puede explorar antes de ordenar'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab6';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(
                jsonb_set(steps,'{0,options,2,label}',to_jsonb('El vector de un documento de referencia elegido manualmente'::text)),
                '{1,options,2,label}',to_jsonb('La cantidad de vecinos que quedan después del corte final'::text)
              ),
              '{2,options,2,label}',to_jsonb('El número de candidatos que se exploran antes del ranking final'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab7';

update public.bd_activity_catalog
set steps = jsonb_set(
              jsonb_set(steps,'{0,options,2,label}',to_jsonb('Scores normalizados de ambos mecanismos antes de sumarlos'::text)),
              '{1,options,2,label}',to_jsonb('Porque el coseno siempre domina numéricamente al score BM25'::text)
            ),
    version=version+1,updated_at=now()
where code='bd-s09-lab8';
