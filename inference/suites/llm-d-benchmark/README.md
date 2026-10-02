# llm-d-benchmark suite adapter

This directory contains the scenario overlays, workload profiles, renderers,
and tests used by `inference/run-benchmark.sh` when
`BENCHMARK_SUITE=llm-d-benchmark`.

Execution and report rendering are intentionally separate. Suite scripts
capture native evidence and standardized Benchmark Report v0.2 stages;
`inference/reporting` turns completed treatments into comparison
reports.

## Praxis candidate

The experimental [`praxis-standalone` treatment](PRAXIS.md) uses a pinned custom
Praxis AI build with `full,llmd-ext-proc`. Read the build and EPP lifecycle
qualification requirements before running it; the released default image does
not include this integration. No benchmark results are implied by rendering a
valid deployment.
