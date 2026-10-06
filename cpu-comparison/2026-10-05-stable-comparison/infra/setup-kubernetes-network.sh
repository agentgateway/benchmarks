#!/bin/bash
# Uniform host and pod TCP profile; no product configuration changes.
set -euo pipefail
base=/opt/gateway-benchmark/network-profile
mkdir -p "$base"
bash /tmp/setup-ai-network.sh
cd "$base"
curl --retry 3 -fsSL https://github.com/containernetworking/plugins/releases/download/v1.8.0/cni-plugins-linux-amd64-v1.8.0.tgz -o cni-plugins.tgz
printf '%s  cni-plugins.tgz\n' ab3bda535f9d90766cccc90d3dddb5482003dd744d7f22bcf98186bf8eea8be6 | sha256sum -c -
tar -xzf cni-plugins.tgz ./tuning
install -m 755 tuning /var/lib/rancher/k3s/data/cni/tuning
sha256sum tuning cni-plugins.tgz > cni-sha256.txt
cp /var/lib/rancher/k3s/agent/etc/cni/net.d/10-flannel.conflist cni-before.json
python3 - <<'PY'
import json
from pathlib import Path
p=Path('/var/lib/rancher/k3s/agent/etc/cni/net.d/10-flannel.conflist')
v=json.loads(p.read_text());assert not any(x['type']=='tuning' for x in v['plugins'])
v['plugins'].append({'type':'tuning','sysctl':{'net.ipv4.ip_local_port_range':'10240 65535','net.ipv4.tcp_tw_reuse':'1','net.ipv4.tcp_tw_reuse_delay':'1000','net.ipv4.tcp_timestamps':'1'}})
p.write_text(json.dumps(v,indent=2)+'\n')
PY
cp /var/lib/rancher/k3s/agent/etc/cni/net.d/10-flannel.conflist cni-after.json
date -u +%FT%TZ > configured-at.txt
