#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Chequeos funcionales reutilizables para validadores de sesión.

A diferencia de una validación de texto (`"Verificar" in celda`), esto
EJECUTA el código real del widget de preguntas contra un payload de prueba
y confirma, con un parser HTML real, que nada se filtra como texto visible.

Es la prueba de regresión del bug corregido el 2026-09-10: `json.dumps()`
de la retroalimentación insertaba comillas dobles sin escapar dentro de un
atributo `onclick="..."` también delimitado por comillas dobles, cerrándolo
antes de tiempo. El payload de prueba incluye a propósito comillas dobles,
comillas simples y `&` en la retroalimentación para que una regresión
futura de ese mismo tipo no pase inadvertida.
"""
from __future__ import annotations

import base64
import json
import sys
import types
from html.parser import HTMLParser


def _visible_text(html_out: str) -> str:
    class Checker(HTMLParser):
        def __init__(self):
            super().__init__()
            self.texts: list[str] = []

        def handle_data(self, data):
            self.texts.append(data)

    checker = Checker()
    checker.feed(html_out)
    return " ".join(t.strip() for t in checker.texts if t.strip())


def check_question_widget_renders(interactivity_code: str) -> list[str]:
    """Ejecuta `pregunta_codificada()` con un payload de prueba y devuelve
    una lista de errores (vacía si todo está bien).

    No requiere IPython instalado: sustituye `IPython.display` por un doble
    de prueba que solo captura el HTML generado, sin mostrarlo.
    """
    errors: list[str] = []
    captured: dict[str, str] = {}

    class FakeHTML:
        def __init__(self, data):
            self.data = data

    def fake_display(x):
        captured["html"] = x.data

    fake_ipython = types.ModuleType("IPython")
    fake_display_module = types.ModuleType("IPython.display")
    fake_display_module.display = fake_display
    fake_display_module.HTML = FakeHTML

    previous_ipython = sys.modules.get("IPython")
    previous_display = sys.modules.get("IPython.display")
    sys.modules["IPython"] = fake_ipython
    sys.modules["IPython.display"] = fake_display_module
    try:
        namespace: dict = {}
        exec(compile(interactivity_code, "<interactivity>", "exec"), namespace)
        if "pregunta_codificada" not in namespace:
            return ["INTERACTIVITY no define pregunta_codificada()"]

        payload = base64.b64encode(
            json.dumps(
                {
                    "numero": 999,
                    "tema": "Prueba de regresión",
                    "pregunta": '¿Pregunta de prueba con "comillas" y & símbolos?',
                    "opciones": ["Opción a", "Opción b"],
                    "correcta": 0,
                    "retro": [
                        'Retroalimentación con "comillas dobles" y & símbolo.',
                        "Otra con apóstrofe: no es 'la' respuesta.",
                    ],
                },
                ensure_ascii=False,
            ).encode("utf-8")
        ).decode("ascii")

        namespace["pregunta_codificada"](payload)
        html_out = captured.get("html", "")
        if not html_out:
            return ["pregunta_codificada() no llamó display(HTML(...))"]

        visible = _visible_text(html_out)
        sospechosos = [
            "innerHTML", "r[i]", "function()", "querySelector",
            "getElementById", "textContent", "onclick",
        ]
        fugas = [s for s in sospechosos if s in visible]
        if fugas:
            errors.append(
                f"El widget de pregunta filtra fragmentos de JS al texto visible: {fugas} "
                f"(revisa el escapado de comillas en el atributo onclick)"
            )
        if "Verificar" not in visible:
            errors.append("El widget de pregunta no muestra el botón 'Verificar' como texto visible")
        if html_out.count("<button") != html_out.count("</button>"):
            errors.append("El HTML generado no tiene la misma cantidad de <button> y </button>")
    except Exception as exc:  # noqa: BLE001 - queremos reportar cualquier fallo como error de validación
        errors.append(f"pregunta_codificada() lanzó una excepción con el payload de prueba: {exc!r}")
    finally:
        if previous_ipython is not None:
            sys.modules["IPython"] = previous_ipython
        else:
            sys.modules.pop("IPython", None)
        if previous_display is not None:
            sys.modules["IPython.display"] = previous_display
        else:
            sys.modules.pop("IPython.display", None)

    return errors
