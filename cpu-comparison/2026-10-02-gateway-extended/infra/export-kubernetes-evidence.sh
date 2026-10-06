#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/.." && pwd)
mkdir -p "$root/evidence/hosts"
for role in kclient kcontrol kcontroller kgateway kbackend; do
 # Invoke only while all Kubernetes benchmark jobs are idle.
 gcloud compute ssh "gwext-1002-$role" --project solo-oss --zone us-central1-a --command="sudo systemctl stop benchmark-collector && sudo tar -C /opt/gateway-benchmark --exclude=venv --exclude=usr --exclude=public-tools --exclude=gateway-api --exclude=praxis-operator-source --exclude=linux-amd64 --exclude=fixture --exclude='*.tgz' --exclude='*.tar' --exclude='*.tar.gz' --exclude=k3s --exclude=./clusterloader2 --exclude=gateway-conformance.test --exclude=python-install.log -czf /tmp/$role-evidence.tar.gz . && sudo chmod 644 /tmp/$role-evidence.tar.gz && sudo systemd-run --unit=benchmark-collector --property=RuntimeMaxSec=44000 /usr/bin/python3 /opt/gateway-benchmark/collect-host.py --runtime cri"
 gcloud compute scp "gwext-1002-$role:/tmp/$role-evidence.tar.gz" "$root/evidence/hosts/$role.tar.gz" --project solo-oss --zone us-central1-a --quiet
done
python3 "$root/harness/sanitize-evidence.py" --root "$root/evidence/hosts" --ledger "$root/evidence/credential-redactions.json"
