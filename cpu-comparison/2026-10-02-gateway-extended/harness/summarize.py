#!/usr/bin/env python3
"""Summarize upstream top-level test outcomes without counting subtests twice."""
import argparse,collections,json,re
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args()
catalog=json.loads((a.root/'evidence/test-catalog.json').read_text());tests={t['name']:t for t in catalog['tests']};channels={f['Name']:f['Channel'] for f in catalog['features']};selected={n:t for n,t in tests.items() if t['selected']}
core={'Gateway','HTTPRoute','ReferenceGrant'}
rows=[]
for log in sorted((a.root/'results').rglob('full.log')):
 case={};text=log.read_text(errors='replace')
 for status,name,seconds in re.findall(r'^    --- (PASS|FAIL|SKIP): TestConformance/([^/\s]+) \(([0-9.]+)s\)',text,re.M):case[name]={'outcome':status.lower(),'seconds':float(seconds)}
 records=[]
 for name,test in selected.items():
  fs=set(test['features']);category='http-core' if fs<=core else 'tls' if 'TLSRoute' in fs else 'grpc' if 'GRPCRoute' in fs else 'http-gateway-extended'
  records.append({'name':name,**case.get(name,{'outcome':'not-executed','seconds':None}),'category':category,'features':test['features'],'channel':'experimental' if any(channels.get(f)=='experimental' for f in fs) else 'standard','provisional':test['provisional']})
 counts=dict(collections.Counter(x['outcome'] for x in records))
 rows.append({'path':str(log.parent.relative_to(a.root)),'test_count':len(selected),'counts':counts,'records':records,'report_present':(log.parent/'report.yaml').exists(),'cleanup_complete':(log.parent/'CLEANUP-COMPLETE').exists()})
out=a.root/'reports/data';out.mkdir(parents=True,exist_ok=True);(out/'test-results.json').write_text(json.dumps(rows,indent=2)+'\n')
for r in rows:print(r['path'],r['counts'],'report',r['report_present'],'cleanup',r['cleanup_complete'])
