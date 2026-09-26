import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);
const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const SUBMISSION_BUCKET="lms-submissions";
const MAX_FILE_BYTES=2*1024*1024;
const ALLOWED_FILE_MIME=new Set(["text/plain","text/csv","application/json","application/sql","application/octet-stream"]);
const ALLOWED=new Set(["https://jazaineam1.github.io"]);

function origin(req:Request){
  const o=req.headers.get("origin");
  if(!o)return "";
  if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;
  return null;
}
function headers(req:Request){
  const o=origin(req);
  return {
    "Access-Control-Allow-Origin":o||"https://jazaineam1.github.io",
    "Access-Control-Allow-Headers":"authorization, content-type",
    "Access-Control-Allow-Methods":"GET, POST, OPTIONS",
    "Vary":"Origin",
    "Cache-Control":"no-store",
    "X-Content-Type-Options":"nosniff",
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
async function current(req:Request){
  const token=bearer(req);if(!token)return null;
  const tokenHash=await sha256(token);
  const {data:s}=await db.from("lms_auth_sessions")
    .select("id,user_id,expires_at,revoked_at,persistent")
    .eq("token_hash",tokenHash).is("revoked_at",null).maybeSingle();
  if(!s)return null;
  if(!s.persistent&&(!s.expires_at||Date.parse(s.expires_at)<=Date.now()))return null;
  const {data:u}=await db.from("lms_users")
    .select("id,username,display_name,role,active,email")
    .eq("id",s.user_id).eq("active",true).maybeSingle();
  return u?{session:s,user:u}:null;
}
async function activeRun(ctx:any){
  const {data:memberships}=await db.from("lms_run_enrollments")
    .select("course_run_id,role,status,enrolled_at")
    .eq("user_id",ctx.user.id).eq("status","active")
    .order("enrolled_at",{ascending:false});
  for(const m of memberships||[]){
    const {data:r}=await db.from("lms_course_runs")
      .select("id,course_code,code,title,timezone,starts_on,ends_on,active")
      .eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:m.role};
  }
  if(["teacher","admin"].includes(ctx.user.role)){
    const {data:r}=await db.from("lms_course_runs")
      .select("id,course_code,code,title,timezone,starts_on,ends_on,active")
      .eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:ctx.user.role};
  }
  return null;
}
function isTeacher(ctx:any){return ["teacher","admin"].includes(ctx.user.role)}
function requireTeacher(ctx:any){if(!isTeacher(ctx))throw new Error("NO_AUTH")}
function clampText(v:any,max:number,required=false){
  const s=String(v??"").trim();
  if(required&&!s)throw new Error("Campo obligatorio");
  return s.slice(0,max);
}
function cleanUrl(v:any){
  const s=String(v??"").trim();
  if(!s)return null;
  if(s.startsWith("/")||s.startsWith("../")||s.startsWith("./"))return s.slice(0,1200);
  try{
    const u=new URL(s);
    if(!["http:","https:"].includes(u.protocol))throw new Error();
    return u.toString().slice(0,1200);
  }catch{throw new Error("URL no válida")}
}
function toIsoOrNull(v:any){
  if(v===null||v===undefined||v==="")return null;
  const d=new Date(String(v));
  if(!Number.isFinite(d.getTime()))throw new Error("Fecha no válida");
  return d.toISOString();
}
async function audit(actor:string,action:string,entity:string,id:string|null,metadata:any={}){
  await db.from("lms_audit_log").insert({
    actor_user_id:actor,action,entity_type:entity,entity_id:id,
    metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}
  }).then(()=>{}).catch(()=>{});
}

async function getHome(ctx:any,run:any,teacher=false){
  const now=new Date().toISOString();
  const [{data:sessions},{data:resources},{data:announcements},{data:assignments}] = await Promise.all([
    db.from("lms_run_sessions_v2").select("*").eq("course_run_id",run.id).order("position"),
    db.from("lms_run_resources_v2").select("*").eq("course_run_id",run.id).eq("visible",true).order("position"),
    db.from("lms_announcements").select("id,title,body,link,pinned,published_at,expires_at,created_at,updated_at")
      .eq("course_run_id",run.id).lte("published_at",now).order("pinned",{ascending:false}).order("published_at",{ascending:false}).limit(50),
    db.from("lms_assignments_v2").select("id,code,session_number,title,instructions,due_at,required,max_score,rubric,allowed_types,active,max_attempts,category,weight,created_at,updated_at")
      .eq("course_run_id",run.id).eq("active",true).order("due_at",{ascending:true})
  ]);
  const sessionRows=(sessions||[]).filter((s:any)=>teacher||s.status!=="draft");
  const allowed=new Set(sessionRows.map((s:any)=>s.session_number));
  const resourceRows=(resources||[]).filter((r:any)=>allowed.has(r.session_number));
  const activeAnnouncements=(announcements||[]).filter((a:any)=>!a.expires_at||Date.parse(a.expires_at)>Date.now());
  let submissions:any[]=[];
  if((assignments||[]).length){
    const ids=(assignments||[]).map((a:any)=>a.id);
    const {data}=await db.from("lms_submissions_v2")
      .select("id,assignment_id,attempt,artifact_type,status,submitted_at,score,feedback,reviewed_at")
      .eq("user_id",ctx.user.id).in("assignment_id",ids)
      .order("attempt",{ascending:false});
    submissions=data||[];
  }
  const latestByAssignment=new Map<string,any>();
  for(const s of submissions)if(!latestByAssignment.has(s.assignment_id))latestByAssignment.set(s.assignment_id,s);
  const assignmentRows=(assignments||[]).map((a:any)=>{
    const sub=latestByAssignment.get(a.id)||null;
    const overdue=!!a.due_at&&Date.parse(a.due_at)<Date.now()&&!sub;
    return {...a,submission:sub,overdue};
  });
  const nextAssignment=assignmentRows.find((a:any)=>!a.submission&&(!a.due_at||Date.parse(a.due_at)>=Date.now()))||null;
  const nextSession=sessionRows.find((s:any)=>s.status==="visible"&&(!s.starts_at||Date.parse(s.starts_at)>=Date.now()))||sessionRows.filter((s:any)=>s.status==="visible").at(-1)||null;
  return {
    viewer:ctx.user,run,
    sessions:sessionRows,resources:resourceRows,
    announcements:activeAnnouncements,
    assignments:assignmentRows,
    next_assignment:nextAssignment,
    next_session:nextSession,
    counts:{
      visible_sessions:sessionRows.filter((s:any)=>s.status==="visible").length,
      completed_assignments:assignmentRows.filter((a:any)=>a.submission&&a.submission.status!=="draft").length,
      pending_assignments:assignmentRows.filter((a:any)=>!a.submission).length,
      overdue_assignments:assignmentRows.filter((a:any)=>a.overdue).length
    }
  };
}
async function teacherOverview(ctx:any,run:any){
  requireTeacher(ctx);
  const home=await getHome(ctx,run,true);
  const [{data:allAnnouncements},{data:allAssignments}] = await Promise.all([
    db.from("lms_announcements").select("*").eq("course_run_id",run.id).order("created_at",{ascending:false}).limit(100),
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).order("session_number").order("created_at",{ascending:false}).limit(200)
  ]);
  return {...home,all_announcements:allAnnouncements||[],all_assignments:allAssignments||[]};
}
async function saveAnnouncement(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const id=clampText(body.id,80);
  const row:any={
    course_run_id:run.id,
    title:clampText(body.title,180,true),
    body:clampText(body.body,5000,true),
    link:cleanUrl(body.link),
    pinned:!!body.pinned,
    published_at:toIsoOrNull(body.published_at)||new Date().toISOString(),
    expires_at:toIsoOrNull(body.expires_at),
    created_by:ctx.user.id,
    updated_at:new Date().toISOString()
  };
  let saved:any,error:any;
  if(id){
    const x=await db.from("lms_announcements").update(row)
      .eq("id",id).eq("course_run_id",run.id).select("*").single();
    saved=x.data;error=x.error;
  }else{
    const x=await db.from("lms_announcements").insert(row).select("*").single();
    saved=x.data;error=x.error;
  }
  if(error)throw error;
  await audit(ctx.user.id,id?"bigdata.announcement.update":"bigdata.announcement.create","announcement",saved.id,{title:saved.title});
  return {ok:true,announcement:saved};
}
async function deleteAnnouncement(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const id=clampText(body.id,80,true);
  const {data,error}=await db.from("lms_announcements").delete()
    .eq("id",id).eq("course_run_id",run.id).select("id,title").maybeSingle();
  if(error)throw error;
  if(!data)throw new Error("Anuncio no encontrado");
  await audit(ctx.user.id,"bigdata.announcement.delete","announcement",id,{title:data.title});
  return {ok:true};
}
async function saveSession(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const n=Math.trunc(Number(body.session_number));
  if(!Number.isInteger(n)||n<1||n>99)throw new Error("Número de sesión inválido");
  const status=String(body.status||"draft");
  if(!["draft","visible","closed"].includes(status))throw new Error("Estado de sesión inválido");
  const title=clampText(body.title,220,true);
  const summary=clampText(body.summary,1200);
  const path=cleanUrl(body.path);
  const starts_at=toIsoOrNull(body.starts_at);
  const now=new Date().toISOString();
  const {data:prior}=await db.from("lms_run_sessions_v2")
    .select("session_number,status,published_at").eq("course_run_id",run.id).eq("session_number",n).maybeSingle();
  const row={
    course_run_id:run.id,session_number:n,title,summary,status,path,starts_at,
    position:n,updated_at:now,
    published_at:status==="visible"?(prior?.published_at||now):prior?.published_at||null
  };
  const {data,error}=await db.from("lms_run_sessions_v2").upsert(row,{onConflict:"course_run_id,session_number"}).select("*").single();
  if(error)throw error;
  await audit(ctx.user.id,"bigdata.session.save","course_session",String(n),{previous_status:prior?.status||null,new_status:status});
  return {ok:true,session:data};
}
async function saveResource(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const id=clampText(body.id,80);
  const n=Math.trunc(Number(body.session_number));
  if(!Number.isInteger(n)||n<1||n>99)throw new Error("Sesión inválida");
  const type=String(body.resource_type||"link");
  if(!["presentation","notebook","guide","reading","lab","link","evidence"].includes(type))throw new Error("Tipo de recurso inválido");
  const row:any={
    course_run_id:run.id,session_number:n,resource_type:type,
    title:clampText(body.title,220,true),summary:clampText(body.summary,1200),
    url:cleanUrl(body.url),position:Math.max(0,Math.trunc(Number(body.position||0))),
    visible:body.visible!==false,updated_at:new Date().toISOString()
  };
  if(!row.url)throw new Error("URL obligatoria");
  let saved:any,error:any;
  if(id){
    const x=await db.from("lms_run_resources_v2").update(row)
      .eq("id",id).eq("course_run_id",run.id).select("*").single();
    saved=x.data;error=x.error;
  }else{
    const x=await db.from("lms_run_resources_v2").insert(row).select("*").single();
    saved=x.data;error=x.error;
  }
  if(error)throw error;
  await audit(ctx.user.id,id?"bigdata.resource.update":"bigdata.resource.create","course_resource",saved.id,{session_number:n});
  return {ok:true,resource:saved};
}
async function deleteResource(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const id=clampText(body.id,80,true);
  const {data,error}=await db.from("lms_run_resources_v2").delete()
    .eq("id",id).eq("course_run_id",run.id).select("id,session_number,title").maybeSingle();
  if(error)throw error;
  if(!data)throw new Error("Recurso no encontrado");
  await audit(ctx.user.id,"bigdata.resource.delete","course_resource",id,{session_number:data.session_number,title:data.title});
  return {ok:true};
}


async function assignmentsForUser(ctx:any,run:any){
  const {data:assignments,error}=await db.from("lms_assignments_v2")
    .select("*").eq("course_run_id",run.id).eq("active",true).order("session_number").order("due_at",{ascending:true});
  if(error)throw error;
  const ids=(assignments||[]).map((x:any)=>x.id);
  if(!ids.length)return {viewer:ctx.user,run,assignments:[]};
  const [{data:subs},{data:accs}]=await Promise.all([
    db.from("lms_submissions_v2").select("*").eq("user_id",ctx.user.id).in("assignment_id",ids).order("attempt",{ascending:false}),
    db.from("lms_assignment_accommodations_v2").select("*").eq("user_id",ctx.user.id).in("assignment_id",ids)
  ]);
  const by=new Map<string,any[]>();for(const s of subs||[]){if(!by.has(s.assignment_id))by.set(s.assignment_id,[]);by.get(s.assignment_id)!.push(s)}
  const am=new Map((accs||[]).map((x:any)=>[x.assignment_id,x]));
  const rows=(assignments||[]).map((a:any)=>{
    const attempts=by.get(a.id)||[],latest=attempts[0]||null,acc:any=am.get(a.id)||{};
    const effective_due=acc.due_at||a.due_at||null,effective_max_attempts=Number(acc.max_attempts||a.max_attempts||1);
    const overdue=!!effective_due&&Date.parse(effective_due)<Date.now()&&!latest;
    const can_submit=attempts.length<effective_max_attempts&&(!effective_due||Date.parse(effective_due)>=Date.now());
    return {...a,effective_due,effective_max_attempts,attempts_used:attempts.length,latest_submission:latest,attempts,overdue,can_submit,accommodation:acc||null}
  });
  return {viewer:ctx.user,run,assignments:rows};
}
async function submitAssignment(ctx:any,run:any,body:any){
  const id=clampText(body.assignment_id,80,true);
  const {data:a}=await db.from("lms_assignments_v2").select("*").eq("id",id).eq("course_run_id",run.id).eq("active",true).maybeSingle();
  if(!a)throw new Error("Tarea no encontrada o no disponible");
  if(a.code==="bd-s08-control")throw new Error("S08 se entrega desde su validador de manifest, no desde este formulario");
  const {data:acc}=await db.from("lms_assignment_accommodations_v2").select("*").eq("assignment_id",id).eq("user_id",ctx.user.id).maybeSingle();
  const due=acc?.due_at||a.due_at||null,maxAttempts=Number(acc?.max_attempts||a.max_attempts||1);
  if(due&&Date.parse(due)<Date.now())throw new Error("La fecha de entrega ya venció para tu cuenta");
  const {data:prior}=await db.from("lms_submissions_v2").select("attempt").eq("assignment_id",id).eq("user_id",ctx.user.id).order("attempt",{ascending:false}).limit(1);
  const attempt=Number(prior?.[0]?.attempt||0)+1;if(attempt>maxAttempts)throw new Error("Ya usaste el máximo de intentos");
  const type=String(body.artifact_type||"text");
  if(!Array.isArray(a.allowed_types)||!a.allowed_types.includes(type))throw new Error("Tipo de entrega no permitido");
  let artifact:any={};
  if(type==="text")artifact={text:clampText(body.text,20000,true)};
  else if(type==="url"){const url=cleanUrl(body.url);if(!url)throw new Error("URL obligatoria");artifact={url}}
  else if(type==="file")throw new Error("Carga de archivo aún no está habilitada; usa texto o URL en esta tarea");
  else throw new Error("La evidencia automática solo puede generarla el sistema");
  const {data,error}=await db.from("lms_submissions_v2").insert({
    assignment_id:id,user_id:ctx.user.id,attempt,artifact_type:type,artifact,status:"submitted",submitted_at:new Date().toISOString()
  }).select("*").single();
  if(error)throw error;
  await audit(ctx.user.id,"bigdata.assignment.submit","submission",data.id,{assignment_id:id,attempt});
  return {ok:true,submission:data};
}
function cleanRubric(raw:any,maxScore:number){
  if(!Array.isArray(raw))return [];
  const out=[];let total=0;
  for(const x of raw.slice(0,20)){
    const title=clampText(x?.title,180,true),code=clampText(x?.code||title.toLowerCase().replace(/[^a-z0-9]+/g,"-"),80,true);
    const max=Number(x?.max);if(!Number.isFinite(max)||max<=0)throw new Error("Máximo de rúbrica inválido");
    total+=max;out.push({code,title,max});
  }
  if(out.length&&Math.abs(total-maxScore)>0.001)throw new Error("La suma de la rúbrica debe coincidir con el puntaje máximo");
  return out;
}
async function saveAssignment(ctx:any,run:any,body:any){
  requireTeacher(ctx);
  const id=clampText(body.id,80),code=clampText(body.code,80,true).toLowerCase();
  if(!/^[a-z0-9][a-z0-9_-]{2,79}$/.test(code))throw new Error("Código de tarea inválido");
  const n=body.session_number===null||body.session_number===""?null:Math.trunc(Number(body.session_number));
  if(n!==null){
    const {data:s}=await db.from("lms_run_sessions_v2").select("session_number").eq("course_run_id",run.id).eq("session_number",n).maybeSingle();
    if(!s)throw new Error("La sesión indicada no existe en esta cohorte");
  }
  const maxScore=Number(body.max_score||100);if(!Number.isFinite(maxScore)||maxScore<=0||maxScore>1000)throw new Error("Puntaje máximo inválido");
  const allowed=(Array.isArray(body.allowed_types)?body.allowed_types:[]).filter((x:any)=>["text","url","file","evidence"].includes(String(x)));
  if(!allowed.length)throw new Error("Selecciona al menos un tipo de entrega");
  const maxAttempts=Math.trunc(Number(body.max_attempts||1));if(maxAttempts<1||maxAttempts>20)throw new Error("Intentos inválidos");
  const row:any={course_run_id:run.id,code,session_number:n,title:clampText(body.title,180,true),instructions:clampText(body.instructions,8000),
    due_at:toIsoOrNull(body.due_at),required:body.required!==false,max_score:maxScore,rubric:cleanRubric(body.rubric,maxScore),
    allowed_types:allowed,active:body.active!==false,max_attempts:maxAttempts,category:clampText(body.category||"coursework",80,true),
    weight:Math.max(0,Number(body.weight??1)),updated_at:new Date().toISOString()};
  let saved:any,error:any;
  if(id){
    const x=await db.from("lms_assignments_v2").update(row).eq("id",id).eq("course_run_id",run.id).select("*").single();saved=x.data;error=x.error;
  }else{
    row.created_by=ctx.user.id;const x=await db.from("lms_assignments_v2").insert(row).select("*").single();saved=x.data;error=x.error;
  }
  if(error)throw error;await audit(ctx.user.id,id?"bigdata.assignment.update":"bigdata.assignment.create","assignment",saved.id,{code:saved.code});
  return {ok:true,assignment:saved};
}
async function setAccommodation(ctx:any,run:any,body:any){
  requireTeacher(ctx);const assignmentId=clampText(body.assignment_id,80,true),userId=clampText(body.user_id,80,true);
  const {data:a}=await db.from("lms_assignments_v2").select("id").eq("id",assignmentId).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Tarea no encontrada");
  const {data:e}=await db.from("lms_run_enrollments").select("user_id").eq("course_run_id",run.id).eq("user_id",userId).maybeSingle();if(!e)throw new Error("Estudiante fuera de la cohorte");
  const due=toIsoOrNull(body.due_at),max=body.max_attempts?Math.trunc(Number(body.max_attempts)):null;if(max!==null&&(max<1||max>20))throw new Error("Intentos inválidos");
  const {data,error}=await db.from("lms_assignment_accommodations_v2").upsert({
    assignment_id:assignmentId,user_id:userId,due_at:due,max_attempts:max,notes:clampText(body.notes,1000),updated_by:ctx.user.id,updated_at:new Date().toISOString()
  },{onConflict:"assignment_id,user_id"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.assignment.accommodation","assignment_accommodation",assignmentId,{user_id:userId});
  return {ok:true,accommodation:data};
}
async function gradebook(ctx:any,run:any){
  requireTeacher(ctx);
  const [{data:assignments},{data:enrollments}]=await Promise.all([
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).order("session_number").order("created_at"),
    db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id)
  ]);
  const studentIds=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const assignmentIds=(assignments||[]).map((x:any)=>x.id);
  const [{data:users},{data:subs},{data:accs}]=await Promise.all([
    studentIds.length?db.from("lms_users").select("id,display_name,username,email,active").in("id",studentIds):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_submissions_v2").select("*").in("assignment_id",assignmentIds).order("attempt",{ascending:false}):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_assignment_accommodations_v2").select("*").in("assignment_id",assignmentIds):Promise.resolve({data:[]} as any)
  ]);
  return {viewer:ctx.user,run,assignments:assignments||[],students:users||[],submissions:subs||[],accommodations:accs||[]};
}
async function gradeSubmission(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=clampText(body.submission_id,80,true);
  const {data:s}=await db.from("lms_submissions_v2").select("*").eq("id",id).maybeSingle();if(!s)throw new Error("Entrega no encontrada");
  const {data:a}=await db.from("lms_assignments_v2").select("*").eq("id",s.assignment_id).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Entrega fuera de Big Data");
  const score=Number(body.score);if(!Number.isFinite(score)||score<0||score>Number(a.max_score))throw new Error("Nota fuera del rango permitido");
  const feedback=clampText(body.feedback,10000),rubricScores=body.rubric_scores&&typeof body.rubric_scores==="object"?body.rubric_scores:{};
  const now=new Date().toISOString();
  const {error:hError}=await db.from("lms_grade_history_v2").insert({
    submission_id:s.id,assignment_id:s.assignment_id,user_id:s.user_id,actor_user_id:ctx.user.id,
    previous_score:s.score,new_score:score,previous_feedback:s.feedback,new_feedback:feedback,rubric_scores:rubricScores,created_at:now
  });if(hError)throw hError;
  const {data,error}=await db.from("lms_submissions_v2").update({score,feedback,rubric_scores:rubricScores,status:"reviewed",reviewed_by:ctx.user.id,reviewed_at:now})
    .eq("id",s.id).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.submission.grade","submission",id,{assignment_id:s.assignment_id,user_id:s.user_id,score});
  return {ok:true,submission:data};
}
async function gradeHistory(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=clampText(body.submission_id,80,true);
  const {data:s}=await db.from("lms_submissions_v2").select("assignment_id").eq("id",id).maybeSingle();if(!s)throw new Error("Entrega no encontrada");
  const {data:a}=await db.from("lms_assignments_v2").select("id").eq("id",s.assignment_id).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Entrega fuera de Big Data");
  const {data}=await db.from("lms_grade_history_v2").select("*").eq("submission_id",id).order("created_at",{ascending:false});
  return {history:data||[]};
}


async function competencyContext(run:any){
  const [{data:competencies},{data:mappings},{data:assignments}] = await Promise.all([
    db.from("lms_competencies_v2").select("*").eq("course_run_id",run.id).order("position"),
    db.from("lms_assignment_competencies_v2").select("*").eq("course_run_id",run.id),
    db.from("lms_assignments_v2").select("id,code,title,max_score,rubric,active").eq("course_run_id",run.id)
  ]);
  return {competencies:competencies||[],mappings:mappings||[],assignments:assignments||[]};
}
function computeCompetencyRows(context:any,submissions:any[]){
  const assignmentMap=new Map((context.assignments||[]).map((a:any)=>[a.id,a]));
  const latest=new Map<string,any>();
  for(const s of (submissions||[]).sort((a:any,b:any)=>Number(b.attempt)-Number(a.attempt))){
    if(s.score==null)continue;
    if(!latest.has(s.assignment_id))latest.set(s.assignment_id,s);
  }
  return (context.competencies||[]).filter((c:any)=>c.active).map((comp:any)=>{
    const maps=(context.mappings||[]).filter((m:any)=>m.competency_code===comp.code);
    const evidence:any[]=[];
    for(const m of maps){
      const a:any=assignmentMap.get(m.assignment_id),s:any=latest.get(m.assignment_id);
      if(!a||!s)continue;
      let score:number|null=null,max:number|null=null,label="Puntaje total";
      if(m.rubric_code&&m.rubric_code!=="__overall__"){
        const criterion=(Array.isArray(a.rubric)?a.rubric:[]).find((x:any)=>String(x.code)===String(m.rubric_code));
        const raw=s.rubric_scores?.[m.rubric_code];
        if(criterion&&raw!==undefined&&raw!==null){score=Number(raw);max=Number(criterion.max);label=criterion.title||m.rubric_code}
      }else if(s.score!==null&&s.score!==undefined){score=Number(s.score);max=Number(a.max_score)}
      if(score===null||max===null||!Number.isFinite(score)||!Number.isFinite(max)||max<=0)continue;
      evidence.push({assignment_id:a.id,assignment_code:a.code,assignment_title:a.title,rubric_code:m.rubric_code,label,score,max,pct:Math.max(0,Math.min(100,100*score/max)),weight:Number(m.weight||1),attempt:s.attempt,reviewed_at:s.reviewed_at,submitted_at:s.submitted_at});
    }
    const totalWeight=evidence.reduce((z:number,e:any)=>z+e.weight,0);
    const mastery_pct=totalWeight?evidence.reduce((z:number,e:any)=>z+e.pct*e.weight,0)/totalWeight:null;
    const enough=evidence.length>=Number(comp.min_evidence_count||1);
    const status=!evidence.length?"pending":(enough&&Number(mastery_pct)>=Number(comp.mastery_threshold)?"mastered":"developing");
    return {...comp,mastery_pct:mastery_pct===null?null:Math.round(mastery_pct*10)/10,evidence_count:evidence.length,status,evidence};
  });
}
async function competenciesForUser(ctx:any,run:any){
  const context=await competencyContext(run);
  const assignmentIds=(context.assignments||[]).map((a:any)=>a.id);
  const {data:subs}=assignmentIds.length?await db.from("lms_submissions_v2").select("*").eq("user_id",ctx.user.id).in("assignment_id",assignmentIds):({data:[]} as any);
  return {viewer:ctx.user,run,competencies:computeCompetencyRows(context,subs||[])};
}
async function teacherCompetencies(ctx:any,run:any){
  requireTeacher(ctx);const context=await competencyContext(run);
  const {data:enrollments}=await db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id);
  const studentIds=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const assignmentIds=(context.assignments||[]).map((a:any)=>a.id);
  const [{data:users},{data:subs}]=await Promise.all([
    studentIds.length?db.from("lms_users").select("id,display_name,username,email,active").in("id",studentIds):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_submissions_v2").select("*").in("assignment_id",assignmentIds):Promise.resolve({data:[]} as any)
  ]);
  const byUser=new Map<string,any[]>();for(const s of subs||[]){if(!byUser.has(s.user_id))byUser.set(s.user_id,[]);byUser.get(s.user_id)!.push(s)}
  const students=(users||[]).map((u:any)=>({...u,competencies:computeCompetencyRows(context,byUser.get(u.id)||[])}));
  return {viewer:ctx.user,run,...context,students};
}
async function saveCompetency(ctx:any,run:any,body:any){
  requireTeacher(ctx);const code=clampText(body.code,80,true).toUpperCase();
  if(!/^[A-Z0-9][A-Z0-9_-]{2,79}$/.test(code))throw new Error("Código de competencia inválido");
  const threshold=Number(body.mastery_threshold??80),minCount=Math.trunc(Number(body.min_evidence_count??1));
  if(!Number.isFinite(threshold)||threshold<0||threshold>100)throw new Error("Umbral inválido");
  if(minCount<1||minCount>20)throw new Error("Número mínimo de evidencias inválido");
  const row={course_run_id:run.id,code,domain:clampText(body.domain,120,true),title:clampText(body.title,220,true),description:clampText(body.description,2000),position:Math.max(0,Math.trunc(Number(body.position||0))),mastery_threshold:threshold,min_evidence_count:minCount,active:body.active!==false,updated_at:new Date().toISOString()};
  const {data,error}=await db.from("lms_competencies_v2").upsert(row,{onConflict:"course_run_id,code"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.competency.save","competency",code,{threshold,min_evidence_count:minCount});
  return {ok:true,competency:data};
}
async function mapCompetency(ctx:any,run:any,body:any){
  requireTeacher(ctx);const assignmentId=clampText(body.assignment_id,80,true),code=clampText(body.competency_code,80,true).toUpperCase();
  const rubricCode=clampText(body.rubric_code||"__overall__",80,true),weight=Number(body.weight||1);
  if(!Number.isFinite(weight)||weight<=0)throw new Error("Peso inválido");
  const [{data:a},{data:comp}]=await Promise.all([
    db.from("lms_assignments_v2").select("id,rubric").eq("id",assignmentId).eq("course_run_id",run.id).maybeSingle(),
    db.from("lms_competencies_v2").select("code").eq("course_run_id",run.id).eq("code",code).maybeSingle()
  ]);
  if(!a||!comp)throw new Error("Tarea o competencia no pertenece a esta cohorte");
  if(rubricCode!=="__overall__"&&!(Array.isArray(a.rubric)&&a.rubric.some((x:any)=>String(x.code)===rubricCode)))throw new Error("El criterio de rúbrica no existe");
  const {data,error}=await db.from("lms_assignment_competencies_v2").upsert({assignment_id:assignmentId,course_run_id:run.id,competency_code:code,rubric_code:rubricCode,weight},{onConflict:"assignment_id,competency_code,rubric_code"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.competency.map","competency_mapping",code,{assignment_id:assignmentId,rubric_code:rubricCode});
  return {ok:true,mapping:data};
}
async function unmapCompetency(ctx:any,run:any,body:any){
  requireTeacher(ctx);const assignmentId=clampText(body.assignment_id,80,true),code=clampText(body.competency_code,80,true).toUpperCase(),rubricCode=clampText(body.rubric_code||"__overall__",80,true);
  const {error}=await db.from("lms_assignment_competencies_v2").delete().eq("assignment_id",assignmentId).eq("course_run_id",run.id).eq("competency_code",code).eq("rubric_code",rubricCode);if(error)throw error;
  await audit(ctx.user.id,"bigdata.competency.unmap","competency_mapping",code,{assignment_id:assignmentId,rubric_code:rubricCode});
  return {ok:true};
}


function maxIso(values:any[]){
  const xs=values.filter(Boolean).map(v=>Date.parse(String(v))).filter(Number.isFinite);
  return xs.length?new Date(Math.max(...xs)).toISOString():null;
}
async function analyticsContext(run:any,userIds:string[]){
  const comp=await competencyContext(run);
  const [{data:assignments},{data:subs},{data:s08},{data:rules}]=await Promise.all([
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).eq("active",true),
    userIds.length?db.from("lms_submissions_v2").select("*").in("user_id",userIds).in("assignment_id",(comp.assignments||[]).map((a:any)=>a.id)):Promise.resolve({data:[]} as any),
    userIds.length?db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",8).in("user_id",userIds):Promise.resolve({data:[]} as any),
    db.from("lms_alert_rules_v2").select("*").eq("course_run_id",run.id).eq("active",true).order("position")
  ]);
  return {comp,assignments:assignments||[],subs:subs||[],s08:s08||[],rules:rules||[]};
}
function evaluateAlerts(metrics:any,rules:any[],studentView=false){
  const alerts:any[]=[];
  for(const r of rules||[]){
    const p=r.params||{};
    if(r.rule_type==="inactivity_days"){
      const days=Math.max(1,Number(p.days||7));
      const age=metrics.last_activity_at?(Date.now()-Date.parse(metrics.last_activity_at))/86400000:null;
      if(age===null||age>=days)alerts.push({code:r.code,title:r.title,kind:"student",evidence:age===null?"Sin actividad académica registrada":Math.floor(age)+" días desde la última actividad registrada",rule:"≥ "+days+" días"});
    }else if(r.rule_type==="overdue_assignments"){
      const n=Math.max(1,Number(p.count||1));if(metrics.overdue_count>=n)alerts.push({code:r.code,title:r.title,kind:"student",evidence:metrics.overdue_count+" entrega(s) vencida(s) sin entrega",rule:"≥ "+n});
    }else if(r.rule_type==="mastery_below"){
      const pct=Number(p.pct??60),min=Number(p.min_evidence??1);
      if(metrics.competency_evidence_count>=min&&metrics.mastery_avg!==null&&metrics.mastery_avg<pct)alerts.push({code:r.code,title:r.title,kind:"student",evidence:"Promedio de dominio "+Number(metrics.mastery_avg).toFixed(1)+"% con "+metrics.competency_evidence_count+" evidencia(s)",rule:"< "+pct+"%"});
    }else if(r.rule_type==="unreviewed_submissions"){
      const n=Math.max(1,Number(p.count||1));if(metrics.unreviewed_count>=n)alerts.push({code:r.code,title:r.title,kind:"teacher",evidence:metrics.unreviewed_count+" entrega(s) esperando revisión docente",rule:"≥ "+n});
    }
  }
  return studentView?alerts.filter(x=>x.kind!=="teacher"):alerts;
}
function metricsForUser(userId:string,context:any){
  const userSubs=(context.subs||[]).filter((s:any)=>s.user_id===userId).sort((a:any,b:any)=>Number(b.attempt)-Number(a.attempt));
  const latest=new Map<string,any>();for(const s of userSubs)if(!latest.has(s.assignment_id))latest.set(s.assignment_id,s);
  let pending=0,overdue=0,reviewed=0,unreviewed=0;
  const now=Date.now();
  for(const a of context.assignments||[]){
    const s=latest.get(a.id);
    if(!s){pending++;if(a.due_at&&Date.parse(a.due_at)<now)overdue++}
    else if(s.status==="reviewed")reviewed++;else if(["submitted","returned"].includes(s.status))unreviewed++;
  }
  const s08=(context.s08||[]).find((x:any)=>x.user_id===userId)||{};
  const comps=computeCompetencyRows(context.comp,userSubs);
  const withEvidence=comps.filter((x:any)=>x.mastery_pct!==null);
  const mastery=withEvidence.length?withEvidence.reduce((z:number,x:any)=>z+Number(x.mastery_pct),0)/withEvidence.length:null;
  const last=maxIso([s08.last_activity_at,...userSubs.map((s:any)=>s.submitted_at),...userSubs.map((s:any)=>s.reviewed_at)]);
  return {
    user_id:userId,last_activity_at:last,pending_count:pending,overdue_count:overdue,reviewed_count:reviewed,unreviewed_count:unreviewed,
    mastery_avg:mastery===null?null:Math.round(mastery*10)/10,mastered_count:comps.filter((x:any)=>x.status==="mastered").length,
    competency_evidence_count:comps.reduce((z:number,x:any)=>z+Number(x.evidence_count||0),0),competencies:comps,
    active_seconds_s08:Number(s08.active_seconds||0)
  };
}
async function saveSnapshot(run:any,m:any){
  const date=new Intl.DateTimeFormat("en-CA",{timeZone:"America/Bogota",year:"numeric",month:"2-digit",day:"2-digit"}).format(new Date());
  await db.from("lms_student_snapshots_v2").upsert({
    course_run_id:run.id,user_id:m.user_id,snapshot_date:date,last_activity_at:m.last_activity_at,
    pending_count:m.pending_count,overdue_count:m.overdue_count,reviewed_count:m.reviewed_count,
    mastery_avg:m.mastery_avg,mastered_count:m.mastered_count,active_seconds_s08:m.active_seconds_s08,created_at:new Date().toISOString()
  },{onConflict:"course_run_id,user_id,snapshot_date"}).then(()=>{}).catch(()=>{});
}
async function analyticsForUser(ctx:any,run:any){
  const context=await analyticsContext(run,[ctx.user.id]),m=metricsForUser(ctx.user.id,context);await saveSnapshot(run,m);
  const {data:history}=await db.from("lms_student_snapshots_v2").select("*").eq("course_run_id",run.id).eq("user_id",ctx.user.id).order("snapshot_date",{ascending:false}).limit(30);
  return {viewer:ctx.user,run,metrics:m,alerts:evaluateAlerts(m,context.rules,true),history:(history||[]).reverse(),rules:context.rules.filter((r:any)=>r.rule_type!=="unreviewed_submissions")};
}
async function teacherAnalytics(ctx:any,run:any){
  requireTeacher(ctx);
  const {data:enrollments}=await db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id);
  const ids=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const context=await analyticsContext(run,ids);
  const [{data:users},{data:interventions},{data:activityRows}]=await Promise.all([
    ids.length?db.from("lms_users").select("id,display_name,username,email,active").in("id",ids):Promise.resolve({data:[]} as any),
    db.from("lms_interventions_v2").select("*").eq("course_run_id",run.id).order("created_at",{ascending:false}).limit(500),
    db.from("bd_lms_activity_progress").select("user_id,activity_code,status,score,max_score,started_at,completed_at").eq("course_run_id",run.id)
  ]);
  const students=[];
  for(const u of users||[]){const m=metricsForUser(u.id,context);await saveSnapshot(run,m);students.push({...u,...m,alerts:evaluateAlerts(m,context.rules,false),open_interventions:(interventions||[]).filter((x:any)=>x.user_id===u.id&&x.status==="open")})}
  const frictionMap=new Map<string,any>();
  for(const a of activityRows||[]){if(!frictionMap.has(a.activity_code))frictionMap.set(a.activity_code,{activity_code:a.activity_code,started:0,evaluated:0,completed:0,score_sum:0,score_n:0});const z=frictionMap.get(a.activity_code);if(a.started_at)z.started++;if(["submitted","completed"].includes(a.status))z.evaluated++;if(a.status==="completed")z.completed++;if(a.max_score>0){z.score_sum+=100*Number(a.score||0)/Number(a.max_score);z.score_n++}}
  const friction=[...frictionMap.values()].map(z=>({...z,avg_pct:z.score_n?Math.round(10*z.score_sum/z.score_n)/10:null}));
  return {viewer:ctx.user,run,students,rules:context.rules,interventions:interventions||[],friction,
    summary:{students:students.length,students_with_student_alerts:students.filter((s:any)=>s.alerts.some((a:any)=>a.kind==="student")).length,unreviewed:students.reduce((z:number,s:any)=>z+s.unreviewed_count,0),open_interventions:(interventions||[]).filter((x:any)=>x.status==="open").length}};
}
async function saveAlertRule(ctx:any,run:any,body:any){
  requireTeacher(ctx);const code=clampText(body.code,80,true).toLowerCase(),type=String(body.rule_type||"");
  if(!/^[a-z0-9][a-z0-9_-]{2,79}$/.test(code))throw new Error("Código de regla inválido");
  if(!["inactivity_days","overdue_assignments","mastery_below","unreviewed_submissions"].includes(type))throw new Error("Tipo de regla inválido");
  const params=body.params&&typeof body.params==="object"?body.params:{};
  const row={course_run_id:run.id,code,title:clampText(body.title,180,true),description:clampText(body.description,1200),rule_type:type,params,active:body.active!==false,position:Math.max(0,Math.trunc(Number(body.position||0))),updated_by:ctx.user.id,updated_at:new Date().toISOString()};
  const {data,error}=await db.from("lms_alert_rules_v2").upsert(row,{onConflict:"course_run_id,code"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.alert_rule.save","alert_rule",code,{rule_type:type,params});return {ok:true,rule:data};
}
async function createIntervention(ctx:any,run:any,body:any){
  requireTeacher(ctx);const userId=clampText(body.user_id,80,true),note=clampText(body.note,4000,true);
  const {data:e}=await db.from("lms_run_enrollments").select("user_id").eq("course_run_id",run.id).eq("user_id",userId).maybeSingle();if(!e)throw new Error("Estudiante fuera de la cohorte");
  const {data,error}=await db.from("lms_interventions_v2").insert({course_run_id:run.id,user_id:userId,created_by:ctx.user.id,kind:clampText(body.kind||"follow_up",80,true),note,status:"open",follow_up_at:toIsoOrNull(body.follow_up_at)}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.intervention.create","intervention",data.id,{user_id:userId,kind:data.kind});return {ok:true,intervention:data};
}
async function resolveIntervention(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=clampText(body.id,80,true),now=new Date().toISOString();
  const {data,error}=await db.from("lms_interventions_v2").update({status:"resolved",resolved_at:now,resolved_by:ctx.user.id}).eq("id",id).eq("course_run_id",run.id).select("*").maybeSingle();if(error)throw error;if(!data)throw new Error("Intervención no encontrada");
  await audit(ctx.user.id,"bigdata.intervention.resolve","intervention",id,{user_id:data.user_id});return {ok:true,intervention:data};
}


async function groupIdsForUser(runId:string,userId:string){
  const {data:members}=await db.from("lms_group_members_v2").select("group_id").eq("user_id",userId);
  const ids=(members||[]).map((x:any)=>x.group_id);if(!ids.length)return [];
  const {data:groups}=await db.from("lms_groups_v2").select("id").eq("course_run_id",runId).eq("active",true).in("id",ids);
  return (groups||[]).map((x:any)=>x.id);
}
async function collaborationOverview(ctx:any,run:any){
  const ownGroupIds=await groupIdsForUser(run.id,ctx.user.id);
  const [{data:groups},{data:members},{data:settings},{data:assignments},{data:groupSubs},{data:threads},{data:posts}] = await Promise.all([
    ownGroupIds.length?db.from("lms_groups_v2").select("*").eq("course_run_id",run.id).in("id",ownGroupIds):Promise.resolve({data:[]} as any),
    ownGroupIds.length?db.from("lms_group_members_v2").select("*").in("group_id",ownGroupIds):Promise.resolve({data:[]} as any),
    db.from("lms_assignment_group_settings_v2").select("*").eq("enabled",true),
    db.from("lms_assignments_v2").select("id,code,title,session_number,due_at,max_score,max_attempts,rubric,allowed_types,active").eq("course_run_id",run.id).eq("active",true),
    ownGroupIds.length?db.from("lms_group_submissions_v2").select("*").in("group_id",ownGroupIds).order("submitted_at",{ascending:false}):Promise.resolve({data:[]} as any),
    db.from("lms_discussion_threads_v2").select("*").eq("course_run_id",run.id).order("pinned",{ascending:false}).order("created_at",{ascending:false}).limit(60),
    db.from("lms_discussion_posts_v2").select("*").eq("hidden",false).order("created_at").limit(500)
  ]);
  const threadIds=new Set((threads||[]).map((t:any)=>t.id));
  const postRows=(posts||[]).filter((p:any)=>threadIds.has(p.thread_id));
  const postIds=postRows.map((p:any)=>p.id);
  const {data:mentions}=postIds.length?await db.from("lms_discussion_mentions_v2").select("post_id,mentioned_user_id,created_at,read_at").eq("mentioned_user_id",ctx.user.id).in("post_id",postIds).order("created_at",{ascending:false}):({data:[]} as any);
  const visibleUserIds=[...new Set([...(members||[]).map((x:any)=>x.user_id),...postRows.map((x:any)=>x.user_id)])];
  const {data:users}=visibleUserIds.length?await db.from("lms_users").select("id,display_name,username").in("id",visibleUserIds):({data:[]} as any);
  const assignmentMap=new Map((assignments||[]).map((a:any)=>[a.id,a]));
  const settingRows=(settings||[]).filter((s:any)=>assignmentMap.has(s.assignment_id));
  const peerTargets:any[]=[];
  for(const setting of settingRows.filter((x:any)=>x.peer_review_enabled)){
    const {data:candidates}=await db.from("lms_group_submissions_v2").select("*").eq("assignment_id",setting.assignment_id).in("status",["submitted","reviewed"]).order("submitted_at",{ascending:false});
    const {data:done}=await db.from("lms_peer_reviews_v2").select("reviewee_submission_id").eq("assignment_id",setting.assignment_id).eq("reviewer_user_id",ctx.user.id);
    const doneSet=new Set((done||[]).map((x:any)=>x.reviewee_submission_id));
    const eligible=(candidates||[]).filter((x:any)=>!ownGroupIds.includes(x.group_id)&&!doneSet.has(x.id));
    for(const x of eligible.slice(0,Number(setting.reviews_per_student||1)))peerTargets.push({
      id:x.id,assignment_id:x.assignment_id,attempt:x.attempt,artifact_type:x.artifact_type,artifact:x.artifact,status:x.status,submitted_at:x.submitted_at,
      assignment:assignmentMap.get(setting.assignment_id),
      peer_setting:{assignment_id:setting.assignment_id,peer_review_enabled:setting.peer_review_enabled,reviews_per_student:setting.reviews_per_student,peer_rubric:setting.peer_rubric,anonymous_peer_review:setting.anonymous_peer_review}
    });
  }
  return {viewer:ctx.user,run,groups:groups||[],members:members||[],member_users:users||[],users:users||[],settings:settingRows,assignments:assignments||[],group_submissions:groupSubs||[],threads:threads||[],posts:postRows,mentions:mentions||[],peer_targets:peerTargets};
}
async function markMentionsRead(ctx:any,run:any){
  const {data:threads}=await db.from("lms_discussion_threads_v2").select("id").eq("course_run_id",run.id);
  const ids=(threads||[]).map((x:any)=>x.id);if(!ids.length)return {ok:true,count:0};
  const now=new Date().toISOString();
  const {data,error}=await db.from("lms_discussion_mentions_v2").update({read_at:now}).eq("mentioned_user_id",ctx.user.id).is("read_at",null).in("thread_id",ids).select("id");
  if(error)throw error;return {ok:true,count:(data||[]).length,read_at:now};
}

async function teacherCollaboration(ctx:any,run:any){
  requireTeacher(ctx);
  const [{data:groups},{data:members},{data:settings},{data:assignments},{data:subs},{data:enrollments},{data:threads},{data:posts},{data:reviews},{data:contributions}] = await Promise.all([
    db.from("lms_groups_v2").select("*").eq("course_run_id",run.id).order("name"),
    db.from("lms_group_members_v2").select("*"),
    db.from("lms_assignment_group_settings_v2").select("*"),
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).order("session_number"),
    db.from("lms_group_submissions_v2").select("*").order("submitted_at",{ascending:false}).limit(500),
    db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id),
    db.from("lms_discussion_threads_v2").select("*").eq("course_run_id",run.id).order("pinned",{ascending:false}).order("created_at",{ascending:false}),
    db.from("lms_discussion_posts_v2").select("*").order("created_at").limit(1000),
    db.from("lms_peer_reviews_v2").select("*").order("submitted_at",{ascending:false}).limit(1000),
    db.from("lms_group_contributions_v2").select("*").order("confirmed_at",{ascending:false}).limit(2000)
  ]);
  const groupIds=new Set((groups||[]).map((g:any)=>g.id));
  const threadIds=new Set((threads||[]).map((t:any)=>t.id));
  const postRows=(posts||[]).filter((p:any)=>threadIds.has(p.thread_id));
  const memberRows=(members||[]).filter((m:any)=>groupIds.has(m.group_id));
  const assignmentIds=new Set((assignments||[]).map((a:any)=>a.id));
  const settingRows=(settings||[]).filter((s:any)=>assignmentIds.has(s.assignment_id));
  const subRows=(subs||[]).filter((s:any)=>assignmentIds.has(s.assignment_id)&&groupIds.has(s.group_id));
  const reviewRows=(reviews||[]).filter((r:any)=>assignmentIds.has(r.assignment_id));
  const subIds=new Set(subRows.map((s:any)=>s.id));
  const contributionRows=(contributions||[]).filter((x:any)=>subIds.has(x.group_submission_id));
  const ids=[...new Set([...(enrollments||[]).map((x:any)=>x.user_id),...memberRows.map((x:any)=>x.user_id)])];
  const {data:users}=ids.length?await db.from("lms_users").select("id,display_name,username,email,active").in("id",ids):({data:[]} as any);
  return {viewer:ctx.user,run,groups:groups||[],members:memberRows,settings:settingRows,assignments:assignments||[],group_submissions:subRows,students:(users||[]).filter((u:any)=>(enrollments||[]).some((e:any)=>e.user_id===u.id&&e.role==="student")),users:users||[],threads:threads||[],posts:postRows,peer_reviews:reviewRows,contributions:contributionRows};
}
async function createGroup(ctx:any,run:any,body:any){
  requireTeacher(ctx);const name=clampText(body.name,120,true),description=clampText(body.description,1000);
  const {data,error}=await db.from("lms_groups_v2").insert({course_run_id:run.id,name,description,created_by:ctx.user.id}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.group.create","group",data.id,{name});return {ok:true,group:data};
}
async function addGroupMember(ctx:any,run:any,body:any){
  requireTeacher(ctx);const groupId=clampText(body.group_id,80,true),userId=clampText(body.user_id,80,true),role=String(body.role||"member");
  if(!["member","lead"].includes(role))throw new Error("Rol de equipo inválido");
  const [{data:g},{data:e}]=await Promise.all([
    db.from("lms_groups_v2").select("id").eq("id",groupId).eq("course_run_id",run.id).eq("active",true).maybeSingle(),
    db.from("lms_run_enrollments").select("user_id").eq("course_run_id",run.id).eq("user_id",userId).eq("status","active").maybeSingle()
  ]);if(!g||!e)throw new Error("Equipo o estudiante fuera de la cohorte");
  const {data,error}=await db.from("lms_group_members_v2").upsert({group_id:groupId,user_id:userId,role},{onConflict:"group_id,user_id"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.group.member.add","group_member",groupId,{user_id:userId,role});return {ok:true,member:data};
}
async function removeGroupMember(ctx:any,run:any,body:any){
  requireTeacher(ctx);const groupId=clampText(body.group_id,80,true),userId=clampText(body.user_id,80,true);
  const {data:g}=await db.from("lms_groups_v2").select("id").eq("id",groupId).eq("course_run_id",run.id).maybeSingle();if(!g)throw new Error("Equipo fuera de la cohorte");
  const {error}=await db.from("lms_group_members_v2").delete().eq("group_id",groupId).eq("user_id",userId);if(error)throw error;
  await audit(ctx.user.id,"bigdata.group.member.remove","group_member",groupId,{user_id:userId});return {ok:true};
}
async function saveGroupSetting(ctx:any,run:any,body:any){
  requireTeacher(ctx);const assignmentId=clampText(body.assignment_id,80,true);
  const {data:a}=await db.from("lms_assignments_v2").select("id").eq("id",assignmentId).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Tarea fuera de la cohorte");
  const n=Math.max(1,Math.min(5,Math.trunc(Number(body.reviews_per_student||1))));
  const rubric=Array.isArray(body.peer_rubric)?body.peer_rubric.slice(0,20).map((x:any,i:number)=>({code:clampText(x.code||"p"+(i+1),80,true),title:clampText(x.title,180,true),max:Number(x.max||0)})).filter((x:any)=>x.max>0):[];
  const {data,error}=await db.from("lms_assignment_group_settings_v2").upsert({assignment_id:assignmentId,enabled:body.enabled!==false,peer_review_enabled:!!body.peer_review_enabled,reviews_per_student:n,peer_rubric:rubric,anonymous_peer_review:!!body.anonymous_peer_review,updated_by:ctx.user.id,updated_at:new Date().toISOString()},{onConflict:"assignment_id"}).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.group.setting.save","group_assignment",assignmentId,{peer_review_enabled:data.peer_review_enabled});return {ok:true,setting:data};
}
async function groupSubmit(ctx:any,run:any,body:any){
  const assignmentId=clampText(body.assignment_id,80,true),groupId=clampText(body.group_id,80,true);
  const [{data:a},{data:setting},{data:g},{data:membership}]=await Promise.all([
    db.from("lms_assignments_v2").select("*").eq("id",assignmentId).eq("course_run_id",run.id).eq("active",true).maybeSingle(),
    db.from("lms_assignment_group_settings_v2").select("*").eq("assignment_id",assignmentId).eq("enabled",true).maybeSingle(),
    db.from("lms_groups_v2").select("*").eq("id",groupId).eq("course_run_id",run.id).eq("active",true).maybeSingle(),
    db.from("lms_group_members_v2").select("*").eq("group_id",groupId).eq("user_id",ctx.user.id).maybeSingle()
  ]);if(!a||!setting||!g||!membership)throw new Error("Entrega grupal no disponible para tu equipo");
  if(a.due_at&&Date.parse(a.due_at)<Date.now())throw new Error("La fecha de entrega grupal ya venció");
  const {data:prior}=await db.from("lms_group_submissions_v2").select("attempt").eq("assignment_id",assignmentId).eq("group_id",groupId).order("attempt",{ascending:false}).limit(1);
  const attempt=Number(prior?.[0]?.attempt||0)+1;if(attempt>Number(a.max_attempts||1))throw new Error("El equipo ya usó el máximo de intentos");
  const type=String(body.artifact_type||"text");if(!["text","url"].includes(type))throw new Error("Tipo de entrega grupal no permitido");
  let artifact:any={};if(type==="text")artifact={text:clampText(body.text,20000,true)};else{const url=cleanUrl(body.url);if(!url)throw new Error("URL obligatoria");artifact={url}};
  const {data:gs,error}=await db.from("lms_group_submissions_v2").insert({assignment_id:assignmentId,group_id:groupId,attempt,artifact_type:type,artifact,status:"submitted",submitted_by:ctx.user.id,submitted_at:new Date().toISOString()}).select("*").single();if(error)throw error;
  const {data:members}=await db.from("lms_group_members_v2").select("user_id").eq("group_id",groupId);
  for(const m of members||[]){
    const {data:last}=await db.from("lms_submissions_v2").select("attempt").eq("assignment_id",assignmentId).eq("user_id",m.user_id).order("attempt",{ascending:false}).limit(1);
    const indAttempt=Number(last?.[0]?.attempt||0)+1;if(indAttempt>Number(a.max_attempts||1))continue;
    await db.from("lms_submissions_v2").insert({assignment_id:assignmentId,user_id:m.user_id,attempt:indAttempt,artifact_type:"evidence",artifact:{source:"group_submission",group_submission_id:gs.id,group_id:groupId},status:"submitted",submitted_at:gs.submitted_at}).then(()=>{}).catch(()=>{});
  }
  const contribution=clampText(body.contribution_text,2000);
  if(contribution)await db.from("lms_group_contributions_v2").upsert({group_submission_id:gs.id,user_id:ctx.user.id,contribution_text:contribution,confirmed_at:new Date().toISOString()},{onConflict:"group_submission_id,user_id"});
  await audit(ctx.user.id,"bigdata.group.submit","group_submission",gs.id,{assignment_id:assignmentId,group_id:groupId,attempt});return {ok:true,submission:gs};
}
async function confirmContribution(ctx:any,run:any,body:any){
  const submissionId=clampText(body.group_submission_id,80,true),text=clampText(body.contribution_text,2000,true);
  const {data:s}=await db.from("lms_group_submissions_v2").select("id,group_id,assignment_id").eq("id",submissionId).maybeSingle();if(!s)throw new Error("Entrega grupal no encontrada");
  const [{data:g},{data:m},{data:a}]=await Promise.all([
    db.from("lms_groups_v2").select("id").eq("id",s.group_id).eq("course_run_id",run.id).maybeSingle(),
    db.from("lms_group_members_v2").select("user_id").eq("group_id",s.group_id).eq("user_id",ctx.user.id).maybeSingle(),
    db.from("lms_assignments_v2").select("id").eq("id",s.assignment_id).eq("course_run_id",run.id).maybeSingle()
  ]);if(!g||!m||!a)throw new Error("No perteneces al equipo de esta entrega");
  const {data,error}=await db.from("lms_group_contributions_v2").upsert({group_submission_id:submissionId,user_id:ctx.user.id,contribution_text:text,confirmed_at:new Date().toISOString()},{onConflict:"group_submission_id,user_id"}).select("*").single();if(error)throw error;
  return {ok:true,contribution:data};
}
async function gradeGroupSubmission(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=clampText(body.group_submission_id,80,true);
  const {data:s}=await db.from("lms_group_submissions_v2").select("*").eq("id",id).maybeSingle();if(!s)throw new Error("Entrega grupal no encontrada");
  const {data:a}=await db.from("lms_assignments_v2").select("*").eq("id",s.assignment_id).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Entrega fuera de la cohorte");
  const score=Number(body.score);if(!Number.isFinite(score)||score<0||score>Number(a.max_score))throw new Error("Puntaje fuera de rango");
  const feedback=clampText(body.feedback,10000),rubricScores=body.rubric_scores&&typeof body.rubric_scores==="object"?body.rubric_scores:{},now=new Date().toISOString();
  const {data:updated,error}=await db.from("lms_group_submissions_v2").update({score,feedback,rubric_scores:rubricScores,status:"reviewed",reviewed_by:ctx.user.id,reviewed_at:now}).eq("id",id).select("*").single();if(error)throw error;
  const {data:members}=await db.from("lms_group_members_v2").select("user_id").eq("group_id",s.group_id);
  for(const m of members||[]){
    const {data:inds}=await db.from("lms_submissions_v2").select("*").eq("assignment_id",s.assignment_id).eq("user_id",m.user_id).order("attempt",{ascending:false});
    const ind=(inds||[]).find((x:any)=>x.artifact?.source==="group_submission"&&x.artifact?.group_submission_id===id);if(!ind)continue;
    await db.from("lms_grade_history_v2").insert({submission_id:ind.id,assignment_id:s.assignment_id,user_id:m.user_id,actor_user_id:ctx.user.id,previous_score:ind.score,new_score:score,previous_feedback:ind.feedback,new_feedback:feedback,rubric_scores:rubricScores,created_at:now}).then(()=>{}).catch(()=>{});
    await db.from("lms_submissions_v2").update({score,feedback,rubric_scores:rubricScores,status:"reviewed",reviewed_by:ctx.user.id,reviewed_at:now}).eq("id",ind.id);
  }
  await audit(ctx.user.id,"bigdata.group.grade","group_submission",id,{assignment_id:s.assignment_id,group_id:s.group_id,score});return {ok:true,submission:updated};
}
async function createThread(ctx:any,run:any,body:any){
  const n=body.session_number===null||body.session_number===""?null:Math.trunc(Number(body.session_number));
  if(n!==null){const {data:s}=await db.from("lms_run_sessions_v2").select("session_number").eq("course_run_id",run.id).eq("session_number",n).maybeSingle();if(!s)throw new Error("Sesión inválida")}
  const assignmentId=clampText(body.assignment_id,80)||null;if(assignmentId){const {data:a}=await db.from("lms_assignments_v2").select("id").eq("id",assignmentId).eq("course_run_id",run.id).maybeSingle();if(!a)throw new Error("Tarea inválida")}
  const initialBody=clampText(body.body,8000,true);
  const {data,error}=await db.from("lms_discussion_threads_v2").insert({course_run_id:run.id,session_number:n,assignment_id:assignmentId,title:clampText(body.title,180,true),pinned:isTeacher(ctx)&&!!body.pinned,locked:false,created_by:ctx.user.id}).select("*").single();if(error)throw error;
  const {data:first,error:postError}=await db.from("lms_discussion_posts_v2").insert({thread_id:data.id,user_id:ctx.user.id,body:initialBody}).select("*").single();if(postError)throw postError;
  return {ok:true,thread:data,post:first};
}
async function postDiscussion(ctx:any,run:any,body:any){
  const threadId=clampText(body.thread_id,80,true),parentId=clampText(body.parent_id,80)||null;
  const {data:t}=await db.from("lms_discussion_threads_v2").select("*").eq("id",threadId).eq("course_run_id",run.id).maybeSingle();if(!t)throw new Error("Conversación no encontrada");if(t.locked&&!isTeacher(ctx))throw new Error("Esta conversación está cerrada");
  let parent:any=null;
  if(parentId){const x=await db.from("lms_discussion_posts_v2").select("id,thread_id,user_id").eq("id",parentId).maybeSingle();parent=x.data;if(!parent||parent.thread_id!==threadId)throw new Error("La respuesta citada no pertenece a esta conversación")}
  const {data,error}=await db.from("lms_discussion_posts_v2").insert({thread_id:threadId,user_id:ctx.user.id,parent_id:parentId,body:clampText(body.body,8000,true)}).select("*").single();if(error)throw error;
  if(parent&&parent.user_id!==ctx.user.id)await db.from("lms_discussion_mentions_v2").upsert({thread_id:threadId,post_id:data.id,mentioned_user_id:parent.user_id,created_by:ctx.user.id,created_at:new Date().toISOString()},{onConflict:"post_id,mentioned_user_id"}).then(()=>{}).catch(()=>{});
  return {ok:true,post:data};
}
async function moderateThread(ctx:any,run:any,body:any){
  requireTeacher(ctx);const threadId=clampText(body.thread_id,80,true);
  const {data,error}=await db.from("lms_discussion_threads_v2").update({pinned:!!body.pinned,locked:!!body.locked}).eq("id",threadId).eq("course_run_id",run.id).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.discussion.moderate","discussion_thread",threadId,{pinned:data.pinned,locked:data.locked});return {ok:true,thread:data};
}
async function pinAnswer(ctx:any,run:any,body:any){
  requireTeacher(ctx);const postId=clampText(body.post_id,80,true);
  const {data:p}=await db.from("lms_discussion_posts_v2").select("id,thread_id").eq("id",postId).maybeSingle();if(!p)throw new Error("Respuesta no encontrada");
  const {data:t}=await db.from("lms_discussion_threads_v2").select("id").eq("id",p.thread_id).eq("course_run_id",run.id).maybeSingle();if(!t)throw new Error("Respuesta fuera de la cohorte");
  const {data,error}=await db.from("lms_discussion_posts_v2").update({pinned_answer:!!body.pinned_answer}).eq("id",postId).select("*").single();if(error)throw error;
  return {ok:true,post:data};
}
async function submitPeerReview(ctx:any,run:any,body:any){
  const submissionId=clampText(body.reviewee_submission_id,80,true);
  const {data:s}=await db.from("lms_group_submissions_v2").select("*").eq("id",submissionId).maybeSingle();if(!s)throw new Error("Entrega a revisar no encontrada");
  const [{data:a},{data:setting},{data:g}]=await Promise.all([
    db.from("lms_assignments_v2").select("id").eq("id",s.assignment_id).eq("course_run_id",run.id).maybeSingle(),
    db.from("lms_assignment_group_settings_v2").select("*").eq("assignment_id",s.assignment_id).eq("peer_review_enabled",true).maybeSingle(),
    db.from("lms_groups_v2").select("id").eq("id",s.group_id).eq("course_run_id",run.id).maybeSingle()
  ]);if(!a||!setting||!g)throw new Error("Revisión por pares no habilitada");
  const own=await groupIdsForUser(run.id,ctx.user.id);if(own.includes(s.group_id))throw new Error("No puedes revisar la entrega de tu propio equipo");
  const scores=body.rubric_scores&&typeof body.rubric_scores==="object"?body.rubric_scores:{};
  for(const criterion of Array.isArray(setting.peer_rubric)?setting.peer_rubric:[]){const v=Number(scores[criterion.code]);if(!Number.isFinite(v)||v<0||v>Number(criterion.max))throw new Error("Puntaje de revisión fuera de rango: "+criterion.title)}
  const feedback=clampText(body.feedback,5000,true);
  const {data,error}=await db.from("lms_peer_reviews_v2").upsert({assignment_id:s.assignment_id,reviewee_submission_id:s.id,reviewer_user_id:ctx.user.id,rubric_scores:scores,feedback,status:"submitted",submitted_at:new Date().toISOString()},{onConflict:"reviewee_submission_id,reviewer_user_id"}).select("*").single();if(error)throw error;
  return {ok:true,review:data};
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);
  if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);
  if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  let action="home",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"home";
  else{
    try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
    action=String(body.action||"home");
  }
  try{
    if(action==="home")return out(req,await getHome(ctx,run,false));
    if(action==="teacher_overview")return out(req,await teacherOverview(ctx,run));
    if(action==="teacher_save_announcement")return out(req,await saveAnnouncement(ctx,run,body));
    if(action==="teacher_delete_announcement")return out(req,await deleteAnnouncement(ctx,run,body));
    if(action==="teacher_save_session")return out(req,await saveSession(ctx,run,body));
    if(action==="teacher_save_resource")return out(req,await saveResource(ctx,run,body));
    if(action==="teacher_delete_resource")return out(req,await deleteResource(ctx,run,body));
    if(action==="assignments")return out(req,await assignmentsForUser(ctx,run));
    if(action==="submit_assignment")return out(req,await submitAssignment(ctx,run,body));
    if(action==="teacher_save_assignment")return out(req,await saveAssignment(ctx,run,body));
    if(action==="teacher_gradebook")return out(req,await gradebook(ctx,run));
    if(action==="teacher_grade_submission")return out(req,await gradeSubmission(ctx,run,body));
    if(action==="teacher_grade_history")return out(req,await gradeHistory(ctx,run,body));
    if(action==="teacher_set_accommodation")return out(req,await setAccommodation(ctx,run,body));
    if(action==="competencies")return out(req,await competenciesForUser(ctx,run));
    if(action==="teacher_competencies")return out(req,await teacherCompetencies(ctx,run));
    if(action==="teacher_save_competency")return out(req,await saveCompetency(ctx,run,body));
    if(action==="teacher_map_competency")return out(req,await mapCompetency(ctx,run,body));
    if(action==="teacher_unmap_competency")return out(req,await unmapCompetency(ctx,run,body));
    if(action==="analytics")return out(req,await analyticsForUser(ctx,run));
    if(action==="teacher_analytics")return out(req,await teacherAnalytics(ctx,run));
    if(action==="teacher_save_alert_rule")return out(req,await saveAlertRule(ctx,run,body));
    if(action==="teacher_create_intervention")return out(req,await createIntervention(ctx,run,body));
    if(action==="teacher_resolve_intervention")return out(req,await resolveIntervention(ctx,run,body));
    if(action==="collaboration")return out(req,await collaborationOverview(ctx,run));
    if(action==="mark_mentions_read")return out(req,await markMentionsRead(ctx,run));
    if(action==="teacher_collaboration")return out(req,await teacherCollaboration(ctx,run));
    if(action==="teacher_create_group")return out(req,await createGroup(ctx,run,body));
    if(action==="teacher_add_group_member")return out(req,await addGroupMember(ctx,run,body));
    if(action==="teacher_remove_group_member")return out(req,await removeGroupMember(ctx,run,body));
    if(action==="teacher_save_group_setting")return out(req,await saveGroupSetting(ctx,run,body));
    if(action==="group_submit")return out(req,await groupSubmit(ctx,run,body));
    if(action==="confirm_contribution")return out(req,await confirmContribution(ctx,run,body));
    if(action==="teacher_grade_group_submission")return out(req,await gradeGroupSubmission(ctx,run,body));
    if(action==="create_thread")return out(req,await createThread(ctx,run,body));
    if(action==="post_discussion")return out(req,await postDiscussion(ctx,run,body));
    if(action==="teacher_moderate_thread")return out(req,await moderateThread(ctx,run,body));
    if(action==="teacher_pin_answer")return out(req,await pinAnswer(ctx,run,body));
    if(action==="submit_peer_review")return out(req,await submitPeerReview(ctx,run,body));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});