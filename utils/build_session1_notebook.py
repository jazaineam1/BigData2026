# -*- coding: utf-8 -*-
"""Genera la sesión 1 de Big Data como clase guiada y reproducible."""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import code, md, save, validate


OUTPUT = "sesion1_introducci_n.ipynb"
WEB_CURSO = "https://jazaineam1.github.io/BigData2026/"
COLAB = (
    "https://colab.research.google.com/github/jazaineam1/BigData2026/"
    "blob/main/sesion1_introducci_n.ipynb"
)


def hidden(cell, *tags):
    cell["metadata"]["tags"] = list(tags or ("hide-input",))
    cell["metadata"]["jupyter"] = {"source_hidden": True}
    cell["metadata"]["cellView"] = "form"
    return cell


def question_cell(numero, tema, contexto, pregunta, opciones, correcta, retro_ok, retro_bad):
    """Crea una llamada breve al helper visual de preguntas."""
    return hidden(
        code(
            f"""
            # Pregunta {numero} de 10 — {tema}
            pregunta_interactiva(
                numero={numero},
                tema={tema!r},
                contexto={contexto!r},
                pregunta={pregunta!r},
                opciones={opciones!r},
                correcta={correcta},
                retro_correcta={retro_ok!r},
                retro_incorrecta={retro_bad!r},
            )
            """
        ),
        "hide-input",
        "pregunta-interactiva",
    )


def build_cells():
    cells = [
        md(
            f"""
            <a href="{COLAB}" target="_parent">
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir en Colab"/>
            </a>

            **Accesos de la sesión:** [página web del curso]({WEB_CURSO}) · [cuaderno en Colab]({COLAB})
            """
        ),
        md(
            """
            # Sesión 1 — Introducción a Big Data e ingesta de datos con Python

            ## Universidad Central
            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 2

            **Docente:** Julio Antonino Zainea Maya<br>
            **Periodo:** 2026-2S<br>
            **Duración sugerida:** 3 horas, incluida una pausa de 15 minutos<br>
            **Última actualización:** 6 de agosto de 2026

            Esta sesión abre el curso con una pregunta profesional: **¿cómo reconocer que un problema de datos
            necesita algo más que una hoja de cálculo o un único archivo cargado en memoria?**

            ### Ficha de la sesión

            | Campo | Valor |
            |---|---|
            | Modalidad de trabajo | Google Colab, explicación guiada y práctica |
            | Lenguaje | Python 3 |
            | Datos | Simulados, Saber 11 y SECOP vía API |
            | Evidencia final | Ficha reproducible de una fuente real |
            """
        ),
        md(
            """
            ## Alcance y producto de la sesión

            Al terminar podrás:

            1. Definir Big Data sin reducirlo a “muchos datos”.
            2. Usar las 5 V para diagnosticar necesidades de volumen, velocidad, variedad, veracidad y valor.
            3. Distinguir datos estructurados, semiestructurados y no estructurados.
            4. Comparar una solución local con una solución en la nube sin asumir que una siempre es superior.
            5. Ingerir datos con `pandas`, procesarlos por fragmentos y consultar una API pública.
            6. Interpretar resultados descriptivos y declarar qué todavía no se puede concluir.

            **Producto verificable:** una ficha breve que clasifique una fuente real de datos, describa su unidad de
            observación y proponga una estrategia de ingesta justificando al menos tres de las 5 V.
            """
        ),
        md(
            """
            ## Agenda sugerida

            | Tiempo | Bloque | Evidencia de aprendizaje |
            |---:|---|---|
            | 15 min | Bienvenida, alcance y caso | Pregunta profesional formulada |
            | 25 min | Por qué importa Big Data | Decisión y riesgo identificados |
            | 30 min | 5 V, infraestructura y nube | Diagnóstico con criterios |
            | 15 min | Pausa | — |
            | 25 min | Tipos de datos | Clasificación argumentada |
            | 40 min | Ingesta con Python | Lectura tabular y por fragmentos |
            | 20 min | Caso SECOP con API Socrata | Muestra consultada e interpretada |
            | 10 min | Ejercicio y cierre | Ficha de salida |

            Las preguntas interactivas aparecen durante todos los bloques. No son un examen final: sirven para
            detenerse, leer la evidencia y corregir el razonamiento mientras avanza la clase.
            """
        ),
        md(
            """
            ## Preparación del entorno

            Ejecuta el cuaderno en Google Colab. La siguiente celda confirma versiones y disponibilidad de las
            bibliotecas utilizadas. No instala paquetes innecesarios y no modifica tu equipo local.
            """
        ),
        hidden(
            code(
                """
                import sys
                import json
                import re
                import html as html_lib
                import xml.etree.ElementTree as ET
                from collections import Counter

                import matplotlib
                import matplotlib.pyplot as plt
                import pandas as pd
                import requests
                from IPython.display import HTML, Markdown, display

                print("Python:", sys.version.split()[0])
                print("pandas:", pd.__version__)
                print("matplotlib:", matplotlib.__version__)
                print("requests:", requests.__version__)
                """
            ),
            "hide-input",
            "soporte-entorno",
        ),
        md(
            """
            **¿Qué nos dice esta salida?** Confirma el entorno real en el que se ejecutará la sesión. Las versiones
            pueden cambiar en Colab; por eso se observan antes de atribuir un error al código o a los datos.
            """
        ),
        hidden(
            code(
                """
                def pregunta_interactiva(
                    numero,
                    tema,
                    contexto,
                    pregunta,
                    opciones,
                    correcta,
                    retro_correcta,
                    retro_incorrecta,
                ):
                    '''Muestra una pregunta autocorregible compatible con Google Colab.'''
                    uid = f"pregunta-{numero}"
                    opciones_html = "".join(
                        f'''<label style="display:block;margin:8px 0;cursor:pointer;">
                        <input type="radio" name="{uid}" value="{i}"> {html_lib.escape(opcion)}
                        </label>'''
                        for i, opcion in enumerate(opciones)
                    )
                    bloque = f'''
                    <div style="border:2px solid #1565c0;border-radius:12px;padding:16px;margin:16px 0;background:#e3f2fd;">
                      <h3 style="color:#0d47a1;margin-top:0;">Pregunta {numero} de 10 — {html_lib.escape(tema)}</h3>
                      <div style="background:#fff8d6;border-left:5px solid #f9a825;padding:12px;margin:10px 0;">
                        <strong>Contexto.</strong> {html_lib.escape(contexto)}
                      </div>
                      <p><strong>Pregunta.</strong> {html_lib.escape(pregunta)}</p>
                      {opciones_html}
                      <button onclick="verificar_{numero}()" style="background:#1565c0;color:white;border:0;border-radius:6px;padding:9px 15px;cursor:pointer;">
                        Verificar respuesta
                      </button>
                      <div id="retro-{numero}" style="margin-top:12px;"></div>
                    </div>
                    <script>
                    function verificar_{numero}() {{
                      const elegida = document.querySelector('input[name="{uid}"]:checked');
                      const salida = document.getElementById('retro-{numero}');
                      if (!elegida) {{
                        salida.innerHTML = '<div style="background:#fff3cd;color:#664d03;padding:10px;border-radius:6px;">Selecciona una opción antes de verificar.</div>';
                        return;
                      }}
                      const esCorrecta = Number(elegida.value) === {correcta};
                      const mensaje = esCorrecta ? {json.dumps(retro_correcta, ensure_ascii=False)} : {json.dumps(retro_incorrecta, ensure_ascii=False)};
                      const estilo = esCorrecta
                        ? 'background:#d1e7dd;color:#0f5132;border:1px solid #badbcc;'
                        : 'background:#f8d7da;color:#842029;border:1px solid #f5c2c7;';
                      salida.innerHTML = '<div style="' + estilo + 'padding:10px;border-radius:6px;">' + mensaje + '</div>';
                    }}
                    </script>
                    '''
                    display(HTML(bloque))
                """
            ),
            "hide-input",
            "soporte-interactividad",
        ),
        md(
            """
            ---
            # Bloque 1 — ¿Por qué importa Big Data?

            ## Caso de apertura: una empresa de entregas urbanas

            Una empresa recibe pedidos, posiciones GPS, lecturas de temperatura, mensajes de clientes y fotografías
            de entregas. La gerencia quiere anticipar retrasos y detectar incidentes antes de que el cliente reclame.

            El problema no es solo almacenar filas. Debe decidir:

            - qué datos capturar y con qué calidad;
            - con qué rapidez procesarlos;
            - cómo integrar tablas, eventos, texto e imágenes;
            - qué decisión concreta mejorará con el análisis;
            - cuánto cuesta operar la solución y qué riesgos de privacidad aparecen.

            **Idea central:** Big Data describe un problema de diseño y decisión. El volumen puede ser importante,
            pero por sí solo no determina la arquitectura.
            """
        ),
        md(
            """
            ### Definición formal, intuición y ejemplo pequeño

            **Definición formal de trabajo.** Un problema es Big Data cuando una o varias características de los datos
            obligan a adaptar la arquitectura de captura, almacenamiento, procesamiento, gobierno o consumo para
            entregar resultados útiles dentro del tiempo requerido.

            **Intuición.** Un archivo de 20 GB puede ser manejable si se procesa una vez al mes. En cambio, miles de
            eventos pequeños por segundo pueden exigir una arquitectura especial aunque el volumen diario no parezca
            enorme.

            **Ejemplo manual.** Si una sola máquina procesa 1 millón de registros por minuto y llegan 3 millones por
            minuto, la cola crece 2 millones por minuto. El problema inmediato es de velocidad y capacidad sostenida,
            no únicamente de almacenamiento.

            **Error común:** equiparar “Big Data” con “archivo grande”. La pregunta correcta es qué característica
            impide cumplir el objetivo con la solución actual.
            """
        ),
        question_cell(
            1,
            "Diagnóstico del problema",
            "La empresa procesa 1 millón de eventos por minuto, pero recibe 3 millones.",
            "¿Cuál es la primera dificultad que debe resolver?",
            [
                "La variedad, porque todos los eventos son diferentes",
                "La velocidad, porque la llegada supera la capacidad de proceso",
                "El valor, porque ningún evento sirve para decidir",
                "La visualización, porque todavía no existe un tablero",
            ],
            1,
            "Correcto. La cola aumenta en 2 millones de eventos por minuto: la capacidad no alcanza el ritmo de llegada. Un tablero no corrige ese cuello de botella.",
            "La opción es tentadora porque Big Data tiene varias dimensiones, pero aquí la evidencia cuantitativa compara 3 millones recibidos con 1 millón procesado. Eso identifica un problema de velocidad y capacidad.",
        ),
        md(
            """
            ## De los datos a una decisión profesional

            Los datos pueden apoyar optimización operativa, detección de fraude, personalización, investigación o
            predicción. Sin embargo, una iniciativa solo crea valor si conecta cuatro elementos:

            **fuente → procesamiento → evidencia → decisión**.

            En el caso de entregas, una alerta de retraso puede priorizar rutas o informar al cliente. Un conteo sin
            decisión asociada es descriptivo, pero todavía no demuestra impacto económico ni causalidad.
            """
        ),
        md(
            """
            ---
            # Bloque 2 — Las 5 V y la elección de infraestructura

            ## Las cinco características

            | V | Definición | Pregunta de diagnóstico | Ejemplo del caso |
            |---|---|---|---|
            | Volumen | Cantidad acumulada de datos | ¿Caben y se procesan con los recursos disponibles? | Años de posiciones GPS |
            | Velocidad | Ritmo de llegada y tiempo máximo de respuesta | ¿Cuánto retraso tolera la decisión? | Alertas durante la ruta |
            | Variedad | Diversidad de estructuras y formatos | ¿Cómo se integran tablas, JSON, texto e imágenes? | Pedidos, eventos y fotos |
            | Veracidad | Calidad, consistencia y relación señal-ruido | ¿Qué errores o sesgos comprometen la evidencia? | GPS ausente o impreciso |
            | Valor | Utilidad para una decisión | ¿Qué acción mejora y cómo se medirá? | Reducir entregas tardías |

            **Qué no prueban las 5 V:** no garantizan que una solución sea rentable, ética o causalmente efectiva.
            Funcionan como diagnóstico inicial, no como receta automática.
            """
        ),
        question_cell(
            2,
            "Las 5 V",
            "Un sensor reporta coordenadas cada segundo, pero el 30 % llega con ubicación imposible.",
            "¿Qué V está comprometida de manera más directa?",
            ["Volumen", "Velocidad", "Veracidad", "Valor"],
            2,
            "Correcto. El 30 % de ubicaciones imposibles afecta la fidelidad del dato. Procesar más rápido no corrige una señal incorrecta.",
            "El flujo puede ser rápido y voluminoso, pero la evidencia específica es que 30 % de las coordenadas es inválido. Eso corresponde a veracidad.",
        ),
        md(
            """
            ## On-premise y nube: una decisión con criterios

            **On-premise** significa que la organización opera infraestructura bajo su control directo. **Nube**
            significa consumir recursos administrados por un proveedor mediante modelos de servicio y pago.

            | Criterio | On-premise | Nube |
            |---|---|---|
            | Inversión | Mayor compra inicial | Pago operativo y por consumo |
            | Escalamiento | Requiere adquirir y configurar capacidad | Puede aprovisionarse con rapidez |
            | Control | Alto control físico y de configuración | Responsabilidad compartida con el proveedor |
            | Operación | La organización mantiene hardware y plataforma | Parte de la operación puede ser administrada |
            | Riesgo frecuente | Capacidad ociosa y renovación lenta | Costos variables y dependencia del proveedor |

            AWS, Microsoft Azure, Google Cloud e IBM Cloud son ejemplos de proveedores. No existe un “mejor” proveedor
            universal: se comparan servicios, residencia de datos, seguridad, habilidades del equipo, costo total y
            posibilidad de salida.

            **Error común:** afirmar que la nube siempre es más barata o más segura. Ambas propiedades dependen del
            diseño, la operación, el uso y el modelo de responsabilidad.
            """
        ),
        question_cell(
            3,
            "On-premise y nube",
            "Una entidad debe almacenar información regulada y necesita demostrar residencia, trazabilidad y control de acceso.",
            "¿Cuál es la decisión más responsable?",
            [
                "Elegir nube porque siempre es más segura",
                "Elegir on-premise porque nunca falla",
                "Comparar requisitos regulatorios, controles, costos y responsabilidades",
                "Comprar el servidor con mayor capacidad disponible",
            ],
            2,
            "Correcto. La arquitectura debe justificarse con requisitos verificables. Ni nube ni on-premise garantizan por sí solos seguridad, cumplimiento o costo óptimo.",
            "Las respuestas absolutas simplifican un problema de arquitectura. La evidencia necesaria incluye regulación, controles, responsabilidades, costos y capacidad operativa.",
        ),
        md(
            """
            > **Pausa sugerida — 15 minutos.** Al volver, pasaremos del diagnóstico de las 5 V a la forma concreta
            > que adoptan los datos y a cómo ingerirlos con Python.
            """
        ),
        md(
            """
            ---
            # Bloque 3 — Datos estructurados, semiestructurados y no estructurados

            ## Definiciones con un mismo caso

            | Tipo | Definición | Ejemplo pequeño | Ejemplo aplicado |
            |---|---|---|---|
            | Estructurado | Sigue un esquema tabular estable | Una fila por empleado | Tabla de pedidos |
            | Semiestructurado | Tiene marcas, claves o jerarquía, pero no exige filas uniformes | Objeto JSON | Evento de una aplicación |
            | No estructurado | Su contenido no está organizado como variables tabulares listas para analizar | Párrafo libre | Foto o comentario del cliente |

            La clasificación se refiere al **contenido analítico**, no a que el archivo carezca por completo de
            estructura técnica. Una imagen JPEG tiene un formato definido, pero sus objetos no aparecen como columnas
            listas para una consulta SQL.

            **Advertencia:** CSV suele tratarse como estructurado por su forma tabular, aunque no impone tipos ni reglas
            tan fuertes como una base de datos.
            """
        ),
        question_cell(
            4,
            "Tipos de datos",
            "Un evento JSON contiene id_pedido, fecha y una lista variable de productos.",
            "¿Cómo se clasifica mejor para fines analíticos?",
            ["Estructurado", "Semiestructurado", "No estructurado", "Dato sin formato"],
            1,
            "Correcto. JSON aporta claves y jerarquía, pero la lista de productos puede variar entre eventos. Esa combinación es característica de datos semiestructurados.",
            "JSON no es texto libre: conserva claves y jerarquía. Tampoco exige necesariamente el esquema tabular uniforme de una tabla relacional.",
        ),
        md(
            """
            ---
            # Bloque 4 — Datos estructurados con `pandas`

            ## Diccionario del ejemplo manual

            **Unidad de observación:** una persona empleada.

            | Variable | Tipo esperado | Significado |
            |---|---|---|
            | `Nombre` | texto | Nombre de la persona |
            | `Edad` | entero | Edad en años |
            | `Departamento` | categoría | Área organizacional |
            | `Salario` | numérico | Salario mensual simulado |

            Los datos son simulados y sirven para aprender operaciones. No representan salarios reales ni permiten
            inferencias sobre una organización.

            **Función usada: `pd.DataFrame()`**

            - Para qué sirve: construye una tabla con filas y columnas.
            - Parámetro usado: diccionario de listas con igual longitud.
            - Qué devuelve: un `DataFrame`.
            - Cómo interpretar: cada fila es una persona y cada columna es una variable.
            """
        ),
        code(
            """
            datos_empleados = {
                "Nombre": ["Ana", "Juan", "María", "Carlos", "Elena", "Pedro", "Laura", "Sofía", "Miguel", "Luis"],
                "Edad": [25, 30, 28, 22, 35, 40, 27, 29, 31, 24],
                "Departamento": ["Ventas", "TI", "RRHH", "Ventas", "Finanzas", "TI", "RRHH", "Finanzas", "TI", "Ventas"],
                "Salario": [50000, 60000, 55000, 45000, 70000, 75000, 52000, 58000, 62000, 48000],
            }

            empleados = pd.DataFrame(datos_empleados)
            display(empleados)
            """
        ),
        md(
            """
            **¿Cómo se lee la tabla?** Contiene 10 filas y 4 variables. Por ejemplo, Pedro tiene 40 años, pertenece
            a TI y registra un salario simulado de 75.000. Esto verifica estructura y contenido, pero todavía no resume
            diferencias entre departamentos ni demuestra desigualdad o causalidad.
            """
        ),
        md(
            """
            **Funciones usadas: filtro booleano y `groupby()`**

            - El filtro `empleados[empleados["Edad"] > 30]` conserva las filas que cumplen una condición.
            - `groupby("Departamento")` reúne filas por área.
            - `mean()` devuelve el promedio dentro de cada grupo.
            - El promedio resume esta tabla simulada; no describe una población real.
            """
        ),
        code(
            """
            mayores_de_30 = empleados[empleados["Edad"] > 30]
            salario_promedio = (
                empleados.groupby("Departamento", as_index=False)["Salario"]
                .mean()
                .sort_values("Salario", ascending=False)
            )

            display(mayores_de_30)
            display(salario_promedio.style.format({"Salario": "{:,.2f}"}))
            """
        ),
        md(
            """
            **¿Qué nos dice el resultado?** Hay 3 personas mayores de 30 años: Elena, Pedro y Miguel. En la tabla
            simulada, TI presenta el salario promedio más alto (65.666,67) y Ventas el más bajo (47.666,67), una
            diferencia descriptiva de 18.000.

            **¿Qué no podemos concluir?** No sabemos si la diferencia se debe al área, la experiencia, el cargo o al
            diseño artificial de los datos. Tampoco es una estimación de salarios reales.
            """
        ),
        question_cell(
            5,
            "Interpretación de una agrupación",
            "TI tiene promedio 65.666,67 y Ventas 47.666,67 en diez registros simulados.",
            "¿Cuál conclusión está respaldada?",
            [
                "Trabajar en TI causa un salario 18.000 mayor",
                "En esta tabla, el promedio de TI supera al de Ventas en 18.000",
                "Toda empresa paga más en TI",
                "La diferencia es estadísticamente significativa",
            ],
            1,
            "Correcto. La resta 65.666,67 − 47.666,67 describe únicamente estos datos. No establece causalidad, generalización ni significancia estadística.",
            "El distractor convierte una descripción de diez datos simulados en una afirmación causal o poblacional. La evidencia solo permite comparar los promedios observados.",
        ),
        md(
            """
            ---
            # Bloque 5 — Ingesta por fragmentos sin perder registros

            Trabajaremos con una copia del conjunto Saber 11 disponible en el repositorio del curso.

            **Fuente:** archivo `Datos/datos_icfes.csv` del repositorio.<br>
            **Unidad de observación:** un registro de resultados de una persona evaluada.<br>
            **Tamaño esperado de la copia:** 546.212 filas y 8 columnas.

            | Variable | Significado resumido |
            |---|---|
            | `ESTU_DEPTO_RESIDE` | Departamento de residencia |
            | `FAMI_ESTRATOVIVIENDA` | Estrato reportado de la vivienda |
            | `PUNT_LECTURA_CRITICA` | Puntaje de lectura crítica |
            | `PUNT_MATEMATICAS` | Puntaje de matemáticas |
            | `PUNT_C_NATURALES` | Puntaje de ciencias naturales |
            | `PUNT_SOCIALES_CIUDADANAS` | Puntaje de sociales y ciudadanas |
            | `PUNT_INGLES` | Puntaje de inglés |
            | `PUNT_GLOBAL` | Puntaje global |

            Los registros se usan para practicar ingesta. Antes de cualquier análisis sustantivo se necesitaría
            revisar procedencia, periodo, cobertura, valores faltantes y documentación oficial completa.
            """
        ),
        md(
            """
            **Función usada: `pd.read_csv()`**

            - Para qué sirve: lee datos tabulares desde un CSV.
            - Parámetros usados: URL, codificación `latin-1` y `chunksize=100_000`.
            - Qué devuelve con `chunksize`: un iterador; cada paso entrega un `DataFrame`.
            - Cómo interpretar: procesar un fragmento a la vez limita la memoria ocupada.

            **Advertencia crítica:** crear el iterador no equivale a leer todo el archivo. Por eso no se debe comparar
            el tiempo de “crear el lector” con el tiempo de cargar el CSV completo.
            """
        ),
        hidden(
            code(
                """
                url_icfes = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/Datos/datos_icfes.csv"
                filas_por_fragmento = []
                suma_puntaje = 0.0
                puntajes_validos = 0
                """
            ),
            "hide-input",
            "preparacion-icfes",
        ),
        code(
            """
            for numero, fragmento in enumerate(pd.read_csv(url_icfes, encoding="latin-1", chunksize=100_000), start=1):
                puntaje = pd.to_numeric(fragmento["PUNT_GLOBAL"], errors="coerce")
                filas_por_fragmento.append(len(fragmento))
                suma_puntaje += puntaje.sum()
                puntajes_validos += puntaje.notna().sum()
                print(f"Fragmento {numero}: {len(fragmento):,} filas")

            total_filas = sum(filas_por_fragmento)
            promedio_global = suma_puntaje / puntajes_validos
            print(f"Total procesado: {total_filas:,} filas")
            print(f"Promedio PUNT_GLOBAL: {promedio_global:.2f}")
            """
        ),
        md(
            """
            **¿Qué nos dice este resultado?** El archivo se recorre en seis fragmentos: cinco de 100.000 filas y uno
            de 46.212. La suma es 546.212, por lo que no se perdió ninguna observación. El promedio del puntaje global
            es aproximadamente 246,19.

            **¿Qué no podemos concluir todavía?** El promedio no mide calidad institucional, no controla diferencias
            territoriales o socioeconómicas y no identifica causas. Primero describe los registros disponibles.
            """
        ),
        question_cell(
            6,
            "Lectura por fragmentos",
            "Cinco fragmentos tienen 100.000 filas y el último 46.212.",
            "¿Qué comprobación protege contra la pérdida accidental de registros?",
            [
                "Ver que el primer fragmento tenga columnas",
                "Sumar las filas de todos los fragmentos y obtener 546.212",
                "Medir solo el tiempo de crear el iterador",
                "Concatenar después de consumir el primer fragmento sin reiniciar",
            ],
            1,
            "Correcto. 5 × 100.000 + 46.212 = 546.212. Ese control detecta si un fragmento fue omitido o consumido antes de la consolidación.",
            "La presencia de columnas no verifica completitud. Además, consumir un fragmento y luego concatenar el mismo iterador puede eliminar silenciosamente esas primeras filas.",
        ),
        md(
            """
            ## Paralelismo: extensión opcional, no primer recurso

            `pandarallel` distribuye ciertas operaciones `apply()` entre varios núcleos. Puede ayudar cuando la función
            es costosa y no existe una operación vectorizada, pero introduce coordinación y movimiento de datos.

            Antes de paralelizar:

            1. usa operaciones vectorizadas de pandas;
            2. mide la operación completa con los mismos datos y el mismo resultado;
            3. verifica que el resultado conserve filas y valores;
            4. solo después evalúa más núcleos o herramientas distribuidas.

            ```python
            # Opción preferida para elevar una columna al cuadrado
            df["lectura_al_cuadrado"] = df["PUNT_LECTURA_CRITICA"] ** 2

            # Extensión opcional cuando no hay alternativa vectorizada
            %pip install -q pandarallel
            from pandarallel import pandarallel
            pandarallel.initialize(nb_workers=3)
            df["resultado"] = df["columna"].parallel_apply(funcion_costosa)
            ```

            **Error común:** interpretar “usa tres núcleos” como “será tres veces más rápido”. La aceleración depende
            del costo de la tarea, los datos, la serialización y el entorno.
            """
        ),
        question_cell(
            7,
            "Paralelismo",
            "Se necesita elevar al cuadrado una columna numérica de pandas.",
            "¿Cuál es el primer enfoque recomendado?",
            [
                "Crear una función Python y paralelizarla inmediatamente",
                "Usar la operación vectorizada columna ** 2",
                "Convertir cada fila a JSON",
                "Duplicar el DataFrame antes de medir",
            ],
            1,
            "Correcto. La operación vectorizada usa las capacidades internas de pandas y evita el costo de ejecutar una función Python por fila.",
            "Paralelizar una función fila a fila añade coordinación innecesaria cuando pandas ya ofrece una operación vectorizada equivalente.",
        ),
        md(
            """
            ---
            # Bloque 6 — Datos semiestructurados: JSON y XML

            **Definición.** Los datos semiestructurados usan claves, etiquetas o jerarquías, pero permiten estructuras
            más flexibles que una tabla relacional.

            **Intuición.** Un objeto puede tener campos anidados u opcionales. Antes de analizarlo como tabla debemos
            decidir qué nivel representa una observación y cómo expandir listas o ausencias.

            **Funciones usadas: `json.dump()` y `json.load()`**

            - `json.dump()`: serializa objetos Python a un archivo JSON.
            - `json.load()`: reconstruye objetos Python desde el archivo.
            - Resultado: lista de diccionarios que luego puede convertirse en `DataFrame`.
            - Advertencia: que el archivo abra no garantiza que todas las claves existan en todos los objetos.
            """
        ),
        code(
            """
            empleados_json = [
                {"nombre": "Juan", "apellido": "Pérez", "edad": 28, "departamento": "Ventas"},
                {"nombre": "María", "apellido": "Gómez", "edad": 32, "departamento": "Desarrollo"},
                {"nombre": "Carlos", "apellido": "López", "edad": 24, "departamento": "Marketing"},
            ]

            with open("empleados.json", "w", encoding="utf-8") as archivo:
                json.dump(empleados_json, archivo, ensure_ascii=False, indent=2)
            """
        ),
        code(
            """
            with open("empleados.json", "r", encoding="utf-8") as archivo:
                datos_desde_json = json.load(archivo)

            empleados_desde_json = pd.DataFrame(datos_desde_json)
            display(empleados_desde_json)
            print("Edad promedio:", empleados_desde_json["edad"].mean())
            """
        ),
        md(
            """
            **¿Qué nos dice este resultado?** Los tres objetos JSON se convirtieron en tres filas y cuatro columnas.
            La edad promedio es 28 años: $(28 + 32 + 24) / 3 = 28$. Cada departamento aparece una vez.

            **¿Qué no podemos concluir?** La estructura regular de estos tres objetos no implica que un JSON real
            siempre tenga las mismas claves o que no contenga listas anidadas.
            """
        ),
        md(
            """
            **Funciones usadas: `ET.Element()`, `ET.SubElement()` y `ET.parse()`**

            - Para qué sirven: construir, guardar y leer una jerarquía XML.
            - Parámetros usados: elemento raíz `empleados` y elementos hijos por variable.
            - Qué devuelven: un árbol y nodos consultables.
            - Cómo interpretar: cada nodo `empleado` se transformará en una fila.
            """
        ),
        code(
            """
            empleados_xml = [
                {"nombre": "Juan", "apellido": "Pérez", "edad": 28, "departamento": "Ventas"},
                {"nombre": "María", "apellido": "Gómez", "edad": 32, "departamento": "Desarrollo"},
                {"nombre": "Carlos", "apellido": "López", "edad": 24, "departamento": "Marketing"},
                {"nombre": "Ana", "apellido": "Martínez", "edad": 30, "departamento": "Recursos Humanos"},
                {"nombre": "Luis", "apellido": "Rodríguez", "edad": 29, "departamento": "Ventas"},
                {"nombre": "Laura", "apellido": "Sánchez", "edad": 28, "departamento": "Desarrollo"},
                {"nombre": "Pedro", "apellido": "González", "edad": 26, "departamento": "Marketing"},
                {"nombre": "Sofía", "apellido": "López", "edad": 27, "departamento": "Ventas"},
            ]
            """
        ),
        code(
            """
            raiz = ET.Element("empleados")
            for registro in empleados_xml:
                nodo = ET.SubElement(raiz, "empleado")
                for clave, valor in registro.items():
                    ET.SubElement(nodo, clave).text = str(valor)

            ET.ElementTree(raiz).write("empleados.xml", encoding="utf-8", xml_declaration=True)
            """
        ),
        md(
            """
**¿Qué nos dice este resultado?** Creó una raíz `empleados`, añadió ocho nodos `empleado` y guardó el árbol
            en UTF-8. Todavía no hay un resumen: la siguiente etapa vuelve a leer el archivo y convierte explícitamente
            cada nodo en una fila.
            """
        ),
        code(
            """
            raiz_leida = ET.parse("empleados.xml").getroot()
            filas_xml = []
            for nodo in raiz_leida.findall("empleado"):
                filas_xml.append({
                    "nombre": nodo.findtext("nombre"),
                    "apellido": nodo.findtext("apellido"),
                    "edad": int(nodo.findtext("edad")),
                    "departamento": nodo.findtext("departamento"),
                })

            tabla_xml = pd.DataFrame(filas_xml)
            display(tabla_xml.head())
            """
        ),
        md(
            """
            **Lectura de la tabla XML.** Se recuperaron 8 filas y 4 columnas. Las primeras filas confirman que `edad`
            fue convertida a entero y que cada nodo `empleado` corresponde a una observación. Ahora sí podemos resumir
            por departamento.
            """
        ),
        code(
            """
            resumen_xml = tabla_xml.groupby("departamento")["edad"].agg(["count", "mean"])
            display(resumen_xml)
            """
        ),
        md(
            """
            **¿Cómo se lee el resumen?** XML produjo 8 observaciones. Ventas tiene 3 personas con edad promedio 28;
            Desarrollo 2 con promedio 30; Marketing 2 con promedio 25; Recursos Humanos 1 con promedio 30.

            **Advertencia:** el promedio de un grupo con una sola observación no representa variabilidad ni una
            población. Es únicamente el valor de esa persona.
            """
        ),
        question_cell(
            8,
            "JSON y XML",
            "Un archivo JSON contiene listas anidadas y algunas claves opcionales.",
            "¿Qué debe definirse antes de convertirlo en tabla?",
            [
                "El color del gráfico final",
                "La unidad de observación y cómo expandir listas y ausencias",
                "El proveedor de nube más grande",
                "El número de núcleos del computador",
            ],
            1,
            "Correcto. Sin unidad de observación, una lista puede convertirse erróneamente en varias columnas o varias filas y cambiar el significado del dato.",
            "La decisión clave ocurre antes de graficar o paralelizar: hay que definir qué representa una fila y cómo tratar la jerarquía y los campos ausentes.",
        ),
        md(
            """
            ---
            # Bloque 7 — Datos no estructurados: texto

            El texto libre no viene separado en variables analíticas. Un flujo básico incluye normalización,
            tokenización, eliminación justificada de palabras frecuentes y construcción de variables.

            **Ejemplo manual:** “datos útiles, datos confiables” contiene cuatro tokens; `datos` aparece dos veces.
            Esa frecuencia describe repetición, no importancia semántica ni sentimiento.

            **Funciones usadas: `re.findall()` y `Counter()`**

            - `re.findall()`: extrae tokens que cumplen un patrón.
            - `Counter()`: cuenta ocurrencias.
            - Resultado: pares palabra-frecuencia.
            - Error común: interpretar palabras funcionales como temas solo porque son frecuentes.
            """
        ),
        code(
            """
            texto = '''
            Una empresa de logística recibe datos de pedidos, datos de sensores y mensajes de clientes.
            Los datos permiten detectar retrasos, pero las decisiones requieren datos confiables y contexto.
            Un conteo de palabras describe el texto; no demuestra por qué ocurre un retraso.
            '''
            tokens = re.findall(r"\\b[a-záéíóúñü]+\\b", texto.lower())
            stopwords = {"de", "y", "el", "la", "las", "los", "un", "una", "pero", "por"}
            tokens_analiticos = [token for token in tokens if token not in stopwords]
            frecuencias = Counter(tokens_analiticos)
            tabla_frecuencias = pd.DataFrame(frecuencias.most_common(8), columns=["palabra", "frecuencia"])
            display(tabla_frecuencias)
            """
        ),
        md(
            """
            **Lectura de la tabla.** Después de retirar palabras funcionales, `datos` aparece 4 veces y es el término
            más repetido. Las demás palabras principales aparecen una vez. El gráfico siguiente representa esa misma
            tabla; no agrega evidencia nueva, pero facilita comparar magnitudes.
            """
        ),
        code(
            """

            plt.figure(figsize=(8, 4))
            plt.bar(tabla_frecuencias["palabra"], tabla_frecuencias["frecuencia"], color="#1565c0")
            plt.title("Palabras analíticas más frecuentes")
            plt.xlabel("Palabra")
            plt.ylabel("Frecuencia")
            plt.xticks(rotation=35)
            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            **¿Qué nos dice la tabla y el gráfico?** `datos` aparece 4 veces y domina este texto preparado. Las demás
            palabras principales aparecen una vez. Esto confirma el tema general del párrafo, pero no demuestra que
            los datos sean confiables, que reduzcan retrasos ni que exista una relación causal.

            **Advertencia:** la lista de palabras vacías depende del idioma y del objetivo. Eliminar una palabra puede
            borrar significado; por ejemplo, quitar “no” alteraría una negación.
            """
        ),
        question_cell(
            9,
            "Texto no estructurado",
            "La palabra datos aparece cuatro veces en un párrafo sobre logística.",
            "¿Cuál interpretación es válida?",
            [
                "Los datos causan retrasos",
                "Datos es el término más repetido del texto procesado",
                "El texto tiene sentimiento positivo",
                "La empresa ya toma buenas decisiones",
            ],
            1,
            "Correcto. La frecuencia describe repetición después del preprocesamiento. No identifica causalidad, sentimiento ni calidad de decisión.",
            "Un conteo de palabras no contiene evidencia suficiente para explicar causas, evaluar sentimiento o juzgar decisiones organizacionales.",
        ),
        md(
            """
            ---
            # Bloque 8 — Caso aplicado: consultar SECOP mediante la API Socrata

            **Pregunta del caso:** ¿cómo obtener una muestra reproducible de contratos públicos sin descargar primero
            el conjunto completo?

            **Fuente:** [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)<br>
            **Documentación de la API:** [Socrata Open Data API](https://dev.socrata.com/foundry/www.datos.gov.co/rpmr-utcd)<br>
            **Unidad de observación:** un registro contractual devuelto por la API.<br>
            **Alcance:** muestra de hasta 500 registros con departamento y valor no nulos.

            | Variable | Significado resumido |
            |---|---|
            | `nombre_de_la_entidad` | Entidad compradora reportada |
            | `nit_de_la_entidad` | Identificador de la entidad |
            | `departamento_entidad` | Departamento asociado |
            | `valor_contrato` | Valor registrado del contrato |

            **Función usada: `requests.get()`**

            - Para qué sirve: envía una solicitud HTTP GET.
            - Parámetros: endpoint, consulta Socrata y tiempo máximo de 30 segundos.
            - Qué devuelve: una respuesta HTTP; `raise_for_status()` detiene el flujo si falla.
            - Cómo interpretar: `response.json()` transforma la respuesta en objetos Python.
            """
        ),
        code(
            """
            url_secop = "https://www.datos.gov.co/resource/rpmr-utcd.json"
            parametros = {
                "$limit": 500,
                "$select": "nombre_de_la_entidad,nit_de_la_entidad,departamento_entidad,valor_contrato",
                "$where": "departamento_entidad is not null AND valor_contrato is not null",
            }

            respuesta = requests.get(url_secop, params=parametros, timeout=30)
            respuesta.raise_for_status()
            """
        ),
        code(
            """

            df_secop = pd.DataFrame(respuesta.json())
            df_secop["valor_contrato"] = pd.to_numeric(df_secop["valor_contrato"], errors="coerce")

            print("Estado HTTP:", respuesta.status_code)
            print("Registros recibidos:", len(df_secop))
            display(df_secop.head())
            """
        ),
        md(
            """
            **¿Cómo se lee esta salida?** Un estado HTTP 200 indica que la solicitud fue atendida. El número de filas
            debe ser menor o igual a 500 por el límite de la consulta. `head()` permite inspeccionar nombres, tipos y
            valores antes de calcular un indicador.

            **Qué no podemos concluir:** las primeras 500 filas no constituyen necesariamente una muestra aleatoria ni
            representan toda la contratación pública. El orden por defecto del servicio puede producir concentración
            por entidad, departamento o periodo.
            """
        ),
        code(
            """
            resumen_departamento = (
                df_secop.dropna(subset=["departamento_entidad", "valor_contrato"])
                .groupby("departamento_entidad", as_index=False)
                .agg(
                    registros=("valor_contrato", "size"),
                    valor_total=("valor_contrato", "sum"),
                    valor_mediano=("valor_contrato", "median"),
                )
                .sort_values("valor_total", ascending=False)
            )
            """
        ),
        md(
            """
            **Preparación del resumen.** La agregación produce una fila por departamento y tres métricas comparables:
            número de registros, suma y mediana. La siguiente celda muestra los diez primeros grupos y genera una lectura
            con los valores obtenidos en la ejecución actual.
            """
        ),
        code(
            """

            formato_dinero = {"valor_total": "${:,.0f}", "valor_mediano": "${:,.0f}"}
            display(resumen_departamento.head(10).style.format(formato_dinero))

            if not resumen_departamento.empty:
                lider = resumen_departamento.iloc[0]
                display(Markdown(
                    f"**Lectura automática de la muestra:** {lider['departamento_entidad']} "
                    f"presenta el mayor valor total observado (${lider['valor_total']:,.0f}) "
                    f"en {int(lider['registros'])} registros. Esta es una descripción de la muestra, no un censo."
                ))
            """
        ),
        md(
            """
            **¿Qué aporta la mediana?** Reduce la influencia de contratos extremadamente altos al representar el valor
            central de cada departamento. Comparar total, mediana y número de registros evita confundir “muchos
            contratos” con “contratos típicamente más altos”.

            **Advertencia:** valores monetarios requieren revisar moneda, ceros, duplicados, adiciones y reglas del
            conjunto antes de construir conclusiones sustantivas.
            """
        ),
        question_cell(
            10,
            "Muestra de una API",
            "La consulta recupera las primeras 500 filas disponibles y un departamento concentra casi todos los registros.",
            "¿Qué conclusión es metodológicamente responsable?",
            [
                "Ese departamento concentra toda la contratación de Colombia",
                "La API está equivocada",
                "La muestra está concentrada y debe revisarse el criterio de consulta antes de generalizar",
                "El valor total demuestra corrupción",
            ],
            2,
            "Correcto. El límite y el orden de la API pueden producir una muestra concentrada. Antes de generalizar hay que definir periodo, cobertura, paginación y estrategia de muestreo.",
            "La muestra no es evidencia suficiente para describir todo el país ni para afirmar irregularidad. El primer diagnóstico debe revisar cómo se seleccionaron las filas.",
        ),
        md(
            """
            ---
            # Ejercicio guiado — Ficha de una fuente real

            Trabaja con SECOP u otra fuente aprobada por el docente. Entrega una ficha de máximo una página que tenga:

            1. pregunta profesional y decisión que se quiere apoyar;
            2. fuente y enlace de descarga o API;
            3. unidad de observación y diccionario de mínimo cuatro variables;
            4. clasificación del tipo de datos;
            5. diagnóstico de al menos tres V;
            6. estrategia de ingesta y control de completitud;
            7. una tabla o gráfico con interpretación concreta;
            8. una conclusión descriptiva y una afirmación que todavía no puede hacerse.

            **Criterio de éxito:** otra persona debe poder repetir la ingesta y comprender exactamente qué representa
            una fila.
            """
        ),
        code(
            """
            # Espacio de trabajo del estudiante
            # 1. Define tu pregunta profesional.
            pregunta_profesional = ""

            # 2. Identifica la unidad de observación.
            unidad_observacion = ""

            # 3. Selecciona variables y construye un resumen reproducible.
            variables_seleccionadas = []

            # Escribe aquí tu código de ingesta, validación y resumen.
            """
        ),
        hidden(
            code(
                """
                # Solución orientativa: úsala después de intentar el ejercicio.
                pregunta_profesional = "¿Qué departamentos concentran mayor valor en la muestra consultada?"
                unidad_observacion = "Un registro contractual devuelto por la API SECOP."
                variables_seleccionadas = ["departamento_entidad", "valor_contrato"]

                solucion = (
                    df_secop[variables_seleccionadas]
                    .dropna()
                    .groupby("departamento_entidad", as_index=False)
                    .agg(registros=("valor_contrato", "size"), valor_total=("valor_contrato", "sum"))
                    .sort_values("valor_total", ascending=False)
                )
                display(solucion.head(10))

                print("Conclusión descriptiva: la tabla ordena el valor observado en la muestra.")
                print("Límite: no representa necesariamente todo SECOP ni demuestra causalidad o irregularidad.")
                """
            ),
            "hide-input",
            "solution",
        ),
        md(
            """
            ---
            # Cierre de la sesión

            ## Recapitulación

            - Big Data es un problema de arquitectura y decisión, no un sinónimo de archivo grande.
            - Las 5 V ayudan a diagnosticar necesidades, pero no garantizan valor ni causalidad.
            - La unidad de observación conecta estructura, ingesta e interpretación.
            - `chunksize` permite recorrer un CSV por fragmentos; la suma de filas protege contra pérdidas.
            - JSON y XML requieren decisiones explícitas para convertirse en tablas.
            - Una API facilita acceso reproducible, pero un límite de filas no crea una muestra representativa.

            ## Idea más importante

            **Toda arquitectura debe justificarse desde una decisión y toda salida debe interpretarse con su alcance y
            sus límites.** Procesar más datos no corrige automáticamente mala calidad, sesgo o una pregunta mal definida.

            ## Errores comunes que debes evitar

            1. comparar tiempos de operaciones que no hacen el mismo trabajo;
            2. consumir un fragmento y luego olvidar reiniciar el iterador;
            3. llamar “muestra representativa” a las primeras filas de una API;
            4. convertir una diferencia descriptiva en una afirmación causal;
            5. elegir nube, paralelismo o una herramienta distribuida antes de diagnosticar el problema.

            ## Próxima sesión

            Conectaremos este diagnóstico con vocabulario de nube y servicios de Google Cloud Platform: cómputo,
            almacenamiento, bases de datos y analítica administrada.
            """
        ),
        md(
            """
            ## Correspondencia con el cuaderno anterior

            | Contenido conservado | Nueva ubicación |
            |---|---|
            | Motivación e impacto de la era de datos | Bloque 1 |
            | 5 V de Big Data | Bloque 2 |
            | On-premise, nube y proveedores | Bloque 2 |
            | Tipos de datos | Bloque 3 |
            | Ejemplo de empleados con pandas | Bloque 4 |
            | `chunksize` e ICFES | Bloque 5, con control de completitud |
            | Paralelismo con pandas | Extensión opcional del bloque 5 |
            | JSON y XML | Bloque 6 |
            | Texto no estructurado | Bloque 7 |
            | API Socrata y SECOP | Bloque 8 y ejercicio guiado |

            La reorganización conserva los temas centrales, corrige los ejemplos que podían inducir pérdidas o
            comparaciones inválidas y añade objetivos, preguntas, interpretaciones y cierre.
            """
        ),
        md(
            """
            ## Referencias y recursos

- [Página web del curso](https://jazaineam1.github.io/BigData2026/)
            - [Documentación de pandas: `read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)
            - [Python: módulo `json`](https://docs.python.org/3/library/json.html)
            - [Python: procesamiento XML](https://docs.python.org/3/library/xml.etree.elementtree.html)
            - [Requests: guía rápida](https://requests.readthedocs.io/en/latest/user/quickstart/)
            - [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)
            - [Socrata Open Data API — SECOP](https://dev.socrata.com/foundry/www.datos.gov.co/rpmr-utcd)
            - [Repositorio del curso](https://github.com/jazaineam1/BigData2026)

            **Nota de uso:** las cifras de SECOP pueden cambiar porque provienen de una API viva. Conserva fecha,
            parámetros y límite de la consulta cuando presentes un resultado.
            """
        ),
    ]
    return cells


def main():
    cells = build_cells()
    validate(cells)
    save(cells, OUTPUT)


if __name__ == "__main__":
    main()
