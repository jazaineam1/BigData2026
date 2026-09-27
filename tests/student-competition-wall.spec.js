const { test, expect } = require('@playwright/test');

async function auth(page){
  await page.addInitScript(()=>{
    const auth={token:'qa-competition-token',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'qa-competition',
      user:{id:'00000000-0000-0000-0000-000000000001',username:'student-qa',display_name:'Estudiante QA',role:'student'}};
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  });
}

test('wall competitivo está embebido y no pide respuestas abiertas',async({page})=>{
  await auth(page);
  const viewer={id:'00000000-0000-0000-0000-000000000001',username:'student-qa',display_name:'Estudiante QA',role:'student'};
  await page.route('**/functions/v1/bigdata-learning**',route=>route.fulfill({
    status:200,contentType:'application/json',
    body:JSON.stringify({viewer,run:{id:'run-qa',title:'Big Data 2026-2S'}})
  }));
  await page.route('**/functions/v1/bigdata-lms-core**',route=>route.fulfill({
    status:200,contentType:'application/json',body:JSON.stringify({viewer,competencies:[]})
  }));
  await page.route('**/functions/v1/bigdata-session**',async route=>{
    const req=route.request(),url=new URL(req.url());
    if(req.method()==='GET'&&url.searchParams.get('action')==='course_progress'){
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        viewer,run:{id:'run-qa',timezone:'America/Bogota'},
        sessions:[{session_number:8,title:'SECOP Data Pipeline',summary:'Taller',status:'visible',starts_at:'2026-10-01T18:00:00-05:00',session_progress:{status:'in_progress'},activities:[]}]
      })});
    }
    if(req.method()==='GET'){
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        viewer,session:{session_number:8,title:'SECOP Data Pipeline'},activities:[],evidence:[]
      })});
    }
    const body=req.postDataJSON?.()||{};
    if(body.action==='competition_wall'){
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        session:{session_number:8,title:'SECOP Data Pipeline'},participants:3,required_total:6,viewer_rank:2,
        ranking:[
          {position:1,alias:'Jugador 7A21',is_me:false,status:'in_progress',completed_required:5,required_total:6,progress_pct:83},
          {position:2,alias:'Jugador 1B4F',is_me:true,status:'in_progress',completed_required:4,required_total:6,progress_pct:67},
          {position:3,alias:'Jugador C908',is_me:false,status:'in_progress',completed_required:2,required_total:6,progress_pct:33}
        ],
        privacy:{identity:'alias',open_responses:false,speed_tiebreak:false}
      })});
    }
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });

  await page.goto('/lms/progress.html?s=8#competitionWall');
  await expect(page.getByRole('heading',{name:/S08 · SECOP Data Pipeline/})).toBeVisible();
  await expect(page.getByText('Wall de competencia')).toBeVisible();
  await expect(page.getByText('Jugador 1B4F · Tú')).toBeVisible();
  await expect(page.getByText('#2',{exact:true})).toBeVisible();
  await expect(page.locator('#competitionList textarea')).toHaveCount(0);
  await expect(page.locator('a[href*="class-wall.html"]')).toHaveCount(0);
  await expect(page.getByText(/Los empates comparten posición/)).toBeVisible();
});
