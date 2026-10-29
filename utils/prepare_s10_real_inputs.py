"""Adquisición docente, una vez: imágenes reales. No redistribuye ni publica binarios."""
import argparse,json,shutil,sys,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from utils import s10_pipeline as etl


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destino',type=Path,default=ROOT/'.local-docente/S10_entradas_reales')
    parser.add_argument('--cantidad',type=int,default=32)
    parser.add_argument('--variante',type=int,default=0)
    parser.add_argument('--solo-empaquetar',action='store_true')
    args=parser.parse_args();target=args.destino
    (target/'sources').mkdir(parents=True,exist_ok=True)
    for name in ['noticias_contratacion_2026.json','entidades_en_noticias_2026.json']:
        shutil.copyfile(ROOT/'Datos'/name,target/'sources'/name)
    inventory=etl.build_inventory(json.loads((target/'sources/noticias_contratacion_2026.json').read_text(encoding='utf-8')),
                                  json.loads((target/'sources/entidades_en_noticias_2026.json').read_text(encoding='utf-8')))
    jobs=(etl.load_inputs(target/'inputs',inventory) if args.solo_empaquetar else
          etl.acquire_inputs(inventory,target/'inputs',args.variante,args.cantidad))
    (target/'runtime').mkdir(exist_ok=True)
    shutil.copyfile(ROOT/'utils/s10_pipeline.py',target/'runtime/s10_pipeline.py')
    for name in ['main.py','paso_a_paso.py','requirements.txt','README.md']:
        src=ROOT/'laboratorios/s10_etl_imagenes'/name
        if src.exists():shutil.copyfile(src,target/name)
    archive=target.with_suffix('.zip')
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(target.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(target).as_posix())
    print(json.dumps({'imagenes_reales':len(jobs),'catalogo':inventory['counts'],
                      'zip_privado':str(archive),'bytes':archive.stat().st_size},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
