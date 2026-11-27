# Limpieza y organización del curso · rama de revisión

## Resultado
Inventario completo antes de limpiar: 998 archivos. Se retiran 149 archivos por 218.54 MiB del árbol de trabajo. No se reescribe Git: el tamaño histórico de un clon completo no se reduce automáticamente. Para recuperar material no sensible, revisar el commit anterior `1645b2003b1afaac416646a0a977fc9ac0521e25`. No recuperar ni reutilizar credenciales antiguas.

| Motivo | Archivos | MiB |
|---|---:|---:|
| artefacto generado o marcador vacío | 9 | 0.00 |
| material auxiliar histórico o configuración de entorno retirado | 22 | 0.90 |
| laboratorio Airflow de edición anterior; no pertenece al grupo 2 vigente | 13 | 89.22 |
| cuaderno histórico fuera del itinerario vigente | 32 | 10.54 |
| retirado por riesgo de credenciales históricas; requiere rotación | 1 | 7.81 |
| infraestructura didáctica histórica; LMS y tutorial Git canónico se conservan | 65 | 109.71 |
| generador de cuaderno histórico retirado | 7 | 0.37 |

## Estructura canónica
- `index.html` y `lms/`: entrada del estudiante y progreso oficial.
- `Presentaciones/ruta-aprendizaje.html`, `assets/pedagogia/`: navegación y exploración comunes.
- `Cuadernos/`: cuadernos vigentes; compatibilidad S02, S10 y S11 por sus referencias públicas y QA.
- `Datos/` y `Cuadernos/datos/`: datos reales, muestras y procedencia. Los 300 mil registros SECOP grandes se conservan deliberadamente. No se han eliminado archivos de datos de clase.
- `Laboratorios/` y `laboratorios/`: dependencias de ejecución vigentes y compatibilidad. S11/S13 mantienen sus ramas de estudiante.
- `infraestructura/lms/`: backend y migraciones; `infraestructura/tutoriales/git/`: consulta S02.
- `utils/`, `tests/`, `.github/workflows/`: generadores y QA. Conservar las comprobaciones contractuales y las rutas que necesitan los correctores. MatchLab es independiente: se conserva íntegro.

## Seguridad
El cuaderno histórico con advertencias por credenciales MongoDB se retiró de esta rama y se eliminó su excepción del escáner. La rotación en Atlas sigue pendiente; borrar un archivo no elimina su historial. No se alteró main, el LMS remoto ni las notas.

## Inventario reproducible
Consultar [inventario-retirados.json](inventario-retirados.json). Los archivos retirados pueden localizarse en el commit anterior por su ruta exacta, sin crear otra rama. No se duplican en una carpeta de archivo.

## Límites de esta revisión
Se revisó el árbol completo y se buscaron referencias por nombre/ruta en los materiales actuales y el índice de código; no se ejecutaron todas las plataformas externas. Conservar recursos históricos explícitamente referenciados por páginas publicadas, validadores o evaluaciones hasta disponer de una migración validada.

## Comprobaciones posteriores
17 páginas y 113 referencias locales literales: sin referencias rotas detectadas. 191 archivos de datos con SHA idéntico al árbol anterior; se quitó únicamente un marcador de un byte. Validación ligera adicional: `python utils/validate_course_inventory.py`. [Segunda auditoría pedagógica](auditoria-pedagogica-poslimpieza.md) y [mapa canónico](mapa-sesiones.md). La publicación GitHub Pages está restringida explícitamente a main, incluso si se usa workflow_dispatch.
