## Qué cambia y por qué

<!-- Una o dos frases: el problema y la decisión. Enlaza el PR o la sesión si corresponde. -->

## Cómo lo verificaste

<!-- Comandos ejecutados y su resultado real. Si algo NO pudiste verificar (Supabase, Colab, red), dilo aquí. -->

## Lista de verificación

- [ ] No introduce respuestas abiertas del estudiante (`AGENTS.md` §4); un campo de texto es una herramienta o del docente y está declarado en `utils/validate_no_open_student.py`.
- [ ] `lms/data/course.json` sigue siendo la fuente de verdad del calendario; la portada no lo contradice.
- [ ] La sesión protegida por SHA sigue intacta.
- [ ] Probado en móvil (390 px) y con tema claro y oscuro donde aplique; el color no es la única señal.
- [ ] Frontend, backend y esquema dicen lo mismo (mismos nombres de campo y mismos tipos permitidos).
- [ ] La migración SQL es idempotente y no toca datos históricos.
- [ ] Sin credenciales, datos de estudiantes ni archivos generados (`check_repo_hygiene.py` y `scan_secrets_pii.py` en verde).
- [ ] Si hay un generador en `utils/`, se modificó el generador y se regeneró; no se editó el `.ipynb` a mano.
- [ ] La documentación afectada está actualizada.
- [ ] Los workflows pasan en el CI (no solo en local).

## Antes del despliegue

<!-- Lo que el merge NO despliega solo: Edge Functions, migraciones SQL, datos externos. Márcalo o escribe «nada». -->
