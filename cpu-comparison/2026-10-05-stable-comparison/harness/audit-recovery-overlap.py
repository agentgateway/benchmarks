#!/usr/bin/env python3
"""Describe process overlap near graceful probe-window ends; not a pass/fail gate."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('root', type=Path, help='Analysis root containing kclient and kgateway')
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
samples = [json.loads(line) for line in (a.root / 'kgateway/host-samples.jsonl').read_text().splitlines()]
rows = []
for phase in ['pass1', 'pass2', 'pass3']:
    for treatment in ['agentgateway', 'praxis-release']:
        path = a.root / 'kclient/results/kubernetes' / phase / treatment / 'recovery/data-plane/probes.jsonl'
        if not path.exists():
            continue
        probes = [json.loads(line) for line in path.read_text().splitlines()]
        first, last = probes[0]['utc'], probes[-1]['utc']
        selected = [s for s in samples if first <= s['utc'] <= last]
        assert selected, 'No retained samples for ' + str(path)
        snapshots = [{'utc': s['utc'],
                      'pids': sorted(c['pid'] for c in s.get('containers', [])
                                     if c['name'].startswith('gateway-benchmark/'))}
                     for s in [selected[0], selected[-1]]]
        rows.append({'pass': phase, 'treatment': treatment,
                     'artifact': str(path.relative_to(a.root)),
                     'first_probe': first, 'last_probe': last,
                     'first_and_last_host_samples': snapshots,
                     'initial_process_present_in_last_sample': bool(
                         set(snapshots[0]['pids']) & set(snapshots[-1]['pids']))})
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps({
    'observations': rows,
    'interpretation': 'The HTTPX probes reuse connections. Presence in the last '
                      'sample means observed process overlap near the window end, '
                      'not proof of the destination for each request. The last '
                      'sample can precede the final probe. These probes do not '
                      'establish complete handoff, fresh-connection availability '
                      'or hard-failure recovery.'}, indent=2) + '\n')
print(json.dumps({'windows': len(rows), 'initial_process_present_near_end': sum(
    r['initial_process_present_in_last_sample'] for r in rows)}))
