"""Smoke test de interfaz S11: no descarga modelos ni usa archivos de usuarios."""
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class InterfazCodespaces(unittest.TestCase):
    def test_arranque_y_orientacion_pedagogica(self):
        archivo = Path(__file__).with_name("app.py")
        app = AppTest.from_file(str(archivo), default_timeout=20).run()
        self.assertEqual(len(app.exception), 0, f"Excepciones: {list(app.exception)}")
        self.assertTrue(any("Laboratorio de evidencias" in x.value for x in app.title))
        self.assertTrue(any("Crear carpeta" in x.label for x in app.sidebar.button))

if __name__ == "__main__":
    unittest.main()
