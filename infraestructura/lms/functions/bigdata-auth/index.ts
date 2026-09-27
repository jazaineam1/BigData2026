import { createClient } from "npm:@supabase/supabase-js@2";
const supabase=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,{auth:{persistSession:false}});
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const COURSE_CODE="bigdata";
function origin(req:Request){const o=req.headers.get("origin");if(!o)return "";if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;return null}
function headers(req:Request){const o=origin(req);return {"Access-Control-Allow-Origin":o||"https://jazaineam1.github.io","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS","Vary":"Origin","Cache-Control":"no-store","X-Content-Type-Options":"nosniff","Referrer-Policy":"strict-origin-when-cross-origin"}}
function out(req:Request,body:unknown,status=200){return new Response(JSON.stringify(body),{status,headers:{...headers(req),"Content-Type":"application/json"}})}
function bearer(req:Request){const h=req.headers.get("authorization")||"";return h.toLowerCase().startsWith("bearer ")?h.slice(7).trim():""}
async function sha256(s:string){const d=await crypto.subtle.digest("SHA-256",new TextEncoder().encode(s));return [...new Uint8Array(d)].map(b=>b.toString(16).padStart(2,"0")).join("")}
const SESSION_POLICY:Record<string,{ttl_hours:number,persistent:boolean,label:string}>={
  student:{ttl_hours:30*24,persistent:true,label:"30 días"},
  teacher:{ttl_hours:12,persistent:false,label:"12 horas"},
  admin:{ttl_hours:4,persistent:false,label:"4 horas"}
};
function sessionPolicy(role:any){return SESSION_POLICY[String(role||"").toLowerCase()]||{ttl_hours:8,persistent:false,label:"8 horas"}}
function randomToken(){const bytes=crypto.getRandomValues(new Uint8Array(32));return btoa(String.fromCharCode(...bytes)).replaceAll("+","-").replaceAll("/","_").replaceAll("=","")}
function deviceLabel(ua:string){const s=ua||"";const os=/Android/i.test(s)?"Android":/iPhone|iPad|iPod/i.test(s)?"iOS/iPadOS":/Windows/i.test(s)?"Windows":/Mac OS X|Macintosh/i.test(s)?"macOS":/Linux/i.test(s)?"Linux":"Dispositivo";const browser=/Edg\//i.test(s)?"Edge":/OPR\//i.test(s)?"Opera":/Chrome\//i.test(s)?"Chrome":/Safari\//i.test(s)?"Safari":/Firefox\//i.test(s)?"Firefox":"navegador";return `${os} · ${browser}`}
async function current(req:Request){const token=bearer(req);if(!token)return null;const token_hash=await sha256(token);const {data:s}=await supabase.from("lms_auth_sessions").select("id,user_id,expires_at,revoked_at,persistent,user_agent,created_at,last_seen_at").eq("token_hash",token_hash).is("revoked_at",null).maybeSingle();if(!s)return null;const deadline=s.expires_at?new Date(s.expires_at).getTime():(new Date(s.created_at).getTime()+(s.persistent?30:1)*24*3600_000);if(!Number.isFinite(deadline)||deadline<=Date.now())return null;const {data:u}=await supabase.from("lms_users").select("id,username,display_name,role,active,email,auth_user_id").eq("id",s.user_id).eq("active",true).maybeSingle();return u?{token,session:s,user:u}:null}
async function currentRun(userId:string){
 const {data:r}=await supabase.from("lms_course_runs").select("id,course_code,code,title,timezone,starts_on,ends_on,active").eq("course_code",COURSE_CODE).eq("active",true).order("created_at",{ascending:false}).limit(1).maybeSingle();
 if(!r)return null;
 const {data:re}=await supabase.from("lms_run_enrollments").select("role,status,enrolled_at").eq("user_id",userId).eq("course_run_id",r.id).eq("status","active").maybeSingle();
 return re?{...r,enrollment_role:re.role}:null
}
async function issueSession(req:Request,user:any,includeRun=true){const token=randomToken(),token_hash=await sha256(token),policy=sessionPolicy(user.role),persistent=policy.persistent,ttlHours=policy.ttl_hours,expires_at=new Date(Date.now()+ttlHours*3600_000).toISOString();const {data:created,error}=await supabase.from("lms_auth_sessions").insert({user_id:user.id,token_hash,user_agent:(req.headers.get("user-agent")||"").slice(0,500),expires_at,persistent}).select("id").single();if(error)throw error;return {token,expires_at,auth_session_id:created.id,persistent,session_policy:{role:user.role,ttl_hours:ttlHours,label:policy.label,persistent},user:{id:user.id,username:user.username,display_name:user.display_name,role:user.role,email:user.email||null},course_run:includeRun?await currentRun(user.id):null}}
async function accessContext(raw:string){
 if(raw.length<30)return {error:"Enlace de acceso incompleto",status:400} as any;
 const token_hash=await sha256(raw);
 const {data:t,error}=await supabase.from("lms_access_tokens").select("id,user_id,request_id,used_at,expires_at").eq("token_hash",token_hash).maybeSingle();
 if(error||!t)return {error:"Este enlace no es válido",status:401} as any;
 if(!t.expires_at||new Date(t.expires_at).getTime()<=Date.now())return {error:"Este enlace venció",status:401,expired:true} as any;
 const {data:reqRow}=await supabase.from("lms_access_requests").select("id,course_code,status").eq("id",t.request_id).eq("course_code",COURSE_CODE).maybeSingle();
 if(!reqRow)return {error:"Este enlace no pertenece a Big Data",status:403} as any;
 const {data:user}=await supabase.from("lms_users").select("id,username,display_name,role,active,email,auth_user_id").eq("id",t.user_id).eq("active",true).maybeSingle();
 if(!user)return {error:"La cuenta ya no está activa",status:403} as any;
 const {data:enrollment}=await supabase.from("lms_enrollments").select("course_code,status").eq("user_id",user.id).eq("course_code",COURSE_CODE).eq("status","active").maybeSingle();
 if(!enrollment)return {error:"La cuenta no tiene matrícula activa en Big Data",status:403} as any;
 return {token_hash,tokenRow:t,user,enrollments:[enrollment],alreadyUsed:!!t.used_at}
}
Deno.serve(async req=>{
 if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
 if(req.method==="OPTIONS")return new Response("ok",{headers:headers(req)});
 if(req.method!=="POST")return out(req,{error:"Método no permitido"},405);
 let body:any={};try{body=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
 const action=String(body.action||"me");
 if(action==="login"){
   const username=String(body.username||"").trim(),password=String(body.password||"");
   if(!username||!password)return out(req,{error:"Usuario y contraseña son obligatorios"},400);
   if(username.length>180||password.length>200)return out(req,{error:"Credenciales inválidas"},400);
   const normalizedUser=username.toLowerCase(),ip=(req.headers.get("cf-connecting-ip")||req.headers.get("x-real-ip")||req.headers.get("x-forwarded-for")||"unknown").split(",")[0].trim();
   const key_hash=await sha256(normalizedUser+"|"+ip+"|bigdata-login-v51"),account_hash=await sha256(normalizedUser+"|account|lms-login-v51"),since=new Date(Date.now()-15*60_000).toISOString();
   const [{count},{count:accountCount}]=await Promise.all([
     supabase.from("lms_login_attempts").select("id",{count:"exact",head:true}).eq("key_hash",key_hash).eq("ok",false).gte("created_at",since),
     supabase.from("lms_login_attempts").select("id",{count:"exact",head:true}).eq("key_hash",account_hash).eq("ok",false).gte("created_at",since)
   ]);
   if((count||0)>=8)return out(req,{error:"Demasiados intentos desde este origen. Espera unos minutos antes de volver a intentar."},429);
   const globalFailures=Number(accountCount||0);
   if(globalFailures>=6){
     const delayMs=Math.min(2000,250*(globalFailures-5));
     await new Promise(resolve=>setTimeout(resolve,delayMs));
   }
   const {data,error}=await supabase.rpc("lms_verify_password",{p_username:username,p_password:password});
   if(error)return out(req,{error:"No se pudo validar el acceso"},500);const row=Array.isArray(data)?data[0]:null;
   if(!row){await supabase.from("lms_login_attempts").insert([{key_hash,ok:false},{key_hash:account_hash,ok:false}]);return out(req,{error:"Usuario o contraseña incorrectos"},401)}
   await supabase.from("lms_login_attempts").insert([{key_hash,ok:true},{key_hash:account_hash,ok:true}]);
   const user={id:row.user_id,username:row.username,display_name:row.display_name,role:row.role,email:null};
   try{return out(req,await issueSession(req,user,false))}catch{return out(req,{error:"No se pudo crear la sesión"},500)}
 }
 if(action==="inspect_access"){
   const raw=String(body.token||"").trim(),ctx:any=await accessContext(raw);if(ctx.error)return out(req,{error:ctx.error,expired:!!ctx.expired},ctx.status||401);
   if(ctx.alreadyUsed)return out(req,{ok:true,already_used:true});
   return out(req,{ok:true,display_name:ctx.user.display_name||ctx.user.username,email:ctx.user.email||null,courses:(ctx.enrollments||[]).map((x:any)=>x.course_code),already_used:false});
 }
 if(action==="claim_access"){
   const raw=String(body.token||"").trim(),ctx:any=await accessContext(raw);if(ctx.error)return out(req,{error:ctx.error,expired:!!ctx.expired},ctx.status||401);
   if(ctx.tokenRow.used_at)return out(req,{error:"Este enlace ya fue utilizado. Ingresa con tu cuenta o solicita ayuda al docente."},410);
   const now=new Date().toISOString();
   const {data:claimed,error:claimError}=await supabase.from("lms_access_tokens").update({used_at:now}).eq("id",ctx.tokenRow.id).is("used_at",null).select("id").maybeSingle();
   if(claimError)return out(req,{error:"No se pudo validar el enlace de acceso"},500);
   if(!claimed)return out(req,{error:"Este enlace ya fue utilizado. Ingresa con tu cuenta o solicita ayuda al docente."},410);
   try{return out(req,{...(await issueSession(req,ctx.user,false)),recovered:false})}
   catch{
     await supabase.from("lms_access_tokens").update({used_at:null}).eq("id",ctx.tokenRow.id).eq("used_at",now);
     return out(req,{error:"No se pudo crear la sesión. Intenta nuevamente."},500)
   }
 }
 if(action==="exchange_supabase"){
   const access=String(body.access_token||"").trim();if(!access)return out(req,{error:"Enlace de acceso incompleto"},400);
   const {data:authData,error:authError}=await supabase.auth.getUser(access);const au=authData?.user;if(authError||!au?.id||!au.email)return out(req,{error:"El enlace de acceso es inválido o venció"},401);
   if(!au.email_confirmed_at)return out(req,{error:"Confirma tu correo antes de continuar"},403);
   const normalizedEmail=au.email.trim().toLowerCase();
   let {data:user}=await supabase.from("lms_users").select("id,username,display_name,role,active,email,auth_user_id").eq("auth_user_id",au.id).maybeSingle();
   if(!user){const byEmail=await supabase.from("lms_users").select("id,username,display_name,role,active,email,auth_user_id").eq("email",normalizedEmail).maybeSingle();user=byEmail.data;if(user&&!user.auth_user_id)await supabase.from("lms_users").update({auth_user_id:au.id,updated_at:new Date().toISOString()}).eq("id",user.id)}
   if(!user||!user.active)return out(req,{error:"Tu cuenta no tiene acceso activo a la plataforma"},403);const {count}=await supabase.from("lms_enrollments").select("course_code",{count:"exact",head:true}).eq("user_id",user.id).eq("course_code",COURSE_CODE).eq("status","active");if(!(count||0))return out(req,{error:"Tu cuenta aún no está matriculada en Big Data"},403);
   try{return out(req,await issueSession(req,user,false))}catch{return out(req,{error:"No se pudo crear la sesión"},500)}
 }
 const ctx=await current(req);if(!ctx)return out(req,{error:"Sesión no válida o vencida"},401);
 if(action==="logout"){await supabase.from("lms_auth_sessions").update({revoked_at:new Date().toISOString()}).eq("id",ctx.session.id);return out(req,{ok:true})}
 if(action==="logout_all"){await supabase.from("lms_auth_sessions").update({revoked_at:new Date().toISOString()}).eq("user_id",ctx.user.id).is("revoked_at",null);return out(req,{ok:true})}
 if(action==="logout_others"){await supabase.from("lms_auth_sessions").update({revoked_at:new Date().toISOString()}).eq("user_id",ctx.user.id).is("revoked_at",null).neq("id",ctx.session.id);return out(req,{ok:true})}
 if(action==="list_sessions"){
   const {data}=await supabase.from("lms_auth_sessions").select("id,user_agent,created_at,last_seen_at,expires_at,persistent").eq("user_id",ctx.user.id).is("revoked_at",null).order("last_seen_at",{ascending:false});
   const now=Date.now(),sessions=(data||[]).filter((s:any)=>{const deadline=s.expires_at?Date.parse(s.expires_at):(Date.parse(s.created_at)+(s.persistent?30:1)*24*3600_000);return Number.isFinite(deadline)&&deadline>now}).map((s:any)=>({...s,current:s.id===ctx.session.id,device_label:deviceLabel(s.user_agent||"")}));
   return out(req,{sessions});
 }
 if(action==="revoke_session"){
   const id=String(body.session_id||"");if(!id)return out(req,{error:"Sesión requerida"},400);if(id===ctx.session.id)return out(req,{error:"Usa Cerrar sesión para terminar el dispositivo actual"},409);
   await supabase.from("lms_auth_sessions").update({revoked_at:new Date().toISOString()}).eq("id",id).eq("user_id",ctx.user.id).is("revoked_at",null);return out(req,{ok:true});
 }
 if(action==="change_password"){
   const password=String(body.password||"");if(password.length<8||password.length>72)return out(req,{error:"La contraseña debe tener entre 8 y 72 caracteres"},400);
   const {error}=await supabase.rpc("lms_set_password",{p_user_id:ctx.user.id,p_password:password});if(error)return out(req,{error:"No se pudo actualizar la contraseña"},500);
   await supabase.from("lms_auth_sessions").update({revoked_at:new Date().toISOString()}).eq("user_id",ctx.user.id).is("revoked_at",null).neq("id",ctx.session.id);
   return out(req,{ok:true,message:"Contraseña actualizada; las demás sesiones quedaron cerradas"});
 }
 if(action==="me"){
   await supabase.from("lms_auth_sessions").update({last_seen_at:new Date().toISOString()}).eq("id",ctx.session.id);
   const policy=sessionPolicy(ctx.user.role);return out(req,{user:ctx.user,expires_at:ctx.session.expires_at,auth_session_id:ctx.session.id,persistent:!!ctx.session.persistent,session_policy:{role:ctx.user.role,ttl_hours:policy.ttl_hours,label:policy.label,persistent:policy.persistent},course_run:await currentRun(ctx.user.id)});
 }
 return out(req,{error:"Acción desconocida"},400);
});