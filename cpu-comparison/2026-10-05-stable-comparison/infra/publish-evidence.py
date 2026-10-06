#!/usr/bin/env python3
"""Publish reviewed evidence to the private campaign release and verify digests."""
import datetime,hashlib,json,subprocess,tempfile
from pathlib import Path
root=Path(__file__).resolve().parents[1];repo='solo-io/gateway-comparison-benchmarks';gh='/opt/homebrew/bin/gh';tag='cpu-2026-10-05-v1.6.0'
def run(args,**kw):return subprocess.run(args,capture_output=True,text=True,check=True,**kw)
assert json.loads((root/'evidence/qualification/final-review.json').read_text())['all_three_passes_reviewed']
assert not json.loads((root/'evidence/cleanup/VERIFIED.json').read_text())['remaining_campaign_resources']
privacy=json.loads(run([gh,'repo','view',repo,'--json','isPrivate,visibility']).stdout)
assert privacy['isPrivate'] and privacy['visibility']=='PRIVATE'
commit=run(['git','rev-parse','HEAD'],cwd=root).stdout.strip()
assert run(['git','rev-parse','origin/main'],cwd=root).stdout.strip()==commit,'Push the reviewed commit before creating its release'
export=json.loads((root/'evidence/EXPORTED.json').read_text());assets=root/'.work/publication'
for name,record in export['files'].items():assert hashlib.sha256((assets/name).read_bytes()).hexdigest()==record['sha256']
notes=root/'.work/release-notes.md'
notes.write_text('''Three-pass CPU comparison of agentgateway v1.6.0, Praxis core v0.5.2 and nightly-20261002, and the separately pinned Praxis AI v0.5.0 and October 2 nightly. Includes direct service baselines, protocol qualification, HTTP/AI load tests, Kubernetes route scale/recovery, and the focused corrected static-address test.

Archives contain raw outputs, configurations and resource samples, including labeled exclusions. Credentials are redacted with a per-member hash ledger. Verify SHA256SUMS before extraction. Read the campaign reports for validity boundaries and the stock operator/core nightly setup block. GPU inference remains paused. Campaign GCP resources were explicitly deleted and absence verified.
''')
existing=subprocess.run([gh,'api',f'repos/{repo}/releases/tags/{tag}'],capture_output=True,text=True)
if existing.returncode:
 assert '404' in existing.stderr,'Cannot establish whether release exists'
 run([gh,'release','create',tag,'--repo',repo,'--target',commit,'--title','Stable gateway comparison: October 5, 2026','--notes-file',str(notes)])
release=json.loads(run([gh,'api',f'repos/{repo}/releases/tags/{tag}']).stdout)
assert release['target_commitish']==commit,'Existing release points at a different reviewed commit'
files=[assets/name for name in sorted(export['files'])]+[assets/'SHA256SUMS',assets/'manifest.json',root/'evidence/credential-redactions.json']
existing_names={x['name'] for x in release['assets']}
for f in files:
 if f.name not in existing_names:run([gh,'release','upload',tag,str(f),'--repo',repo])
release=json.loads(run([gh,'api',f'repos/{repo}/releases/tags/{tag}']).stdout)
verified={}
for f in files:
 asset=next(x for x in release['assets'] if x['name']==f.name)
 digest=hashlib.sha256(f.read_bytes()).hexdigest()
 if asset.get('digest'):
  assert asset['digest']=='sha256:'+digest
 else:
  with tempfile.TemporaryDirectory(prefix='benchmark-verify-') as directory:
   run([gh,'release','download',tag,'--repo',repo,'--pattern',f.name,'--dir',directory])
   assert hashlib.sha256((Path(directory)/f.name).read_bytes()).hexdigest()==digest
 verified[f.name]={'sha256':digest,'bytes':asset['size'],'url':asset['browser_download_url'],'github_digest':asset.get('digest')}
record={'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':repo,'visibility':'PRIVATE','tag':tag,'commit':commit,'release_url':release['html_url'],'assets':verified}
(root/'evidence/PUBLISHED.json').write_text(json.dumps(record,indent=2)+'\n');print(release['html_url'])
