# Evidence layout and interpretation

This public snapshot contains technical review records and generated tables. The
[public evidence guide](PUBLIC-EVIDENCE.md) describes the accepted measurement
subset, configurations, lifecycle diagnostics and host telemetry. Its archive
manifest must match the reviewed local artifact; upload alone is not validation.

## Finding a number

1. Choose the campaign and exact distribution in `evidence/versions/selection.json`.
2. Choose common forwarding, native AI, or Kubernetes HTTP. Resource limits and
   responsibilities differ, so do not merge their rows.
3. Find the table cell in `reports/matrices/`. Each cell uses all three accepted
   repetitions, with mean and range. The report generator rejects incomplete sets.
4. Look up that case in `reports/data/load-rows.json`. It records treatment,
   repetition, timestamps, process exits, metrics and the raw artifact path.
5. Open the matching exported `execution.json` for the precise command and
   `result.json` or AIPerf export for the original measurement. Warmup files are
   separate and are not additional repetitions.
6. Review the corresponding host window and first-pass/final validity decisions.
   A successful parser or process is not proof of a valid comparison.

## Directory map

| Path | Meaning |
| --- | --- |
| `evidence/versions/` | Product/source/tool pins and installed input hashes |
| `evidence/qualification/` | Qualification facts, exclusions and explicit review gates |
| `evidence/diagnostics/` | Focused failure evidence; excluded observations are labeled |
| Exported `client/results/common/passN/` | Accepted standalone matched forwarding cases |
| Exported `client/results/native/passN/` | Accepted native-AI cases |
| Exported `kclient/results/kubernetes/passN/` | Accepted Kubernetes HTTP, scale, recovery or setup-block evidence |
| Exported `kclient/results/static-address/passN/` | Separate corrected-suite static-address follow-up |
| Exported `*/host-samples.jsonl` | Timestamped host/process/cgroup and, for Kubernetes, pod-network observations |
| `reports/data/` | Deterministic summaries of reviewed raw evidence |

## What a blank or unavailable cell means

- **Not evaluated:** a prerequisite did not work or that distribution/workload was
  not selected. It is not a zero and does not count as a failed individual test.
- **Not available:** the requested image tag was absent from the registry at the
  recorded check. A differently dated nightly is not substituted silently.
- **Did not converge:** the route observer's bounded window ended without full
  current-generation status plus all-route traffic verification. Report the
  observed counts and failure mechanism, not a fabricated latency.
- **No failures observed:** the probes saw none in the stated window. This does
  not imply zero production downtime or resilience against every failure mode.
- **Source-supported:** pinned code/docs describe a capability. No runtime or
  performance pass is implied unless linked evidence exercised it.

## Publication and credentials

Export only selected benchmark files. Never archive `/etc/rancher`, SSH keys,
local join tokens, kubeconfigs or container stores. ClusterLoader2 may print
credential fields even when those files are excluded, so sanitize retained logs
and maintain before/after member hashes. Redact generated fixture private keys
as well. Do not modify measurements during sanitization. Publish the sanitized
archive hashes, verify GitHub asset digests, and preserve the exact code commit.
The technical snapshot and its evidence release are public. Internal strategy
and cloud-administration inventories remain outside this public subset.


In native-profile raw paths, `praxis` means Praxis AI v0.5.0 and
`praxis-ai-nightly` means the October 2 AI build. In common/Kubernetes paths,
`praxis-release` and `praxis-nightly` mean the two core images. Reports expand
these internal keys into full distribution/version labels.

The public manifest identifies the accepted subset, rather than every intermediate
administrative or qualification snapshot. Accepted first-pass measurement files
were compared byte-for-byte with final exports before credential redaction, with
retained per-file continuity records. Exclusion decisions are in the technical
review files; earlier current-campaign pilot tool-result directories remain in
the internal full archive and are not inputs to accepted aggregates.
