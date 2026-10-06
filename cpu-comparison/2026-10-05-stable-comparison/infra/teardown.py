#!/usr/bin/env python3
"""Delete only the eight captured campaign VMs after verified local evidence retention."""
import datetime,json,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'evidence/cleanup';out.mkdir(parents=True,exist_ok=True)
assert (root/'evidence/EXPORTED.json').exists(),'Verify a retained local evidence archive before deletion'
roles=['client','gateway','backend','kcontrol','kcontroller','kgateway','kbackend','kclient'];names=[]
for role in roles:
 name='gwcmp160-1005-'+role
 expected=json.loads((root/f'.work/create-{role}.json').read_text())[0]
 r=subprocess.run(['gcloud','compute','instances','describe',name,'--project=solo-oss','--zone=us-central1-a','--format=json'],capture_output=True,text=True,check=True)
 actual=json.loads(r.stdout)
 assert str(actual['id'])==str(expected['id']),name+' identity changed'
 assert actual['labels']['campaign']=='gwcmp160-1005',name+' ownership mismatch'
 assert len(actual['disks'])==1 and actual['disks'][0]['boot'] and actual['disks'][0]['autoDelete'],name+' unexpected disks'
 # Save only cleanup-relevant metadata, avoiding SSH metadata or credentials.
 (out/f'{role}-before-delete.json').write_text(json.dumps({k:actual.get(k) for k in ['name','id','creationTimestamp','machineType','zone','labels','disks','scheduling','status']},indent=2)+'\n')
 names.append(name)
start=datetime.datetime.now(datetime.timezone.utc).isoformat()
cmd=['gcloud','compute','instances','delete',*names,'--project=solo-oss','--zone=us-central1-a','--delete-disks=all','--quiet']
r=subprocess.run(cmd,capture_output=True,text=True)
(out/'vm-delete.json').write_text(json.dumps({'started':start,'finished':datetime.datetime.now(datetime.timezone.utc).isoformat(),'command':cmd,'exit':r.returncode,'stdout':r.stdout,'stderr':r.stderr},indent=2)+'\n')
if r.returncode:raise SystemExit('Inspect partial deletion; do not blindly recreate or overwrite resources')
# Inventory every resource identity, but omit unrelated VM metadata and startup scripts.
commands={
 'instances':['compute','instances','list'],
 'disks':['compute','disks','list'],
 'addresses':['compute','addresses','list'],
 'forwarding-rules':['compute','forwarding-rules','list'],
 'backend-services':['compute','backend-services','list'],
 'target-pools':['compute','target-pools','list'],
 'health-checks':['compute','health-checks','list'],
 'firewalls':['compute','firewall-rules','list'],
 'clusters':['container','clusters','list'],
 'registries':['artifacts','repositories','list','--location=us-central1'],
 'service-accounts':['iam','service-accounts','list'],
}
for kind,args in commands.items():
 r=subprocess.run(['gcloud',*args,'--project=solo-oss','--format=json'],capture_output=True,text=True)
 if r.returncode:
  (out/f'final-{kind}.json').write_text(json.dumps({'inventory_error':r.stderr,'exit':r.returncode}))
  raise SystemExit('Inventory failed: '+kind)
 inventory=json.loads(r.stdout)
 fields=['name','id','creationTimestamp','createTime','zone','region','location','status','labels','sizeGb','type','users','addressType','email','disabled','format']
 (out/f'final-{kind}.json').write_text(json.dumps([{key:value for key,value in v.items() if key in fields} for v in inventory],indent=2)+'\n')
 remaining=[v for v in inventory if v.get('name','').split('/')[-1].startswith(('gwcmp160-1005-',)) or v.get('labels',{}).get('campaign') in ['gwcmp160-1005']]
 assert not remaining,kind+' has remaining campaign resources: '+str([v['name'] for v in remaining])
for file in [root/'.work/k3s-token',root/'.work/client.kubeconfig']:
 file.unlink(missing_ok=True)
(out/'VERIFIED.json').write_text(json.dumps({'verified_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'deleted_instances':names,'remaining_campaign_resources':[],'temporary_local_cluster_credentials_removed':True,'preserved':'Unrelated project resources and pre-existing agentgateway-benchmark-nodes identity'},indent=2)+'\n')
print('Campaign VM/disks deleted; inventory verified; local cluster credentials removed')
