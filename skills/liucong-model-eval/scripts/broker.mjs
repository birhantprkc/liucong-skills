import fs from 'node:fs/promises';
import path from 'node:path';
import http from 'node:http';
import crypto from 'node:crypto';
import {writeJSON,redact} from './core.mjs';
export async function startBroker({key,dataDir,models,maxRequests=200,upstreamURL='https://ark.cn-beijing.volces.com/api/plan',testOnly=false}){
 if(!key||typeof key!=='string')throw Error('缺少Key');
 if(upstreamURL!=='https://ark.cn-beijing.volces.com/api/plan'&&!(testOnly&&/^http:\/\/127\.0\.0\.1:\d+$/.test(upstreamURL)))throw Error('上游只允许官方Agent Plan入口');
 const master=crypto.randomBytes(32).toString('hex'),sessions=new Map();let calls=0;
 const send=(res,status,o)=>{res.writeHead(status,{'Content-Type':'application/json'});res.end(JSON.stringify(o));};
 const server=http.createServer(async(req,res)=>{
  try{
   if(req.url==='/health'&&req.method==='GET')return send(res,200,{ready:true,remainingRequests:Math.max(0,maxRequests-calls)});
   const token=req.headers['x-api-key']||String(req.headers.authorization||'').replace(/^Bearer /,'');
   if(req.method==='DELETE'&&req.url?.startsWith('/session/')){if(token!==master)return send(res,401,{error:'Unauthorized'});sessions.delete(req.url.slice(9));return send(res,200,{revoked:true});}
   const register=req.url==='/session'&&req.method==='POST',session=sessions.get(token);
   if(register?token!==master:!session)return send(res,401,{error:'Unauthorized'});
   if(!register&&(req.method!=='POST'||!/^\/v1\/messages(?:\?[^#]*)?$/.test(req.url)))return send(res,403,{error:'Messages endpoint only'});
   const bs=[];let n=0;for await(const b of req){n+=b.length;if(n>40*1024*1024)return send(res,413,{error:'Payload too large'});bs.push(b);}
   const payload=JSON.parse(Buffer.concat(bs).toString('utf8'));
   if(register){
    if(!models.includes(payload.model))return send(res,403,{error:'Model not configured'});
    const seconds=Number(payload.seconds);if(!Number.isInteger(seconds)||seconds<30||seconds>1800)return send(res,400,{error:'Invalid budget'});
    const nonce=crypto.randomBytes(32).toString('hex');sessions.set(nonce,{model:payload.model,expires:Date.now()+(seconds+30)*1000,calls:0,seconds});
    return send(res,200,{token:nonce});
   }
   if(Date.now()>session.expires)return send(res,401,{error:'Run session expired'});
   if(payload.model!==session.model)return send(res,403,{error:'Run is bound to one model'});
   if(calls>=maxRequests||session.calls>=60)return send(res,429,{error:'Request budget reached'});
   calls++;session.calls++;
   const ac=new AbortController(),timer=setTimeout(()=>ac.abort(),(session.seconds+20)*1000);
   res.on('close',()=>{if(!res.writableEnded)ac.abort();});
   try{
    const headers={'Content-Type':'application/json','x-api-key':key,'Authorization':'Bearer '+key,'anthropic-version':req.headers['anthropic-version']||'2023-06-01'};
    if(req.headers['anthropic-beta'])headers['anthropic-beta']=req.headers['anthropic-beta'];
    const upstream=await fetch(upstreamURL+req.url,{method:'POST',body:JSON.stringify(payload),headers,redirect:'error',signal:ac.signal});
    res.writeHead(upstream.status,{'Content-Type':upstream.headers.get('content-type')||'application/json'});
    for await(const chunk of upstream.body)if(!res.destroyed)res.write(chunk);res.end();
   }finally{clearTimeout(timer);}
  }catch(e){if(!res.headersSent)send(res,502,{error:redact(e.message,[key,master])});else res.end();}
 });
 await fs.mkdir(dataDir,{recursive:true,mode:0o700});
 await new Promise((ok,no)=>{server.once('error',no);server.listen(0,'127.0.0.1',ok);});
 const url='http://127.0.0.1:'+server.address().port,clientFile=path.join(dataDir,'broker-client.json');
 await writeJSON(clientFile,{url,token:master,createdAt:new Date().toISOString()});
 return {url,master,close:async()=>{server.closeAllConnections();await new Promise(r=>server.close(r));const current=JSON.parse(await fs.readFile(clientFile,'utf8').catch(()=>'{}'));if(current.token===master)await fs.unlink(clientFile);sessions.clear();key='';}};
}
