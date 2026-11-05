const {test,expect}=require('@playwright/test');
const route='/Presentaciones/s11-etl-audio-imagenes.html';

test('S11: historia, 28 diapositivas, enlace directo a Colab y sin video',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'#s1');
  await expect(page.locator('.slide')).toHaveCount(28);
  await expect(page.locator('#s1')).toBeVisible();
  await expect(page.locator('#s1 h1')).toContainText('Laura');
  await expect(page.locator('#count')).toHaveText('1 / 28');
  await expect(page.locator('a[href*="11_ETL_Audio_Imagenes.ipynb"]')).not.toHaveCount(0);
  await expect(page.locator('#s1')).toContainText('no trabajaremos video');
  await page.locator('#next').click();
  await expect(page).toHaveURL(/#s2$/);
  await expect(page.locator('#s2')).toBeVisible();
  await page.goto(route+'#s25');
  await expect(page.locator('#s25')).toBeVisible();
  expect(errors).toEqual([]);
});

test('simulador de imagen: intensidad y perfil cambian métrica real',async({page})=>{
  await page.goto(route+'#s9');
  const first=await page.locator('#lumaDemo').innerText();
  expect(first).toContain('Luminancia media');
  await page.locator('#brillo').fill('160');
  await page.locator('#brillo').dispatchEvent('input');
  await expect(page.locator('#brilloTxt')).toHaveText('160 %');
  const second=await page.locator('#lumaDemo').innerText();
  expect(second).not.toBe(first);
  await page.locator('#grisDemo').selectOption('gris');
  await expect(page.locator('#lumaDemo')).toContainText('54400 píxeles');
});

test('simulador de audio: ganancias y recortes medidos sin transcripción falsa',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'#s14');
  await page.locator('#gainDemo').fill('0');
  await page.locator('#gainDemo').dispatchEvent('input');
  await expect(page.locator('#rmsDemo')).toContainText('0.000');
  await page.locator('#gainDemo').fill('200');
  await page.locator('#gainDemo').dispatchEvent('input');
  await expect(page.locator('#rmsDemo')).not.toContainText('0.000');
  await expect(page.locator('#clipDemo')).not.toContainText('Muestras recortadas: 0 /');
  await page.locator('#hearDemo').click();
  expect(errors).toEqual([]);
});

test('tutorial autónomo: ocho comprobaciones locales persisten sin ser nota oficial',async({page})=>{
  await page.goto(route+'#s19');
  await page.locator('[data-check="prep"]').check();
  await page.locator('[data-check="decision"]').check();
  await expect(page.locator('#checkCount')).toContainText('2/9');
  await page.reload();
  await expect(page.locator('[data-check="prep"]')).toBeChecked();
  await expect(page.locator('[data-check="decision"]')).toBeChecked();
  await expect(page.locator('#checkCount')).toContainText('2/9');
  await expect(page.locator('textarea')).toHaveCount(0);
  await expect(page.locator('input[type="text"]')).toHaveCount(0);
});

test('autoevaluación sobre el artefacto generado, sin respuestas abiertas',async({page})=>{
  await page.goto(route+'#s26');
  await page.locator('input[name="qaS11"][value="1"]').check();
  await page.locator('#reviewQuiz').click();
  await expect(page.locator('#reviewQuizFeedback')).toContainText('Un hash solo compara bytes');
  await page.locator('input[name="qaS11"][value="2"]').check();
  await page.locator('#reviewQuiz').click();
  await expect(page.locator('#reviewQuizFeedback')).toContainText('Correcto');
});

for(const width of [390,1366]){
  test('S11 responsive '+width,async({page})=>{
    await page.setViewportSize({width,height:800});
    for(const s of [1,9,14,18,26,28]){
      await page.goto(route+'#s'+s);
      expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+2)).toBe(true);
    }
  });
}

test('la portada y el registro de curso abren S11 en un clic',async({page})=>{
  await page.goto('/index.html');
  const link=page.locator('article.session[data-n="11"] a[href*="s11-etl-audio-imagenes.html"]');
  await expect(link).toBeVisible();
  await link.click();
  await expect(page).toHaveURL(/s11-etl-audio-imagenes.html/);
  await expect(page.locator('#s1')).toBeVisible();
  await page.goto('/lms/data/course.json');
  await expect(page.locator('body')).toContainText('s11-etl-audio-imagenes.html');
});
