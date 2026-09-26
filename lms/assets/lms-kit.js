(()=>{'use strict';
const B=window.BIGDATA_LMS;
if(!B)throw new Error('LMS Kit requiere bigdata-lms.js');
const QUEUE_KEY='lms.bigdata.queue.v1';
const MAX_QUEUE=500;
const RETRY_MS=[1000,2000,4000,8000,30000];
const script=document.currentScript;
let configuredSession=Math.trunc(Number(script?.dataset?.session||new URLSearchParams(location.search).get('s')||0));
let flushing=false,retryTimer=null,heartbeat=null;
const listeners=new Map();

function emit(type,payload){
  for(const fn of listeners.get(type)||[]){try{fn(payload)}catch{}}
}
function on(type,fn){
  if(typeof fn!=='function')return()=>{};
  if(!listeners.has(type))listeners.set(type,new Set());
  listeners.get(type).add(fn);
  return()=>listeners.get(type)?.delete(fn);
}
function uid(prefix='q'){
  if(globalThis.crypto?.randomUUID)return prefix+'-'+crypto.randomUUID();
  return prefix+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,12);
}
function sessionNumber(n=configuredSession){
  const x=Math.trunc(Number(n||0));
  if(!Number.isInteger(x)||x<1)throw new Error('Número de sesión inválido');
  return x;
}
function loadQueue(){
  try{
    const q=JSON.parse(localStorage.getItem(QUEUE_KEY)||'[]');
    return Array.isArray(q)?q.filter(x=>x&&typeof x==='object'&&x.id&&x.kind&&x.payload):[];
  }catch{return[]}
}
function priority(entry){
  if(entry.kind==='evidence'||entry.kind==='wall_post')return 100;
  const t=entry.payload?.event_type;
  if(t==='heartbeat')return 0;
  if(t==='slide_viewed')return 10;
  if(t==='lab_interaction')return 20;
  return 50;
}
function compactQueue(q){
  if(q.length<=MAX_QUEUE)return q;
  const arr=[...q],removeCount=arr.length-MAX_QUEUE;
  const candidates=arr.map((x,i)=>({i,p:priority(x),at:Number(x.created_at_ms||0)}))
    .filter(x=>x.p<100)
    .sort((a,b)=>a.p-b.p||a.at-b.at)
    .slice(0,removeCount);
  const remove=new Set(candidates.map(x=>x.i));
  let out=arr.filter((_,i)=>!remove.has(i));
  // Evidencia y publicaciones nunca se eliminan para hacer espacio a telemetría.
  if(out.length>MAX_QUEUE&&out.every(x=>priority(x)>=100))return out;
  return out.slice(Math.max(0,out.length-MAX_QUEUE));
}
function saveQueue(q){
  const compacted=compactQueue(q);
  try{localStorage.setItem(QUEUE_KEY,JSON.stringify(compacted))}catch{}
  emit('queue',{size:compacted.length,items:compacted});
  return compacted;
}
function queueSize(){return loadQueue().length}
function clearRetry(){
  if(retryTimer){clearTimeout(retryTimer);retryTimer=null}
}
function retryable(error){
  const status=Number(error?.status||0);
  return navigator.onLine===false||!status||status===408||status===425||status===429||status>=500;
}
function enqueue(kind,payload,id=null){
  const q=loadQueue(),entry={
    id:id||uid(kind==='evidence'?'ev':kind==='wall_post'?'post':'evt'),
    kind,payload,attempts:0,created_at_ms:Date.now()
  };
  q.push(entry);saveQueue(q);scheduleFlush(RETRY_MS[0]);
  return entry;
}
async function deliver(entry){
  const p={...entry.payload};
  if(entry.kind==='track'){
    p.client_event_id=entry.id;
    return B.session('track',p);
  }
  if(entry.kind==='evidence'){
    p.client_evidence_id=entry.id;
    return B.session('evidence',p);
  }
  if(entry.kind==='wall_post'){
    p.client_post_id=entry.id;
    return B.session('wall_post',p);
  }
  throw new Error('Tipo de cola desconocido');
}
function scheduleFlush(ms=RETRY_MS[0]){
  if(retryTimer||navigator.onLine===false)return;
  retryTimer=setTimeout(()=>{retryTimer=null;flush().catch(()=>{})},ms);
}
async function flush(){
  if(flushing||navigator.onLine===false)return {ok:false,offline:navigator.onLine===false,size:queueSize()};
  flushing=true;clearRetry();
  try{
    let q=loadQueue(),sent=0;
    while(q.length){
      const entry=q[0];
      try{
        const result=await deliver(entry);
        q.shift();saveQueue(q);sent++;
        emit('sent',{entry,result});
      }catch(error){
        if(retryable(error)){
          entry.attempts=Number(entry.attempts||0)+1;
          q[0]=entry;saveQueue(q);
          const delay=RETRY_MS[Math.min(entry.attempts-1,RETRY_MS.length-1)];
          emit('retry',{entry,error,delay});scheduleFlush(delay);
          return {ok:false,retry:true,size:q.length,sent};
        }
        q.shift();saveQueue(q);
        emit('discard',{entry,error});
      }
    }
    return {ok:true,size:0,sent};
  }finally{flushing=false}
}
async function send(kind,payload){
  const id=uid(kind==='evidence'?'ev':kind==='wall_post'?'post':'evt');
  const entry={id,kind,payload,attempts:0,created_at_ms:Date.now()};
  if(navigator.onLine===false){
    enqueue(kind,payload,id);
    return {ok:true,queued:true,pending:true,client_id:id,feedback:'Tu trabajo quedó guardado temporalmente y se sincronizará cuando vuelva la conexión.'};
  }
  try{
    const result=await deliver(entry);
    flush().catch(()=>{});
    return {...result,client_id:id};
  }catch(error){
    if(!retryable(error))throw error;
    enqueue(kind,payload,id);
    return {ok:true,queued:true,pending:true,client_id:id,feedback:'Tu trabajo quedó guardado temporalmente y se sincronizará cuando vuelva la conexión.'};
  }
}
function track(event_type,{session_number=configuredSession,activity_code=null,metadata={},active_seconds_delta=0,client_at=new Date().toISOString()}={}){
  return send('track',{session_number:sessionNumber(session_number),event_type,activity_code,metadata,active_seconds_delta,client_at});
}
function evidence(activity_code,payload,{session_number=configuredSession,source='presentation'}={}){
  return send('evidence',{session_number:sessionNumber(session_number),activity_code,payload,source});
}
function wallPost(activity_code,body,{session_number=configuredSession,evidence_id=null}={}){
  return send('wall_post',{session_number:sessionNumber(session_number),activity_code,body,evidence_id});
}
function configure({session_number}={}){
  if(session_number!=null)configuredSession=sessionNumber(session_number);
  return api;
}
function keepaliveTrack(event_type,{session_number=configuredSession,activity_code=null,metadata={},active_seconds_delta=0,client_at=new Date().toISOString()}={}){
  const n=sessionNumber(session_number),id=uid('evt'),auth=B.auth?.();
  const payload={action:'track',session_number:n,event_type,activity_code,metadata,active_seconds_delta,client_at,client_event_id:id};
  if(!auth?.token){enqueue('track',{session_number:n,event_type,activity_code,metadata,active_seconds_delta,client_at},id);return false}
  try{
    fetch(B.API+'/bigdata-session',{
      method:'POST',keepalive:true,
      headers:{'Content-Type':'application/json','Authorization':'Bearer '+auth.token},
      body:JSON.stringify(payload)
    }).catch(()=>enqueue('track',{session_number:n,event_type,activity_code,metadata,active_seconds_delta,client_at},id));
    return true;
  }catch{
    enqueue('track',{session_number:n,event_type,activity_code,metadata,active_seconds_delta,client_at},id);return false;
  }
}
function startHeartbeat(activity_code=null,{session_number=configuredSession}={}){
  stopHeartbeat();
  const n=sessionNumber(session_number);let last=Date.now(),beat=Date.now();
  const touch=()=>{last=Date.now()};
  const events=['pointerdown','keydown','scroll','touchstart'];
  events.forEach(ev=>addEventListener(ev,touch,{passive:true}));
  const tick=async()=>{
    const now=Date.now(),visible=document.visibilityState==='visible',active=now-last<90000,
      elapsed=Math.min(30,Math.max(0,Math.round((now-beat)/1000)));
    beat=now;
    if(visible&&active&&elapsed>0)await track('heartbeat',{session_number:n,activity_code,active_seconds_delta:elapsed}).catch(()=>{});
  };
  const timer=setInterval(tick,30000);
  const close=()=>keepaliveTrack('page_closed',{session_number:n,activity_code,metadata:{source:'lms-kit-pagehide'}});
  addEventListener('pagehide',close,{once:true});
  heartbeat={timer,events,touch,close};
  return heartbeat;
}
function stopHeartbeat(){
  if(!heartbeat)return;
  clearInterval(heartbeat.timer);
  heartbeat.events.forEach(ev=>removeEventListener(ev,heartbeat.touch));
  heartbeat=null;
}
function identityPill(el,viewer){
  if(!el)return;
  const v=viewer||B.auth?.()?.user||{},name=v.display_name||v.username||'Usuario';
  el.textContent=name+' · conectado';
  el.setAttribute('data-lms-identity','true');
}
function moduleMenu(el,{session_number=configuredSession}={}){
  if(!el)return;
  const n=sessionNumber(session_number);
  el.innerHTML='<a href="../lms/session.html?s='+n+'">Módulo</a> · <a href="../lms/progress.html?s='+n+'">Mi progreso</a>';
}
const api={
  version:'5.0.0',QUEUE_KEY,MAX_QUEUE,configure,on,flush,queueSize,track,evidence,wallPost,
  startHeartbeat,stopHeartbeat,keepaliveTrack,identityPill,moduleMenu,
  session:(action,payload={})=>B.session(action,{...payload,session_number:payload.session_number||configuredSession}),
  get ready(){return B.requireSession(sessionNumber())}
};
window.LMS=api;
addEventListener('online',()=>flush().catch(()=>{}));
if(navigator.onLine!==false)setTimeout(()=>flush().catch(()=>{}),250);
})();