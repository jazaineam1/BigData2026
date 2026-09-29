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
    const visual=slide.querySelector('.visual,svg,pre,table');
    const vr=visual?rect(visual):null;
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
      if(x.fit<0.82) failures.push('S'+n+' escala '+x.fit);
      if(x.titleSize<30) failures.push('S'+n+' título '+x.titleSize+'px');
      if(x.minBody<13.5) failures.push('S'+n+' cuerpo '+x.minBody+'px');
      if(x.minCode<12.5) failures.push('S'+n+' código '+x.minCode+'px');
      if(!x.titleBeforeBody) failures.push('S'+n+' orden título/cuerpo');
      if(x.topOverlap) failures.push('S'+n+' toolbar sobre título');
      if(x.navOverlap||x.bodyBottom>x.navTop+4) failures.push('S'+n+' navegación sobre contenido');
      if(x.badOverflow.length) failures.push('S'+n+' overflow '+x.badOverflow.join(','));
      if(!x.visualVisible) failures.push('S'+n+' ancla visual demasiado pequeña');
    }
    expect(failures).toEqual([]);
  });
}

test('S10 controles interactivos y orden cognitivo',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s13');
  await expect(page.locator('#inspectOut')).toContainText('container');
  await page.getByRole('button',{name:'Audio'}).click();
  await expect(page.locator('#inspectOut')).toContainText('sample rate');
  await page.evaluate(()=>{location.hash='#s27'});
  await page.locator('#sampleEvery').fill('4');
  await expect(page.locator('#sampleMeter')).toContainText('8 frames');
});

test('S10 accesibilidad crítica',async({page})=>{
  await page.goto('/Presentaciones/s10-etl-multimedia.html#s1');
  const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa']).analyze();
  const critical=results.violations.filter(v=>['critical','serious'].includes(v.impact));
  expect(critical).toEqual([]);
});
