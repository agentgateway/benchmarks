# Review gates

This is an operator review procedure. Machine-generated summaries collect facts;
they do not approve themselves. A failed product scenario can be a valid outcome,
while a successful process can still produce an invalid benchmark.

## Before accepted pass one

- Resolve each requested image to the recorded digest; check the running image,
  container entrypoint, resource limits and rendered destination addresses.
- Confirm all nodes are Ready, roles are isolated and inactive gateways/controllers
  have stopped. Use private IPs for load.
- Confirm exactly one Ready gateway pod/endpoint, stable for ten seconds, with
  the requested digest. Audit retained barriers with `audit-kubernetes-startup.py`.
- Confirm host **and pod** TCP settings, descriptor limits and guest CPU topology.
  Exercise sustained 512-connection unlimited-rate traffic, not only low RPS.
- Verify protocol contents, streaming events, synthetic errors and cancellation.
  For AIPerf, check seed 42, 128/64 token lengths and matching generated messages.
- Attribute every startup/tool failure. Preserve excluded attempts and restart a
  complete affected profile under a fresh output path after a correction.
- Retain reviewed qualification records. CPU runners require the seed field;
  Kubernetes requires its own review marker on the client.

## Before repetitions two and three

- Check every planned first-pass case exists once with complete raw tool output.
  Review nonzero exits, timeouts, HTTP errors, resets and AIPerf error summaries.
  Nighthawk requests still in flight at cutoff are not automatically errors.
- Audit client/backend headroom, CPU steal, memory/OOM, process restarts,
  descriptors, NIC error/drop increments, TCP namespace settings and socket counts.
  Attribute events with timestamps; cumulative restart counters may predate a case.
- Check scale runner exit codes and API/controller logs. “Did not converge” is a
  product outcome only when the observer and infrastructure functioned correctly.
- Check restart command exits, pre-mutation traffic and probe dispatch delay.
- Verify the known nightly setup signature, exact image, exit 1 and Ready nodes;
  any different setup failure requires new diagnosis.
- Freeze accepted configuration/workload identities. Approve repetitions only
  after the first-pass evidence supports them; do not approve from headline ratios.

## Before reporting and deletion

- Recheck all three accepted passes, complete treatment order and input hashes.
  Do not quietly omit later failures because the first pass was valid.
- Generate all matrix rows and means from one immutable CPU export and one
  immutable Kubernetes export. Never aggregate duplicated intermediate snapshots.
- Require exactly 822 accepted load cases / 274 three-pass groups for this design,
  24 scale phases, 12 recovery scenarios and three nightly setup blocks. Static
  follow-up is six separately identified focused conformance attempts.
- Confirm every reported number points to a raw artifact and every capability
  claim distinguishes observation from source review.
- Verify a local archive before teardown. Publish only sanitized artifacts to the
  private repository and check GitHub asset hashes. Cleanup must not wait on an
  unrelated editorial or publication problem once recoverable evidence is safe.
- Delete the eight captured VMs and their boot disks; verify no campaign-owned
  addresses, load balancers, clusters or other resources remain. Preserve unrelated
  project resources and remove local temporary cluster credentials.
