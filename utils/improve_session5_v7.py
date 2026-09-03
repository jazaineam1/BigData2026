#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Reduce carga cognitiva de S5 sin quitar ninguna herramienta.

Se ejecuta después de improve_session5_v6.py. Conserva Colab, Atlas, tutoriales,
pandas/SECOP, Astra/CQL y Python con SCB/token/driver. El cambio es pedagógico:
- 9 resultados dejan de presentarse como 9 productos y se agrupan en 3 productos;
- se explicita qué ENTENDER, qué EJECUTAR y qué MODIFICAR;
- Cassandra se razona primero con papel/cajones y después se traduce a PRIMARY KEY;
- Astra/CQL y Python aparecen como dos tramos del MISMO producto 3;
- el tutorial Astra mantiene todos sus pasos, pero reduce saltos mentales.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos" / "5_Atlas_Cassandra_Query_First.ipynb"
ASTRA = ROOT / "assets" / "tutoriales" / "astra-cassandra-paso-a-paso-v3.html"


def src(cell: dict) -> str:
    value = cell.get("source", "")
    return "".join(value) if isinstance(value, list) else str(value)


def put(cell: dict, text: str) -> None:
    cell["source"] = text.strip()


def md(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": text.strip()}


def find(cells: list[dict], needle: str) -> int:
    for i, cell in enumerate(cells):
        if needle in src(cell):
            return i
    raise RuntimeError(f"No se encontró el marcador {needle!r}")


def insert_once(cells: list[dict], anchor: str, marker: str, new_cells: list[dict], *, after: bool = False) -> None:
    if any(marker in src(c) for c in cells):
        return
    i = find(cells, anchor)
    pos = i + 1 if after else i
    cells[pos:pos] = new_cells


def main() -> None:
    nb = json.loads(NB.read_text(encoding="utf-8"))
    cells = nb["cells"]

    # 1) Tres productos, sin eliminar ninguna tecnología ni evidencia.
    # Esta transformación ya quedó aplicada en una corrida anterior del
    # pipeline (el marcador se convierte en "Contrato de éxito" y no
    # reaparece), así que se omite en vez de fallar buscándolo de nuevo.
    if any("### Producto observable de hoy" in src(c) for c in cells):
        i = find(cells, "### Producto observable de hoy")
        text = src(cells[i])
        prefix = text.split("### Producto observable de hoy", 1)[0].rstrip()
        put(cells[i], prefix + '''

### Contrato de éxito — tres productos, las mismas herramientas

Hoy seguimos usando **todo** el recorrido técnico del curso:

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/01_pipeline_sesion.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/01_pipeline_sesion.png" width="900" alt="Arquitectura de la sesion: Colab, MongoDB Atlas, tutorial visual, pandas, Astra CQL y Python"></a></div>

*Recorrido: Colab (entrada) → MongoDB Atlas (persistencia) → tutorial visual (guía paso a paso) → Colab / pandas (bandeja SECOP) → Astra / CQL (tabla operativa) → Colab / Python (CRUD + comparación).*

La diferencia es que no vas a sentir nueve entregables distintos. Todo queda agrupado en **tres productos**:

| Producto | Qué construyes | Controles/evidencias que viven dentro |
|---|---|---|
| **1 · Vista Atlas** | `menciones_clasificadas` | 142 entidades · 6 alta / 25 media / 111 baja |
| **2 · Bandeja explicable** | 77 candidatos de revisión | `1.000 → 163 → 77` + contraste de hipótesis H1 + límite de la prensa |
| **3 · Consulta operacional** | `corte + departamento → top 5` en Cassandra | diseño query-first + CQL + CRUD/automatización desde Python + comparación con pandas |

El **hito descargable** y `s05_ancla_s06.json` son salidas automáticas que documentan esos tres productos; no son productos adicionales.

> **Criterio de éxito.** Si puedes explicar la vista, justificar cómo llegamos a 77 y razonar por qué la tabla Cassandra responde el top 5, completaste el núcleo conceptual. La conexión Python sigue en la sesión, pero su código de infraestructura se **ejecuta**, no se memoriza.
''')

    # 2) Mapa con roles cognitivos. Se mantienen exactamente las mismas superficies.
    i = find(cells, "## Mapa de la sesión")
    put(cells[i], '''
## Mapa de la sesión — mismas herramientas, menos cambios mentales

| Tramo | Rol | Pregunta | Herramienta | Qué queda |
|---|---|---|---|---|
| 1. Retomar S4 | 🧠 **ENTIENDE** | ¿desde dónde partimos? | Colab + Atlas | 987 + 142 |
| 2. Construir vista | ▶️ **EJECUTA** | ¿cómo publicamos la clasificación? | tutorial + Atlas | producto 1 |
| 3. Construir bandeja | 🧠 + ▶️ | ¿qué procesos pasan primero? | Colab + pandas/SECOP | producto 2 |
| 4. Contrastar hipótesis | 🧠 **ENTIENDE** | ¿qué evidencia aporta realmente la prensa? | Colab | alcance correcto |
| 5. Diseñar Cassandra | 🧠 **ENTIENDE** | ¿qué pregunta repetitiva debemos servir? | papel + cuaderno | partición + orden |
| 6. Implementar CQL | ▶️ **EJECUTA** | ¿la tabla sirve esa pregunta? | tutorial + Astra/CQL | producto 3, tramo A |
| 7. Automatizar | ▶️ + ✏️ **MODIFICA** | ¿cómo usa una aplicación la misma tabla? | Colab + Python | producto 3, tramo B |
| 8. Cerrar | 🧠 **EXPLICA** | ¿qué resolvió cada motor y qué límite queda? | cuaderno | hito + ancla S6 |

### Semáforo de código

- 🧠 **ENTIENDE:** debes poder explicarlo con tus palabras.
- ▶️ **EJECUTA:** corre la celda y verifica la salida; **no necesitas escribirla de memoria**.
- ✏️ **MODIFICA:** cambia únicamente el dato señalado y observa qué ocurre.

**Regla de navegación del curso:** el cuaderno explica **por qué, qué significa y qué límite tiene**; los tutoriales HTML explican **dónde hacer clic y qué debe aparecer**.
''')

    # 3) Cassandra: problema manual antes de vocabulario y sintaxis.
    insert_once(cells, "### Escena operacional", "Microejemplo en papel", [md('''
### Microejemplo en papel — resuelve la consulta antes de conocer Cassandra

Laura tiene estas cinco filas:

| corte | departamento | proceso | valor |
|---|---|---|---:|
| 03-sep | Bogotá | P1 | 50 |
| 03-sep | Bogotá | P2 | 180 |
| 03-sep | Bogotá | P3 | 90 |
| 03-sep | Antioquia | P4 | 300 |
| 02-sep | Bogotá | P5 | 500 |

Pregunta: **para el corte 03-sep y Bogotá, ¿qué tres procesos debe abrir primero si ordenamos por valor?**

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/07_ranking_procesos.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/07_ranking_procesos.png" width="300" alt="Ranking de procesos P2, P3, P1 por valor"></a></div>

Antes de pensar en sintaxis ya sabemos dos cosas:

1. necesitamos **localizar** el grupo `03-sep + Bogotá`;
2. dentro de ese grupo necesitamos **ordenar** de mayor a menor valor.

Cassandra aparecerá después como una forma de materializar exactamente esas dos decisiones.
''')])

    insert_once(cells, "### Ejercicio", "Traducción de la PK en tres pasos", [md('''
### Traducción de la PK en tres pasos — no memorices los paréntesis

```text
PASO 1 · localizar el cajón
(corte, departamento)

PASO 2 · ordenar dentro del cajón
valor_base DESC, id_proceso ASC

PASO 3 · traducirlo a CQL
PRIMARY KEY ((corte, departamento), valor_base, id_proceso)
```

Se lee así:

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/10_pk_traduccion.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/10_pk_traduccion.png" width="560" alt="Traduccion de la PRIMARY KEY en partition key y clustering"></a></div>

**Objetivo de aprendizaje.** No debes reconstruir los paréntesis de memoria. Debes mirar una clave y poder decir **qué localiza la partición y qué organiza sus filas**.
''')])

    # 4) Astra y Python son dos tramos del mismo producto, no dos nuevos objetivos.
    i = find(cells, "## 8. Tutorial visual 2")
    original = src(cells[i])
    body = original.split("\n", 1)[1] if "\n" in original else ""
    put(cells[i], '''
---
## 8. PRODUCTO 3 · Tramo A — implementar la pregunta en Astra/CQL

**▶️ EJECUTA.** Ahora sí llevamos el diseño a la interfaz. No estás aprendiendo “otra historia”: estás implementando la consulta que ya resolviste en papel.

**🧠 ENTIENDE:** `partition → clustering → consulta soportada / consulta no soportada`.  
**▶️ EJECUTA:** crear base, esperar `Active`, abrir CQL Console, crear tabla y probar CQL.  
**✏️ MODIFICA:** valores de consulta cuando el tutorial te lo indique.

''' + body)

    insert_once(cells, "## 9. La misma tabla, ahora desde Python", "Checkpoint", [md('''
### Checkpoint — ya entendiste Cassandra antes de conectar Python

Antes de abrir SCB/token, comprueba que puedes contestar:

1. ¿Qué consulta repetitiva estamos sirviendo?  
2. ¿Cuál es el “cajón” de esa consulta?  
3. ¿Cómo se ordenan sus filas?  
4. ¿Por qué consultar solo por `entidad` requiere otro diseño?

Si puedes responder esas cuatro preguntas, **la comprensión central de Cassandra ya está**. El siguiente tramo conserva Python porque el PDA pide CRUD e integración, pero no introduce otro modelo de datos: automatiza **la misma tabla**.
''')])

    # Esta cabecera se reemplaza a sí misma (pasa a "PRODUCTO 3 · Tramo B") y
    # no reaparece en corridas posteriores del pipeline: se omite si ya fue
    # aplicada antes, en vez de fallar buscándola de nuevo.
    if any("## 9. La misma tabla, ahora desde Python" in src(c) for c in cells):
        i = find(cells, "## 9. La misma tabla, ahora desde Python")
        put(cells[i], '''
---
## 9. PRODUCTO 3 · Tramo B — la misma tabla, ahora desde Python

El PDA pide CRUD con Python. **No es un cuarto producto ni otro motor.** Una aplicación usa la misma tabla Cassandra que acabas de diseñar y probar en CQL Console.

### Qué debes hacer con esta parte

- ▶️ **EJECUTA** la instalación, carga del SCB y creación de `Cluster/Session`.
- 🧠 **ENTIENDE** que SCB = ruta segura, token = autenticación, `Session` = canal para ejecutar CQL.
- ✏️ **MODIFICA** el departamento/consulta en los puntos señalados y compara el resultado.
- 🧠 **ENTIENDE** CRUD como cuatro operaciones sobre la misma tabla; no memorices la ceremonia de conexión.

<div align="center"><a href="https://github.com/jazaineam1/BigData2026/blob/main/assets/diagrams/session5/12_cql_vs_python.svg" target="_blank"><img src="https://raw.githubusercontent.com/jazaineam1/BigData2026/main/assets/diagrams/session5/12_cql_vs_python.png" width="560" alt="Comparacion entre CQL Console y Python para la misma tabla"></a></div>

**PARA LLEVAR.** Python automatiza lo que ya comprendiste en CQL; no cambia el modelo Cassandra.
''')

    # 5) Marcar claramente las celdas de infraestructura y de modificación.
    for cell in cells:
        text = src(cell)
        if cell.get("cell_type") != "code":
            continue
        if "!pip install -q cassandra-driver" in text and "▶️ EJECUTA" not in text:
            put(cell, "# ▶️ EJECUTA · soporte de conexión; no memorices esta celda.\n" + text)
        elif "Sube UN solo Secure Connect Bundle" in text and "▶️ EJECUTA" not in text:
            put(cell, "# ▶️ EJECUTA · infraestructura guiada SCB/token; no memorices objetos.\n" + text)
        elif "departamento_elegido = opciones_departamento" in text and "✏️ MODIFICA" not in text:
            put(cell, "# ✏️ MODIFICA · aquí tu elección sí cambia la evidencia individual.\n" + text)
        elif "top5_propio = list(session.execute" in text and "🧠 ENTIENDE" not in text:
            put(cell, "# 🧠 ENTIENDE · verifica que pandas y Cassandra respondan la misma pregunta.\n" + text)

    # 6) Recap final: tres productos, no nueve tareas sueltas.
    insert_once(cells, "## 12. Hito de la sesión", "Checkpoint de los tres productos", [md('''
### Checkpoint de los tres productos — antes de generar el hito

| Producto | Señal de que está listo |
|---|---|
| **1 · Vista Atlas** | existe `menciones_clasificadas` y controlas `6 + 25 + 111 = 142` |
| **2 · Bandeja explicable** | puedes reconstruir `1.000 → 163 → 77` y explicar qué refutó H1 |
| **3 · Consulta operacional** | sabes por qué la PK sirve `corte + departamento → top 5`, ejecutaste CQL y viste la misma tabla desde Python |

El hito y el ancla S6 que siguen **documentan** este trabajo. No agregan un cuarto o quinto objetivo.
''')])

    NB.write_text(json.dumps(nb, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    json.loads(NB.read_text(encoding="utf-8"))

    # 7) Tutorial Astra v3: misma herramienta y mismos pasos, nueva secuencia cognitiva.
    html = ASTRA.read_text(encoding="utf-8")

    if "Resuélvelo en papel antes de tocar Cassandra" not in html:
        anchor = '<section class="slide"><div class="tag">Antes de hacer clic</div><h2>¿Por qué Cassandra si hoy solo tenemos 77 filas?</h2>'
        extra = '''<section class="slide"><div class="tag gold">🧠 ENTIENDE · antes de hacer clic</div><h2>Resuélvelo en papel antes de tocar Cassandra</h2><p class="sub">Para el corte 03-sep y Bogotá aparecen P1=$50 M, P2=$180 M y P3=$90 M. Laura pide los tres de mayor valor.</p><div class="flow"><div class="node"><b>1. Localizar</b><br>03-sep + Bogotá</div><div class="arrow">↓</div><div class="node"><b>2. Ordenar</b><br>P2 → P3 → P1</div><div class="arrow">↓</div><div class="node"><b>3. Después traducir</b><br>partition + clustering</div></div><div class="call"><b>Regla de la sesión.</b> Primero resuelve la pregunta con sentido común; después aprende cómo Cassandra organiza los datos para servirla.</div></section>\n\n'''
        if anchor not in html:
            raise RuntimeError("Tutorial Astra v3 perdió el ancla '¿Por qué Cassandra...?'")
        html = html.replace(anchor, extra + anchor, 1)

    if "Por qué Cassandra + Astra" not in html:
        anchor = '<section class="slide"><div class="tag">Modelo mental</div><h2>Astra, Cassandra, CQL y keyspace no son lo mismo</h2>'
        extra = '''<section class="slide"><div class="tag">Por qué Cassandra + Astra</div><h2>Dos motores, dos trabajos distintos en la misma historia</h2><div class="grid"><div><table><tr><th>criterio</th><th>MongoDB / Atlas</th><th>Cassandra / Astra</th></tr><tr><td>modelado</td><td>schema-first: modelas los datos y después preguntas</td><td>query-first: la tabla nace de la consulta que vas a servir</td></tr><tr><td>arquitectura</td><td>replica set primario/secundario</td><td>anillo peer-to-peer, sin nodo maestro</td></tr><tr><td>fortaleza</td><td>exploración, transformación, esquema flexible</td><td>lecturas/escrituras masivas y predecibles por clave de partición</td></tr><tr><td>rol en S05</td><td>capa de análisis: clasifica, cruza, formula hipótesis</td><td>capa de servicio: responde la misma pregunta miles de veces</td></tr></table><div class="call"><b>En una frase.</b> Mongo transforma y explora; Cassandra sirve, a escala, una pregunta ya conocida.</div></div><div><div class="call"><b>¿Por qué escala horizontal sin nodo maestro?</b> Si un nodo cae, el anillo sigue sirviendo sin coordinación central: importa para un servicio 24/7 con contratación pública de todo el país.</div><div class="call"><b>¿Por qué Astra y no Cassandra instalado a mano?</b> Administrar un clúster real (anillos, reparación, compactación, tokens) es una carga operativa considerable. Astra la esconde como servicio administrado para que el foco pedagógico sea el <b>modelado de datos</b>, no la infraestructura.</div><div class="call warn"><b>No es &quot;Cassandra es mejor&quot;.</b> Es una decisión de <b>ajuste al patrón de acceso</b>: consulta repetitiva y conocida → Cassandra. Exploración flexible y cambiante → MongoDB.</div></div></div></section>\n\n'''
        if anchor not in html:
            raise RuntimeError("Tutorial Astra v3 perdió el ancla 'Modelo mental'")
        html = html.replace(anchor, extra + anchor, 1)

    if "Tres pasos antes de leer la PRIMARY KEY" not in html:
        anchor = '<section class="slide"><div class="tag">Concepto clave</div><h2>Partition = cajón; clustering = orden dentro del cajón</h2>'
        extra = '''<section class="slide"><div class="tag gold">🧠 ENTIENDE · traducción</div><h2>Tres pasos antes de leer la PRIMARY KEY</h2><div class="cards"><div class="card"><b>1 · Localiza</b><p><code>(corte, departamento)</code> identifica el cajón.</p></div><div class="card"><b>2 · Ordena</b><p><code>valor_base DESC</code> organiza dentro del cajón.</p></div><div class="card"><b>3 · Traduce</b><p><code>PRIMARY KEY ((corte, departamento), valor_base, id_proceso)</code>.</p></div></div><div class="call"><b>No memorices paréntesis.</b> Señala primero qué parte localiza y cuál ordena; la sintaxis viene después.</div></section>\n\n'''
        if anchor not in html:
            raise RuntimeError("Tutorial Astra v3 perdió el ancla de partition/clustering")
        html = html.replace(anchor, extra + anchor, 1)

    if "MISMO PRODUCTO 3 · Tramo B" not in html:
        anchor = '<section class="slide"><div class="tag">Paso 10</div><h2>Connection details → SCB + token</h2>'
        extra = '''<section class="slide"><div class="tag gold">MISMO PRODUCTO 3 · Tramo B</div><h2>De la consola a Python sin cambiar de modelo</h2><p class="sub">Hasta aquí ya diseñaste y probaste Cassandra. Ahora conservamos SCB, token y driver porque una aplicación debe automatizar la misma tabla; no estás empezando otra tecnología conceptual.</p><div class="cards"><div class="card"><b>▶ EJECUTA</b><p>SCB, token y conexión.</p></div><div class="card"><b>🧠 ENTIENDE</b><p>Python envía CQL a la misma tabla.</p></div><div class="card"><b>✏ MODIFICA</b><p>valores de consulta y compara resultados.</p></div></div><div class="call warn"><b>No memorices</b> la ceremonia de conexión. Sí debes poder explicar la consulta, la partición y el resultado.</div></section>\n\n'''
        if anchor not in html:
            raise RuntimeError("Tutorial Astra v3 perdió Connection details Paso 10")
        html = html.replace(anchor, extra + anchor, 1)

    # Etiquetas de acción: no se eliminan pasos, solo se hace visible qué se espera del estudiante.
    html = html.replace('<div class="tag">Concepto clave</div>', '<div class="tag">🧠 ENTIENDE · Concepto clave</div>')
    html = html.replace('<div class="tag gold">Error plantado</div>', '<div class="tag gold">🧠 PREDICE · Error plantado</div>')
    for n in range(1, 12):
        html = html.replace(f'<div class="tag">Paso {n}</div>', f'<div class="tag">▶ EJECUTA · Paso {n}</div>')

    ASTRA.write_text(html, encoding="utf-8")
    print(f"[OK] S5 v7: {len(cells)} celdas; 3 productos, semáforo cognitivo y tutorial Astra reestructurado sin quitar herramientas.")


if __name__ == "__main__":
    main()
