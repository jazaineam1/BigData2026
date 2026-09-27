from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
course=json.loads((ROOT/"lms/data/course.json").read_text(encoding="utf-8"))
portal=(ROOT/"lms/portal.html").read_text(encoding="utf-8")
sql=(ROOT/"infraestructura/lms/lms-calendar-october-2026.sql").read_text(encoding="utf-8")

sessions={int(x["n"]):x for x in course["sessions"]}
checks=[
 ("sesión actual declarada S08", course.get("current_tracked_session")==8),
 ("S08 es taller 1 octubre", sessions[8].get("class_date")=="2026-10-01" and sessions[8].get("class_kind")=="assessment_workshop"),
 ("S09 pasa al 8 octubre", sessions[9].get("class_date")=="2026-10-08" and sessions[9].get("starts_at")=="2026-10-08T18:00:00-05:00"),
 ("portal usa starts_at", "Date.parse(String(s.starts_at||''))" in portal and "const past=scheduled.filter" in portal),
 ("portal elige próxima si aún no inicia", "if(scheduled.length)return scheduled[0]" in portal),
 ("portal muestra horario de clase", "function classTime(s)" in portal and "America/Bogota" in portal),
 ("entrega de misma sesión no desplaza taller", "Number(x.session_number)!==Number(s?.session_number)" in portal),
 ("migración S08 1 oct 18h Bogotá", "2026-10-01T23:00:00Z" in sql and "session_number=8" in sql),
 ("migración S09 8 oct 18h Bogotá", "2026-10-08T23:00:00Z" in sql and "session_number=9" in sql),
 ("migración documenta timezone", "America/Bogota" in sql),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("Calendario octubre FAIL: "+", ".join(failed))
print("Calendario octubre 2026: S08 1/oct · S09 8/oct: OK")
