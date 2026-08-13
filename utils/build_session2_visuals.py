#!/usr/bin/env python3
"""Genera las láminas visuales de las sesiones combinadas 2 y 3 en SVG y PNG.

El SVG es la fuente pedagógica: usa una gramática visual común, tipografía
legible, márgenes seguros sin desbordes de texto y relaciones explícitas.
El PNG se renderiza con Chrome para Colab.
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
NAVY_DARK = "#0D273E"
NAVY_2 = "#1D4F73"
INK = "#17324D"
MUTED = "#52697C"
LINE = "#B8C8D6"
LINE_LIGHT = "#D4E1EB"
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
    """Constructor SVG con estética enriquecida y componentes reutilizables."""

    def __init__(self, title: str, desc: str):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W} {H}" role="img" aria-labelledby="title desc">',
            f"<title id=\"title\">{html.escape(title)}</title>",
            f"<desc id=\"desc\">{html.escape(desc)}</desc>",
            f"""<defs>
              <linearGradient id="header-grad" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stop-color="{NAVY_DARK}"/>
                <stop offset="100%" stop-color="{NAVY_2}"/>
              </linearGradient>
              <linearGradient id="navy-card-grad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="#184368"/>
                <stop offset="100%" stop-color="#0F2B48"/>
              </linearGradient>
              <linearGradient id="hub-grad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#1C4B72"/>
                <stop offset="100%" stop-color="#0A2238"/>
              </linearGradient>
              <filter id="shadow" x="-10%" y="-10%" width="125%" height="130%">
                <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#0F2B48" flood-opacity="0.09"/>
              </filter>
              <filter id="shadow-lg" x="-15%" y="-15%" width="135%" height="140%">
                <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#0F2B48" flood-opacity="0.14"/>
              </filter>
              <marker id="arrow-blue" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{BLUE}"/>
              </marker>
              <marker id="arrow-red" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{RED}"/>
              </marker>
              <marker id="arrow-green" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{GREEN}"/>
              </marker>
              <marker id="arrow-purple" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{PURPLE}"/>
              </marker>
              <marker id="arrow-orange" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{ORANGE}"/>
              </marker>
              <marker id="arrow-amber" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{AMBER}"/>
              </marker>
              <marker id="arrow-teal" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{TEAL}"/>
              </marker>
              <marker id="arrow-ink" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
                <path d="M0,0 L0,6 L9,3 z" fill="{INK}"/>
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
        line_height=1.25, family="Inter, -apple-system, Segoe UI, Arial, sans-serif", italic=False,
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

    def pill(self, x, y, w, label, fill=BLUE_L, color=BLUE, stroke=None, size=13) -> None:
        self.rect(x, y, w, 36, fill=fill, stroke=stroke or fill, sw=1.5, rx=18)
        self.text(x + w / 2, y + 23, label, size=size, fill=color, weight=800, anchor="middle")

    def number_badge(self, cx, cy, number, fill=BLUE, radius=20) -> None:
        self.circle(cx, cy, radius, fill=fill, stroke=fill, sw=1)
        self.text(cx, cy + 6, str(number), size=18, fill=WHITE, weight=900, anchor="middle")

    def header(self, index: str, title: str, subtitle: str) -> None:
        self.rect(0, 0, W, 114, fill="url(#header-grad)", stroke=NAVY_DARK, sw=0, rx=0)
        self.line(0, 114, W, 114, stroke="#2F6FB0", sw=2, arrow=False)
        self.pill(1376, 24, 176, index.upper(), fill="#214E6D", color="#D9EFFB", stroke="#3F769C", size=14)
        title_size = 26 if len(title) > 62 else 28 if len(title) > 50 else 31
        subtitle_size = 15 if len(subtitle) > 92 else 17
        self.text(48, 48, title, size=title_size, fill=WHITE, weight=800)
        self.text(48, 80, subtitle, size=subtitle_size, fill="#D1E6F5", weight=400)

    def footer(self, label: str, text: str, color=NAVY, fill="#E7EFF5") -> None:
        self.rect(48, 836, 1504, 44, fill=fill, stroke="#D0DFEA", sw=1.5, rx=14)
        self.rect(52, 840, max(170, len(label) * 11 + 30), 36, fill=color, stroke=color, sw=0, rx=11)
        self.text(52 + max(170, len(label) * 11 + 30) / 2, 863, label.upper(), size=14, fill=WHITE, weight=900, anchor="middle")
        text_x = max(240, 52 + len(label) * 11 + 45)
        self.text(text_x, 863, text, size=16, fill=INK, weight=600)

    def card(
        self, x, y, w, h, title, body, accent=BLUE, fill=WHITE, number=None,
        tag=None, shadow=True, title_size=18, body_size=15,
    ) -> None:
        self.rect(x, y, w, h, fill=fill, stroke=LINE_LIGHT, sw=1.5, rx=16, shadow=shadow)
        self.rect(x, y, 8, h, fill=accent, stroke=accent, sw=0, rx=4)
        title_x = x + 24
        if number is not None:
            self.number_badge(x + 30, y + 36, number, fill=accent, radius=17)
            title_x = x + 58
        self.text(title_x, y + 42, title, size=title_size, fill=INK, weight=800)
        if tag:
            tag_w = min(w - 44, max(180, len(tag) * 8 + 24))
            self.pill(x + 22, y + 62, tag_w, tag, fill=fill, color=accent, stroke=accent, size=11.5)
            body_y = y + 124
        else:
            body_y = y + 78
        self.text(x + 24, body_y, body, size=body_size, fill=MUTED, weight=500, line_height=1.35)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.parts + ["</svg>"]), encoding="utf-8")


def make_hilo() -> Canvas:
    c = Canvas(
        "Hilo conductor de Compras Claras",
        "Trazabilidad desde una decisión empresarial hasta la acción humana y la mejora del proceso.",
    )
    c.header("Mapa 1 de 7", "La historia completa: de la decisión a la mejora", "Cada componente existe porque responde una pregunta anterior del negocio")

    # Columna izquierda: Punto de partida (Laura)
    c.rect(42, 140, 324, 664, fill="url(#navy-card-grad)", stroke="#2A5878", sw=1.5, rx=22, shadow=True)
    c.pill(70, 168, 165, "PUNTO DE PARTIDA", fill="#214E6D", color="#D9EFFB", stroke="#4E7B99", size=13)
    c.text(70, 236, ["Laura", "Analista de", "seguimiento"], size=25, fill=WHITE, weight=800, line_height=1.18)
    c.text(70, 322, ["Necesita decidir:", "¿qué contratos", "revisar primero?"], size=23, fill="#FFFFFF", weight=700, line_height=1.2)

    c.rect(66, 452, 276, 150, fill="#153650", stroke="#3F6B8A", sw=1, rx=14)
    c.text(86, 484, "Criterio de éxito", size=16, fill="#BFE4F6", weight=800)
    c.text(86, 520, ["menos tiempo para priorizar", "sin acusar ni automatizar", "la decisión humana"], size=15, fill=WHITE, weight=500, line_height=1.35)

    c.rect(66, 626, 276, 126, fill="#10263A", stroke="#3F6B8A", sw=1, rx=14)
    c.text(86, 658, "Regla de diseño", size=16, fill="#F7CCBE", weight=800)
    c.text(86, 694, ["primero propósito;", "después herramienta"], size=17, fill=WHITE, weight=700, line_height=1.3)

    # Fila superior de tarjetas 1, 2, 3
    c.card(406, 150, 334, 232, "Proceso AS-IS", ["Seguimiento contractual", "Actores + tareas + decisiones", "Cuello: consolidación manual"], BLUE, number=1, tag="¿DÓNDE SE DEMORA?")
    c.card(784, 150, 334, 232, "Roles y relevos", ["Negocio define valor", "Gobierno protege significado", "Datos y BI construyen evidencia"], AMBER, number=2, tag="¿QUIÉN RESPONDE?")
    c.card(1162, 150, 392, 232, "Datos y evidencia", ["Origen + significado + calidad", "SECOP + perfil reproducible", "Cada campo tiene responsable"], PURPLE, number=3, tag="¿QUÉ NECESITAMOS SABER?", title_size=18)

    # Fila inferior de tarjetas 4, 5 y Atajo
    c.card(1162, 498, 392, 232, "Ciclo de evidencia", ["Capturar · preparar · analizar", "Visualizar · actuar · registrar", "KPI y controles en cada etapa"], GREEN, number=4, tag="¿CÓMO LLEGA A LA ACCIÓN?")
    c.card(784, 498, 334, 232, "Acción humana", ["Revisar contexto contractual", "Corregir · escalar · descartar", "Registrar motivo y resultado"], ORANGE, number=5, tag="¿QUIÉN DECIDE?")

    c.card(406, 498, 334, 232, "Conversación versionada", ["Propuesta + objeción + corrección", "PR conserva el porqué", "CI ayuda; personas validan"], RED, number=6, tag="¿CÓMO APRENDE EL EQUIPO?", title_size=18)

    # Conectores y flechas
    c.line(366, 274, 406, 274, stroke=BLUE, marker="blue")
    c.line(740, 266, 784, 266, stroke=BLUE, marker="blue")
    c.line(1118, 266, 1162, 266, stroke=AMBER, marker="amber")
    c.line(1358, 382, 1358, 498, stroke=PURPLE, marker="purple")
    c.line(1162, 614, 1118, 614, stroke=GREEN, marker="green")
    c.line(784, 614, 740, 614, stroke=ORANGE, marker="orange")

    # Bucle de retroalimentación
    c.path("M406 614 C370 614 390 780 573 780 C748 780 748 430 508 382", stroke=ORANGE, sw=3, arrow=True, dash="8 6", marker="orange")
    c.pill(450, 762, 330, "CONVERSACIÓN → PROCESO MEJORADO", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=12.5)

    c.footer("Lectura clave", "La arquitectura es una cadena de justificaciones, no una colección de productos.")
    return c


def make_as_is() -> Canvas:
    c = Canvas(
        "Proceso AS-IS de seguimiento contractual",
        "Proceso con tres carriles, datos producidos, validación, cuello de botella y bucle de retrabajo.",
    )
    c.header("Mapa 2 de 7", "Proceso AS-IS: dónde nace el retraso", "Carriles por responsable · artefactos de datos · decisión de completitud · retrabajo explícito")

    # Carriles con títulos divididos en dos líneas para evitar desborde
    lanes = [
        (140, 235, ["ENTIDAD", "CONTRATANTE"], ["Origina y actualiza", "el proceso"], BLUE, BLUE_L),
        (390, 185, ["PLATAFORMA", "SECOP"], ["Registra y publica", "eventos"], AMBER, AMBER_L),
        (590, 225, ["OFICINA DE", "SEGUIMIENTO"], ["Consolida, prioriza", "y revisa"], PURPLE, PURPLE_L),
    ]
    for y, h, title, subtitle, color, fill in lanes:
        c.rect(34, y, 1532, h, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
        c.rect(34, y, 204, h, fill=fill, stroke=color, sw=1.5, rx=16)
        c.text(56, y + 42, title, size=15, fill=color, weight=900, line_height=1.2)
        c.text(56, y + 86, subtitle, size=14, fill=MUTED, weight=500, line_height=1.25)

    # Entidad contratante (Paso 1 a 5)
    steps = [
        (268, "1", "Definir necesidad", "objeto + responsable", BLUE),
        (520, "2", "Publicar proceso", "fecha + modalidad", BLUE),
        (772, "3", "Evaluar ofertas", "criterios + resultado", BLUE),
        (1024, "4", "Formalizar contrato", "proveedor + valor", BLUE),
        (1276, "5", "Reportar ejecución", "estado + fechas", ORANGE),
    ]
    for x, num, title, artifact, color in steps:
        c.rect(x, 180, 218, 112, fill=WHITE, stroke=color, sw=2, rx=14, shadow=True)
        c.number_badge(x + 28, 208, num, fill=color, radius=16)
        c.text(x + 52, 214, title, size=14.5, fill=INK, weight=800)
        c.pill(x + 14, 244, 190, artifact, fill=BLUE_L if color == BLUE else ORANGE_L, color=color, size=11.5)
    for x in [486, 738, 990, 1242]:
        c.line(x, 236, x + 34, 236, stroke=BLUE, marker="blue")

    # Plataforma SECOP (Paso 6 a 8)
    c.card(290, 423, 310, 118, "6 · Recibir evento", ["API / formulario", "marca de tiempo operacional"], AMBER, shadow=False, title_size=17, body_size=14.5)
    c.card(680, 423, 310, 118, "7 · Guardar registro", ["fila operacional", "historial publicado"], AMBER, shadow=False, title_size=17, body_size=14.5)
    c.card(1070, 423, 340, 118, "8 · Exponer consulta", ["archivos / API pública", "sin vista consolidada"], AMBER, shadow=False, title_size=17, body_size=14.5)
    c.line(600, 482, 680, 482, stroke=AMBER, marker="amber")
    c.line(990, 482, 1070, 482, stroke=AMBER, marker="amber")

    # Flecha Paso 5 -> SECOP
    c.path("M1385 292 L1385 382 C1385 405 1370 423 1345 423", stroke=ORANGE, marker="orange")
    c.pill(1200, 342, 285, "reportes periódicos y novedades", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=12)

    # Oficina de seguimiento (Paso 9 a 13)
    office_cards = [
        (270, "9 · Descargar", ["CSV por fuente", "cortes desarticulados"], PURPLE),
        (520, "10 · Consolidar", ["unir + limpiar", "trabajo manual lento"], RED),
        (1070, "12 · Priorizar", ["lista preliminar", "reglas locales"], GREEN),
        (1320, "13 · Revisar", ["contexto + decisión", "resultado registrado"], ORANGE),
    ]
    for x, title, body, color in office_cards:
        c.card(x, 640, 210, 125, title, body, color, shadow=False, title_size=16, body_size=14)

    c.line(480, 702, 520, 702, stroke=PURPLE, marker="purple")
    c.line(730, 702, 785, 702, stroke=RED, marker="red")
    c.line(995, 702, 1070, 702, stroke=GREEN, marker="green")
    c.line(1280, 702, 1320, 702, stroke=GREEN, marker="green")

    # Flujo de datos SECOP 8 -> Oficina 9
    c.path("M1240 541 C1240 580 430 540 375 640", stroke=PURPLE, sw=2.5, arrow=True, dash="6 5", marker="purple")
    c.pill(580, 562, 290, "descarga de CSVs desarticulados", fill=PURPLE_L, color=PURPLE, stroke=PURPLE, size=12)

    # Gateway de completitud (Paso 11)
    c.path("M890 622 L995 702 L890 782 L785 702 Z", stroke=AMBER, sw=3, arrow=False, fill=AMBER_L)
    c.text(890, 684, ["11 · ¿Fechas y", "campos completos?"], size=16, fill=INK, weight=800, anchor="middle", line_height=1.2)
    c.pill(985, 655, 65, "SÍ", fill=GREEN_L, color=GREEN, stroke=GREEN, size=13)

    # Bucle de retrabajo: NO -> devolver a entidad
    c.path("M890 622 C890 570 850 555 820 541", stroke=RED, sw=3, arrow=True, dash="8 6", marker="red")
    c.path("M820 541 C820 360 1390 365 1390 292", stroke=RED, sw=3, arrow=True, dash="8 6", marker="red")
    c.pill(820, 375, 360, "NO · solicitar corrección y esperar nuevo corte", fill=RED_L, color=RED, stroke=RED, size=12)

    # Destaque de cuello de botella
    c.rect(505, 606, 240, 180, fill="none", stroke=RED, sw=3.5, rx=18, dash="10 6")
    c.pill(495, 590, 260, "CUELLO DE BOTELLA MANUAL", fill=RED, color=WHITE, size=12.5)

    # Métricas y KPIs inferiores
    c.pill(270, 786, 275, "KPI · tiempo de consolidación", fill=PURPLE_L, color=PURPLE, stroke=PURPLE, size=12.5)
    c.pill(566, 786, 270, "KPI · % datos completos", fill=AMBER_L, color=AMBER, stroke=AMBER, size=12.5)
    c.pill(857, 786, 260, "KPI · casos priorizados", fill=GREEN_L, color=GREEN, stroke=GREEN, size=12.5)

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

    # 3 Zonas de lectura superiores
    c.rect(40, 136, 248, 78, fill=BLUE_L, stroke=BLUE, sw=1.5, rx=16)
    c.text(60, 164, "1 · OPERACIÓN", size=17, fill=BLUE, weight=900)
    c.text(60, 192, ["registrar sin detener", "el proceso"], size=13, fill=MUTED, weight=600, line_height=1.2)

    c.rect(308, 136, 674, 78, fill=AMBER_L, stroke=AMBER, sw=1.5, rx=16)
    c.text(330, 166, "2 · INTEGRACIÓN", size=17, fill=AMBER, weight=900)
    c.text(330, 194, "elegir ETL, ELT o un híbrido según la restricción", size=13.5, fill=MUTED, weight=600)

    c.rect(1002, 136, 556, 78, fill=PURPLE_L, stroke=PURPLE, sw=1.5, rx=16)
    c.text(1024, 166, "3 · CONSUMO Y ACCIÓN", size=17, fill=PURPLE, weight=900)
    c.text(1024, 194, "integrar historia, comparar y decidir", size=13.5, fill=MUTED, weight=600)

    # Fuente OLTP
    c.rect(40, 244, 248, 404, fill=WHITE, stroke=BLUE, sw=2.5, rx=18, shadow=True)
    c.pill(62, 266, 84, "OLTP", fill=BLUE, color=WHITE, size=15)
    c.text(62, 330, ["Evento operacional", "que no puede esperar"], size=18, fill=NAVY, weight=900, line_height=1.2)
    c.text(62, 420, ["• contrato publicado", "• estado actualizado", "• avance reportado"], size=14.5, fill=INK, weight=600, line_height=1.55)
    c.rect(62, 542, 204, 82, fill=BLUE_L, stroke=BLUE, sw=1, rx=12)
    c.text(76, 568, "ARTEFACTO ORIGEN", size=11.5, fill=BLUE, weight=900)
    c.text(76, 592, "transacción + versión", size=14.5, fill=INK, weight=800)
    c.text(76, 612, "alta concurrencia", size=12.5, fill=MUTED, weight=500)

    # Marco central de Integración
    c.rect(308, 234, 674, 430, fill=WHITE, stroke=LINE, sw=1.5, rx=18)
    c.pill(410, 248, 470, "MISMA E · DISTINTO ORDEN DE T Y L", fill=NAVY, color=WHITE, size=13.5)

    # Carril ETL (Amber)
    c.rect(328, 298, 634, 156, fill="#FFFDF5", stroke=AMBER, sw=2, rx=16)
    c.pill(346, 318, 82, "ETL", fill=AMBER, color=WHITE, size=15)
    etl_steps = [
        (452, "E", "Extraer", ["snapshot +", "metadatos"], BLUE, BLUE_L),
        (618, "T", "Transformar", ["validar y", "enmascarar"], ORANGE, ORANGE_L),
        (784, "L", "Cargar", ["tabla curada", "final"], GREEN, GREEN_L),
    ]
    for x, letter, title, artefact, color, fill in etl_steps:
        c.rect(x, 314, 144, 114, fill=fill, stroke=color, sw=1.5, rx=14)
        c.number_badge(x + 22, 338, letter, fill=color, radius=16)
        c.text(x + 44, 342, title, size=13, fill=color, weight=900)
        c.text(x + 14, 384, artefact, size=11, fill=INK, weight=600, line_height=1.2)
    c.line(596, 370, 618, 370, stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.line(762, 370, 784, 370, stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.text(346, 436, "La política y limpieza actúan ANTES de llegar al destino compartido.", size=12, fill=MUTED, weight=600)

    # Carril ELT (Purple)
    c.rect(328, 474, 634, 172, fill="#F8F6FF", stroke=PURPLE, sw=2, rx=16)
    c.pill(346, 494, 82, "ELT", fill=PURPLE, color=WHITE, size=15)
    elt_steps = [
        (452, "E", "Extraer", ["snapshot +", "metadatos"], BLUE, BLUE_L),
        (618, "L", "Cargar", ["Raw / Bronze", "(zona protegida)"], PURPLE, PURPLE_L),
        (784, "T", "Transformar", ["SQL en destino", "(Silver / Gold)"], TEAL, TEAL_L),
    ]
    for x, letter, title, artefact, color, fill in elt_steps:
        c.rect(x, 490, 144, 120, fill=fill, stroke=color, sw=1.5, rx=14)
        c.number_badge(x + 22, 514, letter, fill=color, radius=16)
        c.text(x + 44, 518, title, size=13, fill=color, weight=900)
        c.text(x + 14, 558, artefact, size=11, fill=INK, weight=600, line_height=1.2)
    c.line(596, 548, 618, 548, stroke=PURPLE, sw=2.5, arrow=True, marker="purple")
    c.line(762, 548, 784, 548, stroke=PURPLE, sw=2.5, arrow=True, marker="purple")
    c.text(346, 628, "Acceso gobernado y retención protegen lo Raw; la T se ejecuta in-engine.", size=12, fill=MUTED, weight=600)

    # Bifurcación desde OLTP
    c.path("M288 446 C330 446 330 370 450 370", stroke=BLUE, sw=2.5, arrow=True, marker="blue")
    c.path("M288 446 C330 446 330 548 450 548", stroke=BLUE, sw=2.5, arrow=True, marker="blue")

    # Cadena analítica derecha
    analytic_cards = [
        (1012, 244, 250, 172, "Warehouse", "historia integrada", "hechos + dimensiones", GREEN, GREEN_L),
        (1292, 244, 250, 172, "Data Mart", "vista de seguimiento", "métricas aprobadas", TEAL, TEAL_L),
        (1012, 464, 250, 172, "OLAP / BI", "comparar y explorar", "medida × dimensión", PURPLE, PURPLE_L),
        (1292, 464, 250, 172, "Acción humana", "priorizar revisión", "motivo explicable", ORANGE, ORANGE_L),
    ]
    for x, y, w, h, title, purpose, artefact, color, fill in analytic_cards:
        c.rect(x, y, w, h, fill=WHITE, stroke=color, sw=2, rx=16, shadow=True)
        c.rect(x, y, w, 46, fill=color, stroke=color, sw=0, rx=16)
        c.rect(x, y + 32, w, 14, fill=color, stroke=color, sw=0, rx=0)
        c.text(x + 20, y + 30, title, size=16.5, fill=WHITE, weight=900)
        c.text(x + 20, y + 80, purpose, size=14.5, fill=INK, weight=800)
        c.pill(x + 18, y + 108, w - 36, artefact, fill=fill, color=color, stroke=color, size=11.5)

    c.line(1262, 330, 1290, 330, stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.path("M1417 416 C1417 442 1250 444 1137 464", stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.line(1262, 550, 1290, 550, stroke=INK, sw=2.5, arrow=True, marker="ink")
    c.path("M928 370 C972 370 980 330 1010 330", stroke=AMBER, sw=2.5, arrow=True, marker="amber")
    c.path("M928 548 C976 548 978 376 1010 354", stroke=PURPLE, sw=2.5, arrow=True, marker="purple")

    # Retroalimentación a OLTP
    c.path("M1417 636 C1417 682 1180 688 854 688 L176 688 C108 688 106 652 106 648", stroke=ORANGE, sw=2.5, arrow=True, dash="8 6", marker="orange")
    c.pill(626, 671, 348, "acción → nueva transacción OLTP", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=12.5)

    # Barra de Controles transversales
    c.rect(40, 716, 1518, 74, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
    c.text(64, 748, "CONTROLES EN AMBAS RUTAS", size=14, fill=NAVY, weight=900)
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
        c.pill(x, 734, width, label, fill=fill, color=color, stroke=color, size=12.5)

    c.footer("Decisión de diseño", "ETL si T debe ocurrir antes del destino; ELT si el destino puede gobernar raw y ejecutar T; híbrido cuando la restricción lo exige.")
    return c


def make_adoption() -> Canvas:
    c = Canvas(
        "Motivación y preparación para adoptar Big Data",
        "Mapa desde una brecha empresarial medible hasta una decisión incremental de adopción.",
    )
    c.header(
        "Mapa 3 de 7",
        "Adopción: primero demostrar valor y preparación",
        "Una necesidad importante no basta: datos, proceso, personas, gobierno y viabilidad deben sostenerla",
    )

    # Flujo principal detrás de las tarjetas.
    c.line(318, 332, 350, 332, stroke=BLUE, sw=3, marker="blue")
    c.line(1140, 332, 1180, 332, stroke=PURPLE, sw=3, marker="purple")

    # Brecha empresarial.
    c.rect(38, 146, 280, 640, fill="url(#navy-card-grad)", stroke="#2A5878", sw=1.5, rx=22, shadow=True)
    c.pill(64, 170, 208, "MOTIVACIÓN", fill="#214E6D", color="#D9EFFB", stroke="#4E7B99", size=13)
    c.text(64, 236, ["La revisión llega", "tres días tarde"], size=25, fill=WHITE, weight=850, line_height=1.2)
    c.text(64, 316, ["Decisión:", "¿qué caso revisar", "primero?"], size=20, fill="#D7EBF7", weight=700, line_height=1.25)
    c.rect(60, 430, 236, 126, fill="#153650", stroke="#3F6B8A", sw=1, rx=14)
    c.text(80, 462, "KPI de valor", size=15, fill="#BFE4F6", weight=900)
    c.text(80, 500, ["tiempo actualización", "→ primera revisión"], size=16, fill=WHITE, weight=650, line_height=1.25)
    c.rect(60, 586, 236, 148, fill="#10263A", stroke="#3F6B8A", sw=1, rx=14)
    c.text(80, 618, "NO ES MOTIVACIÓN", size=14, fill="#F7CCBE", weight=900)
    c.text(80, 658, ["“usar Big Data”", "“comprar una nube”", "“copiar a otra entidad”"], size=15, fill=WHITE, weight=600, line_height=1.3)

    # Seis puertas de preparación.
    gates = [
        (350, 158, "1 · VALOR", ["brecha + decisión", "KPI + patrocinador"], ORANGE, ORANGE_L),
        (620, 158, "2 · DATOS", ["fuente + significado", "calidad + permiso"], AMBER, AMBER_L),
        (890, 158, "3 · PROCESO", ["acción posterior", "SLA + retroalimentación"], BLUE, BLUE_L),
        (350, 362, "4 · PERSONAS", ["dueño + usuario", "habilidad + operación"], PURPLE, PURPLE_L),
        (620, 362, "5 · GOBIERNO", ["riesgo + privacidad", "linaje + control"], RED, RED_L),
        (890, 362, "6 · VIABILIDAD", ["capacidad + plazo", "costo + alternativa"], GREEN, GREEN_L),
    ]
    for x, y, title, body, color, fill in gates:
        c.rect(x, y, 250, 164, fill=WHITE, stroke=color, sw=2, rx=16, shadow=True)
        c.rect(x, y, 250, 45, fill=color, stroke=color, sw=0, rx=16)
        c.rect(x, y + 32, 250, 13, fill=color, stroke=color, sw=0, rx=0)
        c.text(x + 18, y + 29, title, size=15.5, fill=WHITE, weight=900)
        c.text(x + 20, y + 88, body, size=14.5, fill=INK, weight=650, line_height=1.35)
        c.pill(x + 20, y + 126, 210, "EVIDENCIA, NO PROMESA", fill=fill, color=color, stroke=color, size=10.5)

    # Salidas posibles: no todas implican Big Data.
    c.rect(1180, 158, 380, 368, fill=WHITE, stroke=PURPLE, sw=2, rx=20, shadow=True)
    c.rect(1180, 158, 380, 66, fill=PURPLE, stroke=PURPLE, sw=0, rx=20)
    c.rect(1180, 210, 380, 14, fill=PURPLE, stroke=PURPLE, sw=0, rx=0)
    c.text(1370, 198, "DECISIÓN DE PORTAFOLIO", size=17, fill=WHITE, weight=900, anchor="middle")
    outcomes = [
        (246, "MEJORAR BI ACTUAL", "si satisface el caso", GREEN, GREEN_L),
        (334, "EXPERIMENTAR", "si falta evidencia", AMBER, AMBER_L),
        (422, "ESCALAR O DETENER", "según resultado y riesgo", ORANGE, ORANGE_L),
    ]
    for y, title, subtitle, color, fill in outcomes:
        c.rect(1206, y, 328, 68, fill=fill, stroke=color, sw=1.5, rx=13)
        c.text(1226, y + 28, title, size=14.5, fill=color, weight=900)
        c.text(1226, y + 50, subtitle, size=12.5, fill=INK, weight=600)

    # Ruta incremental.
    c.text(350, 580, "RUTA INCREMENTAL", size=15, fill=NAVY, weight=900)
    phases = [
        (350, "A · HIPÓTESIS", ["línea base", "criterio de éxito"], BLUE),
        (620, "B · EXPERIMENTO", ["muestra segura", "costo acotado"], AMBER),
        (890, "C · DECISIÓN", ["continuar · ajustar", "o detener"], GREEN),
    ]
    for x, title, body, color in phases:
        c.card(x, 606, 250, 170, title, body, color, shadow=False, title_size=16, body_size=14.5)
    c.line(600, 690, 620, 690, stroke=AMBER, sw=2.5, marker="amber")
    c.line(870, 690, 890, 690, stroke=GREEN, sw=2.5, marker="green")
    c.path("M1180 498 C1140 566 1125 646 1140 690", stroke=PURPLE, sw=2.5, arrow=True, dash="7 5", marker="purple")

    c.footer("Criterio de adopción", "Big Data se justifica cuando una evidencia muestra que la capacidad actual no cumple la decisión, el SLA o el riesgo aceptable.")
    return c


def make_use_cases() -> Canvas:
    c = Canvas(
        "BI tradicional frente a capacidades Big Data",
        "Comparación basada en requisitos del caso de uso, con umbrales y veredicto proporcional.",
    )
    c.header(
        "Mapa 4 de 7",
        "Caso de uso: decidir cuándo BI es suficiente",
        "La etiqueta tecnológica llega después de usuario, decisión, frecuencia, evidencia, acción y KPI",
    )

    # Panel izquierdo: BI suficiente.
    c.rect(38, 146, 406, 642, fill=WHITE, stroke=GREEN, sw=2, rx=20, shadow=True)
    c.rect(38, 146, 406, 74, fill=GREEN, stroke=GREEN, sw=0, rx=20)
    c.rect(38, 204, 406, 16, fill=GREEN, stroke=GREEN, sw=0, rx=0)
    c.text(241, 188, "BI GOBERNADA ES SUFICIENTE", size=17, fill=WHITE, weight=900, anchor="middle")
    left_items = [
        (250, "DATOS", "estructurados y definidos"),
        (338, "LATENCIA", "horas, días o cierre"),
        (426, "ANÁLISIS", "KPI, tendencia, diagnóstico"),
        (514, "OPERACIÓN", "equipo y costo sostenibles"),
    ]
    for y, title, body in left_items:
        c.rect(68, y, 346, 70, fill=GREEN_L, stroke=GREEN, sw=1.2, rx=13)
        c.text(88, y + 27, title, size=13.5, fill=GREEN, weight=900)
        c.text(88, y + 51, body, size=14, fill=INK, weight=600)
    c.rect(68, 628, 346, 116, fill="#F6FBF8", stroke=GREEN, sw=1.5, rx=14)
    c.text(88, 660, "VEREDICTO COMPRAS CLARAS", size=13, fill=GREEN, weight=900)
    c.text(88, 696, ["lote diario + Python + BI", "sirven para el primer hito"], size=15, fill=INK, weight=700, line_height=1.25)

    # Panel derecho: condiciones para ampliar capacidad.
    c.rect(1156, 146, 406, 642, fill=WHITE, stroke=PURPLE, sw=2, rx=20, shadow=True)
    c.rect(1156, 146, 406, 74, fill=PURPLE, stroke=PURPLE, sw=0, rx=20)
    c.rect(1156, 204, 406, 16, fill=PURPLE, stroke=PURPLE, sw=0, rx=0)
    c.text(1359, 188, "CAPACIDAD BIG DATA JUSTIFICADA", size=16.5, fill=WHITE, weight=900, anchor="middle")
    right_items = [
        (250, "VARIEDAD", "texto, eventos, sensores o imágenes"),
        (338, "LATENCIA", "minutos o segundos cambian la acción"),
        (426, "ESCALA", "capacidad actual incumple SLA/costo"),
        (514, "MÉTODO", "distribución o análisis especializado"),
    ]
    for y, title, body in right_items:
        c.rect(1186, y, 346, 70, fill=PURPLE_L, stroke=PURPLE, sw=1.2, rx=13)
        c.text(1206, y + 27, title, size=13.5, fill=PURPLE, weight=900)
        c.text(1206, y + 51, body, size=13.5, fill=INK, weight=600)
    c.rect(1186, 628, 346, 116, fill="#FAF8FD", stroke=PURPLE, sw=1.5, rx=14)
    c.text(1206, 660, "CONDICIÓN PARA ESCALAR", size=13, fill=PURPLE, weight=900)
    c.text(1206, 696, ["umbral medido + riesgo", "+ beneficio operacional"], size=15, fill=INK, weight=700, line_height=1.25)

    # Núcleo del caso de uso.
    c.rect(490, 150, 620, 242, fill="url(#hub-grad)", stroke=BLUE, sw=2.5, rx=22, shadow=True)
    c.pill(680, 172, 240, "CASO DE USO", fill="#214E6D", color=WHITE, stroke="#4E7B99", size=13)
    c.text(800, 238, "COMPRAS CLARAS", size=24, fill=WHITE, weight=900, anchor="middle")
    c.text(800, 286, ["Usuario: analista de seguimiento", "Decisión: qué revisar primero", "Acción: revisar · corregir · escalar"], size=16, fill="#D7EBF7", weight=600, anchor="middle", line_height=1.35)
    c.pill(620, 344, 360, "KPI: tiempo hasta primera revisión", fill="#173C5A", color="#BFE4F6", stroke="#4E7B99", size=13)

    # Puertas de evidencia en el centro.
    criteria = [
        (490, 424, "1 · TIEMPO", "¿qué latencia cambia la decisión?", BLUE, BLUE_L),
        (810, 424, "2 · ESCALA", "¿qué capacidad incumple el SLA?", AMBER, AMBER_L),
        (490, 532, "3 · VARIEDAD", "¿qué fuente agrega valor necesario?", PURPLE, PURPLE_L),
        (810, 532, "4 · OPERACIÓN", "¿quién recupera fallos y controla costo?", TEAL, TEAL_L),
        (490, 640, "5 · RIESGO", "¿qué acceso, límite y trazabilidad?", RED, RED_L),
        (810, 640, "6 · VALOR", "¿qué KPI mejora frente a la línea base?", GREEN, GREEN_L),
    ]
    for x, y, title, body, color, fill in criteria:
        c.rect(x, y, 300, 88, fill=fill, stroke=color, sw=1.5, rx=13)
        c.text(x + 18, y + 29, title, size=13.5, fill=color, weight=900)
        c.text(x + 18, y + 58, body, size=12.5, fill=INK, weight=600)

    # Flechas de decisión.
    c.path("M490 356 C455 385 438 420 438 470", stroke=GREEN, sw=3, arrow=True, marker="green")
    c.path("M1110 356 C1145 385 1162 420 1162 470", stroke=PURPLE, sw=3, arrow=True, marker="purple")
    c.pill(610, 756, 380, "ELEGIR LO SUFICIENTE · MEDIR · REEVALUAR", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=13)

    c.footer("Regla de decisión", "Big Data amplía la BI solo cuando un requisito medido demuestra que la alternativa actual dejó de ser suficiente.")
    return c


def make_architecture() -> Canvas:
    c = Canvas(
        "Arquitectura empresarial objetivo de Compras Claras",
        "Blueprint por capas con trazabilidad vertical, capacidades, herramientas y controles transversales.",
    )
    c.header("Mapa 5 de 7", "Arquitectura TO-BE: cuatro dominios, una misma decisión", "La trazabilidad baja desde negocio hasta tecnología y vuelve con restricciones verificables")

    # Controles transversales superiores
    c.text(48, 144, "CONTROLES TRANSVERSALES", size=15, fill=NAVY, weight=900)
    controls = [
        (306, 174, "gobierno", PURPLE_L, PURPLE),
        (496, 174, "seguridad", RED_L, RED),
        (686, 174, "privacidad", ORANGE_L, ORANGE),
        (876, 210, "observabilidad", TEAL_L, TEAL),
        (1102, 174, "costos", GREEN_L, GREEN),
        (1292, 246, "calidad + linaje", AMBER_L, AMBER),
    ]
    for x, w, label, fill, color in controls:
        c.pill(x, 124, w, label, fill=fill, color=color, stroke=color, size=13)

    layers = [
        (184, 140, "1 · NEGOCIO", "por qué y quién", ORANGE, ORANGE_L),
        (338, 140, "2 · INFORMACIÓN", "qué significa", AMBER, AMBER_L),
        (492, 140, "3 · APLICACIONES", "qué capacidad", BLUE, BLUE_L),
        (646, 164, "4 · TECNOLOGÍA", "dónde se ejecuta", GREEN, GREEN_L),
    ]
    layer_cards = [
        [
            ("Decisión", "priorizar revisión"), ("Proceso TO-BE", "seguimiento + SLA"),
            ("Responsable", "dueño + usuario"), ("KPI", "tiempo + cobertura"),
        ],
        [
            ("Fuentes", "SECOP + internos"), ("Entidades", "contrato · entidad"),
            ("Reglas", "data steward"), ("Diseño de datos", "arquitecto + linaje"),
        ],
        [
            ("Integración", "ingeniería de datos"), ("Calidad", "steward + pruebas"),
            ("Analítica", "BI + dominio"), ("Consumo", "usuario + acción"),
        ],
        [
            ("Conectividad", "API · archivos"), ("Almacenamiento", "Parquet · objetos"),
            ("Procesamiento", "Pandas · Spark"), ("Operación", "plataforma · SRE"),
        ],
    ]

    # Guías verticales tenues
    for gx in [744, 1054, 1364]:
        c.line(gx, 184, gx, 810, stroke=LINE_LIGHT, sw=1, arrow=False, dash="4 4")

    for idx, (y, h, title, subtitle, color, fill) in enumerate(layers):
        c.rect(36, y, 1528, h, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
        c.rect(36, y, 230, h, fill=fill, stroke=color, sw=1.5, rx=16)
        c.text(60, y + 48, title, size=17.5, fill=color, weight=900)
        c.text(60, y + 80, subtitle, size=14.5, fill=MUTED, weight=600)
        for card_idx, (card_title, card_body) in enumerate(layer_cards[idx]):
            x = 294 + card_idx * 310
            c.rect(x, y + 24, 278, h - 48, fill=WHITE, stroke=color, sw=1.8, rx=13, shadow=True)
            if card_idx == 0:
                c.number_badge(x + 30, y + 50, idx + 1, fill=color, radius=16)
                title_x = x + 54
            else:
                title_x = x + 22
            c.text(title_x, y + 56, card_title, size=16.5, fill=INK, weight=800)
            c.text(x + 22, y + 92, card_body, size=14.5, fill=MUTED, weight=500)

    # Trazabilidad explícita por la columna 1
    for y1, y2, color, marker in [
        (324, 362, ORANGE, "orange"), (478, 516, AMBER, "amber"), (632, 670, BLUE, "blue")
    ]:
        c.line(433, y1, 433, y2, stroke=color, sw=3, marker=marker)
    c.pill(490, 310, 300, "define información requerida", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=12.5)
    c.pill(490, 464, 300, "habilita capacidades", fill=AMBER_L, color=AMBER, stroke=AMBER, size=12.5)
    c.pill(490, 618, 300, "impone requisitos técnicos", fill=BLUE_L, color=BLUE, stroke=BLUE, size=12.5)

    c.rect(1120, 800, 432, 30, fill=RED_L, stroke=RED, sw=1, rx=12)
    c.text(1336, 820, "TO-BE ≠ automatizar la decisión humana", size=13, fill=RED, weight=800, anchor="middle")
    c.footer("Prueba de diseño", "Cada componente técnico debe señalar qué dato, capacidad, proceso y KPI justifica su existencia.")
    return c


def make_nist() -> Canvas:
    c = Canvas(
        "Ciclo analítico NIST aplicado a SECOP",
        "Cinco etapas conectadas alrededor de una decisión humana con artefactos, responsables y controles.",
    )
    c.header("Mapa 6 de 7", "Ciclo analítico: la evidencia debe volver al proceso", "Captura → preparación → análisis → visualización → acción; después aparecen nuevas preguntas")

    c.rect(450, 126, 700, 46, fill=WHITE, stroke=LINE, sw=1.5, rx=16)
    c.text(800, 155, "GOBIERNO · SEGURIDAD · PRIVACIDAD · CALIDAD · TRAZABILIDAD", size=14.5, fill=NAVY, weight=900, anchor="middle")

    cards = [
        (650, 182, "1", "CAPTURA", BLUE, BLUE_L, ["Entrada: API o muestra local", "Artefacto: snapshot + metadatos", "Rol: ingeniero de datos + data owner"]),
        (1120, 288, "2", "PREPARACIÓN", AMBER, AMBER_L, ["Tipar fechas y duraciones", "Artefacto: tabla curada + excepciones", "Roles: ingeniería + data steward"]),
        (1010, 600, "3", "ANÁLISIS", PURPLE, PURPLE_L, ["Perfil descriptivo + reglas", "Artefacto: cola priorizada con motivos", "Roles: BI/datos + experto de dominio"]),
        (290, 600, "4", "VISUALIZACIÓN", TEAL, TEAL_L, ["Contexto de prioridad y filtros", "Artefacto: reporte / tablero analítico", "Roles: analista BI + usuario"]),
        (180, 288, "5", "ACCIÓN", ORANGE, ORANGE_L, ["Revisar contexto · corregir · escalar", "Artefacto: registro de decisión auditable", "Roles: usuario + dueño del proceso"]),
    ]
    for x, y, number, title, color, fill, body in cards:
        c.rect(x, y, 310, 168, fill=WHITE, stroke=color, sw=2, rx=18, shadow=True)
        c.number_badge(x + 36, y + 42, number, fill=color, radius=20)
        c.text(x + 68, y + 48, title, size=18.5, fill=color, weight=900)
        c.text(x + 20, y + 86, body, size=13.5, fill=MUTED, weight=550, line_height=1.35)

    # Núcleo central
    c.circle(800, 492, 138, fill="url(#hub-grad)", stroke="#2F6FB0", sw=3, shadow=True)
    c.text(800, 450, "DECISIÓN SOPORTADA", size=15.5, fill="#BFE4F6", weight=900, anchor="middle")
    c.text(800, 492, ["¿qué contrato revisar", "primero y por qué?"], size=21, fill=WHITE, weight=800, anchor="middle", line_height=1.18)
    c.pill(678, 560, 244, "humana · explicable · trazable", fill="#214E6D", color=WHITE, stroke="#4E7B99", size=12)

    # Recorrido circular
    c.path("M960 260 C1040 245 1110 270 1135 310", stroke=BLUE, sw=3, marker="blue")
    c.path("M1370 455 C1410 530 1320 620 1260 635", stroke=AMBER, sw=3, marker="amber")
    c.path("M1010 682 C850 795 600 795 590 682", stroke=PURPLE, sw=3, marker="purple")
    c.path("M290 635 C190 615 135 520 205 455", stroke=TEAL, sw=3, marker="teal")
    c.path("M330 288 C430 170 590 165 650 226", stroke=ORANGE, sw=3, marker="orange")

    # Píldoras de transición
    c.pill(1040, 204, 150, "datos crudos", fill=BLUE_L, color=BLUE, stroke=BLUE, size=12)
    c.pill(1346, 520, 185, "datos preparados", fill=AMBER_L, color=AMBER, stroke=AMBER, size=12)
    c.pill(710, 765, 180, "alertas y motivos", fill=PURPLE_L, color=PURPLE, stroke=PURPLE, size=12)
    c.pill(60, 520, 200, "evidencia priorizada", fill=TEAL_L, color=TEAL, stroke=TEAL, size=12)
    c.pill(390, 172, 260, "decisión → nuevo dato", fill=ORANGE_L, color=ORANGE, stroke=ORANGE, size=12)

    c.footer("Distinción esencial", "Visualizar muestra evidencia; actuar exige autoridad, criterio, registro y retroalimentación.")
    return c


def make_git_states() -> Canvas:
    c = Canvas(
        "Git y GitHub como conversación entre roles",
        "Propuesta, objeciones profesionales, corrección, CI y decisión humana conservadas en un Pull Request.",
    )
    c.header(
        "Mapa 7 de 7",
        "Git como puente: conservar la conversación profesional",
        "La rama contiene una propuesta; el Pull Request relaciona objeciones, correcciones y validaciones",
    )

    c.card(42, 176, 300, 168, "Necesidad del proceso", ["Priorizar cada 24 horas", "Dueño: ¿es un SLA validado?"], ORANGE, number=1, tag="VALOR + CRITERIO", title_size=17)
    c.card(42, 438, 300, 194, "Propuesta en una rama", ["Arquitectura diaria", "Reglas + datos + controles", "hito/s02-negocio"], BLUE, number=2, tag="NO CAMBIA MAIN", title_size=17)
    c.line(192, 344, 192, 438, stroke=ORANGE, marker="orange")

    reviews = [
        (398, "Dueño del proceso", ["¿de dónde sale el SLA?", "¿qué acción mejora?"], ORANGE, ORANGE_L),
        (768, "Steward + dominio", ["¿qué significa fecha?", "¿cómo tratamos faltantes?"], AMBER, AMBER_L),
        (1138, "Seguridad y privacidad", ["¿qué dato sobra?", "¿quién puede verlo?"], RED, RED_L),
    ]
    for x, title, body, color, fill in reviews:
        c.rect(x, 166, 322, 150, fill=WHITE, stroke=color, sw=2, rx=16, shadow=True)
        c.rect(x, 166, 322, 44, fill=fill, stroke=color, sw=1, rx=16)
        c.text(x + 20, 195, title, size=16, fill=color, weight=900)
        c.text(x + 20, 238, body, size=14, fill=INK, weight=600, line_height=1.35)

    c.rect(430, 400, 420, 236, fill="url(#hub-grad)", stroke=BLUE, sw=2.5, rx=22, shadow=True)
    c.pill(535, 424, 210, "PULL REQUEST", fill="#214E6D", color=WHITE, stroke="#4E7B99", size=13)
    c.text(640, 492, ["Propósito + diferencia", "+ preguntas + límites"], size=22, fill=WHITE, weight=850, anchor="middle", line_height=1.22)
    c.text(640, 572, ["No es una aprobación automática", "Es el lugar de la conversación"], size=14.5, fill="#D7EBF7", weight=600, anchor="middle", line_height=1.3)

    c.line(342, 535, 430, 535, stroke=BLUE, marker="blue")
    c.path("M559 316 C559 354 590 370 610 400", stroke=ORANGE, sw=2.5, marker="orange")
    c.path("M929 316 C900 354 790 370 760 400", stroke=AMBER, sw=2.5, marker="amber")
    c.path("M1299 316 C1180 350 900 360 840 438", stroke=RED, sw=2.5, marker="red")

    c.card(928, 402, 298, 190, "Corrección explicada", ["Arquitectura + ingeniería", "cambian la misma rama", "nueva versión responde al PR"], GREEN, number=3, tag="OBJECIÓN → CAMBIO", title_size=17)
    c.line(850, 518, 928, 500, stroke=GREEN, marker="green")
    c.path("M928 560 C890 650 780 690 700 636", stroke=GREEN, sw=2.5, arrow=True, dash="7 5", marker="green")

    c.card(928, 660, 298, 116, "CI · asistente", ["estructura · marcadores · secretos"], PURPLE, number=4, shadow=False, title_size=16, body_size=13.5)
    c.line(1077, 592, 1077, 660, stroke=PURPLE, marker="purple")

    c.card(1280, 402, 278, 190, "Juicio humano", ["Proceso: ¿sirve?", "Dominio: ¿es válido?", "Seguridad: ¿es aceptable?"], ORANGE, number=5, tag="NO LO HACE CI", title_size=17)
    c.line(1226, 500, 1280, 500, stroke=ORANGE, marker="orange")
    c.path("M1226 718 C1290 718 1300 594 1350 570", stroke=PURPLE, sw=2.5, marker="purple")

    c.card(1280, 660, 278, 116, "Acción del usuario", ["revisar · corregir · escalar", "registrar resultado"], TEAL, number=6, shadow=False, title_size=16, body_size=13)
    c.line(1419, 592, 1419, 660, stroke=TEAL, marker="teal")
    c.path("M1280 718 C1180 820 260 820 192 632", stroke=TEAL, sw=2.5, arrow=True, dash="8 6", marker="teal")
    c.pill(510, 790, 570, "ACCIÓN REGISTRADA → NUEVA EVIDENCIA → NUEVA CONVERSACIÓN", fill=TEAL_L, color=TEAL, stroke=TEAL, size=12.5)

    c.footer("Lectura clave", "Git conserva versiones; GitHub conserva la conversación; las personas conservan la responsabilidad.")
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
        "Inicio del laboratorio desde GitHub.com",
        "Vista conceptual del repositorio semestral, sus artefactos y la creación de una rama desde el navegador.",
    )
    c.header("Guía Git 1 de 4", "Abrir el repositorio y reconocer la historia", "Primero verifica acceso y propietario; después ubica los dos artefactos conectados")
    browser_shell(c, 42, 142, 1030, 650, "github.com · compras-claras-pareja-XX")
    c.text(72, 222, "ucentral-bigdata-2026-2 / compras-claras-pareja-XX", size=18.5, fill=INK, weight=800)
    c.pill(72, 246, 90, "Private", fill="#E9EEF2", color=MUTED, stroke="#D0DFEA", size=13)
    for x, label in [(72, "Code"), (160, "Issues"), (245, "Pull requests"), (380, "Actions")]:
        c.text(x, 310, label, size=15, fill=BLUE if label == "Code" else MUTED, weight=700)
    c.line(62, 330, 1048, 330, stroke=LINE, sw=1, arrow=False)
    c.rect(72, 354, 610, 250, fill=WHITE, stroke=LINE, sw=1, rx=10)
    c.text(94, 388, "Files", size=16, fill=INK, weight=800)
    files = [".github/", "data/", "hitos/", "hitos/s02/", "resultados/", "scripts/", "README.md"]
    for i, name in enumerate(files):
        yy = 420 + i * 25
        c.text(98, yy, "▣", size=14, fill=BLUE, weight=700)
        c.text(124, yy, name, size=14, fill=INK, weight=550)
    c.rect(742, 350, 285, 50, fill=GREEN, stroke=GREEN, sw=0, rx=10)
    c.text(884, 382, "Code ▾", size=17, fill=WHITE, weight=800, anchor="middle")
    c.rect(696, 414, 350, 330, fill=WHITE, stroke=LINE, sw=1.5, rx=12, shadow=True)
    c.text(720, 450, "Editar desde el navegador", size=18, fill=INK, weight=800)
    c.pill(720, 468, 180, "RUTA PRINCIPAL", fill=BLUE_L, color=BLUE, stroke=BLUE, size=13)
    c.text(720, 535, "1 · abrir el artefacto", size=14, fill=MUTED, weight=650)
    c.text(720, 570, "2 · pulsar Edit this file", size=14, fill=MUTED, weight=650)
    c.text(720, 605, "3 · proponer una rama", size=14, fill=MUTED, weight=650)
    c.pill(720, 642, 300, "hito/s02-negocio", fill="#F6F8FA", color=INK, stroke=LINE, size=13)
    c.text(720, 704, "Python usa el perfil precomputado", size=14, fill=AMBER, weight=800)

    c.rect(1100, 142, 458, 650, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1130, 186, "TRES COMPROBACIONES", size=18, fill=NAVY, weight=900)
    options = [
        (218, "1", "Acceso correcto", "cuenta + repositorio", "no estás en la plantilla", GREEN, GREEN_L),
        (372, "2", "Artefactos S02", "decisión + arquitectura", "mismo argumento", BLUE, BLUE_L),
        (526, "3", "Rama propuesta", "cambio separado de main", "abre conversación", AMBER, AMBER_L),
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

    c.footer("Resultado esperado", "Reconoces propietario, dos artefactos y rama; todavía no necesitas terminal ni instalar Git.")
    return c


def make_status_diff() -> Canvas:
    c = Canvas(
        "Lectura de cambios desde GitHub",
        "Comparación conceptual de dos artefactos con preguntas de revisión profesional.",
    )
    c.header("Guía Git 2 de 4", "Leer Files changed antes de aceptar", "El objetivo es relacionar cada diferencia con una decisión, un rol y un límite")

    browser_shell(c, 42, 142, 980, 650, "github.com · Pull Request · Files changed")
    c.text(72, 222, "hito/s02/01_decision_proceso.md", size=17, fill=INK, weight=800)
    c.pill(752, 202, 110, "Viewed", fill=GREEN_L, color=GREEN, stroke=GREEN, size=12)
    c.rect(62, 246, 940, 190, fill="#F8FAFC", stroke=LINE, sw=1, rx=10)
    c.rect(62, 246, 58, 190, fill="#F1F5F9", stroke=LINE, sw=1, rx=10)
    c.text(136, 282, "− Cuello: consolidación tardía.", size=16, fill=RED, weight=600)
    c.rect(120, 300, 880, 64, fill="#E9F7EF", stroke="#C8E9D8", sw=0, rx=0)
    c.text(136, 329, "+ Hipótesis: descargar, unir y validar después de la operación.", size=16, fill=GREEN, weight=650)
    c.text(136, 357, "+ Evidencia pendiente: marcas de tiempo de cuatro semanas.", size=16, fill=GREEN, weight=650)
    c.text(72, 478, "hitos/s02/02_caso_arquitectura_accion.md", size=17, fill=INK, weight=800)
    c.rect(62, 502, 940, 214, fill="#F8FAFC", stroke=LINE, sw=1, rx=10)
    c.rect(62, 502, 58, 214, fill="#F1F5F9", stroke=LINE, sw=1, rx=10)
    c.text(136, 540, "+ Veredicto: BI gobernada por lotes es suficiente.", size=16, fill=GREEN, weight=650)
    c.text(136, 578, "+ Umbral: reevaluar si el lote incumple SLA o costo medido.", size=16, fill=GREEN, weight=650)
    c.text(136, 626, "+ Límite: una alerta prioriza; no demuestra irregularidad.", size=16, fill=GREEN, weight=650)
    c.pill(136, 662, 300, "2 artefactos · una decisión", fill=BLUE_L, color=BLUE, stroke=BLUE, size=13)

    c.rect(1050, 142, 508, 650, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1080, 186, "CUATRO PREGUNTAS DE ROL", size=18, fill=NAVY, weight=900)
    states = [
        (222, "1", "Dueño del proceso", "¿el KPI refleja valor?", BLUE, True),
        (332, "2", "Data steward", "¿la regla conserva significado?", AMBER, False),
        (442, "3", "Arquitecto de datos", "¿qué impacto tiene el cambio?", PURPLE, False),
        (552, "4", "Usuario de evidencia", "¿la salida permite actuar?", GREEN, False),
    ]
    for y, num, title, body, color, active in states:
        fill = BLUE_L if active else "#F6F8FA"
        stroke = color if active else LINE
        c.rect(1080, y, 448, 84, fill=fill, stroke=stroke, sw=2 if active else 1, rx=13)
        c.number_badge(1112, y + 32, num, fill=color if active else MUTED, radius=18)
        c.text(1142, y + 31, title, size=17, fill=INK, weight=800)
        c.text(1142, y + 60, body, size=15, fill=MUTED, weight=550)
        if active:
            c.pill(1375, y + 23, 125, "VALOR PRIMERO", fill=WHITE, color=BLUE, stroke=BLUE, size=11)

    c.rect(1080, 666, 448, 96, fill=GREEN_L, stroke=GREEN, sw=1.5, rx=13)
    c.text(1104, 697, "CRITERIO ANTES DE APROBAR", size=15, fill=GREEN, weight=900)
    c.text(1104, 728, ["¿La corrección responde la objeción?", "¿La evidencia y el límite son verificables?"], size=15, fill=INK, weight=600, line_height=1.25)

    c.footer("Lectura del cambio", "El color muestra una diferencia; el rol explica si esa diferencia mejora la decisión.")
    return c


def make_pull_request() -> Canvas:
    c = Canvas(
        "Pull Request revisable de Compras Claras",
        "Vista de ramas, descripción, archivos, reviewers y check con guía de lectura crítica.",
    )
    c.header("Guía Git 3 de 4", "Pull Request: transformar commits en una explicación", "Un PR de calidad permite reconstruir propósito, evidencia, límites y forma de verificación")

    browser_shell(c, 34, 140, 1130, 660, "github.com · Pull Request #1")
    c.text(64, 214, "Pull requests / #1", size=16, fill=BLUE, weight=700)
    c.text(64, 258, "Compras Claras · arquitectura y ciclo analítico", size=25, fill=INK, weight=800)
    c.pill(64, 278, 84, "Open", fill=GREEN, color=WHITE, size=13)
    c.text(166, 304, "hito/s02-negocio propone cambios sobre main", size=15, fill=MUTED, weight=550)
    c.line(64, 330, 1134, 330, stroke=LINE, sw=1, arrow=False)

    tabs = [(64, "Conversation"), (185, "Commits"), (284, "Checks 1"), (380, "Files changed 2")]
    for x, label in tabs:
        c.text(x, 365, label, size=14, fill=BLUE if label == "Conversation" else MUTED, weight=800 if label == "Conversation" else 600)
    c.line(64, 380, 1134, 380, stroke=LINE, sw=1, arrow=False)

    c.rect(64, 402, 750, 340, fill=WHITE, stroke=LINE, sw=1.2, rx=12)
    c.rect(64, 402, 750, 46, fill="#F6F8FA", stroke=LINE, sw=1, rx=12)
    c.text(88, 432, "Descripción de la pareja", size=15, fill=INK, weight=800)
    body = [
        (480, "Qué se hizo", "Decisión/proceso + caso/arquitectura/acción."),
        (545, "Por qué", "Reducir consolidación manual y explicar la prioridad."),
        (610, "Cómo se verificó", "✓ estructura  ✓ revisión  ✓ límites"),
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
    c.text(866, 706, "2 artefactos · cambios visibles", size=15, fill=PURPLE, weight=700)

    c.rect(1190, 140, 374, 660, fill=WHITE, stroke=NAVY, sw=1.5, rx=18)
    c.text(1218, 184, "CUATRO LECTURAS", size=18, fill=NAVY, weight=900)
    checks = [
        (220, "1", "Ramas correctas", "main ← hito/s02-negocio", BLUE, BLUE_L),
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
    for x, color, marker in [(278, PURPLE, "purple"), (530, GREEN, "green"), (782, ORANGE, "orange"), (1034, NAVY_2, "blue")]:
        c.line(x, 178, x + 32, 178, stroke=color, sw=3, marker=marker)
    c.pill(1320, 159, 220, "EVIDENCIA REVISADA", fill=GREEN_L, color=GREEN, stroke=GREEN, size=13)

    c.rect(42, 258, 730, 520, fill=WHITE, stroke=GREEN, sw=2, rx=18, shadow=True)
    c.rect(42, 258, 730, 70, fill=GREEN_L, stroke=GREEN, sw=1, rx=18)
    c.text(72, 300, "A · VALIDACIÓN AUTOMÁTICA", size=21, fill=GREEN, weight=900)
    c.pill(548, 276, 190, "validar · 8 s · PASS", fill=GREEN, color=WHITE, size=13)
    auto_checks = [
        (365, "✓", "Estructura requerida", "2 artefactos + perfil + fuente"),
        (445, "✓", "Plantillas completas", "no quedan marcadores COMPLETAR"),
        (525, "✓", "Estructura observable", "rama + archivos requeridos + mensajes"),
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

    c.footer("Puerta de calidad", "CI ayuda a detectar reglas observables; el contenido y el razonamiento requieren revisión humana.")
    return c


VISUALS = {
    DIAGRAM_DIR / "01_hilo_decision.svg": make_hilo,
    DIAGRAM_DIR / "02_proceso_as_is.svg": make_as_is,
    DIAGRAM_DIR / "03_adopcion_valor.svg": make_adoption,
    DIAGRAM_DIR / "04_casos_bi.svg": make_use_cases,
    DIAGRAM_DIR / "05_arquitectura_to_be.svg": make_architecture,
    DIAGRAM_DIR / "06_ciclo_nist.svg": make_nist,
    DIAGRAM_DIR / "07_estados_git.svg": make_git_states,
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
