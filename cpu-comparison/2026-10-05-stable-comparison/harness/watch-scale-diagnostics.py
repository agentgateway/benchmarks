#!/usr/bin/env python3
"""Capture read-only runtime evidence during sustained route nonconvergence."""
import json,subprocess,time
from pathlib import Path
base=Path('/opt/gateway-benchmark');deadline=time.monotonic()+30000
pending={(phase,count) for phase in ['pass1','pass2','pass3'] for count in [1000,5000]}
while pending and time.monotonic()<deadline:
 for phase,count in list(pending):
  d=base/f'results/kubernetes/{phase}/praxis-release/scale-{count}'
  result=d/'observations/created-result.json'
  dest=base/f'diagnostics/{phase}-praxis-release-{count}'
  if dest.exists():pending.remove((phase,count));continue
  if not result.exists():continue
  try:v=json.loads(result.read_text())
  except json.JSONDecodeError:continue # The active observer replaces this file.
  if v['complete']:
   # Successful cases already have their complete traffic and controller evidence.
   pending.remove((phase,count));continue
  if len(v['observations'])<6:continue
  if (d.parent/f'scale-{count}-execution.json').exists():
   raise SystemExit('Missed live diagnostic window: '+str(d))
  dest.parent.mkdir(exist_ok=True)
  p=subprocess.run(['bash',str(base/'capture-kubernetes-diagnostics.sh'),str(dest)],capture_output=True,text=True,timeout=100)
  (dest/'capture-execution.json').write_text(json.dumps({'exit':p.returncode,'scope':'Read-only snapshot during nonconvergence; not a final result or another repetition','stdout':p.stdout,'stderr':p.stderr},indent=2)+'\n')
  assert p.returncode==0,'Diagnostic capture failed'
  pending.remove((phase,count));print(phase,count,'diagnostic captured',flush=True)
 time.sleep(10)
assert not pending,'Diagnostic windows did not all occur before watcher deadline'
