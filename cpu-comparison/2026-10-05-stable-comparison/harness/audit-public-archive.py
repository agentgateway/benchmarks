#!/usr/bin/env python3
"""Inventory a proposed public evidence archive without printing credential values."""
import argparse
import collections
import datetime
import hashlib
import json
import re
import tarfile
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('archive', type=Path)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
patterns = {
    'private_key': rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'kubeconfig_key': rb'client-key-data:[ \t]*[A-Za-z0-9+/=]{40,}',
    'kubeconfig_certificate': rb'client-certificate-data:[ \t]*[A-Za-z0-9+/=]{40,}',
    'jwt': rb'eyJ[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}\.[A-Za-z0-9_-]{15,}',
    'gcp_key': rb'"private_key_id"\s*:',
    'github_token': rb'(?:ghp_|github_pat_)[A-Za-z0-9_]{20,}',
    'k3s_join_token': rb'K10[0-9a-f]{64}::',
    'encoded_tls_key': rb'"tls\.key"\s*:\s*"[A-Za-z0-9+/=]{40,}"',
}
hits, inventory, path_issues = [], [], []
counts = collections.Counter()
with tarfile.open(a.archive, 'r:gz') as archive:
    for member in archive:
        path = Path(member.name)
        if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk():
            path_issues.append(member.name)
        if not member.isfile():
            continue
        if any(x in path.name.lower() for x in ['kubeconfig', 'k3s-token', 'id_rsa', 'id_ed25519']):
            path_issues.append(member.name)
        data = archive.extractfile(member).read()
        counts[path.parts[0]] += 1
        inventory.append({'path': member.name, 'bytes': len(data),
                          'sha256': hashlib.sha256(data).hexdigest()})
        for name, pattern in patterns.items():
            count = len(re.findall(pattern, data))
            if count:
                hits.append({'path': member.name, 'pattern': name, 'count': count})
record = {
    'reviewed_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'archive': a.archive.name,
    'sha256': hashlib.sha256(a.archive.read_bytes()).hexdigest(),
    'files_read': len(inventory), 'top_level_files': dict(counts),
    'credential_pattern_hits': hits, 'path_issues': path_issues,
    'files': inventory,
    'limitation': 'A pattern scan is a review aid, not a complete secret detector. '
                  'Publication still requires content review and authorization.',
}
a.output.parent.mkdir(parents=True, exist_ok=True)
a.output.write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps({'files_read': len(inventory), 'credential_pattern_hits': len(hits),
                  'path_issues': len(path_issues)}))
raise SystemExit(bool(hits or path_issues))
