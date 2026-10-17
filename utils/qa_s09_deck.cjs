// S09 · comprobación de presentación sin navegador ni Atlas.
const fs = require("node:fs");
const assert = require("node:assert/strict");
const html = fs.readFileSync("Presentaciones/s09-de-palabras-a-significado.html","utf8");
const inline = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)];
for (const [i,m] of inline.entries()) {
  try { new Function(m[1]); }
  catch(e){ throw new Error("JS inline "+i+": "+e.message); }
}
const start=html.indexOf("const slides=[");
const stop=html.indexOf("\n];",start);
assert(start>=0 && stop>start,"Falta array slides");
const code=html.slice(start,stop+3);
const names=[...new Set([...code.matchAll(/\b(svg[A-Za-z0-9_]+|challengeChoice)\(/g)].map(x=>x[1]))];
const stubs=names.map(name=>name==="challengeChoice"?()=>'<div class="challenge"></div>':()=>'<svg viewBox="0 0 10 10"></svg>');
const slides=(new Function(...names,code+"; return slides;"))(...stubs);
assert.equal(slides.length,35,"Deben existir 35 diapositivas");
for (const [index,slide] of slides.entries()){
  assert(slide && typeof slide==="object", "S"+(index+1)+" no es objeto");
  for(const field of ["t","k","h","b"]){
    assert(typeof slide[field]==="string" && slide[field].trim(),
      "S"+(index+1)+" sin "+field);
    assert(!/\bundefined\b/.test(slide[field]),"S"+(index+1)+" contiene undefined");
  }
}
assert(slides[21].b.includes("atlas-chain"),"S22 sin flujo Colab-Atlas");
assert(slides[27].b.includes("JSON Editor"),"S28 sin creación UI");
assert(slides[28].b.includes("queryable"),"S29 sin verificación de estado");
assert(slides[29].b.includes("Aggregations"),"S30 sin ejecución UI");
assert(slides[31].b.includes("atlasMode"),"S32 sin comparación ANN/ENN");
assert(slides[32].b.includes("s09_pipeline_atlas_ui.json"),"S33 sin pipeline real");
assert(slides[33].b.includes('class="challenge"'),"S34 sin D5");
console.log("S09 DECK QA OK: 35 slides válidas, scripts compilables y ruta Atlas UI.");
