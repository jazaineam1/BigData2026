#!/usr/bin/env python3
"""QA S10 multimodal: ejecuta las celdas del cuaderno publicado de punta a punta."""
import json, os, shutil, sys, tempfile
from pathlib import Path
os.environ["MPLBACKEND"] = "Agg"
ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos/10_Imagenes_Audio.ipynb"
APP = ROOT / "Presentaciones/s10-imagenes-audio.html"
nb = json.loads(NB.read_text(encoding="utf-8"))
assert nb["nbformat"] == 4 and len(nb["cells"]) >= 25
ids = {c["id"] for c in nb["cells"]}
must = {"s10-intro", "s10-imagen-raw", "s10-imagen-features", "s10-audio-raw",
        "s10-audio-ventana", "s10-audio-espectrograma", "s10-catalogo",
        "s10-consulta", "s10-decision", "s10-verificar", "s10-hoja"}
assert must <= ids, must - ids
html=APP.read_text(encoding="utf-8")
assert html.count('class="slide') == 14
for widget in ["imageSize","imageThreshold","imageHistogram","audioUpload","recordAudio",
               "waveCanvas","spectrumCanvas","exportObservations","data-question"]:
    assert widget in html, widget
assert "https://servicios.eltiempo.com/audios/3530042.wav" in html
assert "fetch('https://servicios.eltiempo.com" not in html
with tempfile.TemporaryDirectory(prefix="bigdata-s10-qa-") as temp:
    os.chdir(temp)
    scope={"__name__":"__main__"}
    for c in nb["cells"]:
        if c["cell_type"] != "code":
            continue
        source="".join(c["source"])
        exec(compile(source, c["id"], "exec"), scope)
    root=Path("work_s10_multimodal")
    assert (root/"raw/documento_demo.png").exists()
    assert (root/"raw/senal_demo.wav").exists()
    assert scope["informe"]["ok"], scope["informe"]
    assert len(scope["reabierto"]) == 13
    assert len(scope['audios_reales']) == 10
    assert len(set(x['sha256'] for x in scope['audios_reales'])) == 10
    assert all(x['license']=='CC-BY-4.0' for x in scope['audios_reales'])
    assert all((root/x['path']).is_file() for x in scope['audios_reales'])
    assert (root/'outputs/source_registry.json').is_file()
    assert scope['registro_fuentes']['cross_dataset_article_matches'] == 0
    assert scope['reabierto'].groupby('modality').size().to_dict()=={'audio':11,'image':2}
    assert scope["metricas_ventanas"].iloc[1]["rms"] == 0
    first=scope["comprobar"](root)
    assert first["ok"]
    # Cambiar bytes del derivado debe invalidar la cadena SHA.
    changed=root/"derived/documento_160.png"
    original=changed.read_bytes()
    changed.write_bytes(b"cambio deliberado de QA")
    assert not scope["comprobar"](root)["ok"]
    changed.write_bytes(original)
    assert scope["comprobar"](root)["ok"]
    # Las decisiones inválidas no se aceptan.
    dec=scope["decision"]
    assert not dec["complete"], "El 0 predeterminado debe ser pendiente"
    print("S10 OK: notebook ejecutado, 2 imágenes + 11 audios (10 voces reales con licencia), catálogo reabierto, manifiesto e integridad")
