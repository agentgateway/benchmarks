# Sampled resource usage

Both gateways receive a two-CPU quota in each deployment profile. The standalone
profile also pins two guest cores and permits 2 GiB; Kubernetes permits 256 MiB
without CPU pinning. Compare within a profile and workload. The direct baseline
has no gateway process; gateway-specific resource metrics do not apply to it.

The matrices retain every gateway case and every repetition. They complement
successful throughput and latency; they are not an overall efficiency ranking.
At fixed offered rates, check that both products actually deliver the same rate.
At saturation, higher utilization can simply mean the gateway does more work.

[common http](matrices/common-http-resources.md), [common ai](matrices/common-ai-resources.md), [native ai](matrices/native-ai-resources.md), [kubernetes http](matrices/kubernetes-http-resources.md).

CPU uses cgroup usage deltas divided by the two-CPU quota: 100% means approximately
two CPUs are busy, not the whole eight-vCPU VM. Five-second samples cover the
tool-execution window, including startup and warmup. They do not establish exact
cycles per request or a production cost per request.

Memory is the maximum sampled `memory.current` cgroup charge in each window,
then summarized across three runs. It includes charged memory beyond process RSS,
can miss short peaks, and is not the container lifetime `memory.peak`. Gateway
processes serve multiple cases, so allocator retention and treatment order can
affect later samples. Different memory caps prevent treating standalone versus
Kubernetes differences as a controlled experiment in Kubernetes overhead.

Descriptor maxima are observations, not configured limits. Validity review checks
those limits, process identity, restarts, OOM counters, client/backend capacity,
CPU steal and network error/drop increments separately. Direct unlimited-rate
traffic approaches client or backend capacity in some cases; the baseline remains
the observed full path, not an unconstrained service ceiling.

[Individual resource rows](data/resource-rows.json) map to the same raw execution
artifacts as [load rows](data/load-rows.json); [resource summaries](data/resource-summary.json)
retain all three values. Read [methodology](05-methodology-and-validity.md) before
turning a sampled resource difference into a competitive claim.
