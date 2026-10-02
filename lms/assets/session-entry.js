// Entrada directa al material de cada sesión (AGENTS.md §12): un clic, sin esperar al servidor.
// Fuente única: lms/data/course.json → sessions[].entry {url,label}. Es un archivo estático,
// así que el botón aparece antes de que responda la API y el clic abre el material de inmediato.
(function(){'use strict';
const B=window.BIGDATA_LMS;
const ready=fetch(B.ROOT+'data/course.json',{cache:'no-cache'})
  .then(r=>r.json())
  .then(j=>{const m=new Map((j.sessions||[]).filter(s=>s.entry&&s.entry.url).map(s=>[Number(s.n),s.entry]));m.current=Number(j.current_tracked_session||0);return m})
  .catch(()=>new Map());
const external=url=>/^https?:\/\//i.test(url)&&!url.startsWith(location.origin);
// El registro sale en segundo plano y sobrevive al cambio de página: nunca frena el clic.
function track(n,event_type,metadata){
  const a=B.auth?.();if(!a?.token)return;
  const id='evt-'+(globalThis.crypto?.randomUUID?crypto.randomUUID():Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,12));
  try{fetch(B.API+'/bigdata-session',{method:'POST',keepalive:true,
    headers:{'Content-Type':'application/json','Authorization':'Bearer '+a.token},
    body:JSON.stringify({action:'track',session_number:n,event_type,activity_code:null,metadata:{source:'direct-entry',...metadata},active_seconds_delta:0,client_at:new Date().toISOString(),client_event_id:id})
  }).catch(()=>{})}catch{}
}
function link(n,entry,cls){
  const ext=external(entry.url);
  return '<a class="'+cls+'" href="'+B.esc(entry.url)+'"'+(ext?' target="_blank" rel="noopener"':'')+' data-entry-session="'+Number(n)+'">'+B.esc(entry.label)+(ext?' ↗':'')+'</a>';
}
document.addEventListener('click',e=>{
  const a=e.target.closest?.('a[data-entry-session]');if(!a)return;
  const n=Number(a.dataset.entrySession);
  track(n,'session_entered',{path:a.href});
  track(n,/colab\.research\.google\.com/.test(a.href)?'notebook_opened':'presentation_opened',{path:a.href});
},true);
window.LMS_ENTRY={ready,link,track,external};
})();
