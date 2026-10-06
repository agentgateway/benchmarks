#!/usr/bin/env python3
"""Run approved repetitions and focused conformance checks sequentially."""
import datetime,json,subprocess,sys,time
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
for name in ['pass1-review.json','native-pass1-review.json','kubernetes-pass1-review.json']:
 review=json.loads((root/'evidence/qualification'/name).read_text())
 assert review['infrastructure_valid'] is True
out=root/'evidence/dispatch-kubernetes'
for phase in ['pass2','pass3']:
 for suite,runner,limit in [('kubernetes','/opt/gateway-benchmark/venv/bin/python /opt/gateway-benchmark/run-kubernetes.py',7200),('static-address','bash /opt/gateway-benchmark/run-static-pass.sh',1800)]:
  active=ssh('kclient',"systemctl list-units --state=running --no-legend 'kubernetes-*' 'static-address-*'")
  assert active.returncode==0 and not active.stdout.strip(),active.stdout
  unit=suite+'-tcp-'+phase
  cmd=f'sudo systemd-run --unit={unit} --property=LimitNOFILE=65536 --property=RuntimeMaxSec={limit} {runner} {phase}'
  result=ssh('kclient',cmd)
  record=out/(suite+'-'+phase+'.json');assert not record.exists()
  record.write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'exit':result.returncode,'stdout':result.stdout,'stderr':result.stderr},indent=2)+'\n')
  assert result.returncode==0,result.stderr
  while True:
   time.sleep(15)
   r=ssh('kclient',f'systemctl show {unit} -p ActiveState -p Result; test -f /opt/gateway-benchmark/results/{suite}/{phase}/COMPLETE && echo COMPLETE; true')
   assert r.returncode==0,'Inspect remote job before retrying administrative failure'
   if 'COMPLETE' in r.stdout:break
   assert 'ActiveState=failed' not in r.stdout and 'ActiveState=inactive' not in r.stdout,r.stdout
  print(suite,phase,'complete; final review remains required',flush=True)
subprocess.run([sys.executable,'infra/export-kubernetes.py','kubernetes-final'],cwd=root,check=True)
