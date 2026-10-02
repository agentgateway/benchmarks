# Experimental Praxis inference treatment

`praxis-standalone` adds a Praxis AI proxy beside the same endpoint picker (EPP)
used by `agentgateway-standalone`. It is a benchmark adapter requiring runtime
qualification, not a claim of native Praxis Gateway API inference support or
verified parity with agentgateway. No comparative performance results accompany
this change.

## Exact candidate and build

The integration is pinned to Praxis AI source
`f5f51a751d6f25acde96fb840665b24f2696ce46`, whose workspace depends on Praxis
core 0.7.2. The default published Praxis AI image does **not** enable the
experimental `llmd-ext-proc` feature. Build the full profile plus that feature:

```sh
git clone https://github.com/praxis-proxy/ai.git /tmp/praxis-ai
git -C /tmp/praxis-ai checkout f5f51a751d6f25acde96fb840665b24f2696ce46
inference/suites/llm-d-benchmark/scripts/build-praxis-image.sh \
  /tmp/praxis-ai YOUR_REGISTRY/praxis-ai:benchmark
```

The helper checks a clean source tree and Cargo.lock SHA-256, builds the full
workspace with `--locked`, and retains the upstream runtime/license files. It
adds source, feature and lockfile labels. It does not push. Record the build log,
resolved builder/runtime base-image digests and toolchain versions. Push to the
registry used by your test cluster, then use the resolved image digest:

```sh
export PRAXIS_IMAGE='YOUR_REGISTRY/praxis-ai@sha256:YOUR_DIGEST'
export PRAXIS_SOURCE_REVISION=f5f51a751d6f25acde96fb840665b24f2696ce46
```

The source revision is declared provenance; the runtime inventory does not
independently attest the image's source. Retain the helper output and image
labels beside the campaign. Tests validate rendering and metadata gates; a
native Linux/amd64 source build and real EPP run are still required. Emulated
amd64 containers on ARM are unsuitable for performance comparisons.

## Adapter and semantic limits

The pinned llm-d-router chart v0.9.0 supports `envoy` and `agentgateway` preset
names. This adapter uses its generic Envoy slot but replaces the actual image,
container name, executable, arguments, configuration, mounts and probes with
Praxis. The rendered pod must contain `praxis-proxy` and `epp`, with no Envoy
proxy. EPP remains the same sidecar and uses plaintext gRPC over loopback.

The Praxis source validator permits full-duplex **request** body processing but
rejects all response-body modes other than `none`, and rejects trailer `send`.
The configuration therefore sends request headers/body and response headers,
with response body `none` and both trailer modes `skip`. HTTP responses still
flow to clients; response bodies are not delivered to the external processor.
Do not assume EPP inflight accounting, cache tracking, cancellation and stream
completion are equivalent merely because endpoint selection succeeds.

Before a GPU campaign, validate real EPP endpoint selection and request bodies,
streaming completion, cancellation, upstream/processor errors, and EPP request
lifecycle state. Praxis's upstream environment tests use a deterministic mock
processor, not the real llm-d Go EPP. Preserve qualification failures and stop
GPU measurement if the required semantics are unavailable.

The default proxy resources match the chart's other standalone proxy:
4 CPU/8 GiB requests and 16 GiB memory limit. The EPP also requests resources;
size nodes from the complete rendered pod, not just the proxy. Rendered chart
and normalized configuration hashes prevent comparisons across different
policies/resources/workloads. They do not prove runtime semantic parity.

## Qualification and campaigns

Run the simulator first in an isolated cluster. This command can provision
billable CPU infrastructure; select project, cluster and lifecycle explicitly:

```sh
export BENCHMARK_GKE_PROJECT=YOUR_PROJECT
export BENCHMARK_GKE_CLUSTER=YOUR_DEDICATED_CLUSTER
export BENCHMARK_SMOKE_TREATMENT=praxis-standalone
make benchmark-gke-smoke-sim
```

Once integration qualification passes, use the ordinary treatment runner or
select the GKE campaign treatments and comparisons explicitly:

```sh
export BENCHMARK_TREATMENTS='agentgateway-standalone praxis-standalone'
export BENCHMARK_COMPARISONS='agentgateway-standalone:praxis-standalone'
# Configure model, resource topology, costs and cleanup per the GKE guide first.
make benchmark-gke-all
```

The full campaign defaults are large GPU workloads. Do not run that final
command as a smoke test. Choose the same immutable agentgateway image, EPP,
model, serving engine, workload, deadlines and repetitions, and reverse
`BENCHMARK_TREATMENTS` between repetitions. Keep service-baseline reports
separate: Kubernetes Service balances connections, not necessarily individual
requests on persistent connections.

Reports distinguish simulator transport/routing from real GPU inference and
identify the custom Praxis build. Compare successful goodput, TTFT, token
latencies and errors with all repetitions and resource samples. A shared EPP
comparison measures gateway integration differences, not a better scheduler.
