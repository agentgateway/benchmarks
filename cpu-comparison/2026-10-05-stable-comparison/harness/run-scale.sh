#!/bin/bash
set -uo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
class="$1";count="$2";endpoint="$3";out="$4"
case "$class" in agentgateway) controller=agentgateway.dev/agentgateway ;; praxis) controller=praxis.sh/gateway-controller ;; *) exit 2;; esac
mkdir -p "$(dirname "$out")"
mkdir "$out" || exit 2
export BENCHMARK_SCALE_EVIDENCE="$out/observations"
export BENCHMARK_GATEWAY_URL="$endpoint"
export BENCHMARK_GATEWAY_NAME=benchmark BENCHMARK_GATEWAY_NAMESPACE=gateway-benchmark BENCHMARK_CONTROLLER_NAME="$controller"
cd /opt/gateway-benchmark
bash /opt/gateway-benchmark/cleanup-scale-routes.sh || exit 2
printf 'Routes: %s\nGateway: benchmark\nGatewayNamespace: gateway-benchmark\nBenchmarkNamespace: gateway-scale\n' "$count" > "$out/overrides.yaml"
kubectl get nodes,pods -A -o json > "$out/placement-before.json"
date -u +%FT%TZ > "$out/start.txt"
args=(./clusterloader2 --provider=local --kubeconfig="$KUBECONFIG" --testconfig=configs/clusterloader2/config.yaml --testoverrides="$out/overrides.yaml" --report-dir="$out/cl2" --k8s-clients-number=2 --enable-prometheus-server=false --v=2)
printf '%q ' "${args[@]}" > "$out/command.txt"
timeout --signal=INT --kill-after=20s 20m "${args[@]}" > "$out/full.log" 2>&1
code=$?
printf '%s\n' "$code" > "$out/exit-code.txt"
date -u +%FT%TZ > "$out/end.txt"
kubectl get nodes,pods -A -o json > "$out/placement-after.json"
kubectl get gateway,httproute -A -o json > "$out/routes-after.json"
kubectl get events -A -o json > "$out/events-after.json"
if [ "$class" = agentgateway ]; then
 kubectl logs -n agentgateway-system deployment/agentgateway --all-pods=true --since=25m > "$out/controller.log" 2>&1 || true
else
 kubectl logs -n praxis-system deployment/praxis-operator --all-pods=true --since=25m > "$out/controller.log" 2>&1 || true
fi
exit "$code"
