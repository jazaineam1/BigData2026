const { test, expect } = require('@playwright/test');

test('S09 LAB3/4/8 no crean transferencia abierta ni muro',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s17');
  for(const slide of [17,18,31]){
    await page.evaluate(n=>location.hash='#s'+n,slide);
    await page.waitForTimeout(80);
    await expect(page.locator('.slide.on [data-transfer-for]')).toHaveCount(0);
    await expect(page.locator('.slide.on [data-transfer-field]')).toHaveCount(0);
    await expect(page.locator('.slide.on a[href*="class-wall.html"]')).toHaveCount(0);
  }
});

test('S09 LAB9 explica evidencia sin respuesta abierta en la presentación',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s33');
  await expect(page.getByText('LAB 9 · EVIDENCIA DESDE EL CUADERNO')).toBeVisible();
  await expect(page.getByText(/Sin respuesta abierta/)).toBeVisible();
  await expect(page.locator('.slide.on [data-transfer-field]')).toHaveCount(0);
  await expect(page.locator('.slide.on textarea')).toHaveCount(0);
});
