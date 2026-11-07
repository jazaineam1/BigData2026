#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Califica independientemente un ZIP TC2 sin confiar en el manifest del estudiante.
Uso: python utils/calificar_tc2_zip.py TC2_pareja.zip [--manifest-sha SHA256] [--audit-media]
El contacto institucional, fecha, identidad y procedencia se verifican fuera de esta CLI.
"""
import argparse,hashlib,json,re,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"utils"))
import tc2_core as c
MAX_FILES=300
MAX_UNCOMPRESSED=320_000_000
MAX_SINGLE=60_000_000

def extraer_seguro(archivo,carpeta):
    archivo=Path(archivo);carpeta=Path(carpeta)
    with zipfile.ZipFile(archivo) as z:
        items=z.infolist()
        if not items or len(items)>MAX_FILES:raise ValueError("ZIP vacío o con demasiadas entradas")
        if sum(i.file_size for i in items)>MAX_UNCOMPRESSED:raise ValueError("ZIP descomprimido supera 320 MB")
        for f in items:
            nombre=f.filename.replace("\\","/")
            p=Path(nombre)
            if p.is_absolute() or not p.parts or ".." in p.parts or ":" in p.parts[0]:
                raise ValueError("Ruta ZIP insegura: "+nombre[:80])
            if f.file_size>MAX_SINGLE:raise ValueError("Un archivo supera 60 MB: "+nombre[:70])
            if f.is_dir():continue
            if (f.external_attr>>16)&0o170000==0o120000:raise ValueError("Enlace simbólico en ZIP")
            destino=carpeta.joinpath(*p.parts)
            destino.parent.mkdir(parents=True,exist_ok=True)
            with z.open(f) as lectura,open(destino,"wb") as escritura:
                while True:
                    b=lectura.read(1024*1024)
                    if not b:break
                    escritura.write(b)
    return carpeta

def corregir(archivo,hash_manifest=None,audit_media=False):
    with tempfile.TemporaryDirectory(prefix="tc2-docente-") as tmp:
        trabajo=extraer_seguro(archivo,tmp)
        identidad=c.leer(Path(trabajo)/"identidad.json")
        integrantes=identidad.get("integrantes",[])
        if not integrantes or not integrantes[0].get("codigo"):
            raise ValueError("Identidad de equipo insuficiente")
        clave="-".join([str(integrantes[0]["codigo"]),str(integrantes[1]["codigo"]) if len(integrantes)>1 else ""])
        tema=c.elegir_intencion(ROOT/"Datos",clave)
        if tema["id"]!=identidad.get("intencion"):
            raise ValueError("Intención no coincide con los códigos de la pareja")
        m=Path(trabajo)/"manifest_tc2.json"
        if not m.exists():raise ValueError("Falta manifest_tc2.json en el ZIP")
        digest=c.sha(m)
        if hash_manifest and digest.lower()!=hash_manifest.lower():
            raise ValueError("SHA del correo no coincide con el manifest")
        declarado=c.leer(m)
        if declarado.get("pareja")!=identidad.get("pareja"):
            raise ValueError("Pareja incompatible entre manifest e identidad")
        propio=c.validar(trabajo,c.corpus_lista(ROOT/"Datos"),tema)
        if audit_media:
            from tc2_media_audit import auditar,aplicar_auditoria
            result=auditar(trabajo,n_audios=10)
            propio=aplicar_auditoria(propio,result)
            print("AUDITORÍA OCR:",("CONCORDANTE" if result["ocr"]["aprobado"] else "REVISAR"),
                  "· WHISPER:",("CONCORDANTE" if result["asr"]["aprobado"] else "REVISAR"))
            if not result["aprobado"]:
                print("AVISO: re-inferencia discordante; la nota se mantiene PROVISIONAL hasta revisión humana.")
        else:
            print("AUDITORÍA MEDIA NO EJECUTADA: los metadatos y SHA del ZIP no demuestran inferencia propia.")
        print("TC2 · Calificación independiente, equipo:",identidad["pareja"])
        print("Intención asignada:",tema["id"],"· SHA manifest:",digest)
        print("Declarado:",declarado.get("reporte",{}).get("puntaje"),
              "· recalculado:",propio["puntaje"],"puntos; nota provisional:",propio["nota_provisional"],"/5")
        for cod,row in propio["controles"].items():
            print(("✓" if row["ok"] else "·"),cod,str(row["puntos"])+"/"+str(row["maximo"]),row["detalle"])
        print("REVISIÓN MANUAL PENDIENTE: Atlas remoto/contingencia, identidad, acceso GitHub privado, commit y plazo.")
        return propio

def autoprobacion():
    with tempfile.TemporaryDirectory() as tmp:
        good=Path(tmp)/"good.zip";bad=Path(tmp)/"evil.zip";target=Path(tmp)/"out"
        with zipfile.ZipFile(good,"w") as z:z.writestr("E1/salida.json","{}")
        extraer_seguro(good,target)
        assert (target/"E1/salida.json").exists()
        with zipfile.ZipFile(bad,"w") as z:z.writestr("../../escape.txt","error")
        try:extraer_seguro(bad,target)
        except ValueError:pass
        else:raise AssertionError("Aceptó traversal en ZIP")
        print("TC2 ZIP QA: extracción normal y traversal bloqueado.")

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("zip",nargs="?")
    parser.add_argument("--manifest-sha")
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--audit-media",action="store_true",help="Recalcular OCR y Whisper en CPU (requiere paquetes y modelos)")
    args=parser.parse_args()
    if args.self_test:autoprobacion()
    elif args.zip:corregir(args.zip,args.manifest_sha,audit_media=args.audit_media)
    else:parser.error("indica un ZIP o --self-test")
