# Recorded execution helpers

These preserve the initial host layout, paths and resource names. They are provenance, not a portable one-command installer. Follow `../REPRODUCE.md` to adapt the environment and inspect the pinned campaign patch.

The direct traffic driver stopped after its 512-connection attempt lacked `fortio.json`. The paired 12-case traffic command at its end was then launched separately as `agw-gateway-traffic-2`; the baseline was not repeated. The lifecycle driver waited for all 12 paired attempts, including failures, before starting. The raw bundle contains logs, result plans and final systemd unit definitions.

The first kubelet collector invocation lacked KUBECONFIG and recorded connection errors. The corrected invocation set KUBECONFIG explicitly and appended valid samples. Error rows are retained and counted by `resources.py`. The scale observer was restarted to add Deployment/pod/ConfigMap snapshots; existing five/nine-minute route checkpoints were not overwritten. Both 5,000-route cases used the expanded snapshot capture.

The conformance helper is the final invocation with explicit common features and a namespace-deletion barrier. Earlier attempts are retained and explained in the conformance report. The raw organization string says `Solo.io (independent evaluation)`; this means separately executed by Solo.io, not independent third-party certification.

The recorded shell helpers pass syntax checks and ShellCheck with SC1091 (external `/tmp/gateway.env`) and SC2034 (deliberately unused readiness-loop counter) excluded. The unchanged source scripts are preserved rather than rewritten to hide those historical lint findings.
