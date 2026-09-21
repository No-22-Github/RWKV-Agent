#!/usr/bin/env python3
"""Greedy continuation probe against the training corpus that produced a state.

Takes prefixes from the exported corpus, asks the raw continuation endpoint to
finish each one with and without the uploaded state, and measures how much of the
corpus's own reference continuation comes back. A state that was trained on that
corpus and is loaded as intended should recover the reference far better than the
zero state; no advantage is evidence the load or the prompt format is off.

Diagnostic only: no workbench case, scorer or run ledger is touched.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request


def request(headers, path, body):
    payload = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request('https://api-7b.rwkvos.com/v1/' + path, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=240) as response:
        return json.load(response)


def split_at_last_assistant(text):
    marker = '\nAssistant: '
    if marker not in text:
        return None
    head, _, tail = text.rpartition(marker)
    return head + marker[:len(marker) - 1], tail


def split_at_first_assistant(text):
    marker = '\nAssistant: '
    index = text.find(marker)
    if index < 0:
        return None
    return text[:index + len(marker) - 1], text[index + len(marker):]


def first_call(text):
    start = text.find('<tool_call>')
    if start < 0:
        return None
    end = text.find('</tool_call>', start)
    payload = text[start + len('<tool_call>'):end if end > 0 else len(text)]
    try:
        obj = json.loads(payload)
    except ValueError:
        return None
    if not isinstance(obj, dict) or not isinstance(obj.get('arguments'), dict):
        return None
    return obj


def common_prefix(a, b):
    for index, (x, y) in enumerate(zip(a, b)):
        if x != y:
            return index
    return min(len(a), len(b))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--corpus', default='outputs/workspace-agent-700-state-tune-textonly/train.textonly.jsonl')
    ap.add_argument('--split', choices=['first', 'last'], default='first',
                    help='first: probe the first decision point; last: probe the closing turn')
    ap.add_argument('--rows', type=int, default=24, help='number of corpus rows to probe')
    ap.add_argument('--stride', type=int, default=26, help='take every Nth row for a spread across scenarios')
    ap.add_argument('--state-id', default='state-final.pth')
    ap.add_argument('--credentials', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--max-tokens', type=int, default=96)
    args = ap.parse_args()

    cred = json.loads(Path(args.credentials).read_text())
    headers = {'CF-Access-Client-Id': cred['WIRE_CF_ID'], 'CF-Access-Client-Secret': cred['WIRE_CF_SECRET'],
               'User-Agent': 'curl/8.7.1', 'Content-Type': 'application/json'}

    rows = []
    splitter = split_at_first_assistant if args.split == 'first' else split_at_last_assistant
    with open(args.corpus) as handle:
        for index, line in enumerate(handle):
            if index % args.stride:
                continue
            text = json.loads(line)['text']
            parts = splitter(text)
            if not parts:
                continue
            prompt, reference = parts
            if len(reference) < 8:
                continue
            reference_call = first_call(reference)
            if args.split == 'first' and reference_call is None:
                continue
            rows.append({'row': index, 'prompt': prompt, 'reference': reference, 'reference_call': reference_call})
            if len(rows) >= args.rows:
                break

    record = {'corpus': args.corpus, 'corpus_sha256': hashlib.sha256(Path(args.corpus).read_bytes()).hexdigest(),
              'split': args.split, 'state_id': args.state_id, 'rows': len(rows), 'started_unix': time.time(),
              'arms': {}}
    for arm, state in (('zero', ''), ('state', args.state_id)):
        results = []
        for row in rows:
            body = {'model': 'rwkv-g1k-7b-temp-3601', 'contents': [row['prompt']], 'max_tokens': args.max_tokens,
                    'temperature': 1, 'top_k': 1, 'top_p': 1, 'alpha_presence': 0, 'alpha_frequency': 0,
                    'alpha_decay': 1, 'stop_tokens': [0], 'stream': False, 'chunk_size': 1}
            if state:
                body['state_id'] = state
            response = request(headers, 'batch/completions', body)
            output = response['choices'][0]['message']['content']
            reference = row['reference']
            produced = first_call(output)
            wanted = row['reference_call']
            entry = {'row': row['row'], 'reference': reference[:200], 'output': output[:200],
                     'common_prefix': common_prefix(output.strip(), reference.strip()),
                     'exact_start_16': output.strip()[:16] == reference.strip()[:16]}
            if wanted is not None:
                entry['reference_tool'] = wanted['name']
                entry['produced_tool'] = (produced or {}).get('name')
                entry['tool_match'] = bool(produced) and produced['name'] == wanted['name']
                entry['call_match'] = bool(produced) and produced == wanted
            results.append(entry)
        record['arms'][arm] = results
        print('ARM', arm, 'done', flush=True)
    for arm, results in record['arms'].items():
        tool_rows = [r for r in results if 'tool_match' in r]
        record.setdefault('summary', {})[arm] = {
            'mean_common_prefix': sum(r['common_prefix'] for r in results) / len(results),
            'exact_start_16': sum(r['exact_start_16'] for r in results),
            'tool_match': sum(r['tool_match'] for r in tool_rows),
            'call_match': sum(r['call_match'] for r in tool_rows),
            'tool_rows': len(tool_rows),
            'rows': len(results),
        }
    Path(args.output).write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(record['summary'], indent=2))


if __name__ == '__main__':
    main()
