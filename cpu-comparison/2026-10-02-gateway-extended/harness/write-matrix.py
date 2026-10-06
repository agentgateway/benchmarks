#!/usr/bin/env python3
"""Render grouped case-level evidence; missing or blocked tests never count as failures."""
import json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
rows=json.loads((root/'reports/data/test-results.json').read_text());catalog={x['name']:x for x in json.loads((root/'evidence/test-catalog.json').read_text())['tests']}
index={r['path']:{x['name']:x for x in r['records']} for r in rows}
products=[('praxis-v0.5.2','agentgateway'),('praxis-v0.5.2','praxis'),('praxis-nightly-20261002','agentgateway'),('praxis-nightly-20261002','praxis')]
labels=['Agentgateway v1.6.0 / release comparison','Praxis v0.5.2','Agentgateway v1.6.0 / nightly comparison','Praxis nightly-20261002']
groups={'http-core':'HTTP core','http-gateway-extended':'HTTP/Gateway extensions and backend TLS','grpc':'gRPC','tls':'TLS-dependent tests (including route-kind validation)'}
out=root/'reports/matrix';out.mkdir(exist_ok=True)
for group,title in groups.items():
 candidates=[]
 for name,t in catalog.items():
  if not t['selected']:continue
  fs=set(t['features']);cat='http-core' if fs<={'Gateway','HTTPRoute','ReferenceGrant'} else 'tls' if 'TLSRoute' in fs else 'grpc' if 'GRPCRoute' in fs else 'http-gateway-extended'
  if cat==group:candidates.append((name,t))
 lines=['# '+title+' — per-test evidence','', 'Each cell gives repetitions 1 / 2 / 3: **P** pass, **F** assertion failure, **S** skipped, **N/E** not executed, **pending** no result yet. N/E is not a feature failure. Source links identify the exact pinned upstream test.','', '| Test | Provisional | '+' | '.join(labels)+' |','| --- | --- | '+' | '.join(['---']*4)+' |']
 for name,t in sorted(candidates):
  cells=[]
  for camp,product in products:
   values=[]
   for rep in range(1,4):
    value=index.get(f'results/{camp}/pass{rep}/{product}',{}).get(name,{}).get('outcome','pending');values.append({'pass':'P','fail':'F','skip':'S','not-executed':'N/E'}.get(value,value))
   cells.append(' / '.join(values))
  label='['+name+']('+t.get('source_url','#')+')';lines.append('| '+label+' | '+('yes' if t['provisional'] else 'no')+' | '+' | '.join(cells)+' |')
 if group=='http-gateway-extended':
  lines+=['', 'GatewayStaticAddresses retains the original F outcomes under v1.5.1. This is a known upstream test-race limitation, not a demonstrated implementation defect; see the [CI investigation](../agentgateway-static-address-follow-up.md).']
 lines+=['','Two tests use experimental features: HTTPRouteInvalidParentRefNotMatchingListenerPort and TLSRouteMixedTerminationSameNamespace. All other selected cases use standard-channel feature labels.','']
 (out/(group+'.md')).write_text('\n'.join(lines))
print('Wrote four grouped test matrices')
