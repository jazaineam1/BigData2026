#!/usr/bin/env python3
"""Validador S11: notebook sincronizado, pruebas locales y opcional E2E real.

python utils/validate_session11_etl.py
python utils/validate_session11_etl.py --real

--real usa los mismos enlaces y dependencias que tendrá un estudiante nuevo.
No coloca archivos grandes ni credenciales en el repositorio.
"""
from __future__ import annotations
import argparse
import contextlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOK = ROOT / "Cuadernos" / "11_ETL_Audio_Imagenes.ipynb"


def estructura():
    subprocess.check_call([sys.executable,str(ROOT/"utils"/"build_session11_etl_audio_imagenes.py"),"--check"])
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert len(nb["cells"]) == 73, "La lección S11 espera 73 celdas"
    ids = [x["id"] for x in nb["cells"]]
    for id in ("s11-preparar","s11-cargar-motor","s11-elegir","s11-extraer-imagenes",
               "s11-extraer-audios","s11-transformar-imagenes","s11-transformar-audios",
               "s11-cargar","s11-calidad","s11-escala","s11-escala-lotes","s11-escala-comparar","s11-live-d-setup","s11-live-e-start","s11-live-e-wait","s11-live-f-benchmark","s11-live-g-fallos","s11-live-h-importar","s11-empaquetar","s11-autocomprobar"):
        assert id in ids
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            codigo = "".join(c["source"])
            compile(codigo, f"<S11:{c['id']}>", "exec")
            assert c["outputs"] == []
            assert c.get("metadata", {}).get("cellView") != "form", "El código no debe ocultarse en un formulario"
    assert ids.index("s11-formatos-practica") < ids.index("s11-calidad"), "Formatos antes de control QA"
    assert ids.index("s11-threads-codigo") < ids.index("s11-live-f-benchmark")
    assert ids.index("s11-audio-largo") < ids.index("s11-cargar")
    assert ids.index("s11-autocomprobar") < ids.index("s11-reto-fuente") < ids.index("s11-reto-ficha")
    assert "OCR" in "".join(next(x["source"] for x in nb["cells"] if x["id"]=="s11-reto-ocr-guia"))
    assert "article_id" in "".join(next(x["source"] for x in nb["cells"] if x["id"]=="s11-reto-fuente"))
    assert ids.index("s11-reto-ficha") < ids.index("s11-audionoticia-entrada") < ids.index("s11-audionoticia-integral")
    assert "ACTIVAR_ASR = False" in "".join(next(x["source"] for x in nb["cells"] if x["id"]=="s11-audionoticia-asr"))
    assert "parafrasis_demo" in "".join(next(x["source"] for x in nb["cells"] if x["id"]=="s11-audionoticia-info"))
    assert ids.index("s11-audionoticia-integral") < ids.index("s11-entrega-integral") < ids.index("s11-reto-cierre")
    assert ids.index("s11-escala") < ids.index("s11-escala-lotes") < ids.index("s11-escala-comparar") < ids.index("s11-empaquetar")
    assert ids.index("s11-extraer-imagenes") < ids.index("s11-extraer-audios")
    print("VALIDACIÓN S11: estructura, contrato, orden de tutorial y sintaxis OK")


def laboratorio_real():
    import matplotlib
    matplotlib.use("Agg")
    nb = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="s11-etl-real-") as temp:
        base = Path(temp)
        (base/"utils").mkdir()
        shutil.copy2(ROOT/"utils"/"s11_etl_core.py",base/"utils"/"s11_etl_core.py")
        shutil.copy2(ROOT/"utils"/"s11_noticia_imagen.py",base/"utils"/"s11_noticia_imagen.py")
        shutil.copy2(ROOT/"utils"/"s11_audio_noticia.py",base/"utils"/"s11_audio_noticia.py")
        shutil.copy2(ROOT/"utils"/"s11_etl_live.py",base/"utils"/"s11_etl_live.py")
        shutil.copy2(ROOT/"utils"/"s11_live_dashboard.py",base/"utils"/"s11_live_dashboard.py")
        shutil.copy2(ROOT/"utils"/"s10_asset_bridge.py",base/"utils"/"s10_asset_bridge.py")
        previo = Path.cwd()
        os.chdir(base)
        try:
            espacio = {"__name__":"__main__","__file__":str(NOTEBOOK)}
            for celda in nb["cells"]:
                if celda["cell_type"]!="code":
                    continue
                codigo = "".join(celda["source"])
                if celda["id"]=="s11-elegir":
                    codigo = codigo.replace(
                        "ALTERNATIVA_DESCARTADA = 0 #@param",
                        "ALTERNATIVA_DESCARTADA = 1 #@param")
                    codigo = codigo.replace(
                        "LIMITE_ELEGIDO = 0 #@param",
                        "LIMITE_ELEGIDO = 2 #@param")
                if celda["id"]=="s11-escala-lotes":
                    # La prueba E2E ejercita la ampliación aunque para el alumno esté desactivada.
                    codigo = codigo.replace("ACTIVAR_ESCALA = False #@param",
                                            "ACTIVAR_ESCALA = True #@param")
                if celda["id"]=="s11-empaquetar":
                    codigo = codigo.replace("DESCARGAR_ZIP=False #@param", "DESCARGAR_ZIP=False #@param")
                print(f"\n>>> S11 · {celda['id']}",flush=True)
                exec(compile(codigo, f"<S11:{celda['id']}>", "exec"),espacio)
            controles=espacio["CONTROLES"]
            assert len(controles)==9 and all(controles.values()),controles
            verificar=espacio["core"].verificar(espacio["RAIZ"])
            assert verificar["ok"] and verificar["filas"]==42,verificar
            assert espacio["ARCHIVO_FINAL"].exists()
            assert espacio["RESULTADO_LIVE"]["verified"]["ok"]
            assert espacio["BENCHMARK_S11"]["measurements"]["fingerprint"].nunique()==1
            assert len(espacio["TABLA_THREADS"])==3
            assert espacio["REINTENTO"]["manifest"]["retries"]==1
            assert espacio["CANCELADO"]["status"]=="cancelled"
            assert espacio["RECUPERADO"]["verified"]["ok"]
            print("S11 LIVE E2E REAL: estados, threads 1/2/4, speedup, cancelación y huellas equivalentes")
            assert espacio["REPORTE_ESCALA"].is_file()
            import zipfile
            with zipfile.ZipFile(espacio["REPORTE_ESCALA"]) as report:
                assert report.testzip() is None
                assert "escala_manifest.json" in report.namelist()
                assert "comparaciones_s11.csv" in report.namelist()
            info_escala = espacio["resultado_escala"]["verified"]
            assert info_escala["ok"] and info_escala["rows"] == 174 and info_escala["sources"] == 102, info_escala
            print("S11 ESCALA REAL: 32 fotos + 40 imágenes UCI + 30 voces distintas = 102 RAW; 174 derivados; particiones verificadas")
            if os.environ.get("S11_CI_MEDIO") == "1":
                ampliado=espacio["core"].ejecutar_escala_s11(espacio["RAIZ"],modo="medio",tamano_lote=64)
                assert ampliado["verified"]["ok"] and ampliado["verified"]["sources"]==332
                assert ampliado["verified"]["rows"]==564
                print("S11 MEDIO REAL: 32 fotografías + 200 manuscritos + 100 voces = 332 fuentes; 564 derivados verificados")
                imagenes_med=espacio["core"].extraer_imagenes(espacio["RAIZ"],max_imagenes=32)
                imagenes_med+=espacio["core"].extraer_imagenes_digitos(espacio["RAIZ"],200)
                voces_med=espacio["core"].extraer_audios(espacio["RAIZ"],max_audios=100)
                threads_med=espacio["motor_live"].run_live(
                    espacio["RAIZ"],imagenes_med,voces_med,workers=4,batch_size=64,
                    label="qa_medio_threads",core=espacio["core"])
                assert threads_med["verified"]["ok"] and threads_med["verified"]["rows"]==564
                assert threads_med["manifest"]["sources"]==332
                print("S11 THREADS MEDIO REAL: 332 fuentes con 4 threads, 564 derivados, SHA válido")
            assert espacio["prueba_evidencias"]["ok"]
            assert espacio["analisis_audio"]["text_origin"]=="parafrasis_demo"
            assert espacio["ruta_informe_audio"].is_file()
            assert espacio["ruta_bandeja"].is_file()
            assert espacio["path_zip_integral"].is_file()
            with zipfile.ZipFile(espacio["path_zip_integral"]) as z:
                assert z.testzip() is None
                assert "audio/ficha_audio.json" in z.namelist()
                assert "manifest.json" in z.namelist()
            assert espacio["resumen_multimedia"]["same_article_as_audio_verified"] is False
            print("S11 AUDIO NOTICIA: ASR opcional, entidades/cantidades y evidencia auditada; fuentes separadas")
            print("S11 E2E REAL: 32 imágenes y 10 WAV originales, 42 derivados, Parquet/JSONL, QA 9/9, ZIP OK")
        finally:
            os.chdir(previo)


def main():
    a=argparse.ArgumentParser()
    a.add_argument("--real",action="store_true")
    args=a.parse_args()
    estructura()
    if args.real: laboratorio_real()


if __name__=="__main__":
    main()
