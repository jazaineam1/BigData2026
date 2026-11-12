"""QA ligero de la S11: presentación integral, entrada al LMS y cuaderno único."""
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
        self.assertEqual(p.slides, 63)
        self.assertTrue(all(f"s{i}" in p.ids for i in range(1, 64)))
        self.assertTrue({"next", "prev"} <= p.buttons)
        self.assertIn('addEventListener("keydown"', html)
        self.assertIn("s11-estudiantes/01_laboratorio.ipynb", html)
        self.assertIn("embeddinggemma-2:440m", html)
        self.assertIn("pytesseract", html)
        self.assertIn("WhisperModel", html)
        self.assertIn("HTTP 400", html)
        self.assertIn('"input":[{"image":b64}]', html)
        self.assertIn("PSM 7", html)
        self.assertIn('id="toolQuestion"', html)
        self.assertIn('id="routeButton"', html)
        self.assertIn('id="outlineDialog"', html)
        self.assertEqual(html.count('data-route="ampliacion"'), 24)  # 23 slides + CSS
        self.assertIn('id="werReference"', html)
        self.assertIn('id="cosB"', html)
        self.assertIn('id="timeMeasured"', html)
        self.assertIn("JSONL", html)
        self.assertIn("Parquet", html)
        self.assertIn("122 fuentes", html)
        self.assertNotIn("python lab.py preparar", html)

    def test_tutorial_antiguo_redirige_a_presentacion_unica(self):
        html = TUTORIAL.read_text(encoding="utf-8")
        self.assertIn("s11-videoclase-ocr-asr-embeddings.html#s1", html)
        self.assertIn("http-equiv=\"refresh\"", html)
        self.assertNotIn('id="paso05"', html)

    def test_lms_s11_con_unica_presentacion_y_cuaderno(self):
        import json
        html = HOME.read_text(encoding="utf-8")
        self.assertIn("s11-videoclase-ocr-asr-embeddings.html", html)
        self.assertIn("Cuaderno único", html)
        course = json.loads((ROOT / "lms/data/course.json").read_text(encoding="utf-8"))
        session = next(s for s in course["sessions"] if s["n"] == 11)
        self.assertIn("s11-videoclase-ocr-asr-embeddings.html", session["entry"]["url"])
        self.assertIn("presentación", session["entry"]["label"].lower())

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
