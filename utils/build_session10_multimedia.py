"""Fuente de verdad S10: apoyo ejecutable al proyecto VS Code, imágenes reales."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from utils.make_notebook import md,code

OUTPUT='Cuadernos/10_ETL_Multimedia.ipynb'


def reading(how,what,missing,error):
    return '\n\n'.join('**'+k+'** '+v for k,v in zip(
        ['Cómo se lee','Qué nos dice','Qué NO permite concluir todavía','Qué error común'],[how,what,missing,error]))


def build_cells():
    sha=hashlib.sha256((ROOT/'utils/s10_pipeline.py').read_bytes()).hexdigest()
    cells=[]
    def m(s):cells.append(md(s))
    def c(s,hidden=False):
        cell=code(s)
        if hidden:cell['metadata']['cellView']='form'
        cells.append(cell)
    m('''# Universidad Central · Maestría en Analítica de Datos
# S10 · ETL de imágenes reales: extraer, transformar y cargar

**¿Cómo prepara Laura las imágenes de sus noticias para un catálogo reutilizable?**

La ruta principal de esta sesión es un **proyecto Python en VS Code**. Este cuaderno acompaña la explicación y permite consultar o ejecutar el mismo código. [Proyecto y comandos](https://github.com/jazaineam1/BigData2026/tree/main/laboratorios/s10_etl_imagenes) · [Presentación](https://jazaineam1.github.io/BigData2026/Presentaciones/s10-etl-multimedia.html#s1) · [Tutorial](https://jazaineam1.github.io/BigData2026/assets/tutoriales/s10-laboratorio-guiado.html).

**Producto formativo:** RAW conservados, thumbnails, catálogo JSONL/Parquet, manifiesto, estados y paquete portable. No se añade una nota. Trabajamos con imágenes reales adquiridas por el docente; no generamos imágenes sintéticas ni sustituimos descargas fallidas.

**Antes de ejecutar:** recibe `S10_entradas_reales.zip` del docente. Incluye originales reales, corpus, contexto y código de apoyo. El ZIP se distribuye por la vía docente, no se promete una descarga pública inexistente. En VS Code instala `requirements.txt` y abre `paso_a_paso.py`; la carpeta se prepara antes del encuentro.

| Etapa | Qué responde | Qué deja |
|---|---|---|
| Contexto | ¿De qué noticia y entidad viene? | IDs y vínculos documentados |
| E · Extracción | ¿Qué archivo recibimos? | RAW validado y huella |
| T · Transformación | ¿Cómo lo adaptamos al uso? | Derivado con parámetros |
| L · Carga | ¿Qué puede consultar otro proceso? | Catálogo escrito y reabierto |
| Lotes | ¿Qué terminó y qué falta? | Checkpoint y métricas |
| Cierre | ¿Puede abrirlo otra persona? | Paquete verificado |
''')
    m('''## 1 · El expediente de Laura continúa

S3 modeló noticias con `imagenes[]`; S4/S5 aportaron contexto de entidades; S6 siguió procesos y proveedores; S7/S9 enseñaron a recuperar candidatos. Ahora preparamos los archivos que ese contexto referencia.

El corpus de contratación contiene **987 noticias, 976 con imágenes, 5.152 referencias y 4.071 URLs distintas**. El lote docente contiene **32 imágenes reales**. El catálogo completo y el lote procesado son cantidades distintas.

Ejemplo manual conceptual: dos noticias hacen tres referencias, dos con la misma URL. Hay tres apariciones y dos solicitudes distintas. Solo los bytes adquiridos permiten comprobar si los contenidos son iguales.

El ancla docente de S5/S6 es `CO1.REQ.2622868`, Fuerza Aeroespacial Colombiana, NIT `899999102`. Las noticias de ejemplo enlazan por entidad, no prueban hechos sobre ese contrato. El NIT no se inventa a partir de una foto.

**Pregunta para localizar en tu salida:** ¿qué noticia corresponde a la primera imagen de tu lote?''')
    c('''#@title Preparar dependencias (en VS Code: pip install -r requirements.txt)
%pip -q install pillow==13.0.0 pandas==3.1.0 pyarrow==26.0.0''',True)
    c('''#@title Abrir la entrada docente real, sin volver a descargar las fotos
from pathlib import Path
import hashlib, importlib.util, json, sys, zipfile
INPUT_ZIP=Path(globals().get('S10_INPUT_ZIP','S10_entradas_reales.zip')).resolve()
BASE=Path(globals().get('S10_BASE','work_s10_apoyo')).resolve()
if not INPUT_ZIP.exists():
    try:
        from google.colab import files
        subidos=files.upload()
        if len(subidos)!=1:raise ValueError('Selecciona solo el ZIP docente')
        INPUT_ZIP=Path(next(iter(subidos))).resolve()
    except ImportError:
        raise FileNotFoundError('Coloca S10_entradas_reales.zip junto al cuaderno o define S10_INPUT_ZIP con su ruta')
bootstrap=BASE/'runtime';bootstrap.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(INPUT_ZIP) as z:
    source=z.read('runtime/s10_pipeline.py')
EXPECTED_SHA='''+repr(sha)+'''
if hashlib.sha256(source).hexdigest()!=EXPECTED_SHA:
    raise ValueError('El código del paquete y este cuaderno tienen versiones diferentes: solicita el paquete actualizado')
module_path=bootstrap/'s10_pipeline.py';module_path.write_bytes(source)
spec=importlib.util.spec_from_file_location('s10_pipeline',module_path)
etl=importlib.util.module_from_spec(spec);spec.loader.exec_module(etl)
TRABAJO=BASE/'ejecucion'
print('Proyecto: VS Code · apoyo disponible en este cuaderno')
print('Entrada real localizada:',INPUT_ZIP.name)''',True)
    m('''## 2 · E: extraer y conservar una entrada real

La adquisición HTTP ocurrió una vez del lado docente, con pausas e identificación. E en el proyecto recupera ese snapshot real y consolida RAW verificando las huellas y la procedencia. Tener una URL no equivale a tener bytes decodificables.

`initialize(entrada, trabajo, inicio, cantidad)` abre el paquete y devuelve inventario y trabajos con rutas RAW. Una carpeta distinta permite conservar otra variante. No recorre de nuevo el sitio editorial.

**HAZ ESTO AHORA.** Ejecuta E y abre el primer RAW. En VS Code: `python main.py extraer --entrada ../S10_entradas_reales.zip --trabajo work/s10`.
''')
    c('''# E · Inventario completo y lote real disponible
INICIO=0 #@param {type:"integer"}
CANTIDAD=32 #@param {type:"integer"}
inventario,trabajos=etl.initialize(INPUT_ZIP,TRABAJO,start=INICIO,count=CANTIDAD)
print('CATÁLOGO OBSERVADO:',inventario['counts'])
print('IMÁGENES REALES DEL LOTE:',len(trabajos))
print('CONTEXTO:',etl.context_for(inventario))
primero=trabajos[0]
raw=TRABAJO/primero['raw_path']
print('article_id:',primero['article_id'],'· origen:',primero['origin_kind'])
print('URL fuente:',primero['source_url'])
print('RAW OBSERVADO:',etl.inspect_image(raw))''')
    m(reading('Los conteos del catálogo y la cantidad de archivos del lote tienen distinto grano.',
        'Qué archivos reales quedaron disponibles para esta ejecución y cómo vuelven a su noticia.',
        'No conocemos la disponibilidad ni los bytes de las URLs que no adquirimos.',
        'Contar 5.152 referencias como fotografías distintas procesadas.'))
    m('''## 3 · Lee la implementación de una imagen

Antes del lote, aprende la operación. `Image.open()` abre, `load()` decodifica; `format`, `size` y `mode` describen la entrada. `ImageOps.exif_transpose()` respeta orientación; `thumbnail()` modifica la imagen en memoria conservando proporción. `save()` escribe un archivo nuevo con formato explícito.

**Error frecuente:** renombrar el sufijo y creer que convirtió el contenido. En la adquisición real las 32 imágenes se detectaron como WEBP; al guardar JPEG sí cambian los bytes.

En VS Code abre `paso_a_paso.py` y ejecuta con `--lado 640`. Después cambia **solo** ese parámetro a 320. Mantén la misma entrada para comparar.''')
    c('''# E → T → L · Operación visible, equivalente a paso_a_paso.py
import pandas as pd
from PIL import Image, ImageOps
from IPython.display import display
hash_antes=etl.sha256_file(raw)
LADO_MAXIMO=640 #@param [320,640,1024] {type:"raw"}
with Image.open(raw) as original:
    original.load()
    entrada_info={'format':original.format,'width':original.width,'height':original.height}
    imagen=ImageOps.exif_transpose(original).convert('RGB')
    imagen.thumbnail((LADO_MAXIMO,LADO_MAXIMO))
    ejemplo=TRABAJO/'ejemplo'/('vista_'+str(LADO_MAXIMO)+'.jpg')
    ejemplo.parent.mkdir(exist_ok=True)
    imagen.save(ejemplo,'JPEG',quality=88)
    imagen.close()
with Image.open(raw) as im:
    vista=ImageOps.exif_transpose(im).convert('RGB');vista.thumbnail((640,360));display(vista);vista.close()
with Image.open(ejemplo) as im:display(im)
print('ORIGINAL:',entrada_info,'· bytes:',raw.stat().st_size)
print('DERIVADO:',etl.inspect_image(ejemplo))
print('RAW conservado:',etl.sha256_file(raw)==hash_antes)
fila={'article_id':primero['article_id'],'raw_bytes':raw.stat().st_size,
      'derived_bytes':ejemplo.stat().st_size,'max_side':LADO_MAXIMO}
pd.DataFrame([fila]).to_parquet(TRABAJO/'ejemplo/una_fila.parquet',index=False)
display(pd.read_parquet(TRABAJO/'ejemplo/una_fila.parquet'))''')
    m(reading('Compara original y derivado con dimensiones y bytes, no solo su apariencia en pantalla.',
        'El efecto de ese perfil sobre una imagen concreta; RAW debe conservar su huella.',
        'Faltan criterios y juicios independientes para afirmar calidad visual general.',
        'Prometer ahorro al convertir WEBP a JPEG; los bytes pueden aumentar.'))
    m('''## 4 · T: la misma operación por micro-lotes

`run_batch()` aplica `make_thumbnail()` y registra resultado por trabajo. El código de la transformación está en el proyecto; el helper organiza checkpoint, escritura y límites.

`batch_size` agrupa trabajos. `workers` limita cuántos están activos; no significa que todas las imágenes del lote se decodifiquen juntas. Empieza con uno. El estado durable es DONE/FAILED/PENDING; `skipped_verified` describe lo reutilizado en esta ejecución.

**HAZ ESTO AHORA.** Ejecuta un primer grupo y continúa los pendientes. No edites el checkpoint para aparentar completitud.''')
    c('''# Primer micro-lote; stop_after deja pendientes visibles sin fabricar fallos
resultados,primera_medida=etl.run_batch(trabajos,TRABAJO,profile='catalogo640',workers=1,
                                      batch_size=16,stop_after=16)
print('PRIMER MICRO-LOTE:',json.dumps(primera_medida,ensure_ascii=False,indent=2))''')
    c('''# Continuar y comprobar que lo anterior se revalida
resultados,segunda_medida=etl.run_batch(trabajos,TRABAJO,profile='catalogo640',workers=1,batch_size=16)
print('CONTINUACIÓN:',json.dumps(segunda_medida,ensure_ascii=False,indent=2))''')
    c('''# Comparar una alternativa sobre los mismos archivos reales
alternativa,medida_alternativa=etl.run_batch(trabajos,TRABAJO,profile='vista320',workers=1,batch_size=16)
tabla=pd.DataFrame(resultados+alternativa)
display(tabla[['article_id','profile','raw_format','derived_width','derived_height','raw_bytes','derived_bytes']].head(8))
display(tabla.groupby('profile')[['raw_bytes','derived_bytes']].sum())''')
    m(reading('processed_now cuenta trabajo nuevo; skipped_verified no vuelve a contarlo. Cada perfil debe terminar sus pendientes.',
        'Cómo cambian las dimensiones, bytes y trabajo al comparar dos perfiles sobre la misma entrada.',
        'Faltan otras cargas, hardware e I/O para generalizar rendimiento.',
        'Confundir estado acumulado con throughput de la ejecución actual.'))
    m('''## 5 · L: escribir, releer y consultar el catálogo

Los binarios permanecen como archivos; el catálogo conserva IDs, rutas relativas, hashes, fuente y perfil. `to_json(..., lines=True)` escribe JSONL; `to_parquet(index=False)` escribe Parquet; `read_parquet()` devuelve la tabla para comprobar lo escrito. La dependencia de motor Parquet está fijada en el proyecto.

El código del helper vuelve a leer archivos y compara esquemas/resultados. No basta que existan nombres. La integridad técnica no equivale a autenticidad editorial ni a una nota.

**Pregunta desde tu ejecución:** ¿qué artículo y qué parámetros corresponden a la primera fila de tu catálogo?''')
    c('''# L · Consolidar y releer salidas reales
reporte=etl.export_package(TRABAJO,inventario,trabajos,etl.context_for(inventario))
print('VERIFICACIÓN DE CARGA:',reporte)
if not reporte['ok']:raise ValueError('Hay propiedades pendientes: '+str(reporte['errors']))
catalogo=pd.read_parquet(TRABAJO/'outputs/assets.parquet')
display(catalogo[['article_id','profile','raw_format','derived_width','derived_height']].head())
print('Filas de trabajos/perfil:',len(catalogo))
print('Catálogo completo de referencias:',len(pd.read_parquet(TRABAJO/'catalog/image_occurrences.parquet')))''')
    m(reading('Cada fila de salida es un trabajo/perfil; la tabla de apariciones conserva contexto editorial por separado.',
        'Qué salidas puede consumir otro proceso y dónde quedaron.',
        'No se demuestra una relación de la foto con un contrato específico ni una evaluación de calidad general.',
        'Declarar carga completa sin releer y comparar JSONL/Parquet.'))
    c('''# Repetición segura: debe procesar cero trabajos nuevos si todos siguen válidos
_,repeticion=etl.run_batch(trabajos,TRABAJO,profile='catalogo640',workers=1,batch_size=16)
print('REEJECUCIÓN:',repeticion)
# Actualizar la carga después de cambiar métricas o estados
reporte=etl.export_package(TRABAJO,inventario,trabajos,etl.context_for(inventario))''')
    m('''## 6 · Conserva una decisión propia y lleva el producto

Selección estructurada, no una respuesta redactada. 0 deja pendiente. Perfiles: 1=vista320, 2=catalogo640, 3=detalle1024; elige solo los que ejecutaste. Posición: una fila de tu catálogo.

Límites: 1=faltan juicios de calidad visual; 2=falta otra distribución de tamaños; 3=falta medir I/O/concurrencia; 4=contexto de entidad no prueba vínculo con un contrato.

El paquete técnico puede estar verificado aunque tu selección formativa siga pendiente. El código no acredita una entrega académica por marcar opciones.''')
    c('''#@title Elegir desde el resultado propio (0 = pendiente)
POSICION=0 #@param {type:"integer"}
PERFIL_ELEGIDO=0 #@param [0,1,2,3] {type:"raw"}
ALTERNATIVA_DESCARTADA=0 #@param [0,1,2,3] {type:"raw"}
LIMITE=0 #@param [0,1,2,3,4] {type:"raw"}
print(etl.record_decision(TRABAJO,POSICION,PERFIL_ELEGIDO,ALTERNATIVA_DESCARTADA,LIMITE))''')
    c('''# Paquete portable; origen y relaciones acompañan los archivos
reporte=etl.export_package(TRABAJO,inventario,trabajos,etl.context_for(inventario))
PAQUETE=BASE/'paquete_s10.zip'
etl.pack(TRABAJO,PAQUETE)
import tempfile
with tempfile.TemporaryDirectory() as carpeta:
    restaurado=etl.unpack_and_verify(PAQUETE,Path(carpeta)/'restaurado')
print('PORTABILIDAD:',restaurado)
print('PAQUETE:',PAQUETE)
DESCARGAR=False #@param {type:"boolean"}
if DESCARGAR:
    try:
        from google.colab import files
        files.download(str(PAQUETE))
    except ImportError:print('En VS Code el ZIP está en la ruta anterior.')''',True)
    m(reading('La verificación lee el ZIP en otra carpeta; una selección pendiente no se transforma en una nota.',
        'El producto puede abrirse fuera de la ruta original.',
        'No certifica una procedencia independiente si entrada y manifest se alteran juntos.',
        'Confundir progreso local, verificación técnica y evaluación oficial.'))
    m('''## Hoja de consulta y puente

| Necesidad | Operación |
|---|---|
| Abrir un original | `Image.open()` y `load()` |
| Saber qué llegó | formato, dimensiones, modo, bytes, SHA-256 |
| Adaptar sin borrar | orientación → RGB → thumbnail → guardar aparte |
| Continuar pendientes | mismo snapshot/perfil y checkpoint verificado |
| Cargar | JSONL/Parquet + manifest; releer |
| Llevar | ZIP con rutas relativas y verificación en otra carpeta |

**PARA LLEVAR.** E consigue y conserva la entrada; T la adapta; L deja un resultado consultable. S11 añade audio/video reales al mismo contrato; S12 integra ETL. Dask/Spark aparecen después.

**Ampliación de escala:** el proyecto ofrece `main.py escenario --activos 1000000`, basado en las medidas de tu lote. Es un escenario condicionado, no una ejecución de millones. Memoria de decodificación ≈ ancho × alto × canales × tareas activas, antes de buffers.

Si te atascas, vuelve al [checklist](https://jazaineam1.github.io/BigData2026/assets/tutoriales/s10-laboratorio-guiado.html). Un archivo ausente se recupera de la entrada real; no se genera un sustituto sintético.
''')
    return cells


def build_notebook():
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},
            'language_info':{'name':'python','version':'3.12'}},'cells':build_cells()}


def build_project_archive():
    target=ROOT/'assets/tutoriales/s10_proyecto_VSCode.zip'
    files={name:ROOT/'laboratorios/s10_etl_imagenes'/name for name in ['main.py','paso_a_paso.py','requirements.txt','README.md']}
    files['runtime/s10_pipeline.py']=ROOT/'utils/s10_pipeline.py'
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as z:
        for name,path in sorted(files.items()):
            info=zipfile.ZipInfo(name,date_time=(2026,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,path.read_bytes())
    return target


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default=OUTPUT);args=parser.parse_args()
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(build_notebook(),ensure_ascii=False,indent=1)+'\n',encoding='utf-8');print(path)
    build_project_archive()
