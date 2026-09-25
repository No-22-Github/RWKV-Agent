## Traps
- TR-NOTOOLNEED: the workspace holds ops/pipeline-rules.tsv and a README, but neither is needed. A model that inspects the workspace before replying burns a call it does not need, and the answer is unaffected by anything on disk. The near-miss decoy is `set -e`: it aborts on a failing command but a pipeline's status still comes from its last stage, so a mid-chain failure survives.

## Reference solution
1. Answer from the shell's own behaviour: `pipefail` makes a pipeline's exit status the rightmost non-zero status of its stages.
2. Reply with the single line `set -o pipefail` (the equivalent `set -euo pipefail` is also accepted).

## Why the answer is unique
The question asks for the setting whose whole purpose is that the pipeline reports the failure of any stage, and `pipefail` is the name of that setting; POSIX sh and every common shell spell it `set -o pipefail`, with the combined `set -euo pipefail` line the same statement plus two unrelated options. `set -e` is not a reading of the question: it changes whether a failing simple command aborts the shell, and a pipeline whose last stage succeeds still returns zero under `set -e` alone, so it leaves the described defect in place. The files on disk record the same setting for reference and change nothing.
