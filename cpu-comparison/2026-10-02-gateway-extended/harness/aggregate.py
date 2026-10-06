#!/usr/bin/env python3
"""Aggregate three repetitions without treating missing coverage as failures."""
import collections
import json
import statistics
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = {r['path']: r for r in json.loads((root/'reports/data/test-results.json').read_text())}
result = {}
for campaign in ['praxis-v0.5.2', 'praxis-nightly-20261002']:
    result[campaign] = {}
    for product in ['agentgateway', 'praxis']:
        runs = [rows.get(f'results/{campaign}/pass{i}/{product}') for i in range(1,4)]
        completed = [r for r in runs if r and r['cleanup_complete']]
        scored = [r for r in completed if sum(r['counts'].get(s,0) for s in ['pass','fail']) == r['test_count']]
        data = {
            'repetitions_recorded': len([r for r in runs if r]),
            'repetitions_cleaned_up': len(completed),
            'repetitions_with_all_107_tests_scored': len(scored),
            'repetition_counts': [r['counts'] if r else None for r in runs],
            'mean_pass_count': statistics.mean(r['counts'].get('pass',0) for r in scored) if len(scored)==3 else None,
            'mean_pass_percentage': statistics.mean(r['counts'].get('pass',0)/r['test_count']*100 for r in scored) if len(scored)==3 else None,
            'categories': {}, 'channels': {}, 'repeatability': {},
        }
        for dimension, key in [('categories','category'), ('channels','channel')]:
            for group in sorted({t[key] for r in completed for t in r['records']}):
                data[dimension][group] = [dict(collections.Counter(t['outcome'] for t in r['records'] if t[key]==group)) if r else None for r in runs]
        if len(completed)==3:
            for name in sorted(t['name'] for t in completed[0]['records']):
                data['repeatability'][name] = [next(t['outcome'] for t in r['records'] if t['name']==name) for r in runs]
        result[campaign][product] = data
(root/'reports/data/aggregate.json').write_text(json.dumps(result,indent=2)+'\n')
for campaign, products in result.items():
    for product, data in products.items():
        print(campaign, product, data['repetition_counts'], 'mean', data['mean_pass_count'])
