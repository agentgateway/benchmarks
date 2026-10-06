#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .work
# Only task-created VMs; no service accounts or IAM grants.
for role in client gateway backend; do
 gcloud compute instances create "gwcmp160-1005-$role" \
  --project=solo-oss --zone=us-central1-a --machine-type=n2-standard-8 --min-cpu-platform="Intel Cascade Lake" \
  --image=ubuntu-2404-noble-amd64-v20260918 --image-project=ubuntu-os-cloud \
  --boot-disk-size=100GB --boot-disk-type=pd-balanced \
  --no-service-account --no-scopes --tags=gwcmp160-1005 \
  --labels=campaign=gwcmp160-1005,purpose=gateway-benchmark \
  --max-run-duration=12h --instance-termination-action=DELETE \
  --metadata-from-file=startup-script=infra/startup.sh --format=json > ".work/create-$role.json"
done
