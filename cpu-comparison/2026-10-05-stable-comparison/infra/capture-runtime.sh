#!/bin/bash
# Read-only environment inventory; run after a phase before exporting it.
set -uo pipefail
out=/opt/gateway-benchmark/runtime-inventory
mkdir -p "$out"
date -u +%FT%TZ > "$out/captured-at.txt"
uname -a > "$out/kernel.txt"
cat /etc/os-release > "$out/os-release.txt"
dpkg-query -W -f='${Package}\t${Version}\n' > "$out/os-packages.txt"
python3 --version > "$out/python-version.txt" 2>&1
/opt/gateway-benchmark/venv/bin/pip freeze > "$out/python-freeze.txt" 2>&1
if command -v docker >/dev/null; then
 timeout 5 docker version --format '{{json .}}' > "$out/docker-version.json" 2> "$out/docker-version.stderr" || true
 # Only the six known benchmark gateway containers, captured after measurement.
 if docker inspect agentgateway >/dev/null 2>&1; then
  docker inspect agentgateway praxis-release praxis-nightly agentgateway-native praxis-ai praxis-ai-nightly > "$out/gateway-container-inspect.json"
 fi
fi
if command -v k3s >/dev/null; then k3s --version > "$out/k3s-version.txt" 2>&1; fi
sysctl net.ipv4.ip_local_port_range net.ipv4.tcp_tw_reuse net.ipv4.tcp_tw_reuse_delay net.ipv4.tcp_timestamps > "$out/host-tcp-profile.txt"
systemctl show apt-daily.timer apt-daily-upgrade.timer -p Id -p LoadState -p ActiveState > "$out/maintenance-timers.txt"
