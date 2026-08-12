#!/usr/bin/env python3
"""Genera las diez láminas visuales de la sesión 2 en SVG y PNG.

El SVG es la fuente pedagógica: usa una gramática visual común, tipografía
legible y relaciones explícitas. El PNG se renderiza con Chrome para Colab.
"""

from __future__ import annotations

import argparse
import html
import os
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIAGRAM_DIR = ROOT / "assets" / "diagrams" / "session2"
GIT_DIR = ROOT / "assets" / "session2" / "git"

W, H = 1600, 900

NAVY = "#12395B"
NAVY_2 = "#1D4F73"
INK = "#17324D"
MUTED = "#52697C"
LINE = "#B8C8D6"
BG = "#F3F7FA"
WHITE = "#FFFFFF"
BLUE = "#2F6FB0"
BLUE_L = "#E8F2FB"
GREEN = "#24855A"
GREEN_L = "#E7F5ED"
AMBER = "#C98500"
AMBER_L = "#FFF3D2"
ORANGE = "#E95C3A"
ORANGE_L = "#FDE9E3"
PURPLE = "#6C5AA7"
PURPLE_L = "#EEEAF8"
RED = "#C93F34"
RED_L = "#FCE8E6"
TEAL = "#167C80"
TEAL_L = "#E3F5F5"


class Canvas:
    """Constructor SVG mínimo con componentes reutilizables."""

    def __init__(self, title: str, desc: str):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
            f"<title id=\"title\">{html.escape(title)}</title>",
            f"<desc id=\"desc\">{html.escape(desc)}</desc>",
            """<defs>
              <filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">
                <feDropShadow dx="0" dy="5" stdDeviation="7" flood-color="#17324D" flood-opacity=".12"/>
              </filter>
              <marker id="arrow-blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#2F6FB0"/>
              </marker>
              <marker id="arrow-red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#C93F34"/>
              </marker>
              <marker id="arrow-green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#24855A"/>
              </marker>
              <marker id="arrow-purple" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="#6C5AA7"/>
              </marker>
            </defs>""",
            f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        ]

    def raw(self, markup: str) -> None:
        self.parts.append(markup)

    def rect(
        self, x, y, w, h, fill=WHITE, stroke=LINE, sw=2, rx=18,
        shadow=False, dash=None, opacity=1,
    ) -> None:
        attrs = [
            f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"',
            f'rx="{rx}"', f'fill="{fill}"', f'stroke="{stroke}"',
            f'stroke-width="{sw}"', f'opacity="{opacity}"',
        ]
        if shadow:
            attrs.append('filter="url(#shadow)"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append("<rect " + " ".join(attrs) + "/>")

    def circle(self, cx, cy, r, fill=WHITE, stroke=LINE, sw=2, shadow=False) -> None:
        extra = ' filter="url(#shadow)"' if shadow else ""
        self.parts.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"{extra}/>'
        )

    def line(
        self, x1, y1, x2, y2, stroke=BLUE, sw=3, arrow=True, dash=None,
        marker="blue",
    ) -> None:
        attrs = [
            f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
            f'stroke="{stroke}"', f'stroke-width="{sw}"', 'fill="none"',
            'stroke-linecap="round"',
        ]
        if arrow:
            attrs.append(f'marker-end="url(#arrow-{marker})"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append("<line " + " ".join(attrs) + "/>")

    def path(
        self, d, stroke=BLUE, sw=3, arrow=True, dash=None, marker="blue",
        fill="none",
    ) -> None:
        attrs = [
            f'd="{d}"', f'stroke="{stroke}"', f'stroke-width="{sw}"',
            f'fill="{fill}"', 'stroke-linecap="round"', 'stroke-linejoin="round"',
        ]
        if arrow:
            attrs.append(f'marker-end="url(#arrow-{marker})"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        self.parts.append("<path " + " ".join(attrs) + "/>")

    def text(
        self, x, y, lines, size=22, fill=INK, weight=400, anchor="start",
        line_height=1.25, family="Inter, Segoe UI, Arial, sans-serif", italic=False,
    ) -> None:
        if isinstance(lines, str):
            lines = [lines]
        style = "font-style:italic;" if italic else ""
        self.parts.append(
            f'<text x="{x}" y="{y}" fill="{fill}" font-family="{family}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" '
            f'style="{style}">'
        )
        dy = size * line_height
        for index, line in enumerate(lines):
            offset = 0 if index == 0 else dy
            self.parts.append(
                f'<tspan x="{x}" dy="{offset if index == 0 else dy}">'
                f'{html.escape(str(line))}</tspan>'
            )
        self.parts.append("</text>")

    def pill(self, x, y, w, label, fill=BLUE_L, color=BLUE, stroke=None, size=17) -> None:
        self.rect(x, y, w, 38, fill=fill, stroke=stroke or fill, sw=1, rx=19)
        self.text(x + w / 2, y + 25, label, size=size, fill=color, weight=700, anchor="middle")

    def number_badge(self, cx, cy, number, fill=BLUE, radius=25) -> None:
        self.circle(cx, cy, radius, fill=fill, stroke=fill, sw=1)
        self.text(cx, cy + 8, str(number), size=22, fill=WHITE, weight=800, anchor="middle")

    def header(self, index: str, title: str, subtitle: str) -> None:
        self.rect(0, 0, W, 112, fill=NAVY, stroke=NAVY, sw=0, rx=0)
        self.pill(1376, 24, 176, index.upper(), fill="#2A5878", color="#D9EFFB", size=15)
        title_size = 26 if len(title) > 62 else 28 if len(title) > 50 else 31
        subtitle_size = 16 if len(subtitle) > 92 else 18
        self.text(48, 50, title, size=title_size, fill=WHITE, weight=800)
        self.text(48, 82, subtitle, size=subtitle_size, fill="#CFE4F2", weight=400)

    def footer(self, label: str, text: str, color=NAVY, fill="#E7EFF5") -> None:
        self.rect(48, 838, 1504, 42, fill=fill, stroke=fill, sw=0, rx=13)
        self.text(70, 865, label.upper(), size=15, fill=color, weight=800)
        text_x = max(230, 70 + len(label) * 9.5 + 34)
        self.text(text_x, 865, text, size=17, fill=INK, weight=600)

    def card(
        self, x, y, w, h, title, body, accent=BLUE, fill=WHITE, number=None,
        tag=None, shadow=True, title_size=21, body_size=18,
    ) -> None:
        self.rect(x, y, w, h, fill=fill, stroke=accent, sw=2, rx=18, shadow=shadow)
        self.rect(x, y, 9, h, fill=accent, stroke=accent, sw=0, rx=9)
        title_x = x + 30
        if number is not None:
            self.number_badge(x + 40, y + 40, number, fill=accent, radius=22)
            title_x = x + 75
        self.text(title_x, y + 43, title, size=title_size, fill=INK, weight=800)
        if tag:
            self.pill(x + 28, y + 67, min(w - 56, 240), tag, fill=fill, color=accent, stroke=accent, size=14)
            body_y = y + 130
        else:
            body_y = y + 82
        self.text(x + 30, body_y, body, size=body_size, fill=MUTED, weight=500, line_height=1.35)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")


def make_hilo() -> Canvas:
    c = Canvas(
        "Hilo conductor de Compras Claras",
        "Trazabilidad desde una decisión empresarial hasta la acción humana y la mejora del proceso.",
    )
    c.header("Mapa 1 de 6", "La historia completa: de la decisión a la mejora", "Cada componente existe porque responde una pregunta anterior del negocio")

    c.rect(42, 142, 320, 660, fill=NAVY, stroke=NAVY, sw=0, rx=24, shadow=True)
    c.pill(70, 172, 145, "PUNTO DE PARTIDA", fill="#2A5878", color="#D9EFFB", size=14)
    c.text(70, 240, ["Laura", "Analista de", "seguimiento"], size=25, fill=WHITE, weight=800, line_height=1.15)
    c.text(70, 325, ["Necesita decidir:", "¿qué contratos", "revisar primero?"], size=26, fill="#FFFFFF", weight=700, line_height=1.18)
    c.rect(70, 458, 264, 145, fill="#214E6D", stroke="#4E7B99", sw=1, rx=16)
    c.text(92, 493, "Criterio de éxito", size=17, fill="#BFE4F6", weight=800)
    c.text(92, 532, ["menos tiempo para priorizar", "sin acusar ni automatizar", "la decisión humana"], size=18, fill=WHITE, weight=500, line_height=1.35)
    c.rect(70, 637, 264, 112, fill="#153149", stroke="#4E7B99", sw=1, rx=16)
    c.text(92, 672, "Regla de diseño", size=17, fill="#F7CCBE", weight=800)
    c.text(92, 706, ["primero propósito;", "después herramienta"], size=19, fill=WHITE, weight=600, line_height=1.3)

    c.card(408, 152, 330, 230, "Proceso AS-IS", ["Seguimiento contractual", "Actores + tareas + decisiones", "Cuello: consolidación manual"], BLUE, number=1, tag="¿DÓNDE SE DEMORA?")
    c.card(786, 152, 330, 230, "Datos necesarios", ["Contrato · entidad · estado", "Fechas · duración · calidad", "Responsable y regla por campo"], AMBER, number=2, tag="¿QUÉ EVIDENCIA NACE?")
    c.card(1164, 152, 388, 230, "Capacidades y herramientas", ["Ingerir → validar → integrar", "analizar → explicar → alertar", "Productos solo como candidatos"], PURPLE, number=3, tag="¿QUÉ DEBE HACER EL SISTEMA?")

    c.card(1164, 500, 388, 230, "KPI verificable", ["Tiempo para priorizar", "% de registros completos", "% de casos atendidos en SLA"], GREEN, number=4, tag="¿CÓMO SABEMOS SI MEJORA?")
    c.card(786, 500, 330, 230, "Acción humana", ["Revisar contexto", "Corregir · escalar · descartar", "Registrar motivo y resultado"], ORANGE, number=5, tag="¿QUIÉN DECIDE?")
    c.rect(408, 500, 330, 230, fill=WHITE, stroke=RED, sw=2, rx=18, shadow=True)
    c.text(438, 543, "Atajo que debemos evitar", size=21, fill=RED, weight=800)
    c.text(438, 592, ["“Instalemos una herramienta", "y luego busquemos el problema”"], size=20, fill=INK, weight=600, italic=True, line_height=1.35)
    c.pill(438, 672, 270, "ROMPE LA TRAZABILIDAD", fill=RED_L, color=RED, size=14)

    c.line(362, 280, 408, 280)
    c.line(738, 267, 786, 267)
    c.line(1116, 267, 1164, 267)
    c.line(1358, 382, 1358, 500, stroke=PURPLE, marker="purple")
    c.line(1164, 615, 1116, 615, stroke=GREEN, marker="green")
    c.path("M786 615 C740 615 752 780 573 780 C405 780 392 430 510 382", stroke=ORANGE, sw=3, arrow=True, dash="8 7", marker="red")
    c.pill(487, 761, 276, "RESULTADO → NUEVO DATO", fill=ORANGE_L, color=RED, size=14)

    c.footer("Lectura clave", "La arquitectura es una cadena de justificaciones, no una colección de productos.")
    return c


def make_as_is() -> Canvas:
    c = Canvas(
        "Proceso AS-IS de seguimiento contractual",
        "Proceso con tres carriles, datos producidos, validación, cuello de botella y bucle de retrabajo.",
    )
    c.header("Mapa 2 de 6", "Proceso AS-IS: dónde nace el retraso", "Carriles por responsable · artefactos de datos · decisión de completitud · retrabajo explícito")

    lanes = [
        (140, 235, "ENTIDAD CONTRATANTE", ["Origina y actualiza", "el proceso"], BLUE, BLUE_L),
        (390, 185, "PLATAFORMA SECOP", ["Registra y publica", "eventos"], AMBER, AMBER_L),
        (590, 225, "OFICINA DE SEGUIMIENTO", ["Consolida, prioriza", "y revisa"], PURPLE, PURPLE_L),
    ]
    for y, h, title, subtitle, color, fill in lanes:
        c.rect(34, y, 1532, h, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
        c.rect(34, y, 198, h, fill=fill, stroke=color, sw=1.5, rx=16)
        c.text(58, y + 46, title, size=18, fill=color, weight=900)
        c.text(58, y + 80, subtitle, size=16, fill=MUTED, weight=500, line_height=1.25)

    # Entidad contratante
    steps = [
        (268, "1", "Definir necesidad", "objeto + responsable", BLUE),
        (520, "2", "Publicar proceso", "fecha + modalidad", BLUE),
        (772, "3", "Evaluar ofertas", "criterios + resultado", BLUE),
        (1024, "4", "Formalizar contrato", "proveedor + valor", BLUE),
        (1276, "5", "Reportar ejecución", "estado + fechas", ORANGE),
    ]
    for x, num, title, artifact, color in steps:
        c.rect(x, 180, 218, 112, fill=WHITE, stroke=color, sw=2, rx=14, shadow=True)
        c.number_badge(x + 32, 208, num, fill=color, radius=19)
        c.text(x + 62, 216, title, size=17, fill=INK, weight=800)
        c.pill(x + 18, 242, 182, artifact, fill=BLUE_L if color == BLUE else ORANGE_L, color=color, size=13)
    for x in [486, 738, 990, 1242]:
        c.line(x, 236, x + 34, 236)

    # Plataforma SECOP
    c.card(300, 423, 300, 118, "6 · Recibir evento", ["API / formulario", "marca de tiempo"], AMBER, shadow=False, title_size=18, body_size=16)
    c.card(690, 423, 300, 118, "7 · Guardar registro", ["fila operacional", "historial publicado"], AMBER, shadow=False, title_size=18, body_size=16)
    c.card(1080, 423, 330, 118, "8 · Exponer consulta", ["archivos / API", "sin vista integrada"], AMBER, shadow=False, title_size=18, body_size=16)
    c.line(600, 482, 690, 482, stroke=AMBER)
    c.line(990, 482, 1080, 482, stroke=AMBER)
    c.path("M1385 292 L1385 382 C1385 405 1370 423 1345 423", stroke=ORANGE, marker="red")
    c.pill(1226, 342, 260, "estado · fecha · avance", fill=ORANGE_L, color=ORANGE, size=14)

    # Oficina de seguimiento
    office_cards = [
        (270, "9 · Descargar", ["CSV por fuente", "cortes diferentes"], PURPLE),
        (520, "10 · Consolidar", ["unir + limpiar", "trabajo manual"], RED),
        (1070, "12 · Priorizar", ["lista preliminar", "reglas locales"], GREEN),
        (1320, "13 · Revisar", ["contexto + decisión", "resultado registrado"], ORANGE),
    ]
    for x, title, body, color in office_cards:
        c.card(x, 640, 210, 125, title, body, color, shadow=False, title_size=17, body_size=15)
    c.line(480, 702, 520, 702, stroke=PURPLE, marker="purple")
    c.line(730, 702, 785, 702, stroke=RED, marker="red")
    c.line(995, 702, 1070, 702, stroke=GREEN, marker="green")
    c.line(1280, 702, 1320, 702, stroke=GREEN, marker="green")

    # Gateway de completitud
    c.path("M890 622 L995 702 L890 782 L785 702 Z", stroke=AMBER, sw=3, arrow=False, fill=AMBER_L)
    c.text(890, 684, ["11 · ¿Fechas y", "campos completos?"], size=18, fill=INK, weight=800, anchor="middle", line_height=1.2)
    c.pill(985, 655, 65, "SÍ", fill=GREEN_L, color=GREEN, size=14)
    c.path("M890 622 C890 570 850 555 820 541", stroke=RED, sw=3, arrow=True, dash="8 6", marker="red")
    c.path("M820 541 C820 360 1390 365 1390 292", stroke=RED, sw=3, arrow=True, dash="8 6", marker="red")
    c.pill(620, 550, 385, "NO · solicitar corrección y volver a reportar", fill=RED_L, color=RED, size=14)

    # Bottleneck and metrics
    c.rect(505, 606, 240, 180, fill="none", stroke=RED, sw=4, rx=20, dash="10 6")
    c.pill(500, 592, 250, "CUELLO DE BOTELLA", fill=RED, color=WHITE, size=14)
    c.pill(270, 786, 275, "KPI · tiempo de consolidación", fill=PURPLE_L, color=PURPLE, size=14)
    c.pill(566, 786, 270, "KPI · % datos completos", fill=AMBER_L, color=AMBER, size=14)
    c.pill(857, 786, 260, "KPI · casos priorizados", fill=GREEN_L, color=GREEN, size=14)

    c.footer("Diagnóstico", "El cuello de botella está en descargar, unir y volver a pedir datos; todavía no en el algoritmo.")
    return c


def make_bridge() -> Canvas:
    c = Canvas(
        "Puente entre operación y analítica",
        "ETL y ELT resuelven la misma integración con distinto orden, ubicación de cómputo y momento de control.",
    )
    c.header(
        "Mapa 3 de 6",
        "La T cambia de lugar: dos rutas desde el mismo evento",
        "Compare la secuencia, el artefacto que aterriza primero y el control que debe actuar antes",
    )
    c.raw(
        """<defs>
          <marker id="arrow-amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#C98500"/>
          </marker>
          <marker id="arrow-ink" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
            <path d="M0,0 L0,6 L9,3 z" fill="#17324D"/>
          </marker>
        </defs>"""
    )

    # Reading zones
    c.rect(40, 136, 248, 78, fill=BLUE_L, stroke=BLUE, sw=1.5, rx=16)
    c.text(64, 168, "1 · OPERACIÓN", size=18, fill=BLUE, weight=900)
    c.text(64, 197, "registrar sin detener el proceso", size=14, fill=MUTED, weight=600)
    c.rect(308, 136, 674, 78, fill=AMBER_L, stroke=AMBER, sw=1.5, rx=16)
    c.text(332, 168, "2 · INTEGRACIÓN", size=18, fill=AMBER, weight=900)
    c.text(332, 197, "elegir ETL, ELT o un híbrido según la restricción", size=14, fill=MUTED, weight=600)
    c.rect(1002, 136, 556, 78, fill=PURPLE_L, stroke=PURPLE, sw=1.5, rx=16)
    c.text(1026, 168, "3 · CONSUMO Y ACCIÓN", size=18, fill=PURPLE, weight=900)
    c.text(1026, 197, "integrar historia, comparar y decidir", size=14, fill=MUTED, weight=600)

    # OLTP source
    c.rect(40, 250, 248, 396, fill=WHITE, stroke=BLUE, sw=2.5, rx=20, shadow=True)
    c.pill(62, 272, 84, "OLTP", fill=BLUE, color=WHITE, size=16)
    c.text(62, 336, ["Evento operacional", "que no puede esperar"], size=20, fill=NAVY, weight=900, line_height=1.2)
    c.text(62, 430, ["• contrato publicado", "• estado actualizado", "• avance reportado"], size=16, fill=INK, weight=600, line_height=1.55)
    c.rect(62, 550, 204, 66, fill=BLUE_L, stroke=BLUE, sw=1, rx=12)
    c.text(78, 578, "ARTEFACTO", size=12, fill=BLUE, weight=900)
    c.text(78, 603, "transacción + versión", size=15, fill=INK, weight=700)

    # Integration frame and decision statement
    c.rect(308, 234, 674, 430, fill=WHITE, stroke=LINE, sw=1.5, rx=20)
    c.pill(410, 250, 470, "MISMA E · DISTINTO ORDEN DE T Y L", fill=NAVY, color=WHITE, size=15)

    # ETL lane
    c.rect(330, 306, 630, 148, fill="#FFFBEB", stroke=AMBER, sw=2, rx=16)
    c.pill(348, 326, 82, "ETL", fill=AMBER, color=WHITE, size=16)
    etl_steps = [
        (456, "E", "extraer", "snapshot + metadatos", BLUE, BLUE_L),
        (622, "T", "transformar", "validar · enmascarar", ORANGE, ORANGE_L),
        (788, "L", "cargar", "tabla curada", GREEN, GREEN_L),
    ]
    for x, letter, title, artefact, color, fill in etl_steps:
        c.rect(x, 322, 140, 112, fill=fill, stroke=color, sw=1.5, rx=14)
        c.number_badge(x + 24, 348, letter, fill=color, radius=18)
        c.text(x + 24, 355, letter, size=15, fill=WHITE, weight=900, anchor="middle")
        c.text(x + 48, 350, title, size=13, fill=color, weight=900)
        c.text(x + 16, 394, artefact, size=11, fill=INK, weight=600)
    c.line(596, 378, 620, 378, stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.line(762, 378, 786, 378, stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.text(348, 438, "La política actúa antes de que el dato llegue al destino compartido.", size=13, fill=MUTED, weight=600)

    # ELT lane
    c.rect(330, 482, 630, 162, fill="#F5F3FF", stroke=PURPLE, sw=2, rx=16)
    c.pill(348, 502, 82, "ELT", fill=PURPLE, color=WHITE, size=16)
    elt_steps = [
        (456, "E", "extraer", "snapshot + metadatos", BLUE, BLUE_L),
        (622, "L", "cargar", "zona raw protegida", PURPLE, PURPLE_L),
        (788, "T", "transformar", ["SQL dentro", "del destino"], TEAL, TEAL_L),
    ]
    for x, letter, title, artefact, color, fill in elt_steps:
        c.rect(x, 498, 140, 118, fill=fill, stroke=color, sw=1.5, rx=14)
        c.number_badge(x + 24, 525, letter, fill=color, radius=18)
        c.text(x + 24, 532, letter, size=15, fill=WHITE, weight=900, anchor="middle")
        c.text(x + 48, 527, title, size=13, fill=color, weight=900)
        c.text(x + 16, 566, artefact, size=11, fill=INK, weight=600, line_height=1.2)
    c.line(596, 557, 620, 557, stroke=PURPLE, sw=2.5, arrow=True, marker="purple")
    c.line(762, 557, 786, 557, stroke=PURPLE, sw=2.5, arrow=True, marker="purple")
    c.text(348, 630, "El acceso y la retención protegen lo raw antes de ejecutar la T.", size=13, fill=MUTED, weight=600)

    # Branch from OLTP to both routes
    c.path("M288 448 C330 448 330 378 454 378", stroke=BLUE, sw=2.5, arrow=True, marker="blue")
    c.path("M288 448 C330 448 330 557 454 557", stroke=BLUE, sw=2.5, arrow=True, marker="blue")

    # Analytical responsibility chain
    analytic_cards = [
        (1012, 250, 250, 170, "Warehouse", "historia integrada", "hechos + dimensiones", GREEN, GREEN_L),
        (1292, 250, 250, 170, "Data Mart", "vista de seguimiento", "métricas aprobadas", TEAL, TEAL_L),
        (1012, 470, 250, 170, "OLAP / BI", "comparar y explorar", "medida × dimensión", PURPLE, PURPLE_L),
        (1292, 470, 250, 170, "Acción humana", "priorizar revisión", "motivo explicable", ORANGE, ORANGE_L),
    ]
    for x, y, w, h, title, purpose, artefact, color, fill in analytic_cards:
        c.rect(x, y, w, h, fill=WHITE, stroke=color, sw=2, rx=18, shadow=True)
        c.rect(x, y, w, 48, fill=color, stroke=color, sw=0, rx=18)
        c.rect(x, y + 34, w, 14, fill=color, stroke=color, sw=0, rx=0)
        c.text(x + 20, y + 31, title, size=17, fill=WHITE, weight=900)
        c.text(x + 20, y + 84, purpose, size=16, fill=INK, weight=800)
        c.pill(x + 18, y + 112, w - 36, artefact, fill=fill, color=color, size=13)
    c.line(1262, 334, 1290, 334, stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.path("M1417 420 C1417 446 1250 448 1137 468", stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.line(1262, 554, 1290, 554, stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.path("M928 378 C972 378 980 334 1010 334", stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.path("M928 557 C976 557 978 382 1010 360", stroke=PURPLE, sw=2.5, arrow=True, marker="purple")

    # Feedback and controls
    c.path("M1417 640 C1417 682 1180 688 854 688 L176 688 C110 688 108 652 108 620", stroke=ORANGE, sw=2.5, arrow=True, dash="8 6", marker="red")
    c.pill(626, 671, 348, "acción → nueva transacción OLTP", fill=ORANGE_L, color=ORANGE, size=14)
    c.rect(40, 720, 1518, 70, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
    c.text(64, 748, "CONTROLES EN AMBAS RUTAS", size=15, fill=NAVY, weight=900)
    controls = [
        (326, 148, "calidad", AMBER_L, AMBER),
        (488, 148, "linaje", BLUE_L, BLUE),
        (650, 166, "privacidad", RED_L, RED),
        (830, 150, "acceso", PURPLE_L, PURPLE),
        (994, 192, "observabilidad", TEAL_L, TEAL),
        (1200, 140, "costos", GREEN_L, GREEN),
        (1354, 180, "responsable", ORANGE_L, ORANGE),
    ]
    for x, width, label, fill, color in controls:
        c.pill(x, 736, width, label, fill=fill, color=color, size=13)

    c.footer("Decisión de diseño", "ETL si T debe ocurrir antes del destino; ELT si el destino puede gobernar raw y ejecutar T; híbrido cuando la restricción lo exige.")
    return c


def make_architecture() -> Canvas:
    c = Canvas(
        "Arquitectura empresarial objetivo de Compras Claras",
        "Blueprint por capas con trazabilidad vertical, capacidades, herramientas y controles transversales.",
    )
    c.header("Mapa 4 de 6", "Arquitectura TO-BE: cuatro dominios, una misma decisión", "La trazabilidad baja desde negocio hasta tecnología y vuelve con restricciones verificables")

    c.text(48, 144, "CONTROLES TRANSVERSALES", size=16, fill=NAVY, weight=900)
    controls = [
        (306, 174, "gobierno", PURPLE_L, PURPLE),
        (496, 174, "seguridad", RED_L, RED),
        (686, 174, "privacidad", ORANGE_L, ORANGE),
        (876, 210, "observabilidad", TEAL_L, TEAL),
        (1102, 174, "costos", GREEN_L, GREEN),
        (1292, 246, "calidad + linaje", AMBER_L, AMBER),
    ]
    for x, w, label, fill, color in controls:
        c.pill(x, 123, w, label, fill=fill, color=color, size=15)

    layers = [
        (184, 140, "1 · NEGOCIO", "por qué y quién", ORANGE, ORANGE_L),
        (338, 140, "2 · INFORMACIÓN", "qué significa", AMBER, AMBER_L),
        (492, 140, "3 · APLICACIONES", "qué capacidad", BLUE, BLUE_L),
        (646, 164, "4 · TECNOLOGÍA", "dónde se ejecuta", GREEN, GREEN_L),
    ]
    layer_cards = [
        [
            ("Decisión", "priorizar revisión"), ("Proceso TO-BE", "seguimiento + SLA"),
            ("Responsable", "analista + director"), ("KPI", "tiempo + cobertura"),
        ],
        [
            ("Fuentes", "SECOP + internos"), ("Entidades", "contrato · entidad"),
            ("Reglas", "fechas · unidades"), ("Trazabilidad", "origen + versión"),
        ],
        [
            ("Integración", "captura programada"), ("Calidad", "perfil + excepciones"),
            ("Analítica", "reglas explicables"), ("Consumo", "tablero + alertas"),
        ],
        [
            ("Conectividad", "API · archivos"), ("Almacenamiento", "Parquet · objetos"),
            ("Procesamiento", "Pandas · Spark"), ("Entrega", "BI · CI · monitoreo"),
        ],
    ]
    colors = [ORANGE, AMBER, BLUE, GREEN]
    fills = [ORANGE_L, AMBER_L, BLUE_L, GREEN_L]
    for idx, (y, h, title, subtitle, color, fill) in enumerate(layers):
        c.rect(36, y, 1528, h, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
        c.rect(36, y, 230, h, fill=fill, stroke=color, sw=1.5, rx=16)
        c.text(60, y + 48, title, size=19, fill=color, weight=900)
        c.text(60, y + 82, subtitle, size=16, fill=MUTED, weight=600)
        for card_idx, (card_title, card_body) in enumerate(layer_cards[idx]):
            x = 294 + card_idx * 310
            c.rect(x, y + 24, 278, h - 48, fill=WHITE, stroke=color, sw=1.8, rx=13, shadow=True)
            if card_idx == 0:
                c.number_badge(x + 32, y + 51, idx + 1, fill=color, radius=18)
                title_x = x + 58
            else:
                title_x = x + 22
            c.text(title_x, y + 57, card_title, size=17, fill=INK, weight=800)
            c.text(x + 22, y + 94, card_body, size=16, fill=MUTED, weight=500)

    # Trazabilidad explícita por el primer componente de cada capa.
    for y1, y2, color, marker in [
        (324, 362, ORANGE, "red"), (478, 516, AMBER, "red"), (632, 670, BLUE, "blue")
    ]:
        c.line(433, y1, 433, y2, stroke=color, sw=3, marker=marker)
    c.pill(500, 310, 300, "define información requerida", fill=ORANGE_L, color=ORANGE, size=14)
    c.pill(500, 464, 300, "habilita capacidades", fill=AMBER_L, color=AMBER, size=14)
    c.pill(500, 618, 300, "impone requisitos técnicos", fill=BLUE_L, color=BLUE, size=14)

    c.rect(1120, 800, 432, 30, fill=RED_L, stroke=RED, sw=1, rx=12)
    c.text(1336, 821, "TO-BE ≠ automatizar la decisión humana", size=14, fill=RED, weight=800, anchor="middle")
    c.footer("Prueba de diseño", "Cada componente técnico debe señalar qué dato, capacidad, proceso y KPI justifica su existencia.")
    return c


def make_nist() -> Canvas:
    c = Canvas(
        "Ciclo analítico NIST aplicado a SECOP",
        "Cinco etapas conectadas alrededor de una decisión humana con artefactos, responsables y controles.",
    )
    c.header("Mapa 5 de 6", "Ciclo analítico: la evidencia debe volver al proceso", "Captura → preparación → análisis → visualización → acción; después aparecen nuevas preguntas")

    c.rect(450, 128, 700, 48, fill=WHITE, stroke=LINE, sw=1, rx=18)
    c.text(800, 159, "GOBIERNO · SEGURIDAD · PRIVACIDAD · CALIDAD · TRAZABILIDAD", size=17, fill=NAVY, weight=900, anchor="middle")

    cards = [
        (650, 185, "1", "CAPTURA", BLUE, BLUE_L, ["Entrada: API o muestra", "Artefacto: snapshot + fuente", "Responsable: ingeniería"]),
        (1120, 290, "2", "PREPARACIÓN", AMBER, AMBER_L, ["Tipar fechas y unidades", "Artefacto: tabla + excepciones", "Responsable: datos"]),
        (1010, 600, "3", "ANÁLISIS", PURPLE, PURPLE_L, ["Perfil + reglas descriptivas", "Artefacto: métricas + cola", "Responsable: analista"]),
        (290, 600, "4", "VISUALIZACIÓN", TEAL, TEAL_L, ["Razón de prioridad + contexto", "Artefacto: reporte / tablero", "Responsable: BI"]),
        (180, 290, "5", "ACCIÓN", ORANGE, ORANGE_L, ["Revisar · corregir · escalar", "Artefacto: decisión registrada", "Responsable: negocio"]),
    ]
    for x, y, number, title, color, fill, body in cards:
        c.rect(x, y, 300, 165, fill=WHITE, stroke=color, sw=2, rx=18, shadow=True)
        c.number_badge(x + 38, y + 42, number, fill=color, radius=23)
        c.text(x + 75, y + 49, title, size=20, fill=color, weight=900)
        c.text(x + 24, y + 88, body, size=15, fill=MUTED, weight=550, line_height=1.32)

    c.circle(800, 492, 135, fill=NAVY, stroke="#0D2B43", sw=3, shadow=True)
    c.text(800, 452, "DECISIÓN SOPORTADA", size=17, fill="#BFE4F6", weight=900, anchor="middle")
    c.text(800, 494, ["¿qué contrato revisar", "primero y por qué?"], size=23, fill=WHITE, weight=800, anchor="middle", line_height=1.15)
    c.pill(682, 562, 236, "humana · explicable · trazable", fill="#2A5878", color=WHITE, size=12)

    # Recorrido circular.
    c.path("M950 260 C1040 245 1110 270 1140 315", stroke=BLUE, sw=3, marker="blue")
    c.path("M1370 455 C1410 530 1320 620 1260 635", stroke=AMBER, sw=3, marker="red")
    c.path("M1010 682 C850 800 600 800 590 682", stroke=PURPLE, sw=3, marker="purple")
    c.path("M290 635 C190 615 135 520 205 455", stroke=TEAL, sw=3, marker="green")
    c.path("M330 290 C430 170 590 165 650 230", stroke=ORANGE, sw=3, marker="red")

    c.pill(1040, 205, 155, "datos crudos", fill=BLUE_L, color=BLUE, size=13)
    c.pill(1350, 520, 180, "datos preparados", fill=AMBER_L, color=AMBER, size=13)
    c.pill(710, 770, 180, "resultado explicado", fill=PURPLE_L, color=PURPLE, size=13)
    c.pill(70, 520, 190, "decisión registrada", fill=ORANGE_L, color=ORANGE, size=13)

    c.footer("Distinción esencial", "Visualizar muestra evidencia; actuar exige autoridad, criterio, registro y retroalimentación.")
    return c


def make_git_states() -> Canvas:
    c = Canvas(
        "Estados de Git hasta Pull Request y CI",
        "Flujo local, remoto y colaborativo con comandos, evidencia y bucle de corrección.",
    )
    c.header("Mapa 6 de 6", "Git: el archivo cambia de estado, no solo de lugar", "Working tree, staging, commit, remoto, Pull Request, revisión y CI forman una cadena de evidencia")

    zones = [
        (36, 142, 780, 620, "1 · LOCAL", "Lo que ocurre en tu equipo", BLUE, BLUE_L),
        (836, 142, 300, 620, "2 · REMOTO", "La rama publicada", GREEN, GREEN_L),
        (1156, 142, 408, 620, "3 · COLABORACIÓN", "Conversación y control", PURPLE, PURPLE_L),
    ]
    for x, y, w, h, title, subtitle, color, fill in zones:
        c.rect(x, y, w, h, fill=WHITE, stroke=color, sw=1.5, rx=20)
        c.rect(x, y, w, 72, fill=fill, stroke=color, sw=1.5, rx=20)
        c.rect(x, y + 55, w, 17, fill=fill, stroke=fill, sw=0, rx=0)
        c.text(x + 24, y + 32, title, size=20, fill=color, weight=900)
        c.text(x + 24, y + 58, subtitle, size=15, fill=MUTED, weight=500)

    local = [
        (70, 266, 210, 170, "1", "Working tree", ["archivo modificado", "Git ve: M"], BLUE, "editar Markdown"),
        (321, 266, 210, 170, "2", "Staging", ["cambio seleccionado", "Git ve: staged"], AMBER, "git add"),
        (572, 266, 210, 170, "3", "Commit", ["instantánea + autor", "Git ve: hash"], NAVY_2, "git commit"),
    ]
    for x, y, w, h, num, title, body, color, command in local:
        c.card(x, y, w, h, title, body, color, number=num, shadow=True, title_size=18, body_size=16)
        c.pill(x + 20, y + 115, w - 40, command, fill="#EEF3F7", color=color, size=13)
    c.line(280, 351, 321, 351, stroke=AMBER, marker="red")
    c.line(531, 351, 572, 351, stroke=NAVY_2)
    c.card(195, 492, 430, 174, "Rama entrega/sesion2", ["Aísla el trabajo de main", "Conserva una historia revisable"], BLUE, number="0", tag="git switch -c", shadow=False, title_size=19, body_size=16)
    c.line(410, 492, 410, 436, stroke=BLUE, arrow=True)

    c.card(870, 286, 232, 190, "Rama remota", ["origin/entrega/sesion2", "mismos commits publicados"], GREEN, number=4, tag="git push -u", shadow=True, title_size=18, body_size=16)
    c.line(782, 351, 870, 351, stroke=GREEN, marker="green")
    c.card(870, 548, 232, 110, "No es entrega final", ["Todavía falta revisión"], GREEN, shadow=False, title_size=17, body_size=15)

    c.card(1190, 238, 340, 135, "Pull Request", ["propósito + diff + contexto", "base main ← rama"], PURPLE, number=5, shadow=True, title_size=18, body_size=16)
    c.card(1190, 410, 340, 120, "Revisión humana", ["pregunta · ambigüedad · límite"], ORANGE, number=6, shadow=False, title_size=18, body_size=16)
    c.path("M1360 563 L1435 623 L1360 683 L1285 623 Z", stroke=PURPLE, sw=2.5, arrow=False, fill=PURPLE_L)
    c.text(1360, 609, ["7 · CI", "¿validador verde?"], size=17, fill=PURPLE, weight=900, anchor="middle", line_height=1.2)
    c.line(986, 286, 1190, 306, stroke=PURPLE, marker="purple")
    c.line(1360, 373, 1360, 410, stroke=ORANGE, marker="red")
    c.line(1360, 530, 1360, 563, stroke=PURPLE, marker="purple")

    c.path("M1285 623 C1190 748 1080 750 980 750 L230 750 C135 750 125 520 175 436", stroke=RED, sw=3, arrow=True, dash="10 7", marker="red")
    c.pill(560, 775, 430, "SI FALLA: corregir → nuevo commit → push", fill=RED_L, color=RED, size=15)
    c.pill(1435, 604, 105, "SÍ", fill=GREEN_L, color=GREEN, size=14)

    c.footer("Lectura clave", "El historial no se borra cuando hay un error: la corrección agrega nueva evidencia a la misma rama.")
    return c


def browser_shell(c: Canvas, x: int, y: int, w: int, h: int, title: str) -> None:
    c.rect(x, y, w, h, fill=WHITE, stroke=LINE, sw=1.5, rx=16, shadow=True)
    c.rect(x, y, w, 46, fill="#EFF3F6", stroke=LINE, sw=1, rx=16)
    c.rect(x, y + 32, w, 14, fill="#EFF3F6", stroke="#EFF3F6", sw=0, rx=0)
    for i, color in enumerate(["#FF625A", "#FFC04A", "#2BCB4B"]):
        c.circle(x + 24 + i * 24, y + 23, 6, fill=color, stroke=color, sw=0)
    c.text(x + w / 2, y + 29, title, size=14, fill=MUTED, weight=600, anchor="middle")


def make_environment() -> Canvas:
    c = Canvas(
        "Elección del entorno gratuito",
        "Vista de un repositorio privado con rutas de Git local, Codespaces con cuota personal y github.dev.",
    )
    c.header("Guía Git 1 de 4", "Abrir el repositorio y elegir una ruta sostenible", "Primero verifica acceso y propietario; después decide dónde editar y ejecutar")
    browser_shell(c, 42, 142, 1030, 650, "github.com · compras-claras-pareja-XX")
    c.text(72, 222, "ucentral-bigdata-2026-2 / compras-claras-pareja-XX", size=19, fill=INK, weight=800)
    c.pill(72, 246, 90, "Private", fill="#E9EEF2", color=MUTED, size=13)
    for x, label in [(72, "Code"), (160, "Issues"), (245, "Pull requests"), (380, "Actions")]:
        c.text(x, 310, label, size=15, fill=BLUE if label == "Code" else MUTED, weight=700)
    c.line(62, 330, 1048, 330, stroke=LINE, sw=1, arrow=False)
    c.rect(72, 354, 610, 250, fill=WHITE, stroke=LINE, sw=1, rx=10)
    c.text(94, 388, "Files", size=16, fill=INK, weight=800)
    files = [".devcontainer/", ".github/", "data/", "docs/", "resultados/", "scripts/", "README.md"]
    for i, name in enumerate(files):
        yy = 420 + i * 25
        c.text(98, yy, "▣", size=14, fill=BLUE, weight=700)
        c.text(124, yy, name, size=14, fill=INK, weight=550)
    c.rect(742, 350, 285, 50, fill=GREEN, stroke=GREEN, sw=0, rx=10)
    c.text(884, 382, "Code ▾", size=17, fill=WHITE, weight=800, anchor="middle")
    c.rect(696, 414, 350, 330, fill=WHITE, stroke=LINE, sw=1.5, rx=12, shadow=True)
    c.text(720, 450, "Clone", size=18, fill=INK, weight=800)
    c.pill(720, 468, 92, "HTTPS", fill=BLUE_L, color=BLUE, size=13)
    c.pill(820, 468, 110, "Codespaces", fill="#EEF1F4", color=MUTED, size=13)
    c.text(720, 535, "Clone using the web URL", size=14, fill=MUTED, weight=600)
    c.rect(720, 552, 300, 44, fill="#F6F8FA", stroke=LINE, sw=1, rx=7)
    c.text(734, 580, "https://github.com/.../pareja-XX.git", size=12, fill=INK, weight=500, family="Consolas, monospace")
    c.pill(720, 622, 300, "Open with GitHub Desktop", fill="#F6F8FA", color=INK, stroke=LINE, size=13)
    c.text(720, 694, "Tip: pulsa . para abrir github.dev", size=14, fill=AMBER, weight=800)

    c.rect(1100, 142, 458, 650, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1130, 186, "ÁRBOL DE DECISIÓN", size=18, fill=NAVY, weight=900)
    options = [
        (218, "1", "Git local", "Terminal + Python", "siempre gratuito", GREEN, GREEN_L),
        (372, "2", "Codespaces", "Entorno completo", "solo cuota personal", BLUE, BLUE_L),
        (526, "3", "github.dev", "Editor + Source Control", "sin terminal", AMBER, AMBER_L),
    ]
    for y, num, title, body, constraint, color, fill in options:
        c.rect(1128, y, 402, 128, fill=fill, stroke=color, sw=1.5, rx=14)
        c.number_badge(1162, y + 36, num, fill=color, radius=20)
        c.text(1196, y + 38, title, size=19, fill=INK, weight=800)
        c.text(1196, y + 69, body, size=15, fill=MUTED, weight=600)
        c.pill(1196, y + 82, 230, constraint, fill=WHITE, color=color, stroke=color, size=12)
    c.rect(1128, 690, 402, 70, fill=RED_L, stroke=RED, sw=1.5, rx=12)
    c.text(1329, 718, "NO HAGAS UN FORK PÚBLICO", size=15, fill=RED, weight=900, anchor="middle")
    c.text(1329, 744, "confirma cuenta, pareja y repositorio", size=14, fill=INK, weight=600, anchor="middle")

    c.footer("Resultado esperado", "La URL termina en tu pareja y puedes crear una rama; no estás en la plantilla ni en el demo.")
    return c


def make_status_diff() -> Canvas:
    c = Canvas(
        "Lectura de git status y git diff",
        "Terminal con archivos modificados y panel explicativo de estados antes de staging.",
    )
    c.header("Guía Git 2 de 4", "Observar antes de seleccionar: status y diff", "El objetivo no es memorizar colores: es comprobar qué archivo cambió y qué evidencia contiene")

    browser_shell(c, 42, 142, 980, 650, "VS Code · terminal · entrega/sesion2")
    c.rect(60, 198, 944, 568, fill="#101A22", stroke="#101A22", sw=0, rx=10)
    terminal = [
        (238, "$ git branch --show-current", "#75C7FF"),
        (270, "entrega/sesion2", "#EAF1F6"),
        (318, "$ git status --short", "#75C7FF"),
        (350, " M docs/01_proceso_as_is.md", "#FFD166"),
        (380, " M resultados/perfil_secop.md", "#FFD166"),
        (428, "$ git diff -- docs/01_proceso_as_is.md", "#75C7FF"),
        (460, "@@ Proceso AS-IS @@", "#B7C6D2"),
        (492, "- COMPLETAR: cuello de botella", "#FF8178"),
        (524, "+ Consolidación manual: 3 días promedio", "#63E6A0"),
        (554, "+ y 18 % de registros incompletos.", "#63E6A0"),
        (602, "$ git diff --check", "#75C7FF"),
        (634, "# Sin salida: no hay errores de espacios", "#B7C6D2"),
    ]
    for y, line, color in terminal:
        c.text(88, y, line, size=17, fill=color, weight=500, family="Consolas, Cascadia Mono, monospace")
    c.pill(82, 690, 220, "working tree · MODIFICADO", fill="#213746", color="#9EDAFF", size=13)

    c.rect(1050, 142, 508, 650, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1080, 186, "¿QUÉ SABE GIT AHORA?", size=18, fill=NAVY, weight=900)
    states = [
        (222, "1", "Working tree", "2 archivos cambiaron", BLUE, True),
        (332, "2", "Staging", "todavía vacío", AMBER, False),
        (442, "3", "Commit", "todavía no existe", NAVY_2, False),
        (552, "4", "Remoto", "todavía no cambió", GREEN, False),
    ]
    for y, num, title, body, color, active in states:
        fill = BLUE_L if active else "#F6F8FA"
        stroke = color if active else LINE
        c.rect(1080, y, 448, 84, fill=fill, stroke=stroke, sw=2 if active else 1, rx=13)
        c.number_badge(1112, y + 32, num, fill=color if active else MUTED, radius=18)
        c.text(1142, y + 31, title, size=17, fill=INK, weight=800)
        c.text(1142, y + 60, body, size=15, fill=MUTED, weight=550)
        if active:
            c.pill(1375, y + 23, 125, "ESTADO ACTUAL", fill=WHITE, color=BLUE, stroke=BLUE, size=11)

    c.rect(1080, 666, 448, 96, fill=GREEN_L, stroke=GREEN, sw=1.5, rx=13)
    c.text(1104, 697, "DECISIÓN ANTES DE git add", size=15, fill=GREEN, weight=900)
    c.text(1104, 728, ["¿Los dos archivos pertenecen al mismo propósito?", "¿La cifra está explicada y limitada?"], size=15, fill=INK, weight=600, line_height=1.25)

    c.footer("Lectura del diff", "Rojo retira una plantilla; verde propone evidencia. Todavía no hay commit, push ni PR.")
    return c


def make_pull_request() -> Canvas:
    c = Canvas(
        "Pull Request revisable de Compras Claras",
        "Vista de ramas, descripción, archivos, reviewers y check con guía de lectura crítica.",
    )
    c.header("Guía Git 3 de 4", "Pull Request: transformar commits en una explicación", "Un PR de calidad permite reconstruir propósito, evidencia, límites y forma de verificación")

    browser_shell(c, 34, 140, 1130, 660, "github.com · Pull Request #1")
    c.text(64, 214, "Pull requests / #1", size=16, fill=BLUE, weight=700)
    c.text(64, 258, "Compras Claras · arquitectura y ciclo analítico", size=26, fill=INK, weight=800)
    c.pill(64, 278, 84, "Open", fill=GREEN, color=WHITE, size=13)
    c.text(166, 304, "entrega/sesion2 quiere combinar 2 commits en main", size=15, fill=MUTED, weight=550)
    c.line(64, 330, 1134, 330, stroke=LINE, sw=1, arrow=False)

    tabs = [(64, "Conversation"), (185, "Commits 2"), (284, "Checks 1"), (380, "Files changed 4")]
    for x, label in tabs:
        c.text(x, 365, label, size=14, fill=BLUE if label == "Conversation" else MUTED, weight=800 if label == "Conversation" else 600)
    c.line(64, 380, 1134, 380, stroke=LINE, sw=1, arrow=False)

    c.rect(64, 402, 750, 340, fill=WHITE, stroke=LINE, sw=1.2, rx=12)
    c.rect(64, 402, 750, 46, fill="#F6F8FA", stroke=LINE, sw=1, rx=12)
    c.text(88, 432, "Descripción de la pareja", size=15, fill=INK, weight=800)
    body = [
        (480, "Qué se hizo", "Proceso AS-IS, arquitectura TO-BE y ciclo NIST."),
        (545, "Por qué", "Reducir consolidación manual y explicar la prioridad."),
        (610, "Cómo se verificó", "✓ perfilador  ✓ validador  ✓ dos autores"),
        (675, "Límite", "Una alerta prioriza revisión; no demuestra fraude."),
    ]
    for y, title, value in body:
        c.text(90, y, title, size=16, fill=INK, weight=800)
        c.text(90, y + 28, value, size=15, fill=GREEN if title == "Cómo se verificó" else MUTED, weight=550)

    c.rect(844, 402, 290, 92, fill="#F6F8FA", stroke=LINE, sw=1, rx=11)
    c.text(866, 430, "Reviewers", size=14, fill=INK, weight=800)
    c.text(866, 462, "compañero · docente", size=15, fill=MUTED, weight=550)
    c.rect(844, 510, 290, 112, fill=GREEN_L, stroke=GREEN, sw=1, rx=11)
    c.text(866, 540, "Checks", size=14, fill=INK, weight=800)
    c.circle(878, 576, 12, fill=GREEN, stroke=GREEN, sw=0)
    c.text(878, 582, "✓", size=15, fill=WHITE, weight=900, anchor="middle")
    c.text(902, 582, "validar · aprobado", size=15, fill=GREEN, weight=700)
    c.rect(844, 640, 290, 102, fill=PURPLE_L, stroke=PURPLE, sw=1, rx=11)
    c.text(866, 671, "Files changed", size=14, fill=INK, weight=800)
    c.text(866, 706, "4 archivos · +86 −12", size=16, fill=PURPLE, weight=700)

    c.rect(1190, 140, 374, 660, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1218, 184, "CUATRO LECTURAS", size=18, fill=NAVY, weight=900)
    checks = [
        (220, "1", "Ramas correctas", "main ← entrega/sesion2", BLUE, BLUE_L),
        (354, "2", "Propósito reconstruible", "qué · por qué · límite", ORANGE, ORANGE_L),
        (488, "3", "Diff revisable", "sin secretos ni COMPLETAR", PURPLE, PURPLE_L),
        (622, "4", "Revisión atribuible", "comentario + check verde", GREEN, GREEN_L),
    ]
    for y, num, title, body, color, fill in checks:
        c.rect(1218, y, 318, 110, fill=fill, stroke=color, sw=1.5, rx=13)
        c.number_badge(1252, y + 34, num, fill=color, radius=19)
        c.text(1282, y + 34, title, size=16, fill=INK, weight=800)
        c.text(1282, y + 67, body, size=14, fill=MUTED, weight=550)

    c.footer("Criterio docente", "El check verde no reemplaza leer Files changed ni discutir la decisión arquitectónica.")
    return c


def make_actions() -> Canvas:
    c = Canvas(
        "CI verde y revisión humana",
        "Separación entre validación automática de estructura y evaluación humana del sentido empresarial.",
    )
    c.header("Guía Git 4 de 4", "CI verde + revisión humana: dos controles complementarios", "La automatización detecta incumplimientos observables; una persona evalúa sentido, contexto y límites")

    flow = [
        (58, "1", "Push", BLUE), (310, "2", "Workflow", PURPLE),
        (562, "3", "Validador", GREEN), (814, "4", "Revisión", ORANGE),
        (1066, "5", "Listo para integrar", NAVY_2),
    ]
    for x, num, label, color in flow:
        c.rect(x, 140, 220, 76, fill=WHITE, stroke=color, sw=2, rx=14, shadow=True)
        c.number_badge(x + 34, 178, num, fill=color, radius=20)
        c.text(x + 68, 185, label, size=17, fill=INK, weight=800)
    for x, color, marker in [(278, PURPLE, "purple"), (530, GREEN, "green"), (782, ORANGE, "red"), (1034, NAVY_2, "blue")]:
        c.line(x, 178, x + 32, 178, stroke=color, sw=3, marker=marker)
    c.pill(1320, 159, 220, "EVIDENCIA REVISADA", fill=GREEN_L, color=GREEN, size=14)

    c.rect(42, 258, 730, 520, fill=WHITE, stroke=GREEN, sw=2, rx=18, shadow=True)
    c.rect(42, 258, 730, 70, fill=GREEN_L, stroke=GREEN, sw=1, rx=18)
    c.text(72, 300, "A · VALIDACIÓN AUTOMÁTICA", size=21, fill=GREEN, weight=900)
    c.pill(548, 276, 190, "validar · 8 s · PASS", fill=GREEN, color=WHITE, size=13)
    auto_checks = [
        (365, "✓", "Estructura requerida", "README + 3 documentos + perfil"),
        (445, "✓", "Plantillas completas", "no quedan marcadores COMPLETAR"),
        (525, "✓", "Historia mínima", "rama + dos autores + dos commits"),
        (605, "✓", "Controles básicos", "sin secretos evidentes · Mermaid válido"),
    ]
    for y, mark, title, body in auto_checks:
        c.circle(84, y - 7, 18, fill=GREEN, stroke=GREEN, sw=0)
        c.text(84, y, mark, size=19, fill=WHITE, weight=900, anchor="middle")
        c.text(118, y - 5, title, size=17, fill=INK, weight=800)
        c.text(118, y + 24, body, size=15, fill=MUTED, weight=500)
    c.rect(72, 682, 670, 66, fill="#F6F8FA", stroke=LINE, sw=1, rx=12)
    c.text(407, 709, "Puede responder: ¿cumple reglas observables?", size=16, fill=INK, weight=800, anchor="middle")
    c.text(407, 735, "No puede decidir si la arquitectura tiene sentido.", size=15, fill=RED, weight=700, anchor="middle")

    c.rect(804, 258, 754, 520, fill=WHITE, stroke=ORANGE, sw=2, rx=18, shadow=True)
    c.rect(804, 258, 754, 70, fill=ORANGE_L, stroke=ORANGE, sw=1, rx=18)
    c.text(834, 300, "B · REVISIÓN HUMANA", size=21, fill=ORANGE, weight=900)
    human_checks = [
        (365, "1", "Trazabilidad", "¿la herramienta responde a proceso, dato y KPI?"),
        (445, "2", "Plausibilidad", "¿el cuello y la mejora reflejan el caso?"),
        (525, "3", "Responsabilidad", "¿quién valida, decide y registra la acción?"),
        (605, "4", "Límites", "¿evita causalidad o acusaciones no sustentadas?"),
    ]
    for y, num, title, body in human_checks:
        c.number_badge(846, y - 8, num, fill=ORANGE, radius=18)
        c.text(878, y - 5, title, size=17, fill=INK, weight=800)
        c.text(878, y + 24, body, size=15, fill=MUTED, weight=500)
    c.rect(834, 682, 694, 66, fill=AMBER_L, stroke=AMBER, sw=1, rx=12)
    c.text(1181, 709, "Comentario útil: pide una mejora verificable", size=16, fill=INK, weight=800, anchor="middle")
    c.text(1181, 735, "y explica por qué afecta la decisión.", size=15, fill=AMBER, weight=700, anchor="middle")

    c.footer("Puerta de calidad", "Validador local + CI verde + comentario sustantivo; ninguno sustituye a los otros.")
    return c


VISUALS = {
    DIAGRAM_DIR / "01_hilo_decision.svg": make_hilo,
    DIAGRAM_DIR / "02_proceso_as_is.svg": make_as_is,
    DIAGRAM_DIR / "03_puente_analitico.svg": make_bridge,
    DIAGRAM_DIR / "04_arquitectura_to_be.svg": make_architecture,
    DIAGRAM_DIR / "05_ciclo_nist.svg": make_nist,
    DIAGRAM_DIR / "06_estados_git.svg": make_git_states,
    GIT_DIR / "01_entorno_gratuito.svg": make_environment,
    GIT_DIR / "02_status_diff.svg": make_status_diff,
    GIT_DIR / "03_pull_request.svg": make_pull_request,
    GIT_DIR / "04_actions.svg": make_actions,
}


def find_chrome() -> Path | None:
    candidates = [
        os.environ.get("CHROME_PATH"),
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return Path(candidate)
    return None


def render_png(chrome: Path, svg_path: Path) -> None:
    png_path = svg_path.with_suffix(".png")
    command = [
        str(chrome), "--headless=new", "--disable-gpu", "--hide-scrollbars",
        f"--window-size={W},{H}", f"--screenshot={png_path}", svg_path.resolve().as_uri(),
    ]
    subprocess.run(command, check=True, capture_output=True, text=True, timeout=45)
    if not png_path.exists() or png_path.stat().st_size < 10_000:
        raise RuntimeError(f"PNG inválido o ausente: {png_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--svg-only", action="store_true", help="No renderiza PNG con Chrome.")
    args = parser.parse_args()

    for path, builder in VISUALS.items():
        builder().save(path)
        print(f"[SVG] {path.relative_to(ROOT)}")

    if not args.svg_only:
        chrome = find_chrome()
        if not chrome:
            raise SystemExit("No se encontró Chrome. Define CHROME_PATH o usa --svg-only.")
        for path in VISUALS:
            render_png(chrome, path)
            print(f"[PNG] {path.with_suffix('.png').relative_to(ROOT)}")

    print(f"[OK] {len(VISUALS)} láminas generadas en SVG" + ("." if args.svg_only else " y PNG."))


if __name__ == "__main__":
    main()
