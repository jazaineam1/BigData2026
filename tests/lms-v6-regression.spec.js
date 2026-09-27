const { test, expect } = require('@playwright/test');

async function auth(page, role='student', id='00000000-0000-0000-0000-000000000001') {
  await page.addInitScript(({role,id}) => {
    const auth={token:'qa-v6-token',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'qa-v6',
      user:{id,username:role+'-qa',display_name:role==='teacher'?'Docente QA':'Estudiante QA',role}};
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  }, {role,id});
}

function baseModel(role='student'){
  return {
    viewer:{id:'00000000-0000-0000-0000-000000000001',username:role+'-qa',display_name:role==='teacher'?'Docente QA':'Estudiante QA',role},
    run:{id:'11111111-1111-1111-1111-111111111111',title:'Big Data 2026-2S'},
    session:{session_number:9,title:'Búsqueda semántica',summary:'',status:'visible',metadata:{}},
    activities:[
      {code:'bd-s09-presentation',title:'Presentación S09',kind:'resource',required:true,points:0,metadata:{}},
      {code:'bd-s09-c1',title:'D1 · mecanismo',kind:'checkpoint',required:true,points:1,metadata:{slide:9}},
      {code:'bd-s09-lab1',title:'LAB 1 · Recuperación lexical',kind:'lab',required:true,points:0,metadata:{slide:6}},
      {code:'bd-s09-lab3',title:'LAB 3 · Vecinos y Top-k',kind:'lab',required:true,points:0,metadata:{slide:17}}
    ],
    resources:[],session_progress:{status:'in_progress',active_seconds:60,last_activity_at:new Date().toISOString()},
    activity_progress:[],catalog:[
      {code:'bd-s09-lab1',evaluator:'choice-hash',seeded:false,version:1,steps:[
        {id:'mechanism',type:'choice',label:'Señal',options:[{value:'exact_terms',label:'Términos'},{value:'semantic',label:'Significado'}]}
      ]},
      {code:'bd-s09-lab3',evaluator:'seeded-numeric',seeded:true,version:1}
    ],
    seeds:{},evidence:[],controls:[],summary:{}
  };
}

async function routeSession(page,{role='student',seen=[],controls=[],wallPosts=[]}={}){
  const model=baseModel(role);model.controls=controls;
  await page.route('**/functions/v1/bigdata-session**',async route=>{
    const req=route.request(),url=new URL(req.url()),action=url.searchParams.get('action');
    if(req.method()==='GET'){
      if(action==='teacher_wall')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        ...model,students:[],ranking:[],activity_stats:[],challenge_stats:[],session_window:null,refreshed_at:new Date().toISOString()
      })});
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(model)});
    }
    const body=req.postDataJSON?.()||{};seen.push(body);
    if(body.action==='wall_list')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      viewer:model.viewer,activity:model.activities.find(a=>a.code===body.activity_code),can_view:true,posts:wallPosts
    })});
    if(body.action==='answer_challenge')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      ok:true,correct:true,attempts:1,first_attempt_correct:true,mastery:true,confidence:body.confidence,hint:null
    })});
    if(body.action==='teacher_set_control'||body.action==='teacher_clear_control')
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,controls:[]})});
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });
}

test('S09 exige confianza y la envía al backend', async ({page})=>{
  const seen=[];await auth(page,'student');await routeSession(page,{role:'student',seen});
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s9');
  const answer=page.locator('#ans-bd-s09-c1'),confidence=page.locator('#conf-bd-s09-c1');
  await expect(answer).toBeVisible();await expect(confidence).toBeVisible();
  await page.evaluate(()=>answerChallenge('bd-s09-c1'));
  await expect(page.locator('#fb-bd-s09-c1')).toContainText('Elige una opción');
  await answer.selectOption('lexical');
  await page.evaluate(()=>answerChallenge('bd-s09-c1'));
  await expect(page.locator('#fb-bd-s09-c1')).toContainText('indica tu nivel de confianza');
  await confidence.selectOption('high');
  await page.evaluate(()=>answerChallenge('bd-s09-c1'));
  await expect.poll(()=>seen.some(x=>x.action==='answer_challenge'&&x.confidence==='high')).toBeTruthy();
});

test('S09 muestra pista docente sin cambiar de diapositiva', async ({page})=>{
  const controls=[{id:12,control_key:'hint',control_type:'pin_hint',payload:{text:'Compara score con relevancia humana.'},created_at:new Date().toISOString()}];
  await auth(page,'student');await routeSession(page,{role:'student',controls});
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s9');
  await expect(page.locator('#sessionControlBanner')).toHaveClass(/on/);
  await expect(page.locator('#sessionControlText')).toContainText('Compara score');
  await expect(page).toHaveURL(/#s9$/);
});

test('WALL docente expone controles de ritmo', async ({page})=>{
  await auth(page,'teacher');await routeSession(page,{role:'teacher'});
  await page.goto('/lms/wall.html?s=9');
  await expect(page.getByRole('heading',{name:'Controles docentes'})).toBeVisible();
  await expect(page.locator('#controlLab')).toContainText('LAB 1');
  await expect(page.locator('#gotoSlide')).toBeVisible();
  await expect(page.locator('#pinHint')).toBeVisible();
});

test('modo proyección anonimiza y oculta administración', async ({page})=>{
  const posts=[
    {id:'p1',user_id:'u1',author:'Nombre real 1',body:'La búsqueda semántica recupera paráfrasis, pero aún debo validar relevancia.',status:'visible',created_at:new Date().toISOString(),reactions:{useful:2,same_doubt:0},my_reactions:[]},
    {id:'p2',user_id:'u2',author:'Nombre real 2',body:'BM25 sigue siendo útil cuando necesito coincidencia lexical precisa.',status:'spotlight',created_at:new Date().toISOString(),reactions:{useful:1,same_doubt:1},my_reactions:[]}
  ];
  await auth(page,'teacher');await routeSession(page,{role:'teacher',wallPosts:posts});
  await page.goto('/lms/class-wall.html?s=9&a=bd-s09-lab1&mode=projection');
  await expect(page.locator('body')).toHaveClass(/projection/);
  await expect(page.getByText('Respuesta 1')).toBeVisible();
  await expect(page.getByText('Respuesta 2')).toBeVisible();
  await expect(page.getByText('Nombre real 1')).toHaveCount(0);
  await expect(page.locator('[data-mod]')).toHaveCount(0);
  await expect(page.locator('[data-react]')).toHaveCount(0);
});

test('dos estudiantes y docente conservan sesiones aisladas en el flujo de aula', async ({browser})=>{
  const studentA=await browser.newContext(),studentB=await browser.newContext(),teacher=await browser.newContext();
  const pages=[await studentA.newPage(),await studentB.newPage(),await teacher.newPage()];
  const specs=[
    {page:pages[0],role:'student',id:'00000000-0000-0000-0000-0000000000a1'},
    {page:pages[1],role:'student',id:'00000000-0000-0000-0000-0000000000b2'},
    {page:pages[2],role:'teacher',id:'00000000-0000-0000-0000-0000000000c3'}
  ];
  for(const spec of specs){
    await auth(spec.page,spec.role,spec.id);
    const model=baseModel(spec.role);model.viewer.id=spec.id;
    await spec.page.route('**/functions/v1/bigdata-session**',async route=>{
      const req=route.request(),url=new URL(req.url()),action=url.searchParams.get('action');
      if(req.method()==='GET'&&action==='teacher_wall')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        ...model,students:[],ranking:[],activity_stats:[],challenge_stats:[],session_window:null,refreshed_at:new Date().toISOString()
      })});
      if(req.method()==='GET')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(model)});
      return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
    });
  }
  await pages[0].goto('/lms/session.html?s=9');await pages[1].goto('/lms/session.html?s=9');await pages[2].goto('/lms/wall.html?s=9');
  const ids=await Promise.all(pages.map(p=>p.evaluate(()=>JSON.parse(localStorage.getItem('lms.bigdata.v2')).user.id)));
  expect(new Set(ids).size).toBe(3);
  await studentA.close();await studentB.close();await teacher.close();
});
