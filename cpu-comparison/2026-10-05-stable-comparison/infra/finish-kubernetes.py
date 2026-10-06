#!/usr/bin/env python3
"""Resume after client tools are ready, without recreating any nodes."""
import json,time
from pathlib import Path
from transport import ssh,copy
root=Path(__file__).resolve().parents[1]
assert ssh('kclient','test -f /opt/gateway-benchmark/http-client-ready').returncode==0
for attempt in range(180):
 r=ssh('kcontrol','test -f /opt/gateway-benchmark/praxis-operator-build-complete')
 if r.returncode==0:break
 state=ssh('kcontrol','systemctl show operator-build -p ActiveState -p Result').stdout
 assert 'ActiveState=active' in state,state
 time.sleep(10)
else:raise SystemExit('Operator build timed out')
r=ssh('kcontrol','sudo cp /opt/gateway-benchmark/praxis-operator-image.tar /opt/gateway-benchmark/public-tools/');assert r.returncode==0,r.stderr
rendered=root/'.work/kubernetes-rendered/infra/import-praxis-operator.sh'
copy('kcontroller',[rendered if rendered.exists() else root/'infra/import-praxis-operator.sh'])
r=ssh('kcontroller','sudo bash /tmp/import-praxis-operator.sh',timeout=180);assert r.returncode==0,r.stderr
r=ssh('kcontrol','sudo systemd-run --unit=install-controllers --property=RuntimeMaxSec=900 bash /opt/gateway-benchmark/infra/install-kubernetes-controllers.sh');assert r.returncode==0,r.stderr
for attempt in range(100):
 time.sleep(10);r=ssh('kcontrol','systemctl show install-controllers -p ActiveState -p Result')
 if 'ActiveState=inactive' in r.stdout:
  assert 'Result=success' in r.stdout,r.stdout;break
 assert 'ActiveState=failed' not in r.stdout,r.stdout
else:raise SystemExit('Controller installation timed out')
r=ssh('kcontrol','sudo kubectl create namespace gateway-benchmark; sudo kubectl create namespace gateway-scale; sudo systemctl stop tool-transfer docker docker.socket');assert r.returncode==0,r.stderr
(root/'.work/KUBERNETES-READY').write_text('Bootstrap complete; qualification required\n');print('Kubernetes bootstrap complete',flush=True)
