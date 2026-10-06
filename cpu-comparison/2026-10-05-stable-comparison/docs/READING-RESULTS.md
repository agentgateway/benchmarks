# Read a benchmark result without overstating it

Start with the deployment profile and exact image, then read the workload,
achieved rate, errors and latency together. A higher number is useful only when
it answers the same question for both implementations.

| Reported value | Meaning here | Common misinterpretation |
| --- | --- | --- |
| Successful RPS | Fortio HTTP 200 responses, Nighthawk 2xx responses, or AIPerf valid completions per second | Attempted requests or a configured target rate are not successful throughput |
| Offered rate | Requested dispatch rate; zero means unlimited in the Fortio plan | Both gateways delivering 1,000 RPS does not establish their maximum capacity |
| Connection/concurrency setting | Configured cap on concurrent work | It is not a count of independent users or proof of an open-loop arrival process |
| Mean latency | Average client-observed request time in that case | A fast average does not describe the slowest requests |
| p99 latency | Per-run tail quantile, then arithmetic mean across three runs | The mean of three p99s is not the p99 of all requests pooled together |
| Nighthawk p99 upper bracket | Nearest exported quantile at or above p99 | It is not an exact p99; the original percentile remains in the data |
| TTFT | AIPerf client-observed time to first token | Synthetic-service TTFT does not measure real-model prefill or GPU routing efficiency |
| ITL | AIPerf client-observed inter-token latency | This CPU fixture deliberately paces output; small differences do not imply faster model generation |
| Range and sample standard deviation | Variation across the three retained repetitions | Three runs on one placement do not establish cloud-wide confidence or statistical significance |
| In flight at cutoff | Nighthawk requests without a retained completion/reset at measurement end | These are reported separately from confirmed response errors |

AIPerf's successful request count and error count are separate. Its throughput
uses successful completions; the report retains failed requests alongside that
rate. See the upstream [metrics reference](https://docs.nvidia.com/aiperf/reference/ai-perf-metrics-reference)
and [export schema](https://docs.nvidia.com/aiperf/reference/json-export-schema).
Non-streaming JSON cases use synthetic usage fields that do not represent
tokenization of their byte-sized payloads; they do not audit billing accuracy.
The raw exports from the pinned AIPerf 0.13.0 installation remain authoritative
for this campaign, even if the online documentation later changes.

## What a throughput ratio establishes

A ratio above one for agentgateway/Praxis means the configured agentgateway path
completed more successful requests per second in that case. It does not establish
an overall winner, a production SLO, lower real-provider cost, or equivalent
features. Native AI configurations perform different routing/accounting work;
the common forwarding profile is the closer transport comparison.

The direct baseline measures the entire client-to-service path. It may reach
client or service capacity under unlimited traffic. Dividing by that rate gives
a fraction of the measured reference, not a fraction of an unlimited backend.
The extra network hop is also part of the gateway path.

A gateway/reference ratio slightly above one, or a negative difference between
mean latencies, can occur across separately timed runs. Read the individual ranges
and resource limits before interpreting it. It does not demonstrate that adding
a gateway accelerates the service or removes the extra network hop.

## What a Gateway API result establishes

An upstream conformance pass establishes the assertions exercised by that test,
with its suite revision and configuration. Case counts are not percentages of
the specification. An implementation/controller setup block leaves dependent
tests not evaluated; it does not create individual failures for every feature.

Route scale has two separate checks: current-generation status and actual traffic
through every route. A timeout is a censored observation within the stated window,
not zero convergence time. Do not average only the successful repetitions of an
otherwise failing scenario.

Recovery probes describe graceful mutations at ten requests per second and one
data-plane replica. No observed errors is useful evidence for that interval; it
does not establish zero production downtime or resilience to a hard node failure.
The client reuses connections, and the observation can end while the original
pod is still draining. Complete handoff to the replacement and fresh-connection
availability are not established by these probes.

Use the [evidence map](EVIDENCE-LAYOUT.md) to trace a table cell to raw commands,
outputs and host samples. The [methods report](../reports/05-methodology-and-validity.md)
records exclusions and the boundaries that apply to every competitive statement.
