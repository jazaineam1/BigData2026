# -*- coding: utf-8 -*-
"""
utils/validate_session4_notebook.py
====================================
Valida el cuaderno de la sesion 4 antes de publicarlo.

Mismas comprobaciones que utils/validate_session3_notebook.py, sobre el
archivo de la sesion 4. Ver ese archivo para el porque de cada regla; no se
duplica la explicacion aqui.

Uso
---
    python utils/validate_session4_notebook.py
"""

import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(REPO, "Cuadernos", "4_Atlas_Cassandra_Laura.ipynb")
TOTAL_PREGUNTAS = 8


def lineas_indentadas_fuera_de_fence(fuente):
    dentro_fence = False
    problemas = []
    anterior = ""
    for n, linea in enumerate(fuente, 1):
        texto = linea.rstrip("\n")
        if texto.strip().startswith("```"):
            dentro_fence = not dentro_fence
            anterior = texto
            continue
        if dentro_fence or not texto.strip():
            anterior = texto
            continue
        if texto.startswith("    "):
            previa = anterior.strip()
            es_continuacion = (
                previa.startswith(("-", "*", "+"))
                or re.match(r"^\d+\.", previa)
                or previa.endswith(",")
                or previa.startswith("<")
                or texto.strip().startswith(("(", "—", "<"))
            )
            if not es_continuacion:
                problemas.append((n, texto[:80]))
        anterior = texto
    return problemas


def main():
    with open(NB, encoding="utf-8") as f:
        nb = json.load(f)
    celdas = nb["cells"]
    errores, avisos = [], []

    for i, c in enumerate(celdas):
        if c["cell_type"] != "markdown":
            continue
        for n, texto in lineas_indentadas_fuera_de_fence(c["source"]):
            errores.append(
                f"celda {i}, linea {n}: markdown indentado, se vera como bloque de "
                f"codigo -> {texto!r}"
            )

    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if re.search(r"correcta\s*=\s*\d", src):
            errores.append(f"celda {i}: la respuesta correcta es legible en el fuente")

    enunciados = sum(
        1 for c in celdas
        if c["cell_type"] == "markdown"
        and re.search(r"^#+ Pregunta \d+ de \d+", "".join(c["source"]), re.M)
    )
    verificadores = sum(
        1 for c in celdas if "pregunta-interactiva" in c["metadata"].get("tags", [])
    )
    if enunciados:
        errores.append(
            f"hay {enunciados} enunciados en markdown: la pregunta se veria duplicada en Colab"
        )
    if verificadores != TOTAL_PREGUNTAS:
        errores.append(f"hay {verificadores} preguntas y deberian ser {TOTAL_PREGUNTAS}")

    for i, c in enumerate(celdas):
        for bloque in re.findall(r'style="([^"]*)"', "".join(c["source"])):
            if "background" in bloque and "color:" not in bloque:
                avisos.append(
                    f"celda {i}: hay un estilo con fondo y sin color de texto; "
                    f"quedara ilegible en Colab con tema oscuro"
                )
                break

    for i, c in enumerate(celdas):
        for ch in "".join(c["source"]):
            if ord(ch) < 32 and ch not in "\n\t":
                errores.append(
                    f"celda {i}: contiene el caracter de control {ord(ch):#04x}; "
                    f"seguramente es un escape sin escapar y se comio texto"
                )
                break

    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if src.count("<details>") != src.count("</details>"):
            errores.append(
                f"celda {i}: <details> descuadrado; en Colab cada celda se dibuja "
                f"aparte, asi que no puede abrirse en una y cerrarse en otra"
            )

    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if not src.strip():
            errores.append(f"celda {i}: vacia")
        if c["cell_type"] == "code" and '"""' in src:
            errores.append(f"celda {i}: triple comilla doble en una celda de codigo")

    urls = sorted(set(re.findall(
        r"https://raw\.githubusercontent\.com/[^\s\"')]+", json.dumps(nb, ensure_ascii=False)
    )))

    texto_md = " ".join(
        "".join(c["source"]) for c in celdas if c["cell_type"] == "markdown"
    )
    if re.search(r"\b\d+\s*minutos?\b", texto_md):
        avisos.append("hay referencias a minutos en el texto del estudiante")

    # ── Especificas de la sesion 4 ──────────────────────────────────────────
    # La demostracion de Astra debe quedar marcada como demo docente, no como
    # algo que se le pide ejecutar al estudiante con sus propias credenciales.
    if "cassandra.cluster" in json.dumps(nb, ensure_ascii=False):
        if "demo-astra" not in json.dumps(nb, ensure_ascii=False):
            errores.append("hay codigo de conexion a Cassandra sin la etiqueta demo-astra")

    # cassandra-driver>=3.30 no existe en PyPI; si aparece ese pin exacto es un error.
    if re.search(r"cassandra-driver\s*[>=]=?\s*3\.30", texto_md + json.dumps(nb, ensure_ascii=False)):
        errores.append("se referencia cassandra-driver>=3.30, que no existe publicado en PyPI")

    if len(celdas) > 85:
        errores.append(f"el cuaderno tiene {len(celdas)} celdas y el limite acordado es 85")

    # Nada de esto puede fingir una conexion a Atlas: el modo de respaldo debe
    # avisar explicitamente que no es una conexion real.
    texto_codigo = "\n".join(
        "".join(c["source"]) for c in celdas if c["cell_type"] == "code"
    )
    if "MongoClient(" in texto_codigo and "except Exception" not in texto_codigo:
        avisos.append("hay una conexion a Atlas sin manejo explicito de fallo (modo de respaldo)")

    print(f"Cuaderno: {os.path.relpath(NB, REPO)}")
    print(f"  celdas: {len(celdas)}  |  preguntas: {verificadores}  |  URLs de datos: {len(urls)}")
    print()
    for u in urls:
        print("  dato:", u.replace("https://raw.githubusercontent.com/jazaineam1/BigData2026/main/", ""))
    print()

    if avisos:
        print(f"AVISOS ({len(avisos)}):")
        for a in avisos:
            print("  ·", a)
        print()

    if errores:
        print(f"ERRORES ({len(errores)}):")
        for e in errores:
            print("  ✗", e)
        return 1

    print("Sin errores. Recuerda comprobar las URLs con una peticion real antes de la clase.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
