#!/usr/bin/env python3
"""Summarize observed nightly setup failure; a human decides validity separately."""
import argparse
import datetime
import json
import re
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('case',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
rows=[json.loads(s) for s in (a.case/'runtime.jsonl').read_text().splitlines()]
start=datetime.datetime.fromisoformat((a.case/'start.txt').read_text().strip().replace('Z','+00:00'))
end=datetime.datetime.fromisoformat((a.case/'end.txt').read_text().strip().replace('Z','+00:00'))
crashes={};images=set()
for row in rows:
    for d in row.get('crash_diagnostics',[]):
        if "'routes' is empty" in d.get('log',''):
            crashes[d['pod']]={'container':d['container'],'error':"router: 'routes' is empty; every request would fail with 404"}
    for pod in row.get('pods',{}).get('items',[]):
        if pod['metadata']['namespace'].startswith('gateway-conformance-'):
            images.update(c['image'] for c in pod['spec']['containers'] if c['name']=='praxis')
# Inspect a late pre-timeout snapshot, before cleanup can terminate fixtures.
candidates=[r for r in rows if 180 <= (datetime.datetime.fromisoformat(r['utc'])-start).total_seconds() <= 285]
assert candidates,'No late setup snapshot'
snapshot=candidates[-1];fixtures=[];gateways=[]
for pod in snapshot['pods']['items']:
    meta=pod['metadata']
    if not meta['namespace'].startswith('gateway-conformance-'):
        continue
    item={'namespace':meta['namespace'],'pod':meta['name'],'phase':pod.get('status',{}).get('phase'),
          'ready':any(c['type']=='Ready' and c['status']=='True' for c in pod.get('status',{}).get('conditions',[]))}
    (gateways if any(c['name']=='praxis' for c in pod['spec']['containers']) else fixtures).append(item)
config=json.loads((a.case/'nightly-config.json').read_text())
routers={i['metadata']['name']:bool(re.search(r'\broutes:\s*\[\]',i.get('data',{}).get('config.yaml','')))
         for i in config['items'] if i['kind']=='ConfigMap'}
result={'case':str(a.case),'duration_seconds':(end-start).total_seconds(),'fatal_empty_router_pods':crashes,
        'desired_core_images':sorted(images),'empty_routes_in_generated_configs':routers,
        'late_setup_snapshot':snapshot['utc'],'fixture_pods':fixtures,'praxis_data_plane_pods':gateways,
        'all_observed_fixture_pods_ready':bool(fixtures) and all(f['ready'] for f in fixtures),
        'all_four_base_gateways_failed_to_start':len(crashes)==4 and len(gateways)==4 and not any(g['ready'] for g in gateways),
        'individual_test_status':'not evaluated only if full.log contains no selected top-level outcomes; check summarized results',
        'cleanup_complete':(a.case/'CLEANUP-COMPLETE').exists(),'job_finished':(a.case/'JOB-FINISHED').exists()}
a.output.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['fixture_pods','praxis_data_plane_pods']},indent=2))
