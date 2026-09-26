# Contrato LMS V5 — fuente de verdad y runtime

## Fuente de verdad

El LMS evita duplicar configuración académica entre HTML, JSON y backend.

- `lms/data/course.json`: estructura del curso, sesiones, estado/visibilidad y herramientas de navegación.
- Supabase (`lms_run_sessions_v2`, `lms_run_resources_v2`, `bd_lms_activities`, `bd_activity_catalog`): recursos, actividades, LAB, evaluadores, competencias y reglas de completitud.
- HTML: renderiza la configuración; no es la fuente de verdad de recursos/actividades.
- `lms/session.html?s=N`, `lms/progress.html?s=N`, `lms/wall.html?s=N`: superficies canónicas.
- Páginas específicas por sesión no se crean. S08 permanece protegida; S09 legacy solo redirige.

## Recursos

Una sesión expone como máximo dos recursos principales. Cuando hay presentación, integra explicación, ejemplos y laboratorio. El cuaderno acompaña la práctica reproducible.

## Runtime

`lms/assets/lms-kit.js` envuelve `bigdata-lms.js` sin romper compatibilidad.

- cola: `lms.bigdata.queue.v1`;
- límite normal: 500 entradas;
- evidencia/publicaciones se priorizan frente a telemetría;
- retry: 1 s, 2 s, 4 s, 8 s, 30 s;
- eventos/evidencias/publicaciones llevan idempotency key;
- `pagehide` usa `fetch(..., keepalive:true)` porque `sendBeacon` no permite establecer el header Authorization requerido por el LMS;
- los desafíos que necesitan feedback inmediato no se simulan offline.

## Regla de degradación

Si una escritura recuperable no puede enviarse por red:

1. se conserva localmente;
2. la UI informa que quedó pendiente de sincronización;
3. se reintenta al recuperar conectividad;
4. el backend evita duplicados por idempotencia.

La evidencia tiene más prioridad que heartbeat, slide tracking o interacciones repetitivas.
