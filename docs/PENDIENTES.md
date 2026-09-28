# Pendientes del repositorio y del LMS

Lista viva de lo que **quedó sin hacer** después de los cambios V54-A, V54-B y V56-A, en orden de urgencia. Se actualiza al cerrar cada punto (bórralo al terminarlo, no lo tachues). Lo que cambia cada semana del curso vive en `.local-docente/`, fuera de Git.

Lo ya hecho (PR #104–#109, todos fusionados y cerrados): portada alineada con `course.json`; sin texto libre del estudiante en LMS, LAB9 S09 ni Quiz Neo4j; tipos de pregunta unificados; distractores S09 22/22; higiene, `npm ci` y escáner de secretos. Las guardias son `utils/validate_no_open_student.py`, `utils/validate_s09_distractors.py`, `utils/check_repo_hygiene.py` y `utils/scan_secrets_pii.py`.

## 1. Antes de la clase del 1 de octubre (bloqueantes)

El frontend y el backend V54 quedaron alineados el 28-09-2026: se desplegaron `bigdata-lms-core`, `bigdata-session`, `bigdata-lms-assess` y `bigdata-lms-interop`, y se aplicaron las migraciones V54-A, V54-B y V55. Quedan estos bloqueantes operativos:

- [ ] **Rotar las credenciales de Atlas expuestas.** `Cuadernos/8_NoSQL_Mongo.ipynb` contiene dos URIs con contraseña de aspecto real, versionadas desde 2023-11-02 en `main` y en todas las ramas. En Atlas: eliminar o rotar esos usuarios de base de datos y revisar la lista de IPs permitidas. Después sustituirlas por un marcador en el cuaderno y **borrar la excepción `KNOWN` correspondiente** en `utils/scan_secrets_pii.py` (el escáner la muestra como aviso urgente en cada CI). Quitarlas del árbol no las borra del historial.
- [ ] **Decisión sobre el TC1:** el rol de contribución individual solo se registra en `collaboration.html`, que ni el portal ni `session-08.html` enlazan. Decidir si esos roles cuentan para repartir nota (entonces enlazarlos desde la sesión 8 o mover el selector allí) o si se descartan.
- [ ] **Canal de dudas durante el taller:** el estudiante ya no puede escribir en la plataforma. Decir por dónde pregunta y ponerlo en «Comunicados del docente».
- [ ] Probar con una cuenta de **docente** lo que solo se probó con backend simulado: publicar comunicado y responder en `teacher-collaboration.html`.

## 2. Antes de la clase del 8 de octubre (S09)

- [ ] **El PDA vigente de 2026.** El PDF que hay en el repo es el PDA **2023-I**; el archivo `PDA_2026-02_BIGDATA.pdf` recibido después es idéntico byte a byte. Subir el PDA vigente y actualizar `docs/PDA_guia.md` (porcentajes de evaluación, temas y las diferencias con `course.json`).
- [ ] **Profundización S09, solo si añade valor neto:** quedaron como ideas históricas cinco ampliaciones (Laboratorio integrado, Vector por dentro, Distancia y similitud, Persistencia en MongoDB, Recall vs Precision). No hay PR pendiente asociado. Evaluar únicamente «Vector por dentro» y «Recall vs Precision» contra la dosis de `AGENTS.md` §2 y descartarlas si duplican lo ya publicado.

## 3. Wall de competencia (funcionalidad nueva)

Tablero **estructurado** de progreso de clase, no un foro: alias «Jugador NN» que rotan por sesión, puntaje solo por evidencia objetiva y sin desempate por velocidad. **Diseño completo en [`diseno-wall-competencia.md`](diseno-wall-competencia.md)** (modelo de datos, puntaje reproducible, API, UI, retiro del muro legacy con la lista exacta de validadores acoplados, SQL propuesto sin ejecutar, pruebas, riesgos y 5 PR).

- [ ] **Responder las 12 decisiones de la §8 antes de construir**, en especial D1 (visibilidad; apagado en sesiones evaluativas), D2 (qué cuenta en S09), D4 (cohorte mínima) y D8 (¿cuenta un LAB en revisión?).
- [ ] Construir en 5 PR (unos 3,25 a 5 días): A esquema y puntaje, B backend, C frontend, D retiro de código, E retiro de datos. A–C son aditivos; D y E no se deshacen.
- Hallazgos que cambian el plan: al quitar `wall_post` de `lms-kit.js` una cola offline pendiente puede atascarse (devolver 410/422 en `deliver()`); la competencia BD-E7 exige 2 evidencias y solo un LAB puede aportarla, así que no incluir competencias en el puntaje de S09 v1; `accepted` no siempre significa verificado; los recursos «visitar» nunca llegan a `completed`, por eso el puntaje de #102 no sirve tal cual.
- No reutilizar el diseño legado de alias por hash corto, puntaje por `required` ni retiro inmediato de tablas: el diseño vigente es `docs/diseno-wall-competencia.md`.

## 4. Peso del repositorio y datos

Hoy hay ~413 MB en 5 archivos que la guardia `check_repo_hygiene.py` lista con su razón y que **solo pueden disminuir**.

- [ ] **`Airflow/dw.duckdb` (50 MB):** no basta quitarlo. DuckDB **rechaza un archivo vacío** y el compose lo monta como archivo (si falta, Docker crea un directorio). Solución: montar un directorio, cambiar `DB_PATH` del DAG y **probarlo con Docker**.
- [ ] **CSV de SECOP (3 × ~100 MB) y `part_04.csv` (65 MB):** varios cuadernos los descargan desde `main`. Publicar como GitHub Release, dejar en Git un `manifest.json` (URL, SHA256, tamaño, fuente, fecha, script generador) y muestras pequeñas; **actualizar los enlaces de los cuadernos y comprobar cada URL con una petición real** (`AGENTS.md` §11). Ejecutar cada cuaderno completo después.
- [ ] **Reescribir el historial** (`git filter-repo`) para bajar el peso real de los clones. Operación aparte: copia de respaldo (`git bundle`), congelar, force push coordinado y recrear ramas. No hacerlo cerca de una clase.
- [ ] Ajustar `GRANDFATHERED` en `check_repo_hygiene.py` a medida que salgan archivos.

## 5. Gobernanza de GitHub

No hay PR abiertos ni ramas con código divergente: las ramas históricas fueron alineadas al SHA de `main` después de cerrar sus PR. Los nombres de esas ramas todavía pueden aparecer en GitHub porque el conector disponible no expone la operación DELETE de refs; no contienen trabajo pendiente distinto de `main`.

- [ ] Ajustes del repo (hoy: `delete_branch_on_merge`, `allow_auto_merge` y rulesets desactivados): borrar rama al fusionar, squash merge, PR obligatorio y checks `qa`, `visual` y `higiene` obligatorios. Se hace en Settings; no se ha tocado.
- [ ] Cuando haya acceso a borrado de refs, eliminar nominalmente las ramas históricas ya alineadas. Es limpieza de nombres, no recuperación de trabajo pendiente.

## 6. Consolidación de arquitectura (V55)

- [ ] **`utils/build_index.py`:** generar `index.html` desde `course.json` y hacer que el CI falle con `git diff --exit-code index.html`. Hoy la portada aplica la regla correcta con un script y `validate_index_calendar.py` cubre el estado estático, pero las tarjetas siguen escritas a mano.
- [ ] Retirar las rutas legacy de S09 (`session-09.html`, `progress-09.html`, `teacher-wall-09.html`, `bigdata-session9/`): redirect → deprecado → eliminado.
- [ ] Dividir `bigdata-session/index.ts` (~920 líneas) y `bigdata-lms-core/index.ts` (~900) en módulos internos.
- [ ] Tokens de CSS compartidos y accesibilidad como gate formal (0 critical/serious en axe, teclado, foco, zoom 200 %, `prefers-reduced-motion`).
- [ ] ADR en `docs/DECISIONS/` (fuente de verdad `course.json`, sin respuestas abiertas, wall objetivo) y separar el roadmap en producto, técnico y curso.
- [ ] Plantilla de sesión y de presentación **antes** de construir S10–S16 (hoy `draft`).
- [ ] Observabilidad (fallos de login, errores de Edge Functions, latencia) y RPO/RTO con una restauración de prueba.

## Verificación de producción

El 28-09-2026 se verificó en Supabase producción que:

- las cuatro Edge Functions V54 están activas con una versión nueva;
- no hay tareas activas que acepten `text`;
- el único CHECK de `lms_questions_v2.question_type` admite exclusivamente `single_choice`, `multiple_choice`, `true_false` y `numeric` (queda `NOT VALID` para conservar historia);
- la migración V55 dejó activos los 22 distractores S09 sin cambiar `value` ni hashes.

Sigue pendiente una prueba end-to-end autenticada como docente de comunicados/colaboración y la rotación de credenciales Atlas indicada arriba.
