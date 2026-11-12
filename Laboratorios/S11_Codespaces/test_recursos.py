"""QA de la ruta ACTIVA S11: 16 diapositivas, guía y rama de aprendizaje."""
from __future__ import annotations
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
SLIDES = ROOT / "Presentaciones/s11-videoclase-ocr-asr-embeddings.html"
TUTORIAL = ROOT / "assets/tutoriales/s11-ocr-asr-paso-a-paso.html"
HOME = ROOT / "index.html"

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.ids, self.buttons = [], set(), set()
        self.slides = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "a" and "href" in d:
            self.links.append(d["href"])
        if "id" in d:
            self.ids.add(d["id"])
        if tag == "button" and "id" in d:
            self.buttons.add(d["id"])
        if tag == "section" and "slide" in d.get("class", "").split():
            self.slides += 1

class RecursosS11(unittest.TestCase):
    def test_presentacion_python_desde_cero(self):
        html = SLIDES.read_text(encoding="utf-8")
        p = Links()
        p.feed(html)
        self.assertEqual(p.slides, 16)
        self.assertTrue(all(f"s{i}" in p.ids for i in range(1, 17)))
        self.assertTrue({"next", "prev"} <= p.buttons)
        self.assertIn('addEventListener("keydown"', html)
        self.assertIn("s11-estudiantes/01_laboratorio.ipynb", html)
        self.assertIn("embeddinggemma-2:440m", html)
        self.assertIn("pytesseract", html)
        self.assertIn("WhisperModel", html)
        self.assertNotIn("python lab.py preparar", html)

    def test_tutorial_ocho_pasos(self):
        html = TUTORIAL.read_text(encoding="utf-8")
        for n in range(1, 9):
            self.assertIn(f'id="paso{n:02d}"', html)
        self.assertIn("01_laboratorio.ipynb", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertNotIn("python lab.py preparar", html)

    def test_lms_incluye_ambos_recursos(self):
        html = HOME.read_text(encoding="utf-8")
        self.assertIn("s11-videoclase-ocr-asr-embeddings.html", html)
        self.assertIn("s11-ocr-asr-paso-a-paso.html", html)
        self.assertIn("Python desde cero", html)

    def test_enlaces_locales(self):
        for pagina in (SLIDES, TUTORIAL):
            p = Links()
            p.feed(pagina.read_text(encoding="utf-8"))
            for href in p.links:
                url = urlsplit(href)
                if url.scheme or url.netloc or href.startswith("#"):
                    continue
                ruta = (pagina.parent / unquote(url.path)).resolve()
                self.assertTrue(ruta.is_file(), f"{pagina.name}: {href} roto")

if __name__ == "__main__":
    unittest.main()
