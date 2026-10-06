#!/usr/bin/env python3
"""Check active gateway count, process stability and guest CPU affinity."""
import argparse,datetime,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path)
p.add_argument('--phase',required=True);p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
def epoch(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
samples=[json.loads(s) for s in (a.root/'gateway/host-samples.jsonl').read_text().splitlines()]
samples=[(epoch(s['utc']),s) for s in samples];rows=[];issues=[]
native={'agentgateway':'agentgateway-native','praxis':'praxis-ai','praxis-ai-nightly':'praxis-ai-nightly'}
for profile in ['common','native']:
 for f in sorted((a.root/'client/results'/profile/a.phase).rglob('execution.json')):
  e=json.loads(f.read_text());t=e['treatment']
  expected=None if t=='direct' else '/'+(native[t] if profile=='native' else t)
  start=epoch(e.get('start',e.get('started')));end=epoch(e.get('end',e.get('finished')))
  selected=[s for stamp,s in samples if start<=stamp<=end]
  names=[sorted(c['name'] for c in s.get('containers',[])) for s in selected]
  pids={c['pid'] for s in selected for c in s.get('containers',[])}
  valid=bool(selected) and all(n==([] if expected is None else [expected]) for n in names)
  valid=valid and (not pids if expected is None else len(pids)==1)
  affinities=set()
  quotas=set()
  for s in selected:
   for c in s.get('containers',[]):
    quotas.add(c.get('cpu.max','MISSING').strip())
    match=re.search(r'^Cpus_allowed_list:\s*(.+)$',c.get('status',''),re.M)
    affinities.add(match.group(1).strip() if match else 'MISSING')
  if expected is not None:valid=valid and affinities=={'2-3'} and quotas=={'200000 100000'}
  row={'artifact':str(f.relative_to(a.root/'client')),'expected_container':expected,'samples':len(selected),'pids':sorted(pids),'cpu_affinities':sorted(affinities),'cpu_quotas':sorted(quotas),'passed':valid}
  rows.append(row)
  if not valid:issues.append(row)
assert rows,'No workload windows found'
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps({'phase':a.phase,'windows':len(rows),'issues':issues,'checks':rows},indent=2)+'\n')
print(json.dumps({'windows':len(rows),'issues':len(issues)}))
