function calculate(id,n){
 const fmt=x=>Number(x.toFixed(3)).toLocaleString("es-CO");
 switch(id){
 case"01":return {value:Math.max(0,120-n)*5,unit:"registros pendientes",formula:"max(0, 120 − capacidad) × 5; llegadas constantes"};
 case"02":return {value:100*n*2,unit:"MB brutos",formula:"100 MB/día × días × 2 copias"};
 case"03":return {value:n*100,unit:"bytes de activos",formula:"100 bytes × activos; sin overhead"};
 case"04":return {value:200*n,unit:"MB brutos",formula:"2 fragmentos × 100 MB × copias"};
 case"05":return {value:Math.min(120,n*10),unit:"filas en el bucket máximo",formula:"10 filas/mes × meses por bucket; 12 meses fijos. Número de buckets: "+Math.ceil(12/n)};
 case"06":return {value:2+n,unit:"aristas salientes de A",formula:"Dos aristas iniciales más las nuevas; cada extremo adicional es distinto"};
 case"07":return {value:2.2*n/(1.2+n),unit:"componente TF de BM25",formula:"2,2 × f / (1,2 + f), longitud fija e IDF excluido"};
 case"08":return {value:Math.ceil(12/n)*2,unit:"segundos ideales",formula:"ceil(12 tareas / simultáneas) × 2 s; sin overhead"};
 case"09":return {value:Math.cos(n*Math.PI/180),unit:"similitud coseno",formula:"cos(ángulo); dos vectores unitarios"};
 case"10":return {value:n*500*3,unit:"bytes de matriz RGB",formula:"ancho × 500 × 3 bytes; sin compresión"};
 case"11":return {value:n/20*100,unit:"% WER",formula:"ediciones / 20 palabras × 100; ejemplo manual"};
 case"12":return {value:20-n,unit:"segundos cubiertos",formula:"Audio ficticio de 20 s, 0–10 y (10 + hueco)–20"};
 case"13":return {value:1/(0.2+0.8/n),unit:"× speedup ideal",formula:"1 / (0,2 + 0,8 / p); no tiempo medido"};
 case"14":return {value:n,unit:"registros en la clave máxima",formula:"1.000 totales; otras tres claves reparten "+(1000-n)+" filas"};
 case"14A":return {value:n*1e6*128*8/2**30,unit:"GiB de matriz (mínimo)",formula:"N × 128 × 8 / 2³⁰; no pico RAM ni fit"};
 case"15":return {value:20-(15+3+n),unit:"diferencia entrada − estados",formula:"20 − (15 éxitos + 3 rechazos + pendientes); cero reconcilia"};
 case"16":return {value:2*n,unit:"filas de join",formula:"2 activos × predicciones históricas; ejemplo no evaluativo"};
 default:throw Error("Calculadora desconocida "+id);
 }
}
