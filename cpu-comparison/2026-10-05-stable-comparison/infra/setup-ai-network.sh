#!/bin/bash
set -euo pipefail
# Identical on client, gateway, backend. No reserved-port changes.
mkdir -p /opt/gateway-benchmark/network-profile
sysctl net.ipv4.ip_local_port_range net.ipv4.ip_local_reserved_ports net.ipv4.tcp_tw_reuse net.ipv4.tcp_tw_reuse_delay net.ipv4.tcp_timestamps > /opt/gateway-benchmark/network-profile/before.txt
cat > /etc/sysctl.d/90-ai-benchmark.conf <<'SYSCTL'
net.ipv4.ip_local_port_range = 10240 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_tw_reuse_delay = 1000
net.ipv4.tcp_timestamps = 1
SYSCTL
sysctl -p /etc/sysctl.d/90-ai-benchmark.conf
sysctl net.ipv4.ip_local_port_range net.ipv4.ip_local_reserved_ports net.ipv4.tcp_tw_reuse net.ipv4.tcp_tw_reuse_delay net.ipv4.tcp_timestamps > /opt/gateway-benchmark/network-profile/after.txt
