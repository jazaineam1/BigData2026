"""Verifica rutas y pares reales que el visor presenta al alumnado."""
import json
import unittest
from pathlib import Path

from fuentes import ROOT, inventario, preparar_audios, sha256


class VisorFuentesTest(unittest.TestCase):
    def test_92_registros_visual_documentales(self):
        registros = inventario()
        grupos = {g: [x for x in registros if x["grupo"] == g]
                  for g in ["El Tiempo (30)", "Fotografías con ficha (32)", "Actas SECOP (30)"]}
        self.assertEqual([len(v) for v in grupos.values()], [30, 32, 30])
        for item in registros:
            self.assertTrue(item["original"].is_file(), item["nombre"])
            self.assertTrue(item["preview"].is_file(), item["nombre"])
        for doc in grupos["Actas SECOP (30)"]:
            self.assertEqual(doc["original"].suffix, ".pdf")
            self.assertTrue(doc["preview"].name.endswith("_pagina1.png"))
        self.assertEqual(len({x["nombre"] for x in grupos["Actas SECOP (30)"]}), 30)

    def test_metadatos_y_hashes(self):
        fotos = [x for x in inventario() if x["grupo"] == "Fotografías con ficha (32)"]
        self.assertTrue(any(x["credito"] and x["url"] and x["noticia"] for x in fotos))
        foto = fotos[0]["original"]
        self.assertEqual(len(sha256(foto)), 64)

    def test_30_voces_cuando_estan_preparadas(self):
        from fuentes import AUDIO_MANIFEST
        if not AUDIO_MANIFEST.exists():
            self.skipTest("Audio de HF se descarga en integración; no requiere red en test local")
        data = json.loads(AUDIO_MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(len(data["audios"]), 30)
        self.assertEqual(len({x["registro"] for x in data["audios"]}), 30)
        audios = [x for x in inventario() if x["grupo"] == "Voces MINDS-14 (30)"]
        self.assertEqual(len(audios), 30)
        for item in audios:
            self.assertTrue(item["original"].is_file())



class OCRDocumentalTest(unittest.TestCase):
    def test_psm_explicado_para_pagina_bloque_linea_y_dispersion(self):
        from ocr_documental import PSM_EXPLICACION
        self.assertEqual(set(PSM_EXPLICACION), {3, 6, 7, 11})
        self.assertIn("columnas", PSM_EXPLICACION[3][1])
        self.assertIn("bloque", PSM_EXPLICACION[6][1])
        self.assertIn("dispersos", PSM_EXPLICACION[11][1])
        self.assertIn("línea", PSM_EXPLICACION[7][1])

    def test_pdf_seleccion_y_pagina_dos_real(self):
        import io
        from PIL import Image
        from ocr_documental import pdf_paginas, renderizar_pagina, texto_integrado_pdf
        archivo = ROOT / "datos/raw/actas_pdf/secop_acta_728704921.pdf"
        self.assertTrue(archivo.is_file())
        self.assertGreaterEqual(pdf_paginas(archivo), 2)
        png = renderizar_pagina(str(archivo), 2, 130)
        self.assertTrue(png.startswith(b"\x89PNG\r\n\x1a\n"))
        with Image.open(io.BytesIO(png)) as imagen:
            imagen.verify()
        self.assertIsInstance(texto_integrado_pdf(archivo, 1), str)

    def test_candidatos_con_evidencia_sin_inventar(self):
        from ocr_documental import candidatos_ocr, referencia_doc_728704921
        muestra = (
            "ACTA DE INICIO\nNo. DE CONTRATO: 006 - 2026\n"
            "VALOR DEL CONTRATO: CATORCE MILLONES ($14.760.000,00)\n"
            "DURACION DEL CONTRATO: SEIS (06) MESES\n"
            "FORMA DE PAGO: SEIS (06) PAGOS PARCIALES ($2.460.000,00)\n"
        )
        filas = {x["Campo"]: x for x in candidatos_ocr(muestra)}
        self.assertIn("14.760.000", filas["Valor del contrato"]["Lectura candidata"])
        self.assertIn("2.460.000", filas["Forma de pago"]["Lectura candidata"])
        self.assertIn("006", filas["Número de contrato"]["Lectura candidata"])
        self.assertEqual(filas["Tipo documental"]["Lectura candidata"],
                         "Acta de inicio (texto detectado)")
        ausentes = {x["Campo"]: x for x in candidatos_ocr("texto sin etiquetas")}
        self.assertEqual(ausentes["Valor del contrato"]["Lectura candidata"], "No detectado")
        pdf = ROOT / "datos/raw/actas_pdf/secop_acta_728704921.pdf"
        referencia = referencia_doc_728704921(pdf, 1)
        self.assertEqual(referencia["Valor del contrato"], "$14.760.000 COP")
        self.assertIsNone(referencia_doc_728704921(pdf, 2))

    def test_ocr_real_primera_pagina_no_vacia(self):
        import pytesseract
        from PIL import Image
        path = ROOT / "datos/raw/actas/secop_acta_728704921_pagina1.png"
        with Image.open(path) as imagen:
            texto = pytesseract.image_to_string(imagen, lang="spa", config="--psm 3")
        self.assertGreater(len(texto), 500)


class EmbeddingsFormatoTest(unittest.TestCase):
    """Prueba que LOS DOS BLOQUES del único cuaderno manden input=[entrada]."""

    def _funciones(self, cell_id, funcion):
        import ast
        import requests
        nb = json.loads((ROOT / "01_laboratorio.ipynb").read_text(encoding="utf-8"))
        code = next("".join(c["source"]) for c in nb["cells"] if c["id"] == cell_id)
        arbol = ast.parse(code)
        funcion_ast = next(x for x in arbol.body if isinstance(x, ast.FunctionDef)
                           and x.name == funcion)
        scope = {
            "requests": requests, "MODELO": "embeddinggemma-2:440m",
            "API": "http://127.0.0.1:11434/api/embed",
        }
        exec(compile(ast.Module(body=[funcion_ast], type_ignores=[]),
                     f"{cell_id}.py", "exec"), scope)
        return scope[funcion], code

    def test_objeto_imagen_y_texto_via_lista(self):
        from unittest.mock import MagicMock, patch
        for id, nombre in [("s11-vision-vectores", "vector"),
                           ("lote-embeddings", "embedding")]:
            with self.subTest(celda=id):
                f, codigo = self._funciones(id, nombre)
                self.assertIn('"input": [entrada]', codigo)
                with patch("requests.post") as post:
                    respuesta = MagicMock()
                    respuesta.ok = True
                    respuesta.json.return_value = {"embeddings": [[0.0]*768]}
                    post.return_value = respuesta
                    self.assertEqual(len(f({"image": "WEBP_BASE64"}, "foto.webp")), 768)
                    self.assertEqual(post.call_args.kwargs["json"]["input"],
                                     [{"image": "WEBP_BASE64"}])
                    self.assertEqual(len(f("viviendas en una ladera", "consulta")), 768)
                    self.assertEqual(post.call_args.kwargs["json"]["input"],
                                     ["viviendas en una ladera"])

    def test_http_400_muestra_cuerpo_del_servidor(self):
        from unittest.mock import MagicMock, patch
        for id, nombre in [("s11-vision-vectores", "vector"),
                           ("lote-embeddings", "embedding")]:
            with self.subTest(celda=id):
                f, _ = self._funciones(id, nombre)
                with patch("requests.post") as post:
                    respuesta = MagicMock()
                    respuesta.ok = False
                    respuesta.status_code = 400
                    respuesta.text = '{"error":"invalid input"}'
                    post.return_value = respuesta
                    with self.assertRaisesRegex(RuntimeError, "invalid input"):
                        f({"image": "FAKE"}, "foto.webp")

    def test_bytes_originales_por_defecto(self):
        import ast
        import base64
        from PIL import Image, ImageOps
        from io import BytesIO
        imagen = ROOT / "datos/raw/fotos/eltiempo_023.webp"
        nb = json.loads((ROOT / "01_laboratorio.ipynb").read_text(encoding="utf-8"))
        for id, fn in [("s11-vision-vectores", "preparar_imagen_base64"),
                       ("lote-embeddings", "imagen_para_modelo")]:
            with self.subTest(celda=id):
                code = next("".join(c["source"]) for c in nb["cells"] if c["id"] == id)
                arbol = ast.parse(code)
                f = next(x for x in arbol.body if isinstance(x, ast.FunctionDef) and x.name == fn)
                scope = {"base64": base64, "Image": Image, "ImageOps": ImageOps,
                         "BytesIO": BytesIO, "NORMALIZAR_JPEG": False,
                         "MAX_LADO": 768}
                exec(compile(ast.Module(body=[f], type_ignores=[]), "<image>", "exec"), scope)
                assert base64.b64decode(scope[fn](imagen)) == imagen.read_bytes()

    def test_preparacion_revisa_texto_e_imagen(self):
        script = (ROOT / "preparar_embeddinggemma.sh").read_text(encoding="utf-8")
        self.assertIn('"input": [entrada]', script)
        self.assertIn('foto = Path("datos/raw/fotos/eltiempo_023.webp")', script)
        self.assertIn('incrustar("Una fotografía', script)


class BusquedaVisualLigeraTest(unittest.TestCase):
    """Sólo mocks: nunca descarga pesos ni ejecuta inferencia en las pruebas."""

    def test_indice_con_cache_y_busqueda_texto_con_lista(self):
        from unittest.mock import patch
        from fuentes import ROOT, construir_indice_visual, buscar_indice_visual
        fotos = sorted((ROOT/"datos/raw/fotos").glob("eltiempo_*"))[:1]
        self.assertEqual(len(fotos), 1)
        cache = {}
        entradas = []

        def falso_embedding(entrada):
            entradas.append(entrada)
            vector = [0.0]*768
            vector[0] = 1.0
            return vector

        def guardar(datos):
            cache.clear()
            cache.update(datos)

        with patch("fuentes._cargar_cache_visual", side_effect=lambda: cache), \
             patch("fuentes._guardar_cache_visual", side_effect=guardar), \
             patch("fuentes._embed", side_effect=falso_embedding):
            primera = construir_indice_visual(fotos, limite=1)
            segunda = construir_indice_visual(fotos, limite=1)
            self.assertEqual(primera["calculadas"], 1)
            self.assertEqual(segunda["calculadas"], 0)
            resultado = buscar_indice_visual("lotería", fotos, limite=1)
            self.assertEqual(len(resultado), 1)
            self.assertEqual(resultado[0]["similitud"], 1.0)
            self.assertEqual(len(entradas), 2)  # imagen 1 vez y consulta 1 vez
            self.assertIsInstance(entradas[0], dict)
            self.assertIn("image", entradas[0])
            self.assertIsInstance(entradas[1], str)

    def test_formato_api_imagen_y_texto(self):
        from unittest.mock import patch, MagicMock
        from fuentes import _embed
        with patch("requests.post") as post:
            rsp = MagicMock()
            rsp.ok = True
            rsp.json.return_value = {"embeddings": [[0.0]*768]}
            post.return_value = rsp
            self.assertEqual(len(_embed({"image": "ABC"})), 768)
            self.assertEqual(post.call_args.kwargs["json"]["input"],
                             [{"image": "ABC"}])
            self.assertEqual(len(_embed("viviendas")), 768)
            self.assertEqual(post.call_args.kwargs["json"]["input"],
                             ["viviendas"])

if __name__ == "__main__":
    unittest.main()
