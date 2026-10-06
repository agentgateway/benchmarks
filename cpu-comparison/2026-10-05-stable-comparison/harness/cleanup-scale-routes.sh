#!/bin/bash
# Bulk DELETE avoids kubectl's per-object delete/wait bookkeeping at route scale.
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
start=$SECONDS
kubectl --request-timeout=60s delete --raw '/apis/gateway.networking.k8s.io/v1/namespaces/gateway-scale/httproutes?labelSelector=benchmark%3Dgateway-scale' > /dev/null
while [ "$((SECONDS-start))" -lt 180 ]; do
 count=$(kubectl --request-timeout=30s get httproute -n gateway-scale -l benchmark=gateway-scale -o json | python3 -c 'import json,sys;print(len(json.load(sys.stdin)["items"]))')
 if [ "$count" = 0 ]; then printf 'Scale route cleanup verified empty after %s seconds\n' "$((SECONDS-start))"; exit 0; fi
 sleep 1
done
printf 'Scale route cleanup timed out with %s objects remaining\n' "$count" >&2
exit 1
