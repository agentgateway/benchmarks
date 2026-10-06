# Final infrastructure review

All twelve measured attempts have per-run validity reviews. Nine completed all
107 selected cases; three nightly attempts were blocked by product initialization
before individual cases ran. Each job finished namespace cleanup.

Five host archives cover all twelve measurement windows. The largest observed
sampling gap was 19.40 seconds on the gateway host; the other four stayed below
15.34 seconds. Minimum sampled host MemAvailable was 31,037,092 KiB, maximum
system allocated file descriptors was 2,945, and maximum observed container file
descriptors was 293. No sampled container cgroup had a nonzero OOM-kill counter.
These are correctness-run health checks, not load-capacity or efficiency results.

The gateway collector recorded 111 container-read races: both /proc and cgroup
reads found a vanished process. One additional runtime-inspect call failed at
07:44:00 UTC during release repetition three. Its container belonged to
`praxis-httproute-listener-port-matching-5ccd4b6f9b-4nhnt`, was running with zero
restarts in the preceding snapshot, and was absent in the next. The corresponding
`HTTPRouteListenerPortMatching` case passed. This is consistent with test-resource
removal and does not invalidate the completed assertions. Raw errors remain in
the host archive. No archive had malformed host sample rows.

Runtime node checks found no health/pressure issues, and Kubernetes API collection
had no failures in the measured cases. Product crashes, operator leadership exits,
and terminating exit-137 observations remain in the release/nightly reports.
Sampling does not prove the absence of every transient resource event.

The client TCP-profile repair and maintenance-interrupted third pair are excluded
and retained in the raw evidence. The entire interrupted pair was replaced.
Read the [transport investigation](infrastructure-investigation.md) and
[maintenance investigation](maintenance-interruption.md), including the disclosed
host-package differences across repetitions.

Review records: [host summary](../evidence/validity/host-runtime-review.json),
[review decision](../evidence/validity/host-runtime-decision.json),
[archive checks](../evidence/archive-review.json), and
[final validation inventory](data/CAMPAIGN-VALIDATED.json).
