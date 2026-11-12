const {test,expect}=require('@playwright/test');
const route='/Presentaciones/s11-videoclase-ocr-asr-embeddings.html';
test('S11: navegación e índice de 24 pantallas',async({page})=>{
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(route+'#s1');
 await expect(page.locator('section.slide')).toHaveCount(24);
 await expect(page.locator('section.slide.active')).toHaveCount(1);
 await expect(page.locator('#count')).toHaveText('1 / 24');
 await expect(page.locator('#prev')).toBeDisabled();
 await page.locator('#next').click();
 await expect(page.locator('#count')).toHaveText('2 / 24');
 await page.locator('#index').click();
 await expect(page.locator('#outline')).toBeVisible();
 await expect(page.locator('#links button')).toHaveCount(24);
 await page.locator('#links button').last().click();
 await expect(page.locator('#s24')).toBeVisible();
 await expect(page.locator('#next')).toBeDisabled();
 await expect(page.locator('#s24 .question a')).toHaveAttribute('href',/01_laboratorio\.ipynb/);
 expect(errors).toEqual([]);
});

for(const size of [{width:1366,height:768},{width:1280,height:720},{width:1920,height:1080},{width:390,height:844}]){
 test('S11: 24 diapositivas completas sin scroll ni recortes '+size.width+'x'+size.height,async({page})=>{
  await page.setViewportSize(size);
  await page.goto(route+'#s1');
  const failures=[];
  for(let i=1;i<=24;i++){
    const metrics=await page.evaluate(n=>{
      const slide=document.getElementById('s'+n), main=document.querySelector('main');
      const sr=slide.getBoundingClientRect(),mr=main.getBoundingClientRect();
      const affected=[slide,...slide.querySelectorAll('.card,.visual,.question')].filter(el=>getComputedStyle(el).display!=='none');
      const overflows=affected.filter(el=>el.scrollHeight>el.clientHeight+2 || el.scrollWidth>el.clientWidth+2)
        .map(el=>({part:el.className,scrollH:el.scrollHeight,clientH:el.clientHeight,scrollW:el.scrollWidth,clientW:el.clientWidth}));
      const rect=el=>{let r=el.getBoundingClientRect();return {top:r.top,bottom:r.bottom,left:r.left,right:r.right}};
      return {active:slide.classList.contains('active'),slide:rect(slide),main:rect(main),
        overflows,docH:document.documentElement.scrollHeight,docW:document.documentElement.scrollWidth,
        viewportW:innerWidth,viewportH:innerHeight,
        cards:slide.querySelectorAll('.card').length,
        footer:rect(document.querySelector('footer')),header:rect(document.querySelector('header'))};
    },i);
    const fits=metrics.active && metrics.cards===3 &&
      metrics.docH<=size.height+1 && metrics.docW<=size.width+1 &&
      metrics.overflows.length===0 &&
      metrics.slide.top>=metrics.main.top-2 &&
      metrics.slide.bottom<=metrics.main.bottom+2 &&
      metrics.header.bottom<=metrics.slide.top &&
      metrics.slide.bottom<=metrics.footer.top;
    if(!fits)failures.push({slide:i,metrics});
    if(i<24)await page.locator('#next').click();
  }
  expect(failures).toEqual([]);
 });
}

test('S11: experimentos de selección, PSM, coseno, WER y lote',async({page})=>{
 await page.goto(route+'#s5');
 await page.locator('#method').selectOption('vision');
 await expect(page.locator('#methodOut')).toContainText('EmbeddingGemma');
 await page.goto(route+'#s8');
 await page.locator('#psmMode').selectOption('6');
 await expect(page.locator('#psmOut')).toContainText('bloque');
 await page.goto(route+'#s16');
 await page.locator('#cosine').evaluate(el=>{el.value='0';el.dispatchEvent(new Event('input',{bubbles:true}))});
 await expect(page.locator('#cosineOut')).toContainText('1.000');
 await page.goto(route+'#s20');
 await expect(page.locator('#werOut')).toContainText('33.3%');
 await page.locator('#werHyp').fill('valor del contrato');
 await expect(page.locator('#werOut')).toContainText('0.0%');
 await page.goto(route+'#s23');
 await page.locator('#nImages').selectOption('62');
 await expect(page.locator('#nOut')).toContainText('NO una estimación');
});


test('S11: las 24 diapositivas contienen explicación sustantiva y casos concretos', async({page})=>{
 await page.goto(route+'#s1');
 const audit=await page.locator('section.slide').evaluateAll(slides=>slides.map((slide,i)=>{
   const cards=[...slide.querySelectorAll('.card')];
   const paragraphs=cards.map(c=>c.querySelector('p')?.textContent?.trim()||'');
   const subtitles=slide.querySelector('.slide-sub')?.textContent?.trim()||'';
   return {number:i+1,cards:cards.length,paragraphs:paragraphs.map(p=>p.length),
     subtitle:subtitles.length,hasQuestion:!!slide.querySelector('.question span'),
     hasVisual:!!slide.querySelector('.visual .vtitle'),
     words:(subtitles+' '+paragraphs.join(' ')).split(/\s+/).filter(Boolean).length};
 }));
 for(const screen of audit){
   expect(screen.cards,'Diapositiva '+screen.number).toBe(3);
   expect(screen.hasQuestion,'Comprobación en '+screen.number).toBe(true);
   expect(screen.hasVisual,'Visual en '+screen.number).toBe(true);
   expect(screen.subtitle,'Subtítulo en '+screen.number).toBeGreaterThan(75);
   expect(Math.min(...screen.paragraphs),'Tarjetas escuetas en '+screen.number).toBeGreaterThan(155);
   expect(screen.words,'Explicación insuficiente en '+screen.number).toBeGreaterThan(95);
 }
});

test('S11: la presentación deriva el desarrollo de Python al cuaderno',async({page})=>{
 await page.goto(route+'#s1');
 await expect(page.locator('section.slide .question a')).toHaveCount(24);
 await expect(page.locator('#s1')).toContainText(/cuaderno/i);
 await expect(page.locator('section.slide pre')).toHaveCount(1);
 await expect(page.locator('section.slide')).toHaveCount(24);
});
