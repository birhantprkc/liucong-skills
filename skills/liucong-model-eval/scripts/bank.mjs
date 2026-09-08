import fs from 'node:fs/promises';
import path from 'node:path';
import {args,loadBank,localFile,writeJSON,selectCases,DEFAULT_BANK,hash} from './core.mjs';
const o=args(),cmd=process.argv[2]||'validate',file=path.resolve(String(o.file||DEFAULT_BANK));const {bank,root,sha256}=await loadBank(file);
if(cmd==='validate')console.log(JSON.stringify({valid:true,name:bank.name,cases:bank.cases.length,sha256}));
else if(cmd==='select'){const xs=selectCases(bank,o);console.log(JSON.stringify({bank:bank.name,sha256,seed:o.seed||'42',cases:xs.map(c=>({id:c.id,tier:c.tier,source:c.source,seconds:c.seconds}))},null,2));}
else if(cmd==='import'){
 if(!o.out)throw Error('使用 --out=新题库目录');const out=path.resolve(String(o.out));await fs.mkdir(out,{recursive:false,mode:0o700});const copy=structuredClone(bank);
 for(const c of copy.cases){let i=0;for(const im of c.images){const p=await localFile(root,im),rel='assets/'+c.id+'-'+i+path.extname(p);await fs.mkdir(path.join(out,'assets'),{recursive:true});await fs.copyFile(p,path.join(out,rel));c.images[i++]=rel;}
 for(const f of c.files||[]){const p=await localFile(root,f.path),rel='assets/'+c.id+'-'+f.target;await fs.mkdir(path.join(out,'assets'),{recursive:true});await fs.copyFile(p,path.join(out,rel));f.path=rel;}}
 copy.importedFromSha256=sha256;await writeJSON(path.join(out,'bank.json'),copy);await loadBank(path.join(out,'bank.json'));console.log(path.join(out,'bank.json'));
}else throw Error('使用 validate / select / import');
