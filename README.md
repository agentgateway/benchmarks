# Benchmarks

Community benchmarks for [agentgateway](https://github.com/agentgateway/agentgateway).

This repo holds the tooling and published results for measuring how agentgateway
performs as an AI proxy, Kubernetes Gateway API implementation and inference gateway. CPU-only AI proxy tests use a
deterministic backend; inference tests compare EPP integration against a plain
Kubernetes Service. These workloads answer different questions.

## Layout

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

## Quick start

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

## Current results

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
