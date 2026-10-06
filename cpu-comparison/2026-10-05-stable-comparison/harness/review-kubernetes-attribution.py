#!/usr/bin/env python3
"""Inspect retained outcomes; this audit neither runs workloads nor approves results."""
import argparse,datetime,json,re
from pathlib import Path
parser=argparse.ArgumentParser(description='Verify the retained Kubernetes failure attribution; changed outcomes require a new manual review.')
parser.add_argument('root',type=Path,help='Five-role final export or eight-role analysis root')
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();source=a.root;client=source/'kclient'
def epoch(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
samples=[json.loads(x) for x in (source/'kcontroller/host-samples.jsonl').read_text().splitlines()]
records={'controller_startups':[],'scale_diagnostics':[],'telemetry_gaps':[],'static_signatures':[]}
for phase in ['pass1','pass2','pass3']:
 d=client/'results/kubernetes'/phase/'praxis-release';e=json.loads((d/'http-execution.json').read_text())
 chosen=[s for s in samples if epoch(e['started'])<=epoch(s['utc'])<=epoch(e['finished'])]
 states={}
 for s in chosen:
  for c in s.get('containers',[]):
   if c['name'].startswith('praxis-system/'):
    states.setdefault(str(c['pid']),set()).add(c['restart_count'])
 objects=json.loads((d/'placement.log').read_text())['items'];before=[]
 for pod in objects:
  if pod.get('kind')=='Pod' and pod['metadata'].get('namespace')=='praxis-system':
   for c in pod['status'].get('containerStatuses',[]):
    previous=c.get('lastState',{}).get('terminated')
    if previous:
     before.append({'pod':pod['metadata']['name'],'previous_exit':previous['exitCode'],'previous_finished':previous['finishedAt'],'before_http':epoch(previous['finishedAt'])<epoch(e['started'])})
 assert len(states)==2 and all(len(x)==1 for x in states.values()) and all(x['before_http'] for x in before)
 records['controller_startups'].append({'pass':phase,'http_start':e['started'],'http_end':e['finished'],'samples':len(chosen),'pid_restart_counts':{k:sorted(v) for k,v in states.items()},'previous_terminations':before})
 for count in [1000,5000]:
  folder=client/'diagnostics'/f'{phase}-praxis-release-{count}'
  phase_execution=json.loads((d/f'scale-{count}-execution.json').read_text())
  pods=[x for x in json.loads((folder/'resources.json').read_text())['items'] if x['kind']=='Pod']
  replacements=[x for x in pods if epoch(phase_execution['started'])<=epoch(x['metadata']['creationTimestamp'])<=epoch(phase_execution['finished'])]
  guard_records=[]
  for pod in replacements:
   for f in folder.glob(pod['metadata']['name']+'*.log'):
    messages=sorted(set(re.findall(r"too many filters \(\d+, max 100\)",f.read_text(errors='replace'))))
    if messages:guard_records.append({'artifact':str(f.relative_to(client)),'messages':messages,'pod_created':pod['metadata']['creationTimestamp'],'container_status':[{k:c.get(k) for k in ['name','restartCount','state','lastState']} for c in pod['status'].get('containerStatuses',[])]})
  api_errors=[]
  for line in (folder/'controller.log').read_text(errors='replace').splitlines():
   timestamp=re.search(r'"timestamp":"([^"]+)"',line)
   if timestamp and 'Too long: may not be more than 1048576 bytes' in line and re.search(r'code:\s*422',line):
    if epoch(phase_execution['started'])<=epoch(timestamp.group(1))<=epoch(phase_execution['finished']):api_errors.append(timestamp.group(1))
  guards=sorted({m for x in guard_records for m in x['messages']})
  assert guards and (count!=5000 or api_errors)
  record={'pass':phase,'routes':count,'artifact':str(folder.relative_to(client)),'phase_start':phase_execution['started'],'phase_end':phase_execution['finished'],'filter_guard_messages_from_replacement_pods':guards,'replacement_pod_evidence':guard_records,'configmap_1048576_byte_api422_timestamps_within_phase':sorted(set(api_errors)),'scale_runner_exit':phase_execution['exit']}
  assert record['scale_runner_exit']==0
  records['scale_diagnostics'].append(record)
 for treatment in ['agentgateway','praxis']:
  folder=client/'results/static-address'/phase/treatment
  log=(folder/'full.log').read_text()
  record={'pass':phase,'treatment':treatment,'artifact':str(folder.relative_to(client)),'unsupported_address':'UnsupportedAddress' in log,'explicit_unsupported_spec':'spec.addresses is not supported' in log,'cleanup_complete':(folder/'CLEANUP-COMPLETE').exists()}
  assert record['cleanup_complete']
  if treatment=='praxis':assert record['unsupported_address'] and record['explicit_unsupported_spec']
  records['static_signatures'].append(record)
for line in (source/'kgateway/host-samples.jsonl').open():
 s=json.loads(line)
 if not s.get('collector_error'):continue
 matching=[]
 for phase in ['pass1','pass2','pass3']:
  for f in (client/'results/kubernetes'/phase).glob('*/scale-*-execution.json'):
   e=json.loads(f.read_text())
   if epoch(e['started'])<=epoch(s['utc'])<=epoch(e['finished']):matching.append(str(f.relative_to(client)))
 if matching:records['telemetry_gaps'].append({'utc':s['utc'],'error':s['collector_error'],'within_scale_phases':matching})
a.output.parent.mkdir(parents=True,exist_ok=True)
a.output.write_text(json.dumps(records,indent=2)+'\n')
print(json.dumps({k:len(v) for k,v in records.items()}))
