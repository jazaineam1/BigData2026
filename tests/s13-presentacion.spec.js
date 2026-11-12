const { test, expect } = require('@playwright/test');

const URL = '/Presentaciones/s13-de-una-maquina-a-un-cluster.html';

test('S13: 60 pantallas, navegación y ejemplos interactivos', async ({ page }) => {
  const errores = [];
  page.on('pageerror', error => errores.push(error.message));
  await page.goto(URL + '#s1');
  await expect(page.locator('.slide')).toHaveCount(60);
  await expect(page.locator('#s1')).toBeVisible();

  await page.locator('#next').click();
  await expect(page.locator('#s2')).toBeVisible();
  await expect(page.locator('#counter')).toHaveText('2 / 60');

  await page.goto(URL + '#s3');
  await page.locator('[data-answer="pandas"]').click();
  await expect(page.locator('#decisionFeedback')).toContainText('Elección razonable');
  await page.locator('#nextScenario').click();
  await expect(page.locator('#caseText')).toContainText('SQL');

  await page.goto(URL + '#s9');
  await page.locator('#failNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('otra copia');
  await page.locator('#restoreNode').click();
  await expect(page.locator('#hdfsFeedback')).toContainText('dos ubicaciones');

  await page.goto(URL + '#s35');
  await page.locator('[data-q="correct"]').click();
  await expect(page.locator('#quizResponse')).toContainText('Correcto');
  expect(errores).toEqual([]);
});

test('S13: tutorial legible y sin desborde horizontal en móvil', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(URL + '#s13');
  await expect(page.locator('#s13')).toBeVisible();
  await expect(page.locator('#s13')).toContainText('Codespaces');
  const anchura = await page.evaluate(() => ({
    contenido: document.documentElement.scrollWidth,
    pantalla: window.innerWidth,
  }));
  expect(anchura.contenido).toBeLessThanOrEqual(anchura.pantalla + 4);
  await page.goto(URL + '#s60');
  await expect(page.locator('#s60')).toContainText('PySpark');
});

test('S13: ampliación de 26 mil procesos SECOP y entrenamiento de un solo XGBoost', async ({page}) => {
  await page.goto(URL + '#s36');
  await expect(page.locator('#s36')).toContainText('26.000');
  await page.goto(URL + '#s38');
  await expect(page.locator('#s38')).toContainText('dxgb.train');
  await page.goto(URL + '#s39');
  await expect(page.locator('#s39')).toContainText('embeddinggemma-2:270m');
  await expect(page.locator('#s39')).toContainText('LinearSVC');
});

test('S13: calculadora de TF-IDF reacciona al contenido editado', async ({page}) => {
  await page.goto(URL+'#s44');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyOutput')).toContainText('computadores');
  await page.locator('#tfDoc2').fill('hospital infraestructura');
  await page.locator('#tfidfToyRun').click();
  await expect(page.locator('#tfidfToyOutput')).toContainText('computadores');
  await expect(page.locator('#tfidfToyOutput')).toContainText('1.6931');
});
test('S13: 1k real EmbeddingGemma, 50k fijo y herramientas', async ({page}) => {
  await page.goto(URL+'#s51');
  await expect(page.locator('#s51')).toContainText('50.000');
  await page.goto(URL+'#s56');
  await expect(page.locator('#s56')).toContainText('0,47586');
  await page.goto(URL+'#s57');
  await expect(page.locator('#s57')).toContainText('8503');
});
