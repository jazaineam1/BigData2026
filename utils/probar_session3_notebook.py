# -*- coding: utf-8 -*-
"""
utils/probar_session3_notebook.py
=================================
Ejecuta TODAS las celdas de codigo del cuaderno de la sesion 3, en orden.

Por que existe este archivo
---------------------------
La version anterior de esta prueba saltaba las celdas que llamaban a
`pregunta_interactiva`, clasificandolas como "soporte". Resultado: las ocho
preguntas nunca se ejecutaron, y una llamada con argumentos que ya no
existian llego hasta Colab y reventó en clase con:

    TypeError: pregunta_interactiva() got an unexpected keyword argument 'tema'

La leccion es la del propio cuaderno: una prueba que excluye una parte no
prueba esa parte, y reportar "0 fallos" sobre una muestra recortada es el
mismo error que enseñamos a detectar en el paso 6.

Que hace
--------
- Sustituye `display` y `HTML` de IPython por dobles que capturan la salida,
  para que las celdas de interfaz se ejecuten de verdad.
- Sustituye el arranque de `mongod` por `mongomock`, que es la ruta de
  respaldo declarada en el cuaderno.
- Completa los huecos que el estudiante llena, para poder ejecutar de corrido.
- Puede leer los datos desde `main` o desde los archivos locales.

Uso
---
    python utils/probar_session3_notebook.py
    python utils/probar_session3_notebook.py --local
"""

import argparse
import io
import json
import os
import re
import sys
import traceback

# El cuaderno llama a plt.show(). Con un backend interactivo eso abre una
# ventana y se queda esperando a que alguien la cierre: la prueba se cuelga
# sin decir por que. Agg dibuja en memoria y sigue de largo.
os.environ.setdefault("MPLBACKEND", "Agg")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NB = os.path.join(REPO, "Cuadernos", "3_MongoDB_Documental.ipynb")
RAW = "https://raw.githubusercontent.com/jazaineam1/BigData2026/main"

# Huecos que el estudiante completa. La prueba los rellena para poder
# ejecutar el cuaderno de corrido y comprobar que la solucion es la correcta.
HUECOS = {
    'OPERADOR = "____"': 'OPERADOR = "$gt"',
    'METODO = "____"': 'METODO = "insert_many"',
    '.____("citas", -1)': '.sort("citas", -1)',
    '"_id": "$____", "n"': '"_id": "$revista", "n"',
    '{"$____": "$autores"}': '{"$unwind": "$autores"}',
    '____(a["autores"])': 'len(a["autores"])',
}


class SalidaHTML:
    """Doble de IPython.display.HTML que conserva el contenido."""

    def __init__(self, data):
        self.data = data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--local", action="store_true",
                    help="leer los datos de los archivos locales en vez de main")
    args = ap.parse_args()

    nb = json.load(io.open(NB, encoding="utf-8"))
    capturado = []

    entorno = {
        "__name__": "__main__",
        # Solo nos interesan los bloques HTML: los DataFrame se ignoran aqui.
        "display": lambda x: capturado.append(x.data) if isinstance(x, SalidaHTML) else None,
        "HTML": SalidaHTML,
    }

    ok, fallos, preguntas = 0, [], 0
    html_preguntas = []
    for i, celda in enumerate(nb["cells"]):
        if celda["cell_type"] != "code":
            continue
        src = "".join(celda["source"])

        # La unica celda que no se puede ejecutar aqui: necesita Linux.
        if "fastdl.mongodb.org" in src:
            import mongomock
            entorno["client"] = mongomock.MongoClient()
            entorno["db"] = entorno["client"]["compras_claras"]
            entorno["motor"] = "mongomock (ruta de respaldo del cuaderno)"
            print(f"[{i:3d}] arranque -> respaldo mongomock")
            ok += 1
            continue

        # La celda que importa IPython: ya tenemos los dobles en el entorno.
        src = re.sub(r"^\s*from IPython\.display import .*$", "", src, flags=re.M)

        if args.local:
            src = src.replace(RAW + "/Datos/", "file:///" + REPO.replace("\\", "/") + "/Datos/")
            src = src.replace(RAW + "/Cuadernos/",
                              "file:///" + REPO.replace("\\", "/") + "/Cuadernos/")

        for hueco, relleno in HUECOS.items():
            if hueco in src:
                src = src.replace(hueco, relleno)
                print(f"[{i:3d}] hueco del estudiante completado: {relleno}")

        es_pregunta = "pregunta_interactiva(" in src and "def pregunta_interactiva" not in src
        antes = len(capturado)

        try:
            exec(compile(src, f"celda_{i}", "exec"), entorno)
            ok += 1
            if es_pregunta:
                preguntas += 1
                # Solo los bloques que dibujo ESTA celda cuentan como pregunta.
                html_preguntas.extend(capturado[antes:])
        except Exception:
            fallos.append((i, traceback.format_exc()))
            print(f"[{i:3d}] FALLO")
            print(traceback.format_exc()[-600:])

    # ── Comprobaciones sobre lo que dibujaron las preguntas ──────────────────
    problemas = []
    if preguntas != 8:
        problemas.append(f"se ejecutaron {preguntas} preguntas y deberian ser 8")
    sin_boton = [h for h in html_preguntas if "Verificar respuesta" not in h]
    if sin_boton:
        problemas.append(f"{len(sin_boton)} pregunta(s) se dibujaron sin su boton de verificar")
    radios = sum(h.count('type="radio"') for h in html_preguntas)
    if preguntas and radios != preguntas * 4:
        problemas.append(f"hay {radios} opciones dibujadas y deberian ser {preguntas * 4}")

    print()
    print("=" * 64)
    print(f"celdas de codigo ejecutadas : {ok}")
    print(f"  de ellas, preguntas       : {preguntas} de 8")
    print(f"  bloques HTML de preguntas : {len(html_preguntas)}")
    print(f"  opciones dibujadas        : {radios}")
    print(f"fallos                      : {len(fallos)}")
    for p in problemas:
        print("  ✗", p)
    if not fallos and not problemas:
        print()
        print("Todo ejecuta, incluidas las ocho preguntas.")
    return 1 if (fallos or problemas) else 0


if __name__ == "__main__":
    sys.exit(main())
