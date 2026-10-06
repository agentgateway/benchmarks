#!/usr/bin/env python3
"""Prepare a synthetic technical-evidence subset; never publish automatically."""
import datetime
import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
review = json.loads((root / 'evidence/qualification/final-review.json').read_text())
assert review['infrastructure_valid'] and review['all_three_passes_reviewed']
assert (root / 'evidence/cleanup/VERIFIED.json').exists()
source = root / '.work/analysis-final'
out = root / '.work/public-evidence'
out.mkdir(exist_ok=False)
selected = set()
for role, profiles in [('client', ['common', 'native']),
                       ('kclient', ['kubernetes', 'static-address'])]:
    for profile in profiles:
        for phase in ['pass1', 'pass2', 'pass3']:
            folder = source / role / 'results' / profile / phase
            assert folder.is_dir()
            selected.update(f for f in folder.rglob('*') if f.is_file())
# Resource evidence has process/cgroup metrics, not VM administration metadata.
for role in ['client', 'gateway', 'backend', 'kclient', 'kgateway', 'kbackend',
             'kcontroller', 'kcontrol']:
    selected.add(source / role / 'host-samples.jsonl')
for name in ['agentgateway.yaml', 'agentgateway-native.yaml', 'praxis.yaml',
             'praxis-native.yaml']:
    selected.add(source / 'gateway' / name)
selected.update(f for f in (source / 'kclient/configs').rglob('*') if f.is_file())
for phase in ['pass1', 'pass2', 'pass3']:
    for count in [1000, 5000]:
        folder = source / 'kclient/diagnostics' / f'{phase}-praxis-release-{count}'
        observation = source / 'kclient/results/kubernetes' / phase / 'praxis-release' / f'scale-{count}/observations/created-result.json'
        if not json.loads(observation.read_text())['complete']:
            assert folder.is_dir(), 'Retain nonconvergence diagnostics before preparing public evidence'
        if folder.is_dir():
            selected.update(f for f in folder.rglob('*') if f.is_file())
files = []
with tarfile.open(out / 'accepted-results.tar.gz', 'w:gz') as archive:
    for f in sorted(selected):
        assert f.is_file() and not f.is_symlink()
        name = str(f.relative_to(source))
        assert not any(x in f.name.lower() for x in ['kubeconfig', 'k3s-token'])
        files.append({'path': name, 'bytes': f.stat().st_size,
                      'source_sha256': hashlib.sha256(f.read_bytes()).hexdigest()})
        archive.add(f, arcname=name, recursive=False)
subprocess.run([sys.executable, str(root / 'harness/sanitize-evidence.py'),
                '--root', str(out), '--ledger', str(out / 'redactions.json')], check=True)
archive_path = out / 'accepted-results.tar.gz'
with tarfile.open(archive_path, 'r:gz') as archive:
    members = archive.getmembers()
    assert len(members) == len(files)
    for member in members:
        assert member.isfile() and not member.name.startswith('/')
        assert '..' not in Path(member.name).parts
        stream = archive.extractfile(member)
        while stream.read(1024 * 1024):
            pass
record = {
    'prepared_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Synthetic accepted CPU/Kubernetes measurements, configurations, '
             'route-scale diagnostics and resource samples. Excludes cloud '
             'administration inventories, internal strategy, and cluster credential files. '
             'Retained log credential fields are sanitized with a separate ledger.',
    'publication_status': 'Prepared only; content and credential review required before publication.',
    'file': archive_path.name,
    'bytes': archive_path.stat().st_size,
    'sha256': hashlib.sha256(archive_path.read_bytes()).hexdigest(),
    'source_files': files,
}
(out / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
print('Synthetic technical subset prepared; inspect content before any public upload.')
