## Traps
- TR-DECOY: the path /v1/items/500 has status 200; 404/429 are not 5xx; the status is the 5th field. TR-READONLY: burst_rps = 100 is a look-alike line and edge/_shared is common (edge/README.md), so `s/= 100/= 60/` is wrong.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in access/*.log; do echo "$f $(awk '$5>=500' $f | wc -l)"; done`
Turn 2 (edit, reply DONE):
1. bash: `sed -i 's/^rate_limit_rps = 100$/rate_limit_rps = 60/' edge/api-c/limits.conf edge/api-c/limits.canary.conf edge/api-c/limits.dr.conf`
2. bash: `grep -rn rate_limit edge/api-c`
Turn 3 (edit, reply DONE):
1. bash: `sed -i 's/^rate_limit_rps = 60$/rate_limit_rps = 100/' edge/api-c/limits.canary.conf edge/api-c/limits.dr.conf`
2. bash: `grep -rn rate_limit edge/api-c`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Find the upstream with the most server errors and throttle it to 60 rps in all three limit files, then undo that for canary and dr.
2. Which upstream has the most 5xx? Cut its rate limit to 60, afterwards restore canary and dr.
3. Check the access logs for the worst upstream (5xx), set its rate_limit_rps to 60 in three files, then revert two of them.
4. Highest 5xx count wins: reduce that upstream's rate_limit_rps to 60 and later bring the canary and dr limits back to 100.
5. 找出 5xx 最多的上游，把它三个限流文件的 rate_limit_rps 降到 60，然后恢复 canary 和 dr 的两份
