"""Pruebas deterministas: extracción de noticia, vínculo real por ID y ficha."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from utils import s11_noticia_imagen as news


def fixture_corpus():
    return [
        {"_id": 3562373, "titulo": "Informe de prueba sobre contratos públicos",
         "subtitulo": "Se analizan datos verificables en una ciudad",
         "url": "https://www.eltiempo.com/ejemplo-3562373",
         "publicado": "2026-06-05", "seccion": "Datos",
         "cuerpo": [
             {"texto": "En un documento consultado se consignaron 250 millones de pesos."},
             {"contenido": "La imagen es contextual y no demuestra el contenido por sí sola."}
         ]},
        {"_id": 3547321, "titulo": "Otro artículo de contexto",
         "cuerpo": "Información pública disponible para investigación académica."}
    ]


class NoticiasFotosTest(unittest.TestCase):
    def test_descarga_una_vez_y_vincula_por_article_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            raw=json.dumps(fixture_corpus()).encode()
            with patch.object(news,"descargar_corpus",return_value=raw) as download:
                rows,meta=news.cargar_noticias(root)
                second,m2=news.cargar_noticias(root)
            self.assertEqual(download.call_count,1)
            self.assertEqual(meta["count"],2)
            self.assertEqual(meta["sha256"],m2["sha256"])
            self.assertEqual(rows,second)

    def test_extrae_titulo_cuerpo_cifras_sin_inventar_union(self):
        original={"article_id":"3562373","original_path":"raw/imagenes/real.webp",
                  "original_sha256":"a"*64,"credit":"Fuente editorial","source_url":"https://example.com"}
        article=news.buscar_noticia_por_imagen(original,fixture_corpus())
        self.assertEqual(article["article_id"],"3562373")
        self.assertIn("Informe de prueba",article["titulo"])
        self.assertIn("250 millones",article["texto_lectura"])
        self.assertTrue(any("250 millones" in x for x in article["posibles_cifras_en_texto"]))
        self.assertGreater(len(article["palabras_frecuentes"]),0)
        self.assertTrue(article["not_related_to_MINDS14"])
        with self.assertRaisesRegex(ValueError,"coincidencias"):
            news.buscar_noticia_por_imagen({"article_id":"999","original_path":"x",
                                            "original_sha256":"x"},fixture_corpus())

    def test_ficha_verifica_sha_y_no_reproduce_articulo_entero(self):
        import hashlib
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            body=b"foto de prueba educativa"
            ruta=root/"raw/imagenes/real.webp"
            ruta.parent.mkdir(parents=True)
            ruta.write_bytes(body)
            original={"article_id":"3562373","original_path":"raw/imagenes/real.webp",
                      "original_sha256":hashlib.sha256(body).hexdigest(),"credit":"Cortesía",
                      "source_url":"https://example.com"}
            article=news.buscar_noticia_por_imagen(original,fixture_corpus())
            path=news.guardar_ficha(root,article,
                "Se aprecia texto de ejemplo en una fotografía de prueba",
                "Prueba OCR","imagen_real")
            doc=json.loads(path.read_text())
            self.assertEqual(doc["article_id"],"3562373")
            self.assertLessEqual(len(doc["fragmento_breve"]),220)
            self.assertNotIn("texto_lectura",doc)
            self.assertTrue(doc["no_asociar_audios_MINDS14"])
            ruta.write_bytes(b"manipulado")
            with self.assertRaisesRegex(ValueError,"SHA-256"):
                news.guardar_ficha(root,article,"Una observación visual de prueba",
                                    "","no_disponible")


if __name__=="__main__":
    unittest.main()
