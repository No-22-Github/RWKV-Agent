#!/usr/bin/env python3
"""Summarize an explicit, complete set of comparable repeated runs, offline.

Never mutates the append-only ledger and never launches model requests.
pass_all_k / pass_any_k are empirical per-case all/any outcomes, not pass@k
estimators or uncertainty bounds. Refuses mismatched or incomplete replicas.
"""
import argparse
import hashlib
import json
from pathlib import Path

from wire_metrics import infrastructure_failure


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)


def summarize(runs, k=3):
    if k < 2 or len(runs) != k:
        raise ValueError(f'exactly {k} distinct runs are required, received {len(runs)}')
    records, signatures, run_ids = [], [], set()
    for run in map(Path, runs):
        m = json.loads((run / 'run.json').read_text())
        s = json.loads((run / 'summary.json').read_text())
        meta = json.loads((run / 'experiment.json').read_text())
        if not m.get('run_id') or m['run_id'] in run_ids or s.get('run_id') != m['run_id']:
            raise ValueError('missing, duplicated, or inconsistent run_id: ' + str(run))
        run_ids.add(m['run_id'])
        if meta.get('infrastructure_errors'):
            raise ValueError('infrastructure errors: ' + str(run))
        if not meta.get('binary_sha256'):
            raise ValueError('binary provenance is required: ' + str(run))
        specs = m['cases']
        ids = {c['id'] for c in specs}
        if len(ids) != len(specs) or len(s['cases']) != len(ids) or {c['id'] for c in s['cases']} != ids:
            raise ValueError('missing or duplicate case rows: ' + str(run))
        spec_by_id = {c['id']: c for c in specs}
        for c in s['cases']:
            if type(c.get('passed')) is not bool or len(c.get('turns', [])) != len(spec_by_id[c['id']]['turns']):
                raise ValueError('missing score or incomplete turns: ' + c['id'])
            failures = list(c.get('failures') or []) + [c.get('error', '')]
            for t in c['turns']:
                failures += list(t.get('failures') or []) + [t.get('runner_error', '')]
            if any(infrastructure_failure(f) for f in failures if f):
                raise ValueError('infrastructure failure in ' + c['id'])
        signatures.append(canonical({'model': m['model'], 'sampling': m['sampling'],
                                     'harness': m['harness'], 'cases': sorted(specs, key=lambda c:c['id']),
                                     'binary_sha256': meta['binary_sha256'], 'state_id': meta.get('state_id', '')}))
        records.append({'path': str(run), 'run_id': m['run_id'],
                        'summary_sha256': hashlib.sha256((run/'summary.json').read_bytes()).hexdigest(),
                        'scores': {c['id']: c['passed'] for c in s['cases']}})
    if len(set(signatures)) != 1:
        raise ValueError('replicas differ in frozen cases, scorer/harness, model, state, sampling, or binary; do not pool them')
    cases = []
    for cid in sorted(records[0]['scores']):
        outcomes = [r['scores'][cid] for r in records]
        cases.append({'id': cid, 'outcomes': outcomes, 'passed_replicas': sum(outcomes),
                      'pass_all_k': all(outcomes), 'pass_any_k': any(outcomes)})
    n = len(cases)
    if not n:
        raise ValueError('no cases')
    all_count = sum(c['pass_all_k'] for c in cases)
    any_count = sum(c['pass_any_k'] for c in cases)
    return {'k': k, 'cases_per_replica': n, 'pass_mean': sum(c['passed_replicas'] for c in cases)/(n*k),
            'pass_all_k': {'passed': all_count, 'total': n, 'rate': all_count/n},
            'pass_any_k': {'passed': any_count, 'total': n, 'rate': any_count/n},
            'unstable_cases': [c['id'] for c in cases if 0 < c['passed_replicas'] < k],
            'definition': 'Observed all/any across this explicit replica group. No confidence interval or pass@k estimator.',
            'comparability_sha256': hashlib.sha256(signatures[0].encode()).hexdigest(),
            'runs': [{key:value for key,value in r.items() if key != 'scores'} for r in records], 'cases': cases}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('runs', nargs='+', type=Path)
    p.add_argument('--k', type=int, default=3)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    result = summarize(a.runs, a.k)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('runs','cases')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
