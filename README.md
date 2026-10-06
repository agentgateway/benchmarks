# Benchmarks

Community benchmarks for [agentgateway](https://github.com/agentgateway/agentgateway).

This repo holds the tooling and published results for measuring how agentgateway
performs as an AI proxy, Kubernetes Gateway API implementation and inference gateway. CPU-only AI proxy tests use a
deterministic backend; inference tests compare EPP integration against a plain
Kubernetes Service. These workloads answer different questions.

## Current CPU comparison: agentgateway v1.6.0 and Praxis

The [three-pass comparison](cpu-comparison/2026-10-05-stable-comparison/README.md)
separates agentgateway versus direct service from Praxis versus agentgateway.
It includes core v0.5.2 and core nightly-20261002 for transport, plus the separate
Praxis AI v0.5.0 and October 2 AI nightly for native AI workloads. It runs on
native GCE VMs with dedicated client/gateway/backend roles, using Fortio,
Nighthawk, AIPerf and ClusterLoader2. Streaming uses a deterministic CPU service;
these are not GPU inference or model-quality results.

The [extended Gateway API evidence](cpu-comparison/2026-10-02-gateway-extended/README.md)
retains every selected upstream case and the original suite version. The newer
campaign adds a separate corrected static-address check and lifecycle evidence.
Read full matrices, exclusions, version pins and source-supported feature
boundaries together; no overall gateway score is implied.

Earlier October 1 results below are historical, single-run experiments with
agentgateway v1.5.0 and different infrastructure. Do not relabel them as v1.6.0
or Praxis nightly measurements.

## Layout

- [`cpu-comparison/`](cpu-comparison/2026-10-05-stable-comparison/README.md) - current
  three-pass CPU comparison and retained extended Gateway API evidence.

- [`ai-gateway/`](ai-gateway/README.md) - native CPU-only protocol qualification
  and Fortio proxy measurements for agentgateway, Praxis AI, and a direct backend.

- [`gateway-api/`](gateway-api/README.md) - shared core HTTP conformance, plain
  HTTP traffic, route lifecycle and scale/churn evidence for agentgateway and Praxis.

- [`inference/`](inference/README.md) - the benchmark runner itself: campaign-based
  execution comparing `service`, `agentgateway-standalone`, and
  `agentgateway-gateway` treatments, with automated GKE provisioning/teardown and
  Markdown/PNG/CSV report generation.
- [`inference/reports/`](inference/reports/README.md) - curated, published benchmark
  results with their campaign manifests and provenance, safe to link to directly.

## Inference quick start

Run the `service` treatment locally on Kind:

```bash
make kind-create
BENCHMARK_TREATMENT=service BENCHMARK_CAMPAIGN_ID=local-sim make benchmark
```

The `service` treatment runs fine on a laptop-sized Kind cluster.
`agentgateway-standalone` and `agentgateway-gateway` currently need more CPU/memory
than most laptops provide for the router pod - see
[#2](https://github.com/agentgateway/benchmarks/issues/2).

See [`inference/README.md`](inference/README.md) for the full set of treatments,
GKE campaign instructions, and configuration reference.

## Historical CPU and other inference results

The [initial CPU AI comparison](ai-gateway/results/2026-10-01-initial/README.md)
and [Gateway API comparison](gateway-api/results/2026-10-01-initial/README.md)
retain direct baselines, separate paired reports and full raw evidence. These
are single-round experiments with workload-specific outcomes and disclosed
failures, not GPU inference results.

The previously published inference campaign
([`optimized-baseline-v0230-gateway-refresh-20260817`](inference/reports/llm-d-benchmark/optimized-baseline-qwen3-32b-h100/optimized-baseline-v0230-gateway-refresh-20260817/README.md))
ran Qwen/Qwen3-32B on 16x H100 GPUs across 8 vLLM model servers. At the top of the
request-rate ladder, agentgateway more than doubles peak throughput and cuts TTFT
p90 by over 99% versus a plain Kubernetes Service doing round-robin, because
round-robin has no way to know which backend pod is already overloaded and
agentgateway's EPP-based routing does.

Automated repository checks (`inference/suites/*/tests`, `inference/reporting/tests`)
cover syntax and unit tests only - they don't provision infrastructure or execute
benchmark campaigns.
