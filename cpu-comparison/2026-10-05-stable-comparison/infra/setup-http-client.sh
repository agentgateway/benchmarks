#!/bin/bash
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq docker.io
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{"default-ulimits":{"nofile":{"Name":"nofile","Soft":65536,"Hard":65536}},"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}
EOF
systemctl enable --now docker
systemctl restart docker
cd /opt/gateway-benchmark
curl --retry 3 -fsSL https://github.com/fortio/fortio/releases/download/v1.75.3/fortio-linux_amd64-1.75.3.tgz -o fortio.tgz
tar -xzf fortio.tgz
install usr/bin/fortio /usr/local/bin/fortio
fortio version > fortio-version.txt
sha256sum /usr/local/bin/fortio > fortio-sha256.txt
NH=envoyproxy/nighthawk-dev@sha256:eb19429cce1486360bab7af3b6edff87a0553b5daf17d861c0326cb07d6e6198
docker pull "$NH"
docker image inspect "$NH" > nighthawk-image.json
docker run --rm --entrypoint /usr/local/bin/nighthawk_client "$NH" --help > nighthawk-help.txt 2>&1 || test "$?" -eq 0
for file in clusterloader2 gateway-conformance.test; do
 curl --retry 3 -fsSL "http://10.128.15.217:8089/$file" -o "$file"
 chmod +x "$file"
done
sha256sum clusterloader2 gateway-conformance.test > tool-sha256.txt
bash /opt/gateway-benchmark/infra/configure-tcp-client.sh
touch http-client-ready
