"""Pruebas reproducibles: motor S11 genérico con archivos propios, sin redes/modelos."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import proyecto

class TransferenciaS11(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="s11-transferencia-")
        self.raiz = Path(self.tmp.name) / "mi_proyecto"
        proyecto.crear_proyecto(self.raiz)
        self.cfg = proyecto.cargar_config(self.raiz / "config.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_iniciar_y_plan_no_sobrescribe(self):
        self.assertEqual(proyecto.inventario(self.raiz, self.cfg), [])
        (self.raiz / "entradas/textos/a.txt").write_text("Los contratos están organizados", encoding="utf-8")
        self.assertEqual(len(proyecto.plan(self.raiz, self.cfg)), 1)
        with self.assertRaises(FileExistsError):
            proyecto.crear_proyecto(self.raiz)

    def test_etl_texto_parquet_hash_tamper_indexar_buscar(self):
        archivo = self.raiz / "entradas/textos/minuta.txt"
        archivo.write_text("Orden de compra número 18. Valor 320000 pesos.", encoding="utf-8")
        proyecto.ejecutar(self.raiz, self.cfg)
        filas = proyecto.leer_filas(self.raiz)
        self.assertEqual(len(filas), 1)
        self.assertEqual(filas[0]["tipo"], "texto")
        self.assertEqual(filas[0]["sha256"], proyecto.sha256(archivo))
        self.assertTrue((self.raiz / "salidas/catalogo.parquet").is_file())
        candidatos = [json.loads(s) for s in
                      (self.raiz / "salidas/candidatos.jsonl").read_text().splitlines()]
        self.assertTrue(any(c["valor"] == "320000" for c in candidatos))
        self.assertTrue(all(c["evidencia"] in filas[0]["extracted_text"] for c in candidatos))
        self.assertTrue(all(c["path"] == filas[0]["path"] for c in candidatos))
        self.assertTrue(proyecto.auditar(self.raiz))
        with patch.object(proyecto, "_embed", side_effect=lambda xs, cfg: [[1.] * 768 for _ in xs]):
            proyecto.indexar(self.raiz, self.cfg)
            resultados = proyecto.buscar(self.raiz, self.cfg, "¿Cuál es el valor?", topk=3)
            self.assertEqual(len(resultados), 1)
            self.assertEqual(resultados[0]["path"], "entradas/textos/minuta.txt")
        # Cambiar modelo invalida consultas del índice anterior.
        alterada = json.loads(json.dumps(self.cfg))
        alterada["embeddings"]["modelo"] = "otro-modelo"
        with patch.object(proyecto, "_embed") as emb:
            with self.assertRaisesRegex(ValueError, "Modelo cambiado"):
                proyecto.buscar(self.raiz, alterada, "contratos", 3)
            emb.assert_not_called()
        archivo.write_text("Alterado", encoding="utf-8")
        self.assertFalse(proyecto.auditar(self.raiz))
        with patch.object(proyecto, "_embed") as emb:
            with self.assertRaisesRegex(ValueError, "Catálogo cambió"):
                # Índice viejo se invalida si se regenera el catálogo.
                proyecto.ejecutar(self.raiz, self.cfg)
                proyecto.buscar(self.raiz, self.cfg, "contratos", 3)
            emb.assert_not_called()

    def test_candidatos_fechas_y_referencias_no_duplicados(self):
        fila = {"path": "entradas/textos/acta.txt", "sha256": "a"*64,
                "source_name": "ejemplo", "text_origin": "texto_usuario",
                "extracted_text": "Pedido A17 del 15-11-2026 por 320000 COP.",
                "segments": []}
        datos = proyecto.extraer_candidatos(fila)
        self.assertEqual(len([c for c in datos if c["tipo"] == "fecha"]), 1)
        self.assertTrue(any(c["tipo"] == "referencia" and "A17" in c["valor"] for c in datos))
        self.assertEqual(len([c for c in datos if c["valor"] == "320000"]), 1)

    def test_ocr_imagen_y_pdf_reales(self):
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new("RGB", (1400, 430), "white")
        f = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 65)
        ImageDraw.Draw(img).text((45, 90), "FACTURA 18 PAGO APROBADO", font=f, fill="black")
        path_img = self.raiz / "entradas/imagenes/documento.png"
        path_pdf = self.raiz / "entradas/documentos/documento.pdf"
        img.save(path_img)
        img.save(path_pdf)
        self.cfg["asr"]["activo"] = False
        proyecto.ejecutar(self.raiz, self.cfg)
        filas = proyecto.leer_filas(self.raiz)
        self.assertEqual(len(filas), 2)
        for fila in filas:
            self.assertIn("FACTURA", fila["extracted_text"].upper())
            self.assertEqual(fila["sha256"], proyecto.sha256(self.raiz / fila["path"]))
        self.assertTrue(proyecto.auditar(self.raiz))

    def test_asr_lotes_con_motor_sustituible(self):
        wav = self.raiz / "entradas/audios/voz.wav"
        wav.write_bytes(b"datos_simulados_de_audio")
        class Segment:
            def __init__(self):
                self.start=0.
                self.end=3.
                self.text=" Factura registrada."
        class FakeWhisper:
            def __init__(self, *args, **kwargs):
                pass
            def transcribe(self, *args, **kwargs):
                return iter([Segment()]), None
        import types
        with patch.dict("sys.modules", {"faster_whisper": types.SimpleNamespace(WhisperModel=FakeWhisper)}):
            proyecto.ejecutar(self.raiz, self.cfg)
        fila = proyecto.leer_filas(self.raiz)[0]
        self.assertEqual(fila["tipo"], "audio")
        self.assertEqual(fila["segments"][0]["inicio_s"], 0.0)
        self.assertEqual(fila["extracted_text"], "Factura registrada.")
        self.assertTrue(proyecto.auditar(self.raiz))

    def test_procedencia_por_archivo_independiente(self):
        f1 = self.raiz / "entradas/textos/acta.txt"
        f2 = self.raiz / "entradas/textos/orden.txt"
        f1.write_text("Acta de ejemplo", encoding="utf-8")
        f2.write_text("Orden de compra", encoding="utf-8")
        proyecto.escribir_json(self.raiz / "metadatos.json", {
            "entradas/textos/acta.txt": {"nombre": "comite_pruebas", "credito": "autor A", "licencia": "uso_propietario"},
            "entradas/textos/orden.txt": {"nombre": "departamento_pruebas", "credito": "autor B", "licencia": "uso_autorizado"}
        })
        proyecto.ejecutar(self.raiz, self.cfg)
        registros = {r["path"]: r for r in proyecto.leer_filas(self.raiz)}
        self.assertNotEqual(registros["entradas/textos/acta.txt"]["source_name"],
                            registros["entradas/textos/orden.txt"]["source_name"])
        self.assertEqual(registros["entradas/textos/orden.txt"]["credit"], "autor B")
        self.assertTrue(proyecto.auditar(self.raiz))

    def test_limites_errores_y_config(self):
        f = self.raiz / "entradas/textos/a.txt"
        f.write_text("texto", encoding="utf-8")
        (self.raiz / "entradas/textos/b.csv").write_text("no soportado", encoding="utf-8")
        self.assertEqual(len(proyecto.inventario(self.raiz, self.cfg)), 1)
        cfg_bad = json.loads(json.dumps(self.cfg))
        cfg_bad["asr"]["modelo"] = "large-v3"
        p = self.raiz / "otro.json"
        proyecto.escribir_json(p, cfg_bad)
        with self.assertRaisesRegex(ValueError, "Modelo ASR"):
            proyecto.cargar_config(p)
        cfg_bad = json.loads(json.dumps(self.cfg))
        cfg_bad["limites"]["archivos_maximos"] = 0
        proyecto.escribir_json(p, cfg_bad)
        with self.assertRaisesRegex(ValueError, "archivos_maximos"):
            proyecto.cargar_config(p)

if __name__ == "__main__":
    unittest.main()
