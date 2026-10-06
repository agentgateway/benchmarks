# Agentgateway v1.6.0 and Praxis: three-pass CPU comparison

Solo.io conducted this comparison and contributes to agentgateway. These results
are not an independent certification. Every completed workload uses three
repetitions, with arithmetic means, individual runs and ranges retained.

| Workload | Agentgateway | Praxis distributions | Reference |
| --- | --- | --- | --- |
| Standalone HTTP and AI-protocol forwarding | v1.6.0 | Core v0.5.2 and core nightly-20261002 | Direct deterministic service |
| Native AI protocols, translation and streaming | v1.6.0 | AI v0.5.0 and AI October 2 nightly | Direct deterministic service |
| Kubernetes HTTP, route lifecycle and graceful recovery | Controller/data plane v1.6.0 | Core v0.5.2 with operator fb8beaa | Direct service; stock nightly pairing setup-blocked |

Praxis AI is a separate distribution. Its release uses core libraries 0.7.2.
Its October 2 nightly is pinned through the successful scheduled publishing
workflow and immutable SHA-tag digest, not the core project's dated tag.
[Version pins](evidence/versions/selection.json) identify every image.

## Choose the question

1. [Agentgateway versus direct service](reports/01-agentgateway-vs-direct.md).
2. [Praxis versus agentgateway](reports/02-praxis-vs-agentgateway.md).
3. [Gateway API coverage and lifecycle](reports/03-gateway-api.md).
4. [Source-supported feature differences](reports/04-feature-comparison.md) and
   [requirement-level evidence](reports/requirements-index.md).
5. [Methods, exclusions and validity](reports/05-methodology-and-validity.md).
6. [CPU, memory and descriptor observations](reports/08-resource-usage.md).

The full matrices retain all fixed-rate, unrestricted-rate and streaming cases:
[HTTP forwarding](reports/matrices/common-http.md),
[AI-protocol forwarding](reports/matrices/common-ai.md),
[native AI](reports/matrices/native-ai.md), and
[Kubernetes HTTP](reports/matrices/kubernetes-http.md).

## Scope and interpretation

The campaign uses native Google Compute Engine VMs. Client, gateway and backend
occupy separate machines. Kubernetes uses five dedicated K3s nodes and private
NodePort traffic. No Envoy proxy, GKE cluster or managed GCP load balancer is in
the measured path. Nighthawk is a load client from the Envoy project.

Common forwarding does not apply native AI transformations or accounting.
Native profiles perform different routing/accounting work, so their throughput
ratios do not establish equal-work CPU efficiency. The paced streaming service
is synthetic: there is no model inference, GPU utilization or model-quality
result. Three repeats on one placement describe repeatability, not a cloud-wide
confidence interval. Direct service is the observed reference path and can itself
approach its client or backend capacity.

The [retained extended conformance campaign](../2026-10-02-gateway-extended/README.md)
uses conformance v1.5.1. The current focused static-address test uses v1.6.1.
They remain separate evidence families; no corrected 107/107 score is fabricated.
Stock operator/core nightly setup failures mean dependent Kubernetes cases are
not evaluated, while standalone core nightly and the separate AI nightly have
measured results.

## Reproduce or audit

Start with the [public evidence guide](docs/PUBLIC-EVIDENCE.md),
[reproduction instructions](docs/REPRODUCE.md), and
[reading guide](docs/READING-RESULTS.md). Exact commands, fixtures, image/source
pins, excluded-attempt explanations and manual review records accompany the
results. Do not treat parser success as scientific approval for a fresh run.

[Offline reanalysis](evidence/reanalysis.json) reproduced all 24 numeric data and report files byte-for-byte from the sanitized public archive; both host-resource summaries matched as JSON values.

Download the [checksum-verified public raw evidence](https://github.com/danehans/agentgateway-benchmarks/releases/tag/cpu-2026-10-05-v1.6.0). The [publication record](evidence/PUBLICATION.json) lists asset hashes and the reviewed source commit.
