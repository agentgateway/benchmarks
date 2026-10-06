#!/bin/bash
# Bound dead SYN attempts below the upstream suite's 30-second consistency window.
# This changes the shared client OS only; gateway images and suite assertions stay fixed.
set -euo pipefail
out=/opt/gateway-benchmark/qualification/tcp-client
mkdir -p "$out"
sysctl net.ipv4.tcp_syn_retries net.ipv4.tcp_syn_linear_timeouts > "$out/before.txt"
printf 'net.ipv4.tcp_syn_retries = 2\n' > /etc/sysctl.d/99-gateway-conformance-client.conf
sysctl -p /etc/sysctl.d/99-gateway-conformance-client.conf
sysctl net.ipv4.tcp_syn_retries net.ipv4.tcp_syn_linear_timeouts > "$out/after.txt"
date -u +%FT%TZ > "$out/changed-at.txt"
