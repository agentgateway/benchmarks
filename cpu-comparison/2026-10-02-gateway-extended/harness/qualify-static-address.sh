#!/bin/bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
out=/opt/gateway-benchmark/qualification/static-address
mkdir "$out"
date -u +%FT%TZ > "$out/start.txt"
kubectl get services -A -o json > "$out/services-before.json"
python3 - "$out/services-before.json" <<'PY'
import json,sys
for svc in json.load(open(sys.argv[1]))['items']:
 assert all(x.get('ip')!='198.18.1.254' for x in svc.get('status',{}).get('loadBalancer',{}).get('ingress',[])),'Static test address is already allocated'
PY
cat > "$out/service.yaml" <<'YAML'
apiVersion: v1
kind: Service
metadata:
  name: conformance-static-allocation-check
  namespace: gateway-backend
spec:
  type: LoadBalancer
  loadBalancerIP: 198.18.1.254
  selector:
    app: benchmark-backend
  ports:
  - port: 18081
    targetPort: 8081
YAML
trap 'kubectl delete -f "$out/service.yaml" --ignore-not-found --wait=true > "$out/cleanup.log" 2>&1' EXIT
kubectl apply -f "$out/service.yaml" > "$out/apply.log"
kubectl wait service/conformance-static-allocation-check -n gateway-backend --for=jsonpath='{.status.loadBalancer.ingress[0].ip}'=198.18.1.254 --timeout=120s > "$out/address-wait.log"
kubectl get service/conformance-static-allocation-check -n gateway-backend -o json > "$out/service-assigned.json"
curl --retry 10 --retry-all-errors --retry-delay 1 --max-time 2 --fail -sS http://198.18.1.254:18081/healthz > "$out/body.txt" 2> "$out/curl.log"
test "$(cat "$out/body.txt")" = ok
date -u +%FT%TZ > "$out/end.txt"
touch "$out/PASSED"
