# -*- coding: utf-8 -*-
"""Genera la sesión 7 integral: Elasticsearch, BM25 y despliegue desde Colab.

Fuentes oficiales verificadas: 2026-09-23.
El cuaderno público no contiene tiempos, credenciales ni material docente privado.
"""
from pathlib import Path
import json
import nbformat

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "Cuadernos" / "7_Elasticsearch_BM25_Compras_Claras.ipynb"

NOTEBOOK_JSON = r'''{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "<a href=\"https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/Cuadernos/7_Elasticsearch_BM25_Compras_Claras.ipynb\" target=\"_parent\"><img src=\"https://colab.research.google.com/assets/colab-badge.svg\" alt=\"Abrir S7 en Google Colab\"></a>\n\n# Sesión 7 — Construye un buscador con Elasticsearch\n\n**Caso conductor:** Compras Claras  \n**Entrada única de la sesión:** https://jazaineam1.github.io/BigData2026/assets/tutoriales/s07-recursos.html  \n**Presentación:** https://jazaineam1.github.io/BigData2026/Presentaciones/s07-del-vecindario-al-texto.html  \n**Guía de despliegue:** https://jazaineam1.github.io/BigData2026/assets/tutoriales/s07-despliegue-elasticsearch.html  \n**Checklist técnico:** https://jazaineam1.github.io/BigData2026/assets/tutoriales/s07-laboratorio-guiado.html\n\n## Pregunta profesional\n\nLaura ya tiene contexto contractual desde S6. Ahora necesita decidir **qué procesos leer primero cuando busca una necesidad textual**, por ejemplo “mantenimiento de aeronaves”.\n\nHoy no vas a aprender Elasticsearch mirando una demo. Vas a construir una solución mínima completa:\n\n**corpus → analyzer → índice → ingesta → consulta → ranking → decisión con límites**.\n\n**Entorno:** Google Colab + Elasticsearch Serverless. No necesitas Bash, Docker ni una VM."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Lo que reutilizamos y lo que es nuevo\n\nYa vienes trabajando con Colab, Python, DataFrames, JSON, bases NoSQL, credenciales de servicios cloud y el caso Compras Claras. Por eso aquí no repetimos esas bases.\n\nLo nuevo es específico de búsqueda:\n\n| Concepto | Para qué lo necesitas hoy |\n|---|---|\n| <code>text</code> vs <code>keyword</code> | decidir cómo indexar cada campo |\n| analyzer | convertir texto en términos buscables |\n| índice invertido | localizar candidatos sin recorrer todo el corpus |\n| BM25 | ordenar candidatos por relevancia léxica |\n| mapping | declarar cómo se indexará el documento |\n| <code>bulk()</code> | cargar muchos documentos eficientemente |\n| <code>match</code> / <code>multi_match</code> | construir búsqueda full-text |\n| <code>filter</code> | restringir sin aportar score |\n| <code>highlight</code> | inspeccionar dónde coincidió el texto |\n\n**PARA LLEVAR.** Esta sesión no consiste en memorizar Query DSL. Consiste en aprender a diseñar, desplegar, comprobar e interpretar una búsqueda."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Producto observable\n\nAl terminar debes tener una búsqueda ejecutada sobre Elasticsearch real —o una contingencia claramente declarada— y tres archivos sin credenciales:\n\n1. <code>s07_resultados_busqueda.csv</code>: top 5 de dos configuraciones A/B.\n2. <code>s07_config_busqueda.json</code>: índice, corpus, consulta, conteos y configuración; nunca incluye endpoint ni API key.\n3. <code>hito_s07_relevancia.md</code>: decisión, alternativa descartada, cambio controlado, P@5, resultado dudoso y límite.\n\n### Rúbrica\n\n| Evidencia | Peso |\n|---|---:|\n| conexión real + índice propio + conteo verificado | 25 |\n| mapping + analyzer interpretados | 15 |\n| consulta escalonada y ranking | 20 |\n| experimento A/B + juicio de relevancia / P@5 | 20 |\n| decisión + alternativa + resultado dudoso + límite concreto | 15 |\n| trazabilidad sin secretos | 5 |\n\n**La ruta BM25 local permite continuar si Cloud falla, pero no sustituye la evidencia de despliegue.**"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Mapa de la sesión\n\n| Bloque | Pregunta | Acción | Producto |\n|---|---|---|---|\n| A · Relevancia | ¿por qué <code>contains()</code> no basta? | comparar literal vs BM25 local | ranking de referencia |\n| B · Conexión | ¿Python habla con mi proyecto? | conectar con API key | <code>client.info()</code> |\n| C · Indexación | ¿cómo entiende Elastic mis campos? | mapping + <code>_analyze</code> | índice propio + tokens |\n| D · Ingesta | ¿quedaron cargados todos los documentos? | <code>bulk()</code> + <code>count</code> | 1.994 documentos |\n| E · Consulta | ¿cómo se construye relevancia y cómo se filtra? | match → multi_match → boost → filter → highlight | top 5 explicable |\n| F · Experimento | ¿cambiar el ranking lo mejora? | A/B por boost + juicios de relevancia | posiciones + P@5 |\n| G · Cierre | ¿qué puedo sostener? | exportar evidencia | CSV + JSON + hito |\n\n**Semáforo:** 🧠 entiende · ▶️ ejecuta · ✏️ modifica."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# A · Antes de Elastic: del corpus al ranking\n\n## A1. El corpus real que llega desde S6\n\nNo descargamos SECOP en vivo. Usamos el archivo versionado por el curso:\n\n<code>Datos/s06_contexto_relacional.csv</code>\n\nEl archivo contiene registros candidatos e históricos del caso. Para búsqueda trabajaremos a nivel de **proceso único**.\n\n**Procedencia:** el corpus es el producto versionado de S6. Esta sesión no lo presenta como una muestra representativa de todo SECOP."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "import pandas as pd\nimport numpy as np\nimport json, re, math, unicodedata\nfrom collections import Counter\nfrom pathlib import Path\nfrom IPython.display import display\n\nURL_S06 = \"https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Datos/s06_contexto_relacional.csv\"\nURL_FALLBACK = \"https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Datos/s07_corpus_respaldo.jsonl\"\n\ntry:\n    bruto = pd.read_csv(URL_S06, dtype=str, keep_default_na=False)\n    origen_corpus = \"S6 versionado · s06_contexto_relacional.csv\"\nexcept Exception as e:\n    print(\"No se pudo cargar el corpus S6:\", type(e).__name__)\n    bruto = pd.read_json(URL_FALLBACK, lines=True, dtype=False).fillna(\"\").astype(str)\n    origen_corpus = \"respaldo mínimo S07\"\n\ncolumnas = [\n    \"tipo_registro\",\"entidad\",\"departamento_entidad\",\"id_proceso\",\n    \"nombre_proceso\",\"descripcion\",\"modalidad\",\"url_secop\"\n]\nfor col in columnas:\n    if col not in bruto.columns:\n        bruto[col] = \"\"\n\nif origen_corpus == \"respaldo mínimo S07\" and (bruto[\"tipo_registro\"].astype(str).str.len() == 0).all():\n    bruto[\"tipo_registro\"] = \"historico_adjudicado\"\n\ncorpus = (\n    bruto[columnas]\n    .copy()\n    .drop_duplicates(\"id_proceso\", keep=\"first\")\n    .reset_index(drop=True)\n)\ncorpus[\"texto_busqueda\"] = (\n    corpus[\"nombre_proceso\"].fillna(\"\").astype(str) + \" \" +\n    corpus[\"descripcion\"].fillna(\"\").astype(str)\n).str.strip()\n\nprint(\"Origen:\", origen_corpus)\nprint(\"Filas fuente:\", len(bruto))\nprint(\"Procesos únicos:\", len(corpus))\nprint(\"Entidades:\", corpus[\"entidad\"].nunique())\ndisplay(corpus.head(5))"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** “Filas fuente” cuenta registros del archivo; “procesos únicos” cuenta IDs distintos después de deduplicar.\n\n**Qué nos dice.** Si cargaste el archivo principal del curso debes observar **2.109 filas fuente y 1.994 procesos únicos**.\n\n**Qué NO permite concluir todavía.** Tener 1.994 procesos no significa que el corpus represente toda la contratación pública colombiana. Falta un marco de muestreo de SECOP completo.\n\n**Qué error común.** Confundir una fila histórica proceso–proveedor con un proceso nuevo. Para búsqueda textual hoy deduplicamos por <code>id_proceso</code>."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## A2. Línea base: coincidencia literal\n\nAntes de construir relevancia, veamos qué responde una búsqueda binaria.\n\nLa consulta de demostración será:\n\n**mantenimiento aeronaves**\n\nPrimero pedimos algo mucho más simple: “¿aparecen literalmente estas dos palabras?”"
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "consulta_demo = \"mantenimiento aeronaves\"\nterminos_demo = consulta_demo.lower().split()\n\nmascara_literal = pd.Series(True, index=corpus.index)\nfor termino in terminos_demo:\n    mascara_literal &= corpus[\"texto_busqueda\"].str.lower().str.contains(\n        termino, regex=False, na=False\n    )\n\nliteral = corpus.loc[\n    mascara_literal,\n    [\"id_proceso\",\"entidad\",\"nombre_proceso\",\"descripcion\",\"url_secop\"]\n].copy()\n\nprint(\"Coincidencias literales con TODOS los términos:\", len(literal))\ndisplay(literal.head(10))"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** Cada fila contiene literalmente todos los términos de la consulta en el texto combinado.\n\n**Qué nos dice.** <code>contains()</code> sirve como línea base transparente.\n\n**Qué NO permite concluir todavía.** No responde cuál documento es más relevante. Todas las coincidencias quedan “empatadas”.\n\n**Qué error común.** Llamar “ranking” a una lista que solo cumple una condición booleana."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## A3. Analyzer e índice invertido, en pequeño\n\nEl motor no necesita recorrer todos los documentos cada vez. Primero transforma texto en términos y construye una estructura término → documentos.\n\nLa función de abajo es **solo pedagógica**. No intenta reproducir exactamente el analyzer <code>spanish</code> de Elasticsearch."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "STOP = {\"de\",\"la\",\"el\",\"los\",\"las\",\"del\",\"y\",\"en\",\"para\",\"por\",\"un\",\"una\",\"con\",\"al\",\"se\",\"su\",\"sus\",\"que\",\"es\"}\n\ndef tokens_didacticos(texto):\n    texto = unicodedata.normalize(\"NFKD\", str(texto))\n    texto = \"\".join(c for c in texto if not unicodedata.combining(c)).lower()\n    tokens = re.findall(r\"[a-z0-9]+\", texto)\n    return [t for t in tokens if len(t) > 2 and t not in STOP]\n\nmicro = pd.DataFrame({\n    \"id\":[\"D1\",\"D2\",\"D3\",\"D4\"],\n    \"texto\":[\n        \"mantenimiento programado de aeronaves KFIR\",\n        \"inspección y mantenimiento estructural de aeronave C-130\",\n        \"construcción de centro de investigación aeronáutica\",\n        \"adquisición de blindajes aeronáuticos\"\n    ]\n})\nmicro[\"tokens\"] = micro[\"texto\"].map(tokens_didacticos)\ndisplay(micro)"
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "indice_invertido = {}\nfor _, fila in micro.iterrows():\n    for termino in set(fila[\"tokens\"]):\n        indice_invertido.setdefault(termino, []).append(fila[\"id\"])\n\npd.DataFrame(\n    [{\"termino\": t, \"documentos\": \", \".join(ids)}\n     for t, ids in sorted(indice_invertido.items())]\n)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** La tabla va de término a documentos, no de documento a palabras.\n\n**Qué nos dice.** Esa inversión permite localizar candidatos sin inspeccionar el texto completo de cada documento en cada consulta.\n\n**Qué NO permite concluir todavía.** Saber qué documentos contienen un término no define el orden final.\n\n**Qué error común.** Confundir indexar con buscar. Indexar prepara la estructura; buscar la consulta después."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## A4. BM25 local como respaldo pedagógico\n\nBM25 combina tres intuiciones:\n\n- repetición con saturación;\n- rareza del término en el corpus;\n- normalización por longitud del documento.\n\nLa implementación está oculta porque **el objetivo no es programar BM25**. La usaremos para producir un ranking local si Elastic Cloud falla.\n\n**OJO.** Este tokenizer local no es el analyzer de Elasticsearch. Por eso **no compares scores numéricos entre ambos motores**."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "jupyter": {
     "source_hidden": true
    }
   },
   "outputs": [],
   "source": "def _bm25_scores(textos, consulta, k1=1.2, b=0.75):\n    docs = [tokens_didacticos(x) for x in textos]\n    N = len(docs)\n    lens = np.array([len(d) for d in docs], dtype=float)\n    avgdl = float(lens.mean()) if N else 0.0\n    df_term = Counter()\n    for d in docs:\n        df_term.update(set(d))\n\n    q = tokens_didacticos(consulta)\n    scores = []\n    for i,d in enumerate(docs):\n        tf = Counter(d)\n        score = 0.0\n        for t in q:\n            f = tf.get(t, 0)\n            if not f:\n                continue\n            n = df_term.get(t, 0)\n            idf = math.log(1 + (N - n + 0.5) / (n + 0.5))\n            den = f + k1 * (1 - b + b * (lens[i] / avgdl if avgdl else 0))\n            score += idf * (f * (k1 + 1)) / den\n        scores.append(score)\n    return np.array(scores, dtype=float)\n\ndef _ordenar_scores(df, scores):\n    out = df.copy()\n    out[\"score\"] = scores\n    out = (\n        out[out[\"score\"] > 0]\n        .sort_values([\"score\",\"id_proceso\"], ascending=[False,True])\n        .reset_index(drop=True)\n    )\n    out.insert(0, \"rank\", range(1, len(out)+1))\n    return out\n\ndef buscar_bm25_local(df, consulta):\n    return _ordenar_scores(\n        df,\n        _bm25_scores(df[\"texto_busqueda\"], consulta)\n    )\n\ndef buscar_bm25_local_campos(df, consulta, peso_nombre=1.0):\n    \"\"\"Respaldo didáctico: combina BM25 por campo; no replica multi_match exactamente.\"\"\"\n    score_nombre = _bm25_scores(df[\"nombre_proceso\"], consulta)\n    score_descripcion = _bm25_scores(df[\"descripcion\"], consulta)\n    return _ordenar_scores(\n        df,\n        peso_nombre * score_nombre + score_descripcion\n    )\n"
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "ranking_local_demo = buscar_bm25_local(corpus, consulta_demo)\nprint(\"Resultados con score > 0:\", len(ranking_local_demo))\ndisplay(\n    ranking_local_demo[\n        [\"rank\",\"id_proceso\",\"entidad\",\"nombre_proceso\",\"score\",\"url_secop\"]\n    ].head(10)\n)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** Ahora sí aparece un orden: mayor score local → mayor coincidencia léxica bajo este modelo didáctico.\n\n**Qué nos dice.** Un ranking puede distinguir candidatos que la coincidencia binaria trataba igual.\n\n**Qué NO permite concluir todavía.** El score no es probabilidad, calidad contractual ni riesgo. Tampoco es comparable numéricamente con el score que obtendremos luego en Elasticsearch.\n\n**Qué error común.** Buscar el score “más alto posible”. La pregunta útil es si el ranking mejora para una necesidad concreta."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# B · Desplegar: Python debe hablar con Elasticsearch real\n\nLa documentación vigente de Elastic recomienda **Elasticsearch Serverless** como una ruta simple para empezar. El quickstart oficial de keyword search con Python sigue este patrón:\n\n**proyecto → Project URL → API key → cliente Python → índice → documentos → búsqueda**\n\nGuía visual del curso:  \nhttps://jazaineam1.github.io/BigData2026/assets/tutoriales/s07-despliegue-elasticsearch.html\n\nDocumentación oficial verificada el **23-sep-2026**:\n\n- https://www.elastic.co/docs/solutions/search/get-started/keyword-search-python\n- https://www.elastic.co/docs/reference/elasticsearch/clients/python/getting-started\n- https://www.elastic.co/docs/deploy-manage/api-keys/serverless-project-api-keys\n\n**HAZ ESTO AHORA.** Antes de la siguiente celda debes tener un proyecto Elasticsearch, su Project URL y una API key del proyecto."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "!pip -q install -U elasticsearch pandas tabulate"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## B1. Crea un nombre de índice que no choque con el de otro equipo\n\nSi varios equipos comparten proyecto, todos escribir <code>s07_compras_claras</code> produciría colisiones.\n\nCambia el alias. Usa solo algo reconocible para tu equipo; no pongas correo, documento ni datos personales."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "ALIAS = \"equipo_demo\" #@param {type:\"string\"}\n\ndef slug_indice(valor):\n    valor = unicodedata.normalize(\"NFKD\", str(valor))\n    valor = \"\".join(c for c in valor if not unicodedata.combining(c)).lower()\n    valor = re.sub(r\"[^a-z0-9]+\", \"-\", valor).strip(\"-\")\n    return (valor or \"equipo-demo\")[:35]\n\nalias_seguro = slug_indice(ALIAS)\nINDEX_NAME = f\"s07-compras-claras-{alias_seguro}\"\nprint(\"Índice de este equipo:\", INDEX_NAME)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## B2. Conecta sin escribir secretos en el notebook\n\nLa API key se captura con <code>getpass()</code>; no aparece en la salida ni se guarda en los archivos finales.\n\n**Qué debe verse si salió bien:** información del producto/versión y <code>Modo: Elasticsearch real</code>.\n\n**Error probable:** 401/403 → credencial; timeout → Project URL/red."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "from getpass import getpass\nfrom elasticsearch import Elasticsearch\n\nUSAR_ELASTIC = True #@param {type:\"boolean\"}\nclient = None\nmotor_real = \"BM25 local de respaldo\"\nconexion_error = \"\"\n\nif USAR_ELASTIC:\n    endpoint = input(\"Project URL de Elasticsearch (https://...): \").strip()\n    api_key = getpass(\"API key del proyecto: \").strip()\n    try:\n        client = Elasticsearch(endpoint, api_key=api_key, request_timeout=30)\n        info = client.info()\n        motor_real = \"Elasticsearch real\"\n        print(\"Conexión verificada.\")\n        print(\"Producto:\", info.get(\"tagline\", \"Elasticsearch\"))\n        print(\"Versión:\", info.get(\"version\", {}).get(\"number\", \"serverless/no informada\"))\n    except Exception as e:\n        conexion_error = f\"{type(e).__name__}: {e}\"\n        client = None\n        print(\"No se pudo conectar:\", type(e).__name__)\n        print(\"Continúa con el respaldo local y documenta el error.\")\nelse:\n    print(\"Modo local elegido.\")\n\nprint(\"Modo:\", motor_real)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** <code>client.info()</code> es una prueba de conectividad/autorización, no de que el índice exista.\n\n**Qué nos dice.** Si respondió, Python ya puede enviar solicitudes al servicio.\n\n**Qué NO permite concluir todavía.** No sabemos si el mapping es correcto ni si los documentos fueron indexados.\n\n**Qué error común.** Cambiar el query cuando el problema real es que todavía no hay conexión."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# C · Mapping y analyzer: decidir antes de cargar\n\n## C1. Diseña los campos según su uso\n\n- <code>nombre_proceso</code> y <code>descripcion</code>: búsqueda full-text → <code>text</code> + analyzer <code>spanish</code>.\n- <code>id_proceso</code>, <code>entidad</code>, <code>departamento_entidad</code>, <code>modalidad</code>, <code>tipo_registro</code>: igualdad/filtros → <code>keyword</code>.\n- <code>url_secop</code>: queremos recuperarla, no buscar por ella → se guarda pero no se indexa."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "mappings = {\n    \"properties\": {\n        \"id_proceso\": {\"type\": \"keyword\"},\n        \"tipo_registro\": {\"type\": \"keyword\"},\n        \"entidad\": {\"type\": \"keyword\"},\n        \"departamento_entidad\": {\"type\": \"keyword\"},\n        \"modalidad\": {\"type\": \"keyword\"},\n        \"nombre_proceso\": {\"type\": \"text\", \"analyzer\": \"spanish\"},\n        \"descripcion\": {\"type\": \"text\", \"analyzer\": \"spanish\"},\n        \"url_secop\": {\"type\": \"keyword\", \"index\": False}\n    }\n}\n\npd.DataFrame(\n    [{\"campo\": k, **v} for k,v in mappings[\"properties\"].items()]\n)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## C2. Crea el índice de forma repetible\n\nLa celda elimina **solo el índice personal de tu alias** si ya existe y lo vuelve a crear. Esto hace el laboratorio idempotente."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    if client.indices.exists(index=INDEX_NAME):\n        client.indices.delete(index=INDEX_NAME)\n        print(\"Índice anterior eliminado:\", INDEX_NAME)\n\n    respuesta = client.indices.create(\n        index=INDEX_NAME,\n        mappings=mappings\n    )\n    print(\"Índice creado:\", respuesta.get(\"acknowledged\", True), INDEX_NAME)\nelse:\n    print(\"Sin conexión Elastic: se omite la creación del índice.\")"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## C3. Observa el analyzer real\n\nNo adivines qué hace <code>spanish</code>. Pregúntale a Elasticsearch.\n\nLa API <code>_analyze</code> devuelve los tokens generados por el analyzer."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "texto_analisis = \"Servicios de MANTENIMIENTO de las Aeronaves\"\n\nif client is not None:\n    analisis = client.indices.analyze(\n        index=INDEX_NAME,\n        analyzer=\"spanish\",\n        text=texto_analisis\n    )\n    tokens_elastic = [t[\"token\"] for t in analisis[\"tokens\"]]\n    print(\"Texto:\", texto_analisis)\n    print(\"Tokens Elastic:\", tokens_elastic)\nelse:\n    tokens_elastic = []\n    print(\"Sin Elastic: tokens didácticos =\", tokens_didacticos(texto_analisis))"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** La salida muestra los términos que realmente entran al índice/búsqueda bajo el analyzer elegido.\n\n**Qué nos dice.** El analyzer de idioma puede eliminar stopwords y acercar variantes morfológicas mediante stemming.\n\n**Qué NO permite concluir todavía.** Ver tokens no nos dice si la relevancia final será buena para usuarios reales.\n\n**Qué error común.** Esperar que el analyzer resuelva sinónimos o intención semántica. Eso abre la pregunta de S9."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# D · Ingesta: cargar y verificar\n\n## D1. Prepara documentos limpios\n\nCada documento conservará solo los campos que realmente forman parte de la búsqueda o de la explicación del resultado."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "campos_fuente = [\n    \"id_proceso\",\"tipo_registro\",\"entidad\",\"departamento_entidad\",\n    \"modalidad\",\"nombre_proceso\",\"descripcion\",\"url_secop\"\n]\n\ndocumentos = corpus[campos_fuente].fillna(\"\").astype(str).to_dict(\"records\")\nprint(\"Documentos preparados:\", len(documentos))\nprint(\"Primer ID:\", documentos[0][\"id_proceso\"])"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## D2. Carga con <code>bulk()</code>\n\nElastic recomienda los bulk helpers para ingestas de muchos documentos. El patrón también evita escribir un ciclo de requests individuales.\n\n**Qué debe verse:** documentos indexados = 1.994 y errores = 0 cuando trabajas con el corpus principal."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "from elasticsearch.helpers import bulk\n\nbulk_ok = 0\nbulk_errores = []\n\nif client is not None:\n    acciones = (\n        {\n            \"_index\": INDEX_NAME,\n            \"_id\": d[\"id_proceso\"],\n            \"_source\": d\n        }\n        for d in documentos\n    )\n    bulk_ok, bulk_errores = bulk(\n        client,\n        acciones,\n        refresh=True,\n        raise_on_error=False\n    )\n    print(\"Documentos indexados:\", bulk_ok)\n    print(\"Errores bulk:\", len(bulk_errores))\nelse:\n    print(\"Sin Elastic: ingesta omitida.\")"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## D3. Verifica con una consulta independiente\n\nNo des por hecho que <code>bulk()</code> terminó bien. Cuenta documentos desde el motor y compáralos con el DataFrame."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    conteo_elastic = client.count(index=INDEX_NAME)[\"count\"]\n    conteo_local = len(corpus)\n    print(\"Conteo local:\", conteo_local)\n    print(\"Conteo Elasticsearch:\", conteo_elastic)\n    print(\"¿Coinciden?:\", conteo_elastic == conteo_local)\n    assert conteo_elastic == conteo_local, \"La ingesta no coincide con el corpus.\"\nelse:\n    conteo_elastic = None\n    print(\"Conteo local:\", len(corpus))\n    print(\"Conteo Elasticsearch: no ejecutado\")"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** La comprobación compara dos sistemas: el DataFrame fuente y el índice.\n\n**Qué nos dice.** Si coinciden, la cantidad de documentos indexados corresponde a la cantidad que intentamos cargar.\n\n**Qué NO permite concluir todavía.** El conteo correcto no prueba que los campos estén bien modelados ni que el ranking sea útil.\n\n**Qué error común.** Ver “bulk sin excepción” y asumir que todo está bien sin mirar errores ni conteo."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# E · Query ladder: construir la búsqueda por capas\n\nLa idea es añadir **una decisión por vez**. Así puedes explicar qué aporta cada capa.\n\nPrimero dejamos una función de presentación para no repetir código de formato."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "cellView": "form",
    "jupyter": {
     "source_hidden": true
    }
   },
   "outputs": [],
   "source": "def mostrar_hits(resp):\n    filas = []\n    for pos, h in enumerate(resp.get(\"hits\", {}).get(\"hits\", []), start=1):\n        src = h.get(\"_source\", {})\n        high = h.get(\"highlight\", {})\n        fragmentos = []\n        for piezas in high.values():\n            fragmentos.extend(piezas)\n        filas.append({\n            \"rank\": pos,\n            \"id_proceso\": src.get(\"id_proceso\",\"\"),\n            \"score\": h.get(\"_score\"),\n            \"entidad\": src.get(\"entidad\",\"\"),\n            \"nombre_proceso\": src.get(\"nombre_proceso\",\"\"),\n            \"highlight\": \" ... \".join(fragmentos),\n            \"url_secop\": src.get(\"url_secop\",\"\")\n        })\n    return pd.DataFrame(filas)\n"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## E1. <code>match</code>: un campo\n\nBuscamos la consulta de demostración solo dentro de <code>descripcion</code>."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    resp_match = client.search(\n        index=INDEX_NAME,\n        query={\"match\": {\"descripcion\": consulta_demo}},\n        size=5\n    )\n    tabla_match = mostrar_hits(resp_match)\n    display(tabla_match)\nelse:\n    tabla_match = ranking_local_demo.head(5)\n    print(\"Respaldo local:\")\n    display(tabla_match[[\"rank\",\"id_proceso\",\"entidad\",\"nombre_proceso\",\"score\",\"url_secop\"]])"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** Cada hit tiene <code>_source</code>, <code>_id</code> y <code>_score</code>; por defecto la búsqueda ordena por score.\n\n**Qué nos dice.** Ya estamos haciendo full-text search, no coincidencia literal.\n\n**Qué NO permite concluir todavía.** Un score mayor dentro de esta consulta no implica que el documento sea “mejor” en general.\n\n**Qué error común.** Comparar este score con el de otra consulta como si fuera una escala fija."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## E2. <code>multi_match</code>: nombre + descripción\n\nAhora permitimos coincidencias en dos campos."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    query_multi = {\n        \"multi_match\": {\n            \"query\": consulta_demo,\n            \"fields\": [\"nombre_proceso\", \"descripcion\"]\n        }\n    }\n    resp_multi = client.search(\n        index=INDEX_NAME,\n        query=query_multi,\n        size=5\n    )\n    tabla_multi = mostrar_hits(resp_multi)\n    display(tabla_multi)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## E3. Boost: el nombre pesa más\n\nEl <code>^2</code> representa una decisión de diseño: una coincidencia en el nombre del proceso debe aportar más que la misma coincidencia en una descripción extensa."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    query_boost = {\n        \"multi_match\": {\n            \"query\": consulta_demo,\n            \"fields\": [\"nombre_proceso^2\", \"descripcion\"]\n        }\n    }\n    resp_boost = client.search(\n        index=INDEX_NAME,\n        query=query_boost,\n        size=5\n    )\n    tabla_boost = mostrar_hits(resp_boost)\n    display(tabla_boost)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## E4. <code>filter</code>: restringir sin convertir la condición en score\n\nQueremos buscar texto **solo entre registros históricos adjudicados**.\n\nLa condición exacta vive en <code>filter</code>. La relevancia textual vive en <code>must</code>."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    query_filtrada = {\n        \"bool\": {\n            \"must\": [{\n                \"multi_match\": {\n                    \"query\": consulta_demo,\n                    \"fields\": [\"nombre_proceso^2\", \"descripcion\"]\n                }\n            }],\n            \"filter\": [{\n                \"term\": {\"tipo_registro\": \"historico_adjudicado\"}\n            }]\n        }\n    }\n    resp_filter = client.search(\n        index=INDEX_NAME,\n        query=query_filtrada,\n        size=5\n    )\n    tabla_filter = mostrar_hits(resp_filter)\n    display(tabla_filter)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## E5. <code>highlight</code>: inspeccionar por qué apareció\n\nEl score ordena. El highlight nos ayuda a revisar el texto que produjo la coincidencia."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    resp_highlight = client.search(\n        index=INDEX_NAME,\n        query=query_filtrada,\n        highlight={\n            \"fields\": {\n                \"nombre_proceso\": {},\n                \"descripcion\": {}\n            }\n        },\n        size=5\n    )\n    tabla_highlight = mostrar_hits(resp_highlight)\n    display(\n        tabla_highlight[\n            [\"rank\",\"id_proceso\",\"score\",\"nombre_proceso\",\"highlight\",\"url_secop\"]\n        ]\n    )"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** El ranking viene del bloque de búsqueda; el filtro restringe; el highlight muestra fragmentos coincidentes.\n\n**Qué nos dice.** Podemos separar claramente “qué tan bien coincide” de “qué condición debe cumplir”.\n\n**Qué NO permite concluir todavía.** Un fragmento resaltado no explica por sí solo toda la puntuación BM25 ni valida la pertinencia profesional.\n\n**Qué error común.** Meter todo en <code>must</code> y dejar que condiciones categóricas alteren la lógica de relevancia."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# F · Experimento propio: una perilla, una consecuencia\n\n## F1. Consulta asignada por alias\n\nPara que el resultado sea realmente tuyo, el alias determina de manera reproducible una consulta de trabajo.\n\nLas consultas provienen de temas presentes en el corpus versionado."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "CONSULTAS = [\n    \"mantenimiento equipos\",\n    \"salud publica\",\n    \"gestion ambiental\",\n    \"transporte publico\",\n    \"software informacion\"\n]\n\nindice_consulta = sum(ord(c) for c in alias_seguro) % len(CONSULTAS)\nconsulta_personal = CONSULTAS[indice_consulta]\n\nprint(\"Alias:\", alias_seguro)\nprint(\"Consulta asignada:\", consulta_personal)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## F2. Configuración A: sin boost\n\nMantendremos constante:\n\n- el corpus;\n- la consulta;\n- el filtro;\n- el número de resultados.\n\nSolo cambiaremos el peso del campo <code>nombre_proceso</code>.\n\n**Contingencia local.** Si no hay Elastic, el cuaderno combina un BM25 separado para <code>nombre_proceso</code> y <code>descripcion</code>. Sirve para observar el efecto del peso, pero **no reproduce exactamente** la implementación de <code>multi_match</code> de Elasticsearch."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "def ejecutar_config_elastic(campos, consulta):\n    q = {\n        \"bool\": {\n            \"must\": [{\n                \"multi_match\": {\n                    \"query\": consulta,\n                    \"fields\": campos\n                }\n            }],\n            \"filter\": [{\n                \"term\": {\"tipo_registro\": \"historico_adjudicado\"}\n            }]\n        }\n    }\n    return client.search(\n        index=INDEX_NAME,\n        query=q,\n        highlight={\"fields\":{\"nombre_proceso\":{},\"descripcion\":{}}},\n        size=5\n    )\n\nif client is not None:\n    tabla_A = mostrar_hits(\n        ejecutar_config_elastic(\n            [\"nombre_proceso\",\"descripcion\"],\n            consulta_personal\n        )\n    )\nelse:\n    local_A = buscar_bm25_local_campos(\n        corpus, consulta_personal, peso_nombre=1.0\n    ).head(5)\n    tabla_A = local_A.rename(columns={\"score\":\"score\"})[\n        [\"rank\",\"id_proceso\",\"score\",\"entidad\",\"nombre_proceso\",\"url_secop\"]\n    ].copy()\n    tabla_A[\"highlight\"] = \"\"\n\nprint(\"CONFIGURACIÓN A\")\ndisplay(tabla_A)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## F3. Configuración B: mismo query, más peso al nombre\n\nEsta es la única modificación."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "if client is not None:\n    tabla_B = mostrar_hits(\n        ejecutar_config_elastic(\n            [\"nombre_proceso^3\",\"descripcion\"],\n            consulta_personal\n        )\n    )\nelse:\n    local_B = buscar_bm25_local_campos(\n        corpus, consulta_personal, peso_nombre=3.0\n    ).head(5)\n    tabla_B = local_B[\n        [\"rank\",\"id_proceso\",\"score\",\"entidad\",\"nombre_proceso\",\"url_secop\"]\n    ].copy()\n    tabla_B[\"highlight\"] = \"\"\n\nprint(\"CONFIGURACIÓN B\")\ndisplay(tabla_B)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## F4. Compara posiciones, no solo scores\n\nComo los scores cambian con la configuración, observamos primero el **orden de IDs**."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "def posiciones(tabla, etiqueta):\n    return (\n        tabla[[\"id_proceso\",\"rank\"]]\n        .rename(columns={\"rank\": f\"rank_{etiqueta}\"})\n    )\n\ncomparacion = posiciones(tabla_A,\"A\").merge(\n    posiciones(tabla_B,\"B\"),\n    on=\"id_proceso\",\n    how=\"outer\"\n)\ncomparacion[\"cambio_posicion\"] = comparacion[\"rank_A\"] - comparacion[\"rank_B\"]\n\nprint(\"IDs comunes en top 5:\", len(set(tabla_A[\"id_proceso\"]) & set(tabla_B[\"id_proceso\"])))\ndisplay(comparacion.sort_values([\"rank_A\",\"rank_B\"], na_position=\"last\"))"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** Cambio positivo significa que el documento subió posiciones en B; negativo, que bajó.\n\n**Qué nos dice.** Manteniendo lo demás fijo, puedes atribuir cambios de posición al aumento de peso de <code>nombre_proceso</code>.\n\n**Qué NO permite concluir todavía.** Que el ranking B sea “mejor”. Para eso necesitarías juicios de relevancia o comportamiento de usuarios, no solo movimiento de posiciones.\n\n**Qué error común.** Tunear relevancia mirando únicamente scores sin definir qué significa “mejor” para la tarea."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## F5. ¿El ranking B es realmente mejor?\n\nMover documentos no demuestra una mejora. En búsqueda necesitas una **regla de relevancia** y juicios sobre los resultados.\n\nAntes de etiquetar, escribe una regla breve y observable para tu consulta.\n\nEjemplo para “salud pública”:\n\n> Relevante = el nombre o la descripción del proceso trata directamente una actividad, servicio o intervención de salud pública.\n\nNo califiques si el contrato es bueno o malo; califica si **responde a la necesidad de búsqueda**."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "CRITERIO_RELEVANCIA = \"Escribe una regla observable para decidir si un resultado responde a tu consulta.\" #@param {type:\"string\"}\n\nif len(CRITERIO_RELEVANCIA.strip()) < 25:\n    print(\"OJO: concreta mejor el criterio antes de etiquetar.\")\nelse:\n    print(\"Consulta:\", consulta_personal)\n    print(\"Criterio:\", CRITERIO_RELEVANCIA)"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Etiqueta el top 5\n\nPara cada configuración marca:\n\n- <code>1</code> = relevante para la necesidad;\n- <code>0</code> = no relevante.\n\nLa métrica didáctica será **Precision@5**:\n\n`P@5 = resultados relevantes entre los cinco primeros / 5`.\n\nLa documentación de Elastic usa esta misma idea en la Ranking Evaluation API: primero se necesitan consultas típicas y **document ratings**; luego se calculan métricas como precision, MRR o DCG."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "def etiquetar_top5(tabla, nombre):\n    etiquetas = []\n    print(f\"\\n=== CONFIGURACIÓN {nombre} ===\")\n    for _, fila in tabla.head(5).iterrows():\n        print(\"\\nRank:\", int(fila[\"rank\"]))\n        print(\"ID:\", fila[\"id_proceso\"])\n        print(\"Nombre:\", fila[\"nombre_proceso\"])\n        if str(fila.get(\"highlight\",\"\")).strip():\n            print(\"Coincidencia:\", fila[\"highlight\"][:500])\n        while True:\n            valor = input(\"¿Relevante según TU criterio? [1=sí / 0=no]: \").strip()\n            if valor in {\"0\",\"1\"}:\n                etiquetas.append(int(valor))\n                break\n            print(\"Escribe solo 1 o 0.\")\n    return etiquetas\n\netiquetas_A = etiquetar_top5(tabla_A, \"A\")\netiquetas_B = etiquetar_top5(tabla_B, \"B\")\n\np5_A = sum(etiquetas_A) / 5\np5_B = sum(etiquetas_B) / 5\n\nprint(\"\\nPrecision@5 A:\", p5_A)\nprint(\"Precision@5 B:\", p5_B)\nprint(\"Cambio P@5 (B - A):\", round(p5_B - p5_A, 3))"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "### Cómo se lee\n\n**Cómo se lee.** <code>P@5 = 0.8</code> significa que 4 de los 5 primeros resultados fueron juzgados relevantes bajo tu criterio.\n\n**Qué nos dice.** Ya no evalúas el tuning solo por “el ranking cambió”; tienes una señal de calidad ligada a una necesidad.\n\n**Qué NO permite concluir todavía.** Cinco resultados y una sola consulta no son una evaluación robusta de un buscador. Para producción necesitas un conjunto representativo de consultas y juicios de relevancia.\n\n**Qué error común.** Ajustar el boost hasta que “se vea bonito” y luego usar esos mismos cinco resultados como si fueran una validación independiente.\n\n**MÁS ADELANTE.** Elasticsearch tiene <code>_rank_eval</code> para evaluar múltiples consultas con ratings y métricas como precision, MRR y DCG. Hoy hacemos la versión mínima manual para entender la lógica."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## F6. Puente a búsqueda semántica\n\nPrueba mentalmente:\n\n**consulta:** “mantenimiento aeronaves”  \n**documento:** “reparación de aviones militares”\n\nPuede haber cercanía conceptual sin compartir suficientes términos.\n\n**PARA LLEVAR.** BM25 es una base fuerte para búsqueda léxica. No convierte automáticamente significado en vectores ni resuelve todos los sinónimos. Esa brecha abre S9."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "---\n# G · Hito y exportación\n\nCompleta las respuestas con base en **tu ejecución**. No respondas con definiciones generales."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "DECISION = \"Escribe qué proceso leerías primero y por qué, citando tu resultado.\" #@param {type:\"string\"}\nALTERNATIVA = \"Escribe qué alternativa descartaste y por qué.\" #@param {type:\"string\"}\nCAMBIO_OBSERVADO = \"Describe qué cambió entre A y B en tu top 5.\" #@param {type:\"string\"}\nDUDOSO = \"Identifica un hit dudoso/falso positivo y explica qué texto lo hizo aparecer.\" #@param {type:\"string\"}\nLIMITE = \"Explica qué NO demuestra este ranking y qué evidencia faltaría.\" #@param {type:\"string\"}\n\nrespuestas = [DECISION,ALTERNATIVA,CAMBIO_OBSERVADO,DUDOSO,LIMITE]\nif any(len(x.strip()) < 20 for x in respuestas):\n    print(\"OJO: una o más respuestas todavía son demasiado generales para entregar.\")\nelse:\n    print(\"Respuestas interpretativas completas.\")"
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "from datetime import datetime, timezone\n\nfecha_utc = datetime.now(timezone.utc).isoformat()\nmotor_export = \"Elasticsearch real\" if client is not None else \"BM25 local de respaldo\"\n\nresultados_export = tabla_A.copy()\nresultados_export[\"configuracion\"] = \"A\"\ntmp_B = tabla_B.copy()\ntmp_B[\"configuracion\"] = \"B\"\nresultados_export = pd.concat([resultados_export,tmp_B],ignore_index=True)\nresultados_export[\"consulta\"] = consulta_personal\nresultados_export[\"motor\"] = motor_export\n\ncolumnas_export = [\n    \"configuracion\",\"rank\",\"id_proceso\",\"score\",\"entidad\",\n    \"nombre_proceso\",\"highlight\",\"url_secop\",\"consulta\",\"motor\"\n]\nfor c in columnas_export:\n    if c not in resultados_export.columns:\n        resultados_export[c] = \"\"\nresultados_export[columnas_export].to_csv(\n    \"s07_resultados_busqueda.csv\",\n    index=False,\n    encoding=\"utf-8-sig\"\n)\n\nconfig = {\n    \"fecha_utc\": fecha_utc,\n    \"autor_alias\": alias_seguro,\n    \"origen_corpus\": origen_corpus,\n    \"filas_fuente\": int(len(bruto)),\n    \"procesos_unicos\": int(len(corpus)),\n    \"motor\": motor_export,\n    \"index_name\": INDEX_NAME if client is not None else None,\n    \"conteo_elasticsearch\": int(conteo_elastic) if conteo_elastic is not None else None,\n    \"consulta\": consulta_personal,\n    \"config_A_fields\": [\"nombre_proceso\",\"descripcion\"],\n    \"config_B_fields\": [\"nombre_proceso^3\",\"descripcion\"],\n    \"filter\": {\"tipo_registro\":\"historico_adjudicado\"},\n    \"criterio_relevancia\": CRITERIO_RELEVANCIA,\n    \"etiquetas_A\": etiquetas_A,\n    \"etiquetas_B\": etiquetas_B,\n    \"precision_at_5_A\": p5_A,\n    \"precision_at_5_B\": p5_B,\n    \"analyzer\": \"spanish\",\n    \"tokens_observados\": tokens_elastic,\n    \"conexion_error\": conexion_error if client is None else None\n}\nPath(\"s07_config_busqueda.json\").write_text(\n    json.dumps(config, ensure_ascii=False, indent=2),\n    encoding=\"utf-8\"\n)\n\nhito = f\"\"\"# Hito S07 — Elasticsearch y relevancia textual\n\n- Autor/alias: {alias_seguro}\n- Fecha UTC: {fecha_utc}\n- Origen del corpus: {origen_corpus}\n- Filas fuente: {len(bruto)}\n- Procesos únicos: {len(corpus)}\n- Motor realmente ejecutado: {motor_export}\n- Índice: {INDEX_NAME if client is not None else \"no creado\"}\n- Consulta asignada: {consulta_personal}\n- Configuración A: nombre_proceso + descripcion\n- Configuración B: nombre_proceso^3 + descripcion\n- Filtro constante: tipo_registro = historico_adjudicado\n- Criterio de relevancia: {CRITERIO_RELEVANCIA}\n- Precision@5 A: {p5_A}\n- Precision@5 B: {p5_B}\n\n## Resultado propio\nTop A: {tabla_A[\"id_proceso\"].tolist()}\nTop B: {tabla_B[\"id_proceso\"].tolist()}\n\n## Decisión\n{DECISION}\n\n## Alternativa descartada\n{ALTERNATIVA}\n\n## Cambio observado\n{CAMBIO_OBSERVADO}\n\n## Resultado dudoso / falso positivo\n{DUDOSO}\n\n## Límite\n{LIMITE}\n\n## Interpretación mínima obligatoria\nLa relevancia textual ordena documentos respecto de una consulta. Por sí sola no demuestra irregularidad, fraude, causalidad ni importancia jurídica.\n\"\"\"\nPath(\"hito_s07_relevancia.md\").write_text(hito, encoding=\"utf-8\")\n\nprint(\"Archivos creados:\")\nprint(\"- s07_resultados_busqueda.csv\")\nprint(\"- s07_config_busqueda.json\")\nprint(\"- hito_s07_relevancia.md\")"
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "try:\n    from google.colab import files\n    for archivo in [\n        \"s07_resultados_busqueda.csv\",\n        \"s07_config_busqueda.json\",\n        \"hito_s07_relevancia.md\"\n    ]:\n        files.download(archivo)\nexcept ImportError:\n    print(\"Fuera de Colab: los archivos quedaron en el directorio de trabajo.\")"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Hoja de trucos\n\n| Necesidad | Idea / API |\n|---|---|\n| comprobar conexión | <code>client.info()</code> |\n| crear índice | <code>client.indices.create(..., mappings=...)</code> |\n| observar analyzer | <code>client.indices.analyze(...)</code> |\n| cargar muchos documentos | <code>elasticsearch.helpers.bulk</code> |\n| comprobar ingesta | <code>client.count()</code> |\n| buscar en un campo | <code>match</code> |\n| buscar en varios campos | <code>multi_match</code> |\n| dar más peso a un campo | <code>nombre_proceso^N</code> |\n| condición exacta sin score | <code>bool.filter + term</code> |\n| mostrar fragmentos coincidentes | <code>highlight</code> |\n\n### Tres errores conceptuales que no debes llevarte\n\n1. <code>keyword</code> no significa “palabra clave de búsqueda”; significa valor no analizado como unidad.\n2. score no es probabilidad ni porcentaje.\n3. filtro y relevancia no son la misma cosa."
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Cierre y limpieza\n\nSi creaste un índice solo para la práctica y no lo vas a reutilizar, puedes borrarlo de forma explícita.\n\nNo borres proyectos o índices ajenos. El cuaderno solo conoce tu <code>INDEX_NAME</code>."
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": "BORRAR_MI_INDICE = False #@param {type:\"boolean\"}\n\nif BORRAR_MI_INDICE and client is not None:\n    if client.indices.exists(index=INDEX_NAME):\n        client.indices.delete(index=INDEX_NAME)\n        print(\"Índice eliminado:\", INDEX_NAME)\n    else:\n        print(\"El índice ya no existe.\")\nelse:\n    print(\"Sin limpieza automática.\")"
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": "## Referencias oficiales · verificadas 23-sep-2026\n\n- Keyword search with Python: https://www.elastic.co/docs/solutions/search/get-started/keyword-search-python\n- Python client: https://www.elastic.co/docs/reference/elasticsearch/clients/python\n- Bulk helpers: https://www.elastic.co/docs/reference/elasticsearch/clients/python/client-helpers\n- Spanish analyzer: https://www.elastic.co/docs/reference/text-analysis/analysis-lang-analyzer\n- BM25 / similarity: https://www.elastic.co/docs/reference/elasticsearch/mapping-reference/similarity\n- Highlighting: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/highlighting\n- Ranking evaluation: https://www.elastic.co/docs/reference/elasticsearch/rest-apis/search-rank-eval\n- Search tutorial: https://www.elastic.co/search-labs/tutorials/search-tutorial/welcome\n\n**Puente a S9:** el tutorial oficial también separa búsqueda de texto completo de búsqueda vectorial/semántica. Hoy cerramos la capa léxica con una solución funcional antes de abrir esa siguiente familia."
  }
 ],
 "metadata": {
  "colab": {
   "name": "7_Elasticsearch_BM25_Compras_Claras.ipynb",
   "provenance": []
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "name": "python",
   "version": "3"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}'''

def main():
    nb = nbformat.from_dict(json.loads(NOTEBOOK_JSON))
    nbformat.validate(nb)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, OUTPUT)
    print(f"[OK] S07 integral generada: {len(nb.cells)} celdas -> {OUTPUT}")

if __name__ == "__main__":
    main()
