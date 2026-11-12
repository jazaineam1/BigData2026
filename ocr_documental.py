"""Funciones pequeñas y comprobables del visor OCR de S11.

Separa obtener texto, interpretar campos y revisar la fuente. Las coincidencias
son CANDIDATOS, no hechos certificados por OCR.
"""
from __future__ import annotations

import io
import re
import subprocess
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw

PSM_EXPLICACION = {
    3: ("3 — Automático: detecta columnas y bloques",
        "Tesseract intenta determinar dónde hay columnas, párrafos y bloques. "
        "Es el punto de partida en documentos completos con tablas y texto."),
    6: ("6 — Bloque uniforme: asume una región de texto",
        "Tesseract trata el contenido como un único bloque. "
        "Pruébalo cuando recortes una zona con un párrafo o una tabla simple."),
    11: ("11 — Texto disperso: encuentra fragmentos aislados",
         "Busca textos dispersos donde aparezcan sin reconstruir bien su orden de lectura. "
         "Puede servir para letreros y fotos, pero mezclar columnas en un acta."),
}


def pdf_paginas(pdf: str | Path) -> int:
    """Páginas reales del PDF (no presupone que todos tienen una sola)."""
    ruta = str(pdf)
    resultado = subprocess.run(
        ["pdfinfo", ruta], capture_output=True, text=True, check=True, timeout=25
    )
    m = re.search(r"^Pages:\s+(\d+)", resultado.stdout, flags=re.MULTILINE)
    if not m:
        raise ValueError(f"pdfinfo no reportó las páginas de {ruta}")
    total = int(m.group(1))
    if total < 1 or total > 500:
        raise ValueError(f"Cantidad inesperada de páginas: {total}")
    return total


@lru_cache(maxsize=24)
def renderizar_pagina(pdf: str, pagina: int, dpi: int = 170) -> bytes:
    """Convierte una página a PNG en memoria, sin modificar el PDF ni escribir RAW."""
    total = pdf_paginas(pdf)
    if not (1 <= pagina <= total):
        raise ValueError(f"Página {pagina} fuera del rango 1–{total}")
    if not (100 <= dpi <= 250):
        raise ValueError("La resolución debe estar entre 100 y 250 DPI")
    args = ["pdftoppm", "-f", str(pagina), "-l", str(pagina),
            "-r", str(dpi), "-singlefile", "-png", pdf]
    proc = subprocess.run(args, capture_output=True, check=True, timeout=90)
    if not proc.stdout.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("pdftoppm no produjo una imagen PNG válida")
    return proc.stdout


def texto_integrado_pdf(pdf: str | Path, pagina: int) -> str:
    """Extrae texto seleccionable si el PDF ya lo trae; no ejecuta OCR."""
    proc = subprocess.run(
        ["pdftotext", "-f", str(pagina), "-l", str(pagina),
         "-layout", str(pdf), "-"],
        capture_output=True, check=True, timeout=30,
    )
    return proc.stdout.decode("utf-8", errors="replace").strip()


MONTO = re.compile(
    r"(?<!\d)(?:[$]\s*)?(\d{1,3}(?:[.\s]\d{3}){1,3})(?:[,]\s*0{2})?(?!\d)"
)
CONTRATO = re.compile(r"\b(?:0{0,2}\d{1,4})\s*[-–]\s*20\d{2}\b")


def _contexto(texto: str, clave: str, ancho: int = 450) -> str:
    m = re.search(clave, texto, flags=re.IGNORECASE | re.MULTILINE)
    return texto[m.start():m.start() + ancho].replace("\n", " ").strip() if m else ""


def candidatos_ocr(texto: str) -> list[dict[str, str]]:
    """Propone campos CON FRAGMENTO DE EVIDENCIA, sin inventar datos faltantes."""
    limpio = re.sub(r"[ \t]+", " ", texto)
    regla = [
        ("Tipo documental", r"ACTA\s+DE\s+INICIO", 180),
        ("Número de contrato", r"(?:N[°o.]?\s*DE\s*CONTRATO|CONTRATO)", 220),
        ("Valor del contrato", r"VALOR\s+DEL\s+CONTRATO", 490),
        ("Duración", r"DURACI[ÓO]N\s+DEL\s+CONTRATO", 270),
        ("Forma de pago", r"FORMA\s+DE\s+PAGO", 650),
    ]
    salida = []
    for nombre, regex, ancho in regla:
        fragmento = _contexto(limpio, regex, ancho=ancho)
        if not fragmento:
            salida.append({"Campo": nombre, "Lectura candidata": "No detectado",
                           "Evidencia del OCR": "La etiqueta no se reconoció en esta página"})
            continue
        valor = "Etiqueta encontrada; revisar el fragmento"
        if nombre == "Tipo documental":
            valor = "Acta de inicio (texto detectado)"
        elif nombre == "Número de contrato":
            m = CONTRATO.search(fragmento)
            if m:
                valor = m.group(0)
        elif nombre in ("Valor del contrato", "Forma de pago"):
            montos = MONTO.findall(fragmento)
            if montos:
                valor = " / ".join(montos[:3]) + " (candidatos; verificar)"
        elif nombre == "Duración":
            m = re.search(r"(?:SEIS\s*\(\s*0?6\s*\)|\b\d+\s*MESES\b)", fragmento, re.I)
            if m:
                valor = m.group(0)
        salida.append({"Campo": nombre, "Lectura candidata": valor,
                       "Evidencia del OCR": fragmento[:250]})
    return salida


def referencia_doc_728704921(pdf: str | Path, pagina: int) -> dict[str, str] | None:
    """Referencia VISUAL observada por el docente; nunca se mezcla con salida OCR."""
    if Path(pdf).name != "secop_acta_728704921.pdf" or pagina != 1:
        return None
    return {
        "Tipo": "Acta de inicio",
        "Contrato": "006-2026",
        "Valor del contrato": "$14.760.000 COP",
        "Duración": "6 meses",
        "Forma de pago": "6 pagos parciales de $2.460.000 COP",
        "Control aritmético": "6 × 2.460.000 = 14.760.000",
    }


# En fotografías publicitarias conviene comparar el original con un recorte.
# Estas transformaciones se aplican a copias en memoria; nunca cambian el archivo fuente.
def recortar_por_porcentaje(imagen: Image.Image, horizontal: tuple[int,int],
                           vertical: tuple[int,int]) -> Image.Image:
    if not (0 <= horizontal[0] < horizontal[1] <= 100
            and 0 <= vertical[0] < vertical[1] <= 100):
        raise ValueError("Los porcentajes deben estar ordenados de 0 a 100.")
    w, h = imagen.size
    limites = (int(w * horizontal[0]/100), int(h * vertical[0]/100),
               int(w * horizontal[1]/100), int(h * vertical[1]/100))
    return imagen.crop(limites)


# Sobre la imagen del laboratorio (1200×675), este recorte aisla la palabra VALLE.
# Al escalar proporciones, la imagen sigue funcionando si se exporta en otra resolución.
LOGO_VALLE_BOUNDS = (175/1200, 240/675, 540/1200, 375/675)


def recorte_logo_valle(imagen: Image.Image, zona: str) -> Image.Image:
    w, h = imagen.size
    areas = {
        "Logotipo completo": (145/1200, 125/675, 565/1200, 545/675),
        "Palabra VALLE": LOGO_VALLE_BOUNDS,
        "Eslogan": (205/1200, 363/675, 482/1200, 451/675),
    }
    if zona not in areas:
        raise ValueError(f"Zona de logotipo no reconocida: {zona}")
    x0, y0, x1, y1 = areas[zona]
    return imagen.crop((round(w*x0), round(h*y0),
                        round(w*x1), round(h*y1)))


def preparar_region_ocr(img: Image.Image, escala: int = 1,
                        tratamiento: str = "Sin cambios") -> Image.Image:
    """Devuelve copia de píxeles; la imagen original se mantiene intacta."""
    if escala not in (1, 2, 3):
        raise ValueError("Escala OCR no válida")
    copia = img.convert("RGB")
    if escala > 1:
        copia = copia.resize((copia.width*escala, copia.height*escala),
                             Image.Resampling.LANCZOS)
    if tratamiento == "Contraste y nitidez":
        copia = ImageOps.autocontrast(ImageOps.grayscale(copia))
        copia = copia.filter(ImageFilter.UnsharpMask(radius=1, percent=130, threshold=2))
    elif tratamiento == "Blanco y negro":
        gray = ImageOps.autocontrast(ImageOps.grayscale(copia))
        copia = gray.point(lambda v: 255 if v >= 150 else 0)
    elif tratamiento != "Sin cambios":
        raise ValueError("Tratamiento OCR no reconocido")
    # Un margen blanco ayuda a no cortar caracteres que tocan los bordes.
    return ImageOps.expand(copia, border=12, fill="white")


def detalle_ocr(datos: dict) -> tuple[list[dict],float|None]:
    """Tesseract image_to_data: palabras, cuadros y confianza interna (no exactitud)."""
    filas = []
    for i, palabra in enumerate(datos.get("text", [])):
        palabra = palabra.strip()
        try:
            conf = float(datos["conf"][i])
        except (ValueError, TypeError):
            continue
        if not palabra or conf < 0:
            continue
        filas.append({
            "Palabra": palabra,
            "Confianza interna": round(conf, 1),
            "x": int(datos["left"][i]), "y": int(datos["top"][i]),
            "ancho": int(datos["width"][i]), "alto": int(datos["height"][i])
        })
    promedio = round(sum(f["Confianza interna"] for f in filas)/len(filas), 1) if filas else None
    return filas, promedio


def dibujar_cajas_ocr(img: Image.Image, filas: list[dict]) -> Image.Image:
    salida = img.convert("RGB").copy()
    lapiz = ImageDraw.Draw(salida)
    for fila in filas:
        x, y = fila["x"], fila["y"]
        w, h = fila["ancho"], fila["alto"]
        lapiz.rectangle((x, y, x+w, y+h), outline=(12, 168, 88), width=2)
    return salida
