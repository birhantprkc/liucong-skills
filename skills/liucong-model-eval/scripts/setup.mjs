import fs from 'node:fs/promises';
import path from 'node:path';
import {spawnSync} from 'node:child_process';
import {DATA,CONFIG,DEFAULT_BANK,args,json,writeJSON,config,resolveCLI,validId} from './core.mjs';
const o=args(),cmd=process.argv[2]||'doctor';
if(cmd==='init'){
 if(process.platform!=='darwin')throw Error('本包的执行适配器目前只支持macOS；不以无隔离方式降级。其他系统可编辑/导入题库，执行需已验证的适配器。');
 if(Number(process.versions.node.split('.')[0])<22)throw Error('需要Node.js 22或以上');
 await fs.mkdir(DATA,{recursive:true,mode:0o700});await fs.chmod(DATA,0o700);
 let old=await json(CONFIG).catch(e=>{if(e.code==='ENOENT')return null;throw e;});
 if(old){console.log('已有配置保留：'+CONFIG);process.exit(0);}
 const cli=await fs.realpath(resolveCLI(o.claude)),v=spawnSync(cli,['--version'],{encoding:'utf8',timeout:15000});
 if(v.status!==0)throw Error('Claude Code --version失败，未写配置');
 const id=String(o.model||'glm-5.3-flash');if(!validId(id))throw Error('模型ID非法');
 await writeJSON(CONFIG,{schemaVersion:2,claude:cli,claudeVersion:v.stdout.trim(),models:[id],vision:{[id]:'unknown'},preferences:{bank:DEFAULT_BANK,tier:'simple',count:3,tags:[],seed:'42'},maxRequests:200});
 console.log('初始化完成（未保存Key、未发起模型请求）：'+CONFIG);
}else if(cmd==='doctor'){
 let c;try{c=await config();}catch(e){console.log(e.message);process.exitCode=2;}
 const report={platform:process.platform,node:process.version,initialized:!!c,executionAdapter:process.platform==='darwin'?'macOS Seatbelt':'unsupported'};
 if(c){try{const r=spawnSync(c.claude,['--version'],{encoding:'utf8',timeout:15000});report.claude={ok:r.status===0,version:r.stdout?.trim()};const h=spawnSync(c.claude,['--help'],{encoding:'utf8',timeout:15000});report.requiredFlags=['--bare','--tools','--setting-sources','--strict-mcp-config'].filter(x=>!h.stdout?.includes(x));}catch{report.claude={ok:false};}
 try{await fs.access(c.preferences.bank);report.bankExists=true;}catch{report.bankExists=false;}}
 console.log(JSON.stringify(report,null,2));if(process.platform!=='darwin'||!report.claude?.ok||report.requiredFlags?.length||report.bankExists===false)process.exitCode=2;
}else if(cmd==='model'){
 const c=await config();const id=String(o.id||'');if(!validId(id))throw Error('使用 --id=真实模型ID');if(!c.models.includes(id))c.models.push(id);
 if(o.vision){if(!['yes','no','unknown'].includes(o.vision))throw Error('vision应为yes/no/unknown');c.vision[id]=o.vision;}
 await writeJSON(CONFIG,c);console.log('模型设置已保存；若连接已启动，请先Ctrl+C再重启连接使名单生效。');
}else if(cmd==='preferences'){
 const c=await config();if(o.bank)c.preferences.bank=path.resolve(String(o.bank));if(o.tier){if(!['simple','medium','complex'].includes(o.tier))throw Error('tier无效');c.preferences.tier=o.tier;}
 if(o.count){if(!Number.isInteger(Number(o.count))||Number(o.count)<1||Number(o.count)>1000)throw Error('count无效');c.preferences.count=Number(o.count);}
 if(o.tags)c.preferences.tags=String(o.tags).split(',').filter(Boolean);if(o.seed)c.preferences.seed=String(o.seed);
 await writeJSON(CONFIG,c);console.log(JSON.stringify(c.preferences,null,2));
}else throw Error('使用 init / doctor / model / preferences');
