/* QA local: Postgres embebido y funciones reales del backend, sin usuarios/productivo.
   npm install --prefix /tmp/s10-db-qa @electric-sql/pglite@0.3.14 typescript@5.9.3
   S10_QA_MODULES=/tmp/s10-db-qa/node_modules node utils/test_s10_lms.cjs */
const fs=require('fs'),path=require('path'),vm=require('vm'),assert=require('node:assert/strict');
const modules=process.env.S10_QA_MODULES||path.resolve('node_modules');
const {PGlite}=require(path.join(modules,'@electric-sql/pglite'));
const ts=require(path.join(modules,'typescript'));
const root=path.resolve(__dirname,'..');
(async()=>{
 const pg=new PGlite();
 // Mismas columnas y restricciones usadas por el seed; no necesita Auth/Storage.
 await pg.exec(`create table bd_lms_sessions(course_code text,session_number smallint,title text,path text,position smallint,required boolean,metadata jsonb,primary key(course_code,session_number));
 create table bd_lms_activities(code text primary key,course_code text,session_number smallint,title text,kind text,points numeric,position smallint,required boolean,metadata jsonb);
 create table lms_course_runs(id uuid primary key,code text,course_code text);
 create table lms_run_sessions_v2(course_run_id uuid,session_number integer,title text,summary text,status text,path text,starts_at timestamptz,position integer,metadata jsonb,published_at timestamptz,updated_at timestamptz,primary key(course_run_id,session_number));
 create table lms_run_resources_v2(id bigint generated always as identity primary key,course_run_id uuid,session_number integer,resource_type text check(resource_type in ('presentation','notebook','guide','reading','lab','link','evidence')),title text,summary text,url text,position integer,visible boolean,metadata jsonb,updated_at timestamptz);
 create table history(activity_code text references bd_lms_activities(code),result jsonb);
 insert into lms_course_runs values('00000000-0000-0000-0000-000000000010','bigdata-2026-2','bigdata');
 insert into bd_lms_activities values('bd-s10-lab-audio','bigdata',10,'Anterior','lab',0,12,true,'{"blocks_session_completion":true}'),('s9-control','bigdata',9,'Control','lab',1,1,true,'{"blocks_session_completion":true}');
 insert into history values('bd-s10-lab-audio','{"evidence_verified":true}');`);
 const seed=fs.readFileSync(path.join(root,'infraestructura/lms/s10-multimedia-seed.sql'),'utf8');
 await pg.exec(seed);await pg.exec(seed);
 const rows=(await pg.query('select * from bd_lms_activities order by code')).rows;
 assert.equal(rows.find(x=>x.code==='bd-s10-lab-audio').required,false);
 assert.equal(rows.find(x=>x.code==='s9-control').required,true);
 assert.equal((await pg.query('select * from history')).rows.length,1);
 assert.equal((await pg.query('select * from lms_run_resources_v2 where visible')).rows.length,2);
 assert.equal((await pg.query('select * from bd_lms_activities where session_number=10 and required')).rows.length,2);
 console.log('OK · seed ejecutado dos veces: dos recursos, historial intacto, S09 intacta');
 const source=fs.readFileSync(path.join(root,'infraestructura/lms/functions/bigdata-session/index.ts'),'utf8');
 const file=ts.createSourceFile('backend.ts',source,ts.ScriptTarget.Latest,true,ts.ScriptKind.TS);
 assert.equal(file.parseDiagnostics.length,0,'Sintaxis backend');
 const names=['recomputeSession','answerChallenge','submitEvidence'];
 const selected=file.statements.filter(x=>ts.isFunctionDeclaration(x)&&names.includes(x.name?.text)).map(x=>x.getText(file)).join('\n');
 const javascript=ts.transpileModule(selected,{compilerOptions:{target:ts.ScriptTarget.ES2022}}).outputText;
 let progress=[],writes=[];
 const db={from(table){const q={select(){return q},eq(){return q},in(){return Promise.resolve({data:progress})},maybeSingle(){return Promise.resolve({data:null})},upsert(row){writes.push(row);return Promise.resolve({error:null})}};return q}};
 const sandbox={db,console,Date,Map,Boolean,Number,Error};vm.createContext(sandbox);vm.runInContext(javascript+';globalThis.api={recomputeSession,answerChallenge,submitEvidence}',sandbox);
 const api=sandbox.api,activities=rows.filter(x=>x.session_number===10&&!x.metadata.archived);
 let result=await api.recomputeSession('local','run',10,activities);assert.equal(result.done,false);assert.equal(result.total,2);
 progress=[{activity_code:'bd-s10-presentation',metadata:{visited:true}}];result=await api.recomputeSession('local','run',10,activities);assert.equal(result.done,false);
 progress.push({activity_code:'bd-s10-notebook',metadata:{visited:true}});result=await api.recomputeSession('local','run',10,activities);assert.equal(result.done,true);assert.equal(writes.at(-1).score,0);assert.equal(writes.at(-1).max_score,0);assert.equal(result.lab_completed,0);
 const s9=[{code:'s9-control',kind:'lab',required:true,metadata:{blocks_session_completion:true}}];progress=[{activity_code:'s9-control',status:'completed',metadata:{}}];result=await api.recomputeSession('local','run',9,s9);assert.equal(result.done,false);
 progress[0].metadata.evidence_verified=true;result=await api.recomputeSession('local','run',9,s9);assert.equal(result.done,true);
 await assert.rejects(()=>api.submitEvidence('u','r',10,{kind:'lab',metadata:{archived:true}},{},'qa'),/histórica/);
 await assert.rejects(()=>api.answerChallenge({}, {},10,'old','texto',[{code:'old',kind:'checkpoint',metadata:{archived:true}}]),/histórica/);
 console.log('OK · funciones reales: visitas S10 sin nota, evidencia S09 sigue obligatoria, actividades retiradas rechazan envíos');
 await pg.close();
})().catch(e=>{console.error(e);process.exitCode=1});
