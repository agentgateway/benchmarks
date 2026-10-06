#!/bin/bash
set -euo pipefail
exec > >(tee -a /var/log/gateway-benchmark-startup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
# Freeze automatic package maintenance before provisioning the disposable host.
systemctl mask --now apt-daily.timer apt-daily-upgrade.timer
cat >/etc/apt/apt.conf.d/99-benchmark-freeze <<'EOF'
APT::Periodic::Enable "0";
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
EOF
for i in $(seq 1 60); do
 if ! systemctl is-active --quiet apt-daily.service && ! systemctl is-active --quiet apt-daily-upgrade.service; then break; fi
 sleep 5
done
! systemctl is-active --quiet apt-daily.service
! systemctl is-active --quiet apt-daily-upgrade.service
apt-get -o Acquire::Retries=3 -o Acquire::http::Timeout=30 update -qq
apt-get install -y -qq curl ca-certificates jq python3-venv git sysstat
mkdir -p /opt/gateway-benchmark /etc/rancher/k3s
cd /opt/gateway-benchmark
curl --retry 5 -fsSL 'https://github.com/k3s-io/k3s/releases/download/v1.35.8+k3s1/k3s' -o k3s
curl --retry 5 -fsSL 'https://github.com/k3s-io/k3s/releases/download/v1.35.8+k3s1/sha256sum-amd64.txt' -o k3s-checksums.txt
awk '$2 == "k3s" {print}' k3s-checksums.txt | sha256sum -c -
install k3s /usr/local/bin/k3s
ln -sf /usr/local/bin/k3s /usr/local/bin/kubectl
ln -sf /usr/local/bin/k3s /usr/local/bin/crictl
lscpu --json > cpu.json
lscpu -e > cpu-topology.txt
uname -a > kernel.txt
python3 -m venv /opt/gateway-benchmark/venv
/opt/gateway-benchmark/venv/bin/pip install httpx==0.28.1 > python-install.log 2>&1
touch ready
