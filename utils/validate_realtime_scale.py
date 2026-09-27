from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")
wall=(ROOT/"lms/wall.html").read_text(encoding="utf-8")
backend=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text(encoding="utf-8")
client=(ROOT/"lms/assets/lms-realtime.js").read_text(encoding="utf-8")
migration=(ROOT/"infraestructura/lms/lms-realtime-broadcast-v12.sql").read_text(encoding="utf-8")
checks=[
 ("estudiante solo escucha controles", "scopes:['controls']" in deck and "scopes:['controls','progress']" not in deck),
 ("poll estudiante espaciado", "30000" in deck and "studentTimer=setInterval" in deck),
 ("wall usa throttle 3s", "windowMs=3000" in wall and "lastRealtimeLoad" in wall),
 ("throttle tiene leading update", "elapsed>=windowMs" in wall and "load().catch" in wall),
 ("throttle conserva trailing update", "if(reloadTimer)return" in wall and "setTimeout" in wall),
 ("cliente usa Broadcast", ".on('broadcast',{event:'invalidate'}" in client and "postgres_changes" not in client and "bd_realtime_signals" not in client),
 ("topic por sesión", "'bigdata:session:'+n" in client and 'topic:"bigdata:session:"+n' in backend),
 ("backend usa REST Broadcast", "/realtime/v1/api/broadcast" in backend and '"event":"invalidate"' not in backend and 'event:"invalidate"' in backend),
 ("backend no persiste señal", 'from("bd_realtime_signals").insert' not in backend),
 ("payload Realtime sin PII", "payload:{course_code:COURSE,session_number:n,scope}" in backend and "user_id" not in backend[backend.index('async function realtimeSignal'):backend.index('async function sessionControls')]),
 ("tabla legacy sale de publicación", "alter publication supabase_realtime drop table public.bd_realtime_signals" in migration),
 ("cron legacy se retira", "cron.unschedule('bigdata-prune-realtime-signals')" in migration),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("Realtime Broadcast FAIL: "+", ".join(failed))
print("Realtime Broadcast/fallback: OK")
