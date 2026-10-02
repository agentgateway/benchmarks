#!/usr/bin/env python3
"""Capture actual route state at 5 and 9 minutes of each scale case."""
import datetime,json,os,pathlib,re,subprocess,time
source=pathlib.Path('/opt/benchmark/gateway-lifecycle.log')
out=pathlib.Path('/opt/benchmark/scale-observations');out.mkdir(exist_ok=True)
env=dict(os.environ,KUBECONFIG='/opt/benchmark/kubeconfig')
seen=set()
while True:
    lines=source.read_text().splitlines() if source.exists() else []
    if lines:
        parts=lines[-1].split()
        if len(parts)==2 and re.fullmatch(r'r1-(agentgateway-agentgateway|praxis-praxis)-scale-(10|50)x100',parts[1]):
            age=(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(parts[0])).total_seconds()
            for seconds in (300,540):
                key=f'{parts[1]}-t{seconds}'
                if seconds<=age<590 and key not in seen:
                    seen.add(key);d=out/key
                    if d.exists(): continue
                    d.mkdir()
                    (d/'captured-at.txt').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
                    with (d/'routes.json').open('w') as f:
                        subprocess.run(['kubectl','get','httproute','-A','-o','json'],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=50)
                    with (d/'gateways.json').open('w') as f:
                        subprocess.run(['kubectl','get','gateway','-A','-o','json'],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=30)
                    for ns in ('agentgateway','praxis'):
                        with (d/f'{ns}-deployment-state.json').open('w') as f:
                            subprocess.run(['kubectl','get','pods,deployments,configmaps','-n',ns,'-o','json'],stdout=f,stderr=subprocess.STDOUT,env=env,timeout=30)
    time.sleep(5)
