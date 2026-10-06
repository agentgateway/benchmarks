#!/usr/bin/env python3
"""Save previous operator logs when the existing runtime observer sees a restart.

Read-only auxiliary diagnostics; does not change the workload or any test assertion.
Run repeatedly while a Praxis case is active. The runtime observer already collects
pod state, so this helper does not add another list-pods request.
"""
import argparse
import json
import os
import pathlib
import subprocess

p = argparse.ArgumentParser()
p.add_argument('case', type=pathlib.Path)
a = p.parse_args()
f = a.case / 'runtime.jsonl'
if not f.exists():
    raise SystemExit(0)
with f.open('rb') as stream:
    stream.seek(max(0, f.stat().st_size - 2 * 1024 * 1024))
    rows = stream.read().decode(errors='replace').splitlines()
row = None
for line in reversed(rows):
    try:
        row = json.loads(line)
        break
    except json.JSONDecodeError:
        continue
if row is None:
    raise SystemExit(0)
for pod in row.get('pods', {}).get('items', []):
    meta = pod['metadata']
    if meta['namespace'] != 'praxis-system':
        continue
    for c in pod.get('status', {}).get('containerStatuses', []):
        count = c.get('restartCount', 0)
        if not count:
            continue
        stem = meta['name'] + '-' + c['name'] + '-restart' + str(count)
        target = a.case / (stem + '.log')
        if target.exists():
            continue
        env = dict(os.environ, KUBECONFIG='/etc/rancher/k3s/benchmark.kubeconfig')
        r = subprocess.run(['kubectl', 'logs', '-n', meta['namespace'], meta['name'],
                            '-c', c['name'], '--previous', '--timestamps'],
                           capture_output=True, text=True, timeout=20, env=env)
        (a.case / (stem + '-capture.json')).write_text(json.dumps({
            'observer_utc': row['utc'], 'pod_uid': meta['uid'],
            'restart_count': count, 'exit': r.returncode, 'stderr': r.stderr,
            'last_state': c.get('lastState'),
        }, indent=2) + '\n')
        if r.returncode == 0:
            target.write_text(r.stdout)
            print('Captured ' + target.name)
