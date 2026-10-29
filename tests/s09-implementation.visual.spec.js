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
test('S09 tutorial integrado: seis pasos, progreso y enlace anterior',async({page})=>{
 await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s21');
 await page.locator('#s21 [data-s09-practice]').click();
 const dialog=page.getByRole('dialog',{name:'S09 · Tu laboratorio en seis pasos'});
 await expect(dialog).toBeVisible();await expect(dialog.locator('[data-practice-step]')).toHaveCount(6);
 await dialog.locator('[data-practice-step="1"]').check();await page.reload();
 await page.locator('#s21 [data-s09-practice]').click();
 await expect(dialog.locator('[data-practice-step="1"]')).toBeChecked();
 await dialog.locator('#s09PracticeReset').click();await expect(dialog.locator('#s09PracticeProgress')).toContainText('0 de 6 pasos');
 await dialog.locator('[data-practice-close]').click();await expect(dialog).not.toBeVisible();
 await page.goto('/assets/tutoriales/s09-laboratorio-guiado.html');
 await expect(page).toHaveURL(/s09-de-palabras-a-significado.html#s21$/);
});

for(const width of [1366,390])test('Atlas autónomo guiado y consola UI '+width,async({page})=>{
 await page.setViewportSize({width,height:844});
 await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s26');
 await page.locator('#s26 [data-atlas-setup]').click();
 const dialog=page.getByRole('dialog',{name:'MongoDB Atlas real · no necesitas pedir accesos'});
 await expect(dialog).toBeVisible();
 await expect(dialog.locator('section.atlas-step')).toHaveCount(4);
 await expect(dialog).toContainText('Atlas temporal automático');
 await expect(dialog).toContainText('0.0.0.0/0');
 await expect(dialog).toContainText('Reclamar mi clúster');
 await expect(dialog).toContainText('Data Explorer');
 await expect(dialog).toContainText('s09_vector_index');
 await expect(dialog).toContainText('s09_atlas_evidencia.json');
 await expect(dialog).toContainText('NO EJECUTADO');
 await expect(dialog.locator('details')).toContainText('HOST_ATLAS');
 expect(await dialog.evaluate(e=>e.scrollWidth<=e.clientWidth+2)).toBe(true);
 await page.keyboard.press('Escape');await expect(dialog).not.toBeVisible();
 await page.locator('#s26 [data-atlas-setup]').click();
 await dialog.getByRole('button',{name:'Cerrar',exact:true}).click();
 await expect(dialog).not.toBeVisible();
});
