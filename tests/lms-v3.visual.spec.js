const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

const viewports = [
  { name: 'laptop-1280', width: 1280, height: 720 },
  { name: 'laptop-1366', width: 1366, height: 768 },
  { name: 'desktop-1536', width: 1536, height: 864 },
  { name: 'desktop-1920', width: 1920, height: 1080 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'phone-390', width: 390, height: 844 },
  { name: 'phone-412', width: 412, height: 915 },
];

async function assertNoHorizontalOverflow(page, label) {
  const result = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    innerWidth: window.innerWidth,
    bodyWidth: document.body.scrollWidth
  }));
  expect(result.scrollWidth, label + ' document overflow').toBeLessThanOrEqual(result.innerWidth + 2);
  expect(result.bodyWidth, label + ' body overflow').toBeLessThanOrEqual(result.innerWidth + 2);
}

async function assertVisibleSvgContained(page, label) {
  const failures = await page.evaluate(() => {
    const visible = el => {
      const r=el.getBoundingClientRect(),s=getComputedStyle(el);
      return s.display!=='none'&&s.visibility!=='hidden'&&r.width>1&&r.height>1;
    };
    const out=[];
    for (const svg of document.querySelectorAll('svg')) {
      if(!visible(svg)) continue;
      const host=svg.closest('.diagram,.card,.panel,.lab,.slide')||svg.parentElement;
      if(!host) continue;
      const a=svg.getBoundingClientRect(),b=host.getBoundingClientRect(),tol=3;
      if(a.left < b.left-tol || a.right > b.right+tol) {
        out.push({id:svg.id||null,svg:{left:a.left,right:a.right,width:a.width},host:{class:host.className,left:b.left,right:b.right,width:b.width}});
      }
    }
    return out;
  });
  expect(failures, label + ' SVG fuera de contenedor').toEqual([]);
}

async function mockAuth(page, role='student') {
  await page.addInitScript(({role}) => {
    localStorage.setItem('andesdb.lms.auth.v1',JSON.stringify({
      token:'qa-token',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'qa',
      user:{id:'00000000-0000-0000-0000-000000000001',username:'qa',display_name:'Estudiante QA',role}
    }));
  }, {role});
}

const sessionModel = {
  viewer:{id:'00000000-0000-0000-0000-000000000001',username:'qa',display_name:'Estudiante QA',role:'student'},
  run:{id:'11111111-1111-1111-1111-111111111111',title:'Big Data 2026-2S'},
  session:{session_number:9,title:'Cuando las palabras no coinciden: búsqueda semántica y bases vectoriales',summary:'Búsqueda semántica y recuperación híbrida.',status:'visible',metadata:{estimated_minutes:180,outcomes:['Diferenciar búsqueda lexical y semántica','Interpretar similitud coseno','Evaluar un Top-k']}},
  activities:[
    {code:'bd-s09-presentation',title:'Presentación S09',kind:'resource',required:true,points:0,metadata:{resource_type:'presentation',completion_rule:'visit'}},
    {code:'bd-s09-c1',title:'D1 · mecanismos de búsqueda',kind:'checkpoint',required:true,points:1,metadata:{completion_rule:'mastery',slide:9,evidence:'Distingue búsqueda lexical y semántica.'}},
    {code:'bd-s09-notebook',title:'Cuaderno S09',kind:'resource',required:true,points:0,metadata:{resource_type:'notebook',completion_rule:'visit'}},
    {code:'bd-s09-lab3',title:'LAB 3 · Vecinos y Top-k',kind:'lab',required:true,points:0,metadata:{completion_rule:'evidence',slide:17,evidence:'Resultado propio + decisión + alternativa + límite.'}}
  ],
  resources:[
    {id:'r1',resource_type:'presentation',title:'Presentación S09',url:'../Presentaciones/s09-de-palabras-a-significado.html#s1',metadata:{tracked_activity:'bd-s09-presentation'}},
    {id:'r2',resource_type:'notebook',title:'Cuaderno S09',url:'https://example.com/notebook',metadata:{tracked_activity:'bd-s09-notebook'}}
  ],
  session_progress:{status:'in_progress',active_seconds:540},
  activity_progress:[
    {activity_code:'bd-s09-presentation',status:'in_progress',attempts:1,metadata:{visited:true}}
  ],
  resume:{slide:7,label:'Embeddings',chapter:'SEMÁNTICA'},
  catalog:[{code:'bd-s09-lab3',evaluator:'seeded-numeric',seeded:true,version:1}],
  seeds:{'bd-s09-lab3':'0000000000000001'},
  evidence:[],
  summary:{total_activities:4,required_activities:4,attempted:1,completed:0,resource_visited:1,resource_total:2,checkpoint_mastered:0,checkpoint_total:1}
};

async function mockSessionApi(page, role='student') {
  await mockAuth(page,role);
  let wallPublished=false;
  await page.route('**/functions/v1/bigdata-session**', async route => {
    const req=route.request(),url=new URL(req.url());
    const action=url.searchParams.get('action');
    if(req.method()==='GET' && action==='teacher_wall') {
      const model={...sessionModel,viewer:{...sessionModel.viewer,role:'teacher',display_name:'Docente QA'},students:[],ranking:[],activity_stats:[],challenge_stats:[],session_window:null,refreshed_at:new Date().toISOString()};
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(model)});
    }
    if(req.method()==='GET') return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(sessionModel)});
    const body=req.postDataJSON?.()||{};
    if(body.action==='lab_code')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,code:'ABCD2345',expires_at:'2099-12-31T23:59:59Z'})});
    if(body.action==='evidence')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,completed:true,verdict:'correct',feedback:'Resultado verificado.'})});
    if(body.action==='wall_post'){wallPublished=true;return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,post:{id:'p1'}})})}
    if(body.action==='wall_list'){
      const result=wallPublished?{viewer:sessionModel.viewer,activity:sessionModel.activities.find(a=>a.code==='bd-s09-lab3'),can_view:true,posts:[{id:'p1',author:'Tú',body:'Mantendría k=5 porque el Top-5 ya concentra candidatos aeronáuticos; todavía necesito juicios humanos.',status:'visible',created_at:'2099-01-01T00:00:00Z',reactions:{useful:0,same_doubt:0},my_reactions:[]}]}:{viewer:sessionModel.viewer,activity:sessionModel.activities.find(a=>a.code==='bd-s09-lab3'),can_view:false,posts:[],reason:'publish_first'};
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(result)})
    }
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });
}

test('landing pública no desborda', async ({ page }) => {
  for (const vp of [viewports[0],viewports[5],viewports[6]]) {
    await page.setViewportSize({width:vp.width,height:vp.height});
    await page.goto('/');
    await page.waitForLoadState('domcontentloaded');
    await assertNoHorizontalOverflow(page,'landing '+vp.name);
  }
});

for (const vp of viewports) {
  test('S09 35 diapositivas contenidas · '+vp.name, async ({ page }) => {
    await page.setViewportSize({width:vp.width,height:vp.height});
    await page.goto('/Presentaciones/s09-de-palabras-a-significado.html?preview=1#s1');
    await page.waitForLoadState('domcontentloaded');
    for(let i=1;i<=35;i++){
      await page.evaluate(n=>{location.hash='#s'+n},i);
      await page.waitForTimeout(20);
      await assertNoHorizontalOverflow(page,'S09 '+vp.name+' slide '+i);
      await assertVisibleSvgContained(page,'S09 '+vp.name+' slide '+i);
    }
  });
}

for (const vp of [viewports[0],viewports[5],viewports[6]]) {
  test('módulo universal responsive · '+vp.name, async ({ page }) => {
    await page.setViewportSize({width:vp.width,height:vp.height});
    await mockSessionApi(page,'student');
    await page.goto('/lms/session.html?s=9');
    await expect(page.getByText('Sesión LMS activa')).toBeVisible();
    await assertNoHorizontalOverflow(page,'module '+vp.name);
    const heights=await page.locator('.btn:visible').evaluateAll(xs=>xs.map(x=>x.getBoundingClientRect().height));
    expect(heights.every(h=>h>=44)).toBeTruthy();
  });
}

for (const vp of [viewports[0],viewports[5]]) {
  test('WALL universal responsive · '+vp.name, async ({ page }) => {
    await page.setViewportSize({width:vp.width,height:vp.height});
    await mockSessionApi(page,'teacher');
    await page.goto('/lms/wall.html?s=9');
    await expect(page.getByText('no es un ranking de velocidad')).toBeVisible();
    await assertNoHorizontalOverflow(page,'wall '+vp.name);
  });
}


test('guía interna hereda identidad LMS', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await mockSessionApi(page,'student');
  await page.goto('/assets/tutoriales/atlas-guia-conexion.html');
  await expect(page.getByText('Sesión LMS activa')).toBeVisible();
  await expect(page.getByText('Estudiante QA')).toBeVisible();
  await assertNoHorizontalOverflow(page,'resource bridge Atlas');
});


async function assertA11y(page, label) {
  const result = await new AxeBuilder({ page })
    .withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'])
    .analyze();
  const severe = result.violations.filter(v => ['serious','critical'].includes(v.impact));
  expect(severe, label + ' violaciones WCAG serias/críticas').toEqual([]);
}

test('accesibilidad landing pública', async ({ page }) => {
  await page.setViewportSize({width:1280,height:720});
  await page.goto('/');
  await assertA11y(page,'landing');
});

test('accesibilidad módulo universal autenticado', async ({ page }) => {
  await page.setViewportSize({width:1280,height:720});
  await mockSessionApi(page,'student');
  await page.goto('/lms/session.html?s=9');
  await expect(page.getByText('Sesión LMS activa')).toBeVisible();
  await assertA11y(page,'module');
});


test('accesibilidad WALL docente', async ({ page }) => {
  await page.setViewportSize({width:1280,height:720});
  await mockSessionApi(page,'teacher');
  await page.goto('/lms/wall.html?s=9');
  await expect(page.getByText('no es un ranking de velocidad')).toBeVisible();
  await assertA11y(page,'teacher wall');
});


test('módulo genera código efímero para Colab', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await mockSessionApi(page,'student');
  await page.goto('/lms/session.html?s=9');
  await expect(page.getByText('Código de laboratorio')).toBeVisible();
  await page.getByRole('button',{name:'Generar código'}).click();
  await expect(page.getByText('ABCD2345')).toBeVisible();
  await assertNoHorizontalOverflow(page,'lab code mobile');
});

test('LAB 3 registra evidencia sin desbordes', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await mockSessionApi(page,'student');
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s17');
  await expect(page.getByText('Registrar evidencia · LAB 3')).toBeVisible();
  await page.locator('#lab3Result').fill('4');
  await page.locator('#lab3Decision').selectOption('mantener');
  await page.locator('#lab3Alternative').fill('Descarto subir k porque aumentaría candidatos sin mejorar necesariamente la precisión.');
  await page.locator('#lab3Limit').fill('Me faltan juicios de relevancia humanos para saber si los cinco candidatos realmente responden a la necesidad.');
  await page.locator('#lab3Submit').click();
  await expect(page.getByText(/Resultado verificado/)).toBeVisible();
  await assertNoHorizontalOverflow(page,'LAB 3 evidence mobile');
});


test('muro de clase exige publicar antes de ver', async ({ page }) => {
  await page.setViewportSize({width:390,height:844});
  await mockSessionApi(page,'student');
  await page.goto('/lms/class-wall.html?s=9&a=bd-s09-lab3');
  await expect(page.getByText('Publica tu aporte para abrir el muro.')).toBeVisible();
  await page.locator('#body').fill('Mantendría k=5 porque el Top-5 ya concentra candidatos aeronáuticos; todavía necesito juicios humanos.');
  await page.getByRole('button',{name:'Publicar'}).click();
  await expect(page.getByText('Mantendría k=5 porque el Top-5 ya concentra candidatos aeronáuticos; todavía necesito juicios humanos.')).toBeVisible();
  await assertNoHorizontalOverflow(page,'class wall mobile');
  await assertA11y(page,'class wall');
});


test('solicitud pública no envía Authorization aunque exista sesión LMS', async ({ page }) => {
  let authHeader = null;
  await page.addInitScript(() => {
    localStorage.setItem('lms.bigdata.v2', JSON.stringify({
      token:'token-admin-prueba',
      expires_at:'2099-12-31T23:59:59Z',
      auth_session_id:'qa-admin',
      user:{id:'admin',username:'admin',display_name:'Admin QA',role:'admin'}
    }));
  });
  await page.route('**/functions/v1/learning-access-request', async route => {
    authHeader = route.request().headers()['authorization'] || null;
    await route.fulfill({
      status:200,
      contentType:'application/json',
      body:JSON.stringify({ok:true,message:'Solicitud registrada.'})
    });
  });
  await page.goto('/lms/access.html');
  await page.locator('#name').fill('Estudiante QA');
  await page.locator('#email').fill('estudiante.qa@ucentral.edu.co');
  await page.getByRole('button',{name:'Enviar solicitud'}).click();
  await expect(page.getByText('Solicitud registrada.')).toBeVisible();
  expect(authHeader).toBeNull();
});

test('sesión de pestaña prevalece sobre otra sesión guardada y sobrevive reload', async ({ page }) => {
  await page.addInitScript(() => {
    const tab = {
      token:'token-pestana',
      expires_at:'2099-12-31T23:59:59Z',
      auth_session_id:'tab',
      user:{id:'admin',username:'admin',display_name:'Admin pestaña',role:'admin'}
    };
    const global = {
      token:'token-otra-pestana',
      expires_at:'2099-12-31T23:59:59Z',
      auth_session_id:'global',
      user:{id:'student',username:'student',display_name:'Otra cuenta',role:'student'}
    };
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(tab));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(global));
  });
  const seen=[];
  await page.route('**/functions/v1/bigdata-lms-core**', async route => {
    seen.push(route.request().headers()['authorization']);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      viewer:{id:'admin',username:'admin',display_name:'Admin pestaña',role:'admin'},
      assignments:[],sessions:[],announcements:[]
    })});
  });
  await page.route('**/functions/v1/bigdata-session**', async route => {
    seen.push(route.request().headers()['authorization']);
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      viewer:{id:'admin',username:'admin',display_name:'Admin pestaña',role:'admin'},
      sessions:[]
    })});
  });
  await page.goto('/lms/portal.html');
  await expect(page.locator('#home')).toBeVisible();
  await page.reload();
  await expect(page.locator('#home')).toBeVisible();
  expect(seen.length).toBeGreaterThanOrEqual(4);
  expect(seen.every(x=>x==='Bearer token-pestana')).toBeTruthy();
});


test('estudiante puede cambiar contraseña desde Mi cuenta', async ({ page }) => {
  await page.addInitScript(() => {
    const auth={
      token:'token-estudiante',
      expires_at:'2099-12-31T23:59:59Z',
      auth_session_id:'student-session',
      user:{id:'student',username:'student',display_name:'Estudiante QA',role:'student',email:'student@ucentral.edu.co'}
    };
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  });
  const actions=[];
  await page.route('**/functions/v1/learning-auth', async route => {
    const body=route.request().postDataJSON?.()||{};
    actions.push(body);
    let result={ok:true};
    if(body.action==='me') result={
      user:{id:'student',username:'student',display_name:'Estudiante QA',role:'student',email:'student@ucentral.edu.co'},
      expires_at:'2099-12-31T23:59:59Z',auth_session_id:'student-session',persistent:true
    };
    if(body.action==='list_sessions') result={sessions:[
      {id:'student-session',current:true,device_label:'Android · Chrome',created_at:'2099-01-01T10:00:00Z',last_seen_at:'2099-01-01T11:00:00Z'},
      {id:'other',current:false,device_label:'Windows · Chrome',created_at:'2099-01-01T09:00:00Z',last_seen_at:'2099-01-01T10:30:00Z'}
    ]};
    if(body.action==='change_password') result={ok:true,message:'Contraseña actualizada; las demás sesiones quedaron cerradas'};
    if(body.action==='logout_others') result={ok:true};
    await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(result)});
  });
  await page.setViewportSize({width:390,height:844});
  await page.goto('/lms/account.html');
  await expect(page.getByText('Cambiar contraseña')).toBeVisible();
  await page.locator('#password').fill('NuevaClave123!');
  await page.locator('#confirm').fill('NuevaClave123!');
  await page.getByRole('button',{name:'Actualizar contraseña'}).click();
  await expect(page.getByText(/Contraseña actualizada/)).toBeVisible();
  expect(actions.some(x=>x.action==='change_password'&&x.password==='NuevaClave123!')).toBeTruthy();
  await expect(page.getByText('Android · Chrome')).toBeVisible();
  await expect(page.getByText('Windows · Chrome')).toBeVisible();
  await assertNoHorizontalOverflow(page,'account mobile');
  await assertA11y(page,'account');
});
