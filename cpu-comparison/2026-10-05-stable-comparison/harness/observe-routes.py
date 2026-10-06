#!/usr/bin/env python3
"""Draft CL2 observer: generation-aware status plus independently sampled traffic."""
import argparse,concurrent.futures,datetime,json,os,subprocess,time
from pathlib import Path
import httpx
p=argparse.ArgumentParser();p.add_argument('--namespace',required=True);p.add_argument('--count',type=int,required=True);p.add_argument('--marker',required=True);p.add_argument('--start-only',action='store_true');a=p.parse_args()
root=Path(os.environ['BENCHMARK_SCALE_EVIDENCE']);root.mkdir(parents=True,exist_ok=True)
startfile=root/f'{a.marker}-start.json';report=root/f'{a.marker}-result.json'
if a.start_only:
 startfile.write_text(json.dumps({'monotonic':time.monotonic(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}));raise SystemExit(0)
start=json.loads(startfile.read_text());observation_start=time.monotonic();deadline=observation_start+300
url=os.environ['BENCHMARK_GATEWAY_URL'].rstrip('/')+'/plain?bytes=0'
gateway=os.environ['BENCHMARK_GATEWAY_NAME'];gateway_ns=os.environ['BENCHMARK_GATEWAY_NAMESPACE'];controller=os.environ['BENCHMARK_CONTROLLER_NAME']
rows=[];first_status=None;first_sample=None;first_all=None;final_routes=None
with httpx.Client(timeout=3,limits=httpx.Limits(max_connections=32,max_keepalive_connections=32)) as client, concurrent.futures.ThreadPoolExecutor(max_workers=32) as pool:
 def probe(route):
  name=route['metadata']['name'];host=route['spec']['hostnames'][0]
  try:
   r=client.get(url,headers={'Host':host});return {'route':name,'status':r.status_code,'marker':r.headers.get('x-benchmark-generation'),'passed':r.status_code==200 and r.headers.get('x-benchmark-generation')==a.marker}
  except Exception as e:return {'route':name,'passed':False,'error':str(e)}
 while True:
  t=time.monotonic();raw=subprocess.check_output(['kubectl','get','httproute','-n',a.namespace,'-l','benchmark=gateway-scale','-o','json'],timeout=30,text=True)
  routes=json.loads(raw)['items'];routes.sort(key=lambda r:r['metadata']['name']);final_routes=routes
  def current(r):
   generation=r['metadata']['generation']
   for parent in r.get('status',{}).get('parents',[]):
    ref=parent.get('parentRef',{})
    if ref.get('name')!=gateway or ref.get('namespace',a.namespace)!=gateway_ns or parent.get('controllerName')!=controller:continue
    conditions={c['type']:c for c in parent.get('conditions',[])}
    if all(conditions.get(k,{}).get('status')=='True' and conditions[k].get('observedGeneration')==generation for k in ['Accepted','ResolvedRefs']):return True
   return False
  ready=sum(current(r) for r in routes);all_status=len(routes)==a.count and ready==a.count
  if all_status and first_status is None:first_status=time.monotonic()-start['monotonic']
  sampled=routes[::max(1,len(routes)//100)][:100]
  probes=list(pool.map(probe,sampled));sample_ok=bool(probes) and all(r['passed'] for r in probes)
  if sample_ok and first_sample is None:first_sample=time.monotonic()-start['monotonic']
  full=[]
  if all_status:
   full=list(pool.map(probe,routes))
   if len(full)==a.count and all(r['passed'] for r in full):first_all=time.monotonic()-start['monotonic']
  rows.append({'seconds_from_mutation_start':time.monotonic()-start['monotonic'],'objects':len(routes),'current_generation_accepted_and_resolved':ready,'sample_probes':probes,'full_probe_passed':sum(r['passed'] for r in full),'full_probe_failures':[r for r in full if not r['passed']]})
  result={'namespace':a.namespace,'count':a.count,'marker':a.marker,'start':start,'post_submission_observer_started_seconds':observation_start-start['monotonic'],'status_convergence_seconds':first_status,'sample_traffic_convergence_seconds':first_sample,'all_route_traffic_verified_seconds':first_all,'complete':first_all is not None,'observations':rows}
  report.write_text(json.dumps(result,indent=2)+'\n')
  if first_all is not None or time.monotonic()>=deadline:break
  time.sleep(max(0,5-(time.monotonic()-t)))
(root/f'{a.marker}-routes-final.json').write_text(json.dumps(final_routes,indent=2)+'\n')
# A product that never converges is retained in the result, not a harness exception.
print(json.dumps({k:v for k,v in result.items() if k!='observations'}))
