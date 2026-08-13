# -*- coding: utf-8 -*-
"""Genera la sesión 2 sobre negocio, roles, arquitectura y ciclo analítico."""

from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.make_notebook import code, md, save, validate


OUTPUT = "Cuadernos/2_Definiciones_gcp.ipynb"
WEB_CURSO = "https://jazaineam1.github.io/BigData2026/"
COLAB = (
    "https://colab.research.google.com/github/jazaineam1/BigData2026/"
    "blob/main/Cuadernos/2_Definiciones_gcp.ipynb"
)
DIAGRAMS = "../assets/diagrams/session2"
GIT_CAPTURES = "../assets/session2/git"
TOTAL_QUESTIONS = 14


def hidden(cell, title, *tags):
    """Pliega código de soporte en Colab, manteniendo visible su resultado."""
    source = "".join(cell["source"])
    if not source.startswith("#@title"):
        source = f'#@title {title} {{ display-mode: "form" }}\n' + source
        cell["source"] = [line + "\n" for line in source.split("\n")[:-1]] + [source.split("\n")[-1]]
    cell["metadata"]["tags"] = list(tags or ("hide-input",))
    cell["metadata"]["jupyter"] = {"source_hidden": True}
    cell["metadata"]["cellView"] = "form"
    cell["metadata"]["colab"] = {"formView": "both"}
    return cell


def question_cell(numero, tema, contexto, pregunta, opciones, correcta, retro_opciones):
    """Crea una pregunta visual con retroalimentación específica por distractor."""
    if len(opciones) != 4 or len(retro_opciones) != 4:
        raise ValueError("Cada pregunta debe tener cuatro opciones y cuatro retroalimentaciones.")
    return hidden(
        code(
            f"""
            # Pregunta {numero} de {TOTAL_QUESTIONS} — {tema}
            pregunta_interactiva(
                numero={numero},
                tema={tema!r},
                contexto={contexto!r},
                pregunta={pregunta!r},
                opciones={opciones!r},
                correcta={correcta},
                retro_opciones={retro_opciones!r},
            )
            """
        ),
        f"Activar pregunta {numero} — {tema}",
        "hide-input",
        "pregunta-interactiva",
    )


def diagram(name, alt, width=980):
    """Inserta PNG compatible con Colab y enlaza el SVG para ampliación."""
    return (
        f'<div align="center"><a href="{DIAGRAMS}/{name}.svg" target="_blank">'
        f'<img src="{DIAGRAMS}/{name}.png" width="{width}" alt="{alt}"></a></div>'
    )


def git_diagram(name, alt, width=920):
    """Inserta PNG compatible con Colab y enlaza el SVG para ampliación."""
    return (
        f'<div align="center"><a href="{GIT_CAPTURES}/{name}.svg" target="_blank">'
        f'<img src="{GIT_CAPTURES}/{name}.png" width="{width}" alt="{alt}"></a></div>'
    )


def bash_commands(text):
    """Presenta comandos opcionales de profundización sin ejecutarlos en Colab."""
    return md(
        "<details>\n"
        "<summary><strong>Profundización opcional: ver equivalencia en terminal</strong></summary>\n\n"
        "Estos comandos no son requisito de la sesión ni se evalúan de memoria.\n\n"
        "```bash\n" + text.strip() + "\n```\n"
        "</details>"
    )


def build_cells():
    cells = [
        md(
            f"""
            <a href="{COLAB}" target="_parent">
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir el cuaderno en Google Colab">
            </a>

            **Acceso público:** [página del curso]({WEB_CURSO})

            > **Antes de comenzar en Colab:** selecciona **Entorno de ejecución → Ejecutar todas**. Verás las
            > preguntas, sus opciones y la retroalimentación; el código técnico queda plegado porque no es parte
            > del aprendizaje de esta sesión. Los comandos de Git y del perfilador sí permanecerán visibles.

            > El docente compartirá únicamente el enlace del repositorio privado asignado a cada pareja. Esta
            > actividad usa GitHub Free y no requiere servicios pagos. No necesitas crear cuentas de
            > nube, tarjetas, claves, tokens ni cuentas de servicio.
            """
        ),
        md(
            """
            # Sesión 2 — De la necesidad empresarial al caso de uso de Big Data

            > **Ubicación en el curso:** este cuaderno corresponde **únicamente a la Sesión 2**. Los números que
            > aparecen en los títulos siguientes identifican bloques de esta misma clase; no son sesiones nuevas.

            ## Universidad Central
            <div align="center">
              <img src="https://universidad.ucentral.edu.co/tulengua/wp-content/themes/tulengua/images/logo-ucentral.png"
                   width="340" alt="Logo de la Universidad Central">
            </div>

            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 2

            **Temas:** motivaciones de adopción · arquitectura empresarial · BPM · ciclo analítico · casos de uso · BI tradicional y Big Data<br>
            **Caso:** Compras Claras — seguimiento de contratación pública con SECOP<br>
            **Duración:** 180 minutos — 90 de explicación y 90 de práctica<br>
            **Modalidad:** aprender haciendo, en parejas y con GitHub desde el navegador<br>
            **Última actualización:** 13 de agosto de 2026

            ## Ficha de la sesión

            | Campo | Definición |
            |---|---|
            | Pregunta profesional | ¿Qué procesos contractuales deberían revisarse primero? |
            | Responsable | analista de seguimiento con validación del director |
            | Fuente | SECOP Integrado; muestra local reproducible y API opcional |
            | Entorno | Colab para la clase; GitHub.com para colaborar sin depender de Git instalado |
            | Producto | dos artefactos enlazados: decisión/proceso y caso/arquitectura/acción |
            """
        ),
        md(
            """
            ## Objetivos de aprendizaje y alcance

            Al finalizar podrás:

            1. formular una motivación empresarial, una decisión, un responsable y un KPI antes de proponer tecnología;
            2. evaluar preparación para adoptar Big Data mediante valor, datos, proceso, personas, riesgo y viabilidad;
            3. distinguir proceso, tarea, procedimiento y proyecto, y representar un AS-IS con elementos BPMN;
            4. diferenciar arquitectura empresarial, arquitectura de datos y arquitectura técnica;
            5. aplicar captura, preparación, análisis, visualización y acción al caso SECOP;
            6. formular un caso de uso de su entorno laboral y distinguir cuándo basta BI tradicional y cuándo se
               justifican capacidades Big Data;
            7. elegir capacidades tecnológicas según el problema y no por popularidad del producto;
            8. explicar cómo rama, commit, Pull Request, revisión y CI pueden conservar la conversación entre roles;
            9. comunicar límites: una alerta descriptiva prioriza revisión, pero no prueba causalidad ni irregularidad.

            **Producto de la sesión:** el primer hito del proyecto semestral: blueprint de Compras Claras y ficha de
            transferencia a un caso laboral. Cada decisión queda explicada, revisada y reproducible; no se elegirá
            una plataforma Big Data sin demostrar primero por qué la organización la necesita.
            """
        ),
        md(
            """
            ## Propósito del hilo: convertir una operación en una decisión confiable

            Esta sesión no busca memorizar una lista de siglas. Busca responder una pregunta más útil:

            > ¿Cómo pasa un hecho registrado durante la contratación a convertirse en evidencia que una analista
            > puede usar, explicar y devolver al proceso como una acción?

            El orden de la clase sigue el viaje real de esa evidencia:

            1. **La decisión** define para qué necesitamos información y qué KPI permitirá evaluar la mejora.
            2. **La motivación y la preparación** comprueban si Big Data responde a una necesidad o solo a una moda.
            3. **El proceso BPM** muestra quién trabaja, dónde se decide y en qué actividad nace cada dato.
            4. **El caso de uso** conecta usuario, decisión, evidencia, acción y valor verificable.
            5. **BI tradicional frente a Big Data** se decide por requisitos, no por prestigio de la herramienta.
            6. **La arquitectura y el ciclo NIST** asignan capacidades, controles y responsables de extremo a extremo.
            7. **Los roles conversan** sobre el blueprint; Git y GitHub permiten conservar propuesta, objeción,
               corrección y validación sin convertir los comandos en el objetivo de aprendizaje.

            **Punto de partida.** No se presupone experiencia previa en Bash, Git, nube o contenedores. El flujo
            principal se realiza en GitHub.com. Los estados internos de Git y la terminal aparecen solo como
            profundización opcional. El razonamiento estadístico se aprovecha para interpretar evidencia, no para
            saltar pasos de arquitectura.
            """
        ),
        md(
            """
            ## Agenda: una historia empresarial integrada

            ### Primeros 90 minutos — comprender el sistema

            | Minutos | Pregunta que conduce el bloque | Resultado |
            |---:|---|---|
            | 0–8 | ¿Qué debe decidir la analista y cómo sabrá si mejora? | responsable, alcance y KPI |
            | 8–20 | ¿Por qué adoptar Big Data y qué debe estar preparado? | motivación, valor, viabilidad y riesgos |
            | 20–37 | ¿Qué ocurre hoy y quién responde por cada parte? | proceso AS-IS, roles, datos y cuello de botella |
            | 37–50 | ¿Qué caso de uso existe y basta la BI actual? | ficha del caso y decisión de suficiencia |
            | 50–65 | ¿Cómo se alinean todas las piezas? | arquitectura empresarial TO-BE |
            | 65–77 | ¿Cómo recorre la evidencia el ciclo analítico? | cinco etapas de NIST |
            | 77–84 | ¿Qué capacidades y herramientas son proporcionales? | alternativas justificadas |
            | 84–90 | ¿Cómo conversan los roles sin perder lo acordado? | Git/GitHub como puente de colaboración |

            ### Últimos 90 minutos — construir evidencia

            | Minutos | Actividad | Evidencia observable |
            |---:|---|---|
            | 90–98 | Abrir el repositorio y reconocer artefactos | archivos y roles temporales identificados |
            | 98–118 | Analizar decisión, evidencia, proceso y KPI | primer artefacto argumentado |
            | 118–138 | Formular caso y veredicto BI/Big Data | suficiencia sustentada con requisitos |
            | 138–153 | Completar arquitectura, NIST y responsabilidades | segundo artefacto coherente |
            | 153–165 | Revisar desde el rol contrario | objeción y corrección justificadas |
            | 165–175 | Observar comentario, cambio y versión en GitHub | conversación conservada en un PR |
            | 175–180 | Ticket de salida | decisión, rol crítico y límite |
            """
        ),
        md(
            """
            ## ¿Por qué importa esta sesión?

            En la sesión anterior reconocimos que Big Data no significa solamente “un archivo grande”. Ahora unimos
            la lógica empresarial con los casos de uso organizacionales: conectar una pregunta con el trabajo que
            produce los datos, comprobar si la organización está preparada y decidir si la BI existente es suficiente.

            Si comenzamos por una herramienta, podemos automatizar un proceso defectuoso o construir un tablero que
            nadie usa. Si comenzamos por decisión, proceso y KPI, cada dato y cada componente puede justificarse.
            Por eso la secuencia de esta clase es deliberada y no una lista intercambiable de definiciones.
            """
        ),
        md(
            """
            ## Un repositorio puede conservar el proyecto y su conversación

            Cuando se definan los equipos, cada grupo tendrá **un repositorio propio** que podrá crecer durante el
            semestre. No es necesario crear una copia nueva por cada actividad: los hitos pueden ampliar la misma
            historia con datos, decisiones, análisis, documentación e implementación.

            Esto no convierte Git en una obligación aislada ni en una prueba de memoria. Aparece porque los roles
            necesitan resolver problemas cotidianos: documentos sobrescritos, versiones enviadas por correo,
            decisiones sin autor, reglas de calidad cambiadas sin revisión y desacuerdos que desaparecen.

            | Elemento | Qué permite conservar | Pregunta profesional que ayuda a responder |
            |---|---|---|
            | `main` | versión integrada que el equipo reconoce como base | ¿sobre qué acuerdo seguimos trabajando? |
            | rama `hito/s02-negocio` | propuesta separada mientras se conversa | ¿qué cambio estamos evaluando sin alterar la base? |
            | commit | una versión identificable con autor y explicación | ¿qué cambió y con qué intención? |
            | Pull Request | propuesta, diferencias, preguntas y correcciones | ¿qué objeciones recibió y cómo se atendieron? |
            | revisión humana | criterio de negocio, dominio, datos, seguridad y arquitectura | ¿la propuesta tiene sentido en el proceso real? |
            | CI | comprobaciones automáticas repetibles | ¿faltan secciones, hay secretos evidentes o falló una regla observable? |

            **Git no decide si la arquitectura es correcta.** Ayuda a reconstruir quién propuso una decisión, qué
            evidencia usó, qué objeción recibió y cómo fue corregida. La cantidad de commits, líneas o publicaciones
            no determina la calidad ni la nota.

            ### ¿Cómo se relaciona con el proyecto del semestre?

            Un hito puede convertirse en la base del siguiente cuando el equipo entiende y acepta sus decisiones.
            La retroalimentación deja de ser un comentario que se pierde: puede provocar una corrección trazable. El
            repositorio es, por tanto, una buena herramienta para conservar el aprendizaje acumulado, no el fin del
            curso.

            > **Situación actual.** Los grupos todavía no están definidos. En esta sesión usaremos roles temporales y
            > un repositorio de práctica. Cuando existan equipos estables, cada grupo decidirá con el docente cómo
            > aplicar este flujo a su proyecto.
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
                print("Python:", sys.version.split()[0])
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
            """
            ---
            # Bloque 1 — La historia comienza con una decisión, no con una herramienta

            Son las 8:00 a. m. La analista de seguimiento recibe cientos de registros contractuales. El director no
            le pide “usar Big Data”; le hace una pregunta operativa: **¿qué procesos debemos revisar primero hoy?**

            La oficina consolida información tarde, encuentra estados incompletos y compara duraciones expresadas
            en unidades distintas. La analista necesita una cola explicable para orientar una revisión humana.

            ### Contrato de decisión

            | Elemento | Definición en Compras Claras | Por qué se define primero |
            |---|---|---|
            | Problema | la revisión comienza tarde y sin criterio reproducible | evita diseñar una solución para un síntoma ambiguo |
            | Responsable | analista de seguimiento; el director aprueba el criterio | aclara quién interpreta y quién decide |
            | Decisión | ordenar casos para revisar, corregir o escalar | delimita qué salida debe producir la analítica |
            | Entradas | fechas, estado, duración, unidad, valor y completitud | determina qué evidencia mínima hace falta |
            | KPI de proceso | tiempo desde actualización hasta priorización | mide si el proceso mejora, no solo si el modelo corre |
            | Salvaguarda | toda alerta requiere revisión humana | evita convertir una señal descriptiva en acusación |

            **Definición formal — decisión soportada por datos.** Elección entre cursos de acción cuyo criterio usa
            evidencia trazable, reglas explícitas y responsabilidad humana.

            **Intuición.** Los datos no “toman” la decisión: reducen el espacio de búsqueda. Es como ordenar una
            bandeja de entrada por urgencia; la clasificación ayuda, pero una persona todavía lee y actúa.

            **Ejemplo manual.** Si hay diez expedientes y solo dos horas, revisar primero los que no tienen fecha de
            actualización o cuya duración no puede compararse es un criterio explicable. No afirma que estén mal.

            **Error frecuente:** comenzar con “hagamos un tablero” sin acordar quién actuará, con qué regla y cómo se
            medirá el efecto.
            """
        ),
        md(
            """
            ## Datos y fuentes del caso

            Trabajaremos con una muestra local de **SECOP Integrado**, derivada del portal Datos Abiertos Colombia.
            La API viva sirve como actualización opcional; la clase no depende de su disponibilidad.

            **Unidad de observación:** un proceso contractual publicado en la fuente consultada. Una fila representa
            un registro disponible, no toda la realidad jurídica u operacional del contrato.

            ### Diccionario de variables

            | Variable | Significado | Papel en Compras Claras | Control necesario |
            |---|---|---|---|
            | `id_del_proceso` | identificador del proceso | trazabilidad y detección de duplicados | no nulo y único según el corte |
            | `entidad` | entidad contratante | responsable y dimensión de análisis | catálogo y texto normalizado |
            | `departamento_entidad` | territorio de la entidad | segmentación descriptiva | valores geográficos consistentes |
            | `modalidad_de_contratacion` | mecanismo contractual | comparación entre grupos | categoría documentada |
            | `estado_del_procedimiento` | estado publicado | seguimiento y reglas de completitud | catálogo y fecha de actualización |
            | `tipo_de_contrato` | naturaleza contractual | contexto de comparaciones | categoría documentada |
            | `fecha_de_publicacion_del` | fecha de publicación | antigüedad y oportunidad | tipo fecha y rango plausible |
            | `duracion` | cantidad declarada | señal descriptiva de tiempo | valor numérico no negativo |
            | `unidad_de_duracion` | días, meses u otra unidad | permite comparar duraciones | conversión con regla trazable |
            | `precio_base` | valor de referencia | contexto económico | moneda, escala y valores faltantes |

            **Interpretación.** Las variables no son “columnas sueltas”: cada una nace en una actividad, tiene un
            responsable y necesita una regla antes de alimentar una prioridad. Precio o duración altos no prueban
            riesgo por sí mismos; requieren contexto, calidad y revisión humana.
            """
        ),
        md(
            f"""
            ## El hilo que seguiremos durante toda la sesión

            {diagram('01_hilo_decision', 'Secuencia de la Sesión 2: decisión, proceso actual, datos, ciclo NIST, acción humana y mejora; roles y Git aparecen como soportes transversales')}

            ### Antes de seguir las flechas

            La imagen contiene **tres tipos de información diferentes**. No deben leerse como una sola lista:

            - las **seis tarjetas numeradas** forman la secuencia principal del caso;
            - la **banda superior** indica que los roles participan durante todo el recorrido, no en un paso aislado;
            - la **banda inferior** indica que Git y GitHub pueden conservar versiones y conversaciones durante los
              seis pasos; no son una etapa del proceso contractual ni deciden si una propuesta es correcta.

            ### Qué significa cada paso y por qué conduce al siguiente

            | Paso | Pregunta que responde | Qué ocurre en Compras Claras | Producto que permite avanzar |
            |---:|---|---|---|
            | 1. Decisión + KPI | ¿qué debemos mejorar y cómo sabremos si funcionó? | Laura necesita priorizar revisiones y se mide el tiempo hasta la primera revisión | propósito, responsable y KPI verificable |
            | 2. Proceso AS-IS | ¿dónde nace la demora? | se reconstruyen actividades, actores, decisiones y consolidación manual | mapa del trabajo actual y cuello de botella |
            | 3. Datos necesarios | ¿qué debemos saber para intervenir ese punto? | se definen estados, fechas, duraciones, significado, calidad y responsables | datos autorizados con reglas de interpretación |
            | 4. Ciclo NIST | ¿cómo convertimos esos datos en evidencia? | se captura, prepara, analiza y visualiza una prioridad explicable | cola candidata con motivos y límites visibles |
            | 5. Acción humana | ¿quién decide y qué hace con la evidencia? | la analista revisa contexto, corrige, escala o descarta y registra el motivo | decisión humana trazable, no acusación automática |
            | 6. Medir y mejorar | ¿la intervención redujo la demora sin crear un riesgo mayor? | se compara el KPI con la línea base y se ajustan proceso y controles TO-BE | aprendizaje, proceso mejorado y una nueva pregunta |

            **Ejemplo completo.** Si la línea base muestra tres días entre actualización y revisión, el proceso AS-IS
            ayuda a localizar la consolidación manual. Los campos de SECOP permiten construir una cola diaria con
            motivos visibles. Laura revisa cada caso y registra el resultado. Solo entonces se compara el nuevo tiempo
            con la línea base para decidir si la solución se mantiene, se corrige o se detiene.

            **Qué no significa la imagen.** Los roles no trabajan uno después de otro; acompañan los pasos donde su
            responsabilidad es necesaria. Git tampoco produce la prioridad: conserva qué se propuso, quién objetó,
            qué cambió y qué versión fue revisada. El ciclo NIST apoya una acción humana, no una decisión automática.

            **Conclusión.** La arquitectura es defendible cuando cada componente puede señalar la decisión, el proceso,
            el dato, el responsable y el KPI que justifican su existencia.

            **Limitación y conexión.** Este primer mapa muestra la lógica general, pero todavía no detalla cada tarea
            contractual. Primero comprobaremos si existe una motivación y preparación reales; después abriremos el
            proceso AS-IS actividad por actividad.
            """
        ),
        question_cell(
            1,
            "Decisión y KPI",
            "La directora propone medir el éxito por la cantidad de tecnologías instaladas.",
            "¿Qué medida responde mejor al problema empresarial?",
            [
                "Número de servicios de nube activados.",
                "Cantidad total de columnas descargadas.",
                "Tiempo entre la actualización del registro y su priorización para revisión.",
                "Número de gráficos creados por la analista.",
            ],
            2,
            [
                "Cuenta infraestructura, pero no demuestra que Compras Claras acelere la revisión.",
                "Más columnas pueden aumentar ruido y riesgo; no miden una mejora del proceso.",
                "Este KPI enlaza el problema —consolidación tardía— con la decisión y permite comparar antes y después.",
                "Un gráfico es un artefacto intermedio. El valor aparece cuando la evidencia llega a tiempo a la decisión.",
            ],
        ),
        md(
            """
            ---
            # Bloque 2 — Motivaciones y planificación de la adopción de Big Data

            ## ¿Por qué una organización decide adoptar nuevas capacidades analíticas?

            Este sigue siendo un bloque de la **Sesión 2**. El programa asigna dos lecturas del libro para prepararlo:
            *Business Motivations and Drivers for Big Data Adoption* explica la motivación empresarial y *Big Data
            Adoption and Planning Considerations* explica la preparación para adoptar. En la bibliografía se conserva
            la numeración editorial del libro, pero **este cuaderno y todas sus actividades pertenecen solamente a la
            Sesión 2 del curso**.

            Ambas lecturas separan dos decisiones que suelen confundirse: **tener una motivación empresarial** y
            **estar preparado para adoptar**. Un problema importante no garantiza que la organización disponga de
            datos, responsables, gobierno, habilidades, presupuesto o un proceso capaz de usar el resultado.

            **Definición formal — motivación empresarial.** Presión, oportunidad u objetivo verificable que justifica
            cambiar la manera en que una organización decide o ejecuta un proceso.

            **Intuición.** “Queremos usar Big Data” describe una tecnología deseada. “Necesitamos priorizar revisiones
            antes de 24 horas y hoy tardamos tres días” describe una brecha que puede medirse.

            **Ejemplo manual.** Una clínica que recibe un informe mensual puede operar con BI convencional. Si debe
            detectar deterioro en minutos a partir de señales continuas y texto clínico, aparecen requisitos de
            velocidad, variedad, confiabilidad y operación que deben evaluarse antes de escalar.

            ### Seis preguntas de preparación

            | Dimensión | Pregunta de adopción | Evidencia mínima en Compras Claras | Riesgo si se omite |
            |---|---|---|---|
            | valor | ¿qué decisión o resultado mejora? | reducir tiempo de priorización | proyecto sin usuario ni beneficio |
            | datos | ¿existen, significan lo mismo y pueden usarse? | SECOP, diccionario, fecha de corte y calidad | conclusiones sobre datos ambiguos |
            | proceso | ¿dónde vuelve el resultado como acción? | revisión, corrección o escalamiento | tablero sin respuesta operacional |
            | personas | ¿quién patrocina, interpreta, opera y responde? | director, analista y responsables de captura | solución sin propiedad |
            | riesgo y gobierno | ¿qué límites, acceso y trazabilidad se exigen? | revisión humana, minimización y linaje | daño, exposición o acusaciones indebidas |
            | viabilidad | ¿qué capacidad, costo y plazo son proporcionales? | lote diario y muestra reproducible | sobrediseño y costo sin valor |

            **Aplicación SECOP.** La disponibilidad de una API es una condición técnica, no la motivación. La
            motivación es priorizar mejor; el plan debe validar datos, proceso, responsables, controles y una ruta
            incremental que pueda detenerse si la evidencia no demuestra valor.

            **Error frecuente:** convertir la adopción en una compra irreversible. Una prueba acotada debe producir
            aprendizaje y criterios de continuar, ajustar o detener.
            """
        ),
        md(
            """
            ## Del problema a una decisión de adopción, sin añadir otra lámina

            Usa la tabla anterior como una lista de comprobación en este orden:

            1. **Demostrar la brecha:** línea base, decisión afectada, responsable y KPI.
            2. **Comprobar preparación:** datos, proceso, personas, gobierno y viabilidad.
            3. **Elegir una intervención proporcional:** mejorar la capacidad actual, experimentar de forma acotada
               o detener el caso si el riesgo supera el valor esperado.
            4. **Registrar la evidencia faltante:** no convertir una promesa comercial en una decisión de adopción.

            **Aplicación.** Compras Claras no necesita comenzar comprando una plataforma. Puede probar con una muestra
            local, una regla explicable y el KPI de tiempo hasta primera revisión. Si la evidencia demuestra que esa
            alternativa incumple el SLA, entonces se justifica estudiar una capacidad mayor.

            **Conclusión y conexión.** Adoptar es una decisión de portafolio basada en evidencia. Si la motivación es
            válida, BPM permite localizar en qué trabajo real nace la demora y dónde debe incorporarse la respuesta
            analítica.
            """
        ),
        question_cell(
            2,
            "Motivación empresarial",
            "La organización propone comprar una plataforma porque otras entidades ya la usan.",
            "¿Qué evidencia convertiría esa idea en una motivación empresarial defendible?",
            [
                "Una lista más larga de productos populares.",
                "Una brecha medible entre el desempeño actual y una decisión prioritaria, con responsable y KPI.",
                "El número de publicaciones que mencionan Big Data.",
                "La promesa de que cualquier dato producirá valor automáticamente.",
            ],
            1,
            [
                "Popularidad no demuestra que el producto resuelva una brecha propia ni que el proceso pueda usarlo.",
                "La brecha, el responsable y el KPI permiten verificar valor antes y después de una intervención.",
                "Las publicaciones pueden orientar una exploración, pero no definen el resultado de negocio esperado.",
                "El valor depende de significado, proceso, acción y control; acumular datos no lo produce por sí solo.",
            ],
        ),
        question_cell(
            3,
            "Preparación para adoptar",
            "Compras Claras tiene datos y presupuesto, pero nadie está autorizado para revisar o atender las alertas.",
            "¿Cuál es la principal brecha de preparación?",
            [
                "Falta aumentar el volumen de datos.",
                "Falta definir proceso, responsable y acción para usar el resultado.",
                "Falta cambiar inmediatamente a streaming.",
                "Falta ocultar la limitación en la presentación.",
            ],
            1,
            [
                "Más volumen no crea autoridad ni un mecanismo de atención; puede agravar el problema.",
                "Sin propietario y acción, la analítica termina en una visualización sin efecto operacional.",
                "La latencia solo se justifica desde el tiempo disponible para decidir; no resuelve la falta de responsable.",
                "Una adopción responsable hace visibles sus límites y usa esa evidencia para ajustar el plan.",
            ],
        ),
        md(
            """
            ---
            # Bloque 3 — BPM: comprender el trabajo antes de automatizarlo

            ## ¿Por qué aparece BPM ahora?

            Ya sabemos qué decisión mejorar. Aún no sabemos **qué trabajo produce la información**, dónde se valida
            ni por qué llega tarde. La administración de procesos de negocio —BPM— aporta ese mapa.

            **Definición formal.** BPM es una disciplina de gestión que identifica, modela, analiza, mejora, ejecuta
            y monitorea procesos de extremo a extremo para alcanzar resultados organizacionales medibles.

            **Intuición.** Si la arquitectura es el plano de la organización, el proceso es la película: muestra
            quién hace qué, en qué orden, con qué entrada, qué decisión cambia la ruta y qué resultado entrega.

            ### Conceptos que no son equivalentes

            | Concepto | Qué representa | Ejemplo del caso |
            |---|---|---|
            | Tarea | unidad de trabajo concreta | validar que una fecha tenga formato correcto |
            | Procedimiento | instrucciones para ejecutar una tarea | pasos y regla usados para validar la fecha |
            | Proceso | conjunto de actividades de extremo a extremo | desde reportar ejecución hasta priorizar revisión |
            | Proyecto | esfuerzo temporal para cambiar algo | implementar la primera versión de Compras Claras |

            **Ciclo BPM.** Descubrir → modelar → analizar → rediseñar → implementar → monitorear. Después de medir,
            el ciclo vuelve a comenzar. Automatizar corresponde a una parte; mejorar exige comprobar el resultado.

            ### Elementos mínimos para leer el proceso

            | Elemento | Símbolo habitual | Qué representa | Qué no representa |
            |---|---|---|---|
            | Evento | círculo | algo que inicia, termina o afecta el flujo, como “se recibió un reporte” | una actividad ejecutada por una persona |
            | Tarea | rectángulo con bordes redondeados | trabajo concreto con entrada y salida, como validar una fecha | todo el proceso de extremo a extremo |
            | Gateway o compuerta | rombo | punto de control que divide o reúne rutas según una regla | una persona, una base de datos o el trabajo de validar |
            | Flujo de secuencia | flecha continua | orden permitido entre eventos, tareas y gateways | transferencia automática de datos entre sistemas |
            | Carril | banda horizontal o vertical | participante o responsabilidad que ejecuta tareas | una etapa cronológica obligatoria |

            ### ¿Qué es exactamente un gateway?

            **Definición formal.** En BPMN, un gateway —o compuerta— controla cómo el flujo se divide o se reúne. En
            este cuaderno usamos un **gateway exclusivo**: evalúa condiciones y permite continuar por una sola ruta.

            **Intuición.** Es un cruce con una regla explícita. El rombo no “hace” la validación y tampoco toma una
            decisión por sí mismo. Una tarea o un responsable produce la información; el gateway representa qué ruta
            sigue el caso de acuerdo con el resultado.

            **Ejemplo pequeño.** En un reembolso, la tarea “validar soportes” produce `completos` o `incompletos`.
            Después aparece el gateway “¿soportes completos?”:

            - **Sí:** el caso continúa hacia aprobar y pagar.
            - **No:** se solicita corrección y el caso espera nuevos soportes.

            **Aplicación a Compras Claras.** La oficina consolida el registro y después evalúa “¿fechas y campos
            completos?”. La ruta **Sí** conduce a priorizar. La ruta **No** solicita corrección y regresa a reportar
            ejecución. Para que la decisión sea reproducible, “completo” debe convertirse en reglas observables, por
            ejemplo: campos obligatorios presentes, fechas interpretables y unidad de duración reconocida.

            **Regla de diseño.** Las condiciones de salida deben ser claras, mutuamente excluyentes y cubrir todos los
            resultados esperados. Si se cumplen simultáneamente o no existe ruta para un caso, el flujo es ambiguo.

            ### SLA y KPI no son lo mismo

            - **SLA:** objetivo o compromiso de servicio. Ejemplo: priorizar cada registro completo en máximo 24 horas.
            - **KPI:** medición del desempeño real. Ejemplo: porcentaje priorizado antes de 24 horas y tiempo mediano
              hasta primera revisión.

            El SLA fija el límite esperado; el KPI permite comprobar si el proceso realmente lo cumple.

            **Error frecuente:** dibujar únicamente el camino feliz y ocultar rechazos, correcciones y esperas. Esos
            desvíos suelen explicar el cuello de botella. Otro error es escribir una pregunta dentro de un rombo sin
            definir las condiciones de sus flechas de salida.
            """
        ),
        question_cell(
            4,
            "Proceso frente a tarea",
            "Una persona comprueba que la fecha final sea posterior a la inicial.",
            "¿Cómo se clasifica esa acción?",
            [
                "Como todo el proceso contractual.",
                "Como una tarea de validación dentro del proceso.",
                "Como un proyecto de transformación empresarial.",
                "Como una arquitectura técnica.",
            ],
            1,
            [
                "El proceso incluye varias actividades, actores, decisiones y un resultado de extremo a extremo.",
                "La comprobación tiene una entrada, una regla y una salida concreta; por eso es una tarea.",
                "Un proyecto es temporal y busca producir un cambio; esta validación ocurre en la operación cotidiana.",
                "La arquitectura técnica describe infraestructura y ejecución, no una acción puntual del negocio.",
            ],
        ),
        md(
            f"""
            ## Proceso AS-IS: lo que ocurre hoy

            {diagram('02_proceso_as_is', 'Proceso AS-IS de contratación con carriles, gateway, retrabajo y cuello de botella')}

            ### Cómo leer esta imagen sin perderse

            1. **Empieza por los carriles horizontales.** Cada carril representa quién responde por una parte del
               trabajo: la entidad contratante origina y actualiza; SECOP registra y publica; la oficina de seguimiento
               consolida, prioriza y revisa. Un carril no es una tecnología: es una frontera de responsabilidad.
            2. **Sigue los números 1 a 13.** Los pasos 1–5 describen el proceso contractual resumido; 6–8 muestran lo
               que hace la plataforma con el registro; 9–13 muestran el trabajo posterior de seguimiento.
            3. **Lee las cápsulas dentro o junto a las tareas.** Nombran el dato que deja cada actividad. Por ejemplo,
               “Reportar ejecución” produce estado y fechas; SECOP conserva ese evento y luego lo expone.
            4. **Observa el rombo del paso 11.** Es una decisión: “¿fechas y campos completos?”. La ruta verde permite
               priorizar; la ruta roja solicita corrección y obliga a esperar un nuevo reporte. Ese regreso es retrabajo.
            5. **Ubica el contorno rojo discontinuo.** No acusa a una persona: señala una hipótesis de cuello de
               botella en “Consolidar”, donde se unen y limpian descargas desarticuladas.
            6. **Termina en los KPI inferiores.** Tiempo de consolidación mide la demora; porcentaje de datos completos
               mide calidad; casos priorizados mide cobertura. Ninguno, por sí solo, demuestra que la revisión sea correcta.

            ### Ejemplo de un registro que recorre el proceso

            Un supervisor informa que un contrato continúa “en ejecución” y registra una fecha. SECOP guarda y publica
            el registro. La oficina lo descarga junto con otros cortes. Si la fecha está vacía o la unidad de duración
            es ambigua, la consolidación no puede compararlo de forma confiable: el caso vuelve para corrección. Si los
            campos son suficientes, entra en una lista preliminar; aun así, una persona revisa el contexto antes de actuar.

            **Qué demuestra.** El retraso aparece después de la operación, cuando la oficina descarga, une, valida y
            vuelve a solicitar datos. Por eso no conviene empezar seleccionando un algoritmo.

            **Qué no demuestra.** Es una representación pedagógica simplificada, no el procedimiento normativo completo,
            no asigna culpa y no es un modelo BPMN ejecutable. El dueño del proceso y el experto de dominio deben validar
            que los pasos, excepciones y SLA correspondan a la realidad.

            **Conexión.** Cada actividad deja una huella. Ahora convertiremos el flujo en una tabla que conecte actor,
            entrada, dato, validación, salida, herramienta posible y KPI.
            """
        ),
        md(
            """
            ## Trazabilidad actividad por actividad

            | Paso | Actor | Entrada | Actividad | Dato producido | Validación | Salida | Problema AS-IS | Herramienta posible | KPI |
            |---:|---|---|---|---|---|---|---|---|---|
            | 1 | área solicitante | necesidad y presupuesto | definir necesidad | objeto, monto, responsable | aprobación y disponibilidad | solicitud aprobada | texto ambiguo | gestor documental / ERP | tiempo de aprobación |
            | 2 | equipo contractual | solicitud aprobada | preparar y publicar | modalidad, cronograma, requisitos | campos obligatorios | proceso publicado | campos incompletos | SECOP / Socrata | % publicaciones completas |
            | 3 | comité evaluador | ofertas | evaluar | puntajes, observaciones, decisión | regla de evaluación | proveedor recomendado | criterios dispersos | SECOP + expediente | tiempo de evaluación |
            | 4 | ordenador y jurídico | recomendación | formalizar | contrato, fechas, valor, proveedor | firmas y coherencia | contrato vigente | fechas inconsistentes | SECOP / sistema contractual | % contratos validados |
            | 5 | supervisor | contrato y evidencias | reportar ejecución | avance, estado, novedades | unidad, periodo y soporte | registro actualizado | reporte tardío | formulario / SECOP | oportunidad del reporte |
            | 6 | plataforma | actualización | persistir y publicar | versión del registro | esquema y reglas básicas | dato consultable | calidad heterogénea | API Socrata / sistema fuente | disponibilidad y completitud |
            | 7 | analista | archivos o API | consolidar y priorizar | perfil, reglas y cola | calidad y reproducibilidad | casos ordenados | unión manual y tardía | Python / análisis descriptivo | tiempo hasta priorización |
            | 8 | director y analista | cola explicable | revisar y actuar | comentario, corrección o escalamiento | evidencia humana | decisión registrada | retroalimentación no trazada | gestor de casos | % casos revisados a tiempo |

            **Cómo se interpreta.** Una fila conecta negocio y dato. Por ejemplo, `estado` no es una columna que
            “aparece” en el CSV: nace cuando el supervisor reporta, se valida con una regla y se consume después.

            **Qué no podemos concluir todavía.** La tabla propone herramientas posibles; no confirma que SECOP use
            internamente una base específica ni reemplaza el levantamiento con la entidad.
            """
        ),
        question_cell(
            5,
            "Gateway y retrabajo",
            "El registro puede estar completo o debe regresar al supervisor para corrección.",
            "¿Qué elemento representa mejor esa bifurcación?",
            [
                "Una tarea adicional llamada decidir.",
                "Un evento de inicio.",
                "Un gateway con condiciones explícitas de salida.",
                "Un repositorio de datos.",
            ],
            2,
            [
                "Una tarea ejecuta trabajo; la bifurcación necesita condiciones explícitas y rutas mutuamente excluyentes.",
                "El evento de inicio indica cuándo comienza el flujo, no cómo cambia de ruta.",
                "El gateway hace visible la regla: completo continúa; incompleto genera retrabajo y vuelve al reporte.",
                "Un repositorio conserva datos, pero no representa una decisión ni las rutas del proceso BPM.",
            ],
        ),
        question_cell(
            6,
            "KPI de proceso",
            "El cuello de botella es descargar y unir archivos manualmente antes de priorizar.",
            "¿Qué KPI ayuda a verificar una mejora TO-BE?",
            [
                "Cantidad de logos en el diagrama.",
                "Tiempo desde el último reporte hasta la cola priorizada.",
                "Número de filas sin considerar la fecha de actualización.",
                "Precisión de una acusación automática de fraude.",
            ],
            1,
            [
                "La apariencia no mide desempeño operacional ni valor para la analista.",
                "Compara directamente la demora AS-IS con el flujo mejorado y puede medirse antes y después.",
                "El volumen aporta contexto, pero no demuestra que la priorización llegue más rápido.",
                "Compras Claras no acusa ni demuestra fraude; prioriza revisión humana con señales descriptivas.",
            ],
        ),
        md(
            """
            ## Los roles aparecen porque el proceso cruza varias responsabilidades

            Hasta aquí hablamos de “la organización” como si fuera una sola persona. El AS-IS demuestra lo
            contrario: quien define valor, quien produce el dato, quien gobierna su significado, quien construye el
            flujo y quien usa la evidencia no necesariamente son la misma persona.

            Un **rol** es un conjunto de responsabilidades y decisiones; no siempre coincide con un cargo. En una
            organización pequeña, una persona puede asumir varios roles. Lo importante es que ninguna responsabilidad
            crítica quede implícita.

            ### Roles de negocio: definen valor y acción

            | Rol | Pregunta que responde | Artefacto o decisión en Compras Claras |
            |---|---|---|
            | patrocinador | ¿por qué invertir y qué bloqueo debe removerse? | valor esperado y continuidad del caso |
            | dueño del proceso | ¿qué resultado, KPI y SLA deben mejorar? | prioridad, criterio de aceptación y acción posterior |
            | Product Owner analítico | ¿qué necesidad se atiende primero? | orden de evolución del producto analítico |
            | analista de negocio | ¿cómo se traduce el problema en proceso y reglas? | AS-IS, requerimientos y criterios verificables |
            | experto de dominio | ¿qué excepciones cambian la interpretación? | validación contractual de reglas y límites |
            | usuario de la evidencia | ¿la salida permite decidir y actuar? | revisión de la cola y registro de respuesta |

            ### Arquitectura y gobierno: organizan y protegen el significado

            | Rol | Pregunta que responde | Distinción clave |
            |---|---|---|
            | arquitecto empresarial | ¿cómo se alinean estrategia, proceso, información, aplicaciones y tecnología? | no diseña solo infraestructura |
            | arquitecto de solución | ¿qué componentes integrables materializan el TO-BE? | traduce el blueprint a una solución coherente |
            | arquitecto de datos | ¿cómo se organizan, integran y evolucionan fuentes, modelos y linaje? | diseña; no opera por sí solo todos los flujos |
            | data owner | ¿quién autoriza usos y responde institucionalmente por el dato? | propiedad y riesgo institucional |
            | data steward | ¿qué significa el dato y qué regla mantiene su calidad? | definiciones, metadatos y excepciones |
            | seguridad y privacidad | ¿quién puede acceder y qué debe minimizarse? | controles, separación de funciones y exposición |
            | cumplimiento o auditoría | ¿puede reconstruirse la decisión y su evidencia? | trazabilidad y conformidad |

            ### Construcción y análisis: producen capacidades y evidencia

            | Rol | Responsabilidad principal | No debe confundirse con... |
            |---|---|---|
            | ingeniero de datos | implementar captura, preparación, pruebas y observabilidad | arquitecto de datos, que define organización y evolución |
            | analytics engineer | producir modelos analíticos documentados y reutilizables | analista BI, que interpreta y comunica métricas |
            | analista de datos o BI | explicar qué ocurrió con métricas gobernadas | científico de datos, que diseña experimentos o modelos |
            | científico de datos | formular hipótesis, experimentos o modelos cuando el caso lo justifica | requisito automático de todo proyecto de datos |
            | ingeniero de software | integrar capacidades analíticas con aplicaciones y procesos | responsable del significado del dato |
            | ML engineer/MLOps | operacionalizar y monitorear modelos | necesario para este primer hito descriptivo |
            | plataforma, DevOps o SRE | automatizar operación, recuperación, monitoreo y costos | dueño de la decisión empresarial |
            | responsable de calidad | comprobar datos, código, artefactos y criterios | sustituto del experto de dominio |

            **Relevo clave.** El arquitecto de datos define qué debe significar y cómo debe evolucionar una entidad;
            el ingeniero de datos implementa y opera su recorrido; el data steward verifica que significado y reglas
            sigan vigentes; el analista BI usa el resultado para explicar el proceso. Si hace falta un modelo, el
            científico de datos entra después de demostrar que una regla o análisis descriptivo no basta.

            **Error frecuente:** contratar una herramienta o un científico de datos antes de asignar dueño del
            proceso, experto de dominio y responsable de la acción. Un modelo no repara responsabilidades ausentes.
            """
        ),
        md(
            """
            ## Matriz RACI compacta de Compras Claras

            RACI hace explícito quién **R**ealiza el trabajo, quién **A**prueba o responde finalmente, a quién se
            **C**onsulta y a quién se **I**nforma. No describe jerarquía completa; aclara un relevo concreto.

            | Decisión o artefacto | A | R | C | I |
            |---|---|---|---|---|
            | problema, KPI y SLA | dueño del proceso | analista de negocio | patrocinador, usuario | equipo técnico |
            | proceso AS-IS y excepciones | dueño del proceso | analista de negocio | experto de dominio, usuario | arquitectos |
            | definiciones y reglas de calidad | data owner | data steward | arquitecto e ingeniero de datos | analista BI |
            | arquitectura TO-BE | patrocinador / dueño del proceso | arquitecto empresarial | solución, datos, seguridad, plataforma | equipo analítico |
            | captura y preparación | arquitecto de solución | ingeniero de datos | steward, seguridad, calidad | dueño del proceso |
            | métricas e interpretación | dueño del proceso | analista BI | experto de dominio, steward | patrocinador |
            | revisión y acción contractual | dueño del proceso | usuario de la evidencia | experto de dominio, cumplimiento | equipo de datos |

            **Cómo leer una fila.** En “definiciones y reglas de calidad”, el data steward realiza el trabajo
            semántico; el data owner responde por la decisión institucional; arquitectura e ingeniería son
            consultadas para asegurar que la regla sea implementable; BI necesita conocer el resultado.

            **Limitación.** Esta matriz es una hipótesis docente. En una entidad real debe validarse con estructura,
            competencias y segregación de funciones. El siguiente bloque convierte estas responsabilidades en un
            caso de uso que pueda evaluarse.
            """
        ),
        md(
            """
            ---
            # Bloque 4 — Casos de uso de Big Data en las organizaciones

            El AS-IS ya mostró una demora concreta. Ahora debemos convertirla en un caso de uso que otra persona
            pueda evaluar sin depender de una lista de productos.

            **Definición formal — caso de uso analítico.** Descripción verificable de un usuario que emplea evidencia
            para tomar una decisión o ejecutar una acción dentro de un proceso, bajo restricciones y métricas claras.

            **Intuición.** “Analizar contratos” es demasiado amplio. “Cada mañana, la analista ordena registros para
            revisar primero los que tienen problemas de calidad explicables” permite identificar usuario, momento,
            entrada, salida, acción y valor.

            ### Anatomía mínima del caso

            | Elemento | Pregunta | Compras Claras |
            |---|---|---|
            | usuario | ¿quién consume la evidencia? | analista de seguimiento |
            | decisión | ¿qué elige o prioriza? | qué procesos revisar primero |
            | frecuencia | ¿cada cuánto debe decidir? | cada mañana o después del corte diario |
            | evidencia | ¿qué datos y calidad necesita? | estados, fechas, duración, unidad y completitud |
            | salida | ¿qué recibe y con qué explicación? | lista priorizada con motivo trazable |
            | acción | ¿qué hace después? | revisar, corregir, escalar o descartar la alerta |
            | KPI | ¿cómo sabremos que aporta valor? | tiempo hasta revisión y cobertura dentro del SLA |
            | límite | ¿qué no puede afirmar? | causalidad, fraude o irregularidad |

            **Ejemplo pequeño.** Un restaurante que revisa ventas mensuales por sede tiene un caso de reporte. Si debe
            ajustar abastecimiento durante el día con pedidos, clima y entregas, el caso agrega nuevas restricciones;
            todavía debe demostrar que esa latencia cambia una decisión antes de llamarlo Big Data.

            **Error frecuente:** formular el caso como “implementar Spark” o “crear un dashboard”. Esos son candidatos
            técnicos; el caso debe existir aunque la herramienta cambie.
            """
        ),
        md(
            """
            ## Familias organizacionales: el verbo importa más que el sector

            | Familia | Pregunta típica | Salida | Ejemplo organizacional | Riesgo frecuente |
            |---|---|---|---|---|
            | describir | ¿qué ocurrió y dónde? | KPI, tendencia o segmentación | contratación por modalidad y periodo | confundir asociación con causa |
            | diagnosticar | ¿qué patrón merece investigación? | hipótesis y evidencia relacionada | demoras concentradas en una etapa | acusar sin contexto |
            | predecir | ¿qué podría ocurrir? | probabilidad o pronóstico | demanda, abandono o mantenimiento | usar datos históricos sin vigilar cambio |
            | recomendar | ¿qué alternativa conviene primero? | ranking o siguiente acción | cola de revisión explicable | automatizar una decisión sensible |
            | detectar | ¿qué evento requiere atención? | alerta con motivo y severidad | anomalía de calidad o seguridad | saturar al usuario con falsos positivos |
            | optimizar | ¿cómo asignar recursos bajo restricciones? | plan o combinación factible | turnos, rutas o capacidad | ocultar restricciones humanas |

            **Aplicación.** Compras Claras combina describir, detectar y recomendar: perfila calidad, identifica señales
            y propone un orden de revisión. No predice culpabilidad ni optimiza automáticamente una sanción.

            **Interpretación.** La familia ayuda a elegir evidencia, método y métrica. Un mismo sector puede contener
            varios casos; decir “Big Data en salud” o “Big Data en gobierno” todavía no define ninguno.
            """
        ),
        question_cell(
            7,
            "Formulación del caso de uso",
            "Un equipo escribe como caso de uso: implementar una plataforma de streaming para contratación.",
            "¿Qué reformulación permite evaluar valor antes de elegir tecnología?",
            [
                "Instalar más productos para descubrir después quién los usará.",
                "Definir usuario, decisión, frecuencia, evidencia, acción, KPI y límite del caso.",
                "Cambiar streaming por inteligencia artificial sin modificar el problema.",
                "Llamar estratégico al proyecto y omitir el proceso actual.",
            ],
            1,
            [
                "La plataforma seguiría sin decisión, usuario ni resultado verificable y aumentaría el riesgo de sobrediseño.",
                "Estos elementos convierten la idea en un caso evaluable y permiten comparar alternativas técnicas.",
                "Cambiar la etiqueta tecnológica no corrige la falta de propósito ni de criterio de éxito.",
                "La importancia declarada no sustituye evidencia sobre el trabajo, el responsable y el valor esperado.",
            ],
        ),
        md(
            """
            ---
            ## BI tradicional y BI apoyada por capacidades Big Data

            La inteligencia de negocios —BI— organiza datos, métricas y visualizaciones para comprender el desempeño
            y apoyar decisiones. “Tradicional” no significa inútil: un reporte periódico con datos estructurados,
            definiciones gobernadas y una decisión clara puede ser la solución correcta.

            **Definición formal — BI tradicional.** Capacidades de integración, modelado, consulta y visualización
            orientadas principalmente a datos estructurados, métricas acordadas y análisis descriptivo o diagnóstico
            con latencias compatibles con reportes periódicos.

            **Definición formal — BI con capacidades Big Data.** Extensión del ecosistema analítico cuando variedad,
            velocidad, escala, complejidad o tipos de análisis exceden de forma demostrable la solución actual y
            requieren nuevas capacidades de cómputo, almacenamiento, procesamiento u operación.

            **Intuición.** Big Data no reemplaza automáticamente la BI. Amplía el conjunto de fuentes, tiempos y
            métodos posibles. La pregunta correcta es: ¿qué requisito no puede cumplir de manera confiable y
            sostenible la solución actual?

            | Criterio | BI tradicional puede ser suficiente | Se justifican capacidades Big Data cuando... |
            |---|---|---|
            | decisión | KPI, seguimiento y exploración periódica | la decisión necesita señales más diversas, frecuentes o complejas |
            | datos | fuentes estructuradas y definiciones estables | texto, eventos, sensores, imágenes o múltiples fuentes cambian el análisis |
            | latencia | horas, días o cierre mensual | segundos o minutos modifican una acción real y medible |
            | escala | el volumen cumple SLA y costo en la plataforma actual | una sola máquina o arquitectura no cumple tiempo, concurrencia o retención |
            | método | agregación, segmentación y diagnóstico | se necesitan procesamiento distribuido, búsqueda, grafos o modelos a escala |
            | operación | actualización controlada y equipo existente | fallos, particiones, reintentos y observabilidad exigen operación adicional |
            | gobierno | métricas y acceso gobernados | aumenta la superficie de riesgo, linaje, privacidad y costo |

            ### Veredicto inicial para Compras Claras

            Con una muestra pequeña, actualización diaria y reglas descriptivas, **BI tradicional más Python es
            suficiente para el primer hito**. No necesitamos streaming ni procesamiento distribuido para demostrar
            la trazabilidad decisión–dato–acción.

            Reabriríamos la decisión si aparecen, por ejemplo, millones de eventos, documentos y texto que deban
            analizarse juntos; una latencia de minutos que cambie el proceso; muchos usuarios concurrentes; o una
            medición que demuestre que la solución actual incumple capacidad, tiempo o costo.

            **Error frecuente:** considerar “BI tradicional” como fracaso y “Big Data” como madurez. La madurez está
            en elegir la alternativa suficiente, gobernarla y definir cuándo debe escalar.

            ### Matriz de suficiencia para argumentar, no adivinar

            Cada equipo registrará el estado actual, el requisito futuro y una evidencia observable:

            | Restricción | Estado actual | Umbral que obligaría a cambiar | Evidencia por recolectar |
            |---|---|---|---|
            | tiempo para decidir | lote diario | una demora superior al SLA afecta la acción | marcas de tiempo y casos no atendidos |
            | volumen y concurrencia | una máquina cumple el ejercicio | tiempo o memoria incumplen el objetivo | filas, bytes, duración y usuarios simultáneos |
            | variedad | campos estructurados de SECOP | texto o documentos aportan una señal necesaria | inventario, formato, calidad y permiso |
            | confiabilidad | muestra local y ejecución manual guiada | operación repetida exige recuperación automática | tasa de fallos, reintentos y pérdida tolerable |
            | riesgo y costo | datos minimizados y entorno gratuito | nuevas fuentes amplían acceso, retención o gasto | clasificación, controles y estimación |

            **Comentario docente.** La columna “umbral” evita frases vagas como “cuando haya muchos datos”. Una
            arquitectura evoluciona cuando una medición demuestra que la capacidad actual dejó de ser suficiente.

            **Reserva curricular.** En la sesión 4 estudiaremos formalmente OLTP, OLAP, Data Marts, Data Warehouses,
            Data Lakes y ETL. Aquí solo nombramos capacidades genéricas para no adelantar sus definiciones ni su
            implementación.
            """
        ),
        md(
            """
            ## De la pregunta al veredicto de suficiencia

            No necesitamos otra imagen para tomar esta decisión. Usa la matriz anterior y redacta el veredicto con
            cuatro afirmaciones comprobables:

            1. **Situación actual:** qué datos llegan, con qué frecuencia y cuánto tarda la respuesta.
            2. **Capacidad suficiente hoy:** qué solución cumple el SLA con un costo y una operación razonables.
            3. **Umbral de cambio:** qué medición demostraría que esa solución dejó de ser suficiente.
            4. **Evidencia pendiente:** volumen, latencia, variedad, tasa de fallos, riesgo o costo que todavía debe medirse.

            **Veredicto para Compras Claras.** Un lote diario, Python y una salida de BI gobernada son suficientes para
            el primer hito porque la fuente es estructurada y la decisión tolera 24 horas. Se estudiarían capacidades
            Big Data si una medición muestra que el volumen, la latencia, la variedad o la confiabilidad incumplen el SLA.

            **Qué no podemos concluir todavía.** Este veredicto no selecciona proveedor, presupuesto o arquitectura
            física. Tampoco afirma que BI sea inferior: el diseño responsable comienza por la alternativa suficiente y
            conserva umbrales para evolucionar.

            **Conexión.** Con el caso y el nivel de capacidad definidos, la arquitectura empresarial puede alinear
            negocio, información, aplicaciones y tecnología sin adelantar los sistemas de la sesión 4.
            """
        ),
        question_cell(
            8,
            "BI tradicional frente a Big Data",
            "La oficina recibe un archivo estructurado al día, una máquina lo procesa en minutos y la decisión tolera 24 horas.",
            "¿Cuál es el veredicto más responsable para el primer hito?",
            [
                "Streaming distribuido obligatorio porque el curso se llama Big Data.",
                "BI gobernada y procesamiento simple son suficientes; se documentan umbrales para escalar.",
                "No medir nada hasta comprar una plataforma empresarial.",
                "Declarar que cualquier archivo diario ya es Big Data.",
            ],
            1,
            [
                "La solución agregaría costo y operación sin un requisito de latencia, volumen o variedad que la justifique.",
                "El diseño satisface la decisión actual y convierte una futura evolución en una respuesta a evidencia medible.",
                "La compra no sustituye una línea base; sin medición no puede demostrarse insuficiencia ni valor.",
                "La frecuencia del archivo por sí sola no define una necesidad Big Data ni la capacidad requerida.",
            ],
        ),
        question_cell(
            9,
            "Umbral para escalar",
            "El equipo afirma que en el futuro habrá muchos datos, pero no registra volumen, tiempo de proceso ni usuarios.",
            "¿Qué debe agregar a su blueprint?",
            [
                "Una promesa general de escalabilidad ilimitada.",
                "Umbrales medibles de latencia, capacidad, variedad, concurrencia, riesgo y costo.",
                "Más logotipos de proveedores.",
                "Una conclusión causal a partir del perfil descriptivo.",
            ],
            1,
            [
                "Sin umbral no existe una condición comprobable para cambiar de arquitectura ni estimar inversión.",
                "Los umbrales convierten la evolución en una decisión verificable y enlazada con el SLA del proceso.",
                "Los productos solo pueden compararse después de conocer el requisito que deben cumplir.",
                "El perfil describe la muestra; no demuestra causas y tampoco define requisitos de infraestructura.",
            ],
        ),
        md(
            """
            ---
            # Bloque 5 — Arquitectura empresarial: alinear lo que ya comprendimos

            ## ¿Por qué definirla en este punto?

            Ahora conocemos la motivación, la decisión, el proceso, los datos, el caso de uso y el nivel de capacidad
            requerido. La arquitectura empresarial organiza esas piezas y comprueba que ninguna tecnología quede
            huérfana de propósito.

            **Definición formal.** Conjunto coherente de principios, modelos y decisiones que describe cómo negocio,
            información, aplicaciones y tecnología se relacionan para lograr objetivos y evolucionar de un estado
            AS-IS a uno TO-BE.

            **Intuición.** Es el plano de una ciudad, no una lista de edificios. Muestra rutas, responsabilidades,
            restricciones y cómo un cambio en una zona afecta a las demás.

            **Ejemplo manual.** Una tienda quiere responder reclamos en 12 horas. Negocio define el SLA; información
            define cliente, caso y estado; aplicaciones reciben, enrutan y notifican; tecnología ejecuta y monitorea.

            **Aplicación SECOP.** El objetivo es priorizar; el proceso produce estados y fechas; las aplicaciones
            capturan, perfilan y presentan; la tecnología conecta, ejecuta y observa; gobierno controla acceso y linaje.

            **Error frecuente:** dibujar logos primero y añadir el objetivo al final.
            """
        ),
        md(
            """
            ## Cuatro dominios que responden preguntas distintas

            | Dominio | Pregunta de diseño | Evidencia en Compras Claras |
            |---|---|---|
            | Negocio | ¿qué objetivo, decisión, proceso y responsable mejoran? | priorización y revisión humana |
            | Información | ¿qué entidades, significados, reglas y calidad se requieren? | contrato, entidad, estado, fecha, duración y linaje |
            | Aplicaciones | ¿qué capacidades manipulan y entregan información? | fuente, ingesta, perfilador, reglas, tablero y alertas |
            | Tecnología | ¿dónde se almacena, procesa, conecta y observa? | API, objetos/Parquet, motor analítico, CI y monitoreo |

            **Cómo se relacionan.** Negocio define para qué y para quién; información define qué debe significar el
            dato; aplicaciones definen qué capacidades lo capturan, transforman y entregan; tecnología define dónde y
            bajo qué condiciones operan esas capacidades. Una decisión en una fila impone requisitos a las demás.

            **Distinción importante.** Arquitectura empresarial contiene los cuatro dominios. Arquitectura de datos
            profundiza fuentes, modelos, contratos, flujos, calidad y linaje dentro de ese conjunto. Arquitectura
            técnica profundiza cómputo, red, almacenamiento, despliegue y operación. No son nombres intercambiables.

            **Apoyo de lectura.** Esta tabla permite comparar los dominios antes de ver el diseño aplicado. Primero
            domina las cuatro preguntas; después usa la arquitectura TO-BE para comprobar cómo se conectan en el caso.
            """
        ),
        md(
            f"""
            ## Arquitectura objetivo TO-BE de Compras Claras

            {diagram('05_arquitectura_to_be', 'Arquitectura TO-BE con cuatro dominios y controles transversales')}

            ### Cómo leerla de arriba hacia abajo

            | Zona de la imagen | Qué significa | Ejemplo aplicado | Pregunta de control |
            |---|---|---|---|
            | Banda superior | controles que atraviesan todos los dominios | acceso mínimo, linaje del snapshot, monitoreo del perfil y costo operativo | ¿quién controla y qué evidencia deja? |
            | 1. Negocio | propósito, proceso, responsable y KPI | priorizar revisión; dueño del proceso; tiempo y cobertura | ¿la salida cambia una acción real? |
            | 2. Información | fuentes, entidades, significado y reglas | SECOP, contrato, entidad, fecha, duración y definición mantenida por el steward | ¿dos roles interpretan igual el campo? |
            | 3. Aplicaciones | capacidades que integran, validan, analizan y entregan | perfilador, reglas explicables, reporte y registro de respuesta | ¿qué capacidad transforma la información? |
            | 4. Tecnología | mecanismos donde esas capacidades se ejecutan | API/archivos, almacenamiento, Pandas o Spark según medición y operación observable | ¿cumple SLA, seguridad, recuperación y costo? |

            ### La columna numerada muestra una traza completa

            1. La **decisión** de priorizar define qué información hace falta.
            2. Las **fuentes** entregan los campos con los que puede construirse la evidencia.
            3. La **integración** captura y prepara esos campos de forma reproducible.
            4. La **conectividad** permite leerlos sin convertir un producto comercial en el propósito del diseño.

            Las demás tarjetas no son pasos posteriores: amplían cada dominio. Por ejemplo, “Calidad” y “Analítica”
            son capacidades de aplicación que dependen de reglas semánticas y deben entregar una salida comprensible
            al usuario. La franja roja inferior recuerda que TO-BE no significa automatizar la decisión humana.

            **Conclusión.** La cola priorizada solo tiene valor si existe responsable, dato con significado, aplicación
            explicable, tecnología sostenible y controles transversales. Si una tarjeta técnica no puede señalar la
            decisión o el KPI que la justifica, probablemente sobra o está ubicada demasiado pronto.

            **Limitación.** Es arquitectura lógica: todavía no fija volúmenes, latencia, proveedor, presupuesto ni
            acuerdos institucionales. Esas restricciones se documentan antes de implementar.

            **Conexión.** La arquitectura muestra qué debe existir; el ciclo NIST mostrará cómo un dato recorre esas
            capacidades, se convierte en evidencia y regresa al proceso como una acción.
            """
        ),
        question_cell(
            10,
            "Trazabilidad arquitectónica",
            "El equipo propone Kafka porque es popular, pero no ha definido latencia ni eventos.",
            "¿Qué debe hacer antes de seleccionarlo?",
            [
                "Instalarlo y buscar un problema después.",
                "Definir decisión, proceso, volumen, velocidad, confiabilidad y capacidad requerida.",
                "Reemplazar BPM por una lista de productos.",
                "Ocultar el costo para no limitar el diseño.",
            ],
            1,
            [
                "La tecnología quedaría sin requisito verificable y aumentaría complejidad operacional.",
                "Esas restricciones permiten decidir si hacen falta eventos o si una actualización programada es suficiente.",
                "BPM explica el trabajo; una lista de productos no representa actores, reglas ni retrabajo.",
                "Costo es una preocupación transversal y puede cambiar una alternativa técnicamente válida.",
            ],
        ),
        md(
            """
            ---
            # Bloque 6 — Ciclo analítico de Big Data: del dato a una acción responsable

            ## ¿Por qué no terminamos en una arquitectura o un tablero?

            Diseñar componentes o mostrar datos no mejora por sí solo una decisión. El ciclo analítico describe el
            movimiento de la evidencia hasta una acción y su retroalimentación. Usaremos el modelo NIST: **captura, preparación, análisis,
            visualización y acción**.

            ### Tres ciclos que conviene diferenciar

            | Ciclo | Pregunta central | Alcance |
            |---|---|---|
            | ciclo de vida del dato | ¿cómo se crea, conserva, usa y retira el dato? | gobierno y permanencia |
            | ciclo analítico NIST | ¿cómo se transforma evidencia en acción? | flujo analítico de extremo a extremo |
            | CRISP-DM | ¿cómo se organiza un proyecto de minería de datos? | negocio, datos, modelado, evaluación y despliegue |

            No compiten: se superponen desde perspectivas distintas. En esta sesión NIST es la columna vertebral;
            CRISP-DM sirve como referencia para proyectos de modelado posteriores.
            """
        ),
        md(
            f"""
            ## Las cinco etapas aplicadas

            {diagram('06_ciclo_nist', 'Ciclo NIST aplicado a captura, preparación, análisis, visualización y acción')}

            | Etapa | Entrada | Actividad Compras Claras | Responsable | Artefacto | Control | Métrica de éxito |
            |---|---|---|---|---|---|---|
            | Captura | API o muestra SECOP | registrar fuente, fecha, campos y límite | ingeniero de datos; data owner autoriza | snapshot reproducible | acceso y procedencia | extracción completa según contrato |
            | Preparación | snapshot crudo | tipar, revisar nulos, fechas, duplicados y unidades | ingeniero de datos + data steward | tabla preparada + excepciones | regla y linaje | % filas válidas y excepciones contadas |
            | Análisis | datos preparados | perfilar duraciones y reglas de prioridad | analista BI/datos + experto de dominio | métricas y cola candidata | sesgo y reproducibilidad | cobertura de reglas explicables |
            | Visualización | resultados | presentar razón de prioridad, filtros y calidad | analista BI + usuario | tablero o reporte | accesibilidad y contexto | tiempo para comprender un caso |
            | Acción | cola explicable | revisar, corregir, escalar o descartar alerta | usuario; dueño del proceso responde | decisión registrada | separación de funciones | % casos atendidos en SLA |

            ### Cómo leer el ciclo paso a paso

            1. **Captura:** copia una evidencia identificable. “Snapshot + metadatos” significa conservar registros,
               fecha de corte, fuente, campos y límites para poder repetir el análisis.
            2. **Preparación:** convierte datos crudos en datos interpretables. Tipar una fecha, unificar unidades y
               separar excepciones no crea un hallazgo; evita comparar valores incompatibles.
            3. **Análisis:** aplica perfiles o reglas descriptivas. La salida es una cola candidata con motivos, no una
               sentencia sobre el contrato ni una prueba de irregularidad.
            4. **Visualización:** entrega contexto al usuario: razón de prioridad, filtros, calidad y límites. Su salida
               debe permitir comprender por qué un caso aparece antes que otro.
            5. **Acción:** una persona autorizada revisa contexto, corrige, escala o descarta y registra el resultado.
               La flecha de regreso indica que esa decisión genera un nuevo dato y una nueva pregunta para el proceso.

            **Elementos que no son etapas.** La pregunta central —“¿qué contrato revisar primero y por qué?”— mantiene
            el propósito visible. La banda superior —gobierno, seguridad, privacidad, calidad y trazabilidad— impone
            condiciones a las cinco etapas; no se ejecuta una sola vez al final. Las cápsulas sobre las flechas nombran
            el artefacto que una etapa entrega a la siguiente: datos crudos, preparados, alertas con motivos, evidencia
            priorizada y decisión registrada.

            **Ejemplo de lectura.** Un registro con duración `12` no debe llegar directamente al tablero. Captura
            conserva el valor y su fuente; preparación comprueba si la unidad es días o meses; análisis aplica la regla
            acordada; visualización muestra valor, unidad y motivo; acción permite que Laura revise el contexto. Sin esa
            cadena, “12” puede parecer preciso y aun así inducir una comparación equivocada.

            **Conclusión.** Visualizar no es actuar. Una gráfica se vuelve útil cuando alguien tiene autoridad,
            criterio y canal para registrar la respuesta.

            **Limitación.** El ciclo no prescribe un algoritmo ni un proveedor y no elimina la necesidad de validar
            el proceso, los datos y el impacto.

            **Conexión.** Con las responsabilidades claras, podemos comparar herramientas reales por capacidad.
            """
        ),
        question_cell(
            11,
            "Orden del ciclo NIST",
            "La oficina quiere mostrar un tablero antes de verificar fechas, unidades y nulos.",
            "¿Cuál secuencia conserva mejor la lógica del ciclo?",
            [
                "Visualizar → actuar → capturar → preparar → analizar.",
                "Capturar → preparar → analizar → visualizar → actuar.",
                "Analizar → comprar tecnología → capturar → actuar → preparar.",
                "Capturar → visualizar → acusar → cerrar.",
            ],
            1,
            [
                "Comienza por una representación sin evidencia preparada y puede hacer visible un error como si fuera hallazgo.",
                "La secuencia preserva procedencia, calidad, interpretación y una acción humana trazable.",
                "Comprar tecnología no es una etapa analítica y analizar antes de capturar/preparar rompe trazabilidad.",
                "El ciclo no incluye acusación automática; una señal descriptiva requiere revisión humana.",
            ],
        ),
        question_cell(
            12,
            "Visualización y acción",
            "El tablero muestra cinco registros incompletos, pero nadie tiene asignada la revisión.",
            "¿Qué falta para cerrar el ciclo analítico?",
            [
                "Cambiar los colores del tablero.",
                "Agregar más gráficos sin responsable.",
                "Asignar responsable, regla de atención, SLA y registro de la decisión.",
                "Declarar que los cinco casos son irregulares.",
            ],
            2,
            [
                "El diseño visual puede ayudar a leer, pero no crea capacidad de respuesta.",
                "Más visualización no sustituye gobernanza ni una acción definida.",
                "Estos elementos convierten la señal en trabajo trazable y permiten medir si el proceso mejora.",
                "La incompletitud es una señal de calidad, no prueba de irregularidad o causalidad.",
            ],
        ),
        md(
            """
            ---
            # Bloque 7 — Capacidades y herramientas reales en un flujo empresarial

            Una arquitectura no debe casarse prematuramente con un proveedor. Primero nombra la capacidad; luego
            compara opciones por volumen, velocidad, costo, conocimiento del equipo, seguridad y operación.

            | Capacidad | Pregunta que debe responder | Herramientas reales como ejemplo | Evidencia antes de escalar |
            |---|---|---|---|
            | acceder a evidencia | ¿podemos obtener datos autorizados y reproducibles? | SECOP/Socrata, API, archivos, formularios | fuente, permiso, frecuencia y contrato de campos |
            | perfilar calidad | ¿qué tan completos y consistentes son? | Python, Pandas, DuckDB | nulos, tipos, duplicados, unidades y excepciones |
            | analizar | ¿qué patrón o regla apoya la decisión? | SQL, Python; Spark cuando la medición lo exige | tiempo, memoria, volumen y reproducibilidad |
            | consumir BI | ¿cómo comprende el usuario KPI, tendencia y contexto? | Power BI, Looker, Tableau | usuario, métrica, frecuencia y acción posterior |
            | construir una aplicación | ¿la decisión necesita interacción o flujo propio? | Streamlit, aplicaciones web | tarea, permisos, registro de respuesta y SLA |
            | colaborar y revisar | ¿cómo se explican y aprueban los cambios? | Git, GitHub, Pull Requests | autor, diff, comentario, validación y versión |
            | automatizar | ¿la repetición y recuperación justifican orquestación? | GitHub Actions; Airflow más adelante | dependencia, tasa de fallo, reintento y responsable |

            **Ejemplo de decisión tecnológica.** Para una muestra estable y una clase de tres horas, Python,
            Pandas/DuckDB, Markdown y Git son suficientes. Si una medición demuestra que una máquina no cumple el SLA
            o que nuevas fuentes cambian el caso, se reevalúan capacidades distribuidas. “Big Data” no obliga a usar
            todas las herramientas.

            **Límite de esta sesión.** Nombramos herramientas para reconocer capacidades. La organización técnica de
            OLTP, OLAP, Data Marts, Data Warehouses, Data Lakes y ETL pertenece a la sesión 4.
            """
        ),
        question_cell(
            13,
            "Responsabilidades profesionales",
            "La regla de prioridad usa una fecha cuya definición cambió. El flujo debe corregirse y la métrica debe reinterpretarse.",
            "¿Cuál reparto de responsabilidades conserva mejor el significado y la implementación?",
            [
                "El científico de datos decide solo el significado, modifica producción y aprueba el KPI.",
                "El data steward aclara la definición; el arquitecto de datos evalúa impacto; el ingeniero de datos corrige el flujo; BI reinterpreta la métrica.",
                "El patrocinador cambia el script directamente y omite a los responsables de datos.",
                "El analista BI conserva la métrica anterior para evitar revisar el resultado.",
            ],
            1,
            [
                "Concentrar significado, implementación y aprobación elimina controles y no aprovecha al experto de dominio ni al dueño del proceso.",
                "Correcto: cada rol aporta una responsabilidad distinta y el relevo conserva definición, impacto técnico, operación e interpretación.",
                "El patrocinador justifica valor y remueve bloqueos, pero no sustituye gobierno semántico ni construcción técnica.",
                "Una métrica basada en una definición obsoleta puede ser consistente en código y aun así inducir una decisión equivocada.",
            ],
        ),
        md(
            """
            ---
            # Bloque 8 — Git y GitHub: una conversación que no se pierde

            ## ¿Por qué aparecen después de los roles y del blueprint?

            Negocio definió valor; el dueño del proceso explicó el trabajo; el data steward protegió el significado;
            arquitectura organizó las capacidades; ingeniería preparó la evidencia; BI la convirtió en una salida
            comprensible. El problema siguiente no es comprar otra tecnología:

            > ¿Cómo pueden estos roles construir el mismo proyecto, revisar sus decisiones y conservar por qué cambió
            > la arquitectura?

            Sin un mecanismo compartido aparecen copias como `arquitectura_final_ahora_si_v3`, reglas sobrescritas,
            decisiones sin autor y correcciones que no explican qué objeción resolvieron. Git y GitHub son una buena
            respuesta, no la única, porque combinan versiones identificables con un espacio de revisión.

            **Definición formal.** Git es un sistema distribuido de control de versiones. GitHub aloja repositorios y
            añade colaboración mediante ramas, Pull Requests, revisiones y automatización.

            **Intuición.** Una rama es una propuesta separada; un commit identifica una versión y su intención; un
            Pull Request pone la propuesta sobre la mesa; un comentario formula una objeción; un nuevo commit muestra
            cómo se atendió; CI comprueba reglas observables.

            **Límite esencial.** Git no decide si la arquitectura es correcta. Ayuda a explicar, cuestionar, corregir
            y conservar cómo los roles llegaron a una decisión. La cantidad de commits, líneas o publicaciones no
            mide el valor, la comprensión ni la responsabilidad de una contribución.
            """
        ),
        md(
            """
            ## ¿Qué necesita conservar cada rol?

            | Rol | Evidencia que necesita | Uso posible de GitHub |
            |---|---|---|
            | dueño del proceso | motivo y criterio de aceptación | comentar y aprobar la propuesta |
            | experto de dominio | reglas y excepciones | cuestionar una definición en el PR |
            | arquitecto empresarial | decisiones entre dominios | comparar versiones del blueprint |
            | arquitecto de datos | fuentes, modelos, contratos y linaje | revisar impactos de un cambio |
            | data steward | definiciones y reglas de calidad | pedir correcciones antes de aceptar |
            | ingeniero de datos | scripts, pruebas y configuración | conservar código reproducible y ejecutar CI |
            | analista BI | métricas e interpretación | vincular el resultado con su versión |
            | seguridad y privacidad | controles y exclusiones | detectar exposición o datos innecesarios |
            | plataforma / DevOps | automatización y operación | mostrar fallos tempranos y repetibles |
            | usuario de negocio | comprensión del cambio | confirmar si la salida permite decidir |
            """
        ),
        md(
            """
            ## Ejemplo de Pull Request conceptual

            1. El arquitecto propone una actualización diaria.
            2. El dueño del proceso pregunta de dónde sale el SLA de 24 horas.
            3. El data steward cuestiona el tratamiento de fechas faltantes.
            4. Seguridad solicita retirar identificadores innecesarios.
            5. El ingeniero y el arquitecto corrigen el blueprint.
            6. Un nuevo commit registra la modificación y responde a cada objeción.
            7. El usuario contractual confirma que la salida sigue siendo comprensible.
            8. CI verifica estructura; una persona valida el razonamiento.

            Un comentario útil no dice solamente “está mal”: explica qué decisión, riesgo o criterio resulta afectado.
            """
        ),
        md(
            f"""
            ## Del artefacto a la conversación entre roles

            {diagram('07_estados_git', 'Git y GitHub como conversación entre roles: propuesta, objeciones, corrección, CI y decisión humana')}

            ### Qué significa cada número

            | Paso | Participante principal | Qué sucede | Evidencia que queda |
            |---:|---|---|---|
            | 1. Necesidad | dueño del proceso | propone priorizar cada 24 horas y debe justificar el SLA | criterio de valor y pregunta pendiente |
            | 2. Propuesta | arquitectura | modifica el blueprint en una rama sin cambiar todavía `main` | versión diferenciable y archivos propuestos |
            | 3. Corrección | arquitectura e ingeniería | responden objeciones y cambian la misma rama | nuevo commit relacionado con la conversación |
            | 4. CI asistente | automatización | comprueba estructura, marcadores y secretos evidentes | check reproducible, verde o rojo |
            | 5. Juicio humano | proceso, dominio y seguridad | evalúan si el proceso sirve, el significado es válido y el riesgo es aceptable | aprobación, solicitud de cambios o preguntas abiertas |
            | 6. Acción del usuario | analista de seguimiento | usa la salida, registra resultado y genera nueva evidencia | decisión y retroalimentación para otra versión |

            **Lee después las tres cajas superiores.** No son pasos adicionales: representan preguntas simultáneas
            dentro del Pull Request. El dueño del proceso cuestiona valor y SLA; el data steward y el experto de
            dominio cuestionan significado y faltantes; seguridad cuestiona necesidad y acceso a cada dato.

            **Diferencia entre las herramientas.** Git conserva versiones y diferencias. GitHub aloja esas versiones
            y añade el espacio de conversación. El Pull Request relaciona propuesta, comentarios y correcciones. CI
            ejecuta reglas observables. Ninguno de ellos determina por sí solo si el proceso es realista o la decisión
            es responsable.

            **Sentido de las flechas.** El recorrido sólido va de necesidad a propuesta, conversación, corrección,
            verificación y acción. La flecha de regreso muestra que una acción registrada produce nueva evidencia y
            puede abrir otra conversación; no obliga a crear cambios sin una razón profesional.

            **Conclusión.** El valor no está en mover un archivo por estados técnicos, sino en relacionar una objeción
            profesional con la versión que la resolvió.

            **Limitación.** Un Pull Request conserva conversación, pero no garantiza que las personas correctas hayan
            participado ni que la evidencia sea suficiente.

            **Conexión.** En el laboratorio asumiremos roles temporales y construiremos esa conversación sobre dos
            artefactos conectados.
            """
        ),
        question_cell(
            14,
            "Git como relevo entre roles",
            "El data steward cuestiona fechas faltantes y seguridad pide retirar identificadores; el arquitecto debe corregir la propuesta.",
            "¿Qué práctica aprovecha mejor Git y GitHub en este relevo?",
            [
                "Crear varias copias del archivo y escoger la última por su nombre.",
                "Cerrar los comentarios sin modificar la propuesta para obtener un check verde.",
                "Responder las objeciones, modificar la misma rama y relacionar el nuevo commit con la decisión corregida.",
                "Medir la calidad por cantidad de commits y líneas cambiadas.",
            ],
            2,
            [
                "Las copias separan conversación e historia; no permiten reconstruir qué objeción originó cada cambio.",
                "CI puede estar verde y el razonamiento seguir incompleto; cerrar sin responder elimina la función de la revisión.",
                "Correcto: el PR conserva pregunta, respuesta, diferencia y versión; la aprobación humana evalúa el sentido.",
                "El volumen de actividad es una métrica mecánica y puede premiar cambios innecesarios o fragmentados.",
            ],
        ),
        md(
            """
            ---
            # Bloque 9 — Laboratorio guiado de 90 minutos

            ## Producto y roles temporales

            La pareja construirá dos piezas del mismo argumento:

            - `hitos/s02/01_decision_proceso.md`: motivación, patrocinador, dueño del proceso, decisión, KPI,
              evidencia SECOP, AS-IS, cuello de botella y límites.
            - `hitos/s02/02_caso_arquitectura_accion.md`: caso laboral anonimizado, veredicto BI/Big Data,
              arquitectura TO-BE, ciclo NIST, responsabilidades, RACI, controles y siguiente evidencia necesaria.

            **Estudiante A** asumirá temporalmente analista de negocio y data steward. **Estudiante B** asumirá
            arquitecto de datos y responsable analítico. Durante la revisión intercambiarán perspectivas. Son roles
            pedagógicos, no cargos asignados ni responsabilidades permanentes.

            ### Control de tiempo y criterio de terminación

            | Minutos | Actividad | Evidencia para avanzar |
            |---:|---|---|
            | 90–98 | abrir el repositorio y reconocer artefactos | ambos explican la relación entre los dos archivos |
            | 98–118 | analizar decisión, evidencia, proceso y KPI | el primer artefacto conecta dato, cuello y decisión |
            | 118–138 | formular caso y veredicto BI/Big Data | suficiencia justificada con requisitos |
            | 138–153 | completar arquitectura, NIST y responsabilidades | segundo artefacto coherente |
            | 153–165 | revisar desde el rol contrario | objeción específica y corrección argumentada |
            | 165–175 | observar versión, comentario y CI | conversación reconstruible en GitHub |
            | 175–180 | ticket de salida | decisión, rol crítico y límite |

            **Este laboratorio produce una base reutilizable, no una práctica desechable.** El repositorio es una
            herramienta posible para conservarla y ampliarla durante el semestre. El objetivo conceptual no depende
            de memorizar Git ni de producir una cantidad determinada de commits.

            Si GitHub Actions se demora, la pareja conserva el contenido y revisa el check después. Si no puede
            ejecutar Python, usa el perfil SECOP precomputado: la clase evalúa el razonamiento del diseño, no una
            instalación local.
            """
        ),
        md(
            """
            ## Paso 1 — Abrir el repositorio y reconocer la historia

            **Acción.** Inicia sesión en GitHub.com, abre el repositorio indicado por el docente y verifica el
            propietario antes de editar. En la raíz localiza `hitos/s02/`, `data/`, `resultados/` y `scripts/`.

            **Resultado esperado.** Puedes abrir los dos artefactos y el perfil SECOP; no estás en la plantilla ni
            en el repositorio de otro equipo.

            **Error probable.** Un 404 suele indicar cuenta incorrecta o falta de acceso. No crees un fork público:
            confirma con el docente el nombre de usuario y la URL.
            """
        ),
        bash_commands(
            """
            pwd
            ls
            """
        ),
        md(
            """
            ## Paso 2 — Construir decisión y proceso desde dos responsabilidades

            Estudiante A abre `hitos/s02/01_decision_proceso.md`, pulsa el lápiz de edición y completa los marcadores.
            Estudiante B pregunta si el KPI mide el cuello, si cada dato tiene actividad de origen y si los límites
            impiden acusar fraude o causalidad.

            **Cómo conservar la propuesta.** Al pulsar **Commit changes**, escribe un mensaje que explique la intención
            y selecciona **Create a new branch for this commit and start a pull request**. Usa `hito/s02-negocio`.
            GitHub conserva esa versión sin modificar directamente `main`.

            **Resultado esperado.** El archivo conecta motivación → proceso → dato → evidencia → decisión.

            **Error probable.** Si la rama ya existe, selecciónala antes de confirmar; no crees nombres alternativos
            sin coordinar con la pareja.
            """
        ),
        bash_commands(
            """
            python --version
            git --version
            git status
            git remote -v
            """
        ),
        md(
            """
            **Profundización opcional.** Los comandos plegados comprueban versión, rama y remoto cuando existe Git
            local. El laboratorio principal no depende de esa instalación: en GitHub.com la cuenta autenticada firma
            la versión y el selector de ramas muestra dónde se está trabajando.
            """
        ),
        md(
            """
            ## Paso 3 — Formular el caso, la arquitectura y el regreso a la acción

            Estudiante B cambia a `hito/s02-negocio` y edita
            `hitos/s02/02_caso_arquitectura_accion.md`. Debe comprobar caso, veredicto BI/Big Data, cuatro dominios,
            cinco etapas NIST, RACI, controles y la siguiente evidencia necesaria.

            **Resultado esperado.** La arquitectura puede leerse desde el objetivo hacia la tecnología y desde una
            restricción técnica hacia el proceso. La acción humana produce un registro que retroalimenta el ciclo.
            """
        ),
        bash_commands(
            """
            git config --local user.name "Tu Nombre Completo"
            git config --local user.email "tu-correo-asociado-a-github"
            git config --local --get user.name
            git config --local --get user.email
            git switch -c hito/s02-negocio
            git branch --show-current
            """
        ),
        md(
            """
            **Profundización opcional.** La última línea muestra `hito/s02-negocio`. Si Git responde que la rama ya
            existe, usa `git switch hito/s02-negocio`; no crees nombres alternativos sin avisar a tu pareja.
            """
        ),
        md(
            """
            ## Paso 4 — Revisar desde el rol contrario

            En **Files changed**, cada estudiante revisa el archivo que no lideró. Negocio/steward pregunta por
            significado, evidencia, KPI, excepciones y controles; arquitectura/analítica pregunta por trazabilidad,
            suficiencia, capacidad, etapa y responsable.

            La persona autora corrige en la misma rama y responde: “Se cambió X porque Y; ahora podemos verificar Z”.

            **Comentario insuficiente:** “todo bien”, “me gusta” o “corrige esto” sin explicar el impacto.
            """
        ),
        bash_commands(
            """
            python scripts/perfilar_secop.py
            git status --short
            git diff -- resultados/perfil_secop.md
            """
        ),
        md(
            """
            **Función usada: `git diff`.**

            - Para qué sirve: compara el working tree con la última instantánea.
            - Parámetro usado: ruta del archivo que queremos inspeccionar.
            - Qué devuelve: líneas agregadas y retiradas; todavía no crea historial.
            - Cómo interpretar: verde es contenido propuesto; rojo es contenido removido.

            **Error probable.** Si `perfil_secop.md` sigue con `COMPLETAR`, confirma que ejecutaste el script desde la
            raíz del repositorio y lee el mensaje de error, sin borrar la plantilla manualmente.
            """
        ),
        md(
            """
            ## Paso 5 — Leer el Pull Request como conversación

            La descripción responde qué se propuso, por qué, con qué evidencia, qué objeción se atendió y qué límite
            permanece. **Conversation** conserva preguntas y respuestas; **Files changed** muestra la propuesta;
            **Checks** comunica validaciones automáticas.

            Antes de abrir el PR, prepara esas cinco respuestas en texto. En el paso 7 encontrarás una sola lámina de
            referencia con las zonas que deberás comprobar; no necesitas memorizar la interfaz.
            """
        ),
        bash_commands(
            """
            git status
            git diff --check
            git diff -- hitos/s02/01_decision_proceso.md hitos/s02/02_caso_arquitectura_accion.md
            """
        ),
        md(
            """
            **Resultado esperado.** Solo aparecen los cuatro archivos deliberadamente editados. `git diff --check` no
            imprime nada cuando no encuentra espacios problemáticos. Si ves otro archivo, investiga su origen antes
            de agregarlo.
            """
        ),
        md(
            """
            ## Paso 6 — Distinguir CI de revisión humana

            GitHub Actions puede detectar marcadores sin completar, estructura ausente, errores del perfilador o
            secretos evidentes. No puede decidir si el AS-IS es realista, si el KPI representa valor o si una
            interpretación contractual es válida.

            **Resultado esperado.** La pareja nombra una comprobación automática y un juicio humano indispensable.
            """
        ),
        bash_commands(
            """
            git add hitos/s02/01_decision_proceso.md hitos/s02/02_caso_arquitectura_accion.md
            git status
            git diff --staged
            git commit -m "Formula decisión, proceso y caso de uso"
            git status
            git log --oneline --decorate -3
            """
        ),
        md(
            """
            **Profundización opcional.** En terminal, `git diff --staged` permite leer la instantánea propuesta antes
            de crearla. Un commit equivocado no se usa para castigar: una corrección explicada puede añadir una nueva
            versión y conservar el razonamiento.
            """
        ),
        md(
            """
            ## Profundización opcional — qué ocurre detrás del navegador

            Abre los bloques plegados solo si quieres relacionar la interfaz con Git local. Working tree es el
            contenido editado; staging selecciona la próxima instantánea; commit registra una versión local; push la
            publica. Estos estados no son el criterio conceptual ni un examen de comandos.
            """
        ),
        bash_commands(
            """
            git push -u origin hito/s02-negocio
            """
        ),
        md(
            """
            **Profundización opcional.** Git confirma que la rama local rastrea `origin/hito/s02-negocio`. Un 403
            indica un problema de cuenta o acceso; nunca pegues tokens en archivos, comentarios ni chats.
            """
        ),
        bash_commands(
            """
            git fetch origin
            git switch --track origin/hito/s02-negocio
            git pull --ff-only
            git log --oneline --decorate -3
            """
        ),
        md(
            """
            ### Equivalencia opcional para revisar y publicar los dos artefactos

            Los comandos siguientes muestran cómo una persona con Git instalado observaría diferencias, seleccionaría
            los dos archivos, ejecutaría el validador y publicaría una nueva versión. No se exige reproducirlos.
            """
        ),
        bash_commands(
            """
            git status
            git diff -- hitos/s02/01_decision_proceso.md hitos/s02/02_caso_arquitectura_accion.md
            git add hitos/s02/01_decision_proceso.md hitos/s02/02_caso_arquitectura_accion.md
            git diff --staged
            python scripts/validar_entrega.py
            git commit -m "Relaciona decisión, arquitectura y acción"
            git push
            git log --oneline --decorate -5
            """
        ),
        md(
            """
            **Cómo leerlo.** El validador comprueba estructura observable; el log muestra versiones, pero no demuestra
            por sí solo comprensión ni calidad. Si falla una regla, se corrige el contenido o el validador mediante
            una decisión explicada.
            """
        ),
        md(
            f"""
            ## Paso 7 — Abrir el Pull Request y revisar los artefactos

            En GitHub selecciona **Compare & pull request**. Base: `main`; compare: `hito/s02-negocio`. Completa qué
            se hizo, por qué, cómo se verificó y qué limitaciones conserva. Abre la pestaña **Files changed** y
            confirma que los diagramas editables renderizan y que no quedan marcadores.

            {git_diagram('03_pull_request', 'Esquema conceptual de Pull Request con descripción y archivos revisables')}

            ### Cómo leer la lámina

            1. **Encabezado:** confirma que la base sea `main` y que la propuesta venga de `hito/s02-negocio`. Esta
               relación significa “quiero revisar estos cambios antes de integrarlos”; no significa que ya estén aprobados.
            2. **Descripción:** reconstruye qué se hizo, por qué, cómo se verificó y qué límite permanece. En el ejemplo,
               la prioridad ayuda a revisar, pero no demuestra fraude.
            3. **Pestañas:** `Conversation` contiene preguntas y respuestas; `Commits` identifica versiones; `Checks`
               muestra automatización; `Files changed` permite leer exactamente qué se agregó o retiró.
            4. **Columna derecha:** `Reviewers` indica quién debe emitir juicio; el check comunica el resultado del
               validador; “Files changed: 2” delimita el alcance que debe revisarse.
            5. **Cuatro lecturas laterales:** ramas correctas, propósito reconstruible, diferencia revisable y revisión
               atribuible son condiciones distintas. Un check verde solo cubre una parte de ellas.

            **Nota visual.** Es un esquema conceptual y no una captura de un repositorio estudiantil. La interfaz de
            GitHub puede cambiar de posición, pero las preguntas de revisión permanecen.

            **Resultado esperado.** La pareja puede explicar la propuesta sin depender del nombre del commit, abrir
            `Files changed`, relacionar un comentario con una línea y reconocer qué limitación sigue abierta.

            **Error probable.** Si un diagrama no renderiza, revisa la sintaxis en la vista previa. No lo reemplaces
            por una captura: el artefacto debe continuar editable y revisable.
            """
        ),
        md(
            """
            ## Paso 8 — Revisión argumentada y CI como asistente

            El compañero deja al menos un comentario sustantivo: pregunta por una decisión, señala una ambigüedad o
            propone una mejora verificable. Después abre **Checks** y confirma el validador.

            | CI puede comprobar de forma repetible | Una persona debe juzgar con contexto |
            |---|---|
            | existen los archivos y secciones esperados | el proceso AS-IS refleja el trabajo real |
            | no quedan marcadores como `COMPLETAR` | el cuello de botella está bien sustentado |
            | el perfilador termina y produce estructura válida | el KPI representa valor y no una métrica decorativa |
            | no aparecen secretos evidentes | los datos incluidos son necesarios y su uso es aceptable |
            | el Mermaid cumple sintaxis básica | la arquitectura responde a la decisión y conserva límites |

            **Cómo interpretar el check.** Verde significa que las reglas programadas pasaron en esa versión. No
            significa que el proceso, el KPI o la interpretación sean correctos. Rojo significa que al menos una regla
            observable falló; abre el detalle para identificar archivo, prueba y mensaje antes de corregir.

            **Resultado esperado.** La pareja puede nombrar qué detectó la automatización y qué decisión aún necesita
            al experto de dominio, al dueño del proceso o al docente.

            **Error probable.** Si CI está rojo, abre el detalle, identifica el archivo y corrige en la misma rama.
            Un nuevo push actualiza el PR automáticamente. Si Actions está demorado, conserva la salida verde del
            validador local y revisa CI después.
            """
        ),
        md(
            """
            ## Ticket de salida

            Responde en tres frases:

            1. ¿Qué decisión soporta Compras Claras y qué evidencia la limita?
            2. ¿Qué rol resulta crítico en el siguiente relevo y por qué?
            3. ¿Qué parte puede comprobar CI y qué parte requiere juicio humano?
            """
        ),
        md(
            """
            ## Criterios de calidad del hito

            La evaluación se concentra en el argumento profesional. El historial y la conversación pueden aportar
            evidencia, pero Git no constituye un criterio separado.

            | Criterio | Peso |
            |---|---:|
            | problema, decisión, responsable, KPI y alcance | 15 |
            | proceso AS-IS, datos, cuello de botella y límites | 20 |
            | caso de uso y veredicto BI / Big Data basado en evidencia | 20 |
            | arquitectura objetivo y trazabilidad entre dominios | 20 |
            | ciclo NIST, responsabilidades, RACI y controles | 15 |
            | interpretación, revisión argumentada y límites éticos | 10 |

            **Criterios mínimos de contenido:** los dos artefactos están completos; la evidencia SECOP se interpreta
            sin acusaciones; los roles no se usan como sinónimos; toda capacidad responde a un requisito;
            visualización y acción permanecen diferenciadas; la revisión explica su corrección.

            No se exige una cantidad de commits, pushes o líneas. El docente puede usar la conversación para comprender
            el proceso de trabajo, nunca como contador automático de participación.
            """
        ),
        md(
            """
            ---
            # Cierre de la sesión

            ## Recapitulación

            1. Definimos una motivación, decisión, responsable y KPI antes de elegir tecnología.
            2. Evaluamos valor, datos, proceso, personas, riesgo y viabilidad antes de adoptar.
            3. BPM reveló actividades, datos, gateway, retrabajo y cuello de botella.
            4. El caso de uso conectó usuario, evidencia, acción, KPI y límite.
            5. Comparamos BI tradicional y Big Data mediante requisitos y umbrales medibles.
            6. La arquitectura alineó negocio, información, aplicaciones, tecnología y controles.
            7. NIST llevó la evidencia de captura a acción y retroalimentación.
            8. Git y GitHub mostraron una forma útil de conservar propuestas, objeciones y correcciones entre roles.

            **Idea más importante.** Big Data crea valor cuando una evidencia trazable regresa al proceso como una
            acción responsable. La colección de herramientas es secundaria a esa cadena.

            **Errores que evitaremos:** empezar por productos, llamar Big Data a cualquier reporte, automatizar un
            AS-IS defectuoso, confundir visualización con acción, atribuir causalidad y creer que CI reemplaza la
            revisión profesional.

            ## Próximas sesiones

            > En la sesión 4 estudiaremos formalmente sistemas OLTP y OLAP, Data Marts, Data Warehouses, Data Lakes y
            > ETL. Usaremos el blueprint para explicar cómo se organizan los datos necesarios, sin perder la decisión,
            > el proceso ni los controles definidos hoy.
            """
        ),
        md(
            """
            ## Diccionario de siglas y términos de la Sesión 2

            > **Aclaración rápida:** la sigla correcta es **SLA**, no “SAL”. *Gateway* tampoco es una sigla: es el
            > término inglés para **compuerta**, el rombo que dirige el flujo según condiciones explícitas.

            ### Siglas

            | Sigla | Nombre completo | Significado en palabras sencillas | Uso en Compras Claras |
            |---|---|---|---|
            | API | *Application Programming Interface* — interfaz de programación de aplicaciones | mecanismo para que dos sistemas soliciten o intercambien información mediante reglas definidas | permite consultar registros publicados por SECOP sin descargar manualmente cada archivo |
            | BI | *Business Intelligence* — inteligencia de negocios | prácticas para organizar métricas, consultas y visualizaciones que apoyan decisiones | presenta tiempo de revisión, completitud y cola priorizada con contexto |
            | BPM | *Business Process Management* — gestión de procesos de negocio | disciplina para descubrir, modelar, analizar, mejorar y monitorear procesos | ayuda a localizar la consolidación manual y diseñar el proceso TO-BE |
            | BPMN | *Business Process Model and Notation* | lenguaje visual estandarizado para representar eventos, tareas, compuertas, flujos y responsables | sirve como referencia para leer el AS-IS; la lámina del cuaderno es pedagógica, no un modelo ejecutable completo |
            | CI | *Continuous Integration* — integración continua | ejecución automática de validaciones cada vez que se publica una versión | comprueba estructura, marcadores incompletos y secretos evidentes en el repositorio |
            | CRISP-DM | *Cross-Industry Standard Process for Data Mining* | ciclo para organizar proyectos de minería de datos desde comprensión del negocio hasta despliegue | se menciona como referencia para trabajos de modelado posteriores; no reemplaza el ciclo NIST de esta sesión |
            | CSV | *Comma-Separated Values* — valores separados por comas | archivo de texto tabular donde cada fila es un registro y cada columna una variable | formato de la muestra local y de algunas descargas utilizadas por el perfilador |
            | KPI | *Key Performance Indicator* — indicador clave de desempeño | medida que muestra cómo se está comportando realmente un proceso | tiempo hasta primera revisión, porcentaje dentro del SLA y completitud de datos |
            | NIST | *National Institute of Standards and Technology* | organismo que publica marcos y estándares técnicos; aquí aporta el ciclo analítico usado en clase | organiza captura, preparación, análisis, visualización y acción |
            | PR | *Pull Request* — solicitud de integración de cambios | espacio de GitHub para comparar una propuesta, conversar, corregir y decidir si se integra | relaciona cambios del blueprint con objeciones de negocio, gobierno, seguridad y revisión humana |
            | RACI | *Responsible, Accountable, Consulted, Informed* | matriz que aclara quién ejecuta, quién responde por el resultado, quién es consultado y quién debe ser informado | distribuye responsabilidades sobre problema, datos, arquitectura, validación y acción |
            | SECOP | Sistema Electrónico para la Contratación Pública | plataforma colombiana donde se publica y gestiona información de contratación estatal | fuente del caso Compras Claras y de la muestra reproducible |
            | SLA | *Service Level Agreement* — acuerdo de nivel de servicio | objetivo o compromiso sobre el nivel esperado del servicio; no es una medición del resultado | “priorizar un registro completo en máximo 24 horas” es un SLA |
            | SRE | *Site Reliability Engineering* — ingeniería de confiabilidad de sitios | prácticas para operar servicios con disponibilidad, recuperación y observabilidad | sería relevante cuando Compras Claras pase de ejercicio reproducible a servicio operativo |

            ### Términos que no son siglas

            | Término | Significado | Ejemplo del caso |
            |---|---|---|
            | AS-IS | representación de cómo funciona actualmente el proceso | descarga, unión manual, validación, priorización y retrabajo actuales |
            | Artefacto | producto verificable creado durante el trabajo | mapa AS-IS, tabla preparada, perfil, decisión registrada o blueprint |
            | Carril | zona de un diagrama que asigna actividades a un participante o responsabilidad | entidad contratante, plataforma SECOP y oficina de seguimiento |
            | Commit | instantánea identificable de cambios guardada en el historial local de Git | versión que corrige el tratamiento de fechas faltantes |
            | Data owner | responsable institucional que autoriza usos y responde por un conjunto de datos | determina si la información contractual puede utilizarse para el caso |
            | Data steward | responsable de definiciones, metadatos, reglas de calidad y uso coherente | aclara qué significa una fecha y cómo se tratan valores faltantes |
            | Gateway o compuerta | rombo de BPMN que divide o reúne rutas según una regla; no ejecuta la validación | “¿fechas y campos completos?” dirige a priorizar o a solicitar corrección |
            | Linaje | registro del origen del dato y de las transformaciones que recibió | conecta el campo publicado por SECOP con la regla y la prioridad resultante |
            | Push | publicación de commits locales en la rama remota | actualiza en GitHub la propuesta que está siendo revisada en el PR |
            | Rama o *branch* | línea de trabajo separada que permite proponer cambios sin modificar inmediatamente `main` | `hito/s02-negocio` contiene el incremento de la sesión |
            | Snapshot | copia de datos asociada a fuente, fecha de corte, campos y límites | muestra SECOP que permite repetir el perfil aunque la API cambie |
            | TO-BE | representación del proceso o arquitectura objetivo después de una mejora propuesta | integración reproducible, reglas explicables y revisión humana con respuesta registrada |
            | Workflow | secuencia automatizada de tareas o validaciones | GitHub Actions ejecuta el validador cuando se publica un cambio |

            **Diferencia para recordar.** El **SLA** establece “máximo 24 horas”; el **KPI** mide cuánto tardamos de
            verdad. La tarea valida los campos; el **gateway** usa ese resultado para elegir la ruta del proceso.
            """
        ),
        md(
            f"""
            ## Referencias y recursos

            - **Lecturas asignadas a la Sesión 2:** *Chapter 2 — Business Motivations and Drivers for Big Data Adoption*
              y *Chapter 3 — Big Data Adoption and Planning Considerations*. “Chapter” identifica la numeración del
              libro; ambos textos apoyan esta única sesión del curso.
            - [NIST Big Data Interoperability Framework — Definitions](https://doi.org/10.6028/NIST.SP.1500-1r2)
            - [NIST Big Data Reference Architecture](https://doi.org/10.6028/NIST.SP.1500-6r2)
            - [TOGAF Standard — The Open Group](https://publications.opengroup.org/standards/togaf)
            - [BPMN 2.0.2 — Object Management Group](https://www.omg.org/spec/BPMN/)
            - [CRISP-DM — IBM](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview)
            - [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)
            - [API Socrata de SECOP Integrado](https://dev.socrata.com/foundry/www.datos.gov.co/rpmr-utcd)
            - [Diagramas Mermaid en GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
            - [Editar archivos en GitHub](https://docs.github.com/en/repositories/working-with-files/managing-files/editing-files)
            - [Crear un Pull Request](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/creating-a-pull-request)
            - [Página web del curso]({WEB_CURSO})

            **Nota de reproducibilidad.** Al actualizar SECOP registra fecha, fuente, campos, filtros, límite y regla
            de transformación. Una API viva puede cambiar; la muestra local permite repetir la práctica.
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
