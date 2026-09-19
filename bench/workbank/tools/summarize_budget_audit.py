#!/usr/bin/env python3
"""Offline execution/termination/token audit; never changes official scoring.

Usage: summarize_budget_audit.py ROOT --out REPORT.json
ROOT holds paired-none-steps{10,30} and token-audit.jsonl (from tokenaudit).
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import statistics
from scorer_ablation import analyze, answer


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trajectory_comparison(left, right):
    """Compare model output/actions, excluding wall-clock and workspace metadata."""
    snapshots = []
    for run in [left, right]:
        summary = json.loads((run / 'summary.json').read_text())
        snapshots.append({c['id']: [s for t in c['turns'] for s in t['result'].get('steps', [])] for c in summary['cases']})
    rows = []
    for cid, a in snapshots[0].items():
        b = snapshots[1][cid]
        first = None
        for i, (x, y) in enumerate(zip(a, b)):
            keys = ['model_output', 'action_type', 'tool', 'tool_arguments', 'tool_executed']
            if any(x.get(k) != y.get(k) for k in keys):
                first = {'step': i + 1, 'stored_prompt_equal': x.get('request', {}).get('prompt') == y.get('request', {}).get('prompt')}
                break
        if first or len(a) != len(b):
            rows.append({'id': cid, 'steps': [len(a), len(b)], 'first_difference': first})
    return rows


def summarize(run, tokens, tool_only=True):
    summary = json.loads((run / 'summary.json').read_text())
    manifest = json.loads((run / 'run.json').read_text())
    frozen = {c['id']: c for c in manifest['cases']}
    rescored = analyze(run)
    relaxed = {c['id']: c['arms']['answer_relaxed']['passed'] for c in rescored['details']}
    rows = []
    for c in summary['cases']:
        if tool_only and c['id'].startswith('nt-'):
            continue
        results = [t['result'] for t in c['turns']]
        steps = [s for r in results for s in r.get('steps', [])]
        ts = [s for s in tokens.get(str(run), {}).get('steps', []) if s['case'] == c['id']]
        counts = [s['request_tokens'] for s in ts if s.get('request_complete')]
        complete = len(counts) == len(steps) and bool(steps)
        observed = any(bool(answer(r).strip()) for r in results)
        rows.append({
            'id': c['id'], 'official_passed': c['passed'], 'relaxed_passed': relaxed[c['id']],
            'steps': len(steps), 'reference_calls': frozen[c['id']].get('tags', {}).get('ref_calls'),
            'tool_attempts': sum(s.get('action_type') == 'tool' for s in steps),
            'named_tool_steps': sum(bool(s.get('tool')) for s in steps),
            'executed_tools': sum(bool(s.get('tool_executed')) for s in steps),
            'evidence_steps': sum(bool(s.get('tool_evidence')) for s in steps),
            'protocol_error_steps': sum(bool(s.get('protocol_error')) for s in steps),
            'tool_error_steps': sum(bool(s.get('tool_error')) for s in steps),
            'forced_reasons': [r.get('forced_answer_reason', 'none') for r in results],
            'at_generation_limit': any(len(r.get('steps', [])) >= manifest['harness']['max_steps'] for r in results),
            'literal_answer_stage': any(s.get('stage') == 'answer' for s in steps),
            'observed_model_answer': observed,
            'relaxed_only_pass': relaxed[c['id']] and not c['passed'],
            'provider_prompt_usage_populated': sum(s.get('usage', {}).get('prompt_tokens', 0) > 0 for s in steps),
            'request_tokens': {'complete': complete, 'covered_requests': len(counts),
                               'first': counts[0] if counts and ts[0].get('request_complete') else None,
                               'max': max(counts) if complete else None,
                               'cumulative': sum(counts) if complete else None},
            'terminal_actions': [r.get('steps', [{}])[-1].get('action_type') for r in results if r.get('steps')],
            'runner_errors': [t['runner_error'] for t in c['turns'] if t.get('runner_error')],
        })
    n = len(rows)
    agg = {'cases': n, 'official_passed': sum(c['official_passed'] for c in rows),
           'relaxed_passed': sum(c['relaxed_passed'] for c in rows),
           'forced_reasons': dict(Counter(r for c in rows for r in c['forced_reasons'])),
           'at_generation_limit': sum(c['at_generation_limit'] for c in rows),
           'observed_model_answers': sum(c['observed_model_answer'] for c in rows),
           'literal_answer_stage_cases': sum(c['literal_answer_stage'] for c in rows),
           'relaxed_only_passes': sum(c['relaxed_only_pass'] for c in rows)}
    for key in ['steps','tool_attempts','named_tool_steps','executed_tools','evidence_steps','protocol_error_steps','tool_error_steps']:
        vals = [c[key] for c in rows]
        agg[key] = {'total': sum(vals), 'cases_with_any': sum(v > 0 for v in vals), 'mean': statistics.mean(vals), 'median': statistics.median(vals), 'max': max(vals)}
    agg['tokens'] = {'complete_cases': sum(c['request_tokens']['complete'] for c in rows),
                    'provider_prompt_usage_populated': sum(c['provider_prompt_usage_populated'] for c in rows)}
    for key in ['first','max','cumulative']:
        vals = [c['request_tokens'][key] for c in rows if c['request_tokens'][key] is not None]
        agg['tokens'][key] = {'min': min(vals), 'median': statistics.median(vals), 'max': max(vals), 'sum': sum(vals)} if vals else None
    return {'run': str(run), 'source_sha256': {f: digest(run / f) for f in ['summary.json','run.json']},
            'aggregate': agg, 'cases': rows}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('root', type=Path)
    p.add_argument('--out', required=True, type=Path)
    a = p.parse_args()
    tokens = {r['run']: r for r in map(json.loads, (a.root / 'token-audit.jsonl').read_text().splitlines())}
    runs = [a.root / f'paired-none-steps{n}' for n in [10,30]]
    reports = [summarize(r, tokens) for r in runs]
    manifests = [json.loads((r/'run.json').read_text()) for r in runs]
    metas = [json.loads((r/'experiment.json').read_text()) for r in runs]
    assert manifests[0]['cases'] == manifests[1]['cases']
    assert manifests[0]['sampling'] == manifests[1]['sampling']
    assert manifests[0]['model'] == manifests[1]['model']
    assert metas[0]['binary_sha256'] == metas[1]['binary_sha256']
    hdiff = {k: [m['harness'].get(k) for m in manifests] for k in set(manifests[0]['harness']) | set(manifests[1]['harness']) if manifests[0]['harness'].get(k) != manifests[1]['harness'].get(k)}
    assert set(hdiff) == {'max_steps','wire_hash','wire_canonical'}, hdiff
    paired = []
    byid = [{c['id']: c for c in r['cases']} for r in reports]
    for cid in byid[0]:
        x,y = [b[cid] for b in byid]
        paired.append({'id': cid, 'changed_metrics': {k:[x[k],y[k]] for k in x if x[k]!=y[k]}})
    result = {'scope': 'Original 36 Workbank tool cases; no state, thinking off; frozen scorer unchanged',
              'definitions': {'attempt': 'step.action_type == tool, including nameless malformed calls',
                              'executed': 'step.tool_executed == true; errors still count as executions',
                              'evidence': 'step.tool_evidence == true; does not guarantee sufficient/correct evidence',
                              'observed_model_answer': 'nonempty un-repaired model answer; decision-stage final/no_tool included',
                              'relaxed_only': 'optimistic answer substring/numeric match with all other archived failures retained; not semantic proof',
                              'tokens': 'local RWKV vocabulary recount of complete stored prompts; not server usage'},
              'comparability': {'identical_frozen_cases': True,'identical_sampling':True,'identical_model':True,'binary_sha256':metas[0]['binary_sha256'],'harness_differences':hdiff},
              'vocab_sha256': sorted(set(t['vocab_sha256'] for t in tokens.values())),
              'runs': reports, 'paired': paired, 'elapsed_seconds': [m['elapsed_seconds'] for m in metas],
              'trajectory_changes': trajectory_comparison(*runs),
              'same_budget_repeat_trajectory_changes': trajectory_comparison(a.root / 'none-steps10', runs[0])}
    result['pass_flips'] = {key: {direction: [cid for cid in byid[0] if byid[0][cid][key] == before and byid[1][cid][key] == after]
                                 for direction, before, after in [('gained', False, True), ('lost', True, False)]}
                            for key in ['official_passed', 'relaxed_passed']}
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for r in reports:print(r['run'],json.dumps(r['aggregate'],ensure_ascii=False))


if __name__ == '__main__':
    main()
