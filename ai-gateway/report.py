#!/usr/bin/env python3
"""Derive both comparison reports from the entire initial CPU campaign."""
import argparse
import json
from pathlib import Path


def render(campaign, out, evidence):
    manifest=json.loads((campaign/'manifest.json').read_text())
    status=json.loads((campaign/'campaign-status.json').read_text())
    rows=json.loads((campaign/'summary.json').read_text())
    checks=[json.loads(line) for line in (campaign/'qualification.jsonl').read_text().splitlines()]
    if not checks or not all(x['passed'] for x in checks):
        raise ValueError('Protocol qualification is missing or failed')
    if status['status']!='complete' or len(rows)!=len(manifest['trials']):
        raise ValueError('Incomplete campaign: preserve evidence and write a failure report instead')
    if manifest['mode']!='preliminary-performance':
        raise ValueError('Only preliminary performance data is accepted; smoke timings are not performance results')
    params=manifest['parameters']
    if params['repetitions']!=1:
        raise ValueError('This report is for one initial round; repeated data needs dispersion analysis')
    indexed={(r['case'],r['size'],r['qps'],r['gateway']):r for r in rows}
    if len(indexed)!=len(rows): raise ValueError('Duplicate trial key')
    keys=sorted({(r['case'],r['size'],r['qps']) for r in rows})
    for key in keys:
        for gateway in ('direct','agentgateway','praxis'):
            if (*key,gateway) not in indexed: raise ValueError(f'Missing {key} {gateway}')
    out.mkdir(parents=True,exist_ok=True)
    for baseline,candidate,title,name in [
        ('direct','agentgateway','Agentgateway versus direct backend','agentgateway-vs-direct.md'),
        ('agentgateway','praxis','Praxis versus agentgateway','praxis-vs-agentgateway.md')]:
        text=[f'# {title}: initial CPU-only results','',
              '**Preliminary: one measurement per configuration.** No between-run variance, confidence interval or statistical superiority claim is available. These are deterministic mock-backend proxy tests, not inference/GPU results.','',
              f"Started: `{manifest['started_utc']}`. Full raw evidence: [{evidence}]({evidence}). No successful or failed requests were removed from the tables.",'',
              '## Configuration','',
              f'Dedicated GCP n2-standard-16 Linux/amd64 VM (16 logical CPUs, 64 GiB RAM). Agentgateway configures two workers; Praxis configures two runtime threads per service, with one API listener active per trial. Both receive two logical CPUs on separate physical cores and a 2 GiB memory limit. Mock and Fortio each use a disjoint two-core CPU set and 2 GiB limit. Inactive gateways are stopped before each trial. HTTP, {params["connections"]} connections, {params["warmup"]}-second warmup and {params["duration"]}-second measurement. Access logging is disabled; no auth service, TLS, cache, guardrails or real model is enabled.','',
              'Agentgateway v1.5.0 and Praxis AI 0.5.0 released images are pinned by digest; exact images, fixture hashes, commands and CPU sets are in the manifest and inspections. The initial matrix uses a seeded treatment order per workload. This does not eliminate order effects.','',
              '## Fixed offered rates','',
              f'Baseline **{baseline}**, candidate **{candidate}**. Good QPS counts HTTP 200 responses per measured second. p99 is completion latency in milliseconds. Error columns count non-200 requests/timeouts. A † marks a fixed-rate trial that missed 99% of offered QPS or exceeded 0.1% errors.','',
              '| API | Bytes | Offered QPS | Baseline good QPS | Candidate good QPS | Baseline p99 ms | Candidate p99 ms | Errors baseline/candidate |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for case,size,qps in keys:
            if qps==0: continue
            a,b=indexed[case,size,qps,baseline],indexed[case,size,qps,candidate]
            amark="" if a.get("target_met",True) else "†"
            bmark="" if b.get("target_met",True) else "†"
            text.append(f"| {case} | {size} | {qps} | {a['successful_qps']:.1f}{amark} | {b['successful_qps']:.1f}{bmark} | {a['p99_ms']:.3f} | {b['p99_ms']:.3f} | {a['errors']}/{b['errors']} |")
        text+=['','## Saturation runs','',
               f'Offered QPS 0 tells Fortio to run at maximum throughput at the configured {params["connections"]} connections. Higher successful QPS is better within these configurations; the ratio below is candidate/baseline. It is not a universal speedup. Saturation latencies correspond to different achieved rates; do not interpret their difference as added proxy latency.','',
               '| API | Bytes | Baseline good QPS | Candidate good QPS | Ratio | Baseline p99 ms | Candidate p99 ms | Errors baseline/candidate |',
               '| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |']
        for case,size,qps in keys:
            if qps!=0: continue
            a,b=indexed[case,size,qps,baseline],indexed[case,size,qps,candidate]
            ratio=f"{b['successful_qps']/a['successful_qps']:.3f}×" if a['successful_qps'] else 'undefined'
            text.append(f"| {case} | {size} | {a['successful_qps']:.1f} | {b['successful_qps']:.1f} | {ratio} | {a['p99_ms']:.3f} | {b['p99_ms']:.3f} | {a['errors']}/{b['errors']} |")
        text+=['','## Correctness and limits','',
               f'The campaign preflight passed {len(checks)} JSON content/usage, incremental SSE and upstream 429 checks across the selected API paths, payload sizes and three treatments. Fortio validates response status during timed load; it does not parse every response body. Streaming was qualified at low load; the performance matrix measures nonstreaming requests. Synthetic usage fields are constants, not tokenizer results.','',
               'Fortio uses fixed concurrency, paced arrivals and disabled catch-up. A saturated client/gateway can miss offered QPS; its latency histogram is not a corrected open-loop latency distribution. Read achieved QPS and errors together with latency. Docker resource samples are approximate; no process-RSS or CPU-efficiency winner is claimed from them.','',
               'For translation, the direct backend receives native Chat Completions while gateways receive Anthropic Messages and translate. That baseline checks backend capacity; latency subtraction does not isolate translation cost. Built-in processing differs between products despite matching external behavior.','',
               'Keep this result separate from Gateway API controller tests and paused GPU inference work. Repeated/counterbalanced runs and a second load-generator check are required before broad public performance claims.','']
        (out/name).write_text('\n'.join(text))
    return rows


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--campaign',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--evidence-link',required=True)
    a=p.parse_args();render(a.campaign,a.output,a.evidence_link)
