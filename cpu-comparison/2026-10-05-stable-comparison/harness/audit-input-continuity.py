#!/usr/bin/env python3
"""Compare accepted installed inputs and final container identities, not approvals."""
import argparse
import hashlib
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('exports', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
rows, issues = [], []


def check(first, final, role, relative):
    before = first / relative
    after = final / relative
    first_hash = hashlib.sha256(before.read_bytes()).hexdigest()
    final_hash = hashlib.sha256(after.read_bytes()).hexdigest() if after.exists() else None
    row = {'role': role, 'file': str(relative), 'first_sha256': first_hash,
           'final_sha256': final_hash, 'unchanged': first_hash == final_hash}
    rows.append(row)
    if not row['unchanged']:
        issues.append(row)


for role in ['client', 'gateway', 'backend', 'kclient', 'kgateway', 'kbackend',
             'kcontroller', 'kcontrol']:
    suite = 'cpu' if role in ['client', 'gateway', 'backend'] else 'kubernetes'
    first = a.exports / (suite + '-pass1') / role
    final = a.exports / (suite + '-final') / role
    assert first.is_dir() and final.is_dir()
    selected = {f.relative_to(first) for f in first.iterdir()
                if f.is_file() and f.suffix in ['.py', '.sh', '.yaml']}
    if (first / 'configs').exists():
        selected.update(f.relative_to(first) for f in (first / 'configs').rglob('*')
                        if f.is_file())
    # Capture times and transient process state are deliberately not byte-compared.
    for name in ['kernel.txt', 'os-release.txt', 'os-packages.txt',
                 'python-version.txt', 'python-freeze.txt', 'k3s-version.txt',
                 'host-tcp-profile.txt', 'maintenance-timers.txt']:
        relative = Path('runtime-inventory') / name
        if (first / relative).exists():
            selected.add(relative)
    for relative in sorted(selected):
        check(first, final, role, relative)

campaign = Path(__file__).resolve().parents[1]
expected = json.loads((campaign / 'evidence/qualification/cpu-pass1-input-image-review.json').read_text())['containers']
actual = json.loads((a.exports / 'cpu-final/gateway/runtime-inventory/gateway-container-inspect.json').read_text())
containers = []
for e in expected:
    c = next(x for x in actual if x['Name'] == e['name'])
    h = c['HostConfig']
    checks = {
        'container_id': c['Id'] == e['container_id'],
        'image_id': c['Image'] == e['image_id'],
        'requested_image': c['Config']['Image'] == e['image'],
        'cpu_quota': h['NanoCpus'] == e['cpu_quota'],
        'cpu_set': h['CpusetCpus'] == e['cpu_set'],
        'memory': h['Memory'] == e['memory_bytes'],
        'healthcheck': c['Config'].get('Healthcheck') == e['healthcheck'],
    }
    containers.append({'name': e['name'], 'checks': checks})
    if not all(checks.values()):
        issues.append({'container': e['name'], 'checks': checks})
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps({'files': rows, 'containers': containers,
                               'issues': issues}, indent=2) + '\n')
print(json.dumps({'files': len(rows), 'containers': len(containers), 'issues': len(issues)}))
