#!/usr/bin/env python3
"""Finish unchanged active treatment, then qualify corrected inactive containers."""
import subprocess,sys,time
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
for _ in range(180):
 r=ssh('client','test -f /opt/gateway-benchmark/results/common/pass1/agentgateway/COMPLETE')
 if r.returncode==0:break
 state=ssh('client','systemctl show common-seeded-pass1-agentgateway -p ActiveState -p Result')
 assert state.returncode==0 and 'ActiveState=active' in state.stdout,state.stdout+state.stderr
 time.sleep(15)
else:raise SystemExit('Unchanged agentgateway run did not finish; inspect before modifying containers')
for cmd in [[sys.executable,'infra/disable-standalone-healthchecks.py'],[sys.executable,'infra/run-common-pass.py','qualification-nohealth'],[sys.executable,'infra/run-native-pass.py','qualification-nohealth'],[sys.executable,'infra/export-cpu.py','final-qualification']]:
 subprocess.run(cmd,cwd=root,check=True)
print('Healthcheck correction qualified and exported; manual review required before resuming measured dispatcher',flush=True)
