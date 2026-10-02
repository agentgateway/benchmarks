import json
from pathlib import Path
import tempfile
import unittest

from report import render


class ReportTest(unittest.TestCase):
    def fixture(self,path):
        rows=[]
        for qps in (0,1000):
            for i,gateway in enumerate(('direct','agentgateway','praxis')):
                rows.append(dict(case='openai',size=1024,qps=qps,gateway=gateway,
                                 successful_qps=1000/(i+1),p99_ms=1+i,errors=i))
        manifest={'mode':'preliminary-performance','started_utc':'2026-10-02T00:00:00Z',
                  'host':{'docker_arch':'amd64','docker_cpus':16,'docker_memory':64*2**30,'platform':'test-linux'},
                  'trials':[{} for _ in rows], 'parameters':{'repetitions':1,'connections':32,'warmup':5,'duration':30}}
        for name,value in [('manifest.json',manifest),('campaign-status.json',{'status':'complete'}),('summary.json',rows)]:
            (path/name).write_text(json.dumps(value))
        (path/'qualification.jsonl').write_text(json.dumps({'passed':True})+'\n')
        return manifest,rows

    def test_both_reports_preserve_errors_and_ratio_direction(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);self.fixture(path)
            render(path,path/'reports','raw/')
            text=(path/'reports/praxis-vs-agentgateway.md').read_text()
            self.assertIn('0.667×',text)
            self.assertIn('1/2',text)
            self.assertTrue((path/'reports/agentgateway-vs-direct.md').exists())

    def test_smoke_and_incomplete_treatment_sets_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp);manifest,rows=self.fixture(path)
            manifest['mode']='qualification-only'
            (path/'manifest.json').write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError,'smoke timings'):
                render(path,path/'reports','raw/')
            manifest['mode']='preliminary-performance'
            rows=rows[:-1];manifest['trials']=manifest['trials'][:-1]
            (path/'manifest.json').write_text(json.dumps(manifest))
            (path/'summary.json').write_text(json.dumps(rows))
            with self.assertRaisesRegex(ValueError,'Missing'):
                render(path,path/'reports','raw/')


if __name__=='__main__':unittest.main()
