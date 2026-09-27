import { createClient } from "npm:@supabase/supabase-js@2";

const db=createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  {auth:{persistSession:false}}
);

const COURSE="bigdata";
const RUN_CODE="bigdata-2026-2";
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const PUBLIC_TRACK_EVENTS=new Set([
  "session_entered","page_opened","page_closed","heartbeat",
  "resource_opened","presentation_opened","notebook_opened","guide_opened",
  "lab_started","checkpoint_started","slide_viewed","lab_interaction","ui_action"
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
  for(const k of ["source","action","label","path","resource_type","resource_id","slide","chapter","outcome","control","value"]){
    const v=x[k];
    if(typeof v==="string")z[k]=v.slice(0,240);
    else if(typeof v==="number"||typeof v==="boolean"||v===null)z[k]=v;
  }
  return z;
}
function failIf(error:any,label:string){
  if(error)throw new Error(label+": "+String(error?.message||error).slice(0,320));
}
function clientId(v:any,label:string){
  const s=String(v??"").trim();
  if(!s)return null;
  if(!/^[A-Za-z0-9._:-]{8,120}$/.test(s))throw new Error(label+" inválido");
  return s;
}
function isDuplicate(error:any){return String(error?.code||"")==="23505"}
function trimText(v:any,min:number,max:number,label:string){
  const s=String(v??"").trim();
  if(s.length<min)throw new Error(label+" debe tener al menos "+min+" caracteres");
  return s.slice(0,max);
}
function randomLabCode(){
  const alphabet="ABCDEFGHJKMNPQRSTUVWXYZ23456789",bytes=crypto.getRandomValues(new Uint8Array(8));
  return [...bytes].map(b=>alphabet[b%alphabet.length]).join("");
}
async function seedFor(userId:string,runId:string,activityCode:string){
  return (await sha256(userId+"|"+runId+"|"+activityCode)).slice(0,16);
}
function s09TopKProfile(seed:string,k=5){
  const base=[
    {label:"aeronaves KFIR",aero:true},{label:"flota aérea militar",aero:true},
    {label:"sistemas aeronáuticos",aero:true},{label:"helicópteros",aero:true},
    {label:"infraestructura militar",aero:false},{label:"transporte aéreo",aero:true},
    {label:"pista aeroportuaria",aero:false},{label:"edificio militar",aero:false}
  ];
  const offset=parseInt(seed.slice(0,8),16)%base.length;
  const items=base.map((_,i)=>base[(i+offset)%base.length]);
  return {items,count:items.slice(0,k).filter(x=>x.aero).length,k};
}
async function publicCatalog(codes:string[],userId:string,runId:string){
  if(!codes.length)return {catalog:[],seeds:{}};
  const {data,error}=await db.from("bd_activity_catalog")
    .select("code,evaluator,steps,competency_code,seeded,wall_prompt,version")
    .in("code",codes);
  failIf(error,"No se pudo cargar el catálogo de actividades");
  const seeds:Record<string,string>={};
  for(const x of data||[])if(x.seeded)seeds[x.code]=await seedFor(userId,runId,x.code);
  return {catalog:data||[],seeds};
}
async function ownEvidence(userId:string,runId:string,n:number){
  const {data,error}=await db.from("bd_evidence")
    .select("id,activity_code,step_id,payload,source,verdict,feedback,catalog_version,created_at,reviewed_by,reviewed_at,rubric")
    .eq("user_id",userId).eq("course_run_id",runId).eq("session_number",n)
    .order("created_at",{ascending:false}).limit(100);
  failIf(error,"No se pudo cargar la evidencia");
  return data||[];
}
const TRANSFER_REVIEW_CODES=new Set(["bd-s09-lab3","bd-s09-lab4","bd-s09-lab8"]);
const LAB9_STRUCTURED={
  reason:[
    "Las señales lexical y semántica aportan información complementaria.",
    "La coincidencia exacta de términos fue decisiva en este caso.",
    "La cercanía semántica recuperó mejor la intención aunque cambió el vocabulario."
  ],
  decision:[
    "Priorizar recuperación lexical.",
    "Priorizar recuperación semántica.",
    "Usar recuperación híbrida mediante fusión de rankings."
  ],
  rejected_alternative:[
    "Descarto usar solo lexical porque puede perder paráfrasis.",
    "Descarto usar solo semántica porque puede perder coincidencias exactas.",
    "Descarto sumar scores crudos porque no comparten una escala comparable."
  ],
  limit:[
    "La evaluación depende de juicios de relevancia sobre solo cinco resultados.",
    "El resultado puede cambiar con otra consulta o con otro corpus.",
    "El resultado depende del modelo de embeddings utilizado."
  ]
};
const TRANSFER_ALLOWED:Record<string,Record<string,string[]>>={
  "bd-s09-lab3":{
    result:["El Top-5 concentra suficientes candidatos relevantes","El Top-5 deja demasiados candidatos relevantes fuera"],
    decision:["Mantendría k=5 para esta necesidad","Aumentaría k para revisar más vecinos"],
    rejected_alternative:["Descarto aumentar k porque añade revisión innecesaria","Descarto mantener k=5 porque limita demasiado el recall"],
    interpretation:["El valor de k controla cuántos vecinos se revisan, no la relevancia por sí sola","Más vecinos no significa automáticamente mejores resultados"],
    limit:["La conclusión depende de los juicios de relevancia del Top-5","El resultado puede cambiar con otra consulta o embedding"]
  },
  "bd-s09-lab4":{
    result:["BM25 recuperó mejor la coincidencia exacta del caso","La búsqueda semántica recuperó mejor la intención del caso","Los dos mecanismos aportaron señales complementarias"],
    decision:["Priorizaría recuperación lexical","Priorizaría recuperación semántica","Usaría una estrategia híbrida"],
    rejected_alternative:["Descarto solo lexical porque pierde paráfrasis","Descarto solo semántica porque puede perder identificadores exactos","Descarto usar un único mecanismo porque las señales son complementarias"],
    interpretation:["Lexical prioriza coincidencia de términos y semántica cercanía de representación","Los scores de ambos mecanismos no son probabilidades comparables directamente"],
    limit:["El ranking depende de la consulta y del corpus usado","La evaluación requiere juicios de relevancia y no solo mirar el score"]
  },
  "bd-s09-lab8":{
    result:["RRF cambió el orden al combinar posiciones de ambos rankings","RRF mantuvo en cabeza documentos apoyados por ambos rankings"],
    decision:["Usaría RRF para combinar los rankings","Mantendría los rankings separados para este caso"],
    rejected_alternative:["Descarto sumar scores crudos porque sus escalas no son equivalentes","Descarto elegir un único ranking porque perdería señal complementaria"],
    interpretation:["RRF fusiona posiciones y no necesita comparar scores crudos","Un documento respaldado por varios rankings puede subir de posición"],
    limit:["El parámetro de fusión puede cambiar el orden final","La fusión no reemplaza la evaluación de relevancia"]
  }
};
async function submitEvidence(userId:string,runId:string,n:number,activity:any,payload:any,source:string,rawClientId:any=null){
  if(!activity||activity.kind!=="lab")throw new Error("La actividad no es un laboratorio");
  const evidenceClientId=clientId(rawClientId,"client_evidence_id");
  if(evidenceClientId){
    const {data:existing,error:existingError}=await db.from("bd_evidence")
      .select("id,activity_code,verdict,feedback,created_at,payload")
      .eq("user_id",userId).eq("course_run_id",runId).eq("client_evidence_id",evidenceClientId).maybeSingle();
    failIf(existingError,"No se pudo comprobar la idempotencia de la evidencia");
    if(existing){
      if(existing.activity_code!==activity.code)throw new Error("client_evidence_id ya fue usado en otra actividad");
      return {ok:true,duplicate:true,completed:["correct","accepted"].includes(existing.verdict),
        verdict:existing.verdict,feedback:existing.feedback,evidence:existing};
    }
  }
  const {data:catalog,error:catalogError}=await db.from("bd_activity_catalog").select("*")
    .eq("code",activity.code).maybeSingle();
  failIf(catalogError,"No se pudo cargar el evaluador");
  if(!catalog)throw new Error("El laboratorio no tiene evaluador configurado");
  if(n===9&&catalog.evaluator==="self-report")throw new Error("Este LAB S09 requiere autocorrección. Recarga la presentación e inténtalo de nuevo.");
  const seed=await seedFor(userId,runId,activity.code),normalized:any={};
  const transferMode=n===9&&source==="presentation-transfer"&&TRANSFER_REVIEW_CODES.has(activity.code);
  let verdict="accepted",feedback="Evidencia registrada.";
  if(transferMode){
    const {data:selfProgress,error:selfError}=await db.from("bd_lms_activity_progress")
      .select("status,metadata").eq("user_id",userId).eq("course_run_id",runId)
      .eq("activity_code",activity.code).maybeSingle();
    failIf(selfError,"No se pudo comprobar la autocomprobación previa");
    const selfVerified=selfProgress?.metadata?.self_check_verified===true||
      selfProgress?.metadata?.evidence_verdict==="correct"||selfProgress?.status==="completed";
    if(!selfVerified)throw new Error("Completa primero la autocomprobación del LAB antes de enviar la transferencia.");
    const allowed=TRANSFER_ALLOWED[activity.code];
    if(!allowed)throw new Error("Evidencia estructurada no configurada");
    for(const key of ["result","decision","rejected_alternative","interpretation","limit"]){
      const value=String(payload?.[key]||"");
      if(!allowed[key]?.includes(value))throw new Error("Selecciona una opción válida en "+key);
      normalized[key]=value;
    }
    verdict="pending_review";
    feedback="Evidencia estructurada recibida. Está pendiente de revisión docente.";
  }else if(catalog.evaluator==="seeded-numeric"&&catalog.config?.generator==="s09_topk_aero_count"){
    const k=Number(catalog.config?.k||5),expected=s09TopKProfile(seed,k).count,result=Number(payload?.result);
    if(!Number.isFinite(result))throw new Error("Registra el resultado numérico obtenido");
    const decision=String(payload?.decision||"");
    if(!["mantener","subir"].includes(decision))throw new Error("Elige qué harías con k");
    const expectedDecision=expected>=4?"mantener":"subir";
    normalized.k=k;normalized.result=result;normalized.decision=decision;
    if(result!==expected){verdict="incorrect";feedback="El conteo no coincide con tu ranking. Revisa los cinco candidatos y vuelve a comprobar."}
    else if(decision!==expectedDecision){verdict="incorrect";feedback=expected>=4?"Tu conteo es correcto. Con al menos 4 de 5 candidatos claramente aeronáuticos, k=5 ya cubre bien esta necesidad.":"Tu conteo es correcto. Con menos de 4 candidatos claramente aeronáuticos, conviene ampliar k y revisar más vecinos."}
    else{verdict="correct";feedback="Correcto. El conteo y la decisión sobre k coinciden con tu ranking personalizado."}
  }else if(catalog.evaluator==="choice-hash"){
    const expected=catalog.config?.answers||{},wrong:string[]=[];
    for(const step of Array.isArray(catalog.steps)?catalog.steps:[]){
      const id=String(step.id||"");if(!id)continue;
      const v=String(payload?.[id]||"");
      if(step.type!=="choice"||!Array.isArray(step.options)||!step.options.some((o:any)=>String(o?.value??o)===v))throw new Error("Selecciona una opción válida en "+id);
      normalized[id]=v;
      const actual=await sha256(v),target=String(expected[id]||"");
      if(!target||actual!==target)wrong.push(id);
    }
    if(wrong.length){verdict="incorrect";const first=(catalog.steps||[]).find((s:any)=>String(s.id)===wrong[0]);feedback="Todavía no. "+String(first?.hint||"Revisa el ejemplo del LAB y vuelve a comprobar.")}
    else{verdict="correct";feedback=String(catalog.config?.success_feedback||"Correcto. Las respuestas coinciden con el concepto trabajado en el LAB.")}
  }else if(catalog.evaluator==="authentic-review"){
    if(activity.code!=="bd-s09-lab9")throw new Error("Evaluador auténtico no habilitado para esta actividad");
    const query=trimText(payload?.query,12,500,"La consulta");
    const precision=Number(payload?.precision_at_5);
    if(!Number.isFinite(precision)||precision<0||precision>1)throw new Error("Precision@5 debe estar entre 0 y 1");
    const defensible=Array.isArray(payload?.defensible_results)?payload.defensible_results.map((x:any)=>String(x||"").trim()).filter(Boolean):[];
    if(defensible.length!==2||defensible.some((x:string)=>x.length<3||x.length>220))throw new Error("Registra exactamente dos resultados defendibles");
    const falsePositive=trimText(payload?.false_positive,3,220,"El falso positivo");
    const reason=String(payload?.reason||""),decision=String(payload?.decision||""),
      rejected=String(payload?.rejected_alternative||""),limit=String(payload?.limit||"");
    if(!LAB9_STRUCTURED.reason.includes(reason))throw new Error("Selecciona una razón válida");
    if(!LAB9_STRUCTURED.decision.includes(decision))throw new Error("Selecciona una decisión válida");
    if(!LAB9_STRUCTURED.rejected_alternative.includes(rejected))throw new Error("Selecciona una alternativa válida");
    if(!LAB9_STRUCTURED.limit.includes(limit))throw new Error("Selecciona un límite válido");
    const ids=(value:any,label:string)=>{
      const xs=Array.isArray(value)?value.map((x:any)=>String(x||"").trim()).filter(Boolean):[];
      if(!xs.length||xs.length>5||xs.some((x:string)=>x.length>120))throw new Error("Revisa "+label);
      return xs;
    };
    const trace=payload?.trace&&typeof payload.trace==="object"?payload.trace:{};
    const model=trimText(trace.model,3,160,"El modelo");
    const dimensions=Math.trunc(Number(trace.dimensions));
    if(!Number.isInteger(dimensions)||dimensions<2||dimensions>100000)throw new Error("Dimensiones inválidas");
    normalized.query=query;
    normalized.precision_at_5=Math.round(precision*10000)/10000;
    normalized.defensible_results=defensible;
    normalized.false_positive=falsePositive;
    normalized.reason=reason;
    normalized.decision=decision;
    normalized.rejected_alternative=rejected;
    normalized.limit=limit;
    normalized.top5_lexical=ids(payload?.top5_lexical,"Top-5 lexical");
    normalized.top5_semantic=ids(payload?.top5_semantic,"Top-5 semántico");
    normalized.top5_hybrid=ids(payload?.top5_hybrid,"Top-5 híbrido");
    normalized.trace={source:"colab",model,dimensions};
    verdict="pending_review";
    feedback="Evidencia auténtica recibida. Está pendiente de revisión docente con rúbrica.";
  }else{
    for(const step of Array.isArray(catalog.steps)?catalog.steps:[]){
      const id=String(step.id||"");if(!id)continue;
      if(step.type==="number"){
        const v=Number(payload?.[id]);if(!Number.isFinite(v))throw new Error("Completa "+id);normalized[id]=v;
      }else if(step.type==="choice"){
        const v=String(payload?.[id]||"");if(!Array.isArray(step.options)||!step.options.includes(v))throw new Error("Selecciona una opción válida en "+id);normalized[id]=v;
      }else{
        normalized[id]=trimText(payload?.[id],Number(step.min_chars||1),1200,id);
      }
    }
    feedback="Evidencia recibida. Este laboratorio es formativo y queda disponible para revisión.";
  }
  const now=new Date().toISOString();
  const {data:evidence,error:evidenceError}=await db.from("bd_evidence").insert({
    user_id:userId,course_run_id:runId,session_number:n,activity_code:activity.code,
    step_id:transferMode?"transfer":"submission",payload:normalized,seed,source,client_evidence_id:evidenceClientId,
    verdict,feedback,catalog_version:Number(catalog.version||1),created_at:now
  }).select("id,activity_code,verdict,feedback,created_at,payload").single();
  failIf(evidenceError,"No se pudo guardar la evidencia");
  const {data:p,error:progressError}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",activity.code).maybeSingle();
  failIf(progressError,"No se pudo leer el progreso del laboratorio");
  const verifiedNow=["correct","accepted"].includes(verdict),
    requiresTransfer=Boolean(catalog.config?.requires_transfer)&&TRANSFER_REVIEW_CODES.has(activity.code),
    completed=verifiedNow&&!transferMode&&!requiresTransfer,
    selfCheckVerified=p?.metadata?.self_check_verified===true||(!transferMode&&verifiedNow),
    attempts=Number(p?.attempts||0)+1;
  const {error:upsertError}=await db.from("bd_lms_activity_progress").upsert({
    user_id:userId,course_run_id:runId,activity_code:activity.code,
    status:completed?"completed":"in_progress",started_at:p?.started_at||now,attempts,
    score:0,max_score:0,completed_at:completed?(p?.completed_at||now):null,updated_at:now,
    metadata:{...(p?.metadata||{}),source:transferMode?"transfer-evidence":"evidence",evidence_id:evidence?.id||null,evidence_verdict:verdict,
      evidence_verified:completed,self_check_verified:selfCheckVerified,transfer_required:requiresTransfer||transferMode,
      transfer_pending:transferMode&&verdict==="pending_review",last_evidence_at:now}
  },{onConflict:"user_id,course_run_id,activity_code"});
  failIf(upsertError,"No se pudo actualizar el progreso del laboratorio");
  const {error:eventError}=await db.from("bd_lms_events").insert({
    user_id:userId,course_run_id:runId,event_type:"evidence_submitted",session_number:n,
    activity_code:activity.code,metadata:{source,outcome:verdict},created_at:now
  });
  failIf(eventError,"No se pudo registrar el evento de evidencia");
  if(completed){
    const {error:verifiedError}=await db.from("bd_lms_events").insert({
      user_id:userId,course_run_id:runId,event_type:"evidence_verified",session_number:n,
      activity_code:activity.code,metadata:{source,outcome:verdict},created_at:now
    });
    failIf(verifiedError,"No se pudo registrar la verificación");
  }
  return {ok:true,completed,verdict,feedback,evidence};
}
async function issueLabCode(ctx:any,run:any,n:number){
  const now=new Date(),expires=new Date(now.getTime()+6*3600_000).toISOString();
  const {error:revokeError}=await db.from("bd_lab_codes").update({revoked_at:now.toISOString()})
    .eq("user_id",ctx.user.id).eq("course_run_id",run.id).eq("session_number",n).is("revoked_at",null);
  failIf(revokeError,"No se pudo revocar el código anterior");
  const code=randomLabCode(),hash=await sha256(code);
  const {error}=await db.from("bd_lab_codes").insert({
    code_hash:hash,user_id:ctx.user.id,course_run_id:run.id,session_number:n,
    scope:["evidence"],uses:0,max_uses:200,expires_at:expires
  });
  failIf(error,"No se pudo crear el código de laboratorio");
  const {error:eventError}=await db.from("bd_lms_events").insert({
    user_id:ctx.user.id,course_run_id:run.id,event_type:"lab_code_issued",session_number:n,
    metadata:{source:"module-v4"},created_at:now.toISOString()
  });
  failIf(eventError,"No se pudo auditar el código de laboratorio");
  return {code,expires_at:expires};
}
async function evidenceByCode(body:any){
  const raw=String(body.code||"").trim().toUpperCase();
  if(!/^[A-HJ-NP-Z2-9]{8}$/.test(raw))throw new Error("Código de laboratorio inválido");
  const hash=await sha256(raw),now=new Date();
  const {data:row,error}=await db.from("bd_lab_codes").select("*").eq("code_hash",hash).is("revoked_at",null).maybeSingle();
  failIf(error,"No se pudo validar el código");
  if(!row||new Date(row.expires_at).getTime()<=now.getTime()||Number(row.uses)>=Number(row.max_uses))throw new Error("Código de laboratorio vencido o agotado");
  const activityCode=String(body.activity_code||"");
  const {data:activity,error:activityError}=await db.from("bd_lms_activities").select("*")
    .eq("code",activityCode).eq("course_code",COURSE).eq("session_number",row.session_number).maybeSingle();
  failIf(activityError,"No se pudo validar la actividad");
  if(!activity)throw new Error("Actividad no válida para este código");
  const result=await submitEvidence(row.user_id,row.course_run_id,row.session_number,activity,body.payload||{},"notebook",body.client_evidence_id);
  const {error:useError}=await db.from("bd_lab_codes").update({uses:Number(row.uses||0)+1}).eq("code_hash",hash);
  failIf(useError,"No se pudo actualizar el uso del código");
  return result;
}

async function current(req:Request){
  const token=bearer(req);if(!token)return null;
  const {data:s}=await db.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent,created_at")
    .eq("token_hash",await sha256(token)).is("revoked_at",null).maybeSingle();
  if(!s)return null;
  const deadline=s.expires_at?Date.parse(s.expires_at):(Date.parse(s.created_at)+(s.persistent?30:1)*24*3600_000);if(!Number.isFinite(deadline)||deadline<=Date.now())return null;
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
async function touchActivity(userId:string,runId:string,activity:any,source:string,complete=false,incrementAttempts=true){
  const code=activity.code,now=new Date().toISOString();
  const {data:p}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",userId).eq("course_run_id",runId).eq("activity_code",code).maybeSingle();
  const metadata={...(p?.metadata||{}),source,visited:true,last_event:source};
  const status=complete||p?.status==="completed"?"completed":"in_progress";
  await db.from("bd_lms_activity_progress").upsert({
    user_id:userId,course_run_id:runId,activity_code:code,status,
    started_at:p?.started_at||now,attempts:Number(p?.attempts||0)+(incrementAttempts?1:0),
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
  const {error:eventError}=await db.from("bd_lms_events").insert({
    user_id:ctx.user.id,course_run_id:run.id,event_type:"challenge_answered",
    session_number:n,activity_code:code,
    metadata:{correct,attempt:attempts,first_attempt_correct:firstAttempt,mastery},created_at:now
  });
  failIf(eventError,"No se pudo registrar el intento");
  const summary=await recomputeSession(ctx.user.id,run.id,n,activities);
  return {ok:true,correct,attempts,first_attempt_correct:firstAttempt,mastery,hint:correct?null:key.hint,...summary};
}
async function realtimeSignal(n:number,scope:"controls"|"wall"|"progress"|"teacher_wall"){
  try{
    const base=Deno.env.get("SUPABASE_URL"),key=Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if(!base||!key)return false;
    const response=await fetch(base+"/realtime/v1/api/broadcast",{
      method:"POST",
      headers:{
        "Content-Type":"application/json",
        "apikey":key,
        "Authorization":"Bearer "+key
      },
      body:JSON.stringify({messages:[{
        topic:"bigdata:session:"+n,
        event:"invalidate",
        payload:{course_code:COURSE,session_number:n,scope}
      }]})
    });
    return response.ok;
  }catch{return false}
}
async function sessionControls(runId:string,n:number){
  const now=Date.now();
  const {data,error}=await db.from("bd_session_controls")
    .select("id,control_key,control_type,payload,created_at,expires_at")
    .eq("course_run_id",runId).eq("session_number",n).eq("active",true)
    .order("created_at",{ascending:true});
  failIf(error,"No se pudieron cargar los controles de sesión");
  return (data||[]).filter((x:any)=>!x.expires_at||Date.parse(x.expires_at)>now);
}
async function isLabClosed(runId:string,n:number,activityCode:string){
  const controls=await sessionControls(runId,n);
  const c=controls.find((x:any)=>x.control_key==="lab:"+activityCode);
  return c?.control_type==="close_lab";
}
async function teacherReviewEvidence(ctx:any,run:any,n:number,body:any,activities:any[]){
  requireTeacher(ctx);
  const evidenceId=String(body.evidence_id||"").trim();
  if(!/^[0-9a-fA-F-]{36}$/.test(evidenceId))throw new Error("Evidencia inválida");
  const decision=String(body.decision||"");
  if(!["accepted","rejected"].includes(decision))throw new Error("Decisión de revisión inválida");
  const feedback=trimText(body.feedback,8,800,"El feedback");
  const criteria=["reproducible_result","supported_decision","rejected_alternative","ranking_interpretation","concrete_limit"];
  const scores:any={};let total=0;
  for(const id of criteria){
    const v=Math.trunc(Number(body.rubric?.[id]));
    if(!Number.isInteger(v)||v<0||v>2)throw new Error("Rúbrica incompleta: "+id);
    scores[id]=v;total+=v;
  }
  const {data:evidence,error}=await db.from("bd_evidence")
    .select("id,user_id,activity_code,step_id,source,verdict,payload")
    .eq("id",evidenceId).eq("course_run_id",run.id).eq("session_number",n).maybeSingle();
  failIf(error,"No se pudo cargar la evidencia");
  if(!evidence)throw new Error("Evidencia no encontrada");
  const activity=activities.find((a:any)=>a.code===evidence.activity_code&&a.kind==="lab");
  if(!activity)throw new Error("Actividad de evidencia inválida");
  const {data:catalog,error:catalogError}=await db.from("bd_activity_catalog").select("evaluator").eq("code",activity.code).maybeSingle();
  failIf(catalogError,"No se pudo validar el evaluador");
  const transferEvidence=evidence.step_id==="transfer"&&TRANSFER_REVIEW_CODES.has(evidence.activity_code);
  if(catalog?.evaluator!=="authentic-review"&&!transferEvidence)throw new Error("Esta evidencia no usa revisión auténtica");
  if(!["pending_review","rejected"].includes(String(evidence.verdict)))throw new Error("La evidencia ya fue cerrada");
  const now=new Date().toISOString(),rubric={scores,total,max:10};
  const {data:updated,error:updateError}=await db.from("bd_evidence").update({
    verdict:decision,feedback,rubric,reviewed_by:ctx.user.id,reviewed_at:now
  }).eq("id",evidenceId).select("id,user_id,activity_code,verdict,feedback,rubric,reviewed_at").single();
  failIf(updateError,"No se pudo revisar la evidencia");
  const {data:p,error:pError}=await db.from("bd_lms_activity_progress").select("*")
    .eq("user_id",evidence.user_id).eq("course_run_id",run.id).eq("activity_code",activity.code).maybeSingle();
  failIf(pError,"No se pudo leer el progreso");
  const accepted=decision==="accepted";
  const {error:progressError}=await db.from("bd_lms_activity_progress").upsert({
    user_id:evidence.user_id,course_run_id:run.id,activity_code:activity.code,
    status:accepted?"completed":"in_progress",started_at:p?.started_at||now,attempts:Number(p?.attempts||1),
    score:total,max_score:10,completed_at:accepted?(p?.completed_at||now):null,updated_at:now,
    metadata:{...(p?.metadata||{}),source:"evidence-review",evidence_id:evidenceId,evidence_verdict:decision,
      evidence_verified:accepted,transfer_verified:transferEvidence?accepted:(p?.metadata?.transfer_verified===true),
      transfer_pending:false,last_evidence_review_at:now,rubric_total:total}
  },{onConflict:"user_id,course_run_id,activity_code"});
  failIf(progressError,"No se pudo actualizar el progreso");
  if(accepted){
    const {error:eventError}=await db.from("bd_lms_events").insert({
      user_id:evidence.user_id,course_run_id:run.id,event_type:"evidence_verified",session_number:n,
      activity_code:activity.code,metadata:{source:"teacher-review",outcome:decision,rubric_total:total},created_at:now
    });
    failIf(eventError,"No se pudo registrar la verificación");
  }
  await audit(ctx.user.id,"bigdata.evidence.review","evidence",evidenceId,{session_number:n,activity_code:activity.code,decision,total});
  await realtimeSignal(n,"progress");
  return {ok:true,evidence:updated,completed:accepted,score:total,max_score:10};
}

async function teacherSetControl(ctx:any,run:any,n:number,body:any,activities:any[]){
  requireTeacher(ctx);
  const type=String(body.control_type||"");
  if(!["open_lab","close_lab","goto_slide","pin_hint"].includes(type))throw new Error("Control docente inválido");
  let key="",payload:any={};
  if(type==="open_lab"||type==="close_lab"){
    const code=String(body.activity_code||"");
    const activity=activities.find((a:any)=>a.code===code&&a.kind==="lab");
    if(!activity)throw new Error("Selecciona un LAB válido de esta sesión");
    key="lab:"+code;payload={activity_code:code,title:String(activity.title||code)};
  }else if(type==="goto_slide"){
    const slide=Math.trunc(Number(body.slide));
    if(!Number.isInteger(slide)||slide<1||slide>250)throw new Error("Diapositiva inválida");
    key="slide";payload={slide,label:String(body.label||"").slice(0,120)};
  }else{
    const text=trimText(body.text,3,500,"La pista");
    key="hint";payload={text};
  }
  const now=new Date().toISOString();
  const {error:oldError}=await db.from("bd_session_controls").update({active:false,superseded_at:now})
    .eq("course_run_id",run.id).eq("session_number",n).eq("control_key",key).eq("active",true);
  failIf(oldError,"No se pudo reemplazar el control anterior");
  const {data,error}=await db.from("bd_session_controls").insert({
    course_run_id:run.id,session_number:n,control_key:key,control_type:type,payload,
    active:true,created_by:ctx.user.id,created_at:now
  }).select("id,control_key,control_type,payload,created_at,expires_at").single();
  failIf(error,"No se pudo guardar el control docente");
  await realtimeSignal(n,"controls");
  await audit(ctx.user.id,"bigdata.session.control.set","course_run",run.id,{session_number:n,control_key:key,control_type:type});
  return {ok:true,control:data,controls:await sessionControls(run.id,n)};
}
async function teacherClearControl(ctx:any,run:any,n:number,body:any){
  requireTeacher(ctx);
  const key=String(body.control_key||"");
  if(!(key==="hint"||key==="slide"||/^lab:[A-Za-z0-9._:-]{3,120}$/.test(key)))throw new Error("Control a limpiar inválido");
  const now=new Date().toISOString();
  const {error}=await db.from("bd_session_controls").update({active:false,superseded_at:now})
    .eq("course_run_id",run.id).eq("session_number",n).eq("control_key",key).eq("active",true);
  failIf(error,"No se pudo limpiar el control");
  await realtimeSignal(n,"controls");
  await audit(ctx.user.id,"bigdata.session.control.clear","course_run",run.id,{session_number:n,control_key:key});
  return {ok:true,controls:await sessionControls(run.id,n)};
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
  const [{data:enrollments},{data:progress},{data:activityProgress},{data:events},{data:evidence},window]=await Promise.all([
    db.from("lms_run_enrollments").select("user_id,role,status").eq("course_run_id",run.id).eq("status","active"),
    db.from("bd_lms_session_progress").select("*").eq("course_run_id",run.id).eq("session_number",n),
    activityQuery,
    db.from("bd_lms_events").select("user_id,event_type,activity_code,metadata,created_at").eq("course_run_id",run.id)
      .eq("session_number",n).neq("event_type","heartbeat").order("created_at",{ascending:false}).limit(2500),
    db.from("bd_evidence").select("user_id,activity_code,verdict,created_at").eq("course_run_id",run.id)
      .eq("session_number",n).order("created_at",{ascending:false}).limit(5000),
    sessionWindow(run.id,n)
  ]);
  const ids=(enrollments||[]).filter((x:any)=>x.role==="student").map((x:any)=>x.user_id);
  const {data:users}=ids.length?await db.from("lms_users").select("id,display_name,username,active").in("id",ids):({data:[]} as any);
  const pm=new Map((progress||[]).map((x:any)=>[x.user_id,x])),byUser=new Map<string,any[]>(),lastEvent=new Map<string,any>(),lastSlide=new Map<string,any>(),evByUser=new Map<string,any[]>();
  for(const a of activityProgress||[]){if(!byUser.has(a.user_id))byUser.set(a.user_id,[]);byUser.get(a.user_id)!.push(a)}
  for(const e of events||[]){if(!lastEvent.has(e.user_id))lastEvent.set(e.user_id,e);if(e.event_type==="slide_viewed"&&!lastSlide.has(e.user_id))lastSlide.set(e.user_id,e)}
  for(const e of evidence||[]){if(!evByUser.has(e.user_id))evByUser.set(e.user_id,[]);evByUser.get(e.user_id)!.push(e)}
  const checkpoints=def.activities.filter((a:any)=>a.kind==="checkpoint"),labs=def.activities.filter((a:any)=>a.kind==="lab");
  const rows=(users||[]).map((u:any)=>{
    const p:any=pm.get(u.id)||{},aps=byUser.get(u.id)||[],am=new Map(aps.map((x:any)=>[x.activity_code,x]));
    const mastered=checkpoints.filter((a:any)=>Boolean(am.get(a.code)?.metadata?.mastery)||am.get(a.code)?.status==="completed").length;
    const attempted=aps.length;
    const ev:any=lastEvent.get(u.id),slideEv:any=lastSlide.get(u.id),slideMeta=slideEv?.metadata||{};
    const lastAt=p.last_activity_at||ev?.created_at||null,meaningfulAt=ev?.created_at||null;
    const activeAge=lastAt?(Date.now()-Date.parse(lastAt))/60000:null,meaningfulAge=meaningfulAt?(Date.now()-Date.parse(meaningfulAt))/60000:null,
      currentDef=def.activities.find((a:any)=>a.code===ev?.activity_code),present=ev?.event_type!=="page_closed"&&activeAge!==null&&activeAge<=5;
    const failedCheckpoint=aps.some((a:any)=>a.attempts>0&&a.metadata?.mastery===false);
    const stalledLab=currentDef?.kind==="lab"&&present&&meaningfulAge!==null&&meaningfulAge>5&&meaningfulAge<=30&&p.status!=="completed";
    const needsAttention=failedCheckpoint||stalledLab;
    return {
      user_id:u.id,display_name:u.display_name||u.username,
      status:p.status||"not_started",started_at:p.started_at||null,
      active_seconds:Number(p.active_seconds||0),last_activity_at:lastAt,present,
      current_activity:ev?.activity_code||null,current_event:ev?.event_type||null,
      needs_attention:needsAttention,attempted_activities:attempted,
      completed_activities:aps.filter((a:any)=>a.status==="completed").length,
      mastered_checkpoints:mastered,total_checkpoints:checkpoints.length,completed_checkpoints:mastered,
      presentation_opened:Boolean(am.get("bd-s09-presentation")),notebook_opened:Boolean(am.get("bd-s09-notebook")),
      lab_explored:labs.filter((a:any)=>am.has(a.code)).length,evidence_count:(evByUser.get(u.id)||[]).length,
      checkpoints:checkpoints.map((a:any)=>{const x:any=am.get(a.code)||{},m=x.metadata||{};return {code:a.code,attempts:Number(x.attempts||0),metadata:{first_attempt_correct:typeof m.first_attempt_correct==="boolean"?m.first_attempt_correct:null,mastery:Boolean(m.mastery)}}}),
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
  return {viewer:ctx.user,run,...def,session_window:window,controls:await sessionControls(run.id,n),students:rows,ranking:rows,activity_stats,challenge_stats:activity_stats.filter((x:any)=>x.kind==="checkpoint"),refreshed_at:new Date().toISOString()};
}
async function teacherStudentDetail(ctx:any,run:any,n:number,userId:string){
  requireTeacher(ctx);
  if(!/^[0-9a-f-]{36}$/i.test(userId))throw new Error("Estudiante inválido");
  const {data:enrollment}=await db.from("lms_run_enrollments").select("user_id,role,status")
    .eq("course_run_id",run.id).eq("user_id",userId).eq("role","student").eq("status","active").maybeSingle();
  if(!enrollment)throw new Error("Estudiante no pertenece a esta cohorte");
  const def=await definition(run.id,n,true),codes=def.activities.map((a:any)=>a.code);
  const [{data:user},{data:session_progress},{data:activity_progress},{data:events},{data:evidence}]=await Promise.all([
    db.from("lms_users").select("id,display_name,username,active").eq("id",userId).maybeSingle(),
    db.from("bd_lms_session_progress").select("*").eq("user_id",userId).eq("course_run_id",run.id).eq("session_number",n).maybeSingle(),
    codes.length?db.from("bd_lms_activity_progress").select("*").eq("user_id",userId).eq("course_run_id",run.id).in("activity_code",codes).order("updated_at",{ascending:false}):Promise.resolve({data:[]} as any),
    db.from("bd_lms_events").select("event_type,activity_code,metadata,client_at,created_at").eq("user_id",userId).eq("course_run_id",run.id).eq("session_number",n).neq("event_type","heartbeat").order("created_at",{ascending:false}).limit(250),
    db.from("bd_evidence").select("id,activity_code,payload,source,verdict,feedback,created_at,reviewed_by,reviewed_at,rubric").eq("user_id",userId).eq("course_run_id",run.id).eq("session_number",n).order("created_at",{ascending:false}).limit(100)
  ]);
  return {viewer:ctx.user,run,session:def.session,user,session_progress,activity_progress:activity_progress||[],events:events||[],evidence:evidence||[],activities:def.activities};
}

async function resetSession(ctx:any,run:any,n:number,body:any){
  requireTeacher(ctx);
  const phrase="REINICIAR_S"+String(n).padStart(2,"0");
  if(String(body.confirmation||"")!==phrase)throw new Error("Confirmación de reinicio inválida");
  const def=await definition(run.id,n,true),codes=def.activities.map((a:any)=>a.code);
  const [{data:progress},{data:activity},{data:events},{data:window},{data:evidence},{data:labCodes}]=await Promise.all([
    db.from("bd_lms_session_progress").select("user_id").eq("course_run_id",run.id).eq("session_number",n),
    codes.length?db.from("bd_lms_activity_progress").select("user_id,activity_code").eq("course_run_id",run.id).in("activity_code",codes):Promise.resolve({data:[]} as any),
    db.from("bd_lms_events").select("id").eq("course_run_id",run.id).eq("session_number",n),
    db.from("bd_lms_session_windows").select("course_run_id").eq("course_run_id",run.id).eq("session_number",n),
    db.from("bd_evidence").select("id").eq("course_run_id",run.id).eq("session_number",n),
    db.from("bd_lab_codes").select("code_hash").eq("course_run_id",run.id).eq("session_number",n)
  ]);
  const counts={session_progress:(progress||[]).length,activity_progress:(activity||[]).length,events:(events||[]).length,session_window:(window||[]).length,evidence:(evidence||[]).length,lab_codes:(labCodes||[]).length};
  const deletes:any[]=[
    await db.from("bd_evidence").delete().eq("course_run_id",run.id).eq("session_number",n),
    await db.from("bd_lab_codes").delete().eq("course_run_id",run.id).eq("session_number",n),
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

async function competitionAlias(runId:string,sessionNumber:number,userId:string){
  const h=await sha256(runId+"|competition|"+sessionNumber+"|"+userId);
  return "Jugador "+h.slice(0,4).toUpperCase();
}
async function competitionWall(ctx:any,run:any,n:number){
  const def=await definition(run.id,n,false);
  const required=(def.activities||[]).filter((a:any)=>a.required);
  const requiredCodes=required.map((a:any)=>a.code);
  const {data:enrollments,error:enrollmentError}=await db.from("lms_run_enrollments")
    .select("user_id,role,status").eq("course_run_id",run.id).eq("status","active").eq("role","student");
  failIf(enrollmentError,"No se pudo cargar la cohorte");
  const ids=(enrollments||[]).map((x:any)=>String(x.user_id));
  const [{data:sessionRows,error:sessionError},{data:activityRows,error:activityError}]=await Promise.all([
    ids.length?db.from("bd_lms_session_progress").select("user_id,status,score,max_score").eq("course_run_id",run.id).eq("session_number",n).in("user_id",ids):Promise.resolve({data:[],error:null} as any),
    ids.length&&requiredCodes.length?db.from("bd_lms_activity_progress").select("user_id,activity_code,status").eq("course_run_id",run.id).in("user_id",ids).in("activity_code",requiredCodes):Promise.resolve({data:[],error:null} as any)
  ]);
  failIf(sessionError,"No se pudo cargar el progreso del grupo");
  failIf(activityError,"No se pudo cargar el avance de actividades");
  const spm=new Map((sessionRows||[]).map((x:any)=>[String(x.user_id),x]));
  const byUser=new Map<string,any[]>();
  for(const row of activityRows||[]){
    const id=String(row.user_id);if(!byUser.has(id))byUser.set(id,[]);byUser.get(id)!.push(row);
  }
  const rows=await Promise.all(ids.map(async(userId)=>{
    const aps=byUser.get(userId)||[],p:any=spm.get(userId)||null;
    const completed=aps.filter((x:any)=>x.status==="completed").length;
    const attempted=aps.length;
    const total=required.length;
    const progressPct=total?Math.round((completed/total)*100):((p?.status==="completed")?100:0);
    return {
      alias:await competitionAlias(run.id,n,userId),
      is_me:userId===ctx.user.id,
      status:p?.status||"not_started",
      completed_required:completed,
      required_total:total,
      attempted_required:attempted,
      progress_pct:progressPct
    };
  }));
  rows.sort((a:any,b:any)=>b.progress_pct-a.progress_pct||b.completed_required-a.completed_required||a.alias.localeCompare(b.alias,"es"));
  let rank=0,lastKey="";
  rows.forEach((row:any,index:number)=>{
    const key=row.progress_pct+"|"+row.completed_required;
    if(key!==lastKey){rank=index+1;lastKey=key}
    row.position=rank;
  });
  const viewer=rows.find((x:any)=>x.is_me)||null;
  return {
    session:{session_number:n,title:def.session?.title||("Sesión "+n)},
    participants:rows.length,
    required_total:required.length,
    ranking:rows,
    viewer_rank:viewer?.position||null,
    generated_at:new Date().toISOString(),
    privacy:{identity:"alias",open_responses:false,speed_tiebreak:false}
  };
}

Deno.serve(async(req:Request)=>{
  if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
  if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
  if(!["GET","POST"].includes(req.method))return out(req,{error:"Método no permitido"},405);

  let action="me",body:any={},n=0;
  if(req.method==="GET"){
    const u=new URL(req.url);action=u.searchParams.get("action")||"me";
  }else{
    try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
    action=String(body.action||"me");
  }
  if(action==="evidence_by_code"){
    try{return out(req,await evidenceByCode(body))}
    catch(e){return out(req,{error:String((e as any)?.message||e).slice(0,500)},400)}
  }

  const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión LMS no válida o vencida"},401);
  const run=await activeRun(ctx);if(!run)return out(req,{error:"Tu cuenta no está matriculada en Big Data 2026-2S"},403);
  if(action!=="course_progress"){
    if(req.method==="GET"){const u=new URL(req.url);n=sessionNumber(u.searchParams.get("session_number")||u.searchParams.get("s"))}
    else n=sessionNumber(body.session_number);
  }
  try{
    if(action==="course_progress")return out(req,await courseProgress(ctx,run));
    if(action==="competition_wall"){const u=req.method==="GET"?new URL(req.url):null;const cn=req.method==="GET"?sessionNumber(u!.searchParams.get("session_number")||u!.searchParams.get("s")):sessionNumber(body.session_number);return out(req,await competitionWall(ctx,run,cn));}
    const teacher=["teacher_wall","teacher_open_session","teacher_reset_session","teacher_student_detail","wall_moderate","teacher_set_control","teacher_clear_control","teacher_review_evidence"].includes(action);
    const def=await definition(run.id,n,teacher),codes=def.activities.map((a:any)=>a.code);
    if(action==="me"){
      const [p,cat,evidence]=await Promise.all([
        ownProgress(ctx.user.id,run.id,n,codes),
        publicCatalog(codes,ctx.user.id,run.id),
        ownEvidence(ctx.user.id,run.id,n)
      ]);
      return out(req,{viewer:ctx.user,run,...def,...p,...cat,evidence,controls:await sessionControls(run.id,n),summary:activitySummary(def.activities,p.activity_progress)});
    }
    if(action==="track"){
      const event=String(body.event_type||"");if(!PUBLIC_TRACK_EVENTS.has(event))throw new Error("Evento no permitido para tracking cliente");
      const activityCode=body.activity_code?String(body.activity_code):null;
      const activity=activityCode?def.activities.find((a:any)=>a.code===activityCode):null;
      if(activityCode&&!activity)throw new Error("Actividad no válida para esta sesión");
      const delta=event==="heartbeat"?Math.max(0,Math.min(30,Math.round(Number(body.active_seconds_delta||0)))):0;
      const now=new Date().toISOString(),eventClientId=clientId(body.client_event_id,"client_event_id");
      const {error:eventError}=await db.from("bd_lms_events").insert({
        user_id:ctx.user.id,course_run_id:run.id,event_type:event,session_number:n,
        activity_code:activityCode,active_seconds_delta:delta,metadata:cleanMeta(body.metadata),
        client_at:body.client_at?String(body.client_at):null,client_event_id:eventClientId,created_at:now
      });
      if(isDuplicate(eventError))return out(req,{ok:true,duplicate:true});
      failIf(eventError,"No se pudo registrar el evento");
      if(event==="heartbeat")await heartbeat(ctx.user.id,run.id,n,delta);
      else{
        await ensureSessionStarted(ctx.user.id,run.id,n,def.activities.filter((a:any)=>a.kind==="checkpoint"&&a.required).length);
        if(activity){
          await touchActivity(ctx.user.id,run.id,activity,event,false,event!=="lab_interaction");
        }
      }
      if(["slide_viewed","presentation_opened","notebook_opened","page_closed","lab_interaction"].includes(event))await realtimeSignal(n,"teacher_wall");
      return out(req,{ok:true});
    }
    if(action==="answer_challenge"){const result=await answerChallenge(ctx,run,n,String(body.activity_code||""),body.answer,def.activities);await realtimeSignal(n,"progress");return out(req,result)}
    if(action==="evidence"){
      const activity=def.activities.find((a:any)=>a.code===String(body.activity_code||""));
      if(activity&&await isLabClosed(run.id,n,activity.code))throw new Error("Este LAB está cerrado temporalmente por el docente");
      const result=await submitEvidence(ctx.user.id,run.id,n,activity,body.payload||{},String(body.source||"presentation"),body.client_evidence_id);
      await realtimeSignal(n,"progress");return out(req,result);
    }
    if(action==="lab_code")return out(req,{ok:true,...await issueLabCode(ctx,run,n)});
    if(action==="session_controls")return out(req,{ok:true,controls:await sessionControls(run.id,n)});
    if(action==="teacher_review_evidence")return out(req,await teacherReviewEvidence(ctx,run,n,body,def.activities));
    if(action==="teacher_set_control")return out(req,await teacherSetControl(ctx,run,n,body,def.activities));
    if(action==="teacher_clear_control")return out(req,await teacherClearControl(ctx,run,n,body));
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