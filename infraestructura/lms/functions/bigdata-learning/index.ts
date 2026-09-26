import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,{auth:{persistSession:false}});
const COURSE="bigdata",RUN_CODE="bigdata-2026-2",SESSION=8,CURRENT_VALIDATOR_VERSION="2026-09-26-secoppipeline";
const VALIDATOR_VERSIONS=new Set([CURRENT_VALIDATOR_VERSION]);
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const TRACK_EVENTS=new Set(["page_opened","page_closed","heartbeat","notebook_opened","activity_started","stage_opened","ui_action"]);
const ACTIVITY_CODES=new Set(["bd-s08-e1","bd-s08-e2","bd-s08-e3","bd-s08-e4","bd-s08-e5","bd-s08-e6","bd-s08-final"]);
const STAGE_MAX:Record<string,number>={E1:25,E2:25,E3:10,E4:15,E5:15,E6:10};
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
async function tc1GroupContext(userId:string,runId:string){
 const {data:memberships}=await db.from("lms_group_members_v2").select("group_id,role").eq("user_id",userId);
 const ids=(memberships||[]).map((x:any)=>x.group_id);
 if(!ids.length)return null;
 const {data:groups}=await db.from("lms_groups_v2").select("id,name,description,active").eq("course_run_id",runId).eq("active",true).in("id",ids);
 if(!(groups||[]).length)return null;
 if((groups||[]).length!==1)throw new Error("Tu cuenta pertenece a más de un equipo activo. El docente debe corregir la configuración antes de entregar TC1.");
 const group:any=(groups||[])[0];
 const {data:members}=await db.from("lms_group_members_v2").select("user_id,role").eq("group_id",group.id);
 const userIds=(members||[]).map((x:any)=>x.user_id);
 const {data:users}=userIds.length?await db.from("lms_users").select("id,display_name,username").in("id",userIds):({data:[]} as any);
 const um=new Map((users||[]).map((u:any)=>[u.id,u]));
 return {group,members:(members||[]).map((m:any)=>({user_id:m.user_id,role:m.role,display_name:(um.get(m.user_id) as any)?.display_name||(um.get(m.user_id) as any)?.username||"Participante"}))}
}
async function ownProgress(userId:string,runId:string){
 const [{data:session_progress},{data:activity_progress},{data:submission},window,group_context]=await Promise.all([
  db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",runId).eq("session_number",SESSION).maybeSingle(),
  db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",runId),
  db.from("bd_lms_s08_submissions").select("manifest_version,score,max_score,note_5,sha256,validated,submitted_at,updated_at").eq("user_id",userId).eq("course_run_id",runId).maybeSingle(),
  sessionWindow(runId),
  tc1GroupContext(userId,runId)
 ]);
 return {session_progress,activity_progress:activity_progress||[],submission,session_window:window,group_context}
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
 const version=String(m.version||"");if(!VALIDATOR_VERSIONS.has(version))throw new Error("Versión del validador no reconocida");
 const securityGate=m?.gates?.security_no_secrets;if(!securityGate||securityGate.ok!==true)throw new Error("La entrega contiene o no ha verificado secretos. Corrige los artefactos y genera nuevamente el manifest.");
 const score=Number(m.puntaje),max=Number(m.maximo),note=Number(m.nota_5);if(!Number.isInteger(score)||score<0||score>100||max!==100)throw new Error("Puntaje del manifest inválido");
 const expected=Math.round((1+4*score/100)*100)/100;if(!Number.isFinite(note)||Math.abs(note-expected)>.001)throw new Error("Nota del manifest no corresponde al puntaje");
 const pair=String(m.pareja_id||"").trim();if(pair.length<3||pair.length>160)throw new Error("Identificador de pareja inválido");
 const {clean,stageScores,stageMax}=summarizeControls(m.controles);const sum=Object.values(stageScores).reduce((a:number,b:any)=>a+Number(b),0);if(sum!==score)throw new Error("El detalle por etapas no suma el puntaje total");
 return {pair_hash:await digestHex(pair),score,note,sha:supplied,controls:clean,stageScores,stageMax,version}
}
async function syncManifestGroupGradebook(ctx:any,run:any,m:any,groupCtx:any){
 const {data:a}=await db.from("lms_assignments_v2").select("id,max_attempts,max_score").eq("course_run_id",run.id).eq("code","bd-s08-control").eq("active",true).maybeSingle();
 if(!a)throw new Error("No existe la tarea TC1 activa en el Gradebook.");
 const {data:setting}=await db.from("lms_assignment_group_settings_v2").select("enabled").eq("assignment_id",a.id).eq("enabled",true).maybeSingle();
 if(!setting)throw new Error("TC1 no está habilitado como entrega grupal.");
 const now=new Date().toISOString(),maxAttempts=Number(a.max_attempts||20);
 const {data:prior}=await db.from("lms_group_submissions_v2").select("*").eq("assignment_id",a.id).eq("group_id",groupCtx.group.id).order("attempt",{ascending:false}).limit(1).maybeSingle();
 let gs:any=null;
 if(!prior||Number(prior.attempt)<maxAttempts){
  const attempt=Number(prior?.attempt||0)+1;
  const {data,error}=await db.from("lms_group_submissions_v2").insert({
   assignment_id:a.id,group_id:groupCtx.group.id,attempt,artifact_type:"evidence",
   artifact:{source:"manifest_tc1",sha256:m.sha,validator_version:m.version,pair_hash:m.pair_hash,stage_scores:m.stageScores},
   status:"reviewed",submitted_by:ctx.user.id,submitted_at:now,score:m.score,
   feedback:"Calificación automática grupal desde manifest_tc1.json validado en S08.",
   rubric_scores:m.stageScores,reviewed_at:now
  }).select("*").single();if(error)throw error;gs=data;
 }else{
  const {data,error}=await db.from("lms_group_submissions_v2").update({
   artifact:{source:"manifest_tc1",sha256:m.sha,validator_version:m.version,pair_hash:m.pair_hash,stage_scores:m.stageScores},
   status:"reviewed",submitted_by:ctx.user.id,submitted_at:now,score:m.score,
   feedback:"Calificación automática grupal actualizada desde la validación más reciente de S08.",
   rubric_scores:m.stageScores,reviewed_at:now
  }).eq("id",prior.id).select("*").single();if(error)throw error;gs=data;
 }
 for(const member of groupCtx.members||[]){
  const {data:latest}=await db.from("lms_submissions_v2").select("*").eq("assignment_id",a.id).eq("user_id",member.user_id).order("attempt",{ascending:false}).limit(1).maybeSingle();
  let ind:any=null,previousScore:any=latest?.score??null,previousFeedback:any=latest?.feedback??null;
  if(!latest||Number(latest.attempt)<maxAttempts){
   const attempt=Number(latest?.attempt||0)+1;
   const {data,error}=await db.from("lms_submissions_v2").insert({
    assignment_id:a.id,user_id:member.user_id,attempt,artifact_type:"evidence",
    artifact:{source:"group_submission",group_submission_id:gs.id,group_id:groupCtx.group.id,sha256:m.sha,validator_version:m.version},
    status:"reviewed",submitted_at:now,score:m.score,
    feedback:"Calificación grupal TC1 · "+groupCtx.group.name+".",
    rubric_scores:m.stageScores,reviewed_at:now
   }).select("*").single();if(error)throw error;ind=data;
  }else{
   const {data,error}=await db.from("lms_submissions_v2").update({
    artifact:{source:"group_submission",group_submission_id:gs.id,group_id:groupCtx.group.id,sha256:m.sha,validator_version:m.version},
    status:"reviewed",submitted_at:now,score:m.score,
    feedback:"Calificación grupal TC1 · "+groupCtx.group.name+".",
    rubric_scores:m.stageScores,reviewed_at:now
   }).eq("id",latest.id).select("*").single();if(error)throw error;ind=data;
  }
  if(ind)await db.from("lms_grade_history_v2").insert({
   submission_id:ind.id,assignment_id:a.id,user_id:member.user_id,actor_user_id:null,
   previous_score:previousScore,new_score:m.score,previous_feedback:previousFeedback,new_feedback:ind.feedback,
   rubric_scores:m.stageScores,created_at:now
  }).then(()=>{}).catch(()=>{});
 }
 return gs
}

async function persistManifest(ctx:any,run:any,m:any){
 const groupCtx=await tc1GroupContext(ctx.user.id,run.id);
 if(!groupCtx)throw new Error("TC1 se califica por grupo. El docente debe asignarte a un equipo activo antes de registrar la entrega.");
 const now=new Date().toISOString();
 const groupSubmission=await syncManifestGroupGradebook(ctx,run,m,groupCtx);
 for(const member of groupCtx.members||[]){
  await ensureSessionStarted(member.user_id,run.id);
  const {error}=await db.from("bd_lms_s08_submissions").upsert({
   user_id:member.user_id,course_run_id:run.id,pair_hash:m.pair_hash,manifest_version:m.version,
   score:m.score,max_score:100,note_5:m.note,sha256:m.sha,controls:m.controls,validated:true,
   submitted_at:now,updated_at:now
  },{onConflict:"user_id,course_run_id"});if(error)throw error;
  for(const p of Object.keys(STAGE_ACTIVITY)){
   const code=STAGE_ACTIVITY[p],score=m.stageScores[p],max=m.stageMax[p],done=score===max;
   const {data:prior}=await db.from("bd_lms_activity_progress").select("started_at,attempts").eq("user_id",member.user_id).eq("course_run_id",run.id).eq("activity_code",code).maybeSingle();
   await db.from("bd_lms_activity_progress").upsert({
    user_id:member.user_id,course_run_id:run.id,activity_code:code,status:done?"completed":"submitted",
    started_at:prior?.started_at||now,attempts:Number(prior?.attempts||0),score,max_score:max,
    completed_at:done?now:null,updated_at:now,
    metadata:{source:"group_manifest_tc1",validated:true,group_id:groupCtx.group.id}
   },{onConflict:"user_id,course_run_id,activity_code"});
  }
  const {data:pf}=await db.from("bd_lms_activity_progress").select("started_at,attempts").eq("user_id",member.user_id).eq("course_run_id",run.id).eq("activity_code","bd-s08-final").maybeSingle();
  await db.from("bd_lms_activity_progress").upsert({
   user_id:member.user_id,course_run_id:run.id,activity_code:"bd-s08-final",status:"completed",
   started_at:pf?.started_at||now,attempts:Number(pf?.attempts||0)+1,score:m.score,max_score:100,
   completed_at:now,updated_at:now,metadata:{source:"group_manifest_tc1",validated:true,sha256:m.sha,group_id:groupCtx.group.id}
  },{onConflict:"user_id,course_run_id,activity_code"});
  const {data:sp}=await db.from("bd_lms_session_progress").select("*").eq("user_id",member.user_id).eq("course_run_id",run.id).eq("session_number",SESSION).maybeSingle();
  await db.from("bd_lms_session_progress").upsert({
   user_id:member.user_id,course_run_id:run.id,session_number:SESSION,status:"completed",
   started_at:sp?.started_at||now,active_seconds:Number(sp?.active_seconds||0),last_activity_at:now,
   submitted_at:now,completed_at:now,score:m.score,max_score:100,updated_at:now
  },{onConflict:"user_id,course_run_id,session_number"});
 }
 await db.from("bd_lms_events").insert({
  user_id:ctx.user.id,course_run_id:run.id,event_type:"manifest_submitted",session_number:SESSION,
  activity_code:"bd-s08-final",metadata:{score:m.score,validated:true,group_id:groupCtx.group.id,group_submission_id:groupSubmission.id},created_at:now
 });
 return {group_context:groupCtx,group_submission:groupSubmission}
}
async function openOfficial(ctx:any,run:any){
 if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH");
 const existing=await sessionWindow(run.id);if(existing)return existing;
 const now=new Date().toISOString();const {data,error}=await db.from("bd_lms_session_windows").insert({course_run_id:run.id,session_number:SESSION,opened_at:now,opened_by:ctx.user.id}).select("opened_at,opened_by").single();
 if(!error&&data)return data;const retry=await sessionWindow(run.id);if(retry)return retry;throw error||new Error("No se pudo fijar el inicio oficial")
}
function requireTeacher(ctx:any){
 if(!["teacher","admin"].includes(ctx.user.role))throw new Error("NO_AUTH")
}
function tempPassword(){
 const chars="ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789";
 const bytes=crypto.getRandomValues(new Uint8Array(12));let s="Bd8-";
 for(const b of bytes)s+=chars[b%chars.length];
 return s
}
async function auditAdmin(actor:string,action:string,target:string,metadata:any={}){
 await db.from("lms_audit_log").insert({
  actor_user_id:actor,action,entity_type:"bigdata_user",entity_id:target,
  metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}
 }).then(()=>{}).catch(()=>{})
}
function sessionAlive(s:any){
 if(s.revoked_at)return false;
 if(s.persistent)return true;
 return !!s.expires_at&&Date.parse(s.expires_at)>Date.now()
}
async function teacherAdminOverview(ctx:any,run:any){
 requireTeacher(ctx);
 const [{data:courseEnroll},{data:runEnroll},{data:progress},{data:subs},{data:requests},{data:auditRows}] = await Promise.all([
  db.from("lms_enrollments").select("user_id,role,status,enrolled_at").eq("course_code",COURSE),
  db.from("lms_run_enrollments").select("user_id,role,status,enrolled_at,completed_at").eq("course_run_id",run.id),
  db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",SESSION),
  db.from("bd_lms_s08_submissions").select("user_id,score,max_score,note_5,validated,submitted_at").eq("course_run_id",run.id),
  db.from("lms_access_requests").select("id,full_name,email,status,created_at,reviewed_at,notes").eq("course_code",COURSE).order("created_at",{ascending:false}).limit(200),
  db.from("lms_audit_log").select("id,actor_user_id,action,entity_id,metadata,created_at").contains("metadata",{course_code:COURSE}).order("created_at",{ascending:false}).limit(100)
 ]);
 const ce=courseEnroll||[],re=runEnroll||[],ids=[...new Set([...ce,...re].map((x:any)=>x.user_id))];
 const [{data:users},{data:sessions}] = await Promise.all([
  ids.length?db.from("lms_users").select("id,username,display_name,email,role,active,created_at,updated_at").in("id",ids):Promise.resolve({data:[]} as any),
  ids.length?db.from("lms_auth_sessions").select("id,user_id,created_at,last_seen_at,expires_at,persistent,revoked_at").in("user_id",ids).order("last_seen_at",{ascending:false}):Promise.resolve({data:[]} as any)
 ]);
 const cem=new Map(ce.map((x:any)=>[x.user_id,x])),rem=new Map(re.map((x:any)=>[x.user_id,x]));
 const pm=new Map((progress||[]).map((x:any)=>[x.user_id,x])),sm=new Map((subs||[]).map((x:any)=>[x.user_id,x]));
 const reqByEmail=new Map<string,any>();for(const r of requests||[]){const k=String(r.email||"").toLowerCase();if(!reqByEmail.has(k))reqByEmail.set(k,r)}
 const sessByUser=new Map<string,any[]>();for(const s of sessions||[]){if(!sessionAlive(s))continue;if(!sessByUser.has(s.user_id))sessByUser.set(s.user_id,[]);sessByUser.get(s.user_id)!.push(s)}
 const rows=(users||[]).filter((u:any)=>(cem.get(u.id)?.role||rem.get(u.id)?.role||u.role)==="student").map((u:any)=>{
  const a:any=cem.get(u.id)||{},b:any=rem.get(u.id)||{},p:any=pm.get(u.id)||{},s:any=sm.get(u.id)||{},ss=sessByUser.get(u.id)||[],rq=reqByEmail.get(String(u.email||u.username||"").toLowerCase());
  return {user_id:u.id,display_name:u.display_name||u.username,email:u.email||u.username,global_active:!!u.active,
   course_status:a.status||"none",run_status:b.status||"none",enrolled_at:b.enrolled_at||a.enrolled_at||null,
   s08_status:p.status||"not_started",score:Number(s.score??p.score??0),note_5:s.note_5??null,
   active_seconds:Number(p.active_seconds||0),started_at:p.started_at||null,last_activity_at:p.last_activity_at||null,
   submitted_at:s.submitted_at||p.submitted_at||null,open_sessions:ss.length,last_seen_at:ss[0]?.last_seen_at||null,
   request_id:rq?.id||null,request_status:rq?.status||null}
 });
 rows.sort((a:any,b:any)=>a.display_name.localeCompare(b.display_name,"es",{sensitivity:"base"}));
 const stats={
  total:rows.length,active:rows.filter((x:any)=>x.global_active&&x.course_status==="active"&&x.run_status==="active").length,
  suspended:rows.filter((x:any)=>!x.global_active||x.course_status==="suspended"||x.run_status==="inactive").length,
  started:rows.filter((x:any)=>x.started_at).length,completed:rows.filter((x:any)=>x.s08_status==="completed").length,
  pending_requests:(requests||[]).filter((x:any)=>x.status==="pending").length,
  open_sessions:rows.reduce((a:number,x:any)=>a+x.open_sessions,0)
 };
 const actorIds=[...new Set((auditRows||[]).map((x:any)=>x.actor_user_id).filter(Boolean))];
 const {data:actors}=actorIds.length?await db.from("lms_users").select("id,display_name,username").in("id",actorIds):({data:[]} as any);
 const actorMap=new Map((actors||[]).map((x:any)=>[x.id,x.display_name||x.username]));
 const audit=(auditRows||[]).map((x:any)=>({...x,actor_name:actorMap.get(x.actor_user_id)||"Sistema"}));
 return {viewer:ctx.user,run,stats,users:rows,access_requests:requests||[],audit}
}
async function teacherUserDetail(ctx:any,run:any,target:string){
 requireTeacher(ctx);if(!target)throw new Error("Usuario requerido");
 const {data:ce}=await db.from("lms_enrollments").select("user_id,role,status,enrolled_at").eq("user_id",target).eq("course_code",COURSE).maybeSingle();
 if(!ce)throw new Error("El usuario no pertenece a Big Data");
 const {data:u}=await db.from("lms_users").select("id,username,display_name,email,role,active,created_at,updated_at").eq("id",target).maybeSingle();
 if(!u)throw new Error("Usuario no encontrado");
 const [{data:re},{data:p},{data:a},{data:s},{data:sessions},{data:auditRows},{data:reqs}] = await Promise.all([
  db.from("lms_run_enrollments").select("role,status,enrolled_at,completed_at").eq("user_id",target).eq("course_run_id",run.id).maybeSingle(),
  db.from("bd_lms_session_progress").select("*").eq("user_id",target).eq("course_run_id",run.id).eq("session_number",SESSION).maybeSingle(),
  db.from("bd_lms_activity_progress").select("*").eq("user_id",target).eq("course_run_id",run.id).order("activity_code"),
  db.from("bd_lms_s08_submissions").select("score,max_score,note_5,validated,submitted_at,updated_at,sha256").eq("user_id",target).eq("course_run_id",run.id).maybeSingle(),
  db.from("lms_auth_sessions").select("id,user_agent,created_at,last_seen_at,expires_at,persistent,revoked_at").eq("user_id",target).order("last_seen_at",{ascending:false}).limit(20),
  db.from("lms_audit_log").select("id,actor_user_id,action,metadata,created_at").eq("entity_id",target).order("created_at",{ascending:false}).limit(30),
  db.from("lms_access_requests").select("id,status,created_at,reviewed_at,notes").eq("course_code",COURSE).ilike("email",u.email||u.username).order("created_at",{ascending:false}).limit(10)
 ]);
 return {user:u,course_enrollment:ce,run_enrollment:re,session_progress:p,activity_progress:a||[],submission:s,
  sessions:(sessions||[]).filter(sessionAlive).map((x:any)=>({...x,revoked_at:undefined})),audit:auditRows||[],access_requests:reqs||[]}
}
async function teacherSetEnrollment(ctx:any,run:any,target:string,status:string){
 requireTeacher(ctx);if(!target||!["active","suspended"].includes(status))throw new Error("Acción de matrícula inválida");
 const {data:u}=await db.from("lms_users").select("id,role,active,display_name,username").eq("id",target).maybeSingle();
 if(!u)throw new Error("Usuario no encontrado");if(status==="active"&&!u.active)throw new Error("La cuenta global está inactiva");if(u.role!=="student")throw new Error("Solo se administra matrícula de estudiantes desde este panel");
 const {data:ce}=await db.from("lms_enrollments").select("role,status,enrolled_at").eq("user_id",target).eq("course_code",COURSE).maybeSingle();
 if(!ce)throw new Error("El estudiante no está matriculado en Big Data");
 const now=new Date().toISOString();
 const {error:courseError}=await db.from("lms_enrollments").update({status}).eq("user_id",target).eq("course_code",COURSE);
 if(courseError)throw new Error("No se pudo actualizar la matrícula del curso");
 const {data:re}=await db.from("lms_run_enrollments").select("user_id,status").eq("user_id",target).eq("course_run_id",run.id).maybeSingle();
 if(re){const {error:e}=await db.from("lms_run_enrollments").update({status:status==="active"?"active":"inactive"}).eq("user_id",target).eq("course_run_id",run.id);if(e)throw new Error("No se pudo actualizar la cohorte")}
 else if(status==="active"){const {error:e}=await db.from("lms_run_enrollments").insert({user_id:target,course_run_id:run.id,role:"student",status:"active",enrolled_at:now});if(e)throw new Error("No se pudo matricular en la cohorte")}
 await auditAdmin(ctx.user.id,status==="active"?"bigdata.enrollment.reactivate":"bigdata.enrollment.suspend",target,{previous_status:ce.status,new_status:status});
 return {ok:true,status}
}
async function teacherAddExisting(ctx:any,run:any,emailRaw:string){
 requireTeacher(ctx);const email=String(emailRaw||"").trim().toLowerCase();if(!email||email.length>180||!email.includes("@"))throw new Error("Correo inválido");
 let {data:u}=await db.from("lms_users").select("id,username,display_name,email,role,active").ilike("email",email).maybeSingle();
 if(!u){const x=await db.from("lms_users").select("id,username,display_name,email,role,active").ilike("username",email).maybeSingle();u=x.data}
 if(!u)throw new Error("No existe una cuenta LMS con ese correo. Usa Solicitar acceso para crear una nueva.");
 if(!u.active)throw new Error("La cuenta global está inactiva");if(u.role!=="student")throw new Error("La cuenta encontrada no es de estudiante");
 const now=new Date().toISOString();
 const {data:ce}=await db.from("lms_enrollments").select("user_id").eq("user_id",u.id).eq("course_code",COURSE).maybeSingle();
 if(ce){const {error:e}=await db.from("lms_enrollments").update({role:"student",status:"active"}).eq("user_id",u.id).eq("course_code",COURSE);if(e)throw new Error("No se pudo activar la matrícula")}
 else{const {error:e}=await db.from("lms_enrollments").insert({user_id:u.id,course_code:COURSE,role:"student",status:"active",enrolled_at:now});if(e)throw new Error("No se pudo crear la matrícula")}
 const {data:re}=await db.from("lms_run_enrollments").select("user_id").eq("user_id",u.id).eq("course_run_id",run.id).maybeSingle();
 if(re){const {error:e}=await db.from("lms_run_enrollments").update({role:"student",status:"active"}).eq("user_id",u.id).eq("course_run_id",run.id);if(e)throw new Error("No se pudo activar la cohorte")}
 else{const {error:e}=await db.from("lms_run_enrollments").insert({user_id:u.id,course_run_id:run.id,role:"student",status:"active",enrolled_at:now});if(e)throw new Error("No se pudo añadir a la cohorte")}
 await auditAdmin(ctx.user.id,"bigdata.enrollment.add_existing",u.id,{email});
 return {ok:true,user:{id:u.id,display_name:u.display_name||u.username,email:u.email||u.username}}
}
async function teacherResetPassword(ctx:any,run:any,target:string){
 requireTeacher(ctx);const {data:ce}=await db.from("lms_enrollments").select("role,status").eq("user_id",target).eq("course_code",COURSE).maybeSingle();
 if(!ce||ce.role!=="student")throw new Error("Estudiante Big Data no encontrado");
 const {data:u}=await db.from("lms_users").select("id,username,display_name,email,active").eq("id",target).maybeSingle();if(!u||!u.active)throw new Error("La cuenta global no está activa");
 const password=tempPassword(),{error}=await db.rpc("lms_set_password",{p_user_id:target,p_password:password});if(error)throw new Error("No se pudo restablecer la contraseña");
 const now=new Date().toISOString();await db.from("lms_auth_sessions").update({revoked_at:now}).eq("user_id",target).is("revoked_at",null);
 await auditAdmin(ctx.user.id,"bigdata.identity.password_reset",target,{global_session_revoke:true});
 return {ok:true,username:u.username,password,display_name:u.display_name,email:u.email||u.username,warning:"La contraseña es global para el LMS y todas las sesiones anteriores quedaron cerradas."}
}
async function teacherRevokeSessions(ctx:any,target:string){
 requireTeacher(ctx);const {data:ce}=await db.from("lms_enrollments").select("role").eq("user_id",target).eq("course_code",COURSE).maybeSingle();
 if(!ce||ce.role!=="student")throw new Error("Estudiante Big Data no encontrado");
 const now=new Date().toISOString();const {data,error}=await db.from("lms_auth_sessions").update({revoked_at:now}).eq("user_id",target).is("revoked_at",null).select("id");if(error)throw error;
 await auditAdmin(ctx.user.id,"bigdata.identity.sessions_revoked",target,{count:(data||[]).length,global_scope:true});
 return {ok:true,count:(data||[]).length}
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
  if(action==="submit_manifest"){const m=await verifyManifest(String(body.manifest_text||""));const g=await persistManifest(ctx,run,m);const p=await ownProgress(ctx.user.id,run.id);return out(req,{ok:true,validated:true,score:m.score,note_5:m.note,sha256:m.sha,group_submission_id:g.group_submission.id,...p})}
  if(action==="teacher_open_session"){try{return out(req,{ok:true,session_window:await openOfficial(ctx,run)})}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_wall"){try{return out(req,await teacherWall(ctx,run))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_admin_overview"){try{return out(req,await teacherAdminOverview(ctx,run))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_user_detail"){try{return out(req,await teacherUserDetail(ctx,run,String(body.user_id||"")))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_set_enrollment"){try{return out(req,await teacherSetEnrollment(ctx,run,String(body.user_id||""),String(body.status||"")))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_add_existing"){try{return out(req,await teacherAddExisting(ctx,run,String(body.email||"")))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_reset_password"){try{return out(req,await teacherResetPassword(ctx,run,String(body.user_id||"")))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  if(action==="teacher_revoke_sessions"){try{return out(req,await teacherRevokeSessions(ctx,String(body.user_id||"")))}catch(e){if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);throw e}}
  return out(req,{error:"Acción desconocida"},400)
 }catch(e){return out(req,{error:String((e as any)?.message||e).slice(0,400)},400)}
});