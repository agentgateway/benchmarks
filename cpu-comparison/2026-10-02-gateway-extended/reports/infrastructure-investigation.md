# Test-client TCP startup investigation

The initial full agentgateway attempt produced 101 passes and six failures. It is
retained under `rejected-infrastructure/pre-tcp-client-fix` and excluded from the
three measured repetitions. The upstream test binary and gateway images were not
changed in response to these results.

## Evidence

Several TLS tests blocked in their first TCP connection attempt until the upstream
30-second consistency check ended. Runtime snapshots showed the relevant gateway
pod Ready while that connection was still pending. A separate diagnostic ran the
unchanged TLSRouteSimpleSameNamespace test and observed socket state, Service
configuration, kube-proxy NAT rules, and fresh TLS probes.

- The original conformance socket stayed in SYN-SENT on the same source port.
- Twenty-four fresh TLS connections to the same VIP and port succeeded while that
  socket remained blocked. Their first success was at 23:57:32.795590 UTC.
- The original test nevertheless timed out, demonstrating that a successful gateway
  connection was possible within the test's consistency window.
- The upstream TCP/TLS helpers call DialContext with the whole test context rather
  than a bounded per-attempt connect timeout. An early connection during Service/VIP
  programming can therefore consume the entire consistency window.

The observations establish a client/Service-startup interaction. They are consistent
with a stale initial connection established before the relevant NAT path is ready;
they do not establish a general inability of agentgateway to serve TLS traffic.

## Shared infrastructure repair

On the client VM only, set `net.ipv4.tcp_syn_retries=2` (previously 6).
`net.ipv4.tcp_syn_linear_timeouts` remains 4. The unchanged focused TLS test then
passed with **no additional probe traffic**: its request check completed in 7.21
seconds and the top-level case in 10.31 seconds. The setting applies equally to
both products and both version campaigns. It changes neither the suite's 30-second
consistency window nor any assertion, CRD, gateway configuration or image.

The complete first pass is rerun from scratch under the repaired profile, followed
by first-pair infrastructure review before repetitions two and three. This is not
a selective retry of failing product assertions. The diagnostic is not a measured
campaign result.

The initial `GatewayStaticAddresses` failure is **not explained by this transport
issue**: its condition checks completed, but the Gateway object used by the final
address assertion contained no requested address. The upstream test reuses an object
fetched before its final waits. A later excluded passive watch also captured a
latest-generation `Programmed=True` state with no `status.addresses`, establishing
that the missing address existed in the published ready status. The October 5 CI investigation identified a known upstream test race: ready
conditions and address publication need not be atomic. This observation alone does
not establish a faulty controller code path.
See [the follow-up](agentgateway-static-address-follow-up.md). The observed failure
remains in the results regardless of subsequent full-pass outcomes.

## Reproduce and inspect

`harness/diagnose-tls.py tls-startup` runs an excluded focused test plus fresh
connections; `harness/diagnose-tls.py tls-client-fixed --passive` observes without
sending additional probes. `infra/configure-tcp-client.sh` records the before/after
settings and applies the shared profile. The private client archive retains
`diagnostics/`, `qualification/tcp-client/`, and the entire excluded attempt.
The exclusion decision is recorded in [exclusions.json](../evidence/exclusions.json).

Use top-level `--- PASS` / `--- FAIL` lines for outcomes. Some upstream TCP helpers
log “Request passed” even after a nonfatal assertion failed; that message alone is
not a passing test result.
