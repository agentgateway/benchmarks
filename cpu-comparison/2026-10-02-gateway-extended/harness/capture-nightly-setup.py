#!/usr/bin/env python3
"""Capture generated nightly configuration once, without changing any resources."""
import argparse
import datetime
import json
import os
from pathlib import Path
import subprocess

p=argparse.ArgumentParser();p.add_argument('case',type=Path);a=p.parse_args()
assert 'praxis-nightly-20261002' in str(a.case) and a.case.name=='praxis'
assert (a.case/'start.txt').exists() and not (a.case/'end.txt').exists()
if (a.case/'nightly-config.json').exists():
    raise SystemExit(0)
env=dict(os.environ,KUBECONFIG='/etc/rancher/k3s/benchmark.kubeconfig')
base=['kubectl','-n','gateway-conformance-infra']
selector='app.kubernetes.io/name=praxis'
r=subprocess.run([*base,'get','deployments,configmaps','-l',selector,'-o','json'],env=env,capture_output=True,text=True,check=True)
data=json.loads(r.stdout)
if sum(i['kind']=='Deployment' for i in data['items'])!=4 or sum(i['kind']=='ConfigMap' for i in data['items'])!=4:
    raise SystemExit('Base configuration not ready; retry capture later')
# This raw remote file contains generated fixture keys; sanitize before publication.
(a.case/'nightly-config.json').write_text(r.stdout)
r=subprocess.run([*base,'logs','-l',selector,'--all-containers=true','--prefix','--timestamps','--tail=100','--max-log-requests=8'],env=env,capture_output=True,text=True)
(a.case/'nightly-dataplane.log').write_text(r.stdout)
(a.case/'nightly-capture.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selector':selector,'log_exit':r.returncode,'log_stderr':r.stderr,'note':'Read-only generated-config and startup-log snapshot; runtime observer also retains crash diagnostics.'},indent=2)+'\n')
print('Captured four generated nightly Deployments/ConfigMaps and startup logs')
