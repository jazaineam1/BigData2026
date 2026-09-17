#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parche pedagógico/visual S06: continuidad S5, Graph Lab, grados y WOW."""
from __future__ import annotations
import json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
GRAPH_TUTORIAL="https://jazaineam1.github.io/BigData2026/assets/tutoriales/neo4j-graph-lab-s06.html"
MARKER="GRAPH-LAB-S06-V2"

def s(c):
    v=c.get("source",""); return "".join(v) if isinstance(v,list) else str(v)
def put(c,t): c["source"]=t.splitlines(keepends=True)
def find(cells,x,starts=False):
    h=[i for i,c in enumerate(cells) if (s(c).startswith(x) if starts else x in s(c))]
    if len(h)!=1: raise ValueError(f"Referencia S06 ambigua {x!r}: {h}")
    return h[0]
def md(t): return {"cell_type":"markdown","metadata":{},"source":t.strip("\n").splitlines(keepends=True)}
def code(t,hidden=False,title=None):
    t=t.strip("\n").replace('"""', "'''"); t=(f'#@title {title} {{ display-mode: "form" }}\n'+t) if title else t
    c={"cell_type":"code","execution_count":None,"metadata":{},"outputs":[],"source":t.splitlines(keepends=True)}
    if hidden:c["metadata"]={"tags":["hide-input"],"jupyter":{"source_hidden":True},"cellView":"form","colab":{"formView":"both"}}
    return c

def anchor(cells):
    i=find(cells,"## 1. Recuperar el proceso que Laura abrió en S5")
    put(cells[i],'''---
## 1. Recuperar el proceso que Laura abrió en S5

S6 tiene **dos rutas transparentes**. Si conservaste `s05_ancla_s06.json`, usa tu proceso real de S5; si no, usa la ancla pedagógica versionada. El respaldo permite aprender sin bloquear la clase, pero **no se presenta como si fuera tu elección**. H2-R solo se interpreta como resultado individual cuando el origen sea `archivo propio S5`.
''')
    i=find(cells,"# El cuaderno trae el ancla pedagógica versionada",True)
    put(cells[i],r'''#@title Elegir ancla propia S5 o respaldo { display-mode: "form" }
from pathlib import Path
import json
USAR_MI_ANCLA_S5 = False  #@param {type:"boolean"}
archivo_s5 = Path("s05_ancla_s06.json")
if USAR_MI_ANCLA_S5 and not archivo_s5.is_file():
    try:
        from google.colab import files
        print("Selecciona s05_ancla_s06.json, descargado al final de S5.")
        subidos=files.upload()
        if "s05_ancla_s06.json" not in subidos: raise ValueError("Selecciona exactamente s05_ancla_s06.json o desactiva USAR_MI_ANCLA_S5.")
        archivo_s5.write_bytes(subidos["s05_ancla_s06.json"])
    except ImportError:
        raise FileNotFoundError("Copia s05_ancla_s06.json junto al cuaderno o usa el respaldo.")
if USAR_MI_ANCLA_S5:
    ancla_original=json.loads(archivo_s5.read_text(encoding="utf-8-sig"))
    faltantes=[k for k in ["id_proceso","entidad","nit_entidad"] if not str(ancla_original.get(k,"")).strip()]
    if faltantes: raise ValueError(f"Archivo S5 incompleto: {faltantes}")
    origen_ancla="archivo propio S5"
else:
    ancla_original=dict(manifest["ancla_pedagogica"]); origen_ancla="ancla pedagógica versionada incluida en S6"
print("Origen del ancla:",origen_ancla)
print(json.dumps(ancla_original,ensure_ascii=False,indent=2))
''')

def concepts(cells):
    i=find(cells,"Antes de escribir Cypher, cinco palabras y nada más")
    t=s(cells[i]).replace("cinco palabras y nada más","seis conceptos y nada más").replace("**Los mismos 5 conceptos, en LinkedIn:**","**Los mismos conceptos, en LinkedIn:**")
    t=t.replace("| Camino | una secuencia de nodos y relaciones | Entidad → Proceso → Proveedor |","| Camino | una secuencia de nodos y relaciones | Entidad → Proceso → Proveedor |\n| Patrón | la forma que quieres encontrar | `(e)-[:PUBLICA]->(p)` |")
    put(cells[i],t+'\n**Regla mental:** `MATCH` significa “encuentra coincidencias con esta forma”. El patrón es el corazón de Cypher.\n')
    i=find(cells,'RELACION_PROCESO_PROVEEDOR = "ADJUDICADO_A"',True)
    put(cells[i],'''RELACION_PROCESO_PROVEEDOR = "____"  # completa el nombre de la flecha
if RELACION_PROCESO_PROVEEDOR != "ADJUDICADO_A":
    raise ValueError("La flecha Proceso → Proveedor se llama ADJUDICADO_A.")
patron_estudiante=f"(p:Proceso)-[:{RELACION_PROCESO_PROVEEDOR}]->(v:Proveedor)"
print(patron_estudiante); print("Patrón correcto: ADJUDICADO_A expresa una adjudicación observada.")
''')
    i=find(cells,"### La alternativa que descartamos")
    put(cells[i],s(cells[i])+r'''

### Dos decisiones adicionales de modelado

- **Roles:** aquí `:Entidad` y `:Proveedor` son nodos separados para facilitar la lectura. Un modelo general podría usar `(:Organizacion {nit})` con roles. El grafo es una decisión de diseño, no algo que “sale solo” del CSV.
- **Propiedades en relaciones:** `precio_base` pertenece al `Proceso`; `valor_adjudicado` puede vivir en `ADJUDICADO_A`:

```cypher
(p:Proceso)-[:ADJUDICADO_A {valor_adjudicado:125000000}]->(v:Proveedor)
```

Lo comprobarás haciendo clic sobre nodos y relaciones en Aura.
''')

def contract(cells):
    i=find(cells,"# Ambas métricas usan NIT",True)
    put(cells[i],r'''# Ambas métricas usan NIT; el nombre es una etiqueta, no una segunda clave.
prov_ancla=hist_ancla.groupby("nit_proveedor")["id_proceso"].nunique().rename("procesos_con_entidad")
prov_global=hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas")
resultado_completo_pd=pd.concat([prov_ancla,prov_global],axis=1).loc[prov_ancla.index].reset_index()
resultado_completo_pd["procesos_con_entidad"]=resultado_completo_pd["procesos_con_entidad"].astype(int)
resultado_completo_pd["proveedor"]=resultado_completo_pd["nit_proveedor"].map(nombres_proveedor)
resultado_completo_pd=resultado_completo_pd.sort_values(["entidades_conectadas","procesos_con_entidad","nit_proveedor"],ascending=[False,False,True]).reset_index(drop=True)
esperado_pd=resultado_completo_pd.head(10).copy()  # top 10 es vista, no universo analítico
candidatas_hist=hist[hist["es_entidad_candidata_s05"]].copy(); candidatas_hist["conexiones_proveedor"]=candidatas_hist["nit_proveedor"].map(prov_global)
maximos_candidatas=candidatas_hist.groupby("nit_entidad")["conexiones_proveedor"].max(); MEDIANA_H2R=float(maximos_candidatas.median())
if "mediana_maximo_conectadas_por_nit" in manifest: assert MEDIANA_H2R==float(manifest["mediana_maximo_conectadas_por_nit"]),"La referencia por NIT no coincide."
proveedor_h2r=resultado_completo_pd.iloc[0].copy(); maximo_h2r=int(proveedor_h2r["entidades_conectadas"])
if uso_respaldo_s06: desenlace_h2r_pd="no evaluable con mi ancla"
elif maximo_h2r>MEDIANA_H2R: desenlace_h2r_pd="conexión más fuerte que la mediana de las candidatas de S5"
else: desenlace_h2r_pd="conexión igual o menor que la mediana de las candidatas de S5"
print("Entidades de referencia:",len(maximos_candidatas)); print("Mediana de referencia (candidatas S5):",MEDIANA_H2R)
print("Proveedor que determina H2-R:",proveedor_h2r["nit_proveedor"],"| máximo:",maximo_h2r); print("Desenlace H2-R (pandas):",desenlace_h2r_pd)
if uso_respaldo_s06: print("Comparación descriptiva del respaldo:",maximo_h2r,">",MEDIANA_H2R,"=",maximo_h2r>MEDIANA_H2R)
esperado_pd
''')

def graph_props(cells):
    i=find(cells,"cols = [",True); t=s(cells[i])
    t=t.replace('"nombre_proceso", "descripcion", "precio_base", "modalidad", "proveedor",','"nombre_proceso", "descripcion", "precio_base", "valor_adjudicado", "modalidad", "proveedor",')
    t=t.replace("    p.valor = fila.precio_base,","    p.precio_base = fila.precio_base,").replace("MERGE (p)-[:ADJUDICADO_A]->(v)","MERGE (p)-[a:ADJUDICADO_A]->(v)\nSET a.valor_adjudicado = fila.valor_adjudicado")
    put(cells[i],t)
    for c in cells:
        if "p.valor AS precio_base" in s(c): put(c,s(c).replace("p.valor AS precio_base","p.precio_base AS precio_base").replace("ORDER BY entidad, valor DESC","ORDER BY entidad, precio_base DESC"))

def graphlab():
    return [
    md(f'''---
## 5. Graph Lab — mirar, tocar y entender el grafo

<!-- {MARKER} -->
Antes de H2-R, **vas a ver el grafo real en Aura Query**. La meta no es una imagen bonita: debes identificar el hub, seguir flechas, revisar propiedades y comprobar el mismo resultado en Table.

**Tutorial visual:** [Graph Lab S06 — Aura Query paso a paso ↗]({GRAPH_TUTORIAL})
'''),
    code(f"tutorial('{GRAPH_TUTORIAL}', alto=820)",True,"Abrir Graph Lab visual"),
    code(r'''consulta_graph_basico="""
MATCH (e:Entidad)-[pub:PUBLICA]->(p:Proceso)-[adj:ADJUDICADO_A]->(v:Proveedor)
RETURN e,pub,p,adj,v
LIMIT 20
"""
print("Copia en AuraDB → Query:\n"); print(consulta_graph_basico)
'''),
    md(r'''### Tu primera lectura en Graph

En AuraDB → **Query** ejecuta la consulta y:

1. cambia a **Graph**; 2. usa **Fit to screen**; 3. arrastra nodos para separar ramas; 4. haz clic en `Entidad`, `Proceso` y `Proveedor`; 5. haz clic en `PUBLICA` y `ADJUDICADO_A`; 6. revisa las propiedades; 7. abre **Table** y vuelve a **Graph**.

Debes poder narrar: “esta Entidad llega a este Proveedor pasando por este Proceso”. Si solo ves tabla, devuelve nodos/relaciones/caminos, no únicamente strings y conteos.
'''),
    md(r'''### Grado ≠ entidades conectadas

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
'''),
    code(r'''grado_rel=hist.groupby("nit_proveedor")["id_proceso"].nunique().rename("grado_adjudicaciones")
entidades_2saltos=hist.groupby("nit_proveedor")["nit_entidad"].nunique().rename("entidades_conectadas")
grado_df=pd.concat([grado_rel,entidades_2saltos],axis=1).reset_index(); grado_df["proveedor"]=grado_df["nit_proveedor"].map(nombres_proveedor)
grado_df=grado_df.sort_values(["entidades_conectadas","grado_adjudicaciones","nit_proveedor"],ascending=[False,False,True]).head(10).reset_index(drop=True)
grado_df[["nit_proveedor","proveedor","grado_adjudicaciones","entidades_conectadas"]]
'''),
    code(r'''consulta_wow_global="""
MATCH (v:Proveedor)<-[:ADJUDICADO_A]-(p:Proceso)<-[:PUBLICA]-(e:Entidad)
WITH v,count(DISTINCT e) AS entidades,count(DISTINCT p) AS grado_adjudicaciones
ORDER BY entidades DESC,grado_adjudicaciones DESC,v.nit ASC LIMIT 1
MATCH camino=(e:Entidad)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)
RETURN camino LIMIT 40
"""
print("WOW 1 — proveedor-hub global. Ejecuta en Aura Query:\n"); print(consulta_wow_global)
'''),
    md(r'''### WOW 1 — la estrella contractual

En **Graph** identifica el Proveedor central, los Procesos del primer anillo y las Entidades del segundo. Haz clic en el hub para confirmar NIT/nombre; selecciona `ADJUDICADO_A` y revisa `valor_adjudicado`; selecciona Proceso y contrasta `precio_base`. Arrastra el hub al centro, usa Fit y luego abre **Table**.

**WOW correcto:** varios caminos comparten un actor. **WOW incorrecto:** “el nodo central es sospechoso”. El layout no codifica riesgo ni causalidad.
'''),
    code(r'''nit_literal=str(nit_deseado).replace('"','\\"')
consulta_wow_ancla=f"""
MATCH (ancla:Entidad {{nit:\"{nit_literal}\"}})-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v:Proveedor)
WITH ancla,v,count(*) AS procesos_ancla ORDER BY procesos_ancla DESC,v.nit ASC LIMIT 1
MATCH camino=(ancla)-[:PUBLICA]->(:Proceso)-[:ADJUDICADO_A]->(v)<-[:ADJUDICADO_A]-(:Proceso)<-[:PUBLICA]-(otra:Entidad)
WHERE otra.nit <> ancla.nit
RETURN camino LIMIT 30
"""
print("WOW 2 — desde tu ancla hacia otras entidades:\n"); print(consulta_wow_ancla)
'''),
    md(r'''### WOW 2 — lee un camino completo

Busca `Entidad ancla → Proceso → Proveedor ← Proceso ← otra Entidad`. Recorre un camino nodo por nodo y confirma que los extremos tienen NIT distintos y que el puente es el mismo NIT de proveedor.

**Sí demuestra:** esos registros comparten un proveedor. **No demuestra:** coordinación, colusión, favorecimiento, causalidad o irregularidad. Cuando puedas explicar el dibujo sin mirar Cypher, estás listo para H2-R.
''')]

def move(cells):
    h=find(cells,"## 4. Contrato de resultado: primero pandas"); block=cells[h:h+4]
    if len(block)!=4 or "# Ambas métricas" not in s(block[1]): raise ValueError("Cambió estructura contrato S06")
    del cells[h:h+4]
    i=find(cells,"## 5. Tutorial visual — AuraDB"); put(cells[i],s(cells[i]).replace("## 5. Tutorial visual — AuraDB","## 4. AuraDB — del modelo al motor"))
    i=find(cells,"## 6. Identidad y carga idempotente"); put(cells[i],s(cells[i]).replace("## 6. Identidad y carga idempotente","## 4.1 Identidad y carga idempotente"))
    d=find(cells,"## 7. La consulta que justifica Neo4j"); put(block[0],s(block[0]).replace("## 4. Contrato de resultado: primero pandas","## 6. Contrato de resultado: ahora sí, primero pandas"))
    cells[d:d]=graphlab()+block

def delivery(cells):
    i=find(cells,"### Comprueba tu entrega")
    put(cells[i],s(cells[i])+'''\n### Última milla — deja evidencia en el repositorio privado\n\n1. Crea o abre `hitos/s06/`. 2. Sube `hito_s06_ficha_relacional.md`. 3. Sube `s06_contexto_procesos.jsonl`. 4. Crea un commit descriptivo. 5. Entrega la **URL exacta de ese commit**, no solo la del repositorio.\n\nConfirma en la ficha: origen real del ancla, motor real, proveedor H2-R, proveedor explorado, máximo, mediana, consulta propia y límite interpretativo.\n''')

def enhance_cells(cells):
    if any(MARKER in s(c) for c in cells): return cells
    anchor(cells); concepts(cells); contract(cells); graph_props(cells); move(cells); delivery(cells); return cells

def enhance_checklist(cells):
    p=ROOT/"assets/tutoriales/s06-laboratorio-guiado.html"
    if not p.is_file(): return
    html=p.read_text(encoding="utf-8"); data=json.loads(html.split("const DATA = ",1)[1].split(";\nconst DATA2",1)[0]); pasos=data[0]["pasos"]
    for paso in pasos:
        if paso.get("id")=="patron":
            paso["tipo"]="decide"
            paso["titulo"]="Completa el patrón contractual"
            paso["explicacion"]="El ID del proceso identifica un nodo; el tipo de relación identifica la flecha."
            paso["instruccion"]="Completa el hueco con ADJUDICADO_A y ejecuta la validación antes de continuar."
            paso["evidencia"]="Patrón correcto: ADJUDICADO_A expresa una adjudicación observada."
    ids={"ancla","graph","grado","wow","wow2","entrega"}; pasos[:]=[x for x in pasos if x.get("id") not in ids]
    def cn(x):
        h=[i for i,c in enumerate(cells,1) if x in s(c)]
        if len(h)!=1: raise ValueError(f"Checklist Graph Lab ambiguo {x}: {h}")
        return f"celda {h[0]}"
    extra=[
      dict(id="ancla",tipo="decide",titulo="Declara el origen del ancla",celda=cn("USAR_MI_ANCLA_S5 = False"),explicacion="Distingues continuidad real de respaldo.",instruccion="Usa tu JSON de S5 si lo conservaste; si no, declara respaldo.",evidencia="Origen del ancla explícito."),
      dict(id="graph",tipo="externo",titulo="Abre el resultado como grafo",celda=cn("consulta_graph_basico="),explicacion="Graph y Table son dos lecturas del mismo resultado.",instruccion="Ejecuta en Aura, usa Graph/Fit y revisa propiedades de nodos y relaciones.",evidencia="Explicas Entidad → Proceso → Proveedor."),
      dict(id="grado",tipo="entiende",titulo="Distingue grado y conectividad",celda=cn("grado_df="),explicacion="Grado alto no implica muchas entidades.",instruccion="Compara grado_adjudicaciones y entidades_conectadas.",evidencia="Top 10 con ambas métricas."),
      dict(id="wow",tipo="externo",titulo="WOW 1: proveedor-hub",celda=cn("consulta_wow_global="),explicacion="Lees una estrella sin convertir layout en riesgo.",instruccion="Centra hub, separa ramas, revisa propiedades y contrasta Table.",evidencia="Grafo estrella explicado por anillos."),
      dict(id="wow2",tipo="externo",titulo="WOW 2: desde el ancla",celda=cn("consulta_wow_ancla="),explicacion="Lees un camino de cuatro relaciones.",instruccion="Confirma NIT/ID en un camino completo antes de interpretar.",evidencia="Lees ancla → Proceso → Proveedor ← Proceso ← otra Entidad."),
      dict(id="entrega",tipo="decide",titulo="Cierra con un commit verificable",celda=cn("Última milla — deja evidencia"),explicacion="La evidencia queda versionada.",instruccion="Sube ficha+JSONL a hitos/s06 y entrega URL exacta del commit.",evidencia="Commit privado con ambos archivos."),]
    k=next((i+1 for i,x in enumerate(pasos) if x.get("id")=="cargar"),1); pasos[k:k]=[extra[0]]
    k=next((i+1 for i,x in enumerate(pasos) if x.get("id")=="repetir"),len(pasos)); pasos[k:k]=extra[1:5]; pasos.append(extra[5])
    new="const DATA = "+json.dumps(data,ensure_ascii=False,indent=2)+";\nconst DATA2"
    html=re.sub(r"const DATA = \[.*?;\nconst DATA2",lambda _:new,html,count=1,flags=re.S)
    html=html.replace('"s06lab:nit-v2:" + id','"s06lab:graph-v3:" + id').replace('"s06lab:" + id','"s06lab:graph-v3:" + id')
    p.write_text(html,encoding="utf-8")
