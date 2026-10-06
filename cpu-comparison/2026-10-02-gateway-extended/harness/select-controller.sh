#!/bin/bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
class="$1"; image="${2:-}"
case "$class" in agentgateway|praxis) ;; *) exit 2;; esac
# Clean test namespaces before stopping their owning controller.
remaining=$(kubectl get ns -o name | grep '^namespace/gateway-conformance-' || true)
[ -z "$remaining" ] || { echo 'Prior conformance namespaces still exist' >&2; exit 2; }
for entry in agentgateway-system/agentgateway praxis-system/praxis-operator; do
 ns=${entry%/*}; deploy=${entry#*/}
 kubectl scale deployment "$deploy" -n "$ns" --replicas=0
 for i in $(seq 1 90); do
  count=$(kubectl get pods -n "$ns" -o json | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["items"]))')
  [ "$count" = 0 ] && break
  sleep 2
 done
 [ "$count" = 0 ]
 done
if [ "$class" = praxis ]; then
 [ -n "$image" ]
 kubectl set env deployment/praxis-operator -n praxis-system PRAXIS_IMAGE="$image"
 ns=praxis-system; deploy=praxis-operator
else ns=agentgateway-system; deploy=agentgateway; fi
kubectl scale deployment "$deploy" -n "$ns" --replicas=2
kubectl rollout status deployment/"$deploy" -n "$ns" --timeout=240s
kubectl wait gatewayclass/"$class" --for=condition=Accepted --timeout=180s
kubectl get nodes -o wide
