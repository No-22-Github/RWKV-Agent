#!/usr/bin/env python3
"""Generate a separate 16-case diagnostic, never modify the frozen Workbank.

Eight cells, two deterministic fixtures per cell, 240 UTF-8 fixture bytes each.
P3 intentionally uses five candidates: it cannot satisfy Claude's simultaneous
1-3 file constraint. P4 search may itself reveal the answer; read is not forced.
Pairs are probes, not 16 statistically independent capability observations.
"""
import argparse
import json
from pathlib import Path


def generate():
    cases = []
    cells = [(0, a) for a in range(4)] + [(p, 1) for p in range(1, 5)]
    for cell, (p, a) in enumerate(cells):
        for variant in range(2):
            token = ['LARCH-684', 'OTTER-927'][variant]
            target = 'records/current.txt'
            files = {target: f'verification_code={token}\n'}
            expected, ref = token, 1
            if p == 0:
                prompt = f'Read {target} and report verification_code.'
                if a == 0:
                    files = {target: token + '\n'}
                    prompt = f'Read {target} and report its value.'
                elif a == 2:
                    values = [7, 16, 23, 11] if variant == 0 else [13, 8, 27, 19]
                    files = {target: 'item,qty\n' + ''.join(f'{chr(97+i)},{n}\n' for i, n in enumerate(values))}
                    expected = str(sum(values))
                    prompt = f'Read {target} and report the sum of qty.'
                elif a == 3:
                    files = {'records/east.txt': f'qty={31+variant*20}\n', 'records/west.txt': f'qty={46-variant*12}\n'}
                    expected = 'WEST' if variant == 0 else 'EAST'
                    prompt = 'Read records/east.txt and records/west.txt. Report EAST or WEST, whichever has the larger qty.'
                    ref = 2
            elif p == 1:
                files['README.md'] = f'The current verification record is {target}.\n'
                prompt = 'Read README.md to locate the current verification record, then report its verification_code.'
                ref = 2
            elif p == 2:
                prompt = 'Locate the only file in records and report its verification_code.'
                ref = 2
            elif p == 3:
                files.update({f'records/{name}.txt': f'verification_code=DECOY-{i+100}\n' for i, name in enumerate(['previous','current-backup','archive','template'])})
                prompt = 'Locate the current verification record in records (not a backup, previous, archive, or template record) and report its verification_code.'
                ref = 2
            else:
                files = {'records/batch-a.txt': f'account=ORCHID\nverification_code={token}\n', 'records/batch-b.txt': 'account=MAPLE\nverification_code=DECOY-105\n'}
                prompt = 'Search records for account=ORCHID and report the verification_code belonging to that account.'
                ref = 2
            # Equalize total bytes without adding task facts or extra files.
            padding = 240 - sum(len(v.encode()) for v in files.values())
            assert padding >= 0
            first = next(iter(files))
            files[first] += '\n' * padding
            cid = f'ladder-{cell*2+variant+1:02d}'
            cases.append({'id': cid, 'description': f'Diagnostic P{p} A{a}, fixture {variant+1}; not a frozen benchmark.',
                'files': files, 'tags': {'p': p, 'a': a, 'family': f'p{p}-a{a}', 'ref_calls': ref, 'fixture_bytes':240},
                'turns': [{'prompt': prompt + ' Reply with only the answer.', 'expect': {'output_equals':expected}}]})
    return cases


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    cases = generate()
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'cases.json').write_text(json.dumps({'schema_version':5,'cases':cases}, indent=2)+'\n')
    print(f'Wrote {len(cases)} cases to {args.out / "cases.json"}')
