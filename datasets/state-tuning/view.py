"""Human-readable view of state-tuning semantic batches.

Usage:
    python3 view.py                          # all batches, all subtypes
    python3 view.py -s near_neighbor         # one subtype
    python3 view.py -s positive -s chitchat  # several
    python3 view.py semantic/batch-001.json  # specific file(s)
    python3 view.py --ids abst-0043,abst-0051
"""
import argparse
import collections
import glob
import json

ORDER = ['pure_knowledge', 'pure_calculation', 'chitchat',
         'trap_capability', 'near_neighbor', 'positive']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='*')
    ap.add_argument('-s', '--subtype', action='append', default=[])
    ap.add_argument('--ids', default='')
    ap.add_argument('--brief', action='store_true',
                    help='one line per case: id, action, user')
    args = ap.parse_args()

    paths = args.files or sorted(glob.glob(
        'datasets/state-tuning/semantic/batch-*.json'))
    cases = []
    for p in paths:
        cases.extend(json.load(open(p)))

    wanted_ids = {i.strip() for i in args.ids.split(',') if i.strip()}
    if wanted_ids:
        cases = [c for c in cases if c['id'] in wanted_ids]
    if args.subtype:
        cases = [c for c in cases if c['subtype'] in args.subtype]

    groups = collections.defaultdict(list)
    for c in cases:
        groups[c['subtype']].append(c)

    for subtype in ORDER:
        rows = groups.get(subtype)
        if not rows:
            continue
        print(f'\n{"=" * 78}')
        print(f'{subtype.upper()}  ({len(rows)})')
        print('=' * 78)
        for c in rows:
            action = ('ABSTAIN' if c['action'] == 'abstain'
                      else 'CALL ' + c['call']['name'])
            if args.brief:
                print(f'{c["id"]} [{c["lang"]}] {action:22s} {c["user"]}')
                continue
            print(f'{c["id"]} [{c["lang"]}] {action}')
            print(f'  U  {c["user"]}')
            print(f'  A  {c["answer"]}')
            print(f'  T  {c["think"]}')
            if c['action'] == 'call':
                print('  →  ' + json.dumps(c['call']['arguments'],
                                           ensure_ascii=False))
            tail = '  tools=' + ','.join(c['tools'])
            if c.get('paired_with'):
                tail += f'  pair={c["paired_with"]}'
            print(tail)
    print(f'\ntotal shown: {len(cases)}')


if __name__ == '__main__':
    main()
