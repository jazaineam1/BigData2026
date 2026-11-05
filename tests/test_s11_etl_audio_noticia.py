"""S11: audio de noticia -> metadatos reales, candidatos auditables, reporte."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import wave
import unittest
import numpy as np

from utils import s11_audio_noticia as an


class AudioNoticiaTest(unittest.TestCase):
    TEXT = (
        "La Superintendencia de Industria y Comercio, SIC, pedirá información "
        "a más de cincuenta compañías. El aumento fue del 23 por ciento. "
        "Fenalco y la ANDI hablan del mercado y los precios. "
        "Panamericana y Olímpica aparecieron en la noticia. "
        "Se mencionaron cuarenta mil referencias, promociones y descuentos."
    )

    def test_entities_quantities_topics_have_exact_text_evidence(self):
        analysis=an.extraer_informacion(self.TEXT,origen="transcripcion_aportada")
        check=an.verificar_candidatos(self.TEXT,analysis)
        self.assertTrue(check["ok"],check)
        entities={x["candidate"] for x in analysis["entities_candidates"]}
        self.assertIn("Superintendencia de Industria y Comercio",entities)
        self.assertIn("Fenalco",entities)
        self.assertIn("ANDI",entities)
        self.assertIn("Panamericana",entities)
        self.assertIn("Olímpica",entities)
        numbers=[x["matched_text"].lower() for x in analysis["quantity_candidates"]]
        self.assertTrue(any("más de cincuenta" in x for x in numbers),numbers)
        self.assertTrue(any("23 por ciento" in x for x in numbers),numbers)
        topics={x["topic"] for x in analysis["topic_candidates"]}
        self.assertIn("precios",topics)
        self.assertIn("competencia",topics)
        self.assertIn("promociones",topics)
        # La evidencia debe coincidir realmente con cada tramo fuente.
        for group in ("entities_candidates","quantity_candidates","topic_candidates"):
            for x in analysis[group]:
                self.assertEqual(self.TEXT[x["start_char"]:x["end_char"]],x["matched_text"])

    def test_percentages_with_symbol_and_decimals(self):
        texto = "Se informó 23% en precios, 23 %., 12,5% en ofertas y 23 por ciento."
        out=an.extraer_informacion(texto,origen="transcripcion_aportada")
        cantidades=[e["matched_text"] for e in out["quantity_candidates"]]
        self.assertIn("23%",cantidades)
        self.assertIn("23 %",cantidades)
        self.assertIn("12,5%",cantidades)
        self.assertIn("23 por ciento",cantidades)
        self.assertTrue(an.verificar_candidatos(texto,out)["ok"])

    def test_timestamps_only_from_real_asr_segments(self):
        segmentos=[
            {"start_s":0.5,"end_s":2.1,"text":"La SIC reportó 23%"},
            {"start_s":2.1,"end_s":4.4,"text":"en precios y competencia."},
        ]
        texto=" ".join(x["text"] for x in segmentos)
        evidencia=an.extraer_informacion(texto,origen="asr",segmentos=segmentos)
        self.assertTrue(an.verificar_candidatos(texto,evidencia)["ok"])
        matched=next(x for x in evidencia["quantity_candidates"] if x["matched_text"]=="23%")
        self.assertEqual(matched["audio_interval_s"]["start"],0.5)
        self.assertEqual(matched["audio_interval_s"]["end"],2.1)
        self.assertEqual(matched["audio_interval_s"]["precision"],"segmento_asr_no_palabra")
        sin_tiempo=an.extraer_informacion(texto,origen="parafrasis_demo")
        self.assertFalse(any("audio_interval_s" in item for item in
                             sin_tiempo["quantity_candidates"]))
        with self.assertRaises(ValueError):
            an.extraer_informacion(texto,origen="transcripcion_aportada",segmentos=segmentos)
        with self.assertRaises(ValueError):
            an.extraer_informacion(texto,origen="asr",segmentos=[
                {"start_s":0,"end_s":2,"text":"texto inventado"}])

    def test_no_asr_falsely_claimed_from_demo(self):
        x=an.extraer_informacion("La SIC analiza precios.",origen="parafrasis_demo")
        self.assertEqual(x["text_origin"],"parafrasis_demo")
        self.assertIn("SIC",x["entities_candidates"][0]["matched_text"])
        with self.assertRaises(ValueError):
            an.extraer_informacion("La SIC analiza precios.",origen="asr_simulado")
        with self.assertRaises(ValueError):
            an.extraer_informacion("",origen="asr")

    def test_real_wav_metadata_and_report_provenance(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            raw=root/"3530042.wav"
            sr=8000
            phase=np.arange(sr,dtype=np.float64)/sr
            one_second=np.rint(8000*np.sin(2*np.pi*220*phase)).astype("<i2")
            with wave.open(str(raw),"wb") as w:
                w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr)
                w.writeframesraw(one_second.tobytes())
            meta=an.inspeccionar_audio(raw)
            self.assertEqual(meta["encoding_label"],"WAV")
            self.assertAlmostEqual(meta["duration_s"],1)
            self.assertTrue(meta["extension_matches_encoding"])
            x=an.extraer_informacion(self.TEXT,origen="transcripcion_aportada")
            dest=an.guardar_informe(root,meta,x,source_type="audio_usuario",reference_text=True)
            report=json.loads(dest.read_text(encoding="utf-8"))
            self.assertEqual(report["audio_metadata"]["original_sha256"],meta["original_sha256"])
            self.assertFalse(report["editorial_article_link_verified"])
            self.assertTrue(report["reference_text_not_asr"])
            self.assertNotIn(self.TEXT, dest.read_text(encoding="utf-8"))  # no redistribuir todo

    def test_detects_corrupt_span(self):
        x=an.extraer_informacion("Fenalco analiza precios",origen="parafrasis_demo")
        x["entities_candidates"][0]["matched_text"]="otra institución"
        self.assertFalse(an.verificar_candidatos("Fenalco analiza precios",x)["ok"])


if __name__=="__main__":
    unittest.main()
