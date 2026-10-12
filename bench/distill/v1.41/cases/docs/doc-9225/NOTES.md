## Traps
- TR-DECOY: the user names one file; a backup, old, example or other-environment copy carries a different value (7).

## Reference solution
1. read_file on the named file.
Final answer: 增量备份保留 14 份（.bak 里 7 份是 2025 年旧版）。

## Why the answer is unique
The user names the file; only it holds the current value. The copy with another value is a decoy.
Why bash is not the tool here: one named file and one fact, the read tool is the direct read. The turn forbids bash so rows teach that bash being offered does not make it the default.

## Five alternative phrasings of the task
1. 运维/备份策略.txt 规定增量备份保留多少份？
2. 日增量备份留几份？看 运维/备份策略.txt。
3. 备份策略里每天的增量备份保留份数是多少？
4. 查一下 运维/备份策略.txt：增量备份保留几份？
5. 增量备份的保留数量是多少，以 运维/备份策略.txt 为准。
