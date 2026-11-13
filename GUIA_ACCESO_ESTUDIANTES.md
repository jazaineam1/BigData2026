# S11 · Guía de acceso a Jupyter, Markdown y Codespaces

## Causa comprobada del notebook ausente

**01_laboratorio.ipynb está en la raíz de la rama s11-estudiantes, NO en la raíz de main.**
Si un estudiante crea un fork o copia main, no ve ese archivo. En main hay
otros cuadernos históricos en la carpeta Cuadernos, que no son el mismo laboratorio.
El archivo .devcontainer configura un entorno, **no transporta el notebook**.

### Recuperación en un Codespace nuevo

1. Abre https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes
2. Confirma que el selector muestra **s11-estudiantes**.
3. Abre 01_laboratorio.ipynb en GitHub y comprueba que existe.
4. Selecciona **Code → Codespaces → Create codespace on s11-estudiantes**.
5. Elige **S11 · OCR, visión y voz (aprende Python)**.
6. En la terminal del Codespace, **sin borrar ningún archivo**, ejecuta:

~~~bash
pwd
git branch --show-current
git remote -v
ls -lh 01_laboratorio.ipynb
python verificar_s11.py
~~~

La rama esperada es s11-estudiantes, el notebook debe existir y el diagnóstico
debe confirmar su formato. Si aparece otra rama, **primero guarda cambios
propios** antes de salir, cambiar ramas o eliminar un Codespace.

### Si ya clonaste/forkeaste main

Un fork puede copiar solo la rama predeterminada. No supongas que incluye
automáticamente la rama s11-estudiantes. Es preferible abrir un Codespace nuevo
desde el enlace canónico anterior.

Para añadir la rama del docente a tu fork, después de guardar cambios locales
en un commit y de verificar que el árbol de trabajo está limpio:

~~~bash
git remote -v
git status --short
git remote add upstream https://github.com/jazaineam1/BigData2026.git
git fetch upstream s11-estudiantes
git switch -c s11-estudiantes --track upstream/s11-estudiantes
ls -lh 01_laboratorio.ipynb
~~~

Si ya existe el remoto upstream o una rama con ese nombre, NO repitas comandos
a ciegas. Revisa git remote -v y git branch -avv y conserva tu trabajo.

## Si el .ipynb aparece como JSON o no ejecuta

1. Abre Extensions (Ctrl+Shift+X). Verifica **Jupyter de Microsoft**
   (ms-toolsai.jupyter) y **Python de Microsoft** (ms-python.python).
2. Clic derecho en 01_laboratorio.ipynb → **Open With / Reopen Editor With →
   Jupyter Notebook**. Si ves llaves, cells y texto JSON, el archivo se abrió
   con el editor incorrecto.
3. Arriba a la derecha selecciona **Select Kernel → Python Environments →
   Python 3** del Codespace.
4. Verifica en terminal: python -c "import ipykernel; print('OK')".
5. En **Restricted Mode / Workspace no confiable** las salidas enriquecidas
   pueden quedar ocultas y las celdas no se ejecutan. Confía únicamente
   en el proyecto legítimo que acabas de abrir.
6. Si no aparece la extensión o sigue congelado, usa Ctrl+Shift+P →
   **Developer: Reload Window**. Reconstruye el contenedor solamente como
   último recurso, después de guardar cambios, porque consume cómputo.

**Una celda Markdown del notebook NO es un archivo .md:** sal de la edición de
esa celda Markdown con Shift+Enter para verla renderizada.

## Si README.md y otros Markdown no muestran vista previa

La previsualización de Markdown viene integrada en VS Code, no requiere
instalar un complemento de terceros.

- Abre un archivo con extensión .md (por ejemplo, README.md).
- **Ctrl+Shift+V:** muestra Markdown renderizado.
- **Ctrl+K, luego V:** previsualización al lado; son dos pulsaciones.
- **Ctrl+Shift+P → Markdown: Open Preview to the Side**.
- Si estás mirando un archivo en un editor equivocado: Reopen Editor With →
  Text Editor, luego abre la vista previa Markdown.
- Texto pegado en una terminal, archivo .txt o celda Python no se convierte
  automáticamente en un Markdown visible.
- Si la opción desapareció, revisa que **Markdown Language Features**
  (extensión integrada de VS Code) esté habilitada y que el foco esté en
  el archivo .md correcto.

**github.dev no equivale a un Codespace**: es un editor web y no ofrece por sí
solo el contenedor remoto con Python, Tesseract y Ollama preparado.

## Diagnóstico para un estudiante como Jdonny

Comparte únicamente estas salidas (sin contraseñas ni tokens):

~~~bash
python verificar_s11.py
git branch --show-current
git remote -v
python -m pip show ipykernel nbformat
~~~

Adjunta una captura del Explorador de archivos y del selector **Select Kernel**.
Una captura sin la rama o sin el nombre del archivo no permite asegurar
cuál de las causas está ocurriendo.

## Herramientas de S11

- Presentación: conceptos, casos y comprobaciones, sin código Python extenso.
- 01_laboratorio.ipynb: código explicado y ejercicios completos.
- buscador_multimodal.py: recuperación de imagen, OCR contractual y voz.
- visor_fuentes.py: evidencia visual privada, con originales y metadatos.
- GUIA_ACCESO_ESTUDIANTES.md: resolución de incidentes sin perder trabajos.

Documentación oficial: VS Code Jupyter Notebooks; VS Code Markdown;
GitHub Codespaces/dev containers.
