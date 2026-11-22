"""Pruebas OFFSET rápidas con HTTP simulado. No se consulta SECOP ni se usa Actions pesado."""
from __future__ import annotations
import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "utils"))
import proyecto_final_offset as secop


class Respuesta:
    def __init__(self, status, rows, headers=None):
        self.status_code = status
        self.data = rows
        self.headers = headers or {}

    def json(self):
        return self.data

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class OffsetTests(unittest.TestCase):
    def respuesta(self, url, params, headers, timeout):
        self.assertEqual(url, secop.ENDPOINT)
        self.assertEqual(params["$where"], secop.WHERE)
        self.assertIn(":id ASC", params["$order"])
        o, n = params["$offset"], params["$limit"]
        return Respuesta(200, [{"id": f"fila-{i}", "valor": i} for i in range(o, o+n)])

    def test_paginacion_completa_y_equivalencia(self):
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=self.respuesta, dormir=lambda _: None)
            self.assertTrue(r["exito"])
            self.assertTrue(r["mismas_filas_y_orden"])
            self.assertEqual(r["serie"]["offsets"], [0, 20])
            self.assertEqual(r["serie"]["sha256"], r["paralelo"]["sha256"])
            self.assertEqual(len(json.loads((pathlib.Path(carpeta) /
                              "A_paginas_paralelo.json").read_text())), 40)

    def test_ultima_pagina_parcial(self):
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=self.respuesta,
                               total=45, page_size=20, dormir=lambda _: None)
            self.assertTrue(r["exito"])
            self.assertEqual([p["limit"] for p in r["serie"]["paginas"]], [20, 20, 5])

    def test_pagina_incompleta(self):
        def incompleta(url, params, headers, timeout):
            resp = self.respuesta(url, params, headers, timeout)
            if params["$offset"] == 20:
                resp.data.pop()
            return resp
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=incompleta, dormir=lambda _: None)
            self.assertFalse(r["exito"])
            self.assertIn("incompleta", r["error_detalle"])

    def test_reintento_http_429(self):
        vistos = {}
        def throttle(url, params, headers, timeout):
            o = params["$offset"]
            vistos[o] = vistos.get(o, 0) + 1
            if vistos[o] == 1:
                return Respuesta(429, [], {"Retry-After": "1"})
            return self.respuesta(url, params, headers, timeout)
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=throttle, dormir=lambda _: None)
            self.assertTrue(r["exito"])
            self.assertTrue(any(p["attempts"] == 2 for p in r["serie"]["paginas"]))

    def test_mutacion_fuente(self):
        vistos = {}
        def mutable(url, params, headers, timeout):
            o = params["$offset"]
            vistos[o] = vistos.get(o, 0) + 1
            resp = self.respuesta(url, params, headers, timeout)
            if vistos[o] > 1:
                resp.data[0]["valor"] = -100
            return resp
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=mutable, dormir=lambda _: None)
            self.assertTrue(r["exito"])
            self.assertFalse(r["mismas_filas_y_orden"])


    def test_http_400_no_reintentar(self):
        llamadas = []
        def fallo(url, params, headers, timeout):
            llamadas.append(params["$offset"])
            return Respuesta(400, [])
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=fallo, dormir=lambda _: None)
            self.assertFalse(r["exito"])
            self.assertEqual(len(llamadas), 1)

    def test_json_invalido(self):
        def fallo(url, params, headers, timeout):
            return Respuesta(200, {"message": "formato inválido"})
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=fallo, dormir=lambda _: None)
            self.assertFalse(r["exito"])
            self.assertIn("JSON", r["error_detalle"])

    def test_timeout_reintento(self):
        visitas = {}
        def fallo(url, params, headers, timeout):
            offset = params["$offset"]
            visitas[offset] = visitas.get(offset, 0) + 1
            if visitas[offset] == 1:
                raise TimeoutError("timeout controlado")
            return self.respuesta(url, params, headers, timeout)
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=fallo, dormir=lambda _: None)
            self.assertTrue(r["exito"])

    def test_retry_after_largo_respeta_limite(self):
        visitas = []
        def fallo(url, params, headers, timeout):
            visitas.append(params["$offset"])
            return Respuesta(429, [], {"Retry-After": "60"})
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=fallo, dormir=lambda _: None)
            self.assertFalse(r["exito"])
            self.assertEqual(len(visitas), 1)
            self.assertIn("Retry-After 60", r["error_detalle"])

    def test_offsets_invalidos(self):
        for off in (-20, 5, 40):
            with self.assertRaises(ValueError):
                secop.parametros(off)
        with self.assertRaises(ValueError):
            secop.descargar(paralelo=False, get=self.respuesta, total=90)

    def test_http_429_persistente(self):
        def bloqueado(*args, **kwargs):
            return Respuesta(429, [], {"Retry-After": "1"})
        with tempfile.TemporaryDirectory() as carpeta:
            r = secop.ejecutar(destino=carpeta, get=bloqueado, dormir=lambda _: None)
            self.assertFalse(r["exito"])
            self.assertIn("HTTP 429", r["error_detalle"])


if __name__ == "__main__":
    unittest.main()
