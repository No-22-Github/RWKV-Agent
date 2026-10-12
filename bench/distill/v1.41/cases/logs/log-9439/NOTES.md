## Traps
- TR-DECOY: exact answer 107; the loose reading (counted the first freeze) gives 58.
- TR-TRUNC: the file is 81KB and 1221 data lines; read_file stops at 64KB and bash output at 8KB, so reading it and eyeballing the answer is unreliable.

## Reference solution
Turn 1: bash: `awk '$3=="MARK" && $4=="FREEZE-START" {k++; if (k==2) on=1; next} $3=="MARK" && $4=="FREEZE-END" {on=0} on && $3=="MERGE" {c++} END{print c+0}' repo/activity.dat` -> 107
Final answer: 107 MERGE events fall inside the release freeze.

## Why the answer is unique
Freezes are delimited by exact marker rows and the README names the second as the release freeze. The README (repo/README.md) fixes the rule; the answer is a single number.

## Five alternative phrasings of the task
1. Number of MERGE rows inside the second freeze window.
2. From the second FREEZE-START to its FREEZE-END, count rows whose action is MERGE.
3. Per repo/README.md, how many merges landed during the release freeze?
4. Count MERGE actions in the release freeze (second window) of activity.dat.
5. How many merge events were logged between the second FREEZE-START and the following FREEZE-END?
