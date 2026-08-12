# Módulo 0: onboarding de Git y GitHub

## Objetivo

Dejar la identidad y el repositorio listos para trabajar sin mezclar dos rutas distintas: GitHub Codespaces, recomendado para la sesión 2, e instalación local, opcional para quien prefiera su propio equipo.

## Ruta A — GitHub Codespaces

Codespaces abre el repositorio ya clonado y usa autenticación HTTPS para el repositorio que originó el entorno. En esta ruta no es necesario crear claves SSH ni levantar Docker manualmente.

1. Entra al repositorio asignado por GitHub Classroom.
2. Selecciona `Code > Codespaces > Create codespace`.
3. Abre la terminal y ejecuta:

```bash
python --version
git --version
git status
git branch --show-current
git remote -v
git config --get user.name
git config --get user.email
```

Si falta la identidad, configúrala solo para este repositorio:

```bash
git config user.name "Tu Nombre"
git config user.email "tu-correo@ejemplo.com"
```

## Ruta B — Instalación local opcional

En un equipo propio puedes clonar por HTTPS y autenticarte con Git Credential Manager:

```bash
git clone https://github.com/ORGANIZACION/REPOSITORIO.git
cd REPOSITORIO
git status
```

SSH es una alternativa local, no un requisito. Si la eliges, sigue la [documentación oficial de GitHub](https://docs.github.com/es/authentication/connecting-to-github-with-ssh) y nunca publiques la clave privada.

## Flujo que debes comprender

```text
working tree --git add--> staging --git commit--> historial local --git push--> remoto
                                                       |
                                                       └── Pull Request para revisar
```

La sesión 2 usa este flujo para versionar arquitectura como código. Docker, Airflow y los demás servicios de infraestructura empiezan en sesiones posteriores.

## Errores comunes

- `Please tell me who you are`: configura `user.name` y `user.email`.
- `not a git repository`: abre la terminal en la raíz del repositorio.
- cambios en `main`: crea primero `git switch -c entrega/sesion2`.
- autenticación fallida en Codespaces: confirma el repositorio de origen y `git remote -v`; no cambies inmediatamente a SSH.

## Resultado esperado

Puedes identificar repositorio y rama, distinguir working tree, staging, commit y remoto, y publicar una rama sin crear credenciales innecesarias.
