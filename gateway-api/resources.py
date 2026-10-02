#!/usr/bin/env python3
"""Summarize sampled pod working set/CPU for each complete lifecycle interval."""
import argparse,datetime,json
from pathlib import Path

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--root',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
a=p.parse_args()
results=json.loads((a.root/'gateway-lifecycle/results.json').read_text())
windows=[]
for r in results:
 start=datetime.datetime.fromisoformat(r['started_at']).timestamp()
 windows.append((start,start+r['elapsed_seconds'],r))
summary={}
collector_errors=0
with (a.root/'kubelet-samples.jsonl').open() as stream:
 for line in stream:
  row=json.loads(line)
  if row.get('exit_code')!=0 or 'stats' not in row:
   collector_errors+=1;continue
  at=datetime.datetime.fromisoformat(row['captured_utc']).timestamp()
  active=[r for start,end,r in windows if start<=at<=end]
  if not active:continue
  totals={}
  for pod in row['stats'].get('pods',[]):
   ns=pod.get('podRef',{}).get('namespace')
   if ns not in ('agentgateway','praxis','agentgateway-system','praxis-system'):continue
   total=totals.setdefault(ns,{'containers':0,'working_set_bytes':0,'cpu_cores':0.0})
   for c in pod.get('containers',[]):
    total['containers']+=1
    total['working_set_bytes']+=c.get('memory',{}).get('workingSetBytes',0)
    total['cpu_cores']+=c.get('cpu',{}).get('usageNanoCores',0)/1e9
  for r in active:
   key=f"{r['gateway']}:{r['case']}"
   group=summary.setdefault(key,{'outcome':r['outcome'],'namespaces':{}})
   for ns,v in totals.items():
    metric=group['namespaces'].setdefault(ns,{'samples':0,'max_containers':0,'max_working_set_mib':0.0,'max_cpu_cores':0.0})
    metric['samples']+=1
    metric['max_containers']=max(metric['max_containers'],v['containers'])
    metric['max_working_set_mib']=max(metric['max_working_set_mib'],v['working_set_bytes']/2**20)
    metric['max_cpu_cores']=max(metric['max_cpu_cores'],v['cpu_cores'])
a.output.write_text(json.dumps({'collector_error_rows':collector_errors,'intervals':summary,'interpretation':'Five-second samples; maxima are sampled namespace aggregates, not true peaks or per-process RSS. Windows include command setup/cleanup. CPU from kubelet usageNanoCores. Container records can include rollout overlap or recently terminated containers retained by the collector; they are not a verified live-pod count. No efficiency winner is established.'},indent=2)+'\n')
