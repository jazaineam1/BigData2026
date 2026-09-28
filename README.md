# Big Data 2026 · Universidad Central

Repositorio del curso de **Big Data** de la Maestría en Analítica de Datos (Universidad Central): cuadernos, presentaciones, datos, un LMS propio y la infraestructura de pruebas que los sostiene.

**Sitio del curso:** https://jazaineam1.github.io/BigData2026/ · el estudiante entra siempre por `index.html`.

> Este repositorio es **público**. No contiene datos de estudiantes, credenciales ni material docente privado (ver [Seguridad](#seguridad-y-datos-personales)).

## Qué hay aquí

Cuatro cosas conviven en este repositorio:

| Producto | Qué es | Dónde vive |
|---|---|---|
| **Curso** | Cuadernos de Colab, presentaciones, talleres y datos | `Cuadernos/`, `Presentaciones/`, `Datos/`, `assets/` |
| **LMS** | Aula, sesiones, progreso, entregas, quizzes, competencias y vistas de docente | `lms/` (frontend estático) |
| **Backend** | Edge Functions y migraciones de Supabase | `infraestructura/lms/` |
| **Ingeniería** | Validadores, pruebas de navegador y CI | `utils/`, `tests/`, `.github/workflows/` |

## Una sola fuente de verdad para el calendario

`lms/data/course.json` define la estructura, la visibilidad y las fechas de las sesiones. Supabase define actividades, laboratorios, evaluadores y progreso oficial. Las superficies canónicas del LMS son `lms/session.html?s=N`, `lms/progress.html?s=N` y `lms/wall.html?s=N`.

La sesión actual se calcula igual en todas partes: la última cuyo `starts_at` ya pasó; si ninguna empezó, la próxima. La portada y el portal usan esa misma regla.

## Estructura

```text
index.html            puerta de entrada del estudiante
lms/                  frontend del LMS (HTML estático + lms/data/course.json)
Presentaciones/       presentaciones interactivas de las sesiones
Cuadernos/            cuadernos de Colab
Datos/  Airflow/      datos y pipeline de ejemplo
assets/               imágenes, diagramas y guías de laboratorio
infraestructura/      Docker, tutoriales y el backend del LMS
  └─ lms/               Edge Functions (functions/) y migraciones SQL
utils/                generadores de cuadernos y validadores (validate_*.py)
tests/                pruebas de navegador (Playwright + axe)
.github/workflows/    CI: validación, QA visual, higiene y publicación
AGENTS.md             reglas para producir material del curso
```

## Cómo se prueba

Los cambios pasan por pull request y por estas comprobaciones de CI:

| Workflow | Qué comprueba |
|---|---|
| **Validar LMS Big Data** | Validadores de contrato, seguridad, calendario y la regla «sin respuestas abiertas» |
| **QA visual LMS** | Playwright + axe: desbordes, responsive, accesibilidad y flujos del LMS |
| **Higiene y secretos** | Sin artefactos generados, sin archivos enormes nuevos, sin secretos ni datos personales |
| **Publicar sitio en GitHub Pages** | Construye y despliega el sitio, con una prueba de humo del resultado |

En local:

```bash
npm ci                                   # dependencias fijadas por package-lock.json
python utils/validate_lms_s08.py         # ejemplo de validador; hay uno por área en utils/validate_*.py
python utils/check_repo_hygiene.py       # artefactos y tamaños
python utils/scan_secrets_pii.py         # secretos y datos personales
npx playwright install chromium          # una vez
npx playwright test                      # pruebas de navegador (sirve el sitio en :4173)
```

Las pruebas de navegador esperan el sitio en `http://127.0.0.1:4173`; el CI lo sirve con `python -m http.server 4173`.

## Reglas que no se negocian

- **El estudiante no escribe respuestas abiertas.** Las decisiones, alternativas y límites se capturan con opciones estructuradas, números, código, archivos, URLs o evidencia verificable. Lo comprueba `utils/validate_no_open_student.py` y `AGENTS.md` §4 explica el porqué.
- **Un cuaderno es una clase, no un contenedor de código.** Cada salida se acompaña de cómo se lee, qué dice, qué **no** permite concluir y el error común (`AGENTS.md` §3).
- **Los tiempos viven en el libreto docente, no en el cuaderno del estudiante.**
- **Si hay un generador en `utils/`, se modifica el generador y se regenera**; no se editan cuadernos a mano.

Antes de producir o cambiar material, lee [`AGENTS.md`](AGENTS.md).

## Seguridad y datos personales

- No se versionan credenciales, `.env`, datos de estudiantes (encuestas, entregas, notas) ni material docente privado. `.gitignore` es la primera barrera y `utils/scan_secrets_pii.py` la segunda.
- El navegador nunca es la fuente del expediente académico: el progreso oficial vive en Supabase y se escribe desde Edge Functions con la clave de servicio **solo en el servidor**.
- Si encuentras una credencial o un dato personal en este repositorio, avisa al docente antes de abrir un issue público.

## Datos pesados

Algunos conjuntos de datos (SECOP, benchmarks, una base DuckDB de ejemplo) superan los 50 MB y hoy están versionados. `utils/check_repo_hygiene.py` **impide que entren archivos nuevos de más de 25 MB** y lista los existentes con la razón por la que aún no se han movido. La meta es dejar en Git un manifiesto (URL, SHA256, tamaño, fuente y script que lo genera) y el dato completo fuera del repositorio.

## Contribuir

1. Crea una rama a partir de `main` y haz cambios pequeños y reversibles.
2. Abre un pull request; se usa **squash merge** para que `main` conserve una línea por cambio.
3. El PR debe pasar esos workflows y completar la lista de la plantilla.

Tareas pendientes y decisiones abiertas: [`docs/PENDIENTES.md`](docs/PENDIENTES.md). Documentación técnica del LMS: [`infraestructura/lms/ROADMAP.md`](infraestructura/lms/ROADMAP.md) y [`infraestructura/lms/STANDARDS.md`](infraestructura/lms/STANDARDS.md).
