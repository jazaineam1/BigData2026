import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);

const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const SESSION=9;
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const RESOURCE_CODES=new Set(["bd-s09-presentation","bd-s09-notebook"]);
const CHECKPOINT_CODES=new Set(["bd-s09-c1","bd-s09-c2","bd-s09-c3","bd-s09-c4","bd-s09-c5"]);
const CHALLENGE_HASHES:Record<string,string>={
  "bd-s09-c1":"527bbe6e343018a39e6e78ba0fc39e8c8d67d88e9dbe2ab7d52f6215501e9892",
  "bd-s09-c2":"6e65ee7bd666203cba62114ae0e43eb002dfe01315969773ced9608543eab77f",
  "bd-s09-c3":"701c258052172c1ffcdede204b508111671a980c9101b561ea8d88b021a255ba",
  "bd-s09-c4":"b31e961d21cdf1676df29fa87555cc14edbddfc3b2dcc2a8889dcec440e97956",
  "bd-s09-c5":"e92de32e71f3f3ed64f76dca618fdaefc1bc78e9a349cd7c7731a9d224ef9929"
};
const CHALLENGE_HINTS:Record<string,string>={
  "bd-s09-c1":"Piensa si la necesidad exige coincidencia exacta o puede tolerar paráfrasis.",
  "bd-s09-c2":"El coseno describe cercanía geométrica; no es una probabilidad calibrada.",
  "bd-s09-c3":"Dos rankings se comparan contra juicios de relevancia, no por quién produce el número mayor.",
  "bd-s09-c4":"Separa quién transforma texto en vector de quién lo almacena e indexa.",
  "bd-s09-c5":"RRF trabaja con posiciones de ranking para no asumir que BM25 y coseno comparten escala."
};
const ALL_CODES=new Set([...RESOURCE_CODES,...CHECKPOINT_CODES]);
const TRACK_EVENTS=new Set([
  "page_opened","page_closed","heartbeat",
  "presentation_opened","notebook_opened",
  "checkpoint_started","ui_action"
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
function cleanMeta(raw:any){
  const x=raw&&typeof raw==="object"?raw:{},z:Record<string,string|number|boolean|null>={};
  for(const k of ["source","action","label","path","resource_type"]){
    const v=x[k];
    if(typeof v==="string")z[k]=v.slice(0,180);
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
    const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,active")
      .eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:m.role};
  }
  if(["teacher","admin"].includes(ctx.user.role)){
    const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,active")
      .eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:ctx.user.role};
  }
  return null;
}
function requireTeacher(ctx:any){
  if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH");
}
async function definition(runId:string){
  const [{data:session},{data:activities},{data:resources}]=await Promise.all([
    db.from("bd_lms_sessions").select("*").eq("course_code",COURSE).eq("session_number",SESSION).maybeSingle(),
    db.from("bd_lms_activities").select("*").eq("course_code",COURSE).eq("session_number",SESSION).order("position"),
    db.from("lms_run_resources_v2").select("id,resource_type,title,summary,url,position,metadata")
      .eq("course_run_id",runId).eq("session_number",SESSION).eq("visible",true).order("position")
  ]);
  if(!session)throw new Error("S09 aún no está configurada en el LMS");
  return {session,activities:activities||[],resources:resources||[]};
}
async function sessionWindow(runId:string){
  const {data}=await db.from("bd_lms_session_windows").select("opened_at,opened_by")
    .eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
  return data||null;
}
async function ownProgress(userId:string,runId:string){
  const [{data:session_progress},{data:activity_progress},window]=await Promise.all([
    db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle(),
    db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).in("activity_code",[...ALL_CODES]).order("activity_code"),
    sessionWindow(runId)
  ]);
  return {session_progress,activity_progress:activity_progress||[],session_window:window};
}
async function ensureSessionStarted(userId:string,runId:string){
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_session_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
  if(!p){
    await db.from("bd_lms_session_progress").insert({
      user_id:userId,course_run_id:runId,session_number:SESSION,status:"in_progress",
      started_at:now,active_seconds:0,last_activity_at:now,score:0,max_score:5,updated_at:now
    });
    return;
  }
  await db.from("bd_lms_session_progress").update({
    status:p.status==="completed"?"completed":"in_progress",
    last_activity_at:now,updated_at:now
  }).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION);
}
async function touchActivity(userId:string,runId:string,code:string,source:string){
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code).maybeSingle();
  if(!p){
    await db.from("bd_lms_activity_progress").insert({
      user_id:userId,course_run_id:runId,activity_code:code,status:"in_progress",
      started_at:now,attempts:1,score:0,max_score:0,updated_at:now,metadata:{source}
    });
    return;
  }
  await db.from("bd_lms_activity_progress").update({
    status:p.status==="completed"?"completed":"in_progress",
    attempts:Number(p.attempts||0)+1,updated_at:now,
    metadata:{...(p.metadata||{}),source}
  }).eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code);
}
async function heartbeat(userId:string,runId:string,delta:number){
  const {data:p}=await db.from("bd_lms_session_progress").select("active_seconds")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
  if(!p)return;
  const now=new Date().toISOString();
  await db.from("bd_lms_session_progress").update({
    active_seconds:Number(p.active_seconds||0)+delta,last_activity_at:now,updated_at:now
  }).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION);
}
async function recomputeSession(userId:string,runId:string){
  const {data:rows}=await db.from("bd_lms_activity_progress").select("activity_code,status")
    .eq("user_id",userId).eq("course_run_id",runId).in("activity_code",[...CHECKPOINT_CODES]);
  const completed=(rows||[]).filter((x:any)=>x.status==="completed").length;
  const now=new Date().toISOString(),done=completed===CHECKPOINT_CODES.size;
  const {data:p}=await db.from("bd_lms_session_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
  await db.from("bd_lms_session_progress").upsert({
    user_id:userId,course_run_id:runId,session_number:SESSION,
    status:done?"completed":"in_progress",
    started_at:p?.started_at||now,active_seconds:Number(p?.active_seconds||0),
    last_activity_at:now,completed_at:done?(p?.completed_at||now):null,
    score:completed,max_score:CHECKPOINT_CODES.size,updated_at:now
  },{onConflict:"user_id,course_run_id,session_number"});
  return {completed,total:CHECKPOINT_CODES.size,done};
}
async function completeCheckpoint(ctx:any,run:any,code:string){
  if(!CHECKPOINT_CODES.has(code))throw new Error("Checkpoint no válido");
  await ensureSessionStarted(ctx.user.id,run.id);
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("activity_code",code).maybeSingle();
  await db.from("bd_lms_activity_progress").upsert({
    user_id:ctx.user.id,course_run_id:run.id,activity_code:code,status:"completed",
    started_at:p?.started_at||now,attempts:Number(p?.attempts||0),score:1,max_score:1,
    completed_at:p?.completed_at||now,updated_at:now,metadata:{source:"s09-self-checkpoint",formative:true}
  },{onConflict:"user_id,course_run_id,activity_code"});
  await db.from("bd_lms_events").insert({
    user_id:ctx.user.id,course_run_id:run.id,event_type:"checkpoint_completed",
    session_number:SESSION,activity_code:code,metadata:{formative:true},created_at:now
  });
  return {ok:true,...await recomputeSession(ctx.user.id,run.id)};
}

async function answerChallenge(ctx:any,run:any,code:string,rawAnswer:any){
  if(!CHECKPOINT_CODES.has(code))throw new Error("Desafío no válido");
  const answer=String(rawAnswer||"").trim().slice(0,100);
  if(!answer)throw new Error("Respuesta vacía");
  const expected=CHALLENGE_HASHES[code];
  const actual=await sha256(code+"|"+answer);
  const correct=actual===expected;
  await ensureSessionStarted(ctx.user.id,run.id);
  const now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("activity_code",code).maybeSingle();
  const previousMeta=(p?.metadata&&typeof p.metadata==="object")?p.metadata:{};
  const attempts=Number(p?.attempts||0)+1;
  const firstAttempt=(typeof previousMeta.first_attempt_correct==="boolean")
    ? previousMeta.first_attempt_correct
    : correct;
  const mastery=Boolean(previousMeta.mastery)||correct;
  await db.from("bd_lms_activity_progress").upsert({
    user_id:ctx.user.id,course_run_id:run.id,activity_code:code,
    status:mastery?"completed":"in_progress",
    started_at:p?.started_at||now,attempts,score:mastery?1:0,max_score:1,
    completed_at:mastery?(p?.completed_at||now):null,updated_at:now,
    metadata:{
      source:"s09-live-challenge",formative:true,
      first_attempt_correct:firstAttempt,mastery,last_attempt_correct:correct
    }
  },{onConflict:"user_id,course_run_id,activity_code"});
  await db.from("bd_lms_events").insert({
    user_id:ctx.user.id,course_run_id:run.id,event_type:"challenge_answered",
    session_number:SESSION,activity_code:code,
    metadata:{correct,attempt:attempts,first_attempt_correct:firstAttempt,mastery},
    created_at:now
  });
  const summary=await recomputeSession(ctx.user.id,run.id);
  return {ok:true,correct,attempts,first_attempt_correct:firstAttempt,mastery,hint:correct?null:CHALLENGE_HINTS[code],...summary};
}

async function openOfficial(ctx:any,run:any){
  requireTeacher(ctx);
  const existing=await sessionWindow(run.id);if(existing)return existing;
  const now=new Date().toISOString();
  const {data,error}=await db.from("bd_lms_session_windows").insert({
    course_run_id:run.id,session_number:SESSION,opened_at:now,opened_by:ctx.user.id
  }).select("opened_at,opened_by").single();
  if(!error&&data)return data;
  const retry=await sessionWindow(run.id);if(retry)return retry;
  throw error||new Error("No se pudo fijar el inicio oficial");
}
async function teacherWall(ctx:any,run:any){
  requireTeacher(ctx);
  const [{data:enrollments},{data:progress},{data:activities},window,def]=await Promise.all([
    db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id).eq("status","active"),
    db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",SESSION),
    db.from("bd_lms_activity_progress").select("*").eq("course_run_id",run.id).in("activity_code",[...ALL_CODES]),
    sessionWindow(run.id),
    definition(run.id)
  ]);
  const ids=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const {data:users}=ids.length?await db.from("lms_users").select("id,display_name,username,active").in("id",ids):({data:[]} as any);
  const pm=new Map((progress||[]).map((x:any)=>[x.user_id,x])),byUser=new Map<string,any[]>();
  for(const a of activities||[]){if(!byUser.has(a.user_id))byUser.set(a.user_id,[]);byUser.get(a.user_id)!.push(a)}
  const rows=(users||[]).map((u:any)=>{
    const p:any=pm.get(u.id)||{},a=byUser.get(u.id)||[],am=new Map(a.map((x:any)=>[x.activity_code,x]));
    const completed=[...CHECKPOINT_CODES].filter(code=>am.get(code)?.status==="completed").length;
    let delay:null|number=null;
    if(window?.opened_at&&p.started_at)delay=Math.max(0,Math.round((Date.parse(p.started_at)-Date.parse(window.opened_at))/1000));
    return {
      user_id:u.id,display_name:u.display_name||u.username,status:p.status||"not_started",
      started_at:p.started_at||null,start_delay_seconds:delay,active_seconds:Number(p.active_seconds||0),
      last_activity_at:p.last_activity_at||null,completed_checkpoints:completed,total_checkpoints:CHECKPOINT_CODES.size,
      presentation_opened:!!am.get("bd-s09-presentation"),
      notebook_opened:!!am.get("bd-s09-notebook"),
      checkpoints:[...CHECKPOINT_CODES].map(code=>{
        const cp:any=am.get(code)||{},meta=(cp.metadata&&typeof cp.metadata==="object")?cp.metadata:{};
        return {code,status:cp.status||"not_started",started_at:cp.started_at||null,completed_at:cp.completed_at||null,attempts:Number(cp.attempts||0),first_attempt_correct:typeof meta.first_attempt_correct==="boolean"?meta.first_attempt_correct:null,mastery:Boolean(meta.mastery)};
      })
    };
  });
  rows.sort((a:any,b:any)=>(a.display_name||"").localeCompare(b.display_name||"","es"));
  const challenge_stats=[...CHECKPOINT_CODES].map(code=>{
    const cps=rows.map((r:any)=>r.checkpoints.find((x:any)=>x.code===code)).filter(Boolean);
    return {
      code,
      attempted:cps.filter((x:any)=>x.attempts>0).length,
      first_attempt_correct:cps.filter((x:any)=>x.first_attempt_correct===true).length,
      mastered:cps.filter((x:any)=>x.mastery===true).length
    };
  });
  return {viewer:ctx.user,run,session:def.session,activities:def.activities,resources:def.resources,session_window:window,ranking:rows,challenge_stats};
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  let action="me",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"me";
  else{try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}action=String(body.action||"me")}
  try{
    if(action==="me"){const def=await definition(run.id),p=await ownProgress(ctx.user.id,run.id);return out(req,{viewer:ctx.user,run,...def,...p})}
    if(action==="track"){
      const event=String(body.event_type||"");if(!TRACK_EVENTS.has(event))throw new Error("Evento no permitido");
      const activity=body.activity_code?String(body.activity_code):null;if(activity&&!ALL_CODES.has(activity))throw new Error("Actividad no válida");
      const delta=event==="heartbeat"?Math.max(0,Math.min(30,Math.round(Number(body.active_seconds_delta||0)))):0;
      const now=new Date().toISOString();
      await db.from("bd_lms_events").insert({
        user_id:ctx.user.id,course_run_id:run.id,event_type:event,session_number:SESSION,
        activity_code:activity,active_seconds_delta:delta,metadata:cleanMeta(body.metadata),
        client_at:body.client_at?String(body.client_at):null,created_at:now
      });
      if(event==="heartbeat")await heartbeat(ctx.user.id,run.id,delta);
      else if(["presentation_opened","notebook_opened","checkpoint_started"].includes(event)){
        await ensureSessionStarted(ctx.user.id,run.id);
        if(activity)await touchActivity(ctx.user.id,run.id,activity,event);
      }
      return out(req,{ok:true});
    }
    if(action==="answer_challenge")return out(req,await answerChallenge(ctx,run,String(body.activity_code||""),body.answer));
    if(action==="complete_checkpoint")return out(req,await completeCheckpoint(ctx,run,String(body.activity_code||"")));
    if(action==="teacher_open_session")return out(req,{ok:true,session_window:await openOfficial(ctx,run)});
    if(action==="teacher_wall")return out(req,await teacherWall(ctx,run));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,400)},400);
  }
});