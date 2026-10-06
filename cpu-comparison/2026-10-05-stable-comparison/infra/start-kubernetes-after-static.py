#!/usr/bin/env python3
"""Start the reviewed first Kubernetes pass after focused-test cleanup."""
import datetime,json,time
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
assert json.loads((root/'evidence/qualification/kubernetes-qualification-review.json').read_text())['infrastructure_valid']
for _ in range(180):
 r=ssh('kclient','test -f /opt/gateway-benchmark/results/static-address/pass1/COMPLETE')
 if r.returncode==0:break
 state=ssh('kclient','systemctl show static-address-pass1 -p ActiveState -p Result')
 assert state.returncode==0 and 'ActiveState=active' in state.stdout,state.stdout+state.stderr
 time.sleep(15)
else:raise SystemExit('Focused test cleanup incomplete')
cmd='sudo systemd-run --unit=kubernetes-tcp-pass1 --property=LimitNOFILE=65536 --property=RuntimeMaxSec=7200 /opt/gateway-benchmark/venv/bin/python /opt/gateway-benchmark/run-kubernetes.py pass1'
r=ssh('kclient',cmd);out=root/'evidence/dispatch-kubernetes';out.mkdir(exist_ok=True);(out/'pass1.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n');assert r.returncode==0,r.stderr
print('Corrected Kubernetes pass1 dispatched; repeats remain gated',flush=True)
