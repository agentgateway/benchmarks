#!/usr/bin/env python3
"""Plot all unlimited Fortio and streaming cases; each pass remains visible."""
import argparse,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('data',type=Path);p.add_argument('--output',type=Path,required=True);p.add_argument('--review',type=Path,required=True);a=p.parse_args()
r=json.loads(a.review.read_text());assert r['infrastructure_valid'] and r['all_three_passes_reviewed']
os.environ.setdefault('MPLCONFIGDIR',str(a.output.parent.parent/'.work/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
rows=json.loads((a.data/'load-summary.json').read_text());assert len(rows)==274 and all(x['three_complete_passes'] for x in rows)
a.output.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,'svg.fonttype':'none'})
colors={'direct':'#667085','agentgateway':'#1767a5','praxis-release':'#bd642f','praxis-nightly':'#8550a0','praxis':'#bd642f','praxis-ai-nightly':'#8550a0'}
labels={'direct':'Direct service','agentgateway':'Agentgateway v1.6.0','praxis-release':'Praxis core v0.5.2','praxis-nightly':'Praxis core nightly-20261002','praxis':'Praxis AI v0.5.0','praxis-ai-nightly':'Praxis AI Oct 2 nightly'}
for profile,workload,tool,metric,title in [
 ('common','http','fortio','successful_requests_per_second','Standalone HTTP forwarding'),
 ('common','ai','fortio','successful_requests_per_second','Standalone AI-protocol forwarding'),
 ('native','ai','fortio','successful_requests_per_second','Native AI profiles'),
 ('kubernetes','http','fortio','successful_requests_per_second','Kubernetes HTTP forwarding'),
 ('common','ai','aiperf','ttft_mean_ms','Forwarded synthetic streaming TTFT'),
 ('native','ai','aiperf','ttft_mean_ms','Native synthetic streaming TTFT')]:
 selected=[x for x in rows if x['profile']==profile and x['workload']==workload and x['tool']==tool and (tool!='fortio' or x['rate']==0)]
 ts=[t for t in labels if any(x['treatment']==t for x in selected)]
 def key(x):return(x.get('api') or '',x.get('size') or 0,x.get('concurrency') or 0)
 cases=sorted({key(x) for x in selected});lookup={(key(x),x['treatment']):x for x in selected}
 fig,ax=plt.subplots(figsize=(12,6));positions=np.arange(len(cases));width=.8/len(ts)
 for i,t in enumerate(ts):
  ms=[lookup[(c,t)]['metrics'][metric] for c in cases];xx=positions+(i-(len(ts)-1)/2)*width
  ax.bar(xx,[m['arithmetic_mean'] for m in ms],width=width*.93,label=labels[t],color=colors[t])
  for xpos,m in zip(xx,ms):ax.scatter(xpos+np.array([-.15,0,.15])*width,m['per_pass'],s=15,facecolors='white',edgecolors='#202020',linewidths=.6,zorder=4)
 case_labels=[]
 for api,size,concurrency in cases:
  case_labels.append((api+'\n' if api else '')+(str(size//1024)+' KiB\n' if tool=='fortio' else '')+str(concurrency)+(' streams' if tool=='aiperf' else ' conn.'))
 ax.set_xticks(positions,case_labels);ax.set_ylim(0,max(v for x in selected for v in x['metrics'][metric]['per_pass'])*1.18);ax.set_axisbelow(True);ax.grid(axis='y',alpha=.2)
 ax.set_ylabel('Successful HTTP 200 requests / second' if tool=='fortio' else 'Mean time to first token (ms)')
 ax.set_title(title,loc='left',weight='bold',pad=36)
 subtitle='Gateway: 2-vCPU quota, '+('256 MiB, private NodePort' if profile=='kubernetes' else '2 GiB, pinned guest cores')+'; service: 6-vCPU quota'
 subtitle+='; unlimited offered rate' if tool=='fortio' else '; 128 input / 64 output tokens; deterministic CPU service'
 ax.text(0,1.055,subtitle,transform=ax.transAxes,fontsize=9,color='#444')
 ax.legend(frameon=False,ncol=2,loc='upper right',fontsize=8)
 notes='Bars: arithmetic mean of three passes. Dots: each pass. Shared placement, rotated order. Solo.io evaluation.'
 caveat='Native profiles perform different routing/accounting work; translation direct baseline speaks OpenAI.' if profile=='native' else ('Core nightly/operator setup blocked: not evaluated here.' if profile=='kubernetes' else 'Common profile forwards protocol traffic without native AI transformation/accounting.')
 fig.text(.075,.05,notes,fontsize=8,color='#444');fig.text(.075,.02,caveat,fontsize=8,color='#444')
 fig.tight_layout(rect=(0,.09,1,.97));name=profile+'-'+workload+'-'+tool
 fig.savefig(a.output/(name+'.png'),dpi=170);fig.savefig(a.output/(name+'.svg'));plt.close(fig)
 svg=a.output/(name+'.svg');svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
(a.output/'plot-runtime.json').write_text(json.dumps({'matplotlib':matplotlib.__version__,'numpy':np.__version__,'note':'Plotting dependencies only; load generators are independently pinned.'},indent=2)+'\n')
print('Rendered six PNG/SVG figures')
