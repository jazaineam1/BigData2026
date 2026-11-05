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
  await expect(page.locator('.asset img')).toHaveCount(2); // RAW y derivado
  await expect(page.locator('.asset canvas')).toHaveCount(1); // histograma dibujado
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

test('integración con la presentación: enlace de S10 abre ETL propio sin tercer recurso LMS',async({page})=>{
  await page.goto('/Presentaciones/s10-imagenes-audio.html#s23');
  await expect(page.locator('.slide')).toHaveCount(23);
  await page.locator('#s10EtlLaunch').click();
  await expect(page).toHaveURL(/\/assets\/s10\/etl-reactivo\.html/);
  await expect(page.locator('h1')).toContainText('imágenes y audios');
});

test('integridad negativa: ZIP manipulado es rechazado por CRC o SHA',async({page})=>{
  const fs=require('node:fs/promises');
  await page.goto(route);
  await page.locator('#demo').click();
  await expect(page.locator('#status')).toContainText('L: 2 filas');
  const pending=page.waitForEvent('download');
  await page.locator('#save').click();
  const download=await pending;
  const bytes=Buffer.from(await fs.readFile(await download.path()));
  const offset=bytes.indexOf(Buffer.from('RIFF'));
  expect(offset).toBeGreaterThan(0);
  bytes[offset+50]=bytes[offset+50]^1;
  await page.locator('#importZip').setInputFiles({name:'manipulado.zip',mimeType:'application/zip',buffer:bytes});
  await expect(page.locator('#verifyStatus')).toContainText('PAQUETE RECHAZADO');
});

test('contrato interoperable v2: el ZIP del navegador se abre en Python sin duplicar RAW',async({page})=>{
  const fs=require('node:fs/promises');
  const path=require('node:path');
  const os=require('node:os');
  const {execFileSync}=require('node:child_process');
  await page.goto(route);
  await page.locator('#demo').click();
  await expect(page.locator('#catalogBody')).toContainText('imagen_demo.png');
  const pending=page.waitForEvent('download');
  await page.locator('#save').click();
  const download=await pending;
  const location=await download.path();
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'s10-bridge-'));
  const script="import json,sys; from utils.s10_asset_bridge import importar_zip_etl_web; r=importar_zip_etl_web(sys.argv[1],sys.argv[2]); print(json.dumps({'cantidad':r['cantidad'],'sha_lote':r['sha_lote'],'carpeta':r['carpeta'],'schema':[x['schema_version'] for x in r['registros']],'ids':[x['asset_id'] for x in r['registros']]}))";
  const run=()=>JSON.parse(execFileSync('python3',['-c',script,location,root],{cwd:process.cwd(),encoding:'utf8'}).trim());
  try{
    const first=run();
    expect(first.cantidad).toBe(2);
    expect(first.schema).toEqual(['s10-asset-v2','s10-asset-v2']);
    const second=run();
    expect(second.sha_lote).toBe(first.sha_lote);
    expect(second.carpeta).toBe(first.carpeta); // la misma importación no duplica lotes
    expect(await fs.readFile(path.join(first.carpeta,'catalogo_importado.jsonl'),'utf8')).toContain('"source_kind"');
  }finally{await fs.rm(root,{recursive:true,force:true})}
});

test('el mismo archivo RAW se deduplica aunque se suba dos veces',async({page})=>{
  await page.goto(route);
  const url=await page.evaluate(()=>{const c=document.createElement('canvas');c.width=10;c.height=10;c.getContext('2d').fillRect(0,0,4,4);return c.toDataURL('image/png')});
  const image=Buffer.from(url.split(',')[1],'base64');
  const file={name:'duplicada.png',mimeType:'image/png',buffer:image};
  await page.locator('#files').setInputFiles(file);
  await expect(page.locator('#catalogBody')).toContainText('duplicada.png');
  await page.locator('#files').setInputFiles(file);
  await expect(page.locator('#status')).toContainText('duplicado');
  await expect(page.locator('#catalogBody tr')).toHaveCount(1);
});
