(()=>{'use strict';
const PROJECT_URL='https://gnpouhsvsisqoxketlfr.supabase.co';
const PUBLISHABLE_KEY='sb_publishable_9l_od2Dg78hu1mPrmxAabA_erL2Tlge';
const CLIENT_MODULE='https://esm.sh/@supabase/supabase-js@2.117.1';
let clientPromise=null;

function validSession(v){
  const n=Math.trunc(Number(v));
  if(!Number.isInteger(n)||n<1||n>99)throw new Error('Número de sesión inválido para Realtime');
  return n;
}
async function client(){
  if(!clientPromise){
    clientPromise=import(CLIENT_MODULE).then(({createClient})=>createClient(PROJECT_URL,PUBLISHABLE_KEY,{
      auth:{persistSession:false,autoRefreshToken:false,detectSessionInUrl:false},
      realtime:{params:{eventsPerSecond:4}}
    }));
  }
  return clientPromise;
}
async function subscribe({session_number,scopes=[],onSignal=()=>{},onStatus=()=>{}}={}){
  const n=validSession(session_number),wanted=new Set((scopes||[]).map(String));
  let closed=false,sb=null,channel=null;
  try{
    sb=await client();
    if(closed)return()=>{};
    const name='bigdata-'+n+'-'+Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,8);
    channel=sb.channel(name)
      .on('postgres_changes',{
        event:'INSERT',schema:'public',table:'bd_realtime_signals',
        filter:'session_number=eq.'+n
      },payload=>{
        const scope=String(payload?.new?.scope||'');
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
window.LMSRealtime={version:'1.0.0',subscribe};
})();