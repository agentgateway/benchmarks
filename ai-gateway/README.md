# AI gateway protocol and proxy-overhead campaign

This is the historical October 1, single-run campaign. For the completed
three-pass agentgateway v1.6.0 and Praxis release/nightly comparison, start with
[the current CPU reports](../cpu-comparison/2026-10-05-stable-comparison/README.md).

This harness uses a deterministic Go backend, Fortio 1.75.1, agentgateway v1.5.0
and Praxis AI 0.5.0, with container images pinned in `compose.yaml`. It measures
synthetic proxy overhead; it performs **no model inference**. The [initial single-round report](results/2026-10-01-initial/README.md) includes
all 54 trials and the complete raw evidence archive.

The workload design follows the public
[agentgateway/LiteLLM proxy benchmark](https://github.com/linsun/litellm-agw-perf)
and its fixed-throughput follow-up. The implementation here adds repeatable
payloads, a direct backend, explicit resource isolation, alternating treatment
order, protocol qualification and retained failure evidence. It is newly written;
no source from that harness was copied.

## What is compared

| Case | Client API | Backend API | Enabled processing |
| --- | --- | --- | --- |
| `openai` | Chat Completions | Chat Completions | agentgateway AI provider route; Praxis token usage extraction + routing |
| `anthropic` | Messages | Messages | agentgateway Anthropic provider; Praxis format/protocol filters, token extraction + routing |
| `translation` | Messages | Chat Completions | agentgateway provider translation; Praxis Messages-to-Chat request/response and SSE translation |

Configurations use synthetic credentials. No external authorization, distributed
rate limiting, response cache, guardrail service, TLS, database or real provider
is enabled. Agentgateway uses two workers; Praxis sets `runtime.threads: 2` (per service).
One API listener receives traffic per trial. Both have the same two logical CPUs and
2 GiB memory limit. The mock and load generator have separate two-CPU sets and
2 GiB limits. Record physical core/SMT layout; disjoint logical CPU IDs alone do
not ensure independent physical cores. Access logging is disabled for
agentgateway; Praxis has no access-log filter. Their built-in AI processing is
not identical, so this is a comparison of the documented configurations, not a
proof of equal internal work.

The direct baseline uses the backend wire format. For translation it sends Chat
Completions directly, whereas clients send Messages to the gateways. Use it to
check backend headroom; subtracting its latency does not isolate translation
cost precisely.

## Run

Requirements: Python 3.10+, Go 1.26+, Docker with Compose, and a dedicated native
Linux/amd64 Docker host with at least eight CPUs. The benchmark project name and
loopback ports 28080–28084 are fixed; the runner refuses to reuse existing project
containers. Do not run on a shared host for publication.

```sh
cd ai-gateway
python3 campaign.py --smoke --dry-run
python3 campaign.py --smoke --output /tmp/ai-qualification-001
python3 campaign.py --initial --dry-run
python3 campaign.py --initial --output /tmp/ai-initial-001
# For a separately planned repeated campaign:
python3 campaign.py --output /tmp/ai-performance-001
```

The runner rebuilds the mock for the Docker host architecture, creates only its
Compose services, and removes those services after success or failure. It
refuses to overwrite a campaign. `build-mock.sh` is also available separately.
The default CPU sets are gateway `2-3`, mock `4-5`, client `6-7`; override
`GATEWAY_CPUSET`, `MOCK_CPUSET`, and `CLIENT_CPUSET` after inspecting topology.

Full defaults: three cases, 1,024/16,384 input-content and output-content bytes,
1,000/3,000 offered QPS and maximum throughput, 32 connections, five-second
warmup, 30-second measurement, six repetitions. JSON framing adds bytes beyond
the content size. The 324 measured trials require at least 189 minutes of
warmup/load, plus startup and collection. Each treatment occupies each position
twice per workload. A smaller declared subset can be chosen with `--cases`,
`--sizes`, and `--qps`; preserve the preregistered subset and all outcomes.

`--initial` selects exactly one preliminary round (54 trials, at least 31.5
minutes of warmup/load for the full matrix). It preserves the 30-second minimum
and native/resource checks. This explicitly authorized screening mode cannot
estimate variance or support statistical superiority claims.

Repeated performance mode requires at least five repetitions and 30 seconds, native
amd64 images and nonoverlapping CPU sets. ARM/emulation is allowed only with
`--smoke`, whose short load is qualification-only. The earlier local Praxis image crashed under QEMU; native amd64 protocol
qualification passed. Emulation failures are not native-platform performance
results.

## Qualification and evidence

Before load, `probe.py` checks JSON content/usage, incremental SSE content and
terminal events, and an upstream 429 for each selected case. It records first
semantic output and completion timing at low load; those timings are diagnostic,
not streaming throughput results. The stream emits byte chunks at a fixed
cadence. Synthetic usage fields are constants, not tokenizer measurements.

The campaign stores source/binary hashes, image inspections, resolved Compose,
commands, protocol outcomes, Fortio JSON/logs, resource samples, per-trial
summaries, cleanup status and SHA-256 checksums. Failures remain incomplete and
retain their logs. A clean orchestration exit does not prove that offered load
was sustained; inspect `target_met`, successes, errors and achieved rate.

Fortio uses fixed concurrency and paced traffic with catch-up disabled. Under
load it can fall below offered QPS; its completion latency histogram is not a
corrected open-loop latency distribution. Report offered and successful QPS,
HTTP errors and timeouts alongside percentiles, and use inference-perf for
inference arrivals, TTFT, token latency and SLO goodput. HTTP 200 validation
happens in qualification, not on every Fortio response; add sampled protocol
validation if errors appear only under concurrency.

Docker resource samples are approximate, including startup/stop boundaries;
filter by the exact trial's container names. The named load generator is
included so a client bottleneck is detectable. Sampled maxima are not true
instantaneous peaks, and Docker's memory display is not process RSS. For public
CPU/RSS claims, collect cgroup/process measurements with timestamps on the native
host and retain raw data. Do not select the best repetition or equate a
mock-backend win to improved GPU efficiency.

## Initial reports

Generate the two Markdown comparisons from all trials of a completed initial
campaign. The report command rejects smoke timings, incomplete campaigns and
missing treatment pairs:

```sh
python3 report.py --campaign /tmp/ai-initial-001 --output /tmp/ai-reports \
  --evidence-link PATH_OR_URL_TO_RAW_EVIDENCE
python3 -m pip install -r plot-requirements.txt
python3 plots.py --campaign /tmp/ai-initial-001 --output /tmp/ai-reports
```

The paired reports use direct backend → agentgateway and agentgateway → Praxis.
The saturation ratio always means candidate/baseline. Retain raw error counts
and achieved rates, including cases where either gateway loses. These scripts
support the initial one-round report; repeated campaigns need a separate
analysis of dispersion and treatment order.
