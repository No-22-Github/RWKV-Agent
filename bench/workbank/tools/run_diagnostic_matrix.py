#!/usr/bin/env python3
"""Run no-state scoring/ladder diagnostics with the same binary and budgets.

Secrets are read from a private JSON file and passed only through environment.
The existing wire experiment runner owns official suite execution/provenance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.request

PROFILE = 'xml-v1+align-qwen36+no-tool+bare+one-stage'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--credentials', required=True, type=Path)
    p.add_argument('--root', type=Path, default=Path('runs/scorer-ablation-20260919'))
    p.add_argument('--binary', default='build/rwkv-cli-scorer-ablation')
    args = p.parse_args()
    env = os.environ.copy()
    env.update(json.loads(args.credentials.read_text()))
    env['WIRE_UA'] = 'curl/8.7.1'

    def probe(name):
        headers = {'CF-Access-Client-Id':env['WIRE_CF_ID'], 'CF-Access-Client-Secret':env['WIRE_CF_SECRET'], 'User-Agent':env['WIRE_UA'], 'Content-Type':'application/json'}
        records = []
        for suffix in ['', ' <think></think']:
            body = {'model':'rwkv-g1k-7b-temp-3601','contents':['System: Reply briefly to the user.\n\nUser: Say hello.\n\nAssistant:'+suffix], 'max_tokens':64,'temperature':1,'top_k':1,'top_p':1,'alpha_presence':0,'alpha_frequency':0,'alpha_decay':1,'stop_tokens':[0],'stream':False,'chunk_size':1}
            req = urllib.request.Request('https://api-7b.rwkvos.com/v1/batch/completions',data=json.dumps(body).encode(),headers=headers)
            with urllib.request.urlopen(req,timeout=180) as r:
                response = json.load(r)
            records.append({'request':body,'response':response})
        (args.root / (name+'.probe.json')).write_text(json.dumps(records,indent=2)+'\n')

    def standard(name, fast, suites):
        cmd = [sys.executable,'scripts/wire-experiment.py',name,'--root',str(args.root),'--binary',args.binary,'--buffered','--parallelism','40','--suites',suites,'--credentials',str(args.credentials),'--profile',PROFILE+('+think-fast' if fast else '')]
        # Hold the system control text constant. Fast changes the current
        # empty-think prefix and preserves it on past assistant turns.
        if fast:
            cmd += ['--wire','history=think-fast,thinkcontrol=off']
        subprocess.run(cmd,check=True)

    probe('matrix-before')
    standard('fast-r1', True, 'boundary,workbank,bfcl')
    # A second fresh paired run tests how much pass flips vary on the server.
    standard('none-r2', False, 'boundary,workbank')
    standard('fast-r2', True, 'boundary,workbank')
    baseline = json.loads((args.root/'none-r1-workbank/experiment.json').read_text())['command']
    for fast in [False, True]:
        for catalog in ['default','work-v1']:
            name = ('fast' if fast else 'none')+'-ladder-'+catalog
            output = args.root/name
            if output.exists():
                raise SystemExit('Refusing overwrite '+str(output))
            cmd = baseline.copy()
            cmd[cmd.index('--cases')+1] = str(args.root/'ladder/cases.json')
            cmd[cmd.index('--output')+1] = str(output)
            cmd[cmd.index('--case-parallelism')+1] = '16'
            if catalog == 'default':
                for flag in ['--tool-catalog','--file-tools']:
                    i = cmd.index(flag)
                    del cmd[i:i+2]
            if fast:
                cmd[cmd.index('--profile')+1] = PROFILE+'+think-fast'
                cmd += ['--wire','history=think-fast,thinkcontrol=off']
            print('START',name,flush=True)
            started = time.time()
            with (args.root/(name+'.log')).open('w') as log:
                result = subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT)
            if not (output/'summary.json').exists():
                raise SystemExit((args.root/(name+'.log')).read_text()[-2000:])
            provenance = {'command':cmd,'binary_sha256':hashlib.sha256(Path(args.binary).read_bytes()).hexdigest(),'case_sha256':hashlib.sha256((args.root/'ladder/cases.json').read_bytes()).hexdigest(),'elapsed_seconds':time.time()-started,'exit_code':result.returncode,'state_id':'','evaluation_scope':'diagnostic_ladder'}
            (output/'experiment.json').write_text(json.dumps(provenance,indent=2)+'\n')
            summary = json.loads((output/'summary.json').read_text())
            failures = [f for c in summary['cases'] for t in c['turns'] for f in t.get('failures',[])]
            from wire_metrics import infrastructure_failure
            if any(infrastructure_failure(f) for f in failures):
                raise SystemExit('Infrastructure failure in '+name)
            print('DONE',name,summary['metrics']['task_success'],flush=True)
    probe('matrix-after')


if __name__ == '__main__':
    main()
