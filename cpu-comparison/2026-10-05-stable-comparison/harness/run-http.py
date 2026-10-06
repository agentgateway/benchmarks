#!/usr/bin/env python3
"""One treatment's direct-NodePort HTTP benchmark matrix."""
import argparse,datetime,json,os,resource,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--treatment',choices=['direct','agentgateway','praxis-release','praxis-nightly'],required=True);p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--qualification',action='store_true');p.add_argument('--socket-qualification',action='store_true');a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False);resource.setrlimit(resource.RLIMIT_NOFILE,(65536,65536))
plan=[dict(tool='fortio',size=s,concurrency=c,rate=q) for s in [0,16384] for c in [1,16,512] for q in [1000,0]]
plan += [dict(tool='nighthawk',size=s,concurrency=1,connections=16,rate=1000) for s in [0,16384]]
if a.qualification:plan=[dict(tool='fortio',size=16384,concurrency=512,rate=1000),dict(tool='nighthawk',size=16384,concurrency=1,connections=16,rate=1000)]
if a.socket_qualification:plan=[dict(tool='fortio',size=s,concurrency=512,rate=0) for s in [0,16384]]+[dict(tool='nighthawk',size=16384,concurrency=1,connections=16,rate=1000)]
(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
nh='envoyproxy/nighthawk-dev@sha256:eb19429cce1486360bab7af3b6edff87a0553b5daf17d861c0326cb07d6e6198'
for i,case in enumerate(plan):
 d=a.output/f'{i:02d}-{case["tool"]}';d.mkdir();url=a.url.rstrip('/')+f'/plain?bytes={case["size"]}'
 duration=10 if a.qualification else 30
 if case['tool']=='fortio':
  common=['fortio','load','-stdclient','-qps',str(case['rate']),'-c',str(case['concurrency']),'-uniform','-nocatchup','-timeout','10s','-r','0.000001']
  commands=[common+['-t','5s','-json',str(d/'warmup.json'),url],common+['-t',f'{duration}s','-json',str(d/'result.json'),url]]
 else:
  common=['docker','run','--rm','--network=host','--ulimit','nofile=65536:65536','--entrypoint','/usr/local/bin/nighthawk_client',nh,'--rps',str(case['rate']),'--connections','16','--concurrency','1','--output-format','json','--open-loop','--no-default-failure-predicates']
  commands=[common+['--duration','5',url],common+['--duration',str(duration),url]]
 e={'treatment':a.treatment,'case':case,'url':url,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commands':commands,'processes':[]}
 for j,cmd in enumerate(commands):
  with (d/('warmup.json' if j==0 else 'result.json') if case['tool']=='nighthawk' else d/f'command-{j}.log').open('w') as log, (d/f'stderr-{j}.log').open('w') as err:
   proc=subprocess.Popen(cmd,stdout=log,stderr=err)
   row={'pid':proc.pid}
   try:row['limits']=Path(f'/proc/{proc.pid}/limits').read_text()
   except OSError:pass
   try:row['exit']=proc.wait(timeout=100)
   except subprocess.TimeoutExpired:proc.kill();proc.wait();row['exit']='timeout'
   e['processes'].append(row)
 e['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat();(d/'execution.json').write_text(json.dumps(e,indent=2)+'\n')
 print(json.dumps({'case':case,'exits':[x['exit'] for x in e['processes']]}),flush=True)
 if any(x['exit']=='timeout' for x in e['processes']):raise SystemExit('Tool timeout; diagnose before continuing')
 time.sleep(2)
(a.output/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
