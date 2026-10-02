# Reproduce the initial Gateway API configuration

Use a disposable dedicated native Linux amd64 machine. The recorded host was GCP n2-standard-16 (Intel Cascade Lake, 16 vCPU, 64 GiB) running one kind node. This is a single-host deployment-system experiment; it does not represent production multi-node networking or isolated proxy CPU capacity.

## Pinned components

| Component | Version / identity |
| --- | --- |
| Community suite base | `141add64d25455a6acb7ea7c69e1e813bb05e339` |
| Local campaign patches | `ade5ca160a546d18695a4456225185872d86a6b8`, `25d513948a41463199fadded4828315527736e15` |
| Gateway API source and CRDs | v1.5.1, `e7677b70ae75d14a4448fba94870e7deea6cf0ad` |
| Agentgateway chart / proxy | v1.5.0; actual image digests are in pod snapshots |
| Praxis operator source | `fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c`, native source build |
| Praxis core for primary comparison | 0.5.2, `ghcr.io/praxis-proxy/praxis@sha256:ef01934b86c6368e097fa8adfc879663a0f8b01cdd265802ba9595c3402230f8` |
| kind | v0.33.0 |
| Node image | `kindest/node:v1.35.8@sha256:07b2536e30b803ed61d1677a79df6115f798ce64c80f9e22f6ed45afd09323c0` |
| cloud-provider-kind | v0.11.1; its Gateway/Ingress controllers disabled |
| Go / kubectl / Helm | 1.27.1 / 1.35.8 / 4.3.0 |
| Backend | `howardjohn/hyper-server@sha256:696480437cbbfb171fb3bc37a0d69e403fbec210e22ef3743e9f16b43ab0d7a5` |
| Benchtool | `howardjohn/benchtool@sha256:fb73a9392723c85e90e874beda4e3f7f7e27fc7f9003e713fe29c2ce1123a938` (Fortio 1.68.1) |
| pilot-load | revision pinned by the community suite's `go.mod` |

## Install

1. Check out the community suite at the base revision and apply `praxis-campaign.patch` with `git am`. Build tools and pull images before timed load.
2. Create kind with the pinned node image and a dedicated kubeconfig. Start cloud-provider-kind with `--gateway-channel=disabled --enable-default-ingress=false`. Otherwise it can install its own Gateway API CRDs and controller. Record its Envoy image and actual `/home/envoy/{envoy,cds,lds}.yaml` configuration; `/etc/envoy/envoy.yaml` is an unused image default.
3. Check out Gateway API at the pinned SHA. Install CRDs with `kubectl apply --server-side -k /path/to/gateway-api/config/crd`. Use the same source for tests; do not pass `--allow-crds-mismatch`.
4. Install agentgateway's v1.5.0 CRD chart into `agentgateway-system`, apply `configs/agentgateway-parameters.yaml`, then run `AGENTGATEWAY_VERSION=v1.5.0 bash install/agentgateway-current.sh -f /absolute/path/to/configs/agentgateway-values.yaml` from the patched suite. The class-level parameters apply to conformance-created Gateways as well as the benchmark Gateway.
5. Build the pinned Praxis operator using its Containerfile, load it into kind, and set `PRAXIS_OPERATOR_IMAGE` to that local image. The recorded Docker legacy builder did not support `COPY --chmod`; the retained packaging-only patch replaces that with an equivalent `RUN chmod 0555` before switching user. Operator Rust source is unchanged.
6. Set `PRAXIS_IMAGE` to the core 0.5.2 digest above and run `bash install/praxis.sh`. Normalize operator resources with `kubectl set resources deployment/praxis-operator -n praxis-system --requests=cpu=100m,memory=128Mi --limits=cpu=2,memory=2Gi`, then wait for rollout.
7. Verify actual generated resources/images: both controllers have two replicas and 2 CPU/2 GiB limits per replica. Each proxy has one replica, 100m/64 MiB requests, a 256 MiB memory limit and no CPU quota. Agentgateway uses 16 workers; Praxis detects 16 threads per service. Access logging is disabled. Retain snapshots instead of assuming the desired manifest was applied.

The supported Praxis core 0.5.2 lane is distinct from qualification of core 0.7.2 (`sha256:ed6061326911092315e809e901e773e16153d8826086a44b8e95ab715fc78e6b`). In this operator combination, 0.7.2 rejected the empty router before any HTTPRoute. That attempt is retained rather than silently substituted into the throughput results.

## Correctness and load

Run the Gateway API nested `conformance` module sequentially for each class with `--conformance-profiles=GATEWAY-HTTP --supported-features=Gateway,HTTPRoute,ReferenceGrant`. Explicit feature selection prevents automatic inference of each class's different extension set. Do not add arbitrary test skips. Wait for every `gateway-conformance-*` namespace to finish deletion between implementations. Retain full logs, YAML reports and declared features. These Solo.io observations are not third-party certification.

Export `GATEWAYS=agentgateway/agentgateway,praxis/praxis`, `BACKEND_IMAGE`, and `BENCHTOOL_IMAGE` with the pins above. First use the smoke profile for qualification. The initial measured traffic command is:

```sh
python3 tests/campaign.py --profile full --repetitions 1 \
  --case traffic-c1-q0 --case traffic-c1-q10000 \
  --case traffic-c16-q0 --case traffic-c16-q10000 \
  --case traffic-c512-q0 --case traffic-c512-q10000 \
  --output /tmp/gateway-traffic
```

The direct Service baseline selects the same `app: backend` workload through a separate LoadBalancer Service, port 80 to targetPort 8080. Run the pinned benchtool on host networking, `-d 60 -q 0 -c 1|16|512 -p 0`, writing each invocation to a separate mounted result directory. No direct fixed-rate trial was run. All paths include an Envoy TCP forwarding hop.

**Known qualification limit:** cloud-provider-kind's recorded load balancers inherited a 1,024-descriptor limit. All 512-connection attempts aborted, with `Too many open files` in the direct load-balancer log. Those are unavailable measurements, not zero QPS. A future performance campaign should fix the shared limit and requalify the entire affected matrix; these initial attempts must not be replaced or presented as successful saturation measurements.

After traffic has stopped, remove the two default-namespace traffic HTTPRoutes, then run the lifecycle cases once:

```sh
python3 tests/campaign.py --profile full --repetitions 1 \
  --case attached-routes --case probe --case routechange \
  --case scale-10x100 --case scale-50x100 \
  --output /tmp/gateway-lifecycle
```

Capture kubelet `/stats/summary` every five seconds with timestamps. For each scale case, snapshot actual HTTPRoutes/Gateway status at five and nine minutes to distinguish requested from achieved scale. These API observations are part of the monitoring overhead. Stop after a forced timeout and inspect/clean up before any later case; never continue into contaminated state automatically.

Read test semantics before claiming a win: `attached-routes` reports status convergence relative to workload creation, `probe` stops at the first transport error and measures first-200 after the apply call, and `routechange` checks HTTP-200 continuity while alternating backend port/filter configuration. It does not independently verify each header transformation or prove that every intermediate configuration was served. Scale workloads create synthetic objects and churn; they do not demonstrate 5,000 real inference backends or successful traffic to all routes.

The initial 5,000-route Praxis fixture also exceeded the ConfigMap data-size limit. Preserve its rejection logs; increasing proxy CPU or memory does not remove that Kubernetes API object-size limit. A different configuration layout would be a distinct treatment and requires a new declared experiment.
