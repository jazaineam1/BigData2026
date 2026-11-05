#!/usr/bin/env python3
"""S11 end-to-end sin internet: 32 metadatos, cuatro imágenes y diez voces reales simuladas.

Las pruebas crean entradas sintéticas etiquetadas como fixture; el laboratorio real
únicamente utiliza el snapshot editorial verificado y MINDS-14 de PolyAI.
"""
import io
import json
import os
import runpy
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
import soundfile as sf
from PIL import Image
from utils import s11_etl_audio_imagenes as engine


def fixtures():
    inventory, pictures = [], {}
    for i in range(32):
        img = Image.new("RGB", (150+i, 80+i), color=(i*7 % 255, i*11 % 255, i*19 % 255))
        out=io.BytesIO()
        img.save(out, format="WEBP")
        buf=out.getvalue()
        job=f"ficticio{i:03d}"
        pictures[job] = buf
        inventory.append({
            "job_id": job, "article_id": str(35_000+i%24),
            "source_url": "https://example.invalid/imagenes/" + job,
            "credit": "FIJACIÓN ARTIFICIAL DEL TEST",
            "input_sha256": engine.digest(buf)
        })
    voices=[]
    for i in range(10):
        hz=170+i*47
        rate=16000
        seconds=1.3
        wave=(.25*np.sin(2*np.pi*hz*np.arange(int(rate*seconds))/rate)).astype(np.float32)
        out=io.BytesIO()
        sf.write(out,wave,rate,format="WAV",subtype="PCM_16")
        voices.append({"audio":{"bytes":out.getvalue()}, "path":f"fixture_{i:02d}.wav", "intent_class":i})
    packed=io.BytesIO()
    pd.DataFrame(voices).to_parquet(packed,index=False)
    return inventory, pictures, packed.getvalue()


def simulate_get(inventory, pictures, voices):
    def read(url,limit=65_000_000):
        if "inputs.json" in url:
            return json.dumps(inventory).encode()
        if "minds14" in url:
            return voices
        if url.endswith(".webp"):
            key=url.rsplit("/",1)[-1].split(".")[0]
            return pictures[key]
        raise AssertionError("URL externa no esperada en test: "+url)
    return read


def main():
    os.environ["MPLBACKEND"]="Agg"
    assert Path("Cuadernos/11_ETL_Audio_Imagenes.ipynb").exists()
    notebook=json.loads(Path("Cuadernos/11_ETL_Audio_Imagenes.ipynb").read_text(encoding="utf-8"))
    assert notebook["nbformat"]==4 and len(notebook["cells"])>=20
    ids=[c["id"] for c in notebook["cells"]]
    must=["s11-setup","s11-extract","s11-transform","s11-image-view","s11-audio-view",
          "s11-load","s11-failure","s11-autocheck","s11-export"]
    assert all(k in ids for k in must)
    assert ids.index("s11-extract")<ids.index("s11-transform")<ids.index("s11-load")<ids.index("s11-failure")
    inventory,pictures,voices=fixtures()
    with tempfile.TemporaryDirectory(prefix="s11-test-") as tmp:
        root=Path(tmp)
        with patch.object(engine,"_get",simulate_get(inventory,pictures,voices)),patch.object(engine,"VOICE_SHA",engine.digest(voices)):
            source=engine.download_sources(root,4,10)
            assert len(source["images"])==4 and len(source["audio"])==10
            rows=[]
            for x in source["images"]:
                rows.extend([engine.image_etl(root,x,max_side=320,grayscale=True),engine.image_etl(root,x,max_side=160,grayscale=False)])
            for x in source["audio"]:
                rows.append(engine.audio_etl(root,x,target_rate=16000,gain=1.0))
            report=engine.save_outputs(root,rows,source["selection"])
            proof=engine.verify_outputs(root)
            assert proof["rows"]==18 and proof["images"]==8 and proof["audio"]==10 and proof["files"]==32
            assert all(x["status"]=="ok" for x in rows)
            assert all(x["article_id"] is None for x in rows if x["modality"]=="audio")
            assert all(x["source_record_id"] is None for x in rows if x["modality"]=="image")
            before=engine.digest(root/"outputs/catalogo_s11.jsonl")
            second=engine.save_outputs(root,rows,source["selection"])
            assert before==engine.digest(root/"outputs/catalogo_s11.jsonl") and second["rows"]==18
            copied=root/"derived"/"audio"/Path(rows[-1]["derived_path"]).name
            original=copied.read_bytes()
            copied.write_bytes(b"alteracion QA")
            try:
                engine.verify_outputs(root)
            except ValueError as e:
                assert "SHA-256" in str(e)
            else:
                raise AssertionError("Se aceptaron bytes derivados alterados")
            copied.write_bytes(original)
            assert engine.verify_outputs(root)["ok"]
            # La señal silenciada NO implica silencio en fuente.
            silenced=engine.audio_etl(root,source["audio"][0],target_rate=16000,gain=0)
            assert json.loads(silenced["metrics_json"])["rms"]==0
            assert silenced["original_sha256"]==rows[8]["original_sha256"]
            # No se acepta contaminación del esquema de procedencia.
            corrupt=[dict(r) for r in rows]
            corrupt[-1]["article_id"]="contrato-ficticio"
            try:engine.save_outputs(root,corrupt,source["selection"])
            except ValueError:pass
            else:raise AssertionError("Se creó una relación editorial falsa")
            print("S11 QA E2E: 14 RAW, 18 derivados, 32 archivos, PDF no requerido, 2 catálogos, SHA OK")
    html=Path("Presentaciones/s11-etl-audio-imagenes.html").read_text(encoding="utf-8")
    assert html.count('class="slide')==17
    for token in ["RAW VERIFICADO: 4 imágenes reales + 10 grabaciones reales",
                  "PAQUETE S11 VERIFICADO","FALLO DETECTADO CORRECTAMENTE",
                  "AUTOCOMPROBACIÓN S11", "imagePreview","audioSignal", "Taller 2",
                  "no procesamos video"]:
        assert token.lower() in html.lower(),token
    print("S11 PRESENTACIÓN: 17 diapositivas, 9 hitos, controles y enlaces")
if __name__=="__main__":
    main()
