#!/bin/bash
set -uo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
class="$1"; out="$2"; version="$3"
case "$class" in agentgateway) project=agentgateway; url=https://github.com/agentgateway/agentgateway;; praxis) project=praxis-operator; url=https://github.com/praxis-proxy/operator;; *) exit 2;; esac
mkdir "$out" || exit 2
for ns in $(kubectl get namespace -o name | grep '^namespace/gateway-conformance-' || true); do
 kubectl wait --for=delete "$ns" --timeout=180s || exit 2
done
for kind in crd nodes pods gatewayclass; do kubectl get "$kind" -A -o json > "$out/$kind-before.json" || exit 2; done
features=Gateway,HTTPRoute,ReferenceGrant,GatewayStaticAddresses
args=(/opt/gateway-benchmark/gateway-conformance.test -test.v -test.run '^TestConformance$' -test.timeout=19m
 --gateway-class="$class" --conformance-profiles=GATEWAY-HTTP --run-test=GatewayStaticAddresses --supported-features="$features"
 --usable-address=198.18.1.254 --unusable-address=bogus.example.com
 --organization='Solo.io (independent coverage probes, not a vendor support declaration)' --project="$project" --url="$url" --version="$version"
 --contact=https://github.com/danehans --report-output="$out/report.yaml")
printf '%q ' "${args[@]}" > "$out/command.txt"
date -u +%FT%TZ > "$out/start.txt"
python3 /opt/gateway-benchmark/observe-conformance.py "$out" & observer=$!
timeout --signal=INT --kill-after=30s 20m "${args[@]}" > "$out/full.log" 2>&1
code=$?
printf '%s\n' "$code" > "$out/exit-code.txt"
date -u +%FT%TZ > "$out/end.txt"
kill "$observer"; wait "$observer" 2>/dev/null || true
for kind in nodes pods events gatewayclass gateways httproutes grpcroutes tlsroutes listenersets backendtlspolicies; do kubectl get "$kind" -A -o json > "$out/$kind-after.json"; done
for ns in agentgateway-system praxis-system; do kubectl logs -n "$ns" -l app.kubernetes.io/name="${ns%-system}" --all-containers=true --prefix --timestamps --tail=-1 --since-time="$(cat "$out/start.txt")" > "$out/$ns-controller.log" 2>&1; done
# Praxis operator label differs from the system namespace.
kubectl logs -n praxis-system -l app.kubernetes.io/name=praxis-operator --all-containers=true --prefix --timestamps --tail=-1 --since-time="$(cat "$out/start.txt")" > "$out/praxis-system-controller.log" 2>&1
cleanup_ok=true
for ns in $(kubectl get namespace -o name | grep '^namespace/gateway-conformance-' || true); do
 kubectl wait --for=delete "$ns" --timeout=180s >> "$out/cleanup.log" 2>&1 || cleanup_ok=false
done
if [ "$cleanup_ok" = true ]; then touch "$out/CLEANUP-COMPLETE"; else exit 2; fi
exit "$code"
