# Runbook operativo del LMS Big Data

## Objetivo

Recuperar el LMS Big Data sin improvisar cambios masivos sobre datos académicos. Este documento separa cuatro capas que no deben confundirse:

1. base de datos PostgreSQL;
2. objetos privados de Storage;
3. Edge Functions y configuración;
4. snapshot académico exportable desde el LMS.

## Principio de recuperación

El botón **Generar snapshot** del LMS no sustituye los backups de plataforma. Es un respaldo lógico, portable y verificable de la cohorte Big Data, útil para auditoría, reconstrucción selectiva y validación.

El snapshot:
- incluye datos académicos y metadatos de archivos;
- excluye `password_hash`;
- excluye secretos y claves;
- excluye binarios de Storage;
- incluye SHA-256 del bloque `data`.

## Backups de plataforma

Supabase documenta que sus backups de base de datos no incluyen los objetos almacenados mediante Storage API; la base conserva metadatos, pero restaurar la base no recupera archivos borrados del bucket.

Referencia: https://supabase.com/docs/guides/platform/backups

También documenta que durante un restore el proyecto queda inaccesible, por lo que debe planearse una ventana de indisponibilidad.

## Antes de cualquier recuperación

1. Detener calificaciones, matrículas, limpiezas y cambios administrativos.
2. Registrar:
   - hora del incidente;
   - síntoma;
   - tablas/usuarios potencialmente afectados;
   - último cambio conocido;
   - último snapshot académico disponible.
3. Generar un snapshot adicional si el sistema todavía responde y hacerlo no empeora el incidente.
4. Verificar el SHA-256 del snapshot.
5. Confirmar qué capa falló: DB, Storage, Edge Function o solo datos de una cohorte.

## Estrategia preferida

### A. Problema de proyecto completo

Usar primero el mecanismo de restore/backup de Supabase o restaurar a un proyecto nuevo para inspección cuando esa capacidad esté disponible en el plan.

Un restore a un proyecto nuevo permite validar la base antes de tocar producción, pero Storage, Edge Functions y varias configuraciones requieren reconfiguración separada.

Referencia: https://supabase.com/docs/guides/platform/clone-project

### B. Problema limitado a datos Big Data

Preferir una reconstrucción selectiva desde snapshot, no un restore completo del proyecto compartido con otros cursos.

Nunca insertar filas del snapshot directamente desde el navegador.

## Orden lógico de restauración selectiva

El orden debe respetar las dependencias:

1. `lms_courses` y `lms_course_runs`.
2. usuarios existentes por identificador; no recrear contraseñas desde el snapshot.
3. `lms_enrollments` y `lms_run_enrollments`.
4. sesiones, recursos y anuncios.
5. tareas, rúbricas y competencias.
6. banco de preguntas y quizzes.
7. entregas y notas.
8. archivos: primero objetos de Storage, después metadatos coherentes.
9. grupos, discusiones y revisión por pares.
10. analítica, intervenciones y eventos.
11. tablas `bd_lms_*` específicas de S08.

## Storage

Los binarios deben respaldarse por separado.

Antes de reactivar descargas:
- cada fila `attached` debe apuntar a un objeto existente;
- bucket y ruta deben coincidir;
- tamaño y MIME deben ser razonables;
- no convertir un `pending` en `attached` solo para “arreglar” una inconsistencia.

## Retención

La limpieza del LMS aplica exclusivamente a:
- `pending` antiguos;
- `abandoned` antiguos.

Reglas:
- mínimo 24 horas de antigüedad;
- nunca eliminar `attached`;
- la API reclama primero el registro como `abandoned`;
- el submit solo acepta la transición `pending → attached`;
- la eliminación requiere rol `admin`;
- la acción queda auditada.

Si Storage falla durante la eliminación, el registro queda `abandoned` para poder reintentar con seguridad.

## Verificación posterior

Antes de reabrir el LMS:

1. ejecutar QA acumulativo;
2. comprobar SHA protegido de S07;
3. validar TC1 sintético y notebook reproducible;
4. comprobar Gradebook;
5. comprobar quizzes;
6. comprobar competencias;
7. comprobar colaboración;
8. comprobar descargas privadas;
9. verificar que el curso no exponga secretos;
10. probar en móvil y escritorio.

## Objetivos operativos recomendados

Mientras la plataforma siga siendo un LMS de curso:

- RPO académico lógico: generar snapshot antes de cambios estructurales y evaluaciones críticas;
- conservar snapshots fuera del mismo proyecto;
- no usar el snapshot como sustituto único del backup de plataforma;
- documentar cada restore o limpieza en auditoría.

Cuando el LMS pase a soportar varias cohortes activas de forma institucional, definir RPO/RTO formales con la universidad y evaluar PITR según volumen, criticidad y presupuesto.
