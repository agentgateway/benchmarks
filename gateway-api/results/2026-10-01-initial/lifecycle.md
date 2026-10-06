# Initial Gateway API lifecycle observations

One execution per implementation/case, in agentgateway-then-Praxis order, on the resource-normalized single-node kind VM. These observations are separate from core conformance and from steady-state HTTP saturation. No repeated-run variance is available.

## Attach and remove 1,000 routes

| Suite metric | Agentgateway | Praxis |
| --- | ---: | ---: |
| Workload creation ready time | 8.593 s | 12.981 s |
| `add-all` residual after workload ready | 4.735 ms | 1.866 s |
| Creation start to all attached, derived sum | 8.597 s | 14.847 s |
| `remove-all` residual after teardown starts | 7.945 s | 5.827 s |
| Observed Gateway update samples (`writes` in suite) | 2,000 | 25 |

Both cases completed. `add-all` is not the time to create 1,000 routes: the suite subtracts workload creation time before reporting it. Do not advertise the 4.735 ms figure as complete 1,000-route creation or divide the residual values into a universal speedup. The `writes` field counts informer observations of the Gateway, not independently instrumented API-server write operations. Praxis's fewer observed updates and faster removal are retained alongside agentgateway's faster attachment observation.

## First-200 propagation for 1,000 sequential route creations

Agentgateway completed all 1,000 probes, with total recorded probe time 13.06563393 s and maximum 23.406894 ms. The arithmetic mean is **13.066 ms**. These timings begin after the route apply call returns and end at the first HTTP 200. They exclude apply time and do not prove stable success after convergence.

Praxis's execution stopped at route 0 with a connection reset at `2026-10-02T02:53:40.874610Z`. No successful latency sample was recorded. Report this as a failed attempt with **unavailable latency distribution**, not zero latency, infinite latency, or a quantified speedup. The upstream probe fails immediately on a transport error and does not retry it; HTTP 404s are retried. Gateway/pod rollout evidence is retained, but one attempt does not establish the frequency or general cause of the reset.

## Continuity through 1,000 route changes

Both implementations reached change 999 and completed. The suite reported 665,515 request iterations for agentgateway and 725,065 for Praxis. That counter includes initial readiness polling; it is not a separately validated count of successful timed requests and is not an equal-duration throughput score.

The workload alternates a backend port and a backend-reference response-header modifier with the suite's default 200 ms grace period. The active probe checks HTTP-200 continuity. It does **not** assert that each intermediate version was served, measure per-update convergence, or validate every changed header. These outcomes support the tested continuity property only.

## Scale/churn

All four scale/churn intervals reached their scheduled ten-minute stop and exited with code 0 after SIGINT cleanup. This means the load process completed, not that each product successfully programmed every route. The source logs and snapshots are in `gateway-lifecycle/` and `scale-observations/`.

| Product | Requested routes | Checkpoint | Actual routes | Accepted=True | ResolvedRefs=True | All conditions current | No conditions |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| agentgateway | 1,000 | 5 min | 1,000 | 1,000 | 1,000 | 1,000 | 0 |
| agentgateway | 1,000 | 9 min | 1,000 | 1,000 | 1,000 | 1,000 | 0 |
| agentgateway | 5,000 | 5 min | 5,000 | 5,000 | 5,000 | 5,000 | 0 |
| agentgateway | 5,000 | 9 min | 5,000 | 5,000 | 5,000 | 5,000 | 0 |
| Praxis | 1,000 | 5 min | 1,000 | 5 | 0 | 2 | 995 |
| Praxis | 1,000 | 9 min | 1,000 | 5 | 0 | 1 | 995 |
| Praxis | 5,000 | 5 min | 5,000 | 243 | 0 | 236 | 4,757 |
| Praxis | 5,000 | 9 min | 5,000 | 243 | 0 | 219 | 4,757 |

“Current” means every recorded condition has observedGeneration equal to metadata.generation. It does not mean those conditions are True; read acceptance and resolution separately. Agentgateway had all routes accepted, reference-resolved and current in every checkpoint. Praxis's recorded conditions were Accepted=True alongside ResolvedRefs=False/BackendNotFound. Its 1,000-route Gateway nevertheless reported 1,000 attached routes and Programmed=True. Attached count is not proof of current per-route acceptance or traffic success.

A later 1,000-route diagnostic snapshot found all five referenced Services present with the requested port. A later 5,000-route Service snapshot likewise contained all 243 referenced backend names from the five-minute routes with conditions. The pinned operator gates successful route status on an unchanged configuration hash and a completed proxy Deployment rollout (`src/controller/gateway.rs`, `can_accept_routes`, revision `fb8beaa`). Continuous churn may prevent that gate opening. This is a source-based explanation to investigate, not an experimentally isolated root cause for the 1,000-route observation. The separate 5,000-route ConfigMap rejection is directly recorded below.

The corpus creates synthetic Services/pods and changes configuration every second with workload jitter every two seconds. It does not test real backend health or per-route traffic. No claim that Praxis cannot serve 1,000 static routes follows from these snapshots. No repeated execution, quiescence/recovery experiment or maximum-route threshold search was performed.

## ConfigMap rejection at 5,000 routes

Praxis's operator log at `2026-10-02T03:37:15Z` records Kubernetes HTTP 422 rejecting `ConfigMap praxis-praxis`: `Too long: may not be more than 1048576 bytes`. The retained `praxis-scale-5000-operator.log` and final controller logs contain the errors. The pinned operator [serializes the Gateway configuration into one ConfigMap](https://github.com/praxis-proxy/operator/blob/fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c/src/resources/configmap.rs#L18); [Kubernetes limits a ConfigMap to 1 MiB](https://kubernetes.io/docs/concepts/configuration/configmap/).

Configuration updates were therefore rejected during this 5,000-route fixture. This is a concrete configuration-delivery limit for the tested operator and route shapes, distinct from the 1,000-route status/churn observation. It does not identify a universal maximum route count: serialized size depends on route/backend complexity, and this run did not search for a threshold or test alternative configuration partitioning. A ten-minute process completion does not turn that rejection into a successful scale result.

## Resource samples

[`resources.json`](resources.json) contains per-interval sampled namespace maxima for container working set and CPU usage. Fourteen initial collector error rows are retained and excluded from calculations. Working set is not RSS, five-second samples do not establish true peaks, and container records can include rolling or recently terminated containers. Windows include setup/cleanup and both controllers remain installed. The incomplete Praxis scale configuration also makes an efficiency ranking at requested scale invalid. Use the data for diagnosis, not a memory-efficiency headline.

## Interpretation

Agentgateway's first-response propagation corpus completed; Praxis's did not produce samples. Both passed the update-continuity case. Attachment and removal show different tradeoffs. Preserve these distinctions instead of collapsing them into a single Gateway API score. The cluster's extra TCP load-balancing hop, shared CPU, prior-case teardown, fixed ordering and default memory cap limit generalization. Five/nine-minute API snapshots add monitoring overhead; extra diagnostic reads were performed after anomalies in the Praxis scale cases. The community suite is a useful operational test, not certification of arbitrary production behavior.
