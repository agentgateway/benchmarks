#!/usr/bin/env python3
"""Capture and verify the known unmodified operator/nightly naming incompatibility."""
import argparse,json,subprocess,datetime,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('output',type=Path);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
os.environ['KUBECONFIG']='/etc/rancher/k3s/benchmark.kubeconfig'
def get(args):
 r=subprocess.run(['kubectl',*args],capture_output=True,text=True,check=True);return r.stdout
objects=get(['get','gateways,httproutes,deployments,pods,configmaps','-n','gateway-benchmark','-o','json']);(a.output/'objects.json').write_text(objects)
nodes=json.loads(get(['get','nodes','-o','json']));(a.output/'nodes.json').write_text(json.dumps(nodes,indent=2))
logs=get(['logs','-n','gateway-benchmark','-l','app.kubernetes.io/name=praxis','--all-containers=true','--tail=100','--prefix']);(a.output/'logs.txt').write_text(logs)
items=json.loads(objects)['items'];pods=[x for x in items if x['kind']=='Pod'];assert len(pods)==1
status=pods[0]['status']['containerStatuses'][0]
assert 'be62d256d5ec92aacb1216baba506aac763e2100f9eb361820a5c27c54e17be8' in status['imageID']
assert status['lastState']['terminated']['exitCode']==1 and status['lastState']['terminated']['reason']!='OOMKilled'
assert "cluster name 'gateway-backend~backend~8081' must contain only ASCII alphanumeric, '_', or '-'" in logs
assert all(any(c['type']=='Ready' and c['status']=='True' for c in n['status']['conditions']) for n in nodes['items'])
(a.output/'blocked.json').write_text(json.dumps({'recorded_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'classification':'stock operator/core nightly configuration incompatibility','infrastructure_nodes_ready':True,'image':status['imageID'],'http':'not evaluated','scale':'not evaluated','recovery':'not evaluated','reason':'Operator cluster name contains tilde, rejected by the pinned nightly','modified_product_config':False},indent=2)+'\n')
