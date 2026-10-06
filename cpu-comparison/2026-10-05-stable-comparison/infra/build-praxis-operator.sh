#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
mkdir -p praxis-operator-source
tar -xzf /tmp/praxis-operator-source.tar.gz -C praxis-operator-source
cd praxis-operator-source
# Equivalent file permissions for Ubuntu Docker's classic builder; no product code changes.
sed -e 's/ --chmod=0555//' -e '/^USER operator:operator/i RUN chmod 0555 /usr/local/bin/praxis-operator' Containerfile > Containerfile.compat
if [ -f ../praxis-operator-build.log ]; then mv ../praxis-operator-build.log ../praxis-operator-build-original.log; fi
docker build -f Containerfile.compat -t praxis-operator:fb8beaa --label org.opencontainers.image.revision=fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c . > ../praxis-operator-build.log 2>&1
docker image inspect praxis-operator:fb8beaa > ../praxis-operator-image.json
docker save praxis-operator:fb8beaa -o ../praxis-operator-image.tar
chmod 644 ../praxis-operator-image.tar
touch ../praxis-operator-build-complete
