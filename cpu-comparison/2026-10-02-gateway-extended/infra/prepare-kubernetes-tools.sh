#!/bin/bash
set -euo pipefail
cd /opt/gateway-benchmark
export DEBIAN_FRONTEND=noninteractive
apt-get install -y -qq docker.io
mkdir -p /etc/docker
cat > /etc/docker/daemon.json <<'EOF'
{"default-ulimits":{"nofile":{"Name":"nofile","Soft":65536,"Hard":65536}},"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}
EOF
systemctl enable --now docker
systemctl restart docker
curl --retry 3 -fsSL https://get.helm.sh/helm-v4.3.0-linux-amd64.tar.gz -o helm.tar.gz
curl --retry 3 -fsSL https://get.helm.sh/helm-v4.3.0-linux-amd64.tar.gz.sha256sum -o helm.sha256
printf '%s  helm.tar.gz\n' "$(awk '{print $1}' helm.sha256)" | sha256sum -c -
tar -xzf helm.tar.gz
install linux-amd64/helm /usr/local/bin/helm
helm version > helm-version.txt
retry_pull() {
 for attempt in 1 2 3 4; do
  if "$@"; then return 0; fi
  sleep 10
 done
 return 1
}
retry_pull helm pull oci://cr.agentgateway.dev/charts/agentgateway-crds --version v1.6.0 >> helm-crds-pull.log 2>&1
retry_pull helm pull oci://cr.agentgateway.dev/charts/agentgateway --version v1.6.0 >> helm-controller-pull.log 2>&1
sha256sum agentgateway*.tgz > chart-sha256.txt
curl --retry 3 -fsSL https://raw.githubusercontent.com/metallb/metallb/v0.16.1/config/manifests/metallb-native.yaml -o metallb-native.yaml
sha256sum metallb-native.yaml > metallb-sha256.txt
