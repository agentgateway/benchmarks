#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
exec 9>/run/gwext-campaign.lock
flock -n 9 || { echo "Another campaign job holds the test lock" >&2; exit 2; }
campaign="$1"; repetition="$2"; class="$3"; mode="${4:-full}"
case "$campaign" in
 praxis-v0.5.2) image=ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8; version=fb8beaa-core-v0.5.2;;
 praxis-nightly-20261002) image=ghcr.io/praxis-proxy/praxis@sha256:be62d256d5ec92aacb1216baba506aac763e2100f9eb361820a5c27c54e17be8; version=fb8beaa-core-nightly-20261002-31ac6dc;;
 *) exit 2;;
esac
[[ "$repetition" =~ ^(qualification|pass[123])$ ]] || exit 2
parent="results/$campaign/$repetition"; mkdir -p "$parent"
test ! -e "$parent/$class" && test ! -e "$parent/$class-selection.log"
bash select-controller.sh "$class" "$image" > "$parent/$class-selection.log" 2>&1
[ "$class" = agentgateway ] && version=v1.6.0
set +e
bash run-conformance.sh "$class" "$parent/$class" "$version" "$mode" > "$parent/$class-harness.log" 2>&1
code=$?
set -e
printf '%s\n' "$code" > "$parent/$class-harness-exit.txt"
# Exit 1 may be an ordinary product assertion failure. Review the detailed result.
test -f "$parent/$class/CLEANUP-COMPLETE" || exit 2
touch "$parent/$class/JOB-FINISHED"
