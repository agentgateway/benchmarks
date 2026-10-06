#!/usr/bin/env python3
"""Excluded diagnostic: observe fresh TLS probes alongside an unchanged upstream test."""
import datetime,json,os,pathlib,shlex,subprocess,time,sys
os.chdir('/opt/gateway-benchmark');os.environ['KUBECONFIG']='/etc/rancher/k3s/benchmark.kubeconfig'
out=pathlib.Path('diagnostics')/(sys.argv[1] if len(sys.argv)>1 else 'tls-startup');out.mkdir(parents=True,exist_ok=False)
args=shlex.split(pathlib.Path('results/praxis-v0.5.2/pass1/agentgateway/command.txt').read_text())
args=[x for x in args if not x.startswith('--report-output=')]+['--report-output='+str(out/'report.yaml'),'--run-test=TLSRouteSimpleSameNamespace']
(out/'command.json').write_text(json.dumps(args,indent=2)+'\n')
with (out/'full.log').open('w') as log,(out/'timeline.jsonl').open('w',buffering=1) as timeline:
 proc=subprocess.Popen(args,stdout=log,stderr=subprocess.STDOUT)
 while proc.poll() is None:
  row={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
  r=subprocess.run(['kubectl','--request-timeout=3s','get','service','gateway-tlsroute','-n','gateway-conformance-infra','-o','json'],capture_output=True,text=True)
  if r.returncode==0:
   row['service']=json.loads(r.stdout);ingress=row['service'].get('status',{}).get('loadBalancer',{}).get('ingress',[])
   if ingress:
    ip=ingress[0]['ip'];row['sockets']=subprocess.run(['ss','-tanp'],capture_output=True,text=True).stdout
    row['nat']=subprocess.run(['iptables-save','-t','nat'],capture_output=True,text=True).stdout
    if '--passive' in sys.argv:
     timeline.write(json.dumps(row)+'\n');time.sleep(1);continue
    try:
     r=subprocess.run(['openssl','s_client','-brief','-connect',ip+':443','-servername','abc.example.com'],input='',capture_output=True,text=True,timeout=2)
     row['fresh_tls_probe']={'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr}
    except subprocess.TimeoutExpired:row['fresh_tls_probe']={'timeout_seconds':2}
  timeline.write(json.dumps(row)+'\n');time.sleep(1)
 (out/'exit-code.txt').write_text(str(proc.returncode)+'\n')
print('Excluded diagnostic complete',proc.returncode)
