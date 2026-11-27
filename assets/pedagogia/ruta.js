"use strict";
const $=id=>document.getElementById(id);
const el=(tag,text)=>{const e=document.createElement(tag);if(text!==undefined)e.textContent=text;return e;};
const repo="jazaineam1/BigData2026";
let config,actual,checks=[];
function localRead(key){try{return JSON.parse(localStorage.getItem(key)||"[]");}catch{return [];}}
function localWrite(key,value){try{localStorage.setItem(key,JSON.stringify(value));}catch{/* interfaz funciona sin almacenamiento */}}
function key(){return "bigdata-pedagogia-v1-"+actual.id;}
function link(text,url,alt=false){const a=el("a",text);a.href=url;a.className="action"+(alt?" alt":"");return a;}
function updateProgress(){const n=checks.filter(Boolean).length;$("avance").max=actual.steps.length;$("avance").value=n;$("avanceTexto").textContent=n+" de "+actual.steps.length+" estaciones (solo local).";localWrite(key(),checks);}
function render(id){
 const r=config.routes.find(x=>x.id===id)||config.routes[0];actual=r;
 $("sesion").value=r.id;$("titulo").textContent="S"+r.id+" · "+r.title;$("problema").textContent=r.problem;$("concepto").textContent=r.concept;
 const preview=["localhost","127.0.0.1"].includes(location.hostname)||new URLSearchParams(location.search).has("preview");
 const branch=r.ref===config.branch&&!preview?"main":r.ref;
 const nb="https://github.com/"+repo+"/blob/"+branch+"/"+r.nb;
 const colab="https://colab.research.google.com/github/"+repo+"/blob/"+branch+"/"+r.nb;
 const links=$("links");links.replaceChildren();
 if(r.id==="11"||r.id==="13"){links.append(link("Abrir laboratorio Codespaces","https://codespaces.new/"+repo+"/tree/"+r.ref));}
 else if(r.id==="14A"){links.append(link("Abrir cuaderno para Databricks",nb));}
 else{links.append(link("Abrir cuaderno en Colab",colab));}
 const support=$("apoyos");support.replaceChildren(link("Ver código del cuaderno",nb,true));
 if(r.original)support.append(link("Presentación / guía completa",r.original,true));
 if(r.id==="09")support.append(link("Muro de clase","s09-muro-publico.html",true));
 if(r.id==="11"||r.id==="13")support.append(link("Instrucciones del entorno","https://github.com/"+repo+"/tree/"+r.ref,true));
 const question=$("pregunta");question.replaceChildren(el("legend",r.quiz.question));
 $("feedback").textContent="Elige una opción para ver la explicación.";
 r.quiz.options.forEach((v,i)=>{let lab=el("label"),radio=el("input");radio.type="radio";radio.name="autocomprobacion";radio.value=String(i);radio.addEventListener("change",()=>{$("feedback").textContent=r.quiz.feedback[i];});lab.append(radio,el("span",v));question.append(lab);});
 const spec=Pedagogia.specs[r.kind],values=spec.controls.map(x=>x[4]),ctrl=$("controles");ctrl.replaceChildren();
 const refresh=()=>{const [a,b]=Pedagogia.compute(r.kind,values);$("resultado").textContent=a;$("lectura").textContent=b;
 const visual=Pedagogia.visual(r.kind,values),chart=$("grafico");chart.replaceChildren(el("p",visual.unit));
 const max=Math.max(1e-9,...visual.rows.map(x=>Math.abs(x.value)));
 visual.rows.forEach(x=>{const line=el("div"),label=el("div"),track=el("div"),bar=el("div");
 line.className="chart-row";label.className="chart-label";label.append(el("span",x.label),el("strong",x.value.toLocaleString("es-CO",{maximumFractionDigits:3})));
 track.className="chart-track";bar.className="chart-bar"+(x.value<0?" negative":"");bar.style.width=(Math.abs(x.value)/max*100)+"%";track.setAttribute("aria-hidden","true");track.append(bar);line.append(label,track);chart.append(line);});};
 spec.controls.forEach(([name,min,max,step,initial],i)=>{let box=el("div"),label=el("label"),out=el("output",String(initial)),input=el("input");box.className="control";input.type="range";input.id="control-"+i;label.htmlFor=input.id;label.append(el("span",name),out);input.min=min;input.max=max;input.step=step;input.value=initial;input.addEventListener("input",()=>{values[i]=Number(input.value);out.textContent=input.value;refresh();});box.append(label,input);ctrl.append(box);});refresh();
 checks=localRead(key());if(!Array.isArray(checks)||checks.length!==r.steps.length)checks=r.steps.map(()=>false);checks=checks.map(Boolean);
 const stages=$("estaciones");stages.replaceChildren();
 r.steps.forEach((s,i)=>{let box=el("div"),lab=el("label"),input=el("input");box.className="stage";input.type="checkbox";input.checked=checks[i];input.addEventListener("change",()=>{checks[i]=input.checked;updateProgress();});lab.append(input,el("strong",(i+1)+" · "+s.title));box.append(lab,el("p",s.action),el("small","Evidencia: "+s.evidence));stages.append(box);});updateProgress();
 $("limpiar").onclick=()=>{checks=r.steps.map(()=>false);localWrite(key(),checks);render(r.id);};
 $("codigo").textContent=r.code;$("interpretacion").textContent=r.interpret;$("reto").textContent=r.challenge;$("limite").textContent=r.limit;
 $("copiado").textContent="";$("copiar").onclick=async()=>{try{await navigator.clipboard.writeText(r.code);$("copiado").textContent=" Código copiado.";}catch{$("copiado").textContent=" Selecciona y copia el bloque manualmente.";}};
}
fetch("../assets/pedagogia/rutas.json").then(r=>{if(!r.ok)throw Error("No se pudo cargar la ruta");return r.json();}).then(data=>{
 config=data;data.routes.forEach(r=>{let o=el("option","S"+r.id+" · "+r.title);o.value=r.id;$("sesion").append(o);});
 const id=new URLSearchParams(location.search).get("s")||"01";render(id.padStart(2,"0").toUpperCase());
 $("sesion").addEventListener("change",()=>{const u=new URL(location.href);u.searchParams.set("s",$("sesion").value);history.replaceState(null,"",u);render($("sesion").value);});
}).catch(e=>{$("error").textContent="No fue posible cargar el explorador. Sirve el repositorio por HTTP local y verifica los archivos. "+e.message;});
