#!/usr/bin/env python3
"""Valida S06 sin credenciales de Aura y sin imponer una UI antigua."""
from __future__ import annotations
import ast, base64, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0, str(ROOT))
from utils.notebook_checks import check_question_widget_renders

NB = ROOT / "Cuadernos" / "6_Neo4j_Contexto_Relacional.ipynb"
DATA = ROOT / "Datos" / "s06_contexto_relacional.csv"
MANIFEST = ROOT / "Datos" / "s06_contexto_relacional_manifest.json"
AURA = ROOT / "assets" / "tutoriales" / "neo4j-aura-s06-paso-a-paso.html"
GRAPH = ROOT / "assets" / "tutoriales" / "neo4j-graph-lab-s06.html"
CHECKLIST = ROOT / "assets" / "tutoriales" / "s06-laboratorio-guiado.html"
GEN = ROOT / "utils" / "build_session6_notebook.py"
DATA_GEN = ROOT / "utils" / "build_session6_graph_data.py"


def src(c):
    v=c.get("source",""); return "".join(v) if isinstance(v,list) else str(v)


def main():
    errors=[]
    for p in (NB,DATA,MANIFEST,AURA,GRAPH,CHECKLIST,GEN,DATA_GEN):
        if not p.is_file(): errors.append(f"Falta {p.relative_to(ROOT)}")
    if errors: raise SystemExit("\n".join(errors))
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    expected={"candidatos_s05":77,"historicos_adjudicados":2032,"entidades_candidatas_con_historial_por_nit":28,"mediana_maximo_conectadas_por_nit":21}
    for k,v in expected.items():
        if manifest.get(k)!=v: errors.append(f"Manifest {k}: esperado {v}, observado {manifest.get(k)}")
    if manifest.get("proveedores_compartidos_entre_entidades",0)<=0: errors.append("Falta el patrón central de proveedores compartidos")
    if not manifest.get("ancla_pedagogica",{}).get("id_proceso"): errors.append("Falta ancla pedagógica")
    size_mb=DATA.stat().st_size/1024/1024
    if size_mb>60: errors.append(f"Extracto demasiado grande: {size_mb:.1f} MB")

    nb=json.loads(NB.read_text(encoding="utf-8")); cells=nb.get("cells",[]); text="\n".join(src(c) for c in cells)
    if nb.get("nbformat")!=4: errors.append("nbformat debe ser 4")
    if len(cells)<40: errors.append(f"S06 tiene pocas celdas: {len(cells)}")
    if any(not src(c).strip() for c in cells): errors.append("Hay celdas vacías")

    from utils.build_session6_novice import build_novice_cells
    if cells!=build_novice_cells(): errors.append("Generador final y notebook S06 desincronizados")

    questions=[]
    for i,c in enumerate(cells,1):
        if c["cell_type"]=="code":
            try: ast.parse(src(c))
            except SyntaxError as exc: errors.append(f"Sintaxis inválida en celda {i}: {exc}")
        m=re.search(r'^pregunta_codificada\("([^\"]+)"\)',src(c),re.M)
        if m:
            q=json.loads(base64.b64decode(m.group(1))); questions.append(q)
            if len(q.get("opciones",[]))!=4 or len(q.get("retro",[]))!=4: errors.append(f"Pregunta {q.get('numero')} incompleta")
    if questions and [q["numero"] for q in questions] != list(range(1,len(questions)+1)): errors.append("Numeración de autoevaluaciones inconsistente")

    gen=GEN.read_text(encoding="utf-8")
    m=re.search(r"INTERACTIVITY = r'''(.*?)'''",gen,re.S)
    if not m: errors.append("No se encontró INTERACTIVITY")
    else: errors.extend(check_question_widget_renders(m.group(1)))

    for item in [
        "S06-NOVATOS-V3","esta no es una clase de Python","Mini curso de Cypher en Aura Query",
        "Consulta 1 — ver nodos Entidad","Consulta 4 — qué es el grado","Consulta 5 — qué es un hub",
        "Consulta 6 — responder la pregunta profesional","Profundización — comparar conectividad",
        "Consulta guiada — contar procesos del par entidad–proveedor","AUTOR_ALIAS","s06_contexto_procesos.jsonl"
    ]:
        if item not in text: errors.append(f"Falta contenido principal {item!r}")
    for bad in [
        "WOW 1","WOW 2",'RELACION_PROCESO_PROVEEDOR = "____"','OPERADOR_EXCLUSION = "____"',
        'input("Número de proveedor','input("Con tus números','input("Justifica por qué Proceso',
        "Escribe tu consulta entre las comillas triples","EJERCICIO S06-CONSULTA","EJERCICIO S06-EXCLUIR"
    ]:
        if bad in text: errors.append(f"Persistió interacción no apta para novatos: {bad!r}")

    # Generadores Python que crean Cypher o seleccionan ejemplos deben estar plegados.
    for needle in ["nit_literal = str(nit_deseado)", "query_demo_top =", "query_visual_demo =", "Cinco proveedores de ejemplo"]:
        hits=[c for c in cells if c["cell_type"]=="code" and needle in src(c)]
        if hits and any("hide-input" not in c.get("metadata",{}).get("tags",[]) for c in hits):
            errors.append(f"Python de infraestructura visible: {needle!r}")

    aura=AURA.read_text(encoding="utf-8"); graph=GRAPH.read_text(encoding="utf-8"); checklist=CHECKLIST.read_text(encoding="utf-8")
    for item in ["AuraDB desde cero","RETURN 1 AS conexion","Connection URI","User name","Password"]:
        if item not in aura: errors.append(f"Tutorial Aura incompleto: {item}")
    for item in ["Mini curso visual de Cypher","¿Qué es el grado?","¿Qué es un hub?","proveedor compartido"]:
        if item not in graph: errors.append(f"Mini curso visual incompleto: {item}")
    for item in ["Checklist para no perderse","Mide el grado","Responde la pregunta","Entrega"]:
        if item not in checklist: errors.append(f"Checklist incompleto: {item}")

    secret_patterns=[r"neo4j\+s://[A-Za-z0-9.-]+\.databases\.neo4j\.io",r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",r"github_pat_[A-Za-z0-9_]{20,}"]
    for pattern in secret_patterns:
        if re.search(pattern,text): errors.append("Posible secreto o endpoint personal publicado")

    if errors:
        print("Validación S06 fallida:")
        for e in errors: print("[ERROR]",e)
        raise SystemExit(1)
    print(f"[OK] S06 válida: {len(cells)} celdas; datos {size_mb:.1f} MB")
    print("[OK] Notebook, mini curso, checklist y tutorial Aura sincronizados")
    print("[OK] Sin retos a ciegas; Python de infraestructura plegado; Cypher visible")
    print("[INFO] CI no autentica Aura; esa prueba sigue siendo manual con credenciales propias")

if __name__=="__main__": main()
