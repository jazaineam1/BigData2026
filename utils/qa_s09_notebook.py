#!/usr/bin/env python3
"""QA sin red del laboratorio S09: fuente, sintaxis y recorrido operacional simulado."""
import hashlib
import json
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
from build_session9_notebook import build_notebook

nb = json.loads((ROOT/"Cuadernos/9_Bases_Vectoriales_Busqueda_Semantica.ipynb").read_text(encoding="utf-8"))
expected = build_notebook()
assert nb == expected, "El notebook publicado no coincide con el generador de fuente."
assert len(nb["cells"]) >= 25, "El recorrido quedó incompleto."

def source_containing(fragment):
    matches = ["".join(c["source"]) for c in nb["cells"] if fragment in "".join(c["source"])]
    assert len(matches) == 1, f"No se identificó una sola celda: {fragment!r}; halladas {len(matches)}"
    return matches[0]

for i,c in enumerate(nb["cells"],1):
    if c["cell_type"] != "code":
        continue
    text = "".join(c["source"])
    py = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith(("%","!")))
    if py:
        compile(py, f"notebook_s09_{i}.py", "exec")
full = "\n".join("".join(c["source"]) for c in nb["cells"])
assert "LMSBridge" not in full and "CODIGO_LAB" not in full
assert "COLUMNA_ID" in full and "MODE_DATOS" in full
assert "def buscar_lexical" in full and "def buscar_semantico_local" in full
assert "def rrf_fusion" in full and "def buscar_s09" in full
assert "def comparar_s09" in full and "def exportar_s09" in full
assert "USAR_ATLAS = False" in full
assert "LIMITE = 6000" in full
assert "SECOP ampliado (6000)" in full
assert "sugerir_correcciones" in full and "ortografia_ui" in full
assert "rapidfuzz" in full and "multilingual-e5-small" in full

# Simulación sin E5 remoto ni cuentas: comprueba que los motores usan el mismo
# corpus, ID y metadatos, y producen resultados y expediente reproducibles.
import numpy as np
import pandas as pd

class ModeloE5Ficticio:
    """Solo sustituto determinista para QA, no resultados de E5 real."""
    def encode(self, textos, normalize_embeddings=True, **kwargs):
        filas = []
        for txt in textos:
            v = np.zeros(384, dtype=float)
            for token in re.findall(r"[a-záéíóúüñ0-9]+", str(txt).lower()):
                if token in ("passage", "query"):
                    continue
                j = int(hashlib.sha256(token.encode()).hexdigest()[:8],16) % 384
                v[j] += 1
            norm = np.linalg.norm(v)
            filas.append(v / norm if normalize_embeddings and norm > 0 else v)
        return np.stack(filas)

ns = {"__name__":"__main__"}
load = source_containing("#@title 1. Selecciona de dónde salen tus datos")
load = load.replace('MODE_DATOS = "SECOP del curso"', 'MODE_DATOS = "Ejemplo sintético de respaldo"')
exec(compile(load,"synthetic_data.py","exec"),ns)
exec(compile(source_containing("#@title 2. Identifica y configura"),"mapping.py","exec"),ns)
assert len(ns["corpus"]) == 6
assert ns["corpus"]["id_proceso"].is_unique
assert ns["corpus"]["texto_busqueda"].str.len().min() >= 6

exec(compile(source_containing("#@title 3. Construye el índice lexical"),"bm25.py","exec"),ns)
assert not ns["buscar_lexical"]("aeronaves militares",5).empty
assert ns["tokens"]("Reparación") == ["reparacion"], "Debe normalizar acentos."
corregida,cambios=ns["sugerir_correcciones"]("aeronavess")
assert cambios.get("aeronavess") == "aeronaves", f"Sugerencia real no detectada: {cambios}"
assert ns["sugerir_correcciones"]("CO1.REQ.123")[1] == {}, "No debe corregir IDs/códigos."
ns["modelo"] = ModeloE5Ficticio()
ns["embeddings"] = ns["modelo"].encode(["passage: " + t for t in ns["corpus"]["texto_busqueda"]])
ns["MODEL_NAME"] = "fake-e5-for-smoke"
exec(compile(source_containing("#@title 5. Recupera por significado"),"semantic.py","exec"),ns)
sem = ns["buscar_semantico_local"]("aviones militares",5)
assert len(sem) == 5 and "score_semantico" in sem.columns
exec(compile(source_containing("#@title 6. Fusiona BM25"),"rrf.py","exec"),ns)
hybrid=ns["rrf_fusion"](ns["buscar_lexical"]("aviones militares",5),sem,60)
assert not hybrid.empty and "fuentes" in hybrid.columns

# UI headless: verifica que los controles se crean, los tres rankings se buscan
# y la descarga no solicita token ni registra progreso oficial.
with tempfile.TemporaryDirectory() as tmp:
    import os
    cwd=os.getcwd()
    try:
        os.chdir(tmp)
        exec(compile(source_containing("#@title 7. CONSOLA DE BÚSQUEDA"),"ui.py","exec"),ns)
        assert ns["estado_s09"]["consulta"]
        assert set(ns["estado_s09"]["rankings"]) == {"BM25","E5 semántico","RRF híbrido"}
        assert ns["precision_mia"] is None
        for i,control in enumerate(ns["juicios_controles"].values()):
            control.value = i % 3 != 0
        ns["comparar_s09"](None)
        assert ns["precision_mia"] is not None
        ns["decision_ui"].value="RRF híbrido"
        ns["alternativa_ui"].value="BM25"
        ns["exportar_s09"](None)
        evidence=Path("s09_evidencia_semantica.json")
        assert evidence.exists(), "No se descargó el expediente local."
        data=json.loads(evidence.read_text(encoding="utf-8"))
        assert data["modelo_embedding"] == ns["MODEL_NAME"]
        assert data["precision_at_k"] is not None
        assert data["origen"]["modo"] == "Ejemplo sintético de respaldo"
        assert data["falso_positivo"] is not None
        assert data["decision"] != data["alternativa_descartada"]
        assert data["corpus"]["sha256"]
        assert data["modo_ortografia"] == "sugerir"
        assert data["consulta_empleada"] == data["consulta"]
        assert data["sugerencias_ortograficas"] == {} or isinstance(data["sugerencias_ortograficas"], dict)
        # Aplicar correcciones debe cambiar la consulta usada solo si se solicita.
        ns["consulta_ui"].value = "aeronavess"
        ns["ortografia_ui"].value = "aplicar"
        ns["buscar_s09"]()
        assert ns["estado_s09"]["consulta"] == "aeronavess"
        assert ns["estado_s09"]["consulta_usada"] == "aeronaves"
        ns["ortografia_ui"].value = "sin"
        ns["buscar_s09"]()
        assert ns["estado_s09"]["consulta_usada"] == "aeronavess"
    finally:
        os.chdir(cwd)

# Ensayo de 6.000 filas: no duplicar IDs, mantener la trazabilidad y los filtros.
with tempfile.TemporaryDirectory() as tmp:
    demo=Path(tmp)/"6000.csv"
    df=pd.DataFrame({
        "radicado":[f"SECOP-{j:05d}" for j in range(6000)],
        "asunto":[f"Contrato de servicios {j}" for j in range(6000)],
        "contenido":[f"Servicio operativo y mantenimiento de equipo {j%50}" for j in range(6000)],
        "dependencia":["Operaciones" if j%2 else "Tecnología" for j in range(6000)],
        "enlace":["" for _ in range(6000)]
    })
    df.to_csv(demo,index=False)
    load_file=source_containing("#@title 1. Selecciona de dónde salen tus datos")
    load_file=load_file.replace('MODE_DATOS = "SECOP ampliado (6000)"','MODE_DATOS = "Subir CSV desde computador"')
    load_file=load_file.replace('ARCHIVO_CSV = ""',f"ARCHIVO_CSV = {str(demo)!r}")
    sandbox={"__name__":"__main__"}
    exec(compile(load_file,"six_thousand_csv.py","exec"),sandbox)
    mapping=source_containing("#@title 2. Identifica y configura")
    for key,val in {"COLUMNA_ID":"radicado","COLUMNA_TITULO":"asunto","COLUMNA_TEXTO":"contenido",
                    "COLUMNA_GRUPO":"dependencia","COLUMNA_ENLACE":"enlace"}.items():
        mapping=re.sub(r"^"+key+r" = [^\n]+",f'{key} = "{val}"',mapping,flags=re.M)
    exec(compile(mapping,"six_thousand_mapping.py","exec"),sandbox)
    assert len(sandbox["corpus"]) == 6000
    assert sandbox["corpus"]["id_proceso"].nunique() == 6000

# Verifica transferencia: columnas de un CSV distinto se mapean sin reescribir
# los motores ni depender de un archivo SECOP.
with tempfile.TemporaryDirectory() as tmp:
    demo=Path(tmp)/"tickets.csv"
    pd.DataFrame([
        {"radicado":"A-1","asunto":"Red inestable","contenido":"Se cae la conexión del edificio","dependencia":"Tecnología","enlace":""},
        {"radicado":"A-2","asunto":"Error de facturación","contenido":"La factura llegó duplicada","dependencia":"Finanzas","enlace":""},
        {"radicado":"A-3","asunto":"Sin acceso al portal","contenido":"No abre el formulario de solicitudes","dependencia":"Tecnología","enlace":""}
    ]).to_csv(demo,index=False)
    load_file=source_containing("#@title 1. Selecciona de dónde salen tus datos")
    load_file=load_file.replace('MODE_DATOS = "SECOP del curso"','MODE_DATOS = "Subir CSV desde computador"')
    load_file=load_file.replace('ARCHIVO_CSV = ""',f"ARCHIVO_CSV = {str(demo)!r}")
    other={"__name__":"__main__"}
    exec(compile(load_file,"new_csv.py","exec"),other)
    mapping=source_containing("#@title 2. Identifica y configura")
    for k,val in {"COLUMNA_ID":"radicado","COLUMNA_TITULO":"asunto","COLUMNA_TEXTO":"contenido",
                  "COLUMNA_GRUPO":"dependencia","COLUMNA_ENLACE":"enlace"}.items():
        mapping=re.sub(r"^"+k+r" = [^\n]+",f'{k} = "{val}"',mapping,flags=re.M)
    exec(compile(mapping,"other_mapping.py","exec"),other)
    assert other["corpus"]["id_proceso"].tolist() == ["A-1","A-2","A-3"]
    assert other["corpus"].iloc[0]["entidad"] == "Tecnología"
print("S09 QA OK: celdas sincronizadas, sintaxis, búsqueda, evaluación, exportación y CSV propio.")