#!/usr/bin/env python3
"""Retain the calculations behind the CPU article's scoped throughput claims."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('data', type=Path)
p.add_argument('--review', type=Path, required=True)
a = p.parse_args()
review = json.loads(a.review.read_text())
assert review['infrastructure_valid'] and review['all_three_passes_reviewed']
source = a.data / 'load-summary.json'
groups = json.loads(source.read_text())
rows = json.loads((a.data / 'load-rows.json').read_text())
assert len(groups) == 274 and len(rows) == 822
assert all(g['three_complete_passes'] for g in groups)
keys = ['profile', 'workload', 'tool', 'api', 'size', 'rate', 'concurrency', 'connections']
lookup = {(tuple(g[k] for k in keys), g['treatment']): g for g in groups}
comparisons = []
for g in groups:
    if not g['treatment'].startswith('praxis') or g['tool'] != 'fortio' or g['rate'] != 0:
        continue
    ag = lookup[(tuple(g[k] for k in keys), 'agentgateway')]
    am = ag['metrics']['successful_requests_per_second']
    pm = g['metrics']['successful_requests_per_second']
    cases = [r for r in rows if all(r.get(k) == g[k] for k in keys)
             and r['treatment'] in ['agentgateway', g['treatment']]]
    assert len(cases) == 6
    comparisons.append({**{k: g[k] for k in keys}, 'praxis_treatment': g['treatment'],
                        'agentgateway_rps': am, 'praxis_rps': pm,
                        'ratio_of_means_agentgateway_over_praxis': am['arithmetic_mean'] / pm['arithmetic_mean'],
                        'raw_execution_artifacts': [r['artifact'] for r in cases]})
large = [r for r in comparisons if r['profile'] == 'native' and r['size'] == 16384
         and r['concurrency'] == 32]
assert len(large) == 6
range_groups = {}
for label, apis in [('native_protocols', ['openai', 'anthropic']), ('translation', ['translation'])]:
    selected = [r for r in large if r['api'] in apis]
    ratios = [r['ratio_of_means_agentgateway_over_praxis'] for r in selected]
    range_groups[label] = {'minimum_ratio': min(ratios), 'maximum_ratio': max(ratios),
                           'scope': 'Native profile, 16 KiB content, 32 connections, unlimited offered rate; both Praxis AI builds',
                           'cases': [{k: r[k] for k in keys + ['praxis_treatment']} for r in selected]}
http_counts = {}
for t in ['praxis-release', 'praxis-nightly']:
    selected = [r for r in comparisons if r['profile'] == 'common'
                and r['workload'] == 'http' and r['praxis_treatment'] == t]
    assert len(selected) == 6
    http_counts[t] = {'higher_mean_than_agentgateway': sum(r['ratio_of_means_agentgateway_over_praxis'] < 1 for r in selected),
                      'cases': len(selected), 'interpretation': 'Descriptive count in this matrix, not an overall score'}
record = {'source': source.name, 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'method': 'All three accepted runs; ratios of arithmetic mean successful RPS. No best-run selection or pooled latency percentile.',
          'native_large_payload_ratio_ranges': range_groups,
          'common_http_unlimited_praxis_leads': http_counts,
          'unlimited_fortio_comparisons': comparisons,
          'load_cases': len(rows),
          'confirmed_errors_or_resets': sum(r.get('errors', 0) + r.get('confirmed_non_2xx', 0) + r.get('stream_resets', 0) for r in rows),
          'nighthawk_inflight_at_cutoff': sum(r.get('unaccounted_at_cutoff', 0) for r in rows)}
(a.data / 'article-calculations.json').write_text(json.dumps(record, indent=2) + '\n')
print('Retained scoped article calculations and their raw artifact references')
