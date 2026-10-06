#!/usr/bin/env python3
"""Timestamped host and gateway-process evidence, independent of load clients."""
import argparse,datetime,json,pathlib,subprocess,time
p=argparse.ArgumentParser();p.add_argument("--runtime",choices=["docker","cri"],default="docker");args=p.parse_args()
out=pathlib.Path('/opt/gateway-benchmark/host-samples.jsonl')
network_profiles={}
with out.open('a',buffering=1) as stream:
 while True:
  row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  for name in ['stat','meminfo','net/dev','sys/fs/file-nr','net/sockstat']:
   try:row[name]=pathlib.Path('/proc',name).read_text()
   except OSError as e:row[name]={'error':str(e)}
  try:
   ins=[]
   if args.runtime=='docker':
    r=subprocess.run(['docker','ps','-q'],capture_output=True,text=True,timeout=3)
    ids=r.stdout.split()
    if ids:ins=json.loads(subprocess.check_output(['docker','inspect',*ids],text=True,timeout=3))
   else:
    cs=json.loads(subprocess.check_output(['k3s','crictl','ps','-o','json'],text=True,timeout=3))['containers']
    for c in cs:
     ns=c.get('labels',{}).get('io.kubernetes.pod.namespace','')
     if ns not in ['agentgateway-system','praxis-system','gateway-backend','gateway-benchmark']:continue
     v=json.loads(subprocess.check_output(['k3s','crictl','inspect',c['id']],text=True,timeout=3))
     ins.append({'Name':ns+'/'+c['metadata']['name'],'State':{'Pid':v['info']['pid'],'Status':v['status']['state']},'RestartCount':c['metadata'].get('attempt',0)})
   if ins:
    row['containers']=[]
    for x in ins:
     pid=x['State']['Pid'];p=pathlib.Path('/proc',str(pid));c={'name':x['Name'],'pid':pid,'state':x['State'],'restart_count':x['RestartCount']}
     try:
      if args.runtime=='cri':
       if pid not in network_profiles:
        network_profiles[pid]=subprocess.check_output(['nsenter','-t',str(pid),'-n','sysctl','net.ipv4.ip_local_port_range','net.ipv4.tcp_tw_reuse','net.ipv4.tcp_tw_reuse_delay','net.ipv4.tcp_timestamps'],text=True,timeout=2)
       c['network_profile']=network_profiles[pid]
       c['net_sockstat']=(p/'net/sockstat').read_text()
      c['fd_count']=len(list((p/'fd').iterdir()));c['limits']=(p/'limits').read_text();c['status']=(p/'status').read_text();c['stat']=(p/'stat').read_text()
     except OSError as e:c['error']=str(e)
     try:
      cg=(p/'cgroup').read_text().strip().split(':',2)[2]
      for key in ['cpu.stat','cpu.max','memory.current','memory.events','memory.peak','pids.current']:
       f=pathlib.Path('/sys/fs/cgroup'+cg,key)
       if f.exists():c[key]=f.read_text()
     except OSError as e:c['cgroup_error']=str(e)
     row['containers'].append(c)
  except Exception as e:row['collector_error']=str(e)
  row['clients']=[]
  for proc in pathlib.Path('/proc').iterdir():
   if not proc.name.isdigit():continue
   try:
    cmd=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode(errors='replace')
    if 'fortio load' in cmd or '/aiperf ' in cmd or 'nighthawk_client' in cmd:
     row['clients'].append({'pid':int(proc.name),'command':cmd,'fd_count':len(list((proc/'fd').iterdir())),'limits':(proc/'limits').read_text(),'stat':(proc/'stat').read_text()})
   except (OSError,ProcessLookupError):pass
  stream.write(json.dumps(row,separators=(',',':'))+'\n')
  time.sleep(5)
