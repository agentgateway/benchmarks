#!/bin/bash
set -euo pipefail
role="$1"
control_ip="${2:-}"
private_ip=$(hostname -I | awk '{print $1}')
test -f /opt/gateway-benchmark/ready
modprobe overlay
modprobe br_netfilter
sysctl -w net.ipv4.ip_forward=1 net.bridge.bridge-nf-call-iptables=1
mkdir -p /etc/rancher/k3s
cat > /etc/rancher/k3s/config.yaml <<EOF
node-ip: "$private_ip"
node-label:
- "benchmark-role=$role"
kubelet-arg:
- "max-pods=200"
EOF
if [ "$role" = kcontrol ]; then
 cat >> /etc/rancher/k3s/config.yaml <<EOF
write-kubeconfig-mode: "0600"
advertise-address: "$private_ip"
tls-san:
- "$private_ip"
disable:
- traefik
- servicelb
- metrics-server
- local-storage
disable-network-policy: true
node-taint:
- "CriticalAddonsOnly=true:NoExecute"
EOF
 mode=server
else
 test -n "$control_ip"
 install -m 600 /tmp/k3s-token /etc/rancher/k3s/join-token
 rm /tmp/k3s-token
 cat >> /etc/rancher/k3s/config.yaml <<EOF
server: "https://$control_ip:6443"
token-file: "/etc/rancher/k3s/join-token"
EOF
 if [ "$role" != kgateway ]; then
  printf 'node-taint:\n- "benchmark-role=%s:NoSchedule"\n' "$role" >> /etc/rancher/k3s/config.yaml
 fi
 mode=agent
fi
cat > /etc/systemd/system/k3s.service <<EOF
[Unit]
Description=Temporary native GCE benchmark Kubernetes
After=network-online.target
Wants=network-online.target
[Service]
Type=notify
ExecStart=/usr/local/bin/k3s $mode
Restart=on-failure
RestartSec=5
LimitNOFILE=1048576
LimitNPROC=infinity
TasksMax=infinity
Delegate=yes
KillMode=process
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now k3s
