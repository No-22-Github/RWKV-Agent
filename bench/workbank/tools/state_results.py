#!/usr/bin/env python3
"""Summarize completed state runs without treating transport/drift as model score."""
import argparse
from collections import Counter
import json
from pathlib import Path

from failure_audit import audit
from first_step_metrics import metrics as first_metrics
from wire_metrics import analyze


def collect(root):
    runs={}; manifests={}; first_prompts={}
    for path in sorted(root.glob('*/summary.json')):
        d=path.parent;e=json.loads((d/'experiment.json').read_text()) if (d/'experiment.json').exists() else {}
        s=json.loads(path.read_text());w=analyze(d);a=audit(str(d));case_map={c['id']:c for c in s['cases']}
        manifests[d.name]=json.loads((d/'run.json').read_text())
        first_prompts[d.name]={c['id']:c['turns'][0]['result']['steps'][0].get('request',{}).get('prompt') for c in s['cases'] if c['turns'] and c['turns'][0]['result'].get('steps')}
        scenarios={};extra=Counter();details=[]
        for c in s['cases']:
            scenario=c.get('category','unknown');q=scenarios.setdefault(scenario,{'passed':0,'total':0});q['total']+=1;q['passed']+=c['passed']
            steps=[st for t in c['turns'] for st in t['result'].get('steps',[])]
            calls=[st for st in steps if st.get('action_type')=='tool']
            extra['zero_real_tool_cases']+=not calls
            extra['tool_case_passed']+=bool(c.get('tags',{}).get('ref_calls',0)) and c['passed']
            extra['protocol_error_cases']+=any(st.get('protocol_error') for st in steps)
            extra['plain_number_failure_cases']+=any('not a plain number' in f for t in c['turns'] for f in t.get('failures',[]))
            details.append({'id':c['id'],'passed':c['passed'],'category':scenario,'case_failures':c.get('failures',[]),'case_error':c.get('error'),'turns':[{'output':t['result'].get('output',''),'failures':t.get('failures',[]),'forced':t['result'].get('forced_answer_reason'),'actions':[{'step':st['number'],'tool':st.get('tool'),'arguments':st.get('tool_arguments'),'stage':st.get('stage'),'action':st.get('action_type'),'protocol_error':st.get('protocol_error'),'model_output':st.get('model_output',''),'repairs':st.get('protocol_repairs',[])} for st in t['result'].get('steps',[])]} for t in c['turns']]})
        r={'run':d.name,'valid':e.get('valid_for_model_comparison',False),'canary_stable':e.get('canary_stable'),'canary_effective_stable':e.get('canary_effective_stable'),'transport_valid':e.get('transport_valid_for_model_comparison'),'registration_stable':e.get('state_registration_stable'),'elapsed_seconds':e.get('elapsed_seconds'),'budgets':e.get('actual_request_token_budgets'),'wire':w['wire'],'metrics':w['metrics'],'failure_flags':a['totals'],'extra':dict(extra),'scenarios':scenarios,'case_pass':w['case_pass'],'details':details}
        if d.name.endswith('-workbank'):
            rows=first_metrics(case_map);r['first_step']=rows
            r['source_metrics']={'correct':sum(x['correct'] for x in rows.values()),'local_first_web':sum(x['first_web'] for k,x in rows.items() if not k.startswith(('nt-','web-','hyb-'))),'web_first_web':sum(x['first_web'] for k,x in rows.items() if k.startswith('web-')),'early_duplicate':sum(x['early_dup'] for x in rows.values())}
        r['binary_sha256']=e.get('binary_sha256')
        r['infrastructure_errors']=e.get('infrastructure_errors',[])
        runs[d.name]=r
    comparisons=[]
    for suite in ['workbank','boundary','bfcl']:
        for base,variant,label in [('zero-none','none-state','none state effect'),('zero-fast','fast-state','fast state effect'),('zero-none','zero-fast','format effect without state'),('fast-state-legacy','fast-state','history alignment effect with fast state')]:
            suffix='-high-'+suite
            bn=base+suffix;vn=variant+suffix
            if bn not in runs or vn not in runs:continue
            b,v=runs[bn],runs[vn];bp,vp=b['case_pass'],v['case_pass']
            comparisons.append({'label':label,'base':bn,'variant':vn,'valid':b['valid'] and v['valid'],'same_ids':set(bp)==set(vp),'gains':[k for k in bp if not bp[k] and vp.get(k)],'losses':[k for k in bp if bp[k] and not vp.get(k)]})
    for suite in ['workbank','boundary','bfcl']:
        for arm in ['zero-none','none-state','zero-fast','fast-state']:
            bn=arm+'-high-'+suite;vn=arm+'-repeat-'+suite
            if bn in runs and vn in runs:
                comparisons.append({'label':'repeat stability','base':bn,'variant':vn})
        bn='zero-fast-repeat-'+suite;vn='fast-state-repeat-'+suite
        if bn in runs and vn in runs:
            comparisons.append({'label':'fast state effect repeat','base':bn,'variant':vn})
    if 'zero-fast-repeat-workbank' in runs and 'fast-state-high-workbank' in runs:
        comparisons.append({'label':'fast state effect clean baseline repeat',
                            'base':'zero-fast-repeat-workbank','variant':'fast-state-high-workbank'})
    for c in comparisons:
        bn,vn=c['base'],c['variant'];b,v=runs[bn],runs[vn];bp,vp=b['case_pass'],v['case_pass']
        bm,vm=manifests[bn],manifests[vn];bf,vf=first_prompts[bn],first_prompts[vn]
        c.update(valid=b['valid'] and v['valid'],same_ids=set(bp)==set(vp),
                 gains=[k for k in bp if not bp[k] and vp.get(k)],losses=[k for k in bp if bp[k] and not vp.get(k)],
                 same_binary=b['binary_sha256']==v['binary_sha256'],same_sampling=bm['sampling']==vm['sampling'],
                 same_wire=bm['harness']['wire_canonical']==vm['harness']['wire_canonical'],
                 same_first_prompt_count=sum(bf[k]==vf.get(k) for k in bf),first_prompt_count=len(bf))
    fingerprints={}
    for path in sorted(root.glob('*.canary-*.json')):
        d=json.loads(path.read_text())
        if 'fingerprint' not in d:continue
        key=(d.get('state_id') or 'zero')+('/fast' if d['fast'] else '/none')
        group=fingerprints.setdefault(key,{'files':[],'fingerprints':[]})
        group['files'].append(path.name)
        if d['fingerprint'] not in group['fingerprints']:group['fingerprints'].append(d['fingerprint'])
    return {'runs':runs,'comparisons':comparisons,'canary_fingerprint_groups':fingerprints}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('root');ap.add_argument('--output');args=ap.parse_args();d=collect(Path(args.root))
    if args.output:Path(args.output).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
    for name,r in d['runs'].items():print(name,'VALID' if r['valid'] else 'UNVERIFIED/INVALID',f"{r['metrics']['passed']}/{r['metrics']['cases']}",'canary',r['canary_stable'],'extra',r['extra'])
    for c in d['comparisons']:print(json.dumps(c))
