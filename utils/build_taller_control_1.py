#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Generador del cuaderno TC1 (S08) · V9.

Fuente única: utils/tc1_contrato.py (rúbrica, ventanas, checkpoints, opciones de las listas,
diccionario de las fuentes) y los módulos utils/tc1_*.py, que se incrustan en una celda oculta
con su SHA-256.

Uso:
    python utils/build_taller_control_1.py           # regenera Cuadernos/Taller_Control_1.ipynb
    python utils/build_taller_control_1.py --check   # falla si el cuaderno versionado no coincide
'''
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
sys.path.insert(0, str(ROOT))

import tc1_contrato as C  # noqa: E402
from utils.make_notebook import build, code, md, validate  # noqa: E402

DESTINO = ROOT / "Cuadernos" / "Taller_Control_1.ipynb"
MODULOS = ["tc1_contrato.py", "tc1_secop.py", "tc1_servicios.py", "tc1_validador.py", "tc1_cuaderno.py"]
REPO = "https://github.com/jazaineam1/BigData2026/blob/main/utils/"
# Nombre con que el cuaderno llama a cada módulo: descriptivo, para que una línea como
# taller.checkpoint("E2") se lea sola.
ALIAS = {"tc1_contrato.py": "reglas", "tc1_secop.py": "secop", "tc1_servicios.py": "plataformas",
         "tc1_validador.py": "validador", "tc1_cuaderno.py": "taller"}


def opciones(lista):
    return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in lista) + "]"


def miles(n):
    return f"{n:,}".replace(",", ".")


MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre"]


def mes_es(clave):
    anio, mes = clave.split("-")
    return f"{MESES[int(mes) - 1]} de {anio}"


def rango_datos():
    '''Rangos reales de las ventanas (Datos/tc1_ventanas_resumen.json): el texto del cuaderno no se escribe a mano.'''
    v = json.loads((ROOT / "Datos" / "tc1_ventanas_resumen.json").read_text(encoding="utf-8"))["ventanas"].values()
    rango = lambda xs: (min(xs), max(xs))
    return {"cruzan": rango([x["matched_processes"] for x in v]),
            # Con un decimal: redondear a entero convertía un 10,45 % real en «10 %», que en E6.2 cae en otro rango.
            "cobertura": tuple(f"{100 * c:.1f}".replace(".", ",") for c in rango([x["join_coverage"] for x in v])),
            "repetidas": rango([x["procesos"]["descargados"] - x["procesos"]["unicos"] for x in v]),
            "procesos_api": rango([x["procesos"]["total_api"] for x in v]),
            "contratos_api": rango([x["contratos"]["total_api"] for x in v])}


def ficha(etapa, objetivo, pregunta, donde, provisto, pasos, evidencia, puntos):
    filas = [
        ("Objetivo", objetivo), ("Pregunta", pregunta), ("Dónde trabajas", donde), ("Ya está provisto", provisto),
        ("Tú haces", "<br>".join(f"{i}. {p}" for i, p in enumerate(pasos, 1))),
        ("Checkpoint para avanzar", "<br>".join(f"☐ {c}" for c in C.CHECKPOINTS[etapa])),
        ("Evidencia que queda", evidencia), ("Puntos", puntos),
    ]
    tabla = "\n".join(f"| **{k}** | {v} |" for k, v in filas)
    return md(f"# {etapa} · {C.STAGE_NOMBRE[etapa]} — {C.STAGE_MAX[etapa]} puntos\n\n| | |\n|---|---|\n{tabla}")


def lectura(como, dice, no_permite, error):
    return md(f"**Cómo se lee.** {como}\n\n**Qué nos dice.** {dice}\n\n"
              f"**Qué NO permite concluir todavía.** {no_permite}\n\n**Qué error común.** {error}")


def tabla_diccionario(fuente):
    return "\n".join(f"| {' · '.join(f'`{c}`' for c in cols)} | {que} | {uso} |" for cols, que, uso in C.DICCIONARIO[fuente])


def arbol_zip():
    etapas = list(C.ARTEFACTOS)
    lineas = ["TC1_<PAREJA_ID>.zip          ← tu carpeta de trabajo completa", "├── identidad.json", f"├── {C.MANIFEST}"]
    for i, e in enumerate(etapas):
        rama, sigue = ("└──", "   ") if i == len(etapas) - 1 else ("├──", "│  ")
        archivos = [a for a in C.ARTEFACTOS[e] if "/" not in a]
        lineas.append(f"{rama} {e}/ " + " · ".join(archivos))
        if e == "E1":
            lineas.append(f"{sigue}    raw/procesos.parquet · raw/contratos.parquet · raw/pages/ (páginas firmadas)")
    return "\n".join(lineas)


def celda_infraestructura():
    lineas = ["#@title Preparar el entorno · EJECUTA una vez por sesión · instala dos librerías y carga la infraestructura provista (no se evalúa)",
              "# Código legible y versionado: " + REPO + "tc1_contrato.py (y los demás utils/tc1_*.py).",
              "# Aquí va comprimido para que un solo Ctrl+Enter deje todo listo; el SHA-256 comprueba que el bloque no se dañó al copiarlo.",
              "# El docente no confía en esta celda: recalcula tu ZIP con su propia copia del validador.",
              "import base64, hashlib, importlib, subprocess, sys, zlib",
              "from pathlib import Path",
              "subprocess.run([sys.executable, '-m', 'pip', '-q', 'install', 'pymongo>=4.6,<5', 'neo4j>=5,<7'], check=False)",
              "MODULOS = {"]
    for nombre in MODULOS:
        fuente = (ROOT / "utils" / nombre).read_bytes().replace(b"\r\n", b"\n")
        sha = hashlib.sha256(fuente).hexdigest()
        blob = base64.b64encode(zlib.compress(fuente, 9)).decode()
        partes = [blob[i:i + 120] for i in range(0, len(blob), 120)]
        lineas.append(f"    {nombre!r}: ({sha!r},")
        lineas += [f"        {p!r}" for p in partes]
        lineas.append("    ),")
    importaciones = ", ".join(f"{n[:-3]} as {a}" for n, a in ALIAS.items())
    lineas += [
        "}",
        "for nombre, (sha, blob) in MODULOS.items():",
        "    fuente = zlib.decompress(base64.b64decode(blob))",
        "    assert hashlib.sha256(fuente).hexdigest() == sha, f'{nombre} no coincide con la versión oficial'",
        "    Path(nombre).write_bytes(fuente)",
        "import time, json",
        "from concurrent.futures import ThreadPoolExecutor, as_completed",
        "import pandas as pd",
        f"import {importaciones}",
        f"for modulo in ({', '.join(ALIAS.values())}):",
        "    importlib.reload(modulo)",
        "print(f'TC1 {reglas.VERSION_VISIBLE} listo. Siguiente paso: la celda «0 · Identidad de la pareja».')",
    ]
    return code("\n".join(lineas))


def cells():
    rubrica = "\n".join(f"| {cod} | {desc} | {pts} | {'automático' if t == 'auto' else 'automático + captura'} |"
                        for cod, _, pts, desc, t in C.RUBRICA)
    D = rango_datos()
    return [
        md(f'<a href="{C.COLAB_URL}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" '
           'alt="Abrir el TC1 en Google Colab"/></a>'),
        md(f'''# TC1 · Un snapshot de SECOP, tres preguntas, tres modelos

**VERSIÓN {C.VERSION_VISIBLE}** · Taller de Control 1 · Big Data · Maestría en Analítica de Datos · Universidad Central

## El problema de Laura

Laura coordina la revisión de compras públicas en **Compras Claras**. SECOP II registra decenas de miles de procesos cada mes y su equipo alcanza a revisar unos cien. Necesita decidir **dónde mirar primero**, no si hay irregularidad. Te pide cuatro cosas, y cada una es una etapa del taller:

| Laura necesita | Etapa | Modelo que lo resuelve |
|---|---|---|
| un snapshot de SECOP en el que pueda confiar y que otro pueda recalcular | E1 | archivos firmados (Parquet + SHA-256) |
| leer cada proceso completo, con sus contratos, y una bandeja de hasta cien para revisar | E2 · E3 | documentos (MongoDB Atlas) |
| servir esa bandeja al instante por año y departamento | E4 | tabla diseñada desde su consulta (Cassandra en Astra) |
| saber qué proveedores conectan una entidad con otras | E5 | grafo (Neo4j Aura) |

E6 cierra con tus decisiones y con lo que tus datos todavía **no** permiten concluir.

## OBJETIVO DEL TC1

Construir, en parejas, un pipeline reproducible sobre SECOP II y demostrar que **un mismo snapshot** se reutiliza en distintos modelos de datos según la pregunta que hay que responder. Al terminar habrás demostrado:

1. **adquisición reproducible**: la descarga secuencial y la concurrente producen el mismo snapshot;
2. **modelo documental**: un proceso es un documento en MongoDB Atlas, cargado sin duplicar;
3. **producto analítico**: una bandeja priorizada construida en Atlas;
4. **patrón query-first**: una tabla Cassandra diseñada desde su consulta y ejecutada en Astra;
5. **contexto relacional**: los proveedores que conectan entidades, consultados en Neo4j Aura;
6. **evidencia reproducible**: el docente puede recalcular tu resultado sin confiar en tu palabra.

| Pregunta | Respuesta |
|---|---|
| ¿Qué voy a entregar? | Tres archivos: `TC1_<PAREJA_ID>.ipynb`, `TC1_<PAREJA_ID>.zip` y `manifest_tc1.json`, en una carpeta de Drive restringida, más un correo. |
| ¿Qué necesito antes de empezar? | Un nombre para tu pareja (el que quieras), los códigos de los integrantes y tus tres cuentas activas: Atlas, Astra y Aura. |
| ¿Puedo trabajar solo? | Sí: deja vacíos los tres campos del integrante 2. El taller, la rúbrica y la entrega son los mismos. |
| ¿Dónde trabajo? | E1 Colab · E2 Colab + **Atlas** · E3 **Atlas** + Colab · E4 Colab + **Astra** · E5 Colab + **Aura** · E6 Colab |
| ¿Cómo sé si puedo avanzar? | Cada etapa termina en un **checkpoint** que imprime ✓ o ✗, dice qué falta y lista los archivos que dejó la etapa. |
| ¿Cómo me califican? | Resultados que se recalculan desde tus archivos + tres capturas de los servicios. |

**HAZ ESTO AHORA.** Abre el [checklist paso a paso]({C.CHECKLIST_URL}) en otra pestaña. Marca cada paso cuando su evidencia exista.'''),
        md(f'''## La ruta: un hilo, seis etapas

| Etapa | Pregunta que responde | Dónde trabajas | Evidencia que queda |
|---|---|---|---|
| **E1** · 25 | ¿Puedo usar concurrencia sin alterar la población descargada? | Colab | RAW firmado + benchmark + calidad |
| **E2** · 25 | ¿Cómo represento un proceso como documento y lo cargo sin duplicar? | Colab → **Atlas** | modelo JSON + evidencia de Atlas |
| **E3** · 10 | ¿Qué procesos reviso primero? | **Atlas** → Colab | pipeline + bandeja CSV + `E2_atlas.png` |
| **E4** · 15 | Dado un año y un departamento, ¿cuáles son los 10 procesos de mayor valor? | Colab → **Astra** | `.cql` + salida de Astra + `E4_astra.png` |
| **E5** · 15 | ¿Qué proveedores conectan a la entidad ancla con otras entidades? | Colab → **Aura** | `.cypher` + ranking + `E5_neo4j.png` |
| **E6** · 10 | ¿Qué decidí, con qué evidencia y con qué límite? | Colab | decisiones + informe + paquete |

**Por qué este orden.** Lo que produce una etapa es la entrada de la siguiente: el RAW de E1 se convierte en los documentos de E2; la colección de E2 produce la bandeja de E3; la bandeja de E3 es lo que E4 sirve en Cassandra; los contratos de E1 forman el grafo de E5, y E6 decide con todo lo anterior. Cada motor aparece porque responde una pregunta distinta: Atlas filtra y agrega documentos; Cassandra sirve una consulta conocida de antemano; Neo4j recorre relaciones.

### Calificación

**100 puntos, grupal**: la misma nota para todos los integrantes. `nota = 1 + 4 × puntaje / 100` (50 → 3,0 · 75 → 4,0 · 100 → 5,0). Se registra con un decimal, como pide el PDA (4,84 → 4,8). Sin entrega: 0,0. Corresponde al componente *primer taller de evaluación (teórico-práctico)* del PDA; el docente confirma su porcentaje con el PDA vigente.

<details><summary><b>Rúbrica completa: 22 controles, todos verificables</b></summary>

| Control | Qué se verifica | Puntos | Cómo |
|---|---|---:|---|
{rubrica}
| | **TOTAL** | **100** | |

Con captura: resultado correcto + captura válida = puntaje completo; resultado correcto sin captura válida = puntaje parcial (E2.6: 1 de 3 · E4.3: 2 de 4 · E5.4: 1 de 2); resultado incorrecto = 0. **Una captura sola no da puntos.** El docente vuelve a calcular todo desde tu ZIP con el mismo validador y revisa las tres capturas.
</details>

### Entrega

**Fecha máxima: {C.FECHA_LIMITE}.** Una carpeta de Google Drive **restringida**, compartida con `{C.CORREO_DOCENTE}` como Lector, con exactamente los tres archivos, y un correo institucional. El LMS no es canal de entrega. GitHub es opcional. El último bloque del cuaderno deja los tres archivos listos.'''),
        md(f'''## Antes de empezar: tus tres cuentas

| Servicio | Lo usas en | Revisa hoy | Si no está |
|---|---|---|---|
| MongoDB Atlas (M0) | E2, E3 | clúster activo, usuario de base de datos y Network Access con **0.0.0.0/0**: Colab no tiene IP fija, así que tu IP de casa no sirve | Atlas **pausa** los clústeres gratuitos tras 30 días sin conexiones: si dice *Paused*, pulsa *Resume*. Si la regla 0.0.0.0/0 de S04 venció o la borraste, vuelve a agregarla ([tutorial de conexión de S04](https://jazaineam1.github.io/BigData2026/assets/tutoriales/atlas-guia-conexion.html)) |
| Astra DB (Serverless non-vector) | E4 | la base está **Active** y tiene el keyspace `compras_claras` | Astra pone en *Hibernated* las bases gratuitas tras 48 h sin uso y **las borra a los 30 días**: pulsa *Resume* o crea una nueva ([tutorial S05](https://jazaineam1.github.io/BigData2026/assets/tutoriales/astra-cassandra-paso-a-paso-v3.html)) |
| Neo4j Aura Free | E5 | la instancia está **Running** y tienes su contraseña | Aura pausa la instancia tras 72 h sin uso y **la borra si sigue pausada 30 días**: reanúdala o crea otra ([tutorial S06](https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-aura-s06-paso-a-paso.html)). Si creas otra, guarda en ese momento la URI, el usuario y la contraseña (descarga el archivo de credenciales que ofrece Aura): es lo que pide E5.1 |

**OJO.** Si una plataforma falla de verdad (caída del servicio o cuenta bloqueada), escríbelo en el correo con una captura del error y el docente decide la excepción. Lo que no depende del servicio se califica igual: por ejemplo, el diseño de tu `.cql` (E4.2) y tu archivo Cypher (E5.3).

### Qué está provisto y qué haces tú

| Provisto: no se califica reescribirlo | Tú decides o escribes: se califica |
|---|---|
| cliente HTTP con reintentos, caché firmado por páginas, hash canónico | la descarga secuencial y la concurrente con `ThreadPoolExecutor` (un hueco) |
| carga técnica a Atlas y a Aura (Atlas no importa archivos desde el navegador; S04 cargó igual) | el grano documental, la estrategia de carga, los índices, el filtro A, el orden B y el pipeline E3, **en Atlas** |
| el script CQL que se genera desde tus decisiones | la partición, el clustering y el tipo de la tabla; ejecutarla **en Astra** |
| el validador y el empaquetado | la consulta Cypher de compartidos (un hueco) y la de ranking (la escribes completa), ejecutadas **en Aura**; las decisiones de E6 |

### Cómo leer cada celda

El título de cada celda empieza por lo que te toca hacer:

| En el título | Qué haces |
|---|---|
| **EJECUTA** | pulsa ▶ y lee la salida: no hay nada que editar |
| **ELIGE** | escoge en las listas o escribe en los campos de la derecha (nombres, códigos, números) y ejecuta |
| **COMPLETA** | reemplaza el único `____` del código y ejecuta |
| **ESCRIBE** | escribe tú el código completo: la celda dice qué debe devolver y te muestra si coincide |
| **PEGA** | pega entre las `\'\'\'` lo que copiaste del servicio y ejecuta |
| **CAPTURA** | ejecuta y sube la imagen PNG que se pide |
| **SAL DE COLAB** (en el texto) | trabaja en Atlas, Astra o Aura con los pasos numerados y vuelve |

La celda siguiente carga cinco módulos. En el cuaderno los verás con estos nombres:

| Nombre | Módulo | Qué hace |
|---|---|---|
| `taller` | `tc1_cuaderno.py` | un paso por celda: guarda la evidencia de cada etapa y te la muestra |
| `secop` | `tc1_secop.py` | cliente de la API con reintentos, caché firmado, hash, documentos y consultas de referencia |
| `plataformas` | `tc1_servicios.py` | conexión a Atlas y Aura, lectura de lo que pegas, capturas, Drive y ZIP |
| `validador` | `tc1_validador.py` | el validador: el mismo que el docente ejecuta sobre tu ZIP |
| `reglas` | `tc1_contrato.py` | ventanas, rúbrica, nombres de archivos y checkpoints |

<details><summary>Dónde queda cada cosa que produces</summary>

| Dónde | Qué guarda | Quién lo crea |
|---|---|---|
| Colab: carpeta `tc1_<PAREJA_ID>` | todo lo que se califica, por etapa (`E1/` … `E6/`): es el contenido del ZIP | el cuaderno, celda a celda |
| Drive: `TC1_BIGDATA_<PAREJA_ID>/avance/` | una copia de tu carpeta tras cada checkpoint, para recuperarla si Colab se reinicia | el cuaderno, si activas el avance |
| Drive: `TC1_BIGDATA_<PAREJA_ID>_<APELLIDOS>/` | los tres archivos de la entrega: es la **única** carpeta que compartes | la celda Entregar |
| Atlas: base `{C.ATLAS_DB}`, colección `tc1_<pareja en minúscula>` | un documento por proceso | E2.2 carga; tú creas los índices y el pipeline |
| Astra: keyspace `{C.KEYSPACE_DEFECTO}`, tabla `tc1_<pareja en minúscula>_prioridades` | tu bandeja, servida por año y departamento | tú, pegando el script de E4 |
| Aura: nodos `Entidad`, `Contrato`, `Proveedor` | el grafo de tus contratos | E5.1 carga; tú consultas |
</details>

**Regla de avance.** No avances porque existe una celda siguiente: avanza cuando el checkpoint de la etapa esté en ✓, o cuando te diga que puedes pasar porque lo único pendiente es una captura que se sube en la etapa siguiente. Si E3 no queda completa, E4 trabaja con una bandeja de referencia: pierdes los puntos de E3, no los de E4.'''),
        celda_infraestructura(),
        md(f'''## 0 · Identidad de la pareja

| Campo | Qué escribes | Para qué sirve |
|---|---|---|
| `PAREJA_ID` | el nombre de tu pareja, el que quieras: un número, una palabra… (por ejemplo, el que ya venías usando) | nombra tu carpeta, tu colección de Atlas, tu tabla de Astra y tus archivos |
| `CODIGO_1` · `CODIGO_2` | el código de cada integrante | fija tu **ventana de datos** de SECOP |
| `APELLIDO_1` · `APELLIDO_2` | el primer apellido de cada integrante | nombra tu carpeta de entrega |

**Tu ventana de datos sale de los códigos, no del nombre.** Escribir el mismo nombre que otra pareja (por ejemplo, «1») no les da los mismos datos. Como hay {len(C.VENTANAS)} ventanas, dos parejas distintas pueden coincidir por azar en la misma; aun así, tus decisiones de E6 y tus capturas salen de tu trabajo. Cada ventana empieza el día 1 de un mes entre {mes_es(C.ORDEN_VENTANAS[0])} y {mes_es(C.ORDEN_VENTANAS[-1])} ({len(C.VENTANAS)} posibles, todas verificadas); la celda te dice cuál te tocó y los nombres exactos que usarás en Atlas y Astra.

**OJO.** Escribe el mismo nombre y los mismos códigos en cada sesión. Si cambias un código, cambia tu ventana y la descarga de E1 deja de ser tuya (la celda te avisa); si cambias el nombre, el cuaderno empieza una carpeta nueva.

**Quién ejecuta.** Un solo integrante ejecuta el cuaderno, con **sus** cuentas de Google, Atlas, Astra y Aura; el otro trabaja a su lado. El avance en Drive queda en la cuenta de Google de quien ejecuta: si cambian de computador, sigue ejecutando la misma persona.

Si trabajas solo, deja vacíos los tres campos del integrante 2 (nombre, código y apellido): tu ventana sale de tu código y tu carpeta de entrega lleva solo tu apellido. Los nombres y códigos solo viajan en tu entrega privada al docente; no los publiques. Guardar el avance en Drive deja una copia de tu carpeta de trabajo tras cada checkpoint: si Colab se reinicia, al volver a ejecutar esta celda recuperas lo hecho.'''),
        code(f'''#@title 0 · ELIGE · Identidad de la pareja {{ display-mode: "form" }}
PAREJA_ID = "" #@param {{type:"string"}}
INTEGRANTE_1 = "" #@param {{type:"string"}}
CODIGO_1 = "" #@param {{type:"string"}}
APELLIDO_1 = "" #@param {{type:"string"}}
INTEGRANTE_2 = "" #@param {{type:"string"}}
CODIGO_2 = "" #@param {{type:"string"}}
APELLIDO_2 = "" #@param {{type:"string"}}
GUARDAR_AVANCE_EN_DRIVE = "Sí (recomendado)" #@param ["Sí (recomendado)", "No"]

OUT, DRIVE = taller.iniciar(PAREJA_ID, [(INTEGRANTE_1, CODIGO_1, APELLIDO_1), (INTEGRANTE_2, CODIGO_2, APELLIDO_2)],
                            GUARDAR_AVANCE_EN_DRIVE)'''),
        ficha("E1",
              "Demostrar que una descarga secuencial y una concurrente producen exactamente el mismo snapshot.",
              "¿Puedo usar concurrencia sin alterar la población descargada?",
              "Google Colab.",
              "cliente HTTP con reintentos y backoff; caché por páginas con firma de la consulta y SHA-256; escritura atómica (un `.part` nunca cuenta como página); conteos; hash canónico.",
              ["Lee qué trae cada fuente y ejecuta el contrato de datos y la prueba de 50 filas.",
               "Ejecuta el preflight y la descarga secuencial.",
               "Mira cómo funciona una huella SHA-256.",
               "Completa el hueco de la descarga concurrente y compara offsets, filas y hash.",
               "Descarga los contratos con tu misma función concurrente, consolida el RAW y corre el checkpoint.",
               "Abre tu RAW y mira un proceso junto a su contrato."],
              "`E1/00_dataset_contract.json`, `E1/01_acquisition_manifest.json`, `E1/01_benchmark_threads.json`, `E1/01_quality_report.json` y `E1/raw/` (páginas firmadas + Parquet).",
              "25: contrato 4 · secuencial 4 · concurrencia equivalente 8 · trazabilidad 9. **No se exige speedup**: una ejecución concurrente más lenta también puede ser correcta."),
        md(f'''### E1.0 · Dos fuentes: el proceso y el contrato no son lo mismo

SECOP II publica la compra pública en dos conjuntos de datos, y vas a descargar los dos:

| | **Procesos** · `{C.ENDPOINTS['procesos']}` | **Contratos** · `{C.ENDPOINTS['contratos']}` |
|---|---|---|
| Una fila es | un **proceso de contratación**: la compra que una entidad abre y publica | un **contrato electrónico**: el acuerdo que la entidad firma con un proveedor |
| Nace | al publicarse (`fecha_de_publicacion_del`) | al firmarse (`fecha_de_firma`), días o semanas después |
| Su valor | `precio_base`: lo que la entidad estimó gastar | `valor_del_contrato`: lo que se pactó |
| Se identifica por | `id_del_proceso` (CO1.REQ.…) | `id_contrato` (CO1.PCCNTR.…) |
| Se enlaza por | `id_del_portafolio` (CO1.BDOS.…) | `proceso_de_compra` (CO1.BDOS.…) |
| Tu ventana de dos meses tiene | entre {miles(D['procesos_api'][0])} y {miles(D['procesos_api'][1])} registros, según la pareja | entre {miles(D['contratos_api'][0])} y {miles(D['contratos_api'][1])} contratos con empresas |
| Descargas | los primeros **{miles(C.TARGET_PROCESOS)}**: {C.TARGET_PROCESOS // C.PAGE_SIZE} páginas de {C.PAGE_SIZE}, dos veces (secuencial y concurrente) | los primeros **{miles(C.TARGET_CONTRATOS)}**: {C.TARGET_CONTRATOS // C.PAGE_SIZE} páginas de {C.PAGE_SIZE} |

**Cómo se unen.** Un proceso puede terminar sin contrato, con uno o con varios. El puente es el **portafolio**: `procesos.id_del_portafolio = contratos.proceso_de_compra`. El `id_del_proceso` (CO1.REQ) no existe en la tabla de contratos: cruzar por él da cero filas.

**Cuántos cruzan.** Pocos, y es lo esperado: en las {len(C.VENTANAS)} ventanas posibles, entre {D['cruzan'][0]} y {D['cruzan'][1]} procesos (del {D['cobertura'][0]} % al {D['cobertura'][1]} % de los únicos) encuentran su contrato, casi siempre uno por proceso. E1.4 imprime tu número y las fechas que cubre cada descarga; en E6 explicarás por qué es bajo.

<details><summary>Diccionario: qué trae cada columna que pides y dónde la usas</summary>

**Procesos** · `{C.ENDPOINTS['procesos']}` · {len(C.SELECT_PROCESOS)} columnas

| Columna | Qué contiene | Dónde la usas |
|---|---|---|
{tabla_diccionario("procesos")}

**Contratos** · `{C.ENDPOINTS['contratos']}` · {len(C.SELECT_CONTRATOS)} columnas

| Columna | Qué contiene | Dónde la usas |
|---|---|---|
{tabla_diccionario("contratos")}

La API de Socrata entrega todos los valores como texto; los números se convierten al construir los documentos (E2).
</details>

**Tu contrato de datos.** La consulta no se escribe a mano: sale del contrato de tu pareja y de tu ventana. La celda siguiente la imprime; después de ella están las tres ideas para leerla.

**Una decisión que ya está tomada, y por qué.** El snapshot de contratos guarda solo contratos con **personas jurídicas que no son consorcio** (`tipodocproveedor = 'NIT' AND es_grupo = 'No'`). La gran mayoría de contratos de SECOP son con personas naturales (en enero y febrero de 2025, el 94 %), que suelen firmar con una sola entidad y no forman red; los consorcios se crean para un solo proceso. Sin este filtro, la pregunta de E5 quedaba vacía, o con dos o tres proveedores, en las ventanas que se probaron. Con él, las {len(C.VENTANAS)} ventanas posibles tienen respuesta (`Datos/tc1_ventanas_resumen.json`).'''),
        code('''#@title E1.0 · EJECUTA · Contrato de datos de tu pareja { display-mode: "form" }
PLAN = taller.contrato_e1()'''),
        md(f'''### Tres ideas para leer lo que acabas de imprimir

| Idea | Qué es | Ejemplo para recordarla | En tu taller |
|---|---|---|---|
| **Snapshot** | una foto fija de los datos en un momento | el extracto bancario del día 30: tu cuenta sigue moviéndose, pero el extracto ya no cambia | SECOP se actualiza todos los días; tu análisis usa la foto que descargas en E1, y el docente la recalcula desde tu ZIP |
| **Filtrar en la API** | pedirle al servidor solo las filas (`$where`), las columnas (`$select`) y el orden (`$order`) que necesitas | en la biblioteca pides «los libros de economía de 2025»; no te llevas la biblioteca a casa para buscarlos allá | traes solo {len(C.SELECT_PROCESOS)} columnas de procesos y {len(C.SELECT_CONTRATOS)} de contratos, y solo de tu ventana |
| **Paginación** | la API entrega el resultado por partes: `$limit` dice cuántas filas trae cada página y `$offset` desde qué fila empieza | un libro de 3.000 páginas que te prestan de a 250: el préstamo que empieza en la página 500 es `offset = 500, limit = 250` | {C.TARGET_PROCESOS // C.PAGE_SIZE} páginas de procesos (offsets 0, 250, …, {miles(C.TARGET_PROCESOS - C.PAGE_SIZE)}) y {C.TARGET_CONTRATOS // C.PAGE_SIZE} de contratos |

**Pruébalo mentalmente** (no se califica): si pides dos veces `offset = 250, limit = 250`, ¿obtienes filas nuevas? No: obtienes la misma página. Por eso cada descarga se guarda por su `offset`, y por eso la descarga concurrente de E1.3 debe pedir los mismos offsets que la secuencial.'''),
        code('''# E1.1 · EJECUTA · Prueba pequeña antes de descargar: 50 filas reales
q = PLAN["procesos"]
muestra, meta = secop.fetch_page(q["endpoint"], select=q["select"], where=q["where"], order=q["order"], limit=50, offset=0)
print(f"{len(muestra)} filas en {meta['elapsed_s']} s (intento {meta['attempts']})")
pd.DataFrame(muestra)[["id_del_proceso", "entidad", "fecha_de_publicacion_del", "precio_base"]].head(5)'''),
        lectura("Cada fila es un registro de la API de procesos. `id_del_proceso` identifica el proceso; la misma clave puede repetirse si SECOP trae varias filas para un proceso.",
                "La consulta, los filtros y el orden funcionan antes de lanzar miles de peticiones.",
                "Cuántos registros existen en tu ventana ni cuántas páginas hay que pedir: eso lo dice el preflight.",
                "Lanzar la descarga completa sin probar la consulta. Un nombre de columna mal escrito no se corrige reintentando."),
        code('''#@title E1.2a · EJECUTA · Preflight: cuántos registros hay y qué páginas pedir { display-mode: "form" }
pagina_secuencial, pagina_concurrente, OFFSETS, N_PROCESOS = taller.preflight_e1()'''),
        lectura("La primera cifra de cada línea es lo que existe en tu ventana; la segunda, lo que vas a descargar (los primeros registros, en el orden de la consulta).",
                "Cuántas páginas pedirás y que tu ventana tiene más registros de los que descargas.",
                "Que tu snapshot represente la ventana completa: descargas los primeros N de M registros, ordenados por fecha. Ahí nace el límite de cobertura que defenderás en E6.2.",
                "Leer el total de la ventana como el tamaño de tu snapshot."),
        md('''### E1.2 · Qué pasa con cada página que descargas

| Idea | Qué es | Ejemplo para recordarla | En tu taller |
|---|---|---|---|
| **Caché** | guardar lo que ya descargaste para no pedirlo otra vez | fotocopias el capítulo que necesitas para no volver a la biblioteca | cada página queda en `E1/raw/pages/`; si vuelves a ejecutar, se lee del disco. Por eso una segunda corrida es casi instantánea y sus tiempos no sirven para comparar velocidades |
| **Escritura atómica** | el archivo se escribe primero como borrador (`.part`) y solo cuando está completo se renombra | no firmas un contrato hasta que tiene todas sus páginas | si Colab se cae a mitad de una página, queda un `.part` que nunca cuenta como página descargada: no hay páginas a medias |'''),
        code('''# E1.2b · EJECUTA · Descarga secuencial: una página después de otra
def descargar_secuencial(descargar_pagina, offsets):
    paginas = {}
    for offset in offsets:
        paginas[offset] = descargar_pagina(offset)      # cada llamada devuelve (filas, metadatos)
    return paginas

inicio = time.perf_counter()
paginas_seq = descargar_secuencial(pagina_secuencial, OFFSETS)
SEG_SEQ = time.perf_counter() - inicio
print(f"Secuencial: {sum(len(f) for f, _ in paginas_seq.values()):,} filas en {SEG_SEQ:.1f} s · {len(paginas_seq)} páginas")'''),
        md('''### E1.2c · Una huella para comparar sin mirar fila por fila

Para saber si la descarga concurrente trae lo mismo que la secuencial no se comparan 3.000 filas a ojo: se compara su **huella SHA-256**, un resumen de 64 caracteres que cambia por completo si cambia un solo carácter del contenido.

**Función usada: `hashlib.sha256`**

| | |
|---|---|
| Para qué sirve | calcular la huella de unos bytes |
| Parámetros usados | los bytes del contenido (`texto.encode("utf-8")`) |
| Qué devuelve | un objeto; `.hexdigest()` da la huella como 64 caracteres hexadecimales |
| Cómo se interpreta | huellas iguales = contenido idéntico; huellas distintas = algo cambió |
| Error frecuente | olvidar que el orden cuenta: las mismas filas en otro orden dan otra huella |

El TC1 usa la misma idea en cinco lugares:

| Huella de… | Dónde queda | Qué demuestra |
|---|---|---|
| cada página descargada | `E1/raw/pages/…/page_*.meta.json` | que la página no cambió después de registrar su huella |
| la consulta que pidió la página (`query_signature`) | el mismo `.meta.json` | que la página salió de **tu** consulta oficial |
| el snapshot completo, con las filas en orden canónico | `E1/01_benchmark_threads.json` | que secuencial y concurrente trajeron lo mismo, llegara en el orden que llegara |
| cada módulo `tc1_*.py` | la celda «Preparar el entorno» | que usas la infraestructura oficial |
| `manifest_tc1.json` | la **huella de entrega** de tu correo | que el manifest que el docente abre es el que enviaste |'''),
        code('''# E1.2c · EJECUTA · Un carácter distinto produce una huella irreconocible
import hashlib

for texto in ["CO1.REQ.7614406", "CO1.REQ.7614407"]:
    huella = hashlib.sha256(texto.encode("utf-8")).hexdigest()
    print(f"{texto} → {huella}")'''),
        lectura("Cada línea muestra un texto y su huella: 64 caracteres hexadecimales (256 bits). Los dos textos solo difieren en el último dígito.",
                "Un cambio mínimo produce una huella sin parecido con la anterior, y el mismo texto produce siempre la misma huella. Por eso comparar dos huellas equivale a comparar todo el contenido.",
                "Qué cambió ni dónde: la huella dice «son distintos», no «en qué fila». Para saberlo hay que mirar los datos. Tampoco permite reconstruir el contenido a partir de la huella.",
                "Calcular la huella del DataFrame tal como llegó: si las páginas llegan en otro orden, la huella cambia aunque las filas sean las mismas. Por eso el TC1 ordena las filas de forma canónica antes de calcularla."),
        md('''### E1.3 · La misma descarga con `ThreadPoolExecutor`

Pedir páginas a una API es trabajo **I/O-bound**: casi todo el tiempo Python espera la red. Varios hilos pueden esperar a la vez sin cambiar qué se descarga.

**Ejemplo.** Tienes que pedir 12 pizzas por teléfono. Con un solo teléfono llamas, esperas la confirmación y vuelves a llamar: casi todo el tiempo esperas (eso es la descarga secuencial). Con 4 teléfonos —4 *workers*— cuatro pedidos esperan a la vez: la cocina no es más rápida, pero tú esperas en paralelo. Eso es un trabajo **I/O-bound**: el tiempo se va esperando, no calculando. Si el trabajo fuera calcular (*CPU-bound*), más hilos de Python no lo acelerarían.

**Speedup** = tiempo secuencial ÷ tiempo concurrente: 2,0 es el doble de rápido; menos de 1, más lento. Aquí no se califica: se califica que las dos descargas traigan lo mismo.

**Y si pides demasiado rápido.** Una API protege su servidor limitando cuántas peticiones acepta. Si te pasas, responde **HTTP 429 Too Many Requests** y a veces agrega **Retry-After**: «vuelve en N segundos». El cliente del taller **reintenta con backoff**: espera 1 s, luego 2, 4, 8 y 16 s (o lo que diga Retry-After), hasta 6 intentos. Ejemplo: en una ventanilla te dicen «vuelva en diez minutos»; si vuelves cada segundo, no te atienden antes y retrasas a los demás. La celda E1.3 te dice cuántos reintentos y cuántos 429 hubo en tus descargas; en E6 decidirás qué hacer ante un 429.

**Función usada: `ThreadPoolExecutor` + `as_completed`**

| | |
|---|---|
| Para qué sirve | lanzar varias llamadas a la vez y recoger cada resultado cuando llega |
| Parámetros usados | `max_workers` (entre 2 y 6 en este taller) |
| Qué devuelve | `pool.submit(f, x)` devuelve un *futuro*; `as_completed` los entrega en orden de llegada |
| Cómo se interpreta | el orden de llegada cambia en cada ejecución; por eso se guarda cada página por su `offset` |
| Error frecuente | concatenar en orden de llegada, o pedir páginas distintas de las secuenciales |

**HAZ ESTO AHORA.** En la celda siguiente reemplaza `____` por el dato que identifica qué página debe descargar cada futuro.

**Error más probable:** `NameError: name '____' is not defined` significa que aún no completaste el hueco. Si pones otro valor (por ejemplo, `0`), verás *Mismos offsets ✓ · Mismas filas ✓ · Mismo hash ✗*: los offsets salen del diccionario y siempre coinciden, pero todos los futuros bajaron la misma página. No es que SECOP haya cambiado: revisa el hueco.

<details><summary>Si te atascas</summary>Cada futuro descarga <b>su</b> página: el argumento que falta es <code>offset</code>.</details>'''),
        code('''# E1.3 · COMPLETA · Descarga concurrente (un hueco)
MAX_WORKERS = 4   # entre 2 y 6

def descargar_concurrente(descargar_pagina, offsets, max_workers):
    paginas = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futuros = {pool.submit(descargar_pagina, ____): offset for offset in offsets}
        for futuro in as_completed(futuros):          # llegan en cualquier orden
            offset = futuros[futuro]
            paginas[offset] = futuro.result()
    return paginas

inicio = time.perf_counter()
paginas_thr = descargar_concurrente(pagina_concurrente, OFFSETS, MAX_WORKERS)
SEG_THR = time.perf_counter() - inicio
BENCH = taller.comparar_e1(paginas_seq, SEG_SEQ, paginas_thr, SEG_THR, MAX_WORKERS)'''),
        lectura("Mismos offsets: se pidieron las mismas páginas. Mismas filas: llegó la misma cantidad. Mismo hash: la huella del conjunto de filas, que no depende del orden y conserva los duplicados, es idéntica.",
                "Si las tres respuestas son ✓, la concurrencia cambió *cómo* se descargó, no *qué* se descargó.",
                "Que la concurrencia sea más rápida en general: con pocas páginas, la creación de hilos y la latencia pueden hacerla más lenta. Para afirmarlo harían falta varias corridas limpias, sin caché.",
                "Comparar solo el número de filas. Dos snapshots con las mismas 3.000 filas pueden tener filas distintas; por eso se compara el hash."),
        code('''#@title E1.4 · EJECUTA · Contratos con tu misma función concurrente y consolidación del RAW { display-mode: "form" }
pagina_contrato, OFFSETS_CONTRATOS = taller.descargador_contratos()
paginas_con = descargar_concurrente(pagina_contrato, OFFSETS_CONTRATOS, MAX_WORKERS)
CRUCE = taller.consolidar_e1(paginas_con)
_ = taller.checkpoint("E1")'''),
        lectura("La cobertura es la fracción de procesos únicos de tu snapshot que encontró al menos un contrato por `id_del_portafolio → proceso_de_compra`. Las fechas dicen qué días cubre realmente cada descarga.",
                "Hay población cruzada suficiente para E2–E4, y tu snapshot cubre **pocos días** del inicio de tu ventana, no los dos meses.",
                "Nada sobre la ventana completa ni sobre el año: es el comienzo de la ventana. Tampoco que los procesos sin contrato no tengan contrato: puede firmarse otro día o con una persona natural, que el filtro excluye.",
                "Rellenar con cero los procesos sin contrato o cruzar por `id_del_proceso`. La clave de cruce es `id_del_portafolio → proceso_de_compra`."),
        md('''### E1.5 · Tu RAW en Parquet: un proceso junto a su contrato

**RAW** son los datos tal como llegaron de la API, sin transformar: la base de la que sale todo lo demás, y la que el docente recalcula. E1.4 guardó tu RAW consolidado en dos archivos **Parquet**: `E1/raw/procesos.parquet` y `E1/raw/contratos.parquet`. Parquet es un formato **columnar**: guarda los valores de cada columna juntos y comprimidos, con el nombre y el tipo de cada columna. Por eso, en la prueba del taller, 3.000 procesos ocuparon unos 120 KB en Parquet frente a casi 2 MB en las páginas JSON, y leer dos columnas no obliga a leer las quince. Es el formato que leen pandas, Spark y Dask.

**Función usada: `pd.read_parquet`**

| | |
|---|---|
| Para qué sirve | leer un archivo Parquet como DataFrame |
| Parámetros usados | la ruta del archivo |
| Qué devuelve | un DataFrame con las columnas y los tipos guardados |
| Cómo se interpreta | aquí todas las columnas son texto: la API entrega texto y la conversión a número ocurre en E2 |
| Error frecuente | `FileNotFoundError`: E1.4 todavía no se ejecutó en esta sesión de trabajo |'''),
        code('''# E1.5 · EJECUTA · Abre tu RAW (Parquet) y mira un proceso junto a su contrato
RAW = reglas.rutas(OUT)["raw"]
procesos = pd.read_parquet(RAW / "procesos.parquet")
contratos = pd.read_parquet(RAW / "contratos.parquet")
print(f"procesos.parquet:  {procesos.shape[0]:,} filas × {procesos.shape[1]} columnas")
print(f"contratos.parquet: {contratos.shape[0]:,} filas × {contratos.shape[1]} columnas")

# El puente: el portafolio del proceso es el proceso_de_compra del contrato
cruzados = procesos.merge(contratos, left_on="id_del_portafolio", right_on="proceso_de_compra",
                          suffixes=("_proceso", "_contrato"))
uno = cruzados.iloc[0]
precio, valor = pd.to_numeric(uno["precio_base"], errors="coerce"), pd.to_numeric(uno["valor_del_contrato"], errors="coerce")
print(f"\\nPROCESO  {uno['id_del_proceso']} · portafolio {uno['id_del_portafolio']} · {uno['entidad']}")
print(f"  publicado el {uno['fecha_de_publicacion_del'][:10]} · precio base {precio:,.0f}")
print(f"CONTRATO {uno['id_contrato']} · proceso_de_compra {uno['proceso_de_compra']} · {uno['proveedor_adjudicado']}")
print(f"  firmado el {uno['fecha_de_firma'][:10]} · valor {valor:,.0f}")'''),
        lectura("Las dos primeras líneas dicen cuántas filas y columnas trae cada fuente. Las cuatro siguientes muestran un proceso y un contrato que comparten el portafolio (`CO1.BDOS…`).",
                "Proceso y contrato son registros distintos, con fechas y valores propios: el proceso se publica con un precio base estimado; el contrato se firma después, con un valor pactado y un proveedor.",
                "Que una diferencia entre precio base y valor del contrato sea irregular. Un caso no muestra un patrón, y falta el objeto de cada contrato y sus modificaciones, que este snapshot no descarga.",
                "Cruzar por `id_del_proceso`: ese identificador (CO1.REQ) no existe en contratos y el cruce queda vacío."),
        md('''**PARA LLEVAR.** Desde aquí no se vuelve a consultar la API: E2–E5 trabajan sobre este RAW consolidado y firmado. Si el checkpoint de E1 está en ✓, pasa a E2.'''),
        ficha("E2",
              "Representar un proceso SECOP como documento y comprobar que MongoDB Atlas responde las consultas del caso.",
              "¿Cómo represento un proceso como documento y lo cargo sin duplicar?",
              "Colab para preparar y cargar; **MongoDB Atlas → Data Explorer** (Documents, Indexes) para consultar.",
              "la construcción de los documentos según el grano que elijas, la conexión segura (`getpass`) y la carga técnica en dos pasadas.",
              ["Elige el grano y genera los documentos.", "Conecta Atlas y elige la estrategia de carga.",
               "En Atlas crea el índice único y un índice alineado con una consulta.", "En Atlas escribe el filtro A y pégalo aquí.",
               "En Atlas ordena y limita (consulta B) y pégalo aquí."],
              "`E2/02_modelo_documental.json`, `E2/02_secop_integrado.parquet`, `E2/02_atlas_evidence.json`; la captura `E2_atlas.png` se toma en E3.",
              "25: modelo documental 5 · Atlas idempotente 7 · índices 4 · consulta A 3 · consulta B 3 · evidencia + captura 3."),
        md(f'''### E2.1 · El grano: ¿qué es un documento?

SECOP puede traer varias filas para el mismo proceso: en las ventanas posibles, entre {D['repetidas'][0]} y {D['repetidas'][1]} de las {miles(C.TARGET_PROCESOS)} filas repiten un proceso ya visto. El caso necesita **un documento por proceso**, con sus contratos resumidos dentro. Estas son las rutas de campo que usarás en Atlas:

| Dato | Ruta en el documento |
|---|---|
| identificador | `{C.CAMPO['id']}` |
| precio base | `{C.CAMPO['precio_base']}` |
| año de publicación | `{C.CAMPO['anio']}` |
| departamento | `{C.CAMPO['departamento']}` |
| contratos cruzados | `{C.CAMPO['cantidad']}` |
| valor de los contratos | `{C.CAMPO['valor']}` |

<details><summary>Documento de ejemplo</summary>

```json
{json.dumps(C.EJEMPLO_DOCUMENTO, ensure_ascii=False, indent=2)}
```
</details>

**HAZ ESTO AHORA.** Elige el grano en la lista y ejecuta. Si eliges mal, la celda te muestra la consecuencia: puedes cambiarlo y repetir.'''),
        code(f'''#@title E2.1 · ELIGE · el grano del documento {{ display-mode: "form" }}
GRANO = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.GRANOS)}
DOCUMENTOS = taller.documentos_e2(GRANO)'''),
        lectura("Compara tres números: filas de la API, procesos únicos y documentos generados. Si coinciden los dos últimos y no hay identificadores repetidos, cada proceso es un documento.",
                "El grano define qué cuenta como «uno»: con un documento por fila, una consulta de los 10 procesos de mayor valor podría repetir el mismo proceso.",
                "Que los valores sean correctos: el grano solo garantiza que no se duplica la identidad. Para eso falta comparar cada valor con la página RAW de la que salió.",
                "Elegir el grano por comodidad («así viene de la API») y no por la pregunta que el documento debe responder."),
        md('''### E2.2 · Conectar Atlas y cargar sin duplicar

La carga se hace desde Colab porque el Data Explorer de Atlas no importa archivos, igual que en S04. **Tu decisión es cómo escribir**: la celda prueba tu estrategia dos veces en una colección de ensayo y luego hace la carga oficial.

**Idempotente** significa que repetir una operación deja el mismo resultado que hacerla una vez. Ejemplo: el botón «Guardar» de un documento es idempotente; «Pegar» no, porque cada vez agrega otra copia. Una carga debe ser idempotente porque en la vida real se repite: se corta la red, corriges un dato, vuelves a ejecutar la celda.

| Estrategia | Qué hace cada vez que se ejecuta |
|---|---|
| `insert_many` | agrega todos los documentos como nuevos |
| `insert_many` con índice único en `id_proceso` | agrega todos; la base rechaza los que repiten un `id_proceso` ya guardado |
| **upsert** por `id_proceso` (`UpdateOne` + `upsert=True`) | *update + insert*: busca cada documento por su `id_proceso`; si existe, actualiza los campos que envías (con `$set`; los que no envías se conservan); si no existe, lo inserta. Ejemplo: actualizar una lista de asistencia por código: si el código ya está, corriges su fila; si no, agregas una |

**OJO.** La URI se pide en un campo oculto (`getpass`). Nunca la escribas en una celda ni la imprimas: el validador bloquea la entrega si encuentra una URI con contraseña.'''),
        code('''#@title E2.2a · EJECUTA · Conectar Atlas (la URI se pide oculta) { display-mode: "form" }
ATLAS = taller.conectar_atlas_e2()'''),
        code(f'''#@title E2.2b · ELIGE · la estrategia de carga y ejecuta {{ display-mode: "form" }}
ESTRATEGIA = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.ESTRATEGIAS_CARGA)}
CARGA = taller.cargar_e2(ESTRATEGIA)'''),
        lectura("La primera y la segunda carga deben dejar el mismo número de documentos, sin errores y con 0 duplicados.",
                "Una carga **idempotente** se puede repetir, por un corte de red o por una corrección, sin alterar la colección.",
                "Que el contenido de cada documento en Atlas sea el correcto: la prueba cuenta documentos y duplicados, no compara campo por campo con tu RAW.",
                "Creer que «sin error» significa «sin duplicados»: `insert_many` duplica en silencio."),
        md(f'''### E2.3 · Índices: **SAL DE COLAB. AHORA TRABAJAS EN MONGODB ATLAS.**

**Índice.** Una estructura que lleva directo a los documentos que cumplen una condición, sin revisar toda la colección. Ejemplo: el índice alfabético de un libro te lleva a la página de «Cassandra» sin hojear las 300 páginas. Un **índice único** además impide que dos documentos tengan el mismo valor, como la cédula: no hay dos personas con el mismo número. Un índice ayuda a una consulta cuando su **primer campo** es el que esa consulta filtra u ordena; un índice sobre un campo que ninguna consulta usa solo ocupa espacio.

**HAZ ESTO AHORA.**
1. Atlas → **Data Explorer** → base `{C.ATLAS_DB}` → tu colección, la que imprimió la celda de identidad (por ejemplo `tc1_p03`). Comprueba que el número de documentos es el que imprimió E2.2.
2. Pestaña **Indexes** → **Create Index** → `{{ "id_proceso": 1 }}` y, en *Options*, marca **Create unique index**.
3. Crea **un índice más** cuyo primer campo use una consulta del taller (mira las consultas A, B y E3). Decide cuál y por qué: en E6 lo defenderás.
4. Vuelve y ejecuta la celda siguiente: lee los índices directamente de Atlas.'''),
        code('''#@title E2.3 · EJECUTA · Leer los índices que creaste en Atlas { display-mode: "form" }
INDICES = taller.indices_e2()'''),
        lectura("Cada línea es un índice de tu colección y sus campos (1 ascendente, -1 descendente). `_id_` lo crea Atlas siempre.",
                "Qué índices existen y si el primer campo de alguno coincide con lo que filtra u ordena una consulta del taller.",
                "Que tus consultas se volvieron más rápidas: para afirmarlo falta el plan de ejecución (*Explain* en Atlas) o medir el tiempo con y sin el índice.",
                "Crear un índice sobre un campo que ninguna consulta usa: ocupa espacio y no ayuda."),
        md('''### E2.4 · Consulta A en Atlas → Documents → Filter

**Pregunta:** ¿cuántos procesos tienen `precio base > 0` y **al menos un contrato** cruzado?

**HAZ ESTO AHORA.** Escribe el filtro en la barra *Filter* de tu colección, pulsa **Find** y mira el conteo. Luego copia el filtro **exactamente** como lo escribiste y pégalo entre las comillas de la celda siguiente.

**Así debe verse.** Un filtro tiene la forma `{ "ruta.del.campo": { "$operador": valor } }`; varias condiciones separadas por coma deben cumplirse todas. Por ejemplo, con otro campo: `{ "entidad.departamento": "Antioquia" }` deja solo los procesos de Antioquia. En la celda queda `FILTRO_A = \'\'\'{ … tu filtro … }\'\'\'` y la respuesta termina en `coincide con la referencia de tu snapshot: ✓ sí`.'''),
        code('''# E2.4 · PEGA · el filtro que escribiste en Atlas (Documents → Filter)
FILTRO_A = \'\'\'pega aquí tu filtro\'\'\'
CONTEO_A = taller.consulta_a_e2(FILTRO_A)'''),
        md('''### E2.5 · Consulta B en Atlas → Documents → Options

**Pregunta:** ¿cuáles son los 10 procesos con mayor valor de contratos? Desempate: `id_proceso` ascendente.

**HAZ ESTO AHORA.** En *Options* escribe el **Sort** y pon **Limit** en 10. Pulsa **Find**, comprueba el orden y pega aquí el Sort que usaste.

**Así debe verse.** Un Sort tiene la forma `{ "campo_principal": -1, "campo_de_desempate": 1 }` (-1 descendente, 1 ascendente). La celda imprime diez líneas `1. CO1.REQ.… · valor` y termina en `Top 10 igual a la referencia y en el mismo orden: ✓ sí`.'''),
        code('''# E2.5 · PEGA · el Sort que usaste en Atlas (Documents → Options → Sort)
ORDEN_B = \'\'\'pega aquí tu sort\'\'\'
TOP10_B = taller.consulta_b_e2(ORDEN_B)'''),
        lectura("El número de A y la lista de B salen de **tu** colección en Atlas: la celda vuelve a ejecutar lo que pegaste y lo compara con la referencia calculada desde tu RAW.",
                "Si las dos celdas dicen ✓ sí, tu modelo y tus consultas responden lo que el caso pregunta.",
                "Que esos procesos tengan sobrecosto: B ordena por valor y no dice si el valor es razonable; para eso falta un precio de referencia para el mismo objeto.",
                "En B, olvidar el desempate: con valores iguales, el orden de Atlas puede cambiar entre ejecuciones."),
        code('''#@title Checkpoint E2 · EJECUTA { display-mode: "form" }
_ = taller.checkpoint("E2")'''),
        ficha("E3",
              "Construir en Atlas una bandeja priorizada, reproducible y explicable.",
              "¿Qué procesos reviso primero?",
              "**MongoDB Atlas → Data Explorer → Aggregations**; Colab solo vuelve a ejecutar tu pipeline y guarda el CSV.",
              "la lectura del pipeline que pegues, su ejecución contra tu colección y la exportación a CSV.",
              ["En Aggregations, modo Texto, escribe el pipeline de cuatro etapas.", "Ejecútalo y guárdalo con el nombre pedido.",
               "Exporta el código y pégalo aquí.", "Toma la captura `E2_atlas.png` y súbela."],
              "`E3/03_pipeline_bandeja.json`, `E3/03_resultado_atlas.json`, `E3/03_bandeja_historica.csv` y `E2/E2_atlas.png`.",
              "10: pipeline (estructura y resultado en orden) 7 · CSV 3."),
        md(f'''### E3 · **SAL DE COLAB. AHORA TRABAJAS EN MONGODB ATLAS → Aggregations.**

| Etapa | Qué debe hacer en tu pipeline | Error frecuente |
|---|---|---|
| `$match` | quedarse con los procesos con `{C.CAMPO['precio_base']}` > 0 y `{C.CAMPO['cantidad']}` > 0 | filtrar después de ordenar |
| `$project` | producir exactamente `id_proceso`, `anio`, `departamento`, `entidad`, `valor_contratos` (desde `{C.CAMPO['anio']}`, `{C.CAMPO['departamento']}`, `entidad.nombre` y `{C.CAMPO['valor']}`) | dejar los nombres anidados |
| `$sort` | `valor_contratos` descendente y `id_proceso` ascendente | olvidar el desempate |
| `$limit` | máximo {C.BANDEJA_MAX} | no limitar: la bandeja deja de ser una cola de trabajo |

**Etapa usada: `$project` con un campo anidado**

| | |
|---|---|
| Para qué sirve | elegir qué campos salen de cada documento y con qué nombre |
| Ejemplo con otro campo | `{{ "$project": {{ "_id": 0, "id_proceso": 1, "ciudad": "$entidad.ciudad" }} }}` |
| Cómo se lee | `"_id": 0` quita el identificador interno; `"id_proceso": 1` deja el campo como está; `"ciudad": "$entidad.ciudad"` crea una columna `ciudad` con el **valor** del campo anidado: el `$` delante de la ruta significa «el valor de este campo» |
| Error frecuente | escribir `"ciudad": "entidad.ciudad"` sin `$`: cada fila tendría el texto «entidad.ciudad», no la ciudad |

**HAZ ESTO AHORA.**
1. En tu colección abre **Aggregations** y activa el modo **Texto** (ícono `</>`), como en S04.
2. Escribe el pipeline, pulsa **Run** y revisa que salgan como máximo {C.BANDEJA_MAX} filas.
3. **Save → Save as** con el nombre exacto de pipeline que imprimió la celda de identidad (por ejemplo `tc1-bandeja-p03`).
4. **Export Code → Python 3**, desmarca *Include driver syntax* si aparece, copia el código y pégalo en la celda siguiente. Si se copia también la línea de conexión (`client = MongoClient(...)`), no importa: la celda toma solo el pipeline y descarta la conexión.
5. **Captura `E2_atlas.png`.** Debe verse la interfaz de Atlas, el nombre del pipeline guardado y su resultado. En Windows: `Win + Shift + S`; la imagen queda en *Imágenes → Capturas de pantalla*. Si al subirla el botón no aparece o falla (pasa cuando el navegador bloquea las cookies de terceros), arrastra la imagen al panel 📁 de Colab, renómbrala `E2_atlas.png` y vuelve a ejecutar la celda; lo mismo sirve para las otras dos capturas.

**Así debe verse la bandeja** que imprime la celda: hasta {C.BANDEJA_MAX} filas, una por proceso, de mayor a menor valor (valores de ejemplo). La `posición` empieza en 1, como la que elegirás en E6.1, y `valor_millones` es el mismo valor en millones; el CSV guarda solo las cinco columnas pedidas:

| posición | id_proceso | anio | departamento | entidad | valor_contratos | valor_millones |
|---|---|---|---|---|---|---|
| 1 | CO1.REQ.… | 2025 | Antioquia | ENTIDAD EJEMPLO | 950000000 | 950 |
| 2 | CO1.REQ.… | 2025 | Bogotá D.C. | OTRA ENTIDAD | 870000000 | 870 |

**OJO.** Antes de capturar, comprueba que en la pantalla no aparezcan contraseñas, tokens, URI ni cadenas de conexión.'''),
        code('''# E3 · PEGA · el código que exportaste (Export Code → Python 3) o el pipeline del modo Texto
PIPELINE_E3 = \'\'\'pega aquí tu pipeline\'\'\'
BANDEJA = taller.pipeline_e3(PIPELINE_E3)
BANDEJA.head(10)'''),
        code('''#@title E3 · CAPTURA · Subir E2_atlas.png (Atlas: pipeline guardado + resultado) { display-mode: "form" }
ruta, (ok, motivo) = plataformas.guardar_captura(OUT, "E2")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = taller.checkpoint("E3")'''),
        lectura("Cada fila es un proceso que pasa los dos filtros, en orden de valor de contratos. El orden es reproducible porque el desempate es explícito.",
                "Es una **cola de revisión**: con un equipo que no alcanza a revisar todo, dice por dónde empezar.",
                "Que esos procesos tengan sobrecosto, fraude o irregularidad. Para eso falta un precio de referencia del mercado para el mismo objeto, y la bandeja no lo tiene.",
                "Leer la posición 1 como «el peor proceso». La bandeja prioriza; no califica."),
        ficha("E4",
              "Diseñar una tabla Cassandra desde su patrón de acceso y ejecutarla en el servicio real.",
              "Dado un año y un departamento, ¿cuáles son los 10 procesos con mayor `valor_contratos`?",
              "Colab para decidir y generar el script; **Astra DB → CQL Console** para crear, cargar y consultar.",
              "la generación del script CQL (DROP, CREATE, INSERT de tu bandeja y los dos SELECT) a partir de **tus** decisiones, y la lectura de la salida de la consola.",
              ["Elige partición, clustering y tipo de `valor_contratos`.", "En Astra pega el script por bloques.",
               "Copia la salida de los dos SELECT y pégala aquí.", "Si algo falla, lee la consecuencia, cambia tu decisión y repite.",
               "Toma la captura `E4_astra.png` y súbela."],
              "`E4/04_datos_cassandra.csv`, `E4/04_modelo_cassandra.cql`, `E4/04_cassandra_evidence.json` y `E4/E4_astra.png`.",
              "15: datos cargados (COUNT correcto) 5 · modelo query-first 6 · ejecución real (top 10 + captura) 4."),
        md('''### E4.1 · Primero la consulta, después la tabla

En Cassandra no se diseña la tabla y luego se pregunta: **la consulta define la tabla**. La pregunta de esta etapa es fija:

```sql
SELECT id_proceso, valor_contratos FROM ... WHERE anio = ? AND departamento = ? LIMIT 10;   -- de mayor a menor valor
```

| Concepto | Qué decide | Recuerda de S05 |
|---|---|---|
| partición | en qué partición vive cada fila; la consulta debe fijar sus columnas **con igualdad** | sin eso, Cassandra pide `ALLOW FILTERING`, que está prohibido |
| clustering | cómo se ordenan las filas **dentro** de la partición y qué hace única cada fila | dos filas con la misma PRIMARY KEY se sobrescriben |
| tipo | cómo se compara el valor al ordenar | un número guardado como texto se ordena alfabéticamente |

Tu bandeja tiene procesos de varios departamentos. Para probar la consulta, la celda elige la **partición de prueba**: la combinación (año, departamento) con más filas en tu bandeja. Te dice cuál es, cuántas filas tiene (ese es el COUNT que debes ver en Astra) y cuántas filas cargarás en total.

**HAZ ESTO AHORA.** Toma las tres decisiones. La celda te anuncia qué pasará en Astra antes de que lo ejecutes.'''),
        code(f'''#@title E4.1 · ELIGE · Diseña la tabla {{ display-mode: "form" }}
PARTICION = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + list(C.OPCIONES_PARTICION))}
CLUSTERING = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + list(C.OPCIONES_CLUSTERING))}
TIPO_VALOR = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.OPCIONES_TIPO_VALOR)}
KEYSPACE = "{C.KEYSPACE_DEFECTO}" #@param {{type:"string"}}
CQL = taller.cql_e4(PARTICION, CLUSTERING, TIPO_VALOR, KEYSPACE)
BLOQUES = taller.bloques_cql()'''),
        md('''### E4.2 · **SAL DE COLAB. AHORA TRABAJAS EN ASTRA → CQL Console.**

**HAZ ESTO AHORA.**
1. Abre tu base en Astra. Si dice *Hibernated*, pulsa **Resume** y espera a que diga *Active*.
2. Abre **CQL Console** y pega los bloques **en orden**: primero DROP + CREATE, luego los INSERT y al final los dos SELECT. Espera a que cada bloque termine.
3. Selecciona y copia la salida de los dos SELECT: desde `count` hasta `(10 rows)`. Pégala entre las comillas de la celda siguiente.
4. **Captura `E4_astra.png`**: debe verse CQL Console con el SELECT, la partición (año y departamento) y el resultado con algunos IDs. Sin tokens a la vista.

**Así debe verse lo que pegas** (formato de la consola; tus números e IDs serán otros):

```
 count
-------
    <tu conteo>

(1 rows)

 id_proceso      | valor_contratos
-----------------+-----------------
 CO1.REQ.…       |   <el mayor valor>
 …               |   …

(10 rows)
```

**Si Astra responde con error**, mira primero de dónde viene:

| Si el error dice… | Viene de | Qué haces |
|---|---|---|
| `InvalidRequest`, `ALLOW FILTERING`, `Cannot execute this query` | tu diseño | vuelve a E4.1, cambia la decisión, ejecuta de nuevo y pega otra vez los bloques: el DROP del primer bloque borra la tabla anterior |
| que la base está *Hibernated*, no hay conexión o la sesión venció | el servicio | pulsa *Resume*, espera a que diga *Active* y vuelve a pegar el bloque que falló |'''),
        code('''# E4.2 · PEGA · la salida de CQL Console (desde "count" hasta "(10 rows)")
SALIDA_ASTRA = \'\'\'pega aquí la salida de Astra\'\'\'
LEIDO = taller.astra_e4(SALIDA_ASTRA)'''),
        code('''#@title E4.3 · CAPTURA · Subir E4_astra.png (CQL Console: SELECT + resultado) { display-mode: "form" }
ruta, (ok, motivo) = plataformas.guardar_captura(OUT, "E4")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = taller.checkpoint("E4")'''),
        lectura("El COUNT dice cuántas filas quedaron en la partición; el top 10 sale ordenado sin `ORDER BY` porque el clustering ya ordena por valor dentro de la partición.",
                "Tu tabla responde la pregunta en una sola partición: la lectura no crece con el resto de la tabla.",
                "Que sea el top 10 del departamento en todo el año: la tabla solo tiene las filas de tu bandeja (hasta 100 procesos con contrato cruzado de tu snapshot); para eso faltan todos los procesos del departamento. Tampoco sirve para otra pregunta: «los 10 de una entidad» necesitaría otra tabla, porque en Cassandra se duplica para responder.",
                "Diseñar la clave mirando qué columnas «parecen importantes» en lugar de mirar el `WHERE` de la consulta."),
        ficha("E5",
              "Responder una pregunta de conectividad contractual con un grafo real.",
              "¿Qué proveedores conectan a la entidad ancla con otras entidades dentro del snapshot?",
              "Colab para cargar el grafo; **Neo4j Aura → Query** para consultarlo.",
              "la carga con `UNWIND $filas` + `MERGE` (el patrón de S06), la consulta que encuentra la ancla y la consulta de contexto.",
              ["Conecta Aura y carga el grafo.", "En Aura ejecuta la consulta de la ancla.",
               "Completa el hueco de compartidos y escribe completa la consulta de ranking.", "Ejecuta ambas en Aura.",
               "Captura `E5_neo4j.png` y sube la evidencia."],
              "`E5/05_relaciones_grafo.csv`, `E5/05_neo4j_consultas.cypher`, `E5/05_resultado_relacional.csv`, `E5/05_neo4j_evidence.json` y `E5/E5_neo4j.png`.",
              "15: grafo y ancla 4 · métrica relacional 4 · Cypher 5 · ejecución real + captura 2."),
        md('''### E5.1 · El grafo y la regla de la ancla

El modelo es el de S06, con el contrato como nodo. El grafo usa **todos** tus contratos descargados, no solo los que cruzaron con un proceso: cada contrato ya trae su entidad y su proveedor.

```
(:Entidad {nit})-[:FIRMA]->(:Contrato {id})-[:ADJUDICADO_A]->(:Proveedor {nit})
```

Un **proveedor compartido** es un proveedor que tiene contratos con dos o más entidades. La **entidad ancla** es la entidad con más proveedores compartidos (desempate: más contratos, luego el NIT). La regla se eligió por los datos: con la regla anterior, «la entidad con más contratos», la ancla no compartía ningún proveedor en ninguna de las seis ventanas que se probaron; con esta regla, las ''' + str(len(C.VENTANAS)) + ''' ventanas posibles tienen una red con respuesta.

**OJO.** La contraseña de Aura se pide oculta. La carga solo borra contratos de cargas anteriores del TC1; no toca lo que hiciste en S06.'''),
        code('''#@title E5.1 · EJECUTA · Conectar Aura y cargar el grafo { display-mode: "form" }
AURA = taller.conectar_aura_e5()
CONTEOS = taller.cargar_e5()'''),
        lectura("Tres conteos de nodos en tu instancia (entidades, contratos, proveedores) y si la segunda carga dejó lo mismo que la primera.",
                "El grafo tiene tus contratos con empresas, y `MERGE` no duplica: puedes volver a ejecutar la celda sin inflar los conteos.",
                "Cuántas entidades contratan en todo SECOP: el grafo solo tiene los contratos de tu snapshot, sin personas naturales ni consorcios.",
                "Leer «proveedores» como «empresas distintas del país»: son los proveedores que aparecen en tus contratos descargados."),
        md('''### E5.2 · **SAL DE COLAB. AHORA TRABAJAS EN NEO4J AURA → Query.**

**HAZ ESTO AHORA.**
1. Ejecuta `RETURN 1 AS conexion` para comprobar que Query responde.
2. Ejecuta la consulta de la ancla que imprime la celda siguiente y mira la pestaña **Table**.
3. Vuelve: la celda lee el mismo resultado desde tu instancia y fija tu ancla.'''),
        code('''#@title E5.2 · EJECUTA · La consulta de la ancla (cópiala en Aura) y tu ancla { display-mode: "form" }
print(secop.CYPHER_ANCLA, "\\n")
NIT_ANCLA = taller.ancla_e5()'''),
        lectura("Las primeras líneas son las entidades con más proveedores compartidos; la primera es tu ancla. La línea «Tu entidad ancla» dice cuántos nombres distintos aparecen bajo su NIT.",
                "Desde qué entidad vas a mirar la red en E5.3.",
                "Que la ancla tenga una red inusual: se eligió **por** tener más proveedores compartidos, el mismo rasgo que mide el ranking, así que «tiene muchos» es la regla de selección, no un hallazgo. Además, un NIT puede agrupar muchas sedes (el número de nombres que imprime la celda); falta saber qué sede firmó cada contrato.",
                "Leer el nombre impreso como una sola oficina: el nodo `Entidad` reúne todo lo firmado con ese NIT."),
        md('''### E5.3 · Dos consultas: una con un hueco, otra escrita por ti

| Cypher | Para qué | Ejemplo en tu grafo |
|---|---|---|
| `MATCH` | describe con flechas el camino que buscas | `(e:Entidad)-[:FIRMA]->(c:Contrato)`: una entidad que firma un contrato |
| `WHERE` | descarta caminos que no sirven | `WHERE c.valor > 0`: solo contratos con valor |
| `WITH` | cierra un tramo de la consulta y pasa sus resultados (y sus conteos) al tramo siguiente | `WITH e, count(DISTINCT c) AS firmados`: por cada entidad, cuántos contratos firmó |
| `count(DISTINCT x)` | cuenta nodos distintos, no caminos | ver el ejemplo de abajo |
| `ORDER BY … DESC, … ASC` | ordena; cada columna siguiente desempata a la anterior | igual que el Sort de Atlas y el clustering de Cassandra |

**Ejemplo para entender `DISTINCT`.** Un proveedor firma tres contratos con la misma alcaldía: el lunes, el miércoles y el viernes. ¿Con cuántas entidades contrata? Con una, aunque haya tres contratos. Tu consulta llega a esa alcaldía por tres caminos, uno por contrato: `count(otra)` cuenta caminos (3); `count(DISTINCT otra)` cuenta entidades (1).

**E5.3a · Compartidos — COMPLETA.** Completa el `____` del `WHERE`: la «otra» entidad no puede ser la ancla. Devuelve una fila por proveedor con `nit_proveedor`, `proveedor` y la lista `otras_entidades`. En Aura mira la pestaña **Graph**.

**E5.3b · Ranking de proveedores puente — ESCRIBE.** Escribe tú la consulta completa. Por cada proveedor de la ancla que también contrata con otras entidades debe devolver estas columnas, con estos nombres:

| Columna | Qué es |
|---|---|
| `nit_proveedor` | el NIT del proveedor |
| `proveedor` | su nombre |
| `contratos_con_ancla` | cuántos contratos **distintos** tiene con la ancla |
| `entidades_conectadas` | con cuántas entidades **distintas**, aparte de la ancla, tiene contratos |

Ordenadas por `entidades_conectadas` de mayor a menor, luego `contratos_con_ancla` de mayor a menor y luego `nit_proveedor` ascendente. Usa el parámetro `$nit_ancla` para la entidad ancla. Al ejecutarla, la celda imprime la versión para Aura (con tu NIT), la corre en tu instancia y te dice si coincide con la referencia calculada desde tu RAW; si no coincide, te dice qué revisar y desde qué fila se aparta.

**Error más probable:** contar caminos con `count(otra)`: los números salen inflados.

<details><summary>Si te atascas en E5.3a</summary><code>WHERE otra <> a</code></details>

<details><summary>Pistas para E5.3b, de menos a más (ábrelas una por una)</summary>

1. La consulta de E5.3a ya recorre el camino completo: ancla → contrato → proveedor → contrato → otra entidad. El ranking usa ese mismo camino, partido en dos tramos.
2. Primer tramo: de la ancla a sus proveedores. Antes de seguir, cuenta por proveedor los contratos distintos con la ancla y pásalos con `WITH`.
3. Segundo tramo: de cada proveedor a las otras entidades que le compran; descarta la ancla con `WHERE`.
4. En el `RETURN`, cuenta las otras entidades sin repetir, nombra las cuatro columnas con `AS` y termina con el `ORDER BY` de tres claves.
</details>'''),
        code('''# E5.3a · COMPLETA · Proveedores compartidos (un hueco en el WHERE)
CYPHER_COMPARTIDOS = \'\'\'
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE ____
RETURN p.nit AS nit_proveedor, p.nombre AS proveedor, collect(DISTINCT otra.nombre) AS otras_entidades
\'\'\'
taller.preparar_consulta_e5("compartidos", CYPHER_COMPARTIDOS)'''),
        code('''# E5.3b · ESCRIBE · Ranking de proveedores puente (la consulta completa es tuya)
CYPHER_RANKING = \'\'\'
escribe aquí tu consulta
\'\'\'
taller.preparar_consulta_e5("ranking", CYPHER_RANKING)'''),
        md('''**HAZ ESTO AHORA.** Con las dos consultas ya ejecutadas en Aura, toma **`E5_neo4j.png`**: debe verse Aura Query con la consulta de ranking y su resultado (o la vista Graph de compartidos, si aporta más). Sin contraseñas a la vista. Después ejecuta la celda siguiente.'''),
        code('''#@title E5.4 · CAPTURA · Tus resultados de Aura y E5_neo4j.png { display-mode: "form" }
RANKING = taller.capturar_e5()
ruta, (ok, motivo) = plataformas.guardar_captura(OUT, "E5")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = taller.checkpoint("E5")'''),
        lectura("Cada fila del ranking es un proveedor de la ancla que también contrata con otras entidades: cuántos contratos tiene con la ancla y con cuántas entidades distintas más.",
                "Qué proveedores hacen de **puente** entre tu entidad ancla y el resto de tu snapshot: el contexto que una tabla de contratos no muestra de un vistazo.",
                "Colusión, favorecimiento ni fraude. Además, un NIT puede agrupar varias sedes (SENA, ICBF): su número de conexiones puede reflejar tamaño administrativo, no comportamiento. Y solo ves contratos con empresas durante pocos días.",
                "Leer «conecta muchas entidades» como «es sospechoso». Un proveedor de seguros o de vigilancia contrata con muchas entidades por la naturaleza de su servicio."),
        ficha("E6",
              "Tomar tres decisiones de ingeniería y dos de interpretación ancladas a **tus** resultados, y entregar.",
              "¿Qué decidí, con qué evidencia y con qué límite?",
              "Google Colab.",
              "el informe técnico (se genera desde tus artefactos), el validador y el empaquetado.",
              ["Responde las decisiones mirando tus salidas.", "Responde la microdefensa.",
               "Mira tu carpeta y ejecuta el validador final.", "Genera los tres archivos y entrégalos por Drive + correo."],
              "`E6/06_decision_log.json`, `E6/06_informe_tecnico.md`, `E6/06_microdefensa_grupal.json`, `manifest_tc1.json` y `TC1_<PAREJA_ID>.zip`.",
              "10: decisiones e informe 5 · microdefensa 3 · paquete completo y sin secretos 2."),
        md('''### E6.1 · Decisiones con tu evidencia

Aquí **no se escribe**: se elige. Cada respuesta se compara con **tus** datos y tu snapshot: aunque otra pareja coincidiera contigo en la ventana, sus índices, su bandeja y sus tiempos son los suyos.

- **Concurrencia y 429.** Mira en E1.3 cuántos segundos tardó tu descarga concurrente.
- **Índice.** Elige el índice adicional que **creaste** en Atlas y la consulta que atiende.
- **Límite de la bandeja.** Elige una posición de **tu** bandeja (E3), escribe su `valor_contratos` en millones y elige qué dato falta para hablar de sobrecosto.'''),
        code(f'''#@title E6.1 · ELIGE · Tres decisiones ancladas a tus resultados {{ display-mode: "form" }}
DECISION_429 = "{C.SIN_SELECCION}" #@param {opciones(C.E6_DECISION_429)}
SEGUNDOS_DESCARGA_CONCURRENTE = 0 #@param {{type:"integer"}}
INDICE_ADICIONAL = "{C.SIN_SELECCION}" #@param {opciones(C.E6_INDICE)}
POSICION_EN_TU_BANDEJA = 1 #@param {{type:"slider", min:1, max:10, step:1}}
VALOR_EN_MILLONES = 0 #@param {{type:"integer"}}
DATO_QUE_FALTA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_DATO_FALTANTE)}
_ = taller.decisiones_e6(DECISION_429, SEGUNDOS_DESCARGA_CONCURRENTE, INDICE_ADICIONAL, POSICION_EN_TU_BANDEJA,
                         VALOR_EN_MILLONES, DATO_QUE_FALTA)'''),
        md('''### E6.2 · Microdefensa: dos límites con tus resultados

La *microdefensa* es la defensa corta de tus resultados: no se escribe, se elige en tres listas y se completa con un número que ya imprimiste.

- **Cobertura.** El porcentaje que imprimió E1.4 (la línea `cobertura … %`). Elige su rango y qué lo explica.
- **Red.** El límite: qué **no** permite concluir tu red de E5.
- **Proveedor puente.** El **primero** de tu ranking en E5.4: escribe su número de `entidades_conectadas`.'''),
        code(f'''#@title E6.2 · ELIGE · Microdefensa {{ display-mode: "form" }}
RANGO_DE_TU_COBERTURA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_RANGOS_COBERTURA)}
QUE_EXPLICA_TU_COBERTURA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_CAUSA_COBERTURA)}
QUE_NO_PERMITE_CONCLUIR_LA_RED = "{C.SIN_SELECCION}" #@param {opciones(C.E6_LIMITE_RED)}
ENTIDADES_DE_TU_PROVEEDOR_PUENTE = 0 #@param {{type:"integer"}}
taller.microdefensa_e6(RANGO_DE_TU_COBERTURA, QUE_EXPLICA_TU_COBERTURA, QUE_NO_PERMITE_CONCLUIR_LA_RED,
                       ENTIDADES_DE_TU_PROVEEDOR_PUENTE)'''),
        md('''### E6.3 · Validación final

La celda muestra primero tu carpeta de trabajo, archivo por archivo (✓ existe, ✗ falta): es exactamente lo que irá en el ZIP. Después el validador recalcula todo desde esos archivos, igual que lo hará el docente sobre tu ZIP: no confía en ninguna variable de memoria. Imprime tu puntaje por etapa y, por cada control en ✗, **qué revisar** y **qué encontró**. Si detecta un posible secreto, bloquea la entrega y dice dónde está.

Los controles con captura salen como **provisionales** hasta que el docente vea tus tres imágenes.'''),
        code('''#@title E6.3 · EJECUTA · Mira tu carpeta y valida todo { display-mode: "form" }
taller.ver_carpeta()
print()
MANIFEST = taller.validar()'''),
        code('''#@title Entregar · EJECUTA · genera los tres archivos (en Drive si activaste el avance) { display-mode: "form" }
CARPETA_ENTREGA, HUELLA = taller.entregar(MANIFEST)'''),
        md(f'''## Entrega: Google Drive restringido + correo institucional

**Así debe quedar la carpeta que compartes:**

```
TC1_BIGDATA_<PAREJA_ID>_<APELLIDO1>_<APELLIDO2>/
├── TC1_<PAREJA_ID>.ipynb     ← este cuaderno, con sus salidas
├── TC1_<PAREJA_ID>.zip       ← tu carpeta de trabajo completa (E1/ … E6/)
└── manifest_tc1.json         ← tu puntaje control por control, calculado por el validador
```

Si trabajas solo, la carpeta lleva solo tu apellido: `TC1_BIGDATA_<PAREJA_ID>_<APELLIDO1>/`. La celda «Entregar» imprime el nombre exacto.

<details><summary>Qué hay dentro del ZIP</summary>

```
{arbol_zip()}
```

`manifest_tc1.json` guarda: pareja e integrantes, puntaje y nota, puntos por etapa, cada control con su evidencia, el control de secretos y la fecha en que se generó.
</details>

1. Abre la carpeta que imprimió la celda anterior en tu Drive. Debe contener **solo** los tres archivos. Si no activaste Drive, descarga los tres archivos y súbelos a una carpeta nueva con el nombre impreso. La carpeta `TC1_BIGDATA_<PAREJA_ID>/avance` es tu copia de trabajo: **no la compartas**.
2. Clic derecho sobre la **carpeta de entrega** → **Compartir** → deja **Acceso general: Restringido** → agrega `{C.CORREO_DOCENTE}` como **Lector**.
3. Un integrante envía el correo a `{C.CORREO_DOCENTE}`, con copia al compañero si trabajan en pareja:
   - **Asunto:** cópialo tal cual de la línea `ASUNTO DEL CORREO` que imprimió la celda «Entregar». Tiene la forma `[BIG DATA 2026-2S][TC1] <PAREJA_ID> - <APELLIDO1> - <APELLIDO2>`, con el nombre de tu pareja como queda en los archivos (si trabajas solo, termina en tu apellido).
   - **Cuerpo:** pareja, nombres y códigos, enlace de la carpeta y la **huella SHA-256** que imprimió la celda anterior (una sola huella).
4. Si corriges algo antes del cierre, vuelve a validar y entregar, reemplaza los archivos en la misma carpeta y responde en el mismo hilo con `CORRECCIÓN DE ENTREGA` y la huella nueva.

**Por qué la huella.** Es la SHA-256 de `manifest_tc1.json` (E1.2c). El sello de tiempo del correo fija **tu manifest** —tus puntajes, control por control— y **cuándo** lo enviaste: si el manifest de la carpeta cambiara después en un solo carácter, su huella ya no coincidiría con la del correo. Por eso, si vuelves a validar, envías la huella nueva.

**Fecha máxima: {C.FECHA_LIMITE}.** Cuenta el sello de tiempo del correo.

**GitHub es opcional:** solo por el navegador (*Add file → Upload files*), en un repositorio **privado** y sin códigos de estudiante en el README. No reemplaza Drive + correo.'''),
        md(f'''## Cierre

**La historia, en cinco frases.** Descargaste un snapshot de SECOP de dos maneras y demostraste que es el mismo. Lo convertiste en documentos, un proceso por documento, y lo cargaste en Atlas sin duplicar. En Atlas construiste una bandeja que dice por dónde empezar a revisar. Serviste esa bandeja en Cassandra con una tabla diseñada desde su consulta. Y en Neo4j viste qué proveedores conectan a una entidad con otras.

### ¿Qué resolvimos para Laura, y qué no?

| Laura preguntó | Qué tiene ahora | Qué todavía no sabe, y qué dato falta |
|---|---|---|
| ¿Puedo confiar en el snapshot? | un RAW firmado que cualquiera recalcula | si representa la ventana completa: cubre pocos días; falta descargar toda la ventana |
| ¿Qué reviso primero? | una bandeja de hasta {C.BANDEJA_MAX} procesos por valor de contratos | si hay sobrecosto: falta un precio de referencia del mercado para el mismo objeto |
| ¿Cuáles son los 10 de mayor valor en un año y departamento? | una tabla Cassandra que responde leyendo una sola partición | otras preguntas, como «por entidad», que necesitarían otra tabla |
| ¿Qué proveedores conectan entidades? | un ranking de proveedores puente | si hay colusión: faltan las sedes detrás de cada NIT y los contratos con personas naturales |

**La idea más importante.** El mismo dato necesita modelos distintos según la pregunta: documento para leer un proceso completo, tabla query-first para servir una consulta conocida, grafo para recorrer relaciones. Ninguno reemplaza a los otros.

**Errores comunes.** Comparar solo conteos en vez de hashes · cruzar por `id_del_proceso` · un documento por fila · `insert_many` repetido · olvidar el desempate · diseñar la tabla Cassandra sin mirar el `WHERE` · contar filas en vez de entidades distintas · leer prioridad o conexión como prueba de irregularidad.

**MÁS ADELANTE.** S09 cambia la pregunta: ¿qué pasa cuando las palabras de la consulta no coinciden con las del documento? Ahí aparecen los embeddings y la búsqueda vectorial.

### Hoja de trucos

| Necesitas | Herramienta |
|---|---|
| cruzar procesos con contratos | `id_del_portafolio` (procesos) = `proceso_de_compra` (contratos) |
| descargar en paralelo sin cambiar el resultado | `ThreadPoolExecutor` + `as_completed`, guardando por `offset` |
| saber si dos descargas son iguales | comparar su huella SHA-256, no su número de filas |
| filtrar en Atlas (Documents → Filter) | operadores de comparación de S03: `$gt` (>), `$gte` (≥), `$lt` (<), `$lte` (≤), `$eq` (=); un campo anidado se escribe con punto |
| ordenar en Atlas (Documents → Options) | en Sort, `1` es ascendente y `-1` descendente; con varias claves, cada una desempata a la anterior · Limit |
| bandeja en Atlas | `$match` → `$project` → `$sort` → `$limit` |
| tabla query-first | `PRIMARY KEY ((columnas del WHERE), columna de orden, id)` + `CLUSTERING ORDER BY` |
| grafo | `UNWIND $filas AS fila MERGE ...`; contar con `count(DISTINCT ...)` |
| ver tu carpeta o validar una etapa en cualquier momento | `taller.ver_carpeta()` · `taller.checkpoint("E2")` (o la etapa que quieras) |

### Variables del taller

**Si Colab se reinicia** (se pierden las variables) **o se desconecta** (también se pierden los archivos de Colab, salvo el avance que guardaste en Drive):

| Ibas en | Vuelve a ejecutar |
|---|---|
| cualquier etapa | «Preparar el entorno» y «0 · Identidad» (con Drive activado, si Colab se desconectó, esta celda restaura tu carpeta tal como quedó en tu último checkpoint) |
| E2 o E3 | además, E2.2a (conectar Atlas) |
| E4 | además, E4.1 con tus mismas decisiones: arma otra vez los bloques y conserva la salida de Astra que ya pegaste |
| E5 | además, E5.1 (conectar y cargar; no duplica) y las celdas E5.3a y E5.3b: tu ancla se recupera sola de tus archivos |

Sin avance en Drive, si Colab se desconecta, se repite desde E1.

| Variable | Qué contiene | Nace en |
|---|---|---|
| `OUT` | la ruta de tu carpeta de trabajo | 0 · Identidad |
| `PLAN` | las dos consultas oficiales de tu pareja (procesos y contratos) | E1.0 |
| `OFFSETS` | la posición de cada página: 0, 250, 500… | E1.2a |
| `paginas_seq` · `paginas_thr` | cada descarga como `{{offset: (filas, metadatos)}}` | E1.2b · E1.3 |
| `SEG_SEQ` · `SEG_THR` | segundos de cada descarga | E1.2b · E1.3 |
| `BENCH` · `CRUCE` | la comparación de E1.3 y el resumen del cruce | E1.3 · E1.4 |
| `procesos` · `contratos` | tu RAW leído desde Parquet | E1.5 |
| `DOCUMENTOS` | la lista de documentos, uno por proceso | E2.1 |
| `FILTRO_A` · `ORDEN_B` · `PIPELINE_E3` | lo que pegaste desde Atlas | E2.4 · E2.5 · E3 |
| `BANDEJA` | la bandeja que devolvió tu pipeline | E3 |
| `CQL` · `BLOQUES` | tu script Cassandra y sus bloques para pegar | E4.1 |
| `SALIDA_ASTRA` · `LEIDO` | lo que pegaste desde CQL Console y lo que se leyó de ahí | E4.2 |
| `NIT_ANCLA` · `RANKING` | tu entidad ancla y tus proveedores puente | E5.2 · E5.4 |
| `MANIFEST` · `HUELLA` | el resultado de la validación y su huella de entrega | E6.3 · Entregar |'''),
    ]


def notebook():
    celdas = cells()
    validate(celdas)
    ocultas = (lambda c: c["cell_type"] == "code" and "{ display-mode: \"form\" }" in "".join(c["source"])
               or (c["cell_type"] == "code" and "".join(c["source"]).startswith("#@title Preparar el entorno")))
    for i, c in enumerate(celdas):
        c["id"] = f"tc1-v9-{i:02d}"
        if ocultas(c):
            c["metadata"] = {"cellView": "form", "jupyter": {"source_hidden": True}}
    nb = build(celdas, python_version="3.11")
    nb["metadata"]["colab"] = {"name": "Taller_Control_1.ipynb", "provenance": [], "toc_visible": True,
                               "include_colab_link": True}
    return nb


def serializar(nb):
    return json.dumps(nb, ensure_ascii=False, indent=1) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    texto = serializar(notebook())
    if a.check:
        actual = DESTINO.read_bytes().decode("utf-8") if DESTINO.exists() else ""
        if actual != texto:
            print("FALLA: Cuadernos/Taller_Control_1.ipynb no coincide con el generador. Ejecuta el generador.")
            sys.exit(1)
        print("OK: el cuaderno versionado es exactamente el que produce el generador.")
        return
    DESTINO.write_bytes(texto.encode("utf-8"))
    print(f"[OK] {DESTINO.relative_to(ROOT)} · {len(json.loads(texto)['cells'])} celdas")


if __name__ == "__main__":
    main()
