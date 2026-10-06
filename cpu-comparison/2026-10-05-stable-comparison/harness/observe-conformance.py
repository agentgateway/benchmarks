#!/usr/bin/env python3
"""Capture non-secret runtime state throughout conformance, including failed probes."""
import datetime,json,pathlib,subprocess,sys,time
out=pathlib.Path(sys.argv[1]); seen=set()
with (out/'runtime.jsonl').open('a',buffering=1) as stream:
 while True:
  row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  for kind in ['nodes','pods','events','gateways','httproutes','grpcroutes','tlsroutes','listenersets','backendtlspolicies']:
   try:
    r=subprocess.run(['kubectl','get',kind,'-A','-o','json'],capture_output=True,text=True,timeout=20)
    row[kind]=json.loads(r.stdout) if r.returncode==0 else {'error':r.stderr,'exit':r.returncode}
   except (subprocess.TimeoutExpired,json.JSONDecodeError) as e:row[kind]={'collector_error':str(e)}
  row['crash_diagnostics']=[]
  for pod in row.get('pods',{}).get('items',[]):
   meta=pod['metadata'];ns=meta['namespace']
   if not ns.startswith('gateway-conformance-'):continue
   for c in pod.get('status',{}).get('containerStatuses',[]):
    state=c.get('state',{});key=(meta['uid'],c['name'],c.get('restartCount',0))
    if key in seen or not ('terminated' in state or state.get('waiting',{}).get('reason')=='CrashLoopBackOff'):continue
    seen.add(key);item={'namespace':ns,'pod':meta['name'],'container':c['name'],'state':state,'restarts':c.get('restartCount',0)}
    try:
     r=subprocess.run(['kubectl','logs','-n',ns,meta['name'],'-c',c['name'],'--timestamps','--tail=100'],capture_output=True,text=True,timeout=20)
     item.update(log=r.stdout,stderr=r.stderr,exit=r.returncode)
    except subprocess.TimeoutExpired as e:item['collector_error']=str(e)
    row['crash_diagnostics'].append(item)
  stream.write(json.dumps(row,separators=(',',':'))+'\n');time.sleep(30)
