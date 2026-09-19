#!/usr/bin/env python3
"""Summarize archived paired scoring, evidence and termination diagnostics."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

from scorer_ablation import analyze
from wire_metrics import infrastructure_failure


def summarize(path):
    data = analyze(path)
    manifest = json.loads((path/'run.json').read_text())
    summary = json.loads((path/'summary.json').read_text())
    frozen = {c['id']:c for c in manifest['cases']}
    rows, counts, cells = [], Counter(), defaultdict(Counter)
    for case, scored in zip(summary['cases'],data['details']):
        assert case['id'] == scored['id']
        turns = case['turns']
        steps = [s for t in turns for s in t['result'].get('steps',[])]
        tools = [s for s in steps if s.get('action_type')=='tool' and s.get('tool')!='no_tool']
        executed = [s for s in tools if s.get('tool_executed')]
        evidence = [s for s in executed if s.get('tool_evidence')]
        errors = [f for t in turns for f in t.get('failures',[]) if f.startswith('runner error:')]
        forced = any(t['result'].get('forced_answer_reason') for t in turns)
        last = steps[-1] if steps else {}
        autonomous = bool(turns[-1]['result'].get('output')) and not any(t['result'].get('answer_contract_repaired') for t in turns) and not forced and not errors and not last.get('protocol_error') and not last.get('stage_violation') and last.get('stage')!='answer' and last.get('action_type') in ('final','no_tool')
        tags = frozen[case['id']].get('tags',{})
        ref = tags.get('ref_calls')
        relaxed = scored['arms']['answer_relaxed']['passed']
        casefold = scored['arms'].get('answer_casefold', scored['arms']['answer_relaxed'])['passed']
        # No extra inference: TERM is a joint outcome on the same trace.
        term = relaxed and autonomous and ref is not None and len(steps)<=ref+1
        row = {'id':case['id'],'strict':case['passed'],'relaxed':relaxed,'steps':len(steps),'tool_attempts':len(tools),'executed':len(executed),'evidence':bool(evidence),'autonomous':autonomous,'forced':forced,'term_pass':term,'ref_calls':ref,'path':[(s.get('tool') or s.get('action_type'),s.get('stage')) for s in steps], 'outputs':[t['output'] for t in scored['arms']['answer_relaxed']['turns']]}
        rows.append(row)
        row['casefold_relaxed'] = casefold
        counts['casefold_relaxed'] += casefold
        counts['term_eligible'] += ref is not None
        counts.update({'cases':1,'strict':case['passed'],'relaxed':relaxed,'evidence_cases':bool(evidence),'zero_executed':not executed,'autonomous':autonomous,'forced':forced,'term_pass':term,'relaxed_with_evidence':relaxed and bool(evidence),'infra_cases':any(infrastructure_failure(f) for f in errors),'answer_stage_tool_calls':sum(s.get('stage')=='answer' and s.get('action_type')=='tool' for s in steps),'duplicate_rejections':sum(s.get('tool_rejected_reason')=='duplicate_tool_call' for s in steps)})
        if 'p' in tags:
            cells[f"P{tags['p']}A{tags['a']}"].update({'cases':1,'strict':case['passed'],'relaxed':relaxed,'casefold_relaxed':casefold,'with_evidence':relaxed and bool(evidence),'term_pass':term})
    return {'run':str(path),'counts':dict(counts),'cells':dict(cells),'arms':data['arms'],'rows':rows,'source_sha256':data['source_sha256']}


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,required=True)
    args=p.parse_args()
    runs=[summarize(s.parent) for s in sorted(args.root.glob('*/summary.json'))]
    (args.root/'matrix-summary.json').write_text(json.dumps({'runs':runs},ensure_ascii=False,indent=2)+'\n')
    lines=['| Run | N | Original | Relaxed | Evidence + relaxed | Autonomous | Forced | TERM | Infra |','|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for run in runs:
        c=run['counts']
        lines.append('| '+Path(run['run']).name+' | '+' | '.join('N/A' if k == 'term_pass' and not c['term_eligible'] else str(c[k]) for k in ['cases','strict','relaxed','relaxed_with_evidence','autonomous','forced','term_pass','infra_cases'])+' |')
    (args.root/'matrix-summary.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
