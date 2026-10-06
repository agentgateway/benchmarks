#!/usr/bin/env python3
"""One treatment's AI matrix. Run via a root systemd unit with LimitNOFILE=65536."""
import argparse, datetime, json, os, resource, subprocess, time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument('--treatment', choices=['direct','agentgateway','praxis','praxis-ai-nightly'],required=True)
p.add_argument('--gateway',default='10.128.0.63');p.add_argument('--backend',default='10.128.15.192')
p.add_argument('--output',type=Path,required=True)
p.add_argument('--qualification',action='store_true')
p.add_argument('--socket-qualification',action='store_true')
a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
resource.setrlimit(resource.RLIMIT_NOFILE,(65536,65536))
(a.output/'runner.json').write_text(json.dumps({'args':vars(a)|{'output':str(a.output)},'limits':resource.getrlimit(resource.RLIMIT_NOFILE),'pid':os.getpid()},indent=2))
plan=[]
for api in ['openai','anthropic','translation']:
 for size in [1024,16384]:
  for rate in [1000,3000,0]:plan.append(dict(tool='fortio',api=api,size=size,rate=rate,concurrency=32))
for size in [1024,16384]:plan.append(dict(tool='fortio',api='openai',size=size,rate=0,concurrency=512))
for api in ['openai','anthropic','translation']:
 for concurrency in [16,128]:plan.append(dict(tool='aiperf',api=api,concurrency=concurrency))
if a.qualification:
 plan=[dict(tool='fortio',api='openai',size=16384,rate=3000,concurrency=512),*[dict(tool='aiperf',api=api,concurrency=2) for api in ['openai','anthropic','translation']]]
if a.socket_qualification:
 plan=[dict(tool='fortio',api='openai',size=size,rate=0,concurrency=512) for size in [1024,16384]]
(a.output/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
for index,case in enumerate(plan):
 d=a.output/f'{index:02d}-{case["tool"]}-{case["api"]}';d.mkdir()
 api=case['api'];anthropic=api!='openai' and not(a.treatment=='direct' and api=='translation')
 port='8080' if a.treatment=='agentgateway' else {'openai':'8080','anthropic':'8082','translation':'8084'}[api]
 base='http://'+(a.backend+':8081' if a.treatment=='direct' else a.gateway+':'+port)
 url=base+('/v1/messages' if anthropic else '/v1/chat/completions')
 model='bench-anthropic' if api=='anthropic' else 'bench-openai'
 headers=['Content-Type:application/json','Authorization:Bearer dummy','x-api-key:dummy','anthropic-version:2023-06-01']
 if case['tool']=='fortio':
  req={'model':model,'messages':[{'role':'user','content':'x'*case['size']}],'max_tokens':64,'stream':False}
  payload=d/'payload.json';payload.write_text(json.dumps(req,separators=(',',':')))
  # Standard Go HTTP transport handles both content-length and chunked bodies identically.
  common=['fortio','load','-stdclient','-qps',str(case['rate']),'-c',str(case['concurrency']),'-uniform','-nocatchup','-timeout','10s','-X','POST','-payload-file',str(payload),'-r','0.000001']
  for h in headers+[f'x-bench-output-bytes:{case["size"]}']:common+=['-H',h]
  commands=[common+['-t','5s','-json',str(d/'warmup.json'),url],common+['-t','10s' if a.qualification else '30s','-json',str(d/'result.json'),url]]
 else:
  common=['/opt/gateway-benchmark/venv/bin/aiperf','profile','--model',model,'--tokenizer','builtin','--random-seed','42','--endpoint-type','messages' if anthropic else 'chat','--url',base,'--streaming','--concurrency',str(case['concurrency']),'--isl','128','--isl-stddev','0','--osl','64','--osl-stddev','0','--no-gpu-telemetry','--ui','none','--artifact-dir',str(d/'result')]
  for h in headers:common+=['-H',h]
  commands=[common+(['--request-count','4'] if a.qualification else ['--benchmark-duration','30','--benchmark-grace-period','10','--warmup-duration','5'])]
 metadata={'case':case,'treatment':a.treatment,'commands':commands,'started':datetime.datetime.now(datetime.timezone.utc).isoformat(),'processes':[]}
 for j,cmd in enumerate(commands):
  with (d/f'command-{j}.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT)
   record={'pid':proc.pid,'command':cmd}
   try:record['limits']=Path(f'/proc/{proc.pid}/limits').read_text()
   except OSError:pass
   try:record['exit']=proc.wait(timeout=180)
   except subprocess.TimeoutExpired:proc.kill();proc.wait();record['exit']='timeout'
   metadata['processes'].append(record)
 metadata['finished']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 (d/'execution.json').write_text(json.dumps(metadata,indent=2)+'\n')
 print(json.dumps({'case':case,'exits':[r['exit'] for r in metadata['processes']]}),flush=True)
 # Preserve product errors; classification happens from complete output and host evidence.
 if any(r['exit']=='timeout' for r in metadata['processes']):raise SystemExit('Tool timeout: stop for diagnosis')
 time.sleep(2)
(a.output/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat()+'\n')
