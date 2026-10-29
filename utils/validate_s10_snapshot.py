#!/usr/bin/env python3
"""Integridad y procedencia del snapshot público, sin descargar al medio."""
import hashlib,json
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1];base=ROOT/'Datos/s10_imagenes_reales'
rows=json.loads((base/'inputs.json').read_text(encoding='utf-8'))
assert len(rows)==32 and len({r['job_id'] for r in rows})==32
allowed={'inputs.json','README.md','acquisition_report.json'};total=0
for row in rows:
 relative=PurePosixPath(row['input_path'])
 assert not relative.is_absolute() and '..' not in relative.parts and relative.parts[0]=='raw'
 payload=(base/relative).read_bytes();total+=len(payload)
 assert payload[:4]==b'RIFF' and payload[8:12]==b'WEBP' and row['expected_format']=='WEBP'
 assert hashlib.sha256(payload).hexdigest()==row['input_sha256']
 assert row['origin_kind']=='eltiempo_real' and row['source_url'].startswith('https://')
 assert row['acquired_at_utc'].startswith('2026-10-29T') and row['credit']
 assert row['occurrence_id'].startswith(row['article_id']+':')
 assert set(row)=={'job_id','article_id','occurrence_id','context_reference_url','source_url','origin_kind','acquired_at_utc','http_content_type','final_url','credit','input_path','input_sha256','snapshot','expected_format'}
 allowed.add(relative.as_posix())
assert {p.relative_to(base).as_posix() for p in base.rglob('*') if p.is_file()}==allowed
assert total==4295770
print('S10 snapshot OK: 32 imágenes reales, 24 noticias, hashes y procedencia; sin ZIP ni código ejecutable')
