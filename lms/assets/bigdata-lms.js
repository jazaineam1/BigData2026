(()=>{'use strict';
const API='https://gnpouhsvsisqoxketlfr.supabase.co/functions/v1';
const STORE='andesdb.lms.auth.v1';
const ROOT='/BigData2026/lms/';
const $=id=>document.getElementById(id);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const auth=()=>{try{return JSON.parse(localStorage.getItem(STORE)||'null')}catch{return null}};
const save=x=>{try{x?localStorage.setItem(STORE,JSON.stringify(x)):localStorage.removeItem(STORE)}catch{}};
async function request(path,opt={}){const a=auth(),h={'Content-Type':'application/json',...(opt.headers||{})};if(a?.token)h.Authorization='Bearer '+a.token;const r=await fetch(API+'/'+path,{...opt,headers:h});const x=await r.json().catch(()=>({}));if(!r.ok){const e=new Error(x.error||('HTTP '+r.status));e.status=r.status;e.data=x;throw e}return x}
async function login(username,password){const x=await request('learning-auth',{method:'POST',body:JSON.stringify({action:'login',username,password})});save({token:x.token,expires_at:x.expires_at,auth_session_id:x.auth_session_id,user:x.user});return x}
async function authAction(action,payload={}){return request('learning-auth',{method:'POST',body:JSON.stringify({action,...payload})})}
async function bigdata(action='me',payload={}){if(action==='me'||action==='teacher_wall')return request('bigdata-learning?action='+encodeURIComponent(action),{method:'GET'});return request('bigdata-learning',{method:'POST',body:JSON.stringify({action,...payload})})}
async function requestAccess(payload){return request('learning-access-request',{method:'POST',body:JSON.stringify({...payload,course_code:'bigdata',website:''})})}
async function reviewAccess(payload){return request('learning-access-review',{method:'POST',body:JSON.stringify(payload)})}
async function logout(){try{await authAction('logout')}catch{}save(null);location.href=ROOT+'portal.html'}
function fmtTime(s){s=Math.max(0,Number(s||0));const h=Math.floor(s/3600),m=Math.floor((s%3600)/60);return h?h+' h '+m+' min':m+' min'}
function fmtWhen(v){if(!v)return'—';try{return new Intl.DateTimeFormat('es-CO',{dateStyle:'short',timeStyle:'short',timeZone:'America/Bogota'}).format(new Date(v))}catch{return'—'}}
function fmtDelay(s){if(s==null||!Number.isFinite(Number(s)))return'—';s=Math.max(0,Math.round(Number(s)));const m=Math.floor(s/60),r=s%60;return'+'+String(m).padStart(2,'0')+':'+String(r).padStart(2,'0')}
function safeNext(){const p=new URLSearchParams(location.search),n=p.get('next');if(!n)return ROOT+'portal.html';try{const u=new URL(n,location.origin);return u.origin===location.origin&&u.pathname.startsWith(ROOT)?u.pathname+u.search+u.hash:ROOT+'session-08.html'}catch{return ROOT+'session-08.html'}}
function msg(el,text,type='ok'){if(!el)return;el.className='status '+type;el.textContent=text;el.hidden=false}
async function requireBigData({teacher=false}={}){if(!auth()?.token){location.replace(ROOT+'portal.html?next='+encodeURIComponent(location.pathname+location.search));return null}try{const x=await bigdata(teacher?'teacher_wall':'me');if(teacher&&!['teacher','admin'].includes(x.viewer?.role)){location.replace(ROOT+'portal.html');return null}return x}catch(e){if(e.status===401){save(null);location.replace(ROOT+'portal.html?next='+encodeURIComponent(location.pathname+location.search));return null}throw e}}
function wireLogout(){document.querySelectorAll('[data-logout]').forEach(b=>b.addEventListener('click',logout))}
function startHeartbeat(activity=null){let last=Date.now(),beat=Date.now();const touch=()=>last=Date.now();['pointerdown','keydown','scroll','touchstart'].forEach(ev=>addEventListener(ev,touch,{passive:true}));const send=async()=>{const now=Date.now(),visible=document.visibilityState==='visible',active=now-last<90000,elapsed=Math.min(30,Math.max(0,Math.round((now-beat)/1000)));beat=now;if(visible&&active&&elapsed>0){try{await bigdata('track',{event_type:'heartbeat',activity_code:activity,active_seconds_delta:elapsed,client_at:new Date().toISOString()})}catch{}}};const id=setInterval(send,30000);addEventListener('pagehide',()=>{clearInterval(id);bigdata('track',{event_type:'page_closed',activity_code:activity,client_at:new Date().toISOString()}).catch(()=>{})})}
window.BIGDATA_LMS={API,STORE,ROOT,$,esc,auth,save,login,authAction,bigdata,requestAccess,reviewAccess,logout,fmtTime,fmtWhen,fmtDelay,safeNext,msg,requireBigData,wireLogout,startHeartbeat};
})();