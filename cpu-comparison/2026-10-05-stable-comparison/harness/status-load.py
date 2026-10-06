#!/usr/bin/env python3
"""Compact read-only progress; final validity requires the archived full audit."""
import json
from pathlib import Path
base=Path('/opt/gateway-benchmark/results');rows=[]
for profile in ['common','native','kubernetes']:
 for d in sorted((base/profile).glob('pass[123]/*')):
  if not d.is_dir():continue
  row={'profile':profile,'pass':d.parent.name,'treatment':d.name,'completed_load_cases':0,'complete':(d/'COMPLETE').exists(),'nonzero_tool_exits':[],'fortio_errors':[],'nighthawk_issues':[],'aiperf_issues':[],'setup_blocked':(d/'setup-block/blocked.json').exists()}
  for f in d.rglob('execution.json'):
   try:
    e=json.loads(f.read_text());row['completed_load_cases']+=1
    for x in e['processes']:
     if x['exit']!=0:row['nonzero_tool_exits'].append({'case':e['case'],'exit':x['exit']})
    if e['case']['tool']=='fortio':
     v=json.loads((f.parent/'result.json').read_text());errors={k:n for k,n in v['RetCodes'].items() if k!='200' and n}
     if errors:row['fortio_errors'].append({'case':e['case'],'status_counts':errors})
    if e['case']['tool']=='nighthawk':
     v=json.loads((f.parent/'result.json').read_text());g=next(x for x in v['results'] if x['name']=='global');c={x['name']:int(x['value']) for x in g['counters']}
     errors=sum(n for k,n in c.items() if k.startswith('benchmark.http_'))-c.get('benchmark.http_2xx',0);resets=c.get('benchmark.stream_resets',0)
     if errors or resets:row['nighthawk_issues'].append({'case':e['case'],'non_2xx':errors,'resets':resets})
    if e['case']['tool']=='aiperf':
     v=json.loads((f.parent/'result/profile_export_aiperf.json').read_text());errors=v.get('error_request_count',{}).get('avg',0)
     if errors or not v.get('is_complete') or v['run_info']['random_seed']!=42:row['aiperf_issues'].append({'case':e['case'],'errors':errors,'complete':v.get('is_complete'),'seed':v['run_info']['random_seed']})
   except (ValueError,KeyError,FileNotFoundError) as ex:row.setdefault('artifact_issues',[]).append({'path':str(f),'error':repr(ex)})
  rows.append(row)
print(json.dumps(rows,indent=2))
