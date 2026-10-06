# agentgateway versus direct: initial Gateway HTTP traffic

**One measurement per configuration; no confidence intervals.** This is plain HTTP through a single-node kind deployment, not AI processing or GPU inference. Both paths include the kind provider's Envoy TCP load balancer.

Full source evidence: [raw.tar.gz](raw.tar.gz). Successful QPS counts HTTP 200s; errors include transport failures. p99 covers the tool's observed requests, including errors. A missing histogram is unavailable, never zero throughput.

## Saturation, 60 seconds per measurement

| Connections | Baseline good QPS | Candidate good QPS | Candidate / baseline | Baseline p99 ms | Candidate p99 ms | Errors baseline / candidate |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 16,556.9 | 6,451.0 | 0.390× | 0.095 | 0.246 | 0 / 0 |
| 16 | 103,922.6 | 43,077.9 | 0.415× | 0.298 | 0.689 | 0 / 0 |
| 512 | unavailable | unavailable | unavailable | unavailable | unavailable | aborted before measurement |

## Fixed offered rate: 10,000 QPS

The direct service has saturation headroom observations only; no direct fixed-rate trial was run. Neither gateway sustained 10,000 QPS at one connection. Read successful throughput, errors and latency together; saturation percentiles occur at different achieved rates.

| Treatment | Connections | Good QPS | Errors | Error rate | p99 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| agentgateway | 1 | 6,370.3 | 0 | 0.000% | 0.247 |
| agentgateway | 16 | 9,999.7 | 0 | 0.000% | 0.350 |
| agentgateway | 512 | unavailable | aborted | unavailable | unavailable |

## Environment and failures

GCP n2-standard-16, Intel Cascade Lake, 16 vCPU / 64 GiB, kind Kubernetes v1.35.8. Controller limits: two replicas each, 2 CPU / 2 GiB per replica. Each proxy: one replica, 100m CPU / 64 MiB requests, 256 MiB memory limit, no CPU quota, 16 configured/detected worker threads. The 256 MiB limit is the Praxis operator-generated setting, matched on agentgateway. All components share the VM; this is deployment-level capacity, not an isolated proxy CPU maximum.

Agentgateway controller/proxy v1.5.0; Praxis operator fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c with its documented core 0.5.2 image. The latest tested core 0.7.2 could not start an empty Gateway with this operator and is a separate compatibility finding. Backend and benchtool images are pinned; the community benchtool contains Fortio 1.68.1. Payload flag is zero. This differs from the AI campaign's Fortio version, payloads and CPU isolation.

All five 512-connection attempts (one direct, two per gateway) aborted before producing a Fortio histogram. The direct load balancer logged Too many open files and its open-file limit was 1,024. These points cannot rank either gateway. The raw failure logs are retained; no repeated run or silent limit increase replaced them.

Praxis's 16-connection fixed-rate trial recorded 9,506 transport errors out of 600,000 requests (1.584%). Kubernetes recorded OOMKilled at 2026-10-02T02:51:21Z under the 256 MiB cap, contemporaneous with the connection resets. Its container restarted. Agentgateway recorded zero errors in its corresponding trial. This establishes a failure of this run/configuration, not the behavior at larger memory limits or newer cores. No repeated long-duration experiment was performed.

Praxis achieved higher successful saturation throughput at 1 and 16 connections. That advantage and its fixed-rate failure are both part of the result. The original suite applies each workload in agentgateway-then-Praxis order; one repetition cannot estimate order effects. Cloud-host contention was not measured.

Fortio's paced, fixed-concurrency arrival behavior is not a corrected open-loop distribution. The backend, client, controller, networking and proxy share host resources. Kubelet samples cover pod resource behavior but not total load-balancer/client cost; no CPU-efficiency winner is claimed. Core conformance and lifecycle findings belong in their separate reports.
