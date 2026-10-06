#!/usr/bin/env python3
"""Emit review facts from retained artifacts; never grants an approval itself."""
import argparse,collections,hashlib,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--phase',required=True);p.add_argument('--profile',choices=['common','native','kubernetes'],required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
root=a.root/'results'/a.profile/a.phase
result={'profile':a.profile,'phase':a.phase,'treatments':{},'issues':[],'generated_message_corpora':[]}
for d in sorted(root.iterdir()):
 if not d.is_dir():continue
 t={'complete':(d/'COMPLETE').exists(),'load_cases':0,'nonzero_processes':[],'fortio_status_counts':{},'nighthawk_non_2xx':0,'nighthawk_resets':0,'nighthawk_cutoff_inflight':0,'aiperf_errors':0,'aiperf_completed_cases':0,'protocol_passed':0,'protocol_total':0,'cancellation_passed':0,'cancellation_total':0}
 for f in d.glob('protocol/results.json'):
  checks=json.loads(f.read_text());t['protocol_total']=len(checks);t['protocol_passed']=sum(x['passed'] for x in checks)
 for f in d.glob('cancellation.json'):
  checks=json.loads(f.read_text());t['cancellation_total']=len(checks);t['cancellation_passed']=sum(x['cancellation_propagated'] for x in checks)
 counts=collections.Counter()
 for f in sorted(d.rglob('execution.json')):
  try:
   e=json.loads(f.read_text());t['load_cases']+=1
   t['nonzero_processes'].extend({'artifact':str(f.relative_to(root)),'exit':x['exit']} for x in e['processes'] if x['exit']!=0)
   tool=e['case']['tool']
   if tool=='fortio':
    v=json.loads((f.parent/'result.json').read_text());counts.update(v['RetCodes'])
    assert sum(v['RetCodes'].values())==v['DurationHistogram']['Count']
   elif tool=='nighthawk':
    v=json.loads((f.parent/'result.json').read_text());g=next(x for x in v['results'] if x['name']=='global');c={x['name']:int(x['value']) for x in g['counters']}
    completed=sum(n for k,n in c.items() if k.startswith('benchmark.http_'));ok=c.get('benchmark.http_2xx',0);resets=c.get('benchmark.stream_resets',0)
    t['nighthawk_non_2xx']+=completed-ok;t['nighthawk_resets']+=resets;t['nighthawk_cutoff_inflight']+=max(0,c.get('upstream_rq_total',0)-completed-resets)
   elif tool=='aiperf':
    v=json.loads((f.parent/'result/profile_export_aiperf.json').read_text());t['aiperf_errors']+=v.get('error_request_count',{}).get('avg',0);t['aiperf_completed_cases']+=int(v.get('is_complete',False))
    assert v['run_info']['random_seed']==42
    assert v['input_sequence_length']['avg']==128 and v['output_sequence_length']['avg']==64
    assert v['input_sequence_length']['min']==v['input_sequence_length']['max']==128
    assert v['output_sequence_length']['min']==v['output_sequence_length']['max']==64
    assert v.get('is_complete') and not v.get('was_cancelled')
    inputs=json.loads((f.parent/'result/inputs.json').read_text());messages=[payload['messages'] for x in inputs['data'] for payload in x['payloads']]
    digest=hashlib.sha256(json.dumps(messages,sort_keys=True).encode()).hexdigest()
    result['generated_message_corpora'].append({'treatment':d.name,'case':e['case'],'messages':len(messages),'sha256':digest,'artifact':str(f.parent.relative_to(root))+'/result/inputs.json'})
   else:raise ValueError('Unknown load tool '+tool)
  except Exception as ex:result['issues'].append({'artifact':str(f.relative_to(root)),'error':repr(ex)})
 t['fortio_status_counts']=dict(counts)
 if (d/'setup-block/blocked.json').exists():t['setup_block']=json.loads((d/'setup-block/blocked.json').read_text())
 result['treatments'][d.name]=t
# Same configured API and concurrency must produce the same corpus across treatments.
groups={}
for x in result['generated_message_corpora']:
 key=(x['case']['api'],x['case']['concurrency']);groups.setdefault(key,[]).append(x)
for key,rs in groups.items():
 if len({r['sha256'] for r in rs})>1:result['issues'].append({'corpus_group':key,'error':'Generated message corpora differ','treatments':[r['treatment'] for r in rs]})
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'treatments':len(result['treatments']),'load_cases':sum(t['load_cases'] for t in result['treatments'].values()),'artifact_or_corpus_issues':len(result['issues'])}))
