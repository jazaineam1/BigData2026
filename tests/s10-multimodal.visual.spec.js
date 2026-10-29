const {test,expect}=require('@playwright/test');
const route='/Presentaciones/s10-imagenes-audio.html';
for(const size of [{width:1366,height:768},{width:390,height:844}]){
 test('S10 app responsive '+size.width,async({page})=>{
  await page.setViewportSize(size);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'#s1');
  await expect(page.locator('.slide')).toHaveCount(23);
  for(let n=1;n<=23;n++){
   await page.goto(route+'#s'+n);await expect(page.locator('#s'+n)).toBeVisible();
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2)).toBe(true);
  }
  expect(errors).toEqual([]);
 });
}
test('imagen: controles y cambios de medidas',async({page})=>{
 await page.goto(route+'#s5');
 await expect(page.locator('#imageStats')).toContainText('Derivado');
 const before=await page.evaluate(()=>window.imageMetrics.pixels);
 await page.locator('#imageSize').evaluate(el=>{el.value='80';el.dispatchEvent(new Event('input',{bubbles:true}))});
 const after=await page.evaluate(()=>window.imageMetrics.pixels);
 expect(after).toBeLessThan(before);
 await page.locator('#imageBinary').check();
 expect(await page.evaluate(()=>window.imageMetrics.binarized)).toBe(true);
});
test('audio: señal original, ventana y exportación de resumen',async({page})=>{
 await page.goto(route+'#s8');
 await page.locator('#demoAudio').click();
 await expect(page.locator('#audioStats')).toContainText('RMS ventana');
 await page.locator('#audioStart').evaluate(el=>{el.value='50';el.dispatchEvent(new Event('input',{bubbles:true}))});
 expect(await page.evaluate(()=>window.audioMetrics.window_rms)).toBeLessThan(0.01);
 await expect(page.locator('#s8')).toContainText('10 voces humanas reales');
 await page.goto(route+'#s23');
 const download=page.waitForEvent('download');
 await page.locator('#exportObservations').click();
 expect((await download).suggestedFilename()).toBe('s10-observaciones-locales.json');
});
test('autoevaluación y enlace al cuaderno',async({page})=>{
 await page.goto(route+'#s3');
 await page.locator('[data-question=q1] button[data-correct="1"]').click();
 await expect(page.locator('#s3 .feedback')).toContainText('Correcto');
 await page.goto(route+'#s12');
 const link=page.locator('a[href*="10_Imagenes_Audio.ipynb"]').first();
 await expect(link).toHaveAttribute('href',/10_Imagenes_Audio.ipynb/);
 await expect((await page.request.get('/Cuadernos/10_Imagenes_Audio.ipynb')).status()).toBe(200);
});

test('autonomia: cada paso tiene accion, salida esperada, error y verificaciones del estudiante',async({page})=>{
 await page.goto(route+'#s12');
 await expect(page.locator('#s12')).toContainText('Guardar una copia en Drive');
 await expect(page.locator('#s12')).toContainText('Preparar bibliotecas');
 for(const n of [13,14,15,16,17,18,19,20,21]){
  await page.goto(route+'#s'+n);
  const slide=page.locator('#s'+n);
  await expect(slide).toBeVisible();
  expect((await slide.innerText()).length).toBeGreaterThan(420);
 }
 await expect(page.locator('#s16')).toContainText('VOCES REALES VERIFICADAS: 10');
 await expect(page.locator('#s17')).toContainText('POSICION_VOZ');
 await expect(page.locator('#s18')).toContainText('USAR_ASR');
 await expect(page.locator('#s19')).toContainText('32 referencias');
 await expect(page.locator('#s20')).toContainText('13 filas');
 await expect(page.locator('#s21')).toContainText('AUTOCOMPROBACIÓN: LISTO');
 await expect(page.locator('#s21 .student-progress')).toHaveCount(6);
 for(const box of await page.locator('#s21 .student-progress').all())await box.check();
 await expect(page.locator('#studentChecklistStatus')).toContainText('6 de 6');
 await page.goto(route+'#s22');
 await page.locator('[data-question=q4] button[data-correct="1"]').click();
 await expect(page.locator('#s22 .feedback')).toContainText('Correcto');
 await page.goto(route+'#s23');
 await expect(page.locator('#s23')).toContainText('el producto evaluable');
});
