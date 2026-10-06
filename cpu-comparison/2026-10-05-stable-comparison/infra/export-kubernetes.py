#!/usr/bin/env python3
"""Retain selected benchmark files, never cluster credentials or container stores."""
import argparse,concurrent.futures,datetime,hashlib,json,subprocess
from pathlib import Path
from transport import ssh,options,copy
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=root/'.work/exports'/a.label;out.mkdir(parents=True,exist_ok=False)
def capture(role):
 copy(role,[root/'infra/capture-runtime.sh'])
 inventory=ssh(role,'sudo bash /tmp/capture-runtime.sh');assert inventory.returncode==0,inventory.stderr
 remote=f'/tmp/benchmark-{a.label}-{role}.tar.gz'
 excludes=['venv','usr','public-tools','gateway-api','praxis-operator-source','*.tar.gz','*.tar','k3s','clusterloader2','gateway-conformance.test','mock-server','helm','host-samples.jsonl']
 cmd='sudo tar -czf '+remote+' '+ ' '.join('--exclude='+x for x in excludes)+' -C /opt/gateway-benchmark . && sudo chmod 644 '+remote
 r=ssh(role,cmd,timeout=180);assert r.returncode==0,r.stderr
 opts,host=options(role);dest=out/(role+'.tar.gz');subprocess.run(['/usr/bin/scp',*opts,host+':'+remote,str(dest)],check=True,timeout=180)
 (out/role).mkdir();subprocess.run(['tar','-xzf',str(dest),'-C',str(out/role)],check=True)
 r=ssh(role,'sudo cat /opt/gateway-benchmark/host-samples.jsonl',timeout=180);assert r.returncode==0;(out/role/'host-samples.jsonl').write_text(r.stdout)
 print(role,'exported',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(capture,['kclient','kgateway','kbackend','kcontroller','kcontrol']))
manifest={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':a.label,'files':{str(f.relative_to(out)):hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file() and (f.name.endswith('.tar.gz') or f.name=='host-samples.jsonl')}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out)
