#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
curl --retry 30 --retry-all-errors --retry-delay 5 --max-time 120 -fsSL http://10.128.15.199:8089/praxis-operator-image.tar -o praxis-operator-image.tar
k3s ctr images import praxis-operator-image.tar > praxis-operator-import.log
k3s crictl images -o json > images-after-import.json
touch praxis-operator-import-complete
