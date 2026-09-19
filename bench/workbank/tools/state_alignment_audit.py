#!/usr/bin/env python3
"""Read-only full-corpus audit for the two supplied G1K state training exports."""
import collections
import hashlib
import json
from pathlib import Path
import re

BASE=Path('datasets/data/normalized/v1-selection-baseline')

def audit(kind):
    path=BASE/f'rwkv-agent-state-v1-{kind}-ctx4096.jsonl'
    rows=[json.loads(line) for line in path.open()]
    counters=collections.Counter();calls=collections.Counter();schemas=collections.Counter();buckets=collections.Counter();langs=collections.Counter()
    for row in rows:
        text=row['text'];counters['rows']+=1;buckets[row['meta']['bucket']]+=1;langs[row['meta']['lang']]+=1
        counters['workbank_canary_rows']+='WORKBANK-CANARY' in text
        counters['legacy_tool_role_rows']+=bool(re.search(r'(?:^|\n\n)Tool:',text))
        counters['pseudo_no_tool_tag_rows']+='<no_tool>' in text
        catalog=json.loads(text.split('<tools>',1)[1].split('</tools>',1)[0]);schemas.update(x['name'] for x in catalog)
        messages=re.split(r'\n\n(?=System: |User: |Assistant: )',text)
        assistant=[m[len('Assistant: '):] for m in messages if m.startswith('Assistant: ')]
        counters['assistant_segments']+=len(assistant)
        counters['assistant_empty_think']+=sum(x.startswith('<think></think>') for x in assistant)
        counters['tool_response_segments']+=sum(m.startswith('User: <tool_response>') for m in messages)
        for a,b in row['loss_spans']:
            target=text[a:b];counters['loss_spans']+=1
            counters['loss_prefix_empty_think']+=target.startswith('<think></think>')
            counters['span_preceded_empty_think']+=text[:a].endswith('<think></think>')
            if target.startswith('<tool_call>'):
                counters['supervised_tool_calls']+=1
                try: obj=json.loads(target[len('<tool_call>'):].removesuffix('</tool_call>'));calls[obj['name']]+=1
                except Exception: counters['invalid_supervised_call']+=1
            else:counters['supervised_plain_text']+=1
        counters['rows_above_4096']+=row['meta']['n_tok']>4096
    return {'path':str(path.resolve()),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'counts':dict(counters),'buckets':dict(buckets),'languages':dict(langs),'supervised_call_names':dict(calls.most_common()),'catalog_names':dict(schemas.most_common()),'max_recorded_tokens':max(r['meta']['n_tok'] for r in rows)},rows

if __name__=='__main__':
    none,nrows=audit('none');fast,frows=audit('think-fast')
    paired={r['meta']['id']:r for r in frows};diff=[]
    for r in nrows:
        f=paired.get(r['meta']['id'])
        if not f or f['text'].replace('Assistant: <think></think>','Assistant: ')!=r['text']:diff.append(r['meta']['id'])
    report={'none':none,'fast':fast,'paired_text_differences_after_removing_assistant_empty_think':diff,'same_ids':set(paired)=={r['meta']['id'] for r in nrows},'scope':'Training data audit, not held-out model evaluation. Prefix/loss span counts describe file contents, not proof of the trainer implementation.'}
    print(json.dumps(report,ensure_ascii=False,indent=2))
