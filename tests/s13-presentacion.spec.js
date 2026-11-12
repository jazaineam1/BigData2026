const { test, expect } = require('@playwright/test');
const URL = '/Presentaciones/s13-de-una-maquina-a-un-cluster.html';

test('S13: 32 diapositivas, navegación bidireccional y recursos', async ({ page }) => {
  const errors = []; page.on('pageerror', e => errors.push(e.message));
  await page.goto(URL + '#s1');
  await expect(page.locator('.slide')).toHaveCount(32);
  await expect(page.locator('#s1')).toBeVisible();
  await page.locator('#next').click();
  await expect(page.locator('#s2')).toBeVisible();
  await expect(page.locator('#counter')).toHaveText('2 / 32');
  await page.goto(URL + '#s32');
  await expect(page.locator('#s32')).toContainText('PySpark');
  await page.locator('#prev').click();
  await expect(page.locator('#s31')).toBeVisible();
  expect(errors).toEqual([]);
});

test('S13: elegir herramienta, auditar UNSPSC y simular HDFS', async ({ page }) => {
  await page.goto(URL + '#s3');
  await page.locator('#unspscInput').fill('V1.80111600');
  await page.locator('#unspscRun').click();
  await expect(page.locator('#unspscOut')).toContainText('segmento 80');
  await page.locator('#unspscInput').fill('18');
  await page.locator('#unspscRun').click();
  await expect(page.locator('#unspscOut')).toContainText('no válido');

  await page.goto(URL + '#s4');
  await page.locator('[data-answer="pandas"]').click();
  await expect(page.locator('#decisionFeedback')).toContainText('Elección defendible');
  await page.locator('#nextScenario').click();
  await expect(page.locator('#caseText')).toContainText('SQL');

  await page.goto(URL + '#s6');
  await page.locator('#failNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('Nodo 2 desconectado');
  await page.locator('#restoreNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('dos copias');
});

test('S13: MapReduce muestra el fallo de media de medias', async ({ page }) => {
  await page.goto(URL + '#s7');
  await page.locator('#mapRun').click();
  await expect(page.locator('#mapOut')).toContainText('Media global ponderada');
  await expect(page.locator('#mapOut')).toContainText('Diferencia absoluta');
});

test('S13: grafo diferido y calculadora de costos', async ({ page }) => {
  await page.goto(URL + '#s11');
  await page.locator('#lazyBuild').click();
  await expect(page.locator('#lazyOut')).toContainText('no hubo ejecución');
  await page.locator('#lazyCompute').click();
  await expect(page.locator('#lazyOut')).toContainText('materializados');
  await page.goto(URL + '#s12');
  await page.locator('#costRun').click();
  await expect(page.locator('#costOut')).toContainText('Aceleración extremo a extremo');
  await expect(page.locator('#costOut')).toContainText('operaciones');
});

test('S13: TF-IDF editable, ngramas y ranking coseno', async ({ page }) => {
  await page.goto(URL + '#s15');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyOutput')).toContainText('computadores');
  await page.locator('#tfDoc2').fill('infraestructura computadores');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyOutput')).toContainText('1,6931');

  await page.goto(URL + '#s16');
  await page.locator('#ngramRun').click();
  await expect(page.locator('#ngramOut')).toContainText('Términos:');

  await page.goto(URL + '#s17');
  await page.locator('#cosQuery').fill('hospital');
  await page.locator('#cosRun').click();
  await expect(page.locator('#cosOut')).toContainText('Documento');
  await expect(page.locator('#cosOut')).toContainText('Coseno ≠ probabilidad');
});

test('S13: fuga, F1 y análisis medido 50k', async ({ page }) => {
  await page.goto(URL + '#s18');
  await page.locator('#leakWrong').click();
  await expect(page.locator('#leakOut')).toContainText('Fuga:');
  await page.goto(URL + '#s19');
  await page.locator('#f1Run').click();
  await expect(page.locator('#f1Out')).toContainText('F1 clase');
  await page.goto(URL + '#s23');
  await page.locator('#benchmarkRun').click();
  await expect(page.locator('#benchmarkOut')).toContainText('50.000 train');
  await expect(page.locator('#benchmarkOut')).toContainText('no incluye');
});

test('S13: decisiones, checklist y enlaces coherentes', async ({ page }) => {
  await page.goto(URL + '#s28');
  await page.locator('#gainRun').click();
  await expect(page.locator('#gainOut')).toContainText('TF-IDF');
  await page.goto(URL + '#s30');
  await page.locator('#labCheckRun').click();
  await expect(page.locator('#labFeedback')).toContainText('pasos marcados');
  await page.goto(URL + '#s31');
  await page.locator('[data-quiz-choice="local"]').click();
  await expect(page.locator('#quizResponse')).toContainText('Elección razonable');
  await page.locator('#quizNext').click();
  await expect(page.locator('#quizPrompt')).toContainText('folds');
});

test('S13: pantalla móvil sin desborde horizontal y controles utilizables', async ({ page }) => {
  await page.setViewportSize({ width:390, height:844 });
  await page.goto(URL + '#s15');
  await expect(page.locator('#s15')).toBeVisible();
  await page.locator('#tfidfToyRun').click();
  const sizes=await page.evaluate(()=>({
    content:document.documentElement.scrollWidth,
    viewport:window.innerWidth,
  }));
  expect(sizes.content).toBeLessThanOrEqual(sizes.viewport+4);
  await page.goto(URL + '#s32');
  await expect(page.locator('#s32')).toContainText('Recursos obligatorios');
});
