#!/usr/bin/env python3
"""Condense resource windows for attribution review; never auto-approve a pass."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('input',type=Path);p.add_argument('--phase',required=True);p.add_argument('--profile');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
rows=[r for r in json.loads(a.input.read_text()) if '/'+a.phase+'/' in r['workload'] and (not a.profile or '/'+a.profile+'/' in r['workload'])]
assert rows,'No matching resource windows'
result={'phase':a.phase,'profile':a.profile,'input':str(a.input),'windows':len(rows),'roles':{},'events_to_review':[], 'approved':False}
for role in sorted({r['role'] for r in rows}):
 rs=[r for r in rows if r['role']==role]
 def peak(metric, subset):return max((r[metric]['mean'] for r in subset if r.get(metric)),default=None)
 result['roles'][role]={'windows':len(rs),'minimum_samples':min(r['samples'] for r in rs),'maximum_fd_count':max((r['max_fd'] for r in rs if r['max_fd'] is not None),default=None),'minimum_soft_nofile':min((r['minimum_soft_nofile'] for r in rs if r['minimum_soft_nofile'] is not None),default=None),'peak_mean_host_busy_percent':peak('host_busy_percent',rs),'peak_mean_steal_percent':peak('host_steal_percent',rs),'peak_mean_iowait_percent':peak('host_iowait_percent',rs),'peak_mean_quota_busy_percent':peak('container_quota_busy_percent',rs),'through_gateways_peak_mean_host_busy_percent':peak('host_busy_percent',[r for r in rs if '/direct/' not in r['workload']]),'through_gateways_peak_mean_quota_busy_percent':peak('container_quota_busy_percent',[r for r in rs if '/direct/' not in r['workload']])}
 for r in rs:
  events={k:r[k] for k in ['collector_errors','transient_container_read_errors','network_error_drop_deltas','max_oom_kill_counter','max_restart_count'] if r.get(k)}
  if r['samples']<5:events['few_samples']=r['samples']
  if r['minimum_soft_nofile'] and r['max_fd'] is not None and r['max_fd']>=r['minimum_soft_nofile']*.8:events['near_descriptor_limit']=True
  if events:result['events_to_review'].append({'role':role,'workload':r['workload'],**events})
result['note']='Restart/OOM counters may predate a window. Attribute using raw timestamps/lifecycle evidence; intended product capacity/recovery constraints are not automatically infrastructure failures. Short qualification cases can contain few samples. This summary does not approve a pass.'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'windows':len(rows),'event_windows':len(result['events_to_review'])}))
