'use strict';
const $=id=>document.getElementById(id);
const fmt=x=>new Intl.NumberFormat('es-CO').format(x);
const pct=x=>Number.isFinite(x)?new Intl.NumberFormat('es-CO',{style:'percent',maximumFractionDigits:x<.01?2:1}).format(x):'—';
const h=(str)=>String(str).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const clone=x=>JSON.parse(JSON.stringify(x));
const DEMO={meta:{id:'demo',name:'Liga demostrativa',country:'Sintética',season:'Ejemplo',asOf:'—',timezone:'America/Bogota',topN:2,gamesPerTeam:3,status:'DATOS SINTÉTICOS'},teams:[{id:'A',name:'Aurora',pts:0,pj:0,w:0,d:0,l:0,gf:0,ga:0},{id:'B',name:'Brisa',pts:0,pj:0,w:0,d:0,l:0,gf:0,ga:0},{id:'C',name:'Cóndor',pts:0,pj:0,w:0,d:0,l:0,gf:0,ga:0},{id:'D',name:'Delta',pts:0,pj:0,w:0,d:0,l:0,gf:0,ga:0}],fixtures:[{id:'1-A-B',round:1,home:'A',away:'B'},{id:'1-C-D',round:1,home:'C',away:'D'},{id:'2-A-C',round:2,home:'A',away:'C'},{id:'2-B-D',round:2,home:'B',away:'D'},{id:'3-A-D',round:3,home:'A',away:'D'},{id:'3-B-C',round:3,home:'B',away:'C'}],recentFinals:[],sources:[]};
let data=clone(window.MATCHLAB_INITIAL_DATA),team='DIM',picks=[],probs=[],goalGrids=[],modelProbs=[],goalLambdas=[],sim=null,tableMode='modal',busy=false,lastRoute=0n;
let liveOverlay=new Map(),feedState={status:'starting',lastCheck:null,message:'Todavía no se ha consultado el proveedor',source:'SportScore',updatedAt:null};
const SNAPSHOT=clone(window.MATCHLAB_INITIAL_DATA);

let teamIndex=new Map();
function validate(d){
 if(!d||!d.meta||!Array.isArray(d.teams)||!Array.isArray(d.fixtures))throw Error('JSON: se esperan meta, teams, fixtures.');
 if(d.teams.length<2||d.teams.length>40||d.fixtures.length>80)throw Error('Límites de prueba: entre 2 y 40 clubes y hasta 80 partidos pendientes.');
 const ids=new Set();let gf=0,ga=0;
 for(const t of d.teams){if(!t||typeof t.id!=='string'||!/^[A-Za-z0-9_-]{1,32}$/.test(t.id)||typeof t.name!=='string'||ids.has(t.id))throw Error('ID de club no válido o repetido');ids.add(t.id);
  for(const k of ['pts','pj','w','d','l','gf','ga'])if(!Number.isInteger(t[k])||t[k]<0)throw Error('Estadística inválida de '+t.id+': '+k);
  if(t.w+t.d+t.l!==t.pj||t.pts!==3*t.w+t.d)throw Error('Puntos o PJ inconsistentes de '+t.id);gf+=t.gf;ga+=t.ga;
 }
 if(gf!==ga)throw Error('Balance de goles inconsistente: '+gf+'/'+ga);
 if(!Number.isInteger(d.meta.topN)||d.meta.topN<1||d.meta.topN>d.teams.length)throw Error('topN inválido');
 let seen=new Set(),counts=new Map([...ids].map(id=>[id,0]));
 for(const f of d.fixtures){if(!ids.has(f.home)||!ids.has(f.away)||f.home===f.away)throw Error('Encuentro con club inexistente');let key=f.home+'|'+f.away;if(seen.has(key))throw Error('Partido duplicado: '+key);seen.add(key);counts.set(f.home,counts.get(f.home)+1);counts.set(f.away,counts.get(f.away)+1)}
 if(d.meta.gamesPerTeam!=null){for(const t of d.teams)if(t.pj+counts.get(t.id)!==d.meta.gamesPerTeam)throw Error('Calendario incompleto para '+t.name)}
 return true;
}
function initialize(d,initialTeam){validate(d);data=clone(d);teamIndex=new Map(data.teams.map((t,i)=>[t.id,i]));team=(initialTeam&&teamIndex.has(initialTeam))?initialTeam:data.teams[0].id;
 picks=Array(data.fixtures.length).fill(null);probs=[];modelProbs=[];goalGrids=[];goalLambdas=[];data.fixtures.forEach(f=>{const m=forecastMatch(f);modelProbs.push(m.p);probs.push(m.p.slice());goalGrids.push(m.grids);goalLambdas.push([m.lh,m.la])});sim=null;tableMode='modal';lastRoute=0n;
 renderAll(true);
}
function factorialPMF(lambda,max=10){let a=[Math.exp(-lambda)];for(let k=1;k<=max;k++)a.push(a[k-1]*lambda/k);return a}
function forecastMatch(f){const a=data.teams[teamIndex.get(f.home)],b=data.teams[teamIndex.get(f.away)];const allG=data.teams.reduce((s,t)=>s+t.gf,0),allPJ=data.teams.reduce((s,t)=>s+t.pj,0),avg=allPJ?allG/allPJ:1.25;
 const alpha=8,rate=(g,pj)=>(g+alpha*avg)/(pj+alpha);
 let lh=Math.max(.24,Math.min(3.5,Math.sqrt(rate(a.gf,a.pj)*rate(b.ga,b.pj))*1.11));
 let la=Math.max(.24,Math.min(3.5,Math.sqrt(rate(b.gf,b.pj)*rate(a.ga,a.pj))*.92));
 const ph=factorialPMF(lh),pa=factorialPMF(la),grids=[[],[],[]],w=[0,0,0];
 for(let x=0;x<ph.length;x++)for(let y=0;y<pa.length;y++){
  const o=x>y?0:x===y?1:2,wt=ph[x]*pa[y];grids[o].push([x,y,wt]);w[o]+=wt;
 }
 const sum=w.reduce((a,b)=>a+b,0);return {p:w.map(x=>x/sum),grids,lh,la};
}
function scoreFromOutcome(o){return o===0?[1,0]:o===1?[0,0]:[0,1]}
function own(tid){return data.teams.find(t=>t.id===tid)}

/* Identidad de clubes: escudos publicados por SportScore. No se sustituyen estadísticas de la instantánea. */
const CLUB_BADGES = {"AGU": "https://img.thesports.com/football/team/3190d6d022fe9b36c65d83cf98e16d15.png", "ALI": "https://img.thesports.com/football/team/242d6977e9b86cba5cea704d996edbf8.png", "AME": "https://img.thesports.com/football/team/ed6ae7fa894cb5bdbccfd605d1d6ad04.png", "BUC": "https://img.thesports.com/football/team/70c92764e181ce7abe6176c411a93fe3.png", "CAL": "https://img.thesports.com/football/team/b997a2811a0caed43ff38b631a708420.png", "CHI": "https://img.thesports.com/football/team/1cd42bcb186830f2cffdeef6df5fd2b0.png", "CUC": "https://img.thesports.com/football/team/972c2e951d1ba7680faee53a342bd0a2.png", "DIM": "https://img.thesports.com/football/team/6eef3985d6a6d69a6e5374e27b13b35f.png", "FOR": "https://img.thesports.com/football/team/5a721f997fe18b1c151116a96b1b4ea8.png", "INT": "https://img.thesports.com/football/team/265454b5fee1950f8aa1173147c8c593.png", "JAG": "https://img.thesports.com/football/team/b7f3a068b301edd82ad4c56496f41063.png", "JUN": "https://img.thesports.com/football/team/fd3230c7fa4ad7bde28c640f2f32ca43.png", "LLA": "https://img.thesports.com/football/team/f83a93401d7a60595338bae0337d344c.png", "MIL": "https://img.thesports.com/football/team/88bf2a10fe7e8d3f9a21b73f3f77fcde.png", "NAL": "https://img.thesports.com/football/team/4ee24366d09a9239bb2c4207a5008111.png", "ONC": "https://img.thesports.com/football/team/b060f70150fe2b52fba8aa026a930c4e.png", "PAS": "https://img.thesports.com/football/team/9fbd48de1577477753873c539c3ab106.png", "PER": "https://img.thesports.com/football/team/2a016d670dd775e37ae908540843a444.png", "SFE": "https://img.thesports.com/football/team/5761c77ebe56b383931a6870372f5e46.png", "TOL": "https://img.thesports.com/football/team/40f17f08ff7bb44a641273044db78c64.png"};
/* Goleadores seleccionados, Liga BetPlay II 2026. Fuente: AS, consulta 5/11/2026. No son nóminas completas ni se usan para estimar probabilidades. */
const SCORERS_SNAPSHOT = {"AGU": [["Ricardo Márquez", 4], ["Andrés Mosquera", 2]], "ALI": [["Felipe Pardo", 3]], "AME": [["Yeison Guzmán", 10], ["Tilman Palacios", 2]], "BUC": [["Luciano Pons", 8], ["Enmerson Batalla", 8]], "CAL": [["Eduard Bello", 6], ["Nicolás Benedetti", 5]], "CHI": [["Santiago Mera", 2], ["Jhonier Alomía", 2]], "CUC": [["Jaime Peralta", 5], ["Léider Berdugo", 2]], "DIM": [["John Montaño", 5], ["Jeison Medina", 4]], "FOR": [["Richardson Rivas", 2], ["Sebastián Navarro", 2]], "INT": [["Diego Duarte", 5], ["Fabricio Sanguinetti", 4]], "JAG": [["Andrés Rentería", 6], ["Darwin López", 4]], "JUN": [["Guillermo Paiva", 4], ["Jesús Rivas", 3]], "LLA": [["Néider Ospina", 5], ["Francisco Meza", 3]], "MIL": [["Andrey Estupiñán", 6], ["Leonardo Castro", 5]], "NAL": [["Andrés Sarmiento", 7], ["Edwin Cardona", 6]], "ONC": [["Jefry Zapata", 6], ["Andrés Roa", 2]], "PAS": [["Enrique Serje", 2], ["Diego Chávez", 2]], "PER": [["Jhon Largacha", 3], ["Jordy Monroy", 3]], "SFE": [["Nahuel Bustos", 6], ["Franco Fagúndez", 6]], "TOL": [["Adrián Parra", 4], ["Jorge Hurtado", 3]]};
const PLAYERS_SOURCE = 'https://as.com/resultados/futbol/colombia_ii/2026/ranking/jugadores/goles/';
function clubMark(id,size='sm'){
 const name=own(id)?.name||String(id);
 const url=CLUB_BADGES[id];
 const initials=String(id).slice(0,3);
 if(!url)return `<span class="crest-wrap crest-${size}"><span class="crest-fallback" style="display:inline-flex">${h(initials)}</span></span>`;
 return `<span class="crest-wrap crest-${size}"><img class="crest-img" alt="Escudo de ${h(name)}" loading="lazy" referrerpolicy="no-referrer" src="${h(url)}" onerror="this.style.display='none';this.nextElementSibling.style.display='inline-flex'"><span class="crest-fallback">${h(initials)}</span></span>`;
}
function renderTeamAnalysis(){
 const t=own(team),base=baseRank(),rank=base.findIndex(x=>x.id===team)+1;
 const cutoff=base[data.meta.topN-1];const diff=t.pts-cutoff.pts;
 const games=data.fixtures.map((f,i)=>({f,i})).filter(x=>x.f.home===team||x.f.away===team);
 const badge=$('focus-crest');if(badge)badge.innerHTML=clubMark(team,'md');
 if($('focus-name'))$('focus-name').textContent=t.name;
 if($('focus-meta'))$('focus-meta').textContent=`${data.meta.name} · ${data.meta.season} · ${rank}º de ${base.length} equipos · ${t.pj} partidos disputados`;
 if($('focus-pts'))$('focus-pts').textContent=t.pts;
 if($('focus-sub'))$('focus-sub').textContent=`Máximo ${t.pts+games.length*3}`;
 const st=hardStatus(team),bound=baseBounds(team);
 const info=[
  ['Estado matemático',st.text],
  ['Respecto al 8.º',diff===0?'Mismos puntos':(diff>0?`+${diff}`:String(diff))+' puntos'],
  ['Posición posible, por puntos',bound?`${bound.best}º a ${bound.worst}º`:'Sin certificar'],
  ['Partidos por disputar',String(games.length)],
  ['Goles a favor / contra',`${t.gf} / ${t.ga}`],
  ['Diferencia de gol',(t.gf-t.ga>0?'+':'')+(t.gf-t.ga)]
 ];
 if($('team-analysis'))$('team-analysis').innerHTML=info.map(([name,v])=>`<div class="analysis-row"><span>${h(name)}</span><strong>${h(v)}</strong></div>`).join('');
 if($('team-analysis-note'))$('team-analysis-note').textContent=st.kind==='eliminado'?'La eliminación está demostrada por cotas de puntos; no depende de las probabilidades.':st.kind==='clasificado'?'Ya tiene clasificación matemática asegurada según cotas de puntos.':'Los enfrentamientos restantes de todos los clubes pueden cambiar la posición. Los desempates oficiales adicionales pueden intervenir.';
 if($('team-next'))$('team-next').innerHTML=games.length?games.map(({f,i})=>{
  const home=f.home===team,opp=home?f.away:f.home,p=probs[i];const win=home?p[0]:p[2],draw=p[1],lose=home?p[2]:p[0];
  const lbl=own(opp)?.name||opp;
  return `<div class="team-game"><div class="date">J${h(f.round)}<br>${h(f.date||'Pendiente')}</div>${clubMark(opp,'xs')}<div class="club">${h(lbl)}<div class="probline">${home?'Local':'Visitante'} · G ${pct(win)} · E ${pct(draw)} · P ${pct(lose)}</div></div><span class="chance">${pct(win)}</span></div>`;
 }).join(''):'<p class="hint">No quedan encuentros de esta fase.</p>';
 const players=SCORERS_SNAPSHOT[team];
 if($('team-players'))$('team-players').innerHTML=players?.length?players.map(([name,goals])=>`<div class="player-mini"><span class="player-avatar" aria-hidden="true">⚽</span><div style="flex:1;min-width:0"><div class="player-name">${h(name)}</div><div class="player-stat">Goles en Liga BetPlay II · consulta 05/11</div></div><div class="player-goals">${goals}<span>goles</span></div></div>`).join(''):'<p class="hint">No hay datos individuales verificados para este equipo en el subconjunto consultado.</p>';
 if($('player-source'))$('player-source').innerHTML=`Muestra de goleadores, no nómina completa. Fuente: <a href="${PLAYERS_SOURCE}" target="_blank" rel="noopener noreferrer">ranking de AS, 5 nov. 2026</a>. No se incorporan al modelo Poisson ni se actualizan automáticamente.`;
 if($('club-model'))$('club-model').textContent=`El pronóstico de ${t.name} se basa en goles a favor/en contra de los equipos y ventaja local. No utiliza todavía lesiones, alineaciones ni datos individuales. `+(sim?`Última simulación: ${fmt(sim.n)} temporadas; top ${data.meta.topN} = ${pct(sim.top[teamIndex.get(team)]/sim.n)} (estimación, no certeza).`:'Monte Carlo aún no ejecutado.');
}
function renderLeagueAnalysis(){
 const el=$('league-probabilities');if(!el)return;
 if(!sim){el.innerHTML='<p class="hint">El resumen probabilístico de los 20 equipos aparecerá tras la primera simulación.</p>';return}
 const rows=data.teams.map((t,i)=>({t,i,p:sim.top[i]/sim.n,exp:sim.pt[i]/sim.n})).sort((a,b)=>b.p-a.p||b.exp-a.exp);
 el.innerHTML=rows.map(({t,i,p,exp},idx)=>`<div class="analysis-row"><button type="button" data-global-team="${h(t.id)}">${clubMark(t.id,'xs')}<span class="team-label">${h(t.name)}</span></button><div style="min-width:77px;text-align:right"><strong>${pct(p)}</strong><div class="league-bar"><i style="width:${(p*100).toFixed(2)}%"></i></div><small>${exp.toFixed(1)} pts prom.</small></div></div>`).join('');
}

function outcomeOf(p){return p?.o??null}
function standings(selection){const ts=data.teams.map(t=>({...t}));const ix=new Map(ts.map((t,i)=>[t.id,i]));
 for(let k=0;k<data.fixtures.length;k++){const p=selection[k];if(!p)continue;let f=data.fixtures[k],a=ts[ix.get(f.home)],b=ts[ix.get(f.away)];let [hg,ag]=p.score||scoreFromOutcome(p.o);
 a.pj++;b.pj++;a.gf+=hg;a.ga+=ag;b.gf+=ag;b.ga+=hg;
 if(hg>ag){a.w++;a.pts+=3;b.l++}else if(hg===ag){a.d++;b.d++;a.pts++;b.pts++}else{b.w++;b.pts+=3;a.l++}
 }
 const remaining=new Map(data.teams.map(t=>[t.id,data.fixtures.reduce((n,f,i)=>n+(!selection[i]&&(t.id===f.home||t.id===f.away)?1:0),0)]));
 ts.forEach(t=>{t.dg=t.gf-t.ga;t.max=t.pts+3*remaining.get(t.id)});
 ts.sort((a,b)=>b.pts-a.pts||b.dg-a.dg||b.gf-a.gf||a.name.localeCompare(b.name,'es'));
 return ts;
}
function baseRank(){return standings([])}
function hasAnyPicks(){return picks.some(Boolean)}
function baseBounds(tid){return data.bounds?.[tid]||null}
function hardStatus(tid){const t=own(tid),top=data.meta.topN;
 const bound=baseBounds(tid);
 if(bound){if(bound.best>top)return {kind:'eliminado',text:'Eliminado',details:`Incluso con todos los desempates de puntos a su favor, el mejor puesto posible es ${bound.best}º. Ninguna combinación de los encuentros pendientes permite entrar al top ${top}.`};if(bound.worst<=top)return {kind:'clasificado',text:'Clasificado',details:`En el escenario matemático más adverso, incluyendo empates de puntos tratados en contra, no baja del puesto ${bound.worst}º.`};return {kind:'disputa',text:'En disputa',details:`Cotas por puntos: entre ${bound.best}º (empates favorables) y ${bound.worst}º (empates adversos). La clasificación depende de resultados de otros clubes.`}}
 const ownRemaining=data.fixtures.filter(f=>f.home===tid||f.away===tid).length;const max=t.pts+ownRemaining*3;
 const definitelyAhead=data.teams.filter(v=>v.id!==tid&&v.pts>max).length;
 if(definitelyAhead>=top)return {kind:'eliminado',text:'Eliminado',details:`Al menos ${definitelyAhead} equipos tienen más puntos que su máximo de ${max}.`};
 return {kind:'desconocido',text:'Sin certificar',details:'Para certificar matemáticamente mejores y peores puestos de la liga importada, es necesario ejecutar el optimizador del backend.'};
}
function probabilities(i){return probs[i]}
function renderSelectors(){let select=$('team');const previous=select.value;select.innerHTML=data.teams.slice().sort((a,b)=>a.name.localeCompare(b.name,'es')).map(t=>`<option value="${h(t.id)}">${h(t.name)}</option>`).join('');select.value=team;
 $('competition-info').textContent=`${data.meta.name} · ${data.meta.season} · Corte: ${data.meta.asOf||'no informado'} · ${data.meta.status||'datos importados'}.`;
 $('recent-finals').innerHTML=(data.recentFinals||[]).map(f=>`<span>Final: ${h(own(f.home)?.name||f.home)} ${f.homeGoals}–${f.awayGoals} ${h(own(f.away)?.name||f.away)}</span>`).join('')||'<span>Sin resultados recientes en esta muestra.</span>';
 $('update-pill').textContent=data.meta.status==='DATOS SINTÉTICOS'?'⚠ Liga de prueba':'● Corte de liga + consulta de marcadores';
 $('filter-round').innerHTML='<option value="all">Todas</option>'+[...new Set(data.fixtures.map(f=>f.round))].sort().map(r=>`<option value="${h(r)}">${h(r)}</option>`).join('');
}
function renderFacts(){const t=own(team),current=baseRank().findIndex(x=>x.id===team)+1,b=baseBounds(team),remaining=data.fixtures.filter(f=>f.home===team||f.away===team).length,st=hardStatus(team);
 $('m-current').textContent=current+'º';$('m-points').textContent=t.pts+' / '+(t.pts+remaining*3);
 $('m-points-sub').textContent=remaining+' partidos restantes';
 $('m-best').textContent=b?b.best+'º':'—';$('m-worst').textContent=b?b.worst+'º':'—';$('m-status').textContent=st.text;$('m-status').className=st.kind==='eliminado'?'red':st.kind==='clasificado'?'green':'yellow';$('m-status-sub').textContent='Clasifican '+data.meta.topN;
 $('m-chance').textContent=sim?pct(sim.top[teamIndex.get(team)]/sim.n):'—';$('m-chance-sub').textContent=sim?`Modelo experimental, ${fmt(sim.n)} muestras`:'Sin simulación';
 const picked=picks.filter(Boolean).length;const stBase=standings(picks),selected=stBase.find(v=>v.id===team),rank=stBase.findIndex(v=>v.id===team)+1;
 let comment=st.details;
 if(picked)comment+=` Tienes ${picked} partidos fijados en el editor; en la tabla parcial, ${h(t.name)} ocupa el puesto ${rank}º con ${selected.pts} puntos y puede llegar a ${selected.max}. Esto NO cambia el pronóstico libre.`;
 else comment+=` Tiene ${remaining} partidos restantes y un máximo de ${t.pts+3*remaining} puntos.`;
 $('reason').innerHTML=`<b>${h(st.text)}.</b> ${comment}<p class="hint" style="margin:9px 0 0">La posición exacta en caso de empates en puntos puede requerir goles visitantes y criterios adicionales de Dimayor.</p>`;
 $('reason-state').textContent=b?'Optimización MILP':'Cota básica';
 renderSimForTeam();renderTeamAnalysis();renderLeagueAnalysis();
}
function renderSimForTeam(){const el=$('chart');if(!sim){el.innerHTML='<p class="hint">Ninguna simulación ejecutada todavía.</p>';$('expected-points').textContent='—';$('observed-range').textContent='—';$('sim-status').textContent='Sin simulación';$('sim-description').textContent='La distribución aparecerá tras ejecutar Monte Carlo. El modo libre ignora las selecciones del editor.';return}
 const j=teamIndex.get(team),dist=sim.dist[j],n=sim.n;el.innerHTML=dist.map((v,i)=>`<div class="chart-row"><span>${i+1}º</span><div class="bar"><div style="width:${(v/n*100).toFixed(4)}%"></div></div><span class="value">${pct(v/n)}</span></div>`).join('');
 $('expected-points').textContent=(sim.pt[j]/n).toFixed(2);$('observed-range').textContent=(dist.findIndex(x=>x>0)+1)+'º–'+(dist.length-dist.slice().reverse().findIndex(x=>x>0))+'º';
 $('sim-status').textContent=(sim.conditional?'Condicionado':'Libre')+' · '+fmt(n)+' escenarios';
 const pTop=sim.top[j]/n, margin=1.96*Math.sqrt(pTop*(1-pTop)/n);
 $('sim-description').textContent=`Entre ${fmt(n)} muestras, ${h(own(team).name)} obtuvo top ${data.meta.topN} en ${pct(pTop)} (incertidumbre de muestreo aprox. ±${pct(margin)} al 95 %, sin incluir el error del modelo), y lideró la fase en ${pct(sim.first[j]/n)}. Semilla ${sim.seed}. No es la probabilidad de ganar el campeonato.`;
}
function modalPick(i){
 const live=liveOverlay.get(data.fixtures[i].id);
 if(live){const [h,a]=live.score,minute=live.minute??45,frac=Math.max(0,Math.min(1,(90-minute)/90)),[lh,la]=goalLambdas[i];
  const hm=Math.max(0,Math.floor(lh*frac)),am=Math.max(0,Math.floor(la*frac)),score=[h+hm,a+am];
  return {o:score[0]>score[1]?0:score[0]===score[1]?1:2,score};
 }
 const ps=probs[i],o=ps.indexOf(Math.max(...ps));
 const grids=goalGrids[i][o];const c=grids.reduce((best,x)=>x[2]>best[2]?x:best,grids[0]);
 return {o,score:[c[0],c[1]]};
}
function modalTable(){return standings(data.fixtures.map((_,i)=>modalPick(i)))}
function expectedTable(){
 if(!sim)return modalTable();
 const n=sim.n,rows=data.teams.map((t,j)=>({...t,
   pj:data.meta.gamesPerTeam??t.pj+data.fixtures.filter(f=>f.home===t.id||f.away===t.id).length,
   w:sim.w[j]/n,d:sim.d[j]/n,l:sim.l[j]/n,
   gf:sim.gf[j]/n,ga:sim.ga[j]/n,pts:sim.pt[j]/n,
   max:null
 }));
 rows.forEach(t=>t.dg=t.gf-t.ga);
 rows.sort((a,b)=>b.pts-a.pts||b.dg-a.dg||b.gf-a.gf||a.name.localeCompare(b.name,'es'));
 return rows;
}
function renderTable(){
 let arr,desc;
 const k=picks.filter(Boolean).length;
 if(tableMode==='base'){arr=standings([]);desc=`Tabla de resultados finales incorporados: entre ${Math.min(...arr.map(t=>t.pj))} y ${Math.max(...arr.map(t=>t.pj))} PJ por equipo; no incluye los encuentros que siguen en juego.`;}
 else if(tableMode==='scenario'){arr=standings(picks);desc=k?`Escenario parcial: ${k} encuentros fijados; los demás todavía NO se han simulado en esta tabla.`:'Sin partidos fijados, el escenario equivale a la tabla actual. Elige Pronóstico 19 PJ para proyectar todos los encuentros.';}
 else if(tableMode==='expected'){arr=expectedTable();desc=sim?`Tabla de expectativas tras ${fmt(sim.n)} temporadas Monte Carlo conjuntas. Todos completan ${data.meta.gamesPerTeam} PJ; puntos y goles son promedios, no una clasificación realizable única.`:'Todavía no se ha ejecutado Monte Carlo: mostrando la proyección modal completa provisional.';}
 else{arr=modalTable();desc=`Tabla PRONOSTICADA completa: todos los clubes terminan con ${data.meta.gamesPerTeam} PJ. Cada partido tiene un marcador modal compatible; es una ruta coherente, no una certeza.`;}
 $('table-status').textContent=desc;
 const basePlayed=Math.min(...data.teams.map(t=>t.pj));
 const baseModeButton=document.querySelector('[data-table-mode="base"]');
 if(baseModeButton)baseModeButton.textContent='Tabla real ('+basePlayed+'+ PJ)';
 for(const button of document.querySelectorAll('[data-table-mode="modal"],[data-table-mode="expected"]'))button.textContent=button.dataset.tableMode==='modal'?'Pronóstico completo ('+data.meta.gamesPerTeam+' PJ)':'Promedio Monte Carlo ('+data.meta.gamesPerTeam+' PJ)';
 document.querySelectorAll('[data-table-mode]').forEach(b=>{const on=b.dataset.tableMode===tableMode;b.classList.toggle('primary',on);b.setAttribute('aria-pressed',String(on))});
 const num=(v)=>Number.isInteger(v)?String(v):Number(v).toFixed(1);
 $('table-body').innerHTML=arr.map((t,i)=>`<tr class="${i<data.meta.topN?'cut':'notcut'} ${t.id===team?'selected':''}"><td class="num">${i+1}</td><td class="name"><button class="table-row-btn" data-team="${h(t.id)}">${clubMark(t.id,'xs')}${h(t.name)}</button></td><td class="num">${num(t.pj)}</td><td class="num">${num(t.w)}</td><td class="num">${num(t.d)}</td><td class="num">${num(t.l)}</td><td class="num">${num(t.gf)}</td><td class="num">${num(t.ga)}</td><td class="num">${t.dg>0?'+':''}${num(t.dg)}</td><td class="num"><b>${num(t.pts)}</b></td><td class="num">${t.max==null?'—':num(t.max)}</td></tr>`).join('');
}
function renderFixtures(){const onlyTeam=$('only-team').checked,onlyUnfixed=$('only-unfixed').checked,rd=$('filter-round').value;let count=0;
 $('fixtures').innerHTML=data.fixtures.map((f,i)=>{
  if((onlyTeam&&!(f.home===team||f.away===team))||(onlyUnfixed&&picks[i])||(rd!=='all'&&String(f.round)!==rd))return '';
  count++;const p=picks[i],prob=probs[i],fixed=p!==null;
  const [hg,ag]=p?.score??['',''];const home=own(f.home).name,away=own(f.away).name;const live=liveOverlay.get(f.id);const liveInfo=live?`<span class="live-label">● EN JUEGO ${live.score[0]}–${live.score[1]} (${live.minute==null?'minuto no disponible':live.minute+' min'})</span>`:'';
  return `<div class="fixture ${fixed?'sel':''}" data-fixture="${i}"><div class="round">Jornada ${h(f.round)}<br>${h(f.date||'Por confirmar')} ${h(f.time||'')}</div><div class="teams"><span class="fixture-team">${clubMark(f.home,'sm')}${h(home)}</span><small>contra</small><span class="fixture-team">${clubMark(f.away,'sm')}${h(away)}</span>${liveInfo}</div><div class="prob"><div class="probs"><span>1 ${pct(prob[0])}</span><span>X ${pct(prob[1])}</span><span>2 ${pct(prob[2])}</span></div><span>${p?.score?'Marcador exacto fijado':fixed?'Resultado 1X2 fijado':'Modelo Poisson · no verificado'}</span></div><div class="actions"><div class="outcomes"><button data-i="${i}" data-o="0" class="${p?.o===0?'active':''}">1</button><button data-i="${i}" data-o="1" class="${p?.o===1?'active':''}">X</button><button data-i="${i}" data-o="2" class="${p?.o===2?'active':''}">2</button><button data-i="${i}" data-o="clear" class="clear">↺</button></div><div class="score-control"><input type="number" min="0" max="15" data-score-i="${i}" data-side="h" value="${hg}" aria-label="Goles de ${h(home)}" placeholder="G"><span>–</span><input type="number" min="0" max="15" data-score-i="${i}" data-side="a" value="${ag}" aria-label="Goles de ${h(away)}" placeholder="G"><span class="hint">exacto</span></div></div><details class="advanced"><summary>Ajustar P(1/X/2) · ${h(f.note||'modelo estimado')}</summary><div class="triplet"><label>Local %<input type="number" min="0" max="100" step="0.1" data-pr="${i}" data-k="0" value="${(prob[0]*100).toFixed(1)}"></label><label>Empate %<input type="number" min="0" max="100" step="0.1" data-pr="${i}" data-k="1" value="${(prob[1]*100).toFixed(1)}"></label><label>Visita %<input type="number" min="0" max="100" step="0.1" data-pr="${i}" data-k="2" value="${(prob[2]*100).toFixed(1)}"></label><button class="btn small" data-save-prob="${i}">Aplicar</button></div></details></div>`;
 }).join('')||'<p class="hint">Ningún encuentro cumple el filtro.</p>';
 $('preview-remaining').textContent=`${count} visibles de ${data.fixtures.length} pendientes.`;
}
function renderUniverse(){const free=picks.filter(p=>!p).length,total=3n**BigInt(data.fixtures.length),comp=3n**BigInt(free);
 $('total-universe').textContent=fmt(total);$('compatible-universe').textContent=fmt(comp);
 $('universe-explanation').textContent=`Fijados: ${data.fixtures.length-free} de ${data.fixtures.length}. Quedan ${free} partidos libres, por tanto 3^${free} calendarios compatibles (sin detallar marcadores exactos).`;
 $('picks-total').textContent=`${data.fixtures.length-free} de ${data.fixtures.length} resultados fijados`;
 renderPoints();
}
function renderPoints(){let t=own(team),m=new Map([[t.pts,1]]),count=new Map([[t.pts,1n]]);let onlyFix=$('condition').checked;
 data.fixtures.forEach((f,i)=>{if(f.home!==team&&f.away!==team)return;const isHome=f.home===team,choice=onlyFix?picks[i]:null;
 const ps=choice?[0,1,2].map(o=>o===choice.o?1:0):probs[i];const next=new Map();
 for(const [points,weight] of m){for(let o=0;o<3;o++){const add=o===1?1:(o===0?isHome:!isHome)?3:0,p=points+add;next.set(p,(next.get(p)||0)+weight*ps[o]);}}
 // Need do not mutate source count while iterating; use separate nextCounts
 const nextCounts=new Map();for(const [points,c] of count)for(let o=0;o<3;o++){if(choice&&o!==choice.o)continue;let add=o===1?1:(o===0?isHome:!isHome)?3:0,p=points+add;nextCounts.set(p,(nextCounts.get(p)||0n)+c)}
 m=next;count=nextCounts;
 });
 const rows=[...m.entries()].sort((a,b)=>a[0]-b[0]);const sum=rows.reduce((s,a)=>s+a[1],0);
 $('points-distribution').innerHTML=rows.map(([pts,prob])=>`<div class="stat-row"><span>${pts} puntos</span><span><b>${pct(prob/sum)}</b> <small class="muted">(${fmt(count.get(pts)||0n)} rutas propias)</small></span></div>`).join('');
 $('points-note').textContent=onlyFix?'Distribución condicionada por las selecciones del editor, para los partidos del equipo.':'Distribución sin condiciones del editor. Solo modela puntos del equipo, no posiciones conjuntas.';
}
function renderAudit(){const n=data.fixtures.length,counts=new Map(data.teams.map(t=>[t.id,0]));data.fixtures.forEach(f=>{counts.set(f.home,counts.get(f.home)+1);counts.set(f.away,counts.get(f.away)+1)});
 const good=data.teams.filter(t=>!data.meta.gamesPerTeam||t.pj+counts.get(t.id)===data.meta.gamesPerTeam).length;
 const gf=data.teams.reduce((s,t)=>s+t.gf,0),ga=data.teams.reduce((s,t)=>s+t.ga,0);
 $('audit-finals').textContent=String(data.recentFinals?.length||0);$('audit-fixtures').textContent=n; $('audit-teams').textContent=good+'/'+data.teams.length;$('audit-goals').textContent=gf+' / '+ga;
 $('data-meta').textContent=`${data.meta.name} ${data.meta.season}. Corte declarado: ${data.meta.asOf}. ${data.meta.sourceNote||'Requiere verificar procedencia de datos importados.'}`;renderFeedState();
 $('source-links').innerHTML=(data.sources||[]).map(x=>`<p style="margin:6px 0"><a href="${h(x.url)}" target="_blank" rel="noreferrer">${h(x.label)}</a></p>`).join('')||'<span class="hint">Liga sintética o importada sin fuentes declaradas.</span>';
}
function renderAll(resetFilter=false){if(resetFilter){renderSelectors();$('only-team').checked=window.matchMedia('(max-width:800px)').matches;$('only-unfixed').checked=false;$('condition').checked=false;$('filter-round').value='all'}else{$('team').value=team}
 renderFacts();renderTable();renderFixtures();renderUniverse();renderAudit();}
function choose(i,o){if(o==='clear'){picks[i]=null}else{const a=Number(o);if(![0,1,2].includes(a))return;picks[i]={o:a,score:null}};
 if($('condition').checked)sim=null;renderAll();}
function setScore(i,homeGoals,awayGoals){if(!Number.isInteger(homeGoals)||!Number.isInteger(awayGoals)||homeGoals<0||awayGoals<0||homeGoals>15||awayGoals>15)throw Error('Marcador: ingresa goles entre 0 y 15 en ambos campos.');const o=homeGoals>awayGoals?0:homeGoals===awayGoals?1:2;picks[i]={o,score:[homeGoals,awayGoals]};if($('condition').checked)sim=null;renderAll();}
function setPreset(name){const n=data.fixtures.length,modal=()=>data.fixtures.map((_,i)=>({o:probs[i].indexOf(Math.max(...probs[i])),score:null}));
 if(name==='clear'){picks=Array(n).fill(null)}
 else if(name==='draw'){picks=Array.from({length:n},()=>({o:1,score:null}))}
 else if(name==='modal'){picks=modal()}
 else if(name==='favorable'||name==='adverse'){picks=modal();data.fixtures.forEach((f,i)=>{if(f.home===team||f.away===team)picks[i]={o:name==='favorable'?(f.home===team?0:2):(f.home===team?2:0),score:null}})}
 else if(name==='best'||name==='worst'){
  let r=baseBounds(team);if(!r){$('preset-description').textContent='La liga importada no trae certificados. Se cargó una ruta ilustrativa.';setPreset(name==='best'?'favorable':'adverse');return}
  const route=name==='best'?r.best_route:r.worst_route;picks=route.map(o=>({o,score:null}));
 }
 $('preset-description').textContent=({draw:'Todos los partidos hipotéticos terminan 0–0 en la previsualización; el modelo de goles sigue siendo probabilístico.',modal:'Se eligió el resultado 1X2 individual más probable de cada partido. No es un certificado de la posición final.',favorable:'Todos los partidos del club seleccionado terminan en victoria, los otros siguen resultados modales. Ruta ilustrativa, no necesariamente óptima.',adverse:'El club seleccionado pierde todos sus encuentros, los otros siguen resultados modales. Ruta ilustrativa, no necesariamente peor posición.',best:'Ruta factible calculada por programación lineal para minimizar rivales estrictamente por delante en puntos (empates favorables).',worst:'Ruta factible calculada por programación lineal para maximizar rivales por delante o empatados en puntos (empates adversos).',clear:'No hay partidos condicionados. Vuelve el espacio de escenarios completo.'})[name]||'';
 if($('condition').checked)sim=null;renderAll();}
function encodeRoute(){let v=0n;for(const p of picks){if(!p)return null;v=v*3n+BigInt(p.o)}return v}
function loadRoute(v){const total=3n**BigInt(data.fixtures.length);if(v<0n||v>=total)throw Error('El índice debe estar entre 0 y 3^N−1.');let a=Array(data.fixtures.length).fill(0);for(let i=a.length-1;i>=0;i--){a[i]=Number(v%3n);v/=3n}picks=a.map(o=>({o,score:null}));if($('condition').checked)sim=null;renderAll();$('route-hint').textContent='Ruta reproducible cargada: los '+a.length+' encuentros están definidos en el editor.';}
function uniformRandomIndex(max){const bits=max.toString(2).length,bytes=Math.ceil(bits/8);while(true){const arr=new Uint8Array(bytes);if(globalThis.crypto?.getRandomValues)crypto.getRandomValues(arr);else arr.forEach((_,i)=>{arr[i]=Math.floor(Math.random()*256)});let v=0n;for(const b of arr)v=v*256n+BigInt(b);if(v<max)return v}}
function rng(seed){let x=(seed>>>0)||0x6d2b79f5;return ()=>{x+=0x6d2b79f5;let t=x;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296}}
function sampleScore(i,o,rnd){const cells=goalGrids[i][o],weight=cells.reduce((s,v)=>s+v[2],0);let u=rnd()*weight;for(const c of cells){u-=c[2];if(u<=0)return [c[0],c[1]]}const c=cells.at(-1);return [c[0],c[1]]}
function poissonSample(lambda,rnd){const cutoff=Math.exp(-Math.min(12,lambda));let p=1,k=0;do{k++;p*=rnd()}while(p>cutoff&&k<50);return k-1}
function clearSimulation(){sim=null;renderFacts();$('progress-text').textContent='Parámetros modificados. Ejecuta nuevamente la simulación.';$('progress-bar').style.width='0'}
async function runSimulation(nOverride=null){if(busy)return;const n=Number.isInteger(nOverride)?nOverride:Number($('samples').value),conditioned=$('condition').checked;let seedText=$('seed').value.trim(),seed;
 if(seedText){if(!/^\d{1,10}$/.test(seedText)){alert('Semilla: escribe un entero positivo de hasta 10 dígitos.');return}seed=Number(seedText)>>>0}else{seed=Math.floor(Math.random()*4294967296)>>>0}
 let rnd=rng(seed),N=data.teams.length,F=data.fixtures.length,dist=Array.from({length:N},()=>Array(N).fill(0)),top=Array(N).fill(0),first=Array(N).fill(0),pt=Array(N).fill(0),gf=Array(N).fill(0),ga=Array(N).fill(0),w=Array(N).fill(0),d=Array(N).fill(0),l=Array(N).fill(0),base=data.teams;busy=true;$('run-sim').disabled=true;$('run-sim').textContent='Calculando...';$('progress-bar').style.width='0';
 const idx=teamIndex;
 for(let iteration=0;iteration<n;iteration++){
  const standingsRun=base.map(t=>({id:t.id,name:t.name,pts:t.pts,gf:t.gf,ga:t.ga,w:t.w,d:t.d,l:t.l}));
  for(let fi=0;fi<F;fi++){
   const f=data.fixtures[fi],preset=conditioned?picks[fi]:null,p=probs[fi];
   let score;
   if(preset?.score)score=preset.score;
   else if(preset)score=sampleScore(fi,preset.o,rnd);
   else if(liveOverlay.has(f.id)){
      const live=liveOverlay.get(f.id),[lh,la]=goalLambdas[fi],remaining=Math.max(0,Math.min(1,(90-(live.minute??45))/90));
      score=[live.score[0]+poissonSample(lh*remaining,rnd),live.score[1]+poissonSample(la*remaining,rnd)];
   }else{const r=rnd(),o=r<p[0]?0:r<p[0]+p[1]?1:2;score=sampleScore(fi,o,rnd)}
   const [hg,ag]=score;
   let a=standingsRun[idx.get(f.home)],b=standingsRun[idx.get(f.away)];a.gf+=hg;a.ga+=ag;b.gf+=ag;b.ga+=hg;
   if(hg>ag){a.pts+=3;a.w++;b.l++}else if(hg<ag){b.pts+=3;b.w++;a.l++}else{a.pts++;b.pts++;a.d++;b.d++}
  }
  standingsRun.sort((a,b)=>b.pts-a.pts||(b.gf-b.ga)-(a.gf-a.ga)||b.gf-a.gf||a.name.localeCompare(b.name,'es'));
  for(let pos=0;pos<N;pos++){let t=standingsRun[pos],j=idx.get(t.id);dist[j][pos]++;pt[j]+=t.pts;gf[j]+=t.gf;ga[j]+=t.ga;w[j]+=t.w;d[j]+=t.d;l[j]+=t.l;if(pos<data.meta.topN)top[j]++;if(pos===0)first[j]++}
  if((iteration+1)%250===0){$('progress-text').textContent=`Procesadas ${fmt(iteration+1)} de ${fmt(n)} temporadas (${conditioned?'condicionadas':'libres'}).`;$('progress-bar').style.width=((iteration+1)/n*100).toFixed(1)+'%';await new Promise(r=>setTimeout(r,0))}
 }
 sim={n,seed,conditional:conditioned,liveCount:liveOverlay.size,dist,top,first,pt,gf,ga,w,d,l};busy=false;$('run-sim').disabled=false;$('run-sim').textContent='▶ Repetir simulación';$('progress-bar').style.width='100%';
 $('progress-text').textContent=`${fmt(n)} temporadas conjuntas, todos los ${F} encuentros pendientes, ${liveOverlay.size} en curso. ${conditioned?'Se respetaron tus resultados fijados.':'Sin imponer resultados del editor.'} Semilla ${seed}.`;
 renderFacts();renderTable();
}
function normalizeManual(i,values){if(values.some(v=>!Number.isFinite(v)||v<0||v>100))throw Error('Probabilidades deben estar entre 0 y 100.');const total=values.reduce((s,v)=>s+v,0);if(total<1)throw Error('La suma de probabilidades debe ser positiva.');probs[i]=values.map(v=>v/total);clearSimulation();renderFixtures();renderUniverse();renderTable()}
function saveExport(){const payload={meta:data.meta,selectedTeam:team,model:'poisson-experimental',fixtures:data.fixtures.map((f,i)=>({...f,selectedResult:picks[i],probabilities:probs[i]})),exportedAt:new Date().toISOString()};let blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});let url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='matchlab-escenario-'+data.meta.season+'.json';document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500)}
function switchLeague(v){liveOverlay=new Map();if(v==='demo')initialize(DEMO,'A');else initialize(SNAPSHOT,'DIM');renderFeedState()}
function attachEvents(){
 $('league').addEventListener('change',e=>switchLeague(e.target.value));
 $('team').addEventListener('change',e=>{team=e.target.value;renderAll();});
 $('condition').addEventListener('change',()=>{clearSimulation();renderUniverse()});
 $('run-sim').addEventListener('click',runSimulation);
 document.querySelectorAll('[data-table-mode]').forEach(b=>b.addEventListener('click',()=>{tableMode=b.dataset.tableMode;renderTable()}));
 $('only-team').addEventListener('change',renderFixtures);$('only-unfixed').addEventListener('change',renderFixtures);$('filter-round').addEventListener('change',renderFixtures);
 $('clear-picks').addEventListener('click',()=>setPreset('clear'));
 document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>setPreset(b.dataset.preset)));
 $('table-body').addEventListener('click',e=>{const b=e.target.closest('[data-team]');if(b){team=b.dataset.team;renderAll();document.querySelector('#panorama').scrollIntoView({behavior:'smooth'})}});
 $('league-probabilities').addEventListener('click',e=>{const b=e.target.closest('[data-global-team]');if(b){team=b.dataset.globalTeam;renderAll();document.querySelector('#panorama').scrollIntoView({behavior:'smooth'})}});
 $('fixtures').addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  if(b.dataset.o!=null){choose(Number(b.dataset.i),b.dataset.o);return}
  if(b.dataset.saveProb!=null){const i=Number(b.dataset.saveProb),element=b.closest('.fixture'),arr=[0,1,2].map(k=>Number(element.querySelector(`[data-pr="${i}"][data-k="${k}"]`).value));try{normalizeManual(i,arr)}catch(er){alert(er.message)}return}
 });
 $('fixtures').addEventListener('change',e=>{if(e.target.dataset.scoreI!=null){const i=Number(e.target.dataset.scoreI),card=e.target.closest('.fixture'),h=card.querySelector(`[data-score-i="${i}"][data-side="h"]`).value,a=card.querySelector(`[data-score-i="${i}"][data-side="a"]`).value;
   if(h===''&&a===''){return}if(h===''||a===''){return}try{setScore(i,Number(h),Number(a))}catch(er){alert(er.message)}
 }});
 $('load-route').addEventListener('click',()=>{try{const s=$('route-index').value.trim();if(!/^\d+$/.test(s))throw Error('Identificador no válido');loadRoute(BigInt(s))}catch(e){$('route-hint').textContent=e.message}});
 $('prev-route').addEventListener('click',()=>{try{let s=BigInt($('route-index').value||'0');s=s>0n?s-1n:0n;$('route-index').value=s.toString();loadRoute(s)}catch(e){$('route-hint').textContent=e.message}});
 $('next-route').addEventListener('click',()=>{try{let s=BigInt($('route-index').value||'0');s=s+1n;let top=3n**BigInt(data.fixtures.length)-1n;if(s>top)s=top;$('route-index').value=s.toString();loadRoute(s)}catch(e){$('route-hint').textContent=e.message}});
 $('random-route').addEventListener('click',()=>{let idx=uniformRandomIndex(3n**BigInt(data.fixtures.length));$('route-index').value=idx.toString();loadRoute(idx)});
 $('reset-probs').addEventListener('click',()=>{probs=modelProbs.map(x=>x.slice());clearSimulation();renderFixtures();renderUniverse()});
 $('demo-button').addEventListener('click',()=>{$('league').value='demo';switchLeague('demo')});
 $('certify-fixed').addEventListener('click',async ()=>{
  const target=$('certify-status');target.textContent='Consultando solucionador...';
  try{
   const fixed={};picks.forEach((p,i)=>{if(p)fixed[data.fixtures[i].id]=p.o});
   const r=await fetch('/api/bounds',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({team_id:team,fixed})});
   if(!r.ok)throw Error('El backend no está conectado o rechazó la solicitud ('+r.status+').');
   const x=await r.json();target.textContent=`Con los resultados fijados: puesto óptimo por puntos ${x.best}º a ${x.worst}º; ${Object.keys(fixed).length} encuentros condicionados. Desempates oficiales adicionales pendientes.`;
  }catch(e){target.textContent='No se pudo certificar en línea: '+e.message+' La versión HTML autónoma solo muestra cotas iniciales.'}
 });
 $('export').addEventListener('click',saveExport);
 $('import').addEventListener('change',async e=>{const file=e.target.files?.[0];if(!file)return;try{if(file.size>1e6)throw Error('El archivo supera 1 MB');const json=JSON.parse(await file.text());validate(json);initialize(json,json.teams[0].id);$('league').innerHTML+='<option value="imported">Liga importada · '+h(json.meta.name||'Sin nombre')+'</option>';$('league').value='imported';$('competition-info').textContent+=' · Importación local sin verificación de fuente.';}catch(err){alert('No se pudo importar: '+err.message)}finally{e.target.value=''}});
}

/* CONSULTA AUTOMÁTICA DE MARCADORES. Solo los finales confirmados entran a la tabla base. */
const PROVIDER='https://sportscore.com/api/v1/fixtures/';
const NAME_ALIASES={
 'atletico nacional medellin':'NAL','atletico nacional':'NAL','america de cali':'AME','deportivo cali':'CAL',
 'mill onarios':'MIL','millonarios':'MIL','atletico buc aramanga':'BUC','atletico bucaramanga':'BUC',
 'independiente santa fe':'SFE','santa fe':'SFE','dep independiente medellin':'DIM','independiente medellin':'DIM',
 'aguilas doradas':'AGU','deportiva once caldas':'ONC','once caldas':'ONC','deportes tolima':'TOL','deportivo tolima':'TOL',
 'cucuta deportivo':'CUC','cucuta':'CUC','internacional de bogota':'INT','internacional bogota':'INT',
 'llaneros fc':'LLA','llaneros':'LLA','alianza futbol club':'ALI','alianza fc':'ALI',
 'deportivo pereira':'PER','atletico junior barranquilla':'JUN','junior':'JUN','boyaca chico':'CHI',
 'deportivo pasto':'PAS','jaguares de cordoba':'JAG','fortaleza f c':'FOR','fortaleza fc':'FOR'};
function normalizeName(s){return String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function mapTeam(s){return NAME_ALIASES[normalizeName(s)]||null}
function providerMinute(row){const s=String(row.status_text||'').toLowerCase(),m=s.match(/(\d{1,3})\s*['’]?/);if(m)return Math.max(0,Math.min(90,+m[1]));if(/half.?time/.test(s))return 45;
 const kickoff=new Date(row.time);if(Number.isFinite(+kickoff))return Math.max(0,Math.min(90,Math.round((Date.now()-kickoff.getTime())/60000)));
 return null;
}
function eligibleDate(f,dateUTC){if(!dateUTC)return false;
 const actual=new Date(dateUTC+'T00:00:00Z');if(!Number.isFinite(+actual))return false;
 // Prevent accidental matching to earlier seasons or another stage.
 if(f.date){const expected=new Date(f.date+'T00:00:00Z');return Math.abs(actual-expected)<=2*86400000}
 return actual>=new Date('2026-11-10T00:00:00Z')&&actual<=new Date('2026-11-20T23:59:59Z');
}
function normalizeProviderRows(payload,dateUTC){
 if(!payload||!Array.isArray(payload.matches))throw Error('Respuesta del proveedor sin lista de partidos');
 const out=[];
 for(const m of payload.matches){const home=mapTeam(m.home),away=mapTeam(m.away);if(!home||!away||home===away)continue;
  const status=String(m.status||'').toLowerCase(),hg=Number(m.home_score),ag=Number(m.away_score);
  const validScores=m.home_score!=null&&m.away_score!=null&&Number.isInteger(hg)&&Number.isInteger(ag)&&hg>=0&&ag>=0&&hg<=20&&ag<=20;
  out.push({home,away,status,score:validScores?[hg,ag]:null,minute:providerMinute(m),dateUTC:dateUTC||null,source:'SportScore',url:m.url||null});
 }
 return out;
}
function statusIsFinal(s){return ['finished','final','ft','ended','completed'].includes(String(s).toLowerCase())}
function statusIsLive(s){return ['live','in_progress','inprogress','1st half','2nd half','half-time'].includes(String(s).toLowerCase())}
function providerHealth(rows){
 const finals=SNAPSHOT.recentFinals||[];
 const missed=finals.filter(f=>{const m=rows.find(x=>x.home===f.home&&x.away===f.away);return m&&!statusIsFinal(m.status)});
 if(missed.length)return {ok:false,reason:`El proveedor todavía marca ${missed.length} partidos ya confirmados como no finalizados. Fuente retrasada.`};
 const mismatched=finals.filter(f=>{const m=rows.find(x=>x.home===f.home&&x.away===f.away&&statusIsFinal(x.status)&&x.score);return m&&(m.score[0]!==f.homeGoals||m.score[1]!==f.awayGoals)});
 if(mismatched.length)return {ok:false,reason:`El proveedor contradice ${mismatched.length} marcadores finales verificados. No se utilizarán sus datos para afirmar frescura.`};
 return {ok:true,reason:'Coincide con los marcadores finales comprobables en el corte'};
}
function newStateFromFeed(base,rows){
 const next=clone(base),done=[],live=[];
 const decisions=new Map();
 for(const m of rows){
  const key=m.home+'|'+m.away,targets=next.fixtures.filter(f=>f.home===m.home&&f.away===m.away&&eligibleDate(f,m.dateUTC));
  if(targets.length!==1)continue;
  const f=targets[0];if(statusIsLive(m.status)&&m.score&&(!m.minute||m.minute<=120))live.push({...m,id:f.id});
  if(!statusIsFinal(m.status)||!m.score)continue;
  if(decisions.has(f.id)&&JSON.stringify(decisions.get(f.id).score)!==JSON.stringify(m.score))throw Error('Marcadores finales contradictorios del proveedor');
  decisions.set(f.id,{...m,id:f.id});
 }
 const ix=new Map(next.teams.map(t=>[t.id,t]));
 for(const [id,m] of decisions){
  const fi=next.fixtures.findIndex(f=>f.id===id);if(fi<0)continue;
  const f=next.fixtures[fi],a=ix.get(f.home),b=ix.get(f.away),[hg,ag]=m.score;
  if(!a||!b)throw Error('Equipo no encontrado');
  a.pj++;b.pj++;a.gf+=hg;a.ga+=ag;b.gf+=ag;b.ga+=hg;
  if(hg>ag){a.w++;a.pts+=3;b.l++}else if(hg<ag){b.w++;b.pts+=3;a.l++}else{a.d++;b.d++;a.pts++;b.pts++}
  done.push({home:f.home,away:f.away,homeGoals:hg,awayGoals:ag,status:'final',source:'SportScore',date:m.dateUTC});
 }
 next.fixtures=next.fixtures.filter(f=>!decisions.has(f.id));
 next.recentFinals=[...(next.recentFinals||[]),...done];
 if(done.length){next.meta.asOf=new Date().toISOString();next.meta.status='actualizado_por_feed_con_validacion';next.meta.sourceNote='Los partidos nuevos se incorporaron solo cuando el proveedor informó estado final. Fuente: SportScore.';next.bounds=null}
 validate(next);return {data:next,done,live};
}
function renderFeedState(){
 const el=$('feed-label'),detail=$('feed-details'),updated=$('feed-updated');if(!el)return;
 const st=feedState.status;
 el.className=st==='ok'?'live-ok':'live-error';
 el.textContent=st==='ok'?`● Fuente consultada · ${liveOverlay.size} partidos en curso`:st==='starting'?'Buscando marcadores...':st==='stale'?'⚠ Proveedor retrasado':'⚠ Sin actualización de marcadores';
 detail.textContent=feedState.message;
 updated.textContent=feedState.lastCheck?`Última consulta ${new Date(feedState.lastCheck).toLocaleString('es-CO',{timeZone:'America/Bogota'})} (Bogotá)`:'Sin consulta todavía';
}
function commitFeedUpdate(next,live){
 const prevIds=new Set(data.fixtures.map(f=>f.id)),nextIds=new Set(next.fixtures.map(f=>f.id)),changed=prevIds.size!==nextIds.size;
 if(changed){
  const selection=team,pickById=new Map(data.fixtures.map((f,i)=>[f.id,picks[i]]));
  initialize(next,selection);picks=next.fixtures.map(f=>pickById.get(f.id)||null);
  tableMode='modal'; // Future routes are re-evaluated after each final result.
 }
 const liveNew=new Map(live.filter(x=>nextIds.has(x.id)).map(x=>[x.id,x]));
 const oldKey=JSON.stringify([...liveOverlay.values()].map(x=>[x.id,x.score]));
 const newKey=JSON.stringify([...liveNew.values()].map(x=>[x.id,x.score]));
 liveOverlay=liveNew;
 if(changed||oldKey!==newKey){sim=null;renderAll();if(!busy)runSimulation(2000)}
 else renderFeedState();
 return changed||oldKey!==newKey;
}
function datesForPolling(){
 const d=new Date(),day=Date.UTC(d.getUTCFullYear(),d.getUTCMonth(),d.getUTCDate());
 const dates=[-1,0,1].map(k=>new Date(day+k*86400000).toISOString().slice(0,10));
 for(const f of data.fixtures){if(!f.date)continue;const v=new Date(f.date+'T00:00:00Z');if(Math.abs(v-day)<2*86400000)dates.push(new Date(v).toISOString().slice(0,10))}
 // Ensure UTC midnight matches are queried on their UTC date as well.
 return [...new Set(dates)].sort().slice(0,5);
}
async function fetchLiveFromAPI(dateUTC){
 const q=new URLSearchParams({sport:'football',date:dateUTC,competition:'categoria-primera-a',limit:'200'});
 const res=await fetch(PROVIDER+'?'+q.toString(),{cache:'no-store',signal:AbortSignal.timeout(12000)});
 if(!res.ok)throw Error('HTTP '+res.status);return normalizeProviderRows(await res.json(),dateUTC);
}
async function refreshCachedFeed(){
 if(data.meta.id==='demo')return;
 try{
  const res=await fetch('./live.json?rev='+Math.floor(Date.now()/60000),{cache:'no-store',signal:AbortSignal.timeout(6000)});
  if(!res.ok)return;
  const payload=await res.json();
  if(payload.baseVersion!==SNAPSHOT.meta.version||!Array.isArray(payload.matches))return;
  const rows=payload.matches.flatMap(o=>{
   const f=data.fixtures.find(x=>x.id===o.id),fromBase=SNAPSHOT.fixtures.find(x=>x.id===o.id);if(!f||!fromBase)return [];
   return [{home:f.home,away:f.away,status:o.status,score:o.score,minute:o.minute??null,dateUTC:o.utcDate,source:'SportScore (respaldo)'}];
  });
  const result=payload.staleReference?{data,done:[],live:[]}:newStateFromFeed(data,rows);
  if(result.done.length||result.live.length)commitFeedUpdate(result.data,result.live);
  const ageMinutes=payload.updatedAt?(Date.now()-new Date(payload.updatedAt).getTime())/60000:Infinity;
  const status=payload.staleReference||ageMinutes>30?'stale':'ok';
  if(feedState.status==='starting'||feedState.status==='error'||feedState.status==='stale')feedState={status,lastCheck:payload.updatedAt||null,source:'SportScore (respaldo)',message:ageMinutes>30?'El respaldo periódico está desactualizado; no se confirma frescura en vivo.':'Copia periódica del proveedor, no feed oficial; comprueba la hora de la última actualización.'};
  renderFeedState();
 }catch(e){/* The cached feed is optional; the verified cut remains usable. */}
}
let querying=false;
async function refreshLive(){
 if(querying||data.meta.id==='demo')return;
 querying=true;$('refresh-live').disabled=true;
 try{
  const days=datesForPolling();
  const responses=await Promise.allSettled(days.map(fetchLiveFromAPI));
  const rows=responses.flatMap(x=>x.status==='fulfilled'?x.value:[]);
  if(!responses.some(x=>x.status==='fulfilled'))throw Error('No se pudo consultar la API en ninguna fecha');
  const health=providerHealth(rows);
  // Source can lag. We never overwrite the verified cut with a stale upstream table.
  const baseSnapshot=data;const result=health.ok?newStateFromFeed(baseSnapshot,rows):{data:baseSnapshot,done:[],live:[]};
  const modified=commitFeedUpdate(result.data,result.live);
  feedState={status:health.ok?'ok':'stale',message:health.ok?(result.done.length?`${result.done.length} resultados finales nuevos incorporados. El pronóstico se recalculó para todos los equipos.`:`No hay nuevos finales confirmados. ${result.live.length} encuentros en juego observados. Se consulta cada minuto.`):health.reason+' No se atribuye frescura en vivo a esta respuesta.',lastCheck:new Date().toISOString(),source:'SportScore'};
  renderFeedState();
 }catch(err){feedState={status:'error',lastCheck:new Date().toISOString(),message:'Error consultando SportScore: '+String(err.message||err).slice(0,160)+'. Se conserva el último corte verificado.',source:'SportScore'};renderFeedState();await refreshCachedFeed()}
 finally{querying=false;$('refresh-live').disabled=false}
}

attachEvents();initialize(window.MATCHLAB_INITIAL_DATA,'DIM');
if(window.MATCHLAB_API_AUTO!==true){$('certify-fixed').disabled=true;$('certify-fixed').title='La certificación dinámica requiere un backend; los certificados precomputados se muestran arriba.';$('certify-fixed').textContent='Certificación dinámica: requiere servidor';} 
if(window.MATCHLAB_API_AUTO===true){fetch('/api/state',{cache:'no-store'}).then(r=>r.ok?r.json():Promise.reject('Sin estado')).then(d=>initialize(d,'DIM')).catch(()=>{$('competition-info').textContent+=' · No se pudo cargar el estado del servidor.'})}
document.getElementById("refresh-live").addEventListener("click",async()=>{await refreshLive();await refreshCachedFeed()});setInterval(()=>{if(!document.hidden)refreshLive()},60000);setInterval(()=>{if(!document.hidden)refreshCachedFeed()},120000);refreshCachedFeed();refreshLive();runSimulation(2000);
window.MatchLabTest={refreshLive,normalizeProviderRows,newStateFromFeed,providerHealth,modalTable,expectedTable,liveOverlay:()=>liveOverlay,feedState:()=>feedState,feedCommit:commitFeedUpdate,getData:()=>data,getPicks:()=>picks,select:(id)=>{team=id;renderAll()},preset:setPreset,choose,table:standings,probabilities:()=>probs,run:runSimulation,sim:()=>sim,setScore,scoreFromOutcome,encodeRoute,loadRoute,validate};
