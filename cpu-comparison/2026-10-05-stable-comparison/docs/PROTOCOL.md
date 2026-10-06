# Protocol and recorded amendments

- Exact agentgateway v1.6.0 and both Praxis core digests are inherited from the
  October 2 selection ledger; tags are not re-resolved to newer code.
- Three n2-standard-8 GCP VMs in solo-oss/us-central1-a separate client, gateway,
  and deterministic backend. No managed load balancer, Envoy proxy, GPU, or
  provider API. Nighthawk is a load generator only.
- Equal common profile: HTTP forwarding, 2 pinned vCPUs, two gateway workers,
  2 GiB limit, no access logging or provider transformations. The direct path
  omits the gateway. Both API shapes and streaming are transport workloads.
- Fortio v1.75.3, AIPerf 0.13.0 and pinned Nighthawk retain the previous campaign's
  sizes, rates, warmups and durations. The translation workload is excluded
  from the common profile because it requires native AI functionality.
- Measure three passes with treatment order rotated. Review first-pass tool,
  host and protocol evidence before proceeding. Product failures remain results;
  infrastructure failures invalidate affected measurements and are retained.
- Standalone containers and load-generator processes use open-file limit 65536.
  Kubernetes gateway/backend/controller processes inherit 1048576 from K3s.
  Both gateways receive the same limits within each profile. Apply the same
  expanded ephemeral-port/TIME_WAIT profile to all hosts. Freeze automatic package maintenance before qualification.
- Report every individual pass, arithmetic mean and range, error count and
  achieved rate. Three repetitions on one placement are not independent clouds.
- Preserve immutable evidence and tool/config hashes. Do not pool older version
  results or mark blocked Gateway API setup as individual feature failures.
- Explicitly delete all campaign-created infrastructure after evidence export;
  a 12-hour instance auto-delete is a fallback. Budget remains $2,000 total.

## Native AI profile

The user approved adding the separate Praxis AI distribution. Run agentgateway
v1.6.0 versus Praxis AI v0.5.0, the October 2 AI nightly and direct service,
three repetitions, on the same
standalone topology, after stopping all common-profile gateways. The literal dated AI tag
is absent; the October 2 build was recovered through its successful scheduled
workflow and retained `sha-f5f51a7` tag, with matching image-index digest.

Retain the prior native profile's OpenAI, Anthropic and Anthropic-to-OpenAI
translation configurations, sizes/rates/stream concurrency and correctness
checks. Praxis token_count is enabled, while agentgateway uses its LLM pipeline.
These are explicitly different implementations of the configured functionality;
native-profile ratios do not isolate equal token-accounting work or prove a
universal efficiency ranking. Use the common forwarding profile for matched
transport work. Retain and report successful throughput, errors and latency for
both profiles separately.

## Qualification exclusions

The first common-profile Praxis release startup failed because the harness
appended `-c /etc/config.yaml` to an image entrypoint that already included
`praxis -c /etc/praxis/config.yaml`. No load measurement ran. Override the core
image entrypoint with `praxis` and supply exactly one config argument. Retain
this startup failure as a harness exclusion and rerun all common qualification
under `qualification-v2`; do not count it as a product failure or repetition.

The second qualification also stopped before Praxis load: the draft common
configuration used `filter_chain`/map syntax instead of Praxis's documented
`filter_chains` list and `filter` entries. The corrected configuration is derived
from the previously qualified native profile's router/load-balancer entries.
Both exact core images then independently returned the expected health response.
`qualification-v3` passed before the seed correction; `qualification-seeded`
passed next. Final acceptance uses `qualification-nohealth`, which disables
inherited probes and includes the recovered October 2 AI nightly. Earlier attempts remain
excluded harness-development evidence. No failed readiness attempt is a measured
repetition or a product capability finding.

## Frozen AIPerf corpus

Use `--random-seed 42` for every AIPerf invocation, all treatments and repetitions.
The initial partial common-profile direct-baseline run was stopped before any
gateway performance treatment to make this setting explicit; the entire pilot
is retained but excluded, including its unchanged Fortio cases. No gateway
performance outcome informed this exclusion. Kubernetes cases are unaffected.
Requalify the seeded CPU profiles and restart accepted pass1 in a fresh output
directory. Retain each generated corpus and verify input/output lengths.

The accepted common-profile orders are direct/agentgateway/release/nightly,
agentgateway/release/nightly/direct, and release/nightly/direct/agentgateway.
Each treatment occupies three different positions; three repetitions cannot
fully balance four treatment positions. Native AI uses direct/agentgateway/AI-release/AI-nightly,
agentgateway/AI-release/AI-nightly/direct, and AI-release/AI-nightly/direct/agentgateway.
It has the same four-position balancing limitation. Kubernetes retains its predeclared orders;
among runnable implementations these rotate direct/agentgateway/release through
all three positions, with the nightly setup attempt retained in each pass.

## Kubernetes TCP qualification correction

The first incomplete Kubernetes pass used default host and pod TCP settings
(range 32768–60999, TIME_WAIT reuse 2), despite the intended expanded profile.
Praxis core v0.5.2 returned 502 at unlimited rate/512 connections; its logs show
outbound `BindError`, errno 99. The **entire Kubernetes pilot**, including successful
agentgateway and direct measurements, is excluded. Do not rank products with it.
Standalone containers use host networking and already had the intended settings.

Apply the standalone TCP profile to all five Kubernetes hosts and all new pod
network namespaces. Chain the upstream CNI `tuning` plugin v1.8.0 after Flannel;
verify its downloaded archive against the recorded SHA-256. Recreate the backend
before qualification. This applies uniformly to both products and replacement
pods; it changes the environment, not generated gateway configurations. The
[upstream tuning documentation](https://www.cni.dev/plugins/current/meta/tuning/)
describes namespace-level sysctl configuration.

`qualification-tcp` includes both response sizes at 512 connections/unlimited
rate for 30 seconds, plus Nighthawk, ten-route mutations and recovery. Retain
pod namespace settings and socket counters in host samples. Only after reviewing
this qualification may a fresh Kubernetes pass1 start. If K3s restarts, reapply
and verify the CNI chain before measuring; this campaign does not restart nodes.

The first corrected TCP qualification passed its direct and agentgateway HTTP
checks but stopped before scale mutations: interrupting the earlier pilot had
left ClusterLoader2's temporary `gwcmp-cl2-*` namespace. The tool correctly
rejected a pre-existing namespace. Capture and remove that campaign-owned
namespace, retain the entire failed qualification, and restart qualification.
This is interrupted-harness cleanup, not an agentgateway route failure. See
`evidence/qualification/kubernetes-stale-cl2-exclusion.json`.

## Standalone health-check alignment

Praxis images inherit a five-second Docker healthcheck against port 9901, which
is not enabled in the minimal profiles. Agentgateway has no inherited probe.
Disable inherited healthchecks (`--no-healthcheck`) and requalify before any
Praxis measured treatment. External readiness, protocol and cancellation checks
remain identical. The already-started seeded direct and agentgateway treatments
are unchanged and retained: no Praxis container was active during them and
neither had this probe. This is a configuration correction before measuring the
affected treatments, not a post-result optimization or exclusion of a slow run.
The earlier qualification inspect and corrected inspect are both retained.

## Route failure attribution snapshots

A read-only watcher captures configuration, pod/current-previous logs, events and
controller logs once during each sustained Praxis route-scale nonconvergence
window. It does not alter product settings, inject workload requests, or decide
whether the final route observation passes. These snapshots supplement the
controller logs and placement records captured for every implementation by the
measured runner. Only final current-generation status and all-route traffic
observations determine convergence. The watcher does not run on standalone hosts.

## Single-pod startup barrier correction

First-pass review found a draining old Praxis pod alongside its replacement in
the pre-HTTP placement record. Host samples showed the old process almost idle,
but the setup had only waited for readiness rather than enforcing the declared
one-pod topology. Endpoint eligibility was not captured, so no throughput effect
is asserted. The **entire Kubernetes attempt for every treatment** is retained
and excluded as `results/excluded/kubernetes-startup-drain-pilot`.

The corrected setup requires exactly one nonterminating Ready gateway pod, a
fully observed one-replica deployment, and exactly one Ready nonterminating
EndpointSlice address matching that pod. The identity/topology must stay stable
for ten seconds before endpoint qualification. Both implementations receive the
same barrier. The `qualification-single-pod` attempt is retained but excluded
for the separate image-switch issue below. Accepted qualification uses
`qualification-image-pin`, followed by a fresh complete Kubernetes pass1 before
repetition approval. Standalone CPU
measurements and the separate focused static-address pass1 are unaffected.

The document records actual amendments and exclusions; it is not a claim of
formal preregistration. Product limitations remain outcomes. No excluded result
contributes to accepted averages.

## Requested-image startup barrier correction

The next qualification exposed an image-selection race: the nightly treatment's
operator template requested nightly, but its stable Ready pod still ran the
release digest. A later snapshot contained both release and nightly pods. The
qualification was stopped and excluded in full. This is an infrastructure setup
error, not evidence that nightly successfully passed any measured case.

Treatment switching now stops both controllers and waits for all their pods to
disappear before changing configuration and starting the selected controller.
The common startup barrier also requires the requested data-plane digest in both
the deployment and running container status. Rollout readiness alone is not an
image identity guarantee. The retained snapshot does not establish exact leader
handoff timing; that causal detail is not asserted. See the
[exclusion record](../evidence/exclusions/kubernetes-image-switch-pilot/exclusion.json).

The first `qualification-image-pin` attempt stopped at ClusterLoader2's
pre-existing-namespace guard. Interrupting the preceding qualification had left
`gwcmp-cl2-1`; route cleanup did not remove this separate temporary fixture.
The whole attempt is excluded as
`results/excluded/kubernetes-image-pin-stale-cl2-qualification`. Its namespace
identity was captured before explicit deletion, then the complete qualification
was restarted unchanged. This repeats an interrupted-fixture cleanup failure;
it does not change any product configuration or route-scale parameters.
