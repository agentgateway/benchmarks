#!/usr/bin/env python3
"""Wait for the active qualification and retain a snapshot, without approving it."""
import subprocess,sys,time
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
for _ in range(180):
 r=ssh('kclient','test -f /opt/gateway-benchmark/results/kubernetes/qualification-tcp/COMPLETE')
 if r.returncode==0:break
 state=ssh('kclient','systemctl show kubernetes-qualification-tcp-retry -p ActiveState -p Result')
 assert state.returncode==0 and 'ActiveState=active' in state.stdout,state.stdout+state.stderr
 time.sleep(15)
else:raise SystemExit('Qualification did not finish; inspect remote evidence')
subprocess.run([sys.executable,'infra/export-kubernetes.py','kubernetes-tcp-qualification'],cwd=root,check=True)
print('Kubernetes qualification exported for manual review',flush=True)
