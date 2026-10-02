#!/usr/bin/env python3
"""Plot every measured workload of the initial CPU campaign; no best-run selection."""
import argparse
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--campaign',required=True,type=Path)
p.add_argument('--output',required=True,type=Path)
a=p.parse_args()
manifest=json.loads((a.campaign/'manifest.json').read_text())
status=json.loads((a.campaign/'campaign-status.json').read_text())
if status['status']!='complete' or manifest['mode']!='preliminary-performance':
    raise SystemExit('Only complete preliminary performance campaigns are accepted')
rows=json.loads((a.campaign/'summary.json').read_text())
if len(rows)!=len(manifest['trials']) or manifest['parameters']['repetitions']!=1:
    raise SystemExit('Expected all trials from exactly one preliminary round')
cases=manifest['parameters']['cases'];sizes=manifest['parameters']['sizes']
gateways=['direct','agentgateway','praxis']
labels={'direct':'Direct backend','agentgateway':'agentgateway 1.5.0','praxis':'Praxis AI 0.5.0'}
colors={'direct':'#84939f','agentgateway':'#126fbb','praxis':'#d47924'}
index={(r['case'],r['size'],r['qps'],r['gateway']):r for r in rows}
a.output.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,len(cases),figsize=(12,5.5),squeeze=False,sharey=True)
for col,case in enumerate(cases):
    ax=axes[0,col]
    for i,gateway in enumerate(gateways):
        values=[index[case,size,0,gateway]['successful_qps'] for size in sizes]
        ax.bar([x+(i-1)*.25 for x in range(len(sizes))],values,width=.23,color=colors[gateway],label=labels[gateway])
    ax.set_title(case.title());ax.set_xticks(range(len(sizes)),[f'{s//1024} KiB' for s in sizes])
    ax.yaxis.set_major_formatter(EngFormatter(unit=''))
    ax.grid(axis='y',alpha=.2);ax.set_axisbelow(True)
    if col==0:ax.set_ylabel('Successful requests / second')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.91),ncol=3,frameon=False)
fig.suptitle('AI proxy saturation throughput — initial CPU-only run',y=.99,fontsize=16)
fig.text(.5,.015,'One 30-second run/configuration; 32 connections; 2 CPU / 2 GiB per treatment. No confidence intervals.\nSize labels denote input and output content bytes each; JSON framing adds bytes.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.08,1,.85));fig.savefig(a.output/'saturation-throughput.png',dpi=160);plt.close(fig)
qps=sorted(q for q in manifest['parameters']['qps'] if q>0)
fig,axes=plt.subplots(len(sizes),len(cases),figsize=(12,7),squeeze=False,sharey=True)
for row,size in enumerate(sizes):
    for col,case in enumerate(cases):
        ax=axes[row,col]
        for gateway in gateways:
            vals=[index[case,size,q,gateway]['p99_ms'] for q in qps]
            ax.plot(qps,vals,marker='o',color=colors[gateway],label=labels[gateway])
            for q,val in zip(qps,vals):
                if not index[case,size,q,gateway]['target_met']:
                    ax.scatter([q],[val],marker='X',s=90,color=colors[gateway],zorder=3)
        ax.set_title(f'{case.title()} · {size//1024} KiB');ax.set_xticks(qps)
        ax.grid(alpha=.2);ax.set_yscale('log')
        if col==0:ax.set_ylabel('Completion p99 (ms, log scale)')
        if row==len(sizes)-1:ax.set_xlabel('Offered requests / second')
fig.legend(*axes[0,0].get_legend_handles_labels(),loc='upper center',bbox_to_anchor=(.5,.94),ncol=3,frameon=False)
fig.suptitle('Completion latency at fixed offered rates — initial run',y=.99,fontsize=16)
fig.text(.5,.015,'One observation per point; fixed concurrency. X marks a missed offered-rate/error gate. See achieved QPS and errors.',ha='center',fontsize=9)
fig.tight_layout(rect=(0,.045,1,.90));fig.savefig(a.output/'fixed-rate-p99.png',dpi=160);plt.close(fig)
