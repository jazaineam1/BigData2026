# S13 · Big Data — Laboratorio limpio

**Este es el espacio exclusivo de la Sesión 13.** Aquí no están los cuadernos de otras sesiones, archivos de investigación ni herramientas adicionales del curso.

## Comienza aquí

1. **Crear entorno:** [Abrir S13 en GitHub Codespaces](https://codespaces.new/jazaineam1/BigData2026/tree/s13-laboratorio).
2. Confirma que la rama es **`s13-laboratorio`**. Este espacio tiene **un solo perfil de Codespaces**, seleccionado por defecto; no elijas Airflow.
3. Elige una máquina de **2 núcleos** si está disponible y pulsa **Create codespace**.
4. Espera la instalación automática y el mensaje **`LISTO PARA S13`**.
5. Si el cuaderno no se abrió automáticamente, haz clic en **Cuadernos → 13_Dask_MapReduce_Compras_Claras.ipynb**.
6. Selecciona el kernel **Python 3.11**. Ejecuta las celdas de arriba hacia abajo. Al final, responde el reto de arquitectura.

**[Presentación de S13](https://jazaineam1.github.io/BigData2026/Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1)** · **[Abrir único cuaderno en GitHub](https://github.com/jazaineam1/BigData2026/blob/s13-laboratorio/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb)**

### ¿Por qué no veo las carpetas técnicas?

El explorador de VS Code las oculta deliberadamente para dejar visible el cuaderno. Los datos SECOP, el verificador y los dos módulos Python que usa el notebook **sí están en este espacio**, con sus rutas originales y sin descargas externas. Puedes verlos desactivando `files.exclude` en Settings si necesitas auditar código.

### Si la creación falla

Abre **Terminal → New Terminal** y ejecuta:

```bash
python Laboratorios/S13_Codespaces/verificar_entorno.py
```

La última línea debe decir `LISTO PARA S13`. Si hay un módulo ausente, revisa el error de instalación y ejecuta `python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt`. No cambies de perfil ni clones `main`.

### Alcance de la práctica

Primero SECOP real para tareas y MapReduce; después datos numéricos simulados para K-means local frente a Dask-ML, tiempos y memoria de workers. Son ejemplos deliberadamente pequeños. Ninguna ganancia de velocidad está garantizada.

**Nota:** esta rama de estudiantes está separada de `main`, donde están las diapositivas y el resto del curso. El espacio de trabajo contiene únicamente los archivos necesarios para ejecutar S13. Detén el Codespace al terminar para ahorrar cuota.
