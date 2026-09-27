from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
index=(ROOT/"index.html").read_text(encoding="utf-8")
portal=(ROOT/"lms/portal.html").read_text(encoding="utf-8")
course=json.loads((ROOT/"lms/data/course.json").read_text(encoding="utf-8"))
seed=(ROOT/"infraestructura/lms/s09-vector-search-seed.sql").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-calendar-s08-oct1-v15.sql").read_text(encoding="utf-8")
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")

checks=[
    ("curso marca S08 actual", int(course.get("current_tracked_session") or 0)==8),
    ("progreso actual apunta S08", any(x.get("code")=="progress_current" and x.get("path")=="progress.html?s=8" for x in course.get("student_tools",[]))),
    ("portada anuncia taller S08", "Próxima sesión · jueves 1 de octubre" in index and "S08 · SECOP Data Pipeline" in index and 'href="lms/session.html?s=8"' in index),
    ("S08 marcada actual en ruta", 'class="session evaluation current"' in index and 'data-current="true"' in index and "1 oct · actual" in index),
    ("S09 deja de ser actual", 'class="session current"' not in index and "Próxima · 8 oct" in index),
    ("filtro actual usa data-current", "filter==='current'?c.dataset.current==='true'" in index),
    ("portal conserva ventana activa de clase", "start<=now&&now<start+minutes*60000" in portal and "estimated_minutes" in portal),
    ("portal usa next_session como fallback", "model?.next_session?.session_number" in portal),
    ("portal no toma última visible por defecto", "rows.filter(s=>s.status==='visible').at(-1)" not in portal),
    ("portal WALL S08 correcto", "Number(cs.session_number)===8?'teacher-wall.html':'wall.html?s='+cs.session_number" in portal),
    ("migración fecha S08", "session_number=8" in migration and "2026-10-01 23:00:00+00" in migration),
    ("migración fecha S09", "session_number=9" in migration and "2026-10-08 23:00:00+00" in migration),
    ("seed S09 actualizado", "2026-10-08 23:00:00+00" in seed and "2026-10-01 23:00:00+00" not in seed),
    ("confianza retirada de S09", "¿Qué tan seguro estás?" not in deck and 'id="conf-' not in deck),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
if failed:
    raise SystemExit("Calendario S08/S09 FAIL: "+", ".join(failed))
print("Calendario S08 1-oct / S09 8-oct: OK")
