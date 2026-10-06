#!/usr/bin/env python3
"""Require a stable, single-pod serving topology before steady-state tests."""
import argparse,json,subprocess,time
p=argparse.ArgumentParser();p.add_argument('--expected-image',required=True);a=p.parse_args()
expected_digest=a.expected_image.split('@')[-1]
assert expected_digest.startswith('sha256:')
start=time.monotonic();stable_since=None;previous=None;last=None
while time.monotonic()-start<300:
 raw=subprocess.check_output(['kubectl','get','pods,deployments,endpointslices.discovery.k8s.io','-n','gateway-benchmark','-o','json'],text=True,timeout=20)
 items=json.loads(raw)['items'];pods=[x for x in items if x['kind']=='Pod'];deploys=[x for x in items if x['kind']=='Deployment'];slices=[x for x in items if x['kind']=='EndpointSlice']
 endpoints=[e for s in slices for e in s.get('endpoints',[])]
 good=len(pods)==len(deploys)==len(endpoints)==1
 if good:
  pod,dep,endpoint=pods[0],deploys[0],endpoints[0];status=dep.get('status',{});containers=pod.get('status',{}).get('containerStatuses',[])
  good=(pod['metadata'].get('deletionTimestamp') is None and dep['spec']['replicas']==1 and status.get('observedGeneration',0)>=dep['metadata']['generation'] and all(status.get(k)==1 for k in ['replicas','updatedReplicas','readyReplicas','availableReplicas']) and bool(containers) and all(c['ready'] and 'running' in c['state'] for c in containers) and endpoint.get('conditions',{}).get('ready') is True and not endpoint.get('conditions',{}).get('terminating',False) and endpoint.get('addresses')==[pod['status']['podIP']])
  good=good and all(c.get('imageID','').endswith('@'+expected_digest) for c in containers) and all(c['image'].endswith('@'+expected_digest) for c in dep['spec']['template']['spec']['containers'])
 signature=json.dumps({'pods':[(p['metadata']['uid'],p['metadata'].get('deletionTimestamp'),[(c['name'],c.get('restartCount'),c.get('containerID')) for c in p.get('status',{}).get('containerStatuses',[])]) for p in pods],'deployments':[(d['metadata']['generation'],d.get('status',{}).get('observedGeneration')) for d in deploys],'endpoints':endpoints},sort_keys=True)
 last={'pods':len(pods),'deployments':len(deploys),'endpoints':len(endpoints),'eligible':good}
 if good and signature==previous:
  if stable_since is not None and time.monotonic()-stable_since>=10:
   print(json.dumps({'single_pod_barrier':True,'expected_image':a.expected_image,'stable_seconds':time.monotonic()-stable_since,'wait_seconds':time.monotonic()-start,'pod':pod['metadata']['name'],'pod_uid':pod['metadata']['uid'],'image_ids':[c.get('imageID') for c in containers],'endpoints':endpoints}));raise SystemExit(0)
 else:stable_since=time.monotonic() if good else None
 previous=signature;time.sleep(1)
raise SystemExit('Single-pod topology did not stabilize: '+json.dumps(last))
