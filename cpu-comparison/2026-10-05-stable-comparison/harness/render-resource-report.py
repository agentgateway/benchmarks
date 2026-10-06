#!/usr/bin/env python3
"""Render sampled gateway resources without claiming per-request CPU cost."""
import argparse
import json
import statistics
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('data', type=Path)
p.add_argument('--cpu-hosts', type=Path, required=True)
p.add_argument('--kubernetes-hosts', type=Path, required=True)
p.add_argument('--output', type=Path, required=True)
p.add_argument('--review', type=Path, required=True)
a = p.parse_args()
review = json.loads(a.review.read_text())
assert review['infrastructure_valid'] and review['all_three_passes_reviewed']
loads = json.loads((a.data / 'load-rows.json').read_text())
assert len(loads) == 822
hosts = json.loads(a.cpu_hosts.read_text()) + json.loads(a.kubernetes_hosts.read_text())
lookup = {(r['role'], r['workload']): r for r in hosts}
labels = {'agentgateway': 'Agentgateway v1.6.0',
          'praxis-release': 'Praxis core v0.5.2',
          'praxis-nightly': 'Praxis core nightly-20261002',
          'praxis': 'Praxis AI v0.5.0',
          'praxis-ai-nightly': 'Praxis AI Oct 2 nightly'}
groups = {}
rows = []
for load in loads:
    if load['treatment'] == 'direct':
        continue
    role = 'kgateway' if load['profile'] == 'kubernetes' else 'gateway'
    artifact = load['artifact'].split('/', 1)[1]
    host = lookup[(role, artifact)]
    assert host['samples'] >= 5 and host['container_quota_busy_percent']
    assert host['max_container_memory_bytes'] is not None
    row = {k: load.get(k) for k in ['profile', 'workload', 'tool', 'api', 'size',
                                  'rate', 'concurrency', 'connections',
                                  'treatment', 'pass', 'artifact']}
    row.update({'samples': host['samples'],
                'mean_cpu_percent_of_two_cpu_quota': host['container_quota_busy_percent']['mean'],
                'maximum_sampled_cgroup_memory_mib': host['max_container_memory_bytes'] / 1024**2,
                'maximum_sampled_fds': host['max_fd']})
    rows.append(row)
    key = tuple(row[k] for k in ['profile', 'workload', 'tool', 'api', 'size',
                                'rate', 'concurrency', 'connections', 'treatment'])
    groups.setdefault(key, []).append(row)
assert len(rows) == 606 and len(groups) == 202
summaries = []
for key, rs in groups.items():
    rs.sort(key=lambda r: r['pass'])
    assert [r['pass'] for r in rs] == [1, 2, 3]
    record = {k: rs[0][k] for k in ['profile', 'workload', 'tool', 'api', 'size',
                                  'rate', 'concurrency', 'connections', 'treatment']}
    record['metrics'] = {}
    for metric in ['mean_cpu_percent_of_two_cpu_quota',
                   'maximum_sampled_cgroup_memory_mib', 'maximum_sampled_fds']:
        values = [r[metric] for r in rs]
        record['metrics'][metric] = {'per_pass': values,
                                    'arithmetic_mean': statistics.mean(values),
                                    'min': min(values), 'max': max(values)}
    summaries.append(record)
(a.data / 'resource-rows.json').write_text(json.dumps(rows, indent=2) + '\n')
(a.data / 'resource-summary.json').write_text(json.dumps(summaries, indent=2) + '\n')
matrices = a.output / 'matrices'
matrices.mkdir(parents=True, exist_ok=True)


def metric(row, key):
    m = row['metrics'][key]
    return f"{m['arithmetic_mean']:.2f} [{m['min']:.2f}–{m['max']:.2f}]"


def case(row):
    if row['tool'] == 'aiperf':
        return f"{row['api']}, {row['concurrency']} streams"
    rate = 'unlimited' if row['rate'] == 0 else f"{row['rate']} RPS"
    count = row['connections'] if row['tool'] == 'nighthawk' else row['concurrency']
    return f"{row['api'] + ' / ' if row['api'] else ''}{row['size']} B, {count} connections, {rate}"


links = []
for profile, workload in [('common', 'http'), ('common', 'ai'), ('native', 'ai'),
                          ('kubernetes', 'http')]:
    filename = f'{profile}-{workload}-resources.md'
    links.append(f'[{profile} {workload}](matrices/{filename})')
    lines = [f'# Sampled resources: {profile} {workload}', '',
             'Cells show the arithmetic mean of three per-run values followed by '
             '[minimum–maximum]. CPU is the mean over each sampled tool-execution '
             'window; memory is each window’s maximum sampled cgroup charge. '
             'These include client startup/warmup and are not exact measurement-only '
             'CPU cycles or RSS. See [resource interpretation](../08-resource-usage.md).', '',
             '| Tool / case | Treatment | CPU, % of two-CPU quota | Maximum sampled memory, MiB | Maximum sampled descriptors |',
             '| --- | --- | ---: | ---: | ---: |']
    selected = [r for r in summaries if r['profile'] == profile and r['workload'] == workload]
    selected.sort(key=lambda r: (r['tool'], r['api'] or '', r['size'] or 0,
                                 r['concurrency'] or r['connections'] or 0,
                                 r['rate'] or 0, list(labels).index(r['treatment'])))
    for row in selected:
        lines.append('| ' + ' | '.join([row['tool'] + ': ' + case(row), labels[row['treatment']],
                     metric(row, 'mean_cpu_percent_of_two_cpu_quota'),
                     metric(row, 'maximum_sampled_cgroup_memory_mib'),
                     metric(row, 'maximum_sampled_fds')]) + ' |')
    (matrices / filename).write_text('\n'.join(lines) + '\n')
text = '''# Sampled resource usage

Both gateways receive a two-CPU quota in each deployment profile. The standalone
profile also pins two guest cores and permits 2 GiB; Kubernetes permits 256 MiB
without CPU pinning. Compare within a profile and workload. The direct baseline
has no gateway process; gateway-specific resource metrics do not apply to it.

The matrices retain every gateway case and every repetition. They complement
successful throughput and latency; they are not an overall efficiency ranking.
At fixed offered rates, check that both products actually deliver the same rate.
At saturation, higher utilization can simply mean the gateway does more work.

MATRICES

CPU uses cgroup usage deltas divided by the two-CPU quota: 100% means approximately
two CPUs are busy, not the whole eight-vCPU VM. Five-second samples cover the
tool-execution window, including startup and warmup. They do not establish exact
cycles per request or a production cost per request.

Memory is the maximum sampled `memory.current` cgroup charge in each window,
then summarized across three runs. It includes charged memory beyond process RSS,
can miss short peaks, and is not the container lifetime `memory.peak`. Gateway
processes serve multiple cases, so allocator retention and treatment order can
affect later samples. Different memory caps prevent treating standalone versus
Kubernetes differences as a controlled experiment in Kubernetes overhead.

Descriptor maxima are observations, not configured limits. Validity review checks
those limits, process identity, restarts, OOM counters, client/backend capacity,
CPU steal and network error/drop increments separately. Direct unlimited-rate
traffic approaches client or backend capacity in some cases; the baseline remains
the observed full path, not an unconstrained service ceiling.

[Individual resource rows](data/resource-rows.json) map to the same raw execution
artifacts as [load rows](data/load-rows.json); [resource summaries](data/resource-summary.json)
retain all three values. Read [methodology](05-methodology-and-validity.md) before
turning a sampled resource difference into a competitive claim.
'''
(a.output / '08-resource-usage.md').write_text(text.replace('MATRICES', ', '.join(links) + '.'))
print('Rendered 202 resource groups from 606 gateway load windows')
