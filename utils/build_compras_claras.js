"use strict";
const fs=require("node:fs"),path=require("node:path"),C=require("../assets/pedagogia/compras.js");
const root=path.resolve(__dirname,".."),read=p=>fs.readFileSync(path.join(root,p),"utf8");
const config=JSON.parse(read("assets/pedagogia/rutas.json"));
const source=C.setup(JSON.parse(read("Datos/tc2_corpus_2026.json")),JSON.parse(read("Datos/s10_imagenes_reales/inputs.json")));
const safe=x=>JSON.stringify(x).replace(/</g,"\\u003c").replace(/\u2028/g,"\\u2028").replace(/\u2029/g,"\\u2029");
const values={CSS:read("assets/pedagogia/compras.css"),CONFIG:safe(config),SOURCE:safe(source),ENGINE:read("assets/pedagogia/compras.js"),UI:read("assets/pedagogia/compras-ui.js")};
const out=read("assets/pedagogia/compras-template.html").replace(/__CC_(CSS|CONFIG|SOURCE|ENGINE|UI)__/g,(_,k)=>values[k]);
const target=path.join(root,"Presentaciones/compras-claras.html");
if(process.argv.includes("--check")){if(fs.readFileSync(target,"utf8")!==out)throw Error("HTML desactualizado: regenerar");console.log("HTML autónomo sincronizado");}
else{fs.writeFileSync(target,out);console.log("HTML autónomo generado");}
