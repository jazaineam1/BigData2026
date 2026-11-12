const { test, expect } = require('@playwright/test');
const URL='/Presentaciones/s13-de-una-maquina-a-un-cluster.html';

test('S13: 24 pantallas y navegación por cinco unidades',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(URL+'#s1');
  await expect(page.locator('.slide')).toHaveCount(24);
  await expect(page.locator('#counter')).toHaveText('1 / 24');
  await page.locator('#unitJump').selectOption('12');
  await expect(page.locator('#s13')).toBeVisible();
  await expect(page.locator('#s13')).toContainText('TF-IDF');
  await page.locator('#unitJump').selectOption('20');
  await expect(page.locator('#s21')).toBeVisible();
  await page.goto(URL+'#s24');
  await expect(page.locator('#s24')).toContainText('PySpark');
  expect(errors).toEqual([]);
});

test('S13: la historia principal es distribuir tareas, no entrenar modelos',async({page})=>{
  await page.goto(URL+'#s1');
  await expect(page.locator('#s1')).toContainText('modo datos');
  await expect(page.locator('#s1')).toContainText('simulada');
  const text=await page.locator('main').innerText();
  expect(text).not.toMatch(/HP del estudiante|tu HP|en mi HP/i);
});

test('S13: selector de casos indica el trabajo real de Dask',async({page})=>{
  await page.goto(URL+'#s3');
  await page.locator('#casoDask').selectOption('textos');
  await page.locator('#casoRun').click();
  await expect(page.locator('#casoOut')).toContainText('SECOP');
});

test('S13: seleccionar pandas para una agregación local',async({page})=>{
  await page.goto(URL+'#s4');
  await page.locator('[data-answer="pandas"]').click();
  await expect(page.locator('#decisionFeedback')).toContainText('Elección defendible');
});

test('S13: arquitectura distingue CPU lógicas y workers',async({page})=>{
  await page.goto(URL+'#s5');
  await expect(page.locator('#s5')).toContainText('CPU lógicas');
  await page.locator('#workerConfig').selectOption('4x1');
  await page.locator('#workerRun').click();
  await expect(page.locator('#workersView .wide-node')).toHaveCount(4);
  await page.locator('#workerConfig').selectOption('8x1');
  await page.locator('#workerRun').click();
  await expect(page.locator('#workerOut')).toContainText('sobresuscripción');
});

test('S13: bloques HDFS con recuperación simulada',async({page})=>{
  await page.goto(URL+'#s6');
  await page.locator('#failNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('Nodo 2 desconectado');
  await page.locator('#restoreNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('dos copias');
});

test('S13: MapReduce promedia ponderado y rechaza entradas vacías',async({page})=>{
  await page.goto(URL+'#s7');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapOut')).toContainText('Media global ponderada');
  await page.locator('#mapInput').fill('100,120,\n10,20');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapOut')).toContainText('observación vacía');
});

test('S13: desde la diapositiva se abre el panel Streamlit',async({page})=>{
  await page.goto(URL+'#s8');
  await expect(page.locator('#s8')).toContainText('streamlit run Laboratorios/S13_Codespaces/app_tfidf_unspsc.py');
  await expect(page.locator('#s8')).toContainText('8503');
  await page.locator('#setupCheckRun').click();
  await expect(page.locator('#setupFeedback')).toContainText('pasos');
});

test('S13: los ejemplos de proceso están protegidos y muestran comandos',async({page})=>{
  await page.goto(URL+'#s9');
  await expect(page.locator('#s9')).toContainText('if __name__ == "__main__"');
  await expect(page.locator('#s9')).toContainText('nproc');
  await page.goto(URL+'#s17');
  await expect(page.locator('#s17')).toContainText('if __name__ == "__main__"');
  await expect(page.locator('#s17')).toContainText('--modo datos');
  await expect(page.locator('#s17')).toContainText('--modo espera');
});

test('S13: ejecución diferida y simulador de costos',async({page})=>{
  await page.goto(URL+'#s11');
  await page.locator('#lazyBuild').click();
  await expect(page.locator('#lazyOut')).toContainText('no hubo ejecución');
  await page.locator('#lazyCompute').click();
  await expect(page.locator('#lazyOut')).toContainText('materializados');
  await page.goto(URL+'#s12');
  await page.locator('#costRun').click();
  await expect(page.locator('#costOut')).toContainText('Aceleración extremo a extremo');
});

test('S13: tabla TF-IDF reproduce el mismo minicorpus A-B-C y la norma L2',async({page})=>{
  await page.goto(URL+'#s13');
  await expect(page.locator('#s13')).toContainText('infraestructura computadores');
  await page.goto(URL+'#s14');
  await expect(page.locator('#tfDoc1')).toHaveValue('mantenimiento computadores');
  await expect(page.locator('#tfDoc2')).toHaveValue('infraestructura computadores');
  await expect(page.locator('#tfDoc3')).toHaveValue('hospital mantenimiento');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable th')).toHaveCount(6);
  const hospital=page.locator('#tfidfToyTable tbody tr').filter({hasText:'hospital'});
  await expect(hospital).toContainText('1,6931');
  await expect(hospital).toContainText('0,0000');
  await expect(page.locator('#tfidfToyOutput')).toContainText('Norma L2');
});

test('S13: buscador coseno responde al cambio de consulta',async({page})=>{
  await page.goto(URL+'#s15');
  await page.locator('#cosQuery').fill('hospital');
  await page.locator('#cosRun').click();
  await expect(page.locator('#cosOut')).toContainText('Documento C');
  await expect(page.locator('#cosOut')).toContainText('Coseno ≠ probabilidad');
});

test('S13: dos modos de Dask, medición y simulador honesto',async({page})=>{
  await page.goto(URL+'#s18');
  await expect(page.locator('#s18')).toContainText('preparación de entrada');
  await page.goto(URL+'#s19');
  await expect(page.locator('#s19')).toContainText('--modo datos');
  await expect(page.locator('#s19')).toContainText('--modo espera');
  await page.locator('#nWorkersSim').selectOption('4');
  await page.locator('#scenarioWorkers').click();
  await expect(page.locator('#scenarioOut')).toContainText('2 tandas');
  await expect(page.locator('#scenarioOut')).toContainText('SIMULACIÓN');
});

test('S13: reto y transferencia completan la historia',async({page})=>{
  await page.goto(URL+'#s22');
  await page.locator('#labCheckRun').click();
  await expect(page.locator('#labFeedback')).toContainText('pasos marcados');
  await page.goto(URL+'#s23');
  await page.locator('[data-quiz-choice="local"]').click();
  await expect(page.locator('#quizResponse')).toContainText('Elección razonable');
  await page.locator('#quizNext').click();
  await expect(page.locator('#quizPrompt')).toContainText('folds');
  await page.goto(URL+'#s24');
  await expect(page.locator('#s24')).toContainText('Parquet');
});

test('S13: tabla de TF-IDF usable desde móvil',async({page})=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto(URL+'#s14');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyTable table')).toBeVisible();
  const x=await page.evaluate(()=>({content:document.documentElement.scrollWidth,width:innerWidth}));
  expect(x.content).toBeLessThanOrEqual(x.width+4);
  await expect(page.locator('#unitJump')).toBeVisible();
});
