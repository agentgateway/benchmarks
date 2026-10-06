#!/usr/bin/env python3
"""Summarize conformance, route convergence and restart evidence without hiding failures."""
import argparse, json, statistics
from pathlib import Path
import re
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
conformance=[];scale=[];recovery=[];blocks=[]
for directory in sorted((a.root/'results/kubernetes').glob('pass[123]/*')):
 if directory.name not in ['agentgateway','praxis-release','praxis-nightly']:continue
 identity={'pass':int(directory.parent.name[-1]),'treatment':directory.name}
 if (directory/'setup-block/blocked.json').exists():blocks.append({**identity,**json.loads((directory/'setup-block/blocked.json').read_text())})
 for f in sorted(directory.glob('scale-*/observations/*-result.json')):
  v=json.loads(f.read_text());last=v['observations'][-1]
  scale.append({**identity,**{k:v[k] for k in ['count','marker','complete','post_submission_observer_started_seconds','status_convergence_seconds','sample_traffic_convergence_seconds','all_route_traffic_verified_seconds']},'last_observed_seconds':last['seconds_from_mutation_start'],'final_current_status_count':last['current_generation_accepted_and_resolved'],'final_sample_passed':sum(x['passed'] for x in last['sample_probes']),'final_sample_count':len(last['sample_probes']),'final_full_probe_passed':last['full_probe_passed'],'final_full_probe_attempted':last['objects']==v['count'] and last['current_generation_accepted_and_resolved']==v['count']})
 for f in sorted(directory.glob('recovery/*/summary.json')):
  d=f.parent;v=json.loads(f.read_text());probes=[json.loads(s) for s in (d/'probes.jsonl').read_text().splitlines()];events=json.loads((d/'events.json').read_text());mutation=next(e['seconds'] for e in events if e['event']=='mutation-start');fail=[r for r in probes if not r['success']];post=[r for r in probes if r['start_seconds']>=mutation]
  post_fail=[r for r in post if not r['success']]
  last_failure=max([r['start_seconds'] for r in post_fail],default=None)
  after_failure=[r for r in post if r['success'] and (last_failure is None or r['start_seconds']>last_failure)]
  # First observed successful response after the last failure; sampling is 100 ms.
  observed_recovery=after_failure[0]['start_seconds']-mutation if last_failure is not None and after_failure else None
  results=[r for e in events for r in e.get('results',[])]
  recovery.append({**identity,'kind':d.name,**v,'mutation_seconds':mutation,'first_failed_probe_seconds':min([r['start_seconds'] for r in fail],default=None),'last_failed_probe_seconds':max([r['start_seconds'] for r in fail],default=None),'first_post_mutation_failed_probe_seconds':min([r['start_seconds'] for r in post_fail],default=None),'last_post_mutation_failed_probe_seconds':last_failure,'observed_recovery_after_mutation_seconds':observed_recovery,'post_mutation_failed_requests':len(post_fail),'recovery_censored':bool(post_fail) and not after_failure,'command_exits':[r['exit'] for r in results],'pre_mutation_failures':sum(not r['success'] for r in probes if r['start_seconds']<mutation),'post_mutation_observation_seconds':probes[-1]['start_seconds']-mutation,'first_to_last_post_mutation_failed_probe_span_seconds':last_failure-min(r['start_seconds'] for r in post_fail) if post_fail else 0})
for d in sorted((a.root/'results/static-address').glob('pass[123]/*')):
 if not d.is_dir() or d.name not in ['agentgateway','praxis']:continue
 log=(d/'full.log').read_text();exit_code=int((d/'exit-code.txt').read_text())
 passed=bool(re.search(r'--- PASS: TestConformance/GatewayStaticAddresses(?: |\()',log))
 failed=bool(re.search(r'--- FAIL: TestConformance/GatewayStaticAddresses(?: |\()',log))
 conformance.append({'pass':int(d.parent.name[-1]),'treatment':d.name,'test':'GatewayStaticAddresses','suite':'conformance/v1.6.1','exit':exit_code,'passed':passed,'failed':failed,'cleanup_complete':(d/'CLEANUP-COMPLETE').exists(),'artifact':str(d.relative_to(a.root))})
a.output.mkdir(parents=True,exist_ok=True)
(a.output/'setup-blocks.json').write_text(json.dumps(blocks,indent=2)+'\n')
for name,rows in [('static-address',conformance),('scale',scale),('recovery',recovery)]:
 (a.output/f'{name}-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
for name, rows, keys, metrics in [
 ('scale', scale, ['treatment','count','marker'], ['post_submission_observer_started_seconds','status_convergence_seconds','all_route_traffic_verified_seconds']),
 ('recovery', recovery, ['treatment','kind'], ['requests','failed_requests','pre_mutation_failures','post_mutation_failed_requests','max_dispatch_delay_seconds','observed_recovery_after_mutation_seconds'])]:
 groups={}
 for row in rows:groups.setdefault(tuple(row[k] for k in keys),[]).append(row)
 summaries=[]
 for key, rs in groups.items():
  rs.sort(key=lambda r:r['pass']);entry=dict(zip(keys,key));entry['passes']=[r['pass'] for r in rs];entry['three_complete_passes']=entry['passes']==[1,2,3];entry['metrics']={}
  if name=='scale':entry['converged_passes']=sum(r['complete'] for r in rs)
  for metric in metrics:
   values=[r.get(metric) for r in rs]
   # Never average only the successful subset of a failed convergence scenario.
   if all(isinstance(v,(int,float)) for v in values):entry['metrics'][metric]={'per_pass':values,'arithmetic_mean':statistics.mean(values) if entry['three_complete_passes'] else None,'min':min(values),'max':max(values),'sample_stddev':statistics.stdev(values) if len(values)>1 else None}
  summaries.append(entry)
 (a.output/f'{name}-summary.json').write_text(json.dumps(summaries,indent=2)+'\n')
print(json.dumps({'conformance':len(conformance),'scale_phases':len(scale),'recovery_scenarios':len(recovery)}))
