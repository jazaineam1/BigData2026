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

test('S09 P0 mantiene una sola opción de progreso en la presentación',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s1');
  await expect(page.getByRole('button',{name:'Progreso S09'})).toBeVisible();
  await expect(page.locator('a[href="../lms/progress.html?s=9"]')).toHaveCount(0);
  await expect(page.getByText('Mi progreso',{exact:true})).toHaveCount(0);
});
