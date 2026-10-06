#!/usr/bin/env python3
"""Summarize sampled host evidence over each completed measured workload."""
import argparse,datetime,json,re,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--suite',choices=['ai','gateway'],default='ai');p.add_argument('--phases',action='store_true',help='Summarize Gateway conformance, scale, recovery and complete HTTP phase intervals');p.add_argument('--qualification',action='store_true');p.add_argument('--socket-qualification',action='store_true');p.add_argument('--native-qualification',action='store_true');p.add_argument('--qualification-label',help='Override qualification directory without changing retained earlier reviews');a=p.parse_args()
def epoch(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def parsecpu(s):return {l.split()[0]:list(map(int,l.split()[1:9])) for l in s.splitlines() if l.startswith('cpu')}
def statdict(s):
 return {l.split()[0]:int(l.split()[1]) for l in s.splitlines() if len(l.split())==2}
def netdev(s):
 result={}
 for line in s.splitlines():
  if ':' in line:
   name,values=line.split(':',1);v=list(map(int,values.split()));result[name.strip()]={'rx_bytes':v[0],'tx_bytes':v[8],'rx_errors':v[2],'rx_drops':v[3],'tx_errors':v[10],'tx_drops':v[11]}
 return result
rows=[]
client_role='client' if a.suite=='ai' else 'kclient'
roles=['client','gateway','backend'] if a.suite=='ai' else ['kclient','kgateway','kbackend','kcontroller','kcontrol']
pattern='results/*/pass[123]/*/*/*/execution.json' if a.suite=='ai' else ('results/kubernetes/pass[123]/*/*-execution.json' if a.phases else 'results/kubernetes/pass[123]/*/http/*/execution.json')
if a.qualification:pattern='results/common/qualification-v3/*/*/*/execution.json' if a.suite=='ai' else 'results/kubernetes/qualification/*/http/*/execution.json'
if a.native_qualification:pattern='results/native/qualification/*/*/*/execution.json'
if a.qualification_label:
 assert a.qualification or a.native_qualification
 pattern=pattern.replace('qualification-v3',a.qualification_label) if 'qualification-v3' in pattern else pattern.replace('/qualification/','/'+a.qualification_label+'/')
if a.socket_qualification:pattern='qualification/socket-*/*/execution.json'
for role in roles:
 f=a.root/role/'host-samples.jsonl'
 if not f.exists():continue
 samples=[]
 for line in f.read_text().splitlines():
  try:samples.append(json.loads(line))
  except json.JSONDecodeError:raise SystemExit(f'Truncated/corrupt collector row in {f}')
 for execution in sorted((a.root/client_role).glob(pattern)):
  e=json.loads(execution.read_text());start=epoch(e.get('start',e.get('started')));end=epoch(e.get('end',e.get('finished')))
  selected=[x for x in samples if start<=epoch(x['utc'])<=end]
  busy=[];steal=[];iowait=[];percpu=[];fds=[];limits=[];memory=[];restarts=[];oom=[];containercpu=[];throttled=[];collectorerrors=[];transienterrors=[]
  for before,after in zip(selected,selected[1:]):
   dt=epoch(after['utc'])-epoch(before['utc']);old=parsecpu(before['stat']);new=parsecpu(after['stat'])
   for name,vals in new.items():
    if name not in old:continue
    diff=[x-y for x,y in zip(vals,old[name])];total=sum(diff)
    if total<=0:continue
    usage=100*(total-diff[3]-diff[4])/total
    if name=='cpu':busy.append(usage);steal.append(100*diff[7]/total);iowait.append(100*diff[4]/total)
    else:percpu.append(usage)
   oldc={c['pid']:c for c in before.get('containers',[])}
   for c in after.get('containers',[]):
    if dt>0 and c['pid'] in oldc and 'cpu.stat' in c and 'cpu.max' in c and 'cpu.stat' in oldc[c['pid']]:
     delta=statdict(c['cpu.stat'])['usage_usec']-statdict(oldc[c['pid']]['cpu.stat'])['usage_usec']
     quota,period=c['cpu.max'].split();cpus=float(quota)/float(period) if quota!='max' else len(new)-1
     containercpu.append(100*delta/1e6/dt/cpus)
     previous=statdict(oldc[c['pid']]['cpu.stat']);current=statdict(c['cpu.stat']);periods=current.get('nr_periods',0)-previous.get('nr_periods',0)
     if periods>0:throttled.append(100*(current.get('nr_throttled',0)-previous.get('nr_throttled',0))/periods)
  for sample in selected:
   if sample.get('collector_error'):collectorerrors.append(sample['collector_error'])
   for c in sample.get('containers',[])+sample.get('clients',[]):
    if c.get('error') or c.get('cgroup_error'):transienterrors.append({'name':c.get('name'),'pid':c.get('pid'),'error':c.get('error'),'cgroup_error':c.get('cgroup_error')})
    if 'fd_count' in c:fds.append(c['fd_count'])
    match=re.search(r'Max open files\s+(\d+)\s+(\d+)',c.get('limits',''))
    if match:limits.append([int(match[1]),int(match[2])])
    if 'memory.current' in c:memory.append(int(c['memory.current']))
    if 'restart_count' in c:restarts.append(c['restart_count'])
    if 'memory.events' in c:oom.append(statdict(c['memory.events']).get('oom_kill',0))
  network_delta={};network_rates={}
  if len(selected)>1:
   first=netdev(selected[0]['net/dev']);last=netdev(selected[-1]['net/dev'])
   for interface in first.keys() & last.keys():
    delta={key:last[interface][key]-first[interface][key] for key in first[interface] if key not in ['rx_bytes','tx_bytes']}
    if any(delta.values()):network_delta[interface]=delta
   for before,after in zip(selected,selected[1:]):
    dt=epoch(after['utc'])-epoch(before['utc']);n0=netdev(before['net/dev']);n1=netdev(after['net/dev'])
    if dt<=0:continue
    for interface in n0.keys() & n1.keys():
     rates=network_rates.setdefault(interface,{'rx_mbps':[],'tx_mbps':[]})
     for direction in ['rx','tx']:rates[direction+'_mbps'].append(8*(n1[interface][direction+'_bytes']-n0[interface][direction+'_bytes'])/dt/1e6)
  def stats(v):return {'mean':statistics.mean(v),'max':max(v)} if v else None
  rows.append({'role':role,'workload':str(execution.relative_to(a.root/client_role)),'samples':len(selected),'host_busy_percent':stats(busy),'host_steal_percent':stats(steal),'host_iowait_percent':stats(iowait),'busiest_sampled_vcpu_percent':max(percpu) if percpu else None,'container_quota_busy_percent':stats(containercpu),'container_throttled_period_percent':stats(throttled),'max_fd':max(fds) if fds else None,'minimum_soft_nofile':min(x[0] for x in limits) if limits else None,'minimum_hard_nofile':min(x[1] for x in limits) if limits else None,'max_container_memory_bytes':max(memory) if memory else None,'max_restart_count':max(restarts) if restarts else 0,'max_oom_kill_counter':max(oom) if oom else 0,'collector_errors':collectorerrors,'transient_container_read_errors':transienterrors,'network_error_drop_deltas':network_delta,'interface_mbps':{name:{direction:stats(values) for direction,values in rates.items()} for name,rates in network_rates.items()}})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps({'host_workload_rows':len(rows)}))
