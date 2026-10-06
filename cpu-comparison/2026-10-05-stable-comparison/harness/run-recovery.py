#!/usr/bin/env python3
"""Bounded controller/data-plane restart observations with scheduled traffic."""
import argparse,asyncio,datetime,json,os,time
from pathlib import Path
import httpx
p=argparse.ArgumentParser();p.add_argument('--treatment',choices=['agentgateway','praxis'],required=True);p.add_argument('--url',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
os.environ['KUBECONFIG']='/etc/rancher/k3s/benchmark.kubeconfig';a.output.mkdir(parents=True,exist_ok=False)
async def command(args):
 proc=await asyncio.create_subprocess_exec(*args,stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.PIPE)
 try:out,err=await asyncio.wait_for(proc.communicate(),150)
 except asyncio.TimeoutError:proc.kill();out,err=await proc.communicate();return {'command':args,'exit':'timeout','stdout':out.decode(),'stderr':err.decode()}
 return {'command':args,'exit':proc.returncode,'stdout':out.decode(),'stderr':err.decode()}
async def main():
 for kind in ['controller','data-plane']:
  d=a.output/kind;d.mkdir();rows=[];start=time.monotonic();events=[]
  async with httpx.AsyncClient(timeout=2,limits=httpx.Limits(max_connections=64,max_keepalive_connections=64)) as client:
   async def probe(sequence,scheduled):
    t=time.monotonic();r={'sequence':sequence,'scheduled_seconds':scheduled-start,'start_seconds':t-start,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    try:
     response=await client.get(a.url.rstrip('/')+'/healthz');r.update(status=response.status_code,success=response.status_code==200 and response.text=='ok')
    except Exception as err:r.update(success=False,error=repr(err))
    r['elapsed_seconds']=time.monotonic()-t;rows.append(r)
   async def mutation():
    await asyncio.sleep(10);events.append({'event':'mutation-start','seconds':time.monotonic()-start})
    if kind=='controller':
     ns='agentgateway-system' if a.treatment=='agentgateway' else 'praxis-system';name='agentgateway' if a.treatment=='agentgateway' else 'praxis-operator'
     commands=[['kubectl','rollout','restart',f'deployment/{name}','-n',ns],['kubectl','rollout','status',f'deployment/{name}','-n',ns,'--timeout=120s']]
    else:
     found=await command(['kubectl','get','deployment','-n','gateway-benchmark','-o','json']);items=json.loads(found['stdout'])['items'];assert len(items)==1
     name=items[0]['metadata']['name'];commands=[['kubectl','delete','pod','--all','-n','gateway-benchmark','--wait=false'],['kubectl','rollout','status',f'deployment/{name}','-n','gateway-benchmark','--timeout=120s']]
    results=[]
    for cmd in commands:results.append(await command(cmd))
    events.append({'event':'mutation-commands-complete','seconds':time.monotonic()-start,'results':results})
   task=asyncio.create_task(mutation());pending=[];i=0;completed_at=None
   while time.monotonic()-start<175:
    scheduled=start+i*.1;await asyncio.sleep(max(0,scheduled-time.monotonic()));pending.append(asyncio.create_task(probe(i,scheduled)));i+=1
    if task.done() and completed_at is None:completed_at=time.monotonic()
    if completed_at is not None and time.monotonic()-completed_at>=10:break
   await task;await asyncio.gather(*pending)
  rows.sort(key=lambda r:r['sequence']);(d/'probes.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows));(d/'events.json').write_text(json.dumps(events,indent=2)+'\n')
  (d/'summary.json').write_text(json.dumps({'requests':len(rows),'failed_requests':sum(not r['success'] for r in rows),'max_dispatch_delay_seconds':max(r['start_seconds']-r['scheduled_seconds'] for r in rows),'note':'Scheduled 10 requests/sec; report individual failures and recovery interval, not a production availability estimate.'},indent=2)+'\n')
  print(kind+' observations complete',flush=True)
(a.output/'STARTED').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
asyncio.run(main());(a.output/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
