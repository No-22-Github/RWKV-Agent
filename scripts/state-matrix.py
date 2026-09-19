#!/usr/bin/env python3
"""Matched full-concurrency state matrix; keep failures, continue other arms."""
import json
from pathlib import Path
import subprocess
import sys
import time

root=Path('runs/state-check-20260919')
common=['--credentials','/tmp/rwkv-wire-experiment-credentials.json']
arms=[('zero-none-high',[]),('none-state-high',['--state-id','agent_state_none.pth']),('zero-fast-high',['--fast']),('fast-state-high',['--state-id','agent_state_fast_think.pth','--fast'])]
records=[]
for suite in ['workbank','boundary','bfcl']:
    for name,extra in arms:
        cmd=[sys.executable,'scripts/state-experiment.py',name,'--suites',suite]+extra+common
        print('MATRIX',name,suite,flush=True)
        started=time.time();p=subprocess.run(cmd)
        records.append({'name':name,'suite':suite,'exit_code':p.returncode,'elapsed_seconds':time.time()-started})
        (root/'high-concurrency-matrix-status.json').write_text(json.dumps(records,indent=2)+'\n')
print('MATRIX COMPLETE',flush=True)
