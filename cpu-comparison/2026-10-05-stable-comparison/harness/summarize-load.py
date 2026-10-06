#!/usr/bin/env python3
"""Extract every measured case; aggregate only complete three-repetition groups."""
import argparse,json,re,statistics
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();rows=[]
for f in sorted(a.root.rglob('execution.json')):
 relative=f.relative_to(a.root);parts=relative.parts
 if len(parts)<6 or parts[1]!='results' or (parts[0],parts[2]) not in [('client','common'),('client','native'),('kclient','kubernetes')]:continue
 if not re.fullmatch(r'pass[123]',parts[3]):continue
 passes=[(i,int(x[-1])) for i,x in enumerate(parts) if re.fullmatch(r'pass[123]',x)]
 if len(passes)!=1:continue
 index,rep=passes[0];profile=parts[index-1];treatment=parts[index+1];workload=parts[index+2]
 e=json.loads(f.read_text());case=e['case'];d=f.parent
 row={'profile':profile,'workload':workload,'pass':rep,'treatment':treatment,**case,'artifact':str(relative),'started':e['started'],'finished':e['finished'],'exits':[x['exit'] for x in e['processes']]}
 try:
  if case['tool']=='fortio':
   v=json.loads((d/'result.json').read_text());h=v['DurationHistogram'];n=h['Count'];ok=v['RetCodes'].get('200',0);seconds=v['ActualDuration']/1e9
   row.update(requests=n,errors=n-ok,error_percent=100*(n-ok)/n if n else None,requests_per_second=v['ActualQPS'],successful_requests_per_second=ok/seconds,latency_mean_ms=h['Avg']*1000,latency_p99_ms=next(x['Value']*1000 for x in h['Percentiles'] if x['Percentile']==99),status_counts=v['RetCodes'],duration_seconds=seconds)
  elif case['tool']=='aiperf':
   v=json.loads((d/'result/profile_export_aiperf.json').read_text())
   for name,unit in [('request_count','requests'),('request_throughput','requests/sec'),('request_latency','ms'),('time_to_first_token','ms'),('inter_token_latency','ms')]:
    assert v[name]['unit']==unit, 'Unexpected AIPerf metric unit: '+name
   for dest,src,stat in [('requests','completed_request_count','avg'),('successful_requests','request_count','avg'),('error_percent','request_error_rate','avg'),('successful_requests_per_second','request_throughput','avg'),('latency_mean_ms','request_latency','avg'),('latency_p99_ms','request_latency','p99'),('ttft_mean_ms','time_to_first_token','avg'),('ttft_p99_ms','time_to_first_token','p99'),('itl_mean_ms','inter_token_latency','avg'),('input_tokens','input_sequence_length','avg'),('output_tokens','output_sequence_length','avg'),('output_tokens_per_second','output_token_throughput','avg')]:row[dest]=v.get(src,{}).get(stat)
   row['errors']=v.get('error_request_count',{}).get('avg',0)
   if row['requests'] is None and row['successful_requests'] is not None:row['requests']=row['successful_requests']+row['errors']
   if row['error_percent'] is None and row['requests']:row['error_percent']=100*row['errors']/row['requests']
   row['aiperf_random_seed']=v.get('run_info',{}).get('random_seed')
   row['aiperf_complete']=v.get('is_complete',False)
   row['aiperf_error_summary']=v.get('error_summary',[])
  elif case['tool']=='nighthawk':
   v=json.loads((d/'result.json').read_text());g=next(x for x in v['results'] if x['name']=='global');c={x['name']:int(x['value']) for x in g['counters']};n=c.get('upstream_rq_total',0);ok=c.get('benchmark.http_2xx',0);seconds=float(g['execution_duration'].removesuffix('s'));completed=sum(x for k,x in c.items() if k.startswith('benchmark.http_'));resets=c.get('benchmark.stream_resets',0)
   h=next(x for x in g['statistics'] if x['id']=='benchmark_http_client.request_to_response');q=min((x for x in h['percentiles'] if x['percentile']>=.99),key=lambda x:x['percentile'])
   row.update(requests=n,successful_requests=ok,successful_requests_per_second=ok/seconds,requests_per_second=n/seconds,confirmed_non_2xx=completed-ok,stream_resets=resets,unaccounted_at_cutoff=max(0,n-completed-resets),latency_mean_ms=float(h['mean'].removesuffix('s'))*1000,latency_p99_upper_bracket_ms=float(q['duration'].removesuffix('s'))*1000,upper_bracket_percentile=q['percentile']*100,counters=c,duration_seconds=seconds)
  else:raise ValueError('Unknown tool: '+case['tool'])
  row['artifact_valid']=True
 except Exception as ex:row.update(artifact_valid=False,parse_error=repr(ex))
 rows.append(row)
keys=['profile','workload','treatment','tool','api','size','rate','concurrency','connections'];groups={}
for r in rows:groups.setdefault(tuple(r.get(k) for k in keys),[]).append(r)
summary=[]
for key,rs in groups.items():
 rs.sort(key=lambda r:r['pass']);s=dict(zip(keys,key));s['passes']=[r['pass'] for r in rs];s['three_complete_passes']=s['passes']==[1,2,3] and all(r['artifact_valid'] for r in rs);s['metrics']={}
 for metric in ['successful_requests_per_second','requests_per_second','errors','error_percent','confirmed_non_2xx','stream_resets','unaccounted_at_cutoff','latency_mean_ms','latency_p99_ms','latency_p99_upper_bracket_ms','ttft_mean_ms','ttft_p99_ms','itl_mean_ms','output_tokens_per_second']:
  vals=[r.get(metric) for r in rs]
  if vals and all(isinstance(v,(int,float)) for v in vals):s['metrics'][metric]={'per_pass':vals,'arithmetic_mean':statistics.mean(vals) if s['three_complete_passes'] else None,'min':min(vals),'max':max(vals),'sample_stddev':statistics.stdev(vals) if len(vals)>1 else None}
 summary.append(s)
a.output.mkdir(parents=True,exist_ok=True);(a.output/'load-rows.json').write_text(json.dumps(rows,indent=2)+'\n');(a.output/'load-summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({'rows':len(rows),'invalid_artifacts':sum(not r['artifact_valid'] for r in rows),'groups':len(summary),'complete_three_pass_groups':sum(x['three_complete_passes'] for x in summary)}))
