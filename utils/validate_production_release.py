#!/usr/bin/env python3
from pathlib import Path
import json,re,sys
ROOT=Path(__file__).resolve().parents[1]
manifest=json.loads((ROOT/"infraestructura/lms/production-release.json").read_text("utf-8"))
release=manifest["release"]
errors=[]
for slug in manifest["critical_functions"]:
    p=ROOT/"infraestructura/lms/functions"/slug/"index.ts"
    src=p.read_text("utf-8")
    m=re.search(r'const RELEASE="([^"]+)";',src)
    if not m or m.group(1)!=release:
        errors.append(f"{slug}: RELEASE no coincide con {release}")
    if '"X-BigData-Release":RELEASE' not in src:
        errors.append(f"{slug}: falta X-BigData-Release")
session=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text("utf-8")
if 'action==="deployment_status"' not in session or '"bd_deployment_state"' not in session:
    errors.append("bigdata-session: falta deployment_status")
marker=(ROOT/"infraestructura/lms/lms-v56-deployment-state.sql").read_text("utf-8")
if release not in marker:
    errors.append("migración de canary no coincide con release")
if errors:
    print("PRODUCTION RELEASE: FAIL")
    for e in errors: print(" -",e)
    sys.exit(1)
print("PRODUCTION RELEASE: OK",release)
