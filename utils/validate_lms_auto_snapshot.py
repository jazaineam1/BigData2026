from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
ops=(ROOT/"infraestructura/lms/functions/bigdata-lms-ops/index.ts").read_text(encoding="utf-8")
sql=(ROOT/"infraestructura/lms/lms-ops-auto-snapshot-v9.sql").read_text(encoding="utf-8")
ui=(ROOT/"lms/admin-operations.html").read_text(encoding="utf-8")
docs=(ROOT/"infraestructura/lms/OPERATIONS_V8.md").read_text(encoding="utf-8")

checks=[
 ("bucket privado", "'bigdata-lms-snapshots'" in sql and "false," in sql and "application/json" in sql),
 ("secreto generado en Vault", "bigdata_snapshot_cron_secret" in sql and "gen_random_bytes(32)" in sql),
 ("validador solo service_role", "bigdata_validate_snapshot_cron_secret" in sql and "grant execute" in sql.lower() and "service_role" in sql),
 ("cron diario", "bigdata-daily-academic-snapshot" in sql and "'20 8 * * *'" in sql),
 ("cron usa pg_net", "net.http_post" in sql and "x-lms-snapshot-secret" in sql),
 ("endpoint valida scheduler", 'action==="scheduled_snapshot"' in ops and "snapshotCronAuthorized" in ops),
 ("snapshot automático usa Storage", "SNAPSHOT_BUCKET" in ops and ".upload(" in ops and '"automatic"' in ops),
 ("SHA-256 incluido", "sha256:await sha256(dataJson)" in ops),
 ("retención 30 días", "SNAPSHOT_RETENTION_DAYS=30" in ops and "pruneAutomaticSnapshots" in ops),
 ("auditoría automática", '"bigdata.ops.snapshot.auto"' in ops),
 ("actor sistema sin suplantar usuario", 'audit(null,"bigdata.ops.snapshot.auto"' in ops),
 ("snapshot incluye mapeo de competencias", "lms_activity_competencies_v2:activityCompetencyMappings" in ops),
 ("panel no promete backup", "No equivale al backup administrado de Supabase" in ui and "No es el backup de plataforma" in ui),
 ("panel muestra automático/manual", "academic_snapshot_mode===\'automatic\'" in ui),
 ("runbook aclara límites", "no reemplaza una copia externa ni el backup administrado de plataforma" in docs),
]
failed=[name for name,ok in checks if not ok]
for name,ok in checks: print(("OK   " if ok else "FAIL ")+name)
if failed: raise SystemExit("Auto snapshot FAIL: "+", ".join(failed))
print("LMS automatic academic snapshot: OK")
