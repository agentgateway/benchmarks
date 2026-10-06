#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
pass="$1"
[[ "$pass" =~ ^pass[123]$ ]]
mkdir -p /opt/gateway-benchmark/results/static-address
parent="/opt/gateway-benchmark/results/static-address/$pass"
mkdir "$parent"
for class in agentgateway praxis; do
 bash switch-gateway.sh direct > "$parent/$class-cleanup.log" 2>&1
 bash select-controller.sh "$class" ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8 > "$parent/$class-selection.log" 2>&1
 version=v1.6.0; [ "$class" = praxis ] && version=operator-fb8beaa-core-v0.5.2
 set +e
 bash run-static-address.sh "$class" "$parent/$class" "$version" > "$parent/$class-harness.log" 2>&1
 code=$?
 set -e
 printf '%s\n' "$code" > "$parent/$class-harness-exit.txt"
 test -f "$parent/$class/CLEANUP-COMPLETE"
 [ "$code" = 0 ] || [ "$code" = 1 ]
done
touch "$parent/COMPLETE"
