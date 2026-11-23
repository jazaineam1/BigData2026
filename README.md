# Sesión 13 · Un cuaderno, todos los datos

**[Crear el Codespace de S13](https://codespaces.new/jazaineam1/BigData2026/tree/s13-laboratorio)** · [Presentación interactiva](https://jazaineam1.github.io/BigData2026/Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1)

## Empieza en tres pasos

1. Abre el enlace y confirma que la rama sea **`s13-laboratorio`**. Hay **una sola configuración de Codespaces**, correspondiente a S13; no necesitas elegir entre perfiles.
2. Crea el Codespace con **2 núcleos** si están disponibles. La instalación automática debe terminar con **`LISTO PARA S13`**.
3. Abre **Cuadernos → 13_Dask_MapReduce_Compras_Claras.ipynb** y usa el kernel **Python 3.11**. Ejecuta las celdas de arriba abajo y completa el reto final con tus resultados.

El **cuaderno es idéntico, sin recortes ni cambios de celdas, al publicado en `main`**. Contiene todas las demostraciones de Dask, MapReduce, SECOP, Parquet, K-means, memoria y tiempos. **No se eliminó ni redujo ninguna práctica.**

### Un detalle sobre las instrucciones originales

El cuaderno original incluye una sección que explica cómo elegir manualmente el perfil S13 en la rama `main`. **En esta rama especial ese paso no aplica:** ya estás en el perfil correcto y puedes comenzar directamente con las comprobaciones y el código del mismo cuaderno. Se conserva ese texto para mantener el cuaderno exactamente igual al original.

### Datos suficientes, sin saturar la pantalla

- **9 archivos CSV SECOP:** las seis muestras de prueba de 1.000 registros y los tres fragmentos grandes de aproximadamente 100.000 registros cada uno, para unas **300.000 filas en los tres archivos grandes**, con todas las columnas originales.
- **Corpus complementario de 200 expedientes** y todos los módulos Python imprescindibles.
- **8 pruebas unitarias ligeras** de la demostración Dask, conservadas para verificar integridad sin iniciar automáticamente entrenamiento ni benchmarks pesados.

**La práctica de inicio del cuaderno utiliza la muestra pequeña real de 1.000 filas** y K-means numérico simulado de 1.000 filas (ampliable a 20.000). Los CSV grandes quedan disponibles si después decides trabajar con mayor volumen. **No se promete que el cuaderno procese automáticamente 300.000 registros:** eso requeriría otro alcance y revisión explícita de recursos.

Los datos y scripts están en la rama, pero sus carpetas se ocultan en el Explorador de VS Code para que el estudiante no se distraiga. La configuración visual **no elimina los archivos**; siguen accesibles desde Python.

### Si no aparece LISTO PARA S13

En **Terminal → New Terminal** ejecuta:

```bash
python Laboratorios/S13_Codespaces/verificar_entorno.py
```

No instales Streamlit, Ollama ni abras otros laboratorios. Al finalizar, detén el Codespace para ahorrar cuota.

## Fuentes y reproducibilidad

- [Cuaderno S13 original en `main`](https://github.com/jazaineam1/BigData2026/blob/main/Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb)
- [Código del ejercicio dentro de esta rama](https://github.com/jazaineam1/BigData2026/tree/s13-laboratorio)
- [Documentación de Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/creating-a-codespace-for-a-repository)
