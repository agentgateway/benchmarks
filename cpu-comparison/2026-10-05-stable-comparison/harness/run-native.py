#!/usr/bin/env python3
"""One native-AI treatment; correctness, cancellation and load."""
import argparse,subprocess,json,datetime,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--treatment',required=True);p.add_argument('--gateway',required=True);p.add_argument('--backend',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--qualification',action='store_true');a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
base=Path('/opt/gateway-benchmark');python=str(base/'venv/bin/python')
url=f'http://{a.backend}:8081' if a.treatment=='direct' else f'http://{a.gateway}:8080'
import httpx
for attempt in range(40):
 try:
  with httpx.Client(timeout=2) as c:
   for i in range(3):
    r=c.post(url+'/v1/chat/completions',json={'model':'bench-openai','messages':[{'role':'user','content':'ready'}],'max_tokens':1});assert r.status_code==200;time.sleep(.25)
  break
 except Exception:time.sleep(1)
else:raise SystemExit('Readiness barrier failed')
commands=[
 [python,str(base/'qualify-ai-native.py'),'--treatment',a.treatment,'--gateway',a.gateway,'--backend',a.backend,'--output',str(a.output/'protocol')],
 [python,str(base/'check-cancellation-native.py'),'--treatment',a.treatment,'--gateway',a.gateway,'--backend',a.backend,'--output',str(a.output/'cancellation.json')],
 [python,str(base/'run-ai-native.py'),'--treatment',a.treatment,'--gateway',a.gateway,'--backend',a.backend,'--output',str(a.output/'ai')]]
if a.qualification:
 commands[2].append('--qualification')
for i,cmd in enumerate(commands):
 with (a.output/f'stage-{i}.log').open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 (a.output/f'stage-{i}.json').write_text(json.dumps({'command':cmd,'exit':r.returncode,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
 if r.returncode:raise SystemExit(f'Stage {i} failed; retain output and classify before continuing')
(a.output/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
