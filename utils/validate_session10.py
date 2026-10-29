#!/usr/bin/env python3
"""Contrato S10; ejecución real y navegador se verifican por separado."""
import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'utils'))
import build_session10_multimedia as notebook
import build_session10_deck as presentation
errors=[]
def need(ok,message):
    if not ok:errors.append(message)
nb=json.loads((ROOT/notebook.OUTPUT).read_text(encoding='utf-8'))
need(nb==notebook.build_notebook(),'Notebook no sincronizado')
deck=(ROOT/'Presentaciones/s10-etl-multimedia.html').read_text(encoding='utf-8')
need(deck==presentation.build(),'Presentación no sincronizada')
need(len(presentation.SLIDES)==17,'Mapa de clase incompleto')
ids={c['id'] for c in nb['cells']}
for c in nb['cells']:
 src=''.join(c['source']);need(bool(src.strip()),'Celda vacía')
 if c['cell_type']=='code':
  try:ast.parse('\n'.join(x for x in src.splitlines() if not x.startswith(('%','!'))))
  except SyntaxError as e:errors.append(str(e))
for id in ['s10-raw','s10-funcion-t','s10-bucle','s10-escribir','s10-consultar','s10-producto']:need(id in ids,'Falta E/T/L visible '+id)
need(deck.count('type="checkbox"')==6,'Seis controles nativos requeridos')
for step in notebook.STEPS:need('data-step="'+step[0]+'"' in deck,'Paso ausente '+step[0])
need('s10_proyecto_VSCode.zip' not in deck and '<iframe' not in deck,'Recorrido depende de recurso externo')
need('Universidad Central' in deck and 'Maestría en Analítica' in deck,'Falta portada institucional')
need('aria-live="polite"' in deck,'Falta feedback accesible')
need('tutorial integrado' in ''.join(nb['cells'][0]['source']),'Falta tutorial al inicio')
allcode='\n'.join(''.join(c['source']) for c in nb['cells'] if c['cell_type']=='code')
need('import s10_pipeline' not in allcode and 'sys.path' not in allcode,'Código esencial externo')
need('files.upload(' not in allcode and 'ZipFile(' not in allcode,'La entrada debe obtenerse automáticamente sin carga manual')
need('urllib.request.urlopen' in allcode and 'Datos/s10_imagenes_reales/' in allcode,'Falta conexión visible a las entradas reales del curso')
need('files.download(' not in allcode and 'pack(TRABAJO' not in allcode,'El cierre debe dejar un catálogo, sin ZIP obligatorio')
need('drive.mount(' in allcode and 'shutil.copytree(TRABAJO,conservado' in allcode and 'verify_package(conservado)' in allcode,'La conservación en Drive debe copiar y verificar la carpeta completa')
need('POSICION_NOTICIA' in allcode and 'noticias_disponibles.iloc' in allcode,'Falta consulta elegida sobre el catálogo propio')
seed=(ROOT/'infraestructura/lms/s10-multimedia-seed.sql').read_text(encoding='utf-8')
need('delete from' not in seed.lower(),'No borrar historial')
need('"visible_resources": 2' in seed,'LMS debe declarar dos recursos')
need('"tracked_activity": "bd-s10-notebook", "required": true' in seed,'Cuaderno debe ser principal')
for file in [ROOT/'index.html',ROOT/'lms/data/course.json']:need('Presentaciones/s10-imagenes-audio.html#s1' in file.read_text(encoding='utf-8'),'Falta entrada directa actual')
if errors:print('\n'.join(errors));sys.exit(1)
print('S10 OK: sincronización, E/T/L visible, tutorial nativo, dos recursos, portada e historial conservado')
