# Public technical evidence

This directory contains the source, configured workload definitions, review
records and generated results. The companion evidence release supplies
`accepted-results.tar.gz` and `extended-gateway-api-results.tar.gz`, separate
manifests and credential-redaction ledgers, and `SHA256SUMS`. The verified release
link is available in the [publication record](../evidence/PUBLICATION.json).

[Download the verified evidence release](https://github.com/danehans/agentgateway-benchmarks/releases/tag/cpu-2026-10-05-v1.6.0). Both archives have
been regenerated offline: current numeric reports match byte-for-byte, as do the
historical conformance JSON files and matrices.

The current archive contains all accepted CPU/Kubernetes passes, exact gateway
configurations, host/process resource samples and retained route-scale failure
diagnostics. It excludes cloud-administration inventories, internal strategy,
SSH keys, kubeconfig files and join tokens. Credential fields printed by tools
are redacted with before/after member hashes. Publication is a technical subset;
review records describe the excluded qualification/pilot attempts separately.

After downloading release assets and checking `sha256sum -c SHA256SUMS`, extract
the current archive into `.work/public-analysis`. Its top-level directories are
`client`, `gateway`, `backend`, `kclient`, `kgateway`, `kbackend`, `kcontroller`,
and `kcontrol`. Per-run paths in `reports/data/load-rows.json` are relative to
that analysis root. Do not mix intermediate exports or historical campaigns into
this root.

```sh
mkdir -p .work/public-analysis
tar -xzf /path/to/accepted-results.tar.gz -C .work/public-analysis
python3 harness/summarize-load.py .work/public-analysis --output reports/data
python3 harness/summarize-control.py .work/public-analysis/kclient --output reports/data
python3 harness/summarize-hosts.py .work/public-analysis \
  --output reports/data/cpu-host-workloads.json
python3 harness/summarize-hosts.py .work/public-analysis --suite gateway \
  --output reports/data/kubernetes-host-workloads.json
python3 harness/review-kubernetes-attribution.py .work/public-analysis \
  --output evidence/qualification/final-facts/kubernetes-attribution.json
python3 harness/audit-recovery-overlap.py .work/public-analysis \
  --output evidence/qualification/final-facts/recovery-overlap.json
python3 harness/render-load-reports.py reports/data --output reports \
  --review evidence/qualification/final-review.json
python3 harness/render-control-report.py reports/data \
  --output reports/03-gateway-api.md --review evidence/qualification/final-review.json
python3 harness/render-resource-report.py reports/data \
  --cpu-hosts reports/data/cpu-host-workloads.json \
  --kubernetes-hosts reports/data/kubernetes-host-workloads.json \
  --output reports --review evidence/qualification/final-review.json
python3 harness/summarize-claims.py reports/data \
  --review evidence/qualification/final-review.json
```

Install the separate plotting dependencies from `docs/analysis-requirements.txt`
to run `harness/plot-load.py`. The retained review guard establishes the reviewed
campaign's provenance; copying it to a fresh campaign would not validate new
measurements. Attribution assertions intentionally require reconsideration when
observed behavior changes.

The infrastructure scripts reproduce the original setup and administration
workflow, including private full-archive publication. Public readers should use
this guide for the accepted subset. A fresh cloud run needs a new project/prefix,
credentials, qualification, budget and cleanup, as described in
[the reproduction guide](REPRODUCE.md). Recorded project addresses are historical
fixture values; do not send traffic to them.
