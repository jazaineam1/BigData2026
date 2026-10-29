"""S10: inventario real y ETL de imágenes por micro-lotes. Sin adquisición masiva.

Adquisición docente única de imágenes editoriales enlazadas en el corpus.
No genera imágenes sintéticas ni reemplaza descargas fallidas.
La verificación es técnica, no autenticación de la fuente ni calificación LMS.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import io
import json
import math
from pathlib import Path, PureWindowsPath
import shutil
import tempfile
import threading
import time
import zipfile

import pandas as pd
import PIL
from PIL import Image, ImageOps
import urllib.request
from urllib.parse import urlsplit

VERSION = "s10-batches-v1"
PROFILES = {"vista320": {"max_side": 320, "quality": 82},
            "catalogo640": {"max_side": 640, "quality": 88},
            "detalle1024": {"max_side": 1024, "quality": 90}}
ANCHOR = {"process_id": "CO1.REQ.2622868", "entity": "FUERZA AEROESPACIAL COLOMBIANA",
          "nit": "899999102", "relation": "contexto_por_entidad_no_evidencia_del_contrato"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha256_file(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    tmp.replace(path)


def safe_path(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or PureWindowsPath(relative).drive or "\\" in relative:
        raise ValueError("La ruta debe ser relativa al paquete")
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root):
        raise ValueError("Ruta fuera del paquete")
    return target


def inspect_image(path):
    path = Path(path)
    if not path.is_file() or not 0 < path.stat().st_size <= 32 * 1024**2:
        raise ValueError("Archivo vacío, ausente o mayor de 32 MiB")
    with Image.open(path) as im:
        if im.width * im.height > 24_000_000:
            raise ValueError("Imagen mayor de 24 millones de píxeles")
        im.verify()
    with Image.open(path) as im:
        im.load()
        return {"format": im.format, "width": im.width, "height": im.height,
                "mode": im.mode, "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def build_inventory(news, mentions):
    ids = [str(n["_id"]) for n in news]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs editoriales duplicados")
    occurrences = []
    for n in news:
        for pos, item in enumerate(n.get("imagenes") or []):
            url = item.get("url") if isinstance(item, dict) else None
            if not url:
                continue
            occurrences.append({"occurrence_id": f"{n['_id']}:{pos}",
                "article_id": str(n["_id"]), "image_position": pos, "image_url": url,
                "article_url": n["url"], "published_at": n.get("publicado", ""),
                "credit": item.get("credito") or ""})
    edges = []
    for entity in mentions:
        for example in entity.get("ejemplos", []):
            if str(example["id"]) not in ids:
                raise ValueError("El ejemplo de noticia no existe en el snapshot")
            edges.append({"entity": entity["entidad"], "article_id": str(example["id"]),
                          "relation": "mencion_ejemplo", "scope": "ejemplos_no_total_de_menciones"})
    snapshot = digest(json.dumps(news, sort_keys=True, ensure_ascii=False).encode())
    return {"snapshot": snapshot, "occurrences": occurrences, "relations": edges,
        "counts": {"articles": len(news), "articles_with_images": sum(bool(n.get("imagenes")) for n in news),
                   "image_references": len(occurrences),
                   "unique_urls": len({r["image_url"] for r in occurrences})}}


def context_for(inventory, entity=None):
    entity = entity or ANCHOR["entity"]
    ids = sorted({e["article_id"] for e in inventory["relations"] if e["entity"] == entity})
    return {"entity": entity, "article_ids": ids, "scope": "ejemplos_de_menciones",
            "matched": bool(ids), "limit": "No establece vínculo de la imagen con un contrato particular"}


def acquire_inputs(inventory, directory, variant=0, count=32, pause=0.4):
    """Solo docente: una adquisición acotada, con pausa, caché y trazabilidad."""
    if type(variant) is not int or not 0 <= variant <= 7:
        raise ValueError("Variante entera 0 a 7")
    if type(count) is not int or not 2 <= count <= 128 or pause < 0.4:
        raise ValueError("Lote de 2 a 128; pausa mínima 0,4 segundos")
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    context=context_for(inventory); unique={}
    for item in inventory['occurrences']: unique.setdefault(item['image_url'],item)
    ordered=sorted(unique.values(),key=lambda r:(r['article_id'] not in context['article_ids'],
                   digest((str(variant)+r['image_url']).encode())))
    cache_path=directory/'inputs.json'
    previous=json.loads(cache_path.read_text(encoding='utf-8')) if cache_path.exists() else []
    cached={j['job_id']:j for j in previous}
    rows=[];failures=[];attempts=0
    # Como máximo count+16 candidatos reales. Nunca un sustituto sintético.
    for occ in ordered[:count+16]:
        job=digest((inventory['snapshot']+occ['image_url']+str(variant)+VERSION).encode())[:24]
        old=cached.get(job)
        if old:
            path=safe_path(directory,old['input_path'])
            if inspect_image(path)['sha256']!=old['input_sha256']:
                raise ValueError("Input almacenado alterado; recupera el original")
            rows.append(old)
        else:
            attempts+=1
            try:
                url=occ['image_url']
                if urlsplit(url).scheme!='https':raise ValueError('Origen no HTTPS')
                req=urllib.request.Request(url,headers={'User-Agent':'BigData-UCentral-docente/1.0 (adquisicion docente unica para ETL)'})
                with urllib.request.urlopen(req,timeout=25) as response:
                    payload=response.read(32*1024**2+1)
                    content_type=response.headers.get('Content-Type','')
                    final_url=response.url
                if not 0<len(payload)<=32*1024**2:raise ValueError('Respuesta vacía o mayor de 32 MiB')
                temporary=directory/(job+'.download')
                temporary.write_bytes(payload)
                info=inspect_image(temporary)
                relative='raw/'+job+'.'+info['format'].lower()
                target=safe_path(directory,relative);target.parent.mkdir(exist_ok=True)
                temporary.replace(target)
                rows.append({'job_id':job,'article_id':occ['article_id'],
                    'occurrence_id':occ['occurrence_id'],'context_reference_url':url,
                    'source_url':url,'origin_kind':'eltiempo_real',
                    'acquired_at_utc':datetime.now(timezone.utc).isoformat(),
                    'http_content_type':content_type,'final_url':final_url,
                    'credit':occ['credit'],'input_path':relative,
                    'input_sha256':info['sha256'],'snapshot':inventory['snapshot'],
                    'expected_format':info['format']})
                atomic_json(cache_path,rows)
            except Exception as exc:
                temporary=directory/(job+'.download')
                if temporary.exists():temporary.unlink()
                failures.append({'job_id':job,'url':occ['image_url'],
                                 'error':type(exc).__name__+': '+str(exc)})
            finally:time.sleep(pause)
        if len(rows)>=count:break
    atomic_json(cache_path,rows)
    atomic_json(directory/'acquisition_report.json',{'requested_successes':count,
        'available':len(rows),'new_requests':attempts,'failures':failures,
        'origin_kind':'eltiempo_real','synthetic_substitutes':0})
    if not rows:raise ValueError('No se adquirió ninguna imagen real')
    return load_inputs(directory,inventory)


def load_inputs(directory,inventory):
    directory=Path(directory)
    jobs=json.loads((directory/'inputs.json').read_text(encoding='utf-8'))
    occurrences={r['occurrence_id']:r for r in inventory['occurrences']}
    if not jobs or len({j['job_id'] for j in jobs})!=len(jobs):raise ValueError('Inputs vacíos o duplicados')
    loaded=[]
    for j in jobs:
        occ=occurrences.get(j['occurrence_id'])
        if (not occ or j['snapshot']!=inventory['snapshot'] or j['origin_kind']!='eltiempo_real'
            or j['source_url']!=occ['image_url'] or j['context_reference_url']!=occ['image_url']
            or j['article_id']!=occ['article_id']):raise ValueError('Procedencia incompatible')
        path=safe_path(directory,j['input_path']);info=inspect_image(path)
        if info['sha256']!=j['input_sha256'] or info['format']!=j['expected_format']:
            raise ValueError('Input no coincide con adquisición')
        loaded.append(j|{'path':str(path.resolve())})
    return loaded


def extract_jobs(jobs, root):
    """E: consolidar RAW inmutable antes de transformar."""
    root=Path(root);root.mkdir(parents=True,exist_ok=True)
    extracted=[]
    for job in jobs:
        info=inspect_image(job['path'])
        if info['sha256']!=job['input_sha256']:raise ValueError('Input alterado')
        relative=f"raw/{info['sha256']}/original.{info['format'].lower()}"
        target=safe_path(root,relative);target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists() and sha256_file(target)!=info['sha256']:raise ValueError('RAW previo alterado')
        if not target.exists():shutil.copyfile(job['path'],target)
        extracted.append({k:v for k,v in job.items() if k!='path'}|{'raw_path':relative,'path':str(target.resolve())})
    atomic_json(root/'config/jobs.json',[{k:v for k,v in j.items() if k!='path'} for j in extracted])
    return extracted


def safe_extract(archive,destination):
    destination=Path(destination)
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist())>512*1024**2:raise ValueError('ZIP mayor del límite de práctica')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Nombres duplicados en ZIP')
        for item in z.infolist():
            safe_path(destination,item.filename)
            if (item.external_attr>>16)&0o170000==0o120000:raise ValueError('No se admiten symlinks')
        z.extractall(destination)
    return destination


def initialize(archive,root,start=0,count=32):
    root=Path(root)
    if type(start) is not int or type(count) is not int or start<0 or count<2:raise ValueError('Inicio entero y al menos dos imágenes')
    inputs=root/'entrada'
    # El ZIP es el lote docente; se puede abrir sin red.
    safe_extract(archive,inputs)
    news=json.loads((inputs/'sources/noticias_contratacion_2026.json').read_text(encoding='utf-8'))
    mentions=json.loads((inputs/'sources/entidades_en_noticias_2026.json').read_text(encoding='utf-8'))
    inventory=build_inventory(news,mentions)
    jobs=load_inputs(inputs/'inputs',inventory)[start:start+count]
    if len(jobs)<2:raise ValueError('Selecciona al menos dos imágenes del lote disponible')
    config=root/'config/inventory.json'
    signature=[j['job_id'] for j in jobs]
    if (root/'config/jobs.json').exists():
        previous=json.loads((root/'config/jobs.json').read_text(encoding='utf-8'))
        if [j['job_id'] for j in previous]!=signature:raise ValueError('Usa otra carpeta para otra variante')
    atomic_json(config,inventory)
    atomic_json(root/'config/context.json',context_for(inventory))
    jobs=extract_jobs(jobs,root)
    return inventory,jobs


def open_workspace(root):
    root=Path(root)
    if not (root/'config/jobs.json').exists():raise ValueError('Ejecuta primero la etapa extraer')
    inventory=json.loads((root/'config/inventory.json').read_text(encoding='utf-8'))
    jobs=json.loads((root/'config/jobs.json').read_text(encoding='utf-8'))
    for j in jobs:j['path']=str(safe_path(root,j['raw_path']))
    return inventory,jobs


def make_thumbnail(source, destination, profile):
    """Operación unitaria que el cuaderno enseña antes del ejecutor de lotes."""
    params = PROFILES[profile]
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original).convert("RGB")
        image.thumbnail((params["max_side"], params["max_side"]))
        destination = Path(destination); destination.parent.mkdir(parents=True, exist_ok=True)
        temporary = destination.with_name(destination.name+".tmp")
        image.save(temporary, format="JPEG", quality=params["quality"])
        temporary.replace(destination)
        image.close()


def validate_record(root, row):
    errors = []
    try:
        raw = safe_path(root, row["raw_path"]); derived = safe_path(root, row["derived_path"])
        a, b = inspect_image(raw), inspect_image(derived)
        if a["sha256"] != row["raw_sha256"] or row["asset_id"] != a["sha256"]: errors.append("raw_hash")
        if b["sha256"] != row["derived_sha256"]: errors.append("derived_hash")
        if a["bytes"] != row["raw_bytes"] or b["bytes"] != row["derived_bytes"]: errors.append("bytes")
        if (a["width"],a["height"],a["format"],a["mode"]) != (row["raw_width"],row["raw_height"],row["raw_format"],row["raw_mode"]): errors.append("raw_metadata")
        params = PROFILES[row["profile"]]
        if row["params"] != json.dumps(params, sort_keys=True): errors.append("params")
        with Image.open(raw) as im:
            upright = ImageOps.exif_transpose(im); w,h = upright.size
            upright.thumbnail((params["max_side"],params["max_side"]))
            expected = upright.size
        if (b["width"],b["height"]) != expected or b["format"] != "JPEG": errors.append("profile")
        if (b["width"],b["height"]) != (row["derived_width"],row["derived_height"]): errors.append("derived_metadata")
        if row["parent_asset_id"] != a["sha256"]: errors.append("parent")
        if row['origin_kind']!='eltiempo_real' or row['source_url']!=row['context_reference_url'] or not row['acquired_at_utc']: errors.append('origin')
        if row["input_sha256"] != a["sha256"]: errors.append("input_reference_hash")
    except Exception as exc:
        errors.append("decode_or_schema:" + type(exc).__name__)
    return errors


def process_one(job, root, profile):
    root = Path(root); info = inspect_image(job["path"])
    if not (root/"config/jobs.json").exists():raise ValueError("Ejecuta primero extraer")
    if info["sha256"] != job["input_sha256"]: raise ValueError("input_hash")
    raw_rel = f"raw/{info['sha256']}/original.{info['format'].lower()}"
    raw = safe_path(root, raw_rel); raw.parent.mkdir(parents=True, exist_ok=True)
    if raw.exists() and sha256_file(raw) != info["sha256"]: raise ValueError("RAW previo alterado")
    if not raw.exists(): raise ValueError("Falta RAW: vuelve a extraer la entrada")
    transform = digest((info["sha256"]+json.dumps(PROFILES[profile],sort_keys=True)+VERSION+PIL.__version__).encode())
    derived_rel = f"derived/{info['sha256']}/{transform}.jpg"
    make_thumbnail(raw, safe_path(root, derived_rel), profile)
    if sha256_file(raw) != info["sha256"]: raise ValueError("RAW modificado")
    out = inspect_image(safe_path(root, derived_rel))
    return {k:v for k,v in job.items() if k != "path"} | {
        "profile": profile, "params": json.dumps(PROFILES[profile],sort_keys=True),
        "asset_id": info["sha256"], "parent_asset_id": info["sha256"], "transform_id": transform,
        "raw_path": raw_rel, "derived_path": derived_rel, "raw_sha256": info["sha256"],
        "derived_sha256": out["sha256"], "raw_bytes": info["bytes"], "derived_bytes": out["bytes"],
        "raw_width": info["width"], "raw_height": info["height"], "raw_format": info["format"],
        "raw_mode": info["mode"], "derived_width": out["width"], "derived_height": out["height"],
        "pillow_version": PIL.__version__}


def run_batch(jobs, root, profile="catalogo640", workers=1, stop_after=None, batch_size=16):
    if profile not in PROFILES: raise ValueError("Perfil no válido")
    if type(workers) is not int or workers not in (1,2,4): raise ValueError("Workers: 1, 2 o 4")
    if type(batch_size) is not int or not 1 <= batch_size <= 128: raise ValueError("Micro-lote: 1 a 128")
    if stop_after is not None and (type(stop_after) is not int or stop_after < 1): raise ValueError("stop_after positivo")
    if not jobs or len({j['job_id'] for j in jobs}) != len(jobs): raise ValueError("Lote vacío o trabajos duplicados")
    if len({j['snapshot'] for j in jobs}) != 1: raise ValueError("No mezcles snapshots")
    root = Path(root); root.mkdir(parents=True, exist_ok=True)
    cp_path = root / "state" / "checkpoint.json"
    signature = digest(json.dumps([[j['job_id'],j['input_sha256']] for j in jobs]).encode())
    state = json.loads(cp_path.read_text(encoding='utf-8')) if cp_path.exists() else {"version":VERSION,"signature":signature,"profiles":{}}
    if state.get('signature') != signature or state.get('version') != VERSION: raise ValueError("Usa otra carpeta para otro lote/versión")
    records = state['profiles'].setdefault(profile,{})
    skipped=0; todo=[]
    for job in jobs:
        previous = records.get(job['job_id'],{})
        if previous.get('status')=='DONE' and not validate_record(root,previous['result']): skipped+=1
        else:
            records[job['job_id']]={"status":"PENDING"};todo.append(job)
    selected = todo[:stop_after] if stop_after else todo
    active=0; peak=0; lock=threading.Lock(); durations=[]; processed=[]; failures=[]
    def work(job):
        nonlocal active,peak
        start=time.perf_counter()
        with lock: active+=1;peak=max(peak,active)
        try:
            return job['job_id'],{"status":"DONE","result":process_one(job,root,profile)},time.perf_counter()-start
        except Exception as exc:
            return job['job_id'],{"status":"FAILED","error":type(exc).__name__+": "+str(exc)},time.perf_counter()-start
        finally:
            with lock:active-=1
    started=time.perf_counter()
    atomic_json(cp_path,state)
    for offset in range(0,len(selected),batch_size):
        with ThreadPoolExecutor(max_workers=workers) as executor:
            for key,result,seconds in executor.map(work,selected[offset:offset+batch_size]):
                records[key]=result;durations.append(seconds)
                (processed if result['status']=='DONE' else failures).append(key)
                atomic_json(cp_path,state)
    elapsed=time.perf_counter()-started
    counts={status:sum(v['status']==status for v in records.values()) for status in ('DONE','FAILED','PENDING')}
    assert sum(counts.values())==len(jobs)
    results=[records[j['job_id']]['result'] for j in jobs if records[j['job_id']]['status']=='DONE']
    now={r['job_id']:r for r in results}
    metrics={"timestamp_utc":datetime.now(timezone.utc).isoformat(),"profile":profile,
        "planned":len(jobs),"states":counts,"processed_now":len(processed),"skipped_verified":skipped,
        "failed_now":len(failures),"not_attempted":len(todo)-len(selected),
        "workers":workers,"peak_active":peak,"batch_size":batch_size,"seconds":elapsed,
        "assets_per_second":len(processed)/elapsed if elapsed else 0,
        "raw_bytes_read_now":sum(now[k]['raw_bytes'] for k in processed),
        "derived_bytes_written_now":sum(now[k]['derived_bytes'] for k in processed),
        "slowest_task_seconds":max(durations,default=0),"source":"imagenes_reales_adquiridas_por_docente"}
    assert metrics['processed_now']+metrics['skipped_verified']+metrics['failed_now']+metrics['not_attempted']==len(jobs)
    path=root/'metrics'/(profile+'.json');history=json.loads(path.read_text(encoding='utf-8')) if path.exists() else []
    history.append(metrics);atomic_json(path,history)
    return results, metrics


def normal_records(df):
    return json.loads(df.to_json(orient='records',force_ascii=False))


def export_package(root, inventory, jobs, context):
    root=Path(root); cp=json.loads((root/'state/checkpoint.json').read_text(encoding='utf-8'))
    if any(len(group)!=len(jobs) or any(x['status']!='DONE' for x in group.values()) for group in cp['profiles'].values()):
        raise ValueError('Completa los pendientes de cada perfil antes de cargar el paquete final')
    results=[x['result'] for group in cp['profiles'].values() for x in group.values() if x['status']=='DONE']
    if not results: raise ValueError("No hay resultados")
    for row in results:
        if validate_record(root,row):raise ValueError("Resultado inválido antes de exportar")
    (root/'catalog').mkdir(exist_ok=True);(root/'outputs').mkdir(exist_ok=True)
    pd.DataFrame(inventory['occurrences']).to_parquet(root/'catalog/image_occurrences.parquet',index=False)
    pd.DataFrame(inventory['relations']).to_json(root/'catalog/source_relations.jsonl',orient='records',lines=True,force_ascii=False)
    df=pd.DataFrame(results)
    df.to_json(root/'outputs/assets.jsonl',orient='records',lines=True,force_ascii=False)
    df.to_parquet(root/'outputs/assets.parquet',index=False)
    # Jobs do not depend on paths of the preparing runtime.
    portable=[{k:v for k,v in j.items() if k!='path'} for j in jobs]
    atomic_json(root/'jobs/jobs.json',portable)
    manifest={"schema_version":1,"pipeline":VERSION,"source_snapshot_id":inventory['snapshot'],
        "timestamp_utc":datetime.now(timezone.utc).isoformat(),"counts":inventory['counts'],
        "planned_jobs":len(jobs),"result_count":len(results),"profiles":sorted(cp['profiles']),
        "context":context,"origin_kind":"eltiempo_real", "tools":{"pillow":PIL.__version__,"pandas":pd.__version__},
        "interpretation":"Catálogo e imágenes reales de noticias; contexto por entidad, no prueba sobre un contrato"}
    atomic_json(root/'manifest_s10.json',manifest)
    for name in ['outputs/assets.jsonl','outputs/assets.parquet','catalog/image_occurrences.parquet',
                 'catalog/source_relations.jsonl','jobs/jobs.json','state/checkpoint.json','config/jobs.json','config/inventory.json','config/context.json']:
        manifest.setdefault('files',{})[name]=sha256_file(root/name)
    # Include run metrics in the portable integrity inventory.
    for file in sorted((root/'metrics').glob('*.json')):manifest['files'][file.relative_to(root).as_posix()]=sha256_file(file)
    if (root/'checks/decision.json').exists():manifest['files']['checks/decision.json']=sha256_file(root/'checks/decision.json')
    atomic_json(root/'manifest_s10.json',manifest)
    report=verify_package(root)
    atomic_json(root/'checks/quality_report.json',report)
    return report


def verify_package(root):
    root=Path(root); errors=[]
    try:
        manifest=json.loads((root/'manifest_s10.json').read_text(encoding='utf-8'))
        if manifest['pipeline']!=VERSION or manifest['origin_kind']!='eltiempo_real':errors.append('manifest_origin')
        required={'outputs/assets.jsonl','outputs/assets.parquet','catalog/image_occurrences.parquet',
                  'catalog/source_relations.jsonl','jobs/jobs.json','state/checkpoint.json','config/jobs.json','config/inventory.json','config/context.json'}
        if not required <= set(manifest['files']):errors.append('manifest_files')
        for name,expected in manifest['files'].items():
            if sha256_file(safe_path(root,name))!=expected:errors.append('file_hash:'+name)
        jsonl=pd.read_json(root/'outputs/assets.jsonl',orient='records',lines=True,convert_dates=False,dtype={'article_id':str})
        parquet=pd.read_parquet(root/'outputs/assets.parquet')
        if jsonl.empty:errors.append('empty_exports')
        if normal_records(jsonl)!=normal_records(parquet):errors.append('exports_differ')
        rows=normal_records(parquet)
        if len(rows)!=manifest['result_count'] or len(rows)!=manifest['planned_jobs']*len(manifest['profiles']):errors.append('result_count')
        keys=[(r['job_id'],r['profile']) for r in rows]
        if len(keys)!=len(set(keys)):errors.append('duplicate_jobs')
        jobs=json.loads((root/'jobs/jobs.json').read_text(encoding='utf-8'));byid={j['job_id']:j for j in jobs}
        if len(jobs)!=manifest['planned_jobs'] or len(byid)!=len(jobs):errors.append('jobs_count')
        occurrence=pd.read_parquet(root/'catalog/image_occurrences.parquet')
        if len(occurrence)!=manifest['counts']['image_references'] or occurrence.image_url.nunique()!=manifest['counts']['unique_urls']:errors.append('catalog_counts')
        occs={r['occurrence_id']:r for r in normal_records(occurrence)}
        cp=json.loads((root/'state/checkpoint.json').read_text(encoding='utf-8'))
        if sorted(cp['profiles'])!=manifest['profiles']:errors.append('profiles')
        for profile,states in cp['profiles'].items():
            if set(states)!=set(byid) or any(x['status']!='DONE' for x in states.values()):errors.append('incomplete:'+profile)
        for row in rows:
            errors.extend(row['job_id']+':'+e for e in validate_record(root,row))
            job=byid.get(row['job_id']);occ=occs.get(row['occurrence_id'])
            if not job or any(row[k]!=job[k] for k in ['article_id','occurrence_id','context_reference_url','input_sha256','snapshot','origin_kind','source_url','acquired_at_utc','http_content_type','credit','final_url','input_path','expected_format']):errors.append('job_lineage')
            if not occ or str(occ['article_id'])!=str(row['article_id']) or occ['image_url']!=row['context_reference_url']:errors.append('editorial_lineage')
            if row['snapshot']!=manifest['source_snapshot_id']:errors.append('snapshot')
            stored=cp['profiles'].get(row['profile'],{}).get(row['job_id'],{}).get('result')
            if stored!=row:errors.append('checkpoint_result')
    except Exception as exc:
        errors.append('read_or_schema:'+type(exc).__name__)
    return {"ok":not errors,"errors":errors,"scope":"integridad_tecnica_no_autenticacion_editorial_ni_nota"}


def pack(root, destination):
    report=verify_package(root)
    if not report['ok']:raise ValueError('Paquete inválido: '+str(report['errors'][:3]))
    root=Path(root).resolve();destination=Path(destination).resolve()
    if destination.is_relative_to(root):raise ValueError('ZIP fuera de su propia carpeta')
    with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED) as z:
        for path in sorted(root.rglob('*')):
            if path.is_file():z.write(path,path.relative_to(root).as_posix())
    return destination


def unpack_and_verify(archive,destination):
    destination=Path(destination)
    if destination.exists() and any(destination.iterdir()):raise ValueError('Destino vacío para comprobar portabilidad')
    with zipfile.ZipFile(archive) as z:
        if sum(i.file_size for i in z.infolist())>512*1024**2:raise ValueError('ZIP mayor del límite de práctica')
        if len(z.namelist())!=len(set(z.namelist())):raise ValueError('Nombres duplicados en ZIP')
        for item in z.infolist():
            safe_path(destination,item.filename)
            if (item.external_attr>>16)&0o170000==0o120000:raise ValueError('No se admiten symlinks')
        z.extractall(destination)
    return verify_package(destination)


def record_decision(root,position=0,chosen=0,discarded=0,limit=0):
    codes={0:None,1:'vista320',2:'catalogo640',3:'detalle1024'}
    for v in (position,chosen,discarded,limit):
        if type(v) is not int:raise ValueError('Elige posiciones y códigos enteros; no texto libre')
    if chosen not in codes or discarded not in codes or limit not in (0,1,2,3,4):raise ValueError('Código fuera de opciones')
    root=Path(root);df=pd.read_parquet(root/'outputs/assets.parquet')
    if not 0<=position<=len(df):raise ValueError('Posición de una fila propia o 0 pendiente')
    profiles=set(df.profile)
    if any(codes[c] and codes[c] not in profiles for c in [chosen,discarded]):raise ValueError('El perfil debe haberse ejecutado')
    if chosen and chosen==discarded:raise ValueError('Nombra una alternativa distinta')
    decision={'position':position,'job_id':str(df.iloc[position-1].job_id) if position else None,
        'chosen':codes[chosen],'discarded':codes[discarded],'limit_code':limit,
        'complete':bool(position and chosen and discarded and limit),'graded':False}
    atomic_json(root/'checks/decision.json',decision)
    return decision


def scenario(n,mean_raw_bytes,mean_derived_bytes,seconds_per_asset,width=4000,height=3000,active=2):
    if any(type(x) not in (int,float) or not math.isfinite(x) or x<=0 for x in [n,mean_raw_bytes,mean_derived_bytes,seconds_per_asset,width,height,active]):raise ValueError('Supuestos positivos finitos')
    return {'kind':'escenario_no_benchmark','assets':n,'raw_TB_decimal':n*mean_raw_bytes/1e12,
            'derived_TB_decimal':n*mean_derived_bytes/1e12,'sequential_hours':n*seconds_per_asset/3600,
            'RGB_active_GB_decimal':width*height*3*active/1e9,'excludes':'buffers, I/O, coordinación, reintentos y contención'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify',type=Path,required=True,help='Carpeta de paquete o ZIP')
    args=parser.parse_args()
    if args.verify.suffix=='.zip':
        with tempfile.TemporaryDirectory() as d: report=unpack_and_verify(args.verify,Path(d)/'restored')
    else:report=verify_package(args.verify)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['ok'] else 1)
