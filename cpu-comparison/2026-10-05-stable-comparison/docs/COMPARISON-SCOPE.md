# Version and workload boundaries

This campaign uses agentgateway v1.6.0, Praxis core v0.5.2 and Praxis core
nightly-20261002. Image digests, rather than mutable tag names, identify treatments.

| Question | Evidence to use | What it does not establish |
| --- | --- | --- |
| HTTP forwarding overhead | Common-profile Fortio and Nighthawk, direct service baseline | Native AI policy overhead or an internet-facing TLS deployment |
| OpenAI/Anthropic forwarding and SSE | Common-profile protocol checks, Fortio and AIPerf | Provider translation, token accounting, inference scheduling, or model quality |
| Native AI behavior | Separately identified native-AI profile and distribution | A feature of either Praxis core image merely because Praxis AI implements it |
| Gateway API correctness | October 2 stable/release and stable/nightly campaigns, exact per-case outcomes | Certification, every extension, or a performance score |
| Static address discrepancy | Corrected conformance v1.6.1 follow-up | A retroactive change to the original v1.5.1 raw outcome |
| Kubernetes routing throughput | NodePort workload with controller-generated configuration | Managed GCP load-balancer performance |
| Route scale | ClusterLoader2 hostname plus response-header create/update workload | Maximum bare-route capacity |
| Restart behavior | Scheduled probes around graceful controller/pod replacement | Hard-failure recovery, zero downtime, or production availability |

Praxis AI is a separate project and container distribution, independently
versioned from Praxis core. Its [v0.5.0 README](https://github.com/praxis-proxy/ai/blob/v0.5.0/README.md#praxis-ai-and-praxis) describes this separation.
The registry returned `MANIFEST_UNKNOWN` for the literal dated AI tag, but AI
publishes rolling nightly and SHA tags. The October 2 scheduled build was found
and its retained SHA-tag index matches the workflow digest. Include its amd64
image separately; see [provenance](../evidence/versions/praxis-ai-nightly-provenance.json).
The initial conclusion that no October 2 AI image existed was incorrect and is
withdrawn. Neither AI image is the separately dated core nightly.

## Interpretation rules

Report support declarations, runnable configurations, measured results, and
interpretations separately. A setup block is not a per-feature failure score.
Keep all valid repetitions, including unfavorable results. Attribute tool/host
failures before excluding samples; retain excluded artifacts and reasons.

Use successful response throughput together with errors, achieved load, latency,
and resource use. An arithmetic mean of three p99s is a mean of run-level p99s,
not a pooled p99. The shared placement limits generalization. Synthetic backend
results describe gateway behavior; they do not measure GPU inference.

A full comparison means addressing each agreed workload and documenting its
outcome or evidenced incompatibility. It cannot make an unsupported feature
runnable or turn a failed prerequisite into a valid throughput measurement.

## Nightly operator qualification

The pinned core nightly starts with the standalone common configuration. In the
stock operator deployment, even a nonempty HTTP route produces cluster name
`gateway-backend~backend~8081`; the nightly rejects the `~` characters and exits 1.
The operator HEAD was rechecked October 5 and remains
`fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c`, with no published release returned.
Retain each bounded setup attempt and node/image/config evidence. HTTP, scale and
recovery behind that operator pairing are **not evaluated**, not zero throughput.
Do not silently rewrite the generated configuration to bypass the incompatibility.
This is additional evidence to the earlier empty-router conformance setup block.

## Native-profile work is not identical

Agentgateway uses one LLM listener with model-based provider selection. Praxis AI
uses separate listeners and preselected filter chains for each protocol, with
`token_count` response-usage extraction enabled. It is not an input-tokenizer
benchmark. The common profile removes both products' native AI processing and
routes identically to one fixture. Keep these profiles separate in every table
and chart; do not describe native ratios as equal-work parser efficiency.

For translation, the direct baseline speaks OpenAI Chat Completions to the
backend; the gateway-facing client speaks Anthropic Messages. That comparison
includes format conversion. In the JSON AI cases, 1 KiB and 16 KiB identify
message/response **content** lengths, not total HTTP or JSON envelope bytes.
Default product connection-pool behavior is retained; this is not a per-product
maximum-tuning search.

The agentgateway native container explicitly sets
`AGENTGATEWAY_MESSAGES_PREFER_COMPLETIONS=true`. In the pinned v1.6.0
[conversion table](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/crates/agentgateway/src/llm/mod.rs),
this chooses Chat Completions ahead of Responses for the Messages-to-OpenAI
fallback. Direct Anthropic Messages remains preferred for an Anthropic provider.
The setting preserves the declared translation pair against the Chat Completions
fixture; this campaign does not benchmark the default Messages-to-Responses path.


Release and nightly remain separate treatments with their own three repetitions.
Within each standalone profile, both comparisons share the same three direct and
agentgateway reference runs. Do not double-count those reference runs when reading
two version comparisons or combine native and common-profile measurements.
