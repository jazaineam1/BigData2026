const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1366,height:768}});
  const errors=[];page.on('pageerror',e=>errors.push(String(e)));
  // Remote screenshots have official links; avoid external network dependency in CI.
  await page.route('https://**/*',r=>r.abort());
  await page.goto('http://127.0.0.1:4173/Presentaciones/s14-de-dask-a-spark.html#s1');
  const t=async id=>(await page.locator('#'+id).innerText());
  const open=async n=>{await page.locator('#tocBtn').click();await page.locator('#toc a').nth(n-1).click();assert.equal(await t('counter'),n+'/24')};
  assert.equal(await page.locator('.slide.active').count(),1);
  assert.equal(await page.locator('select').count(),0);
  const overflow=[];
  for(let i=1;i<=24;i++){assert.equal(await t('counter'),i+'/24');let box=await page.evaluate(()=>{let s=document.querySelector('.slide.active');return {w:s.scrollWidth,c:s.clientWidth,body:document.documentElement.scrollHeight,viewport:innerHeight}});assert.ok(box.w<=box.c+2,'Horizontal overflow S'+i);if(box.body>box.viewport+35)overflow.push({i,extra:box.body-box.viewport});if(i<24)await page.locator('#next').click()}
  assert.equal(await page.locator('#next').isDisabled(),true);
  await open(3);await page.locator('#dataGB').fill('80');assert.match(await t('memoryResult'),/64 GB/);
  await open(6);await page.locator('#compareNext').click();assert.equal((await t('compareView')).match(/A: 4 · B: 4 · C: 4/g).length,3);
  await open(9);for(let i=0;i<4;i++)await page.locator('#archNext').click();assert.match(await t('archView'),/Task P4/);
  await open(10);await page.locator('#partitionNext').click();assert.match(await t('partitionView'),/12\/12/);
  await open(11);for(let i=0;i<3;i++)await page.locator('#taskNext').click();assert.match(await t('taskView'),/Rondas: 3 · pendientes: 0/);
  await page.locator('#slots').fill('3');await page.locator('#taskNext').click();await page.locator('#taskNext').click();assert.match(await t('taskView'),/Rondas: 2 · pendientes: 0/);
  await open(12);await page.locator('#shuffleNext').click();assert.match(await t('shuffleView'),/A=3, B=3, C=3/);
  await open(13);for(let i=0;i<4;i++)await page.locator('#dagNext').click();assert.match(await t('dagView'),/Ejecución solicitada/);
  await open(18);for(let i=0;i<3;i++)await page.locator('#medNext').click();assert.match(await t('medExplain'),/4000.*6000/);
  await open(21);await page.locator('#versionNext').click();await page.locator('#versionNext').click();await page.locator('#versionRead').click();assert.match(await t('versionView'),/histórica de versión 1/);
  await open(22);await page.locator('#trainNext').click();await page.locator('#trainNext').click();assert.match(await t('trainView'),/0.85/);
  await open(23);for(let i=0;i<3;i++)await page.locator('#mlNext').click();assert.match(await t('mlView'),/0,575/);
  await open(24);assert.match(await t('matrixView'),/0.6190/);await page.locator('#matrixError').click();assert.doesNotMatch(await t('matrixView'),/0.6190/);
  await page.setViewportSize({width:390,height:844});
  for(let i=1;i<=24;i++){await open(i);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2),'Mobile overflow S'+i)}
  assert.deepEqual(errors,[]);console.log('S14: 24 pantallas desktop/móvil, 12 simulaciones/controles, sin errores JS. Scroll desktop >35px:',JSON.stringify(overflow));
  assert.ok(overflow.length===0,'Diapositivas con scroll excesivo: '+JSON.stringify(overflow));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
