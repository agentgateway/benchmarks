#!/usr/bin/env python3
"""Execute the two requested repeats after explicit first-pass review."""
import json,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
for name in ['pass1-review.json','native-pass1-review.json','kubernetes-pass1-review.json']:
 v=json.loads((root/'evidence/qualification'/name).read_text());assert v['infrastructure_valid'] is True
 if name!='kubernetes-pass1-review.json':assert v['aiperf_random_seed']==42
for phase in ['pass2','pass3']:
 subprocess.run([sys.executable,'infra/run-cpu-pass.py',phase],cwd=root,check=True)
 print(phase,'CPU profiles completed; final validity review still required',flush=True)
subprocess.run([sys.executable,'infra/export-cpu.py','cpu-final'],cwd=root,check=True)
print('CPU campaign exported; no automatic scientific approval or publication',flush=True)
