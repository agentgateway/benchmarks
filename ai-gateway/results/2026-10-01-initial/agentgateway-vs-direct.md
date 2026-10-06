# Agentgateway versus direct backend: initial CPU-only results

**Preliminary: one measurement per configuration.** No between-run variance, confidence interval or statistical superiority claim is available. These are deterministic mock-backend proxy tests, not inference/GPU results.

Started: `2026-10-02T01:43:31Z`. Full raw evidence: [raw.tar.gz](raw.tar.gz). No successful or failed requests were removed from the tables.

## Configuration

Recorded Docker host: x86_64, 16 logical CPUs, 62.8 GiB available memory. Platform: `Linux-7.0.0-1011-gcp-x86_64-with-glibc2.39`. Agentgateway configures two workers; Praxis configures two runtime threads per service, with one API listener active per trial. Both receive two selected logical CPUs and a 2 GiB memory limit. Verify physical-core placement against the recorded host topology. Mock and Fortio each use a disjoint two-core CPU set and 2 GiB limit. Inactive gateways are stopped before each trial. HTTP, 32 connections, 5-second warmup and 30-second measurement. Access logging is disabled; no auth service, TLS, cache, guardrails or real model is enabled.

Agentgateway v1.5.0 and Praxis AI 0.5.0 released images are pinned by digest; exact images, fixture hashes, commands and CPU sets are in the manifest and inspections. The initial matrix uses a seeded treatment order per workload. This does not eliminate order effects.

## Fixed offered rates

Baseline **direct**, candidate **agentgateway**. Good QPS counts HTTP 200 responses per measured second. p99 is completion latency in milliseconds. Error columns count non-200 requests/timeouts. A † marks a fixed-rate trial that missed 99% of offered QPS or exceeded 0.1% errors.

| API | Bytes | Offered QPS | Baseline good QPS | Candidate good QPS | Baseline p99 ms | Candidate p99 ms | Errors baseline/candidate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| anthropic | 1024 | 1000 | 999.0 | 998.9 | 0.205 | 0.577 | 0/0 |
| anthropic | 1024 | 3000 | 2998.9 | 2998.9 | 0.239 | 0.561 | 0/0 |
| anthropic | 16384 | 1000 | 999.0 | 998.9 | 0.442 | 0.791 | 0/0 |
| anthropic | 16384 | 3000 | 2998.9 | 2998.9 | 1.204 | 0.874 | 0/0 |
| openai | 1024 | 1000 | 998.9 | 998.9 | 0.255 | 0.562 | 0/0 |
| openai | 1024 | 3000 | 2998.9 | 2998.9 | 0.254 | 0.500 | 0/0 |
| openai | 16384 | 1000 | 998.9 | 998.9 | 0.469 | 0.763 | 0/0 |
| openai | 16384 | 3000 | 2998.9 | 2998.9 | 0.917 | 0.805 | 0/0 |
| translation | 1024 | 1000 | 999.0 | 998.9 | 0.189 | 0.573 | 0/0 |
| translation | 1024 | 3000 | 2998.9 | 2998.9 | 0.230 | 0.522 | 0/0 |
| translation | 16384 | 1000 | 999.0 | 998.9 | 0.424 | 0.781 | 0/0 |
| translation | 16384 | 3000 | 2998.8 | 2998.9 | 0.839 | 0.788 | 0/0 |

## Saturation runs

Offered QPS 0 tells Fortio to run at maximum throughput at the configured 32 connections. Higher successful QPS is better within these configurations; the ratio below is candidate/baseline. It is not a universal speedup. Saturation latencies correspond to different achieved rates; do not interpret their difference as added proxy latency.

| API | Bytes | Baseline good QPS | Candidate good QPS | Ratio | Baseline p99 ms | Candidate p99 ms | Errors baseline/candidate |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| anthropic | 1024 | 41443.6 | 13604.8 | 0.328× | 2.827 | 3.898 | 0/0 |
| anthropic | 16384 | 11904.7 | 8398.2 | 0.705× | 13.694 | 7.232 | 0/0 |
| openai | 1024 | 41380.6 | 13663.3 | 0.330× | 2.788 | 3.891 | 0/0 |
| openai | 16384 | 11897.1 | 8344.0 | 0.701× | 13.975 | 7.296 | 0/0 |
| translation | 1024 | 42094.9 | 13191.2 | 0.313× | 2.721 | 3.979 | 0/0 |
| translation | 16384 | 11874.1 | 8324.1 | 0.701× | 13.631 | 7.228 | 0/0 |

## Correctness and limits

The campaign preflight passed 54 JSON content/usage, incremental SSE and upstream 429 checks across the selected API paths, payload sizes and three treatments. Fortio validates response status during timed load; it does not parse every response body. Streaming was qualified at low load; the performance matrix measures nonstreaming requests. Synthetic usage fields are constants, not tokenizer results.

Fortio uses fixed concurrency, paced arrivals and disabled catch-up. A saturated client/gateway can miss offered QPS; its latency histogram is not a corrected open-loop latency distribution. Read achieved QPS and errors together with latency. Docker resource samples are approximate; no process-RSS or CPU-efficiency winner is claimed from them.

For translation, the direct backend receives native Chat Completions while gateways receive Anthropic Messages and translate. That baseline checks backend capacity; latency subtraction does not isolate translation cost. Built-in processing differs between products despite matching external behavior.

Keep this result separate from Gateway API controller tests and paused GPU inference work. Repeated/counterbalanced runs and a second load-generator check are required before broad public performance claims.

## Client framing warnings

The following trials emitted repeated Fortio Content-length missing warnings. That adds client logging and signals different HTTP framing/connection behavior. Preserve the observations, but do not attribute these comparisons solely to proxy CPU. A separately planned follow-up should check framing, connection reuse and another client.

| Trial | Warning count |
| --- | ---: |
| 039-praxis-translation-1024-q1000-r1 | 30,016 |
| 042-praxis-translation-1024-q3000-r1 | 90,016 |
| 044-praxis-translation-1024-q0-r1 | 192,884 |
