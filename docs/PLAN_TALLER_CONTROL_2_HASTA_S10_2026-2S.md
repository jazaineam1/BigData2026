# Taller de Control 2 · Revisión contra PDA 2026-2 y repositorio estudiantil existente

**Estado:** corrección curricular del PR #145, **no publicar el cuaderno previo de BM25/E5 como Taller 2** hasta sustituir su centro evaluativo. Documento basado en el PDA institucional `PDA_2026-02_BIGDATA.pdf` (5 páginas) y `docs/PDA_guia.md`, junto al TC1 V9.

## 1. Resolución de los dos errores

1. **Peso real:** el PDA 2026-2 establece **Taller 1 = 20 %, Taller 2 = 20 %, quices = 20 %, laboratorio en casa = 10 %, proyecto final = 30 %**. El dato antiguo de 25 % procede de otra versión del PDA y se descarta para diseñar TC2. El PDF está firmado para **grupo 1**, no para el grupo 2; comprobar aplicabilidad administrativa del mismo PDA, pero no inventar otra distribución.
2. **Tema real:** sesión 10 = ETL con imágenes; sesión 11 = ETL con audio y video; sesión 12 = **segundo taller: implementación de procesos de ETL**. El taller propuesto anteriormente distribuye 60/100 puntos entre BM25, E5 y RRF, por lo que **no cumple la centralidad ETL**. Su código puede sobrevivir como herramienta de recuperación opcional, pero no como núcleo evaluativo.
3. **Restricción docente vigente:** hasta **lo trabajado en la sesión 10 del grupo 2**. Ese material incluyó imágenes y audio. **No evaluar video, Dask, Spark ni Airflow como requisitos del TC2**. Video pertenece a S11 del PDA del grupo 1; explicitar que se trata de una adaptación y no de cumplimiento literal de toda la secuencia.
4. **Entrega:** los estudiantes **ya poseen repositorios GitHub de trabajo**. Nunca obligar a crear un segundo repositorio. Usar el **mismo repositorio GitHub de la pareja/proyecto**, una rama `taller/tc2-etl`, carpeta `talleres/TC2/` y un Pull Request hacia su propia rama principal. Si una pareja ya usa otra ruta/convención, conservarla siempre que identifique claramente la entrega, el commit y los tres artefactos. Compartir el enlace del PR/commit y la huella por correo institucional, como TC1. Se ha localizado `jazaineam1/BigData2026-Verificacion-S3` como repositorio **docente privado de práctica**: no asumir que es el repositorio privado de todas las parejas ni forzar subir entregas allí.
5. **Plazo definido por el profesor:** sábado **14 de noviembre de 2026 a las 23:59:59 hora de Bogotá (UTC−5)**, final del día 14. Es una fecha de entrega administrativa, distinta de las fechas programadas en el PDA grupo 1.

## 2. Alcance integral y correspondencia con el PDA

**Corrección de alcance:** El PDA 2026-2 denomina al TC2 «Implementación de procesos ETL» y le asigna un peso del 20 % sobre la asignatura. Eso **no impide integrar y evaluar los aprendizajes nuevos de S07 y S09** dentro de un sistema ETL y de consulta: BM25, embeddings E5, búsqueda vectorial, comparación de rankings y RRF se estudiaron después del bloque NoSQL cubierto por TC1. Excluirlos por completo deja capacidades nuevas sin evaluar.

**Restricción temporal acordada:** el corte de evaluación sigue siendo **hasta la S10 REAL del grupo 2**; S10 ya trabajó imágenes, audio, RMS/FFT, ejemplos de transcripción y catálogo. Aunque S11 aparezca posteriormente publicada en el LMS, **no cobrar sus actividades nuevas**, ni video del PDA de grupo 1, ni Dask, Spark o Databricks.

**Hilo conductor:** Laura recibe documentos SECOP con texto recuperable, activos de imagen del laboratorio S10 y diez voces humanas autorizadas. Primero comprueba cómo y por qué recupera registros por palabras y significado; luego aplica ETL verdadero sobre imágenes y señales de audio; finalmente carga el catálogo tipado y construye un explorador consultable para una decisión humana. **No inventar vínculos** entre contratos SECOP, fotografías de otras fuentes y voces MINDS14; la procedencia es una clave explícita, no una suposición.

Se reutilizan datos ya preparados de TC1 o del material formativo para no volver a evaluar extracción SECOP, modelado MongoDB documental, Cassandra, Neo4j, ingesta concurrente ni transacciones. El ETL de **datos no estructurados** sí es nuevo y puntuable, incluyendo transformaciones verificables, esquema, carga, recuperación e idempotencia sobre derivados multimedia.

## 3. Rúbrica objetivo integrada: 100 puntos / aporte del TC2 al curso 20 %

| Etapa | Tema nuevo y evidencia esperada | Puntos |
|---|---|---:|
| **E1 · Búsqueda léxica** | S07: tokenización y DF/IDF observados, BM25 y dos rankings reproducibles (literal/paráfrasis), cambio de palabra interpretado | **10** |
| **E2 · Semántica y búsqueda vectorial** | S09: embeddings E5 reales con prefijos, coseno y Top-k; Atlas solo si hay consulta remota verificable, caso contrario ruta local explícita con crédito proporcional | **15** |
| **E3 · Recuperación híbrida y evaluación** | S09: Precision@5, Recall@5 con juicios externos; RRF calculado por posiciones; decisión y alternativa descartada sustentadas en los resultados propios | **10** |
| **E4 · ETL de imágenes** | S10: fuente y formato verificables, lectura de una imagen REAL del material autorizado, RGB/luminancia, transformación y dos perfiles, histograma, legibilidad y limitaciones de extracción de contenido | **20** |
| **E5 · ETL de audio** | S10: diez WAV reales MINDS14 es-ES, decodificación, metadatos, RMS, FFT y espectrograma, prueba de ventana 512/1024, diferenciación entre rasgos acústicos, texto de referencia y ASR real | **20** |
| **E6 · Carga, catálogo y producto integrado** | S10: carga de catálogo multimodal JSONL/Parquet con referencias y derivaciones; relectura y consultas; integridad/duplicados; reejecución y fallo controlado; explorador offline y decisiones con límites | **25** |
| **TOTAL** | **35 puntos de búsqueda/evaluación + 65 puntos de ETL e integración** | **100** |

**Desglose objetivo de controles observables** (requiere codificación y pruebas antes de ser oficial): E1 = 3+4+3; E2 = 4+5+6; E3 = 4+4+2; E4 = 7+8+5; E5 = 6+8+6; E6 = 6+6+5+5+3. Los puntos corresponden a los archivos y parámetros reales de cada pareja, no a preguntas memorísticas o al simple hecho de ejecutar. No otorgar puntaje remoto Atlas por operaciones NumPy locales.

**OCR y ASR:** experimentos guiados de S10, si se usan, deben declarar si hubo OCR/ASR verdaderamente ejecutado o si el texto vino de una anotación existente. No añadir obligatoriedad de modelos o descargas no enseñados hasta el cierre de S10; no calificar precisión de transcripción sin referencia fiable.

## 4. Cómo será una experiencia completa, no seis tareas sueltas

**Producto integrador:** «Explorador de Evidencias Multimodal» generado desde **el mismo expediente reproducible**. Incluye rankings lexical/semántico/híbrido, activos visuales realmente transformados, diez señales de voz realmente decodificadas y un catálogo donde se consulten ruta, fuente, tipo, derivado y métricas. Ningún ID multimedia se equipara con un ID SECOP sin vínculo declarado.

| Secuencia | Pregunta profesional de Laura | Acción autónoma que realiza el estudiante | Evidencia que alimenta la próxima etapa |
|---|---|---|---|
| E1 | ¿Qué encuentro cuando coincide el vocabulario? | Modifica una consulta, implementa DF/IDF, contrasta Top-5 BM25 | Resultados léxicos tipados con IDs |
| E2 | ¿Y cuando cambia la forma de decir lo mismo? | Implementa coseno, ejecuta E5 y prueba Top-k / filtro | Resultados vectoriales y estado Atlas/local honesto |
| E3 | ¿Qué motor ayuda más en esta intención? | Implementa Precision@5 y RRF, compara tres rankings | Selección y evidencia de búsqueda |
| E4 | ¿Qué información técnica puedo conservar de una imagen? | Decodifica imagen autorizada, implementa luminancia, transforma y observa pérdidas | Original, derivado e inventario visual |
| E5 | ¿Qué puedo medir de una grabación sin suponer palabras? | Implementa RMS y manipula FFT de voces reales | Original, derivado y medidas de audio |
| E6 | ¿Puede otra persona reabrir y verificar lo producido? | Une catálogos por **tipo y procedencia**, reabre, consulta, provoca fallo seguro y genera explorador | Manifest, notebook y ZIP comprobables |

**Anatomía al nivel del TC1:** problema, objetivo y rúbrica al inicio; una ruta de 6 etapas; ejemplo manual pequeño y luego ejemplo auténtico; seis celdas COMO MÍNIMO donde completar una función; interpretación inmediata tras cada salida (cómo se lee, qué demuestra, qué no permite concluir, error común); checkpoints con evidencia concreta; errores controlados y recuperación; cierre con decisión estructurada, alternativa descartada y límite. **No fijar un número artificial de celdas**: comparar aprendizaje y trabajo efectivo con las 81 celdas de TC1.

**Previsión de materiales:** un cuaderno ejecutable (Colab CPU) y una guía vinculada a la actividad; conservar el número de recursos definido en `AGENTS.md`. Las soluciones y la preparación del docente no se publican junto con la entrega.

## 5. Repositorio existente de los estudiantes: instrucciones correctas

**No pedir «New repository».** El estudiante entra a su repositorio que ya creó durante el curso. Si el repositorio es un fork público del material docente, **no publicar ahí** sus nombres, códigos ni archivos privados: usar una ruta privada aprobada del mismo proyecto o garantizar que los artefactos publicados sean anonimizados. No crear repositorios adicionales por defecto.

1. Abrir **el repositorio existente de su pareja** y comprobar el nombre, propietario y permisos.
2. Crear rama `taller/tc2-etl` desde su trabajo previo, sin borrar los hitos del proyecto.
3. Agregar `talleres/TC2/TC2_<PAREJA>.ipynb`, `talleres/TC2/TC2_<PAREJA>.zip` y `talleres/TC2/manifest_tc2.json`. Evitar secretos/PII en repos públicos.
4. Registrar los cambios con **commit** verificable y abrir **PR en su propio repositorio** desde la rama TC2 a `main`; no modificar la rama `main` del docente.
5. Enviar desde correo institucional el enlace al repositorio ya creado y al PR/commit, integrantes y SHA-256 del manifest. Si el repositorio es privado, comprobar que el docente tiene acceso (cuenta GitHub institucional por confirmar, no inventar cuál).
6. Considerar entregado antes de las **23:59:59 de Bogotá del 14-11-2026** cuando están presentes los archivos, el commit y el correo; los archivos y el enlace se revisan en el estado del commit de cierre.

**Alerta de operación:** el archivo ZIP de 10 WAV puede superar límites de carga desde la web si se incluyen fuentes grandes. Mantener sólo el material autorizado y necesario; ofrecer Git/LFS si procede, pero no exigir compras ni cuentas adicionales.

## 6. Acciones técnicas para completar antes de publicar

- [ ] Reconstruir `Cuadernos/Taller_Control_2.ipynb` como un taller **integrado**: BM25 + E5 + RRF (35 puntos), ETL imagen + audio + catálogo/consulta (65 puntos). Reutilizar partes verificadas del prototipo sin conservar su rúbrica desbalanceada.
- [ ] Reutilizar únicamente competencias ya enseñadas y comprobadas hasta S10 de `Cuadernos/10_Imagenes_Audio.ipynb`; tomar ejemplos técnicos de S11 solo si no introducen obligaciones nuevas.
- [ ] Adaptar `utils/tc2_core.py` y `utils/validate_taller_control_2.py`: puntos 10/15/10/20/20/25, verificaciones de archivos reales y consulta de catálogo; recalcular ranking/transformaciones/catálogo, probar fallos de transformación y evitar repetir controles SECOP de TC1.
- [ ] Modificar `assets/tutoriales/tc2-paso-a-paso.html`: usar repositorio existente, fecha/hora, PR propio, sin crear otro.
- [ ] Validar end-to-end con datos licenciados, notebook de estudiante limpio y calificador de ZIP externo; probar GitHub en modo público anonimizante y privado restringido.
- [ ] Conciliar el PDA del **grupo 1** con el plan aprobado para **grupo 2** antes de publicar la calificación institucional del 20 %.
- [ ] Fusionar PR y abrir la actividad en LMS sólo cuando los criterios anteriores estén satisfechos.

## 7. Fuentes

- PDA auténtico: `PDA_2026-02_BIGDATA.pdf` p. 1–5: método evaluativo y S10–S12.
- Guía actualizada: `docs/PDA_guia.md` (corrige el error histórico de 2023).
- Primer taller: `Cuadernos/Taller_Control_1.ipynb` (V9).
- Ruta docente de GitHub: `infraestructura/git-ejemplo/README.md`.
- Laboratorio multimedia ya existente: `Cuadernos/11_ETL_Audio_Imagenes.ipynb`.
- Repositorio docente de práctica: `jazaineam1/BigData2026-Verificacion-S3` (privado; no confundir con las copias/repositorios de estudiantes).
