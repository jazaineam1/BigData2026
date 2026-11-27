"use strict";
const assert=require("node:assert/strict"), fs=require("node:fs"), path=require("node:path");
const root=path.resolve(__dirname,"..");
const cfg=JSON.parse(fs.readFileSync(path.join(root,"assets/pedagogia/rutas.json"),"utf8"));
const P=require("../assets/pedagogia/engine.js");
assert.equal(cfg.routes.length,17);
assert.equal(new Set(cfg.routes.map(r=>r.id)).size,17);
for(const r of cfg.routes){
 assert.equal(r.steps.length,4);assert.equal(r.quiz.options.length,r.quiz.feedback.length);
 assert.ok(r.code.trim()&&r.challenge&&r.limit&&r.problem&&r.concept);
 const spec=P.specs[r.kind];assert.ok(spec);
 for(const p of [0,4,1,2]){
   const v=spec.controls.map(c=>c[p===0?1:p===4?4:p===1?2:4]);
   const output=P.compute(r.kind,v);
   assert.equal(output.length,2); const vis=P.visual(r.kind,v);assert.ok(vis.rows.length);assert.ok(vis.rows.every(x=>Number.isFinite(x.value)));assert.ok(output.every(x=>typeof x==="string"&&x.length&&!/NaN|Infinity/.test(x)));
 }
 if(r.ref===cfg.branch)assert.ok(fs.existsSync(path.join(root,r.nb)),r.nb);
 if(r.original)assert.ok(fs.existsSync(path.join(root,"Presentaciones",r.original)),r.original);
}
assert.match(P.compute("queue",[1000,700,600])[0],/180[. ,]?000/);
assert.match(P.compute("training",[25,128,16])[0],/19\.07/);
assert.match(P.compute("amdahl",[120,15,4])[0],/43\.5/);
assert.match(P.compute("replica",[2])[1],/No hay mayoría/);
assert.match(P.compute("metrics",[2,5,3])[0],/imposible/);
assert.match(P.compute("cosine",[0,4])[1],/1\.00/);
const index=fs.readFileSync(path.join(root,"index.html"),"utf8");
for(const r of cfg.routes)assert.ok(index.includes("ruta-aprendizaje.html?s="+r.id),r.id);
assert.ok(index.includes("24 controles evaluables"));
console.log("OK: 17 rutas, 68 estaciones, controles, enlaces locales y casos límite.");
