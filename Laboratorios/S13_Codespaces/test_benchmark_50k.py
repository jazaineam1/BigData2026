"""Pruebas de contrato científico de 50k, sin inferir embeddings."""
import unittest
import numpy as np
import pandas as pd
from benchmark_50k_test_fijo import (
    generar_conjuntos, calidad, vectorizador, huellas_ids, TAMANOS, N_TEST
)

class ControlCientifico(unittest.TestCase):
    def test_parametros_invariables(self):
        self.assertEqual(TAMANOS,(1000,10000,20000,50000))
        self.assertEqual(N_TEST,10000)
        a,b=vectorizador(),vectorizador()
        self.assertEqual(a.get_params(),b.get_params())

    def test_metricas_identicas_en_prediccion_perfecta(self):
        from benchmark_unspsc_tfidf_dask import ETIQUETAS
        x=list(ETIQUETAS)
        m=calidad(x,x)
        self.assertEqual(m["f1_macro"],1.0)
        self.assertEqual(m["balanced_accuracy"],1.0)

    def test_hash_orden_ids(self):
        self.assertEqual(huellas_ids(["1","2"]),huellas_ids(["1","2"]))
        self.assertNotEqual(huellas_ids(["1","2"]),huellas_ids(["2","1"]))


if __name__=="__main__":
    unittest.main()
