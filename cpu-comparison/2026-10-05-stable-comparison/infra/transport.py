"""SSH to captured instance addresses; avoids repeated Compute API lookups.

Host key verification remains enabled against gcloud's existing host-key file.
External addresses carry administration only; workload traffic uses private IPs.
"""
import getpass,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def destination(role):
 v=json.loads((ROOT/f'.work/create-{role}.json').read_text())[0]
 return str(v['id']),v['networkInterfaces'][0]['accessConfigs'][0]['natIP']
def options(role):
 ident,ip=destination(role)
 return ['-i',str(Path.home()/'.ssh/google_compute_engine'),'-o','CheckHostIP=no','-o','HostKeyAlias=compute.'+ident,'-o','IdentitiesOnly=yes','-o','StrictHostKeyChecking=yes','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/google_compute_known_hosts'),'-o','ConnectTimeout=20','-o','ServerAliveInterval=15','-o','ServerAliveCountMax=3'],getpass.getuser()+'@'+ip
def ssh(role,cmd,**kw):
 opts,dest=options(role)
 return subprocess.run(['/usr/bin/ssh',*opts,dest,cmd],**({'capture_output':True,'text':True,'timeout':90}|kw))
def copy(role,files,dest='/tmp/',**kw):
 opts,host=options(role)
 return subprocess.run(['/usr/bin/scp',*opts,*map(str,files),host+':'+dest],**({'capture_output':True,'text':True,'timeout':180,'check':True}|kw))
