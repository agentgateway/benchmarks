#!/usr/bin/env python3
"""Collect all-pass review facts from final snapshots; never approve results."""
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
analysis = root / '.work/analysis-final'
out = root / 'evidence/qualification/final-facts'
out.mkdir(parents=True, exist_ok=True)


def run(script, *args):
    subprocess.run([sys.executable, str(root / 'harness' / script),
                    *map(str, args)], check=True)


run('summarize-hosts.py', analysis, '--output', out / 'cpu-hosts.json')
run('summarize-hosts.py', analysis, '--suite', 'gateway',
    '--output', out / 'kubernetes-hosts.json')
run('summarize-hosts.py', analysis, '--suite', 'gateway', '--phases',
    '--output', out / 'kubernetes-phases.json')
for phase in ['pass1', 'pass2', 'pass3']:
    run('audit-cpu-isolation.py', analysis, '--phase', phase,
        '--output', out / (phase + '-cpu-isolation.json'))
    run('audit-kubernetes-startup.py', analysis / 'kclient', '--phase', phase,
        '--gateway-samples', analysis / 'kgateway/host-samples.jsonl',
        '--output', out / (phase + '-kubernetes-startup.json'))
    for profile in ['common', 'native', 'kubernetes']:
        cpu = profile != 'kubernetes'
        run('audit-load.py', analysis / ('client' if cpu else 'kclient'),
            '--phase', phase, '--profile', profile,
            '--output', out / (phase + '-' + profile + '-load.json'))
        args = ['--profile', profile] if cpu else []
        run('inspect-resource-gate.py',
            out / ('cpu-hosts.json' if cpu else 'kubernetes-hosts.json'),
            '--phase', phase, *args,
            '--output', out / (phase + '-' + profile + '-resources.json'))
run('summarize-load.py', analysis, '--output', root / 'reports/data')
run('summarize-control.py', analysis / 'kclient',
    '--output', root / 'reports/data')
run('review-kubernetes-attribution.py', analysis,
    '--output', out / 'kubernetes-attribution.json')
run('audit-recovery-overlap.py', analysis,
    '--output', out / 'recovery-overlap.json')
run('audit-input-continuity.py', root / '.work/exports',
    '--output', out / 'input-continuity.json')
run('verify-first-pass-retention.py', root / '.work/exports',
    '--output', out / 'first-pass-retention.json')
print('All-pass facts collected. Manual attribution and final review remain required.')
