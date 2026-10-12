## Traps
- TR-DECOY: /checkout/confirm and /checkout/ are different paths from /checkout; 5xx means status 500-599, 404 does not count. TR-MULTISRC: six node logs.

## Reference solution
Turn 1: read_file server/last-deploy.txt -> the last line is 4.12.3 (4.12.0 was rolled back).
Turn 2:
1. bash: `cat server/access/*.log | awk '$4=="/checkout" && $5>=500 {n++} END{print n}'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, read_file is the direct read. Turn 2 spans many files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. How many /checkout requests failed with a server error across the web nodes?
2. Count the 5xx hits on the /checkout path in every access log.
3. Total 500-599 responses for /checkout over all six logs?
4. Sum of server-error responses on exactly /checkout from all nodes.
5. 统计所有 web 节点日志里 /checkout 返回 5xx 的次数
