# Static-address CI discrepancy: corrected interpretation

**October 5 correction:** `GatewayStaticAddresses` runs and passes in agentgateway
CI. Our campaign used an older upstream test containing a known eventual-consistency
race. The earlier recommendation to fix agentgateway's condition/address publication
was not justified by that observation alone and is withdrawn.

## Direct CI evidence

| Revision | CI date | Test result | Job |
| --- | --- | --- | --- |
| v1.6.0 release `ea560864` (the exact benchmark product revision) | October 2 | PASS, 0.34 seconds | [Release CI](https://github.com/agentgateway/agentgateway/actions/runs/37027877882/job/110907035317) |
| `a9e2404c` | October 5 | PASS, 0.67 seconds | [Recent CI](https://github.com/agentgateway/agentgateway/actions/runs/37330195266/job/111831058271) |

These are explicit per-test PASS lines, not an inference from a green overall job.
[Saved excerpts](../evidence/static-address-ci/ci-verification.json) include job URLs,
commit identities, log line numbers and full downloaded-log hashes.

The [release harness](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/controller/test/conformance/conformance_test.go#L65-L86)
selects an available MetalLB IP and enables the test. If address discovery fails,
`CI=true` makes setup fail. Only non-CI execution falls back to skipping this test.
The Makefile's optional skip list defaults to empty; the verified jobs ran the case.
Messages saying a Gateway is skipped *for setup* are a separate fixture-readiness
mechanism and do not mean this conformance case was skipped.

## The decisive difference is the suite version

The release [Go module](https://github.com/agentgateway/agentgateway/blob/ea5608642b9d5c94c5baf5fd9f2f9849b808e963/go.mod#L61-L64)
uses Gateway API v1.6.2 and the separately versioned **conformance v1.6.1** module.
Our comparison deliberately pinned Gateway API/conformance **v1.5.1** for both
products. That pin predates the static-address test fix.

| Assertion behavior | Benchmark v1.5.1 | CI conformance v1.6.1 |
| --- | --- | --- |
| Read Gateway | Before final condition/listener checks | Repeated GET after those checks |
| Wait for the actual address field | No | Yes, using GatewayMustHaveAddress (default 180 seconds), polling every 100 ms |
| Assert assigned address and type | Against an earlier snapshot immediately | Against refreshed status after an address appears |

The newer test also permits parallel execution. The address wait is the directly
relevant assertion change; see the [exact source diff](../evidence/static-address-ci/test-diff.patch).

Upstream [PR #5033](https://github.com/kubernetes-sigs/gateway-api/pull/5033), merged
July 1 as [022ffb57](https://github.com/kubernetes-sigs/gateway-api/commit/022ffb57fc7772335372a7297de4008a07e90e27),
fixes this specific assumption: ready conditions and address publication need not
appear atomically. The test must wait for the field it asserts. The fixed
[test source](https://github.com/kubernetes-sigs/gateway-api/blob/8bb74df00e56ec8f944d48c25e6c1c9c2f6848e3/conformance/tests/gateway-static-addresses.go#L137-L146)
contains that wait.

## How it matches our evidence

In release repetition one, the old test created the Gateway at 00:04:08.766 UTC,
passed its final condition checks, asserted against an empty address list, and
deleted the Gateway at 00:04:09.121 UTC. The controller log then reported a missing
Service at 00:04:09.214 UTC, after test cleanup had already begun. This is not an
observation of failure to assign the IP throughout an address-readiness timeout.
The remaining measured runs failed at the same address assertion.

The excluded passive diagnostic captured generation 3 with `Accepted=True`,
`Programmed=True`, and no `status.addresses`, followed immediately by deletion.
[Its timeline](../evidence/qualification/static-address-status-timeline.json) remains
valid evidence of that transient state. It does **not** establish a specification
violation: upstream explicitly fixed the test to tolerate asynchronous address
publication. The static MetalLB pool was independently qualified successfully.

The controller publishes conditions and Service-derived addresses through separate
paths. This makes the observed ordering plausible, but there is no need to posit
an agentgateway regression to explain why the old assertion fails and corrected CI
passes. Other environment differences (K3s versus kind, two controller replicas
versus the CI default, and allocator/network configuration) can affect timing;
they were not isolated as causal factors in this investigation.

## Reporting and follow-up

- Preserve the original **106/107** observations and raw v1.5.1 evidence. Do not
  silently change them to 107/107 or remove a case from the denominator.
- Classify this as a **known upstream test-race limitation**, not a demonstrated
  missing static-address feature or a confirmed agentgateway implementation defect.
- The corrected test passes on the exact product revision in CI. This CI
  investigation was read-only; the later GCP follow-up is separate evidence below.
- For a follow-up comparison, pin the same corrected upstream suite for both
  products and record a new campaign identity; do not mix suite versions within
  existing repetitions. A focused rerun on the prior topology can first verify
  eventual address publication without changing the product.

The prior analysis should have checked the CI dependency and upstream fix before
recommending a controller correction. No product code or original measurement data
was changed in this investigation, and the original campaign infrastructure
remained deleted. The follow-up used separately identified infrastructure.

## Separate GCP follow-up

The [October 5 campaign](../../2026-10-05-stable-comparison/reports/03-gateway-api.md)
subsequently ran the pinned conformance v1.6.1 static-address case three times per
runnable release, using unchanged agentgateway v1.6.0 and Praxis core v0.5.2 images.
Agentgateway passed all three; Praxis failed all three with `UnsupportedAddress`
and an explicit `spec.addresses is not supported` message. All six fixtures
completed cleanup. The [review](../../2026-10-05-stable-comparison/evidence/qualification/kubernetes-final-review.json)
and raw artifact paths accompany the new rows.

These focused results support the CI-based interpretation without changing the
old 106/107 score. They are not a complete 107-case rerun. The test checks address
validation, status and assignment; it does not send HTTP to the assigned VIP.
