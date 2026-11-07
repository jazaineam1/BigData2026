#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas adversariales de la auditoría docente del TC2 (sin descargar modelos).

Los motores simulados son SÓLO dobles de las pruebas negativas. La prueba E2E
del workflow usa Tesseract y Whisper verdaderos sobre WAV/PNG reales.
"""
from __future__ import annotations
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace

from tc2_media_audit import auditar,aplicar_auditoria,_similitud


class ASRFalso:
    def transcribe(self,ruta,**kwargs):
        indice=int(Path(ruta).stem.split("_")[1])
        return iter([SimpleNamespace(text=f"Quiero revisar mi cuenta numero {indice}")]),None


def escribir(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False),encoding="utf-8")


def prueba_contradicciones():
    with tempfile.TemporaryDirectory(prefix="tc2-auditoria-") as tmp:
        carpeta=Path(tmp)
        ocr={"schema":"tc2-ocr-v1","motor":"tesseract","idioma":"spa","resultados":[
            {"archivo":"E4/ranking.png","texto_ocr":"Expediente CO1.REQ.12345678"},
            {"archivo":"E4/perfil_160.png","texto_ocr":""},
            {"archivo":"E4/perfil_640.png","texto_ocr":"Expediente CO1.REQ.12345678"}]}
        voces=[{"n":i,"archivo":f"voz_{i:02d}.wav","source_record_id":f"ficha-{i}"} for i in range(1,11)]
        trans=[{"n":i,"source_record_id":f"ficha-{i}",
                "transcripcion_asr":f"Quiero revisar mi cuenta numero {i}"}
               for i in range(1,11)]
        escribir(carpeta/"E4/ocr.json",ocr)
        escribir(carpeta/"E5/audios.json",{"audios":voces})
        escribir(carpeta/"E5/asr.json",{"audios":trans})
        for v in voces:(carpeta/"E5/audio"/v["archivo"]).parent.mkdir(parents=True,exist_ok=True)
        for v in voces:(carpeta/"E5/audio"/v["archivo"]).write_bytes(b"WAV de prueba; motor falso no lo abre")
        def lector(ruta,idioma):
            assert idioma=="spa"
            return "Expediente CO1.REQ.12345678"
        bien=auditar(carpeta,motor_asr=ASRFalso(),lector_ocr=lector)
        assert bien["aprobado"] and bien["asr"]["coincidencias"]==10
        # Ataque 1: falsificar salida OCR preservando el mismo nombre de motor.
        ocr["resultados"][0]["texto_ocr"]="texto deliberadamente falsificado sin el codigo original"
        escribir(carpeta/"E4/ocr.json",ocr)
        malo_ocr=auditar(carpeta,motor_asr=ASRFalso(),lector_ocr=lector)
        assert not malo_ocr["ocr"]["aprobado"] and malo_ocr["asr"]["aprobado"]
        # Ataque 2: reemplazar cuatro hipótesis con texto humano o inventado.
        for r in trans[:4]:r["transcripcion_asr"]="no se parece en absoluto a las palabras reales"
        escribir(carpeta/"E5/asr.json",{"audios":trans})
        malo=auditar(carpeta,motor_asr=ASRFalso(),lector_ocr=lector)
        assert not malo["ocr"]["aprobado"] and not malo["asr"]["aprobado"]
        rubrica={"controles":{k:{"maximo":v,"puntos":v,"ok":True,"nivel":"completo"}
                   for k,v in (("E4.4",6),("E5.4",6),("E5.5",2),("E6.2",6))},
                 "puntaje":20,"nota_provisional":1.8}
        revisado=aplicar_auditoria(rubrica,malo)
        assert revisado["puntaje"]==6
        assert revisado["controles"]["E6.2"]["puntos"]==6
        assert all(revisado["controles"][k]["nivel"]=="requiere_revision"
                   for k in ("E4.4","E5.4","E5.5"))
        assert _similitud("Mi cuenta está aquí","mi cuenta esta aqui")==1.0
        print("TC2 AUDITORÍA ADVERSARIAL: OK · OCR falsificado, ASR inventado y revisión de puntos.")


if __name__=="__main__":
    prueba_contradicciones()
