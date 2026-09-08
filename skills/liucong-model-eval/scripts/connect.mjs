import fs from 'node:fs/promises';
import path from 'node:path';
import readline from 'node:readline';
import {DATA,config,json} from './core.mjs';
import {startBroker} from './broker.mjs';
const c=await config();
try{const b=await json(path.join(DATA,'broker-client.json'));const r=await fetch(b.url+'/health',{signal:AbortSignal.timeout(1500)});if(r.ok){console.log('已有临时连接，保留该连接。更换Key时先在原终端Ctrl+C退出。');process.exit(0);}}catch{}
const lock=path.join(DATA,'connection.lock');let lockHandle;
try{lockHandle=await fs.open(lock,'wx',0o600);}catch{throw Error('连接锁存在。先确认旧连接已退出；异常退出后可仅删除 connection.lock，再重启。不要终止不明进程。');}
let key=process.env.LIUCONG_AGENT_KEY||'';delete process.env.LIUCONG_AGENT_KEY;
const unlock=async()=>{await lockHandle.close().catch(()=>{});await fs.unlink(lock).catch(()=>{});};
try{
 if(!key){
  if(!process.stdin.isTTY)throw Error('请在终端运行connect，由本人隐藏输入Key；不要把Key发到聊天或作为命令参数');
  process.stdout.write('输入自己的 Agent Plan Key（不显示，回车确认，Ctrl+C取消）：');
  readline.emitKeypressEvents(process.stdin);process.stdin.setRawMode(true);process.stdin.resume();
  key=await new Promise((resolve,reject)=>{let input='';const onKey=(s,k)=>{if(k?.ctrl&&k.name==='c'){cleanup();reject(Error('已取消'));}else if(k?.name==='return'){cleanup();resolve(input.trim());}else if(k?.name==='backspace')input=input.slice(0,-1);else if(s&&!k?.ctrl&&!k?.meta)input+=s;};const cleanup=()=>{process.stdin.off('keypress',onKey);process.stdin.setRawMode(false);process.stdin.pause();};process.stdin.on('keypress',onKey);});
 }
 if(key.length<16||/[\r\n]/.test(key))throw Error('Key格式不正确，未连接');
 const b=await startBroker({key,dataDir:DATA,models:c.models,maxRequests:c.maxRequests});key='';
 console.log('\n临时连接已启动（尚未验证上游Key）。保持此终端；另一终端先跑 connection。Ctrl+C结束后需重新输入Key。');
 let closing=false;const close=async()=>{if(closing)return;closing=true;await b.close();await unlock();process.exit(0);};
 process.on('SIGINT',close);process.on('SIGTERM',close);
}catch(e){if(process.stdin.isTTY&&process.stdin.isRaw)process.stdin.setRawMode(false);await unlock();console.error(e.message);process.exitCode=1;}
