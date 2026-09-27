import { createClient } from "npm:@supabase/supabase-js@2";
const supabase=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,{auth:{persistSession:false}});
const ALLOWED=new Set(["https://jazaineam1.github.io"]);
const COURSE_CODE="bigdata";
function origin(req:Request){const o=req.headers.get("origin");if(!o)return "";if(ALLOWED.has(o)||/^http:\/\/(localhost|127\.0\.0\.1)(:\d+)?$/.test(o))return o;return null}
function h(req:Request){const o=origin(req);return {"Access-Control-Allow-Origin":o||"https://jazaineam1.github.io","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type","Access-Control-Allow-Methods":"POST, OPTIONS","Vary":"Origin","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}}
function out(req:Request,b:unknown,s=200){return new Response(JSON.stringify(b),{status:s,headers:{...h(req),"Content-Type":"application/json"}})}
Deno.serve(async req=>{
 if(origin(req)===null)return out(req,{error:"Origen no permitido"},403);
 if(req.method==="OPTIONS")return new Response("ok",{headers:h(req)});
 if(req.method!=="POST")return out(req,{error:"Método no permitido"},405);
 let b:any={};try{b=await req.json()}catch{return out(req,{error:"JSON inválido"},400)}
 const full_name=String(b.full_name||"").trim().replace(/\s+/g," ").slice(0,120),email=String(b.email||"").trim().toLowerCase().slice(0,180),course_code=COURSE_CODE,trap=String(b.website||"").trim();
 if(trap)return out(req,{error:"No se pudo registrar la solicitud. Recarga la página e inténtalo de nuevo."},400);if(full_name.length<3)return out(req,{error:"Escribe tu nombre completo."},400);if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return out(req,{error:"Correo no válido."},400);
 const {data:course}=await supabase.from("lms_courses").select("code,status").eq("code",course_code).eq("status","active").maybeSingle();if(!course)return out(req,{error:"Curso no disponible."},400);
 const generic={ok:true,status:"received",message:"Si corresponde, tu solicitud será revisada por el docente. Si ya existe una solicitud o matrícula, no necesitas hacer nada más."};
 const {data:existing}=await supabase.from("lms_access_requests").select("id,status,created_at").eq("email",email).eq("course_code",course_code).order("created_at",{ascending:false}).limit(1).maybeSingle();
 if(existing?.status==="pending"||existing?.status==="approved")return out(req,generic);
 const since=new Date(Date.now()-24*3600_000).toISOString();const {count}=await supabase.from("lms_access_requests").select("id",{count:"exact",head:true}).eq("email",email).eq("course_code",course_code).gte("created_at",since);if((count||0)>=2)return out(req,generic);
 const {error}=await supabase.from("lms_access_requests").insert({full_name,email,course_code,status:"pending"});if(error)return out(req,{error:"No se pudo guardar la solicitud."},500);return out(req,generic);
});