#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Refuerza la enseñanza del grado en S06: Table mide y Graph explica.

Se ejecuta antes de regenerar el notebook. Es idempotente y modifica las dos
fuentes editoriales relevantes: el módulo Graph Lab y su tutorial visual Aura.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENH = ROOT / "utils" / "session6_graphlab_enhancements.py"
TUTORIAL = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
MARKER = "GRAPH-DEGREE-S06-V1"


def upgrade_module() -> None:
    text = ENH.read_text(encoding="utf-8")
    if MARKER in text:
        print("[OK] Graph Lab ya contiene la mejora de grado visual")
        return

    pattern = re.compile(
        r"    md\(r'''### Grado ≠ entidades conectadas\n.*?"
        r"Un proveedor puede tener grado alto porque una sola entidad le adjudicó muchos procesos; "
        r"por eso H2-R no usa simplemente el grado\.\n'''\),",
        re.S,
    )
    replacement = r'''    md(r'''### Grado ≠ entidades conectadas

<!-- GRAPH-DEGREE-S06-V1 -->
**Grado contractual directo del Proveedor:** cuántas relaciones `ADJUDICADO_A` llegan al nodo.  
**Conectividad a dos saltos:** cuántas Entidades distintas llegan al mismo Proveedor pasando por Proceso.

> **Table mide; Graph explica.** El número exacto del grado se obtiene con Cypher. En Graph compruebas visualmente de qué relaciones incidentes sale ese número. El tamaño, la cercanía o la posición automática de un círculo **no representan su grado** salvo que tú hayas configurado explícitamente un estilo para codificarlo.

**1 · Mide el grado exacto en Aura Query → Table**

```cypher
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       count(r) AS grado_adjudicaciones
ORDER BY grado_adjudicaciones DESC, nit_proveedor ASC
LIMIT 10
```

`count(r)` cuenta las relaciones directas `ADJUDICADO_A` que llegan a cada Proveedor en este modelo.

**2 · Comprueba gráficamente el proveedor de mayor grado**

```cypher
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v:Proveedor)
WITH v, count(r) AS grado_adjudicaciones
ORDER BY grado_adjudicaciones DESC, v.nit ASC
LIMIT 1
MATCH (p:Proceso)-[r:ADJUDICADO_A]->(v)
RETURN v, r, p
ORDER BY p.id
LIMIT 40
```

En **Graph**, coloca el Proveedor en el centro y cuenta conceptualmente las líneas `ADJUDICADO_A`: son las relaciones que Cypher acaba de medir. Luego vuelve a **Table** para conservar el valor exacto.

Un proveedor puede tener grado alto porque una sola entidad le adjudicó muchos procesos; por eso H2-R usa `entidades_conectadas` y no simplemente el grado.
'''),'''

    new_text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit("No se encontró exactamente una sección 'Grado ≠ entidades conectadas' en Graph Lab")
    ENH.write_text(new_text, encoding="utf-8")
    print("[OK] Módulo Graph Lab: grado exacto + lectura gráfica añadidos")


def upgrade_tutorial() -> None:
    text = TUTORIAL.read_text(encoding="utf-8")
    if MARKER in text:
        print("[OK] Tutorial Graph Lab ya contiene la mejora de grado visual")
        return

    pattern = re.compile(
        r'<section class="slide"><div class="tag">5 · Grado</div>.*?</section>\s*'
        r'(?=<section class="slide"><div class="tag gold">WOW 1</div>)',
        re.S,
    )
    replacement = r'''<section class="slide"><div class="tag">5 · Grado exacto</div><h2>Table mide; Graph explica</h2><!-- GRAPH-DEGREE-S06-V1 --><div class="grid"><div><p class="sub">Primero mide el <b>grado contractual directo</b>: cuántas relaciones <code>ADJUDICADO_A</code> llegan a cada Proveedor.</p><pre>MATCH (p:Proceso)-[r:ADJUDICADO_A]-&gt;(v:Proveedor)
RETURN v.nit AS nit_proveedor,
       v.nombre AS proveedor,
       count(r) AS grado_adjudicaciones
ORDER BY grado_adjudicaciones DESC, nit_proveedor ASC
LIMIT 10</pre><div class="result ok">Abre <b>Table</b>. <code>count(r)</code> es el valor que debes reportar: no lo adivines mirando el dibujo.</div></div><div><h3>Qué significa aquí “grado”</h3><table><tr><th>Métrica</th><th>Pregunta</th></tr><tr><td><b>grado_adjudicaciones</b></td><td>¿Cuántas relaciones directas de adjudicación llegan al Proveedor?</td></tr><tr><td><b>entidades_conectadas</b></td><td>¿Cuántas Entidades distintas alcanzan al Proveedor pasando por Proceso?</td></tr></table><div class="call warn"><b>No confundas métricas.</b> Diez procesos adjudicados por una sola entidad producen grado 10, pero conectividad institucional 1.</div></div></div></section>
<section class="slide"><div class="tag">5.1 · Grado gráfico</div><h2>Ahora comprueba de dónde sale el número</h2><div class="grid"><div><pre>MATCH (p:Proceso)-[r:ADJUDICADO_A]-&gt;(v:Proveedor)
WITH v, count(r) AS grado_adjudicaciones
ORDER BY grado_adjudicaciones DESC, v.nit ASC
LIMIT 1
MATCH (p:Proceso)-[r:ADJUDICADO_A]-&gt;(v)
RETURN v, r, p
ORDER BY p.id
LIMIT 40</pre><p class="sub">Cambia a <b>Graph</b>, usa Fit to screen, arrastra el Proveedor al centro y sigue cada línea <code>ADJUDICADO_A</code> hasta sus Procesos. Graph hace visible la estructura que Table acaba de medir.</p></div><div><div class="ui" aria-label="Representación de un proveedor central con múltiples adjudicaciones"><div class="ui-top"><b>Result · Graph</b><span>representación</span></div><div class="ui-body"><div class="tabs"><span class="sel">Graph</span><span>Table</span><span>RAW</span></div><div class="graph"><div class="node v" style="left:42%;top:31%;width:92px;height:92px">Proveedor<br>hub</div><div class="node p" style="left:6%;top:8%;width:62px;height:62px">P1</div><div class="node p" style="left:7%;top:66%;width:62px;height:62px">P2</div><div class="node p" style="left:75%;top:8%;width:62px;height:62px">P3</div><div class="node p" style="left:76%;top:66%;width:62px;height:62px">P4</div><div class="edge" style="left:17%;top:24%;width:29%;transform:rotate(22deg)"></div><div class="edge" style="left:17%;top:72%;width:30%;transform:rotate(-22deg)"></div><div class="edge" style="left:57%;top:43%;width:22%;transform:rotate(-35deg)"></div><div class="edge" style="left:57%;top:58%;width:23%;transform:rotate(34deg)"></div></div></div></div><div class="call bad"><b>Muy importante:</b> el tamaño, la posición o la cercanía automática del nodo no codifican grado. El grado exacto viene de <code>count(r)</code>; las líneas del Graph te ayudan a explicarlo.</div></div></div></section>
'''

    new_text, n = pattern.subn(replacement, text, count=1)
    if n != 1:
        raise SystemExit("No se encontró exactamente una diapositiva '5 · Grado' en el tutorial Graph Lab")
    TUTORIAL.write_text(new_text, encoding="utf-8")
    print("[OK] Tutorial Graph Lab: Table→grado exacto→Graph añadido")


def main() -> None:
    for path in (ENH, TUTORIAL):
        if not path.is_file():
            raise SystemExit(f"Falta {path.relative_to(ROOT)}")
    upgrade_module()
    upgrade_tutorial()


if __name__ == "__main__":
    main()
