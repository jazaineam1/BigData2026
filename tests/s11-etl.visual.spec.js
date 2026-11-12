const {test,expect}=require('@playwright/test');
const route='/Presentaciones/s11-etl-audio-imagenes.html';

test('S11: historia, 28 diapositivas, enlace directo a Colab y sin video',async({page})=>{
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(route+'#s1');
  await expect(page.locator('.slide')).toHaveCount(31);
  await expect(page.locator('#s1')).toBeVisible();
  await expect(page.locator('#s1 h1')).toContainText('Laura');
  await expect(page.locator('#count')).toHaveText('1 / 31');
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
  const link=page.locator('article.session[data-n="11"] a[href*="s11-videoclase-ocr-asr-embeddings.html"]');
  await expect(link).toBeVisible();
  await link.click();
  await expect(page).toHaveURL(/s11-videoclase-ocr-asr-embeddings.html/);
  await expect(page.locator('#s1')).toBeVisible();
  await page.goto('/lms/data/course.json');
  await expect(page.locator('body')).toContainText('s11-videoclase-ocr-asr-embeddings.html');
});

test('S11 escala: los lotes cambian particiones previstas, no simulan tiempos reales',async({page})=>{
 await page.goto(route+'#s27');
 await expect(page.locator('#scaleTheory')).toContainText('102 RAW distintos');
 await expect(page.locator('#scaleTheory')).toContainText('174 derivados');
 await page.locator('#scaleMode').selectOption('medio');
 await expect(page.locator('#scaleTheory')).toContainText('332 RAW distintos');
 await expect(page.locator('#scaleTheory')).toContainText('564 derivados');
 await page.locator('#scaleBatch').fill('0');
 await page.locator('#scaleBatch').dispatchEvent('input');
 await expect(page.locator('#scaleBatchText')).toHaveText('8');
 await expect(page.locator('#scaleTheory')).toContainText('42 particiones');
 await page.locator('#scaleMode').selectOption('reto');
 await expect(page.locator('#scaleTheory')).toContainText('1432 RAW distintos');
 await expect(page.locator('#scaleTheory')).toContainText('2464 derivados');
 await expect(page.locator('#s27')).toContainText('NO permite concluir');
 await expect(page.locator('#s27')).toContainText('un solo worker');
});

test('S11 contiene E2E integrada: procesa dos archivos y avanza con métricas reales',async({page})=>{
 await page.goto(route+'#s18');
 const frame=page.frameLocator('#s11LiveFrame');
 await expect(frame.locator('#liveMonitor')).toBeVisible();
 await frame.locator('#demo').click();
 await expect(frame.locator('#liveText')).toHaveText('2/2');
 await expect(frame.locator('#liveProgress')).toHaveJSProperty('value',2);
 await expect(frame.locator('#liveRows tr')).toHaveCount(2);
 await expect(frame.locator('#liveKPIs')).toContainText('Fuentes/s:');
 await expect(frame.locator('#status')).toContainText('L: 2 filas');
 await expect(frame.locator('#save')).toBeEnabled();
 await expect(frame.locator('#liveRows')).toContainText('SHA-256 OK');
});

test('S11 E2E permite modificar el audio y recuperar ZIP con huellas',async({page})=>{
 await page.goto('/assets/s11/etl-live.html');
 await page.locator('#demo').click();
 await expect(page.locator('#liveText')).toHaveText('2/2');
 await page.locator('#audioGain').fill('0');
 await page.locator('#audioGain').dispatchEvent('input');
 await expect(page.locator('#liveText')).toHaveText('2/2');
 await expect(page.locator('#cards')).toContainText('RMS 0;');
 const pending=page.waitForEvent('download');
 await page.locator('#save').click();
 const dl=await pending;
 expect(dl.suggestedFilename()).toMatch(/^S11_ETL_Live_evidencia_.*\.zip$/);
 const fs=require('node:fs/promises');
 const buffer=await fs.readFile(await dl.path());
 await page.locator('#importZip').setInputFiles({name:'s11-prueba.zip',mimeType:'application/zip',buffer});
 await expect(page.locator('#verifyStatus')).toContainText('PAQUETE VERIFICADO');
 await expect(page.locator('#liveText')).toHaveText('2/2');
});


test('S11 E2E procesa completo un WAV de 65 s sin corte en 60 segundos',async({page})=>{
  test.setTimeout(90000);
  await page.goto('/assets/s11/etl-live.html');
  // PCM16 mono 16 kHz: silencio de 65 s (fuente original válida, no editorial).
  const sampleRate=16000,duration=65,n=sampleRate*duration;
  const wav=Buffer.alloc(44+n*2);
  wav.write('RIFF',0);wav.writeUInt32LE(wav.length-8,4);
  wav.write('WAVEfmt ',8);wav.writeUInt32LE(16,16);
  wav.writeUInt16LE(1,20);wav.writeUInt16LE(1,22);
  wav.writeUInt32LE(sampleRate,24);wav.writeUInt32LE(sampleRate*2,28);
  wav.writeUInt16LE(2,32);wav.writeUInt16LE(16,34);
  wav.write('data',36);wav.writeUInt32LE(n*2,40);
  await page.locator('#files').setInputFiles({name:'ensayo_65_segundos.wav',mimeType:'audio/wav',buffer:wav});
  await expect(page.locator('#liveText')).toHaveText('1/1',{timeout:65000});
  await expect(page.locator('#status')).toContainText('T: 1 derivados correctos');
  await expect(page.locator('#cards')).toContainText('Audio 65 s');
  await expect(page.locator('#cards')).not.toContainText('Audio de más de 60 s');
  await expect(page.locator('#liveRows')).toContainText('SHA-256 OK');
});

test('S11: diapositiva 29 enseña el mini reto y sus límites sin inventar relaciones',async({page})=>{
 await page.goto(route+'#s29');
 await expect(page.locator('#s29')).toBeVisible();
 await expect(page.locator('#s29')).toContainText('Mini reto');
 await expect(page.locator('#s29')).toContainText('article_id');
 await expect(page.locator('#s29')).toContainText('OCR');
 await expect(page.locator('#s29')).toContainText('MINDS-14');
 await expect(page.locator('#count')).toContainText('29');
});

test('S11: diapositiva 30 guía audio de noticia, ASR, evidencias y separación de fuentes',async({page})=>{
 await page.goto(route+'#s30');
 await expect(page.locator('#s30')).toBeVisible();
 await expect(page.locator('#s30')).toContainText('3530042.wav');
 await expect(page.locator('#s30')).toContainText('MP3');
 await expect(page.locator('#s30')).toContainText('ASR');
 await expect(page.locator('#s30')).toContainText('más de cincuenta compañías');
 await expect(page.locator('#s30')).toContainText('MINDS');
 await expect(page.locator('#count')).toContainText('30');
});
