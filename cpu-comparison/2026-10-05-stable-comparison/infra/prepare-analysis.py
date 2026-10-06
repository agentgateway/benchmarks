#!/usr/bin/env python3
"""Assemble exactly one completed snapshot per role for offline review."""
import os,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'.work/analysis-final';out.mkdir(exist_ok=False)
for role in ['client','gateway','backend','kclient','kgateway','kbackend','kcontroller','kcontrol']:
 cpu=role in ['client','gateway','backend']
 export=root/'.work/exports'/('cpu-final' if cpu else 'kubernetes-final')
 assert (export/'manifest.json').is_file()
 source=export/role
 shutil.copytree(source,out/role,copy_function=os.link)
 if cpu:shutil.copy2(export/(role+'-host-samples.jsonl'),out/role/'host-samples.jsonl')
 assert (out/role/'host-samples.jsonl').stat().st_size>0
for profile in ['common','native']:
 for phase in ['pass1','pass2','pass3']:
  ds=[d for d in (out/'client/results'/profile/phase).iterdir() if d.is_dir()]
  assert len(ds)==4 and all((d/'COMPLETE').exists() for d in ds)
for profile in ['kubernetes','static-address']:
 for phase in ['pass1','pass2','pass3']:
  assert (out/'kclient/results'/profile/phase/'COMPLETE').exists()
print('Complete role snapshots assembled; audit and manual review remain required')
