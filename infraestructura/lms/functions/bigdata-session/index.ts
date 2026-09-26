import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);

const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const TRACK_EVENTS=new Set([
  "session_entered","page_opened","page_closed","heartbeat",
  "resource_opened","resource_completed","presentation_opened","notebook_opened","guide_opened",
  "lab_started","checkpoint_started","slide_viewed","ui_action",
  "evidence_submitted","evidence_verified","session_completed"
]);

function origin(req:Request){
  const o=req.headers.get("origin");if(!o)return "";
  if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;
  return null;
}
function headers(req:Request){
  const o=origin(req);
  return {
    "Access-Control-Allow-Origin":o||"https://jazaineam1.github.io",
    "Access-Control-Allow-Headers":"authorization, content-type",
    "Access-Control-Allow-Methods":"GET, POST, OPTIONS",
    "Vary":"Origin","Cache-Control":"no-store","X-Content-Type-Options":"nosniff",
    "Referrer-Policy":"strict-origin-when-cross-origin"
  };
}
function out(req:Request,body:unknown,status=200){
  return new Response(JSON.stringify(body),{status,headers:{...headers(req),"Content-Type":"application/json"}});
}
function bearer(req:Request){
  const h=req.headers.get("authorization")||"";
  return h.toLowerCase().startsWith("bearer ")?h.slice(7).trim():"";
}
async function sha256(text:string){
  const d=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text));
  return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,"0")).join("");
}
function sessionNumber(v:any){
  const n=Math.trunc(Number(v));
  if(!Number.isInteger(n)||n<1||n>99)throw new Error("Número de sesión inválido");
  return n;
}
function cleanMeta(raw:any){
  const x=raw&&typeof raw==="object"?raw:{},z:Record<string,string|number|boolean|null>={};
  for(const k of ["source","action","label","path","resource_type","resource_id","slide","chapter","outcome"]){
    const v=x[k];
    if(typeof v==="string")z[k]=v.slice(0,240);
    else if(typeof v==="number"||typeof v==="boolean"||v===null)z[k]=v;
  }
  return z;
}
async function current(req:Request){
  const token=bearer(req);if(!token)return null;
  const {data:s}=await db.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent")
    .eq("token_hash",await sha256(token)).is("revoked_at",null).maybeSingle();
  if(!s)return null;
  if(!s.persistent&&(!s.expires_at||Date.parse(s.expires_at)<=Date.now()))return null;
  const {data:u}=await db.from("lms_users").select("id,username,display_name,role,active,email")
    .eq("id",s.user_id).eq("active",true).maybeSingle();
  return u?{session:s,user:u}:null;
}
async function activeRun(ctx:any){
  const {data:memberships}=await db.from("lms_run_enrollments").select("course_run_id,role,status,enrolled_at")
    .eq("user_id",ctx.user.id).eq("status","active").order("enrolled_at",{ascending:false});
  for(const m of memberships||[]){
    const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,starts_on,ends_on,active")
      .eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:m.role};
  }
  if(["teacher","admin"].includes(ctx.user.role)){
    const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,starts_on,ends_on,active")
      .eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:ctx.user.role};
  }
  return null;
}
function requireTeacher(ctx:any){
  if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH");
}
async function audit(actor:string,action:string,entity:string,id:string|null,metadata:any={}){
  await db.from("lms_audit_log").insert({
    actor_user_id:actor,action,entity_type:entity,entity_id:id,
    metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}
  }).then(()=>{}).catch(()=>{});
}
async function definition(runId:string,n:number,teacher=false){
  const [{data:session},{data:activities},{data:resources}]=await Promise.all([
    db.from("lms_run_sessions_v2").select("*").eq("course_run_id",runId).eq("session_number",n).maybeSingle(),
    db.from("bd_lms_activities").select("*").eq("course_code",COURSE).eq("session_number",n).order("position"),
    db.from("lms_run_resources_v2").select("id,session_number,resource_type,title,summary,url,position,metadata")
      .eq("course_run_id",runId).eq("session_number",n).eq("visible",true).order("position")
  ]);
  if(!session)throw new Error("Sesión no configurada");
  if(session.status==="draft"&&!teacher)throw new Error("Sesión todavía no publicada");
  return {session,activities:activities||[],resources:resources||[]};
}
async function sessionWindow(runId:string,n:number){
  const {data}=await db.from("bd_lms_session_windows").select("opened_at,opened_by")
    .eq("course_run_id",runId).eq("session_number",n).maybeSingle();
  return data||null;
}
async function ownProgress(userId:string,runId:string,n:number,codes:string[]){
  const activityQuery=codes.length
    ?db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).in("activity_code",codes).order("activity_code")
    :Promise.resolve({data:[]} as any);
  const [{data:session_progress},{data:activity_progress},{data:lastSlide},window]=await Promise.all([
    db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n).maybeSingle(),
    activityQuery,
    db.from("bd_lms_events").select("metadata,created_at").eq("user_id",userId).eq("course_run_id",runId)
      .eq("session_number",n).eq("event_type","slide_viewed").order("created_at",{ascending:false}).limit(1).maybeSingle(),
    sessionWindow(runId,n)
  ]);
  const meta=(lastSlide?.metadata&&typeof lastSlide.metadata==="object")?lastSlide.metadata:{};
  const slide=Number(meta.slide||0);
  const resume=slide>0?{slide,label:String(meta.label||""),chapter:String(meta.chapter||""),at:lastSlide?.created_at||null}:null;
  return {session_progress,activity_progress:activity_progress||[],session_window:window,resume};
}
function activitySummary(activities:any[],progress:any[]){
  const pm=new Map((progress||[]).map((x:any)=>[x.activity_code,x]));
  const resources=activities.filter(a=>a.kind==="resource");
  const checkpoints=activities.filter(a=>a.kind==="checkpoint");
  const required=activities.filter(a=>a.required);
  const visitedResources=resources.filter(a=>pm.has(a.code)).length;
  const mastered=checkpoints.filter(a=>Boolean(pm.get(a.code)?.metadata?.mastery)||pm.get(a.code)?.status==="completed").length;
  const completed=required.filter(a=>pm.get(a.code)?.status==="completed").length;
  const attempted=activities.filter(a=>pm.has(a.code)).length;
  return {
    total_activities:activities.length,
    required_activities:required.length,
    attempted,
    completed,
    resource_visited:visitedResources,
    resource_total:resources.length,
    checkpoint_mastered:mastered,
    checkpoint_total:checkpoints.length
  };
}
async function ensureSessionStarted(userId:string,runId:string,n:number,maxScore=0){
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_session_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n).maybeSingle();
  if(!p){
    await db.from("bd_lms_session_progress").insert({
      user_id:userId,course_run_id:runId,session_number:n,status:"in_progress",
      started_at:now,active_seconds:0,last_activity_at:now,score:0,max_score:maxScore,updated_at:now
    });
    return;
  }
  await db.from("bd_lms_session_progress").update({
    status:p.status==="completed"?"completed":"in_progress",
    last_activity_at:now,max_score:Math.max(Number(p.max_score||0),maxScore),updated_at:now
  }).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n);
}
async function touchActivity(userId:string,runId:string,activity:any,source:string,complete=false){
  const code=activity.code,now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code).maybeSingle();
  const metadata={...(p?.metadata||{}),source,visited:true,last_event:source};
  const status=complete||p?.status==="completed"?"completed":"in_progress";
  await db.from("bd_lms_activity_progress").upsert({
    user_id:userId,course_run_id:runId,activity_code:code,status,
    started_at:p?.started_at||now,attempts:Number(p?.attempts||0)+1,
    score:Number(p?.score||0),max_score:Number(p?.max_score||activity.points||0),
    completed_at:status==="completed"?(p?.completed_at||now):null,updated_at:now,metadata
  },{onConflict:"user_id,course_run_id,activity_code"});
}
async function heartbeat(userId:string,runId:string,n:number,delta:number){
  const {data:p}=await db.from("bd_lms_session_progress").select("active_seconds")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n).maybeSingle();
  if(!p)return;
  const now=new Date().toISOString();
  await db.from("bd_lms_session_progress").update({
    active_seconds:Number(p.active_seconds||0)+delta,last_activity_at:now,updated_at:now
  }).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n);
}
async function recomputeSession(userId:string,runId:string,n:number,activities:any[]){
  const checkpoints=activities.filter(a=>a.kind==="checkpoint"&&a.required);
  const codes=activities.map(a=>a.code);
  const {data:rows}=codes.length
    ?await db.from("bd_lms_activity_progress").select("activity_code,status,metadata").eq("user_id",userId).eq("course_run_id",runId).in("activity_code",codes)
    :({data:[]} as any);
  const pm=new Map((rows||[]).map((x:any)=>[x.activity_code,x]));
  const mastered=checkpoints.filter(a=>Boolean(pm.get(a.code)?.metadata?.mastery)||pm.get(a.code)?.status==="completed").length;
  const done=checkpoints.length>0&&mastered===checkpoints.length;
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_session_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n).maybeSingle();
  await db.from("bd_lms_session_progress").upsert({
    user_id:userId,course_run_id:runId,session_number:n,
    status:done?"completed":(p?.status==="completed"?"completed":"in_progress"),
    started_at:p?.started_at||now,active_seconds:Number(p?.active_seconds||0),
    last_activity_at:now,completed_at:done?(p?.completed_at||now):(p?.completed_at||null),
    score:mastered,max_score:checkpoints.length,updated_at:now
  },{onConflict:"user_id,course_run_id,session_number"});
  return {completed:mastered,total:checkpoints.length,done};
}
async function answerChallenge(ctx:any,run:any,n:number,code:string,rawAnswer:any,activities:any[]){
  const activity=activities.find((a:any)=>a.code===code&&a.kind==="checkpoint");
  if(!activity)throw new Error("Desafío no válido");
  const answer=String(rawAnswer||"").trim().slice(0,160);if(!answer)throw new Error("Respuesta vacía");
  const {data:key}=await db.from("bd_lms_activity_keys").select("answer_hash,hint,session_number")
    .eq("activity_code",code).eq("session_number",n).maybeSingle();
  if(!key)throw new Error("Este checkpoint no tiene validación automática configurada");
  const correct=await sha256(code+"|"+answer)===key.answer_hash;
  await ensureSessionStarted(ctx.user.id,run.id,n,activities.filter(a=>a.kind==="checkpoint"&&a.required).length);
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("activity_code",code).maybeSingle();
  const previousMeta=(p?.metadata&&typeof p.metadata==="object")?p.metadata:{};
  const attempts=Number(p?.attempts||0)+1;
  const firstAttempt=typeof previousMeta.first_attempt_correct==="boolean"?previousMeta.first_attempt_correct:correct;
  const mastery=Boolean(previousMeta.mastery)||correct;
  await db.from("bd_lms_activity_progress").upsert({
    user_id:ctx.user.id,course_run_id:run.id,activity_code:code,
    status:mastery?"completed":"in_progress",started_at:p?.started_at||now,
    attempts,score:mastery?Number(activity.points||1):0,max_score:Number(activity.points||1),
    completed_at:mastery?(p?.completed_at||now):null,updated_at:now,
    metadata:{...previousMeta,source:"lms-formative-challenge",formative:true,first_attempt_correct:firstAttempt,mastery,last_attempt_correct:correct}
  },{onConflict:"user_id,course_run_id,activity_code"});
  await db.from("bd_lms_events").insert({
    user_id:ctx.user.id,course_run_id:run.id,event_type:"challenge_answered",
    session_number:n,activity_code:code,
    metadata:{correct,attempt:attempts,first_attempt_correct:firstAttempt,mastery},created_at:now
  });
  const summary=await recomputeSession(ctx.user.id,run.id,n,activities);
  return {ok:true,correct,attempts,first_attempt_correct:firstAttempt,mastery,hint:correct?null:key.hint,...summary};
}
async function openOfficial(ctx:any,run:any,n:number){
  requireTeacher(ctx);
  const existing=await sessionWindow(run.id,n);if(existing)return existing;
  const now=new Date().toISOString();
  const {data,error}=await db.from("bd_lms_session_windows").insert({
    course_run_id:run.id,session_number:n,opened_at:now,opened_by:ctx.user.id
  }).select("opened_at,opened_by").single();
  if(!error&&data)return data;
  const retry=await sessionWindow(run.id,n);if(retry)return retry;
  throw error||new Error("No se pudo fijar el inicio oficial");
}
async function teacherWall(ctx:any,run:any,n:number){
  requireTeacher(ctx);
  const def=await definition(run.id,n,true),codes=def.activities.map((a:any)=>a.code);
  const activityQuery=codes.length
    ?db.from("bd_lms_activity_progress").select("*").eq("course_run_id",run.id).in("activity_code",codes)
    :Promise.resolve({data:[]} as any);
  const [{data:enrollments},{data:progress},{data:activityProgress},{data:events},window]=await Promise.all([
    db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id).eq("status","active"),
    db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",n),
    activityQuery,
    db.from("bd_lms_events").select("user_id,event_type,activity_code,metadata,created_at").eq("course_run_id",run.id)
      .eq("session_number",n).order("created_at",{ascending:false}).limit(5000),
    sessionWindow(run.id,n)
  ]);
  const ids=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const {data:users}=ids.length?await db.from("lms_users").select("id,display_name,username,active").in("id",ids):({data:[]} as any);
  const pm=new Map((progress||[]).map((x:any)=>[x.user_id,x])),byUser=new Map<string,any[]>(),lastEvent=new Map<string,any>(),lastSlide=new Map<string,any>();
  for(const a of activityProgress||[]){if(!byUser.has(a.user_id))byUser.set(a.user_id,[]);byUser.get(a.user_id)!.push(a)}
  for(const e of events||[]){if(!lastEvent.has(e.user_id))lastEvent.set(e.user_id,e);if(e.event_type==="slide_viewed"&&!lastSlide.has(e.user_id))lastSlide.set(e.user_id,e)}
  const checkpoints=def.activities.filter((a:any)=>a.kind==="checkpoint");
  const rows=(users||[]).map((u:any)=>{
    const p:any=pm.get(u.id)||{},aps=byUser.get(u.id)||[],am=new Map(aps.map((x:any)=>[x.activity_code,x]));
    const mastered=checkpoints.filter((a:any)=>Boolean(am.get(a.code)?.metadata?.mastery)||am.get(a.code)?.status==="completed").length;
    const attempted=aps.length;
    const ev:any=lastEvent.get(u.id),slideEv:any=lastSlide.get(u.id),slideMeta=slideEv?.metadata||{};
    const lastAt=p.last_activity_at||ev?.created_at||null;
    const age=lastAt?(Date.now()-Date.parse(lastAt))/60000:null;
    const needsAttention=aps.some((a:any)=>a.attempts>0&&a.metadata?.mastery===false)||(p.started_at&&age!==null&&age>20&&p.status!=="completed");
    return {
      user_id:u.id,display_name:u.display_name||u.username,
      status:p.status||"not_started",started_at:p.started_at||null,
      active_seconds:Number(p.active_seconds||0),last_activity_at:lastAt,
      current_activity:ev?.activity_code||null,current_event:ev?.event_type||null,
      needs_attention:needsAttention,attempted_activities:attempted,
      completed_activities:aps.filter((a:any)=>a.status==="completed").length,
      mastered_checkpoints:mastered,total_checkpoints:checkpoints.length,
      last_slide:Number(slideMeta.slide||0)>0?{slide:Number(slideMeta.slide),label:String(slideMeta.label||""),chapter:String(slideMeta.chapter||""),at:slideEv.created_at}:null,
      activities:def.activities.map((a:any)=>{
        const x:any=am.get(a.code)||{},m=x.metadata||{};
        return {code:a.code,title:a.title,kind:a.kind,status:x.status||"not_started",attempts:Number(x.attempts||0),
          first_attempt_correct:typeof m.first_attempt_correct==="boolean"?m.first_attempt_correct:null,mastery:Boolean(m.mastery),
          started_at:x.started_at||null,completed_at:x.completed_at||null};
      })
    };
  }).sort((a:any,b:any)=>(a.display_name||"").localeCompare(b.display_name||"","es"));
  const activity_stats=def.activities.map((a:any)=>{
    const xs=rows.map((r:any)=>r.activities.find((x:any)=>x.code===a.code)).filter(Boolean);
    return {code:a.code,title:a.title,kind:a.kind,started:xs.filter((x:any)=>x.status!=="not_started").length,
      completed:xs.filter((x:any)=>x.status==="completed").length,
      attempted:xs.filter((x:any)=>x.attempts>0).length,
      first_attempt_correct:xs.filter((x:any)=>x.first_attempt_correct===true).length,
      mastered:xs.filter((x:any)=>x.mastery===true).length};
  });
  return {viewer:ctx.user,run,...def,session_window:window,students:rows,ranking:rows,activity_stats,challenge_stats:activity_stats.filter((x:any)=>x.kind==="checkpoint"),refreshed_at:new Date().toISOString()};
}
async function teacherStudentDetail(ctx:any,run:any,n:number,userId:string){
  requireTeacher(ctx);
  if(!/^[0-9a-f-]{36}$/i.test(userId))throw new Error("Estudiante inválido");
  const {data:enrollment}=await db.from("lms_run_enrollments").select("user_id,role,status")
    .eq("course_run_id",run.id).eq("user_id",userId).eq("role","student").eq("status","active").maybeSingle();
  if(!enrollment)throw new Error("Estudiante no pertenece a esta cohorte");
  const def=await definition(run.id,n,true),codes=def.activities.map((a:any)=>a.code);
  const [{data:user},{data:session_progress},{data:activity_progress},{data:events}]=await Promise.all([
    db.from("lms_users").select("id,display_name,username,active").eq("id",userId).maybeSingle(),
    db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",run.id).eq("session_number",n).maybeSingle(),
    codes.length?db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",run.id).in("activity_code",codes).order("updated_at",{ascending:false}):Promise.resolve({data:[]} as any),
    db.from("bd_lms_events").select("event_type,activity_code,metadata,client_at,created_at").eq("user_id",userId).eq("course_run_id",run.id).eq("session_number",n).order("created_at",{ascending:false}).limit(250)
  ]);
  return {viewer:ctx.user,run,session:def.session,user,session_progress,activity_progress:activity_progress||[],events:events||[],activities:def.activities};
}

async function resetSession(ctx:any,run:any,n:number,body:any){
  requireTeacher(ctx);
  const phrase="REINICIAR_S"+String(n).padStart(2,"0");
  if(String(body.confirmation||"")!==phrase)throw new Error("Confirmación de reinicio inválida");
  const def=await definition(run.id,n,true),codes=def.activities.map((a:any)=>a.code);
  const [{data:progress},{data:activity},{data:events},{data:window}]=await Promise.all([
    db.from("bd_lms_session_progress").select("user_id").eq("course_run_id",run.id).eq("session_number",n),
    codes.length?db.from("bd_lms_activity_progress").select("user_id,activity_code").eq("course_run_id",run.id).in("activity_code",codes):Promise.resolve({data:[]} as any),
    db.from("bd_lms_events").select("id").eq("course_run_id",run.id).eq("session_number",n),
    db.from("bd_lms_session_windows").select("course_run_id").eq("course_run_id",run.id).eq("session_number",n)
  ]);
  const counts={session_progress:(progress||[]).length,activity_progress:(activity||[]).length,events:(events||[]).length,session_window:(window||[]).length};
  const deletes:any[]=[
    await db.from("bd_lms_events").delete().eq("course_run_id",run.id).eq("session_number",n),
    await db.from("bd_lms_session_progress").delete().eq("course_run_id",run.id).eq("session_number",n),
    await db.from("bd_lms_session_windows").delete().eq("course_run_id",run.id).eq("session_number",n)
  ];
  if(codes.length)deletes.push(await db.from("bd_lms_activity_progress").delete().eq("course_run_id",run.id).in("activity_code",codes));
  const failed=deletes.find((x:any)=>x.error);if(failed?.error)throw failed.error;
  await audit(ctx.user.id,"bigdata.session.reset","course_run",run.id,{session_number:n,counts});
  return {ok:true,counts,confirmation:phrase};
}
async function courseProgress(ctx:any,run:any){
  const [{data:sessions},{data:resources},{data:sessionProgress},{data:activities},{data:activityProgress}]=await Promise.all([
    db.from("lms_run_sessions_v2").select("*").eq("course_run_id",run.id).neq("status","draft").order("position"),
    db.from("lms_run_resources_v2").select("id,session_number,resource_type,title,url,position,metadata").eq("course_run_id",run.id).eq("visible",true).order("position"),
    db.from("bd_lms_session_progress").select("*").eq("user_id",ctx.user.id).eq("course_run_id",run.id).order("session_number"),
    db.from("bd_lms_activities").select("*").eq("course_code",COURSE).order("session_number").order("position"),
    db.from("bd_lms_activity_progress").select("*").eq("user_id",ctx.user.id).eq("course_run_id",run.id)
  ]);
  const pm=new Map((sessionProgress||[]).map((x:any)=>[Number(x.session_number),x]));
  const apm=new Map((activityProgress||[]).map((x:any)=>[x.activity_code,x]));
  const rows=(sessions||[]).map((s:any)=>{
    const defs=(activities||[]).filter((a:any)=>Number(a.session_number)===Number(s.session_number));
    const prog=defs.map((a:any)=>apm.get(a.code)).filter(Boolean);
    return {...s,session_progress:pm.get(Number(s.session_number))||null,summary_metrics:activitySummary(defs,prog),
      resources:(resources||[]).filter((r:any)=>Number(r.session_number)===Number(s.session_number)),
      activities:defs.map((a:any)=>({...a,progress:apm.get(a.code)||null}))};
  });
  return {viewer:ctx.user,run,sessions:rows,generated_at:new Date().toISOString()};
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  let action="me",body:any={},n=0;
  if(req.method==="GET"){
    const u=new URL(req.url);action=u.searchParams.get("action")||"me";
    if(action!=="course_progress")n=sessionNumber(u.searchParams.get("session_number")||u.searchParams.get("s"));
  }else{
    try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
    action=String(body.action||"me");
    if(action!=="course_progress")n=sessionNumber(body.session_number);
  }
  try{
    if(action==="course_progress")return out(req,await courseProgress(ctx,run));
    const teacher=["teacher_wall","teacher_open_session","teacher_reset_session"].includes(action);
    const def=await definition(run.id,n,teacher),codes=def.activities.map((a:any)=>a.code);
    if(action==="me"){
      const p=await ownProgress(ctx.user.id,run.id,n,codes);
      return out(req,{viewer:ctx.user,run,...def,...p,summary:activitySummary(def.activities,p.activity_progress)});
    }
    if(action==="track"){
      const event=String(body.event_type||"");if(!TRACK_EVENTS.has(event))throw new Error("Evento no permitido");
      const activityCode=body.activity_code?String(body.activity_code):null;
      const activity=activityCode?def.activities.find((a:any)=>a.code===activityCode):null;
      if(activityCode&&!activity)throw new Error("Actividad no válida para esta sesión");
      const delta=event==="heartbeat"?Math.max(0,Math.min(30,Math.round(Number(body.active_seconds_delta||0)))):0;
      const now=new Date().toISOString();
      await db.from("bd_lms_events").insert({
        user_id:ctx.user.id,course_run_id:run.id,event_type:event,session_number:n,
        activity_code:activityCode,active_seconds_delta:delta,metadata:cleanMeta(body.metadata),
        client_at:body.client_at?String(body.client_at):null,created_at:now
      });
      if(event==="heartbeat")await heartbeat(ctx.user.id,run.id,n,delta);
      else{
        await ensureSessionStarted(ctx.user.id,run.id,n,def.activities.filter((a:any)=>a.kind==="checkpoint"&&a.required).length);
        if(activity){
          const complete=event==="resource_completed"||event==="evidence_verified"||event==="session_completed";
          await touchActivity(ctx.user.id,run.id,activity,event,complete);
        }
      }
      return out(req,{ok:true});
    }
    if(action==="answer_challenge")return out(req,await answerChallenge(ctx,run,n,String(body.activity_code||""),body.answer,def.activities));
    if(action==="teacher_open_session")return out(req,{ok:true,session_window:await openOfficial(ctx,run,n)});
    if(action==="teacher_reset_session")return out(req,await resetSession(ctx,run,n,body));
    if(action==="teacher_student_detail")return out(req,await teacherStudentDetail(ctx,run,n,String(body.user_id||"")));
    if(action==="teacher_wall")return out(req,await teacherWall(ctx,run,n));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});