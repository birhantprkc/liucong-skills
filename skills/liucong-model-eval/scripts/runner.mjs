import fs from 'node:fs/promises';
import path from 'node:path';
import {spawn,spawnSync} from 'node:child_process';
import crypto from 'node:crypto';
import {DATA,args,config,writeJSON,json,loadBank,localFile,selectCases,imageType,profile,hash,brokerClient,score,redact,validId} from './core.mjs';
const o=args(),mode=process.argv[2]||'status';
const runtime=path.join(DATA,'runs');
async function results(){const names=await fs.readdir(runtime).catch(()=>[]);return(await Promise.all(names.map(n=>json(path.join(runtime,n,'result.json')).catch(()=>null)))).filter(Boolean);}
async function isolation(c){
 if(process.platform!=='darwin')throw Error('没有此系统的已验证隔离适配器，停止执行');
 const root=await fs.realpath(DATA),work=await fs.mkdtemp(path.join(root,'isolation-'));
 const sentinel=path.join(root,'outside-probe.txt');await fs.writeFile(sentinel,'NOT_MODEL_INPUT',{mode:0o600});
 const sb=path.join(work,'sandbox.sb'),cli=await fs.realpath(c.claude);await fs.writeFile(sb,profile(work,cli,18765));
 await fs.writeFile(path.join(work,'smoke.mjs'),'console.log("NODE_OK")');
 const commands=[['outsideRead','/bin/cat',[sentinel],true],['outsideWrite','/usr/bin/touch',[path.join(root,'forbidden-probe')],true],['network','/usr/bin/curl',['--noproxy','*','--max-time','3','http://1.1.1.1'],true],['insideWrite','/usr/bin/touch',[path.join(work,'okay')],false],['nodeFile',process.execPath,[path.join(work,'smoke.mjs')],false],['claudeVersion',cli,['--version'],false]];
 const report={};for(const [name,bin,argv,blocked] of commands){const r=spawnSync('/usr/bin/sandbox-exec',['-f',sb,bin,...argv],{cwd:work,encoding:'utf8',timeout:15000,env:{PATH:path.dirname(process.execPath)+':/usr/bin:/bin',TMPDIR:work,OPENSSL_CONF:'/dev/null'}});report[name]={exitCode:r.status,expectedBlocked:blocked,ok:blocked?r.status!==0&&r.status!==null:r.status===0,output:String(r.stdout||'')+String(r.stderr||'')};}
 await writeJSON(path.join(DATA,'isolation-check.json'),report);
 if(Object.values(report).some(x=>!x.ok))throw Error('隔离检查失败，见 isolation-check.json；不允许关闭隔离继续');
 return report;
}
if(mode==='status'){console.log(JSON.stringify((await results()).map(({runId,model,caseId,status,elapsedSeconds,pass})=>({runId,model,caseId,status,elapsedSeconds,pass})),null,2));}
else if(mode==='isolation-check'){console.log(JSON.stringify(await isolation(await config()),null,2));}
else if(mode==='run'){
 const c=await config(),b=await loadBank(o.bank||c.preferences.bank),selected=selectCases(b.bank,o,c.preferences);
 const models=String(o.models||o.model||c.models[0]).split(',');if(models.some(m=>!validId(m)||!c.models.includes(m)))throw Error('模型未配置：先 setup.mjs model --id=模型ID');
 const override=o.seconds?Number(o.seconds):null;if(override!==null&&(!Number.isInteger(override)||override<30||override>1800))throw Error('seconds应为30—1800');
 if(o.repeat&&!o.reason)throw Error('补跑需 --repeat --reason="具体原因"，保留首轮记录');
 const selection={bankSha256:b.sha256,seed:o.seed||c.preferences.seed,caseIds:selected.map(x=>x.id),models,budgets:selected.map(x=>({id:x.id,seconds:override||x.seconds}))};
 if(o['dry-run']){console.log(JSON.stringify(selection,null,2));process.exit(0);}
 const isolationReport=await isolation(c);c.claudeVersion=isolationReport.claudeVersion.output.trim();const broker=await brokerClient();
 const health=await fetch(broker.url+'/health',{signal:AbortSignal.timeout(3000)}).catch(()=>{throw Error('临时连接已失效，请重新connect');});if(!health.ok)throw Error('本地连接不可用');
 const sessionFingerprint=hash(broker.token);
 runLoop: for(const model of models)for(const item of selected){
  const preflightFile=path.join(DATA,'preflight.json'),pf=await json(preflightFile).catch(()=>({}));
  const ready=pf[model]?.connection===true&&pf[model]?.sessionFingerprint===sessionFingerprint;
  if(item.tier!=='preparation'&&!ready)throw Error('先验证当前连接：run --cases=connection --model='+model);
  if(item.kind==='code'&&item.tier!=='preparation'&&pf[model]?.tools!==true)throw Error('代码题先运行 toolscheck，核对实际工具输出');
  if(item.images.length&&item.id!=='visioncheck'&&c.vision[model]!=='yes'&&!(ready&&pf[model]?.vision===true))throw Error('视觉能力尚未确认：先跑 visioncheck；失败时标记未确认/不适用，不转成文字题');
  const seconds=override||item.seconds;
  const prompt=item.kind==='code'?item.prompt.replaceAll('{{BUDGET_SECONDS}}',String(seconds)):item.prompt;
  const promptSha256=hash(prompt),past=await results();
  if(item.tier!=='preparation'&&!o.repeat&&past.some(r=>r.model===model&&r.caseId===item.id&&r.promptSha256===promptSha256&&r.bankSha256===b.sha256&&r.budgetSeconds===seconds))throw Error('已有相同条件记录，未重复扣费。确需补跑加 --repeat 并在报告注明原因。');
  const runId=new Date().toISOString().replace(/[:.]/g,'-')+'_'+model+'_'+item.id+'_'+crypto.randomBytes(3).toString('hex');
  await fs.mkdir(runtime,{recursive:true,mode:0o700});const work=path.join(await fs.realpath(runtime),runId);await fs.mkdir(work,{mode:0o700});await fs.mkdir(path.join(work,'tmp'));await fs.mkdir(path.join(work,'config'));
  const sessionResponse=await fetch(broker.url+'/session',{method:'POST',headers:{'Content-Type':'application/json','x-api-key':broker.token},body:JSON.stringify({model,seconds})});if(!sessionResponse.ok)throw Error('模型连接未接受任务；检查配置后重新connect');
  const {token}=await sessionResponse.json(),cli=await fs.realpath(c.claude);
  const content=[{type:'text',text:prompt}],images=[],inputs=[];
  for(let i=0;i<item.images.length;i++){const src=await localFile(b.root,item.images[i]),bytes=await fs.readFile(src),media=imageType(bytes),filename='input-'+(i+1)+'.'+({ 'image/png':'png','image/jpeg':'jpg','image/webp':'webp'})[media];await fs.writeFile(path.join(work,filename),bytes);content.push({type:'text',text:'Image '+(i+1)},{type:'image',source:{type:'base64',media_type:media,data:bytes.toString('base64')}});images.push({file:filename,sha256:hash(bytes),bytes:bytes.length});}
  for(const f of item.files||[]){const bytes=await fs.readFile(await localFile(b.root,f.path));await fs.writeFile(path.join(work,f.target),bytes);inputs.push({file:f.target,sha256:hash(bytes)});}
  await fs.writeFile(path.join(work,'sandbox.sb'),profile(work,cli,new URL(broker.url).port));
  await writeJSON(path.join(work,'settings.json'),{permissions:{defaultMode:'dontAsk'},env:{CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:'1'}});
  await fs.writeFile(path.join(work,'prompt.txt'),prompt);
  const toolSet=item.kind==='code'?'Read,Write,Edit,Bash':'';
  const argv=['-f',path.join(work,'sandbox.sb'),cli,'--bare','--setting-sources','','--settings',path.join(work,'settings.json'),'--strict-mcp-config','--mcp-config','{"mcpServers":{}}','--disable-slash-commands','--no-chrome','--no-session-persistence','--permission-mode','dontAsk','--model',model,'--tools',toolSet,'--allowedTools',toolSet,'--input-format','stream-json','--output-format','stream-json','--verbose','--effort','high','-p'];
  const env={PATH:path.dirname(process.execPath)+':/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin',TMPDIR:path.join(work,'tmp'),OPENSSL_CONF:'/dev/null',CLAUDE_CONFIG_DIR:path.join(work,'config'),ANTHROPIC_BASE_URL:broker.url,ANTHROPIC_API_KEY:token,ANTHROPIC_AUTH_TOKEN:token,ANTHROPIC_MODEL:model,ANTHROPIC_DEFAULT_HAIKU_MODEL:model,ANTHROPIC_DEFAULT_SONNET_MODEL:model,ANTHROPIC_DEFAULT_OPUS_MODEL:model,CLAUDE_CODE_SUBAGENT_MODEL:model,CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC:'1',CLAUDE_CODE_DISABLE_AUTO_MEMORY:'1',DISABLE_AUTOUPDATER:'1',CLAUDE_CODE_SHELL:'/bin/bash',CLAUDE_CODE_TMPDIR:path.join(work,'tmp'),LANG:'zh_CN.UTF-8',PORT:'18991'};
  // Gold answers/source explanations stay outside the model working directory until the process exits.
  const start=Date.now();const meta={runId,caseId:item.id,model,operator:String(o.operator||'user'),startedAt:new Date().toISOString(),status:'running',budgetSeconds:seconds,promptSha256,bankSha256:b.sha256,selection,source:item.source,images,inputs,tools:toolSet.split(',').filter(Boolean),cliVersion:c.claudeVersion,repeatReason:o.repeat?String(o.reason):null,priorRunIds:past.filter(r=>r.caseId===item.id&&r.model===model).map(r=>r.runId),work};
  await writeJSON(path.join(work,'result.json'),{runId,status:'running',caseId:item.id,model,work,budgetSeconds:seconds,bankSha256:b.sha256,promptSha256});
  console.log('START '+runId);
  let stdout='',stderr='',timedOut=false,cancelled=false;const child=spawn('/usr/bin/sandbox-exec',argv,{cwd:work,env,detached:true});
  const kill=()=>{try{process.kill(-child.pid,'SIGTERM');}catch{};setTimeout(()=>{try{process.kill(-child.pid,'SIGKILL');}catch{}},1500).unref();};
  const stop=()=>{cancelled=true;kill();};process.once('SIGINT',stop);process.once('SIGTERM',stop);
  child.stdout.on('data',b=>{stdout+=b.toString();});child.stderr.on('data',b=>{stderr+=b.toString();});child.stdin.on('error',()=>{});child.stdin.end(JSON.stringify({type:'user',message:{role:'user',content}})+'\n');
  const timer=setTimeout(()=>{timedOut=true;kill();},seconds*1000);
  const exitCode=await new Promise(r=>{child.once('close',r);child.once('error',e=>{stderr+=e.message;r(-1);});});clearTimeout(timer);process.off('SIGINT',stop);process.off('SIGTERM',stop);
  // Terminate any descendants before the evaluator writes gold answers into result.json.
  try{process.kill(-child.pid,'SIGKILL');}catch{}
  await fetch(broker.url+'/session/'+token,{method:'DELETE',headers:{'x-api-key':broker.token}}).catch(()=>{});
  stdout=redact(stdout,[token,broker.token]);stderr=redact(stderr,[token,broker.token]);
  await fs.writeFile(path.join(work,'events.jsonl'),stdout);await fs.writeFile(path.join(work,'stderr.txt'),stderr);
  const events=stdout.split('\n').flatMap(l=>{try{return[JSON.parse(l)]}catch{return[]}}),last=events.findLast(e=>e.type==='result');
  const answer=last?.result||events.filter(e=>e.type==='assistant').flatMap(e=>(e.message?.content||[]).filter(x=>x.type==='text').map(x=>x.text)).join('\n');
  const status=cancelled?'cancelled':timedOut?'timeout':exitCode!==0||!last||last.is_error?'error':'complete';
  const verdict=status==='complete'?score(answer,item.scoring):{pass:null,needsReview:true};
  const artifacts=[];for(const f of item.outputs||[]){const full=path.join(work,f),st=await fs.lstat(full).catch(()=>null);if(st?.isFile()&&!st.isSymbolicLink()){const data=await fs.readFile(full);artifacts.push({file:f,bytes:data.length,sha256:hash(data)});}}
  Object.assign(meta,{status,finishedAt:new Date().toISOString(),elapsedSeconds:Math.round((Date.now()-start)/100)/10,exitCode,answer,scoring:item.scoring,...verdict,artifacts,requiredArtifactsPresent:(item.outputs||[]).every(f=>artifacts.some(a=>a.file===f&&a.bytes>0)),guiAcceptance:item.kind==='code'?'not_tested':'not_applicable',permissionDenials:last?.permission_denials||[],toolCalls:events.filter(e=>e.type==='assistant').flatMap(e=>(e.message?.content||[]).filter(x=>x.type==='tool_use').map(x=>({name:x.name,input:x.input}))),usage:last?.usage||null});
  if(item.id==='connection'){meta.pass=status==='complete'&&answer.trim().length>0;meta.preparationMeaning='上游产生非空回答，不作为答题正确率';}
  if(item.id==='toolscheck'){const observed=events.flatMap(e=>e.message?.content||[]).filter(x=>x.type==='tool_result'&&!x.is_error).map(x=>typeof x.content==='string'?x.content:JSON.stringify(x.content)).join('\n');meta.pass=status==='complete'&&observed.includes('SANDBOX_OK')&&/(?:^|\n)123(?:\n|$)/.test(observed);}
  await writeJSON(path.join(work,'result.json'),meta);
  if(item.tier==='preparation'){pf[model]=ready?pf[model]:{sessionFingerprint};pf[model][({connection:'connection',visioncheck:'vision',toolscheck:'tools'})[item.id]||item.id]=meta.pass===true;await writeJSON(preflightFile,pf);}
  console.log(JSON.stringify({runId,status,seconds:meta.elapsedSeconds,pass:meta.pass,artifacts:artifacts.map(x=>x.file)}));
  if(cancelled)process.exit(130);
  if(status==='error'||(item.tier==='preparation'&&meta.pass!==true)){process.exitCode=2;break runLoop;}
 }
}
else if(mode==='export'){
 const all=await results(),out=path.resolve(String(o.out||path.join(DATA,'exports',new Date().toISOString().replace(/[:.]/g,'-'))));await fs.mkdir(out,{recursive:true});
 await writeJSON(path.join(out,'results.json'),all);
 const cell=v=>'"'+String(v??'').replace(/^[=+@\t\r-]/,"'$&").replaceAll('"','""')+'"';
 await fs.writeFile(path.join(out,'results.csv'),'runId,model,case,status,seconds,pass,artifacts,guiAcceptance\n'+all.map(r=>[r.runId,r.model,r.caseId,r.status,r.elapsedSeconds,r.pass,r.artifacts?.map(x=>x.file).join(';'),r.guiAcceptance].map(cell).join(',')).join('\n'));
 for(const r of all){const dest=path.join(out,r.runId);await fs.mkdir(dest,{recursive:true});for(const f of ['prompt.txt','events.jsonl','result.json','stderr.txt',...(r.images||[]).map(x=>x.file),...(r.inputs||[]).map(x=>x.file),...(r.artifacts||[]).map(x=>x.file)]){const src=path.join(r.work,f),st=await fs.lstat(src).catch(()=>null);if(st?.isFile()&&!st.isSymbolicLink())await fs.copyFile(src,path.join(dest,f));}}
 console.log(out);
}else throw Error('使用 status / isolation-check / run / export');
