#!/usr/bin/env python3
"""Anchor-agreement metrics for a workbank run: how well the first decision matches
the corpus's own trajectory for the same prompt.

Three levels, each with the constant-policy baseline that must be reported:
- tool name agrees with the corpus anchor's first tool
- (tool, arguments) agrees exactly
- the whole first assistant turn agrees byte for byte

Baselines: always emitting the corpus modal action scores at the modal level; a
policy that reproduces nothing scores 0. Agreement well below the modal baseline
means the prompt-conditioned policy is not installed at all.

Usage: measure_anchor_agreement.py <run-dir> [<run-dir> ...]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

CORPUS = 'outputs/workspace-agent-700/generated/rendered/none-ctx4096/train.jsonl'
CALL = re.compile(r'<tool_call>(\s*\{.*?\}\s*)</tool_call>', re.S)


def corpus_anchors():
    anchors = {}
    for line in Path(CORPUS).open():
        record = json.loads(line)
        meta = record['meta']
        if not meta.get('is_seed_anchor'):
            continue
        text = record['text']
        body = text[text.find('\nAssistant:') + len('\nAssistant:'):]
        match = CALL.search(body)
        call = json.loads(match.group(1)) if match else None
        turn_end = body.find('\nUser:')
        anchors[meta['parent_seed_id']] = {
            'call': call,
            'turn': body[:turn_end if turn_end >= 0 else len(body)].strip(),
        }
    return anchors


def main(paths):
    anchors = corpus_anchors()
    modal_name = Counter(a['call']['name'] for a in anchors.values() if a['call']).most_common(1)[0][0]
    modal_call = Counter(json.dumps(a['call'], sort_keys=True) for a in anchors.values() if a['call']).most_common(1)[0]
    print(f'corpus anchors: {len(anchors)}; constant baselines: name={modal_name} '
          f'{sum(1 for a in anchors.values() if a["call"] and a["call"]["name"] == modal_name)}/{len(anchors)}, '
          f'exact {modal_call[1]}/{len(anchors)} {modal_call[0][:60]}')
    for run in paths:
        summary = json.loads((Path(run) / 'summary.json').read_text())
        name_hit = exact_hit = turn_hit = total = 0
        for case in summary['cases']:
            anchor = anchors.get(case['id'])
            steps = case['turns'][0]['result'].get('steps') or []
            if not anchor or not steps:
                continue
            total += 1
            first = steps[0]
            produced = {'name': first.get('tool'), 'arguments': first.get('tool_arguments')} \
                if first.get('action_type') == 'tool' else None
            want = anchor['call']
            if produced and want and produced['name'] == want['name']:
                name_hit += 1
            if produced == want:
                exact_hit += 1
            # The stop token consumes "</tool_call>", so the recorded output omits
            # the close; add it back before comparing the whole first turn.
            produced_turn = (first.get('model_output') or '').strip()
            if produced_turn and not produced_turn.endswith('</tool_call>'):
                produced_turn += '</tool_call>'
            if produced_turn == anchor['turn'].strip():
                turn_hit += 1
        print(f'{Path(run).name:34s} n={total:2d}  name {name_hit:2d}  exact(tool,args) {exact_hit:2d}  '
              f'first-turn bytes {turn_hit:2d}')


if __name__ == '__main__':
    main(sys.argv[1:])
