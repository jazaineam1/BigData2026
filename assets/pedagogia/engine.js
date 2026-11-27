/* Exploradores formativos: datos pequeños o estimaciones, nunca benchmarks. */
(function(root){
"use strict";
const specs={
memory:{controls:[["Filas",1000,1000000,1000,100000],["Columnas float64",1,200,1,20],["Presupuesto MiB",1,1024,1,64]],run:([n,c,m])=>{let mib=n*c*8/1048576;return [mib.toFixed(2)+" MiB mínimos",mib>m?"Excede el presupuesto declarado.":"Cabe la matriz mínima; faltan sobrecostos."]}},
architecture:{controls:[["Latencia máxima (s)",1,600,1,120]],run:([s])=>{let a=[["Local",300,1],["Lotes",60,2],["Eventos",2,4]].filter(x=>x[1]<=s);return [a.length?a[0][0]:"Ninguna alternativa",a.length?"Menor costo relativo entre opciones viables; latencias ficticias.":"Revisar requisitos o diseñar otra opción."]}},
index:{controls:[["Documentos",100,100000,100,10000],["Coincidencias (%)",1,100,1,1]],run:([n,p])=>[n.toLocaleString("es-CO")+" recorridos frente a "+Math.round(n*p/100).toLocaleString("es-CO")+" coincidencias","Modelo de candidatos: no representa páginas de índice ni tiempo real."]},
replica:{controls:[["Votantes caídos",0,3,1,1]],run:([f])=>[(3-f)+" de 3 disponibles",3-f>=2?"Hay mayoría para una posible elección.":"No hay mayoría para elegir primario."]},
partition:{controls:[["Registros de entidad A",50,100,1,80],["Periodos uniformes",1,12,1,4]],run:([a,m])=>{let max=Math.ceil(a/m);return ["Mayor grupo: "+a+" → "+max,"Clave entidad+periodo: reparto uniforme supuesto; requiere conocer periodo."]}},
graph:{controls:[["Entidad ancla (1=A, 2=B, 3=C)",1,3,1,1]],run:([n])=>{let d=[["A","P1"],["A","P2"],["B","P1"],["C","P2"],["C","P3"]],e=["A","B","C"][n-1],p=new Set(d.filter(x=>x[0]===e).map(x=>x[1]));return [d.filter(x=>x[0]!==e&&p.has(x[1])).map(x=>x.join("–")).join(", ")||"Sin coincidencias","Relación observada; no prueba irregularidad."]}},
bm25:{controls:[["k1 × 10",1,30,1,12],["b × 100",0,100,5,75]],run:([k,b])=>{k/=10;b/=100;let d=["salud salud hospital","equipos transporte","hospital salud equipos","salud"].map(x=>x.split(" ")),av=d.reduce((s,x)=>s+x.length,0)/d.length,df=d.filter(x=>x.includes("salud")).length,idf=Math.log(1+(d.length-df+.5)/(df+.5));let r=d.map((x,i)=>{let f=x.filter(y=>y==="salud").length;return [i+1,idf*f*(k+1)/(f+k*(1-b+b*x.length/av))]}).sort((a,b)=>b[1]-a[1]);return [r.map(x=>"D"+x[0]+": "+x[1].toFixed(3)).join(" | "),"BM25 calculado sobre cuatro documentos con consulta salud; cambia un parámetro."]}},
pages:{controls:[["Filas",100,10000,100,3000],["Límite por página",50,500,50,250]],run:([n,l])=>[Math.ceil(n/l)+" páginas","Offsets: 0, "+l+", "+2*l+"… último: "+(Math.ceil(n/l)-1)*l+". La fuente real puede cambiar."]},
cosine:{controls:[["Ángulo (grados)",0,180,5,30],["Candidatos conservados de 4",1,4,1,2]],run:([a,n])=>["Coseno "+Math.cos(a*Math.PI/180).toFixed(3),"Si el filtro de candidatos conserva los "+n+" últimos de [D0,D1,D2,D3] y los exactos son D0,D1, recall@2 = "+(Math.max(0,n-2)/2).toFixed(2)+". Simulación, no HNSW."]},
media:{controls:[["Ancho imagen (px)",100,2000,100,1000],["Alto imagen (px)",100,2000,100,1000],["Audio (segundos)",1,300,1,60],["Muestreo (kHz)",8,48,8,16]],run:([w,h,s,k])=>["RGB "+(w*h*3/1048576).toFixed(2)+" MiB · PCM "+(s*k*1000*2/1048576).toFixed(2)+" MiB","Sin compresión: imagen RGB8 y voz mono PCM16. El tamaño del contenedor puede variar."]},
wer:{controls:[["Palabras de referencia",1,30,1,5],["Ediciones totales",0,40,1,1]],run:([n,e])=>["WER "+(e/n*100).toFixed(1)+"%","(Sustituciones + omisiones + inserciones)/referencia. Puede superar 100%."]},
metrics:{controls:[["Relevantes conocidos",1,10,1,3],["k",1,10,1,5],["Aciertos",0,10,1,2]],run:([r,k,a])=>a>Math.min(r,k)?["Combinación imposible","Aciertos no pueden superar k ni relevantes."]:["Precision "+(a/k).toFixed(2)+" · Recall "+(a/r).toFixed(2),"Mismo conjunto de juicios; los no evaluados requieren una política."]},
amdahl:{controls:[["Tiempo secuencial (s)",10,300,10,120],["Parte serial (%)",0,100,5,15],["Workers ideales",1,16,1,4]],run:([t,s,p])=>{let v=t*(s/100+(1-s/100)/p);return [v.toFixed(1)+" s · "+(t/v).toFixed(2)+"×","Ley de Amdahl sin sobrecostos. Compara con mediciones, no con estimaciones."]}},
shuffle:{controls:[["Filas de hechos (miles)",1,1000,1,100],["Bytes por fila",8,256,8,64],["Dimensión (KiB)",1,1024,1,32],["Ejecutores ilustrativos",1,8,1,4]],run:([n,b,d,p])=>["Hechos "+(n*1000*b/1048576).toFixed(2)+" MiB · copias dimensión "+(d*p/1024).toFixed(2)+" MiB","Estimaciones de tamaño bruto, no bytes de shuffle reales; observa el plan y perfil."]},
training:{controls:[["Millones de filas",0.05,25,0.05,1],["Variables",32,256,32,128],["Presupuesto GiB",1,32,1,16]],run:([n,v,m])=>{let g=n*1000000*.8*v*8/1073741824;return [g.toFixed(2)+" GiB",g>m?"Matriz mínima excede presupuesto. No prueba ejecución Spark.":"Cabe la matriz mínima; falta memoria de entrenamiento."]}},
queue:{controls:[["Llegada registros/s",0,2000,100,1000],["Capacidad registros/s",0,2000,100,700],["Segundos",60,600,60,600]],run:([a,b,s])=>[(Math.max(0,a-b)*s).toLocaleString("es-CO")+" pendientes","Cola inicialmente vacía y tasas constantes; no simula latencias variables."]},
split:{controls:[["Filas",100,10000,100,1000],["Train (%)",50,90,5,80],["Validación (%)",5,40,5,10]],run:([n,t,v])=>t+v>=100?["Sin test disponible","Reserva una fracción para evaluar al final."]:[Math.floor(n*t/100)+" train · "+Math.floor(n*v/100)+" valid · "+(n-Math.floor(n*t/100)-Math.floor(n*v/100))+" test","Distribución aritmética aproximada; el split real depende de grupos, identidad y tiempo."]}
};
function compute(kind,values){if(!specs[kind])throw Error("Explorador desconocido");return specs[kind].run(values);}

function visual(kind,v){
 const [a,b,c,d]=v, row=(label,value)=>({label,value});
 switch(kind){
 case "memory":return {unit:"MiB",rows:[row("Matriz mínima",a*b*8/1048576),row("Presupuesto",c)]};
 case "architecture":return {unit:"segundos (supuesto)",rows:[row("Local",300),row("Lotes",60),row("Eventos",2),row("Límite",a)]};
 case "index":return {unit:"registros",rows:[row("Recorrido completo",a),row("Coincidencias",Math.round(a*b/100))]};
 case "replica":return {unit:"votantes",rows:[row("Disponibles",3-a),row("Caídos",a),row("Mayoría",2)]};
 case "partition":return {unit:"registros por grupo máximo",rows:[row("Entidad",a),row("Entidad + periodo",Math.ceil(a/b))]};
 case "graph":{const e=["A","B","C"][a-1],pairs=[["A","P1"],["A","P2"],["B","P1"],["C","P2"],["C","P3"]],mine=new Set(pairs.filter(x=>x[0]===e).map(x=>x[1]));return {unit:"proveedores compartidos con "+e,rows:["A","B","C"].filter(x=>x!==e).map(x=>row(x,pairs.filter(p=>p[0]===x&&mine.has(p[1])).length))};}
 case "bm25":return {unit:"puntuación BM25",rows:compute(kind,v)[0].split(" | ").map(x=>{const [l,z]=x.split(": ");return row(l,Number(z));})};
 case "pages":return {unit:"registros",rows:[row("Total",a),row("Página completa",Math.min(a,b)),row("Última página",a%b||Math.min(a,b))]};
 case "cosine":return {unit:"valor (coseno puede ser negativo)",rows:[row("Coseno",Math.cos(a*Math.PI/180)),row("Recall@2 exacto",Math.max(0,b-2)/2)]};
 case "media":return {unit:"MiB sin compresión",rows:[row("Imagen RGB8",a*b*3/1048576),row("Audio PCM16",c*d*1000*2/1048576)]};
 case "wer":return {unit:"palabras / ediciones",rows:[row("Referencia",a),row("Ediciones",b)]};
 case "metrics":return {unit:"registros",rows:[row("Relevantes",a),row("Top-k",b),row("Aciertos",c)]};
 case "amdahl":return {unit:"segundos ideales",rows:[...new Set([1,2,4,8,c])].sort((x,y)=>x-y).map(p=>row(p+" worker(s)",a*(b/100+(1-b/100)/p)))};
 case "shuffle":return {unit:"MiB estimados",rows:[row("Hechos",a*1000*b/1048576),row("Copias dimensión",c*d/1024)]};
 case "training":return {unit:"GiB mínimos",rows:[row("Matriz de train",a*1e6*.8*b*8/1073741824),row("Presupuesto",c)]};
 case "queue":return {unit:"registros por segundo",rows:[row("Llegada",a),row("Capacidad",b),row("Exceso",Math.max(0,a-b))]};
 case "split":return {unit:"registros (aprox.)",rows:[row("Train",Math.floor(a*b/100)),row("Validación",Math.floor(a*c/100)),row("Test",Math.max(0,a-Math.floor(a*b/100)-Math.floor(a*c/100)))]};
 default:throw Error("Visual desconocido");
 }
}

const api={specs,compute,visual};if(typeof module!=="undefined"&&module.exports)module.exports=api;else root.Pedagogia=api;
})(typeof globalThis!=="undefined"?globalThis:this);
