#!/usr/bin/env python3
import json,pathlib,sys
root=pathlib.Path(sys.argv[1]); rows=[]
for d in sorted((root/'scale-observations').glob('*')):
 routes=json.loads((d/'routes.json').read_text())['items']; stats={'snapshot':d.name,'routes':len(routes),'accepted':0,'resolved':0,'current':0,'no_conditions':0,'reasons':{}}
 for r in routes:
  cond=[c for p in r.get('status',{}).get('parents',[]) for c in p.get('conditions',[])]
  for typ,key in [('Accepted','accepted'),('ResolvedRefs','resolved')]:
   stats[key]+=int(any(c['type']==typ and c['status']=='True' for c in cond))
  stats['current']+=int(bool(cond) and all(c.get('observedGeneration')==r['metadata'].get('generation') for c in cond))
  stats['no_conditions']+=int(not cond)
  for c in cond:
   if c['status']!='True':
    key=c['type']+':'+c.get('reason','');stats['reasons'][key]=stats['reasons'].get(key,0)+1
 rows.append(stats)
print(json.dumps(rows,indent=2))
