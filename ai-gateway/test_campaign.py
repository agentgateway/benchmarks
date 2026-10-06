import argparse
from collections import Counter
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import campaign


class CampaignTest(unittest.TestCase):
    def test_counterbalanced_repetitions(self):
        args=argparse.Namespace(seed=20261001,cases=['openai','translation'],sizes=[1024],qps=[1000,0],repetitions=6)
        rows=campaign.schedule(args)
        for case in args.cases:
            for qps in args.qps:
                counts=Counter((r['gateway'],r['position']) for r in rows if r['case']==case and r['qps']==qps)
                self.assertEqual(len(counts),9)
                self.assertEqual(set(counts.values()),{2})

    def test_initial_plan_has_one_full_round(self):
        raw=subprocess.check_output(['python3',str(Path(campaign.__file__)), '--initial','--dry-run'],text=True)
        plan=json.loads(raw)
        self.assertEqual(plan['mode'],'preliminary-performance')
        self.assertEqual(len(plan['trials']),54)
        self.assertEqual({r['repeat'] for r in plan['trials']},{1})
        self.assertEqual(Counter(r['gateway'] for r in plan['trials']),{'direct':18,'agentgateway':18,'praxis':18})

    def test_cpu_ranges(self):
        self.assertEqual(campaign.cpu_set('2-3,5'),{2,3,5})
        for value in ('3-2','a','-1','2,,3'):
            with self.assertRaises(ValueError): campaign.cpu_set(value)

    def test_translation_baseline_uses_upstream_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            command=campaign.fortio_command({'gateway':'direct','case':'translation','size':1024,'qps':1000},Path(tmp),30,32)
            self.assertEqual(command[-1],'http://mock:8081/v1/chat/completions')
            self.assertEqual(json.loads((Path(tmp)/'request.json').read_text())['model'],'bench-openai')
            self.assertIn('-nocatchup',command)
            self.assertIn('--user',command)

    def test_client_timeout_removes_container_and_retains_phase(self):
        class Process:
            def __init__(self, client=False): self.client=client;self.killed=False
            def wait(self,timeout):
                if self.client and not self.killed: raise subprocess.TimeoutExpired('fortio',timeout)
                return 0
            def poll(self): return None if self.client and not self.killed else 0
            def kill(self): self.killed=True
            def terminate(self): self.killed=True
        client,stats=Process(True),Process()
        with tempfile.TemporaryDirectory() as tmp, patch.object(campaign.subprocess,'Popen',side_effect=[client,stats]), patch.object(campaign.subprocess,'run') as cleanup:
            cleanup.return_value.returncode=0
            with self.assertRaises(subprocess.TimeoutExpired):
                campaign.run_phase({'gateway':'direct','case':'openai','size':1024,'qps':10},Path(tmp),2,4,False)
            self.assertEqual(cleanup.call_args.args[0][:3],['docker','rm','-f'])
            self.assertTrue(client.killed)
            self.assertTrue(stats.killed)
            self.assertIn('elapsed_seconds',json.loads((Path(tmp)/'fortio-phase.json').read_text()))

if __name__=='__main__': unittest.main()
