#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
curl -fsSL https://github.com/fortio/fortio/releases/download/v1.75.3/fortio-linux_amd64-1.75.3.tgz -o fortio.tgz
tar -xzf fortio.tgz
install usr/bin/fortio /usr/local/bin/fortio
fortio version > fortio-version.txt
sha256sum /usr/local/bin/fortio > fortio-sha256.txt
docker pull envoyproxy/nighthawk-dev@sha256:eb19429cce1486360bab7af3b6edff87a0553b5daf17d861c0326cb07d6e6198
docker image inspect envoyproxy/nighthawk-dev@sha256:eb19429cce1486360bab7af3b6edff87a0553b5daf17d861c0326cb07d6e6198 > nighthawk-image.json
docker run --rm --entrypoint /usr/local/bin/nighthawk_client envoyproxy/nighthawk-dev@sha256:eb19429cce1486360bab7af3b6edff87a0553b5daf17d861c0326cb07d6e6198 --help > nighthawk-help.txt 2>&1 || true
/opt/gateway-benchmark/venv/bin/aiperf profile --help > aiperf-help.txt
