import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,{auth:{persistSession:false}});
const COURSE="bigdata",RUN_CODE="bigdata-2026-2",SESSION=8,VALIDATOR_VERSION="2026-09-17-v3-historico-atlas";
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const TRACK_EVENTS=new Set(["page_opened","page_closed","heartbeat","notebook_opened","activity_started","stage_opened","ui_action"]);
const ACTIVITY_CODES=new Set(["bd-s08-e1","bd-s08-e2","bd-s08-e3","bd-s08-e4","bd-s08-e5","bd-s08-e6","bd-s08-final"]);
const STAGE_MAX:Record<string,number>={E1:20,E2:30,E3:10,E4:15,E5:20,E6:5};
const STAGE_ACTIVITY:Record<string,string>={E1:"bd-s08-e1",E2:"bd-s08-e2",E3:"bd-s08-e3",E4:"bd-s08-e4",E5:"bd-s08-e5",E6:"bd-s08-e6"};

function origin(req:Request){const o=req.headers.get("origin");if(!o)return "";if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;return null}
function headers(req:Request){const o=origin(req);return {"Access-Control-Allow-Origin":o||"https://jazaineam1.github.io","Access-Control-Allow-Headers":"authorization, content-type","Access-Control-Allow-Methods":"GET, POST, OPTIONS","Vary":"Origin","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","Referrer-Policy":"strict-origin-when-cross-origin"}}
function out(req:Request,body:unknown,status=200){return new Response(JSON.stringify(body),{status,headers:{...headers(req),"Content-Type":"application/json"}})}
function bearer(req:Request){const h=req.headers.get("authorization")||"";return h.toLowerCase().startsWith("bearer ")?h.slice(7).trim():""}
async function digestHex(text:string){const d=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(text));return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,"0")).join("")}
function cleanMeta(raw:any){const x=raw&&typeof raw==="object"?raw:{},z:Record<string,string|number|boolean|null>={};for(const k of ["source","action","label","path"]){const v=x[k];if(typeof v==="string")z[k]=v.slice(0,180);else if(typeof v==="number"||typeof v==="boolean"||v===null)z[k]=v}return z}

async function current(req:Request){
 const token=bearer(req);if(!token)return null;
 const token_hash=await digestHex(token);
 const {data:s}=await db.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent").eq("token_hash",token_hash).is("revoked_at",null).maybeSingle();
 if(!s)return null;if(!s.persistent&&(!s.expires_at||new Date(s.expires_at).getTime()<=Date.now()))return null;
 const {data:u}=await db.from("lms_users").select("id,username,display_name,role,active,email").eq("id",s.user_id).eq("active",true).maybeSingle();
 return u?{session:s,user:u}:null
}
async function activeRun(ctx:any){
 const {data:memberships}=await db.from("lms_run_enrollments").select("course_run_id,role,status,enrolled_at").eq("user_id",ctx.user.id).eq("status","active").order("enrolled_at",{ascending:false});
 for(const m of memberships||[]){const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,starts_on,ends_on,active").eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();if(r)return {...r,enrollment_role:m.role}}
 if(["teacher","admin"].includes(ctx.user.role)){const {data:r}=await db.from("lms_course_runs").select("id,course_code,code,title,timezone,starts_on,ends_on,active").eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();if(r)return {...r,enrollment_role:ctx.user.role}}
 return null
}
async function sessionDefinition(){
 const [{data:session},{data:activities}]=await Promise.all([
  db.from("bd_lms_sessions").select("*").eq("course_code",COURSE).eq("session_number",SESSION).single(),
  db.from("bd_lms_activities").select("*").eq("course_code",COURSE).eq("session_number",SESSION).order("position")
 ]);
 return {session,activities:activities||[]}
}
async function sessionWindow(runId:string){const {data}=await db.from("bd_lms_session_windows").select("opened_at,opened_by").eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();return data||null}
async function ownProgress(userId:string,runId:string){
 const [{data:session_progress},{data:activity_progress},{data:submission},window]=await Promise.all([
  db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle(),
  db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",runId),
  db.from("bd_lms_s08_submissions").select("manifest_version,score,max_score,note_5,sha256,validated,submitted_at,updated_at").eq("user_id",userId).eq("course_run_id",runId).maybeSingle(),
  sessionWindow(runId)
 ]);
 return {session_progress,activity_progress:activity_progress||[],submission,session_window:window}
}
async function ensureSessionStarted(userId:string,runId:string){
 const now=new Date().toISOString(),{data:p}=await db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
 if(!p){await db.from("bd_lms_session_progress").insert({user_id:userId,course_run_id:runId,session_number:SESSION,status:"in_progress",started_at:now,active_seconds:0,last_activity_at:now,updated_at:now});return now}
 await db.from("bd_lms_session_progress").update({status:p.status==="completed"?"completed":"in_progress",last_activity_at:now,updated_at:now}).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION);
 return p.started_at||now
}
async function heartbeat(userId:string,runId:string,delta:number){
 const {data:p}=await db.from("bd_lms_session_progress").select("active_seconds,status").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle();
 if(!p)return;
 const now=new Date().toISOString();await db.from("bd_lms_session_progress").update({active_seconds:Number(p.active_seconds||0)+delta,last_activity_at:now,updated_at:now}).eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION)
}
async function touchActivity(userId:string,runId:string,code:string){
 const now=new Date().toISOString(),{data:p}=await db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code).maybeSingle();
 if(!p){await db.from("bd_lms_activity_progress").insert({user_id:userId,course_run_id:runId,activity_code:code,status:"in_progress",started_at:now,attempts:0,score:0,max_score:0,updated_at:now});return}
 await db.from("bd_lms_activity_progress").update({status:p.status==="completed"?"completed":"in_progress",updated_at:now}).eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code)
}
function summarizeControls(controls:any){
 if(!controls||typeof controls!=="object"||Array.isArray(controls))throw new Error("controles inválidos");
 const clean:Record<string,any>={},stageScores:Record<string,number>={E1:0,E2:0,E3:0,E4:0,E5:0,E6:0},stageMax:Record<string,number>={E1:0,E2:0,E3:0,E4:0,E5:0,E6:0};
 for(const [k,v0] of Object.entries(controls)){const v:any=v0;if(!/^E[1-6]_/.test(k)||!v||typeof v!=="object")continue;const p=k.slice(0,2),pts=Number(v.puntos),max=Number(v.maximo);if(!Number.isFinite(pts)||!Number.isFinite(max)||pts<0||max<0||pts>max)throw new Error("puntaje de control inválido");clean[k]={ok:!!v.ok,puntos:pts,maximo:max};stageScores[p]+=pts;stageMax[p]+=max}
 for(const p of Object.keys(STAGE_MAX))if(stageMax[p]!==STAGE_MAX[p])throw new Error("máximo "+p+" inválido");
 return {clean,stageScores,stageMax}
}
async function verifyManifest(rawInput:string){
 if(!rawInput||rawInput.length>120000)throw new Error("archivo vacío o demasiado grande");
 const raw=rawInput.replace(/\r\n/g,"\n").replace(/\r/g,"\n").trimEnd();let m:any;try{m=JSON.parse(raw)}catch{throw new Error("manifest_tc1.json no contiene JSON válido")}
 const supplied=String(m.sha256||"").toLowerCase();if(!/^[0-9a-f]{64}$/.test(supplied))throw new Error("SHA-256 ausente o inválido");
 const pattern=/,\n  "sha256": "[0-9a-fA-F]{64}"\n}$/;const prior=raw.replace(pattern,"\n}");if(prior===raw)throw new Error("El archivo fue reformateado. Carga directamente manifest_tc1.json generado por el validador.");
 if(await digestHex(prior)!==supplied)throw new Error("SHA-256 no coincide: el manifest fue modificado después del validador");
 if(String(m.version||"")!==VALIDATOR_VERSION)throw new Error("Versión del validador no reconocida");
 const score=Number(m.puntaje),max=Number(m.maximo),note=Number(m.nota_5);if(!Number.isInteger(score)||score<0||score>100||max!==100)throw new Error("Puntaje del manifest inválido");
 const expected=Math.round((1+4*score/100)*100)/100;if(!Number.isFinite(note)||Math.abs(note-expected)>.001)throw new Error("Nota del manifest no corresponde al puntaje");
 const pair=String(m.pareja_id||"").trim();if(pair.length<3||pair.length>160)throw new Error("Identificador de pareja inválido");
 const {clean,stageScores,stageMax}=summarizeControls(m.controles);const sum=Object.values(stageScores).reduce((a:number,b:any)=>a+Number(b),0);if(sum!==score)throw new Error("El detalle por etapas no suma el puntaje total");
 return {pair_hash:await digestHex(pair),score,note,sha:supplied,controls:clean,stageScores,stageMax}
}
async function persistManifest(ctx:any,run:any,m:any){
 const now=new Date().toISOString();await ensureSessionStarted(ctx.user.id,run.id);
 const {error}=await db.from("bd_lms_s08_submissions").upsert({user_id:ctx.user.id,course_run_id:run.id,pair_hash:m.pair_hash,manifest_version:VALIDATOR_VERSION,score:m.score,max_score:100,note_5:m.note,sha256:m.sha,controls:m.controls,validated:true,submitted_at:now,updated_at:now},{onConflict:"user_id,course_run_id"});if(error)throw error;
 for(const p of Object.keys(STAGE_ACTIVITY)){const code=STAGE_ACTIVITY[p],score=m.stageScores[p],max=m.stageMax[p],done=score===max,{data:prior}=await db.from("bd_lms_activity_progress").select("started_at,attempts").eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("activity_code",code).maybeSingle();await db.from("bd_lms_activity_progress").upsert({user_id:ctx.user.id,course_run_id:run.id,activity_code:code,status:done?"completed":"submitted",started_at:prior?.started_at||now,attempts:Number(prior?.attempts||0),score,max_score:max,completed_at:done?now:null,updated_at:now,metadata:{source:"manifest_tc1",validated:true}},{onConflict:"user_id,course_run_id,activity_code"})}
 const {data:pf}=await db.from("bd_lms_activity_progress").select("started_at,attempts").eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("activity_code","bd-s08-final").maybeSingle();
 await db.from("bd_lms_activity_progress").upsert({user_id:ctx.user.id,course_run_id:run.id,activity_code:"bd-s08-final",status:"completed",started_at:pf?.started_at||now,attempts:Number(pf?.attempts||0)+1,score:m.score,max_score:100,completed_at:now,updated_at:now,metadata:{source:"manifest_tc1",validated:true,sha256:m.sha}},{onConflict:"user_id,course_run_id,activity_code"});
 const {data:sp}=await db.from("bd_lms_session_progress").select("*").eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("session_number",SESSION).maybeSingle();
 await db.from("bd_lms_session_progress").upsert({user_id:ctx.user.id,course_run_id:run.id,session_number:SESSION,status:"completed",started_at:sp?.started_at||now,active_seconds:Number(sp?.active_seconds||0),last_activity_at:now,submitted_at:now,completed_at:now,score:m.score,max_score:100,updated_at:now},{onConflict:"user_id,course_run_id,session_number"});
 await db.from("bd_lms_events").insert({user_id:ctx.user.id,course_run_id:run.id,event_type:"manifest_submitted",session_number:SESSION,activity_code:"bd-s08-final",metadata:{score:m.score,validated:true},created_at:now})
}
async function openOfficial(ctx:any,run:any){
 if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH");
 const existing=await sessionWindow(run.id);if(existing)return existing;
 const now=new Date().toISOString();const {data,error}=await db.from("bd_lms_session_windows").insert({course_run_id:run.id,session_number:SESSION,opened_at:now,opened_by:ctx.user.id}).select("opened_at,opened_by").single();
 if(!error&&data)return data;const retry=await sessionWindow(run.id);if(retry)return retry;throw error||new Error("No se pudo fijar el inicio oficial")
}
async function teacherWall(ctx:any,run:any){
 if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH");
 const [{data:enrollments},{data:progress},{data:activities},{data:subs},{data:requests},window]=await Promise.all([
  db.from("lms_run_enrollments").select("user_id,role,status,enrolled_at").eq("course_run_id",run.id).eq("status","active"),
  db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",SESSION),
  db.from("bd_lms_activity_progress").select("*").eq("course_run_id",run.id),
  db.from("bd_lms_s08_submissions").select("user_id,score,max_score,note_5,validated,submitted_at,sha256").eq("course_run_id",run.id),
  db.from("lms_access_requests").select("id,full_name,email,course_code,status,created_at,reviewed_at").eq("course_code",COURSE).order("created_at",{ascending:false}).limit(100),
  sessionWindow(run.id)
 ]);
 const ids=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id),{data:users}=ids.length?await db.from("lms_users").select("id,display_name,username,active").in("id",ids):({data:[]} as any);
 const pm=new Map((progress||[]).map((x:any)=>[x.user_id,x])),sm=new Map((subs||[]).map((x:any)=>[x.user_id,x])),byUser=new Map<string,any[]>();
 for(const a of activities||[]){if(!byUser.has(a.user_id))byUser.set(a.user_id,[]);byUser.get(a.user_id)!.push(a)}
 const rows=(users||[]).map((u:any)=>{const p:any=pm.get(u.id)||{},s:any=sm.get(u.id)||{},st=(byUser.get(u.id)||[]).map((a:any)=>({activity_code:a.activity_code,status:a.status,score:Number(a.score||0),max_score:Number(a.max_score||0),started_at:a.started_at,completed_at:a.completed_at}));let delay:null|number=null;if(window?.opened_at&&p.started_at)delay=Math.max(0,Math.round((Date.parse(p.started_at)-Date.parse(window.opened_at))/1000));return {user_id:u.id,display_name:u.display_name||u.username,status:p.status||"not_started",score:Number(s.score??p.score??0),max_score:Number(s.max_score??p.max_score??100),note_5:s.note_5??null,started_at:p.started_at||null,start_delay_seconds:delay,active_seconds:Number(p.active_seconds||0),last_activity_at:p.last_activity_at||null,submitted_at:s.submitted_at||p.submitted_at||null,validated:!!s.validated,sha256:s.sha256||null,stages:st}});
 rows.sort((a:any,b:any)=>{if(b.score!==a.score)return b.score-a.score;if(window?.opened_at){const da=a.start_delay_seconds??Number.MAX_SAFE_INTEGER,dbb=b.start_delay_seconds??Number.MAX_SAFE_INTEGER;if(da!==dbb)return da-dbb}else{const ta=a.started_at?Date.parse(a.started_at):Number.MAX_SAFE_INTEGER,tb=b.started_at?Date.parse(b.started_at):Number.MAX_SAFE_INTEGER;if(ta!==tb)return ta-tb}const sa=a.submitted_at?Date.parse(a.submitted_at):Number.MAX_SAFE_INTEGER,sb=b.submitted_at?Date.parse(b.submitted_at):Number.MAX_SAFE_INTEGER;return sa-sb});
 return {viewer:ctx.user,run,session_window:window,ranking:rows,access_requests:requests||[]}
}

Deno.serve(async(req:Request)=>{
 if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
 const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
 let action="me",body:any={};if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"me";else{try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}action=String(body.action||"me")}
 try{
  if(action==="me"){const def=await sessionDefinition(),progress=await ownProgress(ctx.user.id,run.id);return out(req,{viewer:ctx.user,run,...def,...progress})}
  if(action==="track"){const event=String(body.event_type||"");if(!TRACK_EVENTS.has(event))return out(req,{error:"Evento no permitido"},400);const activity=body.activity_code?String(body.activity_code):null;if(activity&&!ACTIVITY_CODES.has(activity))return out(req,{error:"Actividad no válida"},400);const delta=event==="heartbeat"?Math.max(0,Math.min(30,Math.round(Number(body.active_seconds_delta||0)))):0,now=new Date().toISOString();await db.from("bd_lms_events").insert({user_id:ctx.user.id,course_run_id:run.id,event_type:event,session_number:SESSION,activity_code:activity,active_seconds_delta:delta,metadata:cleanMeta(body.metadata),client_at:body.client_at?String(body.client_at):null,created_at:now});if(["notebook_opened","activity_started","stage_opened"].includes(event))await ensureSessionStarted(ctx.user.id,run.id);else if(event==="heartbeat")await heartbeat(ctx.user.id,run.id,delta);if(activity&&["activity_started","stage_opened"].includes(event))await touchActivity(ctx.user.id,run.id,activity);return out(req,{ok:true})}
  if(action==="submit_manifest"){const m=await verifyManifest(String(body.manifest_text||""));await persistManifest(ctx,run,m);const p=await ownProgress(ctx.user.id,run.id);return out(req,{ok:true,validated:true,score:m.score,note_5:m.note,sha256:m.sha,...p})}
  if(action==="teacher_open_session"){try{return out(req,{ok:true,session_window:await openOfficial(ctx,run)})}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_wall"){try{return out(req,await teacherWall(ctx,run))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  return out(req,{error:"Acción desconocida"},400)
 }catch(e){return out(req,{error:String((e as any)?.message||e).slice(0,400)},400)}
});