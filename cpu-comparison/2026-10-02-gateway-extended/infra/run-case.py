#!/usr/bin/env python3
"""Dispatch exactly one isolated upstream test run; inspect results before repeating."""
import argparse,datetime,json,shlex,subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('campaign',choices=['praxis-v0.5.2','praxis-nightly-20261002']);p.add_argument('repetition',choices=['qualification','pass1','pass2','pass3']);p.add_argument('product',choices=['agentgateway','praxis']);p.add_argument('--smoke',action='store_true');p.add_argument('--run-label',choices=['tcp-client-fixed','maintenance-fixed']);a=p.parse_args()
root=Path(__file__).resolve().parents[1];unit='gwext-'+a.campaign.replace('.','-')+'-'+a.repetition+'-'+a.product
if a.repetition in ['pass2','pass3']:
 review=json.loads((root/('evidence/validity/'+a.campaign+'-pass1.json')).read_text())
 assert review['infrastructure_valid'] is True,'First-pair infrastructure review has not passed'
if a.run_label:unit+='-'+a.run_label
out=root/'evidence/dispatch';out.mkdir(exist_ok=True);f=out/(unit+'.json');assert not f.exists(),'Do not overwrite a dispatch record'
base=['gcloud','compute','ssh','gwext-1002-kclient','--project=solo-oss','--zone=us-central1-a']
check=subprocess.run([*base,'--command',"sudo systemctl list-units --state=running --no-legend 'gwext-*'"],capture_output=True,text=True,check=True)
assert not check.stdout.strip(),'An earlier campaign job is still running: '+check.stdout
cmd=['sudo','systemd-run','--unit='+unit,'--property=RuntimeMaxSec=12600','--property=LimitNOFILE=1048576','/bin/bash','/opt/gateway-benchmark/run-one.sh',a.campaign,a.repetition,a.product,'smoke' if a.smoke else 'full']
r=subprocess.run([*base,'--command',shlex.join(cmd)],capture_output=True,text=True)
record={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'unit':unit,'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr};f.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record,indent=2));raise SystemExit(r.returncode)
