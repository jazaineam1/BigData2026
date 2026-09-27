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

- **RPO objetivo: 24 horas.** Debe existir un snapshot académico verificado por SHA-256 al menos una vez cada 24 horas durante operación activa.
- **RTO objetivo: 4 horas.** Ante incidente severo, el objetivo es restaurar servicio académico verificado dentro de cuatro horas.
- El snapshot académico no contiene contraseñas, tokens, secretos de Edge Functions ni binarios de Storage.
- Storage se recupera por separado y debe reconciliarse con los metadatos del snapshot.

## Señales de observabilidad

El panel `lms/admin-operations.html` expone agregados operativos, no datos sensibles:

- sesiones activas;
- intentos de login y fallos de las últimas 24 h;
- actividad académica de las últimas 24 h;
- señales Realtime de las últimas 24 h;
- archivos pending/abandoned con más de 24 h;
- último snapshot y cumplimiento del RPO.

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
