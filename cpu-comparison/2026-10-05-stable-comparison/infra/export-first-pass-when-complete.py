#!/usr/bin/env python3
"""Retain completed first passes for review; never authorize repetitions."""
import concurrent.futures,subprocess,sys,time
from pathlib import Path
from transport import ssh
root=Path(__file__).resolve().parents[1]
def capture(kind):
 role='client' if kind=='cpu' else 'kclient'
 target=('/opt/gateway-benchmark/results/native/pass1/praxis-ai-nightly/COMPLETE' if kind=='cpu' else '/opt/gateway-benchmark/results/kubernetes/pass1/COMPLETE')
 for _ in range(800):
  r=ssh(role,'test -f '+target)
  if r.returncode==0:break
  assert r.returncode==1,'Administration failed; inspect remote jobs'
  time.sleep(15)
 else:raise RuntimeError('First pass did not complete within bounded wait')
 subprocess.run([sys.executable,'infra/export-'+('cpu' if kind=='cpu' else 'kubernetes')+'.py',kind+'-pass1'],cwd=root,check=True)
 print(kind,'first pass exported; manual scientific review required',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(capture,['cpu','kubernetes']))
