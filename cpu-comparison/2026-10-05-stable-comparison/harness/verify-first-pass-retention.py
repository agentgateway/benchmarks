#!/usr/bin/env python3
"""Verify first-pass measurement bytes survived unchanged into final exports."""
import argparse,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('exports',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
def digest(f):
 h=hashlib.sha256()
 with f.open('rb') as stream:
  while data:=stream.read(1024*1024):h.update(data)
 return h.hexdigest()
rows=[];issues=[]
for suite,role,paths in [('cpu','client',['results/common/pass1','results/native/pass1']),('kubernetes','kclient',['results/kubernetes/pass1','results/static-address/pass1'])]:
 first=a.exports/(suite+'-pass1')/role;final=a.exports/(suite+'-final')/role
 assert first.is_dir() and final.is_dir()
 for relative in paths:
  start=first/relative;end=final/relative;assert start.is_dir() and end.is_dir()
  first_files={str(f.relative_to(first)) for f in start.rglob('*') if f.is_file()};final_files={str(f.relative_to(final)) for f in end.rglob('*') if f.is_file()}
  if first_files!=final_files:issues.append({'scope':relative,'missing':sorted(first_files-final_files),'added':sorted(final_files-first_files)})
  for name in sorted(first_files&final_files):
   before=digest(first/name);after=digest(final/name);rows.append({'role':role,'artifact':name,'sha256':before,'unchanged':before==after})
   if before!=after:issues.append({'role':role,'artifact':name,'first_sha256':before,'final_sha256':after})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps({'verified_files':len(rows),'issues':issues,'files':rows,'scope':'Accepted first-pass measurement files only; original bytes before publication redaction. Config/root snapshots and continuing telemetry are separately retained.'},indent=2)+'\n')
print(json.dumps({'verified_files':len(rows),'issues':len(issues)}));raise SystemExit(bool(issues))
