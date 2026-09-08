import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import http from 'node:http';
import {spawn} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {loadBank,selectCases,score,writeJSON,DEFAULT_BANK} from './core.mjs';
import {startBroker} from './broker.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const run=(file,argv,env={})=>new Promise((ok,no)=>{const c=spawn(process.execPath,[path.join(here,file),...argv],{env:{...process.env,...env}});let out='',err='';c.stdout.on('data',b=>out+=b);c.stderr.on('data',b=>err+=b);c.on('error',no);c.on('close',code=>ok({code,out,err}));});
test('bank selection deterministic, unknown IDs and ambiguous answers rejected',async()=>{
 const {bank}=await loadBank();assert.deepEqual(selectCases(bank,{seed:'42',count:'2'}).map(c=>c.id),selectCases(bank,{seed:'42',count:'2'}).map(c=>c.id));
 assert.throws(()=>selectCases(bank,{cases:'missing'}));assert.equal(score('A',{type:'choice',answers:['A']}).pass,true);
 assert.equal(score('A or B',{type:'choice',answers:['A']}).pass,false);assert.equal(score('10:10',{type:'exact',answers:['08:08']}).pass,false);
});
test('asset traversal and duplicate IDs cannot enter a bank',async()=>{
 const d=await fs.mkdtemp(path.join(os.tmpdir(),'liucong-bank-'));const {bank}=await loadBank();
 const c=structuredClone(bank.cases.find(c=>c.id==='logic'));c.images=['../secret.png'];
 await writeJSON(path.join(d,'bank.json'),{schemaVersion:1,cases:[c]});await assert.rejects(()=>loadBank(path.join(d,'bank.json')));
 c.images=[];await writeJSON(path.join(d,'bank.json'),{schemaVersion:1,cases:[c,c]});await assert.rejects(()=>loadBank(path.join(d,'bank.json')));
 await fs.symlink(path.join(path.dirname(DEFAULT_BANK),'clock.png'),path.join(d,'linked.png'));c.images=['linked.png'];await writeJSON(path.join(d,'bank.json'),{schemaVersion:1,cases:[c]});await assert.rejects(()=>loadBank(path.join(d,'bank.json')));
});
test('broker isolates models, refuses routes, limits quota, removes credential file',async()=>{
 let seen=[];const upstream=http.createServer(async(req,res)=>{let body='';for await(const b of req)body+=b;seen.push({headers:req.headers,body:JSON.parse(body)});res.setHeader('Content-Type','application/json');res.end('{"ok":true}');});
 await new Promise(r=>upstream.listen(0,'127.0.0.1',r));const d=await fs.mkdtemp(path.join(os.tmpdir(),'liucong-broker-'));
 const b=await startBroker({key:'fake-upstream-secret-for-tests',dataDir:d,models:['test-a','test-b'],maxRequests:1,upstreamURL:'http://127.0.0.1:'+upstream.address().port,testOnly:true});
 try{
  const s=await(await fetch(b.url+'/session',{method:'POST',headers:{'x-api-key':b.master},body:JSON.stringify({model:'test-a',seconds:30})})).json();
  const req=(url,model,token=s.token)=>fetch(b.url+url,{method:'POST',headers:{'x-api-key':token},body:JSON.stringify({model,messages:[]})});
  assert.equal((await req('/v1/messages','test-a','bad')).status,401);assert.equal((await req('/v1/messages','test-b')).status,403);
  assert.equal((await req('/anything','test-a')).status,403);assert.equal((await req('/v1/messages','test-a')).status,200);assert.equal((await req('/v1/messages','test-a')).status,429);
  assert.equal(seen.length,1);assert.equal(seen[0].headers['x-api-key'],'fake-upstream-secret-for-tests');
  const file=await fs.readFile(path.join(d,'broker-client.json'),'utf8');assert(!file.includes('fake-upstream-secret-for-tests'));assert.equal((await fs.stat(path.join(d,'broker-client.json'))).mode&0o777,0o600);
 }finally{await b.close();await new Promise(r=>upstream.close(r));}
 await assert.rejects(()=>fs.access(path.join(d,'broker-client.json')));
});
test('fresh init → idempotence → sandboxed mock run → export; no real model call',{skip:process.platform!=='darwin'},async()=>{
 const d=await fs.mkdtemp(path.join(os.tmpdir(),"liucong fresh ' space-"));const cliDir=path.join(d,'mock-cli');await fs.mkdir(cliDir);const cli=path.join(cliDir,'claude');
 const mock=['#!/usr/bin/env node',
 "if(process.argv.includes('--version')){console.log('0.0.0 MOCK');process.exit(0);}",
 "if(process.argv.includes('--help')){console.log('--bare --tools --setting-sources --strict-mcp-config');process.exit(0);}",
 "let input='';process.stdin.on('data',b=>input+=b);process.stdin.on('end',async()=>{",
 "const msg=JSON.parse(input);const response=await fetch(process.env.ANTHROPIC_BASE_URL+'/v1/messages',{method:'POST',headers:{'x-api-key':process.env.ANTHROPIC_API_KEY},body:JSON.stringify({model:process.env.ANTHROPIC_MODEL,messages:[msg.message]})});const value=await response.json();",
 "console.log(JSON.stringify({type:'result',result:value.answer,is_error:false,usage:{}}));",
 "});"].join('\n');
 await fs.writeFile(cli,mock,{mode:0o700});const env={LIUCONG_EVAL_HOME:path.join(d,'state')};
 const init=await run('setup.mjs',['init','--model=test-a','--claude='+cli],env);assert.equal(init.code,0,init.err);
 const before=await fs.readFile(path.join(env.LIUCONG_EVAL_HOME,'config.json'));assert.equal((await run('setup.mjs',['init'],env)).code,0);assert.deepEqual(await fs.readFile(path.join(env.LIUCONG_EVAL_HOME,'config.json')),before);
 const isolation=await run('runner.mjs',['isolation-check'],env);assert.equal(isolation.code,0,isolation.err);
 let observed=[];const upstream=http.createServer(async(req,res)=>{let s='';for await(const x of req)s+=x;const data=JSON.parse(s);observed.push(data);const prompt=data.messages[0].content[0].text;res.end(JSON.stringify({answer:prompt.includes('连接成功')?'连接成功':'wrong'}));});
 await new Promise(r=>upstream.listen(0,'127.0.0.1',r));const broker=await startBroker({key:'test-only-dummy-key',dataDir:env.LIUCONG_EVAL_HOME,models:['test-a'],testOnly:true,upstreamURL:'http://127.0.0.1:'+upstream.address().port});
 try{
 const first=await run('runner.mjs',['run','--cases=connection','--model=test-a'],env);assert.equal(first.code,0,first.err);assert.match(first.out,/"pass":true/);
 const custom=path.join(d,'custom');await fs.mkdir(custom);const {bank}=await loadBank();let c=structuredClone(bank.cases.find(c=>c.id==='logic'));c.id='private-case';c.source={kind:'custom',title:'my private bank'};c.scoring={type:'exact',answers:['GOLD_NOT_MODEL_INPUT']};
 await fs.copyFile(path.join(path.dirname(DEFAULT_BANK),'clock.png'),path.join(custom,'clock.png'));await fs.copyFile(path.join(path.dirname(DEFAULT_BANK),'illusion.png'),path.join(custom,'illusion.png'));c.images=['clock.png','illusion.png'];
 assert.equal((await run('setup.mjs',['model','--id=test-a','--vision=yes'],env)).code,0);
 await writeJSON(path.join(custom,'bank.json'),{schemaVersion:1,name:'private',cases:[c]});
 const second=await run('runner.mjs',['run','--bank='+path.join(custom,'bank.json'),'--cases=private-case','--model=test-a'],env);assert.equal(second.code,0,second.err);assert(!JSON.stringify(observed).includes('GOLD_NOT_MODEL_INPUT'));
 const imgs=observed[1].messages[0].content.filter(x=>x.type==='image');assert.equal(imgs.length,2);assert.equal(imgs[0].source.data,(await fs.readFile(path.join(custom,'clock.png'))).toString('base64'));assert.equal(imgs[1].source.data,(await fs.readFile(path.join(custom,'illusion.png'))).toString('base64'));
 const repeat=await run('runner.mjs',['run','--bank='+path.join(custom,'bank.json'),'--cases=private-case','--model=test-a'],env);assert.notEqual(repeat.code,0);assert.equal(observed.length,2);
 const exported=path.join(d,'export');assert.equal((await run('runner.mjs',['export','--out='+exported],env)).code,0);
 const rows=JSON.parse(await fs.readFile(path.join(exported,'results.json'),'utf8'));assert.equal(rows.length,2);assert.equal(rows.find(r=>r.caseId==='private-case').pass,false);assert(!JSON.stringify(rows).includes('test-only-dummy-key'));
 }finally{await broker.close();await new Promise(r=>upstream.close(r));}
});
