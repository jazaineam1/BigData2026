<!-- Diseño entregado el 2026-09-27 (solo lectura, sin ejecutar). Las 12 decisiones de la §8 siguen abiertas. Ver docs/PENDIENTES.md. -->

# Diseño: Wall de competencia y retiro del muro abierto legacy

Base leída: `C:\Users\nib1l\orca\workspaces\BigData2026\prueba-v54b` (= origin/main 029e13e). Solo lectura: no se editó, ejecutó ni desplegó nada.

Convención de nombres para no confundir dos cosas que hoy se llaman "wall":

| Nombre en el repo | Qué es | Destino |
|---|---|---|
| `lms/wall.html` + acción `teacher_wall` (index.ts:712) | Cabina docente (progreso, fricción, controles, revisión de rúbrica) | SE QUEDA (solo pierde el enlace de proyección del muro) |
| `lms/class-wall.html` + `wall_post/wall_list/wall_react/wall_moderate` | Muro abierto legacy (texto libre, reacciones) | SE RETIRA |
| Wall de competencia (nuevo) | Tablero estructurado con alias, solo lectura para el estudiante | SE CREA. Prefijo `competition_` en acciones y `competition-wall.html` en frontend, para no chocar con `wall_*` ni `teacher_wall` |

---

## 0. Estado real del muro legacy (hallazgos que cambian el plan)

El retiro ya está a medias desde V54-A, lo que baja el riesgo:

- `wallPost` ya rechaza a estudiantes en su primera sentencia (index.ts:291-293) y `class-wall.html` ya redirige al estudiante a `session.html` (class-wall.html:77-78). Es una vista docente de histórico.
- `lms-v54a-no-open-student.sql:12-13` declara que el retiro de tablas de muro es "V54-B" (migración posterior). Este diseño es esa V54-B.
- `validate_no_open_student.py:138-145` ya imprime "PENDIENTE V54-B" (solo para `short_text`; el muro se cubre en la línea 127).
- Un estudiante con `wall_list` todavía recibe datos: `wallList` (index.ts:326-364) permite ver el muro a un no-docente si tiene una publicación previa (`publish_first`). Como `wallPost` ya está cerrado, ningún estudiante nuevo puede cumplir esa condición; los antiguos sí. Quedan como superficie viva hasta retirar `wall_list`.

Hallazgos nuevos (no estaban en el encargo):

1. **Cola offline puede atascarse al quitar `wall_post` de lms-kit.js.** `deliver()` (lms-kit.js:122-140) termina en `throw new Error('Tipo de cola desconocido')` sin `status`. En `flush()` (145-183) un error sin status cuenta como reintentable (`retryable`: `!status`, línea 107) y `flush` hace `return` en el primer fallo (líneas 169-174). Un `wall_post` que un estudiante dejó pendiente en `localStorage` (clave `lms.bigdata.queue.v1`) bloquearía para siempre la entrega de la evidencia que quede detrás. Hoy no pasa porque el backend responde 400 (no reintentable). El PR #102 quita la rama `wall_post` de `deliver` y reintroduce este bug. Ver §5, paso D3.
2. **La competencia BD-E7 no es alcanzable para estudiantes nuevos.** `lms-s09-transfer-evidence-v11.sql:70-74` sube `min_evidence_count` a 2 y mapea lab3/lab4/lab8/lab9; V52 (`lms-s09-no-open-responses-v52.sql:5-19`) retiró la transferencia de lab3/4/8, así que solo lab9 (`authentic-review`, aceptado por docente con rúbrica) genera evidencia `accepted` con `rubric`. Con 1 evidencia posible y mínimo 2, `computeCompetencyRows` (bigdata-lms-core/index.ts:465-467) nunca da `mastered`. No lo pude confirmar contra la base viva: se deduce de las migraciones. Afecta a la decisión D2 de §8.
3. **`bd_evidence.verdict='accepted'` no siempre es verificación.** La rama por defecto de `submitEvidence` (index.ts:131, 204-216) deja `verdict="accepted"` para cualquier evaluador `self-report` de sesiones distintas de S09 con solo enviar texto. Contarlo como "evidencia verificada" sería puntuar por enviar algo. Ver la regla de verificación en §2.
4. **Los recursos "visitar" nunca llegan a `completed`.** `track` llama `touchActivity(..., complete=false, ...)` (index.ts:892) y no hay ningún camino que complete un recurso; los `required=true` de S09 (`bd-s09-presentation`, `bd-s09-notebook`, seed s09-vector-search-seed.sql:26-27) quedan `in_progress` siempre. El `competition_wall` del PR #102 cuenta `required` con `status==="completed"`: por diseño nadie llega al total y además mezcla actividades basadas en clics.
5. **Toda página del estudiante bajo `lms/` (salvo `teacher-*`/`admin-*`) es escaneada por `validate_no_open_student.py`** (líneas 69-75, 97-100): la nueva página no puede tener `<textarea>` ni `<input>` de texto. Y `lms/wall.html` sí está escaneada: cualquier `<input>` de texto nuevo ahí (por ejemplo la frase de confirmación de rotación) exige una entrada en `INPUT_ALLOWLIST` (línea 42).
6. `validate_student_ux_simple.py:33-45` restringe la navegación y el vocabulario de portal/sesión/progreso ("Dominado ", "Tiempo activo", enlaces en header). El acceso al wall debe ser una tarjeta en `session.html`, no un enlace de header.

---

## 1. Modelo de datos

### 1.1 Tablas nuevas (esquema completo en §6)

| Tabla | Para qué | Clave | Acceso |
|---|---|---|---|
| `bd_competition_items` | Lista explícita, por cohorte y sesión, de qué actividades cuentan (deny-by-default). Sin fila no cuenta. | `(course_run_id, session_number, activity_code)` | solo `service_role` |
| `bd_competition_competencies` | (opcional) competencias que suman unidades en esa sesión | `(course_run_id, session_number, competency_code)` | solo `service_role` |
| `bd_competition_settings` | Estado del tablero por sesión: `hidden`/`open`, corte `as_of`, `hide_zero`, `min_cohort`, `rule_version` | `(course_run_id, session_number)` | solo `service_role` |
| `bd_competition_aliases` | Mapa alias -> estudiante, **por sesión**, aleatorio y almacenado | PK `(course_run_id, session_number, user_id)` y `unique (course_run_id, session_number, alias_no)` | solo `service_role` |

Por qué una tabla explícita de ítems y no "todas las actividades `required`":
- `required` es inconsistente hoy (en el seed S09 solo `bd-s09-lab3` de los 12 LAB es `required`, lms-evidence-v4.sql:79-90; los 5 checkpoints y 2 recursos sí).
- Los recursos son señal de clic, prohibida por la regla de evidencia objetiva.
- El puntaje debe poder auditarse con una lista corta y versionada en Git.

### 1.2 Alias por sesión y rotación

- Formato mostrado: `"Jugador " + lpad(alias_no::text, 2, '0')`. `alias_no` sale de una permutación **aleatoria** (`gen_random_uuid()` como clave de orden), no de un hash del `user_id` ni del orden de matrícula/alfabético.
- Rango del pool: `1..greatest(20, 2*N_estudiantes)`. Así el mayor alias no revela el tamaño exacto de la cohorte y se mantienen 2 dígitos hasta 49 estudiantes.
- Alta perezosa e idempotente: `bd_competition_ensure_aliases(run, session)` con `pg_advisory_xact_lock`, asigna alias solo a los estudiantes activos que aún no lo tienen; los que se matriculen tarde reciben un número libre aleatorio del pool.
- **Rotación automática por sesión:** cada `(run, session)` tiene su propia permutación independiente. No existe ningún dato que enlace el alias de S09 con el de S10 salvo que se calcule uno a partir del otro, y no se hace.
- Opcional recomendado: al asignar alias de la sesión N, si algún estudiante repite el mismo `alias_no` que en N-1, intercambiarlo con el siguiente; evita el "siempre soy Jugador 07" por azar (1/N por sesión). No está en el SQL propuesto para mantenerlo simple.
- **Rotación manual** dentro de la sesión: acción `teacher_competition_rotate` borra las filas de alias de esa sesión y las regenera (auditada, con frase de confirmación `ROTAR_ALIAS_S09`).
- El `reset` de sesión (`resetSession`, index.ts:793-818) **no** debe tocar los alias (no están en su lista de deletes). Decidir si se rota en el reset (D6 de §8).

### 1.3 Cómo resuelve el docente alias -> estudiante

Solo por la acción `teacher_competition_board` (rol `teacher`/`admin`, `requireTeacher`, index.ts:415). Hace `join` `bd_competition_aliases` con `lms_users` (`display_name`, `username`, `id`), registra en `lms_audit_log` (`audit()`, index.ts:418) la acción `bigdata.competition.resolve` con `session_number` y conteo de filas, **sin nombres** en el metadata. Consulta directa equivalente en SQL (auditoría manual) en §6.

### 1.4 RLS y permisos (defensa en profundidad)

Las Edge Functions usan `service_role` (index.ts:3-7), que salta RLS; **el control real es el código** (`requireTeacher`, mapeador de respuesta). RLS solo evita que un cliente con la clave publicable lea tablas por PostgREST:

- `alter table ... enable row level security;`
- `revoke all on table ... from anon, authenticated;`
- política de negación explícita `for all to anon, authenticated using (false) with check (false)` (mismo patrón que `bd_session_controls`, lms-v6-live-controls.sql:29-35);
- `grant ... to service_role`.
- **Las funciones SQL también:** en Postgres `EXECUTE` va a `PUBLIC` por defecto y Supabase expone `public` por RPC. Hay que hacer `revoke all on function ... from public, anon, authenticated; grant execute ... to service_role;`. No lo cubre RLS.

### 1.5 Alias y persistencia en el navegador

El alias no se guarda en `localStorage`/`sessionStorage` ni se envía a `track`. La página solo lo lee de la respuesta. (`lms-kit.js` ya limpia por propietario, pero aquí no hay nada que persistir.)

---

## 2. Puntaje objetivo: definición exacta y reproducible

### 2.1 Qué es una "unidad"

Cada estudiante activo (`lms_run_enrollments.role='student' and status='active'` y `lms_users.active`) tiene `units_done` y toda la cohorte comparte el mismo `units_total` (número de ítems declarados). El tablero muestra `units_done/units_total` (por ejemplo `8/17`).

```
units_done  = checkpoints_done + labs_done + competencies_done
units_total = #checkpoints declarados + #labs declarados + #competencias declaradas
```

### 2.2 Regla por componente (con las tablas y columnas leídas)

| Componente | Cuenta cuando... | Tablas/columnas | Dónde se escribe (código leído) |
|---|---|---|---|
| **Checkpoint correcto** | Existe fila de progreso con `metadata->>'mastery' = 'true'` y `completed_at is not null and completed_at <= as_of` | `bd_lms_activity_progress(user_id, course_run_id, activity_code, status, metadata, completed_at)`; ítem con `item_kind='checkpoint'` | `answerChallenge` (index.ts:535-566): `mastery = previousMeta.mastery \|\| correct`; `status = mastery ? completed : in_progress`. El cliente no puede fijarlo: `cleanMeta` (index.ts:49-57) solo acepta claves de una lista fija y `touchActivity` (492-504) solo copia `source` |
| **LAB con evidencia verificada** (LAB completados y evidencias verificadas son la misma unidad: no se cuentan dos veces) | Existe al menos una fila de evidencia "verificada" para ese `activity_code` en la sesión con `coalesce(reviewed_at, created_at) <= as_of` | `bd_evidence(user_id, course_run_id, session_number, activity_code, verdict, reviewed_by, reviewed_at, created_at)` + `bd_activity_catalog(code, evaluator)` | `submitEvidence` (110-254), `teacherReviewEvidence` (601-655) |
| **Competencia demostrada** (opcional, por sesión) | Estado `mastered` por la misma fórmula de `computeCompetencyRows` restringida a evidencia de actividades de esa sesión | `lms_activity_competencies_v2(course_run_id, activity_code, competency_code, weight)`, `lms_competencies_v2(mastery_threshold, min_evidence_count, active)`, `bd_evidence(verdict, rubric->total, rubric->max)` | bigdata-lms-core/index.ts:414-468 |

Definición de "evidencia verificada" (`verified(e)`):

```
verified(e) :=
     (e.verdict = 'correct'  AND catalog.evaluator IN ('choice-hash','seeded-numeric'))
  OR (e.verdict = 'accepted' AND e.reviewed_by IS NOT NULL)      -- aceptada por docente con rúbrica
```

- Un intento `incorrect` no resta ni suma; el número de intentos no interviene: "falló 5 veces y luego acertó" == "acertó a la primera".
- `pending_review` y `rejected` no cuentan. `accepted` sin `reviewed_by` (auto-aceptada de un `self-report`) no cuenta. Esto cubre el hallazgo 3.
- La evidencia histórica de transferencia (`step_id='transfer'`, aceptada por docente) sí cuenta: cumple la segunda cláusula.
- Se apoya en `bd_evidence` (registro de eventos que solo se escribe en `submitEvidence`/`teacherReviewEvidence`) y no en `bd_lms_activity_progress.metadata.evidence_verified`, que se sobrescribe y lo tocan migraciones (V52, lms-s09-no-open-responses-v52.sql:23-47).

### 2.3 Lo que NO entra en el puntaje (lista cerrada)

`bd_lms_activity_progress.attempts`, `bd_lms_session_progress.active_seconds`, `last_activity_at`, `started_at`, cualquier fila de `bd_lms_events` (incluido `heartbeat`, `slide_viewed`, `lab_interaction`), `metadata.first_attempt_correct`, `visited`, recursos (`kind='resource'`), mensajes (ya no existen), y la marca de tiempo del envío salvo como corte `as_of`. Se comprueba de forma estática (ver §7, N5).

### 2.4 Empates y orden

- `position = rank() over (order by units_done desc)`: ranking de competencia (1, 2, 2, 4). Los empatados **comparten posición** y se muestran con la palabra "empate".
- **Sin desempate**: `speed_tiebreak = false`. No se desempata por hora de entrega, intentos, tiempo, racha ni orden alfabético.
- Orden de presentación dentro de un empate: por `alias_no` ascendente. Es estable y no filtra nada porque `alias_no` es aleatorio (por eso hay que evitar derivarlo del nombre o del orden de matrícula).
- Estudiantes con 0 unidades: por defecto se agrupan en una línea "N alias sin avance todavía" (`hide_zero=true`) para no exhibir a quien va más atrás; su propia fila siempre se muestra. Decisión D3.
- Corte reproducible: `p_as_of` (por defecto `now()`). El docente puede fijar `bd_competition_settings.as_of` (por ejemplo al final de la clase) y recalcular el mismo tablero días después.
- Efecto de la revisión docente: un LAB `authentic-review` (lab9) solo cuenta cuando el docente lo acepta. Dos estudiantes con el mismo trabajo pueden quedar separados por la latencia de revisión. Es un límite del criterio, no velocidad del estudiante; se muestra al propio estudiante como "1 en revisión" (solo en su fila `self`). Decisión D8.

### 2.5 Ejemplo S09 (lo que declara el seed leído)

Ítems: checkpoints `bd-s09-c1..c5` (s09-vector-search-seed.sql:28-32) y los 12 LAB de lms-evidence-v4.sql:79-90 (`bd-s09-lab1`, `-lab-e5`, `-lab-chunk`, `-lab2`, `-lab3`, `-lab4`, `-lab5`, `-lab6`, `-lab7`, `-lab8`, `-lab-eval`, `-lab9`). `units_total = 5 + 12 = 17` sin competencias. Con la competencia BD-E7 incluida serían 18, pero por el hallazgo 2 nadie podría llegar a 18/18 y lab9 se contaría dos veces (como LAB y como base de la competencia). **Recomendación v1: no incluir `bd_competition_competencies` para S09** y mostrar las competencias solo en "Mi progreso" como hoy. Decisión D2.

### 2.6 Consulta de reproducción (la misma que usa el backend)

Es `select * from public.bd_competition_units(:run, :session, :as_of)` de §6. Cualquiera con acceso de servicio la ejecuta y obtiene los mismos números que ve el tablero. La consulta de auditoría alias<->nombre está al final de §6.

---

## 3. Acciones de API nuevas (bigdata-session)

Se añaden al despachador (index.ts:839-923). El cliente ya envía todo por POST salvo `me`/`teacher_wall` (bigdata-lms.js:27), así que no requiere cambios de cliente HTTP.

| Acción | Entrada | Salida | Quién |
|---|---|---|---|
| `competition_board` | `{session_number, mode?: "projection"}` | Ver contrato abajo (solo alias) | student, teacher, admin. `mode:"projection"` solo teacher/admin (si no, `NO_AUTH` 403) |
| `teacher_competition_board` | `{session_number}` | Filas con `alias, alias_no, user_id, display_name, units_done, by_component, items[]`, `settings` | teacher, admin (`requireTeacher`). Auditada |
| `teacher_competition_set` | `{session_number, state:"open"\|"hidden", as_of?:ISO\|null, hide_zero?:bool}` | `{ok, settings}` | teacher, admin. Auditada, emite señal Realtime |
| `teacher_competition_rotate` | `{session_number, confirmation:"ROTAR_ALIAS_S09"}` | `{ok, rotated:n}` | teacher, admin. Auditada |
| `me` (existente) | igual | añade `competition_state: "hidden"\|"open"\|"unconfigured"` (solo estado, sin datos) para decidir si mostrar la tarjeta en `session.html` | igual que hoy |

Los tres `teacher_competition_*` se agregan a la lista `teacher` de la línea 864 (así `definition(...)` acepta sesiones en borrador para el docente). `competition_board` usa `definition(run.id, n, false)`: una sesión en `draft` no se puede consultar.

### 3.1 Contrato de `competition_board` para el estudiante

```json
{
  "ok": true,
  "state": "open",
  "session": {"session_number": 9, "title": "..."},
  "rule": {
    "version": 1, "units_total": 17, "speed_tiebreak": false, "tiebreak": "none",
    "components": [{"key":"checkpoint","label":"Checkpoints correctos","total":5},
                   {"key":"lab","label":"LAB con evidencia verificada","total":12}],
    "ignores": ["velocidad","clics","tiempo conectado","mensajes","intentos"]
  },
  "as_of": "2026-10-08T23:30:00Z",
  "participants": 24,
  "rows": [{"position":1,"tied":false,"alias":"Jugador 07","units_done":11,"units_total":17,"is_self":false}],
  "hidden_zero": 3,
  "self": {"alias":"Jugador 12","position":3,"tied":true,"units_done":8,"units_total":17,
           "by_component":[{"key":"checkpoint","done":4,"total":5},{"key":"lab","done":4,"total":12}],
           "pending_review":1}
}
```
Si `state="hidden"` solo devuelve `{ok:true,state:"hidden"}`. Si la sesión no tiene ítems: `state:"unconfigured"`. Modo proyección (docente): en vez de `rows` devuelve `bands:[{units_done:8,aliases:["Jugador 03","Jugador 11"]}]`, sin `self` ni `is_self`.

### 3.2 Cómo se evita exponer datos individuales al estudiante

1. **Mapeador de lista blanca**, en una función aparte (`studentBoardView`) que construye cada fila campo por campo (`position, tied, alias, units_done, units_total, is_self`). Prohibido `{...row}`. A diferencia de `wallList` (index.ts:361), que hace `isTeacher?{...publicPost,user_id}:publicPost`, aquí el dato con identidad nunca entra en la ruta del estudiante.
2. `user_id`, `display_name`, `username`, `email` no existen en el objeto que llega a `studentBoardView`: el cálculo de posiciones se hace con `alias_no` como llave.
3. `is_self` se calcula en el servidor comparando con `ctx.user.id`; el cliente nunca recibe el `user_id` propio dentro del tablero.
4. Sin desglose por componente de otras filas (más detalle = más identificable). Solo `self` lo lleva.
5. La acción no acepta `user_id`, `alias` ni filtros: no hay forma de pedir "quién es X".
6. **Alias no derivable.** El PR #102 usa `sha256(runId|competition|n|userId).slice(0,4)` (competitionAlias, líneas 789-792 de su index.ts): 16 bits sin secreto, con probabilidad de colisión de ~0,7 % en 30 estudiantes (dos "Jugador" iguales) y reversible por cualquiera que conozca los `user_id` de sus compañeros; los `user_id` de los miembros de equipo circulan en el modelo de colaboración. Aquí el alias es aleatorio y almacenado.
7. **Anti-correlación temporal:** el estudiante ve cambiar la fila de otro justo cuando lo ve terminar en clase. Mitigación: los puntajes de las demás filas se calculan con `as_of` redondeado hacia abajo a bloques de 30 s y el cliente sondea cada ~30 s con jitter; `self` se recalcula exacto. El estudiante **no** se suscribe a Realtime (el canal `bigdata:session:N` es `private:false`, lms-realtime.js:33, y una invalidación inmediata es una marca de tiempo para todos).
8. Umbral mínimo de cohorte: si `participants < min_cohort` (por defecto 6) devuelve `state:"too_small"`. Con pocos estudiantes el alias es una máscara, no anonimato (D4).
9. Respuestas ya llevan `Cache-Control: no-store` (index.ts:29).
10. Toda alta/lectura con nombres reales queda en `lms_audit_log`.

---

## 4. UI

### 4.1 Estudiante: `lms/competition-wall.html?s=N`

Página nueva de solo lectura (sin `<textarea>`, sin `<input>` de texto: pasa `validate_no_open_student.py`). Acceso por una tarjeta en `session.html` (cerca de la línea 55) visible cuando `competition_state==="open"`, y opcionalmente un enlace desde `progress.html?s=N`. No va en el header (regla de `validate_student_ux_simple.py:34,42`).

Estructura:
1. `ey` + `h1` "Wall de competencia · SNN". Párrafo de regla en tres frases: qué cuenta (checkpoints correctos y LAB con evidencia verificada), qué no (velocidad, clics, tiempo, intentos), que los empates comparten posición y que los alias cambian en cada sesión.
2. Dos tarjetas: "Tu avance" (`8 de 17`) y "Tu posición" (`3.º · empate con 1 más`).
3. Tabla accesible (`<table>` con `<caption>`, `<th scope="col">`): Posición | Alias | Avance (texto `8/17` + barra) | Marca. La fila propia lleva: borde de 3 px, fondo distinto, texto visible **"Tú"** en la columna Marca, `aria-current="true"` y un `<span class="sr-only">Esta fila eres tú</span>`.
4. Si `hidden_zero>0`: una fila resumen "3 alias sin avance todavía".
5. `PARA LLEVAR` (etiqueta fija de AGENTS §6): "Este tablero resume evidencia ya verificada; no dice cuánto sabes ni prueba que quien va adelante entendió más".
6. `<div id="boardLive" role="status" aria-live="polite" class="sr-only">`: solo se actualiza cuando cambia el avance o la posición **propios** ("Ahora tienes 9 de 17 y estás en 2.º lugar"), no en cada sondeo.

Accesibilidad:
- El color nunca es la única señal: "Tú", "empate", números y texto `8/17`; posición con número, no con medalla. Sin emojis (los que use #102 desaparecen).
- Contraste: texto en `--ink #172033`/`--uc-navy #142153` sobre `#fff` o sobre el fondo de resaltado. `--uc-cyan-text #08777A` sobre blanco da ≈5,4:1 (calculado a mano); no usarlo sobre el fondo de resaltado (≈4,6:1, en el límite). Verificar con axe (ya está en `tests/lms-v3.visual.spec.js:2`, `assertA11y`).
- Barra: `<div role="img" aria-label="8 de 17 ítems verificados">`. Fija color de texto y fondo juntos (AGENTS §6).
- Objetivos táctiles ≥ 44 px (el test `module universal responsive` ya exige `.btn` ≥ 44).
- Móvil: la fila pasa a rejilla de 3 columnas (patrón del `.competition-row` de #102). Sin desborde horizontal (`assertNoHorizontalOverflow`).
- Nada depende del hover. `prefers-reduced-motion`: sin animaciones.
- El CSS del LMS es solo tema claro (`html{color-scheme:light}`, bigdata-lms.css:7), así que no hay tema oscuro que romper; se fija fondo y texto juntos por si se añade.

Actualización: sondeo `competition_board` cada 30 s con jitter y solo si `!document.hidden` (idea de #102), limpieza en `pagehide`.

### 4.2 Modo proyección docente (`?mode=projection`, misma página)

- Solo docente/admin: la página lo valida como `class-wall.html:85` (`projection=projection&&teacher`) **y** el servidor (403 si un estudiante fuerza `mode`).
- Agrupa por bandas: `8/17 · Jugador 03, Jugador 11`. Los empates se ven como el mismo grupo; menos foco en individuos.
- Sin `is_self`, sin nombres, sin controles, sin marcas de tiempo por alias. Botón "Salir de proyección" (patrón de class-wall.html:41 y CSS de la línea 14).
- Tipografía ≥ 1.6rem en filas, contraste máximo, `lang="es"`, `role="status"` `aria-live="polite"` con resumen ("Actualizado; 24 participantes").
- Realtime: esta vista sí se suscribe a `['progress','competition']` con el mismo limitador de 3 s de `wall.html:216-228` y respaldo de sondeo `realtimeReady?60000:15000`. Si el docente proyecta, ve los cambios en 3 s; los estudiantes ven el tablero en bloques de 30 s. (Reflexión de riesgo: quien mira la proyección ve el cambio inmediato de su propia banda; es el precio de una proyección viva, ver D9.)
- Nunca llama a `teacher_competition_board` (la resolución de nombres es otra ventana); un validador lo comprueba.

### 4.3 Cabina docente (`wall.html`)

Sección nueva "Wall de competencia" en `wall.html`: interruptor Abrir/Ocultar para estudiantes, campo de corte `as_of`, botón "Proyectar" (reemplaza el enlace `projectionLink`, wall.html:48 y 146-150), botón "Resolver alias" que abre un `<dialog>` con la tabla alias -> nombre -> desglose (no se proyecta), y "Rotar alias" con frase `ROTAR_ALIAS_S09` (mismo patrón que el reinicio, wall.html:259-261; el `<input>` necesita entrada en `INPUT_ALLOWLIST` de `validate_no_open_student.py`). Mantener la frase "no es un ranking de velocidad" en la línea 36 (la exigen `validate_lms_v3.py:55` y dos pruebas Playwright).

---

## 5. Plan de retiro del muro legacy, paso a paso

Orden lógico: primero existe el reemplazo (PRs A-C de §9), luego se retira el código (D), luego los datos (E). Nunca al revés, porque la migración destructiva no se puede deshacer.

**D1. Backend (`infraestructura/lms/functions/bigdata-session/index.ts`)**
- Borrar `wallPost` (291-325), `wallList` (326-364), `wallReact` (365-379), `wallModerate` (380-389).
- Borrar rutas del despachador (906-909) y `"wall_moderate"` de la lista `teacher` (864).
- `realtimeSignal` (567): cambiar el tipo `"controls"|"wall"|"progress"|"teacher_wall"` a `"controls"|"competition"|"progress"|"teacher_wall"`.
- `publicCatalog` (línea 95): quitar `wall_prompt` del `select` (ya no se usa; se enviaba a todos los estudiantes en `me`).
- `clientId()`/`trimText()` siguen en uso por otros caminos: no borrar.

**D2. Frontend**
- Borrar `lms/class-wall.html`.
- `lms/wall.html`: quitar enlace `projectionLink` (48), `updateProjectionLink` (146-150), su llamada (144), `L.$('controlLab').onchange=updateProjectionLink` (247), y `'wall'` de `scopes` (233). Añadir la sección de §4.3.
- `lms/assets/lms-kit.js`: quitar `wallPost` (212-214), la rama `wall_post` de `deliver` (135-138), `priority` (75), los dos `uid(...)` (116, 185) y el export (270). Subir `version` a `5.2.0` (como #102).

**D3. Cola offline: no atascarse (nuevo, no está en #102)**
En `deliver()` (lms-kit.js:139) sustituir el fallback por:
```js
if(entry.kind==='wall_post')throw Object.assign(new Error('El muro abierto fue retirado'),{status:410,queue_reason:'retired'});
throw Object.assign(new Error('Tipo de cola desconocido'),{status:422,queue_reason:'unknown_kind'});
```
Con `status` 410/422 `retryable()` es falso y `flush` lo pasa a `rejected` (líneas 176-178) sin bloquear la evidencia posterior. Sumar prueba en `utils/test_lms_kit.mjs`.

**D4. Migración SQL V54-B (§6.3).** Se aplica **después** de desplegar la función sin `wall_*` (si no, un cliente viejo insertaría en una tabla inexistente y vería 400). No editar las migraciones históricas (`lms-evidence-v4.sql`, `lms-runtime-v5.sql`, `lms-v51-performance.sql`): re-ejecutar `lms-evidence-v4.sql` recrearía las tablas vacías (`create table if not exists`); anotarlo en la cabecera de la migración nueva. No borrar la columna `bd_activity_catalog.wall_prompt`: la siguen poblando migraciones históricas (`lms-s09-deterministic-v51.sql`, `lms-s09-authentic-evidence-v9.sql:48`) y reejecutarlas fallaría; solo se comenta como obsoleta.

**D5. Datos históricos.** Las filas de `bd_wall_posts` son texto libre de estudiantes. Opción recomendada: V54-B renombra a `bd_wall_posts_archive_v54b` y `bd_wall_reactions_archive_v54b`, revoca todo y se borran en una migración posterior (V54-C) en la fecha que decida el docente; alternativa: exportar a `.local-docente/` (fuera de Git, AGENTS §13) y `drop`. #102 hace `drop table` inmediato sin archivar. Decisión D7.

**D6. CI y documentación.** Actualizar validadores y pruebas (lista siguiente), añadir `test -f _site/lms/competition-wall.html` a `pages.yml` (junto a las líneas 85-88), anotar en `infraestructura/lms/CONTRATO_LMS_V5.md` la superficie nueva y el retiro de `class-wall.html`.

### 5.1 Lista exacta de validadores, pruebas y archivos acoplados

| # | Archivo | Línea(s) | Cambio |
|---|---|---|---|
| 1 | `utils/validate_lms_contract_v5.py` | 25 | Quitar `class_wall=read("lms/class-wall.html")`: `read()` agrega el error "Falta" (líneas 8-12) y fallaría |
| | | 59 | `entry.kind==='evidence'\|\|entry.kind==='wall_post'` -> `entry.kind==='evidence'` |
| | | 65 | Eliminar "idempotencia muro" (exigía `client_post_id`, `bd_wall_posts_client_post_uidx` y `client_post_id:postClientId` en backend) |
| | | 68 | "muro estudiantil sin publicación abierta": pasar a `not (ROOT/"lms/class-wall.html").exists()` y `"wallPost" not in kit` |
| 2 | `utils/validate_lms_evidence_v4.py` | 24 | Quitar `read("lms/class-wall.html")` |
| | | 84 | "muro de clase protegido" (`bd_wall_posts`/`bd_wall_reactions` en lms-evidence-v4.sql): sustituir por comprobar que la migración V54-B archiva o borra ambas tablas |
| | | 103-104 | "muro histórico reservado al docente" y "anonimización histórica" (`publish_first`, `Compañero `, `action==="wall_*"`): invertir a "el backend NO contiene `wall_post/wall_list/wall_react/wall_moderate`, ni `publish_first`, ni `Compañero `" |
| 3 | `utils/validate_lms_v6.py` | 13 | `wall=read("lms/class-wall.html")` -> `lms/competition-wall.html` |
| | | 28 | El SDK local (`assets/vendor/supabase.js?v=2.117.1`) debe estar en `competition-wall.html` (la vista de proyección se suscribe) |
| | | 32 | "fallback polling muro": exigirlo en `competition-wall.html` (`realtimeReady?60000:15000`) |
| | | 37 | `realtimeSignal(n,"wall")` -> `realtimeSignal(n,"competition")` y afirmar que `"wall"` ya no existe en el tipo |
| | | 39-40 | "modo proyección anonimizado"/"proyección sin moderación": reemplazar `body.projection`, `Respuesta '+(index+1)`, `projection&&teacher`, `data-mod` por `mode==='projection'`, validación de rol y ausencia de `display_name`/`user_id` en el camino de proyección |
| | | 44 | "QA V6": esta línea busca el texto "modo proyección anonimiza" en `tests/lms-v6-regression.spec.js`; conservar el título en la nueva prueba o actualizar el texto |
| 4 | `utils/validate_s09_transfer_evidence.py` | 6 | `read_text` directo de `class-wall.html`: lanzaría `FileNotFoundError` |
| | | 18-19 | "muro sin formulario abierto"/"muro solo docente" -> `not exists("lms/class-wall.html")`. Las líneas 16-17 (deck y progreso sin `class-wall.html`) se mantienen |
| 5 | `utils/validate_lms_security_v51.py` | 40 | "muro estudiante no expone user_id" (busca `return isTeacher?{...publicPost,user_id:p.user_id}:publicPost`): reemplazar por "`studentBoardView` no contiene `user_id`, `display_name`, `username` ni `email`" |
| 6 | `utils/validate_no_open_student.py` | 127 | Regex que exige `wallPost(...){ if(!["teacher","admin"]...El muro abierto fue retirado` en backend: pasa a "el backend no define `wallPost` ni la ruta `wall_post`" |
| | | 42-57 | Añadir a `INPUT_ALLOWLIST` `("lms/wall.html","rotateInput")` (frase de rotación) si se usa un `<input>` |
| | | 138-145 | Actualizar comentario "PENDIENTE V54-B" (el muro ya no está pendiente; queda `short_text`) |
| 7 | `utils/validate_session9.py` | 238 | `"class-wall.html" not in student_progress`: sigue cierto; opcional endurecer a `not exists` |
| 8 | `utils/test_lms_kit.mjs` | 97-104 | Test `wallPost usa idempotency key propia`: reemplazar por (a) `LMS.wallPost===undefined`; (b) una entrada `wall_post` sembrada en la cola se descarta con `status:410`, queda en `rejected()` y **no** bloquea una evidencia posterior |
| 9 | `tests/lms-v3.visual.spec.js` | 136, 144-147 | Quitar `wallPublished` y los mocks `wall_post`/`wall_list` (código muerto). Las pruebas de `wall.html` docente (222-231, 265-271) se conservan |
| 10 | `tests/lms-v6-regression.spec.js` | 34, 45-47 | Quitar parámetro `wallPosts` y mock `wall_list` |
| | | 89-102 | Reescribir la prueba "modo proyección anonimiza y oculta administración" contra `competition-wall.html?mode=projection` |
| 11 | `utils/validate_realtime_scale.py` | 4, 12-14 | Sin cambio (mide `wall.html`); confirmar que el throttle de 3 s sigue en `wall.html` |
| 12 | `utils/validate_lms_v3.py`, `validate_lms_s08.py`, `validate_lms_admin.py`, `validate_lms_security_v51.py` (líneas 62-64), `validate_session9.py` (217-244) | varias | Sin cambio: tocan `wall.html`/`teacher_wall`/deck, no el muro abierto. Solo verificar que no se pierda "no es un ranking de velocidad" ni `<th>Posición</th>` en el deck |
| 13 | `infraestructura/lms/lms-evidence-v4.sql` (117-145), `lms-runtime-v5.sql` (11-12, 26-30, 40-42, 48-49), `lms-v51-performance.sql` (10-22), `lms-v6-live-controls.sql` (41: `check ... 'wall'`) | | **No se editan** (historia). Se cubren con la migración V54-B. El `check` de `bd_realtime_signals.scope` es de una tabla legacy vacía |
| 14 | `.github/workflows/lms-s08-qa.yml` | ~13-54 y ~61-101 (dos listas `paths`), ~217 (pasos) | Añadir `utils/validate_competition_wall.py` en ambas listas y un paso `python utils/validate_competition_wall.py` |
| | `.github/workflows/pages.yml` | 85-88 | Añadir `test -f _site/lms/competition-wall.html` |
| 15 | `lms/data/course.json` | 144-151 | Sin cambio (los "WALL" ahí son cabinas docentes) |

Guardia de retiro (para no volver a introducirlo): en el validador nuevo, `git grep -E "wall_post|wall_list|wall_react|wall_moderate|wallPost|class-wall|bd_wall_"` fuera de `infraestructura/lms/*.sql` históricos y de la migración V54-B debe dar 0.

---

## 6. Migración SQL propuesta (esquema; NO ejecutada)

Archivos sugeridos: `infraestructura/lms/lms-v55-competition-wall.sql` (crea) y `infraestructura/lms/lms-v54b-retire-open-wall.sql` (retira). Escritos a mano contra las migraciones leídas; no fueron probados en ninguna base.

### 6.1 Creación (idempotente)

```sql
-- V55 · Wall de competencia: tablero estructurado con alias por sesión.
-- Idempotente. Solo service_role. Sin datos de estudiantes ni texto libre.

create table if not exists public.bd_competition_items(
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  activity_code text not null references public.bd_lms_activities(code) on delete cascade,
  item_kind text not null check (item_kind in ('checkpoint','lab')),
  position smallint not null default 0,
  primary key (course_run_id, session_number, activity_code)
);

create table if not exists public.bd_competition_competencies(
  course_run_id uuid not null,
  session_number smallint not null check (session_number between 1 and 99),
  competency_code text not null,
  primary key (course_run_id, session_number, competency_code),
  foreign key (course_run_id, competency_code)
    references public.lms_competencies_v2(course_run_id, code) on delete cascade
);

create table if not exists public.bd_competition_settings(
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  state text not null default 'hidden' check (state in ('hidden','open')),
  as_of timestamptz null,
  hide_zero boolean not null default true,
  min_cohort smallint not null default 6 check (min_cohort between 1 and 99),
  rule_version smallint not null default 1,
  opened_at timestamptz null,
  updated_by uuid null references public.lms_users(id) on delete set null,
  updated_at timestamptz not null default now(),
  primary key (course_run_id, session_number)
);

create table if not exists public.bd_competition_aliases(
  course_run_id uuid not null references public.lms_course_runs(id) on delete cascade,
  session_number smallint not null check (session_number between 1 and 99),
  user_id uuid not null references public.lms_users(id) on delete cascade,
  alias_no smallint not null check (alias_no between 1 and 999),
  created_at timestamptz not null default now(),
  primary key (course_run_id, session_number, user_id),
  unique (course_run_id, session_number, alias_no)
);
create index if not exists bd_competition_aliases_user_idx on public.bd_competition_aliases(user_id);
create index if not exists bd_competition_items_activity_idx on public.bd_competition_items(activity_code);

do $$
declare t text;
begin
  foreach t in array array['bd_competition_items','bd_competition_competencies','bd_competition_settings','bd_competition_aliases']
  loop
    execute format('alter table public.%I enable row level security', t);
    execute format('revoke all on table public.%I from anon, authenticated', t);
    execute format('drop policy if exists %I on public.%I', t||'_no_direct_access', t);
    execute format('create policy %I on public.%I for all to anon, authenticated using (false) with check (false)', t||'_no_direct_access', t);
    execute format('grant select, insert, update, delete on table public.%I to service_role', t);
  end loop;
end $$;

comment on table public.bd_competition_aliases is
  'Mapa alias->estudiante por sesión. Sensible: solo lectura por Edge Function con rol docente, nunca en snapshots ni respuestas a estudiantes.';

-- Alias aleatorios, asignados una vez por sesión (rotan por sesión porque cada sesión es una permutación independiente).
create or replace function public.bd_competition_ensure_aliases(p_run uuid, p_session smallint)
returns integer
language plpgsql
set search_path = public
as $$
declare v_added integer := 0; v_students integer;
begin
  perform pg_advisory_xact_lock(hashtextextended(p_run::text||':'||p_session::text, 0));
  select count(*) into v_students
  from public.lms_run_enrollments e join public.lms_users u on u.id=e.user_id and u.active
  where e.course_run_id=p_run and e.role='student' and e.status='active';

  with missing as (
    select e.user_id, row_number() over (order by gen_random_uuid()) as rn
    from public.lms_run_enrollments e join public.lms_users u on u.id=e.user_id and u.active
    where e.course_run_id=p_run and e.role='student' and e.status='active'
      and not exists (select 1 from public.bd_competition_aliases a
                      where a.course_run_id=p_run and a.session_number=p_session and a.user_id=e.user_id)
  ), pool as (
    select n, row_number() over (order by gen_random_uuid()) as rn
    from generate_series(1, greatest(20, 2*v_students)) as n
    where n not in (select alias_no from public.bd_competition_aliases
                    where course_run_id=p_run and session_number=p_session)
  )
  insert into public.bd_competition_aliases(course_run_id, session_number, user_id, alias_no)
  select p_run, p_session, m.user_id, p.n::smallint from missing m join pool p using (rn);
  get diagnostics v_added = row_count;
  return v_added;
end $$;

-- Puntaje: solo evidencia objetiva. Sin attempts, active_seconds, eventos ni horas de entrega (salvo el corte as_of).
create or replace function public.bd_competition_units(p_run uuid, p_session smallint, p_as_of timestamptz default now())
returns table(
  user_id uuid, units_done integer, units_total integer,
  checkpoints_done integer, checkpoints_total integer,
  labs_done integer, labs_total integer,
  competencies_done integer, competencies_total integer,
  labs_pending_review integer)
language sql stable
set search_path = public
as $$
  with students as (
    select e.user_id from public.lms_run_enrollments e
    join public.lms_users u on u.id=e.user_id and u.active
    where e.course_run_id=p_run and e.role='student' and e.status='active'
  ), items as (
    select i.activity_code, i.item_kind, c.evaluator
    from public.bd_competition_items i
    join public.bd_lms_activities a on a.code=i.activity_code and a.session_number=i.session_number
    left join public.bd_activity_catalog c on c.code=i.activity_code
    where i.course_run_id=p_run and i.session_number=p_session
  ), cp as (
    select distinct p.user_id, p.activity_code
    from public.bd_lms_activity_progress p
    join items i on i.activity_code=p.activity_code and i.item_kind='checkpoint'
    where p.course_run_id=p_run
      and (p.metadata->>'mastery')='true'
      and p.completed_at is not null and p.completed_at<=p_as_of
  ), lb as (
    select distinct e.user_id, e.activity_code
    from public.bd_evidence e
    join items i on i.activity_code=e.activity_code and i.item_kind='lab'
    where e.course_run_id=p_run and e.session_number=p_session
      and coalesce(e.reviewed_at,e.created_at)<=p_as_of
      and ((e.verdict='correct' and i.evaluator in ('choice-hash','seeded-numeric'))
        or (e.verdict='accepted' and e.reviewed_by is not null))
  ), lp as (
    select distinct e.user_id, e.activity_code
    from public.bd_evidence e join items i on i.activity_code=e.activity_code and i.item_kind='lab'
    where e.course_run_id=p_run and e.session_number=p_session and e.verdict='pending_review'
  ), latest as (   -- misma regla que computeCompetencyRows: última evidencia aceptada con rúbrica por actividad
    select distinct on (e.user_id, e.activity_code)
           e.user_id, e.activity_code,
           least(100, greatest(0, 100.0*(e.rubric->>'total')::numeric/nullif((e.rubric->>'max')::numeric,0))) as pct
    from public.bd_evidence e
    where e.course_run_id=p_run and e.verdict='accepted' and e.rubric is not null
      and coalesce(e.reviewed_at,e.created_at)<=p_as_of
      and e.activity_code in (select activity_code from public.lms_activity_competencies_v2 where course_run_id=p_run)
    order by e.user_id, e.activity_code, coalesce(e.reviewed_at,e.created_at) desc
  ), cm as (
    select l.user_id, m.competency_code,
           count(*) as n, sum(l.pct*m.weight)/nullif(sum(m.weight),0) as mastery_pct
    from latest l
    join public.lms_activity_competencies_v2 m on m.course_run_id=p_run and m.activity_code=l.activity_code
    join public.bd_competition_competencies bc on bc.course_run_id=p_run and bc.session_number=p_session
                                              and bc.competency_code=m.competency_code
    group by l.user_id, m.competency_code
  ), cd as (
    select cm.user_id, count(*) as done
    from cm join public.lms_competencies_v2 c on c.course_run_id=p_run and c.code=cm.competency_code and c.active
    where cm.n>=c.min_evidence_count and cm.mastery_pct>=c.mastery_threshold
    group by cm.user_id
  ), tot as (
    select (select count(*) from items where item_kind='checkpoint')::int as t_cp,
           (select count(*) from items where item_kind='lab')::int as t_lb,
           (select count(*) from public.bd_competition_competencies
             where course_run_id=p_run and session_number=p_session)::int as t_cm
  )
  select s.user_id,
         (coalesce(a.n,0)+coalesce(b.n,0)+coalesce(d.done,0))::int,
         (t.t_cp+t.t_lb+t.t_cm)::int,
         coalesce(a.n,0)::int, t.t_cp, coalesce(b.n,0)::int, t.t_lb,
         coalesce(d.done,0)::int, t.t_cm,
         coalesce(pr.n,0)::int
  from students s cross join tot t
  left join (select user_id, count(*) n from cp group by user_id) a on a.user_id=s.user_id
  left join (select user_id, count(*) n from lb group by user_id) b on b.user_id=s.user_id
  left join cd d on d.user_id=s.user_id
  left join (select lp.user_id, count(*) n from lp
             where not exists (select 1 from lb where lb.user_id=lp.user_id and lb.activity_code=lp.activity_code)
             group by lp.user_id) pr on pr.user_id=s.user_id;
$$;

revoke all on function public.bd_competition_ensure_aliases(uuid, smallint) from public, anon, authenticated;
revoke all on function public.bd_competition_units(uuid, smallint, timestamptz) from public, anon, authenticated;
grant execute on function public.bd_competition_ensure_aliases(uuid, smallint) to service_role;
grant execute on function public.bd_competition_units(uuid, smallint, timestamptz) to service_role;

-- Ítems S09 (5 checkpoints + 12 LAB). Competencias: vacío en v1 (ver decisión D2).
insert into public.bd_competition_items(course_run_id, session_number, activity_code, item_kind, position)
select r.id, 9, x.code, x.kind, x.pos
from public.lms_course_runs r
cross join (values
  ('bd-s09-c1','checkpoint',1),('bd-s09-c2','checkpoint',2),('bd-s09-c3','checkpoint',3),
  ('bd-s09-c4','checkpoint',4),('bd-s09-c5','checkpoint',5),
  ('bd-s09-lab1','lab',6),('bd-s09-lab-e5','lab',7),('bd-s09-lab-chunk','lab',8),('bd-s09-lab2','lab',9),
  ('bd-s09-lab3','lab',10),('bd-s09-lab4','lab',11),('bd-s09-lab5','lab',12),('bd-s09-lab6','lab',13),
  ('bd-s09-lab7','lab',14),('bd-s09-lab8','lab',15),('bd-s09-lab-eval','lab',16),('bd-s09-lab9','lab',17)
) as x(code,kind,pos)
where r.code='bigdata-2026-2'
on conflict (course_run_id, session_number, activity_code) do update set item_kind=excluded.item_kind, position=excluded.position;
```

Notas de esquema:
- `create or replace function` y `create table if not exists` hacen la migración re-ejecutable. Las tablas se crean aunque ya tengan datos.
- `pg_advisory_xact_lock` evita que dos llamadas concurrentes (dos estudiantes abriendo el tablero a la vez) asignen el mismo alias; la restricción `unique` es la segunda red.
- Faltó definir aquí (queda en el backend): `position = rank() over (order by units_done desc)`, agrupamiento `hide_zero` y el redondeo de `as_of` a 30 s para las filas ajenas.

### 6.2 Consulta de auditoría (resolver alias; solo con credenciales de servicio)

```sql
select 'Jugador '||lpad(a.alias_no::text,2,'0') as alias, u.display_name, u.username,
       s.units_done, s.units_total,
       rank() over (order by s.units_done desc) as position
from public.bd_competition_units(:run, 9::smallint, :as_of) s
join public.bd_competition_aliases a on a.course_run_id=:run and a.session_number=9 and a.user_id=s.user_id
join public.lms_users u on u.id=s.user_id
order by position, a.alias_no;
```

### 6.3 Retiro (V54-B, aplicar después de desplegar la función sin `wall_*`)

```sql
-- V54-B · Retiro del muro abierto. Precondición: backend sin wall_*; texto de estudiantes ya archivado/exportado si se desea.
-- No re-ejecutar lms-evidence-v4.sql después de esta migración: recrearía las tablas vacías.
do $$
begin
  if to_regclass('public.bd_wall_posts') is not null and to_regclass('public.bd_wall_posts_archive_v54b') is null then
    alter table public.bd_wall_posts rename to bd_wall_posts_archive_v54b;
  end if;
  if to_regclass('public.bd_wall_reactions') is not null and to_regclass('public.bd_wall_reactions_archive_v54b') is null then
    alter table public.bd_wall_reactions rename to bd_wall_reactions_archive_v54b;
  end if;
end $$;

do $$
declare t text;
begin
  foreach t in array array['bd_wall_posts_archive_v54b','bd_wall_reactions_archive_v54b']
  loop
    if to_regclass('public.'||t) is not null then
      execute format('revoke all on table public.%I from anon, authenticated', t);
      execute format('revoke insert, update, delete on table public.%I from service_role', t);
    end if;
  end loop;
end $$;

comment on column public.bd_activity_catalog.wall_prompt is
  'OBSOLETA desde V54-B: el muro abierto fue retirado. No se elimina porque migraciones históricas la siguen poblando.';
-- V54-C (fecha a decidir por el docente): drop table if exists public.bd_wall_reactions_archive_v54b, public.bd_wall_posts_archive_v54b;
```
Las FK de `bd_wall_reactions -> bd_wall_posts` siguen válidas tras el `rename`. La versión "borrado inmediato" de #102 (`drop table if exists ...`) equivale a saltar directamente a V54-C.

---

## 7. Plan de pruebas

Marco de pruebas existente: validadores Python (`lms-s08-qa.yml`), `node --test utils/test_lms_kit.mjs`, Playwright con backend simulado (`playwright.config.js`; servidor estático en el puerto 4173) y axe. No hay arnés de pruebas para Deno/Edge ni base de datos en CI (comprobado: no lo encontré). Lo que sigue distingue lo que cabe en el CI de hoy de lo que requiere staging.

### 7.1 Positivas

- P1 (Playwright, `tests/lms-v55-competition-wall.spec.js`, base: `student-competition-wall.spec.js` de #102): con `competition_board` simulado, la fila propia dice "Tú", `aria-current`, texto `8/17`, mención de empates, cero `textarea`, cero enlaces a `class-wall.html`.
- P2: `state:"hidden"` muestra "Aún no está abierto", sin filas.
- P3: proyección con docente: bandas, sin "Tú", sin nombres, botón de salida visible.
- P4: sin desborde horizontal en móvil/escritorio (`assertNoHorizontalOverflow`) y `AxeBuilder` sin violaciones serias en ambos modos.
- P5 (SQL fixture, staging): `bd_competition_units` con 3 estudiantes y evidencias sembradas reproduce números esperados; `rank()` da 1,2,2,4 con empates.

### 7.2 Negativas (que el estudiante NO vea nombres reales ni datos ajenos)

| # | Prueba | Cómo |
|---|---|---|
| N1 | UI no renderiza identidad aunque llegue | Playwright: el mock devuelve filas con `display_name`, `user_id`, `username`, `email` (backend defectuoso simulado); afirmar que ningún texto del DOM ni atributo contiene esos valores |
| N2 | Mapeador sin identidad | Validador estático: el cuerpo de `studentBoardView` no contiene `user_id`, `display_name`, `username`, `email`, ni `...row` |
| N3 | Estudiante no llama acciones docentes | Playwright: recolectar `sent`; el conjunto de acciones de la página de estudiante es un subconjunto de `{me, competition_board, track}`; nunca `teacher_competition_*` |
| N4 | Proyección forzada por estudiante | Playwright con rol estudiante + `?mode=projection`: la página redirige/oculta y el mock devuelve 403; no se pinta tablero. Backend (staging): `curl` con token de estudiante y `mode:"projection"` -> 403 |
| N5 | Puntaje sin señales prohibidas | Validador estático sobre `bd_competition_units` y sobre la función TS del tablero: ausencia de `attempts`, `active_seconds`, `last_activity_at`, `started_at`, `bd_lms_events`, `first_attempt_correct`, `heartbeat`; presencia de `speed_tiebreak:false` y `tiebreak:"none"` |
| N6 | Invariancia (SQL fixture, staging) | Dos estudiantes con la misma evidencia y distintos `attempts`/`active_seconds`/horas: mismo `units_done` y misma posición. "5 fallos y luego acierto" == "acierto a la primera" |
| N7 | Qué no cuenta (SQL fixture) | `incorrect`, `pending_review`, `rejected`, `accepted` sin `reviewed_by`, checkpoint sin `mastery`, evidencia posterior a `as_of`: ninguno suma |
| N8 | Alias únicos y no derivados (SQL fixture) | `unique(run,session,alias_no)`; llamar `ensure` dos veces no cambia nada; tras borrar y regenerar, el mapeo cambia (prueba probabilística con N≥20); ningún alias es función del `user_id` (grep estático: sin `sha256`/`hash` en su generación) |
| N9 | Autorización en el servidor | Staging con dos tokens (docente y estudiante, entregados por el docente y no guardados en el repo): estudiante -> `teacher_competition_board/set/rotate` = 403 `No autorizado`. En CI solo cabe el humo sin token: `POST /bigdata-session` con `competition_board` sin `Authorization` -> 401 (mismo estilo que el paso "Smoke endpoints BigData" de `lms-s08-qa.yml:222-235`) |
| N10 | Resolución auditada | Validador estático: `teacher_competition_board` contiene `requireTeacher(ctx)` y `audit(...,"bigdata.competition.resolve"...` |
| N11 | Sin Realtime del estudiante | Validador estático: `competition-wall.html` solo llama `LMSRealtime.subscribe` dentro de la rama `mode==='projection'` |
| N12 | Retiro completo | La guardia de `git grep` de §5.1 da 0 coincidencias; `class-wall.html` no existe |
| N13 | Cola no se atasca | `test_lms_kit.mjs` con un `wall_post` sembrado seguido de una evidencia: la evidencia se entrega |
| N14 | Parámetros manipulados | `?s=abc`, `?s=0`, `?s=9&a=x` -> redirección a `portal.html` (como el patrón `sessionNumber<1`, wall.html:93) |
| N15 | Sin texto libre nuevo | `validate_no_open_student.py` sigue en verde con la página nueva (0 textarea, 0 input de texto) |

### 7.3 No verificado

No ejecuté ninguna prueba ni consulta. Sin acceso a la base viva no pude confirmar: tamaño real de la cohorte, si existen cuentas QA/docentes con rol `student`, qué filas de `bd_evidence.reviewed_by` están pobladas, el estado real de `BD-E7`, ni cómo se despliegan las Edge Functions (no hay paso de despliegue en `.github/workflows/`). Estos puntos se deben confirmar en staging antes de abrir el tablero.

---

## 8. Riesgos y decisiones del docente

### Riesgos

| Riesgo | Nivel | Mitigación |
|---|---|---|
| Desanonimización por contexto: en un grupo pequeño el alias es seudónimo, no anonimato; el estudiante sabe quién terminó y ve cambiar una fila | Alto | `min_cohort`, tablero en bloques de 30 s, colapsar ceros, sin timestamps por alias, aviso explícito a los estudiantes |
| Alias derivables (variante #102) | Alto | Alias aleatorio almacenado; prohibido hash del `user_id` |
| Tabla de alias filtrada | Medio | Solo `service_role`, RLS de negación, fuera de snapshots (el ops snapshot arma tablas explícitas, bigdata-lms-ops/index.ts:112,201; confirmar que no la incluya) |
| Cola offline atascada al retirar `wall_post` | Medio | §5, D3 |
| Orden de despliegue: Pages publica el frontend al hacer merge, las Edge Functions se despliegan aparte (no vi automatización) | Medio | Orden: SQL A -> función -> frontend; V54-B al final; `me` devuelve `competition_state` para que la UI no dependa de que la función ya exista (si falta, `unconfigured`) |
| La gamificación distorsiona el aprendizaje (medallas, presión) | Medio | Sin medallas, "empate" explícito, mensaje "esto no mide cuánto sabes", opción de ocultar |
| Latencia de revisión docente mueve posiciones (lab9) | Medio | Mostrar "en revisión" al propio estudiante; decidir si `authentic-review` cuenta (D8) |
| Deuda de validadores: 8 archivos acoplados | Bajo | §5.1 en un solo PR con el retiro |
| Datos históricos de muro con texto libre | Medio | Archivar y borrar por fecha (D7) |

### Decisiones que debe tomar el docente

- **D1. Visibilidad:** ¿el tablero nace oculto y el docente lo abre por sesión (recomendado) o siempre visible? ¿Se muestra durante evaluaciones (S08)? Recomiendo apagado en sesiones evaluativas.
- **D2. Qué cuenta en S09:** ¿5 checkpoints + 12 LAB = 17 (recomendado), o solo un subconjunto? ¿Incluir competencias? Hoy BD-E7 exige 2 evidencias y solo existe 1 camino; corregirlo requiere bajar `min_evidence_count` a 1 o remapear (decisión curricular).
- **D3. Alias con cero avance:** ¿colapsados en una línea (recomendado) o visibles?
- **D4. Tamaño mínimo de cohorte** para mostrar el tablero (propuesta: 6).
- **D5. Estilo de alias** ("Jugador NN") y si se acepta el aviso a estudiantes de que el docente puede resolverlo.
- **D6. Rotación:** por sesión (automática) más rotación manual; ¿también al reiniciar la sesión?
- **D7. Histórico del muro:** archivar y borrar en fecha X, o exportar a `.local-docente/` y borrar ya. Retención de la tabla de alias (¿se elimina al terminar el curso?).
- **D8. Evidencia con revisión humana:** ¿`authentic-review` cuenta solo al aceptarla (propuesto) o también al enviarla?
- **D9. Proyección en vivo (3 s) vs. bloques de 30 s** para reducir la correlación en el aula.
- **D10. Exclusiones:** cuentas de prueba/QA, docentes matriculados como estudiante, estudiantes retirados.
- **D11. Uso formativo:** confirmar que el tablero no alimenta el gradebook ni la nota (regla propuesta: nunca).
- **D12. Texto de aviso a estudiantes** sobre qué se muestra y a quién (transparencia; AGENTS §13).

---

## 9. Orden recomendado en PRs pequeños y esfuerzo

Esfuerzo en días de desarrollo con revisión, sin contar espera de decisiones ni ejecución en staging.

| PR | Contenido | Depende de | Esfuerzo |
|---|---|---|---|
| **A. Esquema y puntaje** | `lms-v55-competition-wall.sql` (§6.1) + `utils/validate_competition_wall.py` (estático: RLS/grants, funciones sin `execute` para anon, sin columnas prohibidas) + fixture SQL manual | Decisiones D2, D4 | 0,5-1 |
| **B. Backend** | Acciones `competition_board`, `teacher_competition_board/set/rotate`, `studentBoardView`, `competition_state` en `me`, señal `competition`; humo 401 en CI | A aplicada en staging | 1-1,5 |
| **C. Frontend** | `competition-wall.html` (estudiante + proyección), tarjeta en `session.html`, sección en `wall.html` (abrir/ocultar, proyectar, resolver, rotar), `INPUT_ALLOWLIST`, prueba Playwright con negativas N1-N4, N11, N14, N15, axe | B desplegada | 1-1,5 |
| **D. Retiro de código** | §5 D1-D3, D6 y toda la tabla 5.1, prueba de cola N13, guardia N12 | C en producción | 0,5-1 |
| **E. Retiro de datos** | `lms-v54b-retire-open-wall.sql` (§6.3), anotación en CONTRATO/RUNBOOK; V54-C (borrado) en la fecha decidida | D desplegado; D7 decidida | 0,25 + verificación |

Total estimado: 3,25 a 5 días. PR A, B y C son aditivos y reversibles (las tablas nuevas están vacías hasta que el docente abre un tablero); D y E son los que no se deshacen fácilmente y por eso van al final.

Ruta de humo manual antes de abrir a estudiantes (con credenciales que solo tiene el docente): (1) `bd_competition_units` con `as_of` de hoy y comparar con la cabina `wall.html`; (2) abrir el tablero con una cuenta de estudiante de prueba y comprobar que la respuesta JSON no contiene ningún nombre ni `user_id` (leer la respuesta cruda en la pestaña de red); (3) probar `teacher_competition_board` con esa cuenta y ver 403.

---

## 10. Qué del PR #102 merece portarse

`git diff origin/main...origin/fix/student-ux-no-open-wall-v2 --stat`: 26 archivos, 481+/443-. Rama divergida: **no se fusiona**, solo se toman ideas.

| Idea de #102 | Veredicto | Comentario |
|---|---|---|
| Nombre y contrato `competition_wall` con `privacy:{identity:"alias",open_responses:false,speed_tiebreak:false}` | Portar la idea | Aquí como bloque `rule` (más explícito) y con nombres nuevos (`competition_board`) |
| Ranking de competencia con posición compartida en empates (index.ts:826-833 de su versión) | Portar la regla | `rank()` en vez de recorrer filas; la nota "Los empates comparten posición" (progress.html) |
| `progress.html` con sección `#competitionWall`, enlace desde el portal, `defaultFocus()` por `starts_at`, botón Actualizar | Portar parcialmente | Página propia en lugar de inflar `progress.html`; reutilizar `defaultFocus()` para elegir sesión y el enlace del portal si el docente lo quiere (cuidado con `validate_student_ux_simple.py`) |
| Sondeo de 20 s con `if(!document.hidden)` y limpieza en `pagehide` | Portar | Ajustado a 30 s con jitter |
| CSS de filas (`.competition-row`, `.me`, rejilla móvil) | Portar y corregir | Añadir texto "Tú" y `aria-current`; quitar medallas |
| Quitar `wallPost`/`wall_post` de `lms-kit.js` (`version 5.2.0`) | Portar **con el arreglo de la cola** (§5 D3) | Su versión reintroduce el atasco de la cola |
| Prueba `student-competition-wall.spec.js` (rutas simuladas por acción, `getByText('Jugador 1B4F · Tú')`, `textarea` = 0, sin `class-wall.html`) | Portar el esqueleto | Añadir las negativas N1-N4 |
| `validate_student_ux_v53.py`: comprobaciones "class-wall eliminado", "sin enlaces class-wall", "sin wall API abierto", `speed_tiebreak:false` | Portar solo las de muro/alias | Las demás comprueban cambios ajenos (quizzes, colaboración, notebook) |
| Alias `Jugador `+`sha256(run|competition|n|user)[0:4]` | **No portar** | Colisiones, derivable, sin resolución docente ni rotación forzada |
| Puntaje por actividades `required` con `status==="completed"` | **No portar** | Incluye recursos que nunca completan, ignora `bd_evidence`/verdict, excluye LAB no `required`, `attempted_required` expone actividad ajena |
| Exposición de `status`/`attempted_required` de otros | **No portar** | Más identificable y basado en actividad |
| Medallas 1-3 | **No portar** | Refuerza la competencia por velocidad percibida |
| `lms-student-no-open-responses-v53.sql`: `drop table` inmediato + cambios a `lms_questions_v2`, `lms_assignments_v2`, peer review | **No portar en este alcance** | Mezcla temas; el `drop` sin archivo no es reversible |
| Cambios en `bigdata-lms-core/assess`, colaboración, notebook LAB9 estructurado, `course.json` | **Fuera de alcance** | Son otros frentes (V54-A/B de respuestas abiertas) |

---

## Fuentes revisadas (archivo:línea)

Backend: `infraestructura/lms/functions/bigdata-session/index.ts` (1-923; clave: 91-100, 110-254, 291-389, 400-423, 456-475, 535-566, 567-586, 601-655, 712-791, 793-818, 839-923); `bigdata-lms-core/index.ts:395-495` (competencias). Frontend: `lms/wall.html`, `lms/class-wall.html`, `lms/session.html`, `lms/progress.html`, `lms/assets/lms-kit.js`, `lms-realtime.js`, `bigdata-lms.js:27,56`, `bigdata-lms.css`. SQL: `bigdata-lms-s08.sql`, `lms-session-engine-v3.sql`, `lms-runtime-v5.sql`, `lms-evidence-v4.sql`, `lms-v6-live-controls.sql`, `lms-competencies-v2.sql`, `lms-s09-*` (v9, v10, v11, v51, v52, v14), `lms-v54a-no-open-student.sql`, `s09-vector-search-seed.sql`. Validadores/pruebas: los listados en §5.1 más `validate_student_ux_simple.py`, `validate_lms_v3.py`, `validate_session9.py`, `tests/lms-v54a-no-open.spec.js`, `.github/workflows/{lms-s08-qa,lms-visual-qa,pages}.yml`. PR #102: `git show origin/fix/student-ux-no-open-wall-v2:` (index.ts 789-848, progress.html, lms-kit.js, spec, validador, migración V53).
