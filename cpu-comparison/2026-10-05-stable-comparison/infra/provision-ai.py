#!/usr/bin/env python3
"""Provision this fixed-name CPU campaign; fails if names already exist."""
import argparse,json,subprocess,time
p=argparse.ArgumentParser();p.add_argument("--resume-after-create",action="store_true");args=p.parse_args()
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def run(cmd,**kw):return subprocess.run(cmd,check=True,text=True,**kw)
def ssh(role,cmd):return run(['gcloud','compute','ssh',f'gwcmp160-1005-{role}','--project','solo-oss','--zone','us-central1-a','--ssh-flag=-oServerAliveInterval=15','--ssh-flag=-oServerAliveCountMax=3','--command',cmd])
def copy(role,files):run(['gcloud','compute','scp',*[str(x) for x in files],f'gwcmp160-1005-{role}:/tmp/','--project','solo-oss','--zone','us-central1-a','--quiet'])
if not args.resume_after_create:run(['bash',str(root/'infra/create-ai-vms.sh')])
ips={}
for role in ['client','gateway','backend']:
 meta=json.loads((root/f'.work/create-{role}.json').read_text())[0];ips[role]=meta['networkInterfaces'][0]['networkIP']
(root/'.work/ips.json').write_text(json.dumps(ips,indent=2)+'\n')
for role in ips:
 for attempt in range(60):
  try:ssh(role,'test -f /opt/gateway-benchmark/ready');break
  except subprocess.CalledProcessError:time.sleep(10)
 else:raise SystemExit(f'{role} bootstrap failed; inspect startup log and clean up')
configs=root/'.work/configs';configs.mkdir(exist_ok=True)
for name in ['agentgateway','praxis']:
 source=(root/f'configs/ai/{name}.yaml').read_text().replace('10.128.0.63','__BENCHMARK_GATEWAY__').replace('10.128.15.192','__BENCHMARK_BACKEND__').replace('__BENCHMARK_GATEWAY__',ips['gateway']).replace('__BENCHMARK_BACKEND__',ips['backend'])
 (configs/f'{name}.yaml').write_text(source)
# Reuse the previous campaign's byte-identical Go fixture binary.
assert (root/'.work/mock-server').is_file()
for role in ips:
 files=[root/'infra'/f'setup-{role}.sh',root/'infra/setup-ai-network.sh',root/'harness/collect-host.py']
 if role=='backend':files+=[root/'.work/mock-server']
 if role=='gateway':files+=[configs/'agentgateway.yaml',configs/'praxis.yaml']
 if role=='client':files+=[root/'harness'/name for name in ['run-common.py','run-ai.py','run-http.py','qualify-ai.py','check-cancellation.py']]
 copy(role,files)
 if role=='client':
  copy(role,[root/'harness/run-common.py'])
  ssh(role,'sudo cp /tmp/run-common.py /opt/gateway-benchmark/')
 ssh(role,'sudo cp '+ ' '.join('/tmp/'+x.name for x in files)+' /opt/gateway-benchmark/ && sudo bash /opt/gateway-benchmark/setup-ai-network.sh && sudo bash /opt/gateway-benchmark/setup-'+role+'.sh')
 ssh(role,'sudo systemd-run --unit=benchmark-collector --property=RuntimeMaxSec=42000 /usr/bin/python3 /opt/gateway-benchmark/collect-host.py')
print(json.dumps({'private_ips':ips,'next':'Run qualification; inspect all results before measured pass 1.'},indent=2))
