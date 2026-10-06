#!/bin/bash
set -euo pipefail
source /tmp/gateway.env
while systemctl is-active --quiet agw-conformance-praxis-core-clean; do sleep 5; done
for ns in $(kubectl get ns -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep '^gateway-conformance-' || true); do
  kubectl wait --for=delete namespace/"$ns" --timeout=180s
done
cd /opt/benchmark/gateway-source
mkdir /opt/benchmark/gateway-direct
kubectl get pods,deployments,services -A -o json > /opt/benchmark/gateway-direct/before.json
kubectl apply -f - <<'YAML'
apiVersion: v1
kind: Service
metadata:
  name: direct-benchmark
  namespace: default
spec:
  type: LoadBalancer
  selector: {app: backend}
  ports:
  - name: http
    port: 80
    targetPort: 8080
YAML
address=''
for attempt in $(seq 1 120); do
  address=$(kubectl get svc direct-benchmark -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
  if [[ -n "$address" ]] && [[ $(curl -s --max-time 2 -o /dev/null -w '%{http_code}' "http://$address/") == 200 ]]; then break; fi
  sleep 1
done
test -n "$address"
for connections in 1 16 512; do
  dest="/opt/benchmark/gateway-direct/c${connections}-q0"
  mkdir "$dest"
  date -u +%FT%TZ > "$dest/start.txt"
  docker run --rm --init --network=host -v "$dest:/tmp/results" "$BENCHTOOL_IMAGE" -d 60 -q 0 -c "$connections" -p 0 "$address#direct" > "$dest/run.log" 2>&1
  test -s "$dest/fortio.json"
  date -u +%FT%TZ > "$dest/end.txt"
done
kubectl get pods,deployments,services -A -o json > /opt/benchmark/gateway-direct/after.json
python3 tests/campaign.py --profile full --repetitions 1 \
  --case traffic-c1-q0 --case traffic-c1-q10000 \
  --case traffic-c16-q0 --case traffic-c16-q10000 \
  --case traffic-c512-q0 --case traffic-c512-q10000 \
  --output /opt/benchmark/gateway-traffic > /opt/benchmark/gateway-traffic.log 2>&1
