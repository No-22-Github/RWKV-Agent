#!/usr/bin/env python3
"""Run a state evaluation with serial before/after fingerprints and file identity.

Uses the raw continuation endpoint, never chat template defaults. Fingerprints
are drift guards, not cryptographic proof of server-side loaded tensor bytes.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.request

DEFAULT_ROOT = Path('runs/state-check-20260919')
ROOT = DEFAULT_ROOT
PROFILE = 'xml-v1+align-qwen36+no-tool+bare+one-stage'


def digest(value):
    return hashlib.sha256(value).hexdigest()


def effective_fingerprint(record):
    outputs=[]
    for row in record['requests']:
        text=row['output']
        indices=[text.index(stop) for stop in ['</tool_call>','\nUser:','\nSystem:','\nTool:'] if stop in text]
        if indices:text=text[:min(indices)]
        outputs.append(text)
    return digest(json.dumps(outputs,ensure_ascii=False).encode())


def request(headers, path, body=None):
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request('https://api-7b.rwkvos.com/v1/' + path, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.load(response)


def fingerprint(headers, state_id, fast, destination):
    # Synthetic tasks with the same system contract. No benchmark answer is
    # injected; these requests never execute generated tools or receive scores.
    training = Path('datasets/data/normalized/v1-selection-baseline/rwkv-agent-state-v1-none-ctx4096.jsonl')
    system = json.loads(next(training.open()))['text'].split('<tools>', 1)[0]
    catalog = [
        {'name':'read_file','description':'Read one UTF-8 text file inside the workspace, up to 64 KiB.','arguments':{'path':'relative file path'}},
        {'name':'no_tool','description':'Indicate that none of the offered tools is needed. Put a brief, complete user-facing response in reason; it becomes the final reply.','arguments':{'reason':'brief complete user-facing response'}},
    ]
    system += '<tools>[\n' + ',\n'.join(json.dumps(x,separators=(',',':')) for x in catalog) + '\n]</tools>'
    tasks = ['Read settings/canary.txt and report its verification word. Do not guess the file contents.', 'Hello! No file inspection is needed. Please greet me briefly.']
    record = {'state_id':state_id,'fast':fast,'started_unix':time.time(),'state_list':request(headers,'state/list'),'requests':[]}
    for task in tasks:
        prompt = system + '\n\nUser: '+task+'\n\nAssistant:' + (' <think></think' if fast else '')
        body = {'model':'rwkv-g1k-7b-temp-3601','contents':[prompt],'max_tokens':128,'temperature':1,'top_k':1,'top_p':1,'alpha_presence':0,'alpha_frequency':0,'alpha_decay':1,'stop_tokens':[0],'stream':False,'chunk_size':1}
        if state_id:
            body['state_id'] = state_id
        response = request(headers,'batch/completions',body)
        output = response['choices'][0]['message']['content']
        record['requests'].append({'request':body,'request_sha256':digest(json.dumps(body,sort_keys=True).encode()),'output':output,'output_sha256':digest(output.encode()),'response':response})
        destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    record['fingerprint'] = digest(json.dumps([r['output_sha256'] for r in record['requests']]).encode())
    destination.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    return record


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('name')
    ap.add_argument('--state-id',default='')
    ap.add_argument('--fast',action='store_true')
    ap.add_argument('--legacy-history',action='store_true')
    ap.add_argument('--wire',default='',help='extra wire overrides, e.g. nudge=none; incompatible with --fast which sets its own')
    ap.add_argument('--allow-canary-drift',action='store_true',help='record strict canary drift and continue when the client-stop-effective fingerprint is stable')
    ap.add_argument('--suites',default='workbank,boundary,bfcl')
    ap.add_argument('--parallelism',type=int,default=0,help='0 runs every case concurrently: Workbank 40, Boundary 18, BFCL 60')
    ap.add_argument('--credentials',required=True)
    ap.add_argument('--root',default=str(DEFAULT_ROOT),help='run root holding upload receipts, canaries and suite outputs')
    args=ap.parse_args()
    global ROOT
    ROOT = Path(args.root)
    ROOT.mkdir(parents=True,exist_ok=True)
    cred=json.loads(Path(args.credentials).read_text())
    headers={'CF-Access-Client-Id':cred['WIRE_CF_ID'],'CF-Access-Client-Secret':cred['WIRE_CF_SECRET'],'User-Agent':'curl/8.7.1','Content-Type':'application/json'}
    upload = json.loads((ROOT/(args.state_id+'.upload.json')).read_text()) if args.state_id else None
    if upload:
        assert digest(Path(upload['local_path']).read_bytes()) == upload['sha256']
    for suite in args.suites.split(','):
        parallelism=args.parallelism or {'workbank':40,'boundary':18,'bfcl':60}[suite]
        name=args.name+'-'+suite
        dest=ROOT/name
        before=ROOT/(name+'.canary-before.json');after=ROOT/(name+'.canary-after.json')
        if dest.exists() or before.exists():raise SystemExit('Refusing overwrite '+name)
        print('CANARY BEFORE',name,flush=True)
        a=fingerprint(headers,args.state_id,args.fast,before)
        registered=[s for s in a['state_list']['data'] if s['state_id']==args.state_id]
        if args.state_id and (len(registered)!=1 or registered[0]['size_bytes']!=upload['size_bytes']):raise SystemExit('State registration absent or mismatched')
        cmd=[sys.executable,'scripts/wire-experiment.py',args.name,'--root',str(ROOT),'--binary','build/rwkv-cli-state-experiment','--suites',suite,'--buffered','--parallelism',str(parallelism),'--profile',PROFILE+('+think-fast' if args.fast else ''),'--credentials',args.credentials]
        if args.state_id:cmd+=['--state-id',args.state_id]
        if args.fast and not args.legacy_history:cmd+=['--wire','history=think-fast,thinkcontrol=off']
        if args.wire:
            if args.fast:raise SystemExit('--wire and --fast both set the wire overrides; pick one')
            cmd+=['--wire',args.wire]
        result=subprocess.run(cmd)
        print('CANARY AFTER',name,flush=True)
        b=fingerprint(headers,args.state_id,args.fast,after)
        stable=a['fingerprint']==b['fingerprint']
        effective_stable=effective_fingerprint(a)==effective_fingerprint(b)
        current=[s for s in b['state_list']['data'] if s['state_id']==args.state_id]
        stable_registration=registered==current
        p=dest/'experiment.json'
        if p.exists():
            e=json.loads(p.read_text());e.update(state_file=upload,canary_before=str(before),canary_after=str(after),canary_stable=stable,state_registration_stable=stable_registration)
            e['canary_effective_stable']=effective_stable
            e['canary_effective_note']='Applies existing client text stops to both raw canaries; diagnostic distinction only. Strict raw fingerprint validity is retained.'
            e['transport_valid_for_model_comparison']=e['valid_for_model_comparison']
            e['valid_for_model_comparison']=e['valid_for_model_comparison'] and stable and stable_registration
            e['state_fingerprint_note']='run.json state_sha256 may hash ID string; state_file.sha256 here hashes the actual local .pth bytes.'
            p.write_text(json.dumps(e,indent=2)+'\n')
        print('VALIDITY',name,'canary_stable',stable,'registration_stable',stable_registration,flush=True)
        if args.allow_canary_drift and not stable and effective_stable:
            if p.exists():
                e=json.loads(p.read_text())
                e['canary_drift_tolerated']=True
                e['valid_for_model_comparison']=e.get('transport_valid_for_model_comparison',False) and stable_registration
                p.write_text(json.dumps(e,indent=2)+'\n')
            print('CANARY DRIFT TOLERATED',name,'effective_stable',effective_stable,flush=True)
            continue
        if result.returncode or not stable or not stable_registration:raise SystemExit('Run excluded; inspect transport/canary before continuing')


if __name__=='__main__':
    main()
