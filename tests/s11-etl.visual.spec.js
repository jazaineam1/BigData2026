const {test,expect}=require('@playwright/test');
const url='/Presentaciones/s11-etl-audio-imagenes.html';

test('S11: 17 pantallas y continuidad de Laura, sin video obligatorio',async({page})=>{
 await page.goto(url);
 await expect(page.getByRole('heading',{name:'Del archivo individual al lote auditable'})).toBeVisible();
 await expect(page.locator('#steps button')).toHaveCount(17);
 await page.goto(url+'#s3');
 await expect(page.getByText('Video no se desarrolla')).toBeVisible();
 await page.goto(url+'#s4');
 await expect(page.getByText('S10', {exact:true}).first()).toBeVisible();
});
test('S11: cada acción está enlazada a un paso real y salida verificable',async({page})=>{
 await page.goto(url+'#s6');
 for(let n=1;n<=9;n++){
  await page.goto(url+'#s'+({1:6,2:7,3:9,4:10,5:12,6:13,7:14,8:15,9:16}[n]));
  const check=page.locator('[data-step="'+n+'"]');
  await expect(check).toBeVisible();await check.check();
 }
 await page.goto(url+'#s17');
 await expect(page.locator('#completion')).toContainText('9/9');
 await page.reload();
 await expect(page.locator('#completion')).toContainText('9/9');
});
test('S11: controles de imagen y señal responden a parámetros, sin simular semántica',async({page})=>{
 await page.goto(url+'#s8');
 await expect(page.locator('#imagePreview')).toBeVisible();
 await page.locator('#imageGray').check();
 await page.locator('#imageMax').fill('640');await page.locator('#imageMax').dispatchEvent('input');
 await expect(page.locator('#imageExplanation')).toContainText('640 px máximo; color: gris');
 await page.goto(url+'#s11');
 await page.locator('#audioGain').fill('0');await page.locator('#audioGain').dispatchEvent('input');
 await expect(page.locator('#audioMeasure')).toContainText('0.0000');
 await page.locator('#audioGain').fill('150');await page.locator('#audioGain').dispatchEvent('input');
 await expect(page.locator('#audioGainValue')).toHaveText('150');
});
test('S11: cuaderno en ruta pública y sin formularios de ensayo libres',async({page,request})=>{
 const r=await request.get('/Cuadernos/11_ETL_Audio_Imagenes.ipynb');
 expect(r.status()).toBe(200);
 const nb=await r.json();
 expect(nb.cells.length).toBeGreaterThanOrEqual(20);
 const source=nb.cells.map(c=>(c.source||[]).join('')).join('\n');
 expect(source).toContain('s11.download_sources');
 expect(source).toContain('PAQUETE S11 VERIFICADO');
 expect(source).not.toContain('Escribe tu reflexión');
 await page.goto(url+'#s15');
 await expect(page.locator('textarea')).toHaveCount(0);
});
for(const width of [390,1366]){
 test('S11 responsive '+width,async({page})=>{
  await page.setViewportSize({width,height:800});
  for(const hash of ['#s1','#s8','#s11','#s17']){
   await page.goto(url+hash);
   const vw=await page.evaluate(()=>({screen:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth}));
   expect(vw.scroll).toBeLessThanOrEqual(vw.screen+2);
   await expect(page.locator('section.slide.active h1')).toBeVisible();
  }
 });
}
