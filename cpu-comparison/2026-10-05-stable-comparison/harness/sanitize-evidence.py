#!/usr/bin/env python3
"""Redact logged kubeconfig credentials; keep a per-member integrity ledger."""
import argparse,datetime,hashlib,io,json,os,re,tarfile,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('evidence/hosts'));p.add_argument('--ledger',type=Path,default=Path('evidence/credential-redactions.json'));a=p.parse_args()
old=json.loads(a.ledger.read_text()) if a.ledger.exists() else {'archives':{}}
patterns=[('kubeconfig-client-key-data',re.compile(rb'(client-key-data:[ \t]*)[A-Za-z0-9+/=]{40,}'),rb'\1REDACTED_EPHEMERAL_CLUSTER_CREDENTIAL'),('kubeconfig-client-certificate-data',re.compile(rb'(client-certificate-data:[ \t]*)[A-Za-z0-9+/=]{40,}'),rb'\1REDACTED_EPHEMERAL_CLUSTER_CREDENTIAL')]
patterns.append(('ephemeral-test-private-key',re.compile(rb'-----BEGIN ((?:RSA |EC |OPENSSH )?PRIVATE KEY)-----[\s\S]*?-----END \1-----'),b'REDACTED_EPHEMERAL_TEST_PRIVATE_KEY'))
for path in sorted(a.root.glob('*.tar.gz')):
 needs_redaction=False
 with tarfile.open(path,'r:gz') as source:
  for entry in source:
   if not entry.isfile():continue
   data=source.extractfile(entry).read()
   if b'\0' not in data and any(pattern.sub(replacement,data)!=data for _,pattern,replacement in patterns):
    needs_redaction=True;break
 if not needs_redaction:continue
 changes=[]
 fd,tmp=tempfile.mkstemp(prefix='sanitized-',suffix='.tar.gz',dir=path.parent);os.close(fd)
 try:
  with tarfile.open(path,'r:gz') as source,tarfile.open(tmp,'w:gz') as target:
   for entry in source:
    if not entry.isfile():target.addfile(entry);continue
    data=source.extractfile(entry).read();before=data;counts={}
    if b'\0' not in data:
     for name,pattern,replacement in patterns:
      data,n=pattern.subn(replacement,data)
      if n:counts[name]=n
    if data!=before:
     changes.append({'member':entry.name,'original_sha256':hashlib.sha256(before).hexdigest(),'sanitized_sha256':hashlib.sha256(data).hexdigest(),'redacted_fields':counts})
    entry.size=len(data);target.addfile(entry,io.BytesIO(data))
  if changes:
   os.replace(tmp,path);old['archives'][path.name]=changes
  else:os.unlink(tmp)
 except BaseException:
  Path(tmp).unlink(missing_ok=True);raise
old.update({'reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Any logged kubeconfig credential fields and generated test private keys are replaced before publication. Measurements and other log content are unchanged. Original per-member hashes allow reconciliation with first-pass integrity manifests; original credential-bearing files are never published.'})
a.ledger.write_text(json.dumps(old,indent=2)+'\n')
(a.root/'SHA256SUMS').write_text(''.join(hashlib.sha256(x.read_bytes()).hexdigest()+'  '+x.name+'\n' for x in sorted(a.root.glob('*.tar.gz'))))
print(json.dumps({'archives_with_redactions':list(old['archives']),'redacted_members':sum(len(x) for x in old['archives'].values())}))
