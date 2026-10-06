#!/usr/bin/env python3
"""Disable inherited probes on stopped containers, preserving all other settings."""
import json,shlex
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
active=ssh('client',"systemctl list-units --state=running --no-legend 'common-*' 'native-*'")
assert active.returncode==0 and not active.stdout.strip(),'Wait for the active CPU treatment to finish'
r=ssh('gateway','sudo docker stop agentgateway praxis-release praxis-nightly agentgateway-native praxis-ai >/dev/null && sudo docker inspect agentgateway praxis-release praxis-nightly agentgateway-native praxis-ai');assert r.returncode==0
containers=json.loads(r.stdout);out=root/'evidence/qualification';(out/'healthcheck-before-inspect.json').write_text(json.dumps(containers,indent=2)+'\n')
for c in containers:
 name=c['Name'].lstrip('/');assert not c['State']['Running']
 if not c['Config'].get('Healthcheck'):continue
 # Recreate only the stopped Praxis containers; no build, pull or product patch.
 assert name in ['praxis-release','praxis-nightly','praxis-ai']
 args=['sudo','docker','create','--no-healthcheck','--name',name,'--network=host','--cpuset-cpus=2,3','--cpus=2','--memory=2g','--ulimit','nofile=65536:65536']
 for b in c['HostConfig']['Binds']:args+=['-v',b]
 if name!='praxis-ai':args+=['--entrypoint','praxis']
 args += [c['Config']['Image'],'-c','/etc/config.yaml']
 r=ssh('gateway',shlex.join(['sudo','docker','rm',name])+' && '+shlex.join(args));assert r.returncode==0,r.stderr
r=ssh('gateway','sudo docker inspect agentgateway praxis-release praxis-nightly agentgateway-native praxis-ai');assert r.returncode==0
v=json.loads(r.stdout)
for c in v:
 h=c['Config'].get('Healthcheck');assert h is None or h['Test']==['NONE']
 assert c['HostConfig']['NanoCpus']==2000000000 and c['HostConfig']['Memory']==2147483648 and c['HostConfig']['CpusetCpus']=='2,3'
(out/'healthcheck-disabled-inspect.json').write_text(json.dumps(v,indent=2)+'\n')
# Add the user-requested October2 AI nightly, now resolved by its publishing history.
image='ghcr.io/praxis-proxy/ai@sha256:727c4cb043af573cfb812208475dc6b290570b72ff01d07c6b7ca85dc09155e4'
r=ssh('gateway','sudo docker pull '+image+' && sudo docker create --no-healthcheck --name praxis-ai-nightly --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v /opt/gateway-benchmark/praxis-native.yaml:/etc/config.yaml:ro '+image+' -c /etc/config.yaml',timeout=180)
assert r.returncode==0,r.stderr
from transport import copy
copy('client',[root/'harness/run-ai-native.py',root/'harness/qualify-ai-native.py'])
r=ssh('client','sudo cp /tmp/run-ai-native.py /tmp/qualify-ai-native.py /opt/gateway-benchmark/');assert r.returncode==0,r.stderr
r=ssh('gateway','sudo docker inspect praxis-ai-nightly && sudo docker image inspect '+image);assert r.returncode==0
(out/'native-nightly-inspect.txt').write_text(r.stdout)
print('Inherited probes disabled; October2 AI nightly installed; requalification still required')
