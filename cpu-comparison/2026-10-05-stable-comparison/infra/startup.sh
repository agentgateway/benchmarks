#!/bin/bash
set -euo pipefail
exec > >(tee -a /var/log/gateway-benchmark-startup.log) 2>&1
export DEBIAN_FRONTEND=noninteractive
systemctl mask --now apt-daily.timer apt-daily-upgrade.timer
while systemctl is-active --quiet apt-daily.service || systemctl is-active --quiet apt-daily-upgrade.service; do sleep 5; done
printf '%s\n' 'APT::Periodic::Enable "0";' 'APT::Periodic::Unattended-Upgrade "0";' > /etc/apt/apt.conf.d/99-benchmark-freeze
apt-get update -qq
apt-get install -y -qq docker.io python3-venv python3-pip curl jq git ca-certificates sysstat
install -d /etc/docker /opt/gateway-benchmark
cat > /etc/docker/daemon.json <<'JSON'
{"default-ulimits":{"nofile":{"Name":"nofile","Soft":65536,"Hard":65536}},"log-driver":"json-file","log-opts":{"max-size":"10m","max-file":"3"}}
JSON
systemctl enable docker
systemctl restart docker
curl -fsSL https://go.dev/dl/go1.27.1.linux-amd64.tar.gz -o /tmp/go.tgz
tar -C /usr/local -xzf /tmp/go.tgz
ln -sf /usr/local/go/bin/go /usr/local/bin/go
python3 -m venv /opt/gateway-benchmark/venv
/opt/gateway-benchmark/venv/bin/pip install 'aiperf==0.13.0' 'httpx==0.28.1' > /opt/gateway-benchmark/python-install.log 2>&1
lscpu --json > /opt/gateway-benchmark/cpu.json
lscpu -e > /opt/gateway-benchmark/cpu-topology.txt
uname -a > /opt/gateway-benchmark/kernel.txt
/opt/gateway-benchmark/venv/bin/pip freeze > /opt/gateway-benchmark/python-lock.txt
touch /opt/gateway-benchmark/ready
