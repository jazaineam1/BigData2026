const {test,expect}=require('@playwright/test');
const AxeBuilder=require('@axe-core/playwright').default;
const url='/assets/tutoriales/tc2-paso-a-paso.html';
for(const width of [390,768,1366]){
 test('TC2 guía legible y adaptable a '+width+' px',async({page})=>{
   await page.setViewportSize({width,height:880});
   const errors=[];page.on('pageerror',e=>errors.push(e.message));
   await page.goto(url);
   await expect(page.locator('h1')).toContainText('TC2');
   await expect(page.locator('body')).toContainText('14 de noviembre de 2026');
   await expect(page.locator('body')).toContainText('GitHub');
   await expect(page.locator('body')).toContainText('Whisper');
   await expect(page.locator('body')).toContainText('Tesseract');
   await expect(page.locator('input[type=checkbox]')).toHaveCount(41);
   expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2)).toBeTruthy();
   await expect(page.getByRole('link',{name:/Abrir el cuaderno TC2 en Colab/})).toHaveAttribute('href',/Taller_Control_2\.ipynb/);
   expect(errors).toEqual([]);
 });
}
test('TC2 checklist local conserva estado tras recargar y reinicia sin tocar notas',async({page})=>{
 await page.goto(url);
 const boxes=page.locator('input[type=checkbox]');
 await expect(page.locator('#status')).toContainText('0 de 41');
 await boxes.nth(0).check();
 await boxes.nth(3).check();
 await expect(page.locator('#status')).toContainText('2 de 41');
 await page.reload();
 await expect(boxes.nth(0)).toBeChecked();
 await expect(boxes.nth(3)).toBeChecked();
 await page.locator('#clear').click();
 await expect(page.locator('#status')).toContainText('0 de 41');
 await expect(boxes.nth(0)).not.toBeChecked();
 expect(await page.evaluate(()=>localStorage.getItem('bigdata-tc2-checklist-v1'))).toBeNull();
});
test('TC2 sin envío de respuestas ni secretos, accesible por teclado',async({page})=>{
 await page.goto(url);
 await expect(page.locator('textarea')).toHaveCount(0);
 await expect(page.locator('input[type=text],input[type=email],input[type=password]')).toHaveCount(0);
 await page.keyboard.press('Tab');
 const focused=await page.evaluate(()=>document.activeElement?.tagName);
 expect(['A','INPUT','BUTTON']).toContain(focused);
 const accessibility=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();
 expect(accessibility.violations.filter(v=>v.impact==='critical'||v.impact==='serious')).toEqual([]);
});
test('TC2 funciona con modo oscuro sin desbordes',async({page})=>{
 await page.emulateMedia({colorScheme:'dark',reducedMotion:'reduce'});
 await page.setViewportSize({width:390,height:844});
 await page.goto(url);
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+2)).toBeTruthy();
 const bg=await page.locator('body').evaluate(el=>getComputedStyle(el).backgroundColor);
 expect(bg).not.toBe('rgba(0, 0, 0, 0)');
});

test('TC2 ejemplos pedagógicos y recuperación accesibles por teclado',async({page})=>{
 await page.goto(url);
 const details=page.locator('details');
 await expect(details).toHaveCount(8);
 await details.first().locator('summary').focus();
 await page.keyboard.press('Enter');
 await expect(details.first()).toHaveAttribute('open','');
 await expect(details.first()).toContainText('recuperación');
 await expect(page.locator('body')).toContainText('Qué NO permite concluir');
});
