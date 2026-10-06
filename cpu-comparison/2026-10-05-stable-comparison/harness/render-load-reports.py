#!/usr/bin/env python3
"""Render complete matrices after manual validity review; no selective case filter."""
import argparse,json,statistics,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--review',type=Path,required=True);p.add_argument('--matrices-only',action='store_true',help='Render the complete numeric matrices without internal report navigation');a=p.parse_args()
review=json.loads(a.review.read_text());assert review['infrastructure_valid'] is True and review['all_three_passes_reviewed'] is True
rows=json.loads((a.data/'load-rows.json').read_text());groups=json.loads((a.data/'load-summary.json').read_text())
assert len(rows)==822 and len(groups)==274 and all(g['three_complete_passes'] for g in groups)
assert all(r['artifact_valid'] and all(x==0 for x in r['exits']) for r in rows)
out=a.output;out.mkdir(parents=True,exist_ok=True);mat=out/'matrices';mat.mkdir(exist_ok=True)
labels={'direct':'Direct service','agentgateway':'Agentgateway v1.6.0','praxis-release':'Praxis core v0.5.2','praxis-nightly':'Praxis core nightly-20261002','praxis':'Praxis AI v0.5.0','praxis-ai-nightly':'Praxis AI Oct 2 nightly'}
profile_labels={'common':'Standalone common forwarding','native':'Standalone native AI','kubernetes':'Kubernetes HTTP'}
def mean(g,key):return g['metrics'].get(key,{}).get('arithmetic_mean')
def fmt(v):return '—' if v is None else (f'{v:,.0f}' if abs(v)>=1000 else f'{v:.3f}')
def metric(g,key):
 m=g['metrics'].get(key)
 return '—' if not m else f"{fmt(m['arithmetic_mean'])} [{fmt(m['min'])}–{fmt(m['max'])}]"
def case(g):
 if g['tool']=='aiperf':return f"{g['api']}, {g['concurrency']} streams"
 rate='unlimited' if g['rate']==0 else str(g['rate'])+' RPS'
 conc=g['connections'] if g['tool']=='nighthawk' else g['concurrency']
 return f"{g['api']+' / ' if g['api'] else ''}{g['size']} B content, {conc} connections, {rate}"
def key(g):return (g['tool'],g.get('api') or '',g.get('size') or 0,g.get('concurrency') or 0,g.get('rate') or 0,g.get('connections') or 0)
intro='''Values are arithmetic means of three runs followed by [minimum–maximum].
Latency p99 is the mean of each run's p99, **not a pooled p99**. RPS counts successful
responses. Fortio latency includes all response statuses. Do not compare different
workloads, traffic rates, APIs or deployment profiles as if they were equal work.
Every individual pass and raw artifact path is in [load-rows.json](../data/load-rows.json).
'''
for profile,workload in [('common','http'),('common','ai'),('native','ai'),('kubernetes','http')]:
 gs=[g for g in groups if g['profile']==profile and g['workload']==workload]
 lines=[f'# {profile_labels[profile]}: {workload.upper()} matrix','',intro]
 if profile=='native':lines+=['Praxis AI response usage extraction and agentgateway LLM processing are distinct implementations. Translation has an OpenAI direct baseline and Anthropic gateway clients. These ratios do not isolate equal accounting work.','']
 if profile=='kubernetes':lines+=['The pinned operator/core nightly pairing could not start; it is **not evaluated**, not zero throughput.','']
 for tool in ['fortio','nighthawk','aiperf']:
  selected=sorted([g for g in gs if g['tool']==tool],key=lambda g:(key(g),list(labels).index(g['treatment'])))
  if not selected:continue
  lines += [f'## {tool}','']
  if tool=='aiperf':
   lines += ['| Case | Treatment | Successful RPS | Mean TTFT ms | p99 TTFT ms | Mean ITL ms | Errors per run |','| --- | --- | ---: | ---: | ---: | ---: | ---: |']
   for g in selected:lines.append('| '+' | '.join([case(g),labels[g['treatment']],metric(g,'successful_requests_per_second'),metric(g,'ttft_mean_ms'),metric(g,'ttft_p99_ms'),metric(g,'itl_mean_ms'),metric(g,'errors')])+' |')
  else:
   lines += ['| Case | Treatment | Successful RPS | Mean latency ms | p99 latency ms | Error evidence |','| --- | --- | ---: | ---: | ---: | --- |']
   for g in selected:
    latency='latency_p99_upper_bracket_ms' if tool=='nighthawk' else 'latency_p99_ms'
    error=('non-2xx '+metric(g,'confirmed_non_2xx')+'; resets '+metric(g,'stream_resets')+'; in flight at cutoff '+metric(g,'unaccounted_at_cutoff')) if tool=='nighthawk' else metric(g,'errors')+' errors/run'
    lines.append('| '+' | '.join([case(g),labels[g['treatment']],metric(g,'successful_requests_per_second'),metric(g,'latency_mean_ms'),metric(g,latency)+(' †' if tool=='nighthawk' else ''),error])+' |')
   if tool=='nighthawk':lines+=['','† Nighthawk reports the nearest quantile at or above p99; the exact percentile is retained per run. In-flight requests at cutoff are distinct from confirmed failures.']
  lines+=['']
 (mat/(profile+'-'+workload+'.md')).write_text('\n'.join(lines).rstrip()+'\n')
if a.matrices_only:
 print('Rendered four complete matrices');sys.exit(0)
# Comparison ratios use means of successful throughput, never attempted throughput.
lookup={(g['profile'],g['workload'],key(g),g['treatment']):g for g in groups}
comparisons=[]
for g in groups:
 if g['treatment']=='direct':continue
 ref=lookup[(g['profile'],g['workload'],key(g),'agentgateway')]
 direct=lookup[(g['profile'],g['workload'],key(g),'direct')]
 comparisons.append({'profile':g['profile'],'workload':g['workload'],'case':case(g),'tool':g['tool'],'treatment':g['treatment'],'successful_rps_mean':mean(g,'successful_requests_per_second'),'fraction_of_direct_successful_rps':mean(g,'successful_requests_per_second')/mean(direct,'successful_requests_per_second'),'agentgateway_over_treatment_successful_rps':mean(ref,'successful_requests_per_second')/mean(g,'successful_requests_per_second'),'mean_latency_delta_from_direct_ms':None if mean(g,'latency_mean_ms') is None else mean(g,'latency_mean_ms')-mean(direct,'latency_mean_ms')})
(a.data/'load-comparisons.json').write_text(json.dumps(comparisons,indent=2)+'\n')
lines=['# Agentgateway v1.6.0 versus direct service','', 'This report compares the configured agentgateway path with the direct service path. The difference includes the extra network hop and configured gateway processing; it does not isolate intrinsic proxy CPU cost. The baseline is the same deterministic service on a separate VM; it does not include model inference. Results from older releases are not inputs to these averages.','', 'Use the full matrices for every rate and payload: [common HTTP](matrices/common-http.md), [common AI transport](matrices/common-ai.md), [native AI](matrices/native-ai.md), [Kubernetes HTTP](matrices/kubernetes-http.md).','', '## Unlimited-rate Fortio cases','', 'Ratios below are gateway successful throughput divided by direct throughput. Latency deltas are differences of three-run means; these are not per-request paired measurements. Unlimited-rate paths operate at different achieved rates, so these deltas do not isolate per-request proxy overhead. For fixed-rate comparisons, read delivered rate and errors beside latency.','', '| Profile | Case | Agentgateway successful RPS | Direct successful RPS | Fraction of direct | Mean latency delta ms |','| --- | --- | ---: | ---: | ---: | ---: |']
for g in groups:
 if g['treatment']!='agentgateway' or g['tool']!='fortio' or g['rate']!=0:continue
 d=lookup[(g['profile'],g['workload'],key(g),'direct')]
 lines.append('| '+' | '.join([profile_labels[g['profile']],case(g),metric(g,'successful_requests_per_second'),metric(d,'successful_requests_per_second'),f"{mean(g,'successful_requests_per_second')/mean(d,'successful_requests_per_second'):.3f}",fmt(mean(g,'latency_mean_ms')-mean(d,'latency_mean_ms'))])+' |')
lines+=['','## Reading the streaming results','', 'The synthetic service emits 64 tokens after a nominal 25 ms initial delay, then 5 ms between tokens. AIPerf reports client-observed TTFT and ITL. These include service pacing, scheduling and network effects; they are not GPU inference performance. At fixed concurrency the backend pacing limits throughput, so small RPS differences need the latency ranges and errors beside them.','', 'All full-matrix cells retain individual-run variation. Three runs on one placement provide descriptive repeatability, not a cloud-wide confidence interval. See [methodology and validity](05-methodology-and-validity.md).']
lines+=['', 'Sampled CPU, cgroup memory and descriptor evidence is reported separately in [resource usage](08-resource-usage.md); those windows include startup and warmup.']
(out/'01-agentgateway-vs-direct.md').write_text('\n'.join(lines).rstrip()+'\n')
lines=['# Praxis versus agentgateway v1.6.0','', 'Core v0.5.2, core nightly-20261002, AI v0.5.0 and the October 2 AI nightly are separate treatments. Common forwarding uses matching transport responsibilities. Native AI exercises configured functionality with different routing/accounting implementations; do not interpret native ratios as equal-work efficiency.','', 'Every fixed-rate, capacity and streaming case appears in the full matrices: [common HTTP](matrices/common-http.md), [common AI transport](matrices/common-ai.md), [native AI](matrices/native-ai.md), [Kubernetes HTTP](matrices/kubernetes-http.md).','', '## Unlimited-rate Fortio cases','', 'The ratio is agentgateway mean successful RPS divided by Praxis mean successful RPS. Greater than 1 favors agentgateway for this case; less than 1 favors Praxis. It is not an overall score. No best-run selection is used.','', '| Profile | Case | Praxis image | Agentgateway successful RPS | Praxis successful RPS | Agentgateway / Praxis |','| --- | --- | --- | ---: | ---: | ---: |']
for g in groups:
 if not g['treatment'].startswith('praxis') or g['tool']!='fortio' or g['rate']!=0:continue
 ag=lookup[(g['profile'],g['workload'],key(g),'agentgateway')]
 lines.append('| '+' | '.join([profile_labels[g['profile']],case(g),labels[g['treatment']],metric(ag,'successful_requests_per_second'),metric(g,'successful_requests_per_second'),f"{mean(ag,'successful_requests_per_second')/mean(g,'successful_requests_per_second'):.3f}×"] )+' |')
lines+=['','## Compatibility and unavailable cells','', 'The stock operator with the pinned core nightly rejects its generated cluster name. Kubernetes HTTP, scale and recovery for that pairing are not evaluated. Standalone nightly forwarding remains a separate, runnable treatment. The October 2 Praxis AI nightly is separately pinned from its successful scheduled build and retained SHA tag; there is no dated AI tag. The AI release is v0.5.0 and uses core libraries v0.7.2.','', 'See [Gateway API evidence](03-gateway-api.md), [feature comparison](04-feature-comparison.md) and [methodology](05-methodology-and-validity.md). These results do not establish TLS/HTTP2 performance, policy/security equivalence, a universal routing limit or production availability.']
lines+=['', 'Compare [sampled resource usage](08-resource-usage.md) beside achieved throughput. Native accounting work differs, and coarse resource samples do not establish exact CPU cycles per request.']
(out/'02-praxis-vs-agentgateway.md').write_text('\n'.join(lines).rstrip()+'\n')
print('Rendered four complete matrices and two comparison reports')
