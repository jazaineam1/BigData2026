# -*- coding: utf-8 -*-
"""Genera la sesión 2 como clase guiada sobre arquitectura, BPM y analítica."""

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
            # Pregunta {numero} de 12 — {tema}
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


def bash_commands(text):
    """Presenta comandos copiables para Codespaces sin ejecutarlos en Colab."""
    return md("```bash\n" + text.strip() + "\n```")


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
            > actividad usa GitHub Free y no requiere Copilot ni servicios pagos. No necesitas crear cuentas de
            > nube, tarjetas, claves, tokens ni cuentas de servicio.
            """
        ),
        md(
            """
            # Sesión 2 — De una decisión empresarial a una arquitectura analítica

            ## Universidad Central
            <div align="center">
              <img src="https://universidad.ucentral.edu.co/tulengua/wp-content/themes/tulengua/images/logo-ucentral.png"
                   width="340" alt="Logo de la Universidad Central">
            </div>

            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 2

            **Temas:** arquitectura empresarial · administración de procesos de negocio · ciclo analítico de Big Data<br>
            **Caso:** Compras Claras — seguimiento de contratación pública con SECOP<br>
            **Duración:** 180 minutos — 90 de explicación y 90 de práctica<br>
            **Modalidad:** aprender haciendo, en parejas, con GitHub y un entorno gratuito<br>
            **Última actualización:** 11 de agosto de 2026

            ## Ficha de la sesión

            | Campo | Definición |
            |---|---|
            | Pregunta profesional | ¿Qué procesos contractuales deberían revisarse primero? |
            | Responsable | analista de seguimiento con validación del director |
            | Fuente | SECOP Integrado; muestra local reproducible y API opcional |
            | Entorno | Colab para la clase; Git local o cuota personal de Codespaces para el laboratorio |
            | Producto | blueprint empresarial versionado y revisado |
            """
        ),
        md(
            """
            ## Objetivos de aprendizaje y alcance

            Al finalizar podrás:

            1. conectar una decisión con su proceso, datos, aplicaciones, infraestructura y KPI;
            2. distinguir proceso, tarea, procedimiento y proyecto, y representar un AS-IS con elementos BPMN;
            3. explicar por qué OLTP aparece primero y decidir entre ETL y ELT según dónde conviene transformar;
            4. diferenciar arquitectura empresarial, arquitectura de datos y arquitectura técnica;
            5. aplicar captura, preparación, análisis, visualización y acción al caso SECOP;
            6. elegir capacidades tecnológicas según el problema y no por popularidad del producto;
            7. usar working tree, staging, commit, rama, push, Pull Request y CI con evidencia verificable;
            8. comunicar límites: una alerta descriptiva prioriza revisión, pero no prueba causalidad ni irregularidad.

            **Producto de la sesión:** un primer blueprint versionado de Compras Claras. Su valor no está solo en el
            diagrama: cada decisión de diseño queda explicada, revisada y reproducible.
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
            2. **El proceso BPM** muestra quién trabaja, dónde se decide y en qué actividad nace cada dato.
            3. **OLTP** conserva los eventos operacionales sin detener la contratación.
            4. **ETL o ELT** mueve la evidencia y decide si la transformación ocurre antes o después de cargarla.
            5. **Data Warehouse, Data Mart y OLAP** integran historia, enfocan el análisis y permiten comparar.
            6. **La arquitectura y el ciclo NIST** asignan capacidades, controles y responsables de extremo a extremo.
            7. **Git** conserva por qué cambió el blueprint, quién lo revisó y qué validación superó.

            **Punto de partida.** No se presupone experiencia previa en Bash, Git, nube o contenedores. Los comandos
            obligatorios se presentan uno a uno y siempre se explica la salida esperada. Python se usa como una
            herramienta visible y guiada; el razonamiento estadístico se aprovecha para interpretar evidencia, no
            para saltar pasos de arquitectura. El recuadro de profundización es opcional para quien avance más
            rápido.
            """
        ),
        md(
            """
            ## Agenda: una historia en nueve decisiones

            ### Primeros 90 minutos — comprender el sistema

            | Minutos | Pregunta que conduce el bloque | Resultado |
            |---:|---|---|
            | 0–10 | ¿Qué debe decidir la analista y cómo sabrá si mejora? | responsable, alcance y KPI |
            | 10–26 | ¿Qué ocurre hoy antes de esa decisión? | proceso AS-IS y cuello de botella |
            | 26–36 | ¿Qué dato nace en cada actividad? | trazabilidad proceso–dato |
            | 36–47 | ¿Dónde se registran las operaciones? | OLTP y sistema fuente |
            | 47–62 | ¿Transformamos antes o después de cargar? | comparación ETL–ELT y decisión de diseño |
            | 62–71 | ¿Cómo se organiza la historia para analizarla? | DW, Data Mart y OLAP |
            | 71–79 | ¿Cómo se alinean todas las piezas? | arquitectura empresarial TO-BE |
            | 79–85 | ¿Cómo recorre la evidencia el ciclo analítico? | cinco etapas de NIST |
            | 85–90 | ¿Cómo se diseña y revisa sin perder trazabilidad? | capacidades, herramientas y Git |

            ### Últimos 90 minutos — construir evidencia

            | Minutos | Actividad | Evidencia observable |
            |---:|---|---|
            | 90–100 | Abrir el repositorio, elegir entorno y asumir roles | acceso, rama e identidad confirmadas |
            | 100–112 | Ejecutar el perfilador de SECOP | conteos, nulos, fechas y tres observaciones |
            | 112–132 | Estudiante A documenta el AS-IS | proceso, actor, cuello de botella y KPI |
            | 132–147 | Revisar, seleccionar, confirmar y publicar | primer commit atribuible |
            | 147–160 | Estudiante B completa TO-BE y ciclo analítico | arquitectura y matriz de cinco etapas |
            | 160–170 | Validar y corregir | segundo commit y validador aprobado |
            | 170–178 | Abrir PR, revisar y comprobar CI | comentario cruzado y comprobación verde |
            | 178–180 | Ticket de salida | decisión, limitación y riesgo pendiente |
            """
        ),
        md(
            """
            ## ¿Por qué importa esta sesión?

            En la sesión anterior reconocimos que Big Data no significa solamente “un archivo grande”. Ahora damos
            el paso que convierte tecnología en valor: conectar una pregunta empresarial con el trabajo que produce
            los datos, los controles que preservan su significado y la acción que una persona puede ejecutar.

            Si comenzamos por una herramienta, podemos automatizar un proceso defectuoso o construir un tablero que
            nadie usa. Si comenzamos por decisión, proceso y KPI, cada dato y cada componente puede justificarse.
            Por eso la secuencia de esta clase es deliberada y no una lista intercambiable de definiciones.
            """
        ),
        hidden(
            code(
                """
                import json
                import html as html_lib
                import sys
                from IPython.display import HTML, display

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
                      <h3 style="color:#0d47a1;margin-top:0;">Pregunta {numero} de 12 — {html_lib.escape(tema)}</h3>
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
            # 1. La historia comienza con una decisión, no con una herramienta

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

            {diagram('01_hilo_decision', 'Hilo decisión, proceso, datos, herramientas, KPI y acción humana')}

            **Cómo leerlo.** Laura formula la decisión en la columna izquierda. Sigue las tarjetas numeradas:
            proceso, datos, capacidades, KPI y acción humana. El recuadro rojo muestra el atajo que rompe la
            trazabilidad; la flecha punteada devuelve el resultado al proceso como un nuevo dato.

            **Conclusión.** Una herramienta sin decisión, proceso y KPI es un componente aislado, no una solución.

            **Limitación.** El diagrama explica trazabilidad, no asigna todavía responsables a cada actividad.

            **Conexión.** Para saber dónde se demora la decisión debemos observar cómo trabaja hoy la organización:
            ese será nuestro proceso AS-IS.
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
            # 2. BPM: comprender el trabajo antes de automatizarlo

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

            **Ejemplo pequeño.** En un reembolso, recibir solicitud, validar soportes, decidir y pagar forman el
            proceso. “Revisar la factura” es una tarea. Un gateway decide si hay soporte; un SLA fija el tiempo
            máximo y el KPI revela cuánto tarda realmente.

            **Error frecuente:** dibujar únicamente el camino feliz y ocultar rechazos, correcciones y esperas. Esos
            desvíos suelen explicar el cuello de botella.
            """
        ),
        question_cell(
            2,
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

            **Cómo leerlo.** Los tres carriles asignan responsabilidad. En la parte superior, cada actividad muestra
            también el dato que produce. SECOP recibe, guarda y expone registros; la oficina descarga y consolida.
            El rombo pregunta por completitud, la ruta roja devuelve el caso a “Reportar ejecución” y el contorno
            discontinuo identifica el cuello de botella. Los tres KPI inferiores indican cómo comprobar la mejora.

            **Conclusión.** El retraso no nace en un algoritmo: aparece cuando la oficina descarga, une y verifica
            archivos después de que el proceso operacional ya ocurrió.

            **Limitación.** Es una representación simplificada, no el modelo normativo completo de contratación ni
            un diagrama BPMN ejecutable. Debe validarse con responsables reales.

            **Conexión.** Cada actividad deja una huella. En el siguiente paso convertiremos el flujo en una tabla de
            datos, controles, herramientas y KPI.
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
            | 6 | plataforma | actualización | persistir y publicar | versión del registro | esquema y reglas básicas | dato consultable | calidad heterogénea | API Socrata / base OLTP | disponibilidad y completitud |
            | 7 | analista | archivos o API | consolidar y priorizar | perfil, reglas y cola | calidad y reproducibilidad | casos ordenados | unión manual y tardía | Python / DuckDB / BI | tiempo hasta priorización |
            | 8 | director y analista | cola explicable | revisar y actuar | comentario, corrección o escalamiento | evidencia humana | decisión registrada | retroalimentación no trazada | gestor de casos | % casos revisados a tiempo |

            **Cómo se interpreta.** Una fila conecta negocio y dato. Por ejemplo, `estado` no es una columna que
            “aparece” en el CSV: nace cuando el supervisor reporta, se valida con una regla y se consume después.

            **Qué no podemos concluir todavía.** La tabla propone herramientas posibles; no confirma que SECOP use
            internamente una base específica ni reemplaza el levantamiento con la entidad.
            """
        ),
        question_cell(
            3,
            "Gateway y retrabajo",
            "El registro puede estar completo o debe regresar al supervisor para corrección.",
            "¿Qué elemento representa mejor esa bifurcación?",
            [
                "Una tarea adicional llamada decidir.",
                "Un evento de inicio.",
                "Un gateway con condiciones explícitas de salida.",
                "Un Data Warehouse.",
            ],
            2,
            [
                "Una tarea ejecuta trabajo; la bifurcación necesita expresar rutas mutuamente comprensibles.",
                "El evento de inicio indica cuándo comienza el flujo, no cómo cambia de ruta.",
                "El gateway hace visible la regla: completo continúa; incompleto genera retrabajo y vuelve al reporte.",
                "El Data Warehouse almacena historia analítica, pero no representa una decisión del proceso BPM.",
            ],
        ),
        question_cell(
            4,
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
            ---
            # 3. Del proceso al dato: por qué OLTP aparece primero

            El proceso ya mostró **cuándo nace cada dato**. Antes de analizarlo, la organización necesita registrar
            de forma confiable cada publicación, modificación y avance. Esa es la función de un sistema operacional.

            ## OLTP — procesamiento de transacciones en línea

            **Motivo.** Sin registro operacional no existe historia confiable que extraer. Por eso OLTP precede a
            ETL, Data Warehouse y BI en nuestro relato.

            **Definición formal.** OLTP es un patrón de procesamiento orientado a transacciones frecuentes, breves y
            consistentes que crean o actualizan el estado corriente de la operación.

            **Intuición.** Es la caja registradora: debe guardar correctamente cada movimiento, no responder todavía
            todas las preguntas históricas de la gerencia.

            **Ejemplo manual.** Cuando una tienda vende una unidad, la transacción valida inventario, registra venta
            y actualiza existencias. Si falla, se revierte para no dejar estados contradictorios.

            **Aplicación SECOP.** Publicar o actualizar un proceso genera registros operacionales. SECOP/Socrata es
            la fuente expuesta que consultamos; PostgreSQL representa un ejemplo de motor relacional que una
            organización podría usar en su propia operación. No afirmamos que sea la base interna de SECOP.

            **Herramientas reales.** PostgreSQL, SQL Server, Oracle y servicios transaccionales administrados. Las
            APIs permiten exponer parte del estado operacional bajo contratos y límites de acceso.

            **Interpretación.** OLTP optimiza integridad y escritura puntual. Pedirle comparaciones históricas
            complejas de muchos años puede competir con la operación y producir consultas difíciles de gobernar.

            **Error frecuente:** usar el sistema operacional como si fuera el almacén analítico o copiar tablas sin
            documentar fecha, filtros, versión y significado.
            """
        ),
        md(
            """
            ## OLTP y OLAP responden preguntas diferentes

            | Criterio | OLTP — operar | OLAP — comprender |
            |---|---|---|
            | Pregunta típica | ¿cuál es el estado actual de este contrato? | ¿cómo cambian tiempos y completitud por entidad, modalidad y mes? |
            | Operación | insertar o actualizar pocos registros | leer y agregar muchos registros |
            | Horizonte | presente y detalle | historia y comparación |
            | Diseño | consistencia transaccional y baja latencia | dimensiones, métricas y lectura analítica |
            | Usuario | sistema operativo y personal de registro | analista, líder y tablero |

            **Ejemplo manual.** Buscar una factura por número es OLTP. Sumar ventas mensuales por región y comparar
            tendencia interanual es OLAP. Ambas capacidades son necesarias, pero no sustituyen una a la otra.
            """
        ),
        question_cell(
            5,
            "OLTP y OLAP",
            "La analista quiere comparar durante tres años la duración mediana por modalidad y departamento.",
            "¿Qué patrón está mejor orientado a esa consulta?",
            [
                "OLTP, porque toda consulta debe ocurrir en el sistema de captura.",
                "OLAP, porque resume historia por dimensiones y métricas.",
                "BPMN, porque un gateway agrega millones de filas.",
                "Git, porque un commit funciona como almacén de datos.",
            ],
            1,
            [
                "OLTP prioriza transacciones breves y estado corriente; una agregación histórica pesada pertenece al plano analítico.",
                "La consulta combina tiempo, modalidad, territorio y una métrica; es un uso típico de OLAP.",
                "BPMN modela procesos y decisiones, no ejecuta agregaciones analíticas.",
                "Git versiona archivos y decisiones de diseño; no reemplaza un motor OLAP.",
            ],
        ),
        md(
            """
            ---
            # 4. El puente analítico: elegir ETL o ELT antes de diseñar el consumo

            Si OLTP protege la operación, necesitamos un puente que copie de manera controlada la evidencia,
            verifique su calidad, preserve historia y prepare preguntas analíticas. Aquí aparece una decisión que
            no puede resolverse repitiendo siglas: **¿la transformación debe ocurrir antes o después de cargar los
            datos en la plataforma analítica?**

            ## ETL y ELT comparten una responsabilidad, pero no el mismo orden

            **Motivo.** Los datos operacionales llegan con unidades, fechas, nombres y niveles de calidad distintos.
            Además, ejecutar análisis pesados directamente sobre OLTP puede competir con el proceso que debe seguir
            registrando contratos. ETL y ELT separan esos trabajos y hacen explícitos sus controles.

            **Definición formal.**

            - **ETL — Extract, Transform, Load:** extrae desde la fuente, transforma en un motor o zona de integración
              y carga al destino analítico el resultado preparado.
            - **ELT — Extract, Load, Transform:** extrae, carga primero en una plataforma analítica o zona *raw* y
              transforma allí aprovechando su almacenamiento y cómputo.

            La diferencia esencial es **el orden y el lugar de la T**. Ambos enfoques necesitan calidad, seguridad,
            linaje, pruebas y responsables; ELT no significa “cargar sin gobierno” y ETL no significa “tecnología
            antigua”.

            | Criterio | ETL: transformar antes de cargar | ELT: cargar antes de transformar |
            |---|---|---|
            | Secuencia | fuente → extracción → **transformación** → destino curado | fuente → extracción → **zona raw** → transformación en destino |
            | Dónde ocurre la T | Python, Spark, Dataflow, SSIS u otro motor de integración | SQL, dbt o procesamiento dentro del warehouse/lakehouse |
            | Qué llega primero al destino compartido | datos validados, estandarizados o enmascarados | copia cercana al origen con metadatos de ingestión |
            | Conviene cuando | datos sensibles no deben aterrizar en crudo; reglas estables; destino limitado | plataforma escalable; varias transformaciones; se necesita reutilizar el original |
            | Riesgo principal | perder detalle o flexibilidad si se transforma sin conservar linaje y excepciones | exponer datos crudos, elevar costo o crear copias sin control de acceso y retención |
            | Ejemplo pequeño | API SECOP → Python/Pandas → tabla curada | archivo SECOP → DuckDB/BigQuery raw → SQL de transformación |

            ### Un mismo dato, dos recorridos

            Supongamos que la extracción trae tres valores de duración:

            | id_contrato | duración_original | problema que debe resolverse |
            |---|---|---|
            | C-101 | `2 meses` | convertir con una regla explícita |
            | C-102 | `60 días` | ya tiene unidad diaria |
            | C-103 | vacío | no inventar una duración; registrar excepción |

            **Recorrido ETL.**

            1. **Extract:** Python descarga el snapshot de SECOP y registra URL, fecha de corte y parámetros.
            2. **Transform:** antes de cargar la tabla analítica convierte `2 meses` según una regla documentada,
               mantiene `duración_original`, crea `duración_días` y marca C-103 en una tabla de excepciones.
            3. **Load:** carga al warehouse o archivo Parquet la tabla curada y el reporte de calidad.

            **Recorrido ELT.**

            1. **Extract:** se obtiene exactamente el mismo snapshot y los mismos metadatos.
            2. **Load:** se conserva primero en una zona `raw` con acceso restringido y fecha de ingestión.
            3. **Transform:** SQL o dbt dentro de DuckDB, BigQuery o un lakehouse crea la tabla curada, preserva la
               columna original y produce la misma excepción para C-103.

            **Qué nos dice el ejemplo.** La tabla analítica final puede ser equivalente; lo que cambia es dónde se
            usa el cómputo, qué dato aterriza primero y qué controles deben activarse antes. La elección es una
            decisión de arquitectura, no un concurso entre herramientas.

            ### Aplicación a Compras Claras

            - Elegiríamos **ETL** si identificadores sensibles deben enmascararse antes de entrar al destino
              compartido o si una rutina Python pequeña puede producir una tabla estable y verificable.
            - Elegiríamos **ELT** si conservamos snapshots autorizados para varias preguntas y una plataforma
              escalable ejecuta versiones distintas de la lógica con SQL, pruebas y control de costos.
            - Un diseño **híbrido** es frecuente: aplica controles irreversibles antes de cargar, conserva una zona
              raw protegida y realiza el resto de transformaciones dentro de la plataforma.

            > **Profundización opcional.** Si auditoría, finanzas y ciencia de datos necesitan reutilizar el mismo
            > snapshot con reglas diferentes, argumenta por qué ELT o un híbrido puede preservar más flexibilidad.
            > Tu respuesta solo es completa si también define acceso a `raw`, retención, prueba de calidad y control
            > de costo. “Hay mucho volumen” no basta para decidir.

            **Error frecuente:** llamar ETL a cualquier movimiento de archivos, suponer que ELT elimina la limpieza
            o borrar filas problemáticas sin contar cuántas fueron excluidas, por qué y bajo qué versión de la regla.

            **Puente al siguiente concepto.** ETL o ELT explica cómo viaja y se prepara la evidencia. Todavía falta
            decidir dónde se integra la historia y cómo se sirve una vista estable a la oficina de seguimiento.

            ## Data Warehouse

            **Definición formal.** Repositorio integrado, histórico y orientado al análisis, con datos organizados
            para mantener significado consistente entre fuentes y periodos.

            **Intuición.** Es el archivo histórico de la organización: no solo guarda, también conserva contexto y
            permite que “duración” signifique lo mismo en distintos reportes.

            **Aplicación.** Integra procesos, entidades, estados, fechas y hechos de seguimiento. BigQuery es un
            ejemplo; Snowflake, Redshift, Synapse y otros almacenes ofrecen capacidades equivalentes.

            ## Data Mart

            **Definición formal.** Subconjunto analítico gobernado para un área o propósito concreto.

            **Ejemplo Compras Claras.** Una vista de seguimiento contiene solo entidades, contratos, estados,
            métricas de oportunidad y calidad necesarias para priorizar. No duplica sin control todo el warehouse.

            ## OLAP

            **Definición formal.** Capacidad para explorar medidas por dimensiones, agregaciones y jerarquías.

            **Aplicación.** Comparar conteo, mediana de duración y porcentaje incompleto por mes, modalidad y entidad.

            **Qué no podemos concluir.** Una agregación atípica señala dónde mirar; no explica causalidad ni prueba
            incumplimiento.
            """
        ),
        md(
            f"""
            ## Vista completa: de la transacción a la acción

            {diagram('03_puente_analitico', 'Dos rutas desde OLTP: ETL transforma antes de cargar y ELT carga antes de transformar; ambas convergen en consumo analítico y acción')}

            **Cómo leerlo.** La fuente OLTP aparece una sola vez. En el centro, la ruta ETL ejecuta `T` antes de `L`,
            mientras la ruta ELT aterriza una copia `raw` antes de ejecutar `T` dentro de la plataforma. Las dos
            pueden producir datos curados para Warehouse, Data Mart y OLAP. La acción humana vuelve al proceso como
            una nueva transacción; los controles de la franja inferior no desaparecen en ninguna ruta.

            **Conclusión.** OLTP, integración, almacenamiento histórico y consumo no son definiciones aisladas. ETL
            y ELT son dos órdenes posibles para el tramo de integración; la restricción del caso determina cuál
            conviene o qué combinación híbrida se necesita.

            **Limitación.** En una solución pequeña varias responsabilidades pueden vivir en la misma herramienta;
            la separación conceptual sigue siendo útil para no perder controles.

            **Conexión.** Ya podemos alinear negocio, información, aplicaciones y tecnología en una arquitectura.
            """
        ),
        question_cell(
            6,
            "Elegir entre ETL y ELT",
            "Una política exige que identificadores personales no lleguen en crudo al destino analítico compartido. La tabla cargada debe estar enmascarada y la regla debe quedar versionada.",
            "¿Qué diseño responde directamente a esa restricción?",
            [
                "ELT sin controles, porque cargar primero siempre reduce el riesgo.",
                "ETL —o un tramo híbrido equivalente— que enmascara antes de cargar al destino compartido.",
                "OLAP, porque una agregación reemplaza el control de privacidad.",
                "Cualquiera sin documentarlo, porque ETL y ELT solo cambian el nombre de la herramienta.",
            ],
            1,
            [
                "Cargar primero el dato crudo contradice la política si el destino compartido no puede recibir esos identificadores; ELT necesita controles previos o una zona raw autorizada.",
                "La T ocurre antes de la L hacia el destino compartido: el enmascaramiento, su prueba y su versión quedan como parte del tramo ETL o híbrido.",
                "OLAP resume y explora medidas; no evita que el identificador crudo haya aterrizado ni sustituye una política de acceso.",
                "La diferencia sí afecta el orden, la ubicación del cómputo y el momento en que actúan privacidad y calidad; debe quedar documentada.",
            ],
        ),
        question_cell(
            7,
            "Data Warehouse y Data Mart",
            "Seguimiento necesita una vista pequeña con contratos y métricas aprobadas, derivada de historia integrada.",
            "¿Qué combinación describe mejor ese diseño?",
            [
                "El Data Mart integra toda la empresa y el Warehouse es un archivo personal.",
                "El Warehouse conserva historia integrada y el Data Mart sirve al propósito de seguimiento.",
                "Ambos son sinónimos de una tabla OLTP.",
                "El Data Mart reemplaza calidad, gobierno y linaje.",
            ],
            1,
            [
                "Invierte las responsabilidades: la integración empresarial corresponde al warehouse; la vista enfocada, al mart.",
                "La combinación preserva una fuente integrada y entrega una vista gobernada para Compras Claras.",
                "Una tabla operacional prioriza transacciones; warehouse y mart están orientados a historia y análisis.",
                "Reducir el alcance no elimina controles; un Data Mart también necesita definiciones, acceso y trazabilidad.",
            ],
        ),
        md(
            """
            ---
            # 5. Arquitectura empresarial: alinear lo que ya comprendimos

            ## ¿Por qué definirla en este punto?

            Ahora sí conocemos la decisión, el proceso, los datos y el puente analítico. La arquitectura empresarial
            organiza esas piezas y comprueba que ninguna tecnología quede huérfana de propósito.

            **Definición formal.** Conjunto coherente de principios, modelos y decisiones que describe cómo negocio,
            información, aplicaciones y tecnología se relacionan para lograr objetivos y evolucionar de un estado
            AS-IS a uno TO-BE.

            **Intuición.** Es el plano de una ciudad, no una lista de edificios. Muestra rutas, responsabilidades,
            restricciones y cómo un cambio en una zona afecta a las demás.

            **Ejemplo manual.** Una tienda quiere responder reclamos en 12 horas. Negocio define el SLA; información
            define cliente, caso y estado; aplicaciones reciben, enrutan y notifican; tecnología ejecuta y monitorea.

            **Aplicación SECOP.** El objetivo es priorizar; el proceso produce estados y fechas; las aplicaciones
            ingieren, perfilan y presentan; la tecnología almacena y procesa; gobierno controla acceso y linaje.

            **Error frecuente:** dibujar logos primero y añadir el objetivo al final.
            """
        ),
        md(
            """
            ## Cuatro dominios que responden preguntas distintas

            <div align="center">
              <img src="../Images/2.1.png" width="780"
                   alt="Dominios de negocio, información, aplicaciones y tecnología">
            </div>

            | Dominio | Pregunta de diseño | Evidencia en Compras Claras |
            |---|---|---|
            | Negocio | ¿qué objetivo, decisión, proceso y responsable mejoran? | priorización y revisión humana |
            | Información | ¿qué entidades, significados, reglas y calidad se requieren? | contrato, entidad, estado, fecha, duración y linaje |
            | Aplicaciones | ¿qué capacidades manipulan y entregan información? | fuente, ingesta, perfilador, reglas, tablero y alertas |
            | Tecnología | ¿dónde se almacena, procesa, conecta y observa? | API, objetos/Parquet, motor analítico, CI y monitoreo |

            **Cómo leer la imagen.** Cada dominio responde una clase de preguntas y se traduce en requisitos para el
            siguiente. Gobierno, seguridad, privacidad, observabilidad y costos atraviesan a todos.

            **Conclusión.** Arquitectura empresarial es más amplia que arquitectura de datos; la segunda profundiza
            fuentes, modelos, flujos y calidad. La arquitectura técnica profundiza cómputo, red, almacenamiento,
            despliegue y operación.

            **Limitación.** La figura clasifica dominios, pero no muestra todavía el diseño específico del caso.
            """
        ),
        md(
            f"""
            ## Arquitectura objetivo TO-BE de Compras Claras

            {diagram('04_arquitectura_to_be', 'Arquitectura TO-BE con cuatro dominios y controles transversales')}

            **Cómo leerlo.** Recorre las cuatro capas de arriba hacia abajo. La primera tarjeta numerada forma una
            traza completa: decisión → fuente → integración → conectividad. Las demás columnas amplían proceso,
            entidades, reglas, responsables, KPI, aplicaciones y componentes técnicos. La banda superior recuerda
            que gobierno, seguridad, privacidad, observabilidad, costos, calidad y linaje condicionan cada capa.

            **Conclusión.** La cola priorizada solo tiene valor si existe responsable, dato con significado,
            aplicación explicable, tecnología sostenible y controles transversales.

            **Limitación.** Es arquitectura lógica: todavía no fija volúmenes, latencia, proveedor, presupuesto ni
            acuerdos institucionales. Esas restricciones se documentan antes de implementar.

            **Conexión.** Falta describir cómo un dato atraviesa la solución y regresa al proceso como acción; para
            eso usamos el ciclo analítico de NIST.
            """
        ),
        question_cell(
            8,
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
                "Esas restricciones permiten decidir si hacen falta eventos o si una ingesta batch es suficiente.",
                "BPM explica el trabajo; una lista de productos no representa actores, reglas ni retrabajo.",
                "Costo es una preocupación transversal y puede cambiar una alternativa técnicamente válida.",
            ],
        ),
        md(
            """
            ---
            # 6. Ciclo analítico de Big Data: del dato a una acción responsable

            ## ¿Por qué no terminamos en el Data Warehouse?

            Guardar datos no mejora una decisión. El ciclo analítico describe el movimiento de la evidencia hasta
            una acción y su retroalimentación. Usaremos el modelo NIST: **captura, preparación, análisis,
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

            {diagram('05_ciclo_nist', 'Ciclo NIST aplicado a captura, preparación, análisis, visualización y acción')}

            | Etapa | Entrada | Actividad Compras Claras | Responsable | Artefacto | Control | Métrica de éxito |
            |---|---|---|---|---|---|---|
            | Captura | API o muestra SECOP | registrar fuente, fecha, campos y límite | ingeniería de datos | snapshot reproducible | acceso y procedencia | extracción completa según contrato |
            | Preparación | snapshot crudo | tipar, revisar nulos, fechas, duplicados y unidades | analista / datos | tabla preparada + reporte | regla y linaje | % filas válidas y excepciones contadas |
            | Análisis | datos preparados | perfilar duraciones y reglas de prioridad | analista | métricas y cola candidata | sesgo y reproducibilidad | cobertura de reglas explicables |
            | Visualización | resultados | presentar razón de prioridad, filtros y calidad | BI / analista | tablero o reporte | accesibilidad y contexto | tiempo para comprender un caso |
            | Acción | cola explicable | revisar, corregir, escalar o descartar alerta | responsable humano | decisión registrada | separación de funciones | % casos atendidos en SLA |

            **Cómo leer el diagrama.** Sigue el ciclo en sentido horario. Cada tarjeta declara entrada o actividad,
            artefacto y responsable; los rótulos sobre las flechas muestran qué cambia entre etapas. La decisión
            humana permanece en el centro porque todas las fases deben poder justificarla. Los controles
            transversales no son una sexta fase: condicionan las cinco.

            **Conclusión.** Visualizar no es actuar. Una gráfica se vuelve útil cuando alguien tiene autoridad,
            criterio y canal para registrar la respuesta.

            **Limitación.** El ciclo no prescribe un algoritmo ni un proveedor y no elimina la necesidad de validar
            el proceso, los datos y el impacto.

            **Conexión.** Con las responsabilidades claras, podemos comparar herramientas reales por capacidad.
            """
        ),
        question_cell(
            9,
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
            10,
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
            # 7. Capacidades y herramientas reales en un flujo empresarial

            Una arquitectura no debe casarse prematuramente con un proveedor. Primero nombra la capacidad; luego
            compara opciones por volumen, velocidad, costo, conocimiento del equipo, seguridad y operación.

            | Capacidad | Escenario en Compras Claras | Herramientas reales | Cuándo tiene sentido | Advertencia |
            |---|---|---|---|---|
            | fuente operacional / exposición | consultar procesos y estados | SECOP/Socrata; PostgreSQL como ejemplo interno | transacciones y consulta de registros | no confundir API pública con base interna |
            | ingesta batch | actualización diaria o por corte | Python, Airbyte | latencia de horas es suficiente | registrar fecha, filtros y reintentos |
            | eventos | cambios que deben fluir en segundos/minutos | Kafka, Google Pub/Sub | existe evento, productor y consumidor estable | no añadir streaming sin requisito de latencia |
            | preparación pequeña/mediana | muestra local o millones manejables en una máquina | Pandas, DuckDB | desarrollo, perfilado y análisis local | vigilar memoria y tamaño real |
            | procesamiento distribuido | alto volumen, particiones y cómputo paralelo | Spark, Google Dataflow | una sola máquina no cumple tiempo/capacidad | distribución agrega operación y costo |
            | almacenamiento analítico | snapshots y tablas columnares | Parquet en GCS o S3 | historia económica, interoperable y particionada | gobernar esquema, cifrado y ciclo de vida |
            | almacén analítico | SQL concurrente, métricas e historia | BigQuery, Snowflake, Redshift, Synapse | BI gobernada y consultas escalables | controlar costo, acceso y definiciones |
            | consumo | reporte, exploración y aplicación | Streamlit, Power BI, Looker, Tableau | el usuario necesita contexto y acción | un tablero sin dueño no cierra el ciclo |
            | orquestación / automatización | ejecutar, observar y recuperar el flujo | GitHub Actions; Airflow / Composer | tareas repetibles con dependencias | CI valida código; Airflow coordina pipelines |

            **Ejemplo de decisión tecnológica.** Para una muestra estable y una clase de tres horas, Python +
            DuckDB/Pandas + archivos locales es suficiente. Si el proceso exige millones de eventos en segundos,
            se reevalúan Kafka/Pub/Sub y Spark/Dataflow. La palabra “Big Data” no obliga a usar todas las herramientas.
            """
        ),
        question_cell(
            11,
            "Capacidad frente a producto",
            "La oficina actualiza SECOP una vez al día y el volumen cabe en una máquina.",
            "¿Cuál decisión es más proporcionada para el primer hito?",
            [
                "Kafka y Spark obligatoriamente porque el curso se llama Big Data.",
                "Python con ingesta batch y Pandas/DuckDB, dejando criterios para escalar.",
                "Ninguna herramienta; copiar y pegar manualmente para siempre.",
                "Activar todos los productos de GCP sin estimar costos.",
            ],
            1,
            [
                "Streaming y distribución agregan complejidad sin un requisito actual de velocidad o capacidad.",
                "La alternativa satisface el caso presente y conserva una ruta de evolución basada en métricas reales.",
                "La contingencia manual puede salvar una clase, pero no es un proceso reproducible ni sostenible.",
                "Una arquitectura responsable evalúa capacidad, costo, seguridad y operación antes de activar servicios.",
            ],
        ),
        md(
            """
            ## Lectura crítica de arquitecturas de nube

            Las siguientes imágenes históricas se conservan porque ayudan a practicar una habilidad durable:
            **traducir productos en capacidades**. No vamos a crear recursos, cuentas, claves ni facturación.

            <div align="center">
              <img src="../Images/GCP/5.png" width="900" alt="Arquitectura histórica de datos en Google Cloud"><br><br>
              <img src="../Images/GCP/6.png" width="900" alt="Arquitectura histórica de procesamiento en Google Cloud">
            </div>

            ### Método de lectura en cuatro preguntas

            1. ¿Qué fuente produce datos y con qué frecuencia?
            2. ¿Qué capacidad cumple cada bloque: ingesta, almacenamiento, procesamiento, consumo u orquestación?
            3. ¿Dónde aparecen calidad, seguridad, observabilidad, recuperación y costo?
            4. ¿Qué productos o nombres deben verificarse hoy antes de reutilizar la arquitectura?

            **Interpretación.** Aunque un nombre comercial o una interfaz cambie, las necesidades de capturar,
            almacenar, transformar, consultar, servir y gobernar permanecen. Diseñar por capacidad permite comparar
            GCP con AWS, Azure o una alternativa local.

            **Error frecuente:** copiar una arquitectura de referencia completa cuando el caso solo necesita una
            fracción de sus capacidades.
            """
        ),
        md(
            """
            ---
            # 8. Git: arquitectura como evidencia revisable

            ## ¿Por qué Git aparece después del blueprint?

            El diseño ya contiene decisiones y supuestos. Git permite conocer **qué cambió, quién lo cambió, por qué
            y qué revisión recibió**. No es solo respaldo: convierte el blueprint en un artefacto colaborativo.

            **Definición formal.** Git es un sistema distribuido de control de versiones que registra instantáneas y
            relaciones entre cambios. GitHub aloja repositorios y agrega colaboración mediante Pull Requests,
            revisiones y automatización.

            **Intuición.** Working tree es la mesa de trabajo; staging es la bandeja de cambios que elegiste para la
            siguiente fotografía; commit es la fotografía con mensaje y autor; push publica la historia; el Pull
            Request es la conversación antes de integrarla.

            **Error frecuente:** ejecutar `git add .` y `git commit` sin leer `status`, `diff` y `diff --staged`.
            """
        ),
        md(
            f"""
            ## Estados del cambio hasta la revisión

            {diagram('06_estados_git', 'Estados Git desde repositorio, rama y staging hasta Pull Request y CI')}

            **Cómo leerlo.** Primero distingue las tres zonas: local, remoto y colaboración. Dentro de la zona local,
            cada tarjeta explica qué sabe Git del archivo; los comandos cambian working tree → staging → commit. El
            push publica la misma historia, y el PR agrega revisión y CI. La ruta roja vuelve al working tree cuando
            el validador falla: no borra lo anterior, añade un commit correctivo.

            **Conclusión.** Un commit pequeño y deliberado es una unidad de explicación. Un PR reúne propósito,
            evidencia, conversación y validación automática.

            **Limitación.** El diagrama omite conflictos y estrategias de integración; primero practicaremos un flujo
            secuencial para dos personas.

            **Conexión.** El laboratorio recorre exactamente estos estados y comprueba el resultado después de cada
            comando.
            """
        ),
        question_cell(
            12,
            "Working tree y staging",
            "Se editó docs/01_proceso_as_is.md, pero todavía no se ejecuta git add.",
            "¿Dónde está el cambio y qué hace git add?",
            [
                "Ya está en el remoto; git add abre un Pull Request.",
                "Está en working tree; git add lo selecciona para staging.",
                "Ya es un commit; git add lo elimina.",
                "Está en CI; git add ejecuta el validador.",
            ],
            1,
            [
                "Editar es local. El remoto solo cambia después de commit y push; el PR se abre en GitHub.",
                "Correcto: primero se observa como modificado y después se selecciona para la próxima instantánea.",
                "Un archivo editado no se convierte en commit hasta ejecutar git commit con cambios staged.",
                "CI ocurre después de publicar cambios o abrir el PR, según el workflow; git add no ejecuta Actions.",
            ],
        ),
        md(
            """
            ---
            # 9. Laboratorio guiado de 90 minutos

            ## Roles y regla de colaboración

            Cada pareja trabaja secuencialmente sobre `entrega/sesion2` para comprender el historial antes de
            introducir conflictos. Estudiante A documenta AS-IS; estudiante B completa TO-BE y ciclo analítico.
            Ambos revisan el Pull Request.

            ### Evidencias del repositorio

            - `README.md`: problema, responsable, decisión, KPI y límites.
            - `resultados/perfil_secop.md`: tres hallazgos descriptivos y sus limitaciones.
            - `docs/01_proceso_as_is.md`: actores, datos, gateway, cuello de botella y dos KPI.
            - `docs/02_arquitectura_objetivo.md`: cuatro dominios y controles transversales.
            - `docs/03_ciclo_analitico.md`: cinco etapas, responsables, artefactos y métricas.
            - dos commits, rama distinta de `main`, PR, comentario de revisión y CI verde.

            No existe una invitación general para toda la clase. El docente agregará previamente las dos cuentas
            GitHub como colaboradoras y compartirá a cada pareja únicamente la URL de su repositorio privado. No
            publiques esa URL ni trabajes en el repositorio de otro equipo.
            """
        ),
        md(
            """
            ## Apoyo de terminal — cuatro ideas antes de usar Git

            No necesitas conocer Bash para comenzar. En Git Bash, Codespaces y PowerShell usaremos instrucciones
            equivalentes y cortas:

            | Elemento | Qué significa | Cómo comprobarlo |
            |---|---|---|
            | *prompt* | la línea donde la terminal espera; no se copia el símbolo inicial | escribe un comando y pulsa Enter |
            | carpeta actual | lugar sobre el que actuará Git | `pwd` debe terminar en el repositorio de la pareja |
            | contenido | archivos y carpetas disponibles | `ls` debe mostrar `README.md`, `docs` y `scripts` |
            | salida | respuesta del comando; se lee, no se vuelve a escribir | compara con el resultado esperado del paso |

            **Regla de seguridad.** Ejecuta una línea a la vez, lee la salida y detente si la ruta o el repositorio
            no coincide. La flecha arriba recupera el último comando para corregirlo sin volver a escribirlo.
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
            ## Paso 1 — Abrir el repositorio privado y elegir el entorno

            **Acción.** Inicia sesión con la cuenta que informaste al docente y abre la URL privada de tu pareja.
            Comprueba que puedes ver la pestaña **Actions** y el botón **Code**. Elige una ruta:

            1. **Git y Python locales — ruta siempre gratuita:** pulsa **Code → Local → HTTPS**, copia la URL y
               ejecuta `git clone URL` desde VS Code o una terminal instalada.
            2. **Codespaces — ruta opcional:** úsala solo si tu cuenta muestra cuota personal disponible; no se
               habilitará facturación de la organización.
            3. **Contingencia web:** pulsa la tecla `.` para abrir `github.dev`. Permite editar, confirmar y
               sincronizar desde **Source Control**, pero no tiene terminal; usa el perfil SECOP precomputado.

            **Resultado esperado.** Estás dentro del repositorio `compras-claras-pareja-XX`, no en la plantilla ni
            en el repositorio de demostración, y puedes crear una rama de trabajo.

            **Error probable.** Un mensaje 404 normalmente significa que abriste la URL con otra cuenta o que el
            nombre de usuario aún no fue agregado. No crees un fork público: solicita al docente verificar el acceso.

            <div align="center"><img src="../assets/session2/git/01_entorno_gratuito.svg" width="920"
            alt="Vista guiada para elegir Git local, Codespaces con cuota personal o github.dev"></div>

            **Cómo leer la vista.** A la izquierda aparece el repositorio correcto y el menú **Code** abierto; a la
            derecha se comparan las tres rutas por capacidad y restricción. Git local es la ruta gratuita completa,
            Codespaces depende de cuota personal y `github.dev` sirve cuando solo se necesita editar y confirmar.
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
            **Lee la salida.** `git status` debe indicar la rama actual y un working tree limpio. `git remote -v`
            debe apuntar al repositorio de la pareja, no a una copia ajena. Si elegiste Codespaces y Python o Git no
            aparecen, el entorno no terminó de construir; revisa **View Creation Log** o usa Git local.
            """
        ),
        md(
            """
            ## Paso 2 — Configurar identidad y crear la rama

            Usa tu nombre y el correo asociado a GitHub. La opción `--local` aplica solo a este repositorio.
            Codespaces autentica su repositorio de origen y Git local puede usar el inicio de sesión de GitHub; no
            crearemos claves SSH, tokens manuales ni credenciales dentro de archivos en esta sesión.
            """
        ),
        bash_commands(
            """
            git config --local user.name "Tu Nombre Completo"
            git config --local user.email "tu-correo-asociado-a-github"
            git config --local --get user.name
            git config --local --get user.email
            git switch -c entrega/sesion2
            git branch --show-current
            """
        ),
        md(
            """
            **Resultado esperado.** La última línea muestra `entrega/sesion2`. Si Git responde que la rama ya existe,
            usa `git switch entrega/sesion2`; no crees nombres alternativos sin avisar a tu pareja.
            """
        ),
        md(
            """
            ## Paso 3 — Ejecutar el perfilador reproducible

            El script lee la muestra local, calcula conteos, nulos, rango de fechas y resumen de duración. La API
            viva es opcional: una falla de red no debe bloquear la evidencia básica.
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
            ## Paso 4 — Estudiante A documenta AS-IS y revisa antes de seleccionar

            Edita `docs/01_proceso_as_is.md` y `resultados/perfil_secop.md`. Sustituye todos los marcadores
            `COMPLETAR` con evidencia del caso. Luego observa el estado y el diff.

            <div align="center"><img src="../assets/session2/git/02_status_diff.svg" width="920"
            alt="Vista guiada de terminal mostrando git status y git diff en la rama de entrega"></div>

            **Cómo leer la vista.** La terminal aporta la evidencia y el panel derecho traduce su significado: hay
            dos archivos en working tree, mientras staging, commit y remoto siguen sin cambios. Antes de `git add`,
            confirma que ambos archivos pertenecen al mismo propósito y que la cifra está explicada y limitada.
            """
        ),
        bash_commands(
            """
            git status
            git diff --check
            git diff -- docs/01_proceso_as_is.md resultados/perfil_secop.md
            """
        ),
        md(
            """
            **Resultado esperado.** Solo aparecen los dos archivos deliberadamente editados. `git diff --check` no
            imprime nada cuando no encuentra espacios problemáticos. Si ves otro archivo, investiga su origen antes
            de agregarlo.
            """
        ),
        md(
            """
            ## Paso 5 — Seleccionar, revisar staging y crear el primer commit

            `git add` no “guarda todo”: selecciona exactamente qué entra en la próxima instantánea. Por eso revisamos
            otra vez con `git diff --staged`.
            """
        ),
        bash_commands(
            """
            git add docs/01_proceso_as_is.md resultados/perfil_secop.md
            git status
            git diff --staged
            git commit -m "Documenta proceso actual de contratación"
            git status
            git log --oneline --decorate -3
            """
        ),
        md(
            """
            **Resultado esperado.** Antes del commit, los archivos aparecen bajo “Changes to be committed”. Después,
            el working tree queda limpio y el log muestra el nuevo commit con el autor A.

            **Error probable.** Si el commit incluye algo incorrecto y todavía no hiciste push, solicita orientación
            antes de reescribir historial. En esta sesión preferimos un nuevo commit correctivo para conservar la
            trazabilidad.
            """
        ),
        md(
            """
            ## Paso 6 — Publicar la rama y hacer relevo
            """
        ),
        bash_commands(
            """
            git push -u origin entrega/sesion2
            """
        ),
        md(
            """
            **Resultado esperado.** Git confirma que la rama local rastrea `origin/entrega/sesion2` y muestra una URL
            para crear el PR. Si aparece 403, revisa que estés autenticado como integrante del repositorio asignado;
            no pegues tokens en la terminal ni en el chat.

            El estudiante B abre su propio Codespace y ejecuta:
            """
        ),
        bash_commands(
            """
            git fetch origin
            git switch --track origin/entrega/sesion2
            git pull --ff-only
            git log --oneline --decorate -3
            """
        ),
        md(
            """
            ## Paso 7 — Estudiante B completa TO-BE y ciclo analítico

            Edita los dos documentos, comprueba diferencias, selecciona, valida y crea un commit propio.
            """
        ),
        bash_commands(
            """
            git status
            git diff -- docs/02_arquitectura_objetivo.md docs/03_ciclo_analitico.md
            git add docs/02_arquitectura_objetivo.md docs/03_ciclo_analitico.md
            git diff --staged
            python scripts/validar_entrega.py
            git commit -m "Propone arquitectura y ciclo analítico"
            git push
            git log --oneline --decorate -5
            """
        ),
        md(
            """
            **Resultado esperado.** El validador termina con aprobación, el log muestra dos commits con autores
            distintos y `origin/entrega/sesion2` apunta al último. Si el validador falla, lee cada sección señalada,
            corrige el Markdown y vuelve a validar antes de confirmar.
            """
        ),
        md(
            """
            ## Paso 8 — Abrir el Pull Request y revisar Mermaid

            En GitHub selecciona **Compare & pull request**. Base: `main`; compare: `entrega/sesion2`. Completa qué
            se hizo, por qué, cómo se verificó y qué limitaciones conserva. Abre la pestaña **Files changed** y
            confirma que los diagramas Mermaid renderizan y que no quedan marcadores.

            <div align="center"><img src="../assets/session2/git/03_pull_request.svg" width="920"
            alt="Pull Request docente de demostración con descripción y archivos revisables"></div>

            **Cómo leer la vista.** Comprueba ramas, propósito, verificación, límites, archivos cambiados y revisores
            en ese orden. Un check verde prueba reglas observables; la pestaña **Files changed** permite evaluar el
            contenido y la conversación explica las decisiones.

            **Error probable.** Si Mermaid no renderiza, revisa la sintaxis en la vista previa de GitHub. No reemplaces
            el diagrama por una captura: el producto del estudiante debe continuar editable y versionable.
            """
        ),
        md(
            """
            ## Paso 9 — Revisión cruzada y CI verde

            El compañero deja al menos un comentario sustantivo: pregunta por una decisión, señala una ambigüedad o
            propone una mejora verificable. Después abre **Checks** y confirma el validador.

            <div align="center"><img src="../assets/session2/git/04_actions.svg" width="920"
            alt="Comprobación de GitHub Actions aprobada en el Pull Request docente"></div>

            **Cómo leer la vista.** La columna verde enumera lo que puede comprobar CI; la naranja enumera lo que
            requiere juicio humano. La entrega solo cruza la puerta de calidad cuando coinciden validador local,
            check verde y comentario sustantivo.

            **Resultado esperado.** PR con plantilla completa, comentario de revisión y check verde. No se exige hacer
            merge durante la clase.

            **Error probable.** Si CI está rojo, abre el detalle, identifica el archivo y corrige en la misma rama.
            Un nuevo push actualiza el PR automáticamente. Si Actions está demorado, conserva la salida verde del
            validador local y revisa CI después.
            """
        ),
        md(
            """
            ## Criterios de calidad del hito

            | Criterio | Peso |
            |---|---:|
            | problema, decisión, responsable y alcance | 15 |
            | proceso AS-IS, actores, cuello de botella y KPI | 20 |
            | arquitectura objetivo y trazabilidad entre dominios | 25 |
            | ciclo analítico, controles y responsables | 20 |
            | interpretación de evidencia y límites | 10 |
            | flujo Git, commits, PR y revisión | 10 |

            **Condiciones mínimas:** dos autores, rama distinta de `main`, dos commits, PR descrito, revisión,
            CI/local verde, diagramas renderizados, ninguna plantilla sin completar, ningún secreto y ninguna
            afirmación causal o acusación basada solo en el perfil descriptivo.
            """
        ),
        md(
            """
            ---
            # Cierre de la sesión

            ## Recapitulación

            1. Definimos una decisión, responsable y KPI antes de elegir tecnología.
            2. BPM reveló actividades, datos, gateway, retrabajo y cuello de botella.
            3. OLTP registró la operación; ETL y ELT ofrecieron órdenes distintos para transformar y cargar.
            4. Warehouse, Data Mart y OLAP integraron historia, enfocaron el consumo y permitieron comparar.
            5. La arquitectura alineó negocio, información, aplicaciones, tecnología y controles.
            6. NIST llevó la evidencia de captura a acción y retroalimentación.
            7. Git convirtió el blueprint en una decisión versionada, revisada y verificable.

            **Idea más importante.** Big Data crea valor cuando una evidencia trazable regresa al proceso como una
            acción responsable. La colección de herramientas es secundaria a esa cadena.

            **Errores que evitaremos:** empezar por productos, automatizar un AS-IS defectuoso, borrar problemas de
            calidad sin contarlos, confundir visualización con acción, atribuir causalidad y confirmar cambios sin
            revisar el diff.

            ## Próximas sesiones

            > En la sesión 3 estudiaremos casos de uso de Big Data en las organizaciones y compararemos inteligencia
            > de negocios tradicional con BI apoyada por capacidades Big Data. Más adelante evolucionaremos el
            > blueprint de Compras Claras hacia un MVP reproducible con Docker.
            """
        ),
        md(
            """
            ## Correspondencia con los cuadernos de referencia

            | Contenido conservado | Ubicación en esta reconstrucción |
            |---|---|
            | definición y motivación de Big Data empresarial | decisión, proceso y ciclo analítico |
            | OLTP y OLAP | sección 3, como origen y consumo de la evidencia |
            | ETL | sección 4, contrastado con ELT mediante el orden, el lugar de transformación y dos recorridos aplicados |
            | Data Warehouse y Data Mart | sección 4, integrados en el flujo completo |
            | arquitectura empresarial `Images/2.1.png` | sección 5, cuatro dominios |
            | arquitecturas `Images/GCP/5.png` y `6.png` | sección 7, lectura por capacidades |
            | GCP y BigQuery históricos | retirados del cuerpo obligatorio; archivos originales intactos |
            | activación, cuentas, claves, videos y consultas antiguas | no se incluyen por seguridad, vigencia y alcance |
            | práctica de Git | sección 8 y laboratorio paso a paso |

            La reorganización conserva los conceptos esenciales y los usa dentro de una historia. No se modifican
            `Cuadernos/2_BigData.ipynb`, otras sesiones ni las imágenes originales.
            """
        ),
        md(
            f"""
            ## Referencias y recursos

            - [NIST Big Data Interoperability Framework — Definitions](https://doi.org/10.6028/NIST.SP.1500-1r2)
            - [NIST Big Data Reference Architecture](https://doi.org/10.6028/NIST.SP.1500-6r2)
            - [TOGAF Standard — The Open Group](https://publications.opengroup.org/standards/togaf)
            - [BPMN 2.0.2 — Object Management Group](https://www.omg.org/spec/BPMN/)
            - [CRISP-DM — IBM](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview)
            - [ETL y ELT — AWS](https://aws.amazon.com/es/what-is/etl/)
            - [Qué es ELT — Google Cloud](https://cloud.google.com/discover/what-is-elt)
            - [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)
            - [API Socrata de SECOP Integrado](https://dev.socrata.com/foundry/www.datos.gov.co/rpmr-utcd)
            - [Diagramas Mermaid en GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
            - [Editor web github.dev](https://docs.github.com/en/codespaces/the-githubdev-web-based-editor)
            - [Introducción a Codespaces](https://docs.github.com/en/codespaces/getting-started/quickstart)
            - [Control de código fuente en Codespaces](https://docs.github.com/en/codespaces/developing-in-a-codespace/using-source-control-in-your-codespace)
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
