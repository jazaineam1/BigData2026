# S13 · Código que el estudiante puede reutilizar

**Plataforma principal:** GitHub Codespaces con el perfil **S13 · Dask, MapReduce y modelos SECOP**.

No instalar software en el computador personal. Al elegir el Codespace con ese perfil se instalan las dependencias. El perfil raíz del repositorio pertenece a **Airflow**: en `Code → Codespaces → ... → New with options` se debe escoger **S13**, no el perfil predeterminado.

## Primeros pasos

1. Desde la [portada del curso](../../index.html) abre la presentación de S13 y sigue el tutorial embebido.
2. Crea el Codespace con la configuración `.devcontainer/s13-distribuido/devcontainer.json`.
3. Abre una terminal en VS Code web. Comprueba instalación con:

   ```bash
   python --version
   python -m pip show dask
   python -m pip show scikit-learn
   python Laboratorios/S13_Codespaces/verificar_entorno.py
   ```

4. Si falta un módulo, la instalación reproducible se realiza **dentro del Codespace**, no en el equipo:

   ```bash
   python -m pip install -r Laboratorios/S13_Codespaces/requirements.txt
   ```

5. Abre `Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb`, selecciona el kernel de Python del Codespace y ejecuta por secciones.

## Herramientas y demostración

- **Python / MapReduce conceptual:** funciones de sumar y contar; nada de Hadoop MapReduce instalado.
- **HDFS:** simulación de bloques y réplicas; no se afirma haber instalado HDFS.
- **pandas:** resultados de referencia de un archivo SECOP.
- **Dask DataFrame:** particionado y operaciones diferidas, comparación con pandas.
- **scikit-learn:** TF-IDF y regresión logística con división entrenamiento/prueba; la etiqueta es modalidad contractual, NO fraude.
- **Dask Distributed:** distribuye entrenamientos independientes y recupera un fallo controlado de tarea; **no entrena un solo modelo distribuido**.
- **Parquet:** resultado tabular que se reutilizará en S14/PySpark.

## Ejecutar sin abrir Jupyter

```bash
python Laboratorios/S13_Codespaces/analisis.py mapreduce
python Laboratorios/S13_Codespaces/analisis.py comparar
python Laboratorios/S13_Codespaces/analisis.py modelo
python Laboratorios/S13_Codespaces/analisis.py experimentos
python Laboratorios/S13_Codespaces/analisis.py fallo
python Laboratorios/S13_Codespaces/analisis.py exportar
```

Para ejecutar todo: `python Laboratorios/S13_Codespaces/analisis.py todo`.

## Pruebas

```bash
cd Laboratorios/S13_Codespaces
python -m unittest -v test_s13
```

El panel Dask usa el **puerto privado 8787** de Codespaces. Si no se abre, usa `client.scheduler_info()`: el resultado del laboratorio no depende de la interfaz gráfica. Los dos workers son hilos en la misma máquina remota, no dos equipos físicos.

## Transferencia a otros proyectos

El módulo `analisis.py` tiene funciones separadas para lectura, preparación, procesamiento, entrenamiento y exportación. Para adaptar el caso, cambia la ruta del CSV, `COL_TEXTO`, `COL_LABEL` y `CLASES` después de verificar nombres/valores reales. Usa siempre `train_test_split` ANTES de ajustar TF-IDF; nunca selecciones hiperparámetros usando el conjunto de prueba. Prueba cada cambio con una muestra pequeña.

Los archivos creados van a `Laboratorios/S13_Codespaces/salidas/`, excluida de Git. No subas datos personales ni credenciales al repositorio público. Cierra el Codespace al finalizar para ahorrar cuota.

## Datos y límites

- 200 expedientes de `Datos/tc2_corpus_2026.json`: **sin etiqueta de modalidad** y no usados para aprendizaje supervisado.
- 1.000 procesos de `Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv`: 59 columnas, sí incluye descripción y modalidad.
- La muestra de entrenamiento y las dos clases frecuentes no representan el universo SECOP; clasificar modalidad **no prueba irregularidades**.
- Dask puede ser más lento que pandas en datos pequeños; no presentar tiempos medidos en un Codespace como ventaja universal.
