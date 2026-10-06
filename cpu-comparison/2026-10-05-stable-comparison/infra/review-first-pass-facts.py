#!/usr/bin/env python3
"""Generate retained first-pass facts; this script never grants an approval."""
import argparse,shutil,subprocess,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('suite',choices=['cpu','kubernetes']);a=p.parse_args()
root=Path(__file__).resolve().parents[1];export=root/'.work/exports'/(a.suite+'-pass1');out=root/'evidence/qualification'
assert (export/'manifest.json').exists(),'Wait for complete immutable export'
def run(script,*args):subprocess.run([sys.executable,str(root/'harness'/script),*map(str,args)],check=True)
if a.suite=='cpu':
 for role in ['client','gateway','backend']:shutil.copy2(export/(role+'-host-samples.jsonl'),export/role/'host-samples.jsonl')
 run('audit-cpu-isolation.py',export,'--phase','pass1','--output',out/'cpu-pass1-isolation-review.json')
 run('summarize-hosts.py',export,'--output',out/'cpu-pass1-host-review.json')
 for profile in ['common','native']:
  run('audit-load.py',export/'client','--phase','pass1','--profile',profile,'--output',out/(profile+'-pass1-audit.json'))
  run('inspect-resource-gate.py',out/'cpu-pass1-host-review.json','--phase','pass1','--profile',profile,'--output',out/(profile+'-pass1-resource-gate.json'))
else:
 run('audit-kubernetes-startup.py',export/'kclient','--phase','pass1','--gateway-samples',export/'kgateway/host-samples.jsonl','--output',out/'kubernetes-pass1-startup-audit.json')
 run('audit-load.py',export/'kclient','--phase','pass1','--profile','kubernetes','--output',out/'kubernetes-pass1-audit.json')
 run('summarize-hosts.py',export,'--suite','gateway','--output',out/'kubernetes-pass1-host-review.json')
 run('inspect-resource-gate.py',out/'kubernetes-pass1-host-review.json','--phase','pass1','--output',out/'kubernetes-pass1-resource-gate.json')
 run('summarize-hosts.py',export,'--suite','gateway','--phases','--output',out/'kubernetes-pass1-phase-host-review.json')
 run('summarize-control.py',export/'kclient','--output',out/'kubernetes-pass1-control')
print('Facts ready. Attribute every issue and inspect resource/image/protocol evidence before writing review gates.')
