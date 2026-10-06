# Methodology and validity

Status: all three CPU and Kubernetes passes are [reviewed](../evidence/qualification/final-review.json). All eight campaign VMs and boot disks have been explicitly deleted after verified evidence retention.
This methods document does not approve incomplete measurements; the combined
final review follows completion of both evidence families.

## Scope and provenance

Solo.io commissioned this comparison and contributes to agentgateway. It is an
internal, reproducible technical evaluation, not an independent certification.
The protocol retains favorable and unfavorable outcomes for both implementations.
Image digests, configuration files and exact source revisions are part of the
[version ledger](../evidence/versions/selection.json). Different Praxis
distributions are never pooled into one version label.

The CPU campaign has three standalone roles (client, gateway, service) and five
Kubernetes roles (control plane, controller, gateway, service, client). Every VM
is n2-standard-8 on native GCE in us-central1-a with minimum Cascade Lake, the same
Ubuntu image and 100 GiB balanced boot disk. Private addresses carry benchmark
traffic; external addresses are for administration. There is no intermediary
Envoy, GKE or managed GCP load balancer. Nighthawk is a client, not a gateway.
MetalLB allocates test addresses; HTTP performance uses private NodePorts.

Standalone gateways receive two distinct pinned guest cores (2 and 3), a two-CPU
quota and 2 GiB. Kubernetes gateways receive a two-CPU limit and 256 MiB on their
own node; those cores are not pinned. Controller and backend nodes are separate.
Do not compare the two deployment profiles as a controlled measurement of
Kubernetes overhead: the resource limits and network paths differ.

## What the tools measure

| Tool / probe | Question answered | Important limit |
| --- | --- | --- |
| [Fortio](https://github.com/fortio/fortio) 1.75.3, standard Go HTTP client | Successful request rate and latency for configured HTTP/JSON traffic | Fixed concurrency caps in-flight work; unlimited rate is capacity under that cap, not an SLO guarantee |
| Pinned [Nighthawk](https://github.com/envoyproxy/nighthawk) client | An additional open-loop HTTP view at 1,000 RPS | Not a second proxy; nearest exported quantile above p99 is labeled explicitly |
| [AIPerf](https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference) 0.13.0 | Streaming TTFT, ITL, request and output-token rates | Deterministic CPU service; no model inference, quality or GPU utilization claim |
| [Gateway API conformance](https://gateway-api.sigs.k8s.io/docs/concepts/conformance/) | Specific upstream assertions for the selected features | Case counts are not percentages of the specification; this is not official certification |
| [ClusterLoader2](https://github.com/kubernetes/perf-tests/blob/b337418289cce7ac518ed7e6920cded4a816e82c/clusterloader2/README.md) plus observer | Submission, current-generation status and served response markers for 1,000/5,000 routes | Custom route shape and 300-second post-submission window; not a universal maximum route count |
| Scheduled HTTPX probes | Observed errors during graceful controller rollout and data-plane pod deletion | 10 probes/sec on a single data-plane replica; not hard-failure HA or production availability |

These are established upstream tools executing a campaign-specific matrix.
The ClusterLoader2 HTTPRoute scenario, response fixture, correctness checks and
recovery probes are authored for this comparison. They are not a standardized
industry AI-gateway score or an unmodified Kubernetes release scalability
scenario. Upstream Gateway API conformance assertions retain their own suite identity.

Fortio classifies HTTP 200 responses as successful throughput; it does not
semantically validate every response body under load. Separate correctness
fixtures validate content before load. AIPerf additionally parses the streaming
protocol. A successful-rate table is therefore not a proof of every response
being semantically correct under arbitrary pressure.

Fortio and Nighthawk use a separate five-second warmup process followed by a
thirty-second measured process. This warms the gateway/service, but the measured
client opens fresh connections. AIPerf uses five-second warmup, thirty-second benchmark and ten-second grace.
Its fixed seed is 42, with 128 input and 64 output tokens. The synthetic service
has a nominal 25 ms initial delay and 5 ms inter-token interval. JSON content
sizes are 1,024/16,384 bytes; these are not total serialized request or wire sizes.
HTTP response bodies are 0/16,384 bytes. The full generated plans are retained.

For non-streaming JSON, the fixture returns 1,024 or 16,384 content bytes but
reports fixed synthetic usage of 128 input and 64 output tokens. Those fields
exercise usage extraction and are not a tokenizer-derived accounting oracle.
Streaming emits the requested number of ` hello` pieces; AIPerf independently
records the configured 128/64 sequence lengths. The [fixture source](../harness/mock/main.go)
therefore supports protocol/throughput tests, not a token-billing accuracy claim.

The common profile forwards HTTP, including the two AI API shapes, without
provider transformation or token accounting. The native profile uses each
product's AI processing. Praxis response-usage extraction is enabled; agentgateway
uses its built-in LLM path. Praxis selects three configured listeners, while
agentgateway selects models through one listener. These concrete profiles are
useful comparisons, but do not isolate equivalent accounting work. Translation
uses an Anthropic client against an OpenAI backend; the direct baseline calls
the OpenAI backend without a translation step. Agentgateway explicitly sets
`AGENTGATEWAY_MESSAGES_PREFER_COMPLETIONS=true` for that translation pair; the
default Messages-to-Responses fallback is outside this profile. See
[configuration boundaries](../docs/COMPARISON-SCOPE.md).

## Validity and exclusions

Qualification checks response bodies, JSON/SSE behavior, synthetic upstream
errors and cancellation before load. Each pass must retain tool exit codes,
request errors, generated inputs, configuration identities, host samples and
completion markers. Exit zero alone does not approve a pass. Intentional gateway
CPU saturation can be a capacity result; an exhausted client/backend or incorrect
environment requires attribution and exclusion or correction.

The earlier seeded standalone qualification passed 102 protocol checks and 17
cancellation checks across four common and three native treatments. The final
qualification adds the separately pinned October 2 AI nightly as a fourth native
treatment and passed all 120 protocol checks, 20 cancellation checks and 36 short
load cases. Its review is retained separately; these short cases are not sustained
capacity measurements. Earlier duplicate-entrypoint and configuration-schema mistakes are
retained harness failures. An initial partial direct-only CPU pilot was stopped
to freeze the AIPerf seed. The whole pilot was excluded before any comparative
gateway performance outcome existed. The seeded qualification uses identical
canonical generated message contents across treatments. Before any Praxis
measurement, inherited Docker healthchecks against its disabled admin listener
were disabled and requalified. Already-started direct/agentgateway measurements
are unaffected: neither treatment had a probe and Praxis containers were stopped.

The first Kubernetes pilot exposed a separate environment error: the intended
expanded TCP profile had not reached Kubernetes hosts/pods. Praxis 512-connection
traffic returned 502 with outbound `BindError`/errno 99. The complete pilot for
all treatments was excluded, not just the failed case. Corrected qualification
applies the same TCP profile to every host and pod namespace using the upstream
CNI tuning plugin, and adds sustained unlimited-rate 512-connection cases.
[Protocol and exclusion details](../docs/PROTOCOL.md) preserve the sequence.

The next first-pass review found a draining old Praxis pod still present at HTTP
startup. Its sampled CPU was almost idle, but readiness alone did not enforce the
one-pod topology and endpoint eligibility was not retained. The entire Kubernetes
attempt was excluded for all treatments, without asserting a throughput effect.
A new stable-single-pod/EndpointSlice barrier is applied equally and requalified
before a fresh first pass. Standalone CPU and focused static-address results are
unaffected. The [exclusion record](../evidence/exclusions/kubernetes-startup-drain-pilot/exclusion.json)
retains this decision and the original export hash.

A subsequent qualification was also excluded: its nightly switch briefly
qualified a release-image pod while the requested nightly replacement was being
reconciled. The setup now stops the previous controller completely and requires
the requested image digest at the stable topology barrier. The
[image-switch exclusion](../evidence/exclusions/kubernetes-image-switch-pilot/exclusion.json)
retains the contradictory identities; no affected observation enters results.

Administrative GCP/SSH timeouts are distinct from workload failures. Reconnection
uses verified host keys and captured instance identities, and existing remote
jobs are inspected before resuming. No administrative retry silently duplicates
a measured case. Infrastructure corrections are documented even when they remove
an apparent agentgateway advantage.

The corrected Kubernetes qualification found client/backend capacity limits in
the direct unlimited-rate reference, while the gateway paths retained upstream
and client headroom. The direct result is the capacity of the complete measured
service path. It is not an unconstrained backend ceiling or a way to isolate
intrinsic proxy CPU cost. Each measured pass receives its own resource review.

## Statistical interpretation

Three accepted repetitions rotate treatment order on one placement. Report every
pass, arithmetic mean, minimum, maximum and sample standard deviation. These
samples characterize repeatability on those hosts; they are not three independent
cloud placements or a basis for broad statistical significance claims. Four
treatments in each standalone profile cannot be fully position-balanced in only
three passes. Within a standalone profile, the same three agentgateway and
direct-reference runs support both Praxis release/nightly comparisons. These are
shared references, not six independent agentgateway repetitions. Native and common
reference runs remain separate because their configurations differ.

Report successful throughput beside errors. Means of per-run p99 values remain
means of per-run p99 values, not pooled distribution percentiles. At fixed offered
rates, a capacity ratio is inappropriate when both implementations deliver the
same requested load. Streaming throughput is strongly constrained by the mock
service's pacing. Differences close to the observed variation should not become
competitive headlines. Resource samples cover tool execution including startup
and warmup; they do not establish precise CPU cycles per request.

A setup-blocked nightly pairing has no individual feature or performance score.
The route observer requires both current status and traffic. It does not launch
its full-route probe until all statuses are current; a zero full-probe count can
mean not attempted. Probes check each hostname against a shared generation marker
and backend, not a unique response value/backend per route. Marker strings are
also reused across scale scenarios; a successful sample without current status
is not proof of a fresh configuration generation. Individual routing
semantics are covered by the separate conformance assertions.

Unconverged route mutations are censored observations, not zero-second results;
do not average only successful mutations. Graceful restart error counts describe
the retained probe schedule and one desired data-plane replica. Old/new pod
overlap during the induced graceful recovery is part of that scenario; steady
HTTP testing instead requires the stable single-pod barrier before load. The
HTTPX recovery client reuses connections and observes ten seconds after the
mutation commands finish. Across all six data-plane deletion windows, the initial process remains in the
last near-end resource sample in five: agentgateway passes 1/3 and all Praxis
passes. Agentgateway pass 2 ends with a replacement-only sample. These observations
do not establish study-wide complete traffic handoff, fresh-connection
availability or old-process exit during every observation window.
[All-pass overlap evidence](../evidence/qualification/kubernetes-final-facts/recovery-overlap.json).

## Deliberately outside this campaign

TLS/HTTP2 capacity, real providers/models, GPU inference scheduling, long soaks,
multiple placements, realistic policy/auth/quota/telemetry overhead, MCP/A2A
interoperability, guardrail efficacy, distributed budget accuracy and stateful AI
storage resilience are not measured here. Source-supported capabilities are
labeled separately in the [feature comparison](04-feature-comparison.md).


## Final three-pass audit

All 822 accepted load cases completed without confirmed request errors or resets;
360 protocol checks and 60 cancellation checks passed. Nighthawk recorded 26
requests still in flight at cutoff, which are retained separately from failures.
The final review covers 696 standalone isolation checks, 96 Kubernetes startup
checks and byte-for-byte retention of 2,354 first-pass measurement files.

One standalone client sample attempted to read `/proc/0` while Docker removed a
successfully exited Nighthawk container. The sample began about 79 ms after the
measured interval ended; all 30,000 requests completed with HTTP 2xx. Six healthy
container samples cover that measurement. The event remains in the raw telemetry
and [attribution record](../evidence/qualification/final-facts/cpu-telemetry-attribution.json).
It is a post-measurement collection race, not descriptor exhaustion. The separate
route-scale telemetry gaps and recovery limitations above remain applicable.
