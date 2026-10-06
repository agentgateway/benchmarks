# Methodology and interpretation

The comparison asks whether identical Kubernetes Gateway API configurations produce
the upstream-defined behavior. It does not measure AI model quality, inference
speed, HTTP capacity, or scalability. Those earlier campaigns remain separate.
The evaluation was performed for Solo.io, an agentgateway contributor. It is not
an independent third-party assessment. “Independent coverage probes” in the raw
metadata means evaluator-selected tests rather than vendor support declarations.

## Scope fixed before results

- Gateway API v1.5.1, source e7677b70ae75d14a4448fba94870e7deea6cf0ad.
- Experimental CRD bundle from that same commit enables testing both channels.
- Explicit non-mesh feature union: 43 feature flags and 107 applicable tests.
  The catalog records every selected test, dependency, channel and provisional flag.
  Its selector takes the pinned upstream `AllFeatures` registry minus mesh features.
  That registry does not include UDPRoute, so its provisional test is also skipped;
  see the [upstream registry](https://github.com/kubernetes-sigs/gateway-api/blob/e7677b70ae75d14a4448fba94870e7deea6cf0ad/pkg/features/features.go#L54).
  No UDP coverage claim follows from this selection.
- HTTP, gRPC and TLS conformance profiles; upstream default per-test timeouts,
  assertions, fixtures and cleanup. A 179-minute outer Go timeout bounds a run.
- Agentgateway v1.6.0 stable in both comparisons; current Praxis operator
  fb8beaa with either core v0.5.2 or nightly-20261002, pinned by OCI digest.
- Three repetitions per comparison; product order reverses in the middle pass.
  The first pair must pass infrastructure review before repetitions two and three.

The feature union deliberately probes functionality beyond vendors' declarations.
`--supported-features` is an upstream test-selection mechanism here, **not** a
claim that Praxis or agentgateway declares all selected functionality supported.
These are evaluator-selected coverage probes, not official vendor conformance submissions.
The raw upstream reports retain that qualification in implementation metadata.

## Infrastructure

Five native GCE n2-standard-8 instances in solo-oss/us-central1-a, Cascade Lake
minimum CPU platform, Ubuntu 24.04, 100 GB balanced boot disks, no instance service
account. K3s v1.35.8+k3s1 provides Kubernetes; Traefik and ServiceLB are disabled.
Dedicated control-plane, controller, gateway, backend and client roles match the
previous campaign topology. Unmodified upstream conformance fixture pods schedule
on the untainted gateway worker. This is a functional test, not isolated data-plane
capacity measurement. Only one gateway controller is active during a measurement.

Both controller Deployments use two replicas with 2 CPU / 2 GiB limits per replica.
Agentgateway data planes use two workers and a 2 CPU / 256 MiB limit with logging
disabled; Praxis data planes retain the stock operator's 256 MiB limit and no CPU
limit. This is a disclosed deployment configuration, not an equal-resource
throughput comparison. Runtime reviews retain product restarts and distinguish
terminating pods from active-process OOM failures.


MetalLB v0.16.1's controller allocates cluster-internal VIPs. Its speaker is removed;
there is no BGP/L2 advertisement or managed GCP load balancer. Kube-proxy makes
VIPs reachable from the client node. Dynamic pool: 198.18.0.1–198.18.0.254. Static
pool: 198.18.1.254/32, autoAssign=false. The unusable address is bogus.example.com,
following agentgateway's conformance harness convention. No Envoy is deployed.

The shared client uses net.ipv4.tcp_syn_retries=2 with tcp_syn_linear_timeouts=4
to bound a failed startup connection attempt below the upstream consistency window.
The original default-profile attempt and the diagnostic are excluded and retained;
see [the investigation](infrastructure-investigation.md). The suite itself is unchanged. A later host-maintenance interruption caused a
full replacement of the third release pair; [the maintenance report](maintenance-interruption.md)
records the excluded attempts, frozen update timers, and host package differences.

The operator is built from the pinned upstream source. A Dockerfile compatibility
adaptation replaces COPY --chmod with the equivalent chmod command; Rust product
code is unchanged. Agentgateway uses release charts and immutable container images.
Praxis uses its supported PRAXIS_IMAGE override for the nightly comparison.

## Validity and reporting

A product assertion failure remains a result. Unsupported features are identified
from pinned product documentation alongside observed behavior. Missing tests,
setup failures and skipped tests never become passes or individual feature failures.
If a controller/image pairing cannot deploy, report the pairing as blocked and
preserve diagnostics. Do not patch the product or substitute a different image to
manufacture a successful comparison.

Count top-level test cases, not nested assertions. Report standard and experimental
results separately. “Passed in 3/3 runs” describes repeatability; it is not a claim
that every possible configuration of the feature works. Tests can depend on several
features, so a failed multi-feature test cannot by itself locate the defective feature.
GRPCRouteNamedRouteRule is cataloged even though this suite version's profile
mapping omits it from the gRPC extended-feature set; the top-level log remains the
complete outcome source. Excluded mesh and UDP tests are listed in the inventory.

Preserve runtime pod, node, event and route state, controller logs, host FD/memory
samples, exact commands, versions and raw reports. Check node readiness, image
pulls, scheduling, restarts/OOMs, API errors, collector gaps and cleanup before
accepting a pass. Any infrastructure-invalid attempt is retained and excluded with
a reason; reruns receive new identities. No automatic retries hide product failures.

## Cost and cleanup

A twelve-hour automatic instance deletion is a safety limit, not the intended run
length. Approximate maximum five-VM compute/disk/IPv4 cost is $25 before network charges.
Explicit deletion after verified evidence export removes campaign VMs and boot
disks; resource inventory confirms cleanup. Unrelated project resources are preserved.
