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
TOTAL_QUESTIONS = 8

# question_cell en build_session3_notebook.py usa el TOTAL_QUESTIONS de ESE
# modulo para el titulo de la celda ("Pregunta N de 8"). Aqui tambien son 8,
# asi que basta con reutilizar la funcion tal cual.
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
        <div style="border:1px solid #d8dee3;border-radius:12px;overflow:hidden;">
          <iframe src="{url}?embed=1" width="100%" height="{alto_px}"
                  style="border:0;display:block;" loading="lazy"></iframe>
        </div>
        <p style="margin-top:8px;">
          <a href="{url}" target="_blank" rel="noopener">Abrir en una pestaña aparte ↗</a>
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

            1. distinguir MongoDB Community, Compass y Atlas, y decir para qué usarías cada uno;
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
            ### Tres nombres que no son lo mismo

            Ya viste esta distinción al final de la sesión 3. La regla corta que necesitas hoy:

            | | Qué es | Dónde vive el dato |
            |---|---|---|
            | **MongoDB Community** | el servidor que instalas y administras tú | tu computador |
            | **MongoDB Compass** | una aplicación visual que se conecta a un servidor | no guarda nada propio |
            | **MongoDB Atlas** | MongoDB administrado en la nube | un clúster remoto, el mismo para todo tu equipo |

            **Hoy usas los tres**, en este orden: Compass para *ver e importar* de forma visual, Atlas para
            que los datos vivan en un solo lugar compartido, y Colab para lo que Compass no hace —cruzar con
            pandas y automatizar—.

            > Documentación oficial: [entornos de MongoDB](https://www.mongodb.com/docs/deployment/) ·
            > [MongoDB Compass](https://www.mongodb.com/docs/compass/)
            """
        ),
        *question_cell(
            1,
            "Los tres roles",
            "Vas a usar MongoDB Community, Compass y Atlas en la misma sesión, cada uno para algo distinto.",
            "¿Cuál de estas tres tareas le corresponde específicamente a Compass, y no a Atlas ni a Community?",
            [
                "Guardar los 987 documentos de forma permanente para que el equipo los consulte después.",
                "Importar visualmente un archivo JSON a una colección, sin escribir código.",
                "Ejecutar el servidor mongod en tu propio computador.",
                "Coordinar tres nodos que se reparten el trabajo y se vigilan entre sí.",
            ],
            1,
            [
                "Eso lo hace Atlas: es el clúster remoto donde persisten los datos. Compass solo se conecta a él, no guarda nada por su cuenta.",
                "Correcto. Compass es la aplicación visual: conectas, arrastras un archivo y lo importa. Ni Community ni Atlas hacen eso por sí solos — son servidores, no interfaces.",
                "Eso es Community: el servidor autoadministrado que corre en tu máquina. Compass se conecta a un servidor, no lo reemplaza.",
                "Eso describe un clúster de Atlas con réplicas, que viste en la sesión 3. Compass no coordina nodos: solo habla con uno.",
            ],
        ),
        code(
            """
            # Presentacion 1 de 2 — guia de conexion a Atlas.
            # Si ya la recorriste, salta directo a la diapositiva de "Connect -> Drivers -> Python"
            # abriendo esta URL con ?slide=12 al final.
            """
        ),
        embed(GUIA_ATLAS, 560, "Guía de conexión a MongoDB Atlas"),
        md(
            """
            ### Compass, en tu escritorio: crea la base e importa los dos archivos

            Sigue la diapositiva **"Compass → crear base"** de la segunda presentación (más abajo tienes el
            enlace directo). Resumen de lo que vas a hacer, sin repetirlo aquí paso a paso:

            1. **Add New Connection** en Compass, con la misma cadena `mongodb+srv://` de tu clúster.
            2. **Create Database**: `compras_claras`, colección `noticias`.
            3. **Add Data → Import JSON or CSV file** con `noticias_contratacion_2026.json` — marca
               **Stop on errors** para notar de inmediato si algo no cargó, y revisa **View Log** al final.
            4. Repite para una segunda colección, `entidades_noticias`, con `entidades_en_noticias_2026.json`.

            > **OJO — por qué no hay `delete_many({{}})` antes de importar.** En la sesión 3 borrabas y
            > recargabas porque ejecutabas la misma celda muchas veces. Hoy importas **una sola vez**, desde
            > la interfaz. Si una importación se interrumpe a la mitad, borrar antes de reintentar te
            > dejaría sin nada mientras investigas qué pasó — mejor revisar **View Log**, corregir y volver
            > a intentar sobre lo que ya entró.

            **Deberías terminar con:** `noticias` → 987 documentos. `entidades_noticias` → 142 documentos.
            """
        ),
        *question_cell(
            2,
            "$regex: subcadena o palabra completa",
            "Buscas noticias que mencionen la DIAN. `{\"titulo\": {\"$regex\": \"dian\", \"$options\": \"i\"}}` "
            "encuentra 8 noticias. Cambiar el patrón a `\"\\\\bdian\\\\b\"` lo baja a 1.",
            "¿Qué explica la diferencia entre 8 y 1?",
            [
                "El segundo patrón tiene un error de sintaxis y por eso encuentra menos.",
                "El primero busca 'dian' como subcadena dentro de cualquier palabra; el segundo exige que sea una palabra completa, delimitada por \\b.",
                "$options: \"i\" solo funciona en el primer patrón.",
                "La colección cambió entre una consulta y otra.",
            ],
            1,
            [
                "\\b es sintaxis válida de expresiones regulares: son los límites de palabra. No es un error, es una restricción deliberada.",
                "Correcto. Sin \\b, 'dian' aparece dentro de palabras como 'guardian' o 'mediante'. Con \\b, solo cuenta cuando 'dian' es la palabra completa — por eso 8 baja a 1.",
                "$options se aplica igual en los dos: ambos ignoran mayúsculas y minúsculas. La diferencia está en el patrón, no en las opciones.",
                "Es la misma colección, las mismas 987 noticias, en el mismo momento. El cambio está solo en el patrón.",
            ],
        ),
        md(
            """
            ### En Atlas: consultas, agregación y dos vistas

            Ahora en el **Data Explorer de Atlas** (no en Compass), sobre las colecciones que acabas de
            importar. Cada consulta que vas a escribir está también versionada en el repositorio, así que
            si algo no compila puedes compararla:
            [`assets/tutoriales/consultas/atlas/`](https://github.com/jazaineam1/BigData2026/tree/main/assets/tutoriales/consultas/atlas).

            1. Escribe el filtro `{"titulo": {"$regex": "\\\\bdian\\\\b", "$options": "i"}}` sobre `noticias` y
               **guárdalo** como consulta con el nombre `dian-palabra-completa-v1`.
            2. Construye la agregación de resumen por sección (`$match → $group → $sort → $limit`, la misma
               forma que viste en la sesión 3) y guárdala como `resumen-secciones-v1`.
            3. Con **Export Code → Python 3**, exporta esa agregación — es el puente hacia Colab que usarás
               en un momento.
            4. Con `$set` + `$switch`, clasifica cada noticia según su título y subtítulo en tres categorías
               —`terminos_control`, `proceso_contractual`, `ejecucion_obra`— o `contexto` si no encaja en
               ninguna. Guárdalo como `clasificar-noticias-v1`.
            5. Sobre `entidades_noticias`, clasifica cada entidad por su número de menciones: **alta** (20 o
               más), **media** (5 a 19), **baja** (menos de 5). Guárdalo como `menciones-clasificadas-v1`.
            6. Crea dos **vistas** (*Views*, no colecciones): `noticias_clasificadas` desde el pipeline del
               paso 4, y `menciones_clasificadas` desde el del paso 5.

            > **Una vista no es una copia.** Es de solo lectura y se recalcula desde su pipeline cada vez que
            > la consultas — nunca queda desactualizada, pero tampoco puedes escribir en ella directamente.
            > Documentación oficial: [vistas de Atlas](https://www.mongodb.com/docs/atlas/atlas-ui/views/).
            """
        ),
        *question_cell(
            3,
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
        *question_cell(
            4,
            "Leer una tabla de clasificación",
            "313 noticias caen en 'terminos_control' (palabras como corrupción, peculado, sobrecosto) "
            "y 6 entidades tienen nivel de mención 'alta' (20 o más noticias).",
            "¿Cuál de estas lecturas es la correcta?",
            [
                "313 noticias demuestran 313 casos de corrupción distintos en contratación pública.",
                "313 noticias contienen palabras asociadas a control o irregularidad en su título o subtítulo; eso mide lenguaje, no hechos comprobados.",
                "Las 6 entidades de mención 'alta' son, por esa razón, las que más contratos irregulares tienen.",
                "Como 299 noticias no entraron en ninguna categoría de control, se pueden descartar del análisis.",
            ],
            1,
            [
                "Ese es el salto que hay que evitar: una palabra en un título no es una sentencia. El patrón detecta lenguaje, no verifica si hubo irregularidad real.",
                "Correcto. Es exactamente lo que el patrón puede afirmar: presencia de ciertas palabras. Confirmar si hay corrupción de verdad exige leer la noticia completa y, después, revisar el contrato.",
                "Mención alta significa que esa entidad aparece mucho en prensa — puede ser porque es grande, porque maneja presupuestos grandes, o porque efectivamente tiene problemas. La cobertura mide atención, no culpa.",
                "'Contexto' no es descartable: son noticias reales de contratación que simplemente no usan ese vocabulario. Siguen siendo evidencia externa válida.",
            ],
        ),

        # ── SEGUNDA MITAD ────────────────────────────────────────────────
        md(
            """
            ---
            ## Segunda mitad · De la vista de Atlas a la bandeja de Laura

            **NÚCLEO** · aquí sí escribes Python. Todo lo que sigue corre en esta pestaña de Colab.
            """
        ),
        code(
            """
            # Conectar Colab a tu clúster de Atlas, sin escribir la contraseña en el cuaderno.
            from getpass import getpass
            from urllib.parse import quote_plus
            from pymongo import MongoClient

            usuario = input("Usuario de base de datos (el del paso 6 de la guia): ").strip()
            contrasena = quote_plus(getpass("Contraseña (no se muestra en pantalla): "))
            host = input("Host del cluster, la parte que sigue a '@' en tu URI (ej. cluster0.xxxxx.mongodb.net): ").strip()

            uri = f"mongodb+srv://{usuario}:{contrasena}@{host}/?retryWrites=true&w=majority"

            try:
                client = MongoClient(uri, serverSelectionTimeoutMS=6000)
                client.admin.command("ping")
                db = client["compras_claras"]
                motor = "Atlas (conexión real)"
                print("Conectado a Atlas.")
            except Exception as error:
                # Modo de respaldo: NO fingimos una conexion que no existe.
                # Se avisa explicitamente y se sigue con los mismos datos, en local.
                print("No se pudo conectar a Atlas:", type(error).__name__)
                print("Modo de respaldo: trabajando con los archivos locales de la sesión 3.")
                import mongomock
                client = mongomock.MongoClient()
                db = client["compras_claras"]
                motor = "respaldo local (mongomock) — no es una conexión real a Atlas"

            print("Motor activo:", motor)
            """
        ),
        code(
            """
            # Leer la vista menciones_clasificadas. Si estas en modo de respaldo, la
            # reconstruimos localmente con la MISMA regla que usaste en Atlas.
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
        *question_cell(
            5,
            "Filtrar frente a ordenar",
            "La regla de priorización primero descarta procesos (filtra) y solo al final decide el orden (ordena).",
            "¿Por qué importa hacerlo en ese orden y no al revés?",
            [
                "No importa: filtrar y ordenar dan el mismo resultado en cualquier orden.",
                "Porque ordenar primero un millón de filas para luego filtrar desperdicia trabajo: es más barato descartar temprano y ordenar solo lo que sobrevivió.",
                "Porque pandas no permite ordenar antes de filtrar.",
                "Porque el orden alfabético del id_del_proceso cambia si filtras después.",
            ],
            1,
            [
                "El resultado final es el mismo, pero el costo no: es exactamente la regla de 'filtra temprano, agrupa después' que viste con $match y $group en la sesión 3, aplicada ahora a pandas.",
                "Correcto. Con 1.000 filas la diferencia es invisible, pero la regla es la misma que con $match antes de $group: descartar primero reduce el trabajo de lo que sigue.",
                "pandas ordena sin problema en cualquier momento — .sort_values() no exige haber filtrado antes.",
                "El id_del_proceso de cada fila no cambia por el orden en que ejecutes las operaciones; es un dato, no una posición.",
            ],
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
            6,
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
            ## Cassandra: una tabla para una sola pregunta

            **MAPA** · esto lo recorremos hablando y viendo una demostración en vivo. No necesitas una
            cuenta de Astra propia.

            Cassandra entra cuando la pregunta de Laura ya es **estable y se repite**:

            > Para una fecha de corte y un departamento, ¿cuáles son los cinco procesos de mayor valor que
            > debo abrir primero?

            MongoDB sigue alojando los documentos flexibles — noticias, entidades, vistas. Cassandra **no
            duplica** eso: guarda una **proyección desnormalizada**, hecha a la medida de esta consulta.
            Cassandra se modela desde las consultas que vas a hacer, no desde las entidades del negocio —
            es la diferencia de fondo con el modelo documental que usaste toda la noche.

            > Documentación oficial: [modelado de datos en Apache Cassandra](https://cassandra.apache.org/doc/latest/cassandra/developing/data-modeling/intro.html)
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
            7,
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
            """
        ),
        hidden(
            code(
                """
                # DEMOSTRACION DOCENTE — no ejecutes esta celda con tus propias credenciales.
                # Requiere: pip install "cassandra-driver>=3.29,<4" (3.29.3 es la ultima publicada;
                # la version 3.30 mencionada en versiones previas de este libreto no existe en PyPI),
                # un Secure Connect Bundle y un token de Astra generados desde el portal, y el
                # keyspace compras_claras ya creado (Astra no admite CREATE KEYSPACE por CQL).
                from getpass import getpass
                from datetime import date
                from cassandra.cluster import Cluster
                from cassandra.auth import PlainTextAuthProvider

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
            **Lo que deberías ver en Bogotá, si la base está recién creada:** en primer lugar
            `CO1.REQ.5407319` — el mismo Ministerio del Deporte, los mismos $168.750.000. **Es el mismo
            número que ya viste en pandas.** Cassandra no cambia la respuesta: solo la sirve distinto —
            mucho más rápido, y de una tabla hecha exactamente para esta pregunta.
            """
        ),
        *question_cell(
            8,
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
            primer caso verificado— y tu interpretación del límite. Las ocho preguntas son formativas: te
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
