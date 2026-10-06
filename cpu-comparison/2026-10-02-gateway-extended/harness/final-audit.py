#!/usr/bin/env python3
"""Check complete evidence after individual human reviews, then seal its inventory."""
import datetime
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
rows = {r['path']:r for r in json.loads((root/'reports/data/test-results.json').read_text())}
reviews = root/'evidence/validity'
result = []
for campaign in ['praxis-v0.5.2', 'praxis-nightly-20261002']:
    for repetition in range(1, 4):
        for product in ['agentgateway', 'praxis']:
            case = f'results/{campaign}/pass{repetition}/{product}'
            folder = root/case
            row = rows[case]
            review_file = reviews/(f'{campaign}-pass1.json' if repetition == 1 else f'{campaign}-pass{repetition}-{product}.json')
            review = json.loads(review_file.read_text())
            assert review['infrastructure_valid'] is True, str(review_file)
            assert (folder/'CLEANUP-COMPLETE').exists() and (folder/'JOB-FINISHED').exists(), case
            assert int((folder/'exit-code.txt').read_text()) in [0, 1], case + ': outer interruption'
            assert row['test_count'] == 107
            scored = sum(row['counts'].get(k, 0) for k in ['pass', 'fail'])
            blocked = row['counts'] == {'not-executed':107}
            assert scored == 107 or (campaign == 'praxis-nightly-20261002' and product == 'praxis' and blocked), case
            if scored == 107:
                assert row['report_present'], case + ': missing report'
            else:
                assert not row['report_present'], case + ': ambiguous partial report'
                assert "'routes' is empty" in (folder/'runtime.jsonl').read_text(), case + ': missing startup evidence'
            evidence = ['full.log', 'runtime.jsonl', 'start.txt', 'end.txt', 'exit-code.txt', 'command.txt']
            if row['report_present']:
                evidence.append('report.yaml')
            result.append({'case':case, 'counts':row['counts'],
                'classification':'complete selected-case evaluation' if scored == 107 else 'product pairing setup-blocked; individual coverage not evaluated',
                'review':str(review_file.relative_to(root)),
                'sha256':{name:hashlib.sha256((folder/name).read_bytes()).hexdigest() for name in evidence}})
host_review = json.loads((reviews/'host-runtime-decision.json').read_text())
assert host_review['infrastructure_valid'] is True
archive_review = json.loads((root/'evidence/archive-review.json').read_text())
assert archive_review['passed'] is True
report = {'reviewed_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
          'scope':'Two separate three-repetition comparisons, with an independent agentgateway reference run in each pair',
          'measured_attempts':len(result), 'runs':result,
          'host_review':'evidence/validity/host-runtime-decision.json',
          'exclusions':'evidence/exclusions.json',
          'limitations':['Evaluator-selected coverage, not official certification or third-party assessment.',
              'Case counts are not percentages of the whole specification or throughput measurements.',
              'Nightly setup-blocked attempts do not produce individual-feature scores.',
              'Host maintenance interrupted an excluded third release pair; package changes and its full replacement are documented.']}
(root/'reports/data/CAMPAIGN-VALIDATED.json').write_text(json.dumps(report,indent=2)+'\n')
print('Validated', len(result), 'measured attempts with case/runtime/archive reviews')
