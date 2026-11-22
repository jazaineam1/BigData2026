# Reporte de pruebas verificables · proyecto final S14
**Fecha:** 22 de noviembre de 2026 · grupo 2 · uso docente · **NO PUBLICAR EN PORTADA NI LMS**

## Dictamen
**Aprobación PARCIAL.** La fuente SECOP de referencia se inspeccionó realmente, la paginación OFFSET pasó pruebas de fallos, el producto HTML se generó y probó en un navegador, y el material integrador pasó controles estructurales. **No** se ejecutó en esta revisión una descarga parametrizada real de SECOP, un clúster Dask real o una sesión Databricks Free. No asignar aún una nota ni anunciar el taller como completamente verificado.

| Aspecto | Método / recurso | Resultado | Alcance / limitación |
|---|---|---|---|
| CSV SECOP versionado | lectura íntegra del contenido de GitHub con análisis estructural | **1.000 registros, 59 columnas, 1.000 IDs únicos, ninguna fila irregular** | Fuente ya versionada en repo, no una descarga nueva |
| Etiquetas del clasificador | conteos sobre 1.000 filas reales | **830 elegibles: 440 directa y 390 régimen especial** | Antes de la curaduría |
| Riesgo de fuga por texto repetido | normalización/cómputo de descripciones | **19 valores `No Definido` y 1 duplicado adicional** | No trasladar al alumno un trabajo de auditoría docente |
| Base final diseñada | retirar marcadores y duplicado **antes de dividir** | **810 textos únicos: 435 directa, 375 régimen especial** | Falta ejecutar el split en un kernel estudiantil; tamaño esperado train 648/test 162 |
| OFFSET y LIMIT | **11 pruebas Python ejecutadas localmente con HTTP simulado** | **11/11 pasan** | Valida lógica, no servicio vivo |
| HTTP real básico | lectura pública de `/resource/p6dx-8zbt.json` | responde JSON en consulta web | NO acredita filtrado parametrizado |
| HTTP SECOP parametrizado | intento de `$offset`, `$limit`, `$order` mediante herramientas disponibles | **NO VERIFICADO**: URL parametrizada no accesible desde aquí | E1 producirá evidencia HTTP real en Codespaces/Colab |
| Producto offline | generador Python con 4 registros de prueba + Chromium headless | generó HTML y pasó búsqueda, filtro, detalle, CSV exportable y pantalla 375 px | Dataset sintético **solo de test**, no indicador real de SECOP |
| Seguridad del producto | cadena que intenta cerrar `script`, HTML revisado/renderizado | escapado correcto, contenido mostrado como texto | prueba de humo, no pentest |
| Archivos del proyecto | revisión JSON/código/material/URLs/rúbrica | **17 de 17 comprobaciones estáticas pasan** | No certifican ejecución completa |
| Procesamiento Dask | scripts existentes S13 + integración revisada | **NO EJECUTADO ahora** | biblioteca Dask ausente del runtime de pruebas |
| Modelos scikit-learn sobre los 810 SECOP | código alineado con S13, curaduría antes del split | **NO EJECUTADO ahora** | no inventar F1 o tiempos |
| Databricks Free + MLlib | compatibilidad documental y código de E5/E6 inspeccionado | **NO EJECUTADO** | falta cuenta estudiantil y cuota de Free |
| Publicación | comprobación de index/LMS/Pages | taller **sin promoción ni copia en Pages** | el código del repo público sigue visible en GitHub |

## 1. Pruebas OFFSET (11/11)

Ejecuté localmente en Python las variantes del módulo `utils/proyecto_final_offset.py` con `unittest` y clientes HTTP simulados. Casos: 
1. OFFSET 0/20 con 40 registros, orden/hash igual secuencial vs paralelo.
2. Último OFFSET de 45 registros con LIMIT parcial de 5.
3. Página incompleta: debe producir error y no declarar éxito.
4. HTTP 429 con reintento acotado.
5. Fuente alterada entre lecturas: detectar hash no equivalente.
6. OFFSET negativo, desalineado o fuera de rango; demasiadas páginas.
7. HTTP 429 persistente: fallo registrado.
8. HTTP 400: **no** reintentar consulta inválida.
9. JSON de forma inesperada: rechazo.
10. Error de transporte inicial: reintento una sola vez.
11. `Retry-After: 60`: no insistir antes de que venza el límite del servidor; detener experimento.

**Datos y paginación:** mismos filtro y orden de ventana `2024-01` del TC1 (`2024-01-01` hasta `2024-03-01` excluido), terminando en `:id ASC`; tamaño 20, offsets 0/20, número máximo de páginas 3, dos workers, cuatro GET nominales; reintentos pueden aumentarlas si HTTP falla. Cada página comprueba el total esperado y guarda hash; cada método guarda RAW en JSON cuando la API efectivamente responde. No afirmar que ID de proceso es necesariamente único en toda la API: el orden total usa ID interno Socrata como desempate.

### ¿Por qué no certifico la API en vivo?
La consulta web directa al endpoint sin parámetros devolvió datos JSON, pero la interfaz de búsqueda rechazó URLs con parámetros `$offset`/`$limit` y la red de la sesión Python está aislada. **No hay una respuesta HTTP parametrizada íntegra que permita proclamar una descarga exitosa**. El código de la clase permite obtenerla desde Colab/Codespaces con permisos de red, pero esa ejecución sigue pendiente.

## 2. Prueba real de navegador del observatorio

Se creó un archivo HTML auténtico mediante el generador del proyecto y se renderizó en Chromium con Playwright **en este entorno**, a partir de cuatro filas **sintéticas de control** (2 train, 2 test). Se comprobó:
- indicadores iniciales: 4 expedientes;
- búsqueda «sistemas»: se recuperó 1;
- detalle por ID (registro de test);
- filtro `split=test`: 2 expedientes;
- descarga `consulta_observatorio_secop.csv` desde el botón;
- pantalla de 375 píxeles: anchura documentada 375, sin desbordamiento lateral;
- una descripción con HTML malicioso escapada antes de insertarse en JSON/script.

En este navegador de pruebas se bloqueó la navegación `file://`, por lo que se utilizó `page.set_content` con el HTML generado. Eso prueba que la interfaz y JS funcionan, **no** que la apertura directa de un archivo local esté garantizada en todos los dispositivos. El HTML no requiere un servidor por diseño.

Ejecutar manualmente cuando se necesite repetir: `python tests/manual_proyecto_final_browser.py` (solo docente; requiere Chromium/Playwright ya instalados; no poner esa dependencia en Codespaces estudiantil).

## 3. Pruebas con límites y costos

- **No ejecutar en Actions:** la descarga SECOP real, Spark, scikit-learn, OCR, ASR, benchmarks de 50.000 o el navegador. Los tests automáticos baratos usan `unittest` sin red.
- Por equipo, máximo **4 solicitudes iniciales** para E1 (dos métodos × dos páginas); no descargas masivas simultáneas.
- S13 Codespace ya existente, preferentemente 2 núcleos y autoapagado corto; si cuota agotada, Colab CPU descarga solo los archivos mínimos.
- Databricks Free serverless restringe Internet/cuotas; un entrenamiento con MLlib no se da por aprobado sin validación directa.

## 4. Puertas de salida para anunciarlo a los estudiantes

| Puerta | Estado | Validación necesaria |
|---|---|---|
| CSV público y curaduría | validado estructuralmente | ejecutar E2 en Colab para producir efectivamente 810 filas + split |
| E1 HTTP parametrizado | **pendiente** | 4 GET en una red real, trazas status/hash/offset |
| Dask E3/E4 | **pendiente** | 2 workers reales y 3 configuraciones entrenadas en Codespaces/Colab |
| Databricks E5/E6 | **pendiente** | subir CSV y obtener tablas + F1 real en Free |
| Observatorio con datos reales | **pendiente** | generar HTML con las predicciones reales de E7 |
| Navegador con muestra controlada | probado | opcional repetir con archivo completo |
| Peso/fecha grupo 2 | pendiente | confirmar con docente/institución |
| Publicación web/LMS | bloqueada | **no publicar sin aprobación explícita** |

**Fuentes primarias:** [TC1](../Cuadernos/Taller_Control_1.ipynb) · [contrato TC1](../utils/tc1_contrato.py) · [cliente TC1](../utils/tc1_secop.py) · [snapshot S13](../Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv) · [OFFSET de Socrata](https://dev.socrata.com/docs/queries/offset.html) · [GitHub Codespaces](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces) · [Databricks Free Edition](https://docs.databricks.com/aws/en/getting-started/free-edition-limitations).
