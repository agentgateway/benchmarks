#!/usr/bin/env python3
"""Validate request/response semantics before any performance measurement."""
import argparse,json,time
from pathlib import Path
import httpx
p=argparse.ArgumentParser();p.add_argument('--treatment',choices=['direct','agentgateway','praxis','praxis-ai-nightly'],required=True);p.add_argument('--gateway',required=True);p.add_argument('--backend',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
a.output.mkdir(parents=True,exist_ok=False)
results=[]
for api in ['openai','anthropic','translation']:
 url='http://'+(a.backend+':8081' if a.treatment=='direct' else a.gateway+':'+('8080' if a.treatment=='agentgateway' else {'openai':'8080','anthropic':'8082','translation':'8084'}[api]))
 anthropic=api!='openai' and not(a.treatment=='direct' and api=='translation')
 url+='/v1/messages' if anthropic else '/v1/chat/completions'
 for size in [1024,16384]:
  for mode in ['json','stream','429']:
   row={'treatment':a.treatment,'api':api,'size':size,'mode':mode,'url':url}
   req={'model':'bench-anthropic' if api=='anthropic' else 'bench-openai','messages':[{'role':'user','content':'x'*size}],'max_tokens':64,'stream':mode=='stream'}
   headers={'content-type':'application/json','authorization':'Bearer dummy','x-api-key':'dummy','anthropic-version':'2023-06-01','x-bench-output-bytes':str(size)}
   if mode=='429':headers['x-bench-error']='true'
   try:
    if mode=='stream':
     chunks=[];events=[];times=[];start=time.monotonic()
     with httpx.stream('POST',url,json=req,headers=headers,timeout=15) as r:
      assert r.status_code==200,r.status_code
      for line in r.iter_lines():
       if not line.startswith('data: '):continue
       text=line[6:]
       if text=='[DONE]':events.append('DONE');continue
       v=json.loads(text);events.append(v.get('type',v.get('object')))
       piece=v.get('delta',{}).get('text','') if anthropic else (v.get('choices',[{}])[0].get('delta',{}).get('content','') if v.get('choices') else '')
       if piece:chunks.append(piece);times.append(time.monotonic()-start)
     assert ''.join(chunks)==' hello'*64,repr(chunks)[:300]
     assert 'message_stop' in events if anthropic else 'DONE' in events,events
     assert len(times)>1 and times[-1]-times[0]>.15,'stream appears buffered or timestamps invalid'
     row.update(chunks=len(chunks),first_content_seconds=times[0],last_content_seconds=times[-1])
    else:
     r=httpx.post(url,json=req,headers=headers,timeout=15);row['status']=r.status_code
     assert r.status_code==(429 if mode=='429' else 200),r.text[:200]
     v=r.json()
     if mode=='json':
      content=v['content'][0]['text'] if anthropic else v['choices'][0]['message']['content'];assert content=='x'*size
      assert 'usage' in v
    row['passed']=True
   except Exception as e:row.update(passed=False,error=repr(e))
   results.append(row)
   (a.output/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({'checks':len(results),'passed':sum(r['passed'] for r in results)}))
raise SystemExit(int(not all(r['passed'] for r in results)))
