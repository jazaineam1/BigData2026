# Módulo 0: onboarding de Git y GitHub

## Objetivo

Dejar la identidad y el repositorio listos para trabajar sin mezclar dos rutas distintas: GitHub Codespaces, recomendado para la sesión 2, e instalación local, opcional para quien prefiera su propio equipo.

## Ruta A — GitHub Codespaces

Codespaces abre el repositorio ya clonado y usa autenticación HTTPS para el repositorio que originó el entorno. En esta ruta no es necesario crear claves SSH.

1. Entra al repositorio asignado por GitHub Classroom.
2. Selecciona `Code > Codespaces > Create codespace`.
3. Abre la terminal y verifica:

```bash
python --version
git --version
git status
git branch --show-current
git remote -v
```

4. Comprueba tu identidad:

```bash
git config --get user.name
git config --get user.email
```

Si falta algún valor, configúralo para este repositorio:

```bash
git config user.name "Tu Nombre"
git config user.email "tu-correo@ejemplo.com"
```

Usar configuración local evita cambiar por accidente la identidad de otros repositorios o usuarios del equipo.

## Ruta B — Instalación local opcional

En un equipo propio puedes clonar por HTTPS y autenticarte con Git Credential Manager. SSH es otra alternativa, no un requisito de la sesión.

```bash
git clone https://github.com/ORGANIZACION/REPOSITORIO.git
cd REPOSITORIO
git status
```

Si eliges SSH, sigue la [documentación oficial de conexión con SSH](https://docs.github.com/es/authentication/connecting-to-github-with-ssh). Nunca compartas la clave privada; GitHub recibe únicamente la clave pública.

## Mapa mental del flujo

```text
working tree --git add--> staging --git commit--> historial local --git push--> remoto
                                                       |
                                                       └── Pull Request para revisar
```

- `git status`: explica dónde está cada cambio.
- `git diff`: muestra cambios todavía no enviados a staging.
- `git add archivo`: selecciona evidencia para el próximo commit.
- `git commit`: registra una unidad de trabajo con autor y mensaje.
- `git push`: publica los commits de la rama.
- Pull Request: permite explicar, revisar y validar antes de integrar.

## Errores comunes

### `Please tell me who you are`

Git no encuentra nombre o correo. Configura `user.name` y `user.email` como se mostró arriba.

### `not a git repository`

La terminal está en otra carpeta. En Codespaces vuelve al explorador y abre una terminal desde la raíz del repositorio.

### Cambios en `main` por accidente

Crea la rama antes de editar:

```bash
git switch -c entrega/sesion2
```

### Error de autenticación en Codespaces

Primero confirma que abriste el Codespace desde el repositorio asignado y revisa `git remote -v`. No cambies el remoto a SSH como primera solución. Si persiste, vuelve a autorizar Codespaces desde GitHub o solicita apoyo docente.

## Resultado esperado

Al finalizar puedes identificar el repositorio y la rama, explicar los cuatro estados básicos de un cambio y publicar un commit sin crear credenciales innecesarias.
