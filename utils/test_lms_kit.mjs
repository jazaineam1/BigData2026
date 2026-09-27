import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../lms/assets/lms-kit.js',import.meta.url),'utf8');

function harness({online=false,handler,user={id:'user-a',username:'user-a',display_name:'QA'}}={}){
  const store=new Map(),sent=[];let activeUser={...user};
  const localStorage={
    getItem:k=>store.has(k)?store.get(k):null,
    setItem:(k,v)=>store.set(k,String(v)),
    removeItem:k=>store.delete(k)
  };
  const base={
    API:'https://example.test/functions/v1',
    auth:()=>({token:'token-test-'+activeUser.id,user:activeUser}),
    requireSession:async n=>({viewer:{display_name:'QA'},session:{session_number:n}}),
    session:async(action,payload)=>{
      sent.push({action,payload});
      if(handler)return handler(action,payload,sent);
      return {ok:true};
    }
  };
  const listeners=new Map();
  const context={
    window:{BIGDATA_LMS:base},
    document:{currentScript:{dataset:{session:'9'}},visibilityState:'visible'},
    location:{search:'?s=9'},
    navigator:{onLine:online},
    localStorage,
    URLSearchParams,
    Date,Math,JSON,Promise,Error,
    setTimeout:(fn)=>{ context._timers.push(fn); return context._timers.length; },
    clearTimeout:()=>{},
    setInterval:()=>1,clearInterval:()=>{},
    addEventListener:(name,fn)=>{listeners.set(name,fn)},
    removeEventListener:()=>{},
    fetch:async()=>({ok:true}),
    crypto:{randomUUID:(()=>{let i=0;return()=>String(++i).padStart(8,'0')+'-0000-4000-8000-000000000000'})()},
    console,
    _timers:[]
  };
  context.globalThis=context;context.window.window=context.window;context.window.LMS=undefined;
  vm.createContext(context);vm.runInContext(source,context);
  return {LMS:context.window.LMS,context,store,sent,listeners,setUser:u=>{activeUser={...u}}};
}

test('track offline queda en cola y luego se sincroniza con client_event_id',async()=>{
  const h=harness({online:false});
  const x=await h.LMS.track('slide_viewed',{activity_code:'bd-s09-presentation',metadata:{slide:17}});
  assert.equal(x.queued,true);
  assert.equal(h.LMS.queueSize(),1);
  h.context.navigator.onLine=true;
  const flushed=await h.LMS.flush();
  assert.equal(flushed.ok,true);
  assert.equal(h.LMS.queueSize(),0);
  assert.equal(h.sent[0].action,'track');
  assert.match(h.sent[0].payload.client_event_id,/^evt-/);
  assert.equal(h.sent[0].payload.session_number,9);
});

test('evidencia offline conserva client_evidence_id al reintentar',async()=>{
  const h=harness({online:false});
  const x=await h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener'});
  assert.equal(x.pending,true);
  const raw=JSON.parse(h.store.get(h.LMS.QUEUE_KEY));
  assert.equal(raw[0].kind,'evidence');
  const id=raw[0].id;
  h.context.navigator.onLine=true;
  await h.LMS.flush();
  assert.equal(h.sent[0].payload.client_evidence_id,id);
});

test('un 500 conserva la entrada y programa retry',async()=>{
  let fail=true;
  const h=harness({online:true,handler:async()=>{
    if(fail){fail=false;const e=new Error('temporal');e.status=500;throw e}
    return {ok:true};
  }});
  const x=await h.LMS.track('lab_interaction',{activity_code:'bd-s09-lab3'});
  assert.equal(x.queued,true);
  assert.equal(h.LMS.queueSize(),1);
  await h.LMS.flush();
  assert.equal(h.LMS.queueSize(),0);
});

test('la cola elimina telemetría antes que evidencia al superar el límite',async()=>{
  const h=harness({online:false});
  for(let i=0;i<505;i++) await h.LMS.track('heartbeat',{active_seconds_delta:1,metadata:{i}});
  await h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener'});
  const q=JSON.parse(h.store.get(h.LMS.QUEUE_KEY));
  assert.ok(q.length<=h.LMS.MAX_QUEUE);
  assert.equal(q.some(x=>x.kind==='evidence'),true);
});

test('wallPost usa idempotency key propia',async()=>{
  const h=harness({online:false});
  await h.LMS.wallPost('bd-s09-lab3','Una respuesta suficientemente extensa para publicar.');
  h.context.navigator.onLine=true;
  await h.LMS.flush();
  assert.equal(h.sent[0].action,'wall_post');
  assert.match(h.sent[0].payload.client_post_id,/^post-/);
});


test('un 401 conserva evidencia para sincronizar tras nuevo login',async()=>{
  const h=harness({online:true,handler:async()=>{
    const e=new Error('sesión vencida');e.status=401;throw e;
  }});
  const x=await h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener'});
  assert.equal(x.queued,true);
  assert.equal(x.auth_required,true);
  assert.equal(h.LMS.queueSize(),1);
  const q=JSON.parse(h.store.get(h.LMS.QUEUE_KEY));
  assert.equal(q[0].kind,'evidence');
});

test('la cola respeta el máximo de 500 incluso si todas las entradas son durables',async()=>{
  const h=harness({online:false});
  for(let i=0;i<505;i++) await h.LMS.evidence('bd-s09-lab3',{result:i,decision:'mantener'});
  assert.equal(h.LMS.queueSize(),h.LMS.MAX_QUEUE);
});


test('la cola no cruza evidencia entre usuarios del mismo navegador',async()=>{
  const h=harness({online:false,user:{id:'user-a',username:'a',display_name:'Ana'}});
  await h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener'});
  const queued=JSON.parse(h.store.get(h.LMS.QUEUE_KEY));
  assert.equal(queued[0].owner_id,'user-a');

  h.setUser({id:'user-b',username:'b',display_name:'Carlos'});
  h.context.navigator.onLine=true;
  const result=await h.LMS.flush();
  assert.equal(result.sent,0);
  assert.equal(h.sent.length,0);
  assert.equal(h.LMS.queueSize(),1);

  h.setUser({id:'user-a',username:'a',display_name:'Ana'});
  const flushed=await h.LMS.flush();
  assert.equal(flushed.sent,1);
  assert.equal(h.LMS.queueSize(),0);
  assert.equal(h.sent[0].action,'evidence');
});

test('una evidencia rechazada queda disponible en LMS.rejected()',async()=>{
  const h=harness({online:true,handler:async()=>{
    const e=new Error('El límite debe tener al menos 40 caracteres');e.status=400;throw e;
  }});
  await assert.rejects(
    h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener',limit:'corto'}),
    /40 caracteres/
  );

  h.context.navigator.onLine=false;
  await h.LMS.evidence('bd-s09-lab3',{result:4,decision:'mantener',limit:'corto'});
  h.context.navigator.onLine=true;
  await h.LMS.flush();
  const rejected=h.LMS.rejected();
  assert.equal(rejected.length,1);
  assert.equal(rejected[0].kind,'evidence');
  assert.match(rejected[0].error_message,/40 caracteres/);
  assert.equal(h.LMS.queueSize(),0);
});

test('entradas legacy sin propietario no se envían y quedan rechazadas',async()=>{
  const h=harness({online:false});
  h.store.set(h.LMS.QUEUE_KEY,JSON.stringify([{
    id:'legacy-0001',kind:'evidence',payload:{session_number:9,activity_code:'bd-s09-lab3',payload:{result:4}},
    attempts:0,created_at_ms:1
  }]));
  h.context.navigator.onLine=true;
  await h.LMS.flush();
  assert.equal(h.sent.length,0);
  assert.equal(h.LMS.queueSize(),0);
  assert.equal(h.LMS.rejected()[0].reject_reason,'unscoped_legacy');
});
