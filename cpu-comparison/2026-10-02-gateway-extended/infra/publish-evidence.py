#!/usr/bin/env python3
"""Publish reviewed host archives to this private repository and verify digests."""
import datetime
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[1]
repo = 'solo-io/gateway-comparison-benchmarks'
tag = 'gateway-extended-2026-10-02'
gh = '/opt/homebrew/bin/gh'

def run(*args):
    return subprocess.run([gh, *args], check=True, capture_output=True, text=True).stdout

metadata = json.loads(run('api', 'repos/' + repo))
assert metadata['private'] and metadata['visibility'] == 'private', 'Private destination required'
review = json.loads((root / 'evidence/archive-review.json').read_text())
assert review['passed'] and not review['problems'], 'Archive review failed'
assert (root / 'reports/data/CAMPAIGN-VALIDATED.json').exists(), 'Campaign review required'
files = [root / 'evidence/hosts' / row['file'] for row in review['archives']]
files.append(root / 'evidence/hosts/SHA256SUMS')
for row in review['archives']:
    data = (root / 'evidence/hosts' / row['file']).read_bytes()
    assert len(data) == row['bytes'] and hashlib.sha256(data).hexdigest() == row['sha256']
# Do not replace an existing release or silently overwrite assets on retry.
existing = subprocess.run([gh, 'release', 'view', tag, '--repo', repo], capture_output=True)
assert existing.returncode != 0, 'Release exists; inspect and verify it instead of recreating it'
run('release', 'create', tag, *map(str, files), '--repo', repo, '--target', 'main',
    '--title', 'Extended Gateway API coverage: release and nightly campaigns',
    '--notes-file', str(root / 'reports/evidence-release-notes.md'))
release = json.loads(run('api', 'repos/' + repo + '/releases/tags/' + tag))
assets = {a['name']: a for a in release['assets']}
verified = []
for file in files:
    asset = assets[file.name]
    expected = hashlib.sha256(file.read_bytes()).hexdigest()
    assert asset['size'] == file.stat().st_size, file.name + ': size mismatch'
    assert asset.get('digest') == 'sha256:' + expected, file.name + ': absent or mismatched remote digest'
    verified.append({'file': file.name, 'bytes': asset['size'], 'sha256': expected,
                     'asset_id': asset['id'], 'url': asset['browser_download_url']})
(root / 'evidence/PUBLISHED.json').write_text(json.dumps({
    'verified_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'repository': repo, 'private': True, 'release': release['html_url'],
    'verification': 'Each remote asset size and GitHub SHA-256 digest equals the reviewed local file',
    'assets': verified,
}, indent=2) + '\n')
print(release['html_url'])
