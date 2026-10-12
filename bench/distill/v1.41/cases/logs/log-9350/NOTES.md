## Traps
- TR-DECOY: INFO lines contain `WARN-level=off`; only the third field is the level. TR-READONLY: the originals stay in logs (待查/README.md), so it is a copy, not a move; exactly two copies.
- Later turns depend on the result of the first one (the answer of turn 1 picks what turn 2 edits), and the last turn changes part of what the previous edit did.

## Reference solution
Turn 1 (answer in the reply):
1. bash: `for f in logs/*.log; do echo "$f $(awk '$3=="WARN"' $f | wc -l)"; done`
Turn 2 (edit, reply DONE):
1. bash: `cp logs/app-2026-10-02.log logs/app-2026-10-03.log 待查/`
2. bash: `ls 待查 logs`

## Why the answer is unique
The first answer is an exact-match aggregate over the files the README describes; every later edit touches only the lines the requests name, in the order they were asked, and everything else stays byte-identical to the fixture (case_expect.files pins every path).

## Five alternative phrasings of the task
1. 哪天的 WARN 最多？把当天和前一天的日志复制到待查
2. 找出 WARN 行数最多的日期，拷贝这天和前一天的两份日志进 待查
3. WARN 级别最密集的是哪一天？把它和前一天的日志各留一份副本在待查里
4. 按日志级别字段统计 WARN，最多的那天和它前一天的文件复制到待查目录
5. Which day has the most WARN lines? Copy that day's log and the previous day's into 待查, leaving the originals.
