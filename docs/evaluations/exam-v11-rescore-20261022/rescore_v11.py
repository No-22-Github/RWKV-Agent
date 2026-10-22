#!/usr/bin/env python3
"""Rescore finished agent-exam-v1.0 runs under agent-exam-v1.1 without rerunning them.

v1.1 only adds no_call_allowed_tools: ["calculator"] to the notool and BFCL
irrelevance cases (internal/agent/eval/scoring.go onlyAllowedCalls). A turn that
failed v1.0 only on "active no-call required", with outcome called_tool and every
call a calculator call, passes v1.1; nothing else changes.
Usage: rescore_v11.py <run_dir>...   (prints a markdown table)
"""
import json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(ROOT, '../../..'))
manifest = json.load(open(os.path.join(REPO, 'bench/exam/full.json')))
allowed = {}
for c in manifest['cases']:
    case = json.load(open(os.path.join(REPO, c['path'], 'case.json')))
    tools = {tuple(t.get('expect', {}).get('no_call_allowed_tools', [])) for t in case['turns']}
    if any(tools):
        allowed[c['id']] = set().union(*map(set, tools))


def turn_tools(turn):
    return [s['tool'] for s in turn['result'].get('steps', []) if s.get('tool')]


def rescore(run):
    cases = json.load(open(os.path.join(run, 'summary.json')))['cases']
    old = new = 0
    flipped = []
    for c in cases:
        if c.get('invalid'):
            continue
        ok = bool(c['passed'])
        old += ok
        if not ok and c['id'] in allowed:
            ok = True
            for t in c['turns']:
                if t.get('passed'):
                    continue
                fails = t.get('failures') or []
                if not (fails and all(f.startswith('active no-call required') for f in fails)
                        and t.get('outcome') == 'called_tool'
                        and turn_tools(t) and set(turn_tools(t)) <= allowed[c['id']]):
                    ok = False
                    break
            if ok:
                flipped.append(c['id'])
        new += ok
    return len(cases), old, new, flipped


print('| run | 题数 | v1.0 | v1.1 | +翻正 | 翻正题 |')
print('|---|---|---|---|---|---|')
for run in sys.argv[1:]:
    n, old, new, flipped = rescore(run)
    print(f'| {os.path.relpath(run, REPO)} | {n} | {old} | {new} | +{new - old} | {" ".join(sorted(flipped))} |')
