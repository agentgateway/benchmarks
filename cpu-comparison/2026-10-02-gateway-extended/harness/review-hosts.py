#!/usr/bin/env python3
"""Summarize host samples within measured run windows; preserve raw evidence.

This is an infrastructure diagnostic, not an independent throughput benchmark.
Container deletion can cause benign collection races; a human reviews errors.
"""
import argparse
import datetime
import json
import tarfile
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--root', type=Path, default=Path('.'))
a = p.parse_args()
root = a.root
utc = lambda s: datetime.datetime.fromisoformat(s.strip().replace('Z', '+00:00'))
windows = []
for start in sorted((root/'results').glob('*/pass[123]/*/start.txt')):
    end = start.parent/'end.txt'
    if end.exists():
        windows.append((str(start.parent.relative_to(root)), utc(start.read_text()), utc(end.read_text())))
summary = {}
for archive_path in sorted((root/'evidence/hosts').glob('*.tar.gz')):
    per_case = {name: {'samples': 0, 'first_sample': None, 'last_sample': None, 'maximum_gap_seconds': 0, 'minimum_mem_available_kib': None,
        'maximum_system_allocated_fds': 0, 'system_fd_limit': None, 'maximum_observed_container_fds': 0,
        'containers_with_oom_kill_counter': {}, 'collector_errors': [], 'container_read_errors': 0}
        for name, _, _ in windows}
    last = {}
    malformed = 0
    with tarfile.open(archive_path) as archive:
        member = next(m for m in archive if m.name.removeprefix('./') == 'host-samples.jsonl')
        for line in archive.extractfile(member):
            try:
                row = json.loads(line)
                timestamp = utc(row['utc'])
            except (json.JSONDecodeError, KeyError, ValueError):
                malformed += 1
                continue
            for name, start, end in windows:
                if not start <= timestamp <= end:
                    continue
                data = per_case[name]
                data['samples'] += 1
                if data['first_sample'] is None:
                    data['first_sample'] = row['utc']
                data['last_sample'] = row['utc']
                if name in last:
                    data['maximum_gap_seconds'] = max(data['maximum_gap_seconds'], (timestamp-last[name]).total_seconds())
                last[name] = timestamp
                mem = row.get('meminfo', '')
                if isinstance(mem, str):
                    available = next((int(s.split()[1]) for s in mem.splitlines() if s.startswith('MemAvailable:')), None)
                    if available is not None:
                        data['minimum_mem_available_kib'] = available if data['minimum_mem_available_kib'] is None else min(data['minimum_mem_available_kib'], available)
                fds = row.get('sys/fs/file-nr', '')
                if isinstance(fds, str) and len(fds.split()) == 3:
                    allocated, _, limit = map(int, fds.split())
                    data['maximum_system_allocated_fds'] = max(data['maximum_system_allocated_fds'], allocated)
                    data['system_fd_limit'] = limit
                if 'collector_error' in row:
                    data['collector_errors'].append({'utc': row['utc'], 'error': row['collector_error']})
                for container in row.get('containers', []):
                    data['maximum_observed_container_fds'] = max(data['maximum_observed_container_fds'], container.get('fd_count', 0))
                    if 'error' in container or 'cgroup_error' in container:
                        data['container_read_errors'] += 1
                    events = dict(s.split() for s in container.get('memory.events', '').splitlines())
                    kills = int(events.get('oom_kill', 0))
                    if kills:
                        key = container['name'] + '/pid=' + str(container['pid'])
                        data['containers_with_oom_kill_counter'][key] = max(data['containers_with_oom_kill_counter'].get(key, 0), kills)
    summary[archive_path.stem.removesuffix('.tar')] = {'malformed_rows_in_archive': malformed, 'measured_windows': per_case}
output = root/'evidence/validity/host-runtime-review.json'
output.write_text(json.dumps(summary, indent=2)+'\n')
print(output)
