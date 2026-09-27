const { test, expect } = require('@playwright/test');

test('S09 teacher wall embebido carga sin errores JavaScript', async ({ page }) => {
  const runtimeErrors=[];
  page.on('pageerror', err => runtimeErrors.push(err.message));
  page.on('console', msg => {
    if(msg.type()==='error' && /ReferenceError|TypeError|SyntaxError|Uncaught/i.test(msg.text())) runtimeErrors.push(msg.text());
  });

  await page.addInitScript(() => {
    const auth={
      token:'token-teacher-qa',
      expires_at:'2099-12-31T23:59:59Z',
      auth_session_id:'teacher-qa',
      user:{id:'teacher',username:'teacher',display_name:'Docente QA',role:'teacher'}
    };
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  });

  await page.route('**/functions/v1/bigdata-session**', async route => {
    const req=route.request(),url=new URL(req.url()),action=url.searchParams.get('action');
    if(req.method()==='GET' && action==='teacher_wall') {
      return route.fulfill({
        status:200,
        contentType:'application/json',
        body:JSON.stringify({
          viewer:{id:'teacher',username:'teacher',display_name:'Docente QA',role:'teacher'},
          session:{session_number:9,title:'Búsqueda semántica',summary:'',status:'visible',metadata:{}},
          students:[],
          ranking:[],
          activity_stats:[],
          challenge_stats:[],
          session_window:null,
          refreshed_at:new Date().toISOString()
        })
      });
    }
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });

  await page.setViewportSize({width:1280,height:720});
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?wall=docente');
  await expect(page.locator('#teacherWall')).toHaveClass(/on/);
  await expect(page.getByText('S09 Teacher Wall')).toBeVisible();
  await expect(page.locator('#teacherStatus')).toContainText('WALL actualizado');
  expect(runtimeErrors).toEqual([]);
});
