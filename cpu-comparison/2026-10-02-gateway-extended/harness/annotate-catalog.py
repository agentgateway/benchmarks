#!/usr/bin/env python3
"""Add pinned source links to catalog.go output without changing test selection."""
import argparse
import json
import re
from pathlib import Path

p=argparse.ArgumentParser();p.add_argument('gateway_api_source',type=Path);p.add_argument('catalog',type=Path);a=p.parse_args()
root=Path(__file__).resolve().parents[1]
revision=json.loads((root/'evidence/versions/selection.json').read_text())['gateway_api']['commit']
files={}
for file in (a.gateway_api_source/'conformance/tests').rglob('*.go'):
    for name in re.findall(r'ShortName:\s*"([^\"]+)"',file.read_text()):
        assert name not in files, 'Ambiguous test source: '+name
        files[name]=file.relative_to(a.gateway_api_source).as_posix()
catalog=json.loads(a.catalog.read_text())
for test in catalog['tests']:
    assert test['name'] in files, 'No source file for '+test['name']
    test['source_url']='https://github.com/kubernetes-sigs/gateway-api/blob/'+revision+'/'+files[test['name']]
a.catalog.write_text(json.dumps(catalog,indent=2)+'\n')
