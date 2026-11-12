# S13 · Dask Distributed en acción · Guía de Codespaces

**Recursos principales del estudiante:** [presentación/tutorial](../../Presentaciones/s13-de-una-maquina-a-un-cluster.html#s1) y [cuaderno ejecutable](../../Cuadernos/13_Dask_MapReduce_Compras_Claras.ipynb). Esta carpeta contiene su código, no un tercer material obligatorio.

## Objetivo de la sesión

Partir de una función que calcula **frecuencias de términos sobre títulos SECOP reales**, ejecutarla secuencialmente y repartir sus ocho lotes con Dask. Se comprobará que resultados y huellas coincidan y se medirán tres fases: preparación de entrada, ejecución con workers listos y ejecución incluyendo inicio del clúster.

También compararemos el mismo cálculo con **0,6 segundos de espera externa simulada** por tarea. Es un ejemplo de concurrencia, **no una extracción OCR/ASR real**. Nunca se afirma que Dask sea siempre más rápido.

## 1 · Crear Codespace y verificar recursos

1. En [BigData2026](https://github.com/jazaineam1/BigData2026) abre **Code → Codespaces → New with options**.
2. Elige **S13 · Dask, MapReduce y modelos SECOP** (no el perfil Airflow).
3. La instalación ejecuta automáticamente `verificar_entorno.py`: comprueba archivos, Dask DataFrame y **un worker de proceso real** con una tarea mínima.
4. En la terminal de la raíz del repositorio, revisa las capacidades:

```bash
python Laboratorios/S13_Codespaces/verificar_entorno.py
nproc
lscpu | head -25
free -h
cat /proc/self/status | grep Cpus_allowed_list
```

`nproc` informa las CPU lógicas visibles; `cpu.max` puede añadir cuotas dentro de contenedores. Un worker es un proceso con hilos, no un computador nuevo. Una VM con 4 vCPU puede organizar **1×4, 2×2 o 4×1** y hasta más procesos, aunque sobresuscribir CPU consume memoria y puede empeorar los tiempos.

## 2 · Dos casos de Dask real y reproducible

Desde la raíz del repositorio:

```bash
# Conteos reales de palabras, sin esperas sintéticas:
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo datos
# Mismo trabajo y espera de 0,6 s por lote (servicio externo SIMULADO):
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo espera
```

Para mostrar el panel del scheduler mientras permanece encendido:

```bash
python Laboratorios/S13_Codespaces/dask_cuando_si.py --workers 2 --modo espera --tablero --mantener-tablero-segundos 30
```

En Codespaces usa **PORTS → 8787 → Private**. Los segundos dedicados a observar el panel se excluyen del cronómetro.

El programa registra las direcciones y número de hilos de los workers, su límite de memoria, filas, palabras, `top_terminos` y `resultados_identicos=True`. También registra `segundos_preparacion_entrada`, `segundos_secuencial`, `segundos_arranque_y_espera_workers`, `segundos_dask_cluster_caliente` y `segundos_dask_total_incluido_arranque`.

**Cómo se lee:** el último cronómetro incluye arranque y cómputo, pero excluye preparación inicial y persistencia al disco; no lo presentes como una medición completa de producción. Cada ejecución escribe JSON en `salidas/dask_demostracion_s13.json` y también imprime el JSON por stdout.

Solo si hay recursos suficientes, compara `--workers 4`. El modo opcional `--modo cpu` calcula una carga criptográfica sintética y no representa OCR, embeddings ni análisis de SECOP.

## 3 · Panel Streamlit

```bash
streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py --server.address 0.0.0.0 --server.port 8503
```

Abre **PORTS → 8503 → Private**. En la pestaña 5, escoge primero **Datos** y después **Espera**; pulsa **Ejecutar esta prueba pequeña** para cada una. Verás tiempos medidos, ganadores por fase, vocabulario real, un comparador y descarga JSON. El panel no inicia trabajos automáticamente. La pestaña 4 contiene clasificación UNSPSC **opcional, desactivada de forma predeterminada**.

La pestaña 2 y el cuaderno utilizan el **mismo minicorpus de tres textos**:
A «mantenimiento computadores», B «infraestructura computadores», C «hospital mantenimiento». TF-IDF sirve para representación y búsqueda; no es un algoritmo distribuido ni un detector de fraude.

## 4 · Material y transferencia a S14

- `analisis.py`: funciones auxiliares de pandas, Dask DataFrame, MapReduce y exportación de `secop_s13.parquet`.
- `dask_cuando_si.py`: caso principal real y simulación declarada, sin descargar modelos.
- `app_tfidf_unspsc.py`: interfaz para explorar, practicar TF-IDF y ejecutar ambos casos.
- `requirements.txt`: bibliotecas necesarias para la ruta principal.
- `requirements-extras.txt`: dependencias opcionales de experimentos docentes, **no se instalan en el Codespace básico**.

El cuaderno tiene **45 celdas en su ruta principal** y **9 opcionales**. La clasificación UNSPSC opcional usa LinearSVC sobre TF-IDF; no existe una segunda tarea obligatoria de clasificación por modalidad.

**Para S14:** conserva el Parquet y el manifiesto, e interpreta cómo se procesarían esas particiones con PySpark.

## 5 · Política de costos y verificación

Las pruebas de 50.000, 26.000, Ollama, XGBoost distribuido y CV pesada **no forman parte del laboratorio principal** y **no se ejecutan en GitHub Actions automáticamente**. El QA ligero revisa la coherencia del tutorial, sintaxis y resultados unitarios; la integración completa requiere una ejecución manual y explícitamente autorizada.

Documentación: [Dask Distributed](https://distributed.dask.org/) · [Dask buenas prácticas](https://docs.dask.org/en/stable/best-practices.html) · [GitHub Codespaces](https://docs.github.com/en/codespaces).
