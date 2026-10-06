#!/usr/bin/env python3
"""Check archive integrity and accidental credential artifacts before private upload."""
import argparse,hashlib,json,re,tarfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path('evidence/hosts'));p.add_argument('--output',type=Path,default=Path('evidence/archive-review.json'));a=p.parse_args()
rows=[];problems=[]
for file in sorted(a.root.glob('*.tar.gz')):
 sha=hashlib.sha256(file.read_bytes()).hexdigest();entries=0
 with tarfile.open(file) as archive:
  for entry in archive:
   entries+=1;name=entry.name
   if name.startswith('/') or '..' in Path(name).parts:problems.append(f'{file.name}: unsafe path {name}')
   if re.search(r'(^|/)(\.work|\.ssh|\.config|kubeconfig|client\.kubeconfig|benchmark\.kubeconfig|join-token|node-token|k3s-token|credentials\.db|application_default_credentials\.json)(/|$)',name):problems.append(f'{file.name}: credential path {name}')
   if entry.isfile():
    data=archive.extractfile(entry).read()
    if re.search(rb'client-key-data:[ \t]*[A-Za-z0-9+/=]{40,}',data) or re.search(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',data):
     problems.append(f'{file.name}: private credential content in {name}')
   if entry.issym() or entry.islnk():
    if entry.linkname.startswith('/') or '..' in Path(entry.linkname).parts:problems.append(f'{file.name}: external link {name}')
 rows.append({'file':file.name,'bytes':file.stat().st_size,'sha256':sha,'archive_entries':entries})
expected={'kclient.tar.gz','kcontrol.tar.gz','kcontroller.tar.gz','kgateway.tar.gz','kbackend.tar.gz'}
if {r['file'] for r in rows}!=expected:problems.append('Missing or extra host archive')
result={'archives':rows,'problems':problems,'passed':not problems,'scope':'Archive readability, checksums, unsafe paths and known credential filenames, and private-key content patterns. Also inspect exported file inventory and Git diff; this is not a general secret scanner.'}
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(bool(problems))
