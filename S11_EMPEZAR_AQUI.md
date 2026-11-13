# S11 · Dónde está el notebook y cómo abrirlo

**Importante:** esta es la rama principal del curso, **main**. El notebook
único de la Sesión 11 no se encuentra en la raíz de main. Está en la raíz
de la rama **s11-estudiantes**.

**Acceso al laboratorio correcto:**
- [Abrir la rama S11 estudiante](https://github.com/jazaineam1/BigData2026/tree/s11-estudiantes)
- [Abrir el notebook 01_laboratorio.ipynb](https://github.com/jazaineam1/BigData2026/blob/s11-estudiantes/01_laboratorio.ipynb)
- [Guía de acceso, Jupyter y vista Markdown](https://github.com/jazaineam1/BigData2026/blob/s11-estudiantes/GUIA_ACCESO_ESTUDIANTES.md)

En GitHub abre primero la rama **s11-estudiantes**, luego **Code →
Codespaces → Create codespace on s11-estudiantes**. No elijas main pensando
que todos los cuadernos de otras ramas están incluidos.

En la terminal del Codespace:

~~~bash
git branch --show-current
ls -lh 01_laboratorio.ipynb
python verificar_s11.py
~~~

Si el archivo existe pero se ve como texto JSON, haz clic derecho →
**Reopen Editor With → Jupyter Notebook**. Revisa Jupyter de Microsoft y
el kernel Python 3. Si un **README.md** no se previsualiza, abre el archivo
y presiona **Ctrl+Shift+V** o **Ctrl+K, luego V**; una celda Markdown del
notebook se renderiza dentro de Jupyter, no con ese comando.

**No borres el trabajo del alumno ni reconstruyas el Codespace antes de
verificar la rama, el archivo y el editor.** Los problemas de Jupyter, de
Markdown y de rama equivocada son tres causas diferentes.

Nueva práctica: recuperación semántica sobre imágenes, OCR contractual
y voz se encuentra en la sección 9 del **mismo** notebook estudiantil.
