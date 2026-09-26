import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source=fs.readFileSync(new URL('../lms/assets/lms-kit.js',import.meta.url),'utf8');

function harness({online=false,handler}={}){
  const store=new Map(),sent=[];
  const localStorage={
    getItem:k=>store.has(k)?store.get(k):null,
    setItem:(k,v)=>store.set(k,String(v)),
    removeItem:k=>store.delete(k)
  };
  const base={
    API:'https://example.test/functions/v1',
    auth:()=>({token:'token-test',user:{display_name:'QA'}}),
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
  return {LMS:context.window.LMS,context,store,sent,listeners};
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
