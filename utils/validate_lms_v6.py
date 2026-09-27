from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    return (ROOT/path).read_text(encoding="utf-8")

backend=read("infraestructura/lms/functions/bigdata-session/index.ts")
migration=read("infraestructura/lms/lms-v6-live-controls.sql")
realtime=read("lms/assets/lms-realtime.js")
teacher=read("lms/wall.html")
wall=read("lms/class-wall.html")
deck=read("Presentaciones/s09-de-palabras-a-significado.html")
tests=read("tests/lms-v6-regression.spec.js")

checks=[
    ("tabla controles server-side", "create table if not exists public.bd_session_controls" in migration and "revoke all on table public.bd_session_controls from anon, authenticated" in migration),
    ("señal Realtime sin PII", "create table if not exists public.bd_realtime_signals" in migration and "course_code" in migration and "scope" in migration and "user_id" not in migration.split("create table if not exists public.bd_realtime_signals",1)[1].split(");",1)[0]),
    ("publicación Realtime", "alter publication supabase_realtime add table public.bd_realtime_signals" in migration),
    ("cliente Realtime fijado", "@supabase/supabase-js@2.117.1" in realtime and "postgres_changes" in realtime and "bd_realtime_signals" in realtime),
    ("fallback polling docente", "realtimeReady?60000:15000" in teacher and "setInterval" in teacher),
    ("fallback polling muro", "realtimeReady?60000:15000" in wall and "setInterval" in wall),
    ("controles docentes autorizados", "teacher_set_control" in backend and "teacher_clear_control" in backend and "requireTeacher(ctx)" in backend),
    ("acciones controladas", all(x in backend for x in ['"open_lab"','"close_lab"','"goto_slide"','"pin_hint"'])),
    ("LAB cerrado se valida server-side", 'await isLabClosed(run.id,n,activity.code)' in backend),
    ("datos reales siguen tras Edge Function", "session_controls" in backend and "controls:await sessionControls(run.id,n)" in backend),
    ("WALL Realtime por invalidación", 'realtimeSignal(n,"wall")' in backend),
    ("telemetría separada", 'event==="heartbeat"' in backend and 'realtimeSignal(n,"teacher_wall")' in backend),
    ("modo proyección anonimizado", "body.projection" in wall and "Respuesta '+(index+1)" in wall and "projection&&teacher" in wall),
    ("proyección sin moderación", "if(projection||!['teacher','admin'].includes" in wall),
    ("confianza S09", 'id="conf-'+code' in deck and "confidence:conf?.value||null" in deck),
    ("confianza backend", "last_confidence" in backend and "high_confidence_wrong" in backend),
    ("goto slide no forzado", "Tú decides cuándo cambiar." in deck and "location.hash='s'+target" in deck),
    ("QA V6", "dos estudiantes y docente" in tests and "modo proyección anonimiza" in tests and "exige confianza" in tests),
]

failed=[name for name,ok in checks if not ok]
for name,ok in checks:
    print(("OK   " if ok else "FAIL ")+name)
if failed:
    raise SystemExit("Validación LMS V6 falló: "+", ".join(failed))
print("LMS V6 foundation: OK")
