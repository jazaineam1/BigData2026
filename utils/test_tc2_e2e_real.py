#!/usr/bin/env python3
"""Prueba completa del TC2 en Python CPU, con E5 real y diez voces MINDS14.
No equivale a comprobar autenticación de Google Colab/Drive ni conexión Atlas remota.
Ejecuta además re-inferencia independiente de OCR/Whisper desde el ZIP docente.
"""
from __future__ import annotations
import ast,json,os,re,sys,tempfile,time,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
NB=ROOT/"Cuadernos/Taller_Control_2.ipynb"
PARAMS={
 "PAREJA_ID":"test-e2e",
 "INTEGRANTE_1":"Estudiante de prueba",
 "CODIGO_1":"20260001",
 "APELLIDO_1":"TEST",
 "INTEGRANTE_2":"",
 "CODIGO_2":"",
 "APELLIDO_2":"",
 "GUARDAR_AVANCE_EN_DRIVE":False,
 "PREDICCION_INICIAL":"Podrían cambiar los documentos y el orden",
 "PALABRA_NUEVA":"mantenimiento",
 "PREDICCION_CAMBIO":"No puedo saberlo sin ejecutar",
 "MODO_BASE_VECTORIAL":"Ruta local (NO es Atlas)",
 "TOP_K_ALTERNO":3,
 "MOTOR_ELEGIDO":"RRF",
 "MOTOR_DESCARTADO":"BM25",
 "LIMITE_RANKING":"Solo cubre los juicios etiquetados",
 "PERFIL_PREFERIDO":"640",
 "LIMITE_IMAGEN":"Reducir puede volver ilegibles las etiquetas",
 "POSICION_VOZ":1,
 "LIMITE_AUDIO":"RMS y FFT no transcriben palabras",
 "REFERENCIA_HUMANA_NO_ES_ASR":True,
 "MODELO_DEFENSA":"RRF",
 "QUE_NO_DICE_AUDIO":"Transcripción ni intención",
 "QUE_NO_DICE_IMAGEN":"Contenido semántico del contrato"
}
def replace_params(source):
    changed=[]
    for key,v in PARAMS.items():
        match=re.search(r"^"+re.escape(key)+r"\s*=\s*.*#@param\b.*$",source,re.M)
        if match:
            val=repr(v)
            source=source[:match.start()]+key+" = "+val+" #@param (prueba real TC2)"+source[match.end():]
            changed.append(key)
    return source,changed
def referencia_ci(nombre, argumentos):
    """Oráculo de prueba de integración, no una solución ejecutable del estudiante.

    Un notebook publicado no tiene esta función. La calificación efectiva se basa
    en resultados propios y en la auditoría del ZIP. Las pruebas públicas permiten
    inspeccionar criterios: ocultar respuestas en un repositorio abierto no es seguridad.
    """
    import numpy as np
    import tc2_core as core  # esta prueba vive en utils/
    if nombre=="frecuencia_documental_equipo":
        return len([d for d in argumentos["coleccion"]
                    if argumentos["termino"] in core.tokens(core.texto(d))])
    if nombre=="coseno_mini":
        a=np.asarray(argumentos["a"]);b=np.asarray(argumentos["b"])
        return float((a*b).sum()/(np.linalg.norm(a)*np.linalg.norm(b)))
    if nombre=="precision_cinco":
        return len(set(argumentos["ids"][:5]) & set(argumentos["relevantes"]))/5
    if nombre=="rrf_dos_posiciones":
        return sum(1/(60+argumentos[k]) for k in ("posicion_bm25","posicion_e5"))
    if nombre=="luminancia_rgb":
        return float(np.asarray(argumentos["rgb"])@np.asarray([.2126,.7152,.0722]))
    if nombre=="rms_manual":
        return float(np.linalg.norm(argumentos["muestras"])/np.sqrt(len(argumentos["muestras"])))
    if nombre=="ids_desde_texto":
        return re.findall(r"CO1\.REQ\.\d{7,10}",str(argumentos["texto"]).upper())
    if nombre=="palabras_clave_propias":
        return sorted(set(core.tokens(argumentos["texto"])))
    raise ValueError("Ejercicio de CI no registrado: "+nombre)


FUNCIONES_CI=(
    "frecuencia_documental_equipo","coseno_mini","precision_cinco",
    "rrf_dos_posiciones","luminancia_rgb","rms_manual",
    "ids_desde_texto","palabras_clave_propias"
)
def completar_ejercicios_de_prueba(source):
    """Sustituye un hueco por un adaptador exclusivo de CI, nunca por una respuesta lista para pegar."""
    for nombre in FUNCIONES_CI:
        if "def "+nombre+"(" not in source:continue
        if "    return ____" not in source:raise AssertionError("El ejercicio exige un solo hueco: "+nombre)
        source=source.replace("    return ____",
            '    return __referencia_ci__("'+nombre+'", locals())',1)
    return source


def main():
    os.environ["MPLBACKEND"]="Agg"
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    nb=json.loads(NB.read_text(encoding="utf-8"))
    codes=[(i,"".join(c["source"])) for i,c in enumerate(nb["cells"]) if c["cell_type"]=="code"]
    with tempfile.TemporaryDirectory(prefix="tc2-e2e-") as d:
        old=os.getcwd();os.chdir(d)
        env={"__name__":"__main__","__file__":str(NB),
             "__referencia_ci__":referencia_ci}
        used=set()
        try:
            for i,source in codes:
                patched,changes=replace_params(source);used.update(changes)
                patched=completar_ejercicios_de_prueba(patched)
                print("\nTC2 E2E · celda",i,"·",patched.splitlines()[0][:90],flush=True)
                started=time.monotonic()
                try:exec(compile(patched,f"TC2-cell-{i}","exec"),env,env)
                except Exception as e:
                    traceback.print_exc()
                    raise RuntimeError(f"Falló celda ejecutable {i}: {type(e).__name__}: {e}") from e
                print("Celda",i,"OK ·",round(time.monotonic()-started,2),"s",flush=True)
            if set(PARAMS)-used:raise AssertionError("Parámetros no aplicados: "+repr(set(PARAMS)-used))
            assert len(nb["cells"])>=110, "TC2 debe incluir historia y talleres OCR/ASR completos"
            report=env["INFORME"]
            print("Puntaje final real, sin Atlas:",report["puntaje"])
            if report["puntaje"]!=98:
                for cod,val in report["controles"].items():
                    if val["puntos"]!=val["maximo"]:print("PARCIAL:",cod,val)
                if "OCR_REAL" in env:
                    print("DIAGNÓSTICO OCR:",[(x["archivo"],x["tokens_ocr"],x["cobertura_ids"],x["ids_secop_verificados"])
                                             for x in env["OCR_REAL"]["resultados"]])
                    print("IDs esperados:",env["OCR_REAL"]["ids_esperados"])
                raise AssertionError("98/100 esperados: 2 puntos de Atlas no asignables por ejecución local.")
            z=env["ZIP"];manifest=env["MANIFEST_EXTERNO"]
            assert z.exists() and z.stat().st_size>100_000
            assert manifest.exists()
            import zipfile
            with zipfile.ZipFile(z) as f:
                names=set(f.namelist())
                assert {"explorador.html","E4/ocr.json","E4/ocr_manual.json","E5/audios.json","E5/asr.json","E5/asr_manual.json","E6/catalogo.jsonl","E6/catalogo.parquet","E6/recuperacion.json"}<=names
                assert len([x for x in names if re.fullmatch(r"E5/audio/voz_\d\d\.wav",x)])==10
            # El docente recupera exactamente el mismo puntaje desde el ZIP extraído.
            import calificar_tc2_zip as grader
            recalc=grader.corregir(z,env["HUELLA"],audit_media=True)
            assert recalc["auditoria_media"]["aprobado"], "Re-inferencia docente debe concordar"
            assert recalc["puntaje"]==98, "Auditoría independiente debe preservar 98/100"
            # Evidencias realmente generadas por OCR/ASR, no referencias copiadas.
            ocr=env["OCR_REAL"];asr=env["ASR_REAL"]
            assert ocr["motor"]=="tesseract" and len(ocr["resultados"])==3
            assert ocr["resultados"][0]["tokens_ocr"]>0
            assert ocr["resultados"][2]["tokens_ocr"]>0
            assert all(row["tokens_ocr"]>=0 for row in ocr["resultados"])
            assert asr["engine"]=="faster-whisper" and len(asr["audios"])==10
            assert sum(bool(row["transcripcion_asr"].strip()) for row in asr["audios"])>=8
            assert all(row["wer"]==env["core"].wer_palabras(row["transcripcion_referencia"],row["transcripcion_asr"])
                       for row in asr["audios"])
            assert len(env["LEIDO_CATALOGO"])==13 and all("extracted_text" in row for row in env["LEIDO_CATALOGO"])
            assert len(env["RESULTADOS_CONSULTA"]["coincidencias_texto"])>0
            print("TC2 E2E REAL: OK, 200 documentos, E5 384, OCR Tesseract 3 PNG, ASR Whisper 10 voces reales, WER, catálogo, ZIP, score 98/100.")
        finally:
            os.chdir(old)
if __name__=="__main__":main()
