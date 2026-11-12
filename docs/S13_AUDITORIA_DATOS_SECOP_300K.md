# Auditoría de datos SECOP II · Sesión 13 · 300.000 filas

**Estado:** auditoría reproducible sobre los tres CSV versionados del curso; no es validación jurídica del SECOP II ni un dictamen sobre los expedientes.

## Veredicto

El ejercicio anterior demuestra que XGBoost puede entrenar un modelo entre dos trabajadores Dask, **pero no demuestra que su regresión de `precio_base` sea una herramienta apropiada para comparar presupuestos contractuales**. No se deben divulgar los errores de predicción como «contratos sospechosos», «sobreprecios», «alertas de fraude» ni lista de revisión prioritaria.

## Resultados medidos

| Indicador | Filas | Significado |
|---|---:|---|
| Filas analizadas | 300.000 | Tres CSV SECOP de 100.000 filas |
| IDs repetidos | 6.419 | Observaciones adicionales con el mismo `id_del_proceso` |
| `precio_base = 0` | 11.392 (3,797 %) | No asumir 0 válido ni faltante sin contexto |
| `precio_base < 0` | 7 | Requieren interpretación de fuente |
| Precio base 0 con `adjudicado = Sí` | 1.039 | Señal de inconsistencia contextual; no prueba error |
| Precio base 0 con valor adjudicado positivo | 934 | `precio_base` y precio adjudicado son campos diferentes |
| `conteo_de_respuestas_a_ofertas = 0` | 298.726 (99,575 %) | No se puede usar como conteo fiable de oferentes |
| Contador de ofertas 0 con estado «Seleccionado» | 183.527 | El cero no permite concluir falta de competencia |
| Contador de ofertas 0 y `adjudicado = Sí` | 27.292 | Los estados y este contador no son equivalentes |
| Contador de ofertas 0 con respuestas al procedimiento positivas | 31.609 | Son campos con funciones distintas, no sustituibles |
| Precio base 0 en «Solicitud de información a los Proveedores» | 5.544 | No todos los procesos tienen un presupuesto comparable |
| Descripciones con **posibles** pistas monetarias | 15.493 | Heurística de patrones; revisar fuga semántica caso por caso |

**Interpretación rigurosa:** «cero», «no informado», «no aplica», «fase aún no alcanzada» y «error de registro» NO son sinónimos. El archivo CSV no permite distinguir esas razones para todos los registros.

## Un error detectado en nuestro propio modelo

Los códigos de categoría llegan como `V1.80111600`: el prefijo `V1.` corresponde a la versión, y el código UNSPSC son ocho dígitos: `80111600`. Extraer los primeros dos dígitos después de eliminar todo lo no numérico daba «18»; el segmento correcto es **80**. También aparecen valores `UNSPECIFIED`, que no deben transformarse en números válidos.

El modelo se corrigió para extraer **exactamente ocho dígitos** después del prefijo opcional. Se agregó una prueba que exige `V1.80111600 → 80` y `V1.85101600 → 85`.

**Por tanto, NO comparar métricas de la versión antigua con la nueva como si fueran el mismo experimento.**

## Problema metodológico adicional: muestreo

La primera versión elegía los primeros 26.000 registros de CSV que pasaban sus filtros. Aunque algunas distribuciones marginales resulten parecidas a las del conjunto original, **eso no prueba representatividad**. El código revisado aplica muestreo por reservorio con semilla 42 sobre todo el universo válido y comprueba claves únicas, sin inventar duplicados ni reemplazar ceros.

Sigue habiendo limitaciones: las fichas pueden tener revisiones temporales, el precio base puede no ser comparable entre modalidades y el mismo texto puede contener cifras que filtren la etiqueta.

## Qué puede seguir enseñándose

- Dask Distributed con dos workers en el mismo Codespace.
- `xgboost.dask.DaskDMatrix` y `xgboost.dask.train`: **un modelo realmente entrenado con datos distribuidos**.
- Comparación de baselines, particiones, tiempo, errores, variables y exclusiones.
- Auditoría de fuentes, reglas de datos, deduplicación e incertidumbre.

**No se valida:** competencia real, corrupción, precios justos, sobrecostos, irregularidades o utilidad operativa en SECOP.

## Recomendación de rediseño científico

Para una práctica de ML con 20.000 fichas que tenga una variable objetivo mejor definida, prefiero un problema de **clasificación textual de categorías UNSPSC**, con datos y etiquetas explícitos:

1. El objetivo es el código de categoría UNSPSC declarado en la ficha (por ejemplo, segmento 80). Los códigos `UNSPECIFIED` se investigan y excluyen de la etiqueta.
2. Las entradas son la **descripción y el título** del procedimiento, sin usar el código objetivo como característica.
3. Comparar (a) frecuencia mayoritaria, (b) TF-IDF/SVD + XGBoost distribuido y (c) embeddings semánticos solo si mejoran fuera de muestra.
4. Medir **F1 macro, balanced accuracy, F1 por categoría, matriz de confusión y rendimiento por modalidad/año**. La clase mayoritaria no debe ocultar el error en categorías raras.
5. Usar una partición temporal o por grupo, no mezclar versiones del mismo proceso entre train/test.
6. Presentar casos de descripción/categoría incongruentes como **candidatos a revisión del catálogo**, nunca como fraude.

Esta tarea se acerca más a lo que un científico de datos realmente puede automatizar con SECOP: **apoyar la clasificación, el etiquetado y la búsqueda de procesos**, no tasar contratos distintos con información insuficiente.

### Pendiente para aceptar ese reemplazo

Auditar distribución de categorías válidas UNSPSC, clases con al menos 20.000 ejemplos combinados, validez de descripciones y duplicados por ID. No anunciar desempeño del clasificador hasta entrenarlo y evaluarlo.

## Cómo reproducir la auditoría

```bash
python Laboratorios/S13_Codespaces/auditar_ceros_secop.py
```

El resultado se guarda en `Laboratorios/S13_Codespaces/salidas/auditoria_ceros_secop.json` y GitHub Actions publica un artefacto temporal.

## Fuentes

- Fuente pública de SECOP II: https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-II-Procesos-de-Contrataci-n/p6dx-8zbt
- Instrucciones de Colombia Compra Eficiente para interpretar procesos y presupuestos: https://www.colombiacompra.gov.co/base-conocimiento/contratacion-directa-sin-oferta-secop-ii
- Código de la auditoría: `Laboratorios/S13_Codespaces/auditar_ceros_secop.py`
- Datasets del curso: `Cuadernos/datos/secop_chunks/secop_chunk_*.csv`
