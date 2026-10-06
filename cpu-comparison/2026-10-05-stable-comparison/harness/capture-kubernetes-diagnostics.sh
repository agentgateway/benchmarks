#!/bin/bash
# Read-only diagnostic snapshot, separate from measured runner timing.
set -uo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
out="$1"
mkdir "$out" || exit 1
kubectl get gateway,pod,deployment,replicaset,configmap,service -n gateway-benchmark -o json > "$out/resources.json"
kubectl get httproute -n gateway-scale -o json > "$out/routes.json"
kubectl get events -n gateway-benchmark -o json > "$out/events.json"
for pod in $(kubectl get pods -n gateway-benchmark -o name); do
 name="${pod#pod/}"
 kubectl logs -n gateway-benchmark "$pod" --tail=100 > "$out/$name.log" 2>&1 || true
 kubectl logs -n gateway-benchmark "$pod" --previous --tail=100 > "$out/$name-previous.log" 2>&1 || true
done
kubectl logs -n praxis-system deployment/praxis-operator --all-pods=true --since=15m > "$out/controller.log" 2>&1 || true
date -u +%FT%TZ > "$out/captured-at.txt"
