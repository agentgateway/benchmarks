# Excluded third-pair attempt: automatic host maintenance

Ubuntu unattended upgrades interrupted the original third Praxis release attempt.
At 2026-10-03 06:23:57 UTC, the client host's service manager stopped and restarted
the running benchmark unit while package upgrades were in progress. The restarted
runner correctly refused to overwrite its existing result directory. The upstream
suite never reached its final report or normal cleanup. This is an infrastructure
interruption, not a Praxis feature failure.

The entire third pair was replaced and completed. The completed agentgateway half had 106 passes
and one failure, but is retained as superseded alongside the incomplete Praxis half
under `rejected-infrastructure/maintenance-interrupted/praxis-v0.5.2/pass3`.
Neither original half enters the final three-repetition aggregate. The excluded
folder preserves the service journal, partial test/runtime logs, and recovery record.

## Scope of the interruption

The audit covered all five campaign hosts. Automatic upgrade windows were:

| Host | Start (UTC, October 3) | Finish | Overlap |
| --- | --- | --- | --- |
| kcontrol | 06:16:49 | 06:22:26 | Original third Praxis attempt |
| kclient | 06:22:50 | 06:24:14 | Original third Praxis attempt; benchmark service restarted |
| kcontroller, kgateway, kbackend | No post-provisioning upgrade observed | — | None |

The first two measured pairs finished before these windows. Their previous runtime
reviews remain valid; the two mid-run leadership-loss exits in Praxis repetition two
preceded these updates and must not be attributed to this maintenance event.
The original third agentgateway suite also finished before the update windows;
its replacement keeps the third pair together under the repaired profile.

See the [focused service/package histories](../evidence/update-investigation/) and
[exclusion ledger](../evidence/exclusions.json). The focused exports retain service-
manager events, apt histories and timer inventory; unrelated K3s application logs
were omitted, with original/exported hashes recorded.

## Repair and limits

`infra/freeze-maintenance.sh` masks apt daily timers and disables periodic package
updates on these disposable VMs. It waits for active maintenance to finish instead
of killing a package transaction. The same protection is now applied by the
reproduction bootstrap before measurements. All five nodes were Ready and the
interrupted fixtures were removed before the replacement pair started.

The host kernel and K3s processes were not replaced or restarted. The upstream Go
binary, CRDs, container images, controller configuration, assertions and per-test
timeouts remain pinned and unchanged. Client/control host packages did change,
including OpenSSL and libexpat patch versions; the freeze inventory records them.
Thus the host package inventory is not byte-identical across all three repetitions.
The unchanged static Go test binary and containerized products provide the same
correctness probes, but these observations must not be used as equal-host-package
performance measurements. The report retains this environment change explicitly.
