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
    assert len(nb["cells"]) == 29, "La lección S11 espera 29 celdas"
    ids = [x["id"] for x in nb["cells"]]
    for id in ("s11-preparar","s11-cargar-motor","s11-elegir","s11-extraer-imagenes",
               "s11-extraer-audios","s11-transformar-imagenes","s11-transformar-audios",
               "s11-cargar","s11-calidad","s11-escala","s11-escala-lotes","s11-escala-comparar","s11-empaquetar","s11-autocomprobar"):
        assert id in ids
    for c in nb["cells"]:
        if c["cell_type"] == "code":
            codigo = "".join(c["source"])
            compile(codigo, f"<S11:{c['id']}>", "exec")
            assert c["outputs"] == []
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
                if celda["id"]=="s11-empaquetar":
                    codigo = codigo.replace("DESCARGAR_ZIP=False #@param", "DESCARGAR_ZIP=False #@param")
                print(f"\n>>> S11 · {celda['id']}",flush=True)
                exec(compile(codigo, f"<S11:{celda['id']}>", "exec"),espacio)
            controles=espacio["CONTROLES"]
            assert len(controles)==9 and all(controles.values()),controles
            verificar=espacio["core"].verificar(espacio["RAIZ"])
            assert verificar["ok"] and verificar["filas"]==42,verificar
            assert espacio["ARCHIVO_FINAL"].exists()
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
