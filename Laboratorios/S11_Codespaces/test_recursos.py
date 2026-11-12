"""Control barato de enlaces y navegación del material nuevo S11 (sin navegador/red)."""
from __future__ import annotations

import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
PAGE = ROOT / "Presentaciones/s11-videoclase-ocr-asr-embeddings.html"
HOME = ROOT / "index.html"


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.slides = 0
        self.buttons = set()
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and "href" in d:
            self.links.append(d["href"])
        if tag == "section" and "slide" in d.get("class", "").split():
            self.slides += 1
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "button" and "id" in d:
            self.buttons.add(d["id"])


class RecursosS11(unittest.TestCase):
    def test_presentacion_contiene_13_pantallas_y_navegacion(self):
        html = PAGE.read_text(encoding="utf-8")
        parser = Links()
        parser.feed(html)
        self.assertEqual(parser.slides, 13)
        self.assertIn("prev", parser.buttons)
        self.assertIn("next", parser.buttons)
        self.assertIn('window.addEventListener("keydown"', html)
        self.assertTrue(all(f"s{i}" in parser.ids for i in range(1, 14)))

    def test_enlaces_internos_del_material_existen(self):
        for pagina in (PAGE, HOME):
            parser = Links()
            parser.feed(pagina.read_text(encoding="utf-8"))
            for href in parser.links:
                url = urlsplit(href)
                if url.scheme or url.netloc or href.startswith("#"):
                    continue
                destino = (pagina.parent / unquote(url.path)).resolve()
                # Excluir enlaces de navegación generados por JavaScript.
                self.assertTrue(destino.is_file(), f"Enlace roto en {pagina.name}: {href}")

    def test_dos_recursos_formativos_para_s11(self):
        home = HOME.read_text(encoding="utf-8")
        self.assertIn("s11-videoclase-ocr-asr-embeddings.html", home)
        self.assertIn("GUIA_ESTUDIANTE.md", home)
        guia = (ROOT / "Laboratorios/S11_Codespaces/GUIA_ESTUDIANTE.md").read_text()
        for comando in ("python lab.py ocr", "python lab.py asr",
                        "python lab.py extraer", "python lab.py indexar",
                        "python verificar_independiente.py",
                        "python proyecto.py procesar"):
            self.assertIn(comando, guia)


if __name__ == "__main__":
    unittest.main()
