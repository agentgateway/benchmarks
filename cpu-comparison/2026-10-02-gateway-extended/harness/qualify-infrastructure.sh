#!/bin/bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
out="$1"; mkdir -p "$out"
kubectl wait nodes --all --for=condition=Ready --timeout=180s
kubectl get nodes -o json > "$out/nodes.json"
kubectl get pods -A -o json > "$out/pods.json"
kubectl get crds -o json > "$out/crds.json"
kubectl get gatewayclasses -o json > "$out/gatewayclasses.json"
kubectl get ipaddresspools -n metallb-system -o yaml > "$out/ip-pools.yaml"
kubectl get deployments -n agentgateway-system -o json > "$out/agentgateway-deployments.json"
kubectl get deployments -n praxis-system -o json > "$out/praxis-deployments.json"
sha256sum /opt/gateway-benchmark/gateway-conformance.test > "$out/tool-sha256.txt"
cat /proc/self/limits > "$out/client-limits.txt"
cat /proc/sys/fs/file-nr > "$out/host-file-nr.txt"
date -u +%FT%TZ > "$out/captured-at.txt"
python3 - "$out" <<'PY'
import json,pathlib,sys
p=pathlib.Path(sys.argv[1]);nodes=json.loads((p/'nodes.json').read_text())['items'];assert len(nodes)==5
for n in nodes:
 for c in n['status']['conditions']:
  if c['type']=='Ready':assert c['status']=='True',n['metadata']['name']
  if c['type'] in ['MemoryPressure','DiskPressure','PIDPressure']:assert c['status']=='False',(n['metadata']['name'],c)
crds=json.loads((p/'crds.json').read_text())['items']
for c in crds:
 if c['metadata']['name'].endswith('.gateway.networking.k8s.io'):
  a=c['metadata'].get('annotations',{});assert a['gateway.networking.k8s.io/channel']=='experimental';assert a['gateway.networking.k8s.io/bundle-version']=='v1.5.1'
print('Five ready nodes; no node pressure; matching experimental v1.5.1 CRDs')
PY
