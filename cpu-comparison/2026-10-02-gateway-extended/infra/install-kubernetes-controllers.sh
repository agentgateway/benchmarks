#!/bin/bash
set -euo pipefail
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml
cd /opt/gateway-benchmark
curl --retry 3 -fsSL https://github.com/kubernetes-sigs/gateway-api/archive/e7677b70ae75d14a4448fba94870e7deea6cf0ad.tar.gz -o gateway-api.tar.gz
mkdir -p gateway-api
tar -xzf gateway-api.tar.gz --strip-components=1 -C gateway-api
kubectl apply --server-side -k gateway-api/config/crd/experimental
kubectl apply -f metallb-native.yaml
# Only the IP-allocation controller is needed for cluster-internal conformance.
# Packets use normal kube-proxy Service rules; no L2/BGP announcement is configured.
kubectl delete daemonset speaker -n metallb-system --ignore-not-found
kubectl patch deployment controller -n metallb-system --type=merge --patch-file=configs/kubernetes/metallb-controller-patch.json
kubectl rollout status deployment/controller -n metallb-system --timeout=180s
kubectl apply -f configs/kubernetes/metallb-pool.yaml
helm upgrade --install agentgateway-crds agentgateway-crds-*.tgz --namespace agentgateway-system --create-namespace --wait
kubectl apply --server-side -f configs/kubernetes/agentgateway-parameters.yaml
helm upgrade --install agentgateway agentgateway-v1.6.0.tgz --namespace agentgateway-system --wait -f configs/kubernetes/agentgateway-values.yaml
kubectl apply -f configs/kubernetes/backend.yaml
kubectl apply -f praxis-operator-source/deploy/rbac.yaml
kubectl apply -f configs/kubernetes/praxis-operator.yaml
kubectl apply -f praxis-operator-source/deploy/gatewayclass.yaml
kubectl get nodes,pods -A -o wide
