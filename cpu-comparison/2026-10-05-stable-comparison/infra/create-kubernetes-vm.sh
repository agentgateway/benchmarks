#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/.."
role="$1"
case "$role" in kcontrol|kcontroller|kgateway|kbackend|kclient) ;; *) exit 2;; esac
mkdir -p .work
gcloud compute instances create "gwcmp160-1005-$role" \
 --project=solo-oss --zone=us-central1-a --machine-type=n2-standard-8 --min-cpu-platform="Intel Cascade Lake" \
 --image=ubuntu-2404-noble-amd64-v20260918 --image-project=ubuntu-os-cloud \
 --boot-disk-size=100GB --boot-disk-type=pd-balanced \
 --no-service-account --no-scopes --tags=gwcmp160-1005 \
 --labels=campaign=gwcmp160-1005,purpose=gateway-benchmark \
 --max-run-duration=12h --instance-termination-action=DELETE \
 --metadata-from-file=startup-script=infra/kubernetes-startup.sh \
 --format='json(name,id,creationTimestamp,machineType,cpuPlatform,networkInterfaces,scheduling,disks,labels)' > ".work/create-$role.json"
