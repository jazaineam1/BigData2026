#!/usr/bin/env python3
"""Prueba completa del TC2 en Python CPU, con E5 real y diez voces MINDS14.
No equivale a comprobar autenticación de Google Colab/Drive ni conexión Atlas remota.
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
SOLUCIONES = {
 "frecuencia_documental_equipo": '    return sum(1 for documento in coleccion if termino in set(core.tokens(core.texto(documento))))',
 "coseno_mini": '    return float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))',
 "precision_cinco": '    return sum(ident in relevantes for ident in ids[:5])/5',
 "rrf_dos_posiciones": '    return 1/(60+posicion_bm25)+1/(60+posicion_e5)',
 "luminancia_rgb": '    return 0.2126*rgb[0]+0.7152*rgb[1]+0.0722*rgb[2]',
 "rms_manual": '    return float(np.sqrt(np.mean(np.square(muestras))))',
}
def completar_ejercicios_de_prueba(source):
    """La simulación resuelve huecos sin tocar las celdas distribuidas al estudiante."""
    for fn,solution in SOLUCIONES.items():
        if f"def {fn}(" not in source:continue
        pattern=r'(?m)^    raise NotImplementedError\\([^\\n]*\\)
    os.environ["MPLBACKEND"]="Agg"
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    nb=json.loads(NB.read_text(encoding="utf-8"))
    codes=[(i,"".join(c["source"])) for i,c in enumerate(nb["cells"]) if c["cell_type"]=="code"]
    with tempfile.TemporaryDirectory(prefix="tc2-e2e-") as d:
        old=os.getcwd();os.chdir(d)
        env={"__name__":"__main__","__file__":str(NB)}
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
            assert len(nb["cells"])>=81, "TC2 debe tener profundidad comparable al TC1"
            report=env["INFORME"]
            print("Puntaje final real, sin Atlas:",report["puntaje"])
            if report["puntaje"]!=97:
                for cod,val in report["controles"].items():
                    if val["puntos"]!=val["maximo"]:print("PARCIAL:",cod,val)
                raise AssertionError("97/100 esperados: 3 puntos de Atlas no asignables por ejecución local.")
            z=env["ZIP"];manifest=env["MANIFEST_EXTERNO"]
            assert z.exists() and z.stat().st_size>100_000
            assert manifest.exists()
            import zipfile
            with zipfile.ZipFile(z) as f:
                names=set(f.namelist())
                assert "explorador.html" in names and "E5/audios.json" in names
                assert len([x for x in names if re.fullmatch(r"E5/audio/voz_\d\d\.wav",x)])==10
            # El docente recupera exactamente el mismo puntaje desde el ZIP extraído.
            import calificar_tc2_zip as grader
            recalc=grader.corregir(z,env["HUELLA"])
            assert recalc["puntaje"]==97
            print("TC2 E2E REAL: OK, 200 documentos, E5 384, 10 voces licenciadas, imagen, RRF, HTML, ZIP, score 97/100.")
        finally:
            os.chdir(old)
if __name__=="__main__":main()

        source,count=re.subn(pattern,lambda _:solution,source,count=1)
        if count!=1:raise AssertionError("No se pudo resolver el hueco de "+fn)
    return source
def main():
    os.environ["MPLBACKEND"]="Agg"
    os.environ["HF_HUB_DISABLE_TELEMETRY"]="1"
    nb=json.loads(NB.read_text(encoding="utf-8"))
    codes=[(i,"".join(c["source"])) for i,c in enumerate(nb["cells"]) if c["cell_type"]=="code"]
    with tempfile.TemporaryDirectory(prefix="tc2-e2e-") as d:
        old=os.getcwd();os.chdir(d)
        env={"__name__":"__main__","__file__":str(NB)}
        used=set()
        try:
            for i,source in codes:
                patched,changes=replace_params(source);used.update(changes)
                print("\nTC2 E2E · celda",i,"·",patched.splitlines()[0][:90],flush=True)
                started=time.monotonic()
                try:exec(compile(patched,f"TC2-cell-{i}","exec"),env,env)
                except Exception as e:
                    traceback.print_exc()
                    raise RuntimeError(f"Falló celda ejecutable {i}: {type(e).__name__}: {e}") from e
                print("Celda",i,"OK ·",round(time.monotonic()-started,2),"s",flush=True)
            if set(PARAMS)-used:raise AssertionError("Parámetros no aplicados: "+repr(set(PARAMS)-used))
            report=env["INFORME"]
            print("Puntaje final real, sin Atlas:",report["puntaje"])
            if report["puntaje"]!=97:
                for cod,val in report["controles"].items():
                    if val["puntos"]!=val["maximo"]:print("PARCIAL:",cod,val)
                raise AssertionError("97/100 esperados: 3 puntos de Atlas no asignables por ejecución local.")
            z=env["ZIP"];manifest=env["MANIFEST_EXTERNO"]
            assert z.exists() and z.stat().st_size>100_000
            assert manifest.exists()
            import zipfile
            with zipfile.ZipFile(z) as f:
                names=set(f.namelist())
                assert "explorador.html" in names and "E5/audios.json" in names
                assert len([x for x in names if re.fullmatch(r"E5/audio/voz_\d\d\.wav",x)])==10
            # El docente recupera exactamente el mismo puntaje desde el ZIP extraído.
            import calificar_tc2_zip as grader
            recalc=grader.corregir(z,env["HUELLA"])
            assert recalc["puntaje"]==97
            print("TC2 E2E REAL: OK, 200 documentos, E5 384, 10 voces licenciadas, imagen, RRF, HTML, ZIP, score 97/100.")
        finally:
            os.chdir(old)
if __name__=="__main__":main()
