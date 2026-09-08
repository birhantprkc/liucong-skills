#!/usr/bin/env python3
"""Fetch a small, provenance-locked subset from official Hugging Face dataset viewers.
Run with: uv run --python 3.11 scripts/import-benchmark.py --help
Only Python standard library is needed. Never requests an inference key.
"""
import argparse, ast, hashlib, json, pathlib, re, urllib.parse, urllib.request
from datetime import datetime, timezone
CATALOG = {
    "mmmu": ("MMMU/MMMU", "Math", "validation", "Apache-2.0"),
    "blink": ("BLINK-Benchmark/BLINK", "Spatial_Relation", "val", "Apache-2.0"),
    "realworldqa": ("xai-org/RealworldQA", "default", "test", "CC-BY-ND-4.0"),
}
def read_url(url):
    host = urllib.parse.urlparse(url).hostname
    if host not in {"huggingface.co", "datasets-server.huggingface.co"}:
        raise ValueError("Only official dataset and viewer hosts are accepted")
    req = urllib.request.Request(url, headers={"User-Agent":"liucong-model-eval/2.0"})
    with urllib.request.urlopen(req, timeout=90) as response:
        if urllib.parse.urlparse(response.url).hostname not in {"huggingface.co", "datasets-server.huggingface.co"}:
            raise ValueError("Unexpected download redirect")
        payload = response.read(40 * 1024 * 1024 + 1)
    if len(payload) > 40 * 1024 * 1024:
        raise ValueError("Download exceeds 40MiB limit")
    return payload
def read_json(url):
    return json.loads(read_url(url))
def adapter(name,row):
    if name == "blink":
        prompt = row["prompt"]
        answer = str(row["answer"]).strip().strip("()")
        return prompt, {"type":"choice","answers":[answer]}
    if name == "mmmu":
        options = row.get("options",[])
        if isinstance(options,str):
            options = ast.literal_eval(options)
        if not isinstance(options,list) or not all(isinstance(v,str) for v in options):
            raise ValueError("Unexpected MMMU options schema")
        prompt = row["question"]
        if row.get("question_type") == "multiple-choice":
            prompt += "\n" + "\n".join(f"{chr(65+i)}. {v}" for i,v in enumerate(options))
            prompt += "\nAnswer with the option letter only."
            return prompt, {"type":"choice","answers":[str(row["answer"]).strip().strip("()")]}
        return prompt, {"type":"manual","rubric":["Use the official open-ended scorer and answer from source-records.json; do not treat this subset adapter as the official scorer."]}
    prompt = row["question"]
    answer = str(row["answer"]).strip()
    return prompt, {"type":"exact","answers":[answer],"normalization":"trim"}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source",choices=CATALOG,required=True)
    p.add_argument("--config");p.add_argument("--split");p.add_argument("--offset",type=int,default=0)
    p.add_argument("--count",type=int,default=3);p.add_argument("--out",required=True)
    a=p.parse_args()
    if not 1<=a.count<=100 or a.offset<0: p.error("count must be 1–100; offset >=0")
    dataset,default_config,default_split,license_name=CATALOG[a.source]
    subset=a.config or default_config;split=a.split or default_split
    out=pathlib.Path(a.out).expanduser().resolve()
    if out.exists(): p.error("out must be a new directory; do not overwrite a frozen bank")
    info_url="https://huggingface.co/api/datasets/"+dataset
    meta=read_json(info_url);revision=meta["sha"]
    params=urllib.parse.urlencode(dict(dataset=dataset,config=subset,split=split,offset=a.offset,length=a.count))
    data=read_json("https://datasets-server.huggingface.co/rows?"+params)
    rows=data.get("rows",[])
    if not rows: raise ValueError("No rows returned; check source/config/split")
    prepared=[];raw=[];blobs={}
    snapshot_hash=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    for wrapped in rows:
        row=wrapped["row"];index=wrapped["row_idx"]
        prompt,scoring=adapter(a.source,row)
        source_id=str(row.get("id") or row.get("idx") or index)
        case_id=a.source+"-"+re.sub(r"[^a-zA-Z0-9_.-]","-",source_id)
        if len(case_id)>100: case_id=case_id[:80]+"-"+hashlib.sha256(source_id.encode()).hexdigest()[:12]
        keys=sorted([k for k,v in row.items() if k=="image" or re.fullmatch(r"image_\d+",k)],key=lambda k:int(k.split("_")[-1]) if "_" in k else 0)
        images=[];image_hashes=[]
        for k in keys:
            image=row[k]
            if image is None: continue
            url=image["src"];parsed=urllib.parse.urlparse(url)
            # Viewer cache may lag behind the repository. Refuse to mix revisions.
            cached=re.search(r"/--/([a-f0-9]{40})/--/",parsed.path)
            if not cached:
                raise ValueError("Cannot identify viewer image revision")
            blob=read_url(url)
            if blob.startswith(b"\x89PNG\r\n\x1a\n"): ext=".png"
            elif blob[:2]==b"\xff\xd8": ext=".jpg"
            elif blob[:4]==b"RIFF" and blob[8:12]==b"WEBP": ext=".webp"
            else: raise ValueError("Unsupported original image format; do not silently transform")
            if len(blob)>5*1024*1024: raise ValueError("Image exceeds 5MiB; preserve source and define an explicit transform first")
            relative="assets/"+case_id+"-"+k+ext;blobs[relative]=blob;images.append(relative)
            image_hashes.append({"file":relative,"sha256":hashlib.sha256(blob).hexdigest(),"sourcePath":parsed.path,"viewerImageRevision":cached.group(1),"width":image.get("width"),"height":image.get("height")})
        if not images: raise ValueError("Visual benchmark item has no image")
        prepared.append(dict(id=case_id,kind="qa",tier="simple",seconds=120,prompt=prompt,images=images,files=[],outputs=[],tags=[a.source,"vision",subset],scoring=scoring,
           source=dict(kind="benchmark",title=dataset,url="https://huggingface.co/datasets/"+dataset,revision="viewer-snapshot-sha256:"+snapshot_hash,observedRepositoryHead=revision,split=split,itemId=source_id,license=license_name,protocol="subset-strict-v1",subset=subset,modified=a.source=="mmmu",sampling=f"consecutive rows offset={a.offset} count={a.count}",imageHashes=image_hashes)))
        # Gold answers/explanations are retained here, never copied to the model sandbox.
        raw.append({k:({"sourceImage":k} if k in keys and v else v) for k,v in row.items()})
    if read_json(info_url)["sha"] != revision: raise ValueError("Dataset changed during import; no bank written")
    out.mkdir(parents=True,exist_ok=False)
    for relative,blob in blobs.items():
        dest=out/relative;dest.parent.mkdir(exist_ok=True);dest.write_bytes(blob)
    (out/"bank.json").write_text(json.dumps(dict(schemaVersion=1,name=f"{dataset} / {subset} / subset",fetchedAt=datetime.now(timezone.utc).isoformat(),cases=prepared),ensure_ascii=False,indent=2),encoding="utf8")
    (out/"source-records.json").write_text(json.dumps(raw,ensure_ascii=False,indent=2),encoding="utf8")
    (out/"ATTRIBUTION.md").write_text(f"# {dataset}\n\nOfficial source: https://huggingface.co/datasets/{dataset}\n\nDataset revision: {revision}\n\nDataset card license: {license_name}\n\nImages kept as supplied by the official viewer, without cropping, resizing or repainting. A small subset with our answer-format/scoring protocol; not an official benchmark score. Review per-image and original-source rights before redistribution.\n",encoding="utf8")
    print(json.dumps({"bank":str(out/"bank.json"),"cases":len(prepared),"revision":revision},ensure_ascii=False))
if __name__=="__main__": main()
