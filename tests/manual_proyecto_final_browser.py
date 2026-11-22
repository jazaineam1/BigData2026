"""Smoke test OPCIONAL de navegador (NO incluido en Actions ni en Run All).

Ejecutar manualmente SOLO cuando el docente tenga Playwright + Chromium:
python tests/manual_proyecto_final_browser.py
No descarga datos reales, no entrena ni consulta Internet. Datos de prueba
deliberadamente sintéticos para validar la interfaz, nunca como evidencia SECOP.
"""
from __future__ import annotations
import csv
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Laboratorios/Proyecto_Final_2026"))
from generar_observatorio import generar

try:
    from playwright.sync_api import sync_playwright
except ImportError as exc:
    raise SystemExit("Falta Playwright en el entorno docente. No instalar en Codespaces estudiantil.") from exc


def escribir_csv(ruta,campos,filas):
    with ruta.open("w",newline="",encoding="utf-8") as archivo:
        w=csv.DictWriter(archivo,fieldnames=campos)
        w.writeheader()
        w.writerows(filas)


def verificar():
    with tempfile.TemporaryDirectory() as temporal:
        d=Path(temporal)
        registros=[
           {"id_del_proceso":"PRUEBA-101","texto":"mantenimiento de equipos",
            "modalidad":"Contratación directa","split":"train"},
           {"id_del_proceso":"PRUEBA-102","texto":"equipos médicos",
            "modalidad":"Contratación régimen especial","split":"train"},
           {"id_del_proceso":"PRUEBA-103","texto":"sistemas de información",
            "modalidad":"Contratación directa","split":"test"},
           {"id_del_proceso":"PRUEBA-104","texto":"</script><img src=x onerror=alert(1)>",
            "modalidad":"Contratación régimen especial","split":"test"}
        ]
        escribir_csv(d/"secop_final.csv",["id_del_proceso","texto","modalidad","split"],registros)
        pred=[
           {"id_del_proceso":"PRUEBA-103","modalidad_real":"Contratación directa",
            "modalidad_predicha":"Contratación directa","probabilidad_clase_predicha":".83"},
           {"id_del_proceso":"PRUEBA-104","modalidad_real":"Contratación régimen especial",
            "modalidad_predicha":"Contratación directa","probabilidad_clase_predicha":".6"}
        ]
        escribir_csv(d/"predicciones.csv",["id_del_proceso","modalidad_real",
                  "modalidad_predicha","probabilidad_clase_predicha"],pred)
        (d/"D_modelo_dask.json").write_text(json.dumps(
             {"f1_prueba_final":.33,"f1_dummy":.5,"mejor_C":.1,"workers":2}),encoding="utf-8")
        salida=d/"observatorio.html"
        assert generar(d/"secop_final.csv",d/"predicciones.csv",
                       d/"D_modelo_dask.json",salida)["filas"]==4
        contenido=salida.read_text(encoding="utf-8")
        assert "</script><img" not in contenido,"El texto del origen no debe inyectar HTML"
        with sync_playwright() as playwright:
            ejecutable=os.getenv("CHROMIUM_BIN") or "/usr/bin/chromium"
            navegador=playwright.chromium.launch(headless=True,
                 executable_path=ejecutable,args=["--no-sandbox"])
            pagina=navegador.new_page(accept_downloads=True,
                                        viewport={"width":1200,"height":800})
            errores=[]
            pagina.on("pageerror",lambda e:errores.append(str(e)))
            # Evita depender del protocolo file://, bloqueado en algunos entornos.
            pagina.set_content(contenido,wait_until="load")
            assert "4 expedientes" in pagina.locator("#resumen").inner_text()
            pagina.locator("#q").fill("sistemas")
            assert "1 expedientes" in pagina.locator("#resumen").inner_text()
            pagina.locator("#filas button").first.click()
            assert "PRUEBA-103" in pagina.locator("#detalle").inner_text()
            pagina.locator("#q").fill("")
            pagina.locator("#split").select_option("test")
            assert "2 expedientes" in pagina.locator("#resumen").inner_text()
            with pagina.expect_download() as descarga:
                pagina.locator("#exportar").click()
            assert descarga.value.suggested_filename=="consulta_observatorio_secop.csv"
            pagina.set_viewport_size({"width":375,"height":812})
            assert pagina.evaluate("document.documentElement.scrollWidth")<=375
            assert not errores,errores
            navegador.close()
    print("OK navegador: búsqueda, detalle, split, CSV, móvil e inyección HTML.")


if __name__=="__main__":
    verificar()
