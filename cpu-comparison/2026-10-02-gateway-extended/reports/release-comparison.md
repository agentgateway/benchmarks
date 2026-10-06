# Agentgateway v1.6.0 versus Praxis v0.5.2

**Complete: three measured pairs, with identical case-by-case outcomes in every
repetition.** Agentgateway passed 106 of 107 selected cases; Praxis passed 52.
Both passed all 33 selected HTTP core cases. The expanded selection therefore
shows broader tested Gateway API coverage for agentgateway in these versions.

| Product | Repetition 1 | Repetition 2 | Repetition 3 | Mean passing cases |
| --- | ---: | ---: | ---: | ---: |
| Agentgateway v1.6.0 | 106/107 | 106/107 | 106/107 | 106.0 |
| Praxis core v0.5.2 with operator fb8beaa | 52/107 | 52/107 | 52/107 | 52.0 |

The passing-count range is 106–106 and 52–52 respectively; sample standard deviation
is zero for both. Every individual case also had the same outcome across its three
runs. This describes repeatability, not confidence that untested configurations work.
[Machine-readable aggregates](data/aggregate.json) retain all repetition outcomes.

The tested Praxis implementation is operator
`fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c` with core v0.5.2, not a custom standalone
Praxis configuration. All product images and the suite are pinned in
[version selection](../evidence/versions/selection.json). Praxis v0.5.2 was published
August 10, more than two weeks before selection; the requested nightly pairing has
its own [separate report](nightly-compatibility.md).

## Where the results differ

| Selected case group | Cases | Agentgateway passes, each run | Praxis passes, each run |
| --- | ---: | ---: | ---: |
| HTTP core | 33 | 33 | 33 |
| HTTP/Gateway extensions and backend TLS | 54 | 53 | 17 |
| gRPC | 5 | 5 | 0 |
| TLS-dependent, including route-kind validation | 15 | 15 | 2 |
| **Total** | **107** | **106** | **52** |
| Standard-channel cases | 105 | 104 | 51 |
| Experimental-channel cases | 2 | 2 | 1 |

Channel rows partition the total; they are not additional tests. Across the 74 cases
beyond the HTTP-core subset, agentgateway passed 73 and Praxis passed 19 in each run.
Ten selected cases are provisional: agentgateway passed all ten, Praxis passed five.
Case counts are not percentages of the entire specification or counts of distinct
features. The 55 failed Praxis cases are not 55 distinct defects: several stop at
the same unsupported resource or prerequisite.

The selection adds distinctions the core subset does not exercise:

- All five gRPC cases passed for agentgateway and failed for Praxis.
- Positive TLSRoute routing cases passed for agentgateway and failed for Praxis.
  Praxis's two TLS-dependent passes were rejection tests for unsupported listener
  termination modes; they do not establish successful TLSRoute routing. Both products
  passed the separate HTTP-core `HTTPRouteHTTPSListener` case, so this is not a
  claim that Praxis cannot terminate HTTPS for HTTPRoute.
- Agentgateway passed the selected backend certificate-validation, client-certificate,
  ListenerSet, CORS, method/query matching, and mirroring checks that failed for Praxis.
- Praxis passed meaningful extensions, including host/path rewrites and request/backend
  timeouts. Its pinned support document understates these capabilities. Credit the
  observed passes instead of repeating outdated unsupported-feature claims.

See the [HTTP extension](matrix/http-gateway-extended.md), [gRPC](matrix/grpc.md),
[TLS-dependent](matrix/tls.md), and [HTTP core](matrix/http-core.md) matrices for exact
cases, pinned source links, provisional flags, and individual repetition outcomes.
The [assertion index](data/failure-excerpts.json) provides raw-log locations and short
failure excerpts; it does not automatically classify root causes.

## Agentgateway's retained failure

`GatewayStaticAddresses` failed in all three measured runs under conformance v1.5.1.
**October 5 correction:** this older test has a known upstream eventual-consistency
race, fixed in Gateway API PR #5033. Agentgateway CI uses conformance v1.6.1 and
explicitly passes this case on the exact v1.6.0 product revision. The observed
transient ready status without an address is not, by itself, an implementation
defect. See the [CI investigation and correction](agentgateway-static-address-follow-up.md).
The original 106/107 results remain unchanged. This historical campaign did not rerun the corrected suite; see the [separate focused follow-up](../../2026-10-05-stable-comparison/reports/03-gateway-api.md).

## Validity and exclusions

All six measured jobs produced upstream reports, completed all 107 selected cases,
and finished namespace cleanup. [Runtime reviews](../evidence/validity/) recorded
no node health/pressure issues or API collection failures. Praxis operator exits
logged `LeadershipLost`: one in repetition one, three in repetition two, and two in
repetition three. Several occurred after startup. Their logs are retained; the root
cause of the leadership changes is not established.

Runtime snapshots also observed three, three, and one data-plane exit-137 terminations
respectively. Each observed pod was already marked for deletion, had restartCount=0,
and was reported as Error rather than OOMKilled. These rollout/cleanup observations
remain in the validity records. They are not presented as active-process OOM failures.

Two repairs are fully disclosed:

1. The initial agentgateway attempt under the default client TCP retry profile was
   excluded after a diagnosed Service-startup connection issue. Every measured run
   uses the repaired shared profile; the upstream binary, assertions and per-test
   timeouts are unchanged. See [the transport investigation](infrastructure-investigation.md).
2. Automatic host maintenance interrupted the original third Praxis attempt. The
   **entire third pair** was replaced after update timers were frozen. The completed
   original agentgateway half is retained as superseded, alongside the interrupted
   Praxis half. Host package changes and audit windows are documented in the
   [maintenance investigation](maintenance-interruption.md).

Praxis's measured suite durations were 174m41s, 170m22s, and 170m39s; agentgateway's
were 3m56s, 4m28s, and 4m37s. These durations are **not gateway speed measurements**:
failed and unsupported cases spend time in upstream readiness/consistency waits.
No throughput, inference-speed, or resource-efficiency conclusion follows from them.

This is an evaluator-selected coverage comparison performed for Solo.io, an
agentgateway contributor. It is not an independent third-party assessment or
an official vendor conformance certification. Read the [methodology](methodology.md),
[reproduction steps](reproduce.md), and [interpretation guide](reading-the-results.md).

See the [final host and archive validity review](infrastructure-validity.md).
