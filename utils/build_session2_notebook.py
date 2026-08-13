# -*- coding: utf-8 -*-
"""Genera la Sesión 2 como clase guiada para estudiantes no técnicos."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate


OUTPUT = "Cuadernos/2_Definiciones_gcp.ipynb"
COLAB = (
    "https://colab.research.google.com/github/jazaineam1/BigData2026/"
    "blob/main/Cuadernos/2_Definiciones_gcp.ipynb"
)
WEB_CURSO = "https://jazaineam1.github.io/BigData2026/"
DIAGRAMS = "../assets/diagrams/session2"
TOTAL_QUESTIONS = 7


def hidden(cell, title, *tags):
    """Configura una celda para que el estudiante vea el formulario, no su código."""
    first_line = f'#@title {title} {{ display-mode: "form" }}'
    cell["source"] = [first_line + "\n"] + cell["source"]
    cell["metadata"]["tags"] = list(tags or ("hide-input",))
    cell["metadata"]["jupyter"] = {"source_hidden": True}
    cell["metadata"]["cellView"] = "form"
    cell["metadata"]["colab"] = {"formView": "both"}
    return cell


def question_cell(numero, tema, contexto, pregunta, opciones, correcta, retro_opciones):
    options_repr = repr(opciones)
    feedback_repr = repr(retro_opciones)
    return hidden(
        code(
            f"""
            # Pregunta {numero} de {TOTAL_QUESTIONS} — {tema}
            pregunta_interactiva(
                numero={numero},
                tema={tema!r},
                contexto={contexto!r},
                pregunta={pregunta!r},
                opciones={options_repr},
                correcta={correcta},
                retro_opciones={feedback_repr},
            )
            """
        ),
        f"Activar pregunta {numero} — {tema}",
        "hide-input",
        "pregunta-interactiva",
    )


def diagram(name, alt, width=980):
    """Inserta PNG visible y mantiene el SVG como versión ampliable."""
    return (
        f'<div align="center"><a href="{DIAGRAMS}/{name}.svg" target="_blank">'
        f'<img src="{DIAGRAMS}/{name}.png" width="{width}" alt="{alt}"></a></div>'
    )


def build_cells():
    cells = [
        md(
            f"""
            <a href="{COLAB}" target="_parent">
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir el cuaderno en Google Colab">
            </a>

            **Acceso público:** [página del curso]({WEB_CURSO})

            > **En Colab:** selecciona **Entorno de ejecución → Ejecutar todas**. Las siete preguntas aparecerán
            > con sus opciones y retroalimentación; su código permanecerá plegado.

            > **En el laboratorio:** trabajarás desde GitHub.com. No necesitas instalar Git, usar terminal, crear
            > cuentas de nube ni compartir claves. El docente entregará el enlace del repositorio de práctica.
            """
        ),
        md(
            """
            # Sesión 2 — De una necesidad empresarial a una decisión apoyada por datos

            ## Universidad Central
            <div align="center">
              <img src="https://universidad.ucentral.edu.co/tulengua/wp-content/themes/tulengua/images/logo-ucentral.png"
                   width="340" alt="Logo de la Universidad Central">
            </div>

            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 2

            **Temas de esta sesión:** arquitectura empresarial · administración de procesos de negocio · ciclo de
            vida de la analítica de Big Data · casos de uso organizacionales · BI tradicional y con Big Data<br>
            **Caso conductor:** Compras Claras — seguimiento de contratación pública con SECOP<br>
            **Duración:** 180 minutos — 90 de explicación y 90 de práctica<br>
            **Modalidad:** aprender haciendo, en parejas y desde el navegador<br>
            **Última actualización:** 13 de agosto de 2026

            ## Ficha de la sesión

            | Campo | Descripción |
            |---|---|
            | pregunta profesional | ¿qué procesos contractuales deberían revisarse primero? |
            | fuente | muestra local de SECOP con perfil descriptivo precomputado |
            | entorno | Colab para la clase y GitHub.com para el laboratorio |
            | producto | dos documentos conectados del proyecto semestral |
            """
        ),
        md(
            """
            ## Objetivos de aprendizaje y producto

            Al finalizar podrás:

            1. describir un proceso actual e identificar una demora, una decisión y un indicador;
            2. formular un caso de uso sin comenzar por una herramienta;
            3. explicar cuándo BI tradicional es suficiente y cuándo una necesidad puede justificar Big Data;
            4. leer una arquitectura empresarial desde negocio, información, aplicaciones y tecnología;
            5. seguir el recorrido captura → preparación → análisis → visualización → acción;
            6. reconocer quién debe definir, construir, interpretar y usar la evidencia;
            7. conservar una propuesta, una objeción y una corrección mediante GitHub.

            **Producto de la sesión.** Cada pareja completará dos documentos breves del mismo proyecto:

            - `01_decision_proceso.md`: qué debe decidir la organización y qué ocurre hoy;
            - `02_caso_arquitectura_accion.md`: qué solución se propone y cómo la evidencia vuelve al proceso.

            No evaluaremos memoria de comandos ni cantidad de cambios. Evaluaremos si la historia tiene sentido.
            """
        ),
        md(
            """
            ## La historia completa en una frase

            > Laura recibe información contractual tarde. Necesita saber qué revisar primero, comprender dónde se
            > produce la demora y proponer una forma responsable de convertir datos en una acción humana.

            La clase seguirá exactamente ese problema:

            1. **Decisión:** qué necesita resolver Laura.
            2. **Proceso:** cómo se trabaja actualmente y dónde se pierde tiempo.
            3. **Caso de uso y BI:** qué evidencia necesita y qué capacidad es suficiente.
            4. **Arquitectura empresarial:** cómo se organizan las partes de la solución.
            5. **Ciclo analítico:** cómo los datos terminan en una acción y producen nueva evidencia.
            6. **GitHub:** cómo una pareja construye y revisa esos acuerdos sin sobrescribirlos.

            Cada bloque responde una pregunta del anterior. No aparecerá una herramienta antes de explicar qué
            problema resuelve.
            """
        ),
        md(
            """
            ## Agenda de 180 minutos

            ### 90 minutos de explicación y conversación

            | Tiempo | Pregunta de la clase | Resultado |
            |---:|---|---|
            | 0–10 | ¿Qué debe decidir Laura? | decisión, responsable e indicador |
            | 10–30 | ¿Qué ocurre hoy? | proceso AS-IS y cuello de botella |
            | 30–48 | ¿Cuál es el caso de uso? | usuario, evidencia, acción y límite |
            | 48–62 | ¿Basta la BI actual? | veredicto BI / Big Data |
            | 62–77 | ¿Cómo se conectan las partes? | arquitectura empresarial |
            | 77–90 | ¿Cómo vuelve la evidencia al proceso? | ciclo analítico y responsabilidades |

            ### 90 minutos de laboratorio

            | Tiempo | Actividad | Evidencia para avanzar |
            |---:|---|---|
            | 90–100 | reconocer repositorio y evidencia | ambos ubican los tres archivos de trabajo |
            | 100–120 | completar decisión y proceso | cuello, KPI y límite coherentes |
            | 120–140 | completar caso y veredicto BI / Big Data | decisión sustentada sin marcas |
            | 140–158 | completar arquitectura y ciclo | cuatro dominios y cinco etapas conectados |
            | 158–172 | abrir y revisar Pull Request | una objeción específica y una corrección |
            | 172–180 | interpretar CI y cerrar | diferencia entre comprobación automática y juicio humano |
            """
        ),
        hidden(
            code(
                f"""
                import json
                import html as html_lib
                import sys
                from IPython.display import HTML, display

                TOTAL_QUESTIONS = {TOTAL_QUESTIONS}
                print("Interactividad preparada. Continúa con la historia de Compras Claras.")
                """
            ),
            "Preparar entorno e interactividad",
            "hide-input",
            "soporte-entorno",
        ),
        hidden(
            code(
                """
                def pregunta_interactiva(numero, tema, contexto, pregunta, opciones, correcta, retro_opciones):
                    '''Muestra una pregunta autocorregible con explicación específica por opción.'''
                    uid = f"pregunta-{numero}"
                    opciones_html = "".join(
                        f'''<label style="display:block;margin:9px 0;cursor:pointer;">
                        <input type="radio" name="{uid}" value="{i}"> {html_lib.escape(opcion)}
                        </label>'''
                        for i, opcion in enumerate(opciones)
                    )
                    retro_json = json.dumps(retro_opciones, ensure_ascii=False)
                    bloque = f'''
                    <div style="border:2px solid #1565c0;border-radius:12px;padding:16px;margin:16px 0;background:#e3f2fd;">
                      <h3 style="color:#0d47a1;margin-top:0;">Pregunta {numero} de {TOTAL_QUESTIONS} — {html_lib.escape(tema)}</h3>
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
                      const indice = Number(elegida.value);
                      const mensajes = {retro_json};
                      const esCorrecta = indice === {correcta};
                      const estilo = esCorrecta
                        ? 'background:#d1e7dd;color:#0f5132;border:1px solid #badbcc;'
                        : 'background:#f8d7da;color:#842029;border:1px solid #f5c2c7;';
                      salida.innerHTML = '<div style="' + estilo + 'padding:10px;border-radius:6px;"><strong>'
                        + (esCorrecta ? 'Correcto. ' : 'Revisa. ') + '</strong>' + mensajes[indice] + '</div>';
                    }}
                    </script>
                    '''
                    display(HTML(bloque))
                """
            ),
            "Preparar componente de preguntas",
            "hide-input",
            "soporte-interactividad",
        ),
        md(
            f"""
            ---
            # 1. Comenzar por la decisión

            Son las 8:00 a. m. Laura, analista de seguimiento, recibe registros contractuales y debe organizar su
            jornada. El director no le pide “usar Big Data”; le pregunta: **¿qué procesos deberíamos revisar primero?**

            Antes de hablar de arquitectura necesitamos cuatro acuerdos:

            | Acuerdo | Compras Claras | Por qué importa |
            |---|---|---|
            | usuario | Laura, analista de seguimiento | alguien debe interpretar la evidencia |
            | decisión | ordenar los casos que serán revisados | delimita la salida esperada |
            | indicador | tiempo desde actualización hasta primera revisión | permite comparar antes y después |
            | límite | la prioridad orienta una revisión humana | evita presentar una señal como acusación |

            {diagram('01_hilo_decision', 'Historia de Compras Claras: decisión, proceso, datos, evidencia, acción y mejora')}

            **Cómo leer la imagen.** Empieza en la decisión y avanza de izquierda a derecha. Los datos nacen en el
            proceso; la evidencia ayuda a Laura, pero Laura conserva la responsabilidad de actuar. La flecha de
            regreso significa que cada revisión genera nueva información para mejorar el proceso.

            **Conclusión.** Si no podemos nombrar usuario, decisión, indicador y límite, todavía no existe un caso
            analítico bien formulado.

            **Error frecuente:** medir cantidad de gráficos, archivos o herramientas. Esas cifras describen trabajo
            técnico, no demuestran que la revisión sea más oportuna.
            """
        ),
        question_cell(
            1,
            "Decisión e indicador",
            "El director propone medir el éxito por la cantidad de tecnologías instaladas.",
            "¿Qué indicador responde mejor al problema de Laura?",
            [
                "Número de servicios tecnológicos activados.",
                "Cantidad de columnas descargadas.",
                "Tiempo entre la actualización del registro y su primera revisión.",
                "Número de gráficos producidos.",
            ],
            2,
            [
                "Cuenta infraestructura, pero no demuestra que Laura reciba evidencia a tiempo.",
                "Más columnas pueden aumentar trabajo y confusión; no miden la mejora del proceso.",
                "Este indicador corresponde a la demora observada y permite comparar la situación actual con la propuesta.",
                "Un gráfico es un medio de comunicación; el valor aparece cuando apoya una revisión oportuna.",
            ],
        ),
        md(
            """
            ---
            # 2. Administración de procesos de negocio: comprender antes de cambiar

            Ya sabemos qué decisión apoyar. Ahora debemos localizar **dónde nace la demora**. La administración de
            procesos de negocio —BPM— ayuda a observar el trabajo de principio a fin, no solo una tarea aislada.

            **Definición formal.** BPM es la disciplina que permite descubrir, representar, analizar, mejorar y
            observar procesos para alcanzar un resultado medible.

            **En palabras sencillas.** Un proceso es la historia completa del trabajo: quién recibe algo, qué hace,
            qué decisión cambia la ruta y qué resultado entrega.

            | Concepto | Significado sencillo | Ejemplo |
            |---|---|---|
            | tarea | trabajo concreto | validar que una fecha sea coherente |
            | proceso | conjunto de tareas con un resultado | desde reportar ejecución hasta registrar la revisión |
            | compuerta o *gateway* | pregunta que dirige el flujo | ¿la información está completa? |
            | retrabajo | regreso a un paso anterior | solicitar corrección y esperar otra actualización |
            | SLA | tiempo esperado del servicio | priorizar en máximo 24 horas |
            | KPI | medición de lo que ocurrió realmente | horas transcurridas hasta la revisión |

            **Ejemplo pequeño.** En un reembolso, revisar la factura es una tarea. Recibir la solicitud, validar,
            decidir y pagar forman el proceso. Si falta un soporte, una compuerta devuelve el caso y produce retrabajo.

            **Error frecuente:** dibujar solo el camino en el que todo sale bien. Las esperas y devoluciones suelen
            explicar el verdadero cuello de botella.
            """
        ),
        md(
            f"""
            ## El proceso actual — AS-IS

            {diagram('02_proceso_as_is', 'Proceso actual de Compras Claras con actores, datos, decisión, retrabajo y cuello de botella')}

            **Cómo leerlo paso a paso.**

            1. Los carriles muestran quién participa: entidad contratante, SECOP y oficina de seguimiento.
            2. La entidad reporta hechos de la contratación; SECOP los publica; la oficina los descarga y une.
            3. La compuerta pregunta si fechas y estados son suficientes.
            4. Cuando faltan datos, el caso regresa al supervisor: aparece retrabajo y espera.
            5. El bloque rojo señala la consolidación manual, nuestra hipótesis de cuello de botella.

            **Qué dato nace dónde.** El supervisor produce estado y fechas; SECOP conserva el registro; la oficina
            produce una lista de casos; Laura produce la decisión final y su motivo.

            **Qué todavía no sabemos.** El diagrama es una hipótesis razonable, no una prueba de cómo funciona cada
            entidad. Antes de implementar habría que entrevistar a quienes ejecutan el proceso y medir los tiempos.

            **Conexión.** Al comprender el trabajo actual podemos formular un caso de uso que responda al cuello, no
            a una moda tecnológica.
            """
        ),
        question_cell(
            2,
            "Proceso, compuerta y retrabajo",
            "La tarea valida fechas y produce dos resultados: información suficiente o información incompleta.",
            "¿Cómo debe representarse la decisión posterior?",
            [
                "La tarea almacena los archivos y termina el proceso.",
                "Una compuerta dirige: suficiente continúa; incompleta regresa para corrección.",
                "Un gráfico reemplaza la decisión y elimina la revisión.",
                "El SLA decide automáticamente si existe irregularidad.",
            ],
            1,
            [
                "La tarea realiza la validación, pero no muestra las dos rutas ni el retrabajo.",
                "La compuerta hace explícita la regla y permite ver que la ruta incompleta produce espera y corrección.",
                "Una visualización comunica resultados; no representa ni ejecuta el flujo del proceso.",
                "El SLA fija un tiempo esperado y no permite concluir irregularidad ni reemplazar el juicio humano.",
            ],
        ),
        md(
            """
            ---
            # 3. Casos de uso de Big Data en las organizaciones

            Un caso de uso no es el nombre de una herramienta. Es una descripción clara de **quién usa qué evidencia
            para decidir o actuar dentro de un proceso**.

            | Pregunta | Compras Claras |
            |---|---|
            | ¿quién? | Laura, analista de seguimiento |
            | ¿qué decide? | qué registros revisar primero |
            | ¿con qué evidencia? | fechas, estado, duración y completitud |
            | ¿qué recibe? | lista priorizada con el motivo visible |
            | ¿qué hace? | revisa, solicita corrección, escala o descarta |
            | ¿cómo se mide? | tiempo hasta primera revisión |
            | ¿qué no afirma? | fraude, causalidad o irregularidad |

            **Ejemplo no técnico.** “Analizar clientes” no es un caso de uso. “Cada lunes, la coordinadora identifica
            clientes sin respuesta durante siete días para asignar seguimiento” sí lo es: tiene persona, momento,
            evidencia, acción e indicador.

            **Casos comunes en las organizaciones:** describir desempeño, detectar eventos que requieren atención,
            recomendar un orden de trabajo, predecir una demanda u optimizar recursos. El verbo ayuda a reconocer la
            decisión; el sector por sí solo no la define.

            **Compras Claras describe, detecta y recomienda.** Describe calidad y duración, detecta registros que
            merecen atención y recomienda un orden de revisión. No predice culpabilidad.
            """
        ),
        question_cell(
            3,
            "Formulación del caso de uso",
            "Un equipo escribe: «implementar una plataforma tecnológica de tiempo real para contratación».",
            "¿Qué reformulación permite evaluar primero el valor?",
            [
                "Instalar la plataforma y decidir después quién la usará.",
                "Definir usuario, decisión, evidencia, acción, indicador y límite antes de elegir tecnología.",
                "Cambiar una tecnología por inteligencia artificial sin modificar la necesidad.",
                "Llamar estratégico al proyecto y omitir el proceso actual.",
            ],
            1,
            [
                "La plataforma seguiría sin usuario ni resultado verificable y podría aumentar el trabajo sin aportar valor.",
                "Estos elementos convierten la idea en un caso evaluable y permiten comparar soluciones distintas.",
                "Cambiar la etiqueta tecnológica no corrige la ausencia de una decisión y una acción definidas.",
                "La importancia declarada no sustituye evidencia sobre el proceso, el responsable y la mejora esperada.",
            ],
        ),
        md(
            """
            ## Inteligencia de negocios tradicional y con Big Data

            **BI tradicional** organiza datos conocidos, indicadores y reportes para comprender qué ocurrió y apoyar
            decisiones periódicas. Es una solución válida cuando los datos, el tiempo de respuesta y el número de
            usuarios pueden manejarse de forma confiable.

            **BI con capacidades Big Data** amplía esa solución cuando una necesidad demostrable exige trabajar con
            mucha más escala, rapidez, variedad o complejidad. Big Data no reemplaza automáticamente a la BI.

            | Pregunta | BI puede ser suficiente | Conviene estudiar Big Data cuando... |
            |---|---|---|
            | tiempo | un informe diario llega antes de decidir | minutos o segundos cambian una acción real |
            | datos | tablas conocidas y manejables | texto, imágenes, eventos y muchas fuentes son indispensables |
            | escala | el proceso cumple tiempo y costo actuales | deja de cumplirlos de forma medida y repetida |
            | análisis | indicadores y reglas explicables responden | la decisión exige métodos o procesamiento que la solución actual no soporta |

            **Veredicto para el primer hito.** Con una muestra pequeña, una actualización diaria y reglas
            descriptivas, BI gobernada y procesamiento sencillo son suficientes. Se reconsiderará la arquitectura si
            mediciones reales muestran que volumen, tiempo, variedad o confiabilidad impiden cumplir el objetivo.

            **Error frecuente:** pensar que “tradicional” significa atrasado y que “Big Data” siempre significa mejor.
            La solución madura es la que resuelve el problema con una complejidad proporcional.
            """
        ),
        question_cell(
            4,
            "BI tradicional frente a Big Data",
            "La oficina recibe un archivo estructurado al día, lo procesa en minutos y decide dentro de 24 horas.",
            "¿Cuál es el veredicto más responsable para el primer hito?",
            [
                "Usar procesamiento distribuido porque el curso se llama Big Data.",
                "Usar BI gobernada y procesamiento sencillo; definir mediciones que indiquen cuándo reevaluar.",
                "Comprar una plataforma antes de medir el proceso actual.",
                "Declarar que cualquier archivo diario ya necesita Big Data.",
            ],
            1,
            [
                "Añadiría costo y operación sin un requisito de escala, variedad o tiempo que lo justifique.",
                "La solución satisface la decisión actual y deja una condición medible para evolucionar más adelante.",
                "Sin línea base no puede demostrarse que la solución actual sea insuficiente ni que la compra aporte valor.",
                "La frecuencia por sí sola no define Big Data; importa si la capacidad actual incumple una necesidad real.",
            ],
        ),
        md(
            """
            ---
            # 4. Arquitectura empresarial: conectar el propósito con la solución

            Ya conocemos la decisión, el proceso y el caso de uso. Ahora necesitamos comprobar que todas las partes
            de la solución apunten al mismo resultado.

            **Definición formal.** La arquitectura empresarial describe cómo negocio, información, aplicaciones y
            tecnología se relacionan para alcanzar objetivos y evolucionar de una situación actual —AS-IS— a una
            situación deseada —TO-BE—.

            **En palabras sencillas.** Es un plano compartido. No comienza con marcas ni productos; comienza con el
            resultado que la organización quiere mejorar.

            | Dominio | Pregunta sencilla | Compras Claras |
            |---|---|---|
            | negocio | ¿para qué, quién y qué proceso? | priorizar y revisar con responsabilidad humana |
            | información | ¿qué datos deben significar lo mismo? | contrato, estado, fechas, duración y calidad |
            | aplicaciones | ¿qué funciones necesita el usuario? | obtener, revisar calidad, priorizar y mostrar |
            | tecnología | ¿dónde y bajo qué condiciones funciona? | conexión, almacenamiento y ejecución confiable |

            **Ejemplo pequeño.** Una clínica quiere reducir el tiempo de asignación de citas. Negocio define la meta;
            información define paciente, agenda y estado; aplicaciones reciben y asignan; tecnología permite operar
            con seguridad. Comprar un servidor no sustituye esos acuerdos.

            **Controles transversales.** Seguridad, privacidad, calidad y costo se revisan en todos los dominios. Son
            condiciones de la solución, no capas adicionales para memorizar.
            """
        ),
        md(
            f"""
            ## Arquitectura objetivo — TO-BE

            {diagram('05_arquitectura_to_be', 'Arquitectura objetivo de Compras Claras con negocio, información, aplicaciones, tecnología y controles')}

            **Cómo leerla.** Empieza arriba, en el objetivo y la acción humana. Luego baja hacia los datos, las
            funciones necesarias y el soporte tecnológico. La columna numerada muestra una sola cadena completa:
            objetivo → proceso → dato → función → soporte → indicador.

            **Cómo comprobar si algo sobra.** Pregunta “¿qué decisión o necesidad justifica este elemento?”. Si una
            herramienta no puede responder, todavía no debería aparecer en el diseño.

            **Limitación.** Esta arquitectura es lógica: explica qué debe existir, pero todavía no selecciona un
            proveedor ni fija un presupuesto. Eso requiere mediciones que aún no tenemos.

            ### Las responsabilidades que necesitamos en esta historia

            No se trata de memorizar cargos. Para este primer hito basta reconocer cuatro preguntas:

            | Perspectiva | Pregunta que debe quedar respondida |
            |---|---|
            | negocio | ¿qué decisión y qué resultado deben mejorar? |
            | significado del dato | ¿qué quiere decir cada fecha, estado y excepción? |
            | preparación de la evidencia | ¿cómo obtenemos datos comparables y sabemos si fallaron? |
            | análisis | ¿qué ocurrió, cómo se prioriza y qué no podemos concluir? |

            En organizaciones grandes estas responsabilidades pueden corresponder al dueño del proceso, *data
            steward*, ingeniero de datos y analista BI. En un equipo pequeño una persona puede asumir varias. El
            científico de datos solo sería necesario si aparece un problema predictivo que las reglas descriptivas y
            la BI no resuelven suficientemente; no es el punto de partida de Compras Claras.
            """
        ),
        question_cell(
            5,
            "Trazabilidad arquitectónica",
            "El equipo propone una herramienta popular, pero no puede relacionarla con una decisión del proceso.",
            "¿Qué debe hacer antes de incluirla en la arquitectura?",
            [
                "Instalarla y buscar después un problema.",
                "Explicar qué necesidad, dato, función e indicador justifican su existencia.",
                "Reemplazar el proceso por una lista de productos.",
                "Ocultar el costo para no limitar el diseño.",
            ],
            1,
            [
                "La tecnología quedaría sin un resultado verificable y añadiría complejidad innecesaria.",
                "La cadena de trazabilidad permite comprobar que cada componente responde al objetivo empresarial.",
                "Los productos no muestran quién trabaja, qué decide ni qué datos necesita.",
                "El costo es una condición real de la arquitectura y puede cambiar una alternativa técnicamente posible.",
            ],
        ),
        md(
            """
            ---
            # 5. Ciclo de vida de la analítica de Big Data

            La arquitectura muestra las partes. El ciclo analítico muestra **cómo viaja la evidencia** hasta una
            acción. En esta sesión usamos cinco etapas del marco NIST:

            | Etapa | Pregunta sencilla | Compras Claras |
            |---|---|---|
            | captura | ¿de dónde obtenemos los hechos? | muestra de SECOP con fecha y origen |
            | preparación | ¿qué debemos ordenar o validar? | tipos, fechas, faltantes y unidades |
            | análisis | ¿qué patrón ayuda a decidir? | reglas descriptivas y lista candidata |
            | visualización | ¿cómo entiende Laura el resultado? | prioridad, motivo y límite visibles |
            | acción | ¿qué hace la persona y qué registra? | revisar, corregir, escalar o descartar |

            **Ejemplo pequeño.** En una biblioteca: se capturan préstamos, se corrigen fechas, se analiza demanda, se
            muestra una lista de libros y la responsable decide cuáles adquirir. La compra registrada genera nuevos
            datos y el ciclo vuelve a comenzar.

            **Tres ideas importantes.**

            - Preparar no significa “maquillar” datos: significa documentar reglas y excepciones.
            - Visualizar no es actuar: un tablero sin responsable no mejora el proceso.
            - La acción produce nueva evidencia: resultado, fecha, motivo y aprendizaje.

            **Error frecuente:** comenzar por el tablero y descubrir después que las fechas no significan lo mismo.
            """
        ),
        md(
            f"""
            ## El ciclo aplicado a SECOP

            {diagram('06_ciclo_nist', 'Ciclo analítico aplicado a SECOP: captura, preparación, análisis, visualización, acción y retroalimentación')}

            **Cómo leerlo.** Sigue las cinco etapas en sentido horario. La banda central recuerda que calidad,
            seguridad y trazabilidad acompañan todo el recorrido. La flecha de regreso muestra que Laura registra el
            resultado de la revisión y ese dato permite ajustar reglas o incluso replantear el proceso.

            **Conclusión.** El valor no termina en una lista priorizada. Termina cuando una persona usa la evidencia,
            registra qué hizo y permite evaluar si el indicador mejoró.

            **Límite.** El ciclo no prescribe una herramienta ni demuestra causalidad; organiza responsabilidades y
            evidencia.
            """
        ),
        question_cell(
            6,
            "Ciclo analítico: visualización y acción",
            "El tablero muestra cinco registros incompletos, pero nadie tiene asignada la revisión.",
            "¿Qué falta para cerrar el ciclo analítico?",
            [
                "Cambiar los colores del tablero.",
                "Agregar más gráficos sin responsable.",
                "Asignar responsable, regla de atención y registro de la decisión.",
                "Declarar que los cinco casos son irregulares.",
            ],
            2,
            [
                "El diseño visual puede ayudar a leer, pero no crea una acción dentro del proceso.",
                "Más visualización no sustituye a la persona que revisa ni al registro del resultado.",
                "Estos elementos convierten la señal en trabajo trazable y producen evidencia para mejorar el ciclo.",
                "La incompletitud es una señal de calidad y no prueba irregularidad ni causalidad.",
            ],
        ),
        md(
            f"""
            ---
            # GitHub como puente para construir el mismo proyecto

            Hasta aquí cada responsabilidad aportó una parte. El problema siguiente es cotidiano: ¿cómo evitar
            archivos como `final_v2_ahora_si.md`, saber qué cambió y conservar una pregunta del compañero?

            GitHub ofrece una forma práctica:

            | Elemento | Explicación no técnica |
            |---|---|
            | `main` | versión acordada del proyecto |
            | rama | copia de trabajo donde se prepara una propuesta sin alterar `main` |
            | commit | punto guardado con una explicación breve del cambio |
            | Pull Request o PR | espacio para comparar, preguntar y corregir antes de integrar |
            | CI o *Checks* | comprobaciones automáticas sobre aspectos observables |

            {diagram('07_estados_git', 'GitHub como conversación: propuesta, revisión, corrección, comprobación y decisión humana')}

            **Cómo leer la imagen.** Una necesidad produce una propuesta. El compañero formula una objeción; la misma
            rama recibe una corrección; CI comprueba estructura y una persona juzga el sentido. GitHub conserva la
            conversación, pero no decide si la arquitectura es correcta.

            **Por qué aparece aquí y no antes.** Ahora sí tenemos algo valioso que conservar: decisión, proceso,
            arquitectura, ciclo y límites. GitHub es el medio de colaboración, no otro tema para memorizar.
            """
        ),
        question_cell(
            7,
            "Roles y GitHub como relevo",
            "Cambió el significado de una fecha: debe aclararse la definición, corregirse el flujo y reinterpretarse el indicador.",
            "¿Qué práctica conserva mejor ese relevo?",
            [
                "Una sola persona cambia todo directamente en main sin explicar el motivo.",
                "Cada persona envía un archivo final por correo y se usa el más reciente.",
                "El equipo documenta la objeción en un PR, corrige la misma rama y explica el efecto del cambio.",
                "La calidad se decide contando commits y líneas modificadas.",
            ],
            2,
            [
                "El cambio puede funcionar técnicamente y aun perder el significado o la revisión necesaria.",
                "La fecha del archivo no permite reconstruir qué se preguntó, qué se corrigió ni qué se aprobó.",
                "El PR relaciona propuesta, pregunta y corrección; la revisión humana valida el significado y el impacto.",
                "La cantidad de actividad puede premiar fragmentación y no demuestra comprensión ni calidad.",
            ],
        ),
        md(
            """
            ---
            # Laboratorio guiado — 90 minutos desde GitHub.com

            ## Qué debes producir

            La pareja completará únicamente:

            1. `hitos/s02/01_decision_proceso.md`;
            2. `hitos/s02/02_caso_arquitectura_accion.md`.

            El archivo `resultados/perfil_secop.md` ya contiene evidencia descriptiva. **No debes programar ni
            modificarlo.** Úsalo para sustentar tus respuestas.

            - Perspectiva **negocio/dominio:** decisión, proceso, indicador y límites.
            - Perspectiva **datos/analítica:** caso de uso, arquitectura, ciclo e interpretación.

            Luego intercambiarán perspectivas. La meta no es llenar tablas: es que ambos puedan contar la misma
            historia de principio a fin.
            """
        ),
        md(
            """
            ## Paso 0 — Antes de editar

            **Acción**

            1. Inicia sesión en la cuenta de GitHub que usarás en el curso.
            2. Abre el enlace privado entregado por el docente.
            3. Comprueba que en la parte superior aparezca el repositorio de tu pareja.

            **Resultado esperado:** ves `README.md`, `hitos/`, `resultados/` y la rama `main`.

            **Si aparece 404:** probablemente abriste otra cuenta o aún no tienes acceso. No crees un *fork* público;
            informa al docente tu nombre de usuario de GitHub.
            """
        ),
        md(
            """
            ## Paso 1 — Crear la rama de trabajo

            **Acción**

            1. En la página principal del repositorio, localiza el selector que dice **main**.
            2. Ábrelo y escribe `hito/s02-negocio`.
            3. Selecciona **Create branch: hito/s02-negocio from main**.
            4. Comprueba que el selector ahora muestre `hito/s02-negocio`.

            **Qué significa:** creaste una propuesta separada. `main` continúa siendo la versión acordada.

            **Si la rama ya existe:** selecciónala; no crees `hito/s02-negocio-2`. Es posible que tu compañero haya
            comenzado primero.
            """
        ),
        md(
            """
            ## Paso 2 — Leer la evidencia antes de responder

            **Acción**

            1. Verifica que sigues en `hito/s02-negocio`.
            2. Abre `resultados/perfil_secop.md`.
            3. Identifica tres hechos: registros analizados, fechas con problemas y duración máxima.
            4. Lee también la columna de límites.

            **Resultado esperado:** puedes explicar una observación sin afirmar fraude, incumplimiento o causalidad.

            **Error frecuente:** copiar una cifra sin explicar qué permite observar y qué no permite concluir.
            """
        ),
        md(
            """
            ## Paso 3 — Completar decisión y proceso

            **Acción**

            1. Regresa a la raíz del repositorio.
            2. Abre `hitos/s02/01_decision_proceso.md`.
            3. Pulsa el ícono de lápiz **Edit this file**.
            4. Reemplaza cada marcador `<!-- COMPLETAR -->` con respuestas breves.
            5. Usa la pestaña **Preview** para comprobar la tabla y el diagrama.

            **Criterio para avanzar:** el documento dice quién decide, qué decide, dónde está el cuello, qué indicador
            observará y cuál es el límite de la evidencia.

            **Si el diagrama no aparece:** revisa que no hayas borrado las líneas con tres acentos graves. No es
            necesario rediseñarlo; basta con comprenderlo y completar el análisis.
            """
        ),
        md(
            """
            ## Paso 4 — Guardar la primera versión

            **Acción**

            1. Pulsa **Commit changes...**.
            2. En el mensaje escribe: `Explica decisión y proceso actual`.
            3. Confirma que aparezca **Commit directly to the hito/s02-negocio branch**.
            4. Pulsa **Commit changes**.

            **Resultado esperado:** GitHub vuelve al archivo y muestra tu mensaje en el historial. La rama sigue siendo
            `hito/s02-negocio`; `main` no cambió.

            **Si solo ofrece guardar en main:** cancela y verifica el selector de rama antes de continuar.
            """
        ),
        md(
            """
            ## Paso 5 — Completar caso, arquitectura y ciclo

            **Acción**

            1. En la misma rama abre `hitos/s02/02_caso_arquitectura_accion.md`.
            2. Pulsa **Edit this file**.
            3. Completa el caso de uso, el veredicto BI / Big Data, los cuatro dominios y las cinco etapas.
            4. En **Preview**, comprueba que cada tabla pueda leerse sin desplazamientos confusos.
            5. Guarda con el mensaje: `Conecta caso, arquitectura y acción`.

            **Criterio para avanzar:** una persona ajena al equipo puede seguir la cadena decisión → proceso → dato →
            evidencia → acción.

            **Error frecuente:** escribir nombres de herramientas sin explicar qué necesidad resuelven.
            """
        ),
        md(
            """
            ## Paso 6 — Abrir el Pull Request

            **Acción**

            1. Abre la pestaña **Pull requests**.
            2. Pulsa **New pull request**.
            3. Confirma **base: main** y **compare: hito/s02-negocio**.
            4. Pulsa **Create pull request**.
            5. Usa como título: `Hito S02 — decisión, arquitectura y acción`.
            6. Completa las secciones de la plantilla: qué hicimos, por qué, cómo verificamos, interpretación y límites,
               y objeción/corrección entre perspectivas.
            7. Pulsa nuevamente **Create pull request**.

            **Resultado esperado:** el PR muestra las pestañas **Conversation**, **Commits**, **Checks** y
            **Files changed**.

            **Si GitHub dice que no hay cambios:** comprueba que `compare` sea tu rama y que los commits no se hayan
            creado en `main`.
            """
        ),
        md(
            """
            ## Paso 7 — Revisar como compañero

            **Acción**

            1. El segundo integrante abre el mismo PR con su propia cuenta.
            2. Entra en **Files changed**.
            3. Busca una afirmación que necesite evidencia o una definición que pueda ser ambigua.
            4. Pulsa el signo **+** junto a la línea y escribe una pregunta concreta.

            **Modelo de comentario:** “La fecha usada para medir la demora no está definida. ¿Es fecha de publicación,
            inicio o actualización? Esta elección puede cambiar el KPI”.

            **Comentario insuficiente:** “todo bien”, “me gusta” o “corrige esto”.

            **Resultado esperado:** la conversación señala qué decisión se afecta y qué debe poder verificarse.
            """
        ),
        md(
            """
            ## Paso 8 — Corregir sin abrir otra propuesta

            **Acción**

            1. Vuelve a la pestaña **Code** del repositorio.
            2. Selecciona `hito/s02-negocio`.
            3. Edita el archivo señalado y atiende la objeción.
            4. Guarda con el mensaje: `Aclara definición y efecto en el indicador`.
            5. Regresa al PR y responde: “Se cambió X porque Y; ahora puede verificarse Z”.

            **Resultado esperado:** el PR se actualiza automáticamente. No debes abrir otro PR ni crear otra rama.

            **Error frecuente:** responder el comentario sin modificar el artefacto. La conversación debe quedar unida
            a una corrección visible.
            """
        ),
        md(
            """
            ## Paso 9 — Interpretar Checks sin confundirlos con evaluación humana

            **Acción**

            1. Abre **Checks** o pulsa **Details** junto a la validación.
            2. Si está verde, confirma qué reglas ejecutó.
            3. Si está roja, abre el paso fallido, identifica el archivo y corrige en la misma rama.

            | La automatización puede comprobar | Una persona debe juzgar |
            |---|---|
            | existen los dos archivos | el proceso se parece al trabajo real |
            | no quedan marcadores `COMPLETAR` | el indicador representa una mejora valiosa |
            | las tablas y diagramas conservan estructura | la arquitectura responde al problema |
            | no aparecen secretos evidentes | los límites y la interpretación son responsables |

            **Importante:** verde significa “pasaron estas reglas”, no “la respuesta es correcta”.
            """
        ),
        md(
            """
            ## Paso 10 — Detenerse antes de integrar

            No pulses **Merge pull request** hasta recibir la indicación docente. El PR abierto ya es una entrega
            revisable. El docente puede comentar y la pareja puede responder con una nueva corrección en la misma rama.

            **Resultado final esperado**

            - dos documentos completos y coherentes;
            - una rama distinta de `main`;
            - un PR con explicación y límites;
            - una pregunta sustantiva del compañero;
            - una corrección relacionada con esa pregunta;
            - CI verde o un error comprendido y documentado.

            La cantidad de commits, líneas o publicaciones no determina la nota.
            """
        ),
        md(
            """
            ## Criterios de calidad del ejercicio

            | Pregunta de revisión | Evidencia mínima |
            |---|---|
            | ¿la decisión está clara? | usuario, acción e indicador |
            | ¿el proceso explica la demora? | cuello, retrabajo y dato producido |
            | ¿el caso de uso evita comenzar por tecnología? | evidencia, salida, acción y límite |
            | ¿el veredicto BI / Big Data está sustentado? | necesidad actual y condición para reevaluar |
            | ¿la arquitectura conecta las partes? | cuatro dominios relacionados con el objetivo |
            | ¿el ciclo termina en acción? | responsable y nuevo dato registrado |
            | ¿la revisión produjo aprendizaje? | objeción, corrección y explicación |

            **Tiempo de contingencia.** Si GitHub Actions se demora, conserva el PR y explica qué comprobarías. Si
            una cuenta no puede acceder, la pareja puede trabajar en una sola cuenta durante la clase y registrar la
            revisión oral; después se repetirá el flujo con acceso individual.
            """
        ),
        md(
            """
            ## Ticket de salida

            Responde en tres frases:

            1. ¿Qué decisión apoya Compras Claras?
            2. ¿Por qué BI tradicional es suficiente para el primer hito?
            3. ¿Qué parte puede comprobar CI y qué parte exige juicio humano?
            """
        ),
        md(
            """
            ---
            # Cierre de la sesión

            ## Recapitulación

            1. **BPM** permitió localizar el trabajo, la espera y el retrabajo.
            2. El **caso de uso** conectó persona, evidencia, decisión, acción e indicador.
            3. La comparación **BI / Big Data** evitó añadir complejidad sin una necesidad medida.
            4. La **arquitectura empresarial** alineó negocio, información, aplicaciones y tecnología.
            5. El **ciclo analítico** llevó los datos hasta una acción que produce nueva evidencia.
            6. **GitHub** conservó propuesta, pregunta y corrección sin convertirse en el objetivo de la clase.

            **Idea principal.** Una iniciativa de Big Data tiene sentido cuando mejora una decisión dentro de un
            proceso y puede explicar cómo la evidencia llega a una persona responsable.

            **Próxima sesión.** En la sesión 4 estudiaremos formalmente OLTP, OLAP, Data Marts, Data Warehouses, Data
            Lakes y ETL. Esos sistemas se conectarán con el blueprint construido hoy.
            """
        ),
        md(
            """
            ## Diccionario de variables y términos clave

            | Término | Significado en esta sesión |
            |---|---|
            | AS-IS | forma actual de trabajar |
            | TO-BE | forma propuesta de trabajar |
            | BI | prácticas para organizar indicadores, análisis y reportes que apoyan decisiones |
            | BPM | disciplina para comprender y mejorar procesos de principio a fin |
            | compuerta o *gateway* | punto que dirige el proceso según una condición |
            | SLA | tiempo o nivel esperado del servicio |
            | KPI | indicador que mide lo que realmente ocurrió |
            | NIST | organismo cuyo marco usamos para organizar las cinco etapas analíticas |
            | rama | espacio separado para preparar una propuesta |
            | commit | versión guardada con una explicación breve |
            | Pull Request o PR | conversación para comparar, revisar y corregir una propuesta |
            | CI o *Checks* | comprobaciones automáticas sobre reglas observables |
            | data steward | responsabilidad de aclarar el significado y las reglas de calidad de los datos |

            **Ejemplo:** si el equipo acuerda un SLA de “revisar en máximo 24 horas”, el KPI mide cuánto tardó
            realmente cada caso. La tarea valida las fechas; la compuerta usa ese resultado para decidir si el caso
            continúa o vuelve a corrección.
            """
        ),
        md(
            f"""
            ## Referencias

            - [NIST Big Data Reference Architecture](https://doi.org/10.6028/NIST.SP.1500-6r2)
            - [BPMN 2.0.2 — Object Management Group](https://www.omg.org/spec/BPMN/)
            - [TOGAF Standard — The Open Group](https://publications.opengroup.org/standards/togaf)
            - [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)
            - [Editar archivos en GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
            - [Crear un Pull Request](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)
            - [Página web del curso]({WEB_CURSO})

            La muestra local permite repetir el ejercicio aunque la fuente externa cambie. Una actualización futura
            debe registrar fuente, fecha de corte, campos y límites.
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
