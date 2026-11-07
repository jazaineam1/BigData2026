#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auditoría docente opcional por re-inferencia, distinta del manifest de estudiante.

La comparación admite diferencias de versiones y de CPU; no demuestra autoría
individual ni sustituye revisión humana. Se utiliza sobre un ZIP ya extraído
por calificar_tc2_zip.extraer_seguro. Ejecutar en entorno aislado, sin secretos.
Requisitos: pytesseract, Tesseract + spa, faster-whisper y AV compatible.
"""
from __future__ import annotations
import difflib
import json
import re
import unicodedata
from pathlib import Path


def _palabras(texto):
    s="".join(ch for ch in unicodedata.normalize("NFKD",str(texto).lower())
              if not unicodedata.combining(ch))
    return re.findall(r"[a-z0-9]+",s)


def _similitud(a,b):
    aa=_palabras(a);bb=_palabras(b)
    if not aa and not bb:return 1.0
    if not aa or not bb:return 0.0
    return round(difflib.SequenceMatcher(None,aa,bb,autojunk=False).ratio(),4)


def _ocr_leido(ruta,idioma):
    from PIL import Image
    import pytesseract
    from pytesseract import Output
    with Image.open(ruta) as image:
        data=pytesseract.image_to_data(image.convert("RGB"),lang=idioma,
                                       config="--psm 6",output_type=Output.DICT)
    texto=[]
    for word,conf in zip(data["text"],data["conf"]):
        try:score=float(conf)
        except (ValueError,TypeError):score=-1
        if score>=0 and str(word).strip():texto.append(str(word).strip())
    return " ".join(texto)


def auditar(carpeta, n_audios=10, motor_asr=None, lector_ocr=None):
    """Vuelve a leer 2 imágenes y escucha n_audios sin consultar las predicciones declaradas.

    motor_asr opcional y lector_ocr son sólo para pruebas offline: CI E2E utiliza
    implementaciones reales, sin inyectar dobles.
    """
    carpeta=Path(carpeta)
    ocr=json.loads((carpeta/"E4/ocr.json").read_text(encoding="utf-8"))
    asr=json.loads((carpeta/"E5/asr.json").read_text(encoding="utf-8"))
    voces=json.loads((carpeta/"E5/audios.json").read_text(encoding="utf-8"))["audios"]
    fotos={Path(x["archivo"]).name:x for x in ocr["resultados"]}
    fotos_objetivo=("ranking.png","perfil_640.png")
    fotos_scores=[]
    lectura=lector_ocr or _ocr_leido
    for nombre in fotos_objetivo:
        if nombre not in fotos:raise ValueError("No se entregó predicción para "+nombre)
        actual=lectura(carpeta/"E4"/nombre,"spa")
        reportado=fotos[nombre].get("texto_ocr","")
        fotos_scores.append({"archivo":nombre,"similitud":_similitud(actual,reportado),
                             "coincide":_similitud(actual,reportado)>=0.72})
    asr_filas=asr["audios"]
    if len(asr_filas)!=10 or len(voces)!=10:raise ValueError("Se exigen diez audios y diez hipótesis")
    if n_audios<1 or n_audios>10:raise ValueError("n_audios debe estar entre 1 y 10")
    # Se muestrean registros distintos, equiespaciados. Por defecto se re-ejecutan los diez.
    indices=sorted(set(round(i*9/max(n_audios-1,1)) for i in range(n_audios)))
    if n_audios==1:indices=[4]
    if len(indices)!=n_audios:raise ValueError("Muestra no única")
    if motor_asr is None:
        from faster_whisper import WhisperModel
        motor_asr=WhisperModel("tiny",device="cpu",compute_type="int8",cpu_threads=2,num_workers=1)
    audios_scores=[]
    for ix in indices:
        fuente=voces[ix]
        pred=asr_filas[ix]
        if fuente["source_record_id"]!=pred["source_record_id"]:
            raise ValueError("ID de la voz no coincide con predicción")
        audio=carpeta/"E5/audio"/fuente["archivo"]
        parts,_=motor_asr.transcribe(str(audio),language="es",beam_size=1,
                        vad_filter=False,condition_on_previous_text=False)
        transcripcion=" ".join(str(p.text).strip() for p in parts).strip()
        sim=_similitud(transcripcion,pred.get("transcripcion_asr",""))
        audios_scores.append({"voz":int(fuente["n"]),"similitud":sim,
                              "coincide":sim>=0.64 or
                                (not _palabras(transcripcion) and not _palabras(pred.get("transcripcion_asr","")))})
    # No se exigen transcripciones perfectas; sólo reproducibilidad de la predicción.
    buen_audio=sum(int(x["coincide"]) for x in audios_scores)
    audio_ok=buen_audio>=max(1,(4*n_audios+4)//5)
    imagen_ok=all(x["coincide"] for x in fotos_scores)
    return {"schema":"tc2-auditoria-v1","modo":"re-inferencia_independiente",
            "ocr":{"aprobado":imagen_ok,"perfiles":fotos_scores},
            "asr":{"aprobado":audio_ok,"muestra":n_audios,"coincidencias":buen_audio,
                   "registros":audios_scores},
            "aprobado":imagen_ok and audio_ok,
            "advertencia":"Comparar contenido no prueba autoría. Revisar versión, entorno y salidas si hay discrepancias."}


def aplicar_auditoria(reporte,auditoria):
    """Falla cerrada en los controles de reconocimiento ante evidencia reproducible discordante.

    No penaliza divergencias en otros controles que sí son correctos; el docente
    tiene la última palabra si hay diferencia ambiental.
    """
    controles=reporte["controles"]
    changes={}
    for tipo,codigos in (("ocr",("E4.4",)),("asr",("E5.4","E5.5"))):
        if not auditoria[tipo]["aprobado"]:
            for codigo in codigos:
                original=controles[codigo]["puntos"]
                controles[codigo]["puntos"]=0
                controles[codigo]["ok"]=False
                controles[codigo]["nivel"]="requiere_revision"
                controles[codigo]["detalle"]="Re-inferencia docente discrepante; requiere revisión humana antes de nota final."
                changes[codigo]=original
    puntos=sum(v["puntos"] for v in controles.values())
    reporte["puntaje"]=puntos
    # Misma regla del core para redondear medio punto hacia arriba.
    import math
    reporte["nota_provisional"]=math.floor((1+4*puntos/100)*10+0.5+1e-9)/10
    reporte["auditoria_media"]=auditoria
    reporte["ajustes_de_auditoria"]=changes
    if changes:
        reporte["pendiente_revision_docente"]="OCR/ASR discrepa en re-inferencia: revisar entorno y entrega antes de cerrar nota."
    return reporte
