#!/usr/bin/env python3
"""Add stopped native-AI containers and client tools to qualified CPU hosts."""
import json
from pathlib import Path
from transport import ssh,copy
root=Path(__file__).resolve().parents[1];ips=json.loads((root/'.work/ips.json').read_text());out=root/'.work/configs';out.mkdir(exist_ok=True)
for name in ['agentgateway-native','praxis-native']:
 s=(root/f'configs/ai/{name}.yaml').read_text().replace('10.128.0.63','__GATEWAY__').replace('10.128.15.192','__BACKEND__').replace('__GATEWAY__',ips['gateway']).replace('__BACKEND__',ips['backend'])
 (out/(name+'.yaml')).write_text(s)
copy('gateway',[out/'agentgateway-native.yaml',out/'praxis-native.yaml',root/'infra/setup-native.sh'])
r=ssh('gateway','sudo cp /tmp/agentgateway-native.yaml /tmp/praxis-native.yaml /tmp/setup-native.sh /opt/gateway-benchmark/ && sudo bash /opt/gateway-benchmark/setup-native.sh',timeout=180)
assert r.returncode==0,r.stderr
files=[root/'harness'/n for n in ['run-native.py','run-ai-native.py','qualify-ai-native.py','check-cancellation-native.py']]
copy('client',files)
r=ssh('client','sudo cp '+' '.join('/tmp/'+f.name for f in files)+' /opt/gateway-benchmark/')
assert r.returncode==0,r.stderr
print('Native profile installed; qualify before measurements')
