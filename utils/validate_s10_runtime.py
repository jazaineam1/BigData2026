#!/usr/bin/env python3
"""Recorrido completo y casos negativos usando SOLO imágenes reales del ZIP docente.
Uso: python utils/validate_s10_runtime.py --entrada ZIP --salida CARPETA_NUEVA
No descarga terceros; no genera ni publica imágenes de sustitución.
"""
import argparse,json,shutil,sys,time,zipfile
from pathlib import Path
import pandas as pd
sys.path.insert(0,str(Path(__file__).resolve().parent))
import s10_pipeline as e
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--entrada',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args()
if a.salida.exists():raise ValueError('Usa una carpeta nueva para no alterar trabajo previo')
a.salida.mkdir(parents=True);root=a.salida/'work';checks=[];start=time.perf_counter()
def check(ok,label):
    if not ok:raise AssertionError(label)
    checks.append(label);print('OK · '+label,flush=True)
def rejects(fn,label):
    try:fn()
    except (ValueError,TypeError,FileNotFoundError):check(True,label);return
    raise AssertionError('Debió rechazar: '+label)
inv,jobs=e.initialize(a.entrada,root,count=32)
check(len(jobs)==32 and inv['counts']['image_references']==5152,'E: 32 imágenes reales y catálogo completo de 5152 referencias')
raw={j['job_id']:e.sha256_file(root/j['raw_path']) for j in jobs}
rows,m=e.run_batch(jobs,root,stop_after=16);check(m['states']=={'DONE':16,'FAILED':0,'PENDING':16},'T: pausa de 16/32 conserva pendientes')
rejects(lambda:e.export_package(root,inv,jobs,e.context_for(inv)),'L rechaza perfil incompleto')
rows,m=e.run_batch(jobs,root);check(m['processed_now']==16 and m['skipped_verified']==16,'T: continúa sin duplicar trabajo')
_,m=e.run_batch(jobs,root,profile='vista320',workers=2);check(m['processed_now']==32 and m['peak_active']<=2,'T: segundo perfil y concurrencia acotada')
_,m=e.run_batch(jobs,root);check(m['processed_now']==0 and m['skipped_verified']==32,'T: reejecución idempotente revalida las 32 salidas')
check(all(e.sha256_file(root/j['raw_path'])==raw[j['job_id']] for j in jobs),'T conserva todos los RAW')
check(e.export_package(root,inv,jobs,e.context_for(inv))['ok'],'L: JSONL/Parquet, binarios y contexto coherentes')
for params in [('redacta',1,2,1),(True,1,2,1),(1.0,1,2,1),(9999,1,2,1),(1,1,1,1),(1,3,1,1)]:
    rejects(lambda:e.record_decision(root,*params),'Decisión rechaza '+repr(params))
check(e.record_decision(root,1,1,2,4)['complete'],'Decisión propia cerrada incluye alternativa y límite')
check(e.export_package(root,inv,jobs,e.context_for(inv))['ok'],'Carga incorpora decisión propia')
archive=e.pack(root,a.salida/'producto.zip');restored=a.salida/'restaurado'
check(e.unpack_and_verify(archive,restored)['ok'],'ZIP restaurado y verificado en ruta nueva')
inv2,jobs2=e.open_workspace(restored);_,m=e.run_batch(jobs2,restored)
check(m['processed_now']==0 and m['skipped_verified']==32,'Paquete portable continúa sin runtime original')
rejects(lambda:e.pack(restored,a.salida/'stale.zip'),'Paquete detecta métricas cambiadas sin actualizar carga')
check(e.export_package(restored,inv2,jobs2,e.context_for(inv2))['ok'],'Recarga actualiza las métricas después de reejecutar')
# Copias técnicas: mutaciones para probar detectores, nunca datos de clase.
def mutation(label,fn):
    target=a.salida/'negativo';shutil.copytree(root,target);fn(target)
    check(not e.verify_package(target)['ok'],label);shutil.rmtree(target)
def change_manifest(t,fn):
    file=t/'manifest_s10.json';obj=json.loads(file.read_text());fn(obj);e.atomic_json(file,obj)
mutation('Rechaza catálogo JSONL vacío',lambda t:(t/'outputs/assets.jsonl').write_text(''))
mutation('Rechaza hash falso de export',lambda t:change_manifest(t,lambda o:o['files'].__setitem__('outputs/assets.parquet','0'*64)))
mutation('Rechaza thumbnail ausente',lambda t:(t/rows[0]['derived_path']).unlink())
mutation('Rechaza RAW alterado',lambda t:(t/jobs[0]['raw_path']).write_bytes(b'CORRUPT'))
mutation('Rechaza origen distinto de adquisición real',lambda t:change_manifest(t,lambda o:o.__setitem__('origin_kind','otro')))
mutation('Rechaza rutas fuera del paquete',lambda t:change_manifest(t,lambda o:o['files'].__setitem__('../escape','0'*64)))
mutation('Rechaza decisión alterada después de cargar',lambda t:(t/'checks/decision.json').write_text('{}'))
# Recuperación: borrar un derivado real exige nuevo trabajo, nunca DONE ciego.
(root/rows[0]['derived_path']).unlink();_,m=e.run_batch(jobs,root)
check(m['processed_now']==1 and m['skipped_verified']==31,'Recupera un derivado faltante sin repetir otros 31')
check(e.export_package(root,inv,jobs,e.context_for(inv))['ok'],'Recuperación vuelve a producir paquete íntegro')
for relative in ['../fuera','/absoluto','C:/drive','x\\escape']:
    rejects(lambda:e.safe_path(root,relative),'Ruta no portable rechazada '+relative)
bad=a.salida/'escape.zip'
with zipfile.ZipFile(bad,'w') as z:z.writestr('../escape.txt','no')
rejects(lambda:e.unpack_and_verify(bad,a.salida/'escape'),'ZIP con traversal rechazado')
report={'ok':True,'checks':checks,'seconds':time.perf_counter()-start,'images':32,'results':64,'scope':'Linux Python 3.12; imágenes reales; no valida GUI de VS Code, Windows ni Colab'}
(a.salida/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
