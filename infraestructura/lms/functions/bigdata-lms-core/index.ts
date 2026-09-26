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
    db.from("lms_assignments").select("id,session_number,title,instructions,due_at,required,max_score,rubric,allowed_types,active,created_at,updated_at")
      .eq("course_run_id",run.id).eq("active",true).order("due_at",{ascending:true})
  ]);
  const sessionRows=(sessions||[]).filter((s:any)=>teacher||s.status!=="draft");
  const allowed=new Set(sessionRows.map((s:any)=>s.session_number));
  const resourceRows=(resources||[]).filter((r:any)=>allowed.has(r.session_number));
  const activeAnnouncements=(announcements||[]).filter((a:any)=>!a.expires_at||Date.parse(a.expires_at)>Date.now());
  let submissions:any[]=[];
  if((assignments||[]).length){
    const ids=(assignments||[]).map((a:any)=>a.id);
    const {data}=await db.from("lms_submissions")
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
    db.from("lms_assignments").select("*").eq("course_run_id",run.id).order("session_number").order("created_at",{ascending:false}).limit(200)
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
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});