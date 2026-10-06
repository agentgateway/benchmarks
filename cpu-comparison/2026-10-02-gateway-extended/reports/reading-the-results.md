# What this campaign establishes

**October 5 interpretation correction:** the retained static-address assertion is a known
upstream v1.5.1 test race; the corrected v1.6.1 case passes in agentgateway CI.
See the [investigation](agentgateway-static-address-follow-up.md). Original scores remain unchanged.

The earlier 33-case result covered a selected HTTP core subset. Passing that subset
does not establish equivalent Gateway API coverage. Extended features are optional
under the specification, but can be required for a particular customer's deployment.
This campaign applies the same upstream tests to both implementations, including
features that an implementation does not claim to support.

The expanded selection has 107 top-level cases: 33 HTTP core, 54 HTTP/Gateway
extensions and backend TLS, five gRPC cases, and 15 TLS-dependent cases (including route-kind validation). These are test
counts, not counts of independently supported features. Multiple cases exercise the
same feature, and a case can require several features. The inventory contains 43
feature-selection flags. Two selected cases depend on experimental-channel features;
ten carry the upstream provisional marker. The per-case matrices expose these flags.

## Read the two comparisons separately

- The release comparison pairs agentgateway v1.6.0 with Praxis core v0.5.2 and the
  pinned current Praxis operator.
- The development comparison pairs separately measured agentgateway v1.6.0 reference runs
  with the same operator and the immutable nightly-20261002 Praxis core image.

The operator is part of the Praxis implementation under test: a standalone proxy
does not reconcile Gateway API resources. These results therefore concern the
specified operator/core pairing. They do not attribute every observed limitation to
the Praxis proxy binary, nor establish which features a custom configuration could
implement outside Gateway API.

The nightly pairing currently fails the suite's initial empty-Gateway prerequisite.
That is a compatibility finding, not 107 individual feature failures. Its feature
coverage remains **not evaluated** unless that prerequisite succeeds. The release
comparison remains independently interpretable.

## Read repetitions as evidence of repeatability

Each matrix cell records pass, fail, skip, or not executed for each repetition.
Only complete three-run sets receive a mean passing-test count. A fraction such as
106/107 means the selected assertions passed; it is not a percentage of the entire
Gateway API specification. A feature that passed in three runs can still have
untested configurations or bugs. Passing a negative test, such as rejecting an
unsupported listener configuration, does not demonstrate successful TLS routing.
Use the positive routing cases alongside rejection/status checks when discussing
feature support. Both implementations passed the separate HTTP-core
`HTTPRouteHTTPSListener` case; TLSRoute findings must not be generalized into
a claim that Praxis cannot terminate HTTPS for HTTPRoute.

Do not compare the elapsed duration of these correctness runs as gateway speed.
Failed assertions spend time in upstream readiness and consistency waits, so a
longer suite duration primarily reflects those waits. Throughput, request latency,
resource efficiency, route-update latency, and AI-gateway behavior require their own
experiments. The earlier performance campaigns remain separate.

## Use the findings in customer discussions

Start with the customer's required resources and behaviors: gRPC routing, TLS
passthrough, backend certificate validation, rewrites, matching, mirroring, or
listener isolation. Link the corresponding test rows and pinned configuration.
Distinguish an implementation's documented unsupported feature from an unexpected
behavioral failure, and disclose agentgateway failures with the same specificity.

Avoid claims such as “fully conformant,” “all extended features,” or “the nightly
supports nothing” based on this experiment. It is an evaluator-selected
coverage comparison, not an official conformance certification. The evidence is
strongest when attached to the exact behavior, versions, test source, and repetition
results that support it.

The [failure excerpt index](data/failure-excerpts.json) records a source filename,
line number and a short assertion or terminal-output excerpt for each failed
case/run. These excerpts help locate evidence; they are not automatic root-cause
classifications. Complete output and runtime context remain in the raw evidence archive.

## Documentation discrepancies confirmed in all three release runs

The pinned Praxis support document says rewrites and route timeouts are unsupported,
but v0.5.2 with the pinned operator passed `HTTPRouteRewriteHost`,
`HTTPRouteRewritePath`, `HTTPRouteTimeoutBackendRequest`, and
`HTTPRouteTimeoutRequest` in all three measured release runs. These passes remain credited.
The document also understates operational functionality such as leader election.
Use measured cases as the primary evidence; documentation is context and can be
stale. Do not repeat its unsupported-feature claims where the observed tests
contradict them.
