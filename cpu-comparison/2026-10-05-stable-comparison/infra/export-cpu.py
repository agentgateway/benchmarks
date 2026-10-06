#!/usr/bin/env python3
"""Copy a read-only snapshot of CPU results and telemetry, omitting image layers."""
import argparse,hashlib,json,datetime,subprocess
from pathlib import Path
from transport import ssh,options,copy
p=argparse.ArgumentParser();p.add_argument('label');a=p.parse_args();root=Path(__file__).resolve().parents[1];out=root/'.work/exports'/a.label;out.mkdir(parents=True,exist_ok=False)
for role in ['client','gateway','backend']:
 copy(role,[root/'infra/capture-runtime.sh'])
 inventory=ssh(role,'sudo bash /tmp/capture-runtime.sh');assert inventory.returncode==0,inventory.stderr
 remote='/tmp/benchmark-'+a.label+'-'+role+'.tar.gz'
 # Never archive /etc, /home, /root, or cloud/cluster credentials.
 command=f'sudo tar -czf {remote} --exclude=venv --exclude=usr --exclude=fortio.tgz --exclude=mock-server --exclude=mock --exclude=*.tar.gz --exclude=host-samples.jsonl -C /opt/gateway-benchmark . && sudo chmod 644 {remote}'
 r=ssh(role,command,timeout=180);assert r.returncode==0,r.stderr
 opts,host=options(role);dest=out/(role+'.tar.gz');subprocess.run(['/usr/bin/scp',*opts,host+':'+remote,str(dest)],check=True,timeout=180)
 # Capture a live append-only telemetry prefix as a separate immutable snapshot.
 telemetry=out/(role+'-host-samples.jsonl');r=ssh(role,'sudo cat /opt/gateway-benchmark/host-samples.jsonl',timeout=120);assert r.returncode==0;telemetry.write_text(r.stdout)
 subprocess.run(['tar','-xzf',str(dest),'-C',str(out/role)] if (out/role).is_dir() else ['mkdir',str(out/role)],check=True)
 if not (out/role/'cpu.json').exists():subprocess.run(['tar','-xzf',str(dest),'-C',str(out/role)],check=True)
manifest={'captured_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'label':a.label,'files':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in out.iterdir() if f.is_file()}}
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(out)
