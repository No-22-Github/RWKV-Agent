## Traps
- TR-DECOY: atlas==2.30.1 and atlas==2.2.9 are not 2.3.N pins; atlas==2.4.0 is already new. TR-READONLY: docs/archive and docs/CHANGELOG.md are history (docs/README.md). Internal pages all used 2.3.1, so turn 3 has one correct target text.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep -rlE 'atlas==2\.3\.[0-9]+' docs | grep -v archive | grep -v CHANGELOG | wc -l`
Turn 2 (edit, reply DONE):
1. bash: `grep -rlE 'atlas==2\.3\.[0-9]+' docs | grep -v archive | grep -v CHANGELOG | xargs sed -i -E 's/atlas==2\.3\.[0-9]+/atlas==2.4.0/g'`
2. bash: `grep -rn 'atlas==' docs`
Turn 3 (edit, reply DONE):
1. bash: `grep -rl 'atlas==2.4.0' docs/internal | xargs sed -i 's/atlas==2\.4\.0/atlas==2.3.1/g'`
2. bash: `grep -rn 'atlas==' docs/internal`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Count the doc pages pinned to atlas 2.3.x, upgrade them to 2.4.0 (not history), then restore docs/internal to 2.3.1.
2. How many pages use atlas==2.3.N? Move them to 2.4.0 and afterwards put the internal ones back on 2.3.1.
3. Find pages pinned to atlas 2.3.something, switch the pin to 2.4.0 except archive and changelog, then revert internal.
4. Number of non-history docs pinning atlas==2.3.N; update to 2.4.0; internal pages go back to 2.3.1.
5. docs 里有多少页固定了 atlas==2.3.N？都改成 2.4.0（历史页除外），再把 docs/internal 改回 2.3.1
