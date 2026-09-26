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
  const o=req.headers.get("origin"); if(!o)return "";
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
function text(v:any,max:number,required=false){const s=String(v??"").trim();if(required&&!s)throw new Error("Campo obligatorio");return s.slice(0,max)}
function isoDate(v:any){if(!v)return null;const d=new Date(String(v)+"T00:00:00Z");if(!Number.isFinite(d.getTime()))throw new Error("Fecha inválida");return d.toISOString().slice(0,10)}
async function audit(actor:string,action:string,entity:string,id:string|null,metadata:any={}){
  await db.from("lms_audit_log").insert({actor_user_id:actor,action,entity_type:entity,entity_id:id,metadata:{course_code:COURSE,run_code:RUN_CODE,...metadata}}).then(()=>{}).catch(()=>{});
}
function csvEscape(v:any){const s=String(v??"").replace(/\r?\n/g," ");return /[",]/.test(s)?'"'+s.replace(/"/g,'""')+'"':s}
function csv(headers:string[],rows:any[][]){return "\ufeff"+[headers,...rows].map(r=>r.map(csvEscape).join(",")).join("\r\n")+"\r\n"}
function xml(v:any){return String(v??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;").replace(/'/g,"&apos;")}
function ident(v:any){const s=String(v??"item").replace(/[^A-Za-z0-9_.-]+/g,"-").replace(/^-+/,"");return (s||"item").slice(0,120)}
function splitName(display:string,username:string){
  const parts=String(display||"").trim().split(/\s+/).filter(Boolean);
  if(parts.length>=2)return {given:parts.slice(0,-1).join(" "),family:parts.at(-1)!};
  return {given:parts[0]||username||"Usuario",family:"N/D"};
}
function ymd(v:any){if(!v)return "";const d=new Date(v);return Number.isFinite(d.getTime())?d.toISOString().slice(0,10):""}
function icsStamp(v:any){const d=new Date(v);return d.toISOString().replace(/[-:]/g,"").replace(/\.\d{3}Z$/,"Z")}
function uid(prefix:string,id:any){return prefix+"-"+String(id).replace(/[^A-Za-z0-9._@/-]+/g,"-")}

/* ----------------------------- QTI 3 export ----------------------------- */
function qtiOutcome(max:number){return '<qti-outcome-declaration identifier="SCORE" cardinality="single" base-type="float" normal-maximum="'+max+'"><qti-default-value><qti-value>0</qti-value></qti-default-value></qti-outcome-declaration>'}
function qtiSetScore(max:number,condition:string){
  return '<qti-response-processing><qti-response-condition><qti-response-if>'+condition+
    '<qti-set-outcome-value identifier="SCORE"><qti-base-value base-type="float">'+max+'</qti-base-value></qti-set-outcome-value>'+
    '</qti-response-if><qti-response-else><qti-set-outcome-value identifier="SCORE"><qti-base-value base-type="float">0</qti-base-value></qti-set-outcome-value></qti-response-else></qti-response-condition></qti-response-processing>';
}
function qtiItem(q:any){
  const id=ident(q.code+"-v"+q.version),max=Number(q.default_points||1),prompt=xml(q.prompt),opts=Array.isArray(q.options)?q.options:[];
  let decl="",body="",processing="";
  if(q.question_type==="single_choice"||q.question_type==="multiple_choice"){
    const correct=(q.answer_key?.correct_option_ids||[]).map(String);
    const card=q.question_type==="multiple_choice"?"multiple":"single";
    decl='<qti-response-declaration identifier="RESPONSE" cardinality="'+card+'" base-type="identifier"><qti-correct-response>'+
      correct.map((x:string)=>'<qti-value>'+xml(x)+'</qti-value>').join("")+'</qti-correct-response></qti-response-declaration>';
    body='<qti-item-body><p>'+prompt+'</p><qti-choice-interaction response-identifier="RESPONSE" shuffle="false" max-choices="'+(q.question_type==="multiple_choice"?0:1)+'">'+
      opts.map((o:any)=>'<qti-simple-choice identifier="'+xml(o.id)+'">'+xml(o.text)+'</qti-simple-choice>').join("")+
      '</qti-choice-interaction></qti-item-body>';
    processing='<qti-response-processing template="https://www.imsglobal.org/question/qti_v3p0/rptemplates/match_correct.xml"/>';
  }else if(q.question_type==="true_false"){
    const corr=q.answer_key?.value===true?"TRUE":"FALSE";
    decl='<qti-response-declaration identifier="RESPONSE" cardinality="single" base-type="identifier"><qti-correct-response><qti-value>'+corr+'</qti-value></qti-correct-response></qti-response-declaration>';
    body='<qti-item-body><p>'+prompt+'</p><qti-choice-interaction response-identifier="RESPONSE" shuffle="false" max-choices="1"><qti-simple-choice identifier="TRUE">Verdadero</qti-simple-choice><qti-simple-choice identifier="FALSE">Falso</qti-simple-choice></qti-choice-interaction></qti-item-body>';
    processing='<qti-response-processing template="https://www.imsglobal.org/question/qti_v3p0/rptemplates/match_correct.xml"/>';
  }else if(q.question_type==="numeric"){
    const value=Number(q.answer_key?.value),tol=Math.max(0,Number(q.answer_key?.tolerance||0));
    decl='<qti-response-declaration identifier="RESPONSE" cardinality="single" base-type="float"><qti-correct-response><qti-value>'+value+'</qti-value></qti-correct-response></qti-response-declaration>';
    body='<qti-item-body><p>'+prompt+'</p><qti-text-entry-interaction response-identifier="RESPONSE" expected-length="16"/></qti-item-body>';
    const cond=tol>0?'<qti-equal tolerance-mode="absolute" tolerance="'+tol+'"><qti-variable identifier="RESPONSE"/><qti-correct identifier="RESPONSE"/></qti-equal>':'<qti-match><qti-variable identifier="RESPONSE"/><qti-correct identifier="RESPONSE"/></qti-match>';
    processing=qtiSetScore(max,cond);
  }else if(q.question_type==="short_text"){
    decl='<qti-response-declaration identifier="RESPONSE" cardinality="single" base-type="string"/>';
    body='<qti-item-body><p>'+prompt+'</p><qti-extended-text-interaction response-identifier="RESPONSE" expected-lines="5"/></qti-item-body>';
    processing="";
  }else{
    throw new Error("Tipo de pregunta no soportado por el exportador QTI: "+String(q.question_type||""));
  }
  return '<?xml version="1.0" encoding="UTF-8"?>\n<qti-assessment-item xmlns="http://www.imsglobal.org/xsd/imsqtiasi_v3p0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/imsqtiasi_v3p0 https://purl.imsglobal.org/spec/qti/v3p0/schema/xsd/imsqti_asiv3p0_v1p0.xsd" identifier="'+id+'" title="'+xml(q.code)+'" adaptive="false" time-dependent="false">'+decl+qtiOutcome(max)+body+processing+'</qti-assessment-item>';
}
function qtiManifest(items:any[]){
  const resources=items.map(q=>{const id=ident(q.code+"-v"+q.version),href="items/"+id+".xml";return '<resource identifier="'+id+'" type="imsqti_item_xmlv3p0" href="'+href+'"><file href="'+href+'"/></resource>'}).join("");
  return '<?xml version="1.0" encoding="UTF-8"?>\n<manifest identifier="BIGDATA-QTI3" xmlns="http://www.imsglobal.org/xsd/qti/qtiv3p0/imscp_v1p1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.imsglobal.org/xsd/qti/qtiv3p0/imscp_v1p1 https://purl.imsglobal.org/spec/qti/v3p0/schema/xsd/imsqtiv3p0_imscpv1p2_v1p0.xsd"><metadata><schema>QTI Package</schema><schemaversion>3.0.0</schemaversion></metadata><organizations/><resources>'+resources+'</resources></manifest>';
}
async function exportQti(ctx:any,run:any){
  requireTeacher(ctx);
  const {data,error}=await db.from("lms_questions_v2").select("*").eq("course_run_id",run.id).eq("active",true).order("code");if(error)throw error;
  const items=data||[];if(!items.length)throw new Error("No hay preguntas activas para exportar");
  const files=[{name:"imsmanifest.xml",content:qtiManifest(items),mime:"application/xml"},...items.map(q=>{const id=ident(q.code+"-v"+q.version);return {name:"items/"+id+".xml",content:qtiItem(q),mime:"application/xml"}})];
  await audit(ctx.user.id,"bigdata.interop.export.qti","interop_export",null,{items:items.length,profile:"QTI 3.0"});
  return {ok:true,format:"QTI 3.0 package",certified:false,files,warnings:["Exportación basada en QTI 3.0/3.0.1. No equivale a certificación de conformidad 1EdTech."]};
}

/* -------------------------- OneRoster 1.2.1 bulk -------------------------- */
async function interopData(run:any){
  const [{data:enrollments},{data:assignments},{data:sessions}] = await Promise.all([
    db.from("lms_run_enrollments").select("user_id,role,status,enrolled_at").eq("course_run_id",run.id).eq("status","active"),
    db.from("lms_assignments_v2").select("*").eq("course_run_id",run.id).eq("active",true).order("created_at"),
    db.from("lms_run_sessions_v2").select("*").eq("course_run_id",run.id).order("session_number")
  ]);
  const userIds=(enrollments||[]).map((x:any)=>x.user_id);
  const assignmentIds=(assignments||[]).map((x:any)=>x.id);
  const [{data:users},{data:subs}]=await Promise.all([
    userIds.length?db.from("lms_users").select("id,username,display_name,email,active,updated_at").in("id",userIds):Promise.resolve({data:[]} as any),
    assignmentIds.length?db.from("lms_submissions_v2").select("*").in("assignment_id",assignmentIds).order("attempt",{ascending:false}):Promise.resolve({data:[]} as any)
  ]);
  return {enrollments:enrollments||[],assignments:assignments||[],sessions:sessions||[],users:users||[],subs:subs||[]};
}
function manifestCsv(present:Set<string>){
  const names=["academicSessions","categories","classes","classResources","courses","courseResources","demographics","enrollments","lineItemLearningObjectiveIds","lineItems","lineItemScoreScales","orgs","resources","resultLearningObjectiveIds","results","resultScoreScales","roles","scoreScales","userProfiles","userResources","users"];
  return csv(["propertyName","value"],[
    ["manifest.version","1.0"],["oneroster.version","1.2"],
    ...names.map(n=>["file."+n,present.has(n)?"bulk":"absent"]),
    ["source.systemName","BigData2026 LMS"],["source.systemCode","bigdata-2026-2"]
  ]);
}
async function exportOneRoster(ctx:any,run:any){
  requireTeacher(ctx);
  if(!run.starts_on||!run.ends_on)throw new Error("Configura primero las fechas oficiales de inicio y fin del período");
  const d=await interopData(run),org="org-ucentral",term=uid("term",run.id),course=uid("course",COURSE),clazz=uid("class",run.id);
  const start=ymd(run.starts_on),end=ymd(run.ends_on),schoolYear=String(new Date(run.ends_on).getUTCFullYear());
  const userMap=new Map(d.users.map((u:any)=>[u.id,u]));
  const enrMap=new Map(d.enrollments.map((e:any)=>[e.user_id,e]));
  const files:any[]=[];
  files.push({name:"academicSessions.csv",content:csv(["sourcedId","status","dateLastModified","title","type","startDate","endDate","parentSourcedId","schoolYear"],[[term,"","","Big Data 2026-2S","term",start,end,"",schoolYear]])});
  const cats=[...new Set(d.assignments.map((a:any)=>String(a.category||"coursework")))];const catId=(c:string)=>uid("cat",c);
  if(cats.length)files.push({name:"categories.csv",content:csv(["sourcedId","status","dateLastModified","title","weight"],cats.map(c=>[catId(c),"","",c,""]))});
  files.push({name:"orgs.csv",content:csv(["sourcedId","status","dateLastModified","name","type","identifier","parentSourcedId"],[[org,"","","Universidad Central","school","Universidad Central",""]])});
  files.push({name:"courses.csv",content:csv(["sourcedId","status","dateLastModified","schoolYearSourcedId","title","courseCode","grades","orgSourcedId","subjects","subjectCodes"],[[course,"","",term,"Big Data 2026-2S","BIGDATA-2026-2","",org,"Big Data","BIGDATA"]])});
  files.push({name:"classes.csv",content:csv(["sourcedId","status","dateLastModified","title","grades","courseSourcedId","classCode","classType","location","schoolSourcedId","termSourcedIds","subjects","subjectCodes","periods"],[[clazz,"","","Big Data 2026-2S · Grupo 2","",course,"BIGDATA-2026-2","scheduled","",org,term,"Big Data","BIGDATA",""]])});
  const userRows=d.users.map((u:any)=>{const n=splitName(u.display_name,u.username);return [u.id,"","",u.active?"true":"false",u.username,"",n.given,n.family,"","",u.email||"","","","","","","",n.given,"",n.family,org,""]});
  if(userRows.length)files.push({name:"users.csv",content:csv(["sourcedId","status","dateLastModified","enabledUser","username","userIds","givenName","familyName","middleName","identifier","email","sms","phone","agentSourcedIds","grades","password","userMasterIdentifier","preferredGivenName","preferredMiddleName","preferredFamilyName","primaryOrgSourcedId","pronouns"],userRows)});
  if(d.users.length)files.push({name:"roles.csv",content:csv(["sourcedId","status","dateLastModified","userSourcedId","roleType","role","beginDate","endDate","orgSourcedId","userProfileSourcedId"],d.users.map((u:any)=>{const e:any=enrMap.get(u.id);const role=e?.role==="student"?"student":"teacher";return [uid("role",u.id),"","",u.id,"primary",role,start,end,org,""]}))});
  if(d.enrollments.length)files.push({name:"enrollments.csv",content:csv(["sourcedId","status","dateLastModified","classSourcedId","schoolSourcedId","userSourcedId","role","primary","beginDate","endDate"],d.enrollments.map((e:any)=>[uid("enr",e.user_id),"","",clazz,org,e.user_id,e.role==="student"?"student":"teacher",e.role==="teacher"?"true":"",start,end]))});
  if(d.assignments.length)files.push({name:"lineItems.csv",content:csv(["sourcedId","status","dateLastModified","title","description","assignDate","dueDate","classSourcedId","categorySourcedId","academicSessionSourcedId","resultValueMin","resultValueMax","schoolSourcedId"],d.assignments.map((a:any)=>[a.id,"","",a.title,a.instructions||"",ymd(a.created_at),ymd(a.due_at||run.ends_on),clazz,catId(String(a.category||"coursework")),term,0,a.max_score,org]))});
  const latest=new Map<string,any>();
  for(const s of d.subs){const k=s.assignment_id+"|"+s.user_id;if(!latest.has(k))latest.set(k,s)}
  const resultRows=[...latest.values()].filter((s:any)=>s.score!==null&&s.score!==undefined).map((s:any)=>[s.id,"","",s.assignment_id,s.user_id,s.status==="reviewed"?"fully graded":"submitted",s.score,ymd(s.reviewed_at||s.submitted_at),s.feedback||"","",clazz,"false","false","false","false"]);
  if(resultRows.length)files.push({name:"results.csv",content:csv(["sourcedId","status","dateLastModified","lineItemSourcedId","studentSourcedId","scoreStatus","score","scoreDate","comment","textScore","classSourcedId","inProgress","incomplete","late","missing"],resultRows)});
  const present=new Set(files.map(f=>f.name.replace(".csv","")));
  files.unshift({name:"manifest.csv",content:manifestCsv(present)});
  await audit(ctx.user.id,"bigdata.interop.export.oneroster","interop_export",null,{users:d.users.length,assignments:d.assignments.length,results:resultRows.length,profile:"OneRoster 1.2.1 bulk"});
  return {ok:true,format:"OneRoster 1.2.1 CSV bulk package",certified:false,files:files.map(f=>({...f,mime:"text/csv;charset=utf-8"})),warnings:[
    "OneRoster está orientado principalmente a K-12; este paquete es un perfil de compatibilidad para una cohorte de educación superior.",
    "Los nombres se separan de display_name usando el último término como familyName; revisa esa transformación antes de intercambiar PII.",
    "La exportación no incluye contraseñas ni credenciales."
  ]};
}

/* ------------------------------ Calendar ICS ------------------------------ */
async function exportIcs(ctx:any,run:any){
  requireTeacher(ctx);const d=await interopData(run),events:any[]=[];
  for(const s of d.sessions){if(!s.starts_at)continue;events.push({uid:"session-"+run.id+"-"+s.session_number,at:s.starts_at,summary:"Big Data · S"+String(s.session_number).padStart(2,"0")+" · "+s.title,description:s.summary||""})}
  for(const a of d.assignments){if(!a.due_at)continue;events.push({uid:"assignment-"+a.id,at:a.due_at,summary:"Entrega · "+a.title,description:a.instructions||""})}
  const esc=(x:any)=>String(x??"").replace(/\\/g,"\\\\").replace(/\n/g,"\\n").replace(/,/g,"\\,").replace(/;/g,"\\;");
  const body=["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//BigData2026//LMS//ES","CALSCALE:GREGORIAN","METHOD:PUBLISH",
    ...events.flatMap(e=>["BEGIN:VEVENT","UID:"+e.uid+"@bigdata2026","DTSTAMP:"+icsStamp(new Date()),"DTSTART:"+icsStamp(e.at),"SUMMARY:"+esc(e.summary),"DESCRIPTION:"+esc(e.description),"END:VEVENT"]),
    "END:VCALENDAR"].join("\r\n")+"\r\n";
  await audit(ctx.user.id,"bigdata.interop.export.ics","interop_export",null,{events:events.length});
  return {ok:true,format:"iCalendar 2.0",files:[{name:"bigdata-2026-2.ics",content:body,mime:"text/calendar;charset=utf-8"}],warnings:events.length?[]:["No hay fechas registradas en sesiones ni tareas; el calendario quedará vacío."]};
}
async function exportGradebook(ctx:any,run:any){
  requireTeacher(ctx);const d=await interopData(run),students=d.enrollments.filter((e:any)=>e.role==="student"),users=new Map(d.users.map((u:any)=>[u.id,u]));
  const latest=new Map<string,any>();for(const s of d.subs){const k=s.assignment_id+"|"+s.user_id;if(!latest.has(k))latest.set(k,s)}
  const headers=["user_id","estudiante","correo",...d.assignments.map((a:any)=>a.code)];
  const rows=students.map((e:any)=>{const u:any=users.get(e.user_id);return [e.user_id,u?.display_name||u?.username||"",u?.email||"",...d.assignments.map((a:any)=>{const s=latest.get(a.id+"|"+e.user_id);return s?.score??""})]});
  await audit(ctx.user.id,"bigdata.interop.export.gradebook","interop_export",null,{students:students.length,assignments:d.assignments.length});
  return {ok:true,format:"BigData Gradebook CSV",files:[{name:"bigdata-gradebook.csv",content:csv(headers,rows),mime:"text/csv;charset=utf-8"}],warnings:[]};
}
async function saveRunDates(ctx:any,run:any,body:any){
  requireTeacher(ctx);const start=isoDate(body.starts_on),end=isoDate(body.ends_on);if(!start||!end||end<=start)throw new Error("El fin del período debe ser posterior al inicio");
  const {data,error}=await db.from("lms_course_runs").update({starts_on:start,ends_on:end}).eq("id",run.id).select("id,starts_on,ends_on").single();if(error)throw error;
  await audit(ctx.user.id,"bigdata.interop.run_dates.update","course_run",run.id,{starts_on:start,ends_on:end});return {ok:true,run:data};
}
async function overview(ctx:any,run:any){
  requireTeacher(ctx);
  const [{count:questions},{count:students},{count:assignments}] = await Promise.all([
    db.from("lms_questions_v2").select("*",{count:"exact",head:true}).eq("course_run_id",run.id).eq("active",true),
    db.from("lms_run_enrollments").select("*",{count:"exact",head:true}).eq("course_run_id",run.id).eq("status","active").eq("role","student"),
    db.from("lms_assignments_v2").select("*",{count:"exact",head:true}).eq("course_run_id",run.id).eq("active",true)
  ]);
  return {viewer:ctx.user,run:{id:run.id,code:run.code,title:run.title,starts_on:run.starts_on,ends_on:run.ends_on,timezone:run.timezone},counts:{questions:questions||0,students:students||0,assignments:assignments||0},
    capabilities:[
      {code:"qti",title:"QTI 3.0",status:"available",detail:"Exportación de banco de preguntas a paquete QTI 3."},
      {code:"oneroster",title:"OneRoster 1.2.1 CSV",status:run.starts_on&&run.ends_on?"available":"needs_config",detail:"Perfil de compatibilidad bulk; requiere fechas oficiales del período."},
      {code:"ics",title:"iCalendar",status:"available",detail:"Sesiones y entregas que tengan fecha registrada."},
      {code:"gradebook",title:"Gradebook CSV",status:"available",detail:"Matriz simple para análisis o respaldo."},
      {code:"eduapi",title:"Edu-API",status:"planned",detail:"Preferible para integración institucional de educación superior."},
      {code:"lti",title:"LTI 1.3 / Advantage",status:"not_configured",detail:"Requiere plataforma, client/deployment IDs y llaves institucionales."},
      {code:"oidc",title:"SSO OIDC",status:"not_configured",detail:"Requiere proveedor de identidad institucional."},
      {code:"xapi",title:"xAPI / Caliper",status:"not_configured",detail:"No hay LRS/consumer configurado."}
    ]};
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);
  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  requireTeacher(ctx);
  let action="overview",body:any={};
  if(req.method==="GET")action=new URL(req.url).searchParams.get("action")||"overview";
  else{try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}action=String(body.action||"overview")}
  try{
    if(action==="overview")return out(req,await overview(ctx,run));
    if(action==="save_run_dates")return out(req,await saveRunDates(ctx,run,body));
    if(action==="export_qti")return out(req,await exportQti(ctx,run));
    if(action==="export_oneroster")return out(req,await exportOneRoster(ctx,run));
    if(action==="export_ics")return out(req,await exportIcs(ctx,run));
    if(action==="export_gradebook")return out(req,await exportGradebook(ctx,run));
    return out(req,{error:"Acción desconocida"},400);
  }catch(e){
    if(String((e as any)?.message)==="NO_AUTH")return out(req,{error:"No autorizado"},403);
    return out(req,{error:String((e as any)?.message||e).slice(0,500)},400);
  }
});