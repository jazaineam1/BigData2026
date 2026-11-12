# S11 · OCR, ASR, extracción y búsqueda (laboratorio del estudiante)

Esta rama es un espacio de práctica mínimo. No contiene Airflow, otros cuadernos, evaluaciones ni documentos del profesor.

## Iniciar

En GitHub elige rama `s11-estudiantes` y crea Codespace sobre ESA rama. En esta rama existe un único perfil de contenedor, S11.

~~~bash
python --version
tesseract --list-langs
python lab.py --help
python lab.py preparar
python lab.py ocr
cat salidas/ocr.json
tesseract salidas/afiche_simulado.png stdout -l spa --psm 6
python lab.py asr
cat salidas/asr.json
python lab.py evaluar-asr
python lab.py extraer
cat salidas/extraccion.json
~~~

Es la ruta **introductoria**. El material inicial es sintético; no es una noticia real. Abre la imagen y escucha el audio para verificar las cifras.

## Embeddings y búsqueda

~~~bash
bash iniciar_ollama.sh
python lab.py indexar
python lab.py buscar --consulta "¿Cuál era el valor declarado?"
python verificar_independiente.py --caso lab --modelo
~~~

El modelo de texto `embeddinggemma-2:270m` genera vectores de 768 dimensiones y prioriza fragmentos similares, NO certifica los hechos.

## Reutilizar con un proyecto diferente

~~~bash
python proyecto.py iniciar --destino proyectos/mi_caso
cp salidas/afiche_simulado.png proyectos/mi_caso/entradas/imagenes/
cp salidas/voz_simulada.wav proyectos/mi_caso/entradas/audios/
python proyecto.py plan --config proyectos/mi_caso/config.json
python proyecto.py procesar --config proyectos/mi_caso/config.json
python proyecto.py indexar --config proyectos/mi_caso/config.json
python proyecto.py buscar --config proyectos/mi_caso/config.json --consulta "¿Qué valor menciona el caso?"
python proyecto.py auditar --config proyectos/mi_caso/config.json
python verificar_independiente.py --proyecto proyectos/mi_caso
~~~

Mira `catalogo.jsonl`, `candidatos.jsonl`, `catalogo.parquet` y `manifest.json`. Para un ejercicio propio cambia archivos autorizados sin modificar el motor.

## Interfaz opcional

~~~bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
~~~

Mantén el puerto 8501 PRIVADO. El panel llama las mismas funciones del motor que la terminal.

## Instalar en tu computador

Lee `INSTALACION_UBUNTU.md`. Codespaces trae paquetes de sistema en la imagen del contenedor; los estudiantes deben aprender también a instalarlos, diagnosticarlos y actualizarlos.

**Nota de acceso:** una rama con menos archivos no protege las demás ramas de un repositorio público. Para materiales verdaderamente privados debe usarse otro repositorio privado.
