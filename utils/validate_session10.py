#!/usr/bin/env python3
"""Contratos verificables de S10. No sustituye ejecutar el ZIP real ni abrir Colab."""
import ast,importlib.util,json,sys,tempfile,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'utils'))
import build_session10_multimedia as notebook
import build_session10_deck as presentation
errors=[]
def need(ok,message):
    if not ok:errors.append(message)
nb=json.loads((ROOT/'Cuadernos/10_ETL_Multimedia.ipynb').read_text())
need(nb==notebook.build_notebook(),'Notebook no sincronizado con generador')
deck=(ROOT/'Presentaciones/s10-etl-multimedia.html').read_text()
need(deck==presentation.build(),'Presentación no sincronizada con generador')
need(len(presentation.SLIDES)==16,'Ruta de 16 diapositivas')
for i,c in enumerate(nb['cells']):
    src=''.join(c['source']);need(bool(src.strip()),f'Celda vacía {i}')
    if c['cell_type']=='code':
        try:compile('\n'.join(x for x in src.splitlines() if not x.startswith(('%','!'))),f'celda {i}','exec')
        except SyntaxError as e:errors.append(str(e))
with zipfile.ZipFile(ROOT/'assets/tutoriales/s10_proyecto_VSCode.zip') as z:
    expected={'main.py':ROOT/'laboratorios/s10_etl_imagenes/main.py','paso_a_paso.py':ROOT/'laboratorios/s10_etl_imagenes/paso_a_paso.py',
              'README.md':ROOT/'laboratorios/s10_etl_imagenes/README.md','requirements.txt':ROOT/'laboratorios/s10_etl_imagenes/requirements.txt',
              'runtime/s10_pipeline.py':ROOT/'utils/s10_pipeline.py'}
    need(set(z.namelist())==set(expected),'ZIP debe contener solo proyecto editable')
    for name,path in expected.items():need(z.read(name)==path.read_bytes(),'ZIP desactualizado: '+name)
for question,options,answer in presentation.QUESTIONS:
    need(answer in [o[0] for o in options] and all(len(o)==3 and o[2] for o in options),'Opciones sin feedback')
need('aria-live' in deck and "new Option('Elige una opción…','')" in deck,'Autoevaluación debe iniciar pendiente')
checklist=(ROOT/'assets/tutoriales/s10-laboratorio-guiado.html').read_text()
need(checklist.count('type="checkbox"')==6,'Checklist debe tener seis controles propios')
need('s10-laboratorio-guiado.html' in ''.join(nb['cells'][0]['source']) or 's10-laboratorio-guiado.html' in ''.join(nb['cells'][1]['source']),'Falta checklist al inicio')
seed=(ROOT/'infraestructura/lms/s10-multimedia-seed.sql').read_text()
need('delete from' not in seed.lower(),'Seed no debe borrar historial')
need('"archived":true' in seed and '"blocks_session_completion":false' in seed,'Requisitos anteriores deben retirarse')
need("'bd-s10-project'" in seed and '"completion_basis": "resource_visits"' in seed,'Falta recurso VS Code y base de progreso explícita')
for file in [ROOT/'index.html',ROOT/'lms/data/course.json']:
    need('Presentaciones/s10-etl-multimedia.html#s1' in file.read_text(),'Ruta directa ausente '+str(file))
for p in (ROOT/'laboratorios/s10_etl_imagenes').glob('*.py'):compile(p.read_text(),str(p),'exec')
# Los JSON de origen y atomic_json son UTF-8 también bajo locale Windows-1252.
for file in [ROOT/'utils/s10_pipeline.py',ROOT/'utils/prepare_s10_real_inputs.py',*sorted((ROOT/'laboratorios/s10_etl_imagenes').glob('*.py'))]:
    tree=ast.parse(file.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in {'read_text','write_text'}:
            encoding=next((kw.value for kw in node.keywords if kw.arg=='encoding'),None)
            need(isinstance(encoding,ast.Constant) and encoding.value=='utf-8',f'Encoding explícito UTF-8 requerido: {file.name}:{node.lineno}')
if errors:
    print('S10: FAIL\n'+'\n'.join(' - '+e for e in errors));sys.exit(1)
print('S10: OK · fuentes sincronizadas, Python compilable, 16 pantallas, seis preguntas/checks, proyecto portable y LMS formativo')
