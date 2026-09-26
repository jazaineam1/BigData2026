import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);
const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const BUCKET="bigdata-lms-private";
const MAX_FILE=20*1024*1024;
const ALLOWED_MIME=new Set([
  "application/pdf","text/plain","text/csv","application/json","application/zip","application/x-zip-compressed",
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
  "application/vnd.openxmlformats-officedocument.presentationml.presentation",
  "image/png","image/jpeg","image/webp"
]);
const ALLOWED_ORIGINS=new Set(["https://jazaineam1.github.io"]);

function origin(req:Request){
  const o=req.headers.get("origin");
  if(!o)return "";
  if(ALLOWED_ORIGINS.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;
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
    .eq("user_id",ctx.user.id).eq("status","active").order("enrolled_at",{ascending:false});
  for(const m of memberships||[]){
    const {data:r}=await db.from("lms_course_runs")
      .select("id,course_code,code,title,timezone,active")
      .eq("id",m.course_run_id).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:m.role};
  }
  if(["teacher","admin"].includes(ctx.user.role)){
    const {data:r}=await db.from("lms_course_runs")
      .select("id,course_code,code,title,timezone,active")
      .eq("code",RUN_CODE).eq("course_code",COURSE).eq("active",true).maybeSingle();
    if(r)return {...r,enrollment_role:ctx.user.role};
  }
  return null;
}
function isTeacher(ctx:any){return ["teacher","admin"].includes(ctx.user.role)}
function requireTeacher(ctx:any){if(!isTeacher(ctx))throw new Error("NO_AUTH")}
function text(v:any,max:number,required=false){
  const s=String(v??"").trim();
  if(required&&!s)throw new Error("Campo obligatorio");
  return s.slice(0,max);
}
function iso(v:any){
  if(v===null||v===undefined||v==="")return null;
  const d=new Date(String(v));if(!Number.isFinite(d.getTime()))throw new Error("Fecha no válida");
  return d.toISOString();
}
function safeCode(v:any){
  const s=text(v,80,true).toLowerCase();
  if(!/^[a-z0-9][a-z0-9_-]{2,79}$/.test(s))throw new Error("Código inválido");
  return s;
}
function safeFileName(v:any){
  const raw=text(v,180,true).normalize("NFKD").replace(/[^\w.\- ]+/g,"").replace(/\s+/g,"_");
  const s=raw.replace(/^\.+/,"").slice(0,140);
  if(!s||!s.includes("."))throw new Error("Nombre de archivo inválido");
  return s;
}
async function audit(actor:string,action:string,entity:string,id:string|null,metadata:any={}){
  await db.from("lms_audit_log").insert({
    actor_user_id:actor,action,entity_type:entity,entity_id:id,
    metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}
  }).then(()=>{}).catch(()=>{});
}
async function ensureBucket(){
  const {data}=await db.storage.getBucket(BUCKET);
  if(data)return;
  const {error}=await db.storage.createBucket(BUCKET,{
    public:false,fileSizeLimit:MAX_FILE,allowedMimeTypes:[...ALLOWED_MIME]
  });
  if(error&&!String((error as any).message||"").toLowerCase().includes("already"))throw error;
}
async function effectiveAssignment(run:any,userId:string,assignmentId:string){
  const {data:a}=await db.from("lms_assignments_v2").select("*")
    .eq("id",assignmentId).eq("course_run_id",run.id).eq("active",true).maybeSingle();
  if(!a)throw new Error("Tarea no disponible");
  const {data:acc}=await db.from("lms_assignment_accommodations_v2").select("*")
    .eq("assignment_id",assignmentId).eq("user_id",userId).maybeSingle();
  return {assignment:a,due:acc?.due_at||a.due_at||null,maxAttempts:Number(acc?.max_attempts||a.max_attempts||1)};
}
async function nextAssignmentAttempt(userId:string,assignmentId:string){
  const {data}=await db.from("lms_submissions_v2").select("attempt")
    .eq("assignment_id",assignmentId).eq("user_id",userId).order("attempt",{ascending:false}).limit(1);
  return Number(data?.[0]?.attempt||0)+1;
}

/* -------------------------- Private file delivery -------------------------- */
async function prepareFileUpload(ctx:any,run:any,body:any){
  const assignmentId=text(body.assignment_id,80,true);
  const {assignment,due,maxAttempts}=await effectiveAssignment(run,ctx.user.id,assignmentId);
  if(!Array.isArray(assignment.allowed_types)||!assignment.allowed_types.includes("file"))throw new Error("Esta tarea no acepta archivos");
  if(due&&Date.parse(due)<Date.now())throw new Error("La fecha de entrega ya venció para tu cuenta");
  const attempt=await nextAssignmentAttempt(ctx.user.id,assignmentId);if(attempt>maxAttempts)throw new Error("Ya usaste el máximo de intentos");
  const fileName=safeFileName(body.file_name),mime=text(body.mime_type||"application/octet-stream",120,true);
  const size=Math.trunc(Number(body.size_bytes||0));
  if(size<1||size>MAX_FILE)throw new Error("El archivo debe pesar entre 1 byte y 20 MB");
  if(!ALLOWED_MIME.has(mime))throw new Error("Tipo de archivo no permitido");
  await ensureBucket();
  const uploadId=crypto.randomUUID();
  const path=[run.id,assignmentId,ctx.user.id,uploadId,fileName].join("/");
  const {error:insertError}=await db.from("lms_submission_files_v2").insert({
    id:uploadId,assignment_id:assignmentId,user_id:ctx.user.id,bucket:BUCKET,object_path:path,
    file_name:fileName,mime_type:mime,size_bytes:size,status:"pending"
  });
  if(insertError)throw insertError;
  const {data:signed,error}=await db.storage.from(BUCKET).createSignedUploadUrl(path,{upsert:false});
  if(error||!signed){await db.from("lms_submission_files_v2").delete().eq("id",uploadId);throw new Error("No se pudo preparar la carga privada")}
  return {ok:true,upload_id:uploadId,bucket:BUCKET,path:signed.path,token:signed.token,signed_url:signed.signedUrl,max_bytes:MAX_FILE};
}
async function storageObject(path:string){
  const parts=path.split("/"),name=parts.pop()!,dir=parts.join("/");
  const {data,error}=await db.storage.from(BUCKET).list(dir,{limit:20,search:name});
  if(error)throw error;
  return (data||[]).find((x:any)=>x.name===name)||null;
}
async function submitFileAssignment(ctx:any,run:any,body:any){
  const uploadId=text(body.upload_id,80,true);
  const {data:file}=await db.from("lms_submission_files_v2").select("*")
    .eq("id",uploadId).eq("user_id",ctx.user.id).eq("status","pending").maybeSingle();
  if(!file)throw new Error("Carga pendiente no encontrada");
  const {assignment,due,maxAttempts}=await effectiveAssignment(run,ctx.user.id,file.assignment_id);
  if(!Array.isArray(assignment.allowed_types)||!assignment.allowed_types.includes("file"))throw new Error("Esta tarea ya no acepta archivos");
  if(due&&Date.parse(due)<Date.now())throw new Error("La fecha de entrega ya venció para tu cuenta");
  const attempt=await nextAssignmentAttempt(ctx.user.id,file.assignment_id);if(attempt>maxAttempts)throw new Error("Ya usaste el máximo de intentos");
  const obj:any=await storageObject(file.object_path);if(!obj)throw new Error("El archivo aún no aparece en el almacenamiento; completa la carga primero");
  const actualSize=Number(obj.metadata?.size||file.size_bytes);
  if(actualSize<1||actualSize>MAX_FILE)throw new Error("Tamaño real de archivo fuera de rango");
  const {data:sub,error}=await db.from("lms_submissions_v2").insert({
    assignment_id:file.assignment_id,user_id:ctx.user.id,attempt,artifact_type:"file",
    artifact:{file_id:file.id,bucket:BUCKET,path:file.object_path,file_name:file.file_name,mime_type:file.mime_type,size_bytes:actualSize},
    status:"submitted",submitted_at:new Date().toISOString()
  }).select("*").single();
  if(error)throw error;
  await db.from("lms_submission_files_v2").update({submission_id:sub.id,status:"attached",attached_at:new Date().toISOString()}).eq("id",file.id);
  await audit(ctx.user.id,"bigdata.assignment.submit_file","submission",sub.id,{assignment_id:file.assignment_id,attempt,file_id:file.id});
  return {ok:true,submission:sub};
}
async function fileDownloadUrl(ctx:any,run:any,body:any){
  const submissionId=text(body.submission_id,80,true);
  const {data:s}=await db.from("lms_submissions_v2").select("*").eq("id",submissionId).maybeSingle();
  if(!s||s.artifact_type!=="file")throw new Error("Archivo no encontrado");
  const {data:a}=await db.from("lms_assignments_v2").select("course_run_id").eq("id",s.assignment_id).maybeSingle();
  if(!a||a.course_run_id!==run.id)throw new Error("Archivo fuera de esta cohorte");
  if(!isTeacher(ctx)&&s.user_id!==ctx.user.id)throw new Error("NO_AUTH");
  const path=String(s.artifact?.path||"");if(!path)throw new Error("Ruta de archivo inválida");
  const {data,error}=await db.storage.from(BUCKET).createSignedUrl(path,300,{download:String(s.artifact?.file_name||"entrega")});
  if(error||!data)throw new Error("No se pudo firmar la descarga");
  return {ok:true,signed_url:data.signedUrl,expires_in:300,file_name:s.artifact?.file_name||"entrega"};
}

/* ------------------------------- Questions -------------------------------- */
function cleanOptions(raw:any){
  if(!Array.isArray(raw))return [];
  const seen=new Set<string>(),out:any[]=[];
  for(const x of raw.slice(0,30)){
    const id=text(x?.id,60,true);
    if(!/^[A-Za-z0-9_-]{1,60}$/.test(id)||seen.has(id))throw new Error("IDs de opción inválidos o repetidos");
    seen.add(id);out.push({id,text:text(x?.text,1200,true)});
  }
  return out;
}
function cleanQuestion(body:any){
  const type=String(body.question_type||"");
  if(!["single_choice","multiple_choice","true_false","numeric","short_text"].includes(type))throw new Error("Tipo de pregunta inválido");
  const prompt=text(body.prompt,8000,true),explanation=text(body.explanation,8000),points=Number(body.default_points||1);
  if(!Number.isFinite(points)||points<=0||points>1000)throw new Error("Puntaje inválido");
  const tags=(Array.isArray(body.tags)?body.tags:[]).slice(0,20).map((x:any)=>text(x,60)).filter(Boolean);
  let options:any[]=[],answer:any={};
  if(["single_choice","multiple_choice"].includes(type)){
    options=cleanOptions(body.options);if(options.length<2)throw new Error("Una pregunta de selección necesita al menos dos opciones");
    const ids=new Set(options.map(x=>x.id)),correct=(Array.isArray(body.answer_key?.correct_option_ids)?body.answer_key.correct_option_ids:[]).map(String);
    if(type==="single_choice"&&correct.length!==1)throw new Error("Selección única requiere exactamente una respuesta correcta");
    if(type==="multiple_choice"&&!correct.length)throw new Error("Selección múltiple requiere al menos una respuesta correcta");
    if(correct.some((id:string)=>!ids.has(id)))throw new Error("Respuesta correcta fuera de las opciones");
    answer={correct_option_ids:[...new Set(correct)]};
  }else if(type==="true_false"){
    if(typeof body.answer_key?.value!=="boolean")throw new Error("Define verdadero o falso como respuesta correcta");
    answer={value:body.answer_key.value};
  }else if(type==="numeric"){
    const value=Number(body.answer_key?.value),tolerance=Number(body.answer_key?.tolerance??0);
    if(!Number.isFinite(value)||!Number.isFinite(tolerance)||tolerance<0)throw new Error("Respuesta numérica inválida");
    answer={value,tolerance};
  }
  return {type,prompt,options,answer,explanation,points,tags};
}
async function teacherQuestions(ctx:any,run:any){
  requireTeacher(ctx);
  const {data,error}=await db.from("lms_questions_v2").select("*").eq("course_run_id",run.id).order("code").order("version",{ascending:false});
  if(error)throw error;
  const latest=new Map<string,any>();for(const q of data||[])if(!latest.has(q.code))latest.set(q.code,q);
  return {questions:[...latest.values()],versions:data||[]};
}
async function saveQuestion(ctx:any,run:any,body:any){
  requireTeacher(ctx);const q=cleanQuestion(body),id=text(body.id,80),code=safeCode(body.code);
  let version=1,prior:any=null;
  if(id){
    const {data}=await db.from("lms_questions_v2").select("*").eq("id",id).eq("course_run_id",run.id).maybeSingle();
    prior=data;if(!prior)throw new Error("Pregunta no encontrada");if(prior.code!==code)throw new Error("El código no cambia entre versiones");
    const {data:maxRows}=await db.from("lms_questions_v2").select("version").eq("course_run_id",run.id).eq("code",code).order("version",{ascending:false}).limit(1);
    version=Number(maxRows?.[0]?.version||0)+1;
  }else{
    const {data:exists}=await db.from("lms_questions_v2").select("id").eq("course_run_id",run.id).eq("code",code).limit(1);
    if(exists?.length)throw new Error("Ese código ya existe; crea una nueva versión desde la pregunta existente");
  }
  const {data,error}=await db.from("lms_questions_v2").insert({
    course_run_id:run.id,code,version,question_type:q.type,prompt:q.prompt,options:q.options,answer_key:q.answer,
    explanation:q.explanation,default_points:q.points,tags:q.tags,active:true,created_by:ctx.user.id
  }).select("*").single();if(error)throw error;
  if(prior)await db.from("lms_questions_v2").update({active:false,updated_at:new Date().toISOString()}).eq("id",prior.id);
  await audit(ctx.user.id,"bigdata.question.version.create","question",data.id,{code,version,previous_id:prior?.id||null});
  return {ok:true,question:data};
}

/* -------------------------------- Quizzes --------------------------------- */
function shuffled<T>(arr:T[]){const a=arr.slice();for(let i=a.length-1;i>0;i--){const r=new Uint32Array(1);crypto.getRandomValues(r);const j=r[0]%(i+1);[a[i],a[j]]=[a[j],a[i]]}return a}
async function quizItems(quizId:string){
  const {data:items,error}=await db.from("lms_quiz_items_v2").select("*").eq("quiz_id",quizId).order("position");if(error)throw error;
  const ids=(items||[]).map((x:any)=>x.question_id);
  const {data:qs}=ids.length?await db.from("lms_questions_v2").select("*").in("id",ids):({data:[]} as any);
  const qm=new Map((qs||[]).map((q:any)=>[q.id,q]));
  return (items||[]).map((i:any)=>({...i,question:qm.get(i.question_id)})).filter((x:any)=>x.question);
}
async function ensureQuizAssignment(ctx:any,run:any,quiz:any){
  const items=await quizItems(quiz.id);if(!items.length)throw new Error("El quiz debe tener al menos una pregunta");
  const maxScore=items.reduce((z:number,x:any)=>z+Number(x.points),0),code="quiz-"+quiz.code;
  let assignment:any=null;
  if(quiz.assignment_id){
    const {data}=await db.from("lms_assignments_v2").select("*").eq("id",quiz.assignment_id).eq("course_run_id",run.id).maybeSingle();assignment=data;
  }
  if(!assignment){
    const {data}=await db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).eq("code",code).maybeSingle();assignment=data;
  }
  const row:any={course_run_id:run.id,code,session_number:quiz.session_number,title:"Quiz · "+quiz.title,instructions:quiz.instructions||"",
    due_at:quiz.due_at,required:true,max_score:maxScore,rubric:[],allowed_types:["evidence"],active:quiz.published&&quiz.active,
    max_attempts:quiz.max_attempts,category:"quiz",weight:1,updated_at:new Date().toISOString()};
  if(assignment){
    const {data,error}=await db.from("lms_assignments_v2").update(row).eq("id",assignment.id).select("*").single();if(error)throw error;assignment=data;
  }else{
    row.created_by=ctx.user.id;const {data,error}=await db.from("lms_assignments_v2").insert(row).select("*").single();if(error)throw error;assignment=data;
  }
  await db.from("lms_quizzes_v2").update({assignment_id:assignment.id,updated_at:new Date().toISOString()}).eq("id",quiz.id);
  return assignment;
}
async function teacherOverview(ctx:any,run:any){
  requireTeacher(ctx);
  const [{questions,versions},{data:quizzes},{data:items},{data:attempts},{data:responses}]=await Promise.all([
    teacherQuestions(ctx,run),
    db.from("lms_quizzes_v2").select("*").eq("course_run_id",run.id).order("session_number").order("created_at"),
    db.from("lms_quiz_items_v2").select("*"),
    db.from("lms_quiz_attempts_v2").select("*").order("started_at",{ascending:false}).limit(1000),
    db.from("lms_quiz_responses_v2").select("*").order("saved_at",{ascending:false}).limit(3000)
  ]);
  const qids=new Set((quizzes||[]).map((x:any)=>x.id)),attemptRows=(attempts||[]).filter((x:any)=>qids.has(x.quiz_id));
  const attemptIds=new Set(attemptRows.map((x:any)=>x.id)),responseRows=(responses||[]).filter((x:any)=>attemptIds.has(x.attempt_id));
  const userIds=[...new Set(attemptRows.map((x:any)=>x.user_id))];
  const {data:users}=userIds.length?await db.from("lms_users").select("id,display_name,username,email").in("id",userIds):({data:[]} as any);
  const quizItemsRows=(items||[]).filter((x:any)=>qids.has(x.quiz_id));
  return {viewer:ctx.user,run,questions,question_versions:versions,quizzes:quizzes||[],items:quizItemsRows,attempts:attemptRows,responses:responseRows,users:users||[]};
}
async function saveQuiz(ctx:any,run:any,body:any){
  requireTeacher(ctx);const id=text(body.id,80),code=safeCode(body.code),session=body.session_number==null||body.session_number===""?null:Math.trunc(Number(body.session_number));
  if(session!==null){const {data:s}=await db.from("lms_run_sessions_v2").select("session_number").eq("course_run_id",run.id).eq("session_number",session).maybeSingle();if(!s)throw new Error("Sesión inválida")}
  const maxAttempts=Math.trunc(Number(body.max_attempts||1));if(maxAttempts<1||maxAttempts>20)throw new Error("Intentos inválidos");
  const tl=body.time_limit_minutes==null||body.time_limit_minutes===""?null:Math.trunc(Number(body.time_limit_minutes));if(tl!==null&&(tl<1||tl>480))throw new Error("Tiempo límite inválido");
  const row:any={course_run_id:run.id,code,session_number:session,title:text(body.title,180,true),instructions:text(body.instructions,8000),
    release_at:iso(body.release_at),due_at:iso(body.due_at),max_attempts:maxAttempts,time_limit_minutes:tl,
    shuffle_questions:!!body.shuffle_questions,shuffle_options:!!body.shuffle_options,published:!!body.published,active:body.active!==false,updated_at:new Date().toISOString()};
  let quiz:any,error:any;
  if(id){const x=await db.from("lms_quizzes_v2").update(row).eq("id",id).eq("course_run_id",run.id).select("*").single();quiz=x.data;error=x.error}
  else{row.created_by=ctx.user.id;const x=await db.from("lms_quizzes_v2").insert(row).select("*").single();quiz=x.data;error=x.error}
  if(error)throw error;
  if(quiz.published)await ensureQuizAssignment(ctx,run,quiz);
  else if(quiz.assignment_id)await db.from("lms_assignments_v2").update({active:false,updated_at:new Date().toISOString()}).eq("id",quiz.assignment_id);
  await audit(ctx.user.id,id?"bigdata.quiz.update":"bigdata.quiz.create","quiz",quiz.id,{code:quiz.code,published:quiz.published});
  return {ok:true,quiz};
}
async function setQuizItems(ctx:any,run:any,body:any){
  requireTeacher(ctx);const quizId=text(body.quiz_id,80,true);
  const {data:quiz}=await db.from("lms_quizzes_v2").select("*").eq("id",quizId).eq("course_run_id",run.id).maybeSingle();if(!quiz)throw new Error("Quiz no encontrado");
  const raw=Array.isArray(body.items)?body.items.slice(0,100):[];if(!raw.length)throw new Error("Selecciona al menos una pregunta");
  const ids=[...new Set(raw.map((x:any)=>String(x.question_id)))];
  const {data:qs}=await db.from("lms_questions_v2").select("id,course_run_id,default_points").in("id",ids);
  if((qs||[]).length!==ids.length||(qs||[]).some((q:any)=>q.course_run_id!==run.id))throw new Error("Hay preguntas fuera de esta cohorte");
  const qmap=new Map((qs||[]).map((q:any)=>[q.id,q]));
  const rows=raw.map((x:any,i:number)=>{const q:any=qmap.get(String(x.question_id)),points=Number(x.points??q.default_points);if(!Number.isFinite(points)||points<=0||points>1000)throw new Error("Puntaje de ítem inválido");return {quiz_id:quizId,question_id:q.id,position:i+1,points,required:x.required!==false}});
  const {error:del}=await db.from("lms_quiz_items_v2").delete().eq("quiz_id",quizId);if(del)throw del;
  const {error}=await db.from("lms_quiz_items_v2").insert(rows);if(error)throw error;
  if(quiz.published)await ensureQuizAssignment(ctx,run,quiz);
  await audit(ctx.user.id,"bigdata.quiz.items.set","quiz",quizId,{count:rows.length});
  return {ok:true,count:rows.length};
}
function publicQuestion(q:any,order?:string[]){
  let options=Array.isArray(q.options)?q.options:[];
  if(order?.length){const m=new Map(options.map((x:any)=>[x.id,x]));options=order.map(id=>m.get(id)).filter(Boolean)}
  return {id:q.id,code:q.code,version:q.version,question_type:q.question_type,prompt:q.prompt,options};
}
async function attemptPayload(attempt:any){
  const {data:quiz}=await db.from("lms_quizzes_v2").select("*").eq("id",attempt.quiz_id).single();
  const items=await quizItems(attempt.quiz_id),im=new Map(items.map((x:any)=>[x.question_id,x]));
  const order=Array.isArray(attempt.question_order)?attempt.question_order:items.map((x:any)=>x.question_id);
  const {data:resp}=await db.from("lms_quiz_responses_v2").select("question_id,response,auto_score,manual_score,feedback,saved_at").eq("attempt_id",attempt.id);
  const rm=new Map((resp||[]).map((x:any)=>[x.question_id,x]));
  return {quiz:{id:quiz.id,code:quiz.code,title:quiz.title,instructions:quiz.instructions,due_at:quiz.due_at,time_limit_minutes:quiz.time_limit_minutes},
    attempt,questions:order.map((id:string)=>{const x:any=im.get(id);return x?{...publicQuestion(x.question,attempt.option_orders?.[id]),points:Number(x.points),response:rm.get(id)?.response||null}:null}).filter(Boolean)};
}
async function quizAccess(ctx:any,run:any,id:string){
  const {data:q}=await db.from("lms_quizzes_v2").select("*").eq("id",id).eq("course_run_id",run.id).eq("active",true).eq("published",true).maybeSingle();
  if(!q)throw new Error("Quiz no disponible");
  const now=Date.now();if(q.release_at&&Date.parse(q.release_at)>now)throw new Error("El quiz todavía no está disponible");
  let due=q.due_at,maxAttempts=Number(q.max_attempts||1);
  if(q.assignment_id){
    const {data:acc}=await db.from("lms_assignment_accommodations_v2").select("*").eq("assignment_id",q.assignment_id).eq("user_id",ctx.user.id).maybeSingle();
    due=acc?.due_at||due;maxAttempts=Number(acc?.max_attempts||maxAttempts);
  }
  return {quiz:q,due,maxAttempts};
}
async function quizzesForUser(ctx:any,run:any){
  const now=new Date().toISOString();
  const {data:quizzes,error}=await db.from("lms_quizzes_v2").select("id,code,session_number,title,instructions,release_at,due_at,max_attempts,time_limit_minutes,shuffle_questions,shuffle_options,assignment_id")
    .eq("course_run_id",run.id).eq("active",true).eq("published",true).or("release_at.is.null,release_at.lte."+now).order("session_number").order("release_at");
  if(error)throw error;
  const ids=(quizzes||[]).map((x:any)=>x.id);
  const {data:attempts}=ids.length?await db.from("lms_quiz_attempts_v2").select("*").eq("user_id",ctx.user.id).in("quiz_id",ids).order("attempt",{ascending:false}):({data:[]} as any);
  const by=new Map<string,any[]>();for(const a of attempts||[]){if(!by.has(a.quiz_id))by.set(a.quiz_id,[]);by.get(a.quiz_id)!.push(a)}
  return {viewer:ctx.user,run,quizzes:(quizzes||[]).map((q:any)=>({...q,attempts:by.get(q.id)||[]}))};
}
async function startQuiz(ctx:any,run:any,body:any){
  const id=text(body.quiz_id,80,true),{quiz,due,maxAttempts}=await quizAccess(ctx,run,id);
  if(due&&Date.parse(due)<Date.now())throw new Error("La fecha del quiz ya venció para tu cuenta");
  const {data:attempts}=await db.from("lms_quiz_attempts_v2").select("*").eq("quiz_id",id).eq("user_id",ctx.user.id).order("attempt",{ascending:false});
  const current=(attempts||[]).find((a:any)=>a.status==="in_progress");
  if(current&&(!current.expires_at||Date.parse(current.expires_at)>Date.now()))return {ok:true,resumed:true,...await attemptPayload(current)};
  if(current&&current.expires_at&&Date.parse(current.expires_at)<=Date.now())await finalizeAttempt(ctx,run,current.id,true);
  const used=(attempts||[]).length;if(used>=maxAttempts)throw new Error("Ya usaste el máximo de intentos");
  const items=await quizItems(id);if(!items.length)throw new Error("El quiz no tiene preguntas");
  let order=items.map((x:any)=>x.question_id);if(quiz.shuffle_questions)order=shuffled(order);
  const optionOrders:any={};
  for(const x of items){const opts=Array.isArray(x.question.options)?x.question.options.map((o:any)=>o.id):[];optionOrders[x.question_id]=quiz.shuffle_options?shuffled(opts):opts}
  const start=Date.now(),timeEnd=quiz.time_limit_minutes?start+Number(quiz.time_limit_minutes)*60000:null,dueTime=due?Date.parse(due):null;
  const end=timeEnd&&dueTime?Math.min(timeEnd,dueTime):(timeEnd||dueTime);
  const maxScore=items.reduce((z:number,x:any)=>z+Number(x.points),0);
  const {data,error}=await db.from("lms_quiz_attempts_v2").insert({
    quiz_id:id,user_id:ctx.user.id,attempt:used+1,status:"in_progress",started_at:new Date(start).toISOString(),
    expires_at:end?new Date(end).toISOString():null,question_order:order,option_orders:optionOrders,max_score:maxScore
  }).select("*").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.quiz.attempt.start","quiz_attempt",data.id,{quiz_id:id,attempt:data.attempt});
  return {ok:true,resumed:false,...await attemptPayload(data)};
}
function cleanResponse(q:any,raw:any){
  if(q.question_type==="single_choice"||q.question_type==="multiple_choice"){
    const allowed=new Set((q.options||[]).map((x:any)=>x.id)),ids=(Array.isArray(raw?.option_ids)?raw.option_ids:[]).map(String);
    if(q.question_type==="single_choice"&&ids.length>1)throw new Error("Respuesta de selección única inválida");
    if(ids.some((x:string)=>!allowed.has(x)))throw new Error("Opción inválida");
    return {option_ids:[...new Set(ids)]};
  }
  if(q.question_type==="true_false"){if(typeof raw?.value!=="boolean")throw new Error("Selecciona verdadero o falso");return {value:raw.value}}
  if(q.question_type==="numeric"){const n=Number(raw?.value);if(!Number.isFinite(n))throw new Error("Respuesta numérica inválida");return {value:n}}
  if(q.question_type==="short_text")return {text:text(raw?.text,5000,true)};
  throw new Error("Tipo de pregunta desconocido");
}
async function saveResponse(ctx:any,run:any,body:any){
  const attemptId=text(body.attempt_id,80,true),questionId=text(body.question_id,80,true);
  const {data:a}=await db.from("lms_quiz_attempts_v2").select("*").eq("id",attemptId).eq("user_id",ctx.user.id).eq("status","in_progress").maybeSingle();
  if(!a)throw new Error("Intento no disponible");if(a.expires_at&&Date.parse(a.expires_at)<=Date.now())throw new Error("El tiempo del intento terminó");
  const {data:qz}=await db.from("lms_quizzes_v2").select("course_run_id").eq("id",a.quiz_id).maybeSingle();if(!qz||qz.course_run_id!==run.id)throw new Error("Intento fuera de esta cohorte");
  const {data:item}=await db.from("lms_quiz_items_v2").select("question_id").eq("quiz_id",a.quiz_id).eq("question_id",questionId).maybeSingle();if(!item)throw new Error("Pregunta fuera del quiz");
  const {data:q}=await db.from("lms_questions_v2").select("*").eq("id",questionId).maybeSingle();if(!q)throw new Error("Pregunta no encontrada");
  const response=cleanResponse(q,body.response);
  const {error}=await db.from("lms_quiz_responses_v2").upsert({attempt_id:attemptId,question_id:questionId,response,saved_at:new Date().toISOString()},{onConflict:"attempt_id,question_id"});if(error)throw error;
  return {ok:true};
}
function equalSets(a:string[],b:string[]){const x=[...new Set(a)].sort(),y=[...new Set(b)].sort();return x.length===y.length&&x.every((v,i)=>v===y[i])}
function autoScore(q:any,response:any,points:number){
  if(q.question_type==="single_choice"||q.question_type==="multiple_choice")return equalSets(response?.option_ids||[],q.answer_key?.correct_option_ids||[])?points:0;
  if(q.question_type==="true_false")return response?.value===q.answer_key?.value?points:0;
  if(q.question_type==="numeric"){const n=Number(response?.value),v=Number(q.answer_key?.value),tol=Number(q.answer_key?.tolerance||0);return Number.isFinite(n)&&Math.abs(n-v)<=tol?points:0}
  return null;
}
async function syncQuizGrade(run:any,attempt:any){
  const {data:quiz}=await db.from("lms_quizzes_v2").select("*").eq("id",attempt.quiz_id).maybeSingle();if(!quiz?.assignment_id)return;
  const status=attempt.status==="reviewed"?"reviewed":"submitted";
  const row={assignment_id:quiz.assignment_id,user_id:attempt.user_id,attempt:attempt.attempt,artifact_type:"evidence",
    artifact:{source:"quiz",quiz_id:quiz.id,quiz_attempt_id:attempt.id},status,submitted_at:attempt.submitted_at||new Date().toISOString(),score:attempt.score};
  const {data:existing}=await db.from("lms_submissions_v2").select("*").eq("assignment_id",quiz.assignment_id).eq("user_id",attempt.user_id).eq("attempt",attempt.attempt).maybeSingle();
  if(existing){
    await db.from("lms_submissions_v2").update({status:row.status,score:row.score,artifact:row.artifact,reviewed_at:status==="reviewed"?new Date().toISOString():existing.reviewed_at}).eq("id",existing.id);
  }else await db.from("lms_submissions_v2").insert(row);
}
async function finalizeAttempt(ctx:any,run:any,attemptId:string,expired=false){
  const {data:a}=await db.from("lms_quiz_attempts_v2").select("*").eq("id",attemptId).maybeSingle();if(!a)throw new Error("Intento no encontrado");
  if(!isTeacher(ctx)&&a.user_id!==ctx.user.id)throw new Error("NO_AUTH");
  const {data:quiz}=await db.from("lms_quizzes_v2").select("*").eq("id",a.quiz_id).eq("course_run_id",run.id).maybeSingle();if(!quiz)throw new Error("Quiz fuera de esta cohorte");
  if(a.status!=="in_progress")return a;
  const items=await quizItems(a.quiz_id),{data:responses}=await db.from("lms_quiz_responses_v2").select("*").eq("attempt_id",a.id);
  const rm=new Map((responses||[]).map((r:any)=>[r.question_id,r]));let auto=0,manual=0,pendingManual=0;
  for(const item of items){
    const r:any=rm.get(item.question_id),pts=Number(item.points);
    if(item.question.question_type==="short_text"){
      if(r?.manual_score===null||r?.manual_score===undefined)pendingManual++;else manual+=Number(r.manual_score||0);
      continue;
    }
    const score=autoScore(item.question,r?.response||{},pts);auto+=Number(score||0);
    if(r)await db.from("lms_quiz_responses_v2").update({auto_score:score,saved_at:new Date().toISOString()}).eq("attempt_id",a.id).eq("question_id",item.question_id);
    else await db.from("lms_quiz_responses_v2").insert({attempt_id:a.id,question_id:item.question_id,response:{},auto_score:0});
  }
  const status=pendingManual?"submitted":"reviewed",submittedAt=expired&&a.expires_at?a.expires_at:new Date().toISOString(),score=auto+manual;
  const {data:updated,error}=await db.from("lms_quiz_attempts_v2").update({status,submitted_at:submittedAt,auto_score:auto,manual_score:manual,score}).eq("id",a.id).select("*").single();if(error)throw error;
  await syncQuizGrade(run,updated);await audit(ctx.user.id,"bigdata.quiz.attempt.submit","quiz_attempt",a.id,{quiz_id:a.quiz_id,attempt:a.attempt,expired,pending_manual:pendingManual});
  return updated;
}
async function submitQuiz(ctx:any,run:any,body:any){
  const attemptId=text(body.attempt_id,80,true);
  const updated=await finalizeAttempt(ctx,run,attemptId,false);
  return {ok:true,attempt:updated};
}
async function gradeResponse(ctx:any,run:any,body:any){
  requireTeacher(ctx);const attemptId=text(body.attempt_id,80,true),questionId=text(body.question_id,80,true);
  const {data:a}=await db.from("lms_quiz_attempts_v2").select("*").eq("id",attemptId).maybeSingle();if(!a)throw new Error("Intento no encontrado");
  const {data:qz}=await db.from("lms_quizzes_v2").select("*").eq("id",a.quiz_id).eq("course_run_id",run.id).maybeSingle();if(!qz)throw new Error("Quiz fuera de la cohorte");
  const {data:item}=await db.from("lms_quiz_items_v2").select("*").eq("quiz_id",a.quiz_id).eq("question_id",questionId).maybeSingle();if(!item)throw new Error("Pregunta fuera del quiz");
  const {data:q}=await db.from("lms_questions_v2").select("question_type").eq("id",questionId).maybeSingle();if(q?.question_type!=="short_text")throw new Error("Solo las respuestas de texto requieren calificación manual");
  const score=Number(body.score);if(!Number.isFinite(score)||score<0||score>Number(item.points))throw new Error("Puntaje fuera de rango");
  const {error}=await db.from("lms_quiz_responses_v2").update({manual_score:score,feedback:text(body.feedback,5000),graded_by:ctx.user.id,graded_at:new Date().toISOString()}).eq("attempt_id",attemptId).eq("question_id",questionId);if(error)throw error;
  const items=await quizItems(a.quiz_id),{data:rs}=await db.from("lms_quiz_responses_v2").select("*").eq("attempt_id",attemptId);
  const rm=new Map((rs||[]).map((r:any)=>[r.question_id,r]));let auto=0,manual=0,pending=0;
  for(const x of items){const r:any=rm.get(x.question_id);auto+=Number(r?.auto_score||0);if(x.question.question_type==="short_text"){if(r?.manual_score===null||r?.manual_score===undefined)pending++;else manual+=Number(r.manual_score)}}
  const status=pending?"submitted":"reviewed",total=auto+manual;
  const {data:updated}=await db.from("lms_quiz_attempts_v2").update({manual_score:manual,auto_score:auto,score:total,status}).eq("id",attemptId).select("*").single();
  await syncQuizGrade(run,updated);await audit(ctx.user.id,"bigdata.quiz.response.grade","quiz_attempt",attemptId,{question_id:questionId,score});
  return {ok:true,attempt:updated};
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  let action="quizzes",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"quizzes";
  else{try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}action=String(body.action||"quizzes")}
  try{
    if(action==="quizzes")return out(req,await quizzesForUser(ctx,run));
    if(action==="start_quiz")return out(req,await startQuiz(ctx,run,body));
    if(action==="save_response")return out(req,await saveResponse(ctx,run,body));
    if(action==="submit_quiz")return out(req,await submitQuiz(ctx,run,body));
    if(action==="prepare_file_upload")return out(req,await prepareFileUpload(ctx,run,body));
    if(action==="submit_file_assignment")return out(req,await submitFileAssignment(ctx,run,body));
    if(action==="file_download_url")return out(req,await fileDownloadUrl(ctx,run,body));
    if(action==="teacher_overview")return out(req,await teacherOverview(ctx,run));
    if(action==="teacher_save_question")return out(req,await saveQuestion(ctx,run,body));
    if(action==="teacher_save_quiz")return out(req,await saveQuiz(ctx,run,body));
    if(action==="teacher_set_quiz_items")return out(req,await setQuizItems(ctx,run,body));
    if(action==="teacher_grade_response")return out(req,await gradeResponse(ctx,run,body));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});