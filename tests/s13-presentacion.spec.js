const { test, expect } = require('@playwright/test');
const URL = '/Presentaciones/s13-de-una-maquina-a-un-cluster.html';

test('S13 24 pantallas navegables y documentación Dask', async ({page}) => {
  const errors=[]; page.on('pageerror',e=>errors.push(e.message));
  await page.goto(URL+'#s1');
  await expect(page.locator('.slide')).toHaveCount(24);
  await expect(page.locator('#counter')).toHaveText('1 / 24');
  await page.locator('#next').click(); await expect(page.locator('#s2')).toBeVisible();
  await page.goto(URL+'#s24');await expect(page.locator('#s24')).toContainText('PySpark');
  expect(errors).toEqual([]);
});

test('S13 casos útiles reemplazan auditoría de ceros', async ({page}) => {
  await page.goto(URL+'#s3');
  await expect(page.locator('#s3')).not.toContainText('Ceros, duplicados y códigos');
  await page.locator('#casoDask').selectOption('audio');
  await page.locator('#casoRun').click();
  await expect(page.locator('#casoOut')).toContainText('transcribe');
  await page.goto(URL+'#s4');
  await page.locator('[data-answer="pandas"]').click();
  await expect(page.locator('#decisionFeedback')).toContainText('Elección defendible');
});

test('S13 configuración de 1, 2, 4 y 8 workers de una VM', async ({page}) => {
  await page.goto(URL+'#s5');
  await page.locator('#workerConfig').selectOption('4x1');
  await page.locator('#workerRun').click();
  await expect(page.locator('#workersView .wide-node')).toHaveCount(4);
  await expect(page.locator('#workerOut')).toContainText('4 procesos');
  await page.locator('#workerConfig').selectOption('8x1');
  await page.locator('#workerRun').click();
  await expect(page.locator('#workerOut')).toContainText('sobresuscripción');
  await page.goto(URL+'#s9');
  await expect(page.locator('#s9')).toContainText('nproc');
  await expect(page.locator('#s9')).toContainText('free -h');
});

test('S13 MapReduce usa medias ponderadas y rechaza campos vacíos', async ({page}) => {
  await page.goto(URL+'#s7');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapOut')).toContainText('Media global ponderada');
  await page.locator('#mapInput').fill('10,20,30\n50,60');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapOut')).toContainText('observación vacía');
});

test('S13 HDFS representa bloques y réplica conceptual', async ({page}) => {
  await page.goto(URL+'#s6');
  await page.locator('#failNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('Nodo 2 desconectado');
  await page.locator('#restoreNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('dos copias');
});

test('S13 Dask diferido y costo completo en calculadora', async ({page}) => {
  await page.goto(URL+'#s11');
  await page.locator('#lazyBuild').click();
  await expect(page.locator('#lazyOut')).toContainText('no hubo ejecución');
  await page.locator('#lazyCompute').click();
  await expect(page.locator('#lazyOut')).toContainText('materializados');
  await page.goto(URL+'#s12');
  await page.locator('#costRun').click();
  await expect(page.locator('#costOut')).toContainText('Aceleración extremo a extremo');
});

test('S13 TF-IDF enseña el objetivo y una tabla real con L2', async ({page}) => {
  await page.goto(URL+'#s13');
  await expect(page.locator('#s13')).toContainText('¿Por qué convertimos las palabras');
  await page.goto(URL+'#s14');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable table')).toBeVisible();
  await expect(page.locator('#tfidfToyTable th')).toHaveCount(6);
  const hospital=page.locator('#tfidfToyTable tr').filter({has:page.locator('td', {hasText:'hospital'})});
  await expect(hospital).toContainText('1,6931');
  await expect(hospital).toContainText('0,0000');
  await expect(page.locator('#tfidfToyOutput')).toContainText('Norma L2');
  await page.locator('#tfDoc1').fill('constructor computadores');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable')).toContainText('constructor');
  await expect(page.locator('#tfidfToyTable')).not.toContainText('NaN');
});

test('S13 búsqueda por coseno usa el mismo corpus', async ({page}) => {
  await page.goto(URL+'#s15');
  await page.locator('#cosRun').click();
  await expect(page.locator('#cosOut')).toContainText('Documento');
});

test('S13 explica caso útil y simulador 2 y 4 workers', async ({page}) => {
  await page.goto(URL+'#s17');
  await expect(page.locator('#s17')).toContainText('dask_cuando_si.py');
  await page.goto(URL+'#s20');
  await page.locator('#nWorkersSim').selectOption('4');
  await page.locator('#scenarioWorkers').click();
  await expect(page.locator('#scenarioOut')).toContainText('2 tandas');
  await expect(page.locator('#scenarioOut')).toContainText('SIMULACIÓN');
  await expect(page.locator('#s20')).toContainText('Dask real');
});

test('S13 explica los dos modos de Dask y el costo de arranque', async ({page}) => {
  await page.goto(URL+'#s20');
  await expect(page.locator('#s20')).toContainText('--modo texto');
  await page.goto(URL+'#s19');
  await expect(page.locator('#s19')).toContainText('clúster');
});

test('S13 no atribuye equipos personales a estudiantes', async ({page}) => {
  await page.goto(URL+'#s5');
  const html=await page.locator('main').innerText();
  expect(html).not.toMatch(/HP del estudiante|tu HP/i);
  await page.goto(URL+'#s22');
  await page.locator('#labCheckRun').click();
  await expect(page.locator('#labFeedback')).toContainText('pasos marcados');
});

test('S13 pantalla móvil con tabla TF-IDF sin desborde global',async ({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto(URL+'#s14');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable table')).toBeVisible();
  const dims=await page.evaluate(()=>({a:document.documentElement.scrollWidth,b:innerWidth}));
  expect(dims.a).toBeLessThanOrEqual(dims.b+4);
});


test('S13 los ejemplos con workers protegen la creación de procesos', async ({page}) => {
  await page.goto(URL+'#s9');
  await expect(page.locator('#s9')).toContainText('if __name__ == "__main__"');
  await page.goto(URL+'#s17');
  await expect(page.locator('#s17')).toContainText('if __name__ == "__main__"');
});

test('S13 puedo iniciar Streamlit desde la presentación sin otra guía', async ({page}) => {
  await page.goto(URL+'#s8');
  await expect(page.locator('#s8')).toContainText('streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py');
  await expect(page.locator('#s8')).toContainText('8503');
  await page.goto(URL+'#s18');
  await expect(page.locator('#s18')).toContainText('PORTS');
  await expect(page.locator('#s18')).toContainText('Private');
});


test('S13 sincroniza el ejemplo de TF-IDF y el caso de texto real', async ({page}) => {
  await page.goto(URL+'#s13');
  await expect(page.locator('#s13')).toContainText('infraestructura computadores');
  await page.goto(URL+'#s14');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable')).toContainText('1,6931');
  await page.goto(URL+'#s20');
  await expect(page.locator('#s20')).toContainText('--modo texto');
});


test('S13 permite saltar a cinco unidades desde el selector de navegación', async ({page})=>{
  await page.goto(URL+'#s1');
  await expect(page.locator('#unitJump option')).toHaveCount(5);
  await page.locator('#unitJump').selectOption('12');
  await expect(page.locator('#s13')).toBeVisible();
  await expect(page.locator('#s13')).toContainText('TF-IDF');
  await page.locator('#unitJump').selectOption('20');
  await expect(page.locator('#s21')).toBeVisible();
  await expect(page.locator('#counter')).toHaveText('21 / 24');
});

test('S13: cuatro visualizaciones explican MapReduce, costos, tandas y cronómetros',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(URL+'#s7');
  await expect(page.locator('#mapVisual rect')).toHaveCount(3);
  await page.locator('#mapInput').fill('10,20,30\\n50,60');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapVisual rect')).toHaveCount(2);
  await expect(page.locator('#mapVisual')).toContainText('n=3');
  await expect(page.locator('#mapVisual')).toContainText('n=2');
  await expect(page.locator('#mapVisual title')).toHaveCount(1);
  await expect(page.locator('#mapVisual desc')).toHaveCount(1);

  await page.goto(URL+'#s12');
  await page.locator('#costLocal').fill('6');
  await page.locator('#costDask').fill('2');
  await page.locator('#costStart').fill('1');
  await page.locator('#costRepeat').fill('2');
  await page.locator('#costRun').click();
  await expect(page.locator('#costVisual')).toContainText('12,00 s');
  await expect(page.locator('#costVisual')).toContainText('5,00 s');
  await expect(page.locator('#costOut')).toContainText('Distribuido gana');
  await expect(page.locator('#costVisual title')).toHaveCount(1);
  await expect(page.locator('#costVisual desc')).toHaveCount(1);

  await page.goto(URL+'#s19');
  await expect(page.locator('#s19 svg rect')).toHaveCount(5);
  await expect(page.locator('#s19 svg desc')).toHaveCount(1);
  await expect(page.locator('#s19')).toContainText('valores ideales');

  await page.goto(URL+'#s20');
  await page.locator('#nWorkersSim').selectOption('4');
  await page.locator('#nTasksSim').selectOption('12');
  await page.locator('#scenarioWorkers').click();
  await expect(page.locator('#scenarioVisual rect')).toHaveCount(12);
  await expect(page.locator('#scenarioVisual')).toContainText('4 workers');
  await expect(page.locator('#scenarioOut')).toContainText('3 tandas');
  await expect(page.locator('#scenarioVisual title')).toHaveCount(1);
  await expect(page.locator('#scenarioVisual desc')).toHaveCount(1);
  expect(errors).toEqual([]);
});

test('S13: numeración coherente y flujo de seis pasos sin desborde móvil',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto(URL+'#s5');
  await expect(page.locator('#workersView .wide-node')).toHaveCount(4);
  await page.goto(URL+'#s21');
  await expect(page.locator('#s21 .edu-step')).toHaveCount(6);
  const width=await page.evaluate(()=>({document:document.documentElement.scrollWidth,viewport:innerWidth}));
  expect(width.document).toBeLessThanOrEqual(width.viewport+4);
  for(let i=13;i<=24;i++){
    const k=await page.locator('#s'+i+' .kicker').textContent();
    expect(k).toContain(String(i).padStart(2,'0'));
  }
});

test('S13: diagnóstico de altura visible en escritorio sin ocultar problemas',async({page})=>{
  await page.setViewportSize({width:1280,height:720});
  const heights=[];
  for(const n of [1,5,7,12,14,19,20,21]){
    await page.goto(URL+'#s'+n);
    const m=await page.evaluate(()=>({
      scrollHeight:document.documentElement.scrollHeight,
      viewport:innerHeight,
      scrollWidth:document.documentElement.scrollWidth,
      width:innerWidth
    }));
    heights.push({slide:n,extraPx:m.scrollHeight-m.viewport});
    expect(m.scrollWidth).toBeLessThanOrEqual(m.width+4);
  }
  console.log('S13_ALTURA_1280x720',JSON.stringify(heights));
});
