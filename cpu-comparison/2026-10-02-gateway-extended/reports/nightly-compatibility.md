# Praxis nightly: empty-Gateway compatibility finding

**October 5 interpretation correction:** the retained static-address assertion is a known
upstream v1.5.1 test race; the corrected v1.6.1 case passes in agentgateway CI.
See the [investigation](agentgateway-static-address-follow-up.md). Original scores remain unchanged.

**Complete: three separate measured pairs.** All three Praxis nightly attempts
stopped during setup with the same empty-router failure; individual feature coverage
was not evaluated. Each fresh agentgateway v1.6.0 reference run passed 106/107,
with identical individual outcomes and the retained `GatewayStaticAddresses` failure.

| Product | Repetition 1 | Repetition 2 | Repetition 3 | Mean passing cases |
| --- | --- | --- | --- | --- |
| Agentgateway v1.6.0 | 106/107 | 106/107 | 106/107 | 106.0 |
| Praxis nightly-20261002 + operator fb8beaa | Setup blocked; 107 not evaluated | Setup blocked; 107 not evaluated | Setup blocked; 107 not evaluated | Not available |

Agentgateway's passing-count range is 106–106 and sample standard deviation is zero.
The nightly has no feature-score mean. Its three setup attempts each lasted 302
seconds, including the unchanged 300-second prerequisite; this is not a gateway
performance measurement. See [aggregates](data/aggregate.json) and the per-case matrices.


The pinned nightly-20261002 image exits when the current stock Praxis operator
creates the upstream suite's initially route-less Gateways. The data-plane log says:

```text
fatal error; exiting ... router: 'routes' is empty; every request would fail with 404
```

All four base Gateway data-plane pods failed to start; their Gateway status remained
Programmed=False/Pending. The suite stopped at its 300-second readiness prerequisite
before executing HTTPRouteSimpleSameNamespace. Fixtures were running, nodes were
ready, and the same workflow passed with the operator's default core v0.5.2 pairing.

The image's embedded application version says 0.7.2. Its **nightly** identity is
established by the requested immutable digest and OCI revision
31ac6dc86fba30ff510b17f9139021de60d8ba79, not that shared application version string.
See [selection metadata](../evidence/versions/selection.json).

The exact pinned [router implementation](https://github.com/praxis-proxy/praxis/blob/31ac6dc86fba30ff510b17f9139021de60d8ba79/crates/filter/src/builtins/http/traffic_management/router/mod.rs#L249)
rejects an empty routes list with that same error. The operator documents its image
override, but its default remains core 0.5.2. This is evidence of an incompatible
**initially empty Gateway workflow with this operator/image pairing**. It does not
establish that the nightly cannot serve a preconfigured nonempty route, nor does it
measure the nightly's standalone AI-gateway capabilities.

Evidence is retained under
`results/praxis-nightly-20261002/qualification/praxis/nightly-dataplane.log` and
`nightly-config.json`, alongside the raw upstream setup output and runtime
snapshots in the [technical archive](../README.md#raw-evidence).
Generated fixture TLS private keys are redacted; router configuration and
observed outcomes are unchanged. The redaction ledger preserves original and
sanitized file hashes.

Do not convert this setup failure into “0/107 tests passed” or compare an assumed
nightly feature score against agentgateway. Individual test coverage is unavailable
until the stock pairing can complete the prerequisite. Adding placeholder routes,
editing operator translation, or modifying the test fixture would create a different
experiment and is outside this stock-version comparison.

## Repeated evidence and validity

Each attempt used the immutable image selected October 2 at 23:20 UTC, the latest
published nightly at that freeze. Moving tags were not re-resolved between runs.
The initial qualification is separate from the three measured attempts.

| Attempt | Setup/configuration review | Runtime review |
| --- | --- | --- |
| 1 | [Four empty configurations and four fatal startup logs](../evidence/validity/nightly-praxis-pass1-setup.json) | [Health and restarts](../evidence/validity/nightly-praxis-pass1-runtime.json) |
| 2 | [Four empty configurations and four fatal startup logs](../evidence/validity/nightly-praxis-pass2-setup.json) | [Health and restarts](../evidence/validity/nightly-praxis-pass2-runtime.json) |
| 3 | [Four empty configurations and four fatal startup logs](../evidence/validity/nightly-praxis-pass3-setup.json) | [Health and restarts](../evidence/validity/nightly-praxis-pass3-runtime.json) |

All attempts completed cleanup. Each had ten runtime snapshots, no node-health or
API-collection errors, and all observed backend fixture pods Ready in the late
setup snapshot. All four data planes repeatedly exited with code one and the
empty-router error. Each attempt also recorded one operator startup exit with
`LeadershipLost`; those logs are retained separately. The reference runs had no
observed container restarts. Final host review and excluded infrastructure attempts
are documented in the campaign's evidence and infrastructure reports.

The operator's default v0.5.2 pairing completed setup and all selected cases in
its [separate release comparison](release-comparison.md). This isolates a useful
compatibility finding, but does not prove which implementation change should fix it.
Reproduce with [the pinned configurations and commands](reproduce.md), without
adding placeholder routes or patching the operator inside a measured repetition.

See the [final host and archive validity review](infrastructure-validity.md).
