"""Proyecto S10: E, T y L explícitas para imágenes reales. Python 3.12 recomendado."""
from pathlib import Path
import argparse
import json
import sys

HERE=Path(__file__).resolve().parent
for candidate in [HERE/'runtime',HERE.parents[1]/'utils']:
    if (candidate/'s10_pipeline.py').exists():sys.path.insert(0,str(candidate));break
import s10_pipeline as etl


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='stage',required=True)
    for name in ['extraer','transformar','cargar','verificar','decidir','escenario']:
        cmd=sub.add_parser(name)
        cmd.add_argument('--trabajo',type=Path,default=Path('work/s10'))
        if name=='extraer':
            cmd.add_argument('--entrada',type=Path,required=True)
            cmd.add_argument('--inicio',type=int,default=0);cmd.add_argument('--cantidad',type=int,default=32)
        if name=='transformar':
            cmd.add_argument('--perfil',choices=etl.PROFILES,default='catalogo640')
            cmd.add_argument('--workers',type=int,choices=[1,2,4],default=1)
            cmd.add_argument('--lote',type=int,default=16);cmd.add_argument('--hasta',type=int)
        if name=='cargar':cmd.add_argument('--zip',type=Path,default=Path('paquete_s10.zip'))
        if name=='verificar':cmd.add_argument('--zip',type=Path);cmd.add_argument('--destino',type=Path)
        if name=='decidir':
            cmd.add_argument('--posicion',type=int,default=0)
            cmd.add_argument('--elegido',type=int,choices=[0,1,2,3],default=0)
            cmd.add_argument('--descartado',type=int,choices=[0,1,2,3],default=0)
            cmd.add_argument('--limite',type=int,choices=[0,1,2,3,4],default=0)
        if name=='escenario':cmd.add_argument('--activos',type=int,default=1000000)
    args=parser.parse_args(argv);root=args.trabajo
    if args.stage=='extraer':
        inv,jobs=etl.initialize(args.entrada,root,args.inicio,args.cantidad)
        result={'etapa':'E · extracción','catalogo_observado':inv['counts'],'imagenes_reales_del_lote':len(jobs),
                'contexto':etl.context_for(inv),'RAW':'conservado con SHA-256','origen':'eltiempo_real'}
    elif args.stage=='transformar':
        inv,jobs=etl.open_workspace(root)
        rows,metrics=etl.run_batch(jobs,root,args.perfil,args.workers,args.hasta,args.lote)
        result={'etapa':'T · transformación','metricas':metrics,'filas_disponibles':len(rows)}
    elif args.stage=='cargar':
        inv,jobs=etl.open_workspace(root)
        report=etl.export_package(root,inv,jobs,etl.context_for(inv))
        if not report['ok']:raise ValueError(report)
        etl.pack(root,args.zip)
        result={'etapa':'L · carga','relectura':report,'paquete':str(args.zip.resolve())}
    elif args.stage=='verificar':
        if args.zip:
            if not args.destino:parser.error('--zip requiere --destino vacío')
            result=etl.unpack_and_verify(args.zip,args.destino)
        else:result=etl.verify_package(root)
        if not result['ok']:print(json.dumps(result,ensure_ascii=False,indent=2));return 1
    elif args.stage=='decidir':
        result=etl.record_decision(root,args.posicion,args.elegido,args.descartado,args.limite)
    else:
        inv,jobs=etl.open_workspace(root)
        cp=json.loads((root/'state/checkpoint.json').read_text(encoding='utf-8'))
        first=next(iter(cp['profiles']));rows=[r['result'] for r in cp['profiles'][first].values() if r['status']=='DONE']
        metrics=json.loads((root/'metrics'/(first+'.json')).read_text(encoding='utf-8'))
        measured=[m for m in metrics if m['processed_now'] and m['workers']==1]
        if not rows or not measured:raise ValueError('Primero mide un micro-lote con un trabajador para el escenario secuencial')
        seconds=sum(m['seconds'] for m in measured)/sum(m['processed_now'] for m in measured)
        result=etl.scenario(args.activos,sum(r['raw_bytes'] for r in rows)/len(rows),
                            sum(r['derived_bytes'] for r in rows)/len(rows),seconds)
        result['supuesto']='Rendimiento del lote local; no garantiza rendimiento futuro'
    print(json.dumps(result,ensure_ascii=False,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
