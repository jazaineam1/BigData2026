#!/usr/bin/env python3
"""La portada no puede contradecir a lms/data/course.json.

Comprueba invariantes que no caducan con la fecha:
- la sesión que la portada muestra por defecto es la de `current_tracked_session`;
- exactamente una tarjeta y un bloque de hero están marcados como actuales;
- todo bloque de hero apunta a una sesión visible con fecha de inicio;
- la portada conserva la misma regla del portal (última sesión iniciada, o la próxima).
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
course = json.loads((ROOT / "lms/data/course.json").read_text(encoding="utf-8"))
index = (ROOT / "index.html").read_text(encoding="utf-8")
portal = (ROOT / "lms/portal.html").read_text(encoding="utf-8")

sessions = {int(s["n"]): s for s in course["sessions"]}
tracked = int(course.get("current_tracked_session", 0))

heroes = re.findall(r'<aside class="today"[^>]*data-session="(\d+)"([^>]*)>', index)
visible_heroes = [int(n) for n, rest in heroes if "hidden" not in rest]
current_cards = [int(n) for n in re.findall(r'<article class="session[^"]*\bcurrent\b[^"]*" data-n="(\d+)"', index)]
card_numbers = [int(n) for n in re.findall(r'<article class="session[^"]*" data-n="(\d+)"', index)]

def scheduled(n):
    s = sessions.get(n, {})
    return s.get("status") == "visible" and bool(s.get("starts_at"))

checks = [
    ("hero por defecto = current_tracked_session", visible_heroes == [tracked]),
    ("una sola tarjeta actual = current_tracked_session", current_cards == [tracked]),
    ("todo hero apunta a sesión visible con starts_at", bool(heroes) and all(scheduled(int(n)) for n, _ in heroes)),
    ("todas las tarjetas visibles del curso están en la portada",
     {n for n, s in sessions.items() if s.get("status") == "visible"} <= set(card_numbers)),
    ("portada aplica la regla del portal (starts_at <= ahora, si no la próxima)",
     "past.length?past[past.length-1]:rows[0]" in index and "const past=scheduled.filter" in portal),
    ("portada sin red conserva la sesión estática", ".catch(()=>{})" in index),
]
failed = [name for name, ok in checks if not ok]
for name, ok in checks:
    print(("OK   " if ok else "FAIL ") + name)
if failed:
    raise SystemExit("Calendario de portada FAIL: " + ", ".join(failed))
print(f"Portada consistente con course.json (sesión actual declarada: S{tracked:02d}): OK")
