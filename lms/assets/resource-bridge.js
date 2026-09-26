(()=>{'use strict';
const tag=document.currentScript,n=Math.trunc(Number(tag?.dataset?.session||0)),activity=String(tag?.dataset?.activity||''),label=String(tag?.dataset?.label||document.title||'Recurso');
if(!n)return;
const clientUrl=new URL('bigdata-lms.js',tag.src).href;
function loadClient(){return new Promise((resolve,reject)=>{if(window.BIGDATA_LMS)return resolve(window.BIGDATA_LMS);const s=document.createElement('script');s.src=clientUrl;s.onload=()=>resolve(window.BIGDATA_LMS);s.onerror=reject;document.head.appendChild(s)})}
function identity(model,L){
 const el=document.createElement('aside');el.className='lms-resource-identity';
 const who=model.viewer?.display_name||model.viewer?.username||'Estudiante';
 el.innerHTML='<span>Sesión LMS activa</span><b>'+L.esc(who)+'</b><a href="'+L.ROOT+'session.html?s='+n+'">Volver al módulo S'+String(n).padStart(2,'0')+'</a>';
 const st=document.createElement('style');st.textContent='.lms-resource-identity{position:fixed;z-index:9999;right:12px;top:12px;max-width:min(310px,calc(100vw - 24px));display:grid;gap:2px;background:#fff;color:#172033;border:1px solid #dfe3e8;border-left:4px solid #0B8689;border-radius:12px;padding:9px 11px;box-shadow:0 8px 28px #14215322;font:12px/1.35 Roboto,Segoe UI,Arial,sans-serif}.lms-resource-identity span{color:#62676F}.lms-resource-identity b{color:#142153;font-size:13px}.lms-resource-identity a{color:#0B6770;font-weight:800;text-decoration:none;margin-top:2px}@media(max-width:560px){.lms-resource-identity{position:sticky;top:6px;right:auto;margin:6px;max-width:none}}';document.head.appendChild(st);document.body.appendChild(el)
}
(async()=>{try{
 const L=await loadClient();
 if(!L?.auth?.()?.token){location.replace(L.ROOT+'session.html?s='+n);return}
 const model=await L.requireSession(n);if(!model)return;
 identity(model,L);
 await L.session('track',{session_number:n,event_type:'guide_opened',activity_code:activity||null,metadata:{source:'resource-bridge',resource_type:'guide',label,path:location.pathname},client_at:new Date().toISOString()}).catch(()=>{});
 L.startHeartbeat(activity||null,(action,payload)=>L.session(action,{...payload,session_number:n}));
}catch(e){console.error('LMS resource bridge',e)}})();
})();