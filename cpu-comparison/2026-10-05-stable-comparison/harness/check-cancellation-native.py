#!/usr/bin/env python3
"""Verify upstream cancellation propagation separately from throughput."""
import argparse,json,time
from pathlib import Path
import httpx
p=argparse.ArgumentParser();p.add_argument('--treatment',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--gateway',default='10.128.0.63');p.add_argument('--backend',default='10.128.15.192');a=p.parse_args()
rows=[]
with httpx.Client(timeout=10) as c:
 for api,port in [('openai',8080),('anthropic',8082),('translation',8084)]:
  anthropic=api!='openai' and not(a.treatment=='direct' and api=='translation')
  base=f'http://{a.backend}:8081' if a.treatment=='direct' else f'http://{a.gateway}:{8080 if a.treatment=="agentgateway" else port}'
  before=c.get(f'http://{a.backend}:8081/metrics').json()
  req={'model':'bench-anthropic' if api=='anthropic' else 'bench-openai','messages':[{'role':'user','content':' hello'*128}],'max_tokens':1024,'stream':True}
  row={'treatment':a.treatment,'api':api,'before':before}
  try:
   with c.stream('POST',base+('/v1/messages' if anthropic else '/v1/chat/completions'),json=req,headers={'Authorization':'Bearer dummy','x-api-key':'dummy','anthropic-version':'2023-06-01'}) as r:
    r.raise_for_status()
    for line in r.iter_lines():
     if 'hello' in line:break
   start=time.monotonic()
   while time.monotonic()-start<7:
    after=c.get(f'http://{a.backend}:8081/metrics').json()
    if after['active']==0:break
    time.sleep(.05)
   row.update(after=after,settle_seconds=time.monotonic()-start,cancellation_propagated=after['canceled']==before['canceled']+1)
  except Exception as e:row['error']=repr(e)
  rows.append(row)
a.output.write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
