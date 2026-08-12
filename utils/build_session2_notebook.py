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
LAB_REPO = "https://github.com/jazaineam1/BigData2026-Sesion2-Lab"
CODESPACES = "https://codespaces.new/jazaineam1/BigData2026-Sesion2-Lab?quickstart=1"


def hidden(cell, *tags):
    """Oculta celdas de soporte sin ocultar su resultado."""
    cell["metadata"]["tags"] = list(tags or ("hide-input",))
    cell["metadata"]["jupyter"] = {"source_hidden": True}
    cell["metadata"]["cellView"] = "form"
    return cell


def question_cell(numero, tema, contexto, pregunta, opciones, correcta, retro_ok, retro_bad):
    """Crea una pregunta visual autocorregible."""
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
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir el cuaderno en Google Colab">
            </a>

            <a href="{CODESPACES}" target="_blank"
               style="display:inline-block;background:#24292f;color:#fff;padding:8px 14px;border-radius:6px;text-decoration:none;margin-left:8px;">
              Abrir laboratorio en GitHub Codespaces
            </a>

            **Accesos:** [página del curso]({WEB_CURSO}) · [repositorio del laboratorio]({LAB_REPO})

            > El cuaderno es compatible con Colab para lectura y preguntas. La práctica colaborativa se realiza
            > en el repositorio asignado por GitHub Classroom, abierto en Codespaces.
            """
        ),
        md(
            """
            # Sesión 2 — Arquitectura empresarial, BPM y ciclo analítico de Big Data

            ## Universidad Central
            <div align="center">
              <img src="https://universidad.ucentral.edu.co/tulengua/wp-content/themes/tulengua/images/logo-ucentral.png"
                   width="340" alt="Logo de la Universidad Central">
            </div>

            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 2

            **Docente:** Julio Antonino Zainea Maya<br>
            **Periodo:** 2026-2S<br>
            **Duración:** 180 minutos — 90 de explicación y 90 de laboratorio<br>
            **Modalidad:** seis parejas, GitHub Classroom y GitHub Codespaces<br>
            **Última actualización:** 11 de agosto de 2026

            ### Ficha de la sesión

            | Campo | Valor |
            |---|---|
            | Caso profesional | Compras Claras — priorización de revisiones en contratación pública |
            | Datos y fuentes | Muestra estable de SECOP Integrado y API opcional |
            | Herramientas | Markdown, Mermaid, Git, GitHub, Codespaces y Python |
            | Evidencia final | Blueprint empresarial versionado y Pull Request revisado |
            | Continuidad | El blueprint será la entrada de la sesión 3 con Docker |
            """
        ),
        md(
            """
            ## Alcance, objetivos de aprendizaje y producto

            Al terminar podrás:

            1. explicar cómo la arquitectura empresarial alinea estrategia, procesos, información, aplicaciones y tecnología;
            2. diferenciar arquitectura empresarial, de datos y técnica de Big Data;
            3. representar un proceso AS-IS, reconocer actores, decisiones, cuellos de botella y métricas;
            4. proponer un proceso TO-BE apoyado por datos sin confundir automatización con mejora;
            5. aplicar el ciclo de captura, preparación, análisis, visualización y acción;
            6. distinguir ciclo del dato, ciclo analítico y CRISP-DM;
            7. traducir productos de nube en capacidades independientes del proveedor;
            8. usar rama, staging, commit, push y Pull Request en un flujo colaborativo inicial;
            9. comunicar qué permite y qué no permite concluir un perfil descriptivo de SECOP.

            **Producto verificable:** un blueprint con proceso AS-IS, arquitectura objetivo, ciclo analítico,
            interpretación de evidencia, dos commits —uno por estudiante— y un Pull Request revisado.
            """
        ),
        md(
            """
            ## Agenda y ruta de la sesión

            ### Momento 1 — Conceptos y herramientas, 90 minutos

            | Tiempo | Bloque | Producto intermedio |
            |---:|---|---|
            | 0–7 | Apertura y caso | Decisión profesional formulada |
            | 7–27 | Arquitectura empresarial | Cadena de trazabilidad |
            | 27–47 | Administración de procesos | Proceso AS-IS y métricas |
            | 47–65 | Ciclo analítico de Big Data | Mapa de cinco etapas |
            | 65–73 | Lectura crítica de GCP | Capacidades separadas de productos |
            | 73–88 | Git, GitHub y Codespaces | Flujo de entrega comprendido |
            | 88–90 | Transición | Roles asignados |

            ### Momento 2 — Aprender haciendo, 90 minutos

            | Tiempo | Actividad | Evidencia |
            |---:|---|---|
            | 90–100 | Abrir Codespaces y verificar entorno | Rama y versiones visibles |
            | 100–112 | Perfilar la muestra SECOP | Tres observaciones interpretadas |
            | 112–132 | Documentar proceso AS-IS | Diagrama, bottleneck y KPI |
            | 132–147 | Primer commit y relevo | Cambio publicado por estudiante A |
            | 147–160 | Arquitectura y ciclo analítico | Diagramas y matriz completos |
            | 160–170 | Segundo commit y validación | Cambio publicado por estudiante B |
            | 170–178 | Pull Request y revisión | CI verde y comentario cruzado |
            | 178–180 | Ticket de salida | Decisión, riesgo y siguiente paso |
            """
        ),
        md(
            """
            ## ¿Por qué importa esta sesión?

            En la sesión anterior aprendimos que Big Data no significa simplemente “un archivo grande”. Ahora
            aparece una pregunta más exigente: **¿cómo logramos que los datos, las herramientas y los equipos
            trabajen juntos para mejorar una decisión real?**

            Comprar tecnología sin comprender el proceso puede automatizar errores. Diseñar un modelo sin saber
            quién usará el resultado puede producir una predicción que nunca cambia una decisión. La arquitectura
            empresarial evita esa desconexión: empieza por el propósito, sigue el proceso y solo entonces asigna
            datos, aplicaciones y tecnología.

            **Pregunta de apertura:** ¿una colección de herramientas constituye por sí sola una arquitectura?
            Durante la sesión construiremos evidencia para responder que no: una arquitectura necesita relaciones,
            responsabilidades, restricciones y una decisión justificable.
            """
        ),
        md(
            """
            ## Preparación del entorno del cuaderno

            Ejecuta la siguiente celda en Colab o Jupyter. Solo comprueba versiones y prepara el componente visual
            de las preguntas; no crea recursos de nube, no solicita credenciales y no modifica tu computador.
            """
        ),
        hidden(
            code(
                """
                import sys
                import json
                import html as html_lib
                from IPython.display import HTML, display

                print("Python:", sys.version.split()[0])
                print("Entorno listo para las preguntas y la lectura guiada.")
                """
            ),
            "hide-input",
            "soporte-entorno",
        ),
        md(
            """
            **¿Qué nos dice esta salida?** Confirma que el cuaderno puede ejecutar su interactividad. La práctica
            de Git no ocurre en esta celda: se realizará más adelante en el Codespace del equipo, donde cada cambio
            tendrá autor, historial y revisión.
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
                    '''Muestra una pregunta autocorregible en Colab o Jupyter.'''
                    uid = f"pregunta-{numero}"
                    opciones_html = "".join(
                        f'''<label style="display:block;margin:8px 0;cursor:pointer;">
                        <input type="radio" name="{uid}" value="{i}"> {html_lib.escape(opcion)}
                        </label>'''
                        for i, opcion in enumerate(opciones)
                    )
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
            # Caso transversal — Compras Claras

            Una oficina de contratación pública consolida información tarde, encuentra fechas o estados
            incompletos y no puede decidir oportunamente qué contratos necesitan revisión prioritaria.

            **Pregunta empresarial:** ¿qué procesos contractuales deberían revisarse primero debido a duraciones
            atípicas, estados incompletos o problemas de calidad?

            **Decisión soportada:** priorizar una revisión humana y mejorar el proceso de seguimiento.

            Esta formulación es deliberada. El análisis puede ordenar casos para revisión; **no demuestra fraude,
            corrupción, incumplimiento ni causalidad**. Una alerta es el inicio de una investigación, no su conclusión.
            """
        ),
        md(
            """
            ## Datos y fuentes del caso

            La fuente principal es SECOP Integrado, publicada en Datos Abiertos Colombia. En el laboratorio usaremos
            una muestra local para que la disponibilidad de la API no determine el resultado de la clase.

            **Unidad de observación:** un proceso contractual registrado en la fuente consultada.

            ### Diccionario de variables de trabajo

            | Variable | Descripción | Uso en el caso |
            |---|---|---|
            | `id_del_proceso` | Identificador del proceso | Trazabilidad y control de duplicados |
            | `entidad` | Entidad compradora | Responsable y agrupación |
            | `departamento_entidad` | Ubicación territorial | Segmentación descriptiva |
            | `modalidad_de_contratacion` | Mecanismo contractual | Contexto del proceso |
            | `estado_del_procedimiento` | Estado operativo | Seguimiento y reglas de calidad |
            | `tipo_de_contrato` | Naturaleza del contrato | Comparación entre grupos |
            | `fecha_de_publicacion_del` | Fecha de publicación | Oportunidad y antigüedad |
            | `duracion` | Duración declarada | Priorización descriptiva |
            | `unidad_de_duracion` | Días, meses u otra unidad | Interpretación correcta de duración |
            | `precio_base` | Valor de referencia | Contexto económico, no prueba de riesgo |

            **Advertencia:** una fila de SECOP representa un registro publicado, no toda la realidad operativa del
            contrato. La calidad y actualización de la fuente deben formar parte del análisis.
            """
        ),
        md(
            """
            ---
            # Bloque 1 — Arquitectura empresarial: de la estrategia a la tecnología

            ## Definición formal e intuición

            **Definición de trabajo.** La arquitectura empresarial es un sistema coherente de principios, modelos
            y decisiones que describe cómo se organizan el negocio, la información, las aplicaciones y la tecnología
            para alcanzar objetivos concretos.

            **Intuición.** Es el plano de una ciudad, no una lista de edificios. Un plano explica relaciones,
            responsabilidades, restricciones y rutas. De la misma manera, una arquitectura explica por qué existe
            cada componente, a quién sirve y cómo contribuye al resultado.

            **Ejemplo manual.** Una tienda quiere reducir de 48 a 12 horas el tiempo para responder reclamos. Antes
            de comprar una herramienta debe identificar el proceso, los datos del reclamo, las aplicaciones que los
            contienen, la integración necesaria y la infraestructura donde operará la solución.

            **Error común:** dibujar productos tecnológicos primero y agregar el problema de negocio después.
            """
        ),
        md(
            """
            ## Lectura visual — Los cuatro dominios

            <div align="center">
              <img src="../Images/2.1.png" width="760"
                   alt="Arquitectura empresarial con dominios de negocio, información, aplicaciones y tecnología">
            </div>

            **¿Cómo se lee?** La arquitectura de negocio expresa misión, estrategia y procesos. La información
            define datos y significado. Las aplicaciones materializan capacidades. La tecnología ofrece cómputo,
            almacenamiento y comunicación. Ningún bloque funciona aislado.

            **Qué no debemos concluir:** la imagen no determina un proveedor, un producto o una implementación.
            Sirve para organizar preguntas antes de seleccionar herramientas.
            """
        ),
        md(
            """
            ## Los dominios aplicados a Compras Claras

            | Dominio | Pregunta que responde | Ejemplo en el caso |
            |---|---|---|
            | Negocio | ¿Qué objetivo y decisión se mejoran? | Priorizar revisiones y reducir consolidación tardía |
            | Información | ¿Qué datos significan qué? | Proceso, entidad, estado, fecha, duración y valor |
            | Aplicaciones | ¿Qué capacidades manipulan los datos? | SECOP, perfilador, reglas, visualización y alertas |
            | Tecnología | ¿Dónde se ejecuta y almacena? | API, archivos, motor analítico y canal de consumo |

            Gobierno, seguridad, observabilidad y costos atraviesan los cuatro dominios. No son una caja que se
            agrega al final: condicionan quién puede usar el dato, cómo se audita y cuánto cuesta sostenerlo.
            """
        ),
        question_cell(
            1,
            "Propósito de la arquitectura empresarial",
            "La oficina quiere comprar un tablero antes de definir quién tomará la decisión y con qué proceso.",
            "¿Cuál es la primera corrección arquitectónica?",
            [
                "Elegir el proveedor con más servicios disponibles.",
                "Definir objetivo, decisión, proceso y métrica antes de seleccionar tecnología.",
                "Copiar una arquitectura de referencia sin modificarla.",
                "Cargar todos los datos disponibles para decidir después.",
            ],
            1,
            "La arquitectura comienza por el valor esperado y la decisión. Esa trazabilidad permite justificar luego datos, aplicaciones e infraestructura.",
            "Las otras opciones empiezan por tecnología o acumulación de datos. Sin una decisión y una métrica no es posible evaluar si la solución mejora el negocio.",
        ),
        md(
            """
            ## AS-IS, brecha y TO-BE

            - **AS-IS:** describe cómo funciona hoy el proceso, incluso con demoras, trabajo manual y duplicaciones.
            - **Brecha:** explica qué impide lograr el objetivo y qué riesgo produce.
            - **TO-BE:** propone cómo debería operar el proceso con responsabilidades y controles claros.

            En Compras Claras, el AS-IS consolida tarde y revisa de forma reactiva. La brecha es la ausencia de una
            validación oportuna y de criterios reproducibles. El TO-BE captura, valida, perfila, prioriza y presenta
            casos a una persona responsable de revisar.

            **Cadena de trazabilidad:** objetivo → capacidad → proceso → datos → aplicación → tecnología → KPI.
            Si un componente no puede vincularse con esta cadena, debemos cuestionar por qué existe.
            """
        ),
        question_cell(
            2,
            "Dominios arquitectónicos",
            "El equipo define reglas para detectar estados vacíos, fechas inválidas y unidades de duración inconsistentes.",
            "¿En qué dominio se define principalmente el significado y la calidad de esos elementos?",
            [
                "Arquitectura de información.",
                "Arquitectura de tecnología.",
                "Arquitectura física del edificio.",
                "Arquitectura de interfaz visual exclusivamente.",
            ],
            0,
            "Las reglas describen semántica, calidad y uso de los datos; por eso pertenecen principalmente al dominio de información, aunque luego una aplicación las ejecute.",
            "Es tentador elegir tecnología porque allí corre la validación, pero primero debe definirse qué significa dato válido. Implementación y significado no son la misma decisión.",
        ),
        md(
            """
            ## Puente entre operación y analítica: OLTP, OLAP, ETL, Data Warehouse y Data Mart

            | Concepto | Definición | Intuición | Ejemplo |
            |---|---|---|---|
            | OLTP | Sistema optimizado para registrar transacciones | Caja registradora del negocio | Publicar y actualizar un proceso contractual |
            | OLAP | Sistema optimizado para consultas analíticas | Mesa de análisis histórico | Comparar duraciones por entidad y modalidad |
            | ETL | Extraer, transformar y cargar | Mover y preparar datos con reglas | Convertir fechas y unidades antes de resumir |
            | Data Warehouse | Repositorio integrado e histórico | Memoria analítica compartida | Historial consolidado de contratación |
            | Data Mart | Subconjunto orientado a un área | Vista especializada de esa memoria | Información para la oficina de seguimiento |

            **Ejemplo pequeño:** registrar una adjudicación pertenece a la operación. Calcular tendencias de varios
            años pertenece a la analítica. ETL conecta ambos mundos sin ejecutar consultas pesadas sobre el sistema
            que sostiene la operación cotidiana.

            **Error común:** pensar que OLTP y OLAP son productos específicos. Son patrones de carga y propósito;
            diferentes tecnologías pueden implementarlos.
            """
        ),
        question_cell(
            3,
            "Trazabilidad entre negocio y tecnología",
            "El objetivo es reducir el tiempo entre la aparición de un dato incompleto y su revisión humana.",
            "¿Qué indicador conserva mejor la trazabilidad con ese objetivo?",
            [
                "Número total de servicios ofrecidos por el proveedor de nube.",
                "Color elegido para el tablero.",
                "Tiempo medio desde la detección de la alerta hasta su revisión.",
                "Cantidad de columnas originales del archivo.",
            ],
            2,
            "El tiempo detección–revisión mide directamente la capacidad que se quiere mejorar y conecta arquitectura, proceso y valor operativo.",
            "Las demás métricas describen tecnología, apariencia o estructura, pero no indican si la oficina revisa antes los casos que necesitan atención.",
        ),
        md(
            """
            ---
            # Bloque 2 — Administración de procesos de negocio

            ## Definición formal, intuición y ejemplo manual

            **BPM — Business Process Management** es una disciplina para identificar, descubrir, modelar, analizar,
            rediseñar, implementar, medir y mejorar continuamente procesos de negocio.

            **Intuición.** Un proceso es una promesa repetible: recibe una entrada, coordina trabajo entre actores y
            produce un resultado para alguien. BPM permite ver dónde esa promesa se demora, se duplica o falla.

            **Ejemplo de reembolso.** Un cliente radica una solicitud; un analista valida soportes; si faltan
            documentos, solicita corrección; si están completos, calcula y aprueba el pago. El análisis debe medir
            tanto tiempo total como devoluciones por información incompleta.

            **Error común:** automatizar cada paso del proceso actual sin preguntar si algunos pasos sobran o deben
            cambiar de responsable.
            """
        ),
        md(
            """
            ## Proceso, tarea, procedimiento y proyecto

            | Término | Pregunta práctica | Ejemplo |
            |---|---|---|
            | Proceso | ¿Qué flujo repetible entrega valor? | Gestionar un proceso contractual |
            | Tarea | ¿Qué acción puntual realiza un actor? | Validar una fecha de publicación |
            | Procedimiento | ¿Qué instrucciones regulan la acción? | Lista de controles antes de publicar |
            | Proyecto | ¿Qué esfuerzo temporal produce un cambio? | Implementar Compras Claras |

            Un proyecto puede transformar un proceso, pero no se repite indefinidamente. Una tarea pertenece a un
            proceso, pero no explica por sí sola el resultado de extremo a extremo.
            """
        ),
        question_cell(
            4,
            "Proceso frente a tarea",
            "Una persona convierte la columna de fecha a un formato estándar dentro del flujo de seguimiento.",
            "¿Cómo debe clasificarse esa actividad?",
            [
                "Como toda la arquitectura empresarial.",
                "Como una tarea dentro del proceso de preparación y seguimiento.",
                "Como un proyecto permanente.",
                "Como el objetivo estratégico completo.",
            ],
            1,
            "Convertir una fecha es una acción puntual. Cobra sentido cuando se ubica dentro del proceso, con entrada, responsable, regla y salida definidas.",
            "El error consiste en confundir una acción técnica con el flujo o el objetivo completo. Una tarea aislada no entrega por sí sola el valor empresarial.",
        ),
        md(
            """
            ## Ciclo BPM y notación mínima

            1. **Identificar:** seleccionar el proceso relacionado con el objetivo.
            2. **Descubrir:** documentar el AS-IS con evidencia, no con supuestos.
            3. **Analizar:** localizar esperas, retrabajos, fallos y riesgos.
            4. **Rediseñar:** proponer el TO-BE y sus controles.
            5. **Implementar:** cambiar responsabilidades, reglas y herramientas.
            6. **Monitorear:** observar KPI y volver a mejorar.

            Para leer un modelo usaremos cuatro elementos inspirados en BPMN:

            - **evento:** algo inicia, interrumpe o termina el flujo;
            - **tarea:** trabajo realizado por una persona o sistema;
            - **gateway:** decisión que abre rutas alternativas;
            - **carril:** actor responsable de las actividades.

            Mermaid permite representar el flujo en Markdown, pero no sustituye un modelador ni un motor BPMN.
            """
        ),
        md(
            """
            ## Caso aplicado — Proceso AS-IS de Compras Claras

            ```mermaid
            flowchart LR
              subgraph Entidad[Entidad contratante]
                A([Necesidad]) --> B[Preparar y publicar]
                B --> C[Evaluar ofertas]
                C --> D[Formalizar contrato]
                D --> E[Reportar ejecución]
              end
              subgraph Plataforma[SECOP]
                E --> F[Actualizar registro]
              end
              subgraph Seguimiento[Oficina de seguimiento]
                F --> G[Consolidar archivos manualmente]
                G --> H{¿Información suficiente?}
                H -- No --> I[Solicitar corrección]
                I --> E
                H -- Sí --> J[Revisar casos]
              end
              J --> K([Cierre])
            ```

            **¿Cómo se lee?** El proceso genera datos durante la operación, pero la oficina solo los convierte en
            evidencia después de una consolidación manual. El gateway revela retrabajo cuando la información es
            insuficiente. El cuello de botella no se resuelve solamente instalando un tablero.

            **Qué todavía no sabemos:** el diagrama formula una hipótesis de proceso. Antes de rediseñar debemos
            medir tiempos, devoluciones y causas reales con responsables del proceso.
            """
        ),
        question_cell(
            5,
            "Gateway y decisión",
            "Después de consolidar, la oficina debe decidir si la información es suficiente para continuar.",
            "¿Qué elemento representa mejor esa bifurcación?",
            [
                "Un evento final sin salida.",
                "Una tarea de almacenamiento.",
                "Un gateway con rutas Sí y No.",
                "Un carril sin responsable.",
            ],
            2,
            "El gateway expresa una condición que cambia la ruta. Las etiquetas Sí y No permiten entender qué ocurre en cada resultado.",
            "Una tarea ejecuta trabajo y un evento marca una ocurrencia; ninguno expresa por sí solo las rutas alternativas producidas por una condición.",
        ),
        md(
            """
            ## Métricas para no mejorar a ciegas

            - **Tiempo de ciclo:** desde la aparición del registro hasta su revisión.
            - **Porcentaje de registros incompletos:** evidencia la calidad de entrada.
            - **Tasa de retrabajo:** proporción de casos devueltos por corrección.
            - **Tiempo de espera:** lapso en que el caso no está siendo trabajado.
            - **Cumplimiento de SLA:** porcentaje atendido dentro del objetivo acordado.

            Un KPI debe tener fórmula, fuente, responsable, frecuencia y meta. “Mejorar la eficiencia” no es una
            métrica; “revisar 90 % de alertas en menos de 24 horas” sí puede verificarse.
            """
        ),
        question_cell(
            6,
            "Selección de KPI",
            "La oficina quiere reducir las devoluciones causadas por registros incompletos.",
            "¿Qué KPI permite evaluar directamente esa mejora?",
            [
                "Número de colores del dashboard.",
                "Porcentaje de registros devueltos por información incompleta.",
                "Cantidad total de herramientas conocidas por el equipo.",
                "Tamaño del logotipo institucional.",
            ],
            1,
            "La tasa de devolución mide el resultado que se quiere reducir. Además puede desagregarse por causa, etapa y responsable para orientar una mejora.",
            "Las otras opciones son observables, pero no representan el desempeño del proceso. Un KPI debe estar conectado con el objetivo y una acción posible.",
        ),
        md(
            """
            ---
            # Bloque 3 — Ciclo analítico de Big Data

            ## Tres ciclos que no deben confundirse

            | Enfoque | Pregunta central | Alcance |
            |---|---|---|
            | Ciclo de vida del dato | ¿Cómo se crea, almacena, comparte, conserva y elimina? | Gestión del activo durante su existencia |
            | Ciclo analítico | ¿Cómo se transforma dato crudo en conocimiento accionable? | Captura, preparación, análisis, visualización y acción |
            | CRISP-DM | ¿Cómo se conduce iterativamente un proyecto de minería de datos? | Negocio, datos, preparación, modelado, evaluación y despliegue |

            Los modelos son complementarios. Esta sesión usa como columna vertebral las cinco etapas descritas por
            NIST para Big Data, porque terminan explícitamente en una acción empresarial.
            """
        ),
        question_cell(
            7,
            "Ciclo del dato y ciclo analítico",
            "La organización define que los registros deben archivarse cinco años y luego eliminarse de forma segura.",
            "¿Qué ciclo aborda directamente esa decisión?",
            [
                "Ciclo de vida del dato.",
                "Solamente la etapa de visualización.",
                "Únicamente el modelado estadístico.",
                "Diseño de la interfaz del dashboard.",
            ],
            0,
            "Retención, archivo y eliminación pertenecen a la gestión del dato durante su existencia, aunque también condicionan qué análisis pueden realizarse.",
            "El ciclo analítico usa datos para producir conocimiento, pero una política de conservación responde directamente al ciclo de vida y al gobierno del dato.",
        ),
        md(
            """
            ## Las cinco etapas del ciclo analítico

            ```mermaid
            flowchart LR
              A[1. Captura] --> B[2. Preparación]
              B --> C[3. Análisis]
              C --> D[4. Visualización]
              D --> E[5. Acción]
              E -. aprendizaje y nuevas preguntas .-> A
              G[Gobierno · seguridad · privacidad · calidad] --- A
              G --- B
              G --- C
              G --- D
              G --- E
            ```

            1. **Captura:** reunir y conservar datos, generalmente en su forma original.
            2. **Preparación:** limpiar, organizar, integrar y documentar.
            3. **Análisis:** producir conocimiento mediante reglas, estadística o modelos.
            4. **Visualización:** comunicar evidencia para que otra persona pueda comprenderla.
            5. **Acción:** usar el conocimiento para generar valor, cambiar un proceso o tomar una decisión.

            **Idea central:** el dashboard no es el final. Si nadie actúa, el ciclo quedó incompleto.
            """
        ),
        question_cell(
            8,
            "Orden del ciclo analítico",
            "La muestra contiene fechas con formatos distintos y unidades de duración incompatibles.",
            "¿Qué debe ocurrir antes de comparar duraciones?",
            [
                "Publicar de inmediato una alerta.",
                "Preparar y normalizar fechas y unidades con reglas documentadas.",
                "Eliminar aleatoriamente la mitad de los registros.",
                "Elegir colores para el tablero.",
            ],
            1,
            "Comparar requiere primero datos comparables. La preparación convierte fechas y unidades con reglas verificables y conserva evidencia de los cambios.",
            "Analizar antes de normalizar puede producir rankings falsos. La velocidad no compensa una unidad o una fecha interpretada incorrectamente.",
        ),
        md(
            """
            ## Aplicación al caso Compras Claras

            | Etapa | Entrada | Actividad | Resultado | Pregunta de control |
            |---|---|---|---|---|
            | Captura | API y muestra SECOP | Extraer campos y registrar fecha | Archivo crudo trazable | ¿Sabemos cuándo y cómo se obtuvo? |
            | Preparación | Fechas, estados y duraciones | Validar, tipar y normalizar | Datos comparables | ¿Qué filas cambiaron o se excluyeron? |
            | Análisis | Datos preparados | Perfilar calidad y priorizar revisión | Lista explicable | ¿La regla puede auditarse? |
            | Visualización | Métricas y casos | Comunicar patrones y límites | Evidencia comprensible | ¿El responsable entiende por qué aparece una alerta? |
            | Acción | Alertas priorizadas | Revisión humana y corrección | Proceso mejorado | ¿Se redujo tiempo o retrabajo? |

            **Conclusión descriptiva guiada:** una lista priorizada reduce el universo que una persona debe revisar,
            pero no reemplaza la verificación documental ni prueba una irregularidad.
            """
        ),
        question_cell(
            9,
            "Visualización frente a acción",
            "El tablero ordena procesos por duración, pero nadie tiene asignada la revisión de las alertas.",
            "¿Qué parte falta para completar el ciclo?",
            [
                "Agregar más gráficos del mismo indicador.",
                "Definir responsable, criterio, plazo y evidencia de la acción.",
                "Aumentar el tamaño del archivo.",
                "Ocultar la regla de priorización.",
            ],
            1,
            "La acción necesita dueño, criterio, plazo y trazabilidad. Solo entonces puede medirse si el conocimiento cambió el proceso.",
            "Más visualizaciones no resuelven la ausencia de responsabilidad. Un resultado analítico sin mecanismo de uso sigue siendo información no operacionalizada.",
        ),
        md(
            """
            ## Batch, tiempo cercano al real y streaming

            - **Batch:** procesa grupos de datos en intervalos; puede ser suficiente para un informe semanal.
            - **Tiempo cercano al real:** procesa con una demora pequeña y explícita; puede apoyar alertas periódicas.
            - **Streaming:** procesa eventos de forma continua; requiere justificar latencia, costo y complejidad.

            Compras Claras no necesita streaming solo porque trata Big Data. Si la decisión se toma diariamente,
            un procesamiento batch bien gobernado puede ser más simple y suficiente. La frecuencia se deriva del
            tiempo de decisión, no de una moda tecnológica.
            """
        ),
        md(
            """
            ---
            # Bloque 4 — Lectura crítica de una arquitectura de GCP

            ## Imagen histórica 1 — Plataforma analítica

            <div align="center">
              <img src="../Images/GCP/5.png" width="820"
                   alt="Diagrama histórico de productos de Google Cloud organizados por capacidades analíticas">
            </div>

            **¿Cómo se lee?** Las columnas representan capacidades: ingesta, procesamiento, almacenamiento,
            análisis y consumo. Los productos son implementaciones posibles dentro de esas capacidades.

            **Advertencia de vigencia:** la lámina se conserva como recurso histórico. Antes de usar cualquier
            producto en una solución actual deben verificarse nombre, disponibilidad, región, precio y estado del
            servicio en la documentación oficial.
            """
        ),
        md(
            """
            ## Imagen histórica 2 — Arquitectura referencial

            <div align="center">
              <img src="../Images/GCP/6.png" width="820"
                   alt="Arquitectura referencial histórica con ingesta, procesamiento, analítica, consumo y seguridad">
            </div>

            **Lectura docente.** El diagrama es más útil si primero reemplazamos cada marca por una capacidad:

            | Producto mostrado | Capacidad que debemos conservar |
            |---|---|
            | Cloud Storage | Almacenamiento de objetos |
            | Dataflow | Procesamiento y transformación escalable |
            | BigQuery | Consulta analítica y almacén de datos |
            | Composer | Orquestación de flujos |
            | Looker / interfaz BI | Comunicación y consumo |
            | IAM y controles | Acceso, seguridad y gobierno |

            Esta traducción evita que la arquitectura quede bloqueada a un nombre comercial y permite comparar
            alternativas mediante requisitos de negocio, datos, latencia, seguridad y costo.
            """
        ),
        question_cell(
            10,
            "Capacidad frente a producto",
            "Una arquitectura histórica asigna Cloud Storage para conservar archivos crudos.",
            "¿Qué debe permanecer estable si la organización cambia de proveedor?",
            [
                "El logotipo y el nombre comercial exacto.",
                "La capacidad de almacenar objetos con durabilidad, acceso y gobierno definidos.",
                "La ubicación visual de la caja en la diapositiva.",
                "La obligación de usar todos los productos del diagrama.",
            ],
            1,
            "La capacidad expresa lo que la arquitectura necesita. El producto puede cambiar si otra alternativa satisface durabilidad, acceso, gobierno, integración y costo.",
            "Confundir capacidad con marca crea dependencia innecesaria. Una referencia no obliga a desplegar todos sus componentes ni garantiza que sigan vigentes.",
        ),
        md(
            """
            ## Gobierno y seguridad no son un paso final

            Para cada componente debemos responder:

            - ¿quién es dueño del dato y quién puede acceder?;
            - ¿qué información podría afectar a personas o entidades?;
            - ¿cómo se registran origen, transformaciones y versiones?;
            - ¿qué ocurre si el dato llega tarde, duplicado o incompleto?;
            - ¿cómo se observan costos, fallos y tiempos de ejecución?;
            - ¿cuándo se archiva o elimina la información?

            En esta sesión no se crean cuentas, tarjetas, recursos, roles amplios ni archivos JSON de credenciales.
            La práctica se concentra en diseñar y justificar antes de desplegar.
            """
        ),
        question_cell(
            11,
            "Controles transversales",
            "El equipo decide agregar seguridad únicamente después de terminar el pipeline y el dashboard.",
            "¿Qué problema tiene esa decisión?",
            [
                "Ninguno: la seguridad siempre se instala al final.",
                "Seguridad, privacidad y gobierno deben condicionar captura, preparación, análisis, visualización y acción.",
                "Solo importa la seguridad del color del gráfico.",
                "El gobierno sustituye todas las responsabilidades humanas.",
            ],
            1,
            "Los controles atraviesan todo el ciclo: determinan qué se captura, quién accede, cómo se transforma y qué decisiones están permitidas.",
            "Agregar controles al final puede exigir rediseñar datos, permisos y flujos. Tampoco elimina la responsabilidad humana sobre el uso del resultado.",
        ),
        md(
            """
            ---
            # Bloque 5 — Git, GitHub y Codespaces como herramienta de arquitectura

            ## Tres herramientas diferentes

            - **Git** registra versiones, compara cambios y administra ramas en el repositorio.
            - **GitHub** aloja el repositorio y facilita Pull Requests, revisión y automatización.
            - **Codespaces** ofrece un entorno de desarrollo en el navegador, asociado al repositorio.

            En Codespaces el repositorio de origen utiliza autenticación integrada por HTTPS. Para esta actividad
            no es necesario generar claves SSH. En una instalación local, SSH puede estudiarse después como una
            alternativa de autenticación.

            **Por qué importa para arquitectura:** un diagrama sin historial puede cambiar sin explicación. Un
            blueprint versionado permite conocer quién propuso una decisión, qué se modificó y qué revisión recibió.
            """
        ),
        md(
            """
            ## Del archivo al Pull Request

            ```mermaid
            flowchart LR
              A[Working tree: editas] -->|git add archivo| B[Staging: eliges]
              B -->|git commit| C[Repositorio local: registras]
              C -->|git push| D[GitHub: publicas la rama]
              D -->|Pull Request| E[Revisión e integración]
            ```

            **Intuición:** `git status` observa, `git diff` compara, `git add` selecciona, `git commit` registra y
            `git push` publica. Hacer `git add` no crea un commit y hacer `push` no integra automáticamente en `main`.

            **Error común:** usar `git add .` sin revisar. En la sesión agregaremos archivos concretos para evitar
            incluir resultados temporales, credenciales o cambios ajenos.
            """
        ),
        md(
            """
            ## Mini fichas de los comandos nuevos

            **Función usada: `git status`**

            - Para qué sirve: muestra rama y cambios del repositorio.
            - Parámetros usados: ninguno.
            - Qué devuelve: archivos modificados, preparados o no rastreados.
            - Cómo interpretar: permite decidir qué revisar antes de registrar.

            **Función usada: `git switch -c entrega/sesion2`**

            - Para qué sirve: crea y activa una rama de trabajo.
            - Parámetros usados: `-c` y nombre de rama.
            - Qué devuelve: confirmación del cambio de rama.
            - Cómo interpretar: el trabajo queda aislado de `main` hasta su revisión.

            **Función usada: `git diff`**

            - Para qué sirve: compara el contenido modificado.
            - Parámetros usados: ninguno para cambios no preparados.
            - Qué devuelve: líneas agregadas y eliminadas.
            - Cómo interpretar: valida que el cambio diga exactamente lo que el equipo pretende.

            **Función usada: `git add archivo`**

            - Para qué sirve: selecciona un archivo para el próximo commit.
            - Qué devuelve: normalmente no imprime nada si funciona.
            - Cómo interpretar: el archivo pasa a staging, pero todavía no existe un commit.

            **Función usada: `git commit -m "mensaje"`**

            - Para qué sirve: registra una versión con propósito.
            - Qué devuelve: identificador y resumen del commit.
            - Cómo interpretar: la historia local contiene un punto de control auditable.

            **Función usada: `git push -u origin entrega/sesion2`**

            - Para qué sirve: publica la rama y configura su seguimiento remoto.
            - Qué devuelve: confirmación del remoto y enlace sugerido para el PR.
            - Cómo interpretar: el cambio ya puede revisarse en GitHub, pero aún no está integrado.
            """
        ),
        question_cell(
            12,
            "Estados de Git",
            "El estudiante editó `docs/01_proceso_as_is.md` y ejecutó `git add docs/01_proceso_as_is.md`, pero todavía no hizo commit.",
            "¿En qué estado se encuentra el cambio?",
            [
                "Ya está integrado en `main`.",
                "Está en staging, seleccionado para el próximo commit.",
                "Ya fue publicado en GitHub.",
                "Fue eliminado del repositorio.",
            ],
            1,
            "`git add` mueve el cambio a staging. El siguiente paso es revisar y crear un commit; después podrá publicarse con push.",
            "Editar, preparar, registrar y publicar son estados distintos. Sin commit no existe todavía un punto de control en la historia del repositorio.",
        ),
        md(
            f"""
            ---
            # Laboratorio de 90 minutos — Blueprint de Compras Claras

            Usa el enlace de GitHub Classroom entregado por el docente. Después de aceptar la actividad, abre el
            Codespace del repositorio de tu pareja. El repositorio de referencia está en [este enlace]({LAB_REPO}).

            ## Roles y relevo

            - **Estudiante A — líder de proceso:** formula decisión, proceso AS-IS, cuello de botella y KPI.
            - **Estudiante B — líder de datos y arquitectura:** propone dominios, ciclo analítico y controles.
            - Ambos interpretan el perfil SECOP, revisan el resultado y responden por el blueprint completo.

            En la siguiente sesión los roles se intercambiarán.
            """
        ),
        md(
            """
            ## Caso 1 — Verificar el entorno y leer evidencia

            En la terminal del Codespace:

            ```bash
            python --version
            git --version
            git status
            git branch --show-current
            python scripts/perfilar_secop.py --input data/secop_muestra.csv
            ```

            **Qué observar:** total de filas, identificadores duplicados, campos faltantes, distribución de estados,
            duraciones normalizadas y casos priorizados. Escribe tres observaciones en
            `resultados/perfil_secop.md`, incluyendo una limitación por observación.

            **Qué no concluir:** un valor alto o un dato faltante no prueba irregularidad. Indica un caso que puede
            requerir validación de contexto o calidad.
            """
        ),
        md(
            """
            ## Caso 2 — Proceso y primer commit

            Estudiante A:

            ```bash
            git switch -c entrega/sesion2
            # Edita docs/01_proceso_as_is.md y resultados/perfil_secop.md
            git diff
            git add docs/01_proceso_as_is.md resultados/perfil_secop.md
            git commit -m "Documenta proceso actual de contratación"
            git push -u origin entrega/sesion2
            ```

            **Criterio de éxito:** el diagrama debe mostrar actores, inicio, tareas, una decisión, cierre, cuello de
            botella y dos KPI con fórmula o definición operativa.
            """
        ),
        md(
            """
            ## Caso 3 — Arquitectura, ciclo y segundo commit

            Estudiante B, desde su propio Codespace:

            ```bash
            git fetch origin
            git switch --track origin/entrega/sesion2
            git pull --ff-only
            # Edita arquitectura y ciclo analítico
            git diff
            git add docs/02_arquitectura_objetivo.md docs/03_ciclo_analitico.md
            git commit -m "Propone arquitectura y ciclo analítico"
            git push
            git log --oneline --decorate -5
            ```

            **Criterio de éxito:** cada componente debe vincularse con una decisión, proceso, dato o control. La
            matriz del ciclo debe terminar en una acción humana medible.
            """
        ),
        md(
            """
            ## Validación, Pull Request y revisión

            ```bash
            python scripts/validar_entrega.py
            ```

            Después:

            1. abre el Pull Request desde la interfaz de GitHub;
            2. explica qué cambió, por qué y cómo se verificó;
            3. confirma que los diagramas Mermaid se renderizan;
            4. solicita la revisión de tu compañero;
            5. deja al menos un comentario sustantivo y atiende cualquier corrección;
            6. comprueba que GitHub Actions termine en verde.

            **Si la API falla:** la muestra local permite completar la actividad. **Si Actions se demora:** conserva
            la salida del validador local. **Si Codespaces no está disponible:** usa un Codespace por pareja y agrega
            coautoría al commit del relevo.
            """
        ),
        md(
            """
            ## Estructura de la entrega

            ```text
            README.md
            data/secop_muestra.csv
            scripts/perfilar_secop.py
            scripts/validar_entrega.py
            resultados/perfil_secop.md
            docs/01_proceso_as_is.md
            docs/02_arquitectura_objetivo.md
            docs/03_ciclo_analitico.md
            .github/pull_request_template.md
            .github/workflows/validar-entrega.yml
            ```

            La matriz del ciclo tendrá: etapa, entrada, actividad, responsable, artefacto, capacidad o herramienta,
            control y métrica de éxito.
            """
        ),
        md(
            """
            ## Rúbrica del hito

            | Criterio | Peso |
            |---|---:|
            | Problema, decisión y alcance empresarial | 15 |
            | Proceso AS-IS, actores, cuello de botella y KPI | 20 |
            | Arquitectura objetivo y trazabilidad entre capas | 25 |
            | Ciclo analítico, controles y responsables | 20 |
            | Interpretación de evidencia y límites | 10 |
            | Flujo Git, commits, PR y revisión | 10 |

            ### Lista de control mínima

            - [ ] Rama distinta de `main`.
            - [ ] Dos commits atribuibles, uno por estudiante.
            - [ ] Pull Request con descripción y revisión cruzada.
            - [ ] CI verde y diagramas renderizados.
            - [ ] No quedan marcadores de plantilla.
            - [ ] No hay claves, tokens, contraseñas ni datos personales agregados.
            - [ ] Las conclusiones son descriptivas y declaran sus límites.
            """
        ),
        md(
            """
            ## Ticket de salida individual

            Responde en un comentario del Pull Request:

            1. ¿Qué decisión empresarial soporta su arquitectura?
            2. ¿Cuál es el mayor cuello de botella del AS-IS y con qué KPI lo medirán?
            3. ¿Qué riesgo de calidad, seguridad o gobierno sigue abierto?
            4. ¿Qué componente tendría sentido contenerizar en la sesión 3 y por qué?

            La cuarta respuesta es una hipótesis. En esta sesión no se ejecuta Docker ni se escribe un Dockerfile.
            """
        ),
        md(
            """
            ---
            # Cierre de la sesión

            ## Recapitulación

            - La arquitectura empresarial conecta estrategia, procesos, información, aplicaciones y tecnología.
            - BPM permite descubrir, analizar, rediseñar y medir procesos, no solo automatizarlos.
            - El ciclo analítico termina en acción y aprendizaje, no en un gráfico.
            - Gobierno, seguridad, privacidad, calidad y costos atraviesan todos los componentes.
            - Git convierte el blueprint en un artefacto con historia, autoría y revisión.
            - SECOP permite describir y priorizar casos; no permite acusar ni demostrar causalidad por sí solo.

            ## Idea más importante

            **Toda tecnología debe justificarse desde una decisión y todo resultado analítico debe regresar a un
            proceso con responsable, control y métrica.**

            ## Errores comunes

            1. empezar por productos en lugar de empezar por el objetivo;
            2. confundir tarea, proceso y proyecto;
            3. automatizar un AS-IS defectuoso sin rediseñarlo;
            4. presentar un dashboard sin responsable de actuar;
            5. interpretar una alerta descriptiva como prueba de irregularidad;
            6. hacer `git add .` o publicar secretos sin revisar el diff.

            ## Próxima sesión

            Atenderemos comentarios del Pull Request y usaremos Docker para convertir una parte del blueprint en
            un componente reproducible. La arquitectura diseñada hoy será el criterio para decidir qué contenerizar.
            """
        ),
        md(
            """
            ## Mapa de continuidad del material fuente

            | Contenido existente | Ubicación actual |
            |---|---|
            | Arquitectura empresarial y cuatro dominios | Bloque 1 y `Images/2.1.png` |
            | BPM y ejemplo de reembolsos | Bloque 2 |
            | Ciclo de vida y caso SECOP | Bloque 3 y laboratorio |
            | OLTP, OLAP, ETL, Data Warehouse y Data Mart | Puente entre operación y analítica |
            | Cómputo en nube y datacenter | Dominio tecnológico y anexo visual |
            | Mapa de productos GCP | Lectura crítica con `Images/GCP/5.png` |
            | Arquitectura referencial GCP | Lectura crítica con `Images/GCP/6.png` |
            | Capturas de creación y exploración de GCP | Anexo visual histórico |
            | Consultas BigQuery y BigQuery ML | Extensión opcional de lectura |
            | Videos introductorios | Anexo de videos conservados |
            | Proyecto de curso de `2_BigData.ipynb` | Hito semestral versionado en Classroom |

            La reorganización conserva los conceptos y recursos visuales, pero evita convertir instrucciones
            históricas de facturación, roles amplios o claves descargables en una práctica obligatoria.
            """
        ),
        md(
            """
            ---
            # Anexo visual histórico de GCP

            Estas capturas se conservan porque documentan la evolución del material. Úsalas para reconocer la
            interfaz y discutir cómo envejece una guía. **No las tomes como instrucciones vigentes ni ingreses datos
            de pago durante esta sesión.**

            ## Capturas 1 a 4 — Activación y bienvenida históricas

            <div align="center">
              <img src="../Images/GCP/1.png" width="760" alt="Captura histórica 1 de introducción a GCP"><br><br>
              <img src="../Images/GCP/2.png" width="760" alt="Captura histórica 2 de introducción a GCP"><br><br>
              <img src="../Images/GCP/3.png" width="760" alt="Captura histórica 3 de introducción a GCP"><br><br>
              <img src="../Images/GCP/4.png" width="760" alt="Captura histórica 4 de introducción a GCP">
            </div>

            **Lectura crítica:** precios, créditos, interfaces y condiciones pueden cambiar. Verifica siempre la
            documentación vigente y las políticas institucionales antes de activar un servicio.
            """
        ),
        md(
            """
            ## Capturas 7 a 9 — Exploración y carga histórica en BigQuery

            <div align="center">
              <img src="../Images/GCP/7.png" width="760" alt="Captura histórica 7 de exploración de BigQuery"><br><br>
              <img src="../Images/GCP/8.png" width="760" alt="Captura histórica 8 de carga de datos en BigQuery"><br><br>
              <img src="../Images/GCP/9.png" width="760" alt="Captura histórica 9 de carga de datos en BigQuery">
            </div>

            **Lectura crítica:** la capacidad permanece —crear un dataset, describir esquema y consultar— aunque
            la ubicación de botones o los nombres visuales cambien.
            """
        ),
        md(
            """
            ## Capturas 10 a 12 — Identidades y claves: referencia, no práctica

            <div align="center">
              <img src="../Images/GCP/10.png" width="760" alt="Captura histórica 10 de cuentas de servicio"><br><br>
              <img src="../Images/GCP/11.png" width="760" alt="Captura histórica 11 de permisos de servicio"><br><br>
              <img src="../Images/GCP/12.png" width="760" alt="Captura histórica 12 de claves de servicio">
            </div>

            **Advertencia de seguridad:** no descargues claves JSON, no asignes roles amplios y no pegues secretos
            en notebooks o repositorios. Cuando una sesión futura requiera autenticación, se definirá un mecanismo
            de mínimo privilegio apropiado para el entorno.
            """
        ),
        md(
            """
            ## Videos conservados

            - [Introducción visual a centros de datos](https://www.youtube.com/watch?v=XZmGGAbHqa0)
            - [Recorrido histórico por Google Cloud](https://www.youtube.com/watch?v=4QyLYJkLgik)
            - [Conceptos de computación en la nube](https://www.youtube.com/watch?v=kd33UVZhnAA)

            Antes de usarlos en clase, confirma disponibilidad, duración y vigencia. Su función es ampliar la
            explicación; no reemplazan la definición, el ejemplo ni la interpretación docente.
            """
        ),
        md(
            """
            ## Extensión opcional — Consultas históricas de BigQuery

            El material anterior incluía consultas sobre Citi Bike y una carga de Saber 11. Se conservan como
            lectura para reconocer el tipo de pregunta que responde un almacén analítico. No se ejecutan en la
            sesión 2 y no requieren crear una cuenta.

            ```sql
            SELECT
              start_station_name,
              COUNT(*) AS num_trips
            FROM `bigquery-public-data.new_york.citibike_trips`
            GROUP BY start_station_name
            ORDER BY num_trips DESC
            LIMIT 10;
            ```

            **Interpretación esperada:** el resultado ordenaría estaciones por registros observados. No explicaría
            por qué una estación es popular ni garantizaría que los viajes representen toda la movilidad de la ciudad.

            BigQuery ML también permite crear modelos con SQL, pero modelar antes de comprender negocio, datos y
            proceso invertiría el orden pedagógico de esta sesión.
            """
        ),
        md(
            f"""
            ## Referencias y recursos

            - [NIST Big Data Interoperability Framework — definiciones y ciclo analítico](https://doi.org/10.6028/NIST.SP.1500-1r2)
            - [NIST Big Data Reference Architecture](https://doi.org/10.6028/NIST.SP.1500-6r2)
            - [TOGAF Standard — The Open Group](https://publications.opengroup.org/standards/togaf)
            - [BPMN 2.0.2 — Object Management Group](https://www.omg.org/spec/BPMN/)
            - [CRISP-DM — IBM](https://www.ibm.com/docs/en/spss-modeler/saas?topic=dm-crisp-help-overview)
            - [Crear diagramas Mermaid en GitHub](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)
            - [Introducción a dev containers y Codespaces](https://docs.github.com/en/codespaces/setting-up-your-project-for-codespaces/adding-a-dev-container-configuration/introduction-to-dev-containers)
            - [Autenticación de repositorios en Codespaces](https://docs.github.com/en/codespaces/troubleshooting/troubleshooting-authentication-to-a-repository)
            - [SECOP Integrado — Datos Abiertos Colombia](https://www.datos.gov.co/Gastos-Gubernamentales/SECOP-Integrado/rpmr-utcd)
            - [API Socrata de SECOP Integrado](https://dev.socrata.com/foundry/www.datos.gov.co/rpmr-utcd)
            - [Repositorio del laboratorio]({LAB_REPO})
            - [Página web del curso]({WEB_CURSO})

            **Nota de reproducibilidad:** registra fecha, fuente, campos y límite cuando actualices la muestra. La
            API es una fuente viva y sus resultados pueden cambiar.
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
