## Traps
- TR-DECOY: release/NEXT.md.bak has the old codename; linux-arm lines share the prefix with linux and must not be summed. TR-MULTISRC: six monthly files, README in stats/README.md.

## Reference solution
Turn 1: read_file release/NEXT.md -> codename Harbor.
Turn 2:
1. bash: `cat stats/2026-*.txt | awk '$1=="linux" {s+=$2} END{print s}'`
Final answers: turn 1 as above; turn 2 states the number printed by the pipeline.

## Why the answer is unique
Turn 1 names its file; turn 2 is an exact-match aggregate over every file the README describes, so one number follows from the fixture.
Why bash is not the tool in turn 1: one named file and one fact, the read tool is the direct read. Turn 2 spans several files, where one pipeline beats opening them one by one.

## Five alternative phrasings of the task
1. Sum the linux downloads over May to October.
2. Total downloads for exactly the linux platform across stats/2026-*.txt?
3. How many linux downloads in all six months (linux-arm excluded)?
4. Add up every linux line's download count from the monthly stats files.
5. 统计 stats 下六个月文件里 linux 平台的下载量合计
