const { test, expect } = require('@playwright/test');

const URL = '/Presentaciones/s13-de-una-maquina-a-un-cluster.html';

test('S13: 40 pantallas, navegación y ejemplos interactivos', async ({ page }) => {
  const errores = [];
  page.on('pageerror', error => errores.push(error.message));
  await page.goto(URL + '#s1');
  await expect(page.locator('.slide')).toHaveCount(40);
  await expect(page.locator('#s1')).toBeVisible();

  await page.locator('#next').click();
  await expect(page.locator('#s2')).toBeVisible();
  await expect(page.locator('#counter')).toHaveText('2 / 40');

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
  await page.goto(URL + '#s36');
  await expect(page.locator('#s36')).toContainText('PySpark');
});
