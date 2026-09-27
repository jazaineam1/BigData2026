const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;

async function assertA11y(page,label){
  const result=await new AxeBuilder({page})
    .withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa'])
    .analyze();
  const severe=result.violations.filter(v=>['serious','critical'].includes(v.impact));
  expect(severe,label+' violaciones WCAG serias/críticas').toEqual([]);
}
async function setAuth(page,role='student'){
  await page.addInitScript(({role})=>{
    const auth={token:'v8-token',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'v8',
      persistent:role==='student',
      user:{id:'00000000-0000-0000-0000-000000000001',username:role+'-qa',display_name:role==='student'?'Estudiante QA':'Docente QA',role}};
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    if(role==='student')localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  },{role});
}

test('sesión no persistente permanece solo en la pestaña', async ({page})=>{
  await page.goto('/lms/access.html');
  await page.evaluate(()=>{
    window.BIGDATA_LMS.save({token:'teacher-token',persistent:false,user:{role:'teacher'}});
  });
  const state=await page.evaluate(()=>({
    tab:sessionStorage.getItem('lms.bigdata.v2'),
    local:localStorage.getItem('lms.bigdata.v2')
  }));
  expect(state.tab).toContain('teacher-token');
  expect(state.local).toBeNull();
});

test('skip link es visible por teclado y apunta al contenido principal', async ({page})=>{
  await page.goto('/lms/access.html');
  await page.keyboard.press('Tab');
  const skip=page.locator('.skip-link');
  await expect(skip).toBeFocused();
  await expect(skip).toBeVisible();
  await expect(skip).toHaveAttribute('href','#main-content');
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
  await assertA11y(page,'acceso LMS V8');
});

test('cuenta muestra política por rol y permite revocar una sesión', async ({page})=>{
  await setAuth(page,'teacher');const seen=[];
  await page.route('**/functions/v1/bigdata-auth',async route=>{
    const body=route.request().postDataJSON?.()||{};seen.push(body);
    if(body.action==='me')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      user:{id:'00000000-0000-0000-0000-000000000001',display_name:'Docente QA',username:'teacher-qa',role:'teacher',email:'docente@example.edu'},
      expires_at:'2099-12-31T23:59:59Z',auth_session_id:'current',persistent:false,
      session_policy:{role:'teacher',ttl_hours:12,label:'12 horas',persistent:false}
    })});
    if(body.action==='list_sessions')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({sessions:[
      {id:'current',current:true,device_label:'Linux · Chrome',created_at:'2099-01-01T00:00:00Z',last_seen_at:'2099-01-01T01:00:00Z',expires_at:'2099-01-01T12:00:00Z'},
      {id:'other',current:false,device_label:'Android · Chrome',created_at:'2099-01-01T00:00:00Z',last_seen_at:'2099-01-01T00:30:00Z',expires_at:'2099-01-01T12:00:00Z'}
    ]})});
    return route.fulfill({status:200,contentType:'application/json',body:'{"ok":true}'});
  });
  await page.goto('/lms/account.html');
  await expect(page.locator('#sessionPolicy')).toContainText('12 horas');
  await expect(page.getByRole('button',{name:'Cerrar esta sesión'})).toHaveCount(1);
  await page.getByRole('button',{name:'Cerrar esta sesión'}).click();
  await expect.poll(()=>seen.some(x=>x.action==='revoke_session'&&x.session_id==='other')).toBeTruthy();
  await assertA11y(page,'mi cuenta V8');
});

test('observabilidad docente muestra RPO RTO sin datos sensibles', async ({page})=>{
  await setAuth(page,'teacher');
  await page.route('**/functions/v1/bigdata-learning**',async route=>route.fulfill({
    status:200,contentType:'application/json',
    body:JSON.stringify({viewer:{role:'teacher',display_name:'Docente QA'}})
  }));
  await page.route('**/functions/v1/bigdata-lms-ops**',async route=>route.fulfill({
    status:200,contentType:'application/json',
    body:JSON.stringify({
      viewer:{role:'teacher',display_name:'Docente QA'},run:{id:'r1',code:'bigdata-2026-2',title:'Big Data 2026-2S'},
      files:{total:2,total_bytes:1024,by_status:{attached:1,pending:1}},
      health:{generated_at:new Date().toISOString(),overall:'ok',
        auth:{active_sessions:4,login_attempts_24h:10,failed_logins_24h:1,failure_rate_pct:10},
        academic:{events_24h:42,last_event_at:new Date().toISOString()},
        realtime:{mode:'broadcast',transport:'ephemeral',persistent_rows:false,polling_fallback:true},
        retention:{orphan_candidates_24h:0},
        recovery:{rpo_hours:24,rto_hours:4,platform_backup_status:'not_observed_by_lms',last_academic_snapshot_at:new Date().toISOString(),academic_snapshot_age_hours:1.2,academic_snapshot_recent:true,academic_snapshot_target_hours:24}},
      capabilities:['ops.view','backup.export','retention.preview'],
      policies:{login_rate_limit:'8 fallos por IP/cuenta en 15 min mediante bigdata-auth',retention_preview_min_hours:24,cleanup_role:'admin',attached_files_deletable:false,session_ttl_hours:{student:720,teacher:12,admin:4},rpo_hours:24,rto_hours:4,academic_snapshot_target_hours:24,platform_backup_status:'not_observed_by_lms'}
    })
  }));
  await page.goto('/lms/admin-operations.html');
  await expect(page.getByRole('heading',{name:'Estado operativo'})).toBeVisible();
  await expect(page.getByText('Reciente')).toBeVisible();
  await expect(page.getByText(/No equivale al backup administrado de Supabase/)).toBeVisible();
  await expect(page.getByText(/RPO objetivo 24 h · RTO objetivo 4 h/)).toBeVisible();
  await expect(page.getByText('ops.view')).toBeVisible();
  await expect(page.getByText('Broadcast efímero')).toBeVisible();
  await expect(page.getByText(/Sin filas persistentes/)).toBeVisible();
  const body=await page.locator('body').innerText();
  expect(body).not.toContain('key_hash');
  expect(body).not.toContain('token_hash');
  await assertA11y(page,'operaciones V8');
});

test('portafolio mantiene WCAG AA y privacidad', async ({page})=>{
  await setAuth(page,'student');
  await page.route('**/functions/v1/bigdata-learning**',async route=>route.fulfill({
    status:200,contentType:'application/json',body:JSON.stringify({viewer:{role:'student',display_name:'Estudiante QA'}})
  }));
  await page.route('**/functions/v1/bigdata-session**',async route=>{
    const url=new URL(route.request().url()),action=url.searchParams.get('action');
    if(action==='course_progress')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      viewer:{role:'student',display_name:'Estudiante QA'},run:{title:'Big Data 2026-2S'},
      sessions:[{session_number:9,title:'Búsqueda semántica',session_progress:{status:'in_progress'}}]
    })});
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
      viewer:{role:'student'},activities:[{code:'lab',title:'LAB',kind:'lab'}],
      evidence:[{activity_code:'lab',verdict:'correct',feedback:'Evidencia verificada.'}]
    })});
  });
  await page.route('**/functions/v1/bigdata-lms-core**',async route=>route.fulfill({
    status:200,contentType:'application/json',body:JSON.stringify({competencies:[{title:'Recuperación de información',domain:'Big Data',status:'developing',evidence_count:1}]})
  }));
  await page.goto('/lms/portfolio.html');
  await expect(page.getByText('Mis evidencias en Big Data')).toBeVisible();
  await expect(page.getByText('No incluye heartbeats')).toBeVisible();
  await assertA11y(page,'portafolio V8');
});
