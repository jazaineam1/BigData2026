"""S10: dos recursos. Notebook autosuficiente, E/T/L visible y tutorial integrado."""
from pathlib import Path
import argparse,ast,json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from utils.make_notebook import md,code
OUTPUT='Cuadernos/10_ETL_Multimedia.ipynb'
COLAB='https://colab.research.google.com/github/jazaineam1/BigData2026/blob/main/'+OUTPUT
STEPS=[
 ('preparar','Preparar y conectar entradas','Entorno, snapshot real y contexto disponibles.'),
 ('extraer','Extraer y conservar RAW','Original decodificable, fuente y SHA-256.'),
 ('transformar','Transformar una imagen','Derivado real, parámetros y RAW conservado.'),
 ('lotes','Repetir por lotes y continuar','Estados, trabajo nuevo y reutilizado separados.'),
 ('cargar','Cargar, releer y consultar','JSONL/Parquet coherentes y galería desde el catálogo.'),
 ('cerrar','Decidir y transportar','Selección propia, límite y paquete restaurado.')]

def core_source(names):
    source=(ROOT/'utils/s10_pipeline.py').read_text(encoding='utf-8')
    tree=ast.parse(source)
    result = '\n\n'.join(ast.get_source_segment(source,n) for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names)
    return result.replace(chr(34)*3, chr(39)*3)

def reading(how,what,missing,error):
    return '\n\n'.join('**'+k+':** '+v for k,v in zip(['Cómo se lee','Qué nos dice','Qué NO permite concluir todavía','Qué error común'],[how,what,missing,error]))

def build_cells():
    cells=[]
    def m(id,s):
        c=md(s);c['id']=id;c['metadata']['id']=id;cells.append(c)
    def c(id,s,fold=False):
        cell=code(s);cell['id']=id;cell['metadata']['id']=id
        if fold:cell['metadata']['cellView']='form'
        cells.append(cell)
    m('s10-inicio','''# Universidad Central · Maestría en Analítica de Datos
# Big Data · S10 · De una noticia a un catálogo de imágenes reutilizable

**¿Cómo prepara Laura imágenes reales sin perder su origen y consigue volver a consultarlas?**

Dos recursos: [presentación y tutorial integrado](https://jazaineam1.github.io/BigData2026/Presentaciones/s10-etl-multimedia.html#s1) y **este cuaderno Python**. Todo el código ejecutable de la ETL está aquí. Puedes abrir el mismo `.ipynb` en **Colab** o en **VS Code con Python/Jupyter**; en VS Code selecciona el intérprete del kernel antes de ejecutar.

**Producto formativo:** originales conservados, dos perfiles, catálogo JSONL/Parquet, consulta propia y paquete portable. No se añade una nota. El docente entrega `S10_entradas_reales.zip`: es un paquete de **datos reales**, sin módulos Python. No necesitas un ZIP de códigos ni una guía externa.

| Etapa | Pregunta | Producto |
|---|---|---|
| Preparar | ¿Qué fuente y contexto tenemos? | Snapshot y relación entidad–noticia |
| E | ¿Qué bytes llegaron? | RAW, metadata y hash |
| T | ¿Cómo los adapto al uso? | Derivado con parámetros |
| Lotes | ¿Qué terminé y qué puedo reutilizar? | Estados y métricas |
| L | ¿Qué puede leer otro proceso? | Catálogo escrito, reabierto y consultado |
| Cierre | ¿Qué decidí y qué no puedo concluir? | Evidencia y producto para S11 |''')
    m('s10-preparar','''## Paso 1 · Preparar y conectar las entradas

S09 dejó documentos y una selección de búsqueda; S10 prepara las imágenes de noticias que aportan contexto por entidad. **No se deduce que una foto retrate un contrato.** La conexión tiene claves: entidad → noticia de ejemplo → referencia de imagen. S11 ampliará este contrato a otros medios.

El productor docente adquirió el snapshot una vez con pausas e identificación. Cada estudiante utiliza esa entrada, sin repetir descargas masivas del periódico. Las URLs describen procedencia; el ZIP contiene los bytes que vamos a inspeccionar.

**HAZ ESTO AHORA.** Recibe el ZIP de datos, ejecuta dependencias y localiza la entrada. En Colab se ofrece una subida si el archivo no está presente; en VS Code guarda el ZIP junto al notebook o define su ruta. No se pide una tarjeta ni una clave para S10.''')
    c('s10-dependencias','''#@title Preparar bibliotecas (selecciona el kernel Python en VS Code)
%pip -q install pillow==13.0.0 pandas==3.1.0 pyarrow==26.0.0''',True)
    c('s10-utilidades','''#@title Utilidades de archivos e integridad — código incluido; expande para inspeccionarlo
from pathlib import Path, PureWindowsPath
from datetime import datetime, timezone
import hashlib, json, math, shutil, tempfile, zipfile, time
import pandas as pd
import PIL
from PIL import Image, ImageOps
from IPython.display import display
VERSION="s10-batches-v1"
PROFILES={"vista320":{"max_side":320,"quality":88},
          "catalogo640":{"max_side":640,"quality":88}}
ANCHOR={"process_id":"CO1.REQ.2622868","entity":"FUERZA AEROESPACIAL COLOMBIANA",
        "nit":"899999102","relation":"contexto_por_entidad_no_evidencia_del_contrato"}
'''+core_source({'digest','sha256_file','atomic_json','safe_path','inspect_image','build_inventory','context_for','safe_extract','normal_records','validate_record','export_package','verify_package','pack','unpack_and_verify','record_decision'}),True)
    c('s10-entrada','''# Entrada: solo datos. No importamos código del ZIP ni del repositorio.
INPUT_ZIP=Path(globals().get('S10_INPUT_ZIP','S10_entradas_reales.zip')).resolve()
BASE=Path(globals().get('S10_BASE','work_s10')).resolve()
TRABAJO=BASE/'ejecucion'
ENTRADA=BASE/'entrada'
if not INPUT_ZIP.exists():
    try:
        from google.colab import files
        subidos=files.upload()
        if len(subidos)!=1:raise ValueError('Selecciona solo el ZIP de datos docente')
        INPUT_ZIP=Path(next(iter(subidos))).resolve()
    except ImportError:
        raise FileNotFoundError('Localiza S10_entradas_reales.zip o define S10_INPUT_ZIP')
with zipfile.ZipFile(INPUT_ZIP) as z:
    if any(n.endswith(('.py','.ipynb')) for n in z.namelist()):
        raise ValueError('Usa la entrada actualizada: este ZIP debe contener solo datos')
safe_extract(INPUT_ZIP,ENTRADA)
noticias=json.loads((ENTRADA/'sources/noticias_contratacion_2026.json').read_text(encoding='utf-8'))
menciones=json.loads((ENTRADA/'sources/entidades_en_noticias_2026.json').read_text(encoding='utf-8'))
inventario=build_inventory(noticias,menciones)
print('ENTRADA REAL:',INPUT_ZIP.name)
print('CATÁLOGO OBSERVADO:',inventario['counts'])''')
    m('s10-lectura-entrada',reading('El catálogo cuenta noticias y referencias; el ZIP contiene un lote adquirido.',
        'El snapshot tiene 987 noticias, 5.152 apariciones y 4.071 URLs distintas; no son 5.152 imágenes descargadas.',
        'No conocemos la disponibilidad ni los bytes de las URLs no adquiridas.',
        'Tratar una URL como un archivo ya procesado.'))
    c('s10-contexto','''# Conexión de contexto en Python: entidad → noticia → referencia de imagen.
referencias=pd.DataFrame(inventario['occurrences'])
vinculos=pd.DataFrame(inventario['relations'])
ENTIDAD=ANCHOR['entity']
# Herramienta opcional: ruta al expediente propio exportado en S09.
S09_EXPEDIENTE="" #@param {type:"string"}
POSICION_S09=1 #@param {type:"integer"}
if S09_EXPEDIENTE:
    anterior=json.loads(Path(S09_EXPEDIENTE).read_text(encoding='utf-8'))
    filas_s09=anterior.get('resultados_ann_atlas') or anterior.get('resultados_numpy_local') or []
    if not 1<=POSICION_S09<=len(filas_s09):raise ValueError('Posición del resultado propio S09')
    ENTIDAD=filas_s09[POSICION_S09-1]['entidad']
    print('MOTOR DECLARADO S09:',anterior.get('motor_ann_ejecutado','No consta'))
contexto=referencias.merge(vinculos[vinculos.entity.eq(ENTIDAD)],on='article_id',how='inner')
print('CONTEXTO:',ENTIDAD,'· referencias enlazadas:',len(contexto))
display(contexto[['article_id','article_url','image_url','relation']].head(3))
print('ALCANCE: ejemplos de menciones; no demuestra vínculo fotografía–contrato')''')
    m('s10-lectura-contexto',reading('Cada fila enlaza una aparición de imagen con una noticia que menciona la entidad.',
        'La unión es auditable por article_id; una entidad sin coincidencias produce cero filas.',
        'Falta una evidencia específica para vincular una fotografía con un contrato.',
        'Forzar una coincidencia o atribuir a Atlas un resultado de respaldo local.'))
    m('s10-extraer','''## Paso 2 · E: extraer bytes y conservar el original

Elegimos una selección del lote real y copiamos sus bytes a una ruta RAW. Guardamos fuente, crédito, fecha de adquisición y huella. **RAW no se sobrescribe para hacer un thumbnail.**

Ejemplo manual: dos noticias pueden referenciar la misma URL. Conservamos las apariciones editoriales; la identidad del contenido se comprueba con los bytes.

Funciones usadas: `json.loads()` convierte texto JSON en objetos; `shutil.copyfile(origen,destino)` conserva bytes en otra ruta; `Image.open()`/`load()` decodifican y `sha256_file()` devuelve una huella. Un sufijo `.jpg` no determina el formato real.''')
    c('s10-raw','''# E visible: seleccionar → comprobar origen → leer bytes → conservar RAW.
INICIO=0 #@param {type:"integer"}
CANTIDAD=32 #@param {type:"integer"}
if type(INICIO) is not int or type(CANTIDAD) is not int or INICIO<0 or not 2<=CANTIDAD<=32:
    raise ValueError('Inicio entero y cantidad de 2 a 32')
adquiridas=json.loads((ENTRADA/'inputs/inputs.json').read_text(encoding='utf-8'))
seleccion=adquiridas[INICIO:INICIO+CANTIDAD]
if len(seleccion)<2:raise ValueError('Elige al menos dos imágenes disponibles')
por_aparicion={r['occurrence_id']:r for r in inventario['occurrences']}
trabajos=[]
for registro in seleccion:
    referencia=por_aparicion[registro['occurrence_id']]
    if registro['source_url']!=referencia['image_url'] or registro['snapshot']!=inventario['snapshot']:
        raise ValueError('Procedencia incompatible con el snapshot')
    origen=safe_path(ENTRADA/'inputs',registro['input_path'])
    info=inspect_image(origen)
    if info['sha256']!=registro['input_sha256']:raise ValueError('Entrada alterada')
    relativa=f"raw/{info['sha256']}/original.{info['format'].lower()}"
    destino=safe_path(TRABAJO,relativa);destino.parent.mkdir(parents=True,exist_ok=True)
    if destino.exists() and sha256_file(destino)!=info['sha256']:raise ValueError('RAW previo alterado')
    if not destino.exists():shutil.copyfile(origen,destino)
    trabajos.append(registro|{'raw_path':relativa,'path':str(destino)})
previo=TRABAJO/'config/jobs.json'
if previo.exists() and [j['job_id'] for j in json.loads(previo.read_text(encoding='utf-8'))]!=[j['job_id'] for j in trabajos]:
    raise ValueError('Usa otra carpeta para otra selección')
atomic_json(previo,[{k:v for k,v in j.items() if k!='path'} for j in trabajos])
atomic_json(TRABAJO/'config/inventory.json',inventario)
atomic_json(TRABAJO/'config/context.json',context_for(inventario,ENTIDAD))
print('E · RAW REALES:',len(trabajos))
display(pd.DataFrame(trabajos)[['article_id','source_url','credit','raw_path']].head(3))''')
    m('s10-lectura-raw',reading('Cada trabajo apunta a un original identificado y a su noticia.',
        'Los bytes existen y el hash coincide con la entrada adquirida.',
        'La integridad no autentica por sí sola al autor editorial ni el contenido del contrato.',
        'Sobrescribir RAW o inventar una imagen cuando falta el original.'))
    m('s10-transformar','''## Paso 3 · T: adaptar una imagen a un propósito

Queremos una vista de catálogo. Para una entrada de 1200×675 y lado máximo 640, la proporción es 640/1200 y la salida esperada 640×360. Cambiar el sufijo no convierte el archivo.

`ImageOps.exif_transpose()` respeta orientación; `convert('RGB')` prepara canales; `thumbnail((lado,lado))` conserva proporción y no amplía; `save(...,'JPEG',quality=88)` escribe el derivado. Elige el lado para el uso: más pequeño no significa mejor calidad.

Primero lee y ejecuta el ejemplo resuelto. Después cambia únicamente `LADO_MAXIMO`, manteniendo la misma entrada, formato y calidad.''')
    c('s10-funcion-t',core_source({'make_thumbnail'}))
    c('s10-una-imagen','''# T visible: la función anterior contiene la operación Pillow completa.
primero=trabajos[0];raw=TRABAJO/primero['raw_path']
LADO_MAXIMO=640 #@param [320,640] {type:"raw"}
perfil_ejemplo={'max_side':LADO_MAXIMO,'quality':88}
antes=sha256_file(raw)
ejemplo=TRABAJO/'ejemplo'/f'vista_{LADO_MAXIMO}.jpg'
make_thumbnail(raw,ejemplo,'catalogo640' if LADO_MAXIMO==640 else 'vista320')
print('ORIGINAL:',inspect_image(raw))
print('DERIVADO:',inspect_image(ejemplo))
print('RAW CONSERVADO:',sha256_file(raw)==antes)
with Image.open(raw) as im:
    vista=ImageOps.exif_transpose(im).convert('RGB');vista.thumbnail((640,360));display(vista);vista.close()
with Image.open(ejemplo) as im:display(im)''')
    m('s10-lectura-t',reading('Observa imágenes, dimensiones y bytes del mismo original y su derivado.',
        'Muestra el efecto de este parámetro; RAW conserva su huella.',
        'Faltan criterios y juicios para afirmar calidad visual general.',
        'Prometer ahorro: convertir WEBP a JPEG puede aumentar bytes.'))
    m('s10-lotes','''## Paso 4 · Repetir la operación y continuar

La transformación no cambia al pasar al lote. Cada trabajo recibe un resultado o un fallo explícito. Antes de reutilizar un resultado, comprobamos archivo, hash y parámetros. Si algo falta, se vuelve a procesar; no basta leer `DONE`.

El bucle es secuencial para poder seguirlo. `max_nuevos` permite observar una pausa y continuar sin provocar fallos. Los acumulados DONE/FAILED/PENDING y el trabajo nuevo/reutilizado responden preguntas diferentes.''')
    c('s10-un-trabajo',core_source({'process_one'}))
    c('s10-bucle','''# Control del lote visible: verificar previos → procesar pendientes → guardar estado.
def procesar_lote(perfil,max_nuevos=None):
    ruta=TRABAJO/'state/checkpoint.json'
    firma=digest(json.dumps([[j['job_id'],j['input_sha256']] for j in trabajos]).encode())
    estado=json.loads(ruta.read_text(encoding='utf-8')) if ruta.exists() else {'version':VERSION,'signature':firma,'profiles':{}}
    if estado['signature']!=firma:raise ValueError('Otra selección requiere otra carpeta')
    registros=estado['profiles'].setdefault(perfil,{})
    nuevos=reutilizados=fallos=0;inicio=time.perf_counter()
    for trabajo in trabajos:
        key=trabajo['job_id'];prev=registros.get(key,{})
        if prev.get('status')=='DONE' and not validate_record(TRABAJO,prev['result']):
            reutilizados+=1;continue
        if max_nuevos is not None and nuevos+fallos>=max_nuevos:
            registros[key]={'status':'PENDING'};continue
        try:
            fila=process_one(trabajo,TRABAJO,perfil)
            registros[key]={'status':'DONE','result':fila};nuevos+=1
        except Exception as error:
            registros[key]={'status':'FAILED','error':type(error).__name__+': '+str(error)};fallos+=1
        atomic_json(ruta,estado)
    atomic_json(ruta,estado)
    conteos={s:sum(v['status']==s for v in registros.values()) for s in ['DONE','FAILED','PENDING']}
    assert sum(conteos.values())==len(trabajos)
    metrica={'profile':perfil,'planned':len(trabajos),'states':conteos,'processed_now':nuevos,
             'skipped_verified':reutilizados,'failed_now':fallos,'seconds':time.perf_counter()-inicio,'workers':1}
    salida=TRABAJO/'metrics'/f'{perfil}.json'
    historial=json.loads(salida.read_text(encoding='utf-8')) if salida.exists() else []
    atomic_json(salida,historial+[metrica])
    print(json.dumps(metrica,ensure_ascii=False,indent=2))
    return [v['result'] for v in registros.values() if v['status']=='DONE'],metrica''')
    c('s10-aplicar-lote','''# Aplicar, continuar y comparar sobre las mismas imágenes reales.
_,pausa=procesar_lote('catalogo640',max_nuevos=min(16,len(trabajos)))
resultados,continuacion=procesar_lote('catalogo640')
alternativa,comparacion=procesar_lote('vista320')
assert all(m['states']['FAILED']==0 and m['states']['PENDING']==0 for m in [continuacion,comparacion])
tabla=pd.DataFrame(resultados+alternativa)
print('TRABAJOS COMPLETOS:',len(tabla),'= imágenes',len(trabajos),'× perfiles',tabla.profile.nunique())
display(tabla[['article_id','profile','derived_width','derived_height','raw_bytes','derived_bytes']].head())''')
    m('s10-lectura-lote',reading('Las métricas distinguen nuevos, reutilizados y estados acumulados.',
        'Dos perfiles completos dejan N×2 trabajos; continuar omite solo lo revalidado.',
        'Faltan otras cargas, hardware e I/O para generalizar rendimiento.',
        'Sumar trabajo antiguo al throughput actual o confundir dos perfiles con el doble de originales.'))
    m('s10-cargar','''## Paso 5 · L: escribir, releer y consultar

Los binarios quedan como archivos; una fila permite encontrar original, derivado y noticia. `DataFrame` organiza los registros. `to_json(orient='records',lines=True)` guarda JSONL; `to_parquet(index=False)` guarda una tabla tipada; `read_parquet()` vuelve a leerla.

**HAZ ESTO AHORA.** Ejecuta la escritura y la lectura. Después filtra una noticia y observa su imagen desde la ruta que devolvió el catálogo. La carga debe producir algo que otro proceso pueda consultar.''')
    c('s10-escribir','''# L visible: construir catálogo → escribir → releer ambos formatos.
OUT=TRABAJO/'outputs';OUT.mkdir(exist_ok=True)
catalogo=pd.DataFrame(resultados+alternativa)
catalogo.to_json(OUT/'assets.jsonl',orient='records',lines=True,force_ascii=False)
catalogo.to_parquet(OUT/'assets.parquet',index=False)
recargado=pd.read_parquet(OUT/'assets.parquet')
jsonl=pd.read_json(OUT/'assets.jsonl',orient='records',lines=True,convert_dates=False,dtype={'article_id':str})
assert len(recargado)==len(trabajos)*len(PROFILES)>0
assert normal_records(jsonl)==normal_records(recargado)
print('L · FILAS REABIERTAS:',len(recargado))
display(recargado[['article_id','profile','derived_path','derived_width','derived_height']].head())''')
    c('s10-consultar','''# Consulta real: noticia/perfil y costo observado. La galería parte de sus filas.
ARTICULO=str(recargado.iloc[0]['article_id'])
consulta=recargado[recargado.article_id.astype(str).eq(ARTICULO)]
display(consulta[['article_id','profile','derived_width','derived_height','derived_bytes']])
display(recargado.groupby('profile')[['raw_bytes','derived_bytes']].sum())
for _,fila in consulta.head(4).iterrows():
    print('NOTICIA:',fila.article_id,'· PERFIL:',fila.profile,'· bytes:',fila.derived_bytes)
    with Image.open(safe_path(TRABAJO,fila.derived_path)) as imagen:display(imagen)
print('RAW ÚNICOS:',recargado.raw_sha256.nunique(),'· no sumar originales repetidos entre perfiles')''')
    m('s10-lectura-carga',reading('Cada fila es un trabajo/perfil y su ruta vuelve a un binario real.',
        'La tabla se puede consultar y las imágenes se recuperan desde sus filas.',
        'La comparación visual no demuestra calidad general ni relación de la foto con un contrato.',
        'Dar por cargado un archivo por su nombre, sin releerlo; duplicar RAW al sumar perfiles.'))
    m('s10-cerrar','''## Paso 6 · Decidir, conservar y continuar en S11

Elige una posición de tu tabla, un perfil usado y una alternativa descartada. **0 deja pendiente.** Límite: 1=faltan juicios de calidad visual; 2=falta otra distribución de tamaños; 3=falta medir I/O/concurrencia; 4=contexto de entidad no prueba vínculo con contrato. Perfiles: 1=vista320, 2=catalogo640.

La selección es formativa. No se envía prosa ni se acredita una nota por marcar una casilla. El manifiesto describe la ejecución; una comprobación técnica no autentica por sí sola la fuente.''')
    c('s10-decision','''# Opciones cerradas sobre la salida propia; no se admite texto libre.
POSICION=0 #@param {type:"integer"}
PERFIL_ELEGIDO=0 #@param [0,1,2] {type:"raw"}
ALTERNATIVA_DESCARTADA=0 #@param [0,1,2] {type:"raw"}
LIMITE=0 #@param [0,1,2,3,4] {type:"raw"}
print(record_decision(TRABAJO,POSICION,PERFIL_ELEGIDO,ALTERNATIVA_DESCARTADA,LIMITE))''')
    c('s10-producto','''# Continuar sin duplicar; verificar y transportar la misma salida.
_,repeticion=procesar_lote('catalogo640')
print('REPETICIÓN · nuevos:',repeticion['processed_now'],'· reutilizados:',repeticion['skipped_verified'])
reporte=export_package(TRABAJO,inventario,trabajos,context_for(inventario,ENTIDAD))
if not reporte['ok']:raise ValueError(reporte['errors'])
PAQUETE=BASE/'paquete_s10.zip'
pack(TRABAJO,PAQUETE)
with tempfile.TemporaryDirectory() as carpeta:
    restaurado=unpack_and_verify(PAQUETE,Path(carpeta)/'restaurado')
print('PORTABILIDAD:',restaurado)
print('PRODUCTO:',PAQUETE)
DESCARGAR=False #@param {type:"boolean"}
if DESCARGAR:
    try:
        from google.colab import files
        files.download(str(PAQUETE))
    except ImportError:print('En VS Code conserva el archivo de la ruta anterior.')''')
    m('s10-lectura-cierre',reading('La verificación relee archivos en otra carpeta y la repetición revalida resultados.',
        'El producto puede continuar fuera de su ruta original y alimenta la siguiente ETL.',
        'No acredita calidad visual general, autenticidad editorial ni aprendizaje por sí solo.',
        'Confundir progreso de lectura con una ejecución o entregar solo el ZIP de códigos.'))
    m('s10-hoja','''## Para llevar · hoja de consulta

| Necesidad | Operación que acabas de ejecutar |
|---|---|
| Abrir la fuente | `Path.read_text(encoding='utf-8')` + `json.loads()` |
| Relacionar noticia/entidad | `DataFrame.merge(...,on='article_id')` |
| Conservar el original | `shutil.copyfile()` + SHA-256 |
| Transformar | `ImageOps.exif_transpose()` → RGB → `thumbnail()` → `save()` |
| Repetir | `procesar_lote()` y condición de resultado revalidado |
| Cargar y consultar | JSONL/Parquet → relectura → filtro/agrupación |
| Trasladar | Manifiesto, binarios y comprobación en otra carpeta |

S11 toma IDs, origen, RAW/derived, parámetros y catálogo para añadir audio/video reales. S12 integra ETL. El lote medido no es una prueba de escala a millones: una proyección exige declarar distribución de tamaños, hardware e I/O.

Si falta una imagen, recupera la entrada real; no se inventa un sustituto. Si eliges otra selección, usa otra carpeta. Si reinicias el kernel, ejecuta desde Preparar: todo el código está en este cuaderno.''')
    return cells

def build_notebook():
    return {'nbformat':4,'nbformat_minor':5,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'cells':build_cells()}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default=OUTPUT);a=p.parse_args()
    dest=Path(a.output);dest.write_text(json.dumps(build_notebook(),ensure_ascii=False,indent=1)+'\n',encoding='utf-8');print(dest)
