# LMS V8 · Operación, continuidad y accesibilidad

## Objetivo

Cerrar la fase F8B sin mezclar todavía integraciones institucionales bidireccionales. La prioridad es que el LMS pueda operar, degradarse y recuperarse con reglas explícitas.

## Política de sesiones

| Rol | TTL | Persistencia cliente | Motivo |
| --- | ---: | --- | --- |
| student | 30 días | navegador + pestaña | continuidad del aprendizaje |
| teacher | 12 horas | solo pestaña | reducir exposición de cuentas con privilegios docentes |
| admin | 4 horas | solo pestaña | mínima permanencia para privilegios administrativos |

Toda Edge Function autenticada valida `expires_at`. Las sesiones legacy sin fecha explícita conservan el fallback V5.1 únicamente para compatibilidad.

## Objetivos de continuidad

- **RPO objetivo de plataforma: 24 horas.** Es un objetivo de continuidad; el LMS no certifica desde su propio panel el estado de los backups administrados por Supabase.
- **RTO objetivo: 4 horas.** Ante incidente severo, el objetivo es restaurar servicio académico verificado dentro de cuatro horas.
- **Snapshot académico objetivo: 24 horas.** Es una capa adicional de portabilidad verificable por SHA-256; no sustituye el backup de plataforma.
- El snapshot académico no contiene contraseñas, tokens, secretos de Edge Functions ni binarios de Storage.
- Storage se recupera por separado y debe reconciliarse con los metadatos del snapshot.

### Snapshot académico automático

- `pg_cron` ejecuta el snapshot diariamente a las **08:20 UTC (03:20 Bogotá)**.
- `pg_net` invoca `bigdata-lms-ops` con un secreto generado y conservado en **Supabase Vault**.
- La Edge Function valida el secreto mediante un RPC accesible únicamente a `service_role`.
- El JSON se escribe en el bucket privado `bigdata-lms-snapshots` con SHA-256 en el manifiesto.
- La retención automática es de **30 días**.
- El bucket está en el mismo proyecto Supabase: protege frente a errores lógicos y mejora portabilidad, pero **no reemplaza una copia externa ni el backup administrado de plataforma**.
- Los exports manuales continúan disponibles para conservar una copia fuera del proyecto.

## Señales de observabilidad

El panel `lms/admin-operations.html` expone agregados operativos, no datos sensibles:

- sesiones activas;
- intentos de login y fallos de las últimas 24 h;
- actividad académica de las últimas 24 h;
- señales Realtime de las últimas 24 h;
- archivos pending/abandoned con más de 24 h;
- último snapshot académico exportado y su antigüedad;
- el objetivo RPO/RTO declarado, dejando explícito que el estado real del backup administrado de plataforma no se observa desde el LMS.

No se muestran IP, hashes de login, tokens ni respuestas académicas.

## Runbook de incidente

1. Clasificar el incidente: autenticación, datos académicos, Storage, despliegue estático o Edge Functions.
2. Detener únicamente las escrituras afectadas; evitar cambios masivos mientras se preserva evidencia.
3. Registrar hora, alcance, último comportamiento correcto y último snapshot conocido.
4. Verificar primero GitHub Pages/CI y estado de Edge Functions; después PostgreSQL y Storage.
5. Si hay pérdida o corrupción de datos, usar mecanismos de restore de Supabase antes de reinsertar snapshots manualmente.
6. Restaurar dependencias en orden: configuración → matrículas → sesiones/recursos → tareas → entregas/notas → competencias/colaboración → eventos.
7. Reconciliar Storage con `lms_submission_files_v2`.
8. Ejecutar QA completo, pruebas de autenticación y accesibilidad antes de reabrir.
9. Documentar causa raíz, RPO real y RTO real del incidente.

## Accesibilidad

La interfaz LMS debe conservar:

- navegación por teclado;
- foco visible;
- enlace “Saltar al contenido principal”;
- objetivos táctiles de al menos 44 px en los controles principales;
- soporte de `prefers-reduced-motion`;
- soporte de `forced-colors`;
- cero violaciones Axe de impacto `serious` o `critical` para reglas WCAG 2 A/AA, 2.1 A/AA y 2.2 AA en las superficies certificadas.

La certificación automática no sustituye revisión manual de orden de foco, lenguaje, claridad, zoom y uso con lector de pantalla.
