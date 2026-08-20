# -*- coding: utf-8 -*-
"""
Genera la Sesión 3 — Bases de datos documentales con MongoDB.

Decisiones de diseño (ver .local-docente/Plan_Sesiones_3_y_4_2026-2.md):

- Motor: MongoDB Community por tarball oficial dentro del runtime de Colab.
  No se usa apt ni systemctl: Colab no arranca con systemd y toda receta copiada
  de internet se rompe en esa línea. Respaldo probado: mongomock, que sí
  implementa las etapas de agregación que usa el laboratorio (montydb no).
- Datos: noticias de El Tiempo (sitemap XML + feed JSON por artículo). El CSV de
  SECOP es rectangular y no permite demostrar por qué existe un modelo
  documental; las noticias sí traen arreglos, anidamiento y campos ausentes.
- Caso conductor: Compras Claras. Las noticias son la señal externa que Laura
  cruza con los contratos para decidir qué revisar primero.
- Git sin instalar nada: todo el flujo ocurre en GitHub.com, porque el curso se
  dicta en computadores de la universidad donde Git puede no estar disponible.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.make_notebook import code, md, save, validate

OUTPUT = "Cuadernos/3_MongoDB_Documental.ipynb"
COLAB = (
    "https://colab.research.google.com/github/jazaineam1/BigData2026/"
    "blob/main/Cuadernos/3_MongoDB_Documental.ipynb"
)
WEB_CURSO = "https://jazaineam1.github.io/BigData2026/"
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"
DATOS_NOTICIAS = f"{RAW}/Datos/noticias_contratacion_2026.json"
DATOS_SECOP = f"{RAW}/Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv"
DATOS_CRUCE = f"{RAW}/Datos/entidades_en_noticias_2026.json"
DATOS_BANDEJA = f"{RAW}/Datos/bandeja_revision_2026.json"
DATOS_REFERENCIA = f"{RAW}/Datos/cruce_por_referencia_2026.json"
TOTAL_QUESTIONS = 8




def svg(nombre, alt):
    """
    Enlaza un SVG de assets/ desde el repositorio publicado.

    Se enlaza en vez de incrustar en base64 por dos razones: el cuaderno no
    carga con 6 KB de blob por diagrama, y el archivo sigue siendo editable
    sin decodificar nada. El precio es que el diagrama solo se ve si el
    repositorio ya esta publicado, asi que hay que hacer push antes de clase.

    Sin ancho fijo: el SVG trae su propio tamano y se adapta al de la celda.
    Fijar un ancho en pixeles es lo que lo desbordaba por la derecha.
    """
    ruta = os.path.join(ROOT, "assets", "diagrams", "session3", f"{nombre}.svg")
    if not os.path.exists(ruta):
        raise FileNotFoundError(ruta)
    url = f"{RAW}/assets/diagrams/session3/{nombre}.svg"
    return f'<img src="{url}" alt="{alt}" style="max-width:100%;height:auto;">'


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
    """
    Devuelve UNA sola celda: el widget interactivo.

    Antes eran dos —enunciado en Markdown y verificador oculto— para que la
    pregunta se leyera tambien en GitHub. El efecto en Colab, que es donde se
    dicta la clase, era que el estudiante veia el enunciado y las cuatro
    opciones dos veces seguidas, una debajo de la otra. Duplicar contenido
    cuesta mas que el beneficio de leerlo fuera de Colab.

    La respuesta sigue viajando codificada en base64: quien abra el cuaderno en
    GitHub vera el codigo, pero no la respuesta correcta de un vistazo.
    """
    import base64
    import json as _json

    carga = base64.b64encode(
        _json.dumps(
            {"c": correcta, "r": retro_opciones, "t": tema,
             "x": contexto, "p": pregunta},
            ensure_ascii=False,
        ).encode("utf-8")
    ).decode("ascii")

    return [
        hidden(
            code(
                f"""
                # Pregunta {numero} de {TOTAL_QUESTIONS} — {tema}
                # Enunciado, opciones y respuesta van codificados para que no se
                # lean de un vistazo al abrir el cuaderno fuera de Colab.
                pregunta_interactiva(
                    numero={numero},
                    opciones={opciones!r},
                    carga={carga!r},
                )
                """
            ),
            f"Pregunta {numero} de {TOTAL_QUESTIONS} — {tema}",
            "hide-input",
            "pregunta-interactiva",
        )
    ]


def soporte_cells():
    """Celdas de infraestructura del cuaderno: se ven plegadas en Colab."""
    return [
        hidden(
            code(
                """
                import json
                import html as html_lib
                from IPython.display import display, HTML

                TOTAL_QUESTIONS = 8
                print("Entorno listo. Ejecuta las celdas en orden.")
                """
            ),
            "Preparar entorno e interactividad",
            "hide-input",
            "soporte-entorno",
        ),
        hidden(
            code(
                """
                def pregunta_interactiva(numero, opciones, carga):
                    '''Muestra una pregunta autocorregible con explicación específica por opción.'''
                    import base64
                    datos = json.loads(base64.b64decode(carga).decode('utf-8'))
                    correcta, retro_opciones = datos['c'], datos['r']
                    tema, contexto, pregunta = datos['t'], datos['x'], datos['p']
                    uid = f"pregunta-{numero}"
                    opciones_html = "".join(
                        f'''<label style="display:block;margin:9px 0;cursor:pointer;">
                        <input type="radio" name="{uid}" value="{i}"> {html_lib.escape(opcion)}
                        </label>'''
                        for i, opcion in enumerate(opciones)
                    )
                    retro_json = json.dumps(retro_opciones, ensure_ascii=False)
                    bloque = f'''
                    <div style="border:2px solid #1565c0;border-radius:12px;padding:16px;margin:16px 0;background:#e3f2fd;color:#0d1b2a;">
                      <h3 style="color:#0d47a1;margin:0 0 10px;font-size:1.06rem;">Pregunta {numero} de {TOTAL_QUESTIONS} — {html_lib.escape(tema)}</h3>
                      <div style="background:#fff8d6;color:#3e2c00;border-left:5px solid #f9a825;padding:11px 13px;margin:10px 0;">
                        <strong>Contexto.</strong> {html_lib.escape(contexto)}
                      </div>
                      <p style="margin:12px 0 8px;"><strong>{html_lib.escape(pregunta)}</strong></p>
                      {opciones_html}
                      <button onclick="verificar_{numero}()" style="background:#1565c0;color:white;border:0;border-radius:6px;padding:9px 15px;cursor:pointer;">
                        Verificar respuesta
                      </button>
                      <div id="retro-{numero}" aria-live="polite" style="margin-top:12px;"></div>
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
    ]


def build_cells():
    cells = [
        md(
            f"""
            <a href="{COLAB}" target="_parent">
              <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Abrir el cuaderno en Google Colab">
            </a>

            **Acceso público:** [página del curso]({WEB_CURSO})

            > **No necesitas instalar nada en tu computador.** Ni MongoDB, ni Git, ni una cuenta de nube. Todo
            > ocurre dentro de esta pestaña y dentro de GitHub.com. Esto importa porque la clase se dicta en
            > computadores de la universidad donde no siempre hay permisos de instalación.

            ## Cómo usar este cuaderno

            **Este cuaderno es más largo de lo que se puede leer en una noche, y es a propósito.** No está
            hecho para que lo leas de corrido hoy: está hecho para que lo sigas hoy y lo consultes después.

            | | En clase | Después, en tu casa |
            |---|---|---|
            | **Sigues** | lo que dice el profesor y las celdas que ejecutas | — |
            | **Lees completo** | los recuadros de color y las tablas | los bloques largos de «🔎 Leamos el resultado» |
            | **Consultas** | la **hoja de trucos** del final, mientras escribes consultas | la rúbrica y los pasos de GitHub |
            | **Abres solo si te interesa** | — | todo lo que esté plegado en **▸ Ver más** |

            Las cuatro etiquetas que verás en los recuadros, y que significan siempre lo mismo:

            - **HAZ ESTO AHORA** — lo único que exige que hagas algo en ese momento.
            - **OJO** — un error frecuente o una advertencia.
            - **PARA LLEVAR** — la idea que quiero que te quede.
            - **MÁS ADELANTE** — se ve en otra sesión; hoy puedes ignorarlo sin costo.

            > **PARA LLEVAR.** Si en algún momento sientes que vas atrasado leyendo: no lo estás. Lo que
            > importa hoy es que **ejecutes, decidas e interpretes**. El texto queda aquí, y no se borra.
            """
        ),
        md(
            """
            # Sesión 3 — Cuando la tabla ya no cabe: bases de datos documentales con MongoDB

            ## Universidad Central
            <div align="center">
              <img src="https://universidad.ucentral.edu.co/tulengua/wp-content/themes/tulengua/images/logo-ucentral.png"
                   width="340" alt="Logo de la Universidad Central">
            </div>

            > ### Facultad de Ingeniería y Ciencias Básicas
            > ### Maestría en Analítica de Datos — BIG DATA (64491093), Grupo 1

            <img alt="MongoDB" width="190" src="https://upload.wikimedia.org/wikipedia/commons/9/93/MongoDB_Logo.svg">

            ![](https://img.shields.io/badge/motor-MongoDB%208.0-13AA52?style=flat-square)
            ![](https://img.shields.io/badge/entorno-Google%20Colab-F9AB00?style=flat-square)
            ![](https://img.shields.io/badge/datos-987%20noticias%20%C2%B7%20300.000%20procesos-1976D2?style=flat-square)
            ![](https://img.shields.io/badge/caso-Compras%20Claras-8C1D2F?style=flat-square)

            **Tema del PDA:** introducción a bases de datos documentales con MongoDB<br>
            **Finalidad formativa:** comprender el uso e implementación de bases de datos documentales<br>
            **Producción evaluable de hoy:** el hito de la sesión, construido con tu propia ejecución<br>
            **Caso conductor:** Compras Claras — priorizar la revisión de contratación pública<br>
            **Cómo transcurre:** primero conversamos y decidimos; después trabajas tú, con receso en medio<br>
            **Fecha:** 20 de agosto de 2026

            ## Ficha de la sesión

            | Campo | Descripción |
            |---|---|
            | pregunta profesional | ¿qué evidencia externa ayuda a Laura a decidir qué contrato revisar primero? |
            | fuentes | noticias de El Tiempo (sitemap XML + feed JSON) y muestra de contratación SECOP |
            | entorno | Colab, con MongoDB corriendo dentro de esta misma pestaña |
            | producto | una colección de documentos, tres consultas propias y una interpretación con límites |
            """
        ),
        md(
            """
            ## Objetivos de aprendizaje y producto

            Al terminar podrás:

            1. explicar con un caso propio por qué un modelo tabular se queda corto ante datos irregulares;
            2. nombrar las cuatro familias NoSQL y decir qué problema resuelve cada una;
            3. leer un documento JSON/BSON: campos, anidamiento, arreglos y `_id`;
            4. traducir una consulta entre SQL y MongoDB en los dos sentidos;
            5. explicar qué es una réplica, qué es un fragmento y qué garantía se cede al replicar;
            6. escribir consultas `find()` con filtro y proyección, y una agregación de cuatro etapas;
            7. interpretar un resultado diciendo también **qué no permite concluir**;
            8. cerrar en GitHub una propuesta abierta la semana pasada, sin usar la terminal.

            **Producto de la sesión.** Una colección `noticias` cargada en tu propia base, tres consultas escritas
            por ti con su interpretación, y el Pull Request de la sesión 2 integrado.

            No evaluamos memoria de sintaxis. Evaluamos si puedes decidir cómo guardar algo y defender la lectura
            de un resultado.
            """
        ),
        md(
            """
            ## Cómo está organizada la sesión

            | Bloque | Qué pasa | Qué queda |
            |---|---|---|
            | 0 | retomamos el ticket de salida de la sesión 2 | la condición que hoy vamos a cruzar |
            | 1 | por qué esta evidencia no cabe en una tabla | el problema nombrado: variedad |
            | 2 | qué existe en lugar de la tabla | las cuatro familias NoSQL |
            | 3 | cómo se ve un documento por dentro | anidamiento, arreglos, equivalencia con SQL |
            | 4 | y cuando no cabe en un servidor | fragmentar y replicar |
            | 5 | qué se cede al tener copias | ACID, BASE y consistencia eventual |
            | 6 | cómo le pregunto algo a la base | MQL, siempre junto a su SQL |
            | — | **receso** | el motor se instala mientras descansas |
            | 7 | **el laboratorio: aquí trabajas tú** | tu colección, tus consultas, tu interpretación |
            | 8 | cerramos en GitHub lo que quedó abierto | el Pull Request de la sesión 2, integrado |

            La segunda mitad de la sesión es tuya. Lo que produzcas hoy es el insumo de la sesión 4.
            """
        ),
        *soporte_cells(),
        md(
            """
            ---
            # Bloque 0 · En qué quedamos la semana pasada

            *Tu indicador, y la condición que hoy vamos a cruzar*

            Abre el archivo `hitos/s02/01_decision_proceso.md` que tu pareja y tú escribieron hace ocho días. Ahí
            quedó un indicador, con el nombre de ustedes al lado.

            **Hoy vamos a conseguir la evidencia que ese indicador necesita**, y en el camino nos vamos a topar con
            el problema que hace ocho días no vimos. El indicador en sí lo calculas el jueves entrante, cuando
            tengas una base que no se muera al cerrar la pestaña. Hoy resolvemos dónde se guarda la evidencia;
            la semana que viene, cuánto vale.

            ## El ticket de salida de la sesión 2, respondido

            Quedaron tres preguntas sin cerrar. Estas son las respuestas que sirven de punto de partida.

            **1. ¿Qué decisión apoya Compras Claras?**

            > Laura debe decidir **cuáles procesos contractuales revisa primero** con un equipo humano que no
            > alcanza a revisarlos todos. No decide si hay una irregularidad: decide dónde mirar. El indicador
            > ordena una fila de espera, no emite un veredicto.

            **2. ¿Por qué BI tradicional es suficiente para el primer hito?**

            > Porque en el primer hito la evidencia cabe en una máquina, llega por lotes y las preguntas son
            > descriptivas: cuántos, cuánto, de quién, en qué periodo. Nada de eso exige procesamiento
            > distribuido. La condición para reevaluar es concreta: si hay que **incorporar fuentes externas de
            > forma continua y con estructuras distintas**, BI tradicional deja de alcanzar. Hoy vamos a cruzar
            > justamente esa frontera.

            **3. ¿Qué parte puede comprobar CI y qué parte exige juicio humano?**

            > CI comprueba lo mecánico: que el archivo exista, que tenga las secciones pedidas, que no queden
            > campos `COMPLETAR`, que el enlace no esté roto. **CI no puede decir si la decisión está bien
            > planteada, si el indicador mide lo que dice medir o si la conclusión se estiró más de lo que el dato
            > aguanta.** Un check verde no es una aprobación conceptual.

            > **Conexión con hoy.** La respuesta 2 dejó una condición: *incorporar fuentes externas con estructuras
            > distintas*. Eso es exactamente lo que vamos a hacer ahora, y es lo que va a romper la tabla.

            Al terminar la sesión vuelve a `02_caso_arquitectura_accion.md`: el motor que vas a levantar vive en
            el dominio de **tecnología** de la arquitectura que dibujaste, y el documento que vas a diseñar vive
            en el de **información**. Confirma que las casillas que llenaste hace ocho días siguen teniendo
            sentido, y actualiza tu condición para reevaluar: hoy la vas a cruzar.
            """
        ),
        md(
            """
            ---
            # Bloque 1 · Por qué esta evidencia no cabe en una tabla

            *El problema es la variedad, no el volumen*

            ## La necesidad, primero

            **Quién es Laura.** Coordina un equipo de auditoría en una entidad de control. Son **cuatro
            personas**, y cada semana les entran cerca de **1 200 procesos** nuevos de contratación. Alcanzan
            a revisar a fondo unos **veinte**. No les falta criterio: les falta saber **por cuáles veinte
            empezar**, y hoy esa decisión la toman por orden de llegada.

            Laura tiene los contratos. Le faltan **señales externas**: qué entidades están apareciendo en la
            prensa, por qué y con qué frecuencia. Una entidad que aparece en varias noticias sobre un mismo asunto
            no es culpable de nada, pero **merece que alguien mire antes** que una entidad de la que nadie habla.

            Así que necesitamos dos fuentes, y son de naturalezas distintas:

            | Fuente | Qué es | Forma |
            |---|---|---|
            | SECOP II | procesos de contratación pública | **tabla**: 59 columnas fijas, una fila por proceso |
            | El Tiempo | noticias sobre contratación de enero a agosto de 2026 | **documentos**: cada noticia trae listas y partes de tipos distintos |

            ## Cómo se armó la colección de noticias

            El Tiempo publica dos cosas que se pueden enlazar entre sí, y el enlace es **el número que aparece al
            final de cada dirección**:

            | Fuente | Qué entrega | Formato |
            |---|---|---|
            | `sitemap-articles-2026-MM.xml` | el índice de todo lo publicado ese mes | XML |
            | `servicios/feeds/articulo/<ID>` | el artículo completo | JSON |

            El índice del año trae **57 848 artículos**. Descargarlos todos habría sido absurdo, así que primero
            filtramos por la dirección: el texto de la URL ya dice de qué trata el artículo. Los que contienen
            palabras como `contrato`, `licitacion`, `secop`, `sobrecosto`, `contraloria` o `corrupcion` son
            **995**. De esos, 991 respondieron, y al quitar repetidos quedaron **987 noticias**.

            > **Fíjate en el orden, porque es una decisión de ingeniería y no un detalle:** revisamos 57 848
            > artículos con **8 peticiones** (una por mes) y solo descargamos 995. Filtrar donde la información ya
            > está, antes de traer los datos, es la misma idea que vas a ver toda la noche con `$match` y todo el
            > semestre con los índices.

            Empecemos mirando la tabla, que es lo que ya conocemos.
            """
        ),
        code(
            f"""
            # Miramos la muestra de contratación pública tal como viene: una tabla.
            import pandas as pd

            contratos = pd.read_csv("{DATOS_SECOP}", low_memory=False)

            print("Filas:", len(contratos))
            print("Columnas:", len(contratos.columns))

            # ¿Qué tan llena está esta tabla realmente?
            vacias = contratos.isna().mean().mul(100).round(1).sort_values(ascending=False)
            print()
            print("Columnas 100% vacías:", int((vacias == 100).sum()))
            print("Columnas con más del 80% vacío:", int((vacias > 80).sum()))
            print("Columnas sin ningún vacío:", int((vacias == 0).sum()))
            print()
            print("Las 8 columnas más vacías (porcentaje de celdas sin dato):")
            print(vacias.head(8).to_string())
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — la tabla ya nos está avisando

            **Cómo se lee.** De 59 columnas, 2 están completamente vacías y otras 6 están vacías en más del 80 % de
            las filas — el 8 que imprime la celda incluye esas 2 totalmente vacías. Al mismo tiempo, 48 columnas no tienen un solo hueco.

            **Qué nos dice.** La tabla está pagando el precio de un esquema rígido: para que quepan los procesos que
            *sí* tienen fecha de adjudicación, **todos** los procesos tienen que cargar con esa columna, aunque el
            90 % la deje vacía. Cada campo opcional que aparezca en el futuro será una columna nueva y casi vacía.

            **Qué todavía no podemos concluir.** Que la tabla sea el modelo equivocado. Para 48 columnas es perfecta.
            El problema aparece cuando lo irregular deja de ser la excepción.

            **El error común.** Creer que esto se arregla "limpiando los datos". No hay nada sucio: esos procesos
            realmente no tienen fecha de adjudicación porque todavía no se adjudicaron. El dato ausente es
            información, no basura.

            ## Ahora la otra fuente

            Vamos a traer las noticias. Y aquí es donde la tabla se rompe de verdad.
            """
        ),
        code(
            f"""
            # Traemos las noticias ya recolectadas y las miramos SIN base de datos todavía.
            import urllib.request, json
            from collections import Counter

            URL_NOTICIAS = "{DATOS_NOTICIAS}"

            with urllib.request.urlopen(URL_NOTICIAS) as r:
                noticias = json.loads(r.read().decode("utf-8"))

            print("Noticias:", len(noticias))
            fechas = sorted(n["publicado"][:10] for n in noticias)
            print("Van desde", fechas[0], "hasta", fechas[-1])

            # 1) ¿Todas las noticias tienen los mismos campos?
            presencia = Counter(k for n in noticias for k in n)
            print()
            print("Presencia de cada campo (cuántas noticias lo traen):")
            for campo, veces in presencia.most_common():
                marca = "" if veces == len(noticias) else "   <-- NO está en todas"
                print(f"  {{campo:14s}} {{veces:4d}}/{{len(noticias)}}{{marca}}")

            # 2) ¿Cuántas etiquetas trae cada noticia?
            n_etiquetas = [len(n["etiquetas"]) for n in noticias]
            n_imagenes = [len(n["imagenes"]) for n in noticias]
            print()
            print(f"Etiquetas por noticia: mínimo {{min(n_etiquetas)}}, máximo {{max(n_etiquetas)}}")
            print(f"Imágenes por noticia:  mínimo {{min(n_imagenes)}}, máximo {{max(n_imagenes)}}")

            # 3) ¿De qué está hecho el cuerpo de una noticia?
            tipos = Counter(b["tipo"] for n in noticias for b in n["cuerpo"])
            print()
            print(f"El cuerpo está hecho de bloques, y hay {{len(tipos)}} tipos distintos:")
            for tipo, veces in tipos.most_common(8):
                print(f"  {{str(tipo):18s}} {{veces}}")
            print("  ... y otros menos frecuentes")
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — aquí sí se rompe la tabla

            **Cómo se lee.** Tres hechos, y cada uno rompe la tabla de una manera distinta:

            1. **Campos que faltan.** `subcategoria` no está en todas; `tiene_video`, en menos de veinte; y
               `descripcion`, en un puñado. En una tabla, cada uno sería una columna casi vacía. Ya vimos ese costo
               con SECOP.
            2. **Listas dentro de un registro.** Una noticia tiene entre 1 y 24 etiquetas, y entre 0 y 25 imágenes.
               En una tabla solo hay dos salidas, y las dos son malas: inventar `etiqueta_1` … `etiqueta_24`, o
               partir la noticia en veinticuatro filas repitiendo el título en cada una.
            3. **Partes de tipos distintos.** El cuerpo no es un texto: es una lista de bloques —entre 1 y 86 por
               noticia— y hay **25 tipos diferentes**: párrafo, imagen, subtítulo, artículo relacionado, video,
               cita de Instagram, PDF adjunto. Cada tipo guarda campos distintos. Una tabla necesitaría una
               columna por cada campo de cada tipo.

            **Qué nos dice.** El problema no es el tamaño. Son 987 noticias y 9 MB: caben en cualquier portátil. El
            problema es la **variedad**. Esa es la V que está fallando hoy, y por eso la solución no va a ser una
            máquina más grande.

            **Qué no podemos concluir.** Que las tablas sean malas o estén superadas. Los contratos de SECOP siguen
            estando bien en una tabla. Lo que aprendemos es a elegir según la forma del dato.

            > **Pregunta que dejamos colgada.** Estas 987 noticias salieron de filtrar **57 848 artículos**, y eso
            > es ocho meses de **un solo periódico**. Si Laura quiere vigilar diez medios durante cinco años,
            > hablamos de millones de documentos. Aunque arreglemos la forma, ¿dónde guardamos eso? Volveremos a
            > esta pregunta más adelante, cuando hablemos de repartir y copiar.
            """
        ),
        *question_cell(
            1,
            "El límite del modelo tabular",
            "Una noticia trae entre 1 y 24 etiquetas. El equipo quiere guardar las noticias en la misma base "
            "relacional donde ya están los contratos, sin cambiar de tecnología.",
            "¿Cuál de estas opciones describe mejor el costo real de forzar las etiquetas dentro de una tabla?",
            [
                "Ninguno: basta con guardar las etiquetas separadas por comas en una sola columna de texto.",
                "Hay que crear 24 columnas casi siempre vacías, o repetir la noticia completa en 24 filas.",
                "Hay que comprar más disco, porque el problema es el volumen de las noticias.",
                "Hay que limpiar los datos, porque una noticia bien formada debería tener una sola etiqueta.",
            ],
            1,
            [
                "Es la salida más común y la que más duele después: una columna de texto con comas ya no permite "
                "filtrar por una etiqueta sin buscar subcadenas, que es justo el error que veremos al final de la "
                "clase. Guardar una lista como texto es renunciar a poder consultarla.",
                "Correcto. Y las dos salidas son malas por razones distintas: las 24 columnas desperdician espacio y "
                "se quedan cortas con la noticia número 25; repetir la noticia en 24 filas duplica el título, el "
                "autor y el cuerpo, y obliga a recordar que 24 filas son en realidad una sola noticia.",
                "El volumen no es el problema aquí: son 987 noticias y 9 MB. La V que está fallando es la variedad, "
                "y esa no se resuelve con más disco.",
                "No hay nada sucio. Que una noticia tenga varias etiquetas es su forma legítima; el dato está bien y "
                "el modelo es el que no lo admite.",
            ],
        ),
        md(
            """
            ---
            # Bloque 2 · Qué existe en lugar de la tabla

            *Cuatro familias, y cada una renunció a algo distinto*

            Ya sabemos qué le sobra a la tabla. La pregunta obvia es qué existe en su lugar. La respuesta incómoda
            es que no existe *una* alternativa: existen cuatro, y **cada una renunció a algo distinto de la tabla**.

            | Familia | Qué guarda | Renuncia a | Ejemplo real | Cuándo la vemos |
            |---|---|---|---|---|
            | **Documental** | documentos con estructura libre y anidada | el esquema fijo y los JOIN baratos | MongoDB | **hoy** |
            | **Clave-valor** | un valor cualquiera bajo una llave | poder consultar por el contenido | Redis | mención |
            | **Columnar / wide-column** | filas repartidas por una llave de partición | consultas que no anticipaste | Cassandra | sesiones 4 y 5 |
            | **Grafos** | nodos y relaciones como ciudadanos de primera | el rendimiento en agregaciones masivas | Neo4j | sesión 6 |

            **La idea que hay que llevarse.** Ninguna de las cuatro es "mejor". Cada una hizo un intercambio, y
            elegir bien significa saber **qué consulta vas a hacer** antes de elegir dónde guardar. Esa frase va a
            volver hoy, va a volver en la sesión 4 con los índices y va a volver en la sesión 5 con Cassandra.

            **Error común que hay que desactivar de una vez.** "NoSQL significa sin estructura." No. Significa *sin
            esquema fijo impuesto por el motor*. El diseño sigue existiendo; lo que cambia es quién lo sostiene y
            cuándo se decide. Un documento mal diseñado es tan caro como una tabla mal normalizada.
            """
        ),
        *question_cell(
            2,
            "Las cuatro familias NoSQL",
            "El equipo necesita responder rápido, en cualquier momento, una consulta que nadie anticipó: "
            "«dame todas las noticias que mencionen esta entidad, sin importar la sección ni la fecha».",
            "¿Qué familia se ajusta mejor a esa necesidad, según el intercambio que hizo cada una?",
            [
                "Clave-valor, porque es la más rápida de todas.",
                "Columnar, porque reparte los datos entre varias máquinas.",
                "Documental, porque permite consultar por el contenido de los documentos sin haber anticipado la consulta.",
                "Grafos, porque una entidad y una noticia se pueden conectar.",
            ],
            2,
            [
                "Clave-valor es rapidísima, pero solo si ya sabes la llave. No puede responder «búscame las que "
                "mencionen X» sin recorrerlo todo: renunció justamente a consultar por contenido.",
                "Columnar reparte muy bien, pero su intercambio es el contrario del que necesitamos: rinde cuando la "
                "consulta se anticipó al diseñar la llave de partición. Una consulta imprevista es su punto débil, y "
                "lo vamos a comprobar en la sesión 4.",
                "Correcto. La familia documental conserva la capacidad de filtrar por cualquier campo del documento, "
                "incluso dentro de arreglos y estructuras anidadas, sin haber definido esa consulta de antemano.",
                "Un grafo sería excelente si la pregunta fuera sobre *cadenas* de relaciones —qué proveedores comparten "
                "dos entidades, por ejemplo—. Esa pregunta llega en la sesión 6. Para «filtrar por contenido», el grafo "
                "no aporta su ventaja.",
            ],
        ),
        md(
            """
            ---
            # Bloque 3 · Cómo se ve un documento por dentro

            *Campos, anidamiento y arreglos*

            De las cuatro familias, la documental es la que más se parece a lo que ya tienes en la cabeza: un
            documento es lo que llamarías **la ficha completa** de algo. Abramos una.

            ## Primero, dos ejemplos pequeños de otros sectores

            Antes del caso grande, mira la misma idea en dos terrenos que conoces.

            **Un registro clínico.** Un paciente tiene *un* documento con sus datos y *una lista* de atenciones.
            Cada atención tiene su propia forma: una consulta trae diagnóstico, un examen trae resultado y unidad,
            una hospitalización trae fecha de egreso. En una tabla, cada tipo de atención sería una tabla aparte.

            ```json
            {
              "_id": "PAC-1042",
              "nombre": "María R.",
              "atenciones": [
                {"tipo": "consulta",  "fecha": "2026-03-02", "diagnostico": "J06.9"},
                {"tipo": "examen",    "fecha": "2026-03-05", "prueba": "hemograma", "valor": 13.2, "unidad": "g/dL"},
                {"tipo": "urgencias", "fecha": "2026-04-11", "triage": 2, "egreso": "2026-04-12"}
              ]
            }
            ```

            **Qué muestra este ejemplo.** Una entidad principal —el paciente— y dentro de ella una **lista de
            cosas que no tienen todas la misma forma**: la consulta trae diagnóstico, el examen trae valor y
            unidad, la urgencia trae triage y egreso.

            Eso es exactamente una noticia. Y exactamente lo que no cabe en una fila.

            ## El mismo dato, de las dos formas

            {svg("fila_vs_documento", "A la izquierda una tabla con columnas de etiqueta casi siempre vacias; a la derecha el mismo dato como documento con una lista")}

            **Cómo leerlo.** A la izquierda, la tabla necesita una columna por cada etiqueta
            posible y llena de vacíos las que sobran. A la derecha, el mismo dato tiene un campo
            que contiene una lista: caben una o veinticuatro, y no hay nada que dejar vacío.

            **La conclusión.** No es que la tabla esté mal hecha: es que el dato tiene una forma
            que la tabla no puede representar sin inventar columnas.

            ## Anatomía de un documento real

            Vamos a mirar una noticia completa.
            """
        ),
        code(
            """
            # Miramos UNA noticia completa, con su estructura a la vista.
            from pprint import pprint

            n = noticias[0]

            print("CAMPOS DE PRIMER NIVEL")
            for campo, valor in n.items():
                if isinstance(valor, list):
                    print(f"  {campo:12s} -> lista con {len(valor)} elementos")
                elif isinstance(valor, dict):
                    print(f"  {campo:12s} -> objeto anidado")
                else:
                    print(f"  {campo:12s} -> {str(valor)[:60]}")

            print()
            print("DENTRO DEL ARREGLO 'etiquetas' (primeras 2):")
            pprint(n["etiquetas"][:2])

            print()
            print("DENTRO DEL ARREGLO 'cuerpo' (un bloque de cada tipo que trae esta noticia):")
            vistos = set()
            for b in n["cuerpo"]:
                if b.get("tipo") not in vistos:
                    vistos.add(b.get("tipo"))
                    print("  ", str(b.get("tipo")), "-> claves:", [k for k in b if k != "tipo"])
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — leer un documento

            **Cómo se lee.** Hay tres niveles a la vista. Campos simples (`titulo`, `seccion`, `premium`). Arreglos
            de objetos (`etiquetas`, donde cada etiqueta es a su vez un objeto con `id`, `nombre` y `slug`). Y un
            arreglo heterogéneo (`cuerpo`), donde cada bloque tiene **claves distintas según su `tipo`**.

            **Qué nos dice.** Un documento no es "una fila con más campos": es una estructura de árbol. Y guarda
            junto lo que se consulta junto. Si siempre vas a leer la noticia con sus etiquetas, tenerlas adentro
            evita un JOIN que en una base relacional pagarías cada vez.

            **Qué no podemos concluir.** Que anidar sea siempre mejor. Un arreglo que crece sin límite se vuelve un
            problema serio, y es la primera advertencia de diseño de la sesión 4.

            ### Vocabulario mínimo (para los que nunca han usado una base de datos)

            | Palabra | Qué es | Equivalente que ya conoces |
            |---|---|---|
            | base de datos | el contenedor mayor | el archivo de Excel |
            | colección | un conjunto de documentos del mismo tipo | una hoja del archivo |
            | documento | un registro completo | una fila, pero que puede tener árbol adentro |
            | campo | un dato dentro del documento | una celda con su encabezado |
            | `_id` | identificador único, obligatorio | la llave primaria |
            | BSON | el formato binario en que MongoDB guarda el JSON | — |

            ### Equivalencia entre SQL y MongoDB

            | Concepto en SQL | En MongoDB |
            |---|---|
            | tabla | colección |
            | fila | documento |
            | columna | campo |
            | llave primaria | `_id` |
            | `SELECT ... WHERE` | `find(filtro, proyección)` |
            | `GROUP BY` | etapa `$group` de una agregación |
            | esquema declarado al crear la tabla | esquema decidido al diseñar el documento |

            > La fila que falta en esta tabla es `JOIN`. La vemos en la sesión 4, cuando tengamos dos colecciones
            > que de verdad haya que cruzar. Hoy no la necesitamos.

            > **Esto lo vas a necesitar en el hito de hoy**, cuando expliques por qué esta evidencia no cabía en
            > una tabla.
            """
        ),
        *question_cell(
            3,
            "Anatomía de un documento",
            "En el arreglo `cuerpo` de una noticia, un bloque de tipo `paragraph` tiene la clave `texto`, "
            "mientras que un bloque de tipo `related_article` tiene un objeto anidado con otras claves.",
            "¿Qué característica del modelo documental hace posible eso, y qué obligaría a hacer una tabla?",
            [
                "Que el motor no valida nada; una tabla obligaría a limpiar los bloques antes de guardarlos.",
                "Que cada documento puede tener su propia estructura interna; una tabla obligaría a una columna por cada campo de cada tipo de bloque, casi todas vacías.",
                "Que MongoDB convierte todo a texto; una tabla obligaría a usar el tipo VARCHAR.",
                "Que los arreglos están prohibidos en SQL; una tabla obligaría a usar otro motor.",
            ],
            1,
            [
                "El motor sí puede validar si tú se lo pides (hay validación de esquema en MongoDB). Y el problema de "
                "la tabla no se resuelve limpiando: los bloques son legítimamente distintos entre sí.",
                "Correcto. La estructura la decide el documento, no el motor. Con 25 tipos de bloque, cada uno con sus "
                "propias claves, la tabla necesitaría la unión de todas esas claves como columnas, y cada fila dejaría "
                "vacías las que no le corresponden. Es el mismo costo que ya medimos en SECOP, multiplicado.",
                "MongoDB conserva los tipos: números, booleanos, fechas y objetos siguen siendo lo que son. No convierte todo a texto.",
                "Los arreglos no están prohibidos en SQL —varios motores tienen tipos de arreglo y JSON—. El punto no es "
                "la prohibición sino el costo: el modelo relacional te empuja a normalizar en tablas separadas.",
            ],
        ),
        md(
            """
            ---
            # Bloque 4 · Y cuando no cabe en un servidor

            *Repartir y copiar no son lo mismo*

            Al principio de la sesión quedó una pregunta colgada: nuestras 987 noticias salieron de 57 848 artículos,
            de un solo periódico y ocho meses. Aunque arreglemos la forma, ¿dónde guardamos eso?

            Hay dos respuestas, y hacen cosas distintas.

            ## Fragmentar (*sharding*): repartir

            Los documentos se **reparten** entre varias máquinas según una llave. Las noticias de enero a una, las
            de febrero a otra. Ninguna máquina tiene todo; entre todas tienen el total.

            **Y aquí ya hay una trampa de diseño, aprovéchala.** Repartir por mes es fácil de dibujar y malo en la
            práctica: como las noticias nuevas siempre son del mes actual, **todas las escrituras caen en la misma
            máquina** y no resolvimos nada. Una llave de reparto tiene que repartir también el futuro, no solo el
            pasado. Guarda esta idea: en la sesión 5, con Cassandra, elegir la llave de partición **es** el
            ejercicio.

            - **Resuelve:** que el volumen no cabe, y que las escrituras saturan un solo servidor.
            - **Cuesta:** una consulta que no usa la llave de reparto tiene que preguntarle a todas las máquinas.

            ## Replicar: copiar

            El mismo dato se **copia** en varias máquinas. Las tres tienen lo mismo.

            - **Resuelve:** que si una máquina se apaga, el servicio siga respondiendo; y que las lecturas se repartan.
            - **Cuesta:** mantener las copias de acuerdo. Y ahí aparece el problema del bloque siguiente.

            {svg("fragmentar_vs_replicar", "Fragmentar reparte una parte a cada maquina; replicar da el total a todas")}

            **Cómo leer el dibujo.** Son ejes independientes: un sistema real fragmenta *y* replica cada fragmento.
            Lo que hay que retener es que **fragmentar responde a "no cabe" y replicar responde a "no se puede caer"**.

            ## Antes de seguir: ¿qué es un clúster?

            Esto también es de Laura, aunque no lo parezca: su equipo no puede depender de que un servidor
            no se caiga. Si el lunes por la mañana la base no responde, esa semana no se revisa nada.

            La palabra va a aparecer todo el semestre y conviene fijarla ahora, porque es más simple de
            lo que suena.

            > **Un clúster son varias máquinas que se coordinan entre ellas y que tú usas como si fueran
            > una sola.**

            Eso es todo. La parte importante es la segunda mitad: **como si fueran una sola**. Tu código
            no cambia. Le sigues hablando a una dirección, con la misma línea `MongoClient(...)`, y por
            dentro esa dirección esconde tres máquinas que se reparten el trabajo y se vigilan.

            {svg("que_es_un_cluster", "A la izquierda un servidor solo: si se apaga no hay servicio. A la derecha un cluster de tres nodos coordinados que la aplicacion usa como si fuera uno")}

            **Cómo leerlo.** A la izquierda está lo que tienes hoy: **una** máquina, dentro de esta
            pestaña. Si se apaga, se acabó. A la derecha, tres máquinas —llamadas **nodos**— que se hablan
            entre ellas: si el principal cae, los otros dos lo notan, **votan** cuál toma el relevo, y tu
            aplicación ni se entera.

            **Tres palabras que ya puedes usar sin miedo:**

            | Palabra | Qué es |
            |---|---|
            | **nodo** | un `mongod` corriendo. En producción, cada uno en su propia máquina; en tu portátil, los tres en la misma |
            | **principal** *(primary)* | el nodo que recibe las escrituras en ese momento |
            | **réplica** *(secondary)* | un nodo que mantiene una copia del principal |

            **Y por qué votan.** Porque nadie puede decidir solo que el principal murió: podría ser que
            *él* esté bien y sea *quien mira* el que perdió la red. Por eso hace falta **mayoría**, y por
            eso el número mínimo es tres. Con dos nodos no hay mayoría posible y el clúster se queda
            paralizado justo cuando más lo necesitas.

            > **MÁS ADELANTE.** El clúster que vas a usar el jueves entrante, en Atlas, es exactamente
            > esto: tres nodos administrados por otros. Tú solo verás una dirección.

            ## ¿Y qué máquinas hacen falta para esto?

            Es la pregunta correcta, y la respuesta honesta tiene dos partes.

            ### Lo mínimo real, en producción

            | Estrategia | Qué se necesita de verdad | Por qué ese número |
            |---|---|---|
            | **Replicar** | **3 servidores** para un conjunto de réplicas | con 3, si uno cae los otros dos son mayoría y pueden elegir un nuevo principal. Con 2 no hay mayoría posible y el sistema se bloquea |
            | **Fragmentar** | **3 servidores por cada fragmento**, más 3 de configuración, más 1 o más enrutadores | cada fragmento es a su vez un conjunto de réplicas: fragmentar sin replicar significa que si cae una máquina, pierdes esa parte de los datos |

            Los dos nombres que faltan de esa tabla, para que no queden sueltos: los **servidores de
            configuración** son los que saben qué fragmento tiene qué datos —el índice del clúster—, y el
            **enrutador** es el que recibe tu consulta y decide a qué fragmento preguntarle. Tú siempre le
            hablas al enrutador.

            Es decir: un clúster fragmentado de verdad, con tres fragmentos, arranca en **unas 13
            máquinas**.

            **¿Y eso cuánto cuesta?** Para que tengas un ancla y no una sensación: un clúster
            administrado de tres nodos, del tamaño más pequeño que sirve para trabajar en serio, ronda los
            **200 a 500 dólares al mes**. Fragmentado en tres, con sus servidores de configuración,
            fácilmente **pasa de los 2 000**. Súmale a alguien que lo vigile.

            Por eso esto no se monta "por si acaso": se monta cuando el volumen o la disponibilidad lo
            exigen. Y por eso el plan gratuito que vas a usar el jueves entrante es un solo conjunto de
            réplicas de 512 MB, no un clúster fragmentado.

            ### ¿Puedo hacerlo en mi computador?

            **Sí, y es más fácil de lo que parece — pero simulado.** Un conjunto de réplicas de tres nodos
            en un portátil son tres procesos `mongod` en tres puertos distintos, cada uno con su carpeta de
            datos. Funciona, se comporta igual y sirve para aprender.

            Lo que **no** obtienes en tu máquina es lo único que justifica todo esto: **tolerancia a
            fallos reales**. Si se apaga tu portátil, se apagan las tres réplicas a la vez. La copia
            protege contra la caída de *una* máquina, no contra la caída de la máquina que las contiene a
            todas.

            > **PARA LLEVAR.** Replicar en un solo computador enseña el mecanismo y no da la garantía.
            > Es exactamente igual que guardar el respaldo de tu disco duro en el mismo disco duro.

            En la práctica, casi nadie monta esto a mano: se contrata. Eso es lo que hace Atlas, y es lo
            que vas a usar el jueves entrante — un conjunto de réplicas de tres nodos, administrado, en el
            plan gratuito.

            **Error común.** Confundirlos. "Tengo tres servidores" no dice nada por sí solo: hay que preguntar si
            cada uno tiene una parte o si cada uno tiene una copia.
            """
        ),
        md(
            """
            ---
            # Bloque 5 · Qué se cede al tener copias

            *ACID, BASE y el dato que fue verdad hace un momento*

            Tenemos el dato repartido y el dato copiado. **Las copias resuelven un problema y crean otro**, y el
            otro es el que le importa a Laura.

            ## La situación, con el caso de hoy

            Mientras nosotros hablábamos, El Tiempo publicó una noticia nueva. Entró al servidor central a las
            10:00. Hay tres copias: la central y dos réplicas.

            ```
            10:00:00,0   central     noticias = 987   (entra la noticia nueva)
            10:00:00,0   réplica A   noticias = 986
            10:00:00,0   réplica B   noticias = 986
            10:00:00,4   réplica A   noticias = 987
            10:00:02,0   réplica B   noticias = 987
            ```

            **Señala la fila donde el sistema está mal.**

            No hay ninguna. En cada instante, cada copia dice algo que **fue verdad**. Si Laura consulta a las
            10:00:01 y le toca la réplica lenta, ve 986. Consulta dos segundos después y ve 987. No hubo error,
            no se perdió nada, nadie hizo nada mal.

            Eso es **consistencia eventual**: si dejas de escribir, todas las copias van a terminar diciendo lo
            mismo. No te dice cuándo.

            > **La frase que hay que llevarse:** la consistencia eventual no te da un dato falso; **te da un dato que
            > fue verdad hace un momento.**

            ## ACID, letra por letra

            ACID es un acuerdo entre tú y la base de datos: si le pides que trate varias operaciones
            como **una sola transacción**, ella se compromete a cuatro cosas. Se entiende mejor con un
            caso que con la definición, así que usemos uno que a todos nos importa: **una transferencia
            de $200 000 de tu cuenta a la mía.** Son dos operaciones —restar de una, sumar a la otra— y
            tienen que pasar juntas.

            | Letra | Qué promete | En la transferencia | Qué pasa si falla |
            |---|---|---|---|
            | **A** · Atomicidad | o pasa todo, o no pasa nada | si el sistema se cae después de restar y antes de sumar, se deshace el resto | los $200 000 desaparecen |
            | **C** · Consistencia | las reglas del negocio se siguen cumpliendo al terminar | si hay una regla de "el saldo no puede quedar negativo", la transacción se rechaza en vez de violarla | quedan cuentas en estados imposibles |
            | **I** · Aislamiento | dos transacciones simultáneas no se pisan | si tú transfieres y a la vez te cobran la cuota, cada una ve un estado coherente, no la mitad de la otra | el saldo final depende del azar del orden |
            | **D** · Durabilidad | lo confirmado sobrevive a un corte de luz | si el sistema dijo "listo", está en disco aunque se vaya la energía un segundo después | el banco dice que pagaste y mañana no |

            ### Las dos confusiones más frecuentes

            **La C de ACID no es "ver siempre el último valor".** Eso es otra cosa y tiene otro nombre;
            llega en la sesión 4. La C de ACID es que **las reglas que tú declaraste se siguen cumpliendo**:
            que una llave foránea apunte a algo que existe, que un saldo no quede negativo, que un campo
            obligatorio no quede vacío.

            **ACID no es "lo relacional".** El MongoDB que vas a levantar en un rato tiene transacciones
            ACID sobre varios documentos desde la versión 4.0, y una operación sobre **un solo documento
            siempre fue atómica**, desde la primera versión. No son tecnologías: son **garantías que se
            eligen**, y se pagan con coordinación, es decir con tiempo.

            ### Y entonces, ¿qué es BASE?

            BASE es lo que queda cuando **renuncias a parte de esa coordinación para ganar disponibilidad**.
            El nombre es un juego de palabras con ACID —ácido y base— y significa *Basically Available,
            Soft state, Eventually consistent*: básicamente disponible, estado blando, consistente al final.

            Traducido: el sistema prefiere **responderte con algo** antes que hacerte esperar a que todas
            las copias se pongan de acuerdo. Y "al final" no tiene número.

            ## ACID y BASE, en lenguaje de negocio

            | | ACID | BASE |
            |---|---|---|
            | promete | que la transacción respeta las reglas: o pasa entera o no pasa | todas las copias coincidirán, sin decir cuándo |
            | prioriza | consistencia | disponibilidad |
            | típico de | bancos, inventarios, nómina | catálogos, medios, telemetría, redes sociales |
            | cuesta | coordinación, y por lo tanto latencia y escala de escritura | tolerar respuestas desactualizadas |

            ## La pregunta que hay que hacerle al negocio

            No es *"¿quiero consistencia?"*, porque a eso todo el mundo dice que sí. Es:

            > **¿Cuántos segundos de desactualización cambian la decisión?**

            Para Laura, priorizando qué revisar la próxima semana, dos segundos no cambian absolutamente nada. Para
            el saldo de una cuenta después de un retiro, dos segundos son un sobregiro. **Es la misma tecnología. Lo
            que cambia es la decisión que está colgando de ella.**

            Si trabajas en salud, ya viviste esto: el resultado de laboratorio está cargado, pero el médico de
            urgencias todavía no lo ve.

            ## Dos errores frecuentes

            1. *"Consistencia eventual significa que el dato puede estar mal o perderse."* No. No se pierde ni se
               inventa nada. Lo que varía es **qué tan viejo** es el dato.
            2. *"Esto es un tema de NoSQL."* Tampoco. Aparece cuando hay más de una copia **y alguien decide leer de
               una copia que no es la principal**. Ese «alguien decide» es una línea de configuración, y es tuya:
               si lees siempre de la principal, no ves consistencia eventual aunque tengas cinco réplicas. Un
               motor relacional con réplica de lectura tiene exactamente el mismo fenómeno.

            > Existe un resultado clásico llamado **CAP** que formaliza este intercambio bajo fallas de red. Lo
            > nombramos aquí y lo trabajamos con un clúster real en la sesión 4. Hoy basta con que sepas que existe.
            """
        ),
        *question_cell(
            4,
            "Consistencia eventual",
            "El tablero de Laura lee desde una réplica. Un contrato se modificó hace 1,5 segundos en la copia "
            "principal y la réplica todavía no se enteró. Laura consulta justo ahora.",
            "¿Qué está pasando y qué debería preocuparle al equipo?",
            [
                "Hay un error de integridad: el sistema perdió la modificación y hay que restaurar desde una copia de seguridad.",
                "Laura ve un valor que fue verdad hace un momento; lo que hay que preguntarse es si 1,5 segundos de desfase cambian su decisión.",
                "Es un problema exclusivo de MongoDB que se evita usando una base relacional.",
                "El sistema está mal configurado: con consistencia eventual las copias nunca llegan a coincidir.",
            ],
            1,
            [
                "No se perdió nada. La modificación está confirmada y durable en la copia principal, y va en camino a "
                "las réplicas. Restaurar una copia de seguridad aquí sería destruir información buena.",
                "Correcto. Y la segunda mitad es la que convierte esto en una decisión profesional: para priorizar "
                "revisiones de la próxima semana, 1,5 segundos son irrelevantes. Para un saldo bancario después de un "
                "retiro, no lo son. La pregunta correcta no es «¿quiero consistencia?» sino «¿cuántos segundos cambian "
                "la decisión?».",
                "No es exclusivo de MongoDB. Cualquier sistema con más de una copia —incluido un motor relacional con "
                "réplicas de lectura— tiene el mismo fenómeno. Aparece con las copias, no con la tecnología.",
                "«Eventual» significa justamente que sí llegan a coincidir; lo que no se garantiza es en cuánto tiempo. "
                "Que no haya un plazo prometido no es lo mismo que no haya convergencia.",
            ],
        ),
        md(
            """
            ---
            # Bloque 6 · Cómo le pregunto algo a la base

            *MQL, siempre junto a su SQL equivalente*

            Bajemos de la nube al teclado. Todo lo anterior no sirve de nada si no sabemos preguntarle algo a la
            base. En SQL escribirías `SELECT` y `WHERE`. Aquí se escribe distinto y se lee igual. **Voy a poner las
            dos, siempre, una al lado de la otra.**

            ## Traer documentos con un filtro

            ```sql
            -- SQL
            SELECT titulo, seccion
            FROM noticias
            WHERE seccion = 'salud';
            ```

            ```python
            # MongoDB
            db.noticias.find(
                {"seccion": "salud"},          # filtro   -> el WHERE
                {"titulo": 1, "seccion": 1}    # proyección -> el SELECT
            )
            ```

            **Lo que cambia:** en SQL el `SELECT` va primero y el `WHERE` después. En MongoDB el **filtro va
            primero** y la **proyección segunda**. Es el mismo par de ideas en orden inverso.

            ## Comparar números

            ```sql
            SELECT titulo FROM noticias WHERE n_palabras > 800;
            ```

            ```python
            db.noticias.find({"n_palabras": {"$gt": 800}}, {"titulo": 1})
            ```

            | Operador | Significa | En SQL |
            |---|---|---|
            | `$gt` / `$gte` | mayor / mayor o igual | `>` / `>=` |
            | `$lt` / `$lte` | menor / menor o igual | `<` / `<=` |
            | `$ne` | distinto de | `<>` |
            | `$in` | está en la lista | `IN (...)` |
            | `$exists` | el campo existe en el documento | *no tiene equivalente directo* |
            | `$regex` | el texto contiene un patrón | `LIKE '%...%'` |

            > `$exists` no tiene equivalente en SQL, y por una razón de fondo: **en una tabla la columna siempre
            > existe**, aunque esté vacía. En un documento, el campo puede simplemente no estar. Es la diferencia
            > entre "no tiene valor" y "no tiene el campo".

            **El error que vas a cometer si vienes de SQL.** `{"subcategoria": None}` **no** significa "no tiene el
            campo": empata tanto los documentos que lo tienen en nulo como los que no lo traen. Para distinguirlos
            de verdad: `{"subcategoria": {"$exists": False}}`. Y en esta colección importa, porque 180 noticias no
            traen `subcategoria`.

            ## Varias condiciones a la vez

            ```sql
            SELECT titulo FROM noticias WHERE seccion = 'bogota' AND n_palabras > 500;
            ```

            ```python
            db.noticias.find({"seccion": "bogota", "n_palabras": {"$gt": 500}})
            ```

            **Regla que evita el primer error de todos:** varias claves dentro del mismo diccionario significan
            **AND** implícito. Para un **OR** hay que escribirlo: `{"$or": [ {...}, {...} ]}`.

            **Cuidado cuando las dos condiciones entran en el mismo arreglo.** Si escribes
            `{"etiquetas.slug": "salud", "etiquetas.nombre": "Contraloría"}`, eso se cumple aunque sean **dos
            etiquetas diferentes** de la misma noticia. Para exigir que sea la misma:
            `{"etiquetas": {"$elemMatch": {"slug": "salud", "nombre": "Contraloría"}}}`.

            ## Entrar en lo anidado: notación de punto

            Aquí no hay SQL equivalente, porque no hay nada anidado en una tabla.

            ```python
            # noticias que tengan al menos una etiqueta cuyo slug sea exactamente "contraloria"
            db.noticias.find({"etiquetas.slug": "contraloria"})
            ```

            **Lo importante:** `etiquetas` es una **lista** de objetos, y MongoDB busca *dentro de cada elemento*
            de la lista sin que tengas que decirlo. Esa sola línea es lo que en una base relacional exigiría una
            tabla `noticia_etiqueta` y un JOIN.

            ### Mini ficha: `find(filtro, proyección)`

            - **Para qué sirve:** traer los documentos de una colección que cumplen una condición.
            - **Parámetros usados:** `filtro`, un diccionario con las condiciones; `proyección`, un diccionario que
              indica con `1` los campos a mostrar y con `0` los que no.
            - **Qué devuelve:** un cursor, no una lista. Se recorre con un `for` o se convierte con `list(...)`.
            - **Cómo interpretar la salida:** cada elemento es un documento completo, salvo que hayas proyectado.
            - **Error frecuente:** olvidar que `_id` se incluye siempre, aunque no lo pidas. Para quitarlo: `{"_id": 0}`.
            """
        ),
        *question_cell(
            5,
            "Traducir entre SQL y MongoDB",
            "Necesitas las noticias de la sección 'bogota' que además tengan más de 500 palabras, y quieres ver "
            "solamente el título.",
            "¿Cuál de estas consultas de MongoDB corresponde a "
            "`SELECT titulo FROM noticias WHERE seccion='bogota' AND n_palabras>500`?",
            [
                'find({"seccion": "bogota", "n_palabras": {"$gt": 500}}, {"titulo": 1, "_id": 0})',
                'find({"titulo": 1}, {"seccion": "bogota", "n_palabras": {"$gt": 500}})',
                'find({"$or": [{"seccion": "bogota"}, {"n_palabras": {"$gt": 500}}]})',
                'find({"seccion": "bogota"}).find({"n_palabras": 500})',
            ],
            0,
            [
                "Correcto. El filtro va primero y la proyección segunda —al revés que en SQL—, las dos claves dentro "
                "del mismo diccionario significan AND, y `_id: 0` es lo que evita que aparezca el identificador que no pediste.",
                "Están invertidos: eso filtraría por «documentos cuyo campo titulo valga 1» y proyectaría con la "
                "condición. Es el error más común al venir de SQL, donde el SELECT se escribe primero.",
                "`$or` devolvería también las noticias largas de cualquier otra sección, y las de Bogotá de cualquier "
                "longitud. El enunciado pide las dos condiciones a la vez, que es el AND implícito.",
                "`find()` no se encadena así, y `n_palabras: 500` pediría exactamente 500 palabras, no más de 500. "
                "Para «más de» se necesita `$gt`.",
            ],
        ),
        md(
            """
            ---
            # Puente al laboratorio

            > **PARA LLEVAR.** Las ocho preguntas azules **no se califican**: son el ensayo de la única entrega
            > que sí. Fállalas aquí, que sale gratis. La retroalimentación explica por qué cada opción está bien o
            > mal, y varias de esas explicaciones son lo mejor del cuaderno.

            De aquí en adelante trabajas tú. Este es el orden:

            1. arrancar el motor y ver cuál te tocó, real o de respaldo;
            2. cargar las 987 noticias de contratación en tu propia base de datos;
            3. escribir tres consultas tuyas;
            4. marcar una noticia como revisada;
            5. contar, por sección, cuántas noticias hay — y decir qué **no** permite concluir ese conteo;
            6. cruzar las noticias con las entidades de SECOP y descubrir por qué el cruce fácil miente;
            7. cerrar en GitHub el Pull Request que dejamos abierto la semana pasada.

            ## El método, antes de tocar el teclado

            Cada vez que te sientes a consultar datos, responde estas seis preguntas en este orden. Sirve hoy con
            MongoDB y va a seguir sirviendo con Spark y con Cassandra.

            1. **¿Qué pregunta tengo?** En una frase, y en lenguaje de negocio.
            2. **¿Qué documentos necesito?** Cuáles entran y cuáles sobran.
            3. **¿Por qué campos filtro y con qué operadores?**
            4. **¿Qué campos proyecto?** Traer todo es cómodo y caro.
            5. **¿Qué resumen responde mejor?** Un conteo, una suma, un promedio.
            6. **¿Qué interpretación es válida y qué NO puedo concluir todavía?**

            > **Antes del receso:** ejecuta ya la celda de arranque que viene enseguida. Va a seguir trabajando sola
            > mientras descansas. Deja la pestaña abierta y no cierres la tapa del portátil: si al volver dice
            > *reconectando*, vuelve a ejecutarla, tienes margen.
            """
        ),
        md(
            """
            ---
            # Laboratorio — aquí trabajas tú

            *Tu colección, tus consultas, tu interpretación. Lo que produzcas hoy es el
            insumo de la próxima sesión.*

            > **HAZ ESTO AHORA.** Ejecuta la celda de abajo antes de seguir leyendo, y déjala trabajando.

            > **OJO.** Si en cualquier momento del laboratorio ves un `NameError`, no busques la celda
            > culpable: vuelve al Paso 0 y ejecuta desde ahí hacia abajo. Todas las celdas de carga se
            > pueden repetir sin romper nada.

            > **MÁS ADELANTE.** Este arranque descarga MongoDB para Linux y por eso funciona en Colab y
            > solo en Colab. En tu computador con Windows no corre: no pierdas la noche intentándolo. La
            > ruta para tu máquina es Atlas, y llega el jueves entrante.

            ## Paso 0 · Arrancar el motor

            ### Qué va a hacer esta celda, en cuatro pasos

            Una base de datos **no es una librería de Python**: es un **programa aparte** que queda
            corriendo y escuchando peticiones. Instalar `pymongo` no instala MongoDB, igual que instalar
            un navegador no instala un sitio web. Por eso hay dos cosas distintas que preparar.

            | Paso | Qué hace | Equivalente cotidiano |
            |---|---|---|
            | 1 | **Descarga** el programa servidor desde el sitio oficial de MongoDB | bajar el instalador |
            | 2 | **Lo descomprime** en una carpeta de este Colab | instalarlo |
            | 3 | **Lo arranca** en segundo plano, escuchando en el puerto 27017, guardando en una carpeta de datos | abrir el programa y dejarlo abierto |
            | 4 | **Se conecta** desde Python con `pymongo`, que es el cliente | abrir la ventana que le habla al programa |

            Los tres nombres que aparecen y conviene entender:

            - **`mongod`** es el servidor. La *d* es de *daemon*: un programa que se queda corriendo en
              segundo plano. Es quien realmente guarda los datos.
            - **`--dbpath`** es la carpeta donde escribe. Si la borras, borraste la base.
            - **`--port 27017`** es la puerta por donde escucha. `pymongo` toca esa puerta.

            ### Si mañana quieres hacerlo en tu propio proyecto

            La secuencia es siempre la misma, cambie el sistema operativo o el proveedor:

            1. **conseguir un servidor** — instalándolo en tu máquina, levantándolo con Docker, o
               contratándolo ya administrado, que es Atlas;
            2. **saber su dirección** — `localhost:27017` si es tuyo, o un host en internet si es de un
               proveedor;
            3. **instalar el cliente** del lenguaje — `pip install pymongo`;
            4. **conectarte** con `MongoClient(direccion)`.

            **En tu computador con Windows, lo de esta celda no funciona**: descarga la versión de Linux.
            Para tu máquina, la ruta es el instalador oficial de MongoDB Community, o Atlas. No pierdas la
            noche intentándolo con este código.

            > **OJO.** Aquí el servidor vive dentro de esta pestaña. Cuando la cierres, el programa muere y
            > tus datos con él — igual que si apagaras el computador donde corre la base. Esa es
            > exactamente la limitación que la sesión 4 viene a resolver.


            Esta celda **no está oculta a propósito**: si algo falla, tienes que poder leer qué pasó.

            Levanta MongoDB dentro de este mismo Colab. No usa `apt` ni `systemctl`, y aquí está la razón, que vale
            la pena entender: **Colab no arranca con systemd**, así que `sudo systemctl start mongod` —que es lo
            que dicen casi todos los tutoriales— falla siempre. Descargamos el paquete oficial y lo ejecutamos
            directamente.

            Si algo sale mal, la celda **no se rompe**: cambia sola a `mongomock`, un MongoDB de mentiras que corre
            en memoria y que alcanza para todo lo de hoy. Te va a decir cuál de los dos quedó activo.
            """
        ),
        hidden(
            code(
            """
            # Paso 0 — levantar el motor. Ejecuta y sigue leyendo mientras trabaja.
            import os, subprocess, sys, time, urllib.request

            TGZ = "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-8.0.14.tgz"
            BASE, DBPATH, LOG = "/content/mongo", "/content/mongo-data", "/content/mongod.log"
            motor, client = None, None

            def paso(texto):
                print(texto, flush=True)

            try:
                # MongoDB 5 y superiores exigen instrucciones AVX en el procesador.
                with open("/proc/cpuinfo") as f:
                    if "avx" not in f.read():
                        raise RuntimeError("Este procesador no tiene AVX; MongoDB 8 no puede arrancar aqui.")

                # Si ya hay un mongod vivo de una ejecucion anterior, se reutiliza.
                # Sin esto, volver a ejecutar la celda intenta lanzar un segundo servidor
                # sobre el mismo puerto, falla, y caeriamos al respaldo perdiendo los datos.
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymongo"], check=False)
                    from pymongo import MongoClient
                    ya = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=1500)
                    ya.admin.command("ping")
                    client = ya
                    motor = "MongoDB " + client.server_info()["version"] + " (ya estaba corriendo)"
                except Exception:
                    client = None

                if client is None and not os.path.exists(f"{BASE}/bin/mongod"):
                    paso("1/4 Descargando MongoDB (aprox. 100 MB, desde la red de Google)...")
                    urllib.request.urlretrieve(TGZ, "/content/mongo.tgz")
                    paso("2/4 Descomprimiendo...")
                    os.makedirs(BASE, exist_ok=True)
                    subprocess.run(
                        ["tar", "-xzf", "/content/mongo.tgz", "-C", BASE, "--strip-components=1"],
                        check=True,
                    )
                else:
                    paso("1/4 y 2/4 ya estaban hechos; reutilizamos la instalacion.")

                if client is not None:
                    raise StopIteration  # ya conectado arriba; no relanzamos nada

                paso("3/4 Arrancando el servidor...")
                os.makedirs(DBPATH, exist_ok=True)
                subprocess.run(
                    [f"{BASE}/bin/mongod", "--dbpath", DBPATH, "--logpath", LOG,
                     "--bind_ip", "127.0.0.1", "--port", "27017", "--fork"],
                    check=True, capture_output=True,
                )

                paso("4/4 Conectando desde Python...")
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", "pymongo"], check=False)
                from pymongo import MongoClient
                client = MongoClient("mongodb://127.0.0.1:27017", serverSelectionTimeoutMS=8000)
                client.admin.command("ping")
                motor = "MongoDB " + client.server_info()["version"] + " (real, dentro de este Colab)"

            except StopIteration:
                pass

            except Exception as error:
                print()
                print("AVISO, no es un error: en esta maquina no arranco MongoDB real.")
                print("Seguimos con mongomock. El laboratorio es identico y no tienes que hacer nada.")
                print("Detalle tecnico (no necesitas entenderlo):", str(error)[:200])
                subprocess.run([sys.executable, "-m", "pip", "install", "-q", "mongomock"], check=False)
                import mongomock
                client = mongomock.MongoClient()
                motor = "mongomock (respaldo en memoria)"

            db = client["compras_claras"]
            print()
            print("=" * 60)
            print("MOTOR ACTIVO:", motor)
            print("=" * 60)
            """
            ),
            "Levantar el motor de base de datos",
            "hide-input",
            "soporte-motor",
        ),
        md(
            """
            ## Paso 1 · Confirma qué motor te tocó

            - Si dice **MongoDB 8.x (real...)**, estás hablando con un servidor de verdad, con su proceso, su
              archivo de datos y su log. Es lo mismo que correría una empresa, en pequeño.
            - Si dice **mongomock (respaldo...)**, el motor real no arrancó y estás usando una imitación en memoria.
              **Todo el laboratorio funciona igual.** Anótalo, porque en la sesión 4 vas a conectarte a un servidor
              que no vive en tu pestaña.
            - En los dos casos, la variable se llama `client` y la base se llama `db`. El resto del cuaderno no
              cambia ni una línea. **Que el código no dependa de dónde corre la base es una idea de ingeniería, no
              un truco.**

            **Advertencia sobre el reinicio.** Si el runtime de Colab se desconecta, el servidor muere y tus
            documentos con él. Por eso todas las celdas de carga se pueden volver a ejecutar sin duplicar nada.

            ## Cómo se evalúa esta sesión

            **No hay un cuestionario de opción múltiple.** Y la razón es honesta: una pregunta como *"¿cuál de las
            cinco V corresponde a la variedad?"* la responde cualquier asistente de inteligencia artificial en dos
            segundos, así que evaluar eso no mide lo que tú entendiste, mide que tienes internet.

            Lo que sí se evalúa es **lo que solo puedes producir tú, ejecutando esta sesión**: tus consultas, sobre
            la sección que tú elegiste, con los números que te dio tu propia colección, y la interpretación que
            defiendes de ellos.

            ### Lo que entregas

            | # | Qué | Dónde |
            |---|---|---|
            | 1 | La línea que imprimió tu motor y el conteo de tu colección | pegado en el hito |
            | 2 | Tus tres consultas, con la sección que **tú** elegiste y qué encontraste | pegado en el hito |
            | 3 | El `_id` de la noticia que marcaste como revisada, antes y después | pegado en el hito |
            | 4 | Una entidad de la tabla del cruce que **tú** elijas, y por qué la revisarías o no | escrito por ti |
            | 5 | Los dos números de tu cruce (el obvio y el correcto) y por qué se diferencian | escrito por ti |
            | 6 | Una frase sobre datos de **tu** sector: qué guardarías como documento y qué no | escrito por ti |

            Las tres primeras son evidencia de ejecución: o corriste el cuaderno o no. Las tres últimas son
            criterio, y no tienen una respuesta única: se evalúa si tu razonamiento se sostiene y si dices con
            claridad **qué no puedes concluir**.

            > **Una conversación corta al final.** El docente te va a preguntar en voz alta por el punto 4 o
            > el 5, con tu pantalla a la vista. No es un examen: es la forma más rápida de saber si la explicación
            > que escribiste es tuya. Si algo no te salió, decirlo cuenta a favor, no en contra.

            <details>
            <summary><b>Cómo se califica — ábrelo antes de escribir el hito</b></summary>

            ### Cómo se califica

            El hito vale **sobre 5,0** y se corrige con esta tabla. Está aquí, antes de que lo escribas, para que
            sepas contra qué se mide y no tengas que adivinar.

            | Criterio | Peso | 5,0 · Solvente | 3,5 · Cumple | 2,0 · Incompleto | 0 |
            |---|---|---|---|---|---|
            | **Evidencia de ejecución**<br>(motor, conteo, `_id`) | 1,0 | los tres datos están y son coherentes entre sí | están los tres | falta alguno | no hay |
            | **Tus tres consultas**<br>(con la sección que elegiste y por qué) | 1,0 | las consultas responden preguntas propias y justifica la elección de sección | las tres corren y reporta lo que encontró | copia las del cuaderno sin cambiar nada | no hay |
            | **La entidad que elegiste**<br>(revisar o no, y por qué) | 1,0 | decide, nombra la alternativa que descartó y sostiene el criterio | decide y da una razón | menciona una entidad sin decidir | no hay |
            | **Los dos números del cruce**<br>(y por qué se diferencian) | 1,0 | explica el mecanismo —subcadena frente a palabra— con un ejemplo propio | reporta ambos y dice que la diferencia son falsos positivos | reporta un solo número | no hay |
            | **Qué NO permite concluir** | 1,0 | nombra el **dato que falta**, no solo la limitación | dice correctamente qué no se puede afirmar | escribe "faltan datos" | no hay |
            | **Por qué no cabía en una tabla** y **tu sector**<br>(puntos 1 y 6) | se reparten dentro de los anteriores | usa un documento que **abrió** y un dato **real de su trabajo** | responde con un ejemplo del cuaderno | repite el enunciado | no hay |

            **Punto adicional de hasta 0,5**, que no sube de 5,0: una observación propia que el cuaderno no hizo.
            Un patrón que notaste, una consulta que se te ocurrió, un error que encontraste en el material. Se premia
            porque es lo más difícil de todo esto.


            </details>

            **Lo que no se califica:** la cantidad de commits, las líneas escritas, la velocidad, ni si el motor
            real te arrancó o te tocó el respaldo. **Un laboratorio que falló y está bien explicado vale más que uno
            perfecto que no se entiende.**

            **Sobre trabajar en pareja.** Es una entrega por pareja y los dos responden por todo. Si compartieron un
            solo runtime —cosa legítima— decláralo en el hito: no baja la nota, y no declararlo sí es un problema.
            """
        ),
        md(
            """
            ## Paso 2 · Cargar las noticias en tu base

            > **HAZ ESTO AHORA.** Ejecuta la celda de abajo. Es la que pone los datos en tu base.

            Ahora sí, las 987 noticias pasan de ser una lista de Python a ser **documentos dentro de una base de
            datos**. La diferencia importa: en la lista solo puedes recorrer; en la base puedes consultar.
            """
        ),
        code(
            """
            # Paso 2 — cargar. Se puede volver a ejecutar sin duplicar: primero borra, luego inserta.

            # Si vuelves del receso y ves un NameError, no busques nada: esta celda
            # recupera sola las noticias que cargamos durante la explicacion.
            if "noticias" not in dir():
                import urllib.request, json
                print("Recuperando las noticias (el entorno se reinicio)...")
                with urllib.request.urlopen("{DATOS_NOTICIAS}") as r:
                    noticias = json.loads(r.read().decode("utf-8"))
                print("Recuperadas:", len(noticias))

            # 'coleccion' es lo mismo que el 'db.noticias' que vimos en la explicacion.
            coleccion = db["noticias"]

            coleccion.delete_many({})          # idempotencia: dejamos la coleccion vacia
            resultado = coleccion.insert_many(noticias)

            print("Documentos insertados:", len(resultado.inserted_ids))
            print("Documentos en la coleccion:", coleccion.count_documents({}))

            # Leemos UNO para confirmar que llego completo.
            uno = coleccion.find_one({}, {"titulo": 1, "seccion": 1, "n_palabras": 1})
            print()
            print("Un documento cualquiera:")
            print("  ", uno)
            """.replace("{DATOS_NOTICIAS}", DATOS_NOTICIAS)
        ),
        md(
            """
            ### 🔎 Leamos el resultado — el `_id` y la idempotencia

            **Cómo se lee.** El conteo insertado y el conteo de la colección coinciden: nada se perdió ni se duplicó.

            **Qué observar en la salida.** Aparece un campo `_id` que tú no escribiste... salvo que sí lo escribiste:
            nuestras noticias ya traían `_id` con el número que El Tiempo usa para identificar el artículo. Cuando el
            documento no trae `_id`, MongoDB genera uno. **Ese campo es obligatorio y único: es la llave primaria.**

            **Por qué el `delete_many({})` antes.** Porque el runtime se puede reiniciar y vas a volver a ejecutar
            esta celda. Sin él, la segunda ejecución fallaría con error de `_id` duplicado o te dejaría 1 974
            documentos. Una carga que se puede repetir sin cambiar el resultado se llama **idempotente**, y es una
            propiedad que vas a agradecer todo el semestre.

            > **Esto no es un ejemplo inventado.** Al construir esta colección, la primera versión traía 991
            > documentos y la inserción **falló** con `E11000 Duplicate Key Error`. La causa: un artículo que se
            > actualiza aparece listado en el sitemap de varios meses, así que se descargó cuatro veces. La regla
            > del `_id` único **encontró un error de recolección que nadie había notado**. Por eso el archivo que
            > acabas de cargar tiene 987 y no 991. Una restricción de la base no es un estorbo: es un control de
            > calidad que trabaja gratis.

            ### Mini ficha: `insert_many(lista)`

            - **Para qué sirve:** insertar muchos documentos en una sola operación.
            - **Parámetro usado:** una lista de diccionarios.
            - **Qué devuelve:** un resultado con `inserted_ids`, la lista de identificadores creados.
            - **Cómo interpretar la salida:** si la longitud coincide con lo que enviaste, entró todo.
            - **Error frecuente:** insertar en un bucle con `insert_one`. Son N viajes al servidor en vez de uno. En
              la sesión 4, con un servidor en la nube, esa diferencia deja de ser estética: el plan gratuito
              **estrangula a las 100 operaciones por segundo**.
            """
        ),
        md(
            """
            ## Paso 3 · Tres consultas tuyas

            > **HAZ ESTO AHORA.** Aquí escribes tú. Son las tres únicas celdas de la noche donde el
            > cuaderno te deja el hueco: tómate el tiempo.

            Las dos primeras las escribes tú desde cero. La tercera viene con el patrón ya escrito para que solo
            cambies la palabra buscada.

            """
        ),
        code(
            """
            # 3.1 — COMPLÉTALA TÚ. Solo cambia el valor de SECCION.
            # Pregunta: ¿que noticias hay de una seccion que te interese?

            # Pista: estas son las 10 secciones con mas noticias, con su conteo.
            # Hay 57 secciones en total y muchas tienen una sola noticia: si eliges
            # una de esas y ves un solo resultado, tu consulta esta bien.
            conteo = [
                {"$group": {"_id": "$seccion", "n": {"$sum": 1}}},
                {"$sort": {"n": -1}},
                {"$limit": 10},
            ]
            for fila in coleccion.aggregate(conteo):
                print(f"  {fila['_id']:38s} {fila['n']:4d}")

            SECCION = "salud"      # <--- cambia esto

            print()
            for n in coleccion.find({"seccion": SECCION}, {"titulo": 1, "_id": 0}).limit(10):
                print("-", n["titulo"][:80])
            """
        ),
        code(
            """
            # 3.2 — COMPLÉTALA TÚ. Falta el operador: escribe "$gt" donde dice ____
            # Si la ejecutas sin completar, MongoDB dira: unknown operator: ____
            # Eso no es que rompiste algo: es que falta el hueco.
            # Pregunta: ¿cuales son las noticias mas largas?

            OPERADOR = "____"      # <--- reemplaza por el operador de "mayor que"

            largas = coleccion.find(
                {"n_palabras": {OPERADOR: 800}},
                {"titulo": 1, "n_palabras": 1, "_id": 0},
            )
            # .limit(10) evita llenar la pantalla: hay 189 noticias de mas de 800 palabras.
            for n in largas.limit(10):
                print(n["n_palabras"], "|", n["titulo"][:70])
            """
        ),
        code(
            """
            # 3.3 — Esta viene escrita. Cambia SOLO la palabra que buscas.
            # Pregunta: ¿que noticias mencionan un tema en el titulo?
            PALABRA = "salud"        # <--- cambia esto

            # $regex busca un patron dentro del texto; $options "i" ignora mayusculas.
            encontradas = list(coleccion.find(
                {"titulo": {"$regex": PALABRA, "$options": "i"}},
                {"titulo": 1, "seccion": 1, "_id": 0},
            ))

            print(f"Noticias con '{PALABRA}' en el titulo: {len(encontradas)}")
            for n in encontradas[:5]:
                print("  -", n["seccion"], "|", n["titulo"][:70])
            """
        ),
        md(
            """
            ### Qué deberías estar viendo

            Si trabajas solo, en casa o porque faltaste, esta es la forma de saber si te salió bien. Aquí no hay
            trampa: saber el resultado esperado no te ahorra pensar, te ahorra quedarte atascado.

            <details>
            <summary><b>Ver los resultados esperados de las tres consultas</b></summary>

            | Ejercicio | Qué deberías ver |
            |---|---|
            | 3.1 con `SECCION = "salud"` | 10 noticias listadas (la sección tiene 11 en total) |
            | 3.1 con otra sección | el número que aparece en la pista de arriba; si la sección tenía 1, ves 1 y **está bien** |
            | 3.2 con el operador correcto | 10 títulos, todos con más de 800 palabras. Hay 189 en total; `.limit(10)` muestra las primeras |
            | 3.3 con `PALABRA = "salud"` | 34 noticias con esa palabra en el título |
            | 3.3 con `PALABRA = "contrato"` | 299 noticias |

            **El operador que falta en 3.2 es `$gt`** (de *greater than*). Si escribiste `$gte`, obtienes las de
            exactamente 800 palabras también, y no es un error: es otra pregunta.

            **Si te devuelve 0 resultados**, revisa en este orden: que la sección esté escrita igual que en la
            pista (con guiones y sin tildes), que no te hayan quedado las comillas por fuera, y que hayas
            ejecutado el Paso 2 antes.

            </details>
            """
        ),
        md(
            """
            ### Mini ficha: `$regex`

            - **Para qué sirve:** buscar un patrón de texto dentro de un campo. Es el pariente de `LIKE '%...%'`.
            - **Parámetros usados:** el patrón, y `$options: "i"` para ignorar mayúsculas y minúsculas.
            - **Qué devuelve:** los documentos cuyo campo contiene ese patrón **en cualquier posición**.
            - **Advertencia que vas a necesitar en el paso 5:** busca **subcadenas**, no palabras completas. Buscar
              `"sena"` encuentra también `señaló`, `senador` y `enseñanza`. Guarda esta frase: más adelante va a
              explicar un resultado que parecerá bueno y no lo es.
            """
        ),
        *question_cell(
            6,
            "Consultar dentro de un arreglo",
            "Cada noticia tiene un arreglo `etiquetas`, y cada etiqueta es un objeto con `nombre` y `slug`. "
            "Quieres las noticias que tengan al menos una etiqueta cuyo slug sea exactamente 'contraloria'.",
            "¿Qué consulta lo resuelve, y por qué funciona?",
            [
                'find({"etiquetas": "contraloria"}) — porque MongoDB busca en todo el documento.',
                'find({"etiquetas.slug": "contraloria"}) — porque la notación de punto entra en cada elemento del arreglo automáticamente.',
                'Hay que traer todas las noticias y filtrarlas después con un for en Python.',
                'Hay que crear una colección aparte de etiquetas y hacer un JOIN.',
            ],
            1,
            [
                "Eso buscaría una etiqueta que fuera exactamente el texto «contraloria», pero las etiquetas son objetos, "
                "no textos. No encontraría nada.",
                "Correcto. `etiquetas.slug` recorre cada objeto dentro del arreglo y compara su campo `slug`. Es la "
                "diferencia central con una tabla: sin JOIN, sin tabla intermedia y sin recorrer nada a mano.",
                "Funcionaría, pero traería las 987 noticias completas a Python para descartar la mayoría. Con 987 no "
                "se nota; con 4 millones sí. La regla es filtrar donde están los datos, no donde está tu código.",
                "Esa es exactamente la solución relacional, y es la que el modelo documental te permite evitar cuando "
                "las etiquetas solo se consultan junto con su noticia.",
            ],
        ),
        md(
            """
            ## Paso 4 · Marcar una noticia como revisada

            En la sesión 2 dijimos que el ciclo analítico **termina en una acción humana que produce nueva
            evidencia**. Esto es eso: cuando alguien del equipo revisa una noticia, ese hecho tiene que quedar
            registrado en el dato.
            """
        ),
        code(
            """
            # Paso 4 — la accion humana vuelve al dato.
            from datetime import datetime, timezone

            objetivo = coleccion.find_one({}, {"_id": 1, "titulo": 1})
            print("Antes :", coleccion.find_one({"_id": objetivo["_id"]}, {"revision": 1, "_id": 0}))

            cambio = coleccion.update_one(
                {"_id": objetivo["_id"]},
                {"$set": {"revision": {
                    "estado": "revisada",
                    "por": "equipo_auditoria_laura",
                    "fecha": datetime.now(timezone.utc).isoformat(),
                }}},
            )

            print("Coincidieron:", cambio.matched_count, "| Modificados:", cambio.modified_count)
            print("Despues:", coleccion.find_one({"_id": objetivo["_id"]}, {"revision": 1, "_id": 0}))
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — `$set` y el campo que no existía

            **Cómo se lee.** `matched_count` dice cuántos documentos cumplían el filtro; `modified_count`, cuántos
            cambiaron de verdad. Si vuelves a ejecutar esta celda **seguirá diciendo 1 y 1**, porque el `$set`
            incluye la hora actual y la hora cambia cada vez. Si el valor fuera fijo, `modified` bajaría a 0:
            coincidió, pero no había nada nuevo que escribir. Pruébalo mentalmente antes de creerlo.

            **Lo importante, y es el punto de toda la sesión:** el campo `revision` **no existía en ningún
            documento** y ahora existe en uno solo. No hubo que alterar la colección, ni avisarle al motor, ni
            migrar los otros 986 documentos. En una tabla esto habría sido un `ALTER TABLE` que afecta a todas las
            filas y que en producción exige una ventana de mantenimiento.

            **Qué no podemos concluir.** Que esto sea gratis. Ahora tienes documentos con `revision` y documentos
            sin él, y **cualquier consulta futura tiene que decidir qué hacer con los que no lo tienen**. La
            flexibilidad no elimina el trabajo de diseño: lo mueve de la base a tu cabeza.

            ### Mini ficha: `update_one(filtro, cambio)`

            - **Para qué sirve:** modificar el primer documento que cumple el filtro.
            - **Parámetros usados:** el filtro, y un diccionario de operadores como `{"$set": {...}}`.
            - **Qué devuelve:** un resultado con `matched_count` y `modified_count`.
            - **Error frecuente y grave:** olvidar el `$set` y escribir `update_one(filtro, {"campo": valor})`.
              Las versiones modernas lanzan error; en las antiguas **reemplazaba el documento entero** y se perdía
              todo lo demás.
            """
        ),
        md(
            """
            ## Paso 5 · La primera agregación

            `find()` trae documentos. Pero Laura no necesita documentos: necesita **un resumen**. ¿En qué secciones
            se concentra la cobertura de este mes?

            Para eso existe el *aggregation pipeline*: una tubería de etapas donde la salida de una entra a la
            siguiente. Es la misma idea de un `GROUP BY`, escrita por pasos.

            ```sql
            -- SQL
            SELECT seccion, COUNT(*) AS n, AVG(n_palabras) AS promedio
            FROM noticias
            WHERE n_palabras > 0
            GROUP BY seccion
            ORDER BY n DESC
            LIMIT 10;
            ```
            """
        ),
        code(
            """
            # Paso 5 — la misma consulta del SQL de arriba, etapa por etapa.
            pipeline = [
                {"$match": {"n_palabras": {"$gt": 0}}},                 # el WHERE
                {"$group": {                                            # el GROUP BY
                    "_id": "$seccion",
                    "n": {"$sum": 1},
                    "promedio_palabras": {"$avg": "$n_palabras"},
                }},
                {"$sort": {"n": -1}},                                   # el ORDER BY
                {"$limit": 10},                                         # el LIMIT
            ]

            media_global = sum(n["n_palabras"] for n in noticias) / len(noticias)
            print(f"Media global de palabras: {media_global:.0f}")
            print()
            print(f"{'SECCION':32s} {'NOTICIAS':>9s} {'PALABRAS (prom.)':>17s}")
            print("-" * 60)
            for fila in coleccion.aggregate(pipeline):
                print(f"{str(fila['_id'])[:32]:32s} {fila['n']:9d} {fila['promedio_palabras']:17.0f}")
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — leer la tabla, y sobre todo sus límites

            **Cómo se lee.** Cada fila es una sección; `n` es cuántas noticias tiene y `promedio_palabras` qué tan
            extensas son. `_id` en la salida no es un identificador: en `$group` es **el criterio de agrupación**,
            y por eso vale el nombre de la sección.

            **Qué nos dice, y ojo con lo que parece decir.** La cobertura se concentra en secciones judiciales y de
            investigación: eso sí es claro. Pero mira la columna de palabras **antes** de sacar la conclusión
            intuitiva. La sección que encabeza, `justicia/investigacion`, aporta 238 de las 987 noticias y
            promedia 561 palabras: está **por debajo** de la media global de 622. `justicia/delitos` promedia
            491, todavía más abajo. La única sección notoriamente larga es `unidad-investigativa`, con 822
            palabras… y 77 noticias.

            Es decir: la lectura cómoda —«los reportajes judiciales son más largos»— **es falsa en esta tabla**.
            Un promedio sin su `n` al lado y sin una media de referencia no dice nada, y aquí lo acabas de
            comprobar tú mismo.

            **Qué NO permite concluir, y esto es lo importante de hoy.** Que la contratación "sea sobre todo un
            asunto judicial". Nuestro filtro incluyó palabras como `corrupcion`, `contraloria`, `procuraduria` y
            `peculado`, **así que el resultado estaba parcialmente decidido desde que elegimos las palabras**. Si
            hubiéramos filtrado solo por `licitacion` y `adjudicacion`, la sección económica pesaría mucho más.

            Y falta el denominador: no sabemos cuántos artículos publicó en total cada sección, así que no podemos
            distinguir *una sección donde la contratación es tema frecuente* de *una sección que simplemente
            publica mucho de todo*.

            > **Lo que sí podemos afirmar:** "entre los artículos que nuestro filtro seleccionó, estas secciones
            > aparecen más". **Lo que no:** "El Tiempo cubre la contratación principalmente desde lo judicial". La
            > distancia entre esas dos frases es el trabajo profesional.

            ## La historia del año

            Como tenemos ocho meses, podemos hacer algo que con un solo mes no se podía: mirar la evolución.

            ### Mini ficha auxiliar: `$substr`

            - **Para qué sirve:** cortar un pedazo de un texto dentro de una etapa de agregación.
            - **Parámetros usados:** el campo, la posición inicial (desde 0) y cuántos caracteres tomar.
            - **Por qué aquí:** `publicado` es un texto como `2026-03-15T09:41:00-05:00`. Los primeros 7 caracteres
              son `2026-03`, es decir el mes. Agrupamos por ese pedazo.
            - **Advertencia honesta:** esto funciona porque la fecha viene como texto **en formato ISO**, donde el
              orden alfabético coincide con el orden cronológico. Si las fechas estuvieran guardadas como
              `15/03/2026`, este truco daría un resultado sin sentido. Guardar fechas como texto es cómodo y
              frágil; en la sesión 4 las guardaremos como fechas de verdad.

            ### Mini ficha: `$unwind` — desenrollar una lista

            - **Para qué sirve:** cuando un campo es una **lista**, `$unwind` convierte cada elemento en su
              propia fila. Una noticia con 4 etiquetas se vuelve 4 filas, iguales en todo menos en la etiqueta.
            - **Para qué lo necesitas:** para poder agrupar **por** el contenido de una lista. Sin desenrollar,
              `$group` vería la lista entera como un solo valor.
            - **Ejemplo:** contar cuáles son las etiquetas más usadas en la colección.

            ```python
            coleccion.aggregate([
                {"$unwind": "$etiquetas"},                                  # 1 fila por etiqueta
                {"$group": {"_id": "$etiquetas.nombre", "n": {"$sum": 1}}},
                {"$sort": {"n": -1}},
                {"$limit": 5},
            ])
            ```

            - **Cómo interpretar la salida:** cada fila es una etiqueta y su conteo.
            - **Error frecuente, y es importante:** después de `$unwind` **los conteos ya no son aditivos**.
              Si sumas las etiquetas te va a dar más que el número de noticias, porque cada noticia se contó
              tantas veces como etiquetas tenga. Es correcto, pero no es lo mismo que contar noticias.

            ### Mini ficha: `sort()` y `limit()`

            - **`sort("campo", -1)`** ordena de mayor a menor; con `1`, de menor a mayor.
            - **`limit(n)`** se queda con los primeros n. Se encadenan después de `find()`:
              `coleccion.find(filtro).sort("n_palabras", -1).limit(5)`.
            - **Error frecuente:** ordenar en Python después de traerlo todo. Ordena en la base, que para eso está.

            ### Mini ficha: `aggregate(pipeline)`

            - **Para qué sirve:** calcular resúmenes encadenando etapas.
            - **Parámetro usado:** una lista de etapas, **y el orden importa**.
            - **Qué devuelve:** un cursor con un documento por grupo.
            - **Cómo interpretar la salida:** `_id` es el criterio de agrupación, no una llave.
            - **Error frecuente:** poner `$match` después de `$group`. Funciona, pero agrupa todo primero y filtra
              después: haces trabajo de más. **Filtra temprano, agrupa después.**
            """
        ),
        code(
            """
            # ¿Como se distribuye la cobertura de contratacion a lo largo del ano?
            # 'publicado' es un texto ISO: los primeros 7 caracteres son el mes.
            por_mes = [
                {"$group": {"_id": {"$substr": ["$publicado", 0, 7]}, "n": {"$sum": 1}}},
                {"$sort": {"_id": 1}},
            ]

            resultado = list(coleccion.aggregate(por_mes))
            meses = [f["_id"] for f in resultado]
            conteos = [f["n"] for f in resultado]

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots(figsize=(9, 3.4))
            barras = ax.bar(meses, conteos, color="#1976d2", width=0.62)

            # Agosto esta incompleto: lo pintamos distinto para no comparar peras con manzanas.
            barras[-1].set_color("#ef6c00")
            barras[-1].set_hatch("//")

            for barra, n in zip(barras, conteos):
                ax.text(barra.get_x() + barra.get_width() / 2, n + 3, str(n),
                        ha="center", fontsize=9)

            ax.set_title("Noticias de contratacion publicadas por mes", fontsize=12)
            ax.set_ylabel("noticias")
            ax.set_ylim(0, max(conteos) * 1.18)
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(axis="y", alpha=0.25)
            ax.annotate("agosto esta incompleto",
                        xy=(len(meses) - 1, conteos[-1] + 6),
                        xytext=(len(meses) - 1.9, max(conteos) * 0.95),
                        fontsize=9, color="#ef6c00",
                        arrowprops=dict(arrowstyle="->", color="#ef6c00"))
            plt.tight_layout()
            plt.show()
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — el mes que se sale de la serie

            **Cómo se lee.** Cada barra es un mes y su altura es cuántas noticias trae. La última está en otro
            color y rayada a propósito: agosto no está completo.

            **Qué nos dice.** La serie oscila bastante más de lo que parece a simple vista: entre junio (92) y enero
            (141) hay un 53 % de diferencia, **y eso sin contar julio**. Julio, con 175, se sale claramente de
            esa oscilación: ese sí parece un pico real. Agosto, con 80, parece un desplome.

            **Qué NO permite concluir.** Que en julio hubiera más irregularidades. Hay al menos dos explicaciones
            competidoras y con estos datos **no podemos separarlas**:

            - puede que efectivamente hubiera más hechos noticiosos sobre contratación en julio;
            - o puede que el periódico haya publicado más de todo ese mes, y contratación subiera con la marea.

            Distinguirlas exige el denominador: cuántos artículos publicó el periódico cada mes. Ese dato **sí lo
            tenemos** —está en el sitemap, son los 57 848— y aun así este análisis no lo usa. Anótalo: es la
            primera cosa que arreglarías si esto fuera tu trabajo.

            Y el desplome de agosto no es un hallazgo: **el mes estaba a mitad de camino cuando descargamos**, el 19
            de agosto. Haz la cuenta tú mismo: 19 de 31 días, así que 80 × 31 / 19 ≈ **131**. En pleno rango
            normal. La caída no existe: la fabricó el corte.

            Comparar un periodo incompleto con periodos completos es el error de conteo más común que vas a
            encontrar en tu vida profesional. Haz esa división antes de creerle a la última barra de cualquier
            serie que te muestren en tu trabajo.
            """
        ),
        *question_cell(
            7,
            "Interpretar una agregación",
            "El conteo por sección muestra que las secciones judiciales encabezan la lista, en una selección de "
            "987 artículos que se obtuvo filtrando 57 848 por palabras como 'contrato', 'corrupcion', "
            "'contraloria' y 'peculado'.",
            "¿Cuál es la afirmación defendible ante un jefe que va a tomar una decisión con esto?",
            [
                "El periódico cubre la contratación pública principalmente como un asunto judicial.",
                "Entre los artículos que nuestro filtro seleccionó predominan los judiciales; como el filtro incluía palabras como 'corrupcion' y 'peculado', el resultado está parcialmente decidido por el filtro.",
                "Hay más corrupción en contratación de la que se creía, por eso hay tantas noticias judiciales.",
                "El resultado no sirve para nada porque la selección no es aleatoria.",
            ],
            1,
            [
                "Es el salto que hay que evitar. Nosotros elegimos las palabras del filtro, y varias de ellas son "
                "judiciales. El resultado refleja esa elección tanto como refleja al periódico.",
                "Correcto. Se afirma exactamente lo que el dato sostiene y se nombra la causa concreta del sesgo: el "
                "filtro. Eso además indica el arreglo —repetir el ejercicio con un filtro solo de 'licitacion' y "
                "'adjudicacion' y comparar—, que es lo que distingue un análisis de una opinión con tabla.",
                "Este es el salto más peligroso de todos: pasa de «hay noticias» a «hay más corrupción». Una noticia "
                "mide cobertura periodística, no cantidad de hechos. Puede haber más cobertura porque hay más "
                "investigación, más interés o más acceso a fuentes.",
                "Demasiado severo, y también es un error. El resultado sí sirve: describe con precisión lo que el "
                "filtro seleccionó y señala qué habría que cambiar. Descartar evidencia parcial es tan poco riguroso "
                "como sobreinterpretarla.",
            ],
        ),
        md(
            """
            ## Paso 6 · Cruzar las dos fuentes, y descubrir por qué el cruce fácil miente

            Volvamos a la necesidad de Laura: **¿qué entidades de contratación están apareciendo en la prensa?**

            Tenemos las noticias en MongoDB y los contratos en una tabla. Vamos a cruzarlas por el nombre de la
            entidad. Primero de la manera obvia.
            """
        ),
        code(
            """
            # 6.1 — El cruce OBVIO: buscar el nombre corto de la entidad dentro del texto.
            import unicodedata, re
            from collections import Counter

            def normalizar(texto):
                '''Pasa a minusculas y quita tildes, para comparar sin sorpresas.'''
                texto = unicodedata.normalize("NFKD", str(texto).lower())
                return texto.encode("ascii", "ignore").decode()

            # Armamos el texto completo de cada noticia (titulo + parrafos + etiquetas).
            textos = {}
            textos_originales = {}
            for n in coleccion.find({}, {"titulo": 1, "cuerpo": 1, "etiquetas": 1}):
                partes = [n["titulo"]]
                partes += [b.get("texto", "") for b in n["cuerpo"] if b.get("texto")]
                partes += [t.get("nombre", "") for t in n.get("etiquetas", [])]
                textos[n["_id"]] = normalizar(" ".join(partes))
                # Guardamos tambien el texto SIN normalizar: las referencias de
                # contrato van en mayusculas y el normalizador las destruiria.
                textos_originales[n["_id"]] = " ".join(partes)

            claves = ["alcaldia", "gobernacion", "ministerio", "universidad", "hospital",
                      "fiscalia", "contraloria", "icbf", "sena", "dian", "policia"]

            print("CRUCE 1 — buscando la palabra como SUBCADENA (lo obvio):")
            con_alguna = sum(1 for t in textos.values() if any(k in t for k in claves))
            for k in claves:
                hits = sum(1 for t in textos.values() if k in t)
                print(f"  {k:14s} {hits:4d} noticias")
            print(f"  {'AL MENOS UNA':14s} {con_alguna:4d} de {len(textos)} noticias")
            """
        ),
        code(
            """
            # 6.2 — El MISMO cruce, exigiendo que sea una palabra completa.
            print("CRUCE 2 — exigiendo PALABRA COMPLETA:")
            con_alguna_ok = sum(
                1 for t in textos.values()
                if any(re.search(r"\\b" + k + r"\\b", t) for k in claves)
            )
            for k in claves:
                hits = sum(1 for t in textos.values() if re.search(r"\\b" + k + r"\\b", t))
                print(f"  {k:14s} {hits:4d} noticias")
            print(f"  {'AL MENOS UNA':14s} {con_alguna_ok:4d} de {len(textos)} noticias")

            print()
            print(f"Cruce obvio    : {con_alguna} noticias")
            print(f"Cruce correcto : {con_alguna_ok} noticias")
            print(f"Diferencia     : {con_alguna - con_alguna_ok} noticias que NO decian lo que creiamos")
            print()
            print("¿De donde salio el exceso? Miremos que estaba contando de mas:")
            for k in ["sena", "dian"]:
                falsos = [m for t in textos.values() for m in re.findall(r"\\w*" + k + r"\\w*", t) if m != k]
                print(f"  '{k}' aparecia dentro de:", Counter(falsos).most_common(5))
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — el resultado que parecía bueno

            **Qué acaba de pasar.** El primer cruce encontró muchas más menciones que el segundo. Y si lo hubiéramos
            entregado así, con una tabla bonita, nadie habría dudado.

            **De dónde salía el exceso.** `"sena"` estaba contando `señaló`, `señala`, `senador`, `señales`.
            `"dian"` estaba contando `mediante`, `estudiantes`, `diana`, `podían`. El buscador funcionaba
            perfectamente: **buscaba subcadenas, que es lo que le pedimos.** El error no fue del código; fue nuestro,
            al no preguntarnos qué significaba "mencionar una entidad".

            **Por qué esto es lo más importante de la noche.** Recuerda la advertencia de la mini ficha de `$regex`
            en el paso 3. Ahí te dijimos que buscaba subcadenas y no palabras. Un rato después, esa misma línea
            explica una tabla entera de resultados falsos. **La documentación te avisó y el resultado igual te
            convenció.** Así se producen los informes equivocados: no por ignorancia, sino por no verificar lo que ya
            sabíamos.

            **Qué se lleva Laura de aquí.** Que una mención en prensa **no es evidencia de irregularidad**, y ni
            siquiera es evidencia de mención hasta que definamos qué cuenta como mención. Sirve para ordenar una fila
            de revisión, no para acusar a nadie.

            **Qué no podemos concluir todavía.** Ni siquiera con el cruce correcto podemos decir que una entidad
            "está en las noticias por sus contratos": la noticia puede hablar de otra cosa completamente. Cruzar por
            nombre de entidad y cruzar por *tema contractual* son dos problemas distintos, y el segundo necesita
            herramientas que veremos en la sesión 7 con búsqueda textual.
            """
        ),
        code(
            """
            # 6.3 — Cruce por NOMBRE COMPLETO de entidad, contra las 9.111 entidades de SECOP.
            # Este cruce ya esta calculado y versionado: hacerlo aqui tomaria varios minutos.
            with urllib.request.urlopen("{cruce}") as r:
                cruce = json.loads(r.read().decode("utf-8"))

            print(f"Entidades de SECOP nombradas en alguna noticia: {len(cruce)}")
            print()
            print(f"{'ENTIDAD':46s} {'NOTICIAS':>8s} {'PROCESOS':>9s}")
            print("-" * 66)
            for fila in cruce[:12]:
                print(f"{fila['entidad'][:46]:46s} {fila['noticias']:8d} {fila['procesos_en_secop']:9d}")

            # El archivo trae hasta 3 titulares por entidad. Miremos los de la primera fila:
            print()
            print("Titulares de la entidad que encabeza:", cruce[0]["entidad"])
            for ej in cruce[0]["ejemplos"]:
                print("  -", ej["titulo"][:95])
            """.replace("{cruce}", DATOS_CRUCE)
        ),
        md(
            """
            ### 🔎 Leamos el resultado — y la trampa que casi nadie ve

            **Cómo se lee, y de dónde salen estos números.** Este cruce **no** se hizo contra la muestra de 1 000
            procesos que cargaste al principio de la clase: con sus 647 entidades no habría casi coincidencias. Se
            hizo aparte, contra el volcado completo de SECOP II —**300 000 procesos y 9 111 entidades**— y aquí
            solo leemos el resultado ya calculado. El script es `utils/cruzar_noticias_secop.py` y puedes abrirlo.

            > Que un cálculo no quepa dentro de la clase también es un dato sobre el problema.

            De esas 9 111 entidades, **142** aparecen nombradas completas en las noticias del año. La columna
            `NOTICIAS` dice en cuántas apareció; `PROCESOS`, cuántos procesos de contratación tiene en SECOP —de
            los 300 000, no de los 1 000 que viste—.

            **Una advertencia sobre esa columna:** las 142 entidades suman más menciones que noticias hay, porque
            una noticia que nombra cinco entidades cuenta cinco veces. La columna `NOTICIAS` **no se puede sumar**.

            **Ahora mira la primera fila.** La **Procuraduría General de la Nación** encabeza con muchísima
            diferencia: 195 noticias, contra 31 de la segunda. Y tiene 74 procesos en SECOP.

            """
        ),
        md(
            """
            ## Antes de la explicación elegante, la explicación incómoda

            Nosotros construimos este conjunto de noticias filtrando direcciones por una lista de 21 palabras. Y
            en esa lista estaba `procuraduria`.

            **265 de las 987 noticias entraron al conjunto precisamente porque llevaban esa palabra en la
            dirección.** También estaba `contraloria`, que metió otras 168.

            Es decir: la Procuraduría encabeza el conteo de menciones **en un conjunto que se seleccionó buscando
            su nombre**. Contar un término dentro de un corpus que se construyó con ese término no es un hallazgo:
            es medir tu propio filtro y ponerle nombre de entidad.

            > **Esto es la lección del paso 5 cobrándote otra vez, media hora después.** Allá dijimos que "el
            > resultado estaba parcialmente decidido desde que elegimos las palabras". Aquí esa misma decisión
            > fabricó al ganador de la tabla final. La primera vez fue una advertencia; esta es la factura.

            Compruébalo tú: el archivo `noticias_contratacion_2026.meta.json` guarda la lista exacta de palabras
            con las que se filtró. Está publicada a propósito, para que puedas auditar el criterio en vez de
            confiar en él.

            """
        ),
        md(
            """
            ## Y ahora sí, la segunda razón

            Si Laura ordenara su fila de revisión por esta tabla, **empezaría investigando a la Procuraduría**. Y
            sería exactamente al revés: la Procuraduría aparece tanto en la prensa porque **es la entidad que
            investiga a las demás**. Lo mismo pasa con la Contraloría de Bogotá y con Colombia Compra Eficiente,
            que es la entidad que *administra el SECOP*.

            **Esto es lo más importante que te llevas hoy.** El indicador no está mal calculado: está midiendo
            *aparición en prensa*, y aparición en prensa mezcla al menos tres cosas distintas:

            | Por qué una entidad sale en las noticias | Ejemplo en esta tabla |
            |---|---|
            | porque **investiga** a otros | Procuraduría, Contraloría |
            | porque **regula o administra** el sistema | Colombia Compra Eficiente |
            | porque **está siendo cuestionada** | Área Metropolitana del Valle de Aburrá |
            | porque **es un escenario político** y ahí pasan cosas todos los días | Cámara de Representantes |

            Solo la tercera fila le sirve a Laura. Y **el dato, por sí solo, no distingue cuál es cuál.**

            Fíjate en la tercera fila: la Cámara de Representantes tiene 29 noticias y 715 procesos. No investiga, no
            administra el SECOP y no está cuestionada por contratación. Sale en la prensa porque es la Cámara.

            """
        ),
        md(
            """

            ## Y la tentación que viene después

            Tienes dos columnas y vas a querer dividirlas: menciones por proceso. Hazlo mentalmente y mira quién
            queda de primero: el **Ministerio de Relaciones Exteriores**, con 23 noticias y **2 procesos**. Un
            cociente de 11,5.

            Un cociente con denominador 2 no es un indicador: es ruido con decimales. Y la regla vale para todo el
            semestre:

            > **Una tasa sin un mínimo de exposición en el denominador miente más que el conteo crudo que querías
            > arreglar.** Antes de dividir, fija ese mínimo y decláralo.

            Es el mismo problema del denominador del paso 5, pero al revés: allá **no teníamos** el denominador;
            aquí lo tenemos impreso en pantalla y es tan pequeño que usarlo hace más daño que ignorarlo.

            **Qué haría falta para arreglarlo.** Alguna señal del *papel* que juega la entidad en la noticia: si es
            sujeto o si es autoridad. Eso ya no es contar palabras, es entender el texto — y aparece en la sesión 7
            con búsqueda textual, y más adelante con análisis semántico.

            **Y sobre los 74 procesos, que es donde casi todo el mundo se equivoca.** Alguien puede leer "muchas
            noticias y poquísimos contratos" y concluir *"qué sospechoso"*. Es justo al revés: 74 procesos sobre
            300 000 significa que **la Procuraduría casi no contrata**. Y si casi no contrata, es imposible que
            aparezca en la prensa por sus contratos. El número pequeño no es una alarma: es la prueba de que la
            explicación tiene que ser otra.

            **Qué tampoco podemos concluir.** Que las otras 8 969 entidades no salgan en prensa: pueden estar
            nombradas con siglas, con nombre parcial o con su nombre popular. Y hay un motivo adicional que hay
            que declarar: el script **descarta por diseño los nombres de menos de 14 caracteres**, porque generan
            falsos positivos. Eso significa que a algunas entidades **ni siquiera las buscamos**.

            Nuestro cruce exacto es **conservador**: prefiere perder menciones reales antes que inventar falsas.
            Esa preferencia es una decisión de diseño y hay que declararla al entregar el resultado, no esconderla.

            > **Esta sí es una necesidad de Big Data demostrable, no una excusa para usar una herramienta.** Hoy
            > fueron 8 meses, un periódico y 987 noticias, y ya necesitamos cruzar dos fuentes de formas distintas.
            > Con doce medios, cinco años, sinónimos y siglas, deja de caber en una máquina y en un solo formato.
            > Ahí es donde el curso continúa.
            """
        ),
        md(
            """
            ## Paso 6.4 · La bandeja de revisión de Laura

            Hasta aquí sabemos **qué entidades** salieron en prensa. Pero Laura no revisa entidades: **revisa
            procesos**. Decir "mire la Superintendencia de Salud" no es accionable; decir "mire este contrato de
            arrendamiento de 37 mil millones" sí lo es.

            Así que bajemos un nivel. Vamos a cruzar las noticias con los **procesos de contratación** y a armar
            la bandeja: qué debería mirar Laura el lunes por la mañana, y en qué orden.

            ### Las señales que SECOP sí trae

            | Señal | Qué dice | Por qué importa |
            |---|---|---|
            | `modalidad_de_contratacion` | cómo se eligió al contratista | la contratación directa no compite |
            | `precio_base` | cuánto vale | el riesgo no es igual en 5 millones que en 50 mil millones |
            | `respuestas_al_procedimiento` | cuántos proveedores respondieron | cero respuestas es un proceso sin pluralidad |
            | *(externa)* noticias de la entidad | atención pública | contexto que SECOP no puede darte |

            **Y aquí viene la trampa, antes de que la construyas.** Suena razonable decir "contratación directa es
            sospechosa". Compruébalo antes de creerlo: en nuestros 300 000 procesos, la contratación directa es
            el **47 %**. Casi la mitad de la contratación del Estado. Una señal que marca a la mitad del universo
            no prioriza nada.

            Por eso la bandeja no usa una señal: usa **la combinación** de cuatro, y aun así no acusa a nadie.
            """
        ),
        code(
            """
            # Paso 6.4 — la bandeja de revision, ya calculada sobre los 300.000 procesos.
            with urllib.request.urlopen("{bandeja}") as r:
                bandeja = json.loads(r.read().decode("utf-8"))

            print(f"Procesos en la bandeja: {len(bandeja)}")
            print()
            print(f"{'VALOR':>18s}  {'NOT.':>4s}  {'ENTIDAD':34s}  OBJETO")
            print("-" * 108)
            for p in bandeja[:10]:
                print(f"{p['valor']:>18,.0f}  {p['noticias_de_la_entidad']:>4d}  "
                      f"{p['entidad'][:34]:34s}  {p['objeto'][:36]}")
            """.replace("{bandeja}", DATOS_BANDEJA)
        ),
        code(
            """
            # Abre UNO. Este es el nivel de detalle con el que Laura decide.
            import pandas as pd
            from IPython.display import HTML, display

            caso = bandeja[0]      # <--- cambia el numero y mira otro

            # .get() y no [ ]: si un campo no viniera, avisa en vez de romperse.
            ficha = pd.DataFrame(
                [
                    ("Proceso",    caso["id_del_proceso"]),
                    ("Entidad",    caso["entidad"]),
                    ("Ubicacion",  caso["departamento"]),
                    ("Objeto",     caso["objeto"]),
                    ("Valor",      f"$ {caso['valor']:,.0f}"),
                    ("Modalidad",  caso["modalidad"]),
                    ("Respuestas de proveedores", caso["respuestas"]),
                    ("Estado",     f"{caso['estado']} — publicado {caso['publicado']}"),
                ],
                columns=["campo", "valor"],
            )
            display(ficha.style.hide(axis="index"))

            enlace = caso.get("url_secop", "")
            if enlace:
                display(HTML(f'<p><a href="{enlace}" target="_blank">Ver este proceso en SECOP</a></p>'))

            prensa = pd.DataFrame([
                {"fecha": t["publicado"],
                 "titular": f'<a href="{t["url"]}" target="_blank">{t["titulo"][:95]}</a>'}
                for t in caso["titulares"]
            ])
            print("Lo que dijo la prensa sobre esta entidad:")
            display(HTML(prensa.to_html(escape=False, index=False)))
            """
        ),
        md(
            """

            ### 🔎 Leamos el resultado — lo que sí es y lo que no es esta bandeja

            **Qué acabas de construir.** Una lista priorizada de procesos concretos, con su objeto, su valor, cómo
            se contrataron, cuántos proveedores respondieron y qué se dijo en prensa sobre la entidad. Eso es un
            producto de trabajo: Laura puede abrirlo el lunes y empezar por arriba.

            **Y ahora el límite más importante de toda la sesión.** El cruce es **entidad ↔ noticia**, no
            **contrato ↔ noticia**. La noticia habla del Ministerio; casi nunca habla de *este* contrato. Un
            proceso puede estar de primero en la bandeja siendo impecable, solo porque su entidad apareció en
            prensa por un asunto que nada tiene que ver.

            Míralo en la tabla: hay convenios interadministrativos, un empréstito de tesorería y un arrendamiento
            de sede. **Ninguno de esos es raro**; los tres son figuras legales y frecuentes. Lo que la bandeja
            dice es *"aquí hay volumen, poca competencia y atención pública a la vez"*, y eso justifica **mirar**,
            que es exactamente lo que Laura pidió en la sesión 2. No justifica nada más.

            **Y una pregunta incómoda antes de celebrar.** Esta bandeja tiene **200 procesos** y el
            equipo de Laura revisa **20 por semana**: le acabas de entregar **diez semanas de cola**.
            Priorizar no es solo ordenar: también es decidir **dónde se corta la lista**, y ese corte lo
            tiene que justificar alguien. Ahora mismo el tuyo es arbitrario.

            **Qué le falta a esta bandeja para ser buena de verdad**, y anótalo porque es el trabajo de las
            próximas semanas:

            1. **Enlazar la noticia con el contrato**, no con la entidad. Necesita búsqueda textual sobre el
               objeto contractual: sesión 7.
            2. **Un denominador por entidad.** Un ministerio con 746 procesos y 31 noticias no es comparable con
               uno de 2 procesos y 23 noticias. Lo viste con el cociente de denominador pequeño.
            3. **El proveedor.** ¿Se repite entre entidades? Eso es una pregunta de relaciones, y se responde con
               grafos: sesión 6.
            4. **Que se actualice sola.** Hoy esta bandeja es una foto. Para que sirva tiene que rehacerse cada
               semana con noticias nuevas: eso es un proceso de ETL, sesiones 10 y 11.

            **PARA LLEVAR.** Ninguna de esas cuatro cosas es un capricho técnico: cada una es una pregunta que tu
            propio resultado dejó abierta hoy. Así se construye una capacidad de datos — no eligiendo herramientas,
            sino persiguiendo los límites de lo que ya tienes.
            """
        ),
        md(
            """
            ## Todo el recorrido, en una imagen

            {svg("de_la_noticia_al_contrato", "Cinco etapas: 57.848 articulos, 995 candidatos, 987 noticias, 142 entidades y 200 procesos priorizados")}

            **Cómo leerlo.** Cada caja conserva lo que la anterior seleccionó. Por eso la
            advertencia de abajo importa tanto: **el filtro de la segunda caja decide el resultado
            de la cuarta**, y esa decisión viaja hasta el final sin que nadie la vuelva a mirar.

            ## Paso 6.5 · Cuando la noticia nombra el contrato

            Hasta aquí el enlace fue **entidad ↔ noticia**, y ya dijimos que es débil: la noticia habla del
            Ministerio, no de *este* contrato.

            Pero a veces el periodista **da el número**. Cuando eso pasa, la señal deja de ser un indicio y se
            vuelve una identificación. Sería lo mejor que le puede pasar a Laura. Busquémoslos.
            """
        ),
        code(
            """
            # 6.5.1 — ¿Alguna noticia menciona un contrato por su numero?
            # Las referencias de SECOP se ven asi: EDP-545-2022, CD-436-2022, LP-001-2026.
            patron = r"\\b[A-Z]{2,6}-\\d{1,5}-\\d{4}\\b"

            referencias = {}
            for _id, t in textos_originales.items():
                for ref in re.findall(patron, t):
                    referencias.setdefault(ref.upper(), []).append(_id)

            print(f"Referencias de contrato encontradas en las noticias: {len(referencias)}")
            for ref, ids in list(referencias.items())[:8]:
                print(f"  {ref:18s} en {len(ids)} noticia(s)")
            """
        ),
        code(
            """
            # 6.5.2 — Cruzamos esas referencias contra las 268.525 de SECOP.
            import pandas as pd

            secop = pd.read_csv(
                "https://raw.githubusercontent.com/jazaineam1/BigData2026/main/"
                "Cuadernos/datos/secop_chunks/prueba_chunk_0000000.csv",
                usecols=["referencia_del_proceso", "entidad", "precio_base"],
                low_memory=False,
            )
            secop["ref"] = secop["referencia_del_proceso"].astype(str).str.upper().str.strip()

            coinciden = secop[secop["ref"].isin(referencias)]
            print(f"En TU muestra de {len(secop)} procesos coinciden: {len(coinciden)}")
            print()

            # El mismo cruce, hecho aparte sobre los 300.000 procesos completos.
            with urllib.request.urlopen("{referencia}") as r:
                cruce_ref = json.loads(r.read().decode("utf-8"))

            print(f"Sobre los {cruce_ref['procesos_evaluados']:,} procesos completos coinciden: "
                  f"{len(cruce_ref['coincidencias'])}")
            for c in cruce_ref["coincidencias"]:
                print(f"  {c['referencia']:14s} | {c['entidad'][:42]:42s} | {c['valor']:>14,.0f}")
            """.replace("{referencia}", DATOS_REFERENCIA)
        ),
        md(
            """
            ### 🔎 Leamos el resultado — el identificador que no identificaba

            **Primero, lo que ves en tu pantalla.** En tu muestra de 1 000 procesos no coincide **ninguna** de las 13
            referencias. Con 1 000 procesos de los 300 000 que existen, la probabilidad de acertar es mínima: el
            tamaño de la muestra vuelve a decidir el resultado, igual que en el conteo por sección.

            **Y ahora sobre los 300 000 completos**, que es el segundo número que imprimió la celda: el cruce
            devuelve **cuatro coincidencias**, y las cuatro son la misma referencia, `LP-001-2026`. Pertenecen a la
            **Alcaldía de Flandes**, el **Municipio de Vegachí**, el **Municipio de La Mesa** y la **Alcaldía de
            Riohacha**.

            Cuatro municipios que no tienen nada que ver entre sí, ni con la noticia. ¿Qué pasó?

            **Primero: la noticia sí nombraba un contrato, y uno importante.** Dice, textualmente:

            > *"MinTIC confirmó este 18 de agosto de 2026 la cancelación definitiva de la licitación pública
            > **FTIC-LP-001-2026**. El proceso buscaba adjudicar la construcción e interventoría del cable de
            > fibra óptica Putumayo."* — cancelada por sobrecostos, **1,14 billones de pesos**.

            Eso es exactamente lo que Laura quiere: un contrato concreto, nombrado, con un problema declarado.

            **Segundo: nuestro patrón se comió el prefijo.** Fíjate:

            | Referencia real | Lo que capturó el patrón |
            |---|---|
            | `FTIC-LP-001-2026` | `LP-001-2026` ← **perdió `FTIC-`** |
            | `SCJ-1904-2023` | `SCJ-1904-2023` ✓ |

            El símbolo `\\b` de la expresión regular marca **el borde de una palabra**, y para una expresión
            regular **un guion también es un borde**. Así que el patrón empezó a
            contar desde el segundo tramo y descartó justo la parte que decía de qué entidad era.

            <details>
            <summary><b>La tercera capa: por qué una referencia no identifica un contrato</b></summary>

            **Tercero, y es lo más importante: aunque el patrón fuera perfecto, la referencia no basta.**

            En SECOP hay 268 525 referencias distintas, y **10 004 de ellas —el 3,7 %— las usan dos o más
            entidades diferentes**. `002-2024` la usan **52 entidades distintas**. Es lógico: cada alcaldía
            numera sus licitaciones desde 001 cada año.

            > **🚧 La regla que te llevas.** Un identificador que solo es único **dentro de** una organización no
            > identifica nada fuera de ella. Para enlazar de verdad hace falta **entidad + referencia**, o el
            > identificador global que SECOP sí tiene (`id_del_proceso`, del estilo `CO1.REQ.6477624`) — y que
            > ningún periódico publica jamás.

            **Y una limitación honesta de nuestro ejercicio:** `FTIC-LP-001-2026` no está en nuestra muestra,
            porque nuestros datos de SECOP llegan hasta abril de 2026 y esa licitación se canceló en agosto. Sí
            están, en cambio, **485 procesos con el prefijo `FTIC`**: la entidad está, el contrato todavía no.
            Trabajar con una foto desactualizada es la condición normal del oficio, y hay que decirlo, no
            esconderlo.


            </details>

            ### Qué significa esto para la bandeja de Laura

            Si un contrato aparece nombrado **con su entidad** en una noticia, ese proceso **sube directo al tope
            de la fila de revisión**: ya no es una entidad bajo atención pública, es un contrato señalado.

            Eso justifica una columna nueva en la bandeja —*"¿lo nombra la prensa?"*— y explica por qué la
            búsqueda textual sobre el objeto contractual es la sesión 7 y no un adorno: es lo que convierte una
            señal difusa en una identificación.
            """
        ),
        md(
            """
            ## Paso 6.6 · De vuelta a la tabla: documentos y pandas juntos

            Legítima pregunta a esta altura: *si al final quiero una tabla para analizar, ¿para qué
            guardé documentos?*

            Porque son dos momentos distintos del mismo trabajo:

            | | Documento | Tabla |
            |---|---|---|
            | Sirve para | **guardar y consultar** información con forma irregular | **analizar y cruzar** un conjunto ya recortado |
            | Conserva | todo: listas, anidamiento, campos que solo tienen algunos | solo lo que quepa en columnas fijas |
            | Cuándo lo usas | cuando llega el dato y no sabes qué vas a preguntar | cuando ya sabes qué quieres calcular |

            La operación que va de uno a otro se llama **aplanar**: elegir qué del árbol se vuelve
            columna, y aceptar que lo demás se queda atrás. **Aplanar siempre pierde información**, y por
            eso se hace al final y no al principio.
            """
        ),
        code(
            """
            # 6.6.1 — Aplanar: del documento a la fila.
            import pandas as pd

            filas = []
            for n in coleccion.find({}, {"titulo": 1, "seccion": 1, "publicado": 1,
                                         "n_palabras": 1, "etiquetas": 1}):
                filas.append({
                    "id": n["_id"],
                    "titulo": n["titulo"],
                    "seccion": n["seccion"],
                    "mes": n["publicado"][:7],
                    "palabras": n["n_palabras"],
                    # Las decisiones de aplanado, una por una:
                    "n_etiquetas": len(n["etiquetas"]),                                  # la lista -> su tamano
                    "etiquetas": ", ".join(e["nombre"] for e in n["etiquetas"][:4]),     # y un resumen de texto
                })

            noticias_df = pd.DataFrame(filas)
            print("Documentos convertidos en filas:", noticias_df.shape)
            noticias_df.head(4)
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — qué se perdió al aplanar

            Mira lo que acaba de pasar con `etiquetas`. En el documento era **una lista de objetos**, cada
            uno con `id`, `nombre` y `slug`. En la tabla es **un texto separado por comas, y solo los
            primeros cuatro**.

            Lo que perdiste:

            - ya no puedes filtrar por una etiqueta sin buscar subcadenas — y de eso ya sabes lo que pasa;
            - perdiste el `slug` y el `id` de cada etiqueta;
            - perdiste las etiquetas de la quinta en adelante.

            **Y no es un defecto del código: es la definición de aplanar.** Por eso la pregunta correcta
            nunca es *¿tabla o documento?* sino **¿en qué momento de mi trabajo estoy?**

            > **PARA LLEVAR.** Guarda en documentos mientras no sepas qué vas a preguntar. Aplana a tabla
            > cuando ya lo sepas, y deja el documento intacto para poder volver a aplanar distinto mañana.

            ## Ahora sí, la tabla integral

            Con las noticias ya en forma de tabla, se unen con los procesos de SECOP igual que unirías
            dos hojas de cálculo. La llave es la entidad.
            """
        ),
        code(
            """
            # 6.6.2 — Unir las dos fuentes en UNA tabla, con pandas.
            bandeja_df = pd.DataFrame(bandeja)[
                ["entidad", "departamento", "objeto", "valor", "modalidad",
                 "respuestas", "noticias_de_la_entidad"]
            ]

            # Cuantas noticias y cuantas palabras aporta cada entidad, desde el lado noticias.
            #   Nota: aqui no tenemos la entidad en cada noticia, asi que usamos el conteo
            #   que ya trae la bandeja. En la sesion 4 lo haremos con un $lookup de verdad.
            integral = (
                bandeja_df
                .groupby(["entidad", "departamento"], as_index=False)
                .agg(procesos_en_bandeja=("objeto", "count"),
                     valor_total=("valor", "sum"),
                     noticias=("noticias_de_la_entidad", "max"))
                .sort_values("valor_total", ascending=False)
            )

            integral["valor_total"] = integral["valor_total"].map(lambda v: f"$ {v:,.0f}")
            print("Tabla integral:", integral.shape)
            integral.head(10)
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — una sola tabla para decidir

            Ahora tienes en un solo objeto de pandas lo que antes estaba en dos mundos: **cuántos procesos
            de riesgo tiene cada entidad, cuánto suman, y cuánta atención de prensa recibió**. Eso ya es
            un tablero: se ordena, se filtra, se exporta a Excel y se lleva a una reunión.

            **Y aquí cabe la advertencia de siempre**, ahora con más fuerza porque la tabla se ve
            convincente: la columna `noticias` sigue midiendo *aparición en prensa*, con todo lo que eso
            mezcla. Una tabla ordenada no vuelve verdadero un indicador que mide otra cosa.

            **Lo que ganaste al pasar por documentos primero:** si mañana Laura pregunta algo que hoy no
            anticipamos —por autor, por etiqueta, por tipo de bloque— los documentos siguen ahí completos
            y aplanas distinto. Si hubieras guardado directo en esta tabla, esa pregunta ya no se podría
            responder.
            """
        ),
        *question_cell(
            8,
            "El cruce entre dos fuentes",
            "Un compañero entrega la tabla del cruce y dice: «la Procuraduría es la entidad que más aparece en "
            "noticias de contratación, hay que revisar sus contratos primero». Recuerda que el conjunto de "
            "noticias se armó filtrando direcciones por 21 palabras, y que 'procuraduria' era una de ellas.",
            "¿Cuál es la objeción más fuerte que hay que hacerle?",
            [
                "Que el cruce por nombre completo es demasiado conservador y pierde menciones con siglas.",
                "Que el conteo mide en buena parte nuestro propio filtro: 265 de las 987 noticias entraron al conjunto porque llevaban la palabra 'procuraduria' en la dirección.",
                "Que 987 noticias son muy pocas para ordenar una fila de revisión.",
                "Que la Procuraduría tiene solo 74 procesos, y tan pocos contratos con tantas noticias es sospechoso.",
            ],
            1,
            [
                "Es una limitación real y hay que declararla, pero afecta a las entidades que faltan, no a la que "
                "encabeza. No explica por qué la primera fila es engañosa.",
                "Correcto, y es lo más importante de la noche. Antes de discutir si la Procuraduría sale porque "
                "investiga —que también es cierto—, hay algo más básico: **construimos el corpus buscando su nombre y "
                "después contamos su nombre**. Es la misma lección del conteo por sección, media hora después y con "
                "consecuencias mayores. Un indicador puede estar bien calculado y aun así estar midiendo tu método en "
                "vez de la realidad.",
                "Al contrario: 987 noticias de ocho meses bastan para describir un patrón. El problema no es cuántas "
                "son, sino cómo las elegimos.",
                "Esta es la inferencia invertida, y es peligrosa. 74 procesos sobre 300 000 significa que la "
                "Procuraduría **casi no contrata**; y si casi no contrata, es imposible que salga en prensa por sus "
                "contratos. El número pequeño descarta la sospecha, no la sostiene.",
            ],
        ),
        md(
            """
            ---
            ## Paso 7 · Cerrar en GitHub lo que dejamos abierto

            > **HAZ ESTO AHORA.** Esto se hace en pareja y en el navegador. Nada de terminal.

            La semana pasada tu pareja y tú abrieron un Pull Request y **se detuvieron antes de integrarlo**. Hoy
            lo cerramos. Y de paso aprendemos qué significa realmente ese último paso.

            > **Nada de esto necesita Git instalado.** Todo ocurre en `github.com` dentro del navegador. Esto no es
            > una simplificación para la clase: es la ruta que funciona en los computadores de la universidad, donde
            > puede que no tengas permisos para instalar nada.

            ### 7.1 — Revisar antes de integrar

            1. Entra al repositorio de tu pareja y abre la pestaña **Pull requests**.
            2. Abre el PR de la sesión 2 y ve a **Files changed**.
            3. Lee la última versión de los dos archivos. **Comprueba una cosa concreta:** que no quede ningún
               `COMPLETAR` y que el indicador tenga responsable y límite.
            4. Si algo falta, escríbelo como comentario en la línea exacta. Si está bien, sigue.

            ### 7.1-bis — Lo que pasa cuando dos personas tocan el mismo archivo

            Esta es la pregunta que todo el mundo tiene y casi nadie hace. Van a trabajar en pareja sobre
            los mismos archivos, así que conviene resolverla ahora.

            **Primero, tres palabras que no significan lo mismo:**

            | Palabra | Qué hace | Dónde queda |
            |---|---|---|
            | **commit** | guarda una versión con tu nombre y la fecha | **solo en tu copia** |
            | **push** | sube tus commits a GitHub | ahora sí, en el servidor |
            | **pull** | trae a tu copia lo que otros subieron | en tu copia |

            > **OJO.** Un commit sin push **no lo ve nadie**. Es el malentendido más caro de Git: alguien
            > dice "ya lo guardé" y en el servidor no hay nada. Cuando trabajas desde github.com, como
            > nosotros, el commit y el push ocurren juntos al pulsar *Commit changes* — por eso desde el
            > navegador este problema casi no aparece.

            **Ahora el caso: tú y tu pareja editan el mismo archivo.** Hay dos escenarios, y solo uno
            duele.

            **Escenario 1 — tocaron partes distintas del archivo.** Tú escribiste el punto 2 y tu pareja
            el punto 5. Git los combina **solo**, sin preguntar nada. Esto pasa la mayoría de las veces y
            es la razón por la que Git existe: dos personas trabajando a la vez sin pisarse.

            **Escenario 2 — tocaron la misma línea.** Los dos reescribieron el punto 3. Git **no adivina
            cuál es la buena**, y hace lo correcto: se detiene y te lo muestra así:

            ```
            <<<<<<< tu versión
            La sección que elegí fue salud porque trabajo en una EPS.
            =======
            La sección que elegí fue bogota porque vivo aquí.
            >>>>>>> la versión de tu pareja
            ```

            Eso es un **conflicto**. No es un error ni algo que rompiste: es Git diciendo *"aquí hace falta
            una persona"*. Para resolverlo borras las tres líneas de marcas y dejas el texto que acuerden
            —el tuyo, el de tu pareja, o uno nuevo que combine los dos— y guardas.

            > **PARA LLEVAR.** Git nunca borra el trabajo de nadie sin avisar. Si hay duda, para y
            > pregunta. Un conflicto es una conversación pendiente, no un accidente.

            **Y la forma de tener menos conflictos no es técnica:** repártanse **secciones distintas** del
            archivo antes de empezar. En el hito de hoy, por ejemplo, uno toma los puntos 0 a 3 y el otro
            del 4 al 7.

            ### Ejercicio · Provoquen un conflicto a propósito

            Diez minutos, en pareja, desde el navegador. Vale la pena verlo una vez en un archivo que no
            importa, para no verlo por primera vez en la entrega.

            Se hace sobre un archivo de juguete **en el repositorio de ustedes**, no en el del curso: en el
            del curso no tienen permiso para guardar. **Y no lo hagan sobre el archivo del hito:** ese es el
            que les califican, y la idea es equivocarse donde no cuesta nada.

            **Paso previo, lo hace uno solo de los dos (30 segundos).** En su repositorio de equipo:
            **Add file → Create new file**, nombre `practica/conflicto.md`, y dentro una sola línea:

            ```
            Nuestro color favorito es ____
            ```

            *Commit changes* y listo. Ya tienen dónde chocar.

            1. **Ahora sí, los dos a la vez** abren `practica/conflicto.md` y pulsan el lápiz de editar.
               **Sin cerrar ninguna de las dos pestañas.**
            2. En la línea que dice «Nuestro color favorito es ____», **cada uno escribe un color distinto**.
            3. **La persona A** pulsa *Commit changes*. Funciona sin problema.
            4. **La persona B** pulsa *Commit changes* en su pestaña. GitHub le responde con un aviso
               parecido a *"this file has changed since you started editing"* y **no la deja guardar**.

            > **OJO.** Ese aviso **no es un error tuyo y no rompiste nada.** Es GitHub haciendo su trabajo.
               Si aparece, vas bien.

            **Qué acaba de pasar, y es lo importante:** GitHub **protegió** el trabajo de A. Si hubiera
            dejado guardar a B, el texto de A habría desaparecido sin que nadie se enterara. Eso es
            exactamente lo que Git existe para impedir.

            **Ahora resuélvanlo**, que es la otra mitad del ejercicio:

            5. B copia su texto a otro lado, recarga la página y ve la versión de A.
            6. Entre los dos deciden qué queda: una, otra, o una frase nueva que diga las dos cosas.
            7. B edita con el texto acordado y guarda. Ahora sí entra.

            **Escríbanlo en el hito, punto 7:** qué pasó, qué decidieron y por qué. Esa frase vale más que
            cualquier definición de conflicto que puedan copiar.

            > **MÁS ADELANTE.** Aquí guardamos directo para que el choque se vea en dos minutos. En su
            > entrega real siguen con el flujo de la sesión 2 —rama, Pull Request y revisión—, que es el
            > que sirve cuando el trabajo importa. Lo de hoy es un simulacro, no un cambio de método.

            ### 7.2 — Integrar

            1. En la pestaña **Conversation**, revisa los **Checks**.
            2. Pulsa **Merge pull request** y confirma.
            3. Después del merge, GitHub ofrece **Delete branch**. Acéptalo.

            <details>
            <summary><b>Qué significa de verdad cada paso de GitHub</b></summary>

            ### Qué acaba de pasar, en palabras

            | Acción | Qué significa de verdad |
            |---|---|
            | **rama** `hito/s02-negocio` | una propuesta separada, que no toca el trabajo integrado |
            | **commit** | una versión guardada, con autor y fecha, que se puede recuperar |
            | **Pull Request** | la conversación: *propongo esto, ¿qué opinan?* |
            | **comentario en una línea** | una objeción localizada, no un juicio general |
            | **Checks** | comprobaciones mecánicas: que el archivo exista y esté completo |
            | **Merge** | la propuesta pasa a ser **la versión oficial** del equipo |
            | **Delete branch** | la propuesta ya se integró; la rama cumplió su función |


            </details>

            > **Lo que hay que entender, y es la respuesta 3 del ticket de la sesión 2:** un check verde **no
            > significa que la decisión esté bien planteada**. La máquina comprueba que el archivo esté completo. Si
            > tu indicador mide lo que no dice medir, el check sigue verde. Eso solo lo ve una persona.

            ### 7.3 — Abrir el hito de hoy (puedes terminarlo en casa)

            En el mismo repositorio, con el botón **Add file → Create new file**:

            1. Nombre del archivo: `hitos/s03/03_evidencia_documental.md`
            2. Pega la plantilla de aquí abajo y complétala con lo que hiciste hoy.
            3. **Commit** eligiendo *Create a new branch*, con el nombre `hito/s03-documental`, y abre el Pull Request.

            ```markdown
            # Hito 3 — Evidencia documental

            **Pareja:**

            ## 0. Evidencia de ejecución
            - Motor que me tocó (pega la línea que imprimió el Paso 0):
            - Documentos en mi colección:
            - `_id` de la noticia que marqué como revisada, antes y después:

            ## 1. Por qué esta evidencia no cabía en una tabla
            Un ejemplo concreto **de un documento que yo abrí**, no del enunciado:

            ## 2. Mis tres consultas
            | # | Qué quería saber | Consulta que escribí | Cuántas encontré | Qué me llamó la atención |
            |---|---|---|---|---|
            | 1 | | | | |
            | 2 | | | | |
            | 3 | | | | |

            La sección que elegí fue ____ y la elegí porque:

            ## 3. Una entidad de la tabla del cruce
            Elegí ____ (____ noticias, ____ procesos).
            ¿La pondría en la fila de revisión de Laura? Sí / No, porque:

            ## 4. Mi cruce, en dos números
            - Cruce obvio: ____ noticias
            - Cruce correcto: ____ noticias
            - La diferencia sale de:

            ## 5. Qué NO permite concluir mi resultado
            Nombra el dato que falta, no digas solo "faltan datos":

            ## 6. En mi sector
            Trabajo en ____. Un dato de mi trabajo que guardaría como documento y no como fila:
            Y uno que dejaría en una tabla, porque:

            ## 7. Extras (opcional, hasta +0,5)
            Marca lo que hayas hecho y escribe dos líneas de cada uno:
            - [ ] El ejercicio de conflicto de Git: qué pasó y qué decidimos.
            - [ ] El reto de Crossref: qué encontré y qué NO permite concluir.
            - [ ] Una observación propia que el cuaderno no hizo.
            ```

            **Fecha de entrega:** domingo. Se corrige con la rúbrica que está más arriba, en «Cómo se evalúa esta
            sesión». Vuelve a leerla antes de entregar: está escrita para que sepas exactamente qué se mira.
            """
        ),
        md(
            """
            ---
            # Reto final · Hazlo tú, con otros datos

            > **MÁS ADELANTE.** Esto **no se hace en clase**: es para el fin de semana, y es opcional. Lo
            > pongo aquí porque es lo único de la sesión donde te enfrentas solo a datos que nunca viste,
            > que es exactamente lo que te va a pasar en tu trabajo.

            Todo lo de esta noche lo hiciste sobre un caso que yo te di preparado. **Este reto es
            distinto: son datos que nunca has visto, de otro dominio, y el camino lo eliges tú.**

            Si lo terminas, ya no seguiste un tutorial de MongoDB: hiciste un trabajo con MongoDB.

            ## El caso

            Tu programa de maestría quiere saber **qué se está investigando sobre contratación pública en
            el mundo**: cuánta producción hay, de qué revistas sale, cuántos autores firman cada trabajo y
            cuáles se citan más.

            La fuente es **Crossref**, el registro donde se inscriben los artículos académicos con su DOI.
            Es pública, no pide cuenta y devuelve JSON.

            > **OJO.** No la elegí por bonita. La elegí porque tiene la misma forma incómoda que las
            > noticias: `author` es una **lista de objetos**, cada autor puede traer `affiliation` que es
            > **otra lista**, `title` es una **lista** aunque casi siempre tenga un elemento, y la fecha
            > viene como `{"date-parts": [[2024, 3, 27]]}` — una lista dentro de otra lista. Y varios
            > campos **no siempre vienen**. Otra vez: no cabe en una tabla sin pelear.

            ## Cómo funcionan los huecos de este reto

            De aquí en adelante hay celdas con `____`. Ese hueco lo llenas tú, y **hasta que lo llenes la
            celda va a fallar a propósito**. Los errores que vas a ver son estos, y ninguno significa que
            hayas roto algo:

            | Lo que dice la pantalla | Qué significa |
            |---|---|
            | `AttributeError: Collection has no attribute '____'` | falta el nombre de un **método** |
            | `NameError: name '____' is not defined` | falta el nombre de una **función** |
            | `Unrecognized pipeline stage name` o `$____ is not a valid operator` | falta el nombre de una **etapa** de agregación |
            | El resultado sale vacío o raro | el hueco era el nombre de un **campo** y quedó mal |

            > **OJO.** Si ves `____` en un mensaje de error, ya sabes qué pasó: busca `____` en la celda y
            > complétalo. **Leer el error y saber qué te está diciendo es parte del ejercicio** — es lo que
            > vas a hacer el resto de tu vida profesional.

            Y si te atascas, los cinco huecos están resueltos en la caja «Qué deberías estar viendo», al
            final del reto. Mirarlos no es hacer trampa: es no perder la noche.

            ## Reto, paso 1 · Trae los datos y míralos antes de tocarlos

            La primera regla del oficio: **mira la forma antes de decidir nada**.
            """
        ),
        code(
            """
            # Reto 1 — traer y mirar. Cambia el tema si quieres otro.
            import urllib.request, urllib.parse, json
            from pprint import pprint

            TEMA = "public procurement corruption"      # <--- cambialo si quieres

            url = (
                "https://api.crossref.org/works"
                f"?query={urllib.parse.quote(TEMA)}"
                "&rows=120"
                "&select=DOI,title,author,published,container-title,type,is-referenced-by-count"
            )
            # Crossref pide identificarse: es cortesia, y da mejor servicio.
            peticion = urllib.request.Request(
                url, headers={"User-Agent": "BigData-UCentral/1.0 (mailto:curso@ucentral.edu.co)"}
            )
            with urllib.request.urlopen(peticion, timeout=60) as r:
                respuesta = json.loads(r.read().decode("utf-8"))

            articulos = respuesta["message"]["items"]
            print("Articulos traidos:", len(articulos))
            print("Disponibles en Crossref sobre el tema:", respuesta["message"]["total-results"])
            print()
            print("UN ARTICULO COMPLETO, tal como viene:")
            pprint(articulos[0])
            """
        ),
        md(
            """
            ### Antes de seguir, contesta mirando esa salida

            No hace falta escribir nada todavía. Solo mira y responde en voz alta:

            1. ¿Qué campos son **listas**? Hay al menos tres.
            2. ¿Cuál está **anidado dentro de otra lista**?
            3. ¿Qué campo tiene ese artículo que **quizá otro no tenga**?

            ## Reto, paso 2 · Cárgalos en tu base

            Ya sabes hacer esto. Dos advertencias, y las dos las viste hoy:

            - `_id` tiene que ser **único**. El DOI lo es: úsalo.
            - Hazlo **idempotente**, para poder repetirlo sin duplicar.
            """
        ),
        code(
            """
            # Reto 2 — cargar. COMPLETA la linea marcada.
            articulos_col = db["articulos"]

            # Vaciar antes de insertar, para poder repetir la celda sin duplicar.
            articulos_col.delete_many({})

            docs = []
            for a in articulos:
                docs.append({
                    "_id": a["DOI"],                                  # el DOI como llave
                    "titulo": (a.get("title") or ["(sin titulo)"])[0],  # title es LISTA
                    "revista": (a.get("container-title") or ["(sin revista)"])[0],
                    "tipo": a.get("type"),
                    "citas": a.get("is-referenced-by-count", 0),
                    "anio": (a.get("published", {}).get("date-parts", [[None]])[0][0]),
                    "autores": [
                        {"nombre": f"{au.get('given','')} {au.get('family','')}".strip(),
                         "afiliaciones": [af.get("name") for af in au.get("affiliation", [])]}
                        for au in a.get("author", [])
                    ],
                })

            # COMPLETA: escribe entre comillas insert_one o insert_many.
            # Las dos funcionan. Una hace 120 viajes al servidor y la otra uno.
            METODO = "____"

            if METODO == "insert_many":
                articulos_col.insert_many(docs)
            elif METODO == "insert_one":
                for d in docs:
                    articulos_col.insert_one(d)     # 120 viajes en vez de 1
            else:
                print("Falta completar METODO arriba. Escribe insert_one o insert_many.")

            print("Articulos en tu base:", articulos_col.count_documents({}))
            """
        ),
        md(
            """
            > **OJO — el `.get()` está por todas partes y no es casualidad.** `a.get("title")` en vez de
            > `a["title"]` es lo que evita que un artículo sin título rompa la carga entera. Cuando los
            > campos no siempre vienen, indexar directo es una bomba de tiempo.

            ## Reto, paso 3 · Tres preguntas, tres consultas

            Escríbelas tú. Están ordenadas de menor a mayor dificultad, y las tres se responden con lo
            que hiciste esta noche.
            """
        ),
        code(
            """
            # Reto 3.1 — ¿Cuales son los 5 articulos mas citados?
            # Pista: find(), sort() y limit(). Para ordenar de mayor a menor: sort("campo", -1)

            for a in articulos_col.find({}, {"titulo": 1, "citas": 1, "_id": 0}).____("citas", -1).limit(5):
                print(a["citas"], "|", a["titulo"][:78])
            """
        ),
        code(
            """
            # Reto 3.2 — ¿Que revistas publican mas sobre el tema? Top 8.
            # Pista: es el mismo pipeline del paso 5 de esta noche, cambiando el campo.

            pipeline_revistas = [
                {"$match": {"revista": {"$ne": "(sin revista)"}}},
                {"$group": {"_id": "$____", "n": {"$sum": 1}, "citas": {"$sum": "$citas"}}},
                {"$sort": {"n": -1}},
                {"$limit": 8},
            ]

            for r in articulos_col.aggregate(pipeline_revistas):
                print(f"{r['n']:3d} articulos | {r['citas']:5d} citas | {str(r['_id'])[:62]}")
            """
        ),
        code(
            """
            # Reto 3.3 — ¿Quienes son los autores mas frecuentes?
            # Pista: 'autores' es una LISTA. Para contar por autor hay que
            # desenrollarla primero, y esa etapa se llama $unwind.

            pipeline_autores = [
                {"$____": "$autores"},                       # una fila por autor
                # Algunos registros vienen sin nombre de autor: los sacamos antes de contar.
                {"$match": {"autores.nombre": {"$ne": ""}}},
                {"$group": {"_id": "$autores.nombre", "articulos": {"$sum": 1}}},
                {"$sort": {"articulos": -1}},
                {"$limit": 10},
            ]

            for a in articulos_col.aggregate(pipeline_autores):
                print(f"{a['articulos']:3d} | {a['_id']}")
            """
        ),
        md(
            """
            ### 🔎 Leamos el resultado — y la trampa que ya sabes ver

            Antes de escribir ninguna conclusión, hazte las preguntas de esta noche:

            | Pregunta | Aplicada a este reto |
            |---|---|
            | ¿De dónde salió mi muestra? | de **una búsqueda por palabras**, igual que el corpus de noticias |
            | ¿El filtro decide el resultado? | sí: buscaste en inglés, así que la producción en español casi no aparece |
            | ¿Falta un denominador? | sí: no sabes cuántos artículos publicó cada revista **en total** |
            | ¿El conteo es aditivo? | no: un artículo con cinco autores cuenta cinco veces tras el `$unwind` |

            **Escribe una sola frase defendible** con tu resultado, del estilo: *"entre los 120 artículos
            que devolvió esta búsqueda, la revista X es la que más aparece; no sé si publica más sobre el
            tema o si simplemente publica más de todo"*.

            Si puedes escribir esa frase, entendiste la sesión. La sintaxis se busca en Google; **esto no**.

            ## Reto, paso 4 · Llévalo a una tabla

            Aplana tus artículos a un DataFrame y quédate con lo que quepa en columnas. **Y anota qué
            perdiste al aplanar** — ya sabes que siempre se pierde algo.
            """
        ),
        code(
            """
            # Reto 4 — aplanar. Falta UNA cosa: como cuentas los autores de cada articulo?
            import pandas as pd

            tabla = pd.DataFrame([
                {"titulo": a["titulo"][:70],
                 "revista": a["revista"][:40],
                 "anio": a["anio"],
                 "citas": a["citas"],
                 "n_autores": ____(a["autores"])}       # <--- completa
                for a in articulos_col.find({})
            ])

            print("Tu tabla:", tabla.shape)
            tabla.sort_values("citas", ascending=False).head(8)
            """
        ),
        md(
            """
            ### Qué deberías estar viendo

            Los resultados de una API viva **cambian**. Si haces esto el domingo, Crossref puede devolver
            artículos distintos de los del jueves. No compares tus números con los de un compañero:
            compara la **forma** de lo que sale.

            <details>
            <summary><b>Ver qué debería salir en cada paso</b></summary>

            | Paso | Qué deberías ver |
            |---|---|
            | Reto 1 | 120 artículos traídos, y más de un millón disponibles |
            | Reto 2 | 120 documentos cargados. Si salen menos, hubo DOI repetidos — y eso ya sabes leerlo |
            | Reto 3.1 | 5 títulos, el más citado por encima de 20 citas |
            | Reto 3.2 | 8 revistas; la primera con 15 a 30 artículos |
            | Reto 3.3 | 10 autores; los primeros con 4 a 6 artículos cada uno |
            | Reto 4 | una tabla de 120 filas y 5 columnas |

            **Los cinco huecos, si te atascas:** `insert_many` · `sort` · `revista` · `$unwind` · `len`.

            **Si el Reto 1 falla con un error de red:** Crossref limita las peticiones muy seguidas. Espera
            un minuto y vuelve a ejecutarlo. No cambies el código.

            </details>

            ## Si quieres ir más lejos

            - Cambia `TEMA` por algo de **tu sector** —*hospital readmission*, *credit risk*, *urban
              mobility*— y repite el reto entero. El código no cambia: eso es lo que acabas de aprender.
            - Sube `rows` a 500 y mira cuánto tarda. ¿Dónde está el cuello: la red o la base?
            - Cruza los autores con sus `afiliaciones` y mira qué universidades aparecen. **Cuidado:**
              `affiliation` viene vacía muchísimas veces. ¿Cuántas? Cuéntalo antes de concluir.

            ## Entrega opcional

            Si lo haces, pégalo en el **punto 7 del hito**. **No suma ni resta nota por estar bien o mal
            resuelto**: suma por haberlo intentado y por lo que escribas sobre los límites de tu resultado.

            > **PARA LLEVAR.** Fíjate en lo que acabas de hacer: cambiaste de fuente, de dominio y de
            > vocabulario, y **el método no cambió**. Trae, mira la forma, carga, consulta, resume,
            > interpreta y declara los límites. Eso es lo que Laura necesita de ti, y es lo que te llevas
            > de esta noche: no MongoDB, sino saber qué hacer cuando llegan datos que nadie ha mirado.

            
            ---
            ## Ticket de salida

            Responde en tres frases, antes de irte:

            1. ¿Qué característica concreta de las noticias hace que una tabla no sirva? Da un ejemplo real de la
               colección.
            2. ¿Qué diferencia hay entre fragmentar y replicar, y qué problema resuelve cada uno?
            3. El cruce obvio con SECOP dio más menciones que el correcto. ¿Por qué, y qué aprendiste de eso?

            ---
            # Cierre de la sesión

            ## Recapitulación

            1. Una tabla se rompe ante la **variedad**, no ante el volumen: campos que faltan, listas dentro de un
               registro y partes de tipos distintos.
            2. Hay **cuatro familias NoSQL** y cada una renunció a algo diferente. La documental conserva la
               capacidad de consultar por contenido sin haber anticipado la consulta.
            3. Un **documento** es un árbol con `_id` obligatorio; la notación de punto entra en los arreglos sin
               JOIN.
            4. **Fragmentar** responde a "no cabe"; **replicar** responde a "no se puede caer", y su precio es la
               consistencia eventual.
            5. `find()` trae documentos y `aggregate()` trae resúmenes; el orden de las etapas importa y conviene
               filtrar temprano.
            6. Un resultado sin **denominador** describe la muestra, no la realidad.
            7. Un **merge** convierte una propuesta en la versión oficial; un **check verde** no valida el
               razonamiento.

            ## La idea más importante

            > **El modelo de datos se elige desde la consulta que se quiere responder.** Hoy fue el documento. En la
            > sesión 4 será el índice. En la sesión 5 será la llave de partición de Cassandra. Es la misma idea tres
            > veces.

            ## Errores comunes de hoy

            - Creer que NoSQL significa "sin estructura". Significa sin esquema fijo **impuesto por el motor**.
            - Confundir fragmentar con replicar.
            - Olvidar `$set` en un `update_one`.
            - Poner `$match` después de `$group` y hacer trabajo de más.
            - Aceptar un conteo sin preguntar cuál es el denominador.
            - Buscar subcadenas creyendo que se buscan palabras.

            ## Lo que NO te llevas hoy, y por qué existe la próxima clase

            Cuando cierres esta pestaña, **el servidor que levantamos se muere y tus documentos con él.** Eso no es
            un defecto del ejercicio: es la razón de ser de la sesión 4.

            El jueves cada pareja va a tener su propia base corriendo en un servidor que no se apaga, va a subir
            estas mismas noticias ahí, y va a calcular el indicador de su archivo `01_decision_proceso.md`. También
            vamos a medir por primera vez **cuánto cuesta leer** un dato, y ahí aparecerá el almacenamiento
            columnar.

            **Tarea de la semana, y es la que habilita la clase:** crear tu cuenta gratuita en MongoDB Atlas.

            > La colección de noticias que construiste hoy vive dentro de tu Colab y se muere cuando cierres la
            > pestaña. El equipo de Laura no puede trabajar así. Esta semana la vas a poner donde el equipo entero
            > pueda alcanzarla.

            **Guía paso a paso:** [`docs/guia_atlas_cuenta_gratuita.md`](https://github.com/jazaineam1/BigData2026/blob/main/docs/guia_atlas_cuenta_gratuita.md).
            Léela antes de empezar: las tres advertencias del principio son las responsables de casi todos los
            problemas, y una de ellas —el acceso de red— hace fallar la conexión el jueves aunque hayas hecho
            todo lo demás bien.

            **El pantallazo del clúster creado se entrega el miércoles**, no
            el jueves a las seis y cinco.
            """
        ),
        md(
            """
            ---
            # Hoja de trucos — imprímela o déjala en otra pestaña

            Todo lo que necesitas para consultar, en un solo lugar. Está repetido a propósito: un material que
            se consulta debe repetir, no obligarte a hacer scroll.

            ## Las palabras

            | Palabra | Qué es | Lo que ya conoces |
            |---|---|---|
            | base de datos | el contenedor mayor | el archivo de Excel |
            | colección | conjunto de documentos del mismo tipo | una hoja |
            | documento | un registro completo | una fila, pero con árbol adentro |
            | campo | un dato dentro del documento | una celda con su encabezado |
            | `_id` | identificador único, obligatorio | la llave primaria |

            ## Consultar

            ```python
            coleccion.find_one({})                      # un documento cualquiera
            coleccion.find({"seccion": "salud"})         # todos los que cumplen
            coleccion.find(filtro, {"titulo": 1, "_id": 0})   # solo esos campos
            coleccion.find(filtro).limit(10)             # los primeros 10
            coleccion.count_documents(filtro)            # cuántos hay
            coleccion.distinct("seccion")                # valores distintos
            coleccion.find(filtro).sort("campo", -1)     # ordenar: -1 mayor a menor, 1 al reves
            ```

            | Operador | Significa | En SQL |
            |---|---|---|
            | `{"$gt": 800}` | mayor que | `> 800` |
            | `{"$gte": 800}` | mayor o igual | `>= 800` |
            | `{"$lt": 800}` / `{"$lte": 800}` | menor / menor o igual | `<` / `<=` |
            | `{"$ne": "x"}` | distinto de | `<> 'x'` |
            | `{"$in": ["a", "b"]}` | está en la lista | `IN ('a','b')` |
            | `{"$exists": False}` | el campo **no está** en el documento | *no existe en SQL* |
            | `{"$regex": "sal", "$options": "i"}` | contiene ese texto | `LIKE '%sal%'` |

            **Dos claves en el mismo diccionario = AND.** Para OR: `{"$or": [{...}, {...}]}`.
            **Dentro de un arreglo:** `{"etiquetas.slug": "contraloria"}` busca en cada elemento.

            ## Resumir

            ```python
            coleccion.aggregate([
                {"$match":  {"n_palabras": {"$gt": 0}}},          # el WHERE
                {"$group":  {"_id": "$seccion",                    # el GROUP BY
                             "n": {"$sum": 1},
                             "prom": {"$avg": "$n_palabras"}}},
                {"$sort":   {"n": -1}},                            # el ORDER BY
                {"$limit":  10},                                   # el LIMIT
            ])
            ```

            **Filtra temprano, agrupa después.** `$match` antes de `$group` hace menos trabajo.

            Si el campo por el que quieres agrupar es una **lista**, desenróllala primero:
            `{"$unwind": "$etiquetas"}`. Después de eso los conteos **dejan de ser aditivos**.

            ## Escribir

            ```python
            coleccion.insert_many(lista_de_documentos)
            coleccion.update_one(filtro, {"$set": {"campo": valor}})   # NUNCA olvides $set
            coleccion.delete_many({})                                  # vaciar antes de recargar
            ```

            ## Los cinco errores que más cuestan

            | Síntoma | Qué pasó |
            |---|---|
            | `NameError` | el entorno se reinició: vuelve al Paso 0 y ejecuta hacia abajo |
            | `E11000 duplicate key` | estás insertando dos veces el mismo `_id`: falta el `delete_many({})` |
            | 0 resultados y no entiendes por qué | revisa comillas, tildes y que el Paso 2 haya corrido |
            | `DtypeWarning` en rojo | es un **aviso**, no un error: la celda terminó bien |
            | el update no cambia nada | te faltó `$set` |
            """
        ),
        md(
            f"""
            ---
            # Referencias

            ## Datos usados en esta sesión

            - **Noticias de El Tiempo sobre contratación pública**, enero a agosto de 2026. Dos fuentes públicas enlazadas por el identificador
              numérico que aparece al final de cada URL:
              - índice mensual de artículos: `https://www.eltiempo.com/sitemap-articles-2026-MM.xml`
                (**57 848 artículos** entre enero y agosto)
              - contenido de cada artículo: `https://www.eltiempo.com/servicios/feeds/articulo/<ID>`
              - selección por tema, ya recolectada: [`Datos/noticias_contratacion_2026.json`]({DATOS_NOTICIAS})
                — **987 noticias** de las 995 que el filtro identificó
              - cruce con entidades contratantes: [`Datos/entidades_en_noticias_2026.json`]({DATOS_CRUCE})
            - **SECOP II**, muestra de procesos de contratación: [`prueba_chunk_0000000.csv`]({DATOS_SECOP})

            > **Nota sobre la recolección.** Las noticias se descargaron **una sola vez**, del lado del docente, con
            > pausa entre peticiones y un identificador de agente visible. En clase leemos el archivo ya versionado
            > en el repositorio: diez runtimes pidiendo artículos al mismo tiempo sería descortés con la fuente y
            > frágil para nosotros. Los scripts son `utils/build_eltiempo_dataset.py` (recolección) y
            > `utils/cruzar_noticias_secop.py` (cruce), y puedes leerlos: forman parte del material de la sesión.

            ## Documentación oficial

            - [Mapa de equivalencias SQL ↔ MongoDB](https://www.mongodb.com/docs/manual/reference/sql-comparison/)
            - [Mapa de equivalencias SQL ↔ agregación](https://www.mongodb.com/docs/manual/reference/sql-aggregation-comparison/)
            - [Operadores de consulta](https://www.mongodb.com/docs/manual/reference/operator/query/)
            - [Preferencia de lectura y réplicas](https://www.mongodb.com/docs/manual/core/read-preference/)

            ## Texto guía

            - Khattak, W., Buhler, P. y Erl, T. (2016). *Big Data Fundamentals: Concepts, Drivers & Techniques*.
              Pearson. **Capítulo 5**, "Big Data Storage Concepts" (clústeres, fragmentación, replicación, ACID y
              BASE) y **capítulo 7**, "Big Data Storage Technology" (las cuatro familias NoSQL).
            """
        ),
    ]
    return cells


def insertar_diagramas(cells):
    """
    Sustituye los marcadores {svg("nombre", "texto alternativo")} por la imagen.

    Se hace despues de construir las celdas y no con f-strings porque casi
    todas contienen llaves —JSON, filtros de MongoDB, f-strings de ejemplo— y
    convertirlas en f-strings las romperia. El marcador es explicito y no
    colisiona con nada del contenido.
    """
    patron = re.compile(r'\{svg\("([^"]+)",\s*"([^"]+)"\)\}')
    faltantes = []
    for celda in cells:
        texto = "".join(celda["source"])
        if "{svg(" not in texto:
            continue

        def reemplazo(m):
            try:
                return svg(m.group(1), m.group(2))
            except FileNotFoundError:
                faltantes.append(m.group(1))
                return m.group(0)

        celda["source"] = _lineas(patron.sub(reemplazo, texto))

    if faltantes:
        raise FileNotFoundError(
            "Faltan diagramas en assets/diagrams/session3/: " + ", ".join(faltantes)
        )
    return cells


def _lineas(texto):
    """Vuelve a partir un texto en el formato source[] de nbformat."""
    partes = texto.split("\n")
    return [l + "\n" for l in partes[:-1]] + [partes[-1]]


def main():
    cells = insertar_diagramas(build_cells())
    validate(cells)
    save(cells, OUTPUT)


if __name__ == "__main__":
    main()
