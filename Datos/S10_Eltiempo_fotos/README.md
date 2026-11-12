# El Tiempo · fotografías de práctica (S10–S11)

**Estructura corregida el 11 de noviembre de 2026.**

Esta carpeta contiene **30 fotografías originales** (`raw/`) y **30 variantes PNG con sufijo `_ocr`** (`derived/ocr/`). Se preservaron los blobs originales **sin recomprimir ni alterar sus bytes** (mismos IDs de objeto Git), y se emparejan mediante el número de archivo.

```text
Datos/S10_Eltiempo_fotos/
├── raw/             # 30 originales JPG/WEBP
├── derived/ocr/     # 30 PNG variantes, NO respuestas de OCR
├── fuentes_index.json
└── README.md
```

## Uso didáctico correcto

- **Fotografías con textos visibles**: compara OCR sobre original y variante de imagen; prueba letreros como los de `eltiempo_006.webp` y `eltiempo_023.webp`.
- **Fotografías sin letras legibles**: sirve **análisis visual o recuperación de imágenes por significado** (EmbeddingGemma 2 con modalidad de imagen), no OCR. Por ejemplo `eltiempo_001.jpg` y `eltiempo_009.webp`.
- **Documentos para OCR tabular:** usa la fuente **separada** `Datos/S10_secop_acta/raw/`, que contiene PDF y PNG de primeras páginas. No inventes que una acta y una noticia están relacionadas.

**No confundir `*_ocr.png` con resultados de texto.** Son archivos PNG destinados a experimentos de OCR: deben inspeccionarse y compararse con `raw/`. El archivo de texto que produzca Tesseract debe generarse posteriormente como otro derivado (por ejemplo `outputs/ocr.jsonl`).

## Limitaciones de procedencia

La carpeta de 30 fotografías **no tiene aún un manifiesto contrastado de URL por archivo, autor/crédito, identificación de noticia y condiciones de reutilización**. Por eso `fuentes_index.json` conserva esos campos en **null**: son tareas pendientes de curaduría, no datos que podamos inventar.

El conjunto **distinto** `Datos/s10_imagenes_reales/` sí conserva 32 imágenes con `inputs.json`, URL, créditos y SHA-256; no presupongas que sus identificadores corresponden a estas 30 fotos.

Respetar atribuciones, licencias y reutilización académica autorizada. La presencia de una fotografía pública en un repositorio no transfiere sus derechos.

## Preguntas para la clase

1. ¿Cuántas fotos contienen texto legible? ¿Cómo lo medimos?
2. ¿Qué palabras reconoce Tesseract en señales o logos? ¿Qué cambia entre original y derivado?
3. ¿Qué imágenes recupera EmbeddingGemma 2 al preguntar «medicamentos», «viviendas en una ladera» o «punto de venta»?
4. ¿Qué afirmaciones se sostienen en los **píxeles** y cuáles requieren el **texto y URL de la noticia**?

## Integridad

`fuentes_index.json` almacena el SHA-1 del **objeto Git** de cada archivo para asegurar que el traslado no cambió bytes. No es el SHA-256 de contenidos: este debe calcularse y registrarse para la ETL del curso. `utils/validate_s10_eltiempo_layout.py` comprueba 30 pares, los formatos y los objetos de Git.
