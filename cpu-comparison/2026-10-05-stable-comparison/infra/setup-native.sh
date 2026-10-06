#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
AI=ghcr.io/praxis-proxy/ai@sha256:5121c638ee4b2c4dd9184c403b11d9384cd1ea26c1542085d2953a74bb15b4f8
AGW=ghcr.io/agentgateway/agentgateway@sha256:9d3e6044ddcdc0878b1787f77bd401252b95e22684203fb5e874c4c42d2ed90c
docker pull "$AI"
docker create --no-healthcheck --name praxis-ai --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/praxis-native.yaml:/etc/config.yaml:ro" "$AI" -c /etc/config.yaml
docker create --no-healthcheck --name agentgateway-native -e AGENTGATEWAY_MESSAGES_PREFER_COMPLETIONS=true --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/agentgateway-native.yaml:/etc/config.yaml:ro" "$AGW" -f /etc/config.yaml
docker inspect agentgateway-native praxis-ai > native-gateway-inspect.json
docker image inspect "$AI" "$AGW" > native-image-inspect.json

AI_NIGHTLY=ghcr.io/praxis-proxy/ai@sha256:727c4cb043af573cfb812208475dc6b290570b72ff01d07c6b7ca85dc09155e4
docker pull "$AI_NIGHTLY"
docker create --no-healthcheck --name praxis-ai-nightly --network=host --cpuset-cpus=2,3 --cpus=2 --memory=2g --ulimit nofile=65536:65536 -v "$PWD/praxis-native.yaml:/etc/config.yaml:ro" "$AI_NIGHTLY" -c /etc/config.yaml
docker inspect praxis-ai-nightly > native-nightly-gateway-inspect.json
docker image inspect "$AI_NIGHTLY" > native-nightly-image-inspect.json
