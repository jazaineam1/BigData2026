#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Generador del cuaderno TC1 (S08) · V9.

Fuente única: utils/tc1_contrato.py (rúbrica, ventanas, checkpoints, opciones de las listas)
y los módulos utils/tc1_*.py, que se incrustan en una celda oculta con su SHA-256.

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


def opciones(lista):
    return "[" + ", ".join(json.dumps(x, ensure_ascii=False) for x in lista) + "]"


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


def celda_infraestructura():
    lineas = ["#@title Preparar el entorno · instala dos librerías y carga la infraestructura provista (no se evalúa)",
              "# Código legible y versionado: " + REPO + "tc1_contrato.py (y los demás utils/tc1_*.py).",
              "# Aquí va comprimido para que un solo Ctrl+Enter deje todo listo; el SHA-256 garantiza que es la versión oficial.",
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
    lineas += [
        "}",
        "for nombre, (sha, blob) in MODULOS.items():",
        "    fuente = zlib.decompress(base64.b64decode(blob))",
        "    assert hashlib.sha256(fuente).hexdigest() == sha, f'{nombre} no coincide con la versión oficial'",
        "    Path(nombre).write_bytes(fuente)",
        "import time, json",
        "from concurrent.futures import ThreadPoolExecutor, as_completed",
        "import pandas as pd",
        "import tc1_contrato as C, tc1_secop as S, tc1_servicios as X, tc1_validador as V, tc1_cuaderno as T",
        "for modulo in (C, S, X, V, T):",
        "    importlib.reload(modulo)",
        "print(f'TC1 {C.VERSION_VISIBLE} listo. Siguiente paso: la celda «0 · Identidad de la pareja».')",
    ]
    return code("\n".join(lineas))


def cells():
    ventanas = "\n".join(f"| {p} | {i[:10]} | {f[:10]} |" for p, (i, f) in C.VENTANAS.items())
    rubrica = "\n".join(f"| {cod} | {desc} | {pts} | {'automático' if t == 'auto' else 'automático + captura'} |"
                        for cod, _, pts, desc, t in C.RUBRICA)
    lista_parejas = opciones([C.SIN_SELECCION] + C.PAREJAS)
    return [
        md(f'<a href="{C.COLAB_URL}" target="_parent"><img src="https://colab.research.google.com/assets/colab-badge.svg" '
           'alt="Abrir el TC1 en Google Colab"/></a>'),
        md(f'''# TC1 · Un snapshot de SECOP, tres preguntas, tres modelos

**VERSIÓN {C.VERSION_VISIBLE}** · Taller de Control 1 · Big Data · Maestría en Analítica de Datos · Universidad Central

## OBJETIVO DEL TC1

Construir, en parejas, un pipeline reproducible sobre SECOP II y demostrar que **un mismo snapshot** se reutiliza en distintos modelos de datos según la pregunta que hay que responder.

Al terminar habrás demostrado:

1. **adquisición reproducible**: la descarga secuencial y la concurrente producen el mismo snapshot;
2. **modelo documental**: un proceso es un documento en MongoDB Atlas, cargado sin duplicar;
3. **producto analítico**: una bandeja priorizada construida en Atlas;
4. **patrón query-first**: una tabla Cassandra diseñada desde su consulta y ejecutada en Astra;
5. **contexto relacional**: los proveedores que conectan entidades, consultados en Neo4j Aura;
6. **evidencia reproducible**: el docente puede recalcular tu resultado sin confiar en tu palabra.

| Pregunta | Respuesta |
|---|---|
| ¿Qué voy a hacer? | Un pipeline sobre SECOP II: de la API a tres bases de datos, con evidencia verificable. |
| ¿Qué voy a entregar? | Tres archivos: `TC1_<PAREJA_ID>.ipynb`, `TC1_<PAREJA_ID>.zip` y `manifest_tc1.json`. |
| ¿Cuántas etapas? | Seis: E1 → E2 → E3 → E4 → E5 → E6. |
| ¿Dónde trabajo? | E1 Colab · E2 Colab + **Atlas** · E3 **Atlas** + Colab · E4 Colab + **Astra** · E5 Colab + **Aura** · E6 Colab |
| ¿Cómo sé si puedo avanzar? | Cada etapa termina en un **checkpoint** que imprime ✓ o ✗ y dice qué falta. |
| ¿Cómo me califican? | Resultados que se recalculan desde tus datos + artefactos + tres capturas de los servicios. |

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
| MongoDB Atlas (M0) | E2, E3 | clúster activo, usuario de base de datos, Network Access con tu IP o 0.0.0.0/0 | [tutorial de conexión de S04](https://jazaineam1.github.io/BigData2026/assets/tutoriales/atlas-guia-conexion.html) |
| Astra DB (Serverless non-vector) | E4 | la base está **Active** y tiene el keyspace `compras_claras` | Astra pone en *Hibernated* las bases gratuitas tras 48 h sin uso y **las borra a los 30 días**: pulsa *Resume* o crea una nueva ([tutorial S05](https://jazaineam1.github.io/BigData2026/assets/tutoriales/astra-cassandra-paso-a-paso-v3.html)) |
| Neo4j Aura Free | E5 | la instancia está **Running** y tienes su contraseña | Aura pausa la instancia tras 72 h sin uso y **la borra si sigue pausada 30 días**: reanúdala o crea otra ([tutorial S06](https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-aura-s06-paso-a-paso.html)) |

**OJO.** Si una plataforma falla de verdad (caída del servicio o cuenta bloqueada), escríbelo en el correo con una captura del error y el docente decide la excepción. Lo que no depende del servicio se califica igual: por ejemplo, el diseño de tu `.cql` (E4.2) y tu archivo Cypher (E5.3).

### Qué está provisto y qué haces tú

| Provisto: no se califica reescribirlo | Tú decides o escribes: se califica |
|---|---|
| cliente HTTP con reintentos, caché firmado por páginas, hash canónico | la descarga secuencial y la concurrente con `ThreadPoolExecutor` (un hueco) |
| carga técnica a Atlas y a Aura (Atlas no importa archivos desde el navegador; S04 cargó igual) | el grano documental, la estrategia de carga, los índices, el filtro A, el orden B y el pipeline E3, **en Atlas** |
| el script CQL que se genera desde tus decisiones | la partición, el clustering y el tipo de la tabla; ejecutarla **en Astra** |
| el validador y el empaquetado | dos consultas Cypher (un hueco cada una) ejecutadas **en Aura**; las decisiones de E6 |

**Regla de avance.** No avances porque existe una celda siguiente: avanza cuando el checkpoint de la etapa esté en ✓.'''),
        celda_infraestructura(),
        md(f'''## 0 · Identidad de la pareja

Tu `PAREJA_ID` lo asignó el docente y fija tu **ventana** de SECOP: dos parejas nunca comparten datos y la ventana no depende de cómo escribas el identificador.

<details><summary>Tabla de ventanas</summary>

| Pareja | Inicio | Fin |
|---|---|---|
{ventanas}
</details>

Escribe el nombre, el código y el **primer apellido** de cada integrante: los apellidos forman el nombre de la carpeta de entrega. Si trabajas solo, deja vacío el integrante 2. Los nombres y códigos solo viajan en tu entrega privada al docente; no los publiques. Guardar el avance en Drive deja una copia de tu carpeta de trabajo tras cada checkpoint: si Colab se reinicia, al volver a ejecutar esta celda recuperas lo hecho.'''),
        code(f'''#@title 0 · Identidad de la pareja {{ display-mode: "form" }}
PAREJA_ID = "{C.SIN_SELECCION}" #@param {lista_parejas}
INTEGRANTE_1 = "" #@param {{type:"string"}}
CODIGO_1 = "" #@param {{type:"string"}}
APELLIDO_1 = "" #@param {{type:"string"}}
INTEGRANTE_2 = "" #@param {{type:"string"}}
CODIGO_2 = "" #@param {{type:"string"}}
APELLIDO_2 = "" #@param {{type:"string"}}
GUARDAR_AVANCE_EN_DRIVE = "Sí (recomendado)" #@param ["Sí (recomendado)", "No"]

OUT, DRIVE = T.iniciar(PAREJA_ID, [(INTEGRANTE_1, CODIGO_1, APELLIDO_1), (INTEGRANTE_2, CODIGO_2, APELLIDO_2)],
                       GUARDAR_AVANCE_EN_DRIVE)'''),
        ficha("E1",
              "Demostrar que una descarga secuencial y una concurrente producen exactamente el mismo snapshot.",
              "¿Puedo usar concurrencia sin alterar la población descargada?",
              "Google Colab.",
              "cliente HTTP con reintentos y backoff; caché por páginas con firma de la consulta y SHA-256; escritura atómica (un `.part` nunca cuenta como página); conteos; hash canónico.",
              ["Ejecuta el contrato de datos y la prueba de 50 filas.", "Ejecuta el preflight y la descarga secuencial.",
               "Completa el hueco de la descarga concurrente y ejecútala.", "Compara offsets, filas y hash.",
               "Descarga los contratos con tu misma función concurrente.", "Consolida el RAW y corre el checkpoint."],
              "`E1/00_dataset_contract.json`, `E1/01_acquisition_manifest.json`, `E1/01_benchmark_threads.json`, `E1/01_quality_report.json` y `E1/raw/` (páginas firmadas + parquet).",
              "25: contrato 4 · secuencial 4 · concurrencia equivalente 8 · trazabilidad 9. **No se exige speedup**: una ejecución concurrente más lenta también puede ser correcta."),
        md('''### E1.0 · Tu contrato de datos

La consulta no se escribe a mano: sale del contrato de tu pareja. Se filtra y se proyecta en la API (*query pushdown*) para no transferir datos que no se usarán.

**Una decisión que ya está tomada, y por qué.** El snapshot de contratos guarda solo contratos con **personas jurídicas que no son consorcio** (`tipodocproveedor = 'NIT' AND es_grupo = 'No'`). La gran mayoría de contratos de SECOP son con personas naturales (en enero y febrero de 2025, el 94 %), que suelen firmar con una sola entidad y no forman red; los consorcios se crean para un solo proceso. Sin este filtro, la pregunta de E5 quedaba vacía, o con dos o tres proveedores, en las ventanas que se probaron. Con él, las 12 ventanas del curso tienen respuesta (`Datos/tc1_ventanas_resumen.json`).'''),
        code('''#@title E1.0 · Contrato de datos de tu pareja { display-mode: "form" }
PLAN = T.contrato_e1()'''),
        code('''# E1.1 · Prueba pequeña antes de descargar: 50 filas reales
q = PLAN["procesos"]
muestra, meta = S.fetch_page(q["endpoint"], select=q["select"], where=q["where"], order=q["order"], limit=50, offset=0)
print(f"{len(muestra)} filas en {meta['elapsed_s']} s (intento {meta['attempts']})")
pd.DataFrame(muestra)[["id_del_proceso", "entidad", "fecha_de_publicacion_del", "precio_base"]].head(5)'''),
        lectura("Cada fila es un registro de la API de procesos. `id_del_proceso` identifica el proceso; la misma clave puede repetirse si SECOP trae varias filas para un proceso.",
                "La consulta, los filtros y el orden funcionan antes de lanzar miles de peticiones.",
                "Cuántos registros existen en tu ventana ni cuántas páginas hay que pedir: eso lo dice el preflight.",
                "Lanzar la descarga completa sin probar la consulta. Un nombre de columna mal escrito no se corrige reintentando."),
        code('''#@title E1.2a · Preflight: cuántos registros hay y qué páginas pedir { display-mode: "form" }
pagina_secuencial, pagina_concurrente, OFFSETS, N_PROCESOS = T.preflight_e1()'''),
        code('''# E1.2b · Descarga secuencial: una página después de otra
def descargar_secuencial(descargar_pagina, offsets):
    paginas = {}
    for offset in offsets:
        paginas[offset] = descargar_pagina(offset)      # cada llamada devuelve (filas, metadatos)
    return paginas

inicio = time.perf_counter()
paginas_seq = descargar_secuencial(pagina_secuencial, OFFSETS)
SEG_SEQ = time.perf_counter() - inicio
print(f"Secuencial: {sum(len(f) for f, _ in paginas_seq.values()):,} filas en {SEG_SEQ:.1f} s · {len(paginas_seq)} páginas")'''),
        md('''### E1.3 · La misma descarga con `ThreadPoolExecutor`

Pedir páginas a una API es trabajo **I/O-bound**: casi todo el tiempo Python espera la red. Varios hilos pueden esperar a la vez sin cambiar qué se descarga.

**Función usada: `ThreadPoolExecutor` + `as_completed`**

| | |
|---|---|
| Para qué sirve | lanzar varias llamadas a la vez y recoger cada resultado cuando llega |
| Parámetros usados | `max_workers` (entre 2 y 6 en este taller) |
| Qué devuelve | `pool.submit(f, x)` devuelve un *futuro*; `as_completed` los entrega en orden de llegada |
| Cómo se interpreta | el orden de llegada cambia en cada ejecución; por eso se guarda cada página por su `offset` |
| Error frecuente | concatenar en orden de llegada, o pedir páginas distintas de las secuenciales |

**HAZ ESTO AHORA.** En la celda siguiente reemplaza `____` por el dato que identifica qué página debe descargar cada futuro.

**Error más probable:** `NameError: name '____' is not defined` significa que aún no completaste el hueco. Si pones otro valor, el checkpoint mostrará offsets distintos.

<details><summary>Si te atascas</summary>Cada futuro descarga <b>su</b> página: el argumento que falta es <code>offset</code>.</details>'''),
        code('''# E1.3 · Descarga concurrente (completa el hueco)
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
BENCH = T.comparar_e1(paginas_seq, SEG_SEQ, paginas_thr, SEG_THR, MAX_WORKERS)'''),
        lectura("Mismos offsets: se pidieron las mismas páginas. Mismas filas: llegó la misma cantidad. Mismo hash: la huella del conjunto de filas, que no depende del orden y conserva los duplicados, es idéntica.",
                "Si las tres respuestas son ✓, la concurrencia cambió *cómo* se descargó, no *qué* se descargó.",
                "Que la concurrencia sea más rápida en general: con pocas páginas, la creación de hilos y la latencia pueden hacerla más lenta. Para afirmarlo harían falta varias corridas limpias, sin caché.",
                "Comparar solo el número de filas. Dos snapshots con las mismas 3.000 filas pueden tener filas distintas; por eso se compara el hash."),
        code('''#@title E1.4 · Contratos con tu misma función concurrente y consolidación del RAW { display-mode: "form" }
pagina_contrato, OFFSETS_CONTRATOS = T.descargador_contratos()
paginas_con = descargar_concurrente(pagina_contrato, OFFSETS_CONTRATOS, MAX_WORKERS)
CRUCE = T.consolidar_e1(paginas_con)
_ = T.checkpoint("E1")'''),
        lectura("La cobertura es la fracción de procesos únicos de tu snapshot que encontró al menos un contrato por `id_del_portafolio → proceso_de_compra`. Las fechas dicen qué días cubre realmente tu snapshot.",
                "Hay población cruzada suficiente para E2–E4, y tu snapshot cubre **pocos días** del inicio de tu ventana, no los dos meses.",
                "Nada sobre la ventana completa ni sobre 2025: es el comienzo de la ventana. Tampoco que los procesos sin contrato no tengan contrato: puede firmarse otro día o con una persona natural, que el filtro excluye.",
                "Rellenar con cero los procesos sin contrato o cruzar por `id_del_proceso`. La clave de cruce es `id_del_portafolio → proceso_de_compra`."),
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

SECOP puede traer varias filas para el mismo proceso. El caso necesita **un documento por proceso**, con sus contratos resumidos dentro. Estas son las rutas de campo que usarás en Atlas:

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
        code(f'''#@title E2.1 · Elige el grano del documento {{ display-mode: "form" }}
GRANO = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.GRANOS)}
DOCUMENTOS = T.documentos_e2(GRANO)'''),
        lectura("Compara tres números: filas de la API, procesos únicos y documentos generados. Si coinciden los dos últimos y no hay identificadores repetidos, cada proceso es un documento.",
                "El grano define qué cuenta como «uno»: con un documento por fila, una consulta de los 10 procesos de mayor valor podría repetir el mismo proceso.",
                "Que los valores sean correctos: el grano solo garantiza que no se duplica la identidad.",
                "Elegir el grano por comodidad («así viene de la API») y no por la pregunta que el documento debe responder."),
        md('''### E2.2 · Conectar Atlas y cargar sin duplicar

La carga se hace desde Colab porque el Data Explorer de Atlas no importa archivos, igual que en S04. **Tu decisión es cómo escribir**: la celda prueba tu estrategia dos veces en una colección de ensayo y luego hace la carga oficial.

**OJO.** La URI se pide en un campo oculto (`getpass`). Nunca la escribas en una celda ni la imprimas: el validador bloquea la entrega si encuentra una URI con contraseña.'''),
        code('''#@title E2.2a · Conectar Atlas { display-mode: "form" }
ATLAS = T.conectar_atlas_e2()'''),
        code(f'''#@title E2.2b · Elige la estrategia de carga y ejecuta {{ display-mode: "form" }}
ESTRATEGIA = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.ESTRATEGIAS_CARGA)}
CARGA = T.cargar_e2(ESTRATEGIA)'''),
        lectura("La primera y la segunda carga deben dejar el mismo número de documentos, sin errores y con 0 duplicados.",
                "Una carga **idempotente** se puede repetir, por un corte de red o por una corrección, sin alterar la colección.",
                "Que los documentos estén actualizados: un índice único evita duplicados pero hace fallar la segunda carga y no actualiza nada.",
                "Creer que «sin error» significa «sin duplicados»: `insert_many` duplica en silencio."),
        md(f'''### E2.3 · Índices: **SAL DE COLAB. AHORA TRABAJAS EN MONGODB ATLAS.**

**HAZ ESTO AHORA.**
1. Atlas → **Data Explorer** → base `{C.ATLAS_DB}` → colección `tc1_<tu pareja en minúscula>` (por ejemplo `tc1_p03`). Comprueba que el número de documentos es el que imprimió E2.2.
2. Pestaña **Indexes** → **Create Index** → `{{ "id_proceso": 1 }}` y, en *Options*, marca **Create unique index**.
3. Crea **un índice más** cuyo primer campo use una consulta del taller (mira las consultas A, B y E3). Decide cuál y por qué: en E6 lo defenderás.
4. Vuelve y ejecuta la celda siguiente: lee los índices directamente de Atlas.'''),
        code('''#@title E2.3 · Leer los índices de Atlas { display-mode: "form" }
INDICES = T.indices_e2()'''),
        md(f'''### E2.4 · Consulta A en Atlas → Documents → Filter

**Pregunta:** ¿cuántos procesos tienen `precio base > 0` y **al menos un contrato** cruzado?

**HAZ ESTO AHORA.** Escribe el filtro en la barra *Filter* de tu colección, pulsa **Find** y mira el conteo. Luego copia el filtro **exactamente** como lo escribiste y pégalo entre las comillas de la celda siguiente.'''),
        code('''# E2.4 · Pega aquí el filtro que escribiste en Atlas (Documents → Filter)
FILTRO_A = \'\'\'pega aquí tu filtro\'\'\'
CONTEO_A = T.consulta_a_e2(FILTRO_A)'''),
        md('''### E2.5 · Consulta B en Atlas → Documents → Options

**Pregunta:** ¿cuáles son los 10 procesos con mayor valor de contratos? Desempate: `id_proceso` ascendente.

**HAZ ESTO AHORA.** En *Options* escribe el **Sort** y pon **Limit** en 10. Pulsa **Find**, comprueba el orden y pega aquí el Sort que usaste.'''),
        code('''# E2.5 · Pega aquí el Sort que usaste en Atlas (Documents → Options → Sort)
ORDEN_B = \'\'\'pega aquí tu sort\'\'\'
TOP10_B = T.consulta_b_e2(ORDEN_B)'''),
        lectura("El número de A y la lista de B salen de **tu** colección en Atlas: la celda vuelve a ejecutar lo que pegaste y lo compara con la referencia calculada desde tu RAW.",
                "Tu modelo y tus consultas responden lo que el caso pregunta.",
                "Que esos procesos tengan sobrecosto: B ordena por valor y no dice si el valor es razonable.",
                "En B, olvidar el desempate: con valores iguales, el orden de Atlas puede cambiar entre ejecuciones."),
        code('''#@title Checkpoint E2 { display-mode: "form" }
_ = T.checkpoint("E2")'''),
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

**HAZ ESTO AHORA.**
1. En tu colección abre **Aggregations** y activa el modo **Texto** (ícono `</>`), como en S04.
2. Escribe el pipeline, pulsa **Run** y revisa que salgan como máximo {C.BANDEJA_MAX} filas.
3. **Save → Save as** con el nombre exacto `tc1-bandeja-<tu pareja en minúscula>` (por ejemplo `tc1-bandeja-p03`).
4. **Export Code → Python 3**, desmarca *Include driver syntax* si aparece, copia el código y pégalo en la celda siguiente.
5. **Captura `E2_atlas.png`.** Debe verse la interfaz de Atlas, el nombre del pipeline guardado y su resultado. En Windows: `Win + Shift + S`; la imagen queda en *Imágenes → Capturas de pantalla*.

**OJO.** Antes de capturar, comprueba que en la pantalla no aparezcan contraseñas, tokens, URI ni cadenas de conexión.'''),
        code('''# E3 · Pega aquí el código que exportaste (Export Code → Python 3) o el pipeline del modo Texto
PIPELINE_E3 = \'\'\'pega aquí tu pipeline\'\'\'
BANDEJA = T.pipeline_e3(PIPELINE_E3)
BANDEJA.head(10)'''),
        code('''#@title Subir la captura E2_atlas.png (Atlas: pipeline guardado + resultado) { display-mode: "form" }
ruta, (ok, motivo) = X.guardar_captura(OUT, "E2")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = T.checkpoint("E3")'''),
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

**HAZ ESTO AHORA.** Toma las tres decisiones. La celda te anuncia qué pasará en Astra antes de que lo ejecutes.'''),
        code(f'''#@title E4.1 · Diseña la tabla {{ display-mode: "form" }}
PARTICION = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + list(C.OPCIONES_PARTICION))}
CLUSTERING = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + list(C.OPCIONES_CLUSTERING))}
TIPO_VALOR = "{C.SIN_SELECCION}" #@param {opciones([C.SIN_SELECCION] + C.OPCIONES_TIPO_VALOR)}
KEYSPACE = "{C.KEYSPACE_DEFECTO}" #@param {{type:"string"}}
CQL = T.cql_e4(PARTICION, CLUSTERING, TIPO_VALOR, KEYSPACE)
BLOQUES = T.bloques_cql()'''),
        md('''### E4.2 · **SAL DE COLAB. AHORA TRABAJAS EN ASTRA → CQL Console.**

**HAZ ESTO AHORA.**
1. Abre tu base en Astra. Si dice *Hibernated*, pulsa **Resume** y espera a que diga *Active*.
2. Abre **CQL Console** y pega los bloques **en orden**: primero DROP + CREATE, luego los INSERT y al final los dos SELECT. Espera a que cada bloque termine.
3. Selecciona y copia la salida de los dos SELECT: desde `count` hasta `(10 rows)`. Pégala entre las comillas de la celda siguiente.
4. **Captura `E4_astra.png`**: debe verse CQL Console con el SELECT, la partición (año y departamento) y el resultado con algunos IDs. Sin tokens a la vista.

**Si Astra responde con error**, es la consecuencia de tu diseño: vuelve a E4.1, cambia la decisión, ejecuta de nuevo y pega otra vez los bloques. El DROP del primer bloque borra la tabla anterior.'''),
        code('''# E4.2 · Pega aquí la salida de CQL Console (desde "count" hasta "(10 rows)")
SALIDA_ASTRA = \'\'\'pega aquí la salida de Astra\'\'\'
LEIDO = T.astra_e4(SALIDA_ASTRA)'''),
        code('''#@title Subir la captura E4_astra.png (CQL Console: SELECT + resultado) { display-mode: "form" }
ruta, (ok, motivo) = X.guardar_captura(OUT, "E4")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = T.checkpoint("E4")'''),
        lectura("El COUNT dice cuántas filas quedaron en la partición; el top 10 sale ordenado sin `ORDER BY` porque el clustering ya ordena por valor dentro de la partición.",
                "Tu tabla responde la pregunta en una sola partición: la lectura no crece con el resto de la tabla.",
                "Que esta tabla sirva para otra pregunta: «los 10 de una entidad» o «los de todo el país» necesitarían otra tabla. En Cassandra se duplica para responder.",
                "Diseñar la clave mirando qué columnas «parecen importantes» en lugar de mirar el `WHERE` de la consulta."),
        ficha("E5",
              "Responder una pregunta de conectividad contractual con un grafo real.",
              "¿Qué proveedores conectan a la entidad ancla con otras entidades dentro del snapshot?",
              "Colab para cargar el grafo; **Neo4j Aura → Query** para consultarlo.",
              "la carga con `UNWIND $filas` + `MERGE` (el patrón de S06), la consulta que encuentra la ancla y la consulta de contexto.",
              ["Conecta Aura y carga el grafo.", "En Aura ejecuta la consulta de la ancla.",
               "Completa los dos huecos (compartidos y ranking).", "Ejecuta ambas en Aura.",
               "Captura `E5_neo4j.png` y sube la evidencia."],
              "`E5/05_relaciones_grafo.csv`, `E5/05_neo4j_consultas.cypher`, `E5/05_resultado_relacional.csv`, `E5/05_neo4j_evidence.json` y `E5/E5_neo4j.png`.",
              "15: grafo y ancla 4 · métrica relacional 4 · Cypher 5 · ejecución real + captura 2."),
        md('''### E5.1 · El grafo y la regla de la ancla

El modelo es el de S06, con el contrato como nodo:

```
(:Entidad {nit})-[:FIRMA]->(:Contrato {id})-[:ADJUDICADO_A]->(:Proveedor {nit})
```

Un **proveedor compartido** es un proveedor que tiene contratos con dos o más entidades. La **entidad ancla** es la entidad con más proveedores compartidos (desempate: más contratos, luego el NIT). La regla se eligió por los datos: con la regla anterior, «la entidad con más contratos», la ancla no compartía ningún proveedor en ninguna de las seis ventanas que se probaron; con esta regla, las 12 ventanas del curso tienen una red con respuesta.

**OJO.** La contraseña de Aura se pide oculta. La carga solo borra contratos de cargas anteriores del TC1; no toca lo que hiciste en S06.'''),
        code('''#@title E5.1 · Conectar Aura y cargar el grafo { display-mode: "form" }
AURA = T.conectar_aura_e5()
CONTEOS = T.cargar_e5()'''),
        md('''### E5.2 · **SAL DE COLAB. AHORA TRABAJAS EN NEO4J AURA → Query.**

**HAZ ESTO AHORA.**
1. Ejecuta `RETURN 1 AS conexion` para comprobar que Query responde.
2. Ejecuta la consulta de la ancla que imprime la celda siguiente y mira la pestaña **Table**.
3. Vuelve: la celda lee el mismo resultado desde tu instancia y fija tu ancla.'''),
        code('''#@title E5.2 · La consulta de la ancla (cópiala en Aura) y tu ancla { display-mode: "form" }
print(S.CYPHER_ANCLA, "\\n")
NIT_ANCLA = T.ancla_e5()'''),
        md('''### E5.3 · Dos consultas, un hueco en cada una

| Cypher | Para qué |
|---|---|
| `WHERE` | descartar caminos; aquí, que la «otra» entidad no sea la ancla |
| `count(DISTINCT x)` | contar nodos distintos, no caminos (un proveedor puede llegar a la misma entidad por varios contratos) |
| `WITH` | pasar un resultado intermedio a la siguiente parte de la consulta |

**HAZ ESTO AHORA.** Completa el `____` de cada celda y ejecútala. La celda imprime la versión para pegar en Aura (con tu NIT en lugar de `$nit_ancla`). Ejecuta ambas en Aura; en *compartidos* mira la pestaña **Graph**.

**Error más probable:** contar filas con `count(otra)`. Los números saldrán inflados y el checkpoint marcará ✗ en la métrica.

<details><summary>Si te atascas</summary>Compartidos: <code>WHERE otra <> a</code>. Ranking: <code>count(DISTINCT otra)</code>.</details>'''),
        code('''# E5.3a · Proveedores compartidos (completa el WHERE)
CYPHER_COMPARTIDOS = \'\'\'
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE ____
RETURN p.nit AS nit_proveedor, p.nombre AS proveedor, collect(DISTINCT otra.nombre) AS otras_entidades
\'\'\'
T.preparar_consulta_e5("compartidos", CYPHER_COMPARTIDOS)'''),
        code('''# E5.3b · Ranking de proveedores puente (completa el conteo)
CYPHER_RANKING = \'\'\'
MATCH (a:Entidad {nit: $nit_ancla})-[:FIRMA]->(ca:Contrato)-[:ADJUDICADO_A]->(p:Proveedor)
WITH a, p, count(DISTINCT ca) AS contratos_con_ancla
MATCH (p)<-[:ADJUDICADO_A]-(:Contrato)<-[:FIRMA]-(otra:Entidad)
WHERE otra <> a
RETURN p.nit AS nit_proveedor, p.nombre AS proveedor, contratos_con_ancla, ____ AS entidades_conectadas
ORDER BY entidades_conectadas DESC, contratos_con_ancla DESC, nit_proveedor ASC
\'\'\'
T.preparar_consulta_e5("ranking", CYPHER_RANKING)'''),
        md('''**HAZ ESTO AHORA.** Con las dos consultas ya ejecutadas en Aura, toma **`E5_neo4j.png`**: debe verse Aura Query con la consulta de ranking y su resultado (o la vista Graph de compartidos, si aporta más). Sin contraseñas a la vista. Después ejecuta la celda siguiente.'''),
        code('''#@title E5.4 · Capturar tus resultados de Aura y subir E5_neo4j.png { display-mode: "form" }
RANKING = T.capturar_e5()
ruta, (ok, motivo) = X.guardar_captura(OUT, "E5")
print(("✓ " if ok else "✗ ") + f"{ruta.name}: {motivo}")
_ = T.checkpoint("E5")'''),
        lectura("Cada fila del ranking es un proveedor de la ancla que también contrata con otras entidades: cuántos contratos tiene con la ancla y con cuántas entidades distintas más.",
                "Qué proveedores hacen de **puente** entre tu entidad ancla y el resto de tu snapshot: el contexto que una tabla de contratos no muestra de un vistazo.",
                "Colusión, favorecimiento ni fraude. Además, un NIT puede agrupar varias sedes (SENA, ICBF): su centralidad puede reflejar tamaño administrativo, no comportamiento. Y solo ves contratos con empresas durante pocos días.",
                "Leer «conecta muchas entidades» como «es sospechoso». Un proveedor de seguros o de vigilancia contrata con muchas entidades por la naturaleza de su servicio."),
        ficha("E6",
              "Tomar tres decisiones de ingeniería y dos de interpretación ancladas a **tus** resultados, y entregar.",
              "¿Qué decidí, con qué evidencia y con qué límite?",
              "Google Colab.",
              "el informe técnico (se genera desde tus artefactos), el validador y el empaquetado.",
              ["Responde las decisiones mirando tus salidas.", "Responde la microdefensa.",
               "Ejecuta el validador final.", "Genera los tres archivos y entrégalos por Drive + correo."],
              "`E6/06_decision_log.json`, `E6/06_informe_tecnico.md`, `E6/06_microdefensa_grupal.json`, `manifest_tc1.json` y `TC1_<PAREJA_ID>.zip`.",
              "10: decisiones e informe 5 · microdefensa 3 · paquete completo y sin secretos 2."),
        md('''### E6.1 · Decisiones con tu evidencia

Aquí **no se escribe**: se elige. Cada respuesta se compara con **tus** datos, así que copiar la de otra pareja no sirve.

- **Concurrencia y 429.** Mira en E1.3 cuántos segundos tardó tu descarga concurrente.
- **Índice.** Elige el índice adicional que **creaste** en Atlas y la consulta que atiende.
- **Límite de la bandeja.** Elige una posición de **tu** bandeja (E3), escribe su `valor_contratos` en millones y elige qué dato falta para hablar de sobrecosto.'''),
        code(f'''#@title E6.1 · Tres decisiones ancladas a tus resultados {{ display-mode: "form" }}
DECISION_429 = "{C.SIN_SELECCION}" #@param {opciones(C.E6_DECISION_429)}
SEGUNDOS_DESCARGA_CONCURRENTE = 0 #@param {{type:"integer"}}
INDICE_ADICIONAL = "{C.SIN_SELECCION}" #@param {opciones(C.E6_INDICE)}
POSICION_EN_TU_BANDEJA = 1 #@param {{type:"slider", min:1, max:10, step:1}}
VALOR_EN_MILLONES = 0 #@param {{type:"integer"}}
DATO_QUE_FALTA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_DATO_FALTANTE)}
_ = T.decisiones_e6(DECISION_429, SEGUNDOS_DESCARGA_CONCURRENTE, INDICE_ADICIONAL, POSICION_EN_TU_BANDEJA,
                    VALOR_EN_MILLONES, DATO_QUE_FALTA)'''),
        code(f'''#@title E6.2 · Microdefensa {{ display-mode: "form" }}
RANGO_DE_TU_COBERTURA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_RANGOS_COBERTURA)}
QUE_EXPLICA_TU_COBERTURA = "{C.SIN_SELECCION}" #@param {opciones(C.E6_CAUSA_COBERTURA)}
QUE_NO_PERMITE_CONCLUIR_LA_RED = "{C.SIN_SELECCION}" #@param {opciones(C.E6_LIMITE_RED)}
ENTIDADES_DE_TU_PROVEEDOR_PUENTE = 0 #@param {{type:"integer"}}
T.microdefensa_e6(RANGO_DE_TU_COBERTURA, QUE_EXPLICA_TU_COBERTURA, QUE_NO_PERMITE_CONCLUIR_LA_RED,
                  ENTIDADES_DE_TU_PROVEEDOR_PUENTE)'''),
        md('''### E6.3 · Validación final

El validador recalcula todo desde tus archivos, igual que lo hará el docente sobre tu ZIP: no confía en ninguna variable de memoria. Imprime tu puntaje por etapa y, por cada control en ✗, **qué revisar** y **qué encontró**. Si detecta un posible secreto, bloquea la entrega y dice dónde está.

Los controles con captura salen como **provisionales** hasta que el docente vea tus tres imágenes.'''),
        code('''#@title E6.3 · Validar todo { display-mode: "form" }
MANIFEST = T.validar()'''),
        code('''#@title Entregar · genera los tres archivos (en Drive si activaste el avance) { display-mode: "form" }
CARPETA_ENTREGA, HUELLA = T.entregar(MANIFEST)'''),
        md(f'''## Entrega: Google Drive restringido + correo institucional

1. Abre la carpeta que imprimió la celda anterior en tu Drive. Debe contener **solo** `TC1_<PAREJA_ID>.ipynb`, `TC1_<PAREJA_ID>.zip` y `manifest_tc1.json`. Si no activaste Drive, descarga los tres archivos y súbelos a una carpeta nueva con el nombre impreso.
2. Clic derecho sobre la **carpeta** → **Compartir** → deja **Acceso general: Restringido** → agrega `{C.CORREO_DOCENTE}` como **Lector**.
3. Un integrante envía el correo a `{C.CORREO_DOCENTE}` con copia al compañero:
   - **Asunto:** `[BIG DATA 2026-2S][TC1] <PAREJA_ID> - <APELLIDO1> - <APELLIDO2>`
   - **Cuerpo:** pareja, nombres y códigos, enlace de la carpeta y la **huella SHA-256** que imprimió la celda anterior (una sola huella).
4. Si corriges algo antes del cierre, vuelve a validar y entregar, reemplaza los archivos en la misma carpeta y responde en el mismo hilo con `CORRECCIÓN DE ENTREGA` y la huella nueva.

**Fecha máxima: {C.FECHA_LIMITE}.** Cuenta el sello de tiempo del correo.

**GitHub es opcional:** solo por el navegador (*Add file → Upload files*), en un repositorio **privado** y sin códigos de estudiante en el README. No reemplaza Drive + correo.'''),
        md(f'''## Cierre

**La historia, en cinco frases.** Descargaste un snapshot de SECOP de dos maneras y demostraste que es el mismo. Lo convertiste en documentos, un proceso por documento, y lo cargaste en Atlas sin duplicar. En Atlas construiste una bandeja que dice por dónde empezar a revisar. Serviste esa bandeja en Cassandra con una tabla diseñada desde su consulta. Y en Neo4j viste qué proveedores conectan a una entidad con otras.

**La idea más importante.** El mismo dato necesita modelos distintos según la pregunta: documento para leer un proceso completo, tabla query-first para servir una consulta conocida, grafo para recorrer relaciones. Ninguno reemplaza a los otros.

**Errores comunes.** Comparar solo conteos en vez de hashes · un documento por fila · `insert_many` repetido · olvidar el desempate · diseñar la tabla Cassandra sin mirar el `WHERE` · contar filas en vez de entidades distintas · leer prioridad o conexión como prueba de irregularidad.

**MÁS ADELANTE.** S09 cambia la pregunta: ¿qué pasa cuando las palabras de la consulta no coinciden con las del documento? Ahí aparecen los embeddings y la búsqueda vectorial.

### Hoja de trucos

| Necesitas | Herramienta |
|---|---|
| descargar en paralelo sin cambiar el resultado | `ThreadPoolExecutor` + `as_completed`, guardando por `offset` |
| filtrar en Atlas (Documents → Filter) | `{{"campo.anidado": {{"$gt": 0}}, "otro.campo": {{"$gt": 0}}}}`: varias condiciones = todas deben cumplirse |
| ordenar en Atlas (Documents → Options) | Sort `{{"campo": -1, "desempate": 1}}` (-1 descendente, 1 ascendente) · Limit |
| bandeja en Atlas | `$match` → `$project` → `$sort` → `$limit` |
| tabla query-first | `PRIMARY KEY ((columnas del WHERE), columna de orden, id)` + `CLUSTERING ORDER BY` |
| grafo | `UNWIND $filas AS fila MERGE ...`; contar con `count(DISTINCT ...)` |
| validar en cualquier momento | `T.checkpoint("E2")` (o la etapa que quieras) |'''),
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
