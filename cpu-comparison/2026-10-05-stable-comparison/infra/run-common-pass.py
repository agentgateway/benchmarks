#!/usr/bin/env python3
"""Dispatch one pass. Repetitions require a retained first-pass review."""
import argparse,subprocess,json,datetime,time,shlex
from pathlib import Path
from transport import ssh
p=argparse.ArgumentParser();p.add_argument('phase',choices=['qualification-nohealth','qualification-seeded','qualification','qualification-v2','qualification-v3','pass1','pass2','pass3']);p.add_argument('--resume',action='store_true');a=p.parse_args()
active=ssh('client',"systemctl list-units --state=running --no-legend 'common-*' 'native-*'")
assert active.returncode==0,active.stderr
for line in active.stdout.splitlines():
 assert a.resume and line.strip().startswith('common-seeded-'+a.phase+'-'),'Another CPU treatment is active: '+line
r=Path(__file__).resolve().parents[1];ips=json.loads((r/'.work/ips.json').read_text());out=r/'evidence/dispatch'/a.phase;out.mkdir(parents=True,exist_ok=a.resume)
if not a.phase.startswith('qualification'):
 gate=r/'evidence/qualification'/('qualification-review.json' if a.phase=='pass1' else 'pass1-review.json')
 review=json.loads(gate.read_text());assert review['infrastructure_valid'] is True
 assert review['aiperf_random_seed']==42
orders={'qualification':['direct','agentgateway','praxis-release','praxis-nightly'],'pass1':['direct','agentgateway','praxis-release','praxis-nightly'],'pass2':['agentgateway','praxis-release','praxis-nightly','direct'],'pass3':['praxis-release','praxis-nightly','direct','agentgateway']}
for treatment in orders['qualification' if a.phase.startswith('qualification') else a.phase]:
 unit='common-seeded-'+a.phase+'-'+treatment;remote='/opt/gateway-benchmark/results/common/'+a.phase+'/'+treatment
 if not (out/(treatment+'.json')).exists():
  cmd='sudo docker stop agentgateway praxis-release praxis-nightly agentgateway-native praxis-ai praxis-ai-nightly >/dev/null'
  if treatment!='direct':cmd+=' && sudo docker start '+treatment
  result=ssh('gateway',cmd)
  assert result.returncode==0,result.stderr
  command=['sudo','systemd-run','--unit='+unit,'--property=LimitNOFILE=65536','--property=RuntimeMaxSec=2400','/opt/gateway-benchmark/venv/bin/python','/opt/gateway-benchmark/run-common.py','--treatment',treatment,'--gateway',ips['gateway'],'--backend',ips['backend'],'--output',remote]
  if a.phase.startswith('qualification'):command.append('--qualification')
  result=ssh('client',shlex.join(command));(out/(treatment+'.json')).write_text(json.dumps({'command':command,'stdout':result.stdout,'stderr':result.stderr,'exit':result.returncode,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
  assert result.returncode==0,result.stderr
 while True:
  time.sleep(15);result=ssh('client',f'systemctl show {unit} -p ActiveState -p Result; test -f {remote}/COMPLETE && echo COMPLETE; true')
  if result.returncode:raise SystemExit('Progress query failed: inspect existing remote job before retrying')
  if 'COMPLETE' in result.stdout:break
  if 'ActiveState=failed' in result.stdout or 'ActiveState=inactive' in result.stdout:raise SystemExit(result.stdout+' '+remote)
 print(a.phase,treatment,'complete',flush=True)
(out/'COMPLETE').write_text(datetime.datetime.now(datetime.timezone.utc).isoformat())
