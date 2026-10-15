const { test, expect } = require('@playwright/test');

const viewports=[
  {name:'laptop-1536-real',width:1536,height:730},
  {name:'laptop-1366',width:1366,height:768},
  {name:'desktop-1536',width:1536,height:864},
];

async function inspectSlide(page,n){
  await page.evaluate(x=>{location.hash='#s'+x},n);
  await page.waitForTimeout(70);
  return page.evaluate(()=>{
    const slide=document.querySelector('.slide.on'),stage=document.querySelector('.stage'),top=document.querySelector('.top'),nav=document.querySelector('.nav'),h1=slide?.querySelector('h1'),body=slide?.querySelector('.body');
    const rect=el=>el?el.getBoundingClientRect():null,overlap=(a,b,t=3)=>!!(a&&b&&a.left<b.right-t&&a.right>b.left+t&&a.top<b.bottom-t&&a.bottom>b.top+t);
    const sr=rect(stage),tr=rect(top),nr=rect(nav),hr=rect(h1),br=rect(body);
    return {
      slide:Number(slide?.dataset.slide||0),
      fit:Number(slide?.dataset.fit||1),
      fitReason:slide?.dataset.fitReason||'',
      topOverlap:overlap(tr,hr),
      bottomOverlap:overlap(nr,br),
      stage:sr?{left:sr.left,right:sr.right,top:sr.top,bottom:sr.bottom}:null,
      h1:hr?{left:hr.left,right:hr.right,top:hr.top,bottom:hr.bottom}:null,
      brokenFlow:[...document.querySelectorAll('.slide.on .node')].filter(el=>el.scrollWidth>el.getBoundingClientRect().width+2).map(el=>el.textContent),
      labels:[...document.querySelectorAll('.slide.on svg text')].map(el=>({text:(el.textContent||'').trim(),r:rect(el),svg:rect(el.closest('svg'))})).filter(x=>x.r&&x.svg).filter(x=>x.r.left<x.svg.left-3||x.r.right>x.svg.right+3||x.r.top<x.svg.top-3||x.r.bottom>x.svg.bottom+3).map(x=>x.text),
      boxedLabels:[...document.querySelectorAll('.slide.on svg text')].flatMap(el=>{
        const tr=rect(el),svg=el.closest('svg');if(!tr||!svg||!tr.width||!tr.height)return [];
        const cx=(tr.left+tr.right)/2,cy=(tr.top+tr.bottom)/2;
        const boxes=[...svg.querySelectorAll('rect')].map(r=>({el:r,r:rect(r)})).filter(x=>x.r&&cx>=x.r.left&&cx<=x.r.right&&cy>=x.r.top&&cy<=x.r.bottom)
          .sort((a,b)=>(a.r.width*a.r.height)-(b.r.width*b.r.height));
        if(!boxes.length)return [];
        const br=boxes[0].r,t=3,bad=tr.left<br.left-t||tr.right>br.right+t||tr.top<br.top-t||tr.bottom>br.bottom+t;
        return bad?[{text:(el.textContent||'').trim(),textRect:{left:tr.left,right:tr.right,top:tr.top,bottom:tr.bottom},boxRect:{left:br.left,right:br.right,top:br.top,bottom:br.bottom}}]:[];
      })
    };
  });
}

for(const vp of viewports){
  test('S09 P0 geometría real · '+vp.name,async({page})=>{
    await page.setViewportSize({width:vp.width,height:vp.height});
    await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s1');
    const failures=[];
    for(let n=1;n<=35;n++){
      const x=await inspectSlide(page,n);
      if(x.fit<0.79)failures.push('S'+n+' fit='+x.fit+' reason='+x.fitReason);
      if(x.topOverlap)failures.push('S'+n+' toolbar solapa título');
      if(x.bottomOverlap)failures.push('S'+n+' navegación solapa body');
      if(x.labels.length)failures.push('S'+n+' labels fuera SVG: '+x.labels.join(' | '));
      if(x.boxedLabels.length)failures.push('S'+n+' labels fuera de su caja: '+x.boxedLabels.map(z=>z.text).join(' | '));
      if(n===21&&x.brokenFlow.length)failures.push('S21 nodos partidos: '+x.brokenFlow.join(' | '));
    }
    expect(failures).toEqual([]);
  });
}

test('S09 P0 desafíos empiezan vacíos y la respuesta fuente no queda primera',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s9');
  const correct={
    'bd-s09-c1':'lexical',
    'bd-s09-c2':'similarity_not_probability',
    'bd-s09-c3':'judge_relevance',
    'bd-s09-c4':'embedding_model',
    'bd-s09-c5':'rank_fusion'
  };
  for(const [code,value] of Object.entries(correct)){
    const sel=page.locator('#ans-'+code);
    await expect(sel).toHaveValue('');
    await expect(sel.locator('option').first()).toHaveText('Elige una opción…');
    const firstReal=await sel.locator('option').nth(1).getAttribute('value');
    expect(firstReal).not.toBe(value);
  }
});

test('S09 P0 no pregunta nivel de confianza en D1-D5',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s9');
  await expect(page.locator('[id^="conf-"]')).toHaveCount(0);
  await expect(page.getByText('¿Qué tan seguro estás?',{exact:true})).toHaveCount(0);
  for(const code of ['bd-s09-c1','bd-s09-c2','bd-s09-c3','bd-s09-c4','bd-s09-c5']){
    await expect(page.locator('#ans-'+code)).toBeAttached();
  }
});

test('S09 P0 mantiene una barra simple sin Mi progreso global',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s1');
  await expect(page.locator('#liveBtn')).toBeHidden(); // acceso público sin panel de progreso
  await expect(page.locator('a[href="../lms/progress.html?s=9"]')).toHaveCount(0);
  await expect(page.getByText('Mi progreso',{exact:true})).toHaveCount(0);
});


test('S09 se abre sin usuario y permite autocomprobar D1 en modo público',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s9');
  await expect(page).toHaveURL(/s09-de-palabras-a-significado\.html#s9$/);
  await expect(page.locator('#moduleIdentity')).toContainText('Acceso libre');
  await page.locator('#ans-bd-s09-c1').selectOption('lexical');
  await page.locator('#s9 .challenge button').click();
  await expect(page.locator('#fb-bd-s09-c1')).toContainText('Correcto');
  await expect(page.locator('#fb-bd-s09-c1')).toContainText('sin registro');
  await expect(page.getByText('Iniciar sesión',{exact:true})).toHaveCount(0);
});

test('S09 conserva la navegación cuando el usuario escribe en un campo',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s2');
  await page.locator('#caseQ').focus();
  await page.keyboard.press('Space');
  await expect(page).toHaveURL(/#s2$/);
  await expect(page.locator('#caseQ')).toHaveValue(/\s$/);
});

test('S09 Precision@5 requiere evaluar los cinco resultados',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s21');
  await expect(page.locator('#rankScore')).not.toContainText('P@5 =');
  for(const panel of ['#lexRank','#semRank']){
    const buttons=page.locator(panel+' button.rel');
    await expect(buttons).toHaveCount(5);
    for(let i=0;i<5;i++)await buttons.nth(i).click();
  }
  await expect(page.locator('#rankScore')).toContainText('P@5 = 1.00');
});

test('muro S09 público abre sin credenciales y evalúa en modo local',async({page})=>{
  await page.goto('/Presentaciones/s09-muro-publico.html');
  await expect(page.getByText('Muro didáctico abierto')).toBeVisible();
  await page.locator('#choices button[data-value="hibrida"]').click();
  await page.locator('#reveal').click();
  await expect(page.locator('#answer')).toContainText('Correcto como hipótesis');
  await expect(page.locator('#precision')).toHaveText('0/5');
  const labels=page.locator('#items button');
  await expect(labels).toHaveCount(5);
  for(let i=0;i<5;i++)await labels.nth(i).click();
  await expect(page.locator('#precision')).toHaveText('1.00');
});


test('S09 diagramas corregidos mantienen texto dentro del SVG en seis diapositivas',async({page})=>{
  await page.setViewportSize({width:1366,height:768});
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s4');
  for(const n of [4,10,11,12,14,15,17,21,22,25,27,30,31]){
    const x=await inspectSlide(page,n);
    expect(x.labels,'S'+n+' textos fuera del SVG').toEqual([]);
    expect(x.topOverlap,'S'+n+' barra solapada con título').toBeFalsy();
  }
});
test('S09 slide 12 explica mean pooling y las 384 dimensiones',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s12');
  await expect(page.locator('#s12')).toContainText('Mean pooling');
  await expect(page.locator('#s12')).toContainText('tokens válidos');
  await expect(page.locator('#s12')).toContainText('384');
});
test('S09 chunking muestra palabras solapadas y actualiza controles',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s14');
  await expect(page.locator('#chunkOut .chunk-lane')).toHaveCount(4);
  await expect(page.locator('#chunkOut .chunk-token.shared')).not.toHaveCount(0);
  await page.locator('#chunkOverlap').evaluate(el=>{el.value='0';el.dispatchEvent(new Event('input',{bubbles:true}));});
  await expect(page.locator('#chunkOverlapValue')).toHaveText('0');
  await expect(page.locator('#chunkOut .chunk-token.shared')).toHaveCount(0);
  await expect(page.locator('#chunkMeta')).toContainText('overlap: 0');
});


test('S09 acceso público: la diapositiva 20 no tapa el contenido con un panel LMS',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s20');
  await expect(page.locator('#s20')).toBeVisible();
  await expect(page.locator('#s20')).toContainText('Coseno = 0.91');
  await expect(page.locator('#s20')).toContainText('Precision@5');
  await expect(page.locator('#s20')).not.toContainText('Comprueba S09 Live');
  await expect(page.locator('#liveBtn')).toBeHidden();
  await expect(page.locator('#liveDrawer')).toBeHidden();
  await expect(page.locator('#s20 button')).toHaveCount(0);
  await page.keyboard.press('ArrowRight');
  await expect(page).toHaveURL(/#s21$/);
  await expect(page.locator('#liveDrawer')).toBeHidden();
});

test('S09 modo público no muestra controles de seguimiento LMS ni en portada',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s1');
  await expect(page.locator('#liveBtn')).toBeHidden();
  await expect(page.locator('#liveDrawer')).toBeHidden();
  await expect(page.locator('#moduleIdentity')).toContainText('Acceso libre');
});
