import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);
const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
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
  await db.from("lms_learning_events_v2").insert({course_run_id:run.id,user_id:ctx.user.id,event_type:"assignment_submitted",session_number:a.session_number,entity_type:"assignment",entity_id:id,metadata:{attempt},client_at:new Date().toISOString()}).then(()=>{}).catch(()=>{});
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


const LEARNING_EVENTS=new Set(["portal_opened","assignments_opened","competencies_opened","progress_opened","session_resource_opened","assignment_submitted","feedback_viewed"]);
function cleanEventMeta(v:any){
  if(!v||typeof v!=="object"||Array.isArray(v))return {};
  const o:any={};let n=0;
  for(const [k,val] of Object.entries(v)){
    if(n>=12)break;
    if(!/^[a-zA-Z0-9_.-]{1,50}$/.test(k))continue;
    if(["string","number","boolean"].includes(typeof val)){o[k]=typeof val==="string"?String(val).slice(0,300):val;n++}
  }
  return o;
}
async function trackLearningEvent(ctx:any,run:any,body:any){
  const event=String(body.event_type||"");
  if(!LEARNING_EVENTS.has(event))throw new Error("Evento académico no permitido");
  const sessionNumber=body.session_number==null?null:Math.trunc(Number(body.session_number));
  if(sessionNumber!==null&&(!Number.isInteger(sessionNumber)||sessionNumber<1||sessionNumber>99))throw new Error("Sesión inválida");
  const row={
    course_run_id:run.id,user_id:ctx.user.id,event_type:event,session_number:sessionNumber,
    entity_type:body.entity_type?clampText(body.entity_type,60):null,
    entity_id:body.entity_id?clampText(body.entity_id,120):null,
    active_seconds_delta:Math.max(0,Math.min(300,Math.trunc(Number(body.active_seconds_delta||0)))),
    metadata:cleanEventMeta(body.metadata),client_at:toIsoOrNull(body.client_at)
  };
  const {error}=await db.from("lms_learning_events_v2").insert(row);if(error)throw error;
  return {ok:true};
}
function latestDate(values:any[]){
  let best:number|null=null,raw:string|null=null;
  for(const v of values){if(!v)continue;const t=Date.parse(String(v));if(Number.isFinite(t)&&(best===null||t>best)){best=t;raw=String(v)}}
  return raw;
}
async function analyticsContext(run:any){
  const [{data:rules},{data:assignments},{data:enrollments},{data:interventions},{data:events},{data:s08}] = await Promise.all([
    db.from("lms_analytics_rules_v2").select("*").eq("course_run_id",run.id).order("position"),
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).eq("active",true).order("session_number"),
    db.from("lms_run_enrollments").select("user_id,role,status,enrolled_at").eq("course_run_id",run.id),
    db.from("lms_interventions_v2").select("*").eq("course_run_id",run.id).order("created_at",{ascending:false}).limit(500),
    db.from("lms_learning_events_v2").select("id,user_id,event_type,session_number,entity_type,entity_id,metadata,client_at,created_at").eq("course_run_id",run.id).order("created_at",{ascending:false}).limit(5000),
    db.from("bd_lms_session_progress").select("user_id,status,active_seconds,started_at,last_activity_at,completed_at,score").eq("course_run_id",run.id).eq("session_number",8)
  ]);
  const studentEnroll=(enrollments||[]).filter((x:any)=>x.role==="student");
  const userIds=studentEnroll.map((x:any)=>x.user_id);
  const assignmentIds=(assignments||[]).map((x:any)=>x.id);
  const [{data:users},{data:subs},{data:accommodations}]=await Promise.all([
    userIds.length?db.from("lms_users").select("id,display_name,username,email,active").in("id",userIds):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_submissions_v2").select("*").in("assignment_id",assignmentIds):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_assignment_accommodations_v2").select("*").in("assignment_id",assignmentIds):Promise.resolve({data:[]} as any)
  ]);
  const comp=await competencyContext(run);
  return {rules:rules||[],assignments:assignments||[],enrollments:studentEnroll,interventions:interventions||[],events:events||[],s08:s08||[],users:users||[],subs:subs||[],accommodations:accommodations||[],comp};
}
function buildAnalyticsRows(ctx:any){
  const now=Date.now(),assignmentMap=new Map(ctx.assignments.map((a:any)=>[a.id,a]));
  const enrollmentMap=new Map(ctx.enrollments.map((e:any)=>[e.user_id,e]));
  const s08Map=new Map(ctx.s08.map((p:any)=>[p.user_id,p]));
  const eventsByUser=new Map<string,any[]>(),subsByUser=new Map<string,any[]>(),intByUser=new Map<string,any[]>();
  for(const e of ctx.events){if(!eventsByUser.has(e.user_id))eventsByUser.set(e.user_id,[]);eventsByUser.get(e.user_id)!.push(e)}
  for(const s of ctx.subs){if(!subsByUser.has(s.user_id))subsByUser.set(s.user_id,[]);subsByUser.get(s.user_id)!.push(s)}
  for(const i of ctx.interventions){if(!intByUser.has(i.user_id))intByUser.set(i.user_id,[]);intByUser.get(i.user_id)!.push(i)}
  const accommodationMap=new Map(ctx.accommodations.map((x:any)=>[x.assignment_id+":"+x.user_id,x]));
  const ruleMap=new Map(ctx.rules.filter((r:any)=>r.enabled).map((r:any)=>[r.code,r]));
  return ctx.users.map((u:any)=>{
    const userSubs=(subsByUser.get(u.id)||[]).slice().sort((a:any,b:any)=>Number(b.attempt)-Number(a.attempt));
    const latest=new Map<string,any>();for(const s of userSubs)if(!latest.has(s.assignment_id))latest.set(s.assignment_id,s);
    let pending=0,overdue=0,maxAttempt=0,weighted=0,weights=0;
    for(const a of ctx.assignments){
      const s:any=latest.get(a.id),ac:any=accommodationMap.get(a.id+":"+u.id);
      const due=ac?.due_at||a.due_at;
      if(!s){pending++;if(due&&Date.parse(due)<now)overdue++}
      if(s){maxAttempt=Math.max(maxAttempt,Number(s.attempt||0));if(s.score!==null&&s.score!==undefined&&Number(a.max_score)>0){const w=Math.max(0,Number(a.weight||1));weighted+=(100*Number(s.score)/Number(a.max_score))*w;weights+=w}}
    }
    const ev=eventsByUser.get(u.id)||[],p:any=s08Map.get(u.id)||{},ints=intByUser.get(u.id)||[];
    const lastAcademicAt=latestDate([p.last_activity_at,p.completed_at,...ev.map((x:any)=>x.client_at||x.created_at),...userSubs.map((x:any)=>x.submitted_at||x.reviewed_at)]);
    const comps=computeCompetencyRows(ctx.comp,userSubs);
    const signals:any[]=[];
    const overdueRule:any=ruleMap.get("overdue_assignment");if(overdueRule&&overdue>0)signals.push({code:overdueRule.code,title:overdueRule.title,severity:overdueRule.severity,reason:overdue+" entrega(s) requerida(s) vencida(s) sin envío."});
    const inactiveRule:any=ruleMap.get("inactive_days");
    if(inactiveRule){
      const days=Math.max(1,Number(inactiveRule.config?.days||7)),enrolled=(enrollmentMap.get(u.id) as any)?.enrolled_at;
      const basis=lastAcademicAt||enrolled;const age=basis?Math.floor((now-Date.parse(basis))/86400000):0;
      if(basis&&age>=days)signals.push({code:inactiveRule.code,title:inactiveRule.title,severity:inactiveRule.severity,reason:(lastAcademicAt?"Última actividad académica":"Matrícula sin actividad académica")+" hace "+age+" día(s)."});
    }
    const attemptRule:any=ruleMap.get("repeated_attempts");if(attemptRule&&maxAttempt>=Math.max(2,Number(attemptRule.config?.attempts||3)))signals.push({code:attemptRule.code,title:attemptRule.title,severity:attemptRule.severity,reason:"Máximo de "+maxAttempt+" intento(s) en una tarea. Revisar si fue iteración deliberada o fricción."});
    const compRule:any=ruleMap.get("competency_developing"),developing=comps.filter((x:any)=>x.status==="developing");
    if(compRule&&developing.length)signals.push({code:compRule.code,title:compRule.title,severity:compRule.severity,reason:developing.length+" competencia(s) con evidencia evaluada todavía bajo su umbral."});
    return {
      user_id:u.id,display_name:u.display_name||u.username,email:u.email||u.username,global_active:!!u.active,
      run_status:(enrollmentMap.get(u.id) as any)?.status||"none",enrolled_at:(enrollmentMap.get(u.id) as any)?.enrolled_at||null,
      last_academic_at:lastAcademicAt,pending_assignments:pending,overdue_assignments:overdue,
      grade_pct:weights?Math.round(weighted/weights*10)/10:null,max_attempt:maxAttempt,
      s08_status:p.status||"not_started",s08_active_seconds:Number(p.active_seconds||0),
      competencies:comps,mastered_competencies:comps.filter((x:any)=>x.status==="mastered").length,
      developing_competencies:developing.length,signals,
      interventions:ints,open_interventions:ints.filter((x:any)=>x.status!=="closed").length,
      event_count:ev.length
    };
  }).sort((a:any,b:any)=>b.signals.length-a.signals.length||a.display_name.localeCompare(b.display_name,"es",{sensitivity:"base"}));
}
async function teacherAnalytics(ctx:any,run:any){
  requireTeacher(ctx);const context=await analyticsContext(run),students=buildAnalyticsRows(context);
  const assignmentStats=context.assignments.map((a:any)=>{
    const rows=context.subs.filter((s:any)=>s.assignment_id===a.id),users=new Set(rows.map((x:any)=>x.user_id));
    const reviewed=rows.filter((x:any)=>x.score!==null&&x.score!==undefined),avg=reviewed.length?reviewed.reduce((z:number,x:any)=>z+100*Number(x.score)/Number(a.max_score),0)/reviewed.length:null;
    return {assignment_id:a.id,code:a.code,title:a.title,session_number:a.session_number,submitted_students:users.size,total_submissions:rows.length,average_pct:avg===null?null:Math.round(avg*10)/10,average_attempts:users.size?Math.round(rows.length/users.size*10)/10:0};
  });
  const compCodes=(context.comp.competencies||[]).filter((x:any)=>x.active).map((x:any)=>x.code);
  const competencyStats=compCodes.map((code:string)=>{
    const states=students.map((s:any)=>s.competencies.find((c:any)=>c.code===code)?.status||"pending");
    const comp=context.comp.competencies.find((c:any)=>c.code===code);
    return {code,title:comp?.title||code,mastered:states.filter((x:string)=>x==="mastered").length,developing:states.filter((x:string)=>x==="developing").length,pending:states.filter((x:string)=>x==="pending").length};
  });
  return {viewer:ctx.user,run,rules:context.rules,students,assignment_stats:assignmentStats,competency_stats:competencyStats,summary:{
    students:students.length,students_with_signals:students.filter((s:any)=>s.signals.length).length,
    overdue_total:students.reduce((z:number,s:any)=>z+s.overdue_assignments,0),
    open_interventions:students.reduce((z:number,s:any)=>z+s.open_interventions,0)
  }};
}
async function myAnalytics(ctx:any,run:any){
  const context=await analyticsContext(run),student=buildAnalyticsRows(context).find((x:any)=>x.user_id===ctx.user.id);
  if(!student)throw new Error("No se encontró tu matrícula");
  const ev=(context.events||[]).filter((x:any)=>x.user_id===ctx.user.id);
  const now=Date.now(),week=7*86400000;
  const current=ev.filter((x:any)=>{const t=Date.parse(x.client_at||x.created_at);return t>=now-week}).length;
  const previous=ev.filter((x:any)=>{const t=Date.parse(x.client_at||x.created_at);return t<now-week&&t>=now-2*week}).length;
  return {viewer:ctx.user,run,student:{...student,interventions:undefined,signals:undefined},self_compare:{events_last_7_days:current,events_previous_7_days:previous},recent_events:ev.slice(0,30).map((x:any)=>({event_type:x.event_type,session_number:x.session_number,created_at:x.created_at,entity_type:x.entity_type,entity_id:x.entity_id}))};
}
async function saveIntervention(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=clampText(body.id,80),userId=clampText(body.user_id,80,true);
  const {data:e}=await db.from("lms_run_enrollments").select("user_id,role").eq("course_run_id",run.id).eq("user_id",userId).maybeSingle();
  if(!e||e.role!=="student")throw new Error("Estudiante fuera de esta cohorte");
  const status=String(body.status||"open");if(!["open","follow_up","closed"].includes(status))throw new Error("Estado de intervención inválido");
  const row:any={course_run_id:run.id,user_id:userId,signal_code:body.signal_code?clampText(body.signal_code,80):null,note:clampText(body.note,5000,true),action_text:clampText(body.action_text,3000),status,follow_up_at:toIsoOrNull(body.follow_up_at),updated_by:ctx.user.id,updated_at:new Date().toISOString()};
  let saved:any,error:any;
  if(id){const x=await db.from("lms_interventions_v2").update(row).eq("id",id).eq("course_run_id",run.id).select("*").single();saved=x.data;error=x.error}
  else{row.created_by=ctx.user.id;const x=await db.from("lms_interventions_v2").insert(row).select("*").single();saved=x.data;error=x.error}
  if(error)throw error;
  await audit(ctx.user.id,id?"bigdata.intervention.update":"bigdata.intervention.create","intervention",saved.id,{user_id:userId,status,signal_code:row.signal_code});
  return {ok:true,intervention:saved};
}
async function saveAnalyticsRule(ctx:any,run:any,body:any){
  requireTeacher(ctx);const code=clampText(body.code,80,true);
  const {data:prior}=await db.from("lms_analytics_rules_v2").select("*").eq("course_run_id",run.id).eq("code",code).maybeSingle();if(!prior)throw new Error("Regla no encontrada");
  const severity=String(body.severity||prior.severity);if(!["info","medium","high"].includes(severity))throw new Error("Severidad inválida");
  const config=body.config&&typeof body.config==="object"&&!Array.isArray(body.config)?body.config:prior.config;
  if(code==="inactive_days"){const days=Number(config.days);if(!Number.isFinite(days)||days<1||days>90)throw new Error("Días de inactividad fuera de rango")}
  if(code==="repeated_attempts"){const attempts=Number(config.attempts);if(!Number.isFinite(attempts)||attempts<2||attempts>20)throw new Error("Intentos fuera de rango")}
  const {data,error}=await db.from("lms_analytics_rules_v2").update({enabled:body.enabled!==false,severity,config,updated_by:ctx.user.id,updated_at:new Date().toISOString()}).eq("course_run_id",run.id).eq("code",code).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.analytics_rule.update","analytics_rule",code,{enabled:data.enabled,severity:data.severity,config:data.config});
  return {ok:true,rule:data};
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
    if(action==="track_learning_event")return out(req,await trackLearningEvent(ctx,run,body));
    if(action==="my_analytics")return out(req,await myAnalytics(ctx,run));
    if(action==="teacher_analytics")return out(req,await teacherAnalytics(ctx,run));
    if(action==="teacher_save_intervention")return out(req,await saveIntervention(ctx,run,body));
    if(action==="teacher_save_analytics_rule")return out(req,await saveAnalyticsRule(ctx,run,body));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});