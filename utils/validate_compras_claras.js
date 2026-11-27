"use strict";
const fs=require("node:fs"),assert=require("node:assert/strict"),path=require("node:path"),C=require("../assets/pedagogia/compras.js");
const root=path.resolve(__dirname,".."),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));
const cfg=read("assets/pedagogia/rutas.json"),src=C.setup(read("Datos/tc2_corpus_2026.json"),read("Datos/s10_imagenes_reales/inputs.json"));
let count=0;
for(const scale of [40,80,120])for(const opt of [0,1,2]){
 let s=C.fresh(src);
 for(const id of C.ids){const r=cfg.routes.find(x=>x.id===id);s=C.run(s,id,id==="01"?String(scale):r.mission.options[opt],src,cfg);count++}
 assert.deepEqual(C.validate(JSON.parse(JSON.stringify(s)),src,cfg),s);
 const a=s.steps.find(x=>x.id==="15").result;
 assert.equal(a.rowsAfter,a.repeatRows);assert.equal(a.rowsAfter,a.rowsBefore+a.added);assert.ok(a.conflictRejected);
 const bad=JSON.parse(JSON.stringify(s));bad.steps[3].result.rows=0;assert.throws(()=>C.validate(bad,src,cfg));
 const rewind=C.rewind(s,"03");assert.equal(C.next(rewind),"03");assert.equal(rewind.steps.length,2);
}
let s=C.fresh(src);assert.throws(()=>C.run(s,"02","120",src,cfg));
for(const id of C.required){const r=cfg.routes.find(x=>x.id===id);s=C.run(s,id,r.mission.options[1],src,cfg)}
assert.equal(C.next(s),null);assert.equal(s.steps.length,16);
const html=fs.readFileSync(path.join(root,"Presentaciones/compras-claras.html"),"utf8");
const embedded=JSON.parse(html.match(/<script type="application\/json" id="source">([\s\S]*?)<\/script>/)[1]);assert.deepEqual(embedded,src);
console.log("OK",count,"etapas, 9 recorridos, importación, manipulación, retroceso y ruta sin opcional");
