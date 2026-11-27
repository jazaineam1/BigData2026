/* Núcleo portable de Compras Claras. No pretende ejecutar motores externos. */
(function(root){
"use strict";
const ids=["01","02","03","04","05","06","07","08","09","10","11","12","13","14","14A","15","16"];
const required=ids.filter(x=>x!=="14A");
const copy=x=>JSON.parse(JSON.stringify(x));
const stable=x=>Array.isArray(x)?"["+x.map(stable).join(",")+"]":x&&typeof x==="object"?"{"+Object.keys(x).sort().map(k=>JSON.stringify(k)+":"+stable(x[k])).join(",")+"}":JSON.stringify(x);
// Huella de coherencia no criptográfica: no certifica autenticidad.
function fingerprint(x){let h=2166136261;for(const c of stable(x)){h=Math.imul(h^c.charCodeAt(0),16777619);}return (h>>>0).toString(16).padStart(8,"0")}
function assert(ok,msg){if(!ok)throw Error(msg)}
const tokens=s=>String(s||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().match(/[a-z0-9]+/g)||[];
const counts=(arr,key)=>{const m=new Map();for(const x of arr){const k=key(x);m.set(k,(m.get(k)||0)+1)}return [...m].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]))};
const txt=d=>d.nombre_proceso+" "+d.descripcion;
function rank(docs,q,mode){const query=[...new Set(tokens(q))],ds=docs.map(d=>({id:d.id_proceso,t:tokens(txt(d))})),avg=ds.reduce((a,d)=>a+d.t.length,0)/Math.max(1,ds.length)||1;const dfs=new Map();for(const d of ds)for(const t of new Set(d.t))dfs.set(t,(dfs.get(t)||0)+1);
const idf=t=>Math.log(1+(ds.length-(dfs.get(t)||0)+.5)/((dfs.get(t)||0)+.5));
const tfidf=t=>Math.log((ds.length+1)/((dfs.get(t)||0)+1))+1;
const vector=ts=>new Map(counts(ts,x=>x).map(([t,f])=>[t,f*tfidf(t)]));const qv=vector(query);const norm=v=>Math.sqrt([...v.values()].reduce((s,x)=>s+x*x,0));
return ds.map(d=>{let score=0;if(mode==="bm25"){for(const t of query){const f=d.t.filter(x=>x===t).length;score+=idf(t)*f*2.2/(f+1.2*(.25+.75*d.t.length/avg));}}else{const v=vector(d.t);score=[...qv].reduce((s,[t,w])=>s+w*(v.get(t)||0),0)/(norm(qv)*norm(v)||1)}return {id:d.id,score:Number(score.toFixed(9))}}).filter(x=>x.score>0).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));}
function fuse(a,b){const m=new Map();[a,b].forEach(r=>r.forEach((x,i)=>m.set(x.id,(m.get(x.id)||0)+1/(60+i+1))));return [...m].map(([id,score])=>({id,score:Number(score.toFixed(9))})).sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id))}
function setup(corpus,media){const raw=corpus.documentos.map(d=>({id_proceso:String(d.id_proceso),nombre_proceso:String(d.nombre_proceso||""),descripcion:String(d.descripcion||""),entidad:String(d.entidad||""),url_secop:String(d.url_secop||""),fuente:String(d.fuente||""),tipo_registro:String(d.tipo_registro||"")}));
assert(raw.length>120&&new Set(raw.map(d=>d.id_proceso)).size===raw.length,"Corpus insuficiente o IDs duplicados");
const assets=media.map(m=>({id:String(m.job_id),article_id:String(m.article_id),source_url:String(m.source_url),credit:String(m.credit||"Sin crédito informado"),sha256:String(m.input_sha256),type:"imagen"}));
assert(new Set(assets.map(x=>x.id)).size===assets.length,"IDs multimedia duplicados");
const dataset=fingerprint({raw,assets});return {raw,assets,dataset}}
function fresh(source){return {schema:"compras-claras-v1",dataset:source.dataset,steps:[],lab:{}}}
function next(s){return required.find(x=>!s.steps.some(t=>t.id===x))||null}
function find(s,id){const r=s.steps.find(x=>x.id===id);assert(r,"Falta S"+id);return r.result}
function output(id,p,s,src){
const n=Number(p),list=(id)=>find(s,id),docs=()=>list("03").docs;
switch(id){
case "01":{const raw=src.raw.slice(0,n);assert([40,80,120].includes(n),"Escala no permitida");return {raw,rows:raw.length,source:"Datos/tc2_corpus_2026.json",coverage:raw.length/src.raw.length}}
case "02":{const raw=list("01");const options=[["local",300,1],["lotes",60,2],["eventos",2,4]];const choice=options.find(x=>x[1]<=n);assert(choice,"Requisito no viable");return {inputRows:raw.rows,architecture:choice[0],alternatives:options,latency:n,kind:"hipótesis, no SLA medido"}}
case "03":{list("02");const d=list("01").raw.map(x=>({...x,metadata:{source:x.fuente,recordType:x.tipo_registro}}));return {docs:d,rows:d.length,distinct:new Set(d.map(x=>x[p])).size,field:p}}
case "04":{const d=docs();return {ids:d.slice(0,n).map(x=>x.id_proceso),rows:Math.min(n,d.length),order:"orden de muestra, no riesgo",persistence:"exportar/importar JSON; Atlas se comprueba en el cuaderno"}}
case "05":{const q=list("04"),d=docs(),groups=Object.fromEntries(counts(d,x=>x[p]).map(([k])=>[k,d.filter(x=>x[p]===k).map(x=>x.id_proceso)]));const first=d.find(x=>x.id_proceso===q.ids[0]);return {key:p,groups,lookup:first[p],ids:groups[first[p]],max:Math.max(...Object.values(groups).map(x=>x.length))}}
case "06":{const g=list("05"),d=docs();const entities=counts(d,x=>x.entidad).slice(0,n).map(x=>x[0]);return {anchor:g.ids[0],edges:d.filter(x=>entities.includes(x.entidad)).map(x=>({entity:x.entidad,process:x.id_proceso})),entities,scope:"entidad-proceso; proveedor no disponible en este corpus"}}
case "07":{list("06");return {query:p,ranking:rank(docs(),p,"bm25"),engine:"BM25 local JavaScript"}}
case "08":{const d=docs(),q=list("04"),g=list("06"),r=list("07"),known=new Set(d.map(x=>x.id_proceso));assert(q.ids.every(x=>known.has(x))&&g.edges.every(x=>known.has(x.process))&&r.ranking.every(x=>known.has(x.id)),"Referencia inválida");return {version:"1.0",rows:d.length,checked:Math.min(n,d.length),referencesOK:true,top:r.ranking.slice(0,n)}}
case "09":{list("08");const a=rank(docs(),p,"bm25"),b=rank(docs(),p,"tfidf");return {query:p,lexical:a,cosine:b,hybrid:fuse(a,b),engine:"BM25 + coseno TF-IDF + RRF local; NO embeddings E5"}}
case "10":{list("09");return {assets:src.assets.slice(0,n),rows:Math.min(n,src.assets.length),source:"Datos/s10_imagenes_reales/inputs.json",scope:"inventario real de imágenes, sin unión con SECOP"}}
case "11":{const a=list("10").assets;return {assets:a.map(x=>({...x,extraction:"pendiente de resultado real"})),mode:p,available:p==="imagen"?a.length:0,extracted:0,scope:"sin ejecutar OCR/ASR en navegador; revisar archivo de laboratorio adjunto"}}
case "12":{const a=list("11"),r=list("09");return {version:"2.0",checked:Math.min(n,a.assets.length),inventory:a.assets.length,extracted:a.extracted,hybridTop:r.hybrid.slice(0,5),scope:"metadatos locales; evidencia externa separada"}}
case "13":{list("12");const d=docs(),parts=Array.from({length:n},()=>[]);d.forEach((x,i)=>parts[i%n].push(x));const sum=new Map();for(const part of parts)for(const [k,v] of counts(part,x=>x.entidad))sum.set(k,(sum.get(k)||0)+v);const grouped=[...sum].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));assert(stable(grouped)===stable(counts(d,x=>x.entidad)),"Reducción incorrecta");return {partitions:parts.map(x=>x.length),grouped,rows:d.length,engine:"particiones lógicas locales; Dask real en cuaderno"}}
case "14":{const a=list("13");return {gold:a.grouped.slice(0,n),rows:a.rows,total:a.grouped.reduce((s,x)=>s+x[1],0),scope:"agregación local; no inferencia MLlib"}}
case "14A":{list("14");return {rows:n*1e6,dimensions:128,trainGiB:n*1e6*.8*128*8/1073741824,budgetGiB:16,scope:"estimación float64; no entrenamiento"}}
case "15":{list("14");const old=docs(),incoming=src.raw.slice(old.length,old.length+n);const merge=(base,batch)=>{const m=new Map(base.map(x=>[x.id_proceso,x]));for(const x of batch){if(m.has(x.id_proceso)){const y=m.get(x.id_proceso);assert(y.nombre_proceso===x.nombre_proceso&&y.descripcion===x.descripcion&&y.entidad===x.entidad,"Conflicto de identidad")}else m.set(x.id_proceso,x)}return [...m.values()]};const first=merge(old,incoming),again=merge(first,incoming);assert(stable(first)===stable(again),"Repetición no idempotente");let conflict=false;try{merge(first,[{...first[0],nombre_proceso:"CAMBIO CONTROLADO"}])}catch{conflict=true}assert(conflict,"No se detectó conflicto");return {rowsBefore:old.length,rowsAfter:first.length,added:incoming.length,repeatRows:again.length,conflictRejected:conflict,updated:first,scope:"prueba de algoritmo local; atomicidad en S15 SQLite"}}
case "16":{const a=list("15"),b=list("12"),r=list("09");return {version:"3.0",rows:a.rowsAfter,inventory:b.inventory,extracted:b.extracted,top:rank(a.updated,r.query,"bm25").slice(0,n),grouped:counts(a.updated,x=>x.entidad).slice(0,n),scope:"observatorio local; evidencia de motores externos adjunta, no certificada"}}
default:throw Error("Sesión desconocida")}
}
function run(s,id,param,src,cfg){assert(s.dataset===src.dataset,"Otra versión de fuentes");const r=cfg.routes.find(x=>x.id===id);assert(r&&r.mission.options.includes(String(param)),"Parámetro fuera del contrato");assert(!s.steps.some(x=>x.id===id),"Etapa ya confirmada: reinicia desde ella para cambiar parámetros");
if(id==="14A"){assert(s.steps.some(t=>t.id==="14"),"Primero S14");}else assert(next(s)===id,"Completa primero S"+next(s));
const result=output(id,String(param),s,src),prev=s.steps.filter(t=>t.id!=="14A").at(-1)?.fingerprint||src.dataset;
const input=id==="14A"?s.steps.find(t=>t.id==="14").fingerprint:prev;const step={id,param:String(param),input,result,fingerprint:fingerprint({id,param:String(param),input,result})};return {...s,steps:[...s.steps,step]}}
function validate(candidate,src,cfg){assert(candidate&&candidate.schema==="compras-claras-v1"&&candidate.dataset===src.dataset&&Array.isArray(candidate.steps),"Archivo no corresponde al contrato o fuentes");let s=fresh(src);for(const t of candidate.steps){s=run(s,t.id,t.param,src,cfg);assert(stable(s.steps.at(-1))===stable(t),"Resultado alterado en S"+t.id)}for(const [id,lab] of Object.entries(candidate.lab||{}))s=attach(s,id,lab);return s}
function rewind(s,id){const cut=required.indexOf(id);if(id==="14A")return {...s,steps:s.steps.filter(x=>x.id!=="14A"),lab:Object.fromEntries(Object.entries(s.lab).filter(([k])=>k!=="14A"))};assert(cut>=0,"Etapa desconocida");return {...s,steps:s.steps.filter(x=>x.id==="14A"?cut>required.indexOf("14"):required.indexOf(x.id)<cut),lab:Object.fromEntries(Object.entries(s.lab).filter(([k])=>k==="14A"?cut>required.indexOf("14"):required.indexOf(k)<cut))}}

function sha256(s){
 const encoded=encodeURIComponent(s),data=[];for(let i=0;i<encoded.length;i++){if(encoded[i]==="%"){data.push(parseInt(encoded.slice(i+1,i+3),16));i+=2}else data.push(encoded.charCodeAt(i))}
 const bits=data.length*8;data.push(128);while(data.length%64!==56)data.push(0);for(let i=7;i>=0;i--)data.push(Math.floor(bits/2**(8*i))&255);
 const K=[0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2];
 let H=[0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19];const rr=(x,n)=>(x>>>n)|(x<<(32-n));
 for(let off=0;off<data.length;off+=64){const w=[];for(let i=0;i<16;i++){const j=off+4*i;w[i]=(data[j]<<24)|(data[j+1]<<16)|(data[j+2]<<8)|data[j+3]}for(let i=16;i<64;i++){const s0=rr(w[i-15],7)^rr(w[i-15],18)^(w[i-15]>>>3),s1=rr(w[i-2],17)^rr(w[i-2],19)^(w[i-2]>>>10);w[i]=(w[i-16]+s0+w[i-7]+s1)|0}
 let [a,b,c,d,e,f,g,h]=H;for(let i=0;i<64;i++){const S1=rr(e,6)^rr(e,11)^rr(e,25),ch=(e&f)^(~e&g),t1=(h+S1+ch+K[i]+w[i])|0,S0=rr(a,2)^rr(a,13)^rr(a,22),maj=(a&b)^(a&c)^(b&c),t2=(S0+maj)|0;h=g;g=f;f=e;e=(d+t1)|0;d=c;c=b;b=a;a=(t1+t2)|0}H=H.map((x,i)=>(x+[a,b,c,d,e,f,g,h][i])|0)}
 return H.map(x=>(x>>>0).toString(16).padStart(8,"0")).join("")
}

function attach(s,id,lab){assert(ids.includes(id)&&s.steps.some(t=>t.id===id),"Confirma etapa local primero");assert(lab&&lab.schema==="compras-claras-lab-v1"&&lab.session===id&&["dataframe","json","scalar","manual"].includes(lab.kind)&&typeof lab.source==="string"&&lab.source.length>0&&/^[a-f0-9]{64}$/.test(lab.sha256)&&lab.payload!==undefined,"Formato de evidencia inválido");assert(JSON.stringify(lab).length<300000,"Adjunto demasiado grande");assert(typeof lab.payload_json==="string"&&sha256(lab.payload_json)===lab.sha256,"SHA-256 no coincide con el adjunto");assert(stable(JSON.parse(lab.payload_json))===stable(lab.payload),"Contenido y serialización no coinciden");return {...s,lab:{...s.lab,[id]:copy(lab)}}}

function compare(s,id,param,src,cfg){const base=s.steps.find(t=>t.id===id);assert(base,"Confirma la primera decisión");assert(base.param!==String(param),"Elige una alternativa distinta");const alternative=run(rewind(s,id),id,param,src,cfg).steps.at(-1);return {id,chosen:base.param,alternative:String(param),chosenFingerprint:base.fingerprint,alternativeFingerprint:alternative.fingerprint,chosenResult:base.result,alternativeResult:alternative.result,changed:stable(base.result)!==stable(alternative.result)}}

const api={setup,fresh,next,run,validate,rewind,attach,fingerprint,stable,required,ids,compare,sha256};if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.Compras=api;
})(typeof globalThis!=="undefined"?globalThis:this);
