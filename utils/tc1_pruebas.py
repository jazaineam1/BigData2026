# -*- coding: utf-8 -*-
'''Apoyo de las pruebas del TC1: API SECOP simulada con datos reales congelados e imágenes PNG.'''
from __future__ import annotations

import gzip
import json
import struct
import threading
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import tc1_contrato as C

FIXTURES = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "tc1"
# Los datos congelados P03_* son los de la ventana 2025-03 (marzo de 2025).
FIXTURE, FIXTURE_VENTANA = "P03", "2025-03"


def codigo_para(ventana, prefijo="9"):
    '''Un código de prueba cuya ventana es la pedida: así las pruebas descargan los datos congelados de esa ventana.'''
    for i in range(100000, 1000000):
        if C.ventana_de([f"{prefijo}{i}"]) == ventana:
            return f"{prefijo}{i}"
    raise ValueError(f"no hay código para {ventana}")


def servidor_socrata(fixture=FIXTURE, offset_429="500"):
    '''Sirve $select/$limit/$offset y count(*) sobre los datos congelados; inyecta un 429 una vez.'''
    datos = {}
    for nombre in ("procesos", "contratos"):
        with gzip.open(FIXTURES / f"{fixture}_{nombre}.json.gz", "rt", encoding="utf-8") as fh:
            datos[C.ENDPOINTS[nombre]] = json.load(fh)
    estado = {"peticiones": 0, "429_enviados": 0}

    class Manejador(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            u = urlparse(self.path)
            q = {k: v[0] for k, v in parse_qs(u.query).items()}
            filas = datos.get(u.path.rsplit("/", 1)[-1].replace(".json", ""))
            estado["peticiones"] += 1
            if filas is None:
                self.send_response(404)
                self.end_headers()
                return
            if offset_429 is not None and q.get("$offset") == offset_429 and estado["429_enviados"] == 0:
                estado["429_enviados"] += 1
                self.send_response(429)
                self.send_header("Retry-After", "0")
                self.end_headers()
                return
            if q.get("$select", "").startswith("count(*)"):
                cuerpo = [{"n": str(len(filas))}]
            else:
                inicio, limite = int(q.get("$offset", 0)), int(q.get("$limit", 1000))
                columnas = q.get("$select", "").split(",")
                cuerpo = [{k: v for k, v in f.items() if k in columnas} for f in filas[inicio:inicio + limite]]
            data = json.dumps(cuerpo, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), Manejador)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, estado


def png(ancho, alto):
    fila = b"\x00" + b"\x9b\xb5\xd6" * ancho
    chunk = lambda t, d: struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", ancho, alto, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(fila * alto)) + chunk(b"IEND", b""))


def evidencias_checklist(html):
    '''[(paso, fragmento)] de cada evidencia del checklist; los «…» separan partes variables.'''
    import re
    salida = []
    for paso, bloque in re.findall(r'data-paso="(\w+)">(.*?)</div>', html, re.S):
        for ev in re.findall(r'<span class="ev">(.*?)</span>', bloque):
            plano = re.sub(r"<[^>]+>", "", ev).replace("&lt;", "<").replace("&gt;", ">")
            for trozo in (t.strip(" ·") for t in plano.split("…")):
                if len(trozo) >= 8 and "P0X" not in trozo:
                    salida.append((paso, trozo))
    return salida


def verificar_evidencias(html, salida, omitir=()):
    '''Fragmentos del checklist que NO aparecen en la salida real del cuaderno.'''
    return [(p, t) for p, t in evidencias_checklist(html) if p not in omitir and t not in salida]
