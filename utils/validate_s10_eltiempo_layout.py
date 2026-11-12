"""Comprueba organización RAW/derivados del conjunto de 30 fotografías de S10."""
from __future__ import annotations
import json
import subprocess
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
B=ROOT/"Datos/S10_Eltiempo_fotos"
j=json.loads((B/"fuentes_index.json").read_text(encoding="utf-8"))
pares=j["pares"]
assert len(pares)==30
assert sorted(p["id"] for p in pares)==[f"{n:03d}" for n in range(1,31)]
assert len(list((B/"raw").iterdir()))==30
assert len(list((B/"derived/ocr").iterdir()))==30
assert not list(B.glob("eltiempo_*")), "Mezcla de RAW y derivados en raíz"

for par in pares:
    for campo,fmt in [("original",{"JPEG","WEBP"}),("derivado_para_ocr",{"PNG"})]:
        rel=par[campo]
        p=(B/rel).resolve()
        assert p.is_file() and B.resolve() in p.parents,(campo,rel)
        with Image.open(p) as img:
            img.verify()
            assert img.format in fmt,(p,img.format)
        gitsha=subprocess.check_output(["git","hash-object",str(p)],text=True).strip()
        sha_key="git_sha1_original" if campo=="original" else "git_sha1_derivado"
        assert gitsha==par[sha_key],(rel,"Los bytes cambiaron")
print("OK:",len(pares),"fotografías RAW +",len(pares),"derivados PNG; sin modificaciones de bytes")
