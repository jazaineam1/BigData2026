"""Lee la implementación de una imagen antes de ejecutar el lote completo."""
import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from PIL import Image, ImageOps

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--trabajo',type=Path,default=Path('work/s10'))
parser.add_argument('--posicion',type=int,default=1)
parser.add_argument('--lado',type=int,choices=[320,640,1024],default=640)
args=parser.parse_args()
root=args.trabajo.resolve()
if not (root/'config/jobs.json').exists():parser.error('Primero ejecuta main.py extraer')
jobs=json.loads((root/'config/jobs.json').read_text())
if not 1<=args.posicion<=len(jobs):parser.error('Elige una posición del lote extraído')
job=jobs[args.posicion-1]
raw=(root/job['raw_path']).resolve()
if not raw.is_relative_to(root):parser.error('Ruta fuera del trabajo')

# E · El original ya se extrajo del snapshot real. Leemos sus bytes y su contexto.
antes=hashlib.sha256(raw.read_bytes()).hexdigest()
with Image.open(raw) as original:
    original.load()
    formato=original.format
    ancho,alto=original.size
    # T · Esta es la transformación que luego se aplica a cada trabajo del lote.
    imagen=ImageOps.exif_transpose(original).convert('RGB')
    imagen.thumbnail((args.lado,args.lado))
    salida=root/'ejemplo'/f"fila_{args.posicion}_{args.lado}.jpg"
    salida.parent.mkdir(exist_ok=True)
    imagen.save(salida,'JPEG',quality=88)
    nuevo_ancho,nuevo_alto=imagen.size
    imagen.close()

# L · Metadata estructurada; los binarios permanecen como archivos separados.
fila={'article_id':job['article_id'],'source_url':job['source_url'],
      'raw_sha256':antes,'raw_format':formato,'raw_width':ancho,'raw_height':alto,
      'derived_width':nuevo_ancho,'derived_height':nuevo_alto,
      'raw_bytes':raw.stat().st_size,'derived_bytes':salida.stat().st_size,
      'derived_path':salida.relative_to(root).as_posix(),'max_side':args.lado}
catalogo=pd.DataFrame([fila])
catalogo.to_json(root/'ejemplo/assets.jsonl',orient='records',lines=True,force_ascii=False)
catalogo.to_parquet(root/'ejemplo/assets.parquet',index=False)
recargado=pd.read_parquet(root/'ejemplo/assets.parquet')
assert len(recargado)==1 and antes==hashlib.sha256(raw.read_bytes()).hexdigest()
with Image.open(salida) as verificada:
    verificada.load()
    assert max(verificada.size)<=args.lado
print(recargado.to_string(index=False))
print('Cómo se lee: una fila enlaza noticia, original y derivado.')
print('Qué nos dice: dimensiones y bytes reales de la transformación elegida.')
print('Qué NO permite concluir todavía: faltan criterios y juicios para medir calidad visual general.')
print('Qué error común: asumir ahorro por convertir WEBP a JPEG; observa los bytes.')
print('RAW conservado: True · Abre original y derivado en VS Code para compararlos.')
