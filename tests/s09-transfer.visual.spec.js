const { test, expect } = require('@playwright/test');

async function auth(page){
  await page.addInitScript(()=>{
    const auth={token:'qa-transfer-token',expires_at:'2099-12-31T23:59:59Z',auth_session_id:'qa-transfer',
      user:{id:'00000000-0000-0000-0000-000000000031',username:'student-transfer',display_name:'Estudiante Transfer',role:'student'}};
    sessionStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
    localStorage.setItem('lms.bigdata.v2',JSON.stringify(auth));
  });
}

function model(){
  return {
    viewer:{id:'00000000-0000-0000-0000-000000000031',username:'student-transfer',display_name:'Estudiante Transfer',role:'student'},
    run:{id:'11111111-1111-1111-1111-111111111111',code:'bigdata-2026-2',title:'Big Data 2026-2S'},
    session:{session_number:9,title:'De palabras a significado',summary:'',status:'visible',metadata:{}},
    activities:[
      {code:'bd-s09-lab3',title:'LAB 3 · Vecinos y Top-k',kind:'lab',required:true,points:0,metadata:{slide:17}},
      {code:'bd-s09-lab4',title:'LAB 4 · BM25 vs semántica',kind:'lab',required:false,points:0,metadata:{slide:18}},
      {code:'bd-s09-lab8',title:'LAB 8 · RRF',kind:'lab',required:false,points:0,metadata:{slide:31}},
      {code:'bd-s09-lab9',title:'LAB 9 · Evidencia final',kind:'lab',required:false,points:0,metadata:{slide:33}}
    ],
    activity_progress:[
      {activity_code:'bd-s09-lab3',status:'in_progress',attempts:1,metadata:{self_check_verified:true,evidence_verdict:'correct'}},
      {activity_code:'bd-s09-lab4',status:'in_progress',attempts:1,metadata:{self_check_verified:true,evidence_verdict:'correct'}},
      {activity_code:'bd-s09-lab8',status:'in_progress',attempts:1,metadata:{self_check_verified:true,evidence_verdict:'correct'}}
    ],
    session_progress:{session_number:9,status:'in_progress',active_seconds:120,last_activity_at:new Date().toISOString()},
    catalog:[
      {code:'bd-s09-lab3',evaluator:'seeded-numeric',seeded:true,steps:[
        {id:'result',type:'number',label:'Resultado'},
        {id:'decision',type:'choice',label:'Decisión',options:[{value:'mantener',label:'Mantener'},{value:'subir',label:'Subir'}]}
      ],config:{requires_transfer:true}},
      {code:'bd-s09-lab4',evaluator:'choice-hash',seeded:false,steps:[
        {id:'paraphrase',type:'choice',label:'Paráfrasis',options:[{value:'semantic',label:'Semántica'},{value:'lexical',label:'Lexical'}]}
      ],config:{requires_transfer:true}},
      {code:'bd-s09-lab8',evaluator:'choice-hash',seeded:false,steps:[
        {id:'fusion',type:'choice',label:'Fusión',options:[{value:'rank_positions',label:'Posiciones'},{value:'raw_scores',label:'Scores crudos'}]}
      ],config:{requires_transfer:true}},
      {code:'bd-s09-lab9',evaluator:'authentic-review',seeded:false,steps:[],config:{requires_review:true}}
    ],
    seeds:{'bd-s09-lab3':'abcdef1234567890'},
    evidence:[],
    controls:[],
    summary:{}
  };
}

async function route(page){
  let state=model();
  await page.route('**/functions/v1/bigdata-session',async route=>{
    const req=route.request();
    if(req.method()==='OPTIONS')return route.fulfill({status:200,body:'ok'});
    let body={};try{body=req.postDataJSON()||{}}catch{}
    const url=new URL(req.url()),action=body.action||url.searchParams.get('action')||'';
    if(action==='me')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(state)});
    if(action==='evidence'&&body.source==='presentation-transfer'){
      const ev={id:'22222222-2222-2222-2222-222222222222',activity_code:body.activity_code,step_id:'transfer',
        source:'presentation-transfer',verdict:'pending_review',feedback:'Transferencia recibida. Está pendiente de revisión docente con rúbrica.',
        payload:body.payload,created_at:new Date().toISOString()};
      state={...state,evidence:[ev,...state.evidence]};
      return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,completed:false,verdict:'pending_review',feedback:ev.feedback,evidence:ev})});
    }
    if(action==='track'||action==='session_controls')return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true,controls:[]})});
    return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({ok:true})});
  });
}

test('S09 LAB3/4/8 conservan autocomprobación y esconden transferencia hasta abrirla',async({page})=>{
  await auth(page);await route(page);
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s17');
  for(const [slide,code] of [[17,'bd-s09-lab3'],[18,'bd-s09-lab4'],[31,'bd-s09-lab8']]){
    await page.evaluate(n=>location.hash='#s'+n,slide);
    await page.waitForTimeout(120);
    const selfCheck=page.locator('.slide.on [data-evidence-kind="self-check"]');
    const transfer=page.locator('.slide.on [data-transfer-for="'+code+'"]');
    await expect(selfCheck).toHaveCount(1);
    await expect(transfer).toHaveCount(1);
    await expect(transfer).not.toHaveAttribute('open','');
    await expect(transfer.locator('[data-transfer-field]')).toHaveCount(5);
  }
});

test('S09 transferencia usa evidence existente y queda pendiente de revisión',async({page})=>{
  await auth(page);await route(page);
  await page.goto('/Presentaciones/s09-de-palabras-a-significado.html#s17');
  const transfer=page.locator('[data-transfer-for="bd-s09-lab3"]');
  await transfer.locator('summary').click();
  const values={
    result:'Observé cuatro de cinco candidatos aeronáuticos en mi Top-5.',
    decision:'Mantendría k igual a cinco para esta consulta concreta.',
    rejected_alternative:'Descarto subir k porque agregaría candidatos menos pertinentes.',
    interpretation:'El resultado muestra buena concentración de vecinos útiles en el Top-5.',
    limit:'La conclusión depende de una sola consulta y de juicios manuales de relevancia.'
  };
  for(const [id,value] of Object.entries(values))await transfer.locator('[data-transfer-field="'+id+'"]').fill(value);
  await transfer.locator('[data-submit-transfer]').click();
  await expect(transfer.locator('[data-transfer-status]')).toContainText('pendiente de revisión docente');
});
