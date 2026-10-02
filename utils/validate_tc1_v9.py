#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Validador estructural del TC1 V9 (S08): comprueba estructura y hechos verificables.

- El cuaderno versionado es exactamente el que produce el generador.
- La infraestructura incrustada en el cuaderno es la de utils/ (SHA-256).
- Cada etapa tiene su ficha completa y cada salida importante su lectura de cuatro rótulos.
- Ninguna lista trae preseleccionada una opción; hay tres huecos de código.
- El checklist cita evidencias que el código realmente imprime y su JS es válido.
- El LMS no califica el TC1 y la ventana de cada pareja pasó el control de datos.
'''
from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "utils"))
sys.path.insert(0, str(ROOT))
import tc1_contrato as C  # noqa: E402

errores = []


def falla(cond, msg):
    if not cond:
        errores.append(msg)


def leer(rel):
    p = ROOT / rel
    if not p.exists():
        errores.append(f"falta {rel}")
        return ""
    return p.read_bytes().decode("utf-8")


# ── Generador y cuaderno ──────────────────────────────────────────────────────
import build_taller_control_1 as B  # noqa: E402

nb_txt = leer("Cuadernos/Taller_Control_1.ipynb")
falla(nb_txt == B.serializar(B.notebook()), "el cuaderno no coincide con el generador: ejecuta utils/build_taller_control_1.py")
nb = json.loads(nb_txt) if nb_txt else {"cells": []}
fuentes = ["".join(c.get("source", [])) for c in nb["cells"]]
codigo = [f for f, c in zip(fuentes, nb["cells"]) if c["cell_type"] == "code"]
todo = "\n".join(fuentes)
falla(not any(c.get("outputs") for c in nb["cells"] if c["cell_type"] == "code"), "el cuaderno trae salidas preejecutadas")
falla(all(c.get("id") for c in nb["cells"]), "hay celdas sin id (nbformat 4.5)")
falla("colab.research.google.com" in fuentes[0], "la primera celda debe abrir el cuaderno en Colab")
falla("OBJETIVO DEL TC1" in fuentes[1] and C.CHECKLIST_URL in fuentes[1], "la primera pantalla debe traer el objetivo y el enlace al checklist")
falla(C.VERSION_VISIBLE in fuentes[1], "la versión visible no está en la primera pantalla")

infra = next((f for f in codigo if f.startswith("#@title Preparar el entorno")), "")
for nombre in B.MODULOS:
    fuente = (ROOT / "utils" / nombre).read_bytes().replace(b"\r\n", b"\n")
    falla(hashlib.sha256(fuente).hexdigest() in infra, f"{nombre}: el cuaderno no incrusta la versión actual")
    falla(b'"""' not in fuente, f"{nombre}: usa triple comilla doble (rompe el generador)")
    falla(b"\r\n" not in (ROOT / "utils" / nombre).read_bytes(), f"{nombre}: tiene saltos CRLF")
m = re.search(r"'tc1_contrato.py': \('([0-9a-f]{64})',(.*?)\),", infra, re.S)
if m:
    blob = "".join(re.findall(r"'([A-Za-z0-9+/=]+)'", m.group(2)))
    falla(hashlib.sha256(zlib.decompress(base64.b64decode(blob))).hexdigest() == m.group(1),
          "el módulo incrustado no coincide con su SHA-256")

posiciones = [todo.find(f"# {e} · {C.STAGE_NOMBRE[e]}") for e in C.STAGE_MAX]
falla(all(p >= 0 for p in posiciones) and posiciones == sorted(posiciones), "las seis etapas deben aparecer en orden E1→E6")
for rotulo in ("Objetivo", "Pregunta", "Dónde trabajas", "Ya está provisto", "Tú haces", "Checkpoint para avanzar",
               "Evidencia que queda", "Puntos"):
    falla(todo.count(f"| **{rotulo}** |") == 6, f"el rótulo «{rotulo}» no está en las seis fichas")
for etapa, lista in C.CHECKPOINTS.items():
    for texto in lista:
        falla(texto in todo, f"{etapa}: el checkpoint «{texto[:50]}…» no aparece en el cuaderno")
lecturas = [f for f in fuentes if f.startswith("**Cómo se lee.**")]
falla(len(lecturas) >= 8, f"se esperaban al menos 8 lecturas de cuatro rótulos; hay {len(lecturas)}")
for f in lecturas:
    falla(f.index("Cómo se lee") < f.index("Qué nos dice") < f.index("Qué NO permite concluir todavía") < f.index("Qué error común"),
          "una lectura no usa los cuatro rótulos en orden")
listas = [ln for f in codigo for ln in f.splitlines() if "#@param [" in ln and not ln.startswith("GUARDAR_AVANCE")]
falla(listas and all(f'= "{C.SIN_SELECCION}" #@param' in ln for ln in listas), "alguna lista trae una opción preseleccionada")
falla(sum(f.count("____") for f in codigo) == 3, "debe haber exactamente tres huecos de código (E1.3, E5.3a, E5.3b)")
for prohibido in ("APP_TOKEN", "X-App-Token", "networkx", "consulta_cassandra_simulada", "nx.DiGraph"):
    falla(prohibido not in todo, f"el cuaderno todavía contiene {prohibido}")
falla(todo.count("SAL DE COLAB") >= 4, "Atlas, Astra y Aura deben anunciarse con «SAL DE COLAB» (E2, E3, E4, E5)")
filas_rubrica = re.findall(r"^\| (E\d\.\d) \| .*? \| (\d+) \|", todo, re.M)
falla(len(filas_rubrica) == len(C.RUBRICA) and sum(int(p) for _, p in filas_rubrica) == 100, "la rúbrica del cuaderno no suma 100")
for nombre in C.CAPTURAS.values():
    falla(nombre in todo, f"el cuaderno no pide {nombre}")

# Claridad: qué hacer en cada celda, qué trae cada fuente y qué demuestra cada huella.
ACCIONES = ("EJECUTA", "ELIGE", "COMPLETA", "PEGA", "CAPTURA")
for f in codigo:
    titulo = f.splitlines()[0]
    falla(any(f" {a} " in titulo for a in ACCIONES), f"la celda «{titulo[:60]}» no dice qué hacer (EJECUTA, ELIGE, COMPLETA, PEGA o CAPTURA)")
    falla(("____" in f) == (" COMPLETA " in titulo), f"«{titulo[:60]}»: COMPLETA debe marcar exactamente las celdas con hueco")
    falla(("pega aquí" in f) == (" PEGA " in titulo), f"«{titulo[:60]}»: PEGA debe marcar exactamente las celdas donde se pega")
falla("Cómo leer cada celda" in todo, "falta la leyenda de acciones (Cómo leer cada celda)")
for frase in ("proceso de contratación", "contrato electrónico", "procesos.id_del_portafolio = contratos.proceso_de_compra",
              "Función usada: `hashlib.sha256`", "huella de entrega", "Función usada: `pd.read_parquet`",
              "El problema de Laura", "¿Qué resolvimos para Laura, y qué no?", "Variables del taller", "asigna el docente"):
    falla(frase in todo, f"el cuaderno no explica «{frase}»")
for col in C.SELECT_PROCESOS + C.SELECT_CONTRATOS:
    falla(f"`{col}`" in todo, f"el diccionario no describe la columna {col}")
falla(not re.search(r"(?<![\w.])[TSXVC]\.[a-z_]+", "\n".join(f for f in codigo if not f.startswith("#@title Preparar"))),
      "el cuaderno usa alias de una letra (T., S., X.) en vez de taller, secop, plataformas")

# ── Checklist ─────────────────────────────────────────────────────────────────
html = leer("assets/tutoriales/s08-secoppipeline.html")
for etapa in ("h0", "h1", "h2", "h3", "h4", "h5", "h6"):
    falla(f'id="{etapa}"' in html, f"el checklist no tiene la sección {etapa}")
falla(html.count('data-paso="') >= 18, "el checklist debe tener un paso por acción (≥18)")
falla(html.count('<span class="ev">') >= 18, "cada paso del checklist debe citar su evidencia")
falla("<textarea" not in html and 'type="text"' not in html, "el checklist no puede pedir texto libre")
# Que cada evidencia citada sea texto que el cuaderno realmente imprime se comprueba ejecutando:
# test_tc1_v9.py (CI) y test_tc1_v9_e2e.py (cuaderno completo con servicios reales).
scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
for s in scripts:
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
        fh.write(s)
    r = subprocess.run(["node", "--check", fh.name], capture_output=True, text=True)
    falla(r.returncode == 0, "JS del checklist inválido: " + r.stderr[:200])
    Path(fh.name).unlink(missing_ok=True)

# ── LMS, índice y datos ───────────────────────────────────────────────────────
edge = leer("infraestructura/lms/functions/bigdata-learning/index.ts")
falla('if(action==="submit_manifest"){return out(req,{error:' in edge and "TC1_FUERA_DEL_LMS" in edge,
      "el backend del LMS todavía acepta manifests del TC1 (y escribiría la nota)")
s08 = leer("lms/session-08.html")
falla("Este TC1 no se entrega en el LMS." in s08 and '<div style="display:none" aria-hidden="true">' in s08,
      "la página S08 del LMS debe decir que no se entrega allí y no mostrar el formulario")
index = leer("index.html")
tarjeta = index[index.find('data-session="8"'):index.find('data-session="9"')]
falla(all(x in tarjeta for x in ("Atlas", "Astra", "Aura", "Drive")), "la tarjeta S08 del índice no describe el TC1 V9")
# Una sola fecha de entrega en todas las superficies que ve el estudiante.
dia = C.FECHA_LIMITE.split(" de ")[0]
for nombre, texto in (("cuaderno", todo), ("checklist", html), ("LMS S08", s08)):
    falla(f"{dia} de octubre" in texto, f"{nombre}: no dice la fecha de entrega ({dia} de octubre)")
    otras = set(re.findall(r"\b(\d{1,2}) de octubre", texto)) - {dia}
    falla(not otras, f"{nombre}: menciona otra fecha de octubre ({', '.join(sorted(otras))})")
falla(f"antes del {dia} de octubre" in tarjeta, f"la tarjeta S08 del índice no dice «antes del {dia} de octubre»")
resumen = json.loads(leer("Datos/tc1_ventanas_resumen.json") or "{}")
ventanas = resumen.get("ventanas", {})
falla(set(ventanas) == set(C.VENTANAS), "el control de datos no cubre las 12 ventanas")
for p, v in ventanas.items():
    falla(v.get("pasa") is True and v.get("inicio") == C.VENTANAS[p][0][:10], f"{p}: la ventana no pasó el control de datos")
for f in ("P03_procesos.json.gz", "P03_contratos.json.gz", "P03_cqlsh_salida.txt", "P03_E5/05_neo4j_evidence.json"):
    falla((ROOT / "tests" / "fixtures" / "tc1" / f).exists(), f"falta el fixture tests/fixtures/tc1/{f}")

if errores:
    print("TC1 V9: FAIL")
    for e in errores:
        print(" -", e)
    sys.exit(1)
print("TC1 V9: OK")
print(f" - cuaderno = generador · {len(nb['cells'])} celdas · infraestructura incrustada con SHA-256")
print(" - 6 fichas de etapa completas, lecturas de cuatro rótulos, listas sin preselección, 3 huecos")
print(" - checklist con evidencias que el código imprime · LMS sin nota del TC1 · 12 ventanas con datos verificados")
