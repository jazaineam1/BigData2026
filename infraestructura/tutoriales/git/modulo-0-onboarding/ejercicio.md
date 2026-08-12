# Ejercicio 0: validar Git en Codespaces

## Objetivo

Recorrer por primera vez working tree, staging, commit y remoto. La sesión 2 no requiere Docker ni claves SSH.

## Pasos

1. Verifica el entorno:

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

3. Crea una rama:

```bash
git switch -c feature/onboarding
```

4. Crea `entorno-listo.txt` con tu nombre, fecha y una frase que explique `git add`.
5. Observa y selecciona únicamente ese archivo:

```bash
git status
git diff
git add entorno-listo.txt
git status
git diff --staged
```

6. Registra y publica:

```bash
git commit -m "Valida entorno inicial del curso"
git push -u origin feature/onboarding
git log --oneline --decorate -3
```

7. Abre un Pull Request desde GitHub y explica la verificación realizada.

## Qué se evalúa

- identidad atribuible;
- rama distinta de `main`;
- selección consciente del archivo en staging;
- commit claro;
- push y Pull Request exitosos.

Si trabajas localmente, usa HTTPS con Git Credential Manager o configura SSH como alternativa siguiendo la documentación oficial.
