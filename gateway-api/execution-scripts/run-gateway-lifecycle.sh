#!/bin/bash
set -euo pipefail
source /tmp/gateway.env
while systemctl is-active --quiet agw-gateway-traffic-2; do sleep 5; done
# Do not start lifecycle activity until every planned traffic case has finished.
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/opt/benchmark/gateway-traffic')
plan=json.loads((p/'plan.json').read_text());results=json.loads((p/'results.json').read_text())
assert len(results)==len(plan)==12
assert not any(r['outcome']=='timeout' for r in results)
PY
kubectl delete httproute -n default agentgateway praxis --ignore-not-found
cd /opt/benchmark/gateway-source
python3 tests/campaign.py --profile full --repetitions 1 \
  --case attached-routes --case probe --case routechange --case scale-10x100 --case scale-50x100 \
  --output /opt/benchmark/gateway-lifecycle > /opt/benchmark/gateway-lifecycle.log 2>&1
