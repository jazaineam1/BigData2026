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
  const {data:s}=await db.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent")
    .eq("token_hash",await sha256(token)).is("revoked_at",null).maybeSingle();
  if(!s)return null;if(!s.persistent&&(!s.expires_at||Date.parse(s.expires_at)<=Date.now()))return null;
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
async function audit(actor:string,action:string,entity:string,id:string|null,metadata:any={}){
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

async function exportBackup(ctx:any,run:any){
  requireTeacher(ctx);
  const data=await backupData(run);
  const dataJson=JSON.stringify(data);
  const fileRows=data.lms_submission_files_v2||[];
  const manifest={
    format:"bigdata-lms-academic-snapshot",
    version:BACKUP_VERSION,
    course_code:COURSE,
    run_code:RUN_CODE,
    course_run_id:run.id,
    generated_at:new Date().toISOString(),
    generated_by:ctx.user.id,
    sha256:await sha256(dataJson),
    table_counts:counts(data),
    storage_files:fileRows.length,
    storage_bytes:fileRows.reduce((a:number,x:any)=>a+Number(x.size_bytes||0),0),
    includes_binary_files:false,
    excludes:["password_hash","Supabase Auth secrets","Edge Function secrets","binary Storage objects"]
  };
  await audit(ctx.user.id,"bigdata.ops.backup.export","course_run",run.id,{tables:Object.keys(data).length,storage_files:manifest.storage_files});
  return {ok:true,manifest,data,warnings:[
    "Este snapshot respalda datos académicos y metadatos de archivos; no incluye binarios de Storage.",
    "No contiene password_hash ni secretos de autenticación.",
    "La restauración debe seguir el runbook y realizarse en una ventana controlada."
  ]};
}

async function runAssignmentIds(run:any){return ids(await eqRows("lms_assignments_v2","course_run_id",run.id))}
async function retentionPreview(ctx:any,run:any,body:any={}){
  requireTeacher(ctx);
  const hours=Math.max(24,Math.min(24*90,Number(body.older_than_hours||24)));
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
    .select("id,assignment_id,bucket,object_path,status,created_at")
    .in("id",fileIds).in("assignment_id",assignmentIds)
    .in("status",["pending","abandoned"])
    .lt("created_at",cutoff);
  if(error)throw error;
  const rows=data||[];
  if(rows.length!==fileIds.length)throw new Error("Uno o más archivos ya no son candidatos seguros para limpieza");
  if(rows.some((x:any)=>x.status==="attached"))throw new Error("Nunca se eliminan archivos attached");

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
    backup:{format:"bigdata-lms-academic-snapshot",version:BACKUP_VERSION,includes_binary_files:false},
    files:{total:files.length,total_bytes:files.reduce((a:number,x:any)=>a+Number(x.size_bytes||0),0),by_status:byStatus},
    policies:{
      login_rate_limit:"8 fallos / 15 min en learning-auth compartido",
      retention_preview_min_hours:24,
      cleanup_role:"admin",
      attached_files_deletable:false
    }
  };
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  let action="overview",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"overview";
  else{try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}action=String(body.action||"overview")}
  try{
    if(action==="overview")return out(req,await overview(ctx,run));
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