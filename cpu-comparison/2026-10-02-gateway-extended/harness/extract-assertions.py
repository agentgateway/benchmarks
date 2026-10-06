#!/usr/bin/env python3
"""Index the first assertion excerpt for each failed case; do not infer root cause."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = json.loads((root/'reports/data/test-results.json').read_text())
result = []
for row in rows:
    if not re.search(r'/pass[123]/', row['path']):
        continue
    failures = {r['name'] for r in row['records'] if r['outcome'] == 'fail'}
    if not failures:
        continue
    lines = (root/row['path']/'full.log').read_text(errors='replace').splitlines()
    current = None
    found = set()
    for index, line in enumerate(lines):
        match = re.match(r'^=== RUN   TestConformance/([^/\s]+)', line)
        if match:
            current = match.group(1)
        if current not in failures or current in found or not re.search(r'\bError:\s', line):
            continue
        start = max(0, index-3)
        end = index+1
        while end < min(len(lines), index+15):
            if lines[end].startswith('=== RUN') or lines[end].startswith('    ---'):
                break
            end += 1
        result.append({'run':row['path'], 'test':current,
            'source_file':row['path']+'/full.log', 'start_line':start+1,
            'excerpt':'\n'.join(lines[start:end]),
            'interpretation':'First logged assertion only; additional failures and runtime context remain in the full evidence archive.'})
        found.add(current)
    # Some upstream helpers call t.Fatalf directly without testify's Error label.
    # Preserve their terminal output, without labeling a transient retry as root cause.
    starts = [(i, m.group(1)) for i,line in enumerate(lines)
              if (m := re.match(r'^=== RUN   TestConformance/([^/\s]+)$', line))]
    for n,(start,name) in enumerate(starts):
        if name not in failures-found:
            continue
        end = starts[n+1][0] if n+1 < len(starts) else len(lines)
        first = max(start, end-6)
        result.append({'run':row['path'], 'test':name,
            'source_file':row['path']+'/full.log', 'start_line':first+1,
            'excerpt':'\n'.join(lines[first:end]),
            'interpretation':'Terminal output for a failed case whose helper does not use a testify Error label; consult full output and runtime evidence for root cause.'})
        found.add(name)
    missing = failures-found
    assert not missing, row['path'] + ': missing excerpt for ' + str(missing)
(root/'reports/data/failure-excerpts.json').write_text(json.dumps(result,indent=2)+'\n')
print('Indexed',len(result),'failed case/run assertion excerpts')
