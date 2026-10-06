#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
docker pull ghcr.io/agentgateway/agentgateway@sha256:9d3e6044ddcdc0878b1787f77bd401252b95e22684203fb5e874c4c42d2ed90c
docker create --no-healthcheck --name agentgateway --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/agentgateway.yaml:/etc/config.yaml:ro" ghcr.io/agentgateway/agentgateway@sha256:9d3e6044ddcdc0878b1787f77bd401252b95e22684203fb5e874c4c42d2ed90c -f /etc/config.yaml
docker pull ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8
docker create --no-healthcheck --name praxis-release --entrypoint praxis --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/praxis.yaml:/etc/config.yaml:ro" ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8 -c /etc/config.yaml
docker pull ghcr.io/praxis-proxy/praxis@sha256:be62d256d5ec92aacb1216baba506aac763e2100f9eb361820a5c27c54e17be8
docker create --no-healthcheck --name praxis-nightly --entrypoint praxis --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/praxis.yaml:/etc/config.yaml:ro" ghcr.io/praxis-proxy/praxis@sha256:be62d256d5ec92aacb1216baba506aac763e2100f9eb361820a5c27c54e17be8 -c /etc/config.yaml
docker inspect agentgateway praxis-release praxis-nightly > gateway-inspect.json
