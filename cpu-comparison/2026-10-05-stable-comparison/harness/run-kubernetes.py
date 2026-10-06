#!/usr/bin/env python3
"""One Kubernetes performance/scale/recovery pass; conformance reported separately."""
import argparse,subprocess,json,datetime,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('phase',choices=['qualification','qualification-tcp','qualification-single-pod','qualification-image-pin','pass1','pass2','pass3']);a=p.parse_args()
os.environ['KUBECONFIG']='/etc/rancher/k3s/benchmark.kubeconfig';base=Path('/opt/gateway-benchmark');os.chdir(base)
if not a.phase.startswith('qualification'):
 marker=base/('kubernetes-qualification-approved.json' if a.phase=='pass1' else 'kubernetes-pass1-approved.json');assert json.loads(marker.read_text())['infrastructure_valid'] is True
out=base/'results/kubernetes'/a.phase;out.mkdir(parents=True,exist_ok=False)
orders={'qualification':['direct','agentgateway','praxis-release','praxis-nightly'],'pass1':['direct','agentgateway','praxis-release','praxis-nightly'],'pass2':['praxis-release','praxis-nightly','direct','agentgateway'],'pass3':['praxis-nightly','agentgateway','praxis-release','direct']}
def execute(cmd,path,timeout):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 with path.with_suffix('.log').open('w') as f:
  try:code=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=timeout).returncode
  except subprocess.TimeoutExpired:code='timeout'
 path.with_suffix('.json').write_text(json.dumps({'command':cmd,'exit':code,'started':start,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
 return code
for treatment in orders['qualification' if a.phase.startswith('qualification') else a.phase]:
 d=out/treatment;d.mkdir();code=execute(['bash','switch-gateway.sh',treatment],d/'switch',720)
 if code:
  if treatment!='praxis-nightly':raise SystemExit('Setup failed; preserve and attribute: '+str(d))
  assert execute(['venv/bin/python','capture-kubernetes-block.py',str(d/'setup-block')],d/'block-classification',60)==0,'Unknown setup failure; stop for review'
  (d/'COMPLETE').write_text('Verified setup block; dependent suites not evaluated\n')
  print(a.phase,treatment,'verified setup block',flush=True)
  continue
 endpoint=next(json.loads(s)['url'] for s in reversed((d/'switch.log').read_text().splitlines()) if s.startswith('{'))
 execute(['kubectl','get','nodes,pods,deployments,services','-A','-o','json'],d/'placement',60)
 cmd=['venv/bin/python','run-http.py','--treatment',treatment,'--url',endpoint,'--output',str(d/'http')]
 if a.phase=='qualification':cmd+=['--qualification']
 if a.phase in ['qualification-tcp','qualification-single-pod','qualification-image-pin']:cmd+=['--socket-qualification']
 assert execute(cmd,d/'http-execution',1000)==0
 if treatment!='direct':
  cls='agentgateway' if treatment=='agentgateway' else 'praxis'
  for count in ([10] if a.phase.startswith('qualification') else [1000,5000]):
   assert execute(['bash','run-scale.sh',cls,str(count),endpoint,str(d/f'scale-{count}')],d/f'scale-{count}-execution',1300)==0,'Inspect scale runner failure'
  assert execute(['bash','switch-gateway.sh',treatment],d/'recovery-switch',720)==0
  endpoint=next(json.loads(s)['url'] for s in reversed((d/'recovery-switch.log').read_text().splitlines()) if s.startswith('{'))
  assert execute(['venv/bin/python','run-recovery.py','--treatment',cls,'--url',endpoint,'--output',str(d/'recovery')],d/'recovery-execution',400)==0
 (d/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
 print(a.phase,treatment,'complete',flush=True)
(out/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
