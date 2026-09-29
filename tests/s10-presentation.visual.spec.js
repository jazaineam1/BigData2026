const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const viewports=[
  {name:'laptop-real',width:1536,height:730},
  {name:'laptop-1366',width:1366,height:768},
  {name:'desktop',width:1536,height:864},
];

async function inspect(page,n){
  await page.evaluate(x=>{location.hash='#s'+x},n);
  await page.waitForTimeout(60);
  return page.evaluate(()=>{
    const slide=document.querySelector('.slide.on'),body=slide.querySelector('.body'),h1=slide.querySelector('h1'),nav=document.querySelector('.nav'),top=document.querySelector('.top');
    const rect=e=>e.getBoundingClientRect();
    const r=rect(slide),br=rect(body),hr=rect(h1),nr=rect(nav),tr=rect(top);
    const overlap=(a,b)=>a.left<b.right-2&&a.right>b.left+2&&a.top<b.bottom-2&&a.bottom>b.top+2;
    const badOverflow=[...slide.querySelectorAll('.card,.note,.lab,.diagram,.inspector,.sampling,pre')].filter(e=>e.scrollWidth>e.clientWidth+3||e.scrollHeight>e.clientHeight+3).map(e=>e.className||e.tagName);
    const visualRects=[...slide.querySelectorAll('.visual,svg,pre,table')]
      .map(el=>rect(el))
      .filter(r=>r&&r.width>0&&r.height>0)
      .sort((a,b)=>(b.width*b.height)-(a.width*a.height));
    const vr=visualRects[0]||null;
    const bodyText=[...slide.querySelectorAll('p,li,td,th,.card span,.card')].filter(e=>e.children.length===0||e.matches('p,li,td,th')).map(e=>parseFloat(getComputedStyle(e).fontSize)).filter(Number.isFinite);
    const codeText=[...slide.querySelectorAll('pre')].map(e=>parseFloat(getComputedStyle(e).fontSize));
    return {
      fit:Number(slide.dataset.fit||1),
      titleSize:parseFloat(getComputedStyle(h1).fontSize),
      minBody:bodyText.length?Math.min(...bodyText):16,
      minCode:codeText.length?Math.min(...codeText):99,
      titleBeforeBody:hr.bottom<=br.top+8,
      topOverlap:overlap(tr,hr),
      navOverlap:overlap(nr,br),
      badOverflow,
      visualSize:vr?{w:vr.width/r.width,h:vr.height/r.height}:null,
      visualVisible:!!vr&&vr.width>80&&vr.height>35,
      bodyBottom:br.bottom,
      navTop:nr.top
    };
  });
}

for(const vp of viewports){
  test('S10 disposición para ojo humano · '+vp.name,async({page})=>{
    await page.setViewportSize({width:vp.width,height:vp.height});
    await page.goto('/Presentaciones/s10-etl-multimedia.html#s1');
    const failures=[];
    for(let n=1;n<=34;n++){
      const x=await inspect(page,n);
      if(x.fit<0.92) failures.push('S'+n+' escala '+x.fit);
      const effTitle=x.titleSize*x.fit,effBody=x.minBody*x.fit,effCode=x.minCode*x.fit;
      if(effTitle<46) failures.push('S'+n+' título efectivo '+effTitle.toFixed(1)+'px');
      if(effBody<15) failures.push('S'+n+' cuerpo efectivo '+effBody.toFixed(1)+'px');
      if(effCode<13) failures.push('S'+n+' código efectivo '+effCode.toFixed(1)+'px');
      if(!x.titleBeforeBody) failures.push('S'+n+' orden título/cuerpo');
      if(x.topOverlap) failures.push('S'+n+' toolbar sobre título');
      if(x.navOverlap||x.bodyBottom>x.navTop+4) failures.push('S'+n+' navegación sobre contenido');
      if(x.badOverflow.length) failures.push('S'+n+' overflow '+x.badOverflow.join(','));
      if(!x.visualVisible) failures.push('S'+n+' ancla visual demasiado pequeña');
      if(x.visualSize && (x.visualSize.w<0.27 || x.visualSize.h<0.10)) failures.push('S'+n+' visual principal insuficiente '+JSON.stringify(x.visualSize));
    }
    expect(failures).toEqual([]);
  });
}

test('S10 controles interactivos y orden cognitivo',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s10');
  const selects=page.locator('[data-pipe-pos]');
  await selects.nth(0).selectOption('raw');
  await selects.nth(1).selectOption('identify');
  await selects.nth(2).selectOption('inspect');
  await selects.nth(3).selectOption('transform');
  await selects.nth(4).selectOption('validate');
  await selects.nth(5).selectOption('manifest');
  await page.locator('#pipelinePreviewBtn').click();
  await expect(page.locator('#pipelinePreview')).toContainText('orden defendible');
  await page.evaluate(()=>{location.hash='#s27'});
  await page.locator('#videoDuration').fill('60');
  await page.locator('#videoMaxFrames').fill('10');
  await expect(page.locator('#samplingInterval')).toContainText('6.0 s');
});

test('S10 accesibilidad crítica',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s1');
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze();
  const critical=results.violations.filter(v=>['critical','serious'].includes(v.impact));
  expect(critical).toEqual([]);
});


test('S10 conserva la escala visual de S07',async({page})=>{
  await page.setViewportSize({width:1536,height:730});
  await page.goto('/Presentaciones/s07-del-vecindario-al-texto.html');
  await page.waitForTimeout(120);
  const refTitle=await page.locator('.slide.on h1').evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
  const refLead=await page.locator('.slide.on .lead').evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
  await page.locator('#next').click();
  await page.waitForTimeout(60);
  const refCard=await page.locator('.slide.on .card').first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize));
  for(let i=0;i<3;i++){await page.locator('#next').click();await page.waitForTimeout(40)}
  const refCode=await page.locator('.slide.on pre').first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize));

  await page.goto('/Presentaciones/s10-etl-multimedia.html#s1');
  await page.waitForTimeout(80);
  const s10Title=await page.locator('.slide.on h1').evaluate(el=>parseFloat(getComputedStyle(el).fontSize)*Number(el.closest('.slide').dataset.fit||1));
  const s10Lead=await page.locator('.slide.on .lead').evaluate(el=>parseFloat(getComputedStyle(el).fontSize)*Number(el.closest('.slide').dataset.fit||1));
  await page.evaluate(()=>{location.hash='#s2'});
  await page.waitForTimeout(60);
  const s10Card=await page.locator('.slide.on .card').first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize)*Number(el.closest('.slide').dataset.fit||1));
  const s10Code=await page.locator('.slide.on pre').first().evaluate(el=>parseFloat(getComputedStyle(el).fontSize)*Number(el.closest('.slide').dataset.fit||1));

  expect(s10Title).toBeGreaterThanOrEqual(refTitle*0.95);
  expect(s10Lead).toBeGreaterThanOrEqual(refLead*0.95);
  expect(s10Card).toBeGreaterThanOrEqual(refCard*0.95);
  expect(s10Code).toBeGreaterThanOrEqual(refCode*0.95);
});

test('S10 V2 tiene Live, D1-D8, simuladores y LAB verificables',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s1');
  await expect(page.locator('#liveBtn')).toBeVisible();
  await page.locator('#liveBtn').click();
  await expect(page.locator('#liveDrawer')).toHaveClass(/on/);
  await expect(page.locator('[data-submit-challenge]')).toHaveCount(8);
  await expect(page.locator('[data-submit-lab]')).toHaveCount(3);
  for(const id of ['articleIndex','hashText','pipelineBuilder','mediaFile','audioRate','videoMaxFrames','manifestPreview'])await expect(page.locator('#'+id)).toHaveCount(1);
});

test('S10 herramientas pedagógicas responden en modo local',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s13');
  await page.locator('#hashCalc').click();
  const h1=await page.locator('#hashOut').textContent();
  expect((h1||'').trim().length).toBe(64);
  await page.locator('#hashMutate').click();
  const h2=await page.locator('#hashOut').textContent();
  expect(h2).not.toBe(h1);

  await page.evaluate(()=>{location.hash='#s21'});
  await page.locator('#audioRate').selectOption('16000');
  await page.locator('#audioChannels').selectOption('1');
  await page.locator('#audioFormat').selectOption('wav');
  await expect(page.locator('#audioGoal')).toContainText('Cumple');

  await page.evaluate(()=>{location.hash='#s27'});
  await page.locator('#videoDuration').fill('60');
  await page.locator('#videoMaxFrames').fill('10');
  await expect(page.locator('#samplingInterval')).toContainText('6.0 s');

  await page.evaluate(()=>{location.hash='#s33'});
  await page.locator('#ans-bd-s10-c8').selectOption('sha256_sampling');
  await page.locator('[data-submit-challenge="bd-s10-c8"]').click();
  await expect(page.locator('#fb-bd-s10-c8')).toContainText('Correcto');
});
