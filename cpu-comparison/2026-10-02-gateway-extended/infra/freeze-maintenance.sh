#!/bin/bash
# Disposable campaign VMs only. Avoid package-triggered service restarts in a run.
set -euo pipefail
systemctl mask --now apt-daily.timer apt-daily-upgrade.timer
cat >/etc/apt/apt.conf.d/99-benchmark-freeze <<'EOF'
APT::Periodic::Enable "0";
APT::Periodic::Update-Package-Lists "0";
APT::Periodic::Unattended-Upgrade "0";
EOF
# Never interrupt dpkg or an in-flight update. Let it complete before measuring.
for i in $(seq 1 60); do
 if ! systemctl is-active --quiet apt-daily.service && ! systemctl is-active --quiet apt-daily-upgrade.service; then break; fi
 sleep 5
done
! systemctl is-active --quiet apt-daily.service
! systemctl is-active --quiet apt-daily-upgrade.service
systemctl is-enabled apt-daily.timer apt-daily-upgrade.timer || true
systemctl show k3s -p MainPID -p ActiveEnterTimestamp
uname -a
dpkg-query -W libc6 libssl3t64 libexpat1 systemd python3
