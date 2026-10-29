const {test,expect}=require('@playwright/test');

async function openLab(page,slide=21){
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s'+slide);
  await page.locator('.s09v-float').click();
  const dialog=page.locator('#s09VectorLab');
  await expect(dialog).toBeVisible();
  await expect(dialog).toContainText('SIMULACIÓN LOCAL');
  return dialog;
}
async function gotoTab(dialog,tab){await dialog.locator('[data-tab="'+tab+'"]').click()}
async function readyIndex(dialog){
  await gotoTab(dialog,'indice');
  await dialog.locator('[data-action="create-index"]').click();
  await expect(dialog.locator('.s09v-state')).toContainText('pendiente');
  await dialog.locator('[data-action="ready-index"]').click();
  await expect(dialog.locator('.s09v-state')).toContainText('disponible (simulado)');
}
test('S09 laboratorio abre desde S21, mantiene el curso y se oculta antes de S21',async({page})=>{
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s20');
  await expect(page.locator('.s09v-float')).toBeHidden();
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s21');
  const dialog=await openLab(page);
  await expect(dialog.locator('[role="tab"]')).toHaveCount(5);
  await expect(dialog).toContainText('Del documento al índice');
  await expect(dialog).toContainText('Estos dos números son ficticios');
  await dialog.locator('[data-action="close"]').click();
  await expect(dialog).toBeHidden();
  await expect(page.locator('#s21')).toContainText('AQUÍ NOS HABÍAMOS QUEDADO');
});
test('S09 documento: upsert idempotente sin afirmar persistencia remota',async({page})=>{
  const dialog=await openLab(page);
  await expect(dialog.locator('.s09v-metric')).toContainText('8');
  await dialog.locator('#s09v-newtitle').fill('Reparación de aeronaves de prueba');
  await dialog.locator('[data-action="upsert"]').click();
  await expect(dialog.locator('.s09v-metric')).toContainText('9');
  await expect(dialog).toContainText('DEMO-009');
  await dialog.locator('[data-action="upsert"]').click();
  await expect(dialog.locator('.s09v-metric')).toContainText('9');
  await expect(dialog).toContainText('Upsert repetido');
  await expect(dialog).toContainText('no calcula un nuevo embedding');
});
test('S09 índice exige campo, dimensionalidad y transición pendiente -> disponible',async({page})=>{
  const dialog=await openLab(page);
  await gotoTab(dialog,'indice');
  await expect(dialog.locator('[data-action="ready-index"]')).toBeDisabled();
  await dialog.locator('#s09v-dim').selectOption('384');
  await dialog.locator('[data-action="create-index"]').click();
  await expect(dialog).toContainText('Índice incompatible');
  await expect(dialog.locator('.s09v-state')).toContainText('sin índice');
  await dialog.locator('#s09v-dim').selectOption('2');
  await dialog.locator('[data-action="create-index"]').click();
  await expect(dialog.locator('.s09v-state')).toContainText('pendiente');
  await gotoTab(dialog,'consulta');
  await expect(dialog.locator('[data-action="run-query"]')).toBeDisabled();
  await gotoTab(dialog,'indice');
  await dialog.locator('[data-action="ready-index"]').click();
  await gotoTab(dialog,'consulta');
  await expect(dialog.locator('[data-action="run-query"]')).toBeEnabled();
  await gotoTab(dialog,'indice');
  await dialog.locator('#s09v-field').selectOption('objeto');
  await expect(dialog.locator('.s09v-state')).toContainText('sin índice');
  await gotoTab(dialog,'consulta');
  await expect(dialog.locator('[data-action="run-query"]')).toBeDisabled();
});
test('S09 consulta, filtro y ANN conceptual: parámetros invalidan el ranking anterior',async({page})=>{
  const dialog=await openLab(page);
  await readyIndex(dialog);
  await gotoTab(dialog,'consulta');
  await dialog.locator('[data-action="run-query"]').click();
  await expect(dialog.locator('.s09v-result')).toHaveCount(3);
  await expect(dialog).toContainText('Exacta en la muestra');
  await dialog.locator('#s09v-filter').selectOption('A');
  await expect(dialog).toContainText('vuelve a ejecutar');
  await expect(dialog.locator('.s09v-result')).toHaveCount(0);
  await dialog.locator('[data-action="run-query"]').click();
  await expect(dialog).toContainText('filtro entidad A');
  await dialog.locator('#s09v-mode').selectOption('ann');
  await dialog.locator('#s09v-budget').fill('2');
  await dialog.locator('[data-action="run-query"]').click();
  await expect(dialog).toContainText('Aproximada ilustrativa');
  await expect(dialog).toContainText('Coincidencia con Top-k exacto');
  await expect(dialog).toContainText('no el índice HNSW real');
});
test('S09 precisión exige juicios completos y no convierte simulación en Atlas real',async({page})=>{
  const dialog=await openLab(page);
  await readyIndex(dialog);
  await gotoTab(dialog,'consulta');
  await dialog.locator('[data-action="run-query"]').click();
  await gotoTab(dialog,'evaluacion');
  await expect(dialog.locator('.s09v-metric')).toContainText('Faltan 3 juicios');
  await dialog.locator('[data-action="judge"][data-judge="yes"]').first().click();
  await expect(dialog.locator('.s09v-metric')).toContainText('Faltan 2 juicios');
  await dialog.locator('[data-action="judge"][data-judge="yes"]').nth(1).click();
  await dialog.locator('[data-action="judge"][data-judge="yes"]').nth(2).click();
  await expect(dialog.locator('.s09v-metric')).toContainText('Precision@3');
  await expect(dialog.locator('.s09v-metric')).toContainText('1.00');
  await gotoTab(dialog,'evidencia');
  const report=await page.evaluate(()=>window.S09VectorLab.getState().report);
  expect(report.tipo).toBe('SIMULACION_DIDACTICA_LOCAL_2D');
  expect(report.motor_real_atlas_ejecutado).toBe(false);
  expect(report.modelo_E5_ejecutado).toBe(false);
  expect(report.consulta.ids).toHaveLength(3);
  await expect(dialog).toContainText('s09_simulacion_local.json');
  await expect(dialog.locator('a[href*="colab.research.google.com"]')).toBeVisible();
});
for(const viewport of [{width:1366,height:768},{width:390,height:844}]){
  test('S09 laboratorio adaptable y accesible '+viewport.width+'x'+viewport.height,async({page})=>{
    await page.setViewportSize(viewport);
    const dialog=await openLab(page,28);
    await gotoTab(dialog,'consulta');
    const dims=await dialog.evaluate(el=>({scrollWidth:el.scrollWidth,clientWidth:el.clientWidth,dialogHeight:el.getBoundingClientRect().height,innerHeight:window.innerHeight}));
    expect(dims.scrollWidth).toBeLessThanOrEqual(dims.clientWidth+4);
    expect(dims.dialogHeight).toBeLessThanOrEqual(dims.innerHeight);
    await page.keyboard.press('Escape');
    await expect(dialog).toBeHidden();
    await expect(page.locator('.s09v-float')).toBeVisible();
  });
}
