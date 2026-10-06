#!/usr/bin/env python3
"""Excluded, passive watch diagnostic around the unchanged static-address test."""
import datetime
import fcntl
import json
import os
from pathlib import Path
import shlex
import subprocess
import threading
import time

os.chdir('/opt/gateway-benchmark')
os.environ['KUBECONFIG'] = '/etc/rancher/k3s/benchmark.kubeconfig'
lock = open('/run/gwext-campaign.lock', 'w')
fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
deployments = json.loads(subprocess.check_output(['kubectl','get','deployments','-A','-o','json']))
assert any(d['metadata']['namespace']=='agentgateway-system' and d['spec'].get('replicas',1)>0 for d in deployments['items'])
assert all(d['spec'].get('replicas',1)==0 for d in deployments['items'] if d['metadata']['namespace']=='praxis-system')
out = Path('diagnostics/static-address-status')
out.mkdir(parents=True, exist_ok=False)
args = shlex.split(Path('results/praxis-v0.5.2/pass1/agentgateway/command.txt').read_text())
args = [x for x in args if not x.startswith('--report-output=')]
args += ['--report-output='+str(out/'report.yaml'), '--run-test=GatewayStaticAddresses']
(out/'command.json').write_text(json.dumps(args,indent=2)+'\n')
processes, threads, handles = [], [], []
def watch(kind, proc):
    decoder, buffer = json.JSONDecoder(), ''
    with (out/(kind+'.jsonl')).open('w',buffering=1) as stream:
        for line in proc.stdout:
            buffer += line
            while buffer.strip():
                buffer = buffer.lstrip()
                try:
                    event, end = decoder.raw_decode(buffer)
                except json.JSONDecodeError:
                    break
                stream.write(json.dumps({'received_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'event':event})+'\n')
                buffer = buffer[end:]
for kind in ['gateways','services']:
    err = (out/(kind+'-watch.stderr')).open('w'); handles.append(err)
    proc = subprocess.Popen(['kubectl','get',kind,'-A','--watch','--output-watch-events','-o','json'],stdout=subprocess.PIPE,stderr=err,text=True)
    processes.append(proc)
    thread = threading.Thread(target=watch,args=(kind,proc),daemon=True)
    thread.start(); threads.append(thread)
try:
    time.sleep(1)
    with (out/'full.log').open('w') as log:
        run = subprocess.run(args,stdout=log,stderr=subprocess.STDOUT,timeout=600)
    (out/'exit-code.txt').write_text(str(run.returncode)+'\n')
    time.sleep(2)
finally:
    for proc in processes: proc.terminate()
    for proc in processes: proc.wait(timeout=10)
    for thread in threads: thread.join(timeout=10)
    for handle in handles: handle.close()
print('Excluded static-address diagnostic complete')
