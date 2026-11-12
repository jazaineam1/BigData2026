const {test,expect}=require('@playwright/test');
const route='/Presentaciones/s11-videoclase-ocr-asr-embeddings.html';

test('S11 vigente: 24 módulos accesibles y navegación estable',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'#s1');
  await expect(page.locator('section.slide')).toHaveCount(24);
  await expect(page.locator('section.slide.active')).toHaveCount(1);
  await expect(page.locator('#count')).toContainText('1 / 24');
  await page.locator('#next').click();
  await expect(page.locator('#count')).toContainText('2 / 24');
  await page.goto(route+'#s24');
  await expect(page.locator('#s24')).toBeVisible();
  await expect(page.locator('#next')).toBeDisabled();
  expect(errors).toEqual([]);
});

test('S11 lectura íntegra: elimina límites y desplazamientos internos',async({page})=>{
  await page.goto(route+'#s1');
  const toggle=page.locator('#s11ReadingToggle');
  await expect(page.locator('body')).toHaveClass(/reading-mode/);
  const module=page.locator('#s1 .lesson-module').first();
  expect(await module.evaluate(el=>getComputedStyle(el).maxHeight)).toBe('none');
  expect(await module.evaluate(el=>getComputedStyle(el).overflowY)).toBe('visible');
  await toggle.click();
  await expect(page.locator('body')).not.toHaveClass(/reading-mode/);
  await expect(toggle).toHaveAttribute('aria-pressed','false');
  await toggle.click();
  await expect(page.locator('body')).toHaveClass(/reading-mode/);
});

test('S11 autoevaluación: retroalimentación específica y no nota oficial',async({page})=>{
  await page.goto(route+'#s1');
  await page.locator('#s11QuizOpen').click();
  await expect(page.locator('#s11QuizDialog')).toBeVisible();
  await page.locator('#s11Q1').selectOption('ocr');
  await page.locator('#s11Q2').selectOption('rank');
  await page.locator('#s11Q3').selectOption('bytes');
  await page.locator('#s11QuizCheck').click();
  await expect(page.locator('#s11QuizFeedback')).toContainText('3 de 3 correctas');
  await expect(page.locator('#s11QuizFeedback')).toContainText('SHА-256'.replace('А','A'));
  await page.locator('#s11QuizClose').click();
  await expect(page.locator('#s11QuizDialog')).not.toBeVisible();
});

for(const width of [390,768,1366]){
  test('S11 presentación vigente, adaptación '+width,async({page})=>{
    await page.setViewportSize({width,height:800});
    await page.goto(route+'#s14');
    await expect(page.locator('#s14')).toBeVisible();
    const result=await page.evaluate(()=>({body:document.documentElement.scrollWidth,screen:window.innerWidth}));
    expect(result.body).toBeLessThanOrEqual(result.screen+2);
  });
}
