#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
curl --retry 3 -fsSL http://10.128.15.199:8089/gateway-conformance.test -o gateway-conformance.test
chmod +x gateway-conformance.test
sha256sum gateway-conformance.test > tool-sha256.txt
bash /opt/gateway-benchmark/infra/configure-tcp-client.sh
touch http-client-ready
