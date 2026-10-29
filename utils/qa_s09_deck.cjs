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
// Un fallo anterior mostraba "\n" literalmente dentro de las tarjetas de código.
for (let i=21; i<slides.length; i++) {
  const codes=[...slides[i].b.matchAll(/<pre\b[^>]*>([\s\S]*?)<\/pre>/gi)];
  for (const code of codes) {
    assert(!code[1].includes('\\n'),
      "S"+(i+1)+" muestra texto literal \\n en lugar de un salto de línea");
  }
}
assert(slides[21].b.includes("atlas-chain"),"S22 sin flujo Colab-Atlas");
assert(slides[27].b.includes("JSON Editor"),"S28 sin creación UI");
assert(slides[28].b.includes("queryable"),"S29 sin verificación de estado");
assert(slides[29].b.includes("Aggregations"),"S30 sin ejecución UI");
assert(slides[31].b.includes("USAR_ENTIDAD_DEL_RESULTADO"),"S32 sin decisión sobre resultado propio");
assert(slides[32].b.includes("s09_pipeline_atlas_ui.json"),"S33 sin pipeline real");
assert(slides[20].b.includes("AQUÍ NOS HABÍAMOS QUEDADO"),"S21 sin marca de reanudación");
for(const label of ["Cómo se lee","Qué nos dice","Qué NO permite concluir todavía","Qué error común"]) assert(slides[33].b.includes(label),"S34 sin interpretación: "+label);
const vectorLabJs = fs.readFileSync("assets/s09/vector-lab.js","utf8");
const vectorLabCss = fs.readFileSync("assets/s09/vector-lab.css","utf8");
assert(html.includes('src="../assets/s09/vector-lab.js'),"S09 no carga la aplicación vectorial");
assert(html.includes('href="../assets/s09/vector-lab.css'),"S09 no carga los estilos de la aplicación");
new Function(vectorLabJs);
assert(vectorLabJs.includes("SIMULACION_DIDACTICA_LOCAL_2D"),"Falta advertencia de motor simulado");
assert(vectorLabJs.includes("motor_real_atlas_ejecutado:false"),"La simulación no debe reportar Atlas real");
assert(vectorLabJs.includes("s09_simulacion_local.json"),"Salida simulada mal identificada");
assert(vectorLabCss.includes("@media(max-width:760px)"),"Falta disposición móvil");
console.log("S09 DECK QA OK: 35 slides válidas, scripts compilables y ruta Atlas UI.");
