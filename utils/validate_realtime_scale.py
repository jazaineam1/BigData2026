from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
deck=(ROOT/"Presentaciones/s09-de-palabras-a-significado.html").read_text(encoding="utf-8")
wall=(ROOT/"lms/wall.html").read_text(encoding="utf-8")
retention=(ROOT/"infraestructura/lms/lms-realtime-retention.sql").read_text(encoding="utf-8")
broadcast=(ROOT/"infraestructura/lms/lms-realtime-broadcast-v10.sql").read_text(encoding="utf-8")
client=(ROOT/"lms/assets/lms-realtime.js").read_text(encoding="utf-8")
backend=(ROOT/"infraestructura/lms/functions/bigdata-session/index.ts").read_text(encoding="utf-8")
checks=[
 ("estudiante solo escucha controles", "scopes:['controls']" in deck and "scopes:['controls','progress']" not in deck),
 ("poll estudiante espaciado", "30000" in deck and "studentTimer=setInterval" in deck),
 ("wall usa throttle 3s", "windowMs=3000" in wall and "lastRealtimeLoad" in wall),
 ("throttle tiene leading update", "elapsed>=windowMs" in wall and "load().catch" in wall),
 ("throttle conserva trailing update", "if(reloadTimer)return" in wall and "setTimeout" in wall),
 ("señales tienen índice temporal", "bd_realtime_signals_created_at_idx" in retention),
 ("retención 24h", "interval '24 hours'" in retention),
 ("cron idempotente", "bigdata-prune-realtime-signals" in retention and "if not exists" in retention.lower()),
 ("cliente usa Broadcast", ".on('broadcast',{event:'signal'}" in client and "postgres_changes" not in client),
 ("backend emite Broadcast", 'type:"broadcast"' in backend and 'event:"signal"' in backend and 'db.channel("bigdata-s"+n)' in backend),
 ("backend deja de insertar filas de señal", 'db.from("bd_realtime_signals").insert' not in backend),
 ("publication legacy retirada", "alter publication supabase_realtime drop table public.bd_realtime_signals" in broadcast.lower()),
 ("tabla legacy documentada", "LEGACY V10" in broadcast and "ya no recibe invalidaciones nuevas" in broadcast),
]
failed=[n for n,ok in checks if not ok]
for n,ok in checks: print(("OK   " if ok else "FAIL ")+n)
if failed: raise SystemExit("Realtime scale FAIL: "+", ".join(failed))
print("Realtime Broadcast/scale/retention: OK")
