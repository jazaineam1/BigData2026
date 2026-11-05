const {test,expect}=require('@playwright/test');
const route='/assets/s10/etl-reactivo.html';

test('ejemplo autónomo: E/T/L, resultado reactivo, ZIP y relectura con hashes',async({page})=>{
  const jsErrors=[];page.on('pageerror',e=>jsErrors.push(e.message));
  await page.goto(route);
  await expect(page.locator('#save')).toBeDisabled();
  await page.locator('#demo').click();
  await expect(page.locator('#catalogBody tr')).toHaveCount(2);
  await expect(page.locator('#status')).toContainText('L: 2 filas');
  await expect(page.locator('.asset')).toHaveCount(2);
  const hash=await page.locator('#catalogBody tr').first().locator('td').last().innerText();
  await page.locator('#maxSide').selectOption('160');
  await expect(page.locator('#manifestPreview')).toContainText('"lado_maximo": 160');
  await expect(page.locator('#status')).toContainText('L: 2 filas');
  const nextHash=await page.locator('#catalogBody tr').first().locator('td').last().innerText();
  expect(nextHash).toBe(hash); // el RAW no debe mutar por cambiar el perfil
  const downloadPromise=page.waitForEvent('download');
  await page.locator('#save').click();
  const download=await downloadPromise;
  expect(download.suggestedFilename()).toMatch(/^S10_ETL_evidencia_.*\.zip$/);
  const archive=await download.path();
  await page.locator('#importZip').setInputFiles(archive);
  await expect(page.locator('#verifyStatus')).toContainText('PAQUETE VERIFICADO');
  await expect(page.locator('#catalogBody tr')).toHaveCount(2);
  expect(jsErrors).toEqual([]);
});

test('imagen propia: archivo subido, derivado y descripción sin inferencia semántica',async({page})=>{
  await page.goto(route);
  const dataUrl=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=120;c.height=80;const g=c.getContext('2d');g.fillStyle='#28786c';g.fillRect(0,0,120,80);g.fillStyle='#ffffff';g.fillRect(20,20,40,30);return c.toDataURL('image/png')});
  const png=Buffer.from(dataUrl.split(',')[1],'base64');
  await page.locator('#files').setInputFiles({name:'mi_imagen.png',mimeType:'image/png',buffer:png});
  await expect(page.locator('#catalogBody')).toContainText('mi_imagen.png');
  await expect(page.locator('#catalogBody tr')).toHaveCount(1);
  await expect(page.locator('.asset')).toContainText('No identifica objetos');
  await page.locator('#gray').check();
  await expect(page.locator('#manifestPreview')).toContainText('"gris": true');
  await expect(page.locator('#status')).toContainText('L: 1 filas');
});

test('control de calidad: rechaza archivos superiores al límite y no guarda respuestas libres',async({page})=>{
  await page.goto(route);
  const tooBig=Buffer.alloc(8*1024*1024+1,42);
  await page.locator('#files').setInputFiles({name:'grande.png',mimeType:'image/png',buffer:tooBig});
  await expect(page.locator('#status')).toContainText('supera 8 MiB');
  await expect(page.locator('#save')).toBeDisabled();
  await expect(page.locator('textarea')).toHaveCount(0);
  await expect(page.locator('input[type=text]')).toHaveCount(0);
});

for(const width of [390,1366]){
 test('ETL reactivo adaptable a '+width+' px',async({page})=>{
  await page.setViewportSize({width,height:844});
  await page.goto(route);
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2)).toBe(true);
 });
}
