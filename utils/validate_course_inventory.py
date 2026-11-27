"""Comprobación ligera de inventario; no ejecuta modelos ni requiere red."""
from pathlib import Path
import json
import re
import subprocess
ROOT=Path(__file__).resolve().parents[1]
cfg=json.loads((ROOT/"assets/pedagogia/rutas.json").read_text(encoding="utf-8"))
inv=json.loads((ROOT/"docs/inventario-retirados.json").read_text(encoding="utf-8"))
tracked=set(subprocess.check_output(["git","ls-files","-z"],cwd=ROOT).decode().split("\0"))
assert not {x["path"] for x in inv["removed"]}&tracked, "Reapareció material retirado"
assert len(cfg["routes"])==17
index=(ROOT/"index.html").read_text(encoding="utf-8")
cards={i.upper().zfill(2):body for i,body in re.findall(r'<article\b[^>]*data-n="([^"]+)"[^>]*>(.*?)</article>', index,re.S)}
assert set(cards)=={r["id"] for r in cfg["routes"]}
for r in cfg["routes"]:
    if r["ref"]==cfg["branch"]:
        assert r["nb"] in tracked, r["nb"]
    first=re.search(r'<div class="session-actions">(.*?)</div>',cards[r["id"]],re.S)
    assert first and len(re.findall(r'<a\b',first.group(1)))==2, r["id"]
    expected = "s01-fundamentos-adquisicion.html" if r["id"]=="01" else "compras-claras.html?s="+r["id"]
    assert expected in first.group(1), r["id"]
    assert len(r["steps"])==4
    if r.get("original"):
        assert (ROOT/"Presentaciones"/r["original"]).is_file(), r["original"]
assert not any(x.startswith("Airflow/") for x in tracked)
course=json.loads((ROOT/"lms/data/course.json").read_text(encoding="utf-8"))
assert next(x for x in course["sessions"] if x["n"]==15)["status"]=="draft"
print("OK: inventario, 17 sesiones, 2 accesos por sesión y S15 no publicada")
