# -*- coding: utf-8 -*-
"""
utils/validate_session3_notebook.py
===================================
Valida el cuaderno de la sesion 3 antes de publicarlo.

Comprueba hechos verificables, no vocabulario. Prohibir palabras produce
falsos fallos y contradice la idea de anunciar lo que viene.

El primer chequeo es el que motivo este archivo
-----------------------------------------------
Una celda markdown cuya linea empieza con cuatro espacios se renderiza como
BLOQUE DE CODIGO. Como `make_notebook._to_source` usa `textwrap.dedent`, y
dedent calcula el prefijo comun de todas las lineas no vacias, basta con que
UNA linea quede sin indentar para que la celda entera conserve sus 8 o 12
espacios y se rompa. Paso desapercibido en las ocho preguntas de esta sesion:
la caja azul, la negrita y las opciones se veian como codigo gris.

Uso
---
    python utils/validate_session3_notebook.py
"""

import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(REPO, "Cuadernos", "3_MongoDB_Documental.ipynb")


def lineas_indentadas_fuera_de_fence(fuente):
    """Devuelve las lineas markdown que Colab renderizaria como codigo sin querer."""
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
            # Continuacion de lista o de etiqueta HTML: es indentacion legitima.
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

    # ── 1. Markdown que se renderiza como bloque de codigo ────────────────────
    for i, c in enumerate(celdas):
        if c["cell_type"] != "markdown":
            continue
        for n, texto in lineas_indentadas_fuera_de_fence(c["source"]):
            errores.append(
                f"celda {i}, linea {n}: markdown indentado, se vera como bloque de "
                f"codigo -> {texto!r}"
            )

    # ── 2. La respuesta correcta no puede leerse en GitHub ────────────────────
    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if re.search(r"correcta\s*=\s*\d", src):
            errores.append(f"celda {i}: la respuesta correcta es legible en el fuente")

    # ── 3. Cada pregunta tiene enunciado visible y verificador oculto ─────────
    enunciados = sum(
        1 for c in celdas
        if c["cell_type"] == "markdown"
        and re.search(r"^#+ Pregunta \d+ de \d+", "".join(c["source"]), re.M)
    )
    verificadores = sum(
        1 for c in celdas if "pregunta-interactiva" in c["metadata"].get("tags", [])
    )
    # La pregunta vive en UNA sola celda, la del widget. Si aparece tambien en
    # markdown, el estudiante la lee dos veces seguidas en Colab.
    if enunciados:
        errores.append(
            f"hay {enunciados} enunciados en markdown: la pregunta se veria duplicada en Colab"
        )
    if verificadores != 8:
        errores.append(f"hay {verificadores} preguntas y deberian ser 8")

    # ── 4. Accesibilidad: fondo sin color de texto ────────────────────────────
    for i, c in enumerate(celdas):
        for bloque in re.findall(r'style="([^"]*)"', "".join(c["source"])):
            if "background" in bloque and "color:" not in bloque:
                avisos.append(
                    f"celda {i}: hay un estilo con fondo y sin color de texto; "
                    f"quedara ilegible en Colab con tema oscuro"
                )
                break

    # ── 4-bis. Caracteres de control que se comen el texto ────────────────────
    # Un `\b` escrito sin escapar en el generador se guarda como retroceso real
    # (\x08) y borra la palabra que explica. Paso desapercibido en la frase que
    # explicaba por que el patron se comio el prefijo FTIC-.
    for i, c in enumerate(celdas):
        for ch in "".join(c["source"]):
            if ord(ch) < 32 and ch not in "\n\t":
                errores.append(
                    f"celda {i}: contiene el caracter de control {ord(ch):#04x}; "
                    f"seguramente es un escape sin escapar y se comio texto"
                )
                break

    # ── 4-ter. <details> abierto en una celda y cerrado en otra ───────────────
    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if src.count("<details>") != src.count("</details>"):
            errores.append(
                f"celda {i}: <details> descuadrado; en Colab cada celda se dibuja "
                f"aparte, asi que no puede abrirse en una y cerrarse en otra"
            )

    # ── 5. Sin celdas vacias y sin triple comilla doble en codigo ─────────────
    for i, c in enumerate(celdas):
        src = "".join(c["source"])
        if not src.strip():
            errores.append(f"celda {i}: vacia")
        if c["cell_type"] == "code" and '"""' in src:
            errores.append(f"celda {i}: triple comilla doble en una celda de codigo")

    # ── 6. Los datos que el cuaderno descarga deben existir en main ───────────
    urls = sorted(set(re.findall(
        r"https://raw\.githubusercontent\.com/[^\s\"')]+", json.dumps(nb, ensure_ascii=False)
    )))

    # ── 7. Sin referencias a minutos de clase ─────────────────────────────────
    texto_md = " ".join(
        "".join(c["source"]) for c in celdas if c["cell_type"] == "markdown"
    )
    if re.search(r"\b\d+\s*minutos?\b", texto_md):
        avisos.append("hay referencias a minutos en el texto del estudiante")

    # ── Informe ───────────────────────────────────────────────────────────────
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
