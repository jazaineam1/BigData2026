"""S11: pruebas estrictamente ligeras; sin OCR, modelos ni red."""
import contextlib, hashlib, io, json, tempfile, types, unittest
from pathlib import Path
from unittest.mock import Mock, patch
import buscador_multimodal as mm

class ConsultaMultimodalTest(unittest.TestCase):
    def test_fragmentos_completos(self):
        texto = "Inicio " + ("abc " * 400) + "FIN DOCUMENTO"
        trozos = mm.trozos(texto, ancho=220, solape=35)
        self.assertGreater(len(trozos), 2)
        self.assertTrue(trozos[0].startswith("Inicio"))
        self.assertTrue(trozos[-1].endswith("FIN DOCUMENTO"))

    def test_coseno_validado(self):
        self.assertAlmostEqual(mm.coseno([1,0],[1,0]),1)
        self.assertAlmostEqual(mm.coseno([1,0],[0,1]),0)
        with self.assertRaises(ValueError): mm.coseno([0,0],[1,0])

    def test_api_embedding_lista_imagen_y_texto(self):
        response=Mock(ok=True)
        response.json.return_value={"embeddings":[[1.0]+[0.0]*767]}
        post=Mock(return_value=response)
        fake=types.SimpleNamespace(post=post, RequestException=OSError)
        with patch.dict("sys.modules",{"requests":fake}):
            for entrada in ["texto contractual",{"image":"BASE64"}]:
                self.assertEqual(len(mm.incrustar(entrada)),768)
                self.assertEqual(post.call_args.kwargs["json"]["input"],[entrada])

    def test_http_400_conserva_detalle(self):
        rsp=Mock(ok=False,status_code=400,text="input inválido")
        fake=types.SimpleNamespace(post=Mock(return_value=rsp),RequestException=OSError)
        with patch.dict("sys.modules",{"requests":fake}):
            with self.assertRaisesRegex(RuntimeError,"input inválido"):
                mm.incrustar({"image":"INVALIDA"})

    def test_cache_y_resultado_incluye_fuente_y_texto_completo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            photo=root/"foto.webp"
            photo.write_bytes(b"imagen de prueba")
            rec={"id":"imagen:foto.webp","modalidad":"imagen","fuente":"foto.webp",
                 "sha256":mm.huella(photo),"texto":"Lotería del Valle",
                 "origen_texto":"tesseract_ocr_psm11","pagina":None,
                 "credito":"Prueba","segmentos":[],"referencia_humana":""}
            vector=[1.0]+[0.0]*767
            with patch.object(mm,"ROOT",root),patch.object(mm,"INDICE",root/"index.json"),patch.object(mm,"incrustar",return_value=vector) as embed:
                idx=mm.crear_indice([rec],n_max=2)
                self.assertEqual(len(idx["entradas"]),2)
                mm.crear_indice([rec],n_max=1)
                self.assertEqual(embed.call_count,2)
                hits=mm.buscar("Lotería",[rec],idx,k=5)
                self.assertEqual(len(hits),1)
                out=io.StringIO()
                with contextlib.redirect_stdout(out):mm.presentar(hits,completo=True)
                self.assertIn("Lotería del Valle",out.getvalue())
                self.assertIn(rec["sha256"],out.getvalue())

    def test_limite_no_inicia_modelo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);photo=root/"foto.webp";photo.write_bytes(b"test")
            rec={"id":"i1","modalidad":"imagen","fuente":"foto.webp",
                 "sha256":mm.huella(photo),"texto":"Palabras para un vector"}
            with patch.object(mm,"ROOT",root),patch.object(mm,"INDICE",root/"idx.json"),patch.object(mm,"incrustar") as emb:
                with self.assertRaisesRegex(ValueError,"Se necesitan 2 vectores"):
                    mm.crear_indice([rec],n_max=1)
                emb.assert_not_called()

    def test_notebook_y_editor(self):
        root=Path(__file__).parent
        nb=json.loads((root/"01_laboratorio.ipynb").read_text())
        ids={c.get("id") for c in nb["cells"]}
        self.assertIn("s11-multimodal-intro",ids)
        self.assertIn("s11-multimodal-buscar-codigo",ids)
        for i,c in enumerate(nb["cells"]):
            if c["cell_type"]=="code":
                compile("".join(c["source"]),f"celda-{i}","exec")
        cfg=json.loads((root/".devcontainer/devcontainer.json").read_text())
        self.assertIn("ms-toolsai.jupyter",cfg["customizations"]["vscode"]["extensions"])
        self.assertTrue((root/"GUIA_ACCESO_ESTUDIANTES.md").is_file())

if __name__=="__main__":
    unittest.main()
