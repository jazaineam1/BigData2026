const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const route='/Presentaciones/s10-etl-multimedia.html';
for(const vp of [{width:1366,height:768},{width:1920,height:1080},{width:390,height:844}]){
 test(`S10: 17 pantallas legibles ${vp.width}`,async({page})=>{
  await page.setViewportSize(vp);const errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(route+'#s1');
  for(let n=1;n<=17;n++){
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
test('tutorial nativo: pasos, enlaces al cuaderno y progreso local',async({page})=>{
 await page.goto(route+'#s1');await expect(page.locator('#s1')).toContainText('Universidad Central');
 await page.getByRole('link',{name:'Tutorial integrado',exact:true}).click();await expect(page).toHaveURL(/#s5$/);
 const checks=page.locator('[data-step]');expect(await checks.count()).toBe(6);
 for(const n of [5,7,9,11,13,16]){
  await page.evaluate(n=>{location.hash='s'+n},n);
  await expect(page.locator('#s'+n+' a')).toHaveAttribute('href',/colab.*#scrollTo=s10-/);
  await page.locator('#s'+n+' [data-step]').check();
  await expect(page.locator('#s'+n+' [aria-live]')).toContainText('no acredita');
 }
 await page.reload();await expect(page.locator('#s16 [data-step]')).toBeChecked();
 await expect(page.locator('#s16 [aria-live]')).toContainText('6 / 6');
 expect(await page.locator('iframe,a[href$="s10_proyecto_VSCode.zip"]').count()).toBe(0);
 await page.goto('/assets/tutoriales/s10-laboratorio-guiado.html');await expect(page).toHaveURL(/s10-etl-multimedia.html#s5$/);
});
test('navegación por teclado y acceso al cuaderno',async({page})=>{
 await page.goto(route+'#s1');await page.keyboard.press('ArrowRight');await expect(page).toHaveURL(/#s2$/);
 await expect(page.getByRole('link',{name:'Cuaderno Python',exact:true})).toHaveAttribute('href',/Cuadernos\/10_ETL_Multimedia.ipynb$/);
 const res=await page.request.get('/Cuadernos/10_ETL_Multimedia.ipynb');expect(res.ok()).toBe(true);
 const nb=await res.json();expect(nb.cells.length).toBe(29);
});
test('accesibilidad: portada, código y tutorial',async({page})=>{
 for(const n of [1,3,5,9,13,16]){await page.goto(route+'#s'+n);const result=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();expect(result.violations.map(x=>x.id+': '+x.nodes.map(y=>y.target).join(','))).toEqual([]);}
});
