"""Ensayos de paridad: los dos caminos deben recibir mismo modelo y datos."""
import unittest
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.svm import LinearSVC
from benchmark_paridad_50k import svm, PARAMETROS_XGB, evaluar
from benchmark_unspsc_tfidf_dask import CODIGO, ETIQUETAS

class Paridad50kTest(unittest.TestCase):
    def test_ambos_svm_son_iguales(self):
        m1,m2=svm(),svm()
        self.assertEqual(m1.get_params(),m2.get_params())
        X=csr_matrix(np.array([[1,0],[0,1],[1,1],[0,0]],dtype=np.float32))
        y=["80","85","80","85"]
        m1.fit(X,y)
        m2.fit(X.copy(),y)
        self.assertEqual(list(m1.predict(X)),list(m2.predict(X)))
    def test_objetivo_y_etiquetas(self):
        self.assertEqual(PARAMETROS_XGB["objective"],"multi:softprob")
        self.assertEqual(PARAMETROS_XGB["num_class"],len(ETIQUETAS))
        self.assertEqual(CODIGO.fullmatch("V1.80111600").group(1)[:2],"80")
    def test_metricas(self):
        y=["80","85","80","85"]
        self.assertEqual(evaluar(y,y)["f1_macro"],round(2/len(ETIQUETAS),5))
        self.assertEqual(evaluar(y,y)["balanced_accuracy"],1.0)
if __name__=="__main__":
    unittest.main()
