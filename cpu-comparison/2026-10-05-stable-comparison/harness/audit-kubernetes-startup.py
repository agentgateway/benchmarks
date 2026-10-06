#!/usr/bin/env python3
"""Check retained single-pod barriers and pre-load placement; no approval."""
import argparse,datetime,json
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('root',type=Path,help='Exported kclient directory')
p.add_argument('--phase',required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--gateway-samples',type=Path)
a=p.parse_args();base=a.root/'results/kubernetes'/a.phase
result={'phase':a.phase,'checks':[],'issues':[]}
def epoch(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
samples=[]
if a.gateway_samples:
 samples=[json.loads(line) for line in a.gateway_samples.read_text().splitlines()]
 samples=[(epoch(s['utc']),s) for s in samples]
digests={'agentgateway':'sha256:9d3e6044ddcdc0878b1787f77bd401252b95e22684203fb5e874c4c42d2ed90c','praxis-release':'sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8'}
for treatment in ['agentgateway','praxis-release']:
 d=base/treatment
 for name in ['switch','recovery-switch']:
  try:
   assert json.loads((d/(name+'.json')).read_text())['exit']==0
   records=[json.loads(line) for line in (d/(name+'.log')).read_text().splitlines() if line.startswith('{')]
   barriers=[x for x in records if x.get('single_pod_barrier') is True]
   assert len(barriers)==1
   b=barriers[0];assert b['stable_seconds']>=10
   assert b['expected_image'].split('@')[-1]==digests[treatment]
   assert len(b['endpoints'])==1 and b['endpoints'][0]['conditions']['ready'] is True
   assert not b['endpoints'][0]['conditions'].get('terminating',False)
   assert b['image_ids'] and all(i.endswith('@'+b['expected_image'].split('@')[-1]) for i in b['image_ids'])
   if name=='switch':
    items=json.loads((d/'placement.log').read_text())['items']
    pods=[x for x in items if x['kind']=='Pod' and x['metadata'].get('namespace')=='gateway-benchmark']
    assert len(pods)==1 and pods[0]['metadata']['uid']==b['pod_uid']
    assert not pods[0]['metadata'].get('deletionTimestamp')
    assert all(c['ready'] and 'running' in c['state'] for c in pods[0]['status']['containerStatuses'])
   result['checks'].append({'treatment':treatment,'stage':name,'barrier':b,'passed':True})
  except Exception as ex:
   result['issues'].append({'treatment':treatment,'stage':name,'error':repr(ex)})
 if a.gateway_samples:
  for f in sorted((d/'http').glob('*/execution.json')):
   try:
    e=json.loads(f.read_text());start=epoch(e.get('start',e.get('started')));end=epoch(e.get('end',e.get('finished')))
    selected=[s for t,s in samples if start<=t<=end]
    assert len(selected)>=5
    processes=[[c for c in s.get('containers',[]) if c['name'].startswith('gateway-benchmark/')] for s in selected]
    assert all(len(cs)==1 for cs in processes),[len(cs) for cs in processes]
    pids={cs[0]['pid'] for cs in processes};assert len(pids)==1,pids
    profiles={cs[0].get('network_profile','') for cs in processes}
    assert len(profiles)==1
    profile=next(iter(profiles))
    assert 'net.ipv4.ip_local_port_range = 10240\t65535' in profile
    assert 'net.ipv4.tcp_tw_reuse = 1\n' in profile
    assert 'net.ipv4.tcp_tw_reuse_delay = 1000\n' in profile
    assert 'net.ipv4.tcp_timestamps = 1\n' in profile
    assert all(cs[0].get('cpu.max','').split()==['200000','100000'] for cs in processes)
    result['checks'].append({'treatment':treatment,'stage':str(f.relative_to(d)),'samples':len(selected),'pids':sorted(pids),'network_profile':profile,'cpu_quota':'200000/100000','passed':True})
   except Exception as ex:
    result['issues'].append({'treatment':treatment,'stage':str(f.relative_to(d)),'error':repr(ex)})
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(result['checks']),'issues':len(result['issues'])}))
