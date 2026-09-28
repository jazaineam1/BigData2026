# Pendientes del repositorio y del LMS

Lista viva de lo que **quedó sin hacer** después de los cambios V54-A, V54-B y V56-A, en orden de urgencia. Se actualiza al cerrar cada punto (bórralo al terminarlo, no lo tachues). Lo que cambia cada semana del curso vive en `.local-docente/`, fuera de Git.

Lo ya hecho (PR #104, #105, #106): portada alineada con `course.json`; sin texto libre del estudiante en entregas y colaboración; tipos de pregunta unificados; higiene, `npm ci` y escáner de secretos. Las guardias son `utils/validate_no_open_student.py`, `utils/check_repo_hygiene.py` y `utils/scan_secrets_pii.py`.

## 1. Antes de la clase del 1 de octubre (bloqueantes)

El merge publica solo el **frontend** (Pages). Nada de lo siguiente se despliega solo, y sin ello el frontend nuevo y el backend viejo se desalinean (registrar rol de contribución y revisión por pares fallarían).

- [ ] **Rotar las credenciales de Atlas expuestas.** `Cuadernos/8_NoSQL_Mongo.ipynb` contiene dos URIs con contraseña de aspecto real, versionadas desde 2023-11-02 en `main` y en todas las ramas. En Atlas: eliminar o rotar esos usuarios de base de datos y revisar la lista de IPs permitidas. Después sustituirlas por un marcador en el cuaderno y **borrar la excepción `KNOWN` correspondiente** en `utils/scan_secrets_pii.py` (el escáner la muestra como aviso urgente en cada CI). Quitarlas del árbol no las borra del historial.
- [ ] **Desplegar las Edge Functions** `bigdata-lms-core`, `bigdata-session`, `bigdata-lms-assess` y `bigdata-lms-interop` (no hay paso de despliegue automatizado en `.github`).
- [ ] **Aplicar el SQL en este orden**, tras leer las consultas informativas de cada cabecera:
  1. `infraestructura/lms/lms-v54a-no-open-student.sql` (antes: listar tareas activas que solo aceptaban texto y reescribir sus instrucciones).
  2. `infraestructura/lms/lms-v54b-question-types.sql` (antes: contar filas `short_text`; después: confirmar que queda un solo CHECK y que el viejo se descubrió en `pg_constraint`). **No ejecutar `VALIDATE CONSTRAINT`** mientras existan filas históricas `short_text`.
  Ninguna se ha ejecutado nunca; solo se comprobó la sintaxis con el parser de PostgreSQL.
- [ ] **Decisión sobre el TC1:** el rol de contribución individual solo se registra en `collaboration.html`, que ni el portal ni `session-08.html` enlazan. Decidir si esos roles cuentan para repartir nota (entonces enlazarlos desde la sesión 8 o mover el selector allí) o si se descartan.
- [ ] **Canal de dudas durante el taller:** el estudiante ya no puede escribir en la plataforma. Decir por dónde pregunta y ponerlo en «Comunicados del docente».
- [ ] Probar con una cuenta de **docente** lo que solo se probó con backend simulado: publicar comunicado y responder en `teacher-collaboration.html`.

## 2. Antes de la clase del 8 de octubre (S09)

- [ ] **LAB 9 estructurado (prioridad).** Las celdas 33 y 34 de `Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb` piden texto libre (`razon`, `decision`, `alternativa_descartada`, `limite`, mínimo 12 caracteres) y lo envían al LMS como `reason`, `decision`, `rejected_alternative`, `limit`. Contradice `AGENTS.md` §4.
  - Modificar el **generador** `utils/build_session9_notebook.py` y regenerar; no editar el `.ipynb`.
  - Sustituir cada campo por una **selección entre opciones** contextualizadas (errores plausibles del grupo, no respuestas regaladas) y un resultado verificable propio (Top-k y Precision@5 propios).
  - Del PR #102 (rama `fix/student-ux-no-open-wall-v2`) portar `LAB9_STRUCTURED` del backend y el generador. **No portar sus valores por defecto** (`razon_clave="complementarias"`, `decision_clave="hibrida"`, `alternativa_clave="sumar_scores"`): entregan la respuesta correcta, igual para todos.
  - Ajustar el evaluador `authentic-review` (hoy revisión docente con rúbrica) y añadir prueba negativa: el cuaderno no debe volver a aceptar texto libre.
- [ ] **Distractores de calidad (PR #91):** portar sobre `main` las etiquetas de D2 y D5 de la presentación, ~22 cambios de etiqueta por migración **idempotente** (en #91 usa `version=version+1`) y `validate_s09_distractors.py`. Dos distractores rozan la respuesta correcta (lab8 paso 0 opción 2 y lab4 paso 1 opción 2): decidir su redacción antes de portarlos.
- [ ] **Profundización (PR #52):** 5 diapositivas nuevas (Laboratorio integrado, Vector por dentro, Distancia y similitud, Persistencia en MongoDB, Recall vs Precision). Decisión de contenido y de dosis (`AGENTS.md` §2): quizá solo «Vector por dentro» y «Recall vs Precision». Portar primero la presentación y después el generador del cuaderno; el orden con #91 y con el LAB 9 importa: #91, luego #52, luego LAB 9.

## 3. Wall de competencia (funcionalidad nueva)

Tablero **estructurado** de progreso de clase, no un foro: alias «Jugador NN» que rotan por sesión, puntaje solo por evidencia objetiva y sin desempate por velocidad. **Diseño completo en [`diseno-wall-competencia.md`](diseno-wall-competencia.md)** (modelo de datos, puntaje reproducible, API, UI, retiro del muro legacy con la lista exacta de validadores acoplados, SQL propuesto sin ejecutar, pruebas, riesgos y 5 PR).

- [ ] **Responder las 12 decisiones de la §8 antes de construir**, en especial D1 (visibilidad; apagado en sesiones evaluativas), D2 (qué cuenta en S09), D4 (cohorte mínima) y D8 (¿cuenta un LAB en revisión?).
- [ ] Construir en 5 PR (unos 3,25 a 5 días): A esquema y puntaje, B backend, C frontend, D retiro de código, E retiro de datos. A–C son aditivos; D y E no se deshacen.
- Hallazgos que cambian el plan: al quitar `wall_post` de `lms-kit.js` una cola offline pendiente puede atascarse (devolver 410/422 en `deliver()`); la competencia BD-E7 exige 2 evidencias y solo un LAB puede aportarla, así que no incluir competencias en el puntaje de S09 v1; `accepted` no siempre significa verificado; los recursos «visitar» nunca llegan a `completed`, por eso el puntaje de #102 no sirve tal cual.
- No portar de #102 su alias (hash de 4 hex: colisiona y es derivable), su puntaje por `required` ni su `drop table` inmediato.

## 4. Peso del repositorio y datos

Hoy hay ~413 MB en 5 archivos que la guardia `check_repo_hygiene.py` lista con su razón y que **solo pueden disminuir**.

- [ ] **`Airflow/dw.duckdb` (50 MB):** no basta quitarlo. DuckDB **rechaza un archivo vacío** y el compose lo monta como archivo (si falta, Docker crea un directorio). Solución: montar un directorio, cambiar `DB_PATH` del DAG y **probarlo con Docker**.
- [ ] **CSV de SECOP (3 × ~100 MB) y `part_04.csv` (65 MB):** varios cuadernos los descargan desde `main`. Publicar como GitHub Release, dejar en Git un `manifest.json` (URL, SHA256, tamaño, fuente, fecha, script generador) y muestras pequeñas; **actualizar los enlaces de los cuadernos y comprobar cada URL con una petición real** (`AGENTS.md` §11). Ejecutar cada cuaderno completo después.
- [ ] **Reescribir el historial** (`git filter-repo`) para bajar el peso real de los clones. Operación aparte: copia de respaldo (`git bundle`), congelar, force push coordinado y recrear ramas. No hacerlo cerca de una clase.
- [ ] Ajustar `GRANDFATHERED` en `check_repo_hygiene.py` a medida que salgan archivos.

## 5. PR antiguos y gobernanza de GitHub

- [ ] **#66 (TC1 2025–2026):** conservar solo como referencia. Portarlo cambiaría reglas y versión del validador con los estudiantes ya entregando, y el corte dinámico da un snapshot distinto a cada grupo (choca con `AGENTS.md` §10). Reutilizables con poco riesgo: las 3 preguntas de caso y sus límites.
- [ ] **#102, #91, #52:** cerrar como «superado por V54» solo cuando su contenido útil esté portado (secciones 2 y 3).
- [ ] Rama `fix/student-ux-no-open-wall-v3`: revisar sus 2 commits (cuaderno S09 y `bigdata-lms-assess`) y borrarla.
- [ ] Ajustes del repo (hoy: `delete_branch_on_merge`, `allow_auto_merge` y rulesets desactivados): borrar rama al fusionar, squash merge, PR obligatorio y checks `qa`, `visual` y `higiene` obligatorios. Se hace en Settings; no se ha tocado.

## 6. Consolidación de arquitectura (V55)

- [ ] **`utils/build_index.py`:** generar `index.html` desde `course.json` y hacer que el CI falle con `git diff --exit-code index.html`. Hoy la portada aplica la regla correcta con un script y `validate_index_calendar.py` cubre el estado estático, pero las tarjetas siguen escritas a mano.
- [ ] Retirar las rutas legacy de S09 (`session-09.html`, `progress-09.html`, `teacher-wall-09.html`, `bigdata-session9/`): redirect → deprecado → eliminado.
- [ ] Dividir `bigdata-session/index.ts` (~920 líneas) y `bigdata-lms-core/index.ts` (~900) en módulos internos.
- [ ] Tokens de CSS compartidos y accesibilidad como gate formal (0 critical/serious en axe, teclado, foco, zoom 200 %, `prefers-reduced-motion`).
- [ ] ADR en `docs/DECISIONS/` (fuente de verdad `course.json`, sin respuestas abiertas, wall objetivo) y separar el roadmap en producto, técnico y curso.
- [ ] Plantilla de sesión y de presentación **antes** de construir S10–S16 (hoy `draft`).
- [ ] Observabilidad (fallos de login, errores de Edge Functions, latencia) y RPO/RTO con una restauración de prueba.

## Lo que no está verificado

Ninguna migración ni Edge Function se ejecutó contra Supabase; no hay Postgres local. Solo hay sintaxis (parser oficial de PostgreSQL y `node --check` sobre TypeScript sin tipos), lectura de código y pruebas de navegador con backend simulado. Tampoco se probó nada autenticado como docente.
