# Ejercicio 0: validar Git en Codespaces

## Objetivo

Comprobar el entorno y recorrer por primera vez working tree, staging, commit y remoto. La sesión 2 no requiere Docker ni claves SSH.

## Pasos

1. Verifica entorno, identidad, repositorio y rama:

```bash
python --version
git --version
git config --get user.name
git config --get user.email
git status
git branch --show-current
git remote -v
```

2. Si falta la identidad, configúrala para este repositorio:

```bash
git config user.name "Tu Nombre"
git config user.email "tu-correo@ejemplo.com"
```

3. Crea una rama antes de editar:

```bash
git switch -c feature/onboarding
```

4. Crea `entorno-listo.txt` con tu nombre, fecha y una frase que explique qué hace `git add`.
5. Observa el cambio y selecciona solamente ese archivo:

```bash
git status
git diff
git add entorno-listo.txt
git status
git diff --staged
```

6. Registra y publica la evidencia:

```bash
git commit -m "Valida entorno inicial del curso"
git push -u origin feature/onboarding
git log --oneline --decorate -3
```

7. Abre un Pull Request desde GitHub y describe qué verificaste.

## Qué se evalúa

- identidad atribuible;
- rama distinta de `main`;
- uso consciente de staging;
- commit claro y acotado;
- push y Pull Request exitosos.

## Ruta local opcional

Si trabajas fuera de Codespaces, usa HTTPS con Git Credential Manager o configura SSH siguiendo la documentación oficial. El producto y los comandos Git del ejercicio son los mismos.
