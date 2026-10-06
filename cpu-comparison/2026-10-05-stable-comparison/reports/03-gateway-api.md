# Gateway API: correctness, configuration scale and recovery

These are separate evidence families. HTTP throughput does not establish feature coverage, and a successful status condition does not by itself establish that updated routes serve the intended response.

## Retained extended-conformance campaign

The October 2 campaign used the same agentgateway v1.6.0 and Praxis core image digests, but upstream conformance v1.5.1. Both release implementations passed all 33 selected HTTP core cases in each repetition. Across 107 selected cases, the recorded results were 106/107 for agentgateway and 52/107 for Praxis core v0.5.2. The selected cases include core and extended HTTP/Gateway behavior, gRPC and TLS routes; counts are test cases, not percentages of the specification or official certification.

Use the [release comparison](../../2026-10-02-gateway-extended/reports/release-comparison.md) for all retained per-case outcomes and the [nightly compatibility report](../../2026-10-02-gateway-extended/reports/nightly-compatibility.md) for its setup block. Do not manufacture a new 107-case score by combining suite versions.

## Corrected static-address follow-up

The old `GatewayStaticAddresses` test asserted an earlier status snapshot. Agentgateway release CI explicitly ran and passed the corrected test; it was not skipped. This campaign runs only that case from conformance v1.6.1, source `8bb74df00e56ec8f944d48c25e6c1c9c2f6848e3`, on GCE for both runnable releases. Product images remain unchanged.

| Implementation | Repetition 1 | Repetition 2 | Repetition 3 |
| --- | --- | --- | --- |
| Agentgateway v1.6.0 | PASS | PASS | PASS |
| Praxis core v0.5.2 | FAIL | FAIL | FAIL |

The [prior CI investigation](../../2026-10-02-gateway-extended/reports/agentgateway-static-address-follow-up.md) remains the authority for the original discrepancy. Fresh follow-up rows and artifact paths are in [static-address-rows.json](data/static-address-rows.json). Original v1.5.1 failures remain unchanged.

The [pinned test](https://github.com/kubernetes-sigs/gateway-api/blob/8bb74df00e56ec8f944d48c25e6c1c9c2f6848e3/conformance/tests/gateway-static-addresses.go) checks address validation, conditions, listener status and address assignment. It does not send HTTP traffic to the assigned address. This campaign uses MetalLB for allocation/status and private NodePort for measured HTTP; it does not demonstrate external VIP reachability.

## Route create/update scenarios

ClusterLoader2 submits 1,000 or 5,000 hostname-bearing HTTPRoutes at 100 writes/sec. Each adds a generation-specific response header. The observer checks current-generation Accepted/ResolvedRefs status and then verifies every route through traffic. Its bounded observation window is 300 seconds after submission; times below include submission. “Not observed” is censored, not zero.

| Implementation | Routes | Mutation | Fully verified runs | Completion seconds: mean [min–max] |
| --- | ---: | --- | ---: | ---: |
| Agentgateway v1.6.0 | 1000 | created | 3/3 | 12.052 [11.655–12.324] |
| Agentgateway v1.6.0 | 1000 | updated | 3/3 | 11.669 [11.611–11.726] |
| Agentgateway v1.6.0 | 5000 | created | 3/3 | 57.575 [57.083–57.921] |
| Agentgateway v1.6.0 | 5000 | updated | 3/3 | 57.150 [56.943–57.413] |
| Praxis core v0.5.2 | 1000 | created | 0/3 | Not observed |
| Praxis core v0.5.2 | 1000 | updated | 0/3 | Not observed |
| Praxis core v0.5.2 | 5000 | created | 0/3 | Not observed |
| Praxis core v0.5.2 | 5000 | updated | 0/3 | Not observed |

### Every route mutation

| Implementation | Pass | Routes | Mutation marker | Fully verified | Current status count at end | Sample passing at end | Full-traffic completion seconds |
| --- | ---: | ---: | --- | --- | ---: | --- | ---: |
| Agentgateway v1.6.0 | 1 | 1000 | created | Yes | 1000 | 100/100 | 12.324 |
| Agentgateway v1.6.0 | 1 | 1000 | updated | Yes | 1000 | 100/100 | 11.726 |
| Agentgateway v1.6.0 | 1 | 5000 | created | Yes | 5000 | 100/100 | 57.921 |
| Agentgateway v1.6.0 | 1 | 5000 | updated | Yes | 5000 | 100/100 | 57.095 |
| Agentgateway v1.6.0 | 2 | 1000 | created | Yes | 1000 | 100/100 | 11.655 |
| Agentgateway v1.6.0 | 2 | 1000 | updated | Yes | 1000 | 100/100 | 11.668 |
| Agentgateway v1.6.0 | 2 | 5000 | created | Yes | 5000 | 100/100 | 57.719 |
| Agentgateway v1.6.0 | 2 | 5000 | updated | Yes | 5000 | 100/100 | 56.943 |
| Agentgateway v1.6.0 | 3 | 1000 | created | Yes | 1000 | 100/100 | 12.177 |
| Agentgateway v1.6.0 | 3 | 1000 | updated | Yes | 1000 | 100/100 | 11.611 |
| Agentgateway v1.6.0 | 3 | 5000 | created | Yes | 5000 | 100/100 | 57.083 |
| Agentgateway v1.6.0 | 3 | 5000 | updated | Yes | 5000 | 100/100 | 57.413 |
| Praxis core v0.5.2 | 1 | 1000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 1 | 1000 | updated | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 1 | 5000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 1 | 5000 | updated | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 2 | 1000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 2 | 1000 | updated | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 2 | 5000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 2 | 5000 | updated | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 3 | 1000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 3 | 1000 | updated | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 3 | 5000 | created | No | 0 | 0/100 | Not observed |
| Praxis core v0.5.2 | 3 | 5000 | updated | No | 0 | 0/100 | Not observed |

All phase-level times and per-pass/grouped summaries are in [scale rows](data/scale-rows.json) and [scale summary](data/scale-summary.json). A failure for this route shape is not a universal bare-route limit. Full-route probes run only after every route has current status; a zero full-probe count can therefore mean not attempted. The sample and full probes check a shared generation marker through each hostname, not distinct backends or per-route unique response values. Marker strings are reused between scenarios, so a successful sample without current status is not proof of a fresh configuration generation. Attribute status, generated-configuration/API-size and traffic-propagation failures from their raw controller/API evidence.

### Recorded nonconvergence mechanisms

Each 1,000-route diagnostic captured a new Praxis pod rejecting `1003` filter entries against the compiled `100`-entry chain guard. In the three 5,000-route phases, replacement configurations contained 4,273, 4,277, 4,301 entries; the controller also received timestamped API 422 errors because its generated ConfigMap exceeded 1,048,576 bytes. These are constraints of this generated configuration and filter-bearing route shape, not proof of a universal bare-route limit. Increasing pod memory would not alter either constraint.

The [attribution review](../evidence/qualification/final-facts/kubernetes-attribution.json) ties each diagnostic to a replacement pod created during that phase and restricts API errors to that phase’s timestamps. It also retains the six process-namespace collection gaps during these crashing scale scenarios; no HTTP measurement window has those gaps.

## Graceful restart observations

A separate probe schedules ten health requests/sec. The controller scenario rolls both controller replicas; the data-plane scenario deletes the sole gateway pod with normal Kubernetes termination. Reported recovery is the first sampled success after the last observed post-mutation failure, relative to mutation start. If no failure occurs, recovery latency is not inferred.

| Implementation | Pass | Mutation | Failed probes / total | Pre-mutation failures | Observed recovery seconds | Maximum dispatch delay seconds |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| Agentgateway v1.6.0 | 1 | controller | 0/262 | 0 | No failures observed | 0.049 |
| Agentgateway v1.6.0 | 1 | data-plane | 0/228 | 0 | No failures observed | 0.025 |
| Agentgateway v1.6.0 | 2 | controller | 0/251 | 0 | No failures observed | 0.048 |
| Agentgateway v1.6.0 | 2 | data-plane | 0/230 | 0 | No failures observed | 0.024 |
| Agentgateway v1.6.0 | 3 | controller | 0/251 | 0 | No failures observed | 0.049 |
| Agentgateway v1.6.0 | 3 | data-plane | 0/222 | 0 | No failures observed | 0.024 |
| Praxis core v0.5.2 | 1 | controller | 0/236 | 0 | No failures observed | 0.048 |
| Praxis core v0.5.2 | 1 | data-plane | 34/244 | 0 | 4.276 | 0.024 |
| Praxis core v0.5.2 | 2 | controller | 0/237 | 0 | No failures observed | 0.047 |
| Praxis core v0.5.2 | 2 | data-plane | 37/241 | 0 | 4.476 | 0.024 |
| Praxis core v0.5.2 | 3 | controller | 0/227 | 0 | No failures observed | 0.049 |
| Praxis core v0.5.2 | 3 | data-plane | 33/240 | 0 | 3.776 | 0.024 |

Across the three Praxis graceful-deletion windows, observed recovery after mutation is 4.176 [3.776–4.476] seconds. Agentgateway has no observed failure in these windows, so its recovery latency is not assigned zero.

See [every recovery row](data/recovery-rows.json) and [three-pass summaries](data/recovery-summary.json). The HTTPX probes reuse connections. Graceful termination may overlap a draining pod and its replacement, and the window can end while the old process remains. These probes do not establish complete traffic handoff or fresh-connection availability. Steady-state HTTP tests separately enforce one stable pod before load. The observations are not an HA or hard-failure guarantee. Probe timing is quantized by the 100 ms schedule; command completion and traffic recovery are different events.

## Core nightly/operator compatibility

All three current setup attempts preserve the stock operator configuration and exact nightly digest. The operator produces cluster name `gateway-backend~backend~8081`; core nightly rejects the `~` characters and exits 1. HTTP, scale and recovery behind this pairing are **not evaluated**. Do not label the dependent cases individual failures or record zero throughput. Standalone nightly forwarding is measured separately.

[Setup-block evidence](data/setup-blocks.json) retains image, process-exit, node readiness and generated-configuration details. The earlier expanded-conformance attempt also encountered empty-router startup incompatibility. No silent operator or data-plane patch was applied to improve either product’s score.

## Validity

The [review](../evidence/qualification/final-review.json) approves this three-pass Kubernetes evidence family; standalone CPU profiles have separate measurements. It records 96 startup checks, 126 HTTP load cases, no load-tool/HTTP errors or resets, 23 Nighthawk requests in flight at cutoff, and unchanged installed inputs. The recurring Praxis controller restart counters predate HTTP; both controller processes remain stable during each HTTP window.

The default-TCP and startup-drain Kubernetes pilots, image-switch qualification, and interrupted-fixture attempts are excluded in full. Only the corrected, reviewed three-pass campaign contributes to current performance/scale/recovery tables. See [methodology and exclusions](05-methodology-and-validity.md) and [reproduction](../docs/REPRODUCE.md).
