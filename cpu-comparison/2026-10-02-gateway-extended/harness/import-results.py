#!/usr/bin/env python3
"""Import a local raw snapshot, redacting generated private keys before Git publication."""
import argparse,hashlib,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('snapshot',type=Path);p.add_argument('root',type=Path);a=p.parse_args()
changes={}
pattern=re.compile(rb'-----BEGIN ((?:RSA |EC |OPENSSH )?PRIVATE KEY)-----[\s\S]*?-----END \1-----')
for src in (a.snapshot/'results').rglob('*'):
 if not src.is_file():continue
 rel=src.relative_to(a.snapshot);dst=a.root/rel;dst.parent.mkdir(parents=True,exist_ok=True);data=src.read_bytes();clean,n=pattern.subn(b'REDACTED_EPHEMERAL_TEST_PRIVATE_KEY',data);dst.write_bytes(clean)
 if n:changes[str(rel)]={'original_sha256':hashlib.sha256(data).hexdigest(),'sanitized_sha256':hashlib.sha256(clean).hexdigest(),'redacted_ephemeral_test_private_keys':n}
(a.root/'evidence/result-redactions.json').write_text(json.dumps(changes,indent=2)+'\n')
print('Imported snapshot; redacted private keys in',len(changes),'files')
