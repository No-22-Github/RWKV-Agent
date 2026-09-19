#!/usr/bin/env python3
"""Paired, offline scorer sensitivity on archived outputs; never reruns a model.

Preserves archived non-target failures, including runtime/protocol errors,
answer-contract repair, required tools, file verification and script execution.
Uses each run's frozen case expectations, not today's bank. Numeric-any is an
optimistic diagnostic, not a semantic correctness or deployable scorer claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re

NUMBER = re.compile(r"(?<![\w.])[+-]?\d+(?:,\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?(?!\w|\.\d)")


def answer(result):
    if result.get('original_output') or result.get('answer_contract_repaired'):
        return result.get('original_output', '')
    return result.get('output', '')


def rescore(case, frozen, relax=False, drop_calls=False, remove_unknown=False, relax_numeric=True, ignore_case=False):
    failures = list(case.get('failures') or [])
    if case.get('error'):
        failures.append('case error: ' + case['error'])
    observations = []
    if len(case['turns']) < len(frozen['turns']):
        failures.append('case incomplete: not all specified turns ran')
    assert len(case['turns']) <= len(frozen['turns'])
    for turn, spec in zip(case['turns'], frozen['turns']):
        remaining = list(turn.get('failures') or [])
        expect = spec['expect']
        output = answer(turn['result'])
        matches = None
        numbers = []
        if relax and 'output_equals' in expect:
            remaining = [f for f in remaining if not (f.startswith('output = ') and f.endswith('after trimming outer whitespace'))]
            expected_text = expect['output_equals'].strip()
            matches = expected_text.casefold() in output.casefold() if ignore_case else expected_text in output
        elif relax and relax_numeric and 'expected_number' in expect:
            remaining = [f for f in remaining if not (f.startswith('output ') and f.endswith('is not a plain number') or f.startswith('numeric output = '))]
            numbers = [float(v.replace(',', '')) for v in NUMBER.findall(output)]
            matches = any(abs(n - expect['expected_number']) <= expect.get('tolerance', .01) for n in numbers)
        if matches is False:
            remaining.append('diagnostic relaxed answer did not match')
        if drop_calls:
            remaining = [f for f in remaining if not f.startswith(('missing required call to ', 'forbidden tool '))]
        if remove_unknown and case['id'] in ('nt-0003', 'nt-0004'):
            alternatives = [v for v in expect['output_contains_any'] if v != 'UNKNOWN']
            remaining = [f for f in remaining if not f.startswith('output does not contain any of ')]
            if not any(v in output for v in alternatives):
                remaining.append('diagnostic no-UNKNOWN alternatives did not match')
        failures.extend(remaining)
        observations.append({'output': output, 'relaxed_match': matches, 'numbers': numbers,
                             'remaining_failures': remaining})
    return {'passed': not failures, 'failures': failures, 'turns': observations}


def analyze(path):
    manifest_path, summary_path = path / 'run.json', path / 'summary.json'
    manifest = json.loads(manifest_path.read_text())
    summary = json.loads(summary_path.read_text())
    frozen = {c['id']: c for c in manifest['cases']}
    boundary = all(c['id'].startswith('pb_') for c in summary['cases'])
    arms = {'original': {}, 'answer_relaxed': {'relax': True}}
    if boundary:
        arms['answer_relaxed']['relax_numeric'] = False
        arms['answer_relaxed_drop_calls_forbidden'] = {'relax': True, 'drop_calls': True, 'relax_numeric': False}
    elif all(c['id'].startswith('ladder-') for c in summary['cases']):
        arms['answer_casefold'] = {'relax': True, 'ignore_case': True}
    else:
        arms['no_unknown_only'] = {'remove_unknown': True}
        arms['answer_relaxed_no_unknown'] = {'relax': True, 'remove_unknown': True}
    details = []
    for case in summary['cases']:
        row = {'id': case['id'], 'official_passed': case['passed'], 'arms': {}}
        for name, options in arms.items():
            row['arms'][name] = rescore(case, frozen[case['id']], **options)
        if row['arms']['original']['passed'] != case['passed']:
            raise ValueError('Archived failure reconstruction mismatch: ' + case['id'])
        details.append(row)
    counts = {}
    for name in arms:
        counts[name] = {'passed': sum(r['arms'][name]['passed'] for r in details),
                        'gained': [r['id'] for r in details if r['arms'][name]['passed'] and not r['official_passed']],
                        'lost': [r['id'] for r in details if not r['arms'][name]['passed'] and r['official_passed']]}
    return {'run': str(path), 'cases': len(details), 'arms': counts,
            'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (manifest_path, summary_path)},
            'details': details}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', nargs='+', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    results = [analyze(p) for p in args.runs]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({'method': __doc__, 'runs': results}, ensure_ascii=False, indent=2) + '\n')
    for result in results:
        print(result['run'], result['cases'], json.dumps(result['arms'], ensure_ascii=False))


if __name__ == '__main__':
    main()
