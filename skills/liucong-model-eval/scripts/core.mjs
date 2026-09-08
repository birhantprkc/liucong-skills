import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
export const SKILL=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
export const DATA=path.resolve(process.env.LIUCONG_EVAL_HOME||path.join(os.homedir(),'.local/share/liucong-model-eval'));
if([path.parse(DATA).root,os.homedir(),'/Users','/usr','/etc','/opt','/private','/tmp','/private/tmp'].includes(DATA))throw Error('LIUCONG_EVAL_HOME须是专用子目录，不能是系统目录或整个用户主目录');
export const CONFIG=path.join(DATA,'config.json');
export const DEFAULT_BANK=path.join(SKILL,'assets/demo/bank.json');
export const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
export const args=(argv=process.argv.slice(2))=>Object.fromEntries(argv.filter(x=>x.startsWith('--')).map(x=>{const n=x.indexOf('=');return n<0?[x.slice(2),true]:[x.slice(2,n),x.slice(n+1)]}));
export const json=async p=>JSON.parse(await fs.readFile(p,'utf8'));
export async function writeJSON(p,data){await fs.mkdir(path.dirname(p),{recursive:true,mode:0o700});const tmp=p+'.'+crypto.randomUUID()+'.tmp';await fs.writeFile(tmp,JSON.stringify(data,null,2)+'\n',{mode:0o600});await fs.rename(tmp,p);}
export async function config(){try{return await json(CONFIG)}catch(e){if(e.code==='ENOENT')throw Error('尚未初始化：在 Skill 目录运行 node scripts/setup.mjs init');throw e;}}
export function resolveCLI(explicit){const r=explicit||process.env.LIUCONG_CLAUDE_BIN||spawnSync('/usr/bin/which',['claude'],{encoding:'utf8'}).stdout?.trim();if(!r)throw Error('未找到 Claude Code：先按 references/initialization.md 安装，或传 --claude=/完整路径/claude');return path.resolve(r);}
export function validId(id){return typeof id==='string'&&/^[a-zA-Z0-9][a-zA-Z0-9_.-]{0,99}$/.test(id);}
export async function localFile(root,relative){if(typeof relative!=='string'||path.isAbsolute(relative)||relative.split(/[\\/]/).includes('..'))throw Error('素材必须是题库内相对路径');const base=await fs.realpath(root),p=await fs.realpath(path.join(base,relative));if(!p.startsWith(base+path.sep))throw Error('素材符号链接越界');if(!(await fs.stat(p)).isFile())throw Error('素材不是文件');return p;}
export async function loadBank(file=DEFAULT_BANK){
 const b=await json(file),root=path.dirname(path.resolve(file)),ids=new Set();
 if(b.schemaVersion!==1||!Array.isArray(b.cases)||!b.cases.length)throw Error('题库要求 schemaVersion:1 与非空 cases 数组');
 for(const c of b.cases){
  if(!validId(c.id)||ids.has(c.id))throw Error('非法或重复题号：'+c.id);ids.add(c.id);
  if(!['qa','code'].includes(c.kind)||!['simple','medium','complex','preparation'].includes(c.tier)||typeof c.prompt!=='string'||!c.prompt.trim())throw Error('题型、难度或题面不完整：'+c.id);
  if(!Number.isInteger(c.seconds)||c.seconds<30||c.seconds>1800)throw Error('seconds 应为30—1800整数：'+c.id);
  if(!c.source||!['demo','custom','benchmark'].includes(c.source.kind)||!c.source.title)throw Error('缺少来源：'+c.id);
  if(c.source.kind==='benchmark'&&['url','revision','split','itemId','license','protocol'].some(k=>!c.source[k]))throw Error('benchmark 来源元数据不完整：'+c.id);
  if(!Array.isArray(c.images)||c.images.length>8||!Array.isArray(c.tags))throw Error('images/tags 格式错误');
  if(!c.scoring||!['exact','choice','manual'].includes(c.scoring.type))throw Error('缺少评分方式');
  if(c.scoring.type!=='manual'&&(!Array.isArray(c.scoring.answers)||!c.scoring.answers.length||c.scoring.answers.some(a=>typeof a!=='string')))throw Error('缺少标准答案');
  if(c.scoring.type==='choice'&&c.scoring.answers.some(a=>!/^[A-Z]$/.test(a)))throw Error('选择题答案须为单个大写字母');
  if(c.scoring.type==='manual'&&(!Array.isArray(c.scoring.rubric)||!c.scoring.rubric.length))throw Error('人工评分须给rubric');
  let imageBytes=0;
  for(const im of c.images){const f=await localFile(root,im);const b=await fs.readFile(f);imageType(b);imageBytes+=b.length;if(b.length>5*1024*1024)throw Error('单图超过5MiB，先确认压缩协议并记录变换');}
  if(imageBytes>20*1024*1024)throw Error('单题图片合计超过20MiB，先定义预处理协议');
  for(const f of c.files||[]){if(!validId(f.target)||['settings.json','sandbox.sb','prompt.txt','result.json','bash-env.sh'].includes(f.target))throw Error('输入目标名非法');await localFile(root,f.path);}
  for(const f of c.outputs||[])if(!validId(f))throw Error('产物须使用普通文件名');
 }
 return {bank:b,root,sha256:hash(await fs.readFile(file))};
}
export function imageType(b){if(b.subarray(0,8).equals(Buffer.from([137,80,78,71,13,10,26,10])))return'image/png';if(b[0]===255&&b[1]===216)return'image/jpeg';if(b.toString('ascii',0,4)==='RIFF'&&b.toString('ascii',8,12)==='WEBP')return'image/webp';throw Error('仅支持真实PNG/JPEG/WebP图片');}
export function selectCases(bank,o,prefs={}){
 let xs=bank.cases.filter(c=>c.tier!=='preparation');
 if(o.cases){const ids=String(o.cases).split(',');xs=ids.map(id=>{const c=bank.cases.find(c=>c.id===id);if(!c)throw Error('未知题号：'+id);return c;});}
 else {const tier=o.tier||prefs.tier||'simple';xs=xs.filter(c=>c.tier===tier);const tags=o.tags?String(o.tags).split(','):prefs.tags||[];if(tags.length)xs=xs.filter(c=>tags.some(t=>c.tags.includes(t)));
 const seed=String(o.seed||prefs.seed||'42');xs=xs.sort((a,b)=>hash(seed+':'+a.id).localeCompare(hash(seed+':'+b.id)));
 const count=Number(o.count||prefs.count||3);if(!Number.isInteger(count)||count<1||count>1000)throw Error('count应为1—1000');xs=xs.slice(0,count);}
 if(!xs.length)throw Error('没有匹配题目；检查bank/tier/tags');if(new Set(xs.map(c=>c.id)).size!==xs.length)throw Error('不能重复题号');return xs;
}
export function score(answer,s){if(s.type==='manual')return{pass:null,needsReview:true};const a=answer.trim();if(s.type==='choice'){const m=a.match(/^(?:\(([A-Z])\)|([A-Z]))[.!。]?$/);return{pass:!!m&&s.answers.includes(m[1]||m[2]),needsReview:!m,rule:'strict-choice-v1'};}const norm=x=>s.normalization==='compact'?x.replace(/\s/g,''):x.trim();return{pass:s.answers.some(x=>norm(x)===norm(a)),needsReview:false,rule:'exact-'+(s.normalization||'trim')};}
export function profile(work,claude,port){
 const allow=[work,path.dirname(claude),path.dirname(process.execPath),'/System','/usr','/bin','/sbin','/opt/homebrew/Cellar','/opt/homebrew/opt','/Library/Apple','/private/etc/ssl','/private/etc/hosts','/private/etc/localtime','/dev/null','/dev/tty','/dev/urandom'];
 // macOS dyld reads the root directory itself during process startup, not its descendants.
 allow.push('/');
 return ['(version 1)','(allow default)','(deny file-read* (subpath "/"))','(allow file-read-metadata)',...allow.map(p=>'(allow file-read* ('+(p==='/'?'literal':'subpath')+' '+JSON.stringify(p)+'))'),'(deny file-write* (subpath "/"))','(allow file-write* (subpath '+JSON.stringify(work)+') (literal "/dev/null") (literal "/dev/tty"))','(deny network*)','(allow network-outbound (remote ip "localhost:'+port+'"))','(allow network-bind (local ip "localhost:18991"))','(allow network-inbound (local ip "localhost:18991"))','(allow network-outbound (remote ip "localhost:18991"))','(deny appleevent-send)'].join('\n');
}
export async function brokerClient(){const b=await json(path.join(DATA,'broker-client.json')).catch(()=>{throw Error('临时连接未启动：node scripts/connect.mjs');});const u=new URL(b.url);if(u.protocol!=='http:'||u.hostname!=='127.0.0.1'||!u.port)throw Error('本地连接地址非法');return b;}
export const redact=(s,tokens=[])=>tokens.reduce((v,t)=>t?v.split(t).join('[REDACTED]'):v,String(s)).replace(/ark-[a-zA-Z0-9-]{20,}/g,'[REDACTED]');
