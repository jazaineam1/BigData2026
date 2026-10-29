#!/usr/bin/env python3
"""Ejecuta el cuaderno publicado con imágenes reales; no sustituye Colab GUI."""
import argparse,json,time,zipfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--entrada',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--cantidad',type=int,choices=[8,32],default=32);p.add_argument('--locale-cp1252',action='store_true');a=p.parse_args()
if a.salida.exists():raise ValueError('Salida debe ser nueva')
a.salida.mkdir(parents=True)
if a.locale_cp1252:
 original_read,original_write=Path.read_text,Path.write_text
 def read(self,*args,**kwargs):kwargs.setdefault('encoding','cp1252');return original_read(self,*args,**kwargs)
 def write(self,*args,**kwargs):kwargs.setdefault('encoding','cp1252');return original_write(self,*args,**kwargs)
 Path.read_text,Path.write_text=read,write
root=Path(__file__).resolve().parents[1]
nb=json.loads((root/'Cuadernos/10_ETL_Multimedia.ipynb').read_text(encoding='utf-8'))
env={'S10_INPUT_ZIP':str(a.entrada.resolve()),'S10_BASE':str(a.salida.resolve()),'__name__':'__main__'}
timings=[];started=time.perf_counter();sources={}
for cell in nb['cells']:
 if cell['cell_type']!='code':continue
 source=''.join(cell['source']);source='\n'.join(line for line in source.splitlines() if not line.startswith('%pip'))
 if cell['id']=='s10-raw':source=source.replace('CANTIDAD=32',f'CANTIDAD={a.cantidad}')
 sources[cell['id']]=source;t=time.perf_counter();exec(compile(source,cell['id'],'exec'),env);timings.append({'cell':cell['id'],'seconds':time.perf_counter()-t})
assert len(env['recargado'])==a.cantidad*2
# Repetir carga y extracción no duplica ni invalida el trabajo posterior.
for id in ['s10-entrada','s10-contexto','s10-raw']:exec(compile(sources[id],id,'exec'),env)
_,metric=env['procesar_lote']('catalogo640');assert metric['processed_now']==0 and metric['skipped_verified']==a.cantidad
# Selección propia cerrada: válida; texto libre rechazado realmente al ejecutar.
decision=env['record_decision'](env['TRABAJO'],1,1,2,4);assert decision['complete']
for values in [('redacta',1,2,4),(True,1,2,4),(1,1,1,4)]:
 try:env['record_decision'](env['TRABAJO'],*values)
 except (TypeError,ValueError):pass
 else:raise AssertionError('Se aceptó respuesta no válida')
assert env['export_package'](env['TRABAJO'],env['inventario'],env['trabajos'],env['context_for'](env['inventario'],env['ENTIDAD']))['ok']
archive=a.salida/'producto_verificado.zip';env['pack'](env['TRABAJO'],archive)
assert env['unpack_and_verify'](archive,a.salida/'restauracion_final')['ok']
with zipfile.ZipFile(a.entrada) as z:assert not any(n.endswith(('.py','.ipynb')) for n in z.namelist())
report={'ok':True,'images':a.cantidad,'rows':a.cantidad*2,'seconds':time.perf_counter()-started,'slowest_cell':max(timings,key=lambda t:t['seconds']),'load_repeated':True,'closed_decision_validated':True,'restore_verified':True,'encoding':'cp1252_simulado' if a.locale_cp1252 else 'UTF8_entorno','scope':'Python Linux; dependencias preinstaladas. No valida interfaz Colab ni Windows nativo.'}
(a.salida/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(report,ensure_ascii=False))
