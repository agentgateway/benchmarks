# Requirements and supporting evidence

Use a requirement to select evidence, rather than collapsing correctness,
throughput and source features into one score. All Gateway API rows below refer
to agentgateway controller/data plane **v1.6.0** and Praxis operator **fb8beaa**
with core **v0.5.2**. Core nightly-20261002 was setup-blocked in the retained
conformance campaign, so these rows do not score nightly coverage.

## Gateway API behavior

Except for the separately marked static-address follow-up, these are retained
October 2 observations under conformance v1.5.1, repeated three times per release. A failing multi-assertion test does not by itself identify a
specific defect or prove that every related capability is absent. The linked
matrices include exact upstream test sources and all outcomes.

| Requirement | Agentgateway v1.6.0 | Praxis operator/core v0.5.2 | Exact tests / interpretation |
| --- | --- | --- | --- |
| Selected HTTP core behavior | All 33 cases passed each time | All 33 cases passed each time | [Core matrix](../../2026-10-02-gateway-extended/reports/matrix/http-core.md); core parity is observed |
| Host/path rewriting | Passed | Passed | `HTTPRouteRewriteHost`, `HTTPRouteRewritePath`; do not claim these as agentgateway-only features |
| Request/backend timeouts | Passed | Passed | `HTTPRouteTimeoutRequest`, `HTTPRouteTimeoutBackendRequest` |
| Response header modification | Passed | Passed | `HTTPRouteResponseHeaderModifier`; large-scale lifecycle is a separate question |
| WebSocket backend behavior | Passed | Passed | `HTTPRouteBackendProtocolWebSocket`; no WebSocket capacity test is included |
| Method/query matching | Passed | Did not pass | `HTTPRouteMethodMatching`, `HTTPRouteQueryParamMatching` |
| CORS | Passed | Did not pass | `HTTPRouteCORS`, `HTTPRouteCORSAllowCredentialsBehavior` |
| Request mirroring | Passed | Did not pass | `HTTPRouteRequestMirror`, `HTTPRouteRequestMultipleMirrors`, provisional percentage-mirror case |
| gRPC routing selection | All five selected cases passed | No selected case passed | [gRPC matrix](../../2026-10-02-gateway-extended/reports/matrix/grpc.md); not a throughput result |
| TLSRoute positive routing | Selected positive cases passed | Selected positive cases did not pass | [TLS matrix](../../2026-10-02-gateway-extended/reports/matrix/tls.md); Praxis passed two negative unsupported-mode cases, which are not positive TLS routing |
| Backend TLS policy/certificate assertions | Selected cases passed | Selected cases did not pass | `BackendTLSPolicy`, conflict, invalid-ref/kind, generation and SAN cases; inspect the assertion before attributing a security defect |
| ListenerSet delegation/conflicts | Selected cases passed | Selected cases did not pass | Namespace selection, reference grants, routing and conflict cases |
| Static address assignment | Old-suite assertion failed; corrected v1.6.1 follow-up passed 3/3 | Old-suite assertion failed; corrected follow-up failed 3/3 with UnsupportedAddress | [Corrected-suite GCE evidence](03-gateway-api.md); separate from the retained 107-case score |

Unlinked named tests in this table appear in the [HTTP/Gateway extended matrix](../../2026-10-02-gateway-extended/reports/matrix/http-gateway-extended.md).
For HTTPS, note that Praxis passed the core HTTPS-listener test even though the
separate TLSRoute cases above did not pass. “Cannot terminate TLS” would be an
unsupported generalization.

## AI gateway requirements

| Requirement | Evidence family | Version / boundary |
| --- | --- | --- |
| Efficient forwarding of OpenAI/Anthropic traffic | Common Fortio/AIPerf and protocol fixtures | AGW v1.6.0 versus core v0.5.2 and core nightly; no translation/accounting claim |
| Native provider handling and Anthropic-to-OpenAI translation | Native profile, protocol/SSE/cancellation fixtures | AGW v1.6.0 versus **Praxis AI v0.5.0** and **October 2 AI nightly**; separate distribution pins |
| Streaming latency | AIPerf TTFT/ITL and error evidence | Synthetic service pacing; no GPU or real-provider latency conclusion |
| Token accounting correctness / hard quota enforcement | Source review only for this campaign | Configured extraction/accounting does not prove accuracy or a hard distributed spending bound |
| Gateway-owned Responses/Conversations storage | Pinned Praxis AI source/docs | A substantive Praxis capability; persistence, isolation and replica behavior not benchmarked |
| MCP/A2A interoperability | Pinned source review | Transport/profile details matter; no binary “supported” score or interoperability pass |
| Guardrail efficacy or security equivalence | Not measured | Presence of policy/guardrail code is not an efficacy test |
| EPP integration availability | Pinned source/build review | Both have integration paths; Praxis AI requires an opt-in build feature; neither path exercised here |
| Inference scheduling, accelerator utilization, model quality or inference cost | Paused | No claim can be derived from this CPU campaign |

See the [feature comparison](04-feature-comparison.md) for exact source links and
build-profile differences. The October 2 Praxis AI image is pinned from its successful scheduled workflow
and SHA tag. Absence of the literal dated tag did not establish image absence.

## Operational requirements

Configuration scale needs both current-generation status and verified traffic.
Recovery needs event timing, errors, probe scheduling and replica count. Stock
operator/core compatibility needs a runnable supported pairing before individual
features can be evaluated. The current campaign retains these as separate reports
and raw evidence families; a standalone forwarding success does not establish
Kubernetes lifecycle compatibility.
