#!/usr/bin/env python3
"""Derive the October 1 initial paired traffic tables; retain unavailable runs."""
import argparse
import json
from pathlib import Path


def measurement(root, gateway, connections, qps):
    if gateway == 'direct':
        trial = f'gateway-direct/c{connections}-q{qps}'
    else:
        trial = f'gateway-traffic/r1-{gateway}-{gateway}-traffic-c{connections}-q{qps}'
    p = root / trial / 'fortio.json'
    if not p.exists():
        return None
    data = json.loads(p.read_text())
    duration = data['ActualDuration'] / 1e9
    counts = data['RetCodes']
    requests = sum(counts.values())
    if duration <= 0 or requests <= 0:
        raise ValueError(f'Empty measurement: {p}')
    success = counts.get('200', 0)
    pct = {v['Percentile']: 1000 * v['Value'] for v in data['DurationHistogram']['Percentiles']}
    return dict(trial=trial, requests=requests, errors=requests-success,
                good_qps=success/duration, p99_ms=pct[99], duration_seconds=duration,
                error_percent=100*(requests-success)/requests)


def render(root, out, evidence):
    plan = json.loads((root/'gateway-traffic/plan.json').read_text())
    results = json.loads((root/'gateway-traffic/results.json').read_text())
    if len(plan) != 12 or len(results) != 12 or any(r['repetition'] != 1 for r in results):
        raise ValueError('Expected all 12 attempts from the single-round initial matrix')
    out.mkdir(parents=True, exist_ok=True)
    for baseline, candidate, name in [('direct','agentgateway','agentgateway-vs-service'),
                                      ('agentgateway','praxis','praxis-vs-agentgateway')]:
        text=[f'# {candidate} versus {baseline}: initial Gateway HTTP traffic','',
              '**One measurement per configuration; no confidence intervals.** This is plain HTTP through a single-node kind deployment, not AI processing or GPU inference. Both paths include the kind provider\'s Envoy TCP load balancer.','',
              f'Full source evidence: [{evidence}]({evidence}). Successful QPS counts HTTP 200s; errors include transport failures. p99 covers the tool\'s observed requests, including errors. A missing histogram is unavailable, never zero throughput.','',
              '## Saturation, 60 seconds per measurement','',
              '| Connections | Baseline good QPS | Candidate good QPS | Candidate / baseline | Baseline p99 ms | Candidate p99 ms | Errors baseline / candidate |',
              '| ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for connections in [1,16,512]:
            a=measurement(root,baseline,connections,0);b=measurement(root,candidate,connections,0)
            if not a or not b:
                text.append(f'| {connections} | unavailable | unavailable | unavailable | unavailable | unavailable | aborted before measurement |')
            else:
                text.append(f"| {connections} | {a['good_qps']:,.1f} | {b['good_qps']:,.1f} | {b['good_qps']/a['good_qps']:.3f}× | {a['p99_ms']:.3f} | {b['p99_ms']:.3f} | {a['errors']:,} / {b['errors']:,} |")
        text+=['','## Fixed offered rate: 10,000 QPS','',
               'The direct service has saturation headroom observations only; no direct fixed-rate trial was run. Neither gateway sustained 10,000 QPS at one connection. Read successful throughput, errors and latency together; saturation percentiles occur at different achieved rates.','',
               '| Treatment | Connections | Good QPS | Errors | Error rate | p99 ms |',
               '| --- | ---: | ---: | ---: | ---: | ---: |']
        for g in ([candidate] if baseline=='direct' else [baseline,candidate]):
            for connections in [1,16,512]:
                a=measurement(root,g,connections,10000)
                if a:
                    text.append(f"| {g} | {connections} | {a['good_qps']:,.1f} | {a['errors']:,} | {a['error_percent']:.3f}% | {a['p99_ms']:.3f} |")
                else:
                    text.append(f'| {g} | {connections} | unavailable | aborted | unavailable | unavailable |')
        text+=['','## Environment and failures','',
               'GCP n2-standard-16, Intel Cascade Lake, 16 vCPU / 64 GiB, kind Kubernetes v1.35.8. Controller limits: two replicas each, 2 CPU / 2 GiB per replica. Each proxy: one replica, 100m CPU / 64 MiB requests, 256 MiB memory limit, no CPU quota, 16 configured/detected worker threads. The 256 MiB limit is the Praxis operator-generated setting, matched on agentgateway. All components share the VM; this is deployment-level capacity, not an isolated proxy CPU maximum.','',
               'Agentgateway controller/proxy v1.5.0; Praxis operator fb8beaa14cf714dacf0e6964cc8be94d1b5c1d7c with its documented core 0.5.2 image. The latest tested core 0.7.2 could not start an empty Gateway with this operator and is a separate compatibility finding. Backend and benchtool images are pinned; the community benchtool contains Fortio 1.68.1. Payload flag is zero. This differs from the AI campaign\'s Fortio version, payloads and CPU isolation.','',
               'All five 512-connection attempts (one direct, two per gateway) aborted before producing a Fortio histogram. The direct load balancer logged Too many open files and its open-file limit was 1,024. These points cannot rank either gateway. The raw failure logs are retained; no repeated run or silent limit increase replaced them.','',
               'Praxis\'s 16-connection fixed-rate trial recorded 9,506 transport errors out of 600,000 requests (1.584%). Kubernetes recorded OOMKilled at 2026-10-02T02:51:21Z under the 256 MiB cap, contemporaneous with the connection resets. Its container restarted. Agentgateway recorded zero errors in its corresponding trial. This establishes a failure of this run/configuration, not the behavior at larger memory limits or newer cores. No repeated long-duration experiment was performed.','',
               'Praxis achieved higher successful saturation throughput at 1 and 16 connections. That advantage and its fixed-rate failure are both part of the result. The original suite applies each workload in agentgateway-then-Praxis order; one repetition cannot estimate order effects. Cloud-host contention was not measured.','',
               'Fortio\'s paced, fixed-concurrency arrival behavior is not a corrected open-loop distribution. The backend, client, controller, networking and proxy share host resources. Kubelet samples cover pod resource behavior but not total load-balancer/client cost; no CPU-efficiency winner is claimed. Core conformance and lifecycle findings belong in their separate reports.','']
        (out/f'{name}.md').write_text('\n'.join(text))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--evidence-link',required=True)
    a=p.parse_args();render(a.root,a.output,a.evidence_link)
