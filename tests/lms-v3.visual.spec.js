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
  await page.route('**/functions/v1/bigdata-session**', async route => {
    const req=route.request(),url=new URL(req.url());
    const action=url.searchParams.get('action');
    if(req.method()==='GET' && action==='teacher_wall') {
      const model={...sessionModel,viewer:{...sessionModel.viewer,role:'teacher',display_name:'Docente QA'},students:[],ranking:[],activity_stats:[],challenge_stats:[],session_window:null,refreshed_at:new Date().toISOString()};
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(model)});
    }
    if(req.method()==='GET') return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(sessionModel)});
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
