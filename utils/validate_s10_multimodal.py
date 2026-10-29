#!/usr/bin/env python3
"""QA S10 multimodal: ejecuta las celdas del cuaderno publicado de punta a punta."""
import json, os, shutil, sys, tempfile
from pathlib import Path
os.environ["MPLBACKEND"] = "Agg"
ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "Cuadernos/10_Imagenes_Audio.ipynb"
APP = ROOT / "Presentaciones/s10-imagenes-audio.html"
nb = json.loads(NB.read_text(encoding="utf-8"))
assert nb["nbformat"] == 4 and len(nb["cells"]) >= 46
ids = {c["id"] for c in nb["cells"]}
must = {"s10-intro", "s10-imagen-raw", "s10-imagen-features", "s10-audio-raw",
        "s10-audio-ventana", "s10-audio-espectrograma", "s10-catalogo",
        "s10-consulta", "s10-decision", "s10-verificar", "s10-hoja",
        "s10-autocomprobar", "s10-descargar-zip", "s10-asr-ejecutar"}
assert must <= ids, must - ids
order=[c["id"] for c in nb["cells"]]
assert order.index("s10-corpus-descargar")<order.index("s10-corpus-analizar")<order.index("s10-asr-ejecutar")<order.index("s10-corpus-unir-metadatos"), "ASR debe ejecutarse después de obtener las voces"
assert order.index("s10-verificar")<order.index("s10-autocomprobar")<order.index("s10-descargar-zip")<order.index("s10-drive"), "primero comprobar, luego guardar"
html=APP.read_text(encoding="utf-8")
assert html.count('class="slide') == 23
for widget in ["imageSize","imageThreshold","imageHistogram","audioUpload","recordAudio",
               "waveCanvas","spectrumCanvas","exportObservations","data-question"]:
    assert widget in html, widget
assert "https://servicios.eltiempo.com/audios/3530042.wav" in html
# Glosario contextual, instrumentos visuales editables y mediciones dependientes.
for term in ["Histograma", "luminancia", "píxel", "RMS", "FFT", "espectrograma",
             "binarización", "contraste", "frecuencia", "códec", "WER"]:
    assert term.lower() in html.lower(), f"Falta definición pedagógica de {term}"
for control in ["quickGlossary","histogramBins","histogramExplanation","imageBrightness",
                "imageContrast","imagePixelZoom","pixelStats","toneLow","toneHigh",
                "toneGain","fftWindow","audioSpectrogram","audioEditorExplanation"]:
    assert f'id="{control}"' in html, f"Falta control funcional {control}"
for term in ["histDraw(hist,bins)","showPixelDetails()","spectrogramDraw()",
             "frequency_resolution_hz","histogram_counts"]:
    assert term in html, f"Falta calcular o dibujar {term}"

for slug in ['id="s12"','id="s13"','id="s14"','id="s15"','id="s16"','id="s17"',
             'id="s18"','id="s19"','id="s20"','id="s21"','id="s22"','id="s23"']:
    assert slug in html, slug
for step in ['Conectar','Guardar una copia en Drive','VOCES REALES VERIFICADAS: 10',
             'source_record_id','AUTOCOMPROBACIÓN: LISTO','DESCARGAR_ZIP',
             'INCOMPLETO','manifest_s10.json','32 referencias','13 filas']:
    assert step in html, step
assert 'Descargar para VS Code' not in html

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
    assert not scope["autocomprobacion_lista"], "Con las 3 decisiones en 0 debe advertir INCOMPLETO"
    assert len(scope["controles"])==9
    assert sum(scope["controles"].values())==8
    assert not scope["controles"]["09 · Decisión propia completada"]
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
    # Simular los tres cambios que realiza un estudiante, sin alterar el notebook publicado.
    student_code=next(c for c in nb["cells"] if c["id"]=="s10-decision")
    student_source="".join(student_code["source"])
    for before,after in [("PERFIL_IMAGEN=0","PERFIL_IMAGEN=1"),
                         ("REGION_AUDIO=0","REGION_AUDIO=2"),("LIMITE=0","LIMITE=1")]:
        assert before in student_source
        student_source=student_source.replace(before,after,1)
    exec(compile(student_source, "s10-decision-estudiante", "exec"), scope)
    exec(compile("".join(next(c for c in nb["cells"] if c["id"]=="s10-verificar")["source"]),
                 "s10-verificar-estudiante","exec"),scope)
    exec(compile("".join(next(c for c in nb["cells"] if c["id"]=="s10-autocomprobar")["source"]),
                 "s10-autocomprobar-estudiante","exec"),scope)
    assert scope["decision"]["complete"], scope["decision"]
    assert scope["autocomprobacion_lista"] and all(scope["controles"].values())
    # Probar ZIP completo sin ejecutar la descarga de Google Colab en CI.
    zipcell="".join(next(c for c in nb["cells"] if c["id"]=="s10-descargar-zip")["source"])
    assert "DESCARGAR_ZIP=False" in zipcell
    zipcell=zipcell.replace("DESCARGAR_ZIP=False","DESCARGAR_ZIP=True",1)
    exec(compile(zipcell,"s10-descargar-zip-estudiante","exec"),scope)
    import zipfile
    with zipfile.ZipFile(root.parent/"s10_multimodal_evidencia.zip") as package:
        assert len([n for n in package.namelist() if n.endswith(".wav") and n.startswith("raw/voz_real/")])==20
        assert "manifest_s10.json" in package.namelist()
        assert "outputs/assets.parquet" in package.namelist()
    print("AUTONOMÍA S10 OK: elección estudiantil 3/3, autocomprobación 9/9 y ZIP de 20 WAV")
    if os.getenv("S10_TEST_ASR") == "1":
        # Comprobar realmente la opción de voz->texto sobre una de las diez grabaciones.
        # Descarga Whisper tiny de acceso público solo en este job de CI.
        asr_src="".join(next(c for c in nb["cells"] if c["id"]=="s10-asr-ejecutar")["source"])
        assert "USAR_ASR=False" in asr_src
        asr_src=asr_src.replace("USAR_ASR=False","USAR_ASR=True",1)
        exec(compile(asr_src,"s10-asr-estudiante-real","exec"),scope)
        assert isinstance(scope.get("prediccion"),str) and len(scope["prediccion"].strip())>0
        assert scope.get("wer_ejemplo") is not None and 0 <= scope["wer_ejemplo"] <= 10
        print("ASR REAL OK: Whisper tiny ejecutado sobre una de las diez voces; WER calculado")

    print("S10 OK: notebook ejecutado, 2 imágenes + 11 audios (10 voces reales con licencia), catálogo reabierto, manifiesto e integridad")
