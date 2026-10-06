#!/usr/bin/env python3
"""Bootstrap already-created isolated campaign nodes; records each stage."""
import concurrent.futures,json,os,re,subprocess,tarfile,time
from pathlib import Path
root=Path(__file__).resolve().parents[1];os.chdir(root)
roles=['kcontrol','kcontroller','kgateway','kbackend','kclient']
base=['--project=solo-oss','--zone=us-central1-a'];prefix='gwext-1002-'
def run(cmd,**kw):return subprocess.run(cmd,check=True,text=True,**kw)
def ssh(role,cmd,**kw):return run(['gcloud','compute','ssh',prefix+role,*base,'--command',cmd],**kw)
def copy(role,files,dest='/tmp/'):
 return run(['gcloud','compute','scp',*[str(f) for f in files],prefix+role+':'+dest,*base,'--quiet'])
ips={r:json.loads((root/f'.work/create-{r}.json').read_text())[0]['networkInterfaces'][0]['networkIP'] for r in roles}
previous_file=root/'.work/kubernetes-ips.json'
previous_ips=json.loads(previous_file.read_text()) if previous_file.exists() else {'kcontrol':'10.128.15.199','kbackend':'10.128.15.206','kgateway':'10.128.15.201'}
previous_file.write_text(json.dumps(ips,indent=2)+'\n')
# Render this campaign's role placeholders to newly allocated private addresses.
replacements={'CONTROL_INTERNAL_IP':ips['kcontrol'],'BACKEND_INTERNAL_IP':ips['kbackend'],'GATEWAY_INTERNAL_IP':ips['kgateway']}
for role in ['kcontrol','kbackend','kgateway']:replacements[previous_ips[role]]=ips[role]
pattern=re.compile('|'.join(re.escape(k) for k in replacements))
for dirname in ['infra','harness','configs']:
 for p in (root/dirname).rglob('*'):
  if p.is_file() and p.suffix in ['.py','.sh','.yaml','.json'] and p.name!='provision-kubernetes.py':
   s=p.read_text()
   s=pattern.sub(lambda m:replacements[m.group(0)],s)
   p.write_text(s)
def ready(r):
 for _ in range(90):
  try:ssh(r,'test -f /opt/gateway-benchmark/ready',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);break
  except subprocess.CalledProcessError:time.sleep(10)
 else:raise RuntimeError(r+' startup failed')
 copy(r,[root/'infra/start-kubernetes-node.sh'])
 print(r+' ready',flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:list(pool.map(ready,roles))
ssh('kcontrol','sudo bash /tmp/start-kubernetes-node.sh kcontrol')
for _ in range(60):
 try:token=ssh('kcontrol','sudo cat /var/lib/rancher/k3s/server/node-token',capture_output=True).stdout;break
 except subprocess.CalledProcessError:time.sleep(5)
else:raise RuntimeError('control token unavailable')
secret=root/'.work/k3s-token';secret.write_text(token);secret.chmod(0o600)
def worker(r):
 copy(r,[secret]);ssh(r,'sudo bash /tmp/start-kubernetes-node.sh '+r+' '+ips['kcontrol'])
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(worker,roles[1:]))
ssh('kcontrol','sudo kubectl wait nodes --all --for=condition=Ready --timeout=240s')
kube=ssh('kcontrol','sudo cat /etc/rancher/k3s/k3s.yaml',capture_output=True).stdout.replace('127.0.0.1',ips['kcontrol'])
kube_file=root/'.work/client.kubeconfig';kube_file.write_text(kube);kube_file.chmod(0o600)
copy('kclient',[kube_file]);ssh('kclient','sudo install -m 600 /tmp/client.kubeconfig /etc/rancher/k3s/benchmark.kubeconfig && rm /tmp/client.kubeconfig')
payload=root/'.work/kubernetes-payload.tar.gz'
with tarfile.open(payload,'w:gz') as t:
 t.add(root/'configs',arcname='configs')
 for p in (root/'harness').iterdir():
  if p.is_file():t.add(p,arcname=p.name)
 for p in (root/'infra').glob('*.sh'):t.add(p,arcname='infra/'+p.name)
for r in ['kcontrol','kclient']:
 copy(r,[payload]);ssh(r,'sudo tar -xzf /tmp/kubernetes-payload.tar.gz -C /opt/gateway-benchmark')
for r in roles:
 copy(r,[root/'harness/collect-host.py']);ssh(r,'sudo cp /tmp/collect-host.py /opt/gateway-benchmark/ && sudo systemd-run --unit=benchmark-collector --property=RuntimeMaxSec=44000 /usr/bin/python3 /opt/gateway-benchmark/collect-host.py --runtime cri')
copy('kbackend',[root/'.work/mock-server']);ssh('kbackend','sudo mkdir -p /opt/gateway-benchmark/fixture && sudo install -m 755 /tmp/mock-server /opt/gateway-benchmark/fixture/mock-server')
copy('kcontrol',[root/'.work/praxis-operator-source.tar.gz',root/'.work/clusterloader2',root/'.work/gateway-conformance.test'])
ssh('kcontrol','sudo bash /opt/gateway-benchmark/infra/prepare-kubernetes-tools.sh && sudo systemd-run --unit=operator-build --property=RuntimeMaxSec=1800 bash /opt/gateway-benchmark/infra/build-praxis-operator.sh')
ssh('kcontrol','sudo mkdir -p /opt/gateway-benchmark/public-tools && sudo cp /tmp/clusterloader2 /tmp/gateway-conformance.test /opt/gateway-benchmark/public-tools/ && sudo systemd-run --unit=tool-transfer --property=RuntimeMaxSec=1800 python3 -m http.server 8089 --bind '+ips['kcontrol']+' --directory /opt/gateway-benchmark/public-tools')
ssh('kclient','sudo bash /opt/gateway-benchmark/infra/setup-http-client.sh')
for _ in range(180):
 try:ssh('kcontrol','test -f /opt/gateway-benchmark/praxis-operator-build-complete',stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);break
 except subprocess.CalledProcessError:time.sleep(10)
else:raise RuntimeError('operator build incomplete')
ssh('kcontrol','sudo cp /opt/gateway-benchmark/praxis-operator-image.tar /opt/gateway-benchmark/public-tools/')
copy('kcontroller',[root/'infra/import-praxis-operator.sh']);ssh('kcontroller','sudo bash /tmp/import-praxis-operator.sh')
ssh('kcontrol','sudo bash /opt/gateway-benchmark/infra/install-kubernetes-controllers.sh && sudo kubectl create namespace gateway-benchmark && sudo kubectl create namespace gateway-scale && sudo systemctl stop tool-transfer docker docker.socket')
(root/'.work/KUBERNETES-READY').write_text('Bootstrap complete; qualification required\n')
print('Kubernetes bootstrap complete; qualification required',flush=True)
