#!/usr/bin/env python3
"""Package one final snapshot per role, sanitize, and verify local retention."""
import datetime,hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
review=json.loads((root/'evidence/qualification/final-review.json').read_text())
assert review['infrastructure_valid'] and review['all_three_passes_reviewed']
analysis=root/'.work/analysis-final';assert analysis.is_dir()
out=root/'.work/publication';out.mkdir(exist_ok=False)
roles=['client','gateway','backend','kclient','kgateway','kbackend','kcontroller','kcontrol']
for role in roles:
 export=root/'.work/exports'/('cpu-final' if role in roles[:3] else 'kubernetes-final')
 source=analysis/role
 assert source.is_dir() and (export/'manifest.json').exists()
 assert (source/'host-samples.jsonl').stat().st_size>0
 with tarfile.open(out/(role+'.tar.gz'),'w:gz') as archive:
  archive.add(source,arcname='.')
 print(role,'packaged',flush=True)
ledger=root/'evidence/credential-redactions.json'
subprocess.run([sys.executable,str(root/'harness/sanitize-evidence.py'),'--root',str(out),'--ledger',str(ledger)],check=True)
files={}
for role in roles:
 path=out/(role+'.tar.gz')
 with tarfile.open(path,'r:gz') as archive:
  members=archive.getmembers()
  assert any(x.name=='./host-samples.jsonl' for x in members)
  for member in members:
   assert not member.issym() and not member.islnk(),'Unexpected link '+member.name
   assert '..' not in Path(member.name).parts and not member.name.startswith('/')
   if member.isfile():
    # Read every compressed member to detect truncation before cloud deletion.
    stream=archive.extractfile(member)
    while stream.read(1024*1024):pass
 files[path.name]={'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'bytes':path.stat().st_size,'members':len(members)}
record={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'files':files,'roles':roles,'scope':'All final role snapshots, including retained pilots/qualifications, raw measurements, configurations and telemetry. Credentials sanitized with member hashes. Verified full archive decompression before teardown.','publication':'Private GitHub release upload and remote digest verification remain separate steps.'}
(root/'evidence/EXPORTED.json').write_text(json.dumps(record,indent=2)+'\n')
shutil.copy2(root/'evidence/EXPORTED.json',out/'manifest.json')
print('All eight final archives locally verified; explicit teardown is now permitted',flush=True)
