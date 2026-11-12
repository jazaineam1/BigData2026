"""Contrato mínimo: UNSPSC válido, limpieza y partición temporal."""
import unittest
import pandas as pd
from benchmark_unspsc_tfidf_dask import (
    CODIGO, texto_limpio, seleccion_n, ETIQUETAS, TOP_SEGMENTOS
)

class BenchmarkS13(unittest.TestCase):
    def test_segmento_unspc(self):
        self.assertEqual(CODIGO.fullmatch("V1.80111600").group(1)[:2],"80")
        self.assertIsNone(CODIGO.fullmatch("UNSPECIFIED"))
        self.assertIsNone(CODIGO.fullmatch("V1.8011160"))
        self.assertEqual(CODIGO.fullmatch("V1.85101600").group(1)[:2],"85")

    def test_codigo_no_se_fuga_al_texto(self):
        limpio=texto_limpio("Contrato V1.80111600","Servicio 80111600 de mantenimiento")
        self.assertNotIn("80111600",limpio)
        self.assertIn("mantenimiento",limpio)

    def test_corte_temporal_y_claves(self):
        datos=pd.DataFrame({
            "id":[str(i) for i in range(100)],
            "fecha":pd.date_range("2020-01-01",periods=100,freq="D"),
            "texto":["un documento de prueba"]*100,
            "etiqueta":["80"]*50+["85"]*50,
        })
        tr,te=seleccion_n(datos,100)
        self.assertEqual(len(tr),80)
        self.assertEqual(len(te),20)
        self.assertLessEqual(tr.fecha.max(),te.fecha.min())
        self.assertFalse(set(tr.id)&set(te.id))

    def test_clases_fijas(self):
        self.assertEqual(len(ETIQUETAS),6)
        self.assertEqual(len(TOP_SEGMENTOS),5)
        self.assertIn("OTRAS",ETIQUETAS)


if __name__=="__main__":
    unittest.main()
