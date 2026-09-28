# Producción LMS Big Data

La publicación tiene dos planos independientes: GitHub Pages y Supabase. Un merge
verde no se considera desplegado si las Edge Functions o el esquema siguen atrás.

## Contrato V56

- `production-release.json` declara el release esperado.
- Las Edge Functions críticas exponen `X-BigData-Release`.
- `bigdata-session?action=deployment_status` devuelve solo el release de la
  función y el marcador de esquema; no expone datos académicos ni identidades.
- `validate_production_release.py` comprueba el contrato en el repositorio.
- En `main`, GitHub Actions compara el contrato con Supabase real.

## Orden de despliegue

1. Validadores y pruebas de la rama/PR.
2. Aplicar migraciones nuevas e idempotentes.
3. Desplegar las Edge Functions críticas modificadas.
4. Verificar cabeceras de release y `deployment_status`.
5. Fusionar a `main`; el gate de drift vuelve a verificar producción.
6. GitHub Pages publica solo si el link checker del artefacto pasa.

## Enlaces y capturas pendientes

`utils/validate_static_links.py` valida referencias locales reales. Una captura
todavía pendiente debe mostrarse como placeholder mediante `data-pending-src`;
no debe usar un `src` inexistente que provoque un 404.
