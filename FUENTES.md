# Fuentes del laboratorio: procedencia y cautelas

## Fotografías del periódico

Se incluyen **cuatro imágenes existentes** de `Datos/S10_Eltiempo_fotos/raw` del repositorio principal, sin alterar los blobs originales:

- `eltiempo_001.jpg`: fotografía sanitaria; no adecuada para OCR textual.
- `eltiempo_006.webp`: taquillas y anuncios; adecuada para OCR de letreros.
- `eltiempo_009.webp`: viviendas en una ladera; consulta visual.
- `eltiempo_023.webp`: logotipo de una lotería; combina texto y escena.

**Procedencia:** corpus histórico de fotografías de El Tiempo en `BigData2026`. Los metadatos de crédito, noticia y autorización específica de estas 30 imágenes **no están contrastados por archivo**; no asumas licencias abiertas. La existencia en un repo público no equivale a permiso para redistribuir o hacer minería sin restricciones.

**No son el mismo inventario** que `Datos/s10_imagenes_reales`, que cuenta con 32 imágenes, `inputs.json` y créditos separados. No inventes relaciones.

## Documentos SECOP

Se incluyen dos PNG originales de **primera página** procedentes de `Datos/S10_secop_acta/raw`:
- `secop_acta_728490281_pagina1.png`
- `secop_acta_728704921_pagina1.png`

Estos archivos pueden contener nombres, identificaciones o datos financieros de personas. Son para discusión en un entorno de práctica controlado. **No publiques el OCR completo** ni capturas con datos personales innecesarios. En el notebook, la revisión se centra en total, descuentos y neto. Las cifras del primer ejemplo se validaron visualmente en la primera página, pero **no confirman autenticidad de la transacción**.

## Audio real con licencia

- **PolyAI MINDS-14, es-ES**, voz humana, audios de atención bancaria.
- Licencia declarada: **CC BY 4.0**.
- Archivo de fuente: https://huggingface.co/datasets/PolyAI/minds14/resolve/main/es-ES/train-00000-of-00001.parquet
- SHA-256 del Parquet oficial verificado en la preparación S10: `989bf2f90676a5eb5852fe785a03b1d9b97763e0febbd0fd0a3f489afd83badf`.

Los WAV se extraen en ejecución dentro de la carpeta ignorada `datos/raw`. El audio **no corresponde a fotos ni noticias de El Tiempo**. En informes atribuye la fuente y la licencia.

## Separación de modalidades

No unas una fotografía con un audio porque ambos estén dentro del mismo proyecto. Necesitas IDs documentales compartidos, metadatos y un vínculo verificable. Los embeddings solo ayudan a recuperar candidatos similares, no a justificar una relación causal ni histórica.

## Corpus ampliado para S11

El kit actual conserva **62 fotografías originales** de dos conjuntos (30 de El Tiempo sin crédito individual contrastado y 32 del inventario con ficha), **30 actas SECOP** con PDF completo y la primera página PNG, y permite preparar **30 voces reales** mediante selección reproducible por rondas de intenciones de MINDS-14 es-ES. Los WAV no se agregan como archivos binarios al repositorio: se descargan desde su fuente con comprobación SHA-256 y se guardan en directorios ignorados por Git.

La aplicación **visor_fuentes.py** permite examinar visualmente cada archivo, y el cuaderno **02_lotes_122_fuentes.ipynb** permite analizarlos con código Python escrito por estudiantes. Las vistas PNG no representan documentos extra: el inventario documental es de 30 actas.
