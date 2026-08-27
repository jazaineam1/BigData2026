# -*- coding: utf-8 -*-
"""
Genera la Sesión 4 — ¿Qué contrato debe revisar Laura primero?

Continúa exactamente donde se detuvo la sesión 3 (### Hasta aquí el taller):
no repite documentos, CRUD, find() ni agregaciones básicas. El hilo:

    MongoDB Atlas conserva 987 noticias
    -> Atlas clasifica y publica vistas
    -> Colab cruza las vistas con 1.000 procesos SECOP
    -> una regla transparente obtiene 77 candidatos
    -> Cassandra sirve la consulta repetitiva por corte y departamento
    -> Laura abre SECOP y realiza la revision humana

Todos los numeros que aparecen en el texto estan verificados contra los
datos versionados (ver utils/validate_atlas_laboratorio.py, que calcula los
mismos baselines de forma independiente):

    987 noticias | 189 con mas de 800 palabras | DIAN: 8 subcadena -> 1 palabra
    clasificacion de noticias: 313 / 349 / 26 / 299
    niveles de mencion: 6 altas / 25 medias / 111 bajas
    1.000 procesos SECOP | 163 coinciden por entidad | 77 candidatos finales
    primer candidato: CO1.REQ.5407319, MINISTERIO DEL DEPORTE, $168.750.000
    0 de los 77 tienen su referencia de proceso citada literalmente en prensa
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils import build_session3_notebook as _s3
from utils.make_notebook import code, md, save, validate
from utils.build_session3_notebook import hidden, question_cell as _question_cell, soporte_cells

OUTPUT = "Cuadernos/4_Atlas_Cassandra_Laura.ipynb"
COLAB = (
    "https://colab.research.google.com/github/jazaineam1/BigData2026/"
    "blob/main/Cuadernos/4_Atlas_Cassandra_Laura.ipynb"
)
WEB_CURSO = "https://jazaineam1.github.io/BigData2026/"
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
GUIA_ATLAS = f"{WEB_CURSO}assets/tutoriales/atlas-guia-conexion.html"
LAB_COMPASS = f"{WEB_CURSO}assets/tutoriales/atlas-laboratorio-consultas.html"
DATOS_NOTICIAS = f"{RAW}/Datos/noticias_contratacion_2026.json"
DATOS_ENTIDADES = f"{RAW}/Datos/entidades_en_noticias_2026.json"
DATOS_SECOP_1000 = f"{RAW}/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
TOTAL_QUESTIONS = 4

# question_cell (definida en build_session3_notebook.py) toma el numero total
# de preguntas del TOTAL_QUESTIONS de SU PROPIO modulo, no del de aqui, porque
# ahi es donde vive el closure que arma "Pregunta N de #". Se sobreescribe ese
# atributo antes de generar para que el titulo de cada celda diga "de 4".
_s3.TOTAL_QUESTIONS = TOTAL_QUESTIONS
question_cell = _question_cell


def embed(url, alto_px, titulo):
    """
    Incrusta una presentacion HTML publicada en un iframe, con enlace de
    respaldo. Va en una celda de CODIGO con display(HTML(...)) porque Colab
    sanea los atributos de las celdas de markdown; un <iframe> puesto ahi se
    pierde en silencio.
    """
    return code(
        f"""
        # {titulo} — si el iframe no carga (redes institucionales a veces
        # bloquean iframes de terceros), usa el enlace de abajo.
        from IPython.display import display, HTML

        display(HTML('''
        <iframe src="{url}?embed=1" width="100%" height="{alto_px}"
                style="border:0;display:block;border-radius:8px;" loading="lazy"></iframe>
        <p style="margin-top:8px;">
          <a href="{url}" target="_blank" rel="noopener">Abrir en pantalla completa, en una pestaña aparte ↗</a>
        </p>
        '''))
        """
    )


def build_cells():
    cells = [
        md(
            f"""
            <a href="{COLAB}" target="_parent">
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir el cuaderno en Google Colab">
            </a>

            **Acceso público:** [página del curso]({WEB_CURSO})

            > **Este cuaderno continúa exactamente donde se detuvo la sesión 3**, en *"Hasta aquí el
            > taller"*. Si `find`, `update_one`, `aggregate` o los documentos con arreglos todavía no te
            > son familiares, vuelve primero al cuaderno 3 — aquí no se vuelven a explicar.
            """
        ),
        md(
            """
            # Sesión 4 — ¿Qué contrato debe revisar Laura primero?

            ## Universidad Central
            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093)

            <img alt="MongoDB Atlas" width="170" src="https://www.mongodb.com/assets/images/global/leaf.svg">
            <img alt="Apache Cassandra" width="150" src="https://upload.wikimedia.org/wikipedia/commons/2/29/Cassandra_logo.svg">

            **Tema del PDA:** práctica de MongoDB e introducción a bases de datos columnares<br>
            **Producción evaluable de hoy:** la bandeja priorizada de Laura, construida con tu propia ejecución<br>
            **Caso conductor:** Compras Claras — el mismo de la sesión 3, ahora con el motor en la nube<br>
            **Periodo:** 2026-2S

            ## El hilo de hoy, de punta a punta

            ```text
            MongoDB Atlas conserva 987 noticias
            → Atlas clasifica y publica vistas
            → Colab cruza las vistas con 1.000 procesos SECOP
            → una regla transparente obtiene 77 candidatos
            → Cassandra sirve la consulta repetitiva por corte y departamento
            → Laura abre SECOP y realiza la revisión humana
            ```

            **Lo que esta sesión resuelve:** la priorización operativa — a qué contrato dedicarle la primera
            hora de revisión. **Lo que NO resuelve:** una revisión completa, ni una detección de
            irregularidades. Que una entidad aparezca en una noticia **no significa** que esa noticia hable
            de este contrato en particular. Vas a comprobar ese límite con un número exacto más adelante.
            """
        ),
        md(
            """
            ## Objetivos de aprendizaje

            Al terminar podrás:

            1. distinguir MongoDB Community de Atlas, y decir para qué usarías cada uno;
            2. conectar Colab a un clúster real en la nube, sin escribir tu contraseña en el cuaderno;
            3. leer una **vista** de Atlas y explicar en qué se diferencia de una consulta guardada y de un pipeline;
            4. cruzar una colección documental con una tabla de pandas aplicando una regla explícita, no un modelo;
            5. explicar qué problema resuelve Cassandra que Atlas ya resolvía, y por qué se modela distinto;
            6. identificar la clave de partición y las claves de *clustering* en una tabla Cassandra;
            7. decir, con un número, cuál es el límite de la evidencia que construiste hoy.
            """
        ),

        # ── PRIMERA MITAD ────────────────────────────────────────────────
        md(
            """
            ---
            ## Primera mitad · Reactivar, conectar, clasificar en Atlas

            **NÚCLEO** · antes de tocar nada nuevo, confirma que los controles de la sesión 3 siguen dando
            los mismos números. Si algo aquí no coincide, algo está mal *antes* de llegar a Cassandra.
            """
        ),
        code(
            """
            # Reactivar en menos de 10 minutos: los mismos controles de la sesion 3.
            import json, urllib.request

            with urllib.request.urlopen("{DATOS_NOTICIAS}") as r:
                noticias = json.loads(r.read().decode("utf-8"))

            largas = sum(1 for n in noticias if (n.get("n_palabras") or 0) > 800)

            print("Noticias                    :", len(noticias))
            print("Con mas de 800 palabras      :", largas)
            assert len(noticias) == 987 and largas == 189, "estos dos numeros deben coincidir con la sesion 3"
            print("Coincide con la sesion 3. Seguimos.")
            """.replace("{DATOS_NOTICIAS}", DATOS_NOTICIAS)
        ),
        md(
            """
            ### Dos nombres que no son lo mismo

            Ya viste esta distinción al final de la sesión 3. La regla corta que necesitas hoy:

            | | Qué es | Dónde vive el dato |
            |---|---|---|
            | **MongoDB Community** | el servidor que instalas y administras tú | tu computador |
            | **MongoDB Atlas** | MongoDB administrado en la nube | un clúster remoto, el mismo para todo tu equipo |

            **Hoy usas Atlas y Colab**, en este orden: Atlas para que los datos vivan en un solo lugar
            compartido y para *consultarlos*, y Colab para lo único que Atlas no hace por su cuenta —meter
            el primer archivo, cruzar con datos que no son de Mongo, y hablar con Cassandra—.

            > **Y esto es lo importante de todo el cuaderno, dilo en voz alta si hace falta:** las
            > **consultas de MongoDB** —el filtro de DIAN, la agregación por sección, las dos
            > clasificaciones, las dos vistas— **se escriben y se corren en la interfaz de Atlas.** No en
            > Python. Un profesional de datos que usa MongoDB todos los días casi nunca escribe `pymongo`
            > para *explorar*; explora en la interfaz, que para eso existe.
            >
            > **La única excepción de hoy es la carga inicial**, y es una excepción real, no una elección de
            > estilo: **Atlas no tiene un botón para importar un archivo JSON desde el navegador.** Esa
            > función existe en la aplicación de escritorio Compass o en la herramienta de línea de comandos
            > `mongoimport` — ninguna de las dos vas a usar hoy. La alternativa que no depende de instalar
            > nada es la que ya conoces de la sesión 3: `insert_many()`, ahora apuntando a tu clúster en la
            > nube en vez de a tu `mongod` local. Fuera de esa única celda, todo lo demás —consultar,
            > agregar, clasificar, crear vistas— ocurre en la interfaz de Atlas, tal como se explica arriba.

            > Documentación oficial: [entornos de MongoDB](https://www.mongodb.com/docs/deployment/)
            """
        ),
        code(
            """
            # Presentacion 1 de 2 — guia de conexion a Atlas.
            # Si ya la recorriste, salta directo a la diapositiva de "Connect -> Drivers -> Python"
            # abriendo esta URL con ?slide=12 al final.
            """
        ),
        embed(GUIA_ATLAS, 780, "Guía de conexión a MongoDB Atlas"),
        md(
            """
            ### ⚠️ El error que casi todo el mundo se encuentra aquí: `ServerSelectionTimeoutError`

            Antes de seguir, un problema que se ve **todos los semestres** y que no tiene nada que ver con
            tu usuario ni tu contraseña.

            Si tu clúster quedó configurado con **"Add My Current IP Address"** (la opción que Atlas ofrece
            por defecto en el paso 7 de la guía de arriba), solo tu computador puede conectarse. **Google
            Colab corre en máquinas de Google, con una IP distinta a la tuya y que además cambia cada vez
            que abres un entorno nuevo.** Por eso una cadena de conexión que funciona perfecto si la pruebas
            en tu propio computador puede fallar *exactamente igual* desde Colab, con este error:

            ```
            No se pudo conectar a Atlas: ServerSelectionTimeoutError
            ```

            **Cómo distinguirlo de un error de verdad:** si fuera tu usuario o tu contraseña, el error
            sería `OperationFailure: bad auth`, no `ServerSelectionTimeoutError`. Este error específico
            significa que **la red te está bloqueando antes de que Atlas siquiera revise quién eres**.

            **La solución, en tu navegador, no en el cuaderno:**

            1. Entra a [cloud.mongodb.com](https://cloud.mongodb.com) → tu proyecto → **Network Access**
               (en el menú de la izquierda, bajo *Security*).
            2. Pulsa **+ ADD IP ADDRESS**.
            3. Elige **ALLOW ACCESS FROM ANYWHERE**, o escribe `0.0.0.0/0` a mano.
            4. Confirma. Queda activo en menos de un minuto — no hay que reiniciar el clúster.
            5. Vuelve aquí y ejecuta de nuevo la celda de conexión, con la misma cadena.

            > **PARA LLEVAR.** No es un fallo de tu código ni de tus credenciales: es que le falta permiso
            > de red a una IP que ni siquiera es tuya. Es el mismo motivo por el que el paso 7 de la guía de
            > arriba dice explícitamente `0.0.0.0/0` y no "tu IP actual".
            """
        ),
        code(
            """
            # Presentacion 2 de 2 — de Atlas a la bandeja de Laura, con capturas reales.
            """
        ),
        embed(LAB_COMPASS, 780, "Laboratorio: Atlas y la bandeja de Laura"),
        md(
            """
            ### Crea la base en Atlas, y carga los dos archivos con Python

            **Crear la base sí es interfaz, sin Compass:** en Atlas, `Database → Browse Collections` sobre tu
            `Cluster0` → **+ Create Database** → `compras_claras`, colección `noticias`.

            **Cargar el archivo es la única excepción de código de esta mitad.** Atlas no tiene un botón
            para subir un JSON desde el navegador — eso es justo lo que hacía Compass, y hoy no lo usamos.
            La celda de abajo conecta y carga las dos colecciones con `insert_many()`, el mismo método de
            la sesión 3. Vas a necesitar tu cadena de conexión y tu contraseña —igual que en la guía de
            arriba— así que esta es también la primera vez que te conectas hoy.
            """
        ),
        code(
            """
            # Conectar a Atlas y cargar las dos colecciones. Esta es la UNICA celda de la
            # primera mitad que escribe en Mongo con Python -- todo lo demas que sigue,
            # de aqui a "Segunda mitad", ocurre en la interfaz de Atlas.
            !pip install -q pymongo dnspython mongomock

            from getpass import getpass
            from urllib.parse import quote_plus
            from pymongo import MongoClient
            import json, urllib.request

            # Pega la cadena TAL COMO Atlas te la dio en "Connect -> Drivers -> Python"
            # (trae <db_username> y <db_password> literales si aun no personalizaste el
            # usuario en esa pantalla). NO escribas el host a mano.
            uri_pegada = input("Pega tu cadena de conexion completa: ").strip()
            usuario = input("Tu usuario de base de datos (el del paso 6 de la guia): ").strip()
            contrasena = quote_plus(getpass("Tu contraseña real (no se muestra en pantalla): "))

            uri = uri_pegada
            if "<db_username>" in uri:
                uri = uri.replace("<db_username>", quote_plus(usuario))
            if "<db_password>" in uri:
                uri = uri.replace("<db_password>", contrasena)
            if "<db_username>" not in uri_pegada and "<db_password>" not in uri_pegada and usuario not in uri:
                resto = uri_pegada.split("@", 1)[-1]
                uri = f"mongodb+srv://{quote_plus(usuario)}:{contrasena}@{resto}"

            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=6000)
                client.admin.command("ping")
                db = client["compras_claras"]
                motor = "Atlas (conexión real)"
                print("Conectado a Atlas.")

                RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
                with urllib.request.urlopen(f"{RAW}/Datos/noticias_contratacion_2026.json") as r:
                    noticias_para_cargar = json.loads(r.read().decode("utf-8"))
                db["noticias"].delete_many({})   # asi puedes ejecutar esta celda mas de una vez sin duplicar
                db["noticias"].insert_many(noticias_para_cargar)
                print("noticias:", db["noticias"].count_documents({}))

                with urllib.request.urlopen(f"{RAW}/Datos/entidades_en_noticias_2026.json") as r:
                    entidades_para_cargar = json.loads(r.read().decode("utf-8"))
                db["entidades_noticias"].delete_many({})
                db["entidades_noticias"].insert_many(entidades_para_cargar)
                print("entidades_noticias:", db["entidades_noticias"].count_documents({}))
            except Exception as error:
                # Modo de respaldo: NO fingimos una conexion que no existe.
                print("No se pudo conectar a Atlas:", type(error).__name__)
                print("Modo de respaldo: trabajando con los archivos locales de la sesión 3.")
                import mongomock
                client = mongomock.MongoClient()
                db = client["compras_claras"]
                motor = "respaldo local (mongomock) — no es una conexión real a Atlas"

            print("Motor activo:", motor)
            """
        ),
        md(
            """
            ### En Atlas: consultas, agregación y dos vistas

            Ahora en el **Data Explorer de Atlas**, sobre las dos colecciones que acabas de cargar. Cada
            consulta que vas a escribir está **embebida aquí abajo, además de versionada** en el
            repositorio — no tienes que salir de Colab para comparar: si algo no compila, cópiala tal
            cual y ejecútala.

            **1. Filtro `dian-palabra-completa-v1`** sobre `noticias`. Escríbelo y **guárdalo** con ese
            nombre exacto:

            ```json
            {"titulo": {"$regex": "\\bdian\\b", "$options": "i"}}
            ```

            *(archivo completo, con la comparación 8 → 1 documentada:*
            [`dian-palabra-completa-v1.json`](https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/tutoriales/consultas/atlas/dian-palabra-completa-v1.json)*)*

            **2. Agregación `resumen-secciones-v1`** (`$match → $group → $sort → $limit`, la misma forma que
            viste en la sesión 3):

            ```json
            [
              {"$match": {"n_palabras": {"$gt": 0}}},
              {"$group": {"_id": "$seccion", "noticias": {"$sum": 1}, "promedio_palabras": {"$avg": "$n_palabras"}}},
              {"$sort": {"noticias": -1, "_id": 1}},
              {"$limit": 10}
            ]
            ```

            [`resumen-secciones-v1.json`](https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/tutoriales/consultas/atlas/resumen-secciones-v1.json)

            **3.** Con **Export Code → Python 3**, exporta esa misma agregación — es el puente hacia Colab
            que usarás en un momento.

            **4. Pipeline `clasificar-noticias-v1`** — clasifica cada noticia por su título y subtítulo en
            tres categorías, o `contexto` si no encaja en ninguna:

            ```json
            [
              {"$set": {"texto_clasificar": {"$concat": [{"$ifNull": ["$titulo", ""]}, " ", {"$ifNull": ["$subtitulo", ""]}]}}},
              {"$set": {"clasificacion": {"$switch": {"branches": [
                {"case": {"$regexMatch": {"input": "$texto_clasificar", "regex": "sobrecost|detriment|peculad|corrupci(?:o|ó)n|irregular", "options": "i"}}, "then": "terminos_control"},
                {"case": {"$regexMatch": {"input": "$texto_clasificar", "regex": "contrat|licitaci(?:o|ó)n|adjudic|secop|convenio", "options": "i"}}, "then": "proceso_contractual"},
                {"case": {"$regexMatch": {"input": "$texto_clasificar", "regex": "obra|retras|incumpl|ejecuci(?:o|ó)n", "options": "i"}}, "then": "ejecucion_obra"}
              ], "default": "contexto"}}}},
              {"$project": {"_id": 0, "titulo": 1, "seccion": 1, "publicado": 1, "url": 1, "n_palabras": 1, "clasificacion": 1}},
              {"$sort": {"publicado": -1}}
            ]
            ```

            [`clasificar-noticias-v1.json`](https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/tutoriales/consultas/atlas/clasificar-noticias-v1.json)

            **5. Pipeline `menciones-clasificadas-v1`** sobre `entidades_noticias` — nivel de mención por
            número de noticias: **alta** (≥ 20), **media** (5 a 19), **baja** (< 5):

            ```json
            [
              {"$set": {"nivel_menciones": {"$switch": {"branches": [
                {"case": {"$gte": ["$noticias", 20]}, "then": "alta"},
                {"case": {"$gte": ["$noticias", 5]}, "then": "media"}
              ], "default": "baja"}}}},
              {"$project": {"_id": 0, "entidad": 1, "departamento": 1, "procesos_en_secop": 1, "noticias": 1, "nivel_menciones": 1, "ejemplos": {"$slice": ["$ejemplos", 2]}}},
              {"$sort": {"noticias": -1, "entidad": 1}}
            ]
            ```

            [`menciones-clasificadas-v1.json`](https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/tutoriales/consultas/atlas/menciones-clasificadas-v1.json)

            **6.** Crea dos **vistas** (*Views*, no colecciones): `noticias_clasificadas` desde el pipeline
            del paso 4, y `menciones_clasificadas` desde el del paso 5.

            > **Una vista no es una copia.** Es de solo lectura y se recalcula desde su pipeline cada vez que
            > la consultas — nunca queda desactualizada, pero tampoco puedes escribir en ella directamente.
            > Documentación oficial: [vistas de Atlas](https://www.mongodb.com/docs/atlas/atlas-ui/views/).
            """
        ),
        *question_cell(
            1,
            "Consulta, pipeline y vista",
            "Guardaste una consulta simple, construiste un pipeline de agregación, y luego creaste una vista a partir de ese pipeline.",
            "¿Cuál de estas afirmaciones describe correctamente la diferencia?",
            [
                "Son tres nombres distintos para exactamente lo mismo: filtrar documentos.",
                "Una consulta guardada filtra; un pipeline transforma en varias etapas; una vista es un pipeline que se comporta como si fuera una colección de solo lectura.",
                "La vista es una copia física de los resultados, así que hay que recrearla si los datos cambian.",
                "El pipeline solo sirve para contar documentos, nunca para clasificarlos.",
            ],
            1,
            [
                "Si fueran lo mismo, no habría tres nombres ni tres pantallas distintas en Atlas. Cada una hace algo que la anterior no hace por sí sola.",
                "Correcto. Es la escalera completa: filtrar (consulta) → transformar por etapas (pipeline) → empaquetar ese pipeline para consultarlo como si fuera una colección, siempre actualizado (vista).",
                "Es justo lo contrario: la vista NO es una copia. Se recalcula en cada consulta, por eso nunca queda vieja — a cambio, no admite escrituras directas.",
                "$switch dentro de $set es exactamente clasificar: le pone una etiqueta nueva a cada documento según condiciones. Es lo que acabas de hacer con noticias y con entidades.",
            ],
        ),
        md(
            """
            ### 🔎 Lee los conteos antes de seguir

            Si tus vistas están bien construidas, deberías ver:

            | Clasificación de noticias | Conteo |
            |---|---:|
            | `terminos_control` | 313 |
            | `proceso_contractual` | 349 |
            | `ejecucion_obra` | 26 |
            | `contexto` | 299 |

            | Nivel de menciones | Entidades |
            |---|---:|
            | alta (≥ 20) | 6 |
            | media (5–19) | 25 |
            | baja (< 5) | 111 |

            **Qué nos dice.** Casi tres de cada diez noticias (299 de 987) no encajan en ninguna de las tres
            categorías de control: hablan de contratación sin lenguaje de irregularidad. **Qué no podemos
            concluir.** Que las 313 con lenguaje de "términos de control" describan corrupción real — el
            patrón busca palabras, no hechos comprobados. Es la misma advertencia de la sesión 3, aplicada a
            una clasificación nueva.
            """
        ),
        # ── SEGUNDA MITAD ────────────────────────────────────────────────
        md(
            """
            ---
            ## Segunda mitad · De la vista de Atlas a la bandeja de Laura

            **NÚCLEO** · aquí sí escribes Python. Y aquí está la respuesta completa a la pregunta que te
            quedó dando vueltas en la primera mitad: **¿por qué toda esa parte fue en Atlas y esta es en
            Colab?**

            ### La regla, sin excepciones, y por qué existe

            | Si la tarea es... | La haces en... | Porque... |
            |---|---|---|
            | filtrar, agrupar, clasificar, crear una vista | **Atlas** (Data Explorer) o **Community** (`mongosh`) | es exactamente para eso que existe esa interfaz — y la ves ejecutarse y corregirse al instante, sin reiniciar nada |
            | cargar el archivo inicial, o cruzar lo que hay en Mongo con algo que **no vive en Mongo** | **Python**, aquí en Colab | ni Atlas ni su interfaz saben leer un archivo local o un CSV de SECOP. Eso solo existe fuera de Mongo |
            | hablar con **otro motor** (Cassandra, más adelante) | **Python** | son sistemas distintos; algo tiene que estar de puente entre los dos |

            **Ya estás conectado** — usaste esa misma conexión para cargar `noticias` y `entidades_noticias`
            al principio de la sesión. No hace falta pegar la cadena otra vez: `client` y `db` siguen vivos
            en este cuaderno. **La `menciones_clasificadas` que vas a leer en la próxima celda ya la
            construiste tú, en Atlas, en la primera mitad.** Python no la va a volver a calcular ni a
            mejorar: solo la va a **sacar** de Mongo para poder juntarla con los 1.000 procesos de SECOP,
            que están en un CSV y nunca estuvieron en tu base. Ese cruce —y la carga inicial que ya
            hiciste— son los dos únicos motivos por los que aparece código en toda la sesión: no porque
            Python sea "mejor" para consultar que la interfaz de Mongo, sino porque hay dos tareas
            puntuales que la interfaz no puede hacer sola.
            """
        ),
        code(
            """
            # Sacar de Atlas la vista que YA construiste en la interfaz -- no se vuelve a
            # calcular aqui, solo se trae para poder cruzarla con SECOP. Si estas en modo
            # de respaldo, la reconstruimos localmente con la MISMA regla que usaste en Atlas.
            import json, urllib.request

            if "menciones_clasificadas" in db.list_collection_names():
                menciones = list(db["menciones_clasificadas"].find({}, {"_id": 0}))
            else:
                with urllib.request.urlopen("{DATOS_ENTIDADES}") as r:
                    entidades = json.loads(r.read().decode("utf-8"))
                for e in entidades:
                    n = e.get("noticias", 0)
                    e["nivel_menciones"] = "alta" if n >= 20 else "media" if n >= 5 else "baja"
                menciones = entidades

            from collections import Counter
            niveles = Counter(m["nivel_menciones"] for m in menciones)
            print("Entidades por nivel de mencion:", dict(niveles))
            assert dict(niveles) == {"baja": 111, "media": 25, "alta": 6}, "deberia coincidir con Atlas"
            """.replace("{DATOS_ENTIDADES}", DATOS_ENTIDADES)
        ),
        code(
            """
            # Cargar la muestra de 1.000 procesos SECOP en pandas.
            import pandas as pd

            secop = pd.read_csv("{DATOS_SECOP_1000}", low_memory=False)
            print("Procesos SECOP en la muestra:", len(secop))
            assert len(secop) == 1000
            """.replace("{DATOS_SECOP_1000}", DATOS_SECOP_1000)
        ),
        code(
            """
            # La regla de priorizacion, en cuatro pasos explicitos. Nada de esto es un
            # modelo: es una regla que cualquiera puede leer y discutir.
            entidades_en_prensa = {m["entidad"] for m in menciones}

            # 1) coincidencia EXACTA de entidad con la vista de noticias
            paso1 = secop[secop["entidad"].isin(entidades_en_prensa)]
            print("1) entidad coincide con prensa :", len(paso1))

            # 2) modalidad que contiene 'directa'
            paso2 = paso1[paso1["modalidad_de_contratacion"].str.contains("directa", case=False, na=False)]

            # 3) respuestas NUMERICAS iguales a cero; los faltantes quedan EXCLUIDOS
            #    (fillna(0) los convertiria en "cero", que no es lo mismo que "no se sabe")
            respuestas = pd.to_numeric(paso2["respuestas_al_procedimiento"], errors="coerce")
            paso3 = paso2[respuestas.eq(0)]

            # 4) orden: precio_base descendente, id_del_proceso ascendente como desempate
            candidatos = paso3.sort_values(
                ["precio_base", "id_del_proceso"], ascending=[False, True]
            ).reset_index(drop=True)

            print("2) + modalidad directa          :", len(paso2))
            print("3) + cero respuestas (sin NaN)  :", len(paso3))
            print()
            print("Candidatos finales               :", len(candidatos))
            assert len(paso1) == 163 and len(candidatos) == 77, "la regla deberia dar 163 -> 77"
            """
        ),
        md(
            """
            ### 🔎 Por qué el paso 3 no usa `fillna(0)`

            Si conviertes los valores faltantes en cero con `fillna(0).eq(0)`, un proceso **sin dato de
            respuestas** entraría a la bandeja igual que uno que de verdad tuvo cero. Son cosas distintas:
            uno no tiene evidencia de competencia, el otro no tiene *dato*. `pd.to_numeric(..., errors="coerce")`
            convierte lo no numérico en `NaN`, y `NaN == 0` es `False` — así que los faltantes quedan
            **fuera**, que es lo correcto cuando no sabes.
            """
        ),
        code(
            """
            # Verificar el primer candidato: es el número que vas a defender si alguien pregunta.
            primero = candidatos.iloc[0]
            print("Primer candidato:")
            print("  id_del_proceso:", primero["id_del_proceso"])
            print("  entidad       :", primero["entidad"])
            print("  precio_base   : $", f"{primero['precio_base']:,.0f}")

            assert primero["id_del_proceso"] == "CO1.REQ.5407319"
            assert primero["entidad"] == "MINISTERIO DEL DEPORTE"
            assert int(primero["precio_base"]) == 168750000
            print()
            print("Coincide con el resultado esperado.")
            """
        ),
        code(
            """
            # Enriquecer cada fila: rango, razones, menciones, enlace a SECOP,
            # indicador de referencia explicita, y el limite de la evidencia.
            menciones_por_entidad = {m["entidad"]: m for m in menciones}

            titulos_y_subtitulos = " ".join(
                f'{n.get("titulo") or ""} {n.get("subtitulo") or ""}' for n in noticias
            )

            filas = []
            for i, fila in candidatos.iterrows():
                m = menciones_por_entidad.get(fila["entidad"], {})
                referencia = str(fila.get("referencia_del_proceso") or "").strip()
                tiene_referencia = bool(referencia) and len(referencia) >= 6 and referencia in titulos_y_subtitulos

                filas.append({
                    "rango": i + 1,
                    "id_del_proceso": fila["id_del_proceso"],
                    "entidad": fila["entidad"],
                    "departamento": fila.get("departamento_entidad") or "No definido",
                    "objeto": str(fila.get("nombre_del_procedimiento") or "")[:120],
                    "modalidad": str(fila.get("modalidad_de_contratacion") or ""),
                    "precio_base": int(fila["precio_base"]),
                    "razones": "entidad en prensa; contratación directa; 0 respuestas de proveedores",
                    "menciones_entidad": m.get("noticias", 0),
                    "nivel_menciones": m.get("nivel_menciones", "sin dato"),
                    "referencia_citada_en_prensa": tiene_referencia,
                    "url_secop": fila.get("urlproceso", ""),
                    "limite": (
                        "la referencia de este proceso SÍ aparece citada en una noticia"
                        if tiene_referencia else
                        "la entidad aparece en prensa; este contrato específico NO está citado por su referencia"
                    ),
                })

            bandeja = pd.DataFrame(filas)
            con_referencia = int(bandeja["referencia_citada_en_prensa"].sum())
            print(f"Candidatos con su referencia de proceso citada literalmente en prensa: {con_referencia} de {len(bandeja)}")
            bandeja.head(5)
            """
        ),
        md(
            """
            ### 🔎 El número que sostiene el límite de hoy

            Cero. **Ninguno de los 77 candidatos tiene su número de proceso citado literalmente en una
            noticia.** La evidencia que usaste hoy es por **entidad**, no por **contrato**: la prensa dice
            que el Ministerio del Deporte aparece en tantas noticias, no que esta compra específica de
            $168.750.000 sea la que motivó alguna de ellas.

            Esa es la frase que Laura tiene que decirle a su jefe si le preguntan por qué revisa este
            contrato primero: *"la entidad tiene cobertura de prensa y esta compra cumple tres señales
            objetivas de riesgo — no que la prensa haya señalado este contrato."*
            """
        ),
        code(
            """
            # Vista navegable para Laura: una tabla HTML, con enlace directo a cada proceso.
            from IPython.display import display, HTML

            def fila_html(f):
                bandera = "🔴" if not f["referencia_citada_en_prensa"] else "🟢"
                return f'''
                <tr>
                  <td>{f["rango"]}</td>
                  <td>{f["entidad"][:40]}</td>
                  <td style="text-align:right;">$ {f["precio_base"]:,.0f}</td>
                  <td>{f["nivel_menciones"]} ({f["menciones_entidad"]})</td>
                  <td>{bandera}</td>
                  <td><a href="{f["url_secop"]}" target="_blank">Ver en SECOP</a></td>
                </tr>'''

            filas_html = "".join(fila_html(f) for f in filas[:15])
            display(HTML(f'''
            <table style="border-collapse:collapse;width:100%;font-size:13px;">
              <tr style="background:#123f2b;color:#fff;">
                <th style="padding:8px;">#</th><th style="padding:8px;">Entidad</th>
                <th style="padding:8px;">Valor base</th><th style="padding:8px;">Menciones</th>
                <th style="padding:8px;">Ref. citada</th><th style="padding:8px;">SECOP</th>
              </tr>
              {filas_html}
            </table>
            <p style="font-size:12px;color:#666;">🔴 = la entidad aparece en prensa, pero este contrato no está citado por su referencia. Primeros 15 de {len(bandeja)}.</p>
            '''))
            """
        ),
        code(
            """
            # Exportar: un CSV para seguir trabajando, un Markdown para el hito.
            import os

            os.makedirs("resultados", exist_ok=True)
            os.makedirs("hitos/s04", exist_ok=True)

            bandeja.to_csv("resultados/s04_priorizacion_laura.csv", index=False, encoding="utf-8")

            with open("hitos/s04/priorizacion_laura.md", "w", encoding="utf-8") as f:
                f.write("# Bandeja de priorización — sesión 4\\n\\n")
                f.write(f"Candidatos: {len(bandeja)} de 1.000 procesos evaluados.\\n\\n")
                f.write("| # | Entidad | Valor base | Menciones | Ref. citada |\\n|---|---|---:|---|---|\\n")
                for fl in filas[:20]:
                    f.write(f"| {fl['rango']} | {fl['entidad'][:35]} | $ {fl['precio_base']:,.0f} | "
                            f"{fl['nivel_menciones']} ({fl['menciones_entidad']}) | "
                            f"{'sí' if fl['referencia_citada_en_prensa'] else 'no'} |\\n")
                f.write("\\n**Límite.** Ningún candidato tiene su referencia de proceso citada literalmente "
                        "en prensa: la evidencia es por entidad, no por contrato.\\n")

            print("Guardado: resultados/s04_priorizacion_laura.csv")
            print("Guardado: hitos/s04/priorizacion_laura.md")
            """
        ),
        *question_cell(
            2,
            "MongoDB frente a Cassandra",
            "MongoDB Atlas ya guarda las noticias, las vistas y hasta podría guardar la bandeja de 77 candidatos.",
            "Si Atlas ya lo tiene todo, ¿para qué añadir Cassandra en el mismo flujo?",
            [
                "Porque MongoDB no puede filtrar por dos campos a la vez.",
                "Porque Laura va a repetir muchas veces la misma consulta —corte y departamento—, y Cassandra está optimizada para servir exactamente ese patrón de acceso repetitivo a gran velocidad y escala.",
                "Porque Cassandra reemplaza a MongoDB: de ahora en adelante todo se guarda ahí.",
                "Porque Cassandra es la única que permite ordenar resultados.",
            ],
            1,
            [
                "MongoDB filtra por cuantos campos hagan falta — la sesión 3 entera fue sobre eso. No es una limitación técnica.",
                "Correcto. No es que Atlas 'no pueda': es que Cassandra se diseña para una consulta específica, repetida miles de veces, con latencia mínima y escritura distribuida — un patrón distinto al de Atlas, que sigue siendo el lugar donde viven los documentos flexibles.",
                "Nada se reemplaza: MongoDB sigue alojando noticias y vistas. Cassandra guarda solo una proyección desnormalizada para esta consulta puntual.",
                "MongoDB ordena resultados sin problema, con $sort. No es una capacidad exclusiva de Cassandra.",
            ],
        ),

        # ── CASSANDRA ─────────────────────────────────────────────────────
        md(
            """
            ---
            ## Cassandra: qué es, y por qué aparece aquí

            **MAPA** · esto lo recorremos hablando y viendo una demostración en vivo. No necesitas una
            cuenta de Astra propia.

            ### Qué es, en una frase que puedas repetir

            **Apache Cassandra es un motor de base de datos hecho para escribir muchísimo, muy rápido, sin
            que nada se caiga — a cambio de que solo respondas las preguntas que decidiste de antemano.**
            Nació en Facebook en 2008 para una necesidad muy concreta: la bandeja de mensajes de todos sus
            usuarios, que crecía sin parar y no podía depender de un solo servidor. Hoy la usan, para
            problemas del mismo tipo, Netflix (qué viste y hasta dónde), Uber (dónde está cada carro ahora
            mismo) y Apple (el historial de iMessage). Ninguno de esos tres casos es "consultar de mil
            formas distintas": es **una pregunta fija, repetida sin parar, con una respuesta que tiene que
            llegar en milisegundos.**

            ### Cómo lo logra

            Reparte los datos entre varias máquinas usando la clave de partición —lo que ya viste con
            `(corte, departamento)`— y **cada máquina responde solo por su porción**. Ninguna consulta
            típica necesita hablar con todas las máquinas a la vez, y ninguna máquina sola es
            indispensable: si una se apaga, las demás siguen respondiendo. Ese reparto es lo que le permite
            escalar horizontalmente —agregar más máquinas en vez de comprar una más grande— sin que las
            escrituras se vuelvan más lentas a medida que crecen los datos.

            ### Para qué datos sirve, y para cuáles no

            | Sirve muy bien para... | No es la herramienta para... |
            |---|---|
            | pocas preguntas **conocidas de antemano**, repetidas millones de veces | preguntas **exploratorias**, que cambian según lo que vayas descubriendo — eso es MongoDB, que usaste toda la noche |
            | datos que se **escriben una vez y casi nunca se modifican** (mensajes, eventos, lecturas de sensores, el corte de hoy) | datos que se **actualizan y relacionan** todo el tiempo entre sí — eso pide transacciones, más cercano a lo relacional |
            | volúmenes que **no caben** en una sola máquina | volúmenes pequeños que caben de sobra en una — como los 77 de hoy |

            ### Por qué aparece en el contexto de Laura, siendo honestos con la escala de esta noche

            Con 77 filas, Cassandra es **una herramienta de más**: esa consulta la responde una lista de
            Python en microsegundos, y nadie necesita repartir 77 filas entre varias máquinas. Si la sesión
            terminara aquí, la respuesta honesta sería "no lo necesitas todavía".

            **Pero Compras Claras es un piloto, y esta sesión practica para cuando deje de serlo.** Si el
            programa escala a nivel nacional —miles de entidades, cientos de miles de procesos, un tablero
            que decenas de analistas de la Contraloría consultan **al mismo tiempo**, cada minuto, siempre
            con la misma pregunta: *"para este corte y este departamento, ¿qué reviso primero?"*— eso deja
            de ser un ejercicio de pandas. Se vuelve exactamente el patrón que Cassandra resuelve mejor que
            cualquier otro motor: escritura constante (cada corte nuevo se agrega sin tocar los anteriores)
            y lectura ultrarrápida de una pregunta fija, sin que un solo servidor se convierta en cuello de
            botella cuando todos consultan a la vez.

            > **PARA LLEVAR.** Hoy diseñas la tabla con 77 filas de juguete para que, el día que sean 77
            > millones y la estén consultando cien personas a la vez, ya sepas cuál es la pregunta que hay
            > que fijar de antemano y cómo construir la tabla alrededor de ella. Eso es exactamente lo que
            > sigue: cómo se diseña *para* una pregunta, en vez de diseñar para los datos en general.

            > Documentación oficial: [modelado de datos en Apache Cassandra](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/intro.html)
            """
        ),
        md(
            """
            ### *Query First Design*: se diseña desde la pregunta, no desde la entidad

            En MongoDB —y en SQL— modelas primero las cosas que existen (noticias, procesos, entidades) y
            preguntas después: si necesitas cruzar dos, usas `$lookup` o un `JOIN`. Cassandra invierte el
            orden: **primero decides qué vas a preguntar, y la tabla se construye para que esa pregunta sea
            barata.** No existe `JOIN` en Cassandra — ni falta: si necesitaras cruzar `noticias` con
            `procesos` en cada consulta, la respuesta de Cassandra no es "cruza más rápido", es "no cruces
            nunca en el momento de leer: cruza una vez, al escribir, y guarda el resultado ya armado". Eso
            es exactamente lo que hiciste hoy en pandas —cruzar una vez y guardar la bandeja— y es lo mismo
            que la tabla `prioridades_por_corte_departamento` hace de forma permanente.

            **Y hay una regla dura que viene con ese diseño:** en un `WHERE`, las claves de partición son
            **obligatorias y van todas juntas** —no puedes preguntar solo por `corte` y dejar
            `departamento` suelto—, mientras que las claves de *clustering* (`valor_base`, `id_proceso`)
            son **opcionales**. Y sobre cualquier otro campo —`entidad`, `nivel_menciones`— Cassandra
            **se niega a filtrar** a menos que agregues explícitamente `ALLOW FILTERING`, que es la forma en
            que el motor te avisa: *"esto va a recorrer toda la tabla, y te lo voy a dejar hacer, pero
            sabiendo que es lento"*. No es una limitación torpe: es el motor obligándote a diseñar para tu
            consulta en vez de confiar en que ya lo hiciste bien.
            """
        ),
        code(
            """
            # CQL — la tabla se modela por como se va a preguntar, no por como se guarda la entidad.
            cql_crear_tabla = '''
            CREATE TABLE compras_claras.prioridades_por_corte_departamento (
                corte date,
                departamento text,
                valor_base bigint,
                id_proceso text,
                entidad text,
                objeto text,
                modalidad text,
                respuestas int,
                noticias_entidad int,
                nivel_menciones text,
                estado_revision text,
                url_secop text,
                criterio text,
                PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
            ) WITH CLUSTERING ORDER BY (
                valor_base DESC,
                id_proceso ASC
            );
            '''
            print(cql_crear_tabla)
            """
        ),
        md(
            """
            ### Cómo leer esa llave primaria

            | Parte | Nombre | Qué hace |
            |---|---|---|
            | `(corte, departamento)` | **clave de partición** | decide **en qué máquina** vive la fila. Todas las filas con el mismo corte y departamento quedan juntas |
            | `valor_base, id_proceso` | **claves de *clustering*** | deciden el **orden dentro de** esa partición — por eso `CLUSTERING ORDER BY valor_base DESC` ya te entrega la fila más cara primero, sin ordenar nada después |

            **La consecuencia práctica:** `SELECT ... WHERE corte = ? AND departamento = ? LIMIT 5` no
            recorre toda la tabla — va directo a la partición correcta y lee las primeras 5 filas, ya
            ordenadas. Es la razón de ser de este modelo: está construido *para esa consulta exacta*, no
            para cualquier consulta.
            """
        ),
        *question_cell(
            3,
            "Clave de partición y claves de clustering",
            "La tabla tiene PRIMARY KEY ((corte, departamento), valor_base, id_proceso) "
            "y CLUSTERING ORDER BY (valor_base DESC, id_proceso ASC).",
            "Si quieres los 5 procesos de mayor valor de Bogotá para un corte específico, ¿por qué esta tabla responde rápido sin ALLOW FILTERING?",
            [
                "Porque Cassandra revisa toda la tabla en memoria, así que siempre es rápida.",
                "Porque (corte, departamento) es la clave de partición: localiza la partición exacta de un salto, y dentro de ella las filas ya están ordenadas por valor_base gracias al clustering order — LIMIT 5 solo lee las primeras.",
                "Porque la tabla no tiene más de 77 filas y cualquier consulta sobre ella es instantánea.",
                "Porque departamento aparece primero en la cláusula WHERE.",
            ],
            1,
            [
                "Es justo lo que Cassandra evita: recorrer todo. Por diseño, la clave de partición existe para no tener que hacerlo.",
                "Correcto. Partición = ubicación física de un salto. Clustering = orden ya resuelto dentro de esa partición. Las dos cosas juntas son lo que hace que 'los 5 más caros de este corte y departamento' sea una lectura casi directa.",
                "El razonamiento no depende del tamaño de hoy: el mismo diseño sigue siendo rápido con millones de filas, porque la partición sigue acotando la búsqueda igual.",
                "El orden en el WHERE no importa para Cassandra: lo que importa es que corte y departamento sean exactamente los dos campos declarados como clave de partición, juntos.",
            ],
        ),
        md(
            """
            ### La demostración en vivo

            Esta parte la ejecuta el docente con una cuenta de Astra DB (el servicio administrado de
            Cassandra). **No necesitas tu propio token ni bundle.** Observa e interpreta la ejecución real:
            77 inserciones y una consulta que responde en milisegundos.

            > El *keyspace* `compras_claras` ya existe, creado desde el portal de Astra —a diferencia de
            > MongoDB, Astra **no admite** `CREATE KEYSPACE` por CQL. Documentación oficial:
            > [gestión de keyspaces en Astra](https://docs.datastax.com/en/astra-db-serverless/databases/manage-keyspaces.html) ·
            > [conexión con Python, token y Secure Connect Bundle](https://docs.datastax.com/en/astra-db-serverless/drivers/python-driver.html)

            **Docente: dónde están tus dos datos, antes de ejecutar la celda.** Colab corre en un
            servidor de Google, no en tu computador: el bundle tiene que **subirse**, no solo indicar
            una ruta local.

            | Lo que pide la celda | Dónde lo consigues |
            |---|---|
            | El Secure Connect Bundle | El archivo `Cassandra/bundle.zip` de tu repositorio local. La celda abre un botón **Choose Files** — selecciónalo ahí, no escribas una ruta |
            | El token | Ábrelo con un editor de texto: `Cassandra/token.json`, campo `"token"`. Empieza por `AstraCS:` |
            """
        ),
        hidden(
            code(
                """
                # DEMOSTRACION DOCENTE — no ejecutes esta celda con tus propias credenciales.
                # Necesita el Secure Connect Bundle y el token de Astra (ver la tabla de arriba
                # para saber donde estan), y el keyspace compras_claras ya creado (Astra no
                # admite CREATE KEYSPACE por CQL). cassandra-driver no viene instalado en Colab
                # por defecto: se instala aqui (3.29.3 es la ultima version publicada en PyPI;
                # la 3.30 mencionada en borradores previos de este libreto no existe).
                !pip install -q "cassandra-driver>=3.29,<4"

                from getpass import getpass
                from datetime import date
                from cassandra.cluster import Cluster
                from cassandra.auth import PlainTextAuthProvider

                # En Colab real aparece un boton "Choose Files": ahi seleccionas
                # Cassandra/bundle.zip desde tu computador. Fuera de Colab (por ejemplo
                # probando esta celda en un Jupyter local), se pide la ruta en el disco.
                try:
                    from google.colab import files
                    print("Sube tu Secure Connect Bundle (Cassandra/bundle.zip):")
                    subido = files.upload()
                    bundle = list(subido.keys())[0]
                except ImportError:
                    bundle = input("Ruta al Secure Connect Bundle (.zip): ").strip()

                token = getpass("Token de Astra (empieza por AstraCS:...): ")

                cluster = Cluster(
                    cloud={"secure_connect_bundle": bundle},
                    auth_provider=PlainTextAuthProvider("token", token),
                )
                session = cluster.connect()
                session.execute(cql_crear_tabla)

                insertar = session.prepare('''
                    INSERT INTO compras_claras.prioridades_por_corte_departamento
                    (corte, departamento, valor_base, id_proceso, entidad, objeto, modalidad,
                     respuestas, noticias_entidad, nivel_menciones, estado_revision, url_secop, criterio)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''')

                corte_hoy = date.today()

                # 77 inserciones con sentencia preparada. Sin BATCH: cada fila puede caer en
                # una particion distinta (corte, departamento), y agrupar particiones distintas
                # en un mismo BATCH es justamente el antipatron que Cassandra penaliza.
                for f in filas:
                    session.execute(insertar, (
                        corte_hoy,
                        f["departamento"],
                        f["precio_base"],
                        f["id_del_proceso"],
                        f["entidad"],
                        f["objeto"],
                        f["modalidad"],
                        0,                        # respuestas: la regla ya exige que sea 0
                        f["menciones_entidad"],
                        f["nivel_menciones"],
                        "pendiente",              # estado_revision: nadie la ha abierto todavia
                        f["url_secop"],
                        f["razones"],
                    ))

                print(f"Insertadas {len(filas)} filas en prioridades_por_corte_departamento.")

                # La consulta que justifica el modelo: un salto a la particion, sin ALLOW FILTERING.
                resultado = session.execute('''
                    SELECT id_proceso, entidad, valor_base FROM compras_claras.prioridades_por_corte_departamento
                    WHERE corte = %s AND departamento = %s LIMIT 5
                ''', (corte_hoy, "Distrito Capital de Bogotá"))

                print()
                print("Los 5 de mayor valor en Bogotá, para el corte de hoy:")
                for fila_cass in resultado:
                    print(f"  {fila_cass.id_proceso}  {fila_cass.entidad[:40]:40s}  $ {fila_cass.valor_base:,}")

                cluster.shutdown()
                """
            ),
            "Demostración docente — conexión real a Astra (no ejecutar sin credenciales propias)",
            "hide-input",
            "demo-astra",
        ),
        md(
            """
            **Lo que vas a ver en Bogotá — ya verificado, no es una promesa:** en primer lugar
            `CO1.REQ.5407319`, Ministerio del Deporte, $168.750.000. **Es el mismo número que ya viste en
            pandas.** Cassandra no cambia la respuesta: solo la sirve distinto — mucho más rápido, y de una
            tabla hecha exactamente para esta pregunta.
            """
        ),
        *question_cell(
            4,
            "El límite analítico de hoy",
            "77 candidatos, priorizados por tres señales objetivas: entidad en prensa, contratación directa, cero respuestas de proveedores.",
            "¿Cuál es la afirmación que un analista responsable puede sostener frente a su jefe hoy?",
            [
                "Detectamos 77 contratos con irregularidades confirmadas en la contratación pública.",
                "Priorizamos 77 procesos para revisión humana con tres señales objetivas y explicables; ninguno tiene su referencia citada literalmente en prensa, así que la evidencia es sobre la entidad, no sobre el contrato específico.",
                "Como ningún candidato tiene su referencia citada en prensa, la bandeja completa no sirve y hay que descartarla.",
                "Cassandra confirma que estos 77 son los más urgentes, porque los guarda ordenados por valor.",
            ],
            1,
            [
                "Es el salto de siempre: una regla de priorización no es una detección de irregularidad. Nada en esta sesión demuestra que haya un solo contrato mal ejecutado.",
                "Correcto. Nombra exactamente lo que la regla puede sostener —tres señales objetivas, explicables, reproducibles— y declara el límite con el número que lo prueba: 0 de 77 referencias citadas. Es un punto de partida para revisión humana, no un veredicto.",
                "El 0 de 77 no invalida la bandeja: dice qué tipo de evidencia es (por entidad) y cuál no es (por contrato). Sigue siendo un punto de partida razonable para decidir qué mirar primero.",
                "Cassandra solo sirve rápido lo que ya se decidió en pandas. Ordenar por valor_base no es evidencia de urgencia: es el criterio que tú elegiste, y hay que poder defenderlo, no atribuírselo a la base de datos.",
            ],
        ),
        md(
            """
            ---
            ## Cómo se evalúa esta sesión

            Igual que en la sesión 3: **no hay cuestionario de opción múltiple como instrumento**. Lo que se
            evalúa es tu ejecución —la bandeja que exportaste, con el número correcto de candidatos y el
            primer caso verificado— y tu interpretación del límite. Las cuatro preguntas son formativas: te
            avisan si un concepto quedó suelto, no son la nota.

            ## Qué sigue

            En la sesión 5 vuelves a Cassandra, esta vez a fondo: por qué escribir es barato y leer por un
            campo que no es la clave es caro, consistencia ajustable, y cuándo esta arquitectura deja de
            tener sentido. Hoy solo viste el resultado funcionando.
            """
        ),
    ]
    return cells


def main():
    cells = soporte_cells() + build_cells()
    validate(cells)
    save(cells, OUTPUT)


if __name__ == "__main__":
    main()
