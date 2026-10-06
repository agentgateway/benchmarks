#!/bin/bash
# Read-only lifecycle evidence; does not change any measured workload or resource.
set -uo pipefail
export KUBECONFIG=/etc/rancher/k3s/benchmark.kubeconfig
out="$1"
namespace="$2"
mkdir "$out" || exit 1
kubectl get pods,deployments,events -n "$namespace" -o json > "$out/resources.json"
for pod in $(kubectl get pods -n "$namespace" -o name); do
 name="${pod#pod/}"
 kubectl logs -n "$namespace" "$pod" --tail=150 > "$out/$name.log" 2>&1 || true
 kubectl logs -n "$namespace" "$pod" --previous --tail=150 > "$out/$name-previous.log" 2>&1 || true
done
date -u +%FT%TZ > "$out/captured-at.txt"
