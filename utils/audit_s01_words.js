"use strict";
const fs=require("node:fs"),path=require("node:path");
function auditar(s,n){
 const teaching=s.filter(x=>x[1]!=="Pausa"),word=t=>(t.match(/[\p{L}\p{N}]+/gu)||[]).length;
 const counts={reading:teaching.reduce((a,x)=>a+word(x[8].join(" ")),0),chapters:teaching.reduce((a,x)=>a+(x[11]||[]).reduce((b,z)=>b+word(z.paragraphs.join(" ")),0),0),formative:teaching.reduce((a,x)=>a+word([x[10].question,...x[10].choices,...x[10].feedback,x[10].transfer].join(" ")),0),notebook:n.cells.filter(x=>x.cell_type==="markdown").reduce((a,x)=>a+word(x.source.join("")),0)};
 const blocks=[...teaching.flatMap(x=>[...x[8],...(x[11]||[]).flatMap(z=>z.paragraphs),x[10].question,...x[10].choices,...x[10].feedback,x[10].transfer]),...n.cells.filter(x=>x.cell_type==="markdown").flatMap(c=>c.source.join("").split(/\n\s*\n/))];
 const clean=t=>t.replace(/^#{1,6} .+$/gm,"").replace(/https?:\/\/[^\s)]+/g,"").replace(/\[[^\]]+\]\([^)]*\)/g,"").replace(/`[^`]*`/g,"").replace(/^\s*[-*]\s+/gm,"").trim();
 let seen=new Set(),removed=0,items=[];
 for(let t of blocks){t=clean(t);if(!t)continue;const k=t.normalize("NFKC").toLowerCase().replace(/\s+/g," ");if(seen.has(k)){removed+=word(t);continue}seen.add(k);const tok=k.match(/[\p{L}\p{N}]+/gu)||[],sh=new Set(tok.slice(0,-4).map((_,i)=>tok.slice(i,i+5).join(" ")));items.push({t,tok,sh})}
 let matches=[],pairs=0;for(let i=0;i<items.length;i++){const a=items[i];if(a.tok.length<40)continue;for(let j=0;j<i;j++){const b=items[j];if(b.tok.length<40)continue;pairs++;const [x,y]=a.sh.size<b.sh.size?[a.sh,b.sh]:[b.sh,a.sh];let hits=0;for(const k of x)if(y.has(k))hits++;const containment=hits/x.size,ratio=Math.min(a.tok.length,b.tok.length)/Math.max(a.tok.length,b.tok.length);if(containment>=.55&&ratio>=.7)matches.push({i,j,containment,ratio,a:a.t.slice(0,120),b:b.t.slice(0,120)})}}
 const lexical=items.reduce((a,x)=>a+word(x.t),0);
 return {counts,gross:Object.values(counts).reduce((a,x)=>a+x,0),lexical_exact_dedup:lexical,exact_duplicate_words:removed,blocks:items.length,pairs,near_matches:matches,near_method:"5 palabras consecutivas; contención ≥0,55; razón de longitud ≥0,7; ambos bloques ≥40 palabras",limitations:"Excluye encabezados Markdown, enlaces, código inline y duplicados de bloque exactos; no cuenta celdas de código, datos o salidas. No acredita ausencia de paráfrasis repetitivas ni calidad semántica."}
}
const root=path.resolve(__dirname,".."),read=p=>JSON.parse(fs.readFileSync(path.join(root,p),"utf8"));const result=auditar(read("revision/s01-source.json"),read("revision/s01-laboratorio.ipynb"));console.log(JSON.stringify(result,null,2));if(result.lexical_exact_dedup<40000||result.near_matches.length)process.exitCode=1;
