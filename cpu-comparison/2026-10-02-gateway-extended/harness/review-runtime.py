#!/usr/bin/env python3
"""Summarize runtime evidence for human review; never auto-certify validity."""
import argparse
import collections
import datetime
import json
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('case', type=Path)
parser.add_argument('--output', type=Path)
args = parser.parse_args()
rows = []
truncated = False
for line in (args.case / 'runtime.jsonl').read_text().splitlines():
    try:
        rows.append(json.loads(line))
    except json.JSONDecodeError:
        truncated = True
issues, errors, restarts, images, warnings, terminations = {}, [], {}, set(), {}, {}
times = []
for row in rows:
    times.append(datetime.datetime.fromisoformat(row['utc']))
    for kind, data in row.items():
        if isinstance(data, dict) and ('error' in data or 'collector_error' in data):
            errors.append({'utc': row['utc'], 'kind': kind, 'detail': data})
    for node in row.get('nodes', {}).get('items', []):
        name = node['metadata']['name']
        for condition in node.get('status', {}).get('conditions', []):
            bad = (condition['type'] == 'Ready' and condition['status'] != 'True') or (
                condition['type'].endswith('Pressure') and condition['status'] != 'False')
            if bad:
                issues[name + '/' + condition['type']] = condition
    for pod in row.get('pods', {}).get('items', []):
        meta = pod['metadata']
        for container in pod.get('status', {}).get('containerStatuses', []):
            key = meta['namespace'] + '/' + meta['name'] + '/' + container['name']
            images.add(container.get('imageID', container.get('image', 'unknown')))
            if container.get('restartCount', 0):
                restarts[key] = max(restarts.get(key, 0), container['restartCount'])
            for state_key in ['state', 'lastState']:
                terminated = container.get(state_key, {}).get('terminated')
                if terminated:
                    terminations[key] = terminated
    for event in row.get('events', {}).get('items', []):
        if event.get('type') != 'Warning':
            continue
        obj = event.get('involvedObject', {})
        key = event['metadata']['uid']
        warnings[key] = {k: event.get(k) for k in ['reason', 'message', 'firstTimestamp', 'lastTimestamp', 'count']}
        warnings[key]['object'] = '/'.join(obj.get(k, '') for k in ['namespace', 'kind', 'name'])
result = {
    'case': str(args.case), 'snapshots': len(rows), 'truncated_row': truncated,
    'first_snapshot': str(times[0]) if times else None,
    'last_snapshot': str(times[-1]) if times else None,
    'maximum_snapshot_gap_seconds': max(((b-a).total_seconds() for a,b in zip(times,times[1:])), default=0),
    'node_issues': issues, 'collection_errors': errors,
    'containers_with_restart_count': restarts, 'terminations': terminations,
    'observed_image_ids': sorted(images), 'warning_events': list(warnings.values()),
    'warning_reason_counts': dict(collections.Counter(e['reason'] for e in warnings.values())),
    'cleanup_complete': (args.case/'CLEANUP-COMPLETE').exists(),
    'job_finished': (args.case/'JOB-FINISHED').exists(),
    'review_note': 'Events can precede the run; assess timestamps and product behavior before classifying infrastructure validity.'
}
text = json.dumps(result, indent=2) + '\n'
if args.output:
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
else:
    print(text, end='')
