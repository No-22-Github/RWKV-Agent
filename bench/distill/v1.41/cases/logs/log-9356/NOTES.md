## Traps
- TR-DECOY: `oom_score_adj=0` lines are not OOM kills; only the exact text OOM-killed counts. TR-READONLY: hosts without a kill keep restart: none; job-1 is already queued and stays the first line (inventory/README.md: append only).
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `grep -c 'OOM-killed' logs/*.log`
Turn 2 (edit, reply DONE):
1. bash: `echo cache-1 >> inventory/restart.list; sed -i 's/^restart: none$/restart: pending/' inventory/cache-1.yaml; echo web-1 >> inventory/restart.list; sed -i 's/^restart: none$/restart: pending/' inventory/web-1.yaml; echo web-2 >> inventory/restart.list; sed -i 's/^restart: none$/restart: pending/' inventory/web-2.yaml`
2. bash: `cat inventory/restart.list; grep -n restart: inventory/*.yaml`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. Which hosts were hit by the OOM killer? Add them to the restart list and set restart: pending on their inventory files.
2. Find hosts with an OOM-killed message, append them to restart.list and mark them pending in inventory.
3. List hosts whose logs show OOM-killed; queue them (restart.list plus restart: pending in their yaml).
4. Check the logs for OOM kills; the affected hosts go onto the restart queue and get restart: pending.
5. 哪些主机的日志里出现了 OOM-killed？把它们加进 restart.list，并在 inventory 里把 restart 改成 pending
