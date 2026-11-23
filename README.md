# Sesión 13 · Un cuaderno y todos los datos SECOP

[**CREAR CODESPACE S13**](https://codespaces.new/jazaineam1/BigData2026/tree/s13-laboratorio) · [**Presentación S13**](https://jazaineam1.github.io/BigData2026/Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1)

## Iniciar en tres pasos

1. Abre el enlace para crear el Codespace y verifica que la rama sea **`s13-laboratorio`**. Esta rama contiene **un único perfil predeterminado: S13 · Un solo cuaderno de Dask**. No debes elegir Airflow ni abrir `main`.
2. Selecciona una máquina de **2 núcleos** si está disponible y pulsa **Create codespace**. Espera a que termine la instalación automática y aparezca **`LISTO PARA S13`**.
3. Abre el cuaderno **`Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`** (normalmente se abre automáticamente), selecciona **Python 3.11** como kernel y ejecuta las celdas en orden. El reto de decisión final se completa después de analizar las mediciones.

Si necesitas verificar el entorno, abre **Terminal → New Terminal** y ejecuta:

```bash
python Laboratorios/S13_Codespaces/verificar_entorno.py
```

El mensaje final esperado es **`LISTO PARA S13`**. Ante fallas, revisa la instalación y el error. No instales herramientas adicionales salvo una dependencia que haya fallado.

## Qué hay dentro

- **Un solo cuaderno de 55 celdas**, con las **22 celdas de código y todas las prácticas originales sin modificaciones**. Se actualizaron únicamente los textos iniciales de acceso para esta rama.
- **Nueve CSV SECOP**: seis muestras pequeñas y tres archivos grandes de cerca de 100.000 filas cada uno; los grandes suman aproximadamente 300.000 registros. Los archivos grandes siguen disponibles para prácticas adicionales, no se procesan automáticamente durante el Run All inicial.
- **Corpus de 200 expedientes** y módulos Python internos para pandas, Dask, MapReduce, Parquet, K-means, mediciones de memoria y tiempos.
- **Presentación S13** accesible desde el enlace superior.

Las carpetas técnicas están ocultas en el Explorador de VS Code para que el estudiante vea principalmente su cuaderno. **No están eliminadas** y las rutas que utilizan los ejercicios funcionan normalmente.

## Al terminar

Revisa tus resultados y completa el reto final seleccionando `ARQUITECTURA` y `LIMITE`. **Detén el Codespace para ahorrar cuota.** Para esta sesión no necesitas hacer descargas locales, abrir otros laboratorios ni configurar Airflow.

[**Ver el cuaderno en la rama estudiantil**](https://github.com/jazaineam1/BigData2026/blob/s13-laboratorio/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb)
