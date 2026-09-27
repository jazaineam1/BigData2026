(()=>{'use strict';
const PROJECT_URL='https://gnpouhsvsisqoxketlfr.supabase.co';
const PUBLISHABLE_KEY='sb_publishable_9l_od2Dg78hu1mPrmxAabA_erL2Tlge';
const CLIENT_VERSION='2.117.1';
let clientPromise=null;

function validSession(v){
  const n=Math.trunc(Number(v));
  if(!Number.isInteger(n)||n<1||n>99)throw new Error('Número de sesión inválido para Realtime');
  return n;
}
async function client(){
  if(!clientPromise){
    clientPromise=Promise.resolve().then(()=>{
      const createClient=window.supabase?.createClient;
      if(typeof createClient!=='function')throw new Error('SDK Realtime local no disponible');
      return createClient(PROJECT_URL,PUBLISHABLE_KEY,{
        auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false},
        realtime:{params:{eventsPerSecond:4}}
      });
    });
  }
  return clientPromise;
}
async function subscribe({session_number,scopes=[],onSignal=()=>{},onStatus=()=>{}}={}){
  const n=validSession(session_number),wanted=new Set((scopes||[]).map(String));
  let closed=false,sb=null,channel=null;
  try{
    sb=await client();
    if(closed)return()=>{};
    const topic='bigdata:session:'+n;
    channel=sb.channel(topic,{config:{private:false}})
      .on('broadcast',{event:'invalidate'},message=>{
        const payload=message?.payload||{};
        if(String(payload.course_code||'')!=='bigdata')return;
        if(Math.trunc(Number(payload.session_number))!==n)return;
        const scope=String(payload.scope||'');
        if(!wanted.size||wanted.has(scope))onSignal({scope,payload});
      })
      .subscribe(status=>onStatus(status));
  }catch(error){
    onStatus('ERROR',error);
  }
  return async()=>{
    closed=true;
    try{if(sb&&channel)await sb.removeChannel(channel)}catch{}
  };
}
window.LMSRealtime={version:'2.0.0',transport:'broadcast',sdk_version:CLIENT_VERSION,subscribe};
})();