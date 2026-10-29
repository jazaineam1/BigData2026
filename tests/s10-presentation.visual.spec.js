const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const route='/Presentaciones/s10-etl-multimedia.html';
for(const vp of [{width:1366,height:768},{width:1920,height:1080},{width:390,height:844}]){
 test(`S10: 16 pantallas legibles ${vp.width}`,async({page})=>{
  await page.setViewportSize(vp);const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(route+'#s1');
  for(let n=1;n<=16;n++){
   await page.evaluate(n=>{location.hash='s'+n},n);await expect(page.locator('#s'+n)).toBeVisible();
   const box=await page.locator('#s'+n).evaluate(el=>{
    const content=el.querySelector('.slide-content').getBoundingClientRect(),nav=document.querySelector('.nav').getBoundingClientRect(),title=el.querySelector('h1').getBoundingClientRect(),top=document.querySelector('.top').getBoundingClientRect();
    return {overflow:document.documentElement.scrollWidth>innerWidth+1,bottom:content.bottom,navTop:nav.top,overlap:title.top<top.bottom&&title.right>top.left,font:parseFloat(getComputedStyle(el.querySelector('.body')).fontSize),code:[...el.querySelectorAll('pre')].map(x=>parseFloat(getComputedStyle(x).fontSize))};
   });
   expect(box.overflow,'S'+n+' desborde horizontal').toBe(false);
   expect(box.overlap,'S'+n+' título bajo controles').toBe(false);
   expect(box.font).toBeGreaterThanOrEqual(vp.width<900?18:19);
   for(const size of box.code)expect(size).toBeGreaterThanOrEqual(vp.width<900?15:17);
   if(vp.width>=900)expect(box.bottom,'S'+n+' contenido invade navegación').toBeLessThanOrEqual(box.navTop-5);
  }
  expect(errors).toEqual([]);
 });
}
test('autoevaluación: todas las alternativas explican su resultado y arrancan pendientes',async({page})=>{
 await page.goto(route);const boxes=page.locator('[data-question]');expect(await boxes.count()).toBe(6);
 for(let i=0;i<6;i++){
  const box=boxes.nth(i);await page.evaluate(id=>{location.hash='s'+document.querySelector(`[data-question="${id}"]`).closest('.slide').dataset.slide},i);
  await expect(box.locator('select')).toHaveValue('');
  for(const value of ['a','b','c']){await box.locator('select').selectOption(value);await box.locator('button').click();await expect(box.locator('[aria-live]')).toContainText('sin nota ni registro oficial');}
 }
});
test('teclado, enlaces directos y catálogo local sin interpretar HTML',async({page})=>{
 await page.goto(route+'#s1');await page.keyboard.press('ArrowRight');await expect(page).toHaveURL(/#s2$/);
 await page.goto(route+'#s15');await page.locator('#catalogFile').setInputFiles({name:'assets.jsonl',mimeType:'application/json',buffer:Buffer.from(JSON.stringify({article_id:'<img src=x onerror=alert(1)>',profile:'vista320',derived_width:320,derived_height:180})+'\n')});
 await expect(page.locator('#catalogPreview')).toContainText('1 filas');expect(await page.locator('#catalogPreview img').count()).toBe(0);
 await expect(page.locator('.top a').first()).toHaveAttribute('href','../assets/tutoriales/s10_proyecto_VSCode.zip');
 const response=await page.request.get('/assets/tutoriales/s10_proyecto_VSCode.zip');expect(response.ok()).toBe(true);
 await page.goto(route+'#s3');await page.locator('select:visible').focus();await page.keyboard.press('ArrowRight');await expect(page).toHaveURL(/#s3$/);
});
test('checklist guarda progreso local y permite reiniciar',async({page})=>{
 await page.goto('/assets/tutoriales/s10-laboratorio-guiado.html');const check=page.locator('input[type=checkbox]').first();await check.check();await page.reload();await expect(check).toBeChecked();await page.getByRole('button',{name:/Reiniciar/}).click();await expect(check).not.toBeChecked();
});
test('accesibilidad: portada, código, pregunta y archivos locales',async({page})=>{
 for(const n of [1,3,6,7,15]){await page.goto(route+'#s'+n);const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(result.violations.map(x=>x.id+': '+x.nodes.map(y=>y.target).join(','))).toEqual([]);}
});
