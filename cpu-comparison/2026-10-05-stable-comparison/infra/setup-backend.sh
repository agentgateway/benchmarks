#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
private_ip=$(hostname -I | awk '{print $1}')
docker run -d --name mock --network=host --cpus=6 --memory=4g --ulimit nofile=65536:65536 -e LISTEN_ADDR="$private_ip:8081" -v "$PWD/mock-server:/mock:ro" alpine@sha256:5291449c3df73caf6ed85e649dec1b9e818b39a5d8c871e97afc13e9cd5e8fa8 /mock
docker inspect mock > backend-inspect.json
