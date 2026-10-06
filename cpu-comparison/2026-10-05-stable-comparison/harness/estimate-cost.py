#!/usr/bin/env python3
"""Estimate recorded VM lifetimes after verified deletion; never query billing."""
import datetime
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
cleanup = root/'evidence/cleanup'
assert (cleanup/'VERIFIED.json').exists(), 'Complete cleanup verification first'
deletion = json.loads((cleanup/'vm-delete.json').read_text())
assert deletion['exit'] == 0
end = datetime.datetime.fromisoformat(deletion['finished'])
rates = {'compute_per_vm_hour':0.388472, 'disk_per_gib_hour':0.000136986, 'ipv4_per_address_hour':0.005}
rows = []
for role in ['client','gateway','backend','kcontrol','kcontroller','kgateway','kbackend','kclient']:
    vm = json.loads((cleanup/(role+'-before-delete.json')).read_text())
    assert vm['machineType'].endswith('/n2-standard-8')
    hours = (end-datetime.datetime.fromisoformat(vm['creationTimestamp'])).total_seconds()/3600
    assert hours > 0
    rows.append({'name':vm['name'], 'id':vm['id'], 'created':vm['creationTimestamp'],
                 'deletion_completed_no_later_than':deletion['finished'], 'lifetime_hours':hours,
                 'compute_usd':hours*rates['compute_per_vm_hour'],
                 'disk_usd':hours*100*rates['disk_per_gib_hour'],
                 'external_ipv4_usd':hours*rates['ipv4_per_address_hour']})
totals = {k:sum(r[k] for r in rows) for k in ['compute_usd','disk_usd','external_ipv4_usd']}
totals['subtotal_before_transfer_usd'] = sum(totals.values())
result = {'method':'Conservative creation-to-batch-deletion-finish lifetime at public list prices; not metered billing',
          'currency':'USD', 'region':'us-central1', 'rates':rates,
          'source':'reports/cost-basis.md', 'instances':rows, 'totals':totals,
          'excluded':'Internet evidence-transfer charges; no invoice or billing export was queried'}
(root/'reports/data/cost-estimate.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(totals,indent=2))
