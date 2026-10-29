const {test,expect}=require('@playwright/test');
for(const viewport of [{width:1366,height:680},{width:1366,height:768},{width:1536,height:730},{width:390,height:844}]){
 test('S09 implementación legible '+viewport.width+'x'+viewport.height,async({page})=>{
  await page.setViewportSize(viewport);
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s21');
  await expect(page.locator('#s21 .resume-mark')).toContainText('AQUÍ NOS HABÍAMOS QUEDADO');
  await expect(page.locator('#phaseBadge')).toContainText('Aquí retomamos');
  for(let n=21;n<=35;n++){
   await page.evaluate(n=>go(n-1),n);await page.waitForTimeout(60);
   const state=await page.locator('.slide.on').evaluate(e=>{
    const c=e.querySelector('.slide-content'),r=c.getBoundingClientRect(),body=e.querySelector('.vector-body');
    const scale=Number(e.dataset.fit||1);
    return {fit:scale,width:r.width,body:parseFloat(getComputedStyle(body).fontSize)*scale,
     code:[...e.querySelectorAll('pre')].map(x=>parseFloat(getComputedStyle(x).fontSize)*scale),
     overflow:c.scrollWidth>c.clientWidth+3};
   });
   expect(state.overflow,'S'+n+' horizontal').toBe(false);
   expect(state.body,'S'+n+' body').toBeGreaterThanOrEqual(viewport.width>900?19:17);
   for(const size of state.code)expect(size,'S'+n+' code').toBeGreaterThanOrEqual(viewport.width>900?17:14);
   if(viewport.width>900)expect(state.fit,'S'+n+' scale').toBeGreaterThanOrEqual(.98);
  }
 });
}
test('S09 tutorial conserva progreso local sin redirigir',async({page})=>{
 await page.goto('/assets/tutoriales/s09-laboratorio-guiado.html');
 await expect(page.locator('[data-step]')).toHaveCount(6);
 await page.locator('[data-step="1"]').check();await page.reload();
 await expect(page.locator('[data-step="1"]')).toBeChecked();
 await page.locator('#reset').click();await expect(page.locator('[data-step="1"]')).not.toBeChecked();
 await expect(page.locator('#progress')).toHaveText('0 de 6 pasos marcados en este navegador.');
});

for(const width of [1366,390])test('Atlas preparación embebida '+width,async({page})=>{
 await page.setViewportSize({width,height:844});
 await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s26');
 await page.locator('#s26 [data-atlas-setup]').click();
 const dialog=page.getByRole('dialog',{name:'Atlas + Colab · preparación paso a paso'});
 await expect(dialog).toBeVisible();
 await expect(dialog.locator('.atlas-step')).toHaveCount(7);
 await expect(dialog).toContainText('1 week');
 await expect(dialog).toContainText('Specific Privileges');
 await expect(dialog).toContainText('IP_COLAB');
 expect(await dialog.evaluate(e=>e.scrollWidth<=e.clientWidth+2)).toBe(true);
 await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();
 await page.locator('#s26 [data-atlas-setup]').click();
 await dialog.getByRole('button',{name:'Cerrar',exact:true}).click();
 await expect(dialog).not.toBeVisible();
});
