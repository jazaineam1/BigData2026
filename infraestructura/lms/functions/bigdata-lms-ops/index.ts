import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);
const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const BACKUP_VERSION=1;
const RPO_HOURS=24;
const RTO_HOURS=4;
const SNAPSHOT_BUCKET="bigdata-lms-snapshots";
const SNAPSHOT_RETENTION_DAYS=30;
const SESSION_TTL_HOURS={student:30*24,teacher:12,admin:4};
function roleCapabilities(role:string){
  if(role==="admin")return ["ops.view","backup.export","retention.preview","retention.cleanup","users.manage","course.manage"];
  if(role==="teacher")return ["ops.view","backup.export","retention.preview","course.manage"];
  return [];
}

function origin(req:Request){
  const o=req.headers.get("origin");if(!o)return "";
  if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;
  return null;
}
function headers(req:Request){
  const o=origin(req);
  return {"Access-Control-Allow-Origin":o||"https://jazaineam1.github.io",
    "Access-Control-Allow-Headers":"authorization, content-type",
    "Access-Control-Allow-Methods":"GET, POST, OPTIONS","Vary":"Origin","Cache-Control":"no-store",
    "X-Content-Type-Options":"nosniff","Referrer-Policy":"strict-origin-when-cross-origin"};
}
function out(req:Request,body:unknown,status=200){
  return new Response(JSON.stringify(body),{status,headers:{...headers(req),"Content-Type":"application/json"}});
}
function bearer(req:Request){const h=req.headers.get("authorization")||"";return h.toLowerCase().startsWith("bearer ")?h.slice(7).trim():""}
async function sha256(text:string){const d=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text));return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,"0")).join("")}
async function current(req:Request){
  const token=bearer(req);if(!token)return null;
  const {data:s}=await db.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent,created_at")
    .eq("token_hash",await sha256(token)).is("revoked_at",null).maybeSingle();
  if(!s)return null;const deadline=s.expires_at?Date.parse(s.expires_at):(Date.parse(s.created_at)+(s.persistent?30:1)*24*3600_000);if(!Number.isFinite(deadline)||deadline<=Date.now())return null;
  const {data:u}=await db.from("lms_users").select("id,username,display_name,role,active,email")
    .eq("id",s.user_id).eq("active",true).maybeSingle();
  return u?{session:s,user:u}:null;
}
async function activeRun(ctx:any){
  const {data:memberships}=await db.from("lms_run_enrollments").select("course_run_id,role,status,enrolled_at")
    .eq("user_id",ctx.user.id).eq("status","active").order("enrolled_at",{ascending:false});
  for(const m of memberships||[]){
    const {data:r}=await db.from("lms_course_runs").select("*").eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:m.role};
  }
  if(["teacher","admin"].includes(ctx.user.role)){
    const {data:r}=await db.from("lms_course_runs").select("*").eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:ctx.user.role};
  }
  return null;
}
function requireTeacher(ctx:any){if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH")}
function requireAdmin(ctx:any){if(ctx.user.role!=="admin")throw new Error("ADMIN_ONLY")}
async function audit(actor:string|null,action:string,entity:string,id:string|null,metadata:any={}){
  await db.from("lms_audit_log").insert({actor_user_id:actor,action,entity_type:entity,entity_id:id,metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}}).then(()=>{}).catch(()=>{});
}
async function eqRows(table:string,column:string,value:any,select="*"){
  const {data,error}=await db.from(table).select(select).eq(column,value);if(error)throw error;return data||[];
}
async function inRows(table:string,column:string,values:any[],select="*"){
  if(!values.length)return [];
  const {data,error}=await db.from(table).select(select).in(column,values);if(error)throw error;return data||[];
}
function ids(rows:any[]){return rows.map(x=>x.id).filter(Boolean)}
function counts(data:Record<string,any[]>){
  const o:Record<string,number>={};for(const [k,v] of Object.entries(data))o[k]=Array.isArray(v)?v.length:0;return o;
}

async function backupData(run:any){
  const [
    course,runEnrollments,courseEnrollments,runSessions,runResources,announcements,
    assignments,rubrics,competencies,questions,quizzes,groups,threads,
    interventions,snapshots,learningEvents,analyticsRules,alertRules,
    activityProgress,sessionProgress,events,bdActivities,bdSessions,bdActivityProgress,
    bdSessionProgress,bdEvents,bdSubmissions,bdWindows,accessRequests,bookmarks,certificates
  ]=await Promise.all([
    eqRows("lms_courses","code",COURSE),
    eqRows("lms_run_enrollments","course_run_id",run.id),
    eqRows("lms_enrollments","course_code",COURSE),
    eqRows("lms_run_sessions_v2","course_run_id",run.id),
    eqRows("lms_run_resources_v2","course_run_id",run.id),
    eqRows("lms_announcements","course_run_id",run.id),
    eqRows("lms_assignments_v2","course_run_id",run.id),
    eqRows("lms_rubric_templates_v2","course_run_id",run.id),
    eqRows("lms_competencies_v2","course_run_id",run.id),
    eqRows("lms_questions_v2","course_run_id",run.id),
    eqRows("lms_quizzes_v2","course_run_id",run.id),
    eqRows("lms_groups_v2","course_run_id",run.id),
    eqRows("lms_discussion_threads_v2","course_run_id",run.id),
    eqRows("lms_interventions_v2","course_run_id",run.id),
    eqRows("lms_student_snapshots_v2","course_run_id",run.id),
    eqRows("lms_learning_events_v2","course_run_id",run.id),
    eqRows("lms_analytics_rules_v2","course_run_id",run.id),
    eqRows("lms_alert_rules_v2","course_run_id",run.id),
    eqRows("lms_activity_progress","course_run_id",run.id),
    eqRows("lms_session_progress","course_run_id",run.id),
    eqRows("lms_events","course_run_id",run.id),
    eqRows("bd_lms_activities","course_code",COURSE),
    eqRows("bd_lms_sessions","course_code",COURSE),
    eqRows("bd_lms_activity_progress","course_run_id",run.id),
    eqRows("bd_lms_session_progress","course_run_id",run.id),
    eqRows("bd_lms_events","course_run_id",run.id),
    eqRows("bd_lms_s08_submissions","course_run_id",run.id),
    eqRows("bd_lms_session_windows","course_run_id",run.id),
    eqRows("lms_access_requests","course_code",COURSE),
    eqRows("lms_bookmarks","course_run_id",run.id),
    eqRows("lms_certificates","course_run_id",run.id)
  ]);

  const assignmentIds=ids(assignments),quizIds=ids(quizzes),groupIds=ids(groups),threadIds=ids(threads),questionIds=ids(questions);
  const [
    submissions,submissionFiles,gradeHistory,accommodations,assignmentCompetencies,assignmentGroupSettings,
    quizItems,quizAttempts,groupMembers,groupSubmissions,posts,peerReviews
  ]=await Promise.all([
    inRows("lms_submissions_v2","assignment_id",assignmentIds),
    inRows("lms_submission_files_v2","assignment_id",assignmentIds),
    inRows("lms_grade_history_v2","assignment_id",assignmentIds),
    inRows("lms_assignment_accommodations_v2","assignment_id",assignmentIds),
    inRows("lms_assignment_competencies_v2","assignment_id",assignmentIds),
    inRows("lms_assignment_group_settings_v2","assignment_id",assignmentIds),
    inRows("lms_quiz_items_v2","quiz_id",quizIds),
    inRows("lms_quiz_attempts_v2","quiz_id",quizIds),
    inRows("lms_group_members_v2","group_id",groupIds),
    inRows("lms_group_submissions_v2","group_id",groupIds),
    inRows("lms_discussion_posts_v2","thread_id",threadIds),
    inRows("lms_peer_reviews_v2","assignment_id",assignmentIds)
  ]);
  const attemptIds=ids(quizAttempts),groupSubmissionIds=ids(groupSubmissions),postIds=ids(posts);
  const [quizResponses,groupContributions,mentions]=await Promise.all([
    inRows("lms_quiz_responses_v2","attempt_id",attemptIds),
    inRows("lms_group_contributions_v2","group_submission_id",groupSubmissionIds),
    inRows("lms_discussion_mentions_v2","post_id",postIds)
  ]);

  const userIds=[...new Set([
    ...runEnrollments.map((x:any)=>x.user_id),
    ...submissions.map((x:any)=>x.user_id),
    ...quizAttempts.map((x:any)=>x.user_id),
    ...groupMembers.map((x:any)=>x.user_id)
  ].filter(Boolean))];
  const users=await inRows("lms_users","id",userIds,"id,username,display_name,role,active,email,created_at,updated_at");
  const activityCompetencyMappings=await eqRows("lms_activity_competencies_v2","course_run_id",run.id);

  const data:Record<string,any[]>={
    lms_courses:course,
    lms_course_runs:[{...run,enrollment_role:undefined}],
    lms_users:users,
    lms_enrollments:courseEnrollments.filter((x:any)=>userIds.includes(x.user_id)),
    lms_run_enrollments:runEnrollments,
    lms_run_sessions_v2:runSessions,
    lms_run_resources_v2:runResources,
    lms_announcements:announcements,
    lms_assignments_v2:assignments,
    lms_rubric_templates_v2:rubrics,
    lms_assignment_accommodations_v2:accommodations,
    lms_assignment_competencies_v2:assignmentCompetencies,
    lms_activity_competencies_v2:activityCompetencyMappings,
    lms_assignment_group_settings_v2:assignmentGroupSettings,
    lms_submissions_v2:submissions,
    lms_submission_files_v2:submissionFiles,
    lms_grade_history_v2:gradeHistory,
    lms_competencies_v2:competencies,
    lms_questions_v2:questions,
    lms_quizzes_v2:quizzes,
    lms_quiz_items_v2:quizItems,
    lms_quiz_attempts_v2:quizAttempts,
    lms_quiz_responses_v2:quizResponses,
    lms_groups_v2:groups,
    lms_group_members_v2:groupMembers,
    lms_group_submissions_v2:groupSubmissions,
    lms_group_contributions_v2:groupContributions,
    lms_discussion_threads_v2:threads,
    lms_discussion_posts_v2:posts,
    lms_discussion_mentions_v2:mentions,
    lms_peer_reviews_v2:peerReviews,
    lms_interventions_v2:interventions,
    lms_student_snapshots_v2:snapshots,
    lms_learning_events_v2:learningEvents,
    lms_analytics_rules_v2:analyticsRules,
    lms_alert_rules_v2:alertRules,
    lms_activity_progress:activityProgress,
    lms_session_progress:sessionProgress,
    lms_events:events,
    lms_access_requests:accessRequests,
    lms_bookmarks:bookmarks,
    lms_certificates:certificates,
    bd_lms_activities:bdActivities,
    bd_lms_sessions:bdSessions,
    bd_lms_activity_progress:bdActivityProgress,
    bd_lms_session_progress:bdSessionProgress,
    bd_lms_events:bdEvents,
    bd_lms_s08_submissions:bdSubmissions,
    bd_lms_session_windows:bdWindows
  };
  return data;
}

async function snapshotEnvelope(run:any,generatedBy:string|null,mode:"manual"|"automatic"){
  const data=await backupData(run),dataJson=JSON.stringify(data),fileRows=data.lms_submission_files_v2||[];
  const manifest={
    format:"bigdata-lms-academic-snapshot",
    version:BACKUP_VERSION,
    course_code:COURSE,
    run_code:RUN_CODE,
    course_run_id:run.id,
    generated_at:new Date().toISOString(),
    generated_by:generatedBy,
    generation_mode:mode,
    sha256:await sha256(dataJson),
    table_counts:counts(data),
    storage_files:fileRows.length,
    storage_bytes:fileRows.reduce((a:number,x:any)=>a+Number(x.size_bytes||0),0),
    includes_binary_files:false,
    platform_backup_equivalent:false,
    excludes:["password_hash","Supabase Auth secrets","Edge Function secrets","binary Storage objects"]
  };
  return {manifest,data,warnings:[
    "Este snapshot sirve para portabilidad y recuperación académica; no sustituye el backup administrado de la plataforma.",
    "No contiene password_hash ni secretos de autenticación.",
    "La restauración debe seguir el runbook y realizarse en una ventana controlada."
  ]};
}
async function snapshotCronAuthorized(req:Request){
  const secret=String(req.headers.get("x-lms-snapshot-secret")||"");
  if(secret.length<32)return false;
  const {data,error}=await db.rpc("bigdata_validate_snapshot_cron_secret",{p_secret:secret});
  return !error&&data===true;
}
async function pruneAutomaticSnapshots(){
  const cutoff=Date.now()-SNAPSHOT_RETENTION_DAYS*24*3600_000;
  const {data,error}=await db.storage.from(SNAPSHOT_BUCKET).list(RUN_CODE,{
    limit:100,offset:0,sortBy:{column:"created_at",order:"asc"}
  });
  if(error)return {removed:0,warning:error.message};
  const expired=(data||[]).filter((x:any)=>x.name&&x.created_at&&Date.parse(x.created_at)<cutoff)
    .map((x:any)=>RUN_CODE+"/"+x.name);
  if(!expired.length)return {removed:0};
  const {error:removeError}=await db.storage.from(SNAPSHOT_BUCKET).remove(expired);
  return removeError?{removed:0,warning:removeError.message}:{removed:expired.length};
}
async function scheduledSnapshot(){
  const {data:run,error}=await db.from("lms_course_runs").select("*")
    .eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
  if(error||!run)throw new Error("No se encontró la cohorte activa para snapshot");
  const envelope=await snapshotEnvelope(run,null,"automatic");
  const stamp=envelope.manifest.generated_at.replace(/[:.]/g,"-");
  const path=RUN_CODE+"/snapshot-"+stamp+".json";
  const payload=JSON.stringify({ok:true,...envelope})+"\n";
  const {error:uploadError}=await db.storage.from(SNAPSHOT_BUCKET).upload(
    path,new Blob([payload],{type:"application/json"}),
    {contentType:"application/json",upsert:false,cacheControl:"3600"}
  );
  if(uploadError)throw new Error("No se pudo guardar el snapshot automático: "+uploadError.message);
  const retention=await pruneAutomaticSnapshots();
  await audit(null,"bigdata.ops.snapshot.auto","course_run",run.id,{
    path,sha256:envelope.manifest.sha256,tables:Object.keys(envelope.data).length,
    storage_files:envelope.manifest.storage_files,retention_removed:retention.removed||0,
    retention_warning:retention.warning||null
  });
  return {ok:true,manifest:envelope.manifest,path,retention};
}

async function exportBackup(ctx:any,run:any){
  requireTeacher(ctx);
  const envelope=await snapshotEnvelope(run,ctx.user.id,"manual");
  await audit(ctx.user.id,"bigdata.ops.snapshot.export","course_run",run.id,{
    tables:Object.keys(envelope.data).length,
    storage_files:envelope.manifest.storage_files,
    sha256:envelope.manifest.sha256
  });
  return {ok:true,...envelope};
}

async function runAssignmentIds(run:any){return ids(await eqRows("lms_assignments_v2","course_run_id",run.id))}
async function retentionPreview(ctx:any,run:any,body:any={}){
  requireTeacher(ctx);
  const requested=Number(body.older_than_hours??24);
  const hours=Number.isFinite(requested)?Math.max(24,Math.min(24*90,requested)):24;
  const assignmentIds=await runAssignmentIds(run);
  if(!assignmentIds.length)return {viewer:ctx.user,older_than_hours:hours,candidates:[],total_bytes:0};
  const cutoff=new Date(Date.now()-hours*3600_000).toISOString();
  const {data,error}=await db.from("lms_submission_files_v2")
    .select("id,assignment_id,user_id,bucket,object_path,file_name,mime_type,size_bytes,status,created_at,submission_id")
    .in("assignment_id",assignmentIds)
    .in("status",["pending","abandoned"])
    .lt("created_at",cutoff)
    .order("created_at",{ascending:true});
  if(error)throw error;
  const candidates=data||[];
  return {viewer:ctx.user,older_than_hours:hours,cutoff,candidates,total_bytes:candidates.reduce((a:number,x:any)=>a+Number(x.size_bytes||0),0)};
}

async function cleanupRetention(ctx:any,run:any,body:any){
  requireAdmin(ctx);
  const fileIds=Array.isArray(body.file_ids)?[...new Set(body.file_ids.map(String))].slice(0,200):[];
  if(!fileIds.length)throw new Error("Selecciona archivos candidatos");
  if(String(body.confirmation||"")!=="ELIMINAR_HUERFANOS")throw new Error("Confirmación de limpieza inválida");
  const assignmentIds=await runAssignmentIds(run);if(!assignmentIds.length)return {ok:true,deleted:0};
  const cutoff=new Date(Date.now()-24*3600_000).toISOString();
  const {data,error}=await db.from("lms_submission_files_v2")
    .update({status:"abandoned"})
    .in("id",fileIds).in("assignment_id",assignmentIds)
    .in("status",["pending","abandoned"])
    .lt("created_at",cutoff)
    .select("id,assignment_id,bucket,object_path,status,created_at");
  if(error)throw error;
  const rows=data||[];
  if(rows.length!==fileIds.length)throw new Error("Uno o más archivos ya no son candidatos seguros para limpieza");
  if(rows.some((x:any)=>x.status!=="abandoned"))throw new Error("La limpieza solo puede reclamar archivos abandoned");

  const byBucket=new Map<string,string[]>();
  for(const r of rows){const a=byBucket.get(r.bucket)||[];a.push(r.object_path);byBucket.set(r.bucket,a)}
  for(const [bucket,paths] of byBucket){
    const {error:storageError}=await db.storage.from(bucket).remove(paths);
    if(storageError)throw new Error("Storage no pudo eliminar todos los objetos: "+storageError.message);
  }
  const {error:deleteError}=await db.from("lms_submission_files_v2").delete().in("id",fileIds)
    .in("assignment_id",assignmentIds).in("status",["pending","abandoned"]);
  if(deleteError)throw deleteError;
  await audit(ctx.user.id,"bigdata.ops.retention.cleanup","course_run",run.id,{deleted:fileIds.length,file_ids:fileIds});
  return {ok:true,deleted:fileIds.length};
}

async function healthSnapshot(ctx:any,run:any){
  requireTeacher(ctx);
  const now=Date.now(),nowIso=new Date(now).toISOString(),since24=new Date(now-24*3600_000).toISOString(),
    legacyPersistentCutoff=new Date(now-30*24*3600_000).toISOString(),
    legacyTemporaryCutoff=new Date(now-24*3600_000).toISOString(),
    orphanCutoff=new Date(now-24*3600_000).toISOString();
  const assignmentIds=await runAssignmentIds(run);
  const [
    explicitSessionsQ,legacyPersistentQ,legacyTemporaryQ,
    loginTotalQ,loginFailedQ,snapshotQ,eventQ,realtimeQ,orphanQ
  ]=await Promise.all([
    db.from("lms_auth_sessions").select("id",{count:"exact",head:true}).is("revoked_at",null).gt("expires_at",nowIso),
    db.from("lms_auth_sessions").select("id",{count:"exact",head:true}).is("revoked_at",null).is("expires_at",null).eq("persistent",true).gte("created_at",legacyPersistentCutoff),
    db.from("lms_auth_sessions").select("id",{count:"exact",head:true}).is("revoked_at",null).is("expires_at",null).eq("persistent",false).gte("created_at",legacyTemporaryCutoff),
    db.from("lms_login_attempts").select("id",{count:"exact",head:true}).gte("created_at",since24),
    db.from("lms_login_attempts").select("id",{count:"exact",head:true}).gte("created_at",since24).eq("ok",false),
    db.from("lms_audit_log").select("created_at,action,metadata").in("action",["bigdata.ops.snapshot.auto","bigdata.ops.snapshot.export","bigdata.ops.backup.export"])
      .eq("entity_id",run.id).order("created_at",{ascending:false}).limit(1),
    db.from("bd_lms_events").select("created_at",{count:"exact"}).eq("course_run_id",run.id).gte("created_at",since24).order("created_at",{ascending:false}).limit(1),
    db.from("bd_realtime_signals").select("created_at,scope",{count:"exact"}).eq("course_code",COURSE).gte("created_at",since24).order("created_at",{ascending:false}).limit(1),
    assignmentIds.length
      ?db.from("lms_submission_files_v2").select("id",{count:"exact",head:true}).in("assignment_id",assignmentIds).in("status",["pending","abandoned"]).lt("created_at",orphanCutoff)
      :Promise.resolve({count:0,error:null} as any)
  ]);
  for(const [label,q] of [
    ["sesiones con vencimiento",explicitSessionsQ],["sesiones legacy persistentes",legacyPersistentQ],
    ["sesiones legacy temporales",legacyTemporaryQ],["intentos login",loginTotalQ],["fallos login",loginFailedQ],
    ["snapshot académico",snapshotQ],["eventos",eventQ],["Realtime",realtimeQ],["retención",orphanQ]
  ] as any[]){
    if(q?.error)throw new Error("No se pudo consultar "+label+": "+String(q.error.message||q.error));
  }
  const activeSessions=Number(explicitSessionsQ.count||0)+Number(legacyPersistentQ.count||0)+Number(legacyTemporaryQ.count||0);
  const total=Number(loginTotalQ.count||0),failed=Number(loginFailedQ.count||0);
  const lastSnapshotRow=snapshotQ.data?.[0]||null,lastSnapshot=lastSnapshotRow?.created_at||null,
    snapshotAge=lastSnapshot?Math.max(0,(now-Date.parse(lastSnapshot))/3600_000):null,
    snapshotRecent=snapshotAge!==null&&snapshotAge<=RPO_HOURS,
    snapshotMode=lastSnapshotRow?.action==="bigdata.ops.snapshot.auto"?"automatic":"manual";
  const lastAcademic=eventQ.data?.[0]?.created_at||null,lastRealtime=realtimeQ.data?.[0]?.created_at||null;
  return {
    generated_at:new Date(now).toISOString(),
    overall:snapshotRecent?"ok":"attention",
    database:{status:"ok",note:"La Edge Function respondió y pudo consultar PostgreSQL."},
    auth:{active_sessions:activeSessions,login_attempts_24h:total,failed_logins_24h:failed,failure_rate_pct:total?Math.round(failed/total*1000)/10:0},
    academic:{events_24h:Number(eventQ.count||0),last_event_at:lastAcademic},
    realtime:{signals_24h:Number(realtimeQ.count||0),last_signal_at:lastRealtime},
    retention:{orphan_candidates_24h:Number(orphanQ.count||0)},
    recovery:{
      rpo_hours:RPO_HOURS,rto_hours:RTO_HOURS,
      platform_backup_status:"not_observed_by_lms",
      last_academic_snapshot_at:lastSnapshot,
      academic_snapshot_age_hours:snapshotAge===null?null:Math.round(snapshotAge*10)/10,
      academic_snapshot_recent:snapshotRecent,
      academic_snapshot_target_hours:RPO_HOURS,
      academic_snapshot_mode:lastSnapshot?snapshotMode:null,
      academic_snapshot_path:lastSnapshotRow?.metadata?.path||null,
      automatic_snapshot_retention_days:SNAPSHOT_RETENTION_DAYS
    }
  };
}

async function overview(ctx:any,run:any){
  requireTeacher(ctx);
  const assignmentIds=await runAssignmentIds(run);
  let files:any[]=[];
  if(assignmentIds.length){
    const {data,error}=await db.from("lms_submission_files_v2").select("id,status,size_bytes,created_at").in("assignment_id",assignmentIds);
    if(error)throw error;files=data||[];
  }
  const byStatus:Record<string,number>={};for(const f of files)byStatus[f.status]=(byStatus[f.status]||0)+1;
  return {
    viewer:ctx.user,
    run:{id:run.id,code:run.code,title:run.title},
    academic_snapshot:{format:"bigdata-lms-academic-snapshot",version:BACKUP_VERSION,includes_binary_files:false,platform_backup_equivalent:false},
    files:{total:files.length,total_bytes:files.reduce((a:number,x:any)=>a+Number(x.size_bytes||0),0),by_status:byStatus},
    health:await healthSnapshot(ctx,run),
    capabilities:roleCapabilities(ctx.user.role),
    policies:{
      login_rate_limit:"8 fallos por combinación IP+cuenta en 15 min; desde 6 fallos globales de cuenta se aplica retardo progresivo sin bloqueo global.",
      retention_preview_min_hours:24,
      cleanup_role:"admin",
      attached_files_deletable:false,
      session_ttl_hours:SESSION_TTL_HOURS,
      rpo_hours:RPO_HOURS,
      rto_hours:RTO_HOURS,
      academic_snapshot_target_hours:RPO_HOURS,
      platform_backup_status:"not_observed_by_lms"
    }
  };
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);

  let action="overview",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"overview";
  else{
    try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
    action=String(body.action||"overview");
  }

  if(action==="scheduled_snapshot"){
    if(req.method!=="POST")return out(req,{error:"Método no permitido"},405);
    if(!(await snapshotCronAuthorized(req)))return out(req,{error:"Scheduler no autorizado"},403);
    try{return out(req,await scheduledSnapshot())}
    catch(e){return out(req,{error:String((e as any)?.message||e).slice(0,500)},500)}
  }

  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  try{
    if(action==="overview")return out(req,await overview(ctx,run));
    if(action==="health")return out(req,{viewer:ctx.user,health:await healthSnapshot(ctx,run),capabilities:roleCapabilities(ctx.user.role)});
    if(action==="export_backup")return out(req,await exportBackup(ctx,run));
    if(action==="retention_preview")return out(req,await retentionPreview(ctx,run,body));
    if(action==="retention_cleanup")return out(req,await cleanupRetention(ctx,run,body));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    const m=String((e as any)?.message||e);
    if(m==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    if(m==="ADMIN_ONLY")return out(req,{error:"Esta operación requiere rol admin"},403);
    return out(req,{error:m.slice(0,500)},400);
  }
});
