# Módulo 0: onboarding de Git y GitHub

## Objetivo

Preparar el repositorio privado y la identidad Git para trabajar durante todo el semestre sobre un único proyecto
acumulativo. Cada pareja recibirá `compras-claras-pareja-XX`; las nuevas actividades llegarán mediante Pull Requests
del docente y no mediante GitHub Classroom o forks.

## Antes de empezar

- Entra únicamente al repositorio que el docente asignó a tu pareja.
- Comprueba que no estás en la plantilla, la solución o el repositorio de otro equipo.
- No habilites Copilot, presupuestos ni facturación de Codespaces para esta actividad.
- No publiques la URL privada ni agregues colaboradores por tu cuenta.

## Ruta A — Git y Python locales

Es la opción recomendada porque no depende de cuota de nube. En **Code → Local → HTTPS** copia la URL y ejecuta:

```bash
git clone URL_DEL_REPOSITORIO_ASIGNADO
cd compras-claras-pareja-XX
python scripts/configurar_entorno.py
git status
git remote -v
```

Usa Git Credential Manager o el inicio de sesión que ofrezca tu instalación. SSH es opcional; si lo eliges, sigue la
[documentación oficial de GitHub](https://docs.github.com/es/authentication/connecting-to-github-with-ssh) y nunca
compartas la clave privada.

## Ruta B — Codespaces con cuota personal

Codespaces abre el repositorio ya clonado y usa autenticación HTTPS. Úsalo solo si tu cuenta muestra cuota personal
disponible; la organización no pagará consumo adicional.

1. Selecciona **Code → Codespaces → Create codespace**.
2. Espera a que termine `postCreateCommand`.
3. Verifica:

```bash
python --version
git --version
git status
git branch --show-current
git remote -v
```

No es necesario crear claves SSH ni levantar Docker para S02.

## Ruta C — github.dev como contingencia

Pulsa `.` en el repositorio para abrir el editor web gratuito. Permite editar, confirmar y sincronizar desde
**Source Control**, pero no ofrece terminal. Usa entonces los resultados precomputados indicados por el docente.

## Configurar identidad

```bash
git config --get user.name
git config --get user.email
```

Si falta un valor, configúralo solo para este repositorio:

```bash
git config user.name "Tu Nombre"
git config user.email "correo-verificado-o-noreply-de-github"
```

## Flujo semanal

1. Leer y fusionar el PR docente `docente/sXX-kit`.
2. Actualizar `main` con `git pull --ff-only`.
3. Crear `hito/sXX-descripcion`; para S02 usa:

   ```bash
   git switch -c hito/s02-blueprint
   ```

4. Revisar `git status`, `git diff`, `git add` y `git diff --staged` antes de cada commit.
5. Publicar la rama, abrir PR hacia `main`, revisar y esperar CI verde.
6. Fusionar con merge commit y eliminar la rama al terminar.

```text
working tree --git add--> staging --git commit--> historial local --git push--> remoto
                                                       |
                                                       └── Pull Request → revisión → CI → main
```

## Errores comunes

- `Please tell me who you are`: configura `user.name` y `user.email` localmente.
- `not a git repository`: abre la terminal en la raíz del clon.
- cambios directos en `main`: crea la rama del hito antes de editar.
- rama ya existente: usa `git switch hito/s02-blueprint` en lugar de crear otro nombre.
- autenticación fallida en Codespaces: revisa `git remote -v`; no cambies inmediatamente a SSH.
- validador bloquea un commit: corrige el archivo o posible secreto indicado; no desactives el hook.

## Resultado esperado

Puedes identificar el repositorio y la rama correctos, distinguir working tree, staging, commit y remoto, y explicar
por qué el mismo repositorio conserva la evolución completa del proyecto.
