const { test, expect } = require('@playwright/test');

async function seedAuth(page){
  await page.addInitScript(()=>{
    localStorage.setItem('lms.bigdata.v2',JSON.stringify({
      token:'portfolio-qa',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'qa',
      user:{id:'u-self',username:'estudiante.qa',display_name:'Estudiante QA',role:'student'}
    }));
  });
}
function models(){
  const viewer={id:'u-self',username:'estudiante.qa',display_name:'Estudiante QA',role:'student'};
  const run={id:'run-1',title:'Big Data 2026-2S'};
  const course={viewer,run,sessions:[
    {session_number:8,title:'Procesamiento distribuido',session_progress:{status:'completed'}},
    {session_number:9,title:'Búsqueda semántica',session_progress:{status:'in_progress'}}
  ]};
  const details={
    8:{viewer,run,session:{session_number:8,title:'Procesamiento distribuido'},activities:[{code:'lab8',title:'LAB Dask',kind:'lab'}],evidence:[{activity_code:'lab8',verdict:'accepted',feedback:'Evidencia verificada.',created_at:'2026-09-20T12:00:00Z'}]},
    9:{viewer,run,session:{session_number:9,title:'Búsqueda semántica'},activities:[{code:'lab9',title:'LAB Top-k',kind:'lab'}],evidence:[]}
  };
  const competencies={viewer,competencies:[
    {title:'Procesamiento distribuido',domain:'Big Data',status:'mastered',evidence_count:2,min_evidence_count:2},
    {title:'Búsqueda vectorial',domain:'Recuperación',status:'developing',evidence_count:1,min_evidence_count:2},
    {title:'Orquestación',domain:'Plataformas',status:'pending',evidence_count:0,min_evidence_count:2}
  ]};
  return {viewer,run,course,details,competencies};
}
async function mockApis(page){
  const m=models();
  await page.route('**/functions/v1/**',async route=>{
    const req=route.request(),u=new URL(req.url());
    if(u.pathname.endsWith('/bigdata-learning')&&req.method()==='GET')
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({viewer:m.viewer,run:m.run})});
    if(u.pathname.endsWith('/bigdata-session')){
      if(req.method()==='GET'&&u.searchParams.get('action')==='course_progress')
        return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(m.course)});
      if(req.method()==='GET'&&u.searchParams.get('action')==='me'){
        const n=Number(u.searchParams.get('session_number'));
        return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(m.details[n]||{viewer:m.viewer,run:m.run,session:{session_number:n},activities:[],evidence:[]})});
      }
    }
    if(u.pathname.endsWith('/bigdata-lms-core')){
      const body=req.postDataJSON?.()||{};
      if(body.action==='competencies')
        return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(m.competencies)});
    }
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });
}

test('Mi progreso muestra competencias simples sin otro dashboard pesado',async({page})=>{
  await seedAuth(page);await mockApis(page);
  await page.goto('/lms/progress.html?s=9');
  await expect(page.getByRole('heading',{name:'Competencias'})).toBeVisible();
  await expect(page.getByText('Búsqueda vectorial')).toBeVisible();
  await expect(page.getByText('Evidencia suficiente ✓')).toBeVisible();
  await expect(page.getByText('En progreso')).toBeVisible();
  await expect(page.getByRole('link',{name:'Exportar mi portafolio'})).toHaveAttribute('href','portfolio.html');
  await expect(page.locator('#competencyList')).not.toContainText('%');
});

test('portafolio contiene solo sesiones, evidencias y competencias propias',async({page})=>{
  await seedAuth(page);await mockApis(page);
  await page.goto('/lms/portfolio.html');
  await expect(page.getByRole('heading',{name:'Mis evidencias en Big Data'})).toBeVisible();
  await expect(page.locator('#studentName')).toHaveText('Estudiante QA');
  await expect(page.getByText('LAB Dask')).toBeVisible();
  await expect(page.getByText('Evidencia verificada.')).toBeVisible();
  await expect(page.getByText('Búsqueda vectorial')).toBeVisible();
  await expect(page.getByText('heartbeats')).toHaveCount(0);
  await expect(page.getByText('u-self')).toHaveCount(0);
  await expect(page.getByRole('button',{name:'Guardar como PDF'})).toBeVisible();
});

test('portafolio es responsive sin overflow horizontal',async({page})=>{
  await seedAuth(page);await mockApis(page);
  for(const vp of [{width:1280,height:720},{width:390,height:844}]){
    await page.setViewportSize(vp);await page.goto('/lms/portfolio.html');
    const widths=await page.evaluate(()=>({doc:document.documentElement.scrollWidth,win:innerWidth,body:document.body.scrollWidth}));
    expect(widths.doc).toBeLessThanOrEqual(widths.win+2);
    expect(widths.body).toBeLessThanOrEqual(widths.win+2);
  }
});
