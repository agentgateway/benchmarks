#!/bin/bash
# Run one implementation at a time, after review of the Gateway smoke results.
set -u
source /tmp/gateway.env
class="$1"
case "$class" in
  agentgateway) project=agentgateway; version=v1.5.0; url=https://github.com/agentgateway/agentgateway ;;
  praxis) project=praxis-operator; version=fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c-core-0.5.2; url=https://github.com/praxis-proxy/operator ;;
  *) echo 'Expected agentgateway or praxis' >&2; exit 2 ;;
esac
evidence="/opt/benchmark/conformance-${class}-core${RUN_SUFFIX:-}"
mkdir "$evidence" || exit 2
# Previous suite cleanup requests namespace deletion asynchronously.
# Wait for deletion before the next implementation starts.
for ns in $(kubectl get namespaces -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' | grep '^gateway-conformance-' || true); do
  kubectl wait --for=delete namespace/"$ns" --timeout=180s || exit 2
done
kubectl get crd -o json > "$evidence/crds-before.json"
kubectl get pods -A -o json > "$evidence/pods-before.json"
date -u +%FT%TZ > "$evidence/start.txt"
cd /opt/benchmark/gateway-api/conformance || exit 2
timeout --signal=INT --kill-after=30s 45m go test -count=1 -timeout=44m -v . -run '^TestConformance$' -args \
  --gateway-class="$class" --conformance-profiles=GATEWAY-HTTP \
  --supported-features=Gateway,HTTPRoute,ReferenceGrant \
  --organization='Solo.io (independent evaluation)' --project="$project" \
  --url="$url" --version="$version" --contact=https://github.com/danehans \
  --report-output="$evidence/report.yaml" > "$evidence/full.log" 2>&1
code=$?
printf '%s\n' "$code" > "$evidence/exit-code.txt"
date -u +%FT%TZ > "$evidence/end.txt"
kubectl get pods -A -o json > "$evidence/pods-after.json"
kubectl get events -A -o json > "$evidence/events-after.json"
kubectl get gateway,httproute -A -o json > "$evidence/routes-after.json"
exit "$code"
