#!/usr/bin/env python3
"""Read-only compact progress and latest observed health for long test jobs."""
import datetime
import json
import pathlib
import re
import subprocess

root = pathlib.Path('/opt/gateway-benchmark')
units = subprocess.run(['systemctl', 'list-units', '--state=running', '--no-legend', 'gwext-*'], capture_output=True, text=True)
print(units.stdout.strip() or 'No campaign systemd job running')
for p in sorted((root / 'results').rglob('full.log')):
    if (p.parent / 'end.txt').exists():
        continue
    content = p.read_text(errors='replace')
    top = re.findall(r'^=== RUN   TestConformance/([^/\n]+)$', content, re.M)
    all_cases = re.findall(r'^=== RUN   (TestConformance/[^\n]+)$', content, re.M)
    start = datetime.datetime.fromisoformat((p.parent / 'start.txt').read_text().strip().replace('Z', '+00:00'))
    now = datetime.datetime.now(datetime.timezone.utc)
    result = {'path': str(p.parent.relative_to(root)), 'elapsed_minutes': round((now-start).total_seconds()/60, 1),
              'top_level_test': top[-1] if top else 'Setup', 'current_subtest': all_cases[-1] if all_cases else None}
    runtime = p.parent / 'runtime.jsonl'
    if runtime.exists():
        with runtime.open('rb') as stream:
            stream.seek(max(0, runtime.stat().st_size - 2*1024*1024))
            lines = stream.read().decode(errors='replace').splitlines()
        row = None
        for line in reversed(lines):
            try:
                row = json.loads(line)
                break
            except json.JSONDecodeError:
                continue
        if row:
            result['snapshot_age_seconds'] = round((now-datetime.datetime.fromisoformat(row['utc'])).total_seconds())
            result['node_issues'] = [n['metadata']['name'] + '/' + c['type']
                for n in row.get('nodes', {}).get('items', []) for c in n.get('status', {}).get('conditions', [])
                if (c['type'] == 'Ready' and c['status'] != 'True') or (c['type'].endswith('Pressure') and c['status'] != 'False')]
            result['collection_errors'] = [k for k,v in row.items() if isinstance(v, dict) and ('error' in v or 'collector_error' in v)]
            result['controller_restarts'] = {pod['metadata']['name']:sum(c.get('restartCount', 0) for c in pod.get('status', {}).get('containerStatuses', []))
                for pod in row.get('pods', {}).get('items', []) if pod['metadata']['namespace'] in ['agentgateway-system', 'praxis-system']}
    print(json.dumps(result))
